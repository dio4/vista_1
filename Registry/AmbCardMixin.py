# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import os
import subprocess
import sys
from PyQt4 import QtCore, QtGui, QtSql

from Events.Action import ActionStatus, CAction, CActionTypeCache
from Events.ActionInfo import CActionInfo, CLocActionInfoList
from Events.EventInfo import CDiagnosisInfoList, CEventInfo, CLocEventInfoList
from Events.TempInvalidInfo import CTempInvalidInfoList
from Events.Utils import EventOrder, getActionTypeDescendants, getMKBName, payStatusText, setActionPropertiesColumnVisible
from Orgs.Utils import getOrgStructurePersonIdList
from Registry.RegistryTable import CAmbCardAnalysesActionsTableModel, CAmbCardDiagnosticsAccompDiagnosticsTableModel, \
    CAmbCardDiagnosticsActionsTableModel, CAmbCardDiagnosticsTableModel, CAmbCardDiagnosticsVisitsTableModel, \
    CAmbCardStatusActionsTableModel, CClientFilesTableModel
from Registry.Utils import getClientBanner, getClientInfo2
from Reports.ClientVisits import CClientVisits
from Reports.ReportView import CReportViewDialog
from library.DialogBase import CConstructHelperMixin
from library.PrintInfo import CInfoContext
from library.PrintTemplates import applyTemplate, compileAndExecTemplate, getFirstPrintTemplate, getPrintAction, getTemplate
from library.Utils import forceDate, forceInt, forceRef, forceString, forceStringEx, toVariant
from library.web import openInDicomViewer, openURLinBrowser


class CAmbCardMixin(CConstructHelperMixin):
    def preSetupUi(self):
        self.addModels('AmbCardDiagnostics', CAmbCardDiagnosticsTableModel(self))
        self.addModels('AmbCardDiagnosticsVisits', CAmbCardDiagnosticsVisitsTableModel(self))
        self.addModels('AmbCardDiagnosticsAccompDiagnostics', CAmbCardDiagnosticsAccompDiagnosticsTableModel(self))
        self.addModels('AmbCardDiagnosticsActions', CAmbCardDiagnosticsActionsTableModel(self))
        self.addModels('AmbCardStatusActions', CAmbCardStatusActionsTableModel(self))
        self.addModels('AmbCardDiagnosticActions', CAmbCardStatusActionsTableModel(self))
        self.addModels('AmbCardCureActions', CAmbCardStatusActionsTableModel(self))
        self.addModels('AmbCardMiscActions', CAmbCardStatusActionsTableModel(self))
        self.addModels('AmbCardAnalysesActions', CAmbCardAnalysesActionsTableModel(self))
        self.addModels('AmbCardClientFiles', CClientFilesTableModel(self))
        self.actAmbCardUploadFile =               QtGui.QAction(u'Добавить', self)
        self.actAmbCardUploadFile.setObjectName('actAmbCardUploadFile')
        self.actAmbCardDownloadFile =             QtGui.QAction(u'Скачать', self)
        self.actAmbCardDownloadFile.setObjectName('actAmbCardDownloadFile')
        self.actAmbCardDeleteFile =               QtGui.QAction(u'Удалить', self)
        self.actAmbCardDeleteFile.setObjectName('actAmbCardDeleteFile')
        self.actAmbCardOpenFile =                 QtGui.QAction(u'Открыть', self)
        self.actAmbCardOpenFile.setObjectName('actAmbCardOpenFile')
        self.actAmbCardPrintEvents =      QtGui.QAction(u'Напечатать список визитов', self)
        self.actAmbCardPrintEvents.setObjectName('actAmbCardPrintEvents')
        self.actAmbCardPrintCaseHistory = getPrintAction(self, 'caseHistory', u'Напечатать карту')
        self.actAmbCardPrintCaseHistory.setObjectName('actAmbCardPrintCaseHistory')
        self.mnuAmbCardPrintEvents = QtGui.QMenu(self)
        self.mnuAmbCardPrintEvents.setObjectName('mnuAmbCardPrintEvents')
        self.mnuAmbCardPrintEvents.addAction(self.actAmbCardPrintEvents)
        self.mnuAmbCardPrintEvents.addAction(self.actAmbCardPrintCaseHistory)
        self.actAmbCardPrintAction =         getPrintAction(self, None, u'Напечатать по шаблону', False)
        self.actAmbCardPrintAction.setObjectName('actAmbCardPrintAction')
        self.actAmbCardPrintActions =        QtGui.QAction(u'Напечатать список мероприятий', self)
        self.actAmbCardPrintActions.setObjectName('actAmbCardPrintActions')
        self.actAmbCardPrintActionTemplate = QtGui.QAction(u'Напечатать Мед.карту', self)
        self.actAmbCardPrintActionTemplate.setObjectName('actAmbCardPrintActionTemplate')
        self.actAmbCardPrintActionTemplate.setShortcut('F6')
        self.actAmbCardPrintActionsHistory = getPrintAction(self, 'actionsHistory', u'Напечатать карту мероприятий', False)
        self.actAmbCardPrintActionsHistory.setObjectName('actAmbCardPrintActionsHistory')
        self.mnuAmbCardPrintActions = QtGui.QMenu(self)
        self.mnuAmbCardPrintActions.setObjectName('mnuAmbCardPrintActions')
        self.mnuAmbCardPrintActions.addAction(self.actAmbCardPrintAction)
        self.mnuAmbCardPrintActions.addAction(self.actAmbCardPrintActions)
        self.mnuAmbCardPrintActions.addAction(self.actAmbCardPrintActionsHistory)
        self.mnuAmbCardPrintActions.addAction(self.actAmbCardPrintActionTemplate)

        self.__ambCardDiagnosticsFilter = {}
        self._statusActionsSet = set()
        self._diagnosticActionsSet = set()
        self._cureActionsSet = set()
        self._miscActionsSet = set()
        self._analysesActionsSet = set()

        # TODO: skkachaev: Это потому что CTextBrowser возвращает покорёженную html'ку
        self._statusActionsHTML = u''
        self._diagnosticActionsHTML = u''
        self._cureActionsHTML = u''
        self._miscActionsHTML = u''
        self._analysesActionsHTML = u''

    def postSetupUi(self):
        self.setModels(self.tblAmbCardDiagnostics, self.modelAmbCardDiagnostics, self.selectionModelAmbCardDiagnostics)
        self.setModels(self.tblAmbCardDiagnosticsVisits, self.modelAmbCardDiagnosticsVisits, self.selectionModelAmbCardDiagnosticsVisits)
        self.setModels(self.tblAmbCardDiagnosticsAccompDiagnostics, self.modelAmbCardDiagnosticsAccompDiagnostics, self.selectionModelAmbCardDiagnosticsAccompDiagnostics)
        self.setModels(self.tblAmbCardDiagnosticsActions, self.modelAmbCardDiagnosticsActions, self.selectionModelAmbCardDiagnosticsActions)
        self.setModels(self.tblAmbCardStatusActions, self.modelAmbCardStatusActions, self.selectionModelAmbCardStatusActions)
        self.setModels(self.tblAmbCardDiagnosticActions, self.modelAmbCardDiagnosticActions, self.selectionModelAmbCardDiagnosticActions)
        self.setModels(self.tblAmbCardCureActions, self.modelAmbCardCureActions, self.selectionModelAmbCardCureActions)
        self.setModels(self.tblAmbCardMiscActions, self.modelAmbCardMiscActions, self.selectionModelAmbCardMiscActions)
        self.setModels(self.tblAmbCardAnalysesActions, self.modelAmbCardAnalysesActions, self.selectionModelAmbCardAnalysesActions)
        self.setModels(self.tblFiles, self.modelAmbCardClientFiles, self.selectionModelAmbCardClientFiles)

        self.cmbAmbCardDiagnosticsPurpose.setTable('rbEventTypePurpose', True)
        self.cmbAmbCardDiagnosticsSpeciality.setTable('rbSpeciality', True)

        self.cmbAmbCardStatusGroup.setClass(0)
        self.cmbAmbCardDiagnosticGroup.setClass(1)
        self.cmbAmbCardCureGroup.setClass(2)
        self.cmbAmbCardMiscGroup.setClass(3)
        self.cmbAmbCardAnalysesGroup.setClass(4)

        self.cmbAmbCardStatusEventType.setTable('EventType')
        self.cmbAmbCardDiagnosticEventType.setTable('EventType')
        self.cmbAmbCardCureEventType.setTable('EventType')
        self.cmbAmbCardMiscEventType.setTable('EventType')
        self.cmbAmbCardAnalysesEventType.setTable('EventType')

        self.tabAmbCardContent.setCurrentIndex(0)
        self.btnAmbCardPrint.setMenu(self.mnuAmbCardPrintEvents)

        self.on_cmdAmbCardDiagnosticsButtonBox_reset()
        self.on_cmdAmbCardStatusButtonBox_reset()
        self.on_cmdAmbCardDiagnosticButtonBox_reset()
        self.on_cmdAmbCardCureButtonBox_reset()
        self.on_cmdAmbCardMiscButtonBox_reset()
        self.on_cmdAmbCardAnalysesButtonBox_reset()

        self.tblFiles.createPopupMenu([self.actAmbCardUploadFile,
                                          self.actAmbCardDeleteFile,
                                          '-',
                                          self.actAmbCardOpenFile,
                                          '-',
                                          self.actAmbCardDownloadFile
                                          ])

        self.btnShowSnapshots.setVisible(False)     # После инициализации активна первая вкладка. На ней кнопки быть не должно.
        self.btnCheckSurvey.setVisible(False)     # После инициализации активна первая вкладка. На ней кнопки быть не должно.
        self.btnCheckSurvey.setEnabled(False)
        self.connect(QtGui.qApp, QtCore.SIGNAL('currentClientIdChanged()'), self.resetModelFiles)

        self.tblAmbCardStatusActions.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblAmbCardDiagnosticActions.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblAmbCardCureActions.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblAmbCardMiscActions.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tblAmbCardAnalysesActions.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

    def prepareActionTable(self, tbl, *actions):
        tbl.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        tbl.model().setReadOnly(True)
        tbl.addPopupCopyCell()
        tbl.addPopupSeparator()
        for action in actions:
            if action == '-':
                tbl.addPopupSeparator()
            else:
                tbl.addPopupAction(action)

    def updateAmbCardDiagnostics(self, filter):
        """
            в соответствии с фильтром обновляет список Diagnostics на вкладке AmbCard/Diagnostics.
        """
        self.__ambCardDiagnosticsFilter = filter
        db = QtGui.qApp.db
        tableDiagnostic = db.table('Diagnostic')
        queryTable = tableDiagnostic
        tableEvent = db.table('Event')
        queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableDiagnostic['event_id']))
        cond = [tableDiagnostic['deleted'].eq(0),
                tableEvent['deleted'].eq(0),
                tableEvent['client_id'].eq(self.currentClientId())]
        begDate = filter.get('begDate', None)
        if begDate:
            cond.append(tableDiagnostic['endDate'].ge(begDate))
        endDate = filter.get('endDate', None)
        if endDate:
            cond.append(tableDiagnostic['endDate'].le(endDate))
        eventPurposeId = filter.get('eventPurposeId', None)
        if eventPurposeId:
            tableEventType = db.table('EventType')
            queryTable = queryTable.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
            cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
        specialityId = filter.get('specialityId', None)
        if specialityId:
            cond.append(tableDiagnostic['speciality_id'].eq(specialityId))
        personId = filter.get('personId', None)
        if personId:
            cond.append(tableDiagnostic['person_id'].eq(personId))
        orgStructureId = filter.get('orgStructureId', None)
        if orgStructureId:
            tablePerson = db.table('Person')
            queryTable = queryTable.innerJoin(tablePerson, tablePerson['id'].eq(tableEvent['execPerson_id']))
            cond.append(tablePerson['orgStructure_id'].inlist(db.getDescendants('OrgStructure', 'parent_id', orgStructureId)))
        tableDiagnosisType = db.table('rbDiagnosisType')
        queryTable = queryTable.leftJoin(tableDiagnosisType, tableDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']))
        #cond.append(tableDiagnosisType['code'].inlist(['1', '2', '4']))
        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            idList = db.getIdList(queryTable,
                           tableDiagnostic['id'].name(),
                           cond,
                           ['endDate DESC', 'id'])
            self.tblAmbCardDiagnostics.setIdList(idList, None)
        finally:
            QtGui.QApplication.restoreOverrideCursor()

    def focusAmbCardDiagnostics(self):
        self.tblAmbCardDiagnostics.setFocus(QtCore.Qt.TabFocusReason)

    def updateAmbCardDiagnosticsInfo(self): # обновить таблички внизу AmbCardDiagnostic
        diagnosticId = self.tblAmbCardDiagnostics.currentItemId()
        if diagnosticId:
            eventId = forceRef(QtGui.qApp.db.translate('Diagnostic', 'id', diagnosticId, 'event_id'))
        else:
            eventId = None
        pageIndex = self.tabAmbCardDiagnosticDetails.currentIndex()
        if pageIndex == 0:
            self.updateAmbCardDiagnosticsEvent(eventId, diagnosticId)
        elif pageIndex == 1:
            self.updateAmbCardDiagnosticsVisits(eventId)
        elif pageIndex == 2:
            self.updateAmbCardDiagnosticsAccompDiagnostics(eventId, diagnosticId)
        elif pageIndex == 3:
            self.updateAmbCardDiagnosticsActions(eventId)

    def updateAmbCardDiagnosticsEvent(self, eventId, diagnosticId):
        db = QtGui.qApp.db
        if eventId:
            stmt = 'SELECT Event.externalId AS externalId, '\
                   'EventType.name AS eventTypeName, ' \
                   'Organisation.shortName AS orgName, ' \
                   'P1.name AS setPersonName, Event.setDate, ' \
                   'P2.name AS execPersonName, Event.execDate, ' \
                   'Event.isPrimary, Event.order, Event.nextEventDate, Event.nextEventDate, Event.payStatus, ' \
                   'rbResult.name AS result ' \
                   'FROM Event ' \
                   'LEFT JOIN EventType    ON EventType.id = Event.eventType_id ' \
                   'LEFT JOIN Organisation ON Organisation.id = Event.org_id ' \
                   'LEFT JOIN vrbPersonWithSpeciality AS P1 ON P1.id = Event.setPerson_id ' \
                   'LEFT JOIN vrbPersonWithSpeciality AS P2 ON P2.id = Event.execPerson_id ' \
                   'LEFT JOIN rbResult     ON rbResult.id = Event.result_id ' \
                   'WHERE Event.id=%d' % eventId
            query = db.query(stmt)
            if query.first():
                record=query.record()
            else:
                record=QtSql.QSqlRecord()
        else:
            record=QtSql.QSqlRecord()
        if diagnosticId:
            stmt = 'SELECT createPerson.name AS createName,  modifyPerson.name AS modityName, ' \
                   'Diagnosis.MKB, Diagnosis.MKBEx ' \
                   'FROM '\
                   'Diagnostic '\
                   'LEFT JOIN vrbPersonWithSpeciality AS createPerson ON createPerson.id = Diagnostic.createPerson_id '\
                   'LEFT JOIN vrbPersonWithSpeciality AS modifyPerson ON modifyPerson.id = Diagnostic.modifyPerson_id '\
                   'LEFT JOIN Diagnosis ON Diagnosis.id = Diagnostic.diagnosis_id '\
                   'WHERE Diagnostic.id=%d' % diagnosticId
            query = db.query(stmt)
            if query.first():
                diagnosticRecord=query.record()
            else:
                diagnosticRecord=QtSql.QSqlRecord()
        else:
            diagnosticRecord=QtSql.QSqlRecord()

        self.lblAmbCardEventExtIdValue.setText(forceString(record.value('externalId')))
        self.lblAmbCardEventTypeValue.setText(forceString(record.value('eventTypeName')))
        self.lblAmbCardEventOrgValue.setText(forceString(record.value('orgName')))
        self.lblAmbCardEventSetPersonValue.setText(forceString(record.value('setPersonName')))
        self.lblAmbCardEventSetDateValue.setText(forceString(record.value('setDate')))
        self.lblAmbCardEventExecPersonValue.setText(forceString(record.value('execPersonName')))
        self.lblAmbCardEventExecDateValue.setText(forceString(record.value('execDate')))
        self.lblAmbCardEventOrderValue.setText(EventOrder.getName(forceInt(record.value('order'))))
        self.chkAmbCardEventPrimary.setChecked(forceInt(record.value('isPrimary'))==1)

        self.lblAmbCardEventCreatePersonValue.setText(forceString(diagnosticRecord.value('createName')))
        self.lblAmbCardEventModifyPersonValue.setText(forceString(diagnosticRecord.value('modifyName')))
        MKB = forceString(diagnosticRecord.value('MKB'))
        self.lblAmbCardEventDiagValue.setText(MKB)
        self.lblAmbCardEventDiagName.setText(getMKBName(MKB) if MKB else '')
        MKBEx = forceString(diagnosticRecord.value('MKBEx'))
        self.lblAmbCardEventDiagExValue.setText(MKBEx)
        self.lblAmbCardEventDiagExName.setText(getMKBName(MKBEx) if MKBEx else '')

        self.lblAmbCardEventNextDateValue.setText(forceString(forceDate(record.value('nextEventDate'))))
        self.lblAmbCardEventResultValue.setText(forceString(record.value('result')))
        self.lblAmbCardEventPayStatusValue.setText(payStatusText(forceInt(record.value('payStatus'))))

    def updateAmbCardDiagnosticsVisits(self, eventId):
        if eventId:
            db = QtGui.qApp.db
            table = db.table('Visit')
            try:
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                idList = db.getIdList(table,
                                      table['id'].name(),
                                      [table['event_id'].eq(eventId), table['deleted'].eq(0)],
                                      ['date', 'id'])
            finally:
                QtGui.QApplication.restoreOverrideCursor()
        else:
            idList = []
        self.tblAmbCardDiagnosticsVisits.setIdList(idList, None)

    def updateAmbCardDiagnosticsAccompDiagnostics(self, eventId, diagnosticId):
        if eventId:
            db = QtGui.qApp.db
            table = db.table('Diagnostic')
            specialityId = db.translate(table, 'id', diagnosticId, 'speciality_id')
            tableDiagnosisType = db.table('rbDiagnosisType')
            queryTable = table.leftJoin(tableDiagnosisType, tableDiagnosisType['id'].eq(table['diagnosisType_id']))
            cond = [table['event_id'].eq(eventId),
                    table['deleted'].eq(0),
                    table['speciality_id'].eq(specialityId),
                    tableDiagnosisType['code'].notInlist(['1', '2', '4'])]
            try:
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                idList = db.getIdList(queryTable, table['id'], cond, ['endDate', 'id'])
            finally:
                QtGui.QApplication.restoreOverrideCursor()
        else:
            idList = []
        self.tblAmbCardDiagnosticsAccompDiagnostics.setIdList(idList, None)

    def updateAmbCardDiagnosticsActions(self, eventId):
        if eventId:
            db = QtGui.qApp.db
            table = db.table('Action')
            try:
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                idList = db.getIdList(table,
                                      table['id'].name(),
                                      [table['event_id'].eq(eventId),
                                       table['deleted'].eq(0),
                                       table['status'].ne(ActionStatus.WithoutResult)
                                      ],
                                      ['endDate DESC', 'id'])
            finally:
                QtGui.QApplication.restoreOverrideCursor()
        else:
            idList = []
        self.tblAmbCardDiagnosticsActions.setIdList(idList, None)

    def resetAmbCardFilter(self, edtBegDate, edtEndDate, cmbGroup, edtOffice, cmbOrgStructure):
        edtBegDate.setDate(QtCore.QDate())
        edtEndDate.setDate(QtCore.QDate())
        cmbGroup.setValue(None)
        edtOffice.setText('')
        cmbOrgStructure.setValue(None)

    def getAmbCardFilter(self, edtBegDate, edtEndDate, cmbGroup, edtOffice, cmbOrgStructure, cmbEventType):
        ambCardFilter = {
            'begDate'           : edtBegDate.date(),
            'endDate'           : edtEndDate.date(),
            'actionGroupId'     : cmbGroup.value(),
            'office'            : forceString(edtOffice.text()),
            'orgStructureId'    : cmbOrgStructure.value(),
            'eventTypeList'     : cmbEventType.getValue()
                         }
        return ambCardFilter

    def selectAmbCardActions(self, filter, classCode):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        queryTable = tableAction
        tableEvent = db.table('Event')
        tableEventType = db.table('EventType')
        queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        tableActionType = db.table('ActionType')
        queryTable = queryTable.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        cond = [tableAction['deleted'].eq(0),
                tableAction['status'].ne(ActionStatus.WithoutResult),
                tableEvent['deleted'].eq(0),
                tableEvent['client_id'].eq(self.currentClientId()),
                tableActionType['class'].eq(classCode),
                tableEventType['code'].ne('queue'),
                tableActionType['flatCode'].notInlist(['parodentInsp', 'dentitionInspection', 'temperatureSheet'])
                ]
        begDate = filter.get('begDate', None)
        if begDate and not begDate.isNull():
            cond.append(tableAction['endDate'].ge(begDate))
        endDate = filter.get('endDate', None)
        if endDate and not endDate.isNull():
            cond.append(tableAction['endDate'].le(endDate))
        actionGroupId = filter['actionGroupId']
        if actionGroupId:
            cond.append(tableAction['actionType_id'].inlist(getActionTypeDescendants(actionGroupId, classCode)))
        office = filter.get('office', '')
        if office:
            cond.append(tableAction['office'].like(office))
        orgStructureId = filter['orgStructureId']
        if orgStructureId:
            cond.append(tableAction['person_id'].inlist(getOrgStructurePersonIdList(orgStructureId)))
        eventTypeList = filter['eventTypeList']
        if eventTypeList:
            cond.append(tableEventType['id'].inlist(eventTypeList))
        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            return db.getIdList(queryTable,
                   tableAction['id'].name(),
                   cond,
                   ['endDate DESC', 'id'])
        finally:
            QtGui.QApplication.restoreOverrideCursor()

    def updateAmbCardStatus(self, filter):
        """
            в соответствии с фильтром обновляет список Actions на вкладке AmbCard/Status.
        """
        self.__ambCardStatusFilter = filter
        self.tblAmbCardStatusActions.setIdList(self.selectAmbCardActions(filter, 0), None)

    def focusAmbCardStatusActions(self):
        self.tblAmbCardStatusActions.setFocus(QtCore.Qt.TabFocusReason)

    def updateAmbCardDiagnostic(self, filter):
        """
            в соответствии с фильтром обновляет список Actions на вкладке AmbCard/Diagnostic.
        """
        self.__ambCardDiagnosticFilter = filter
        self.tblAmbCardDiagnosticActions.setIdList(self.selectAmbCardActions(filter, 1), None)

    def focusAmbCardDiagnosticActions(self):
        self.tblAmbCardDiagnosticActions.setFocus(QtCore.Qt.TabFocusReason)

    def updateAmbCardCure(self, filter):
        """
            в соответствии с фильтром обновляет список Actions на вкладке AmbCard/Cure.
        """
        self.__ambCardCureFilter = filter
        self.tblAmbCardCureActions.setIdList(self.selectAmbCardActions(filter, 2), None)

    def focusAmbCardCureActions(self):
        self.tblAmbCardCureActions.setFocus(QtCore.Qt.TabFocusReason)

    def updateAmbCardMisc(self, filter):
        """
            в соответствии с фильтром обновляет список Actions на вкладке AmbCard/Misc.
        """
        self.__ambCardMiscFilter = filter
        self.tblAmbCardMiscActions.setIdList(self.selectAmbCardActions(filter, 3), None)

    def focusAmbCardMiscActions(self):
        self.tblAmbCardMiscActions.setFocus(QtCore.Qt.TabFocusReason)

    def updateAmbCardAnalyses(self, filter):
        """
            в соответствии с фильтром обновляет список Actions на вкладке AmbCard/Analyses.
        """
        self.__ambCardAnalysesFilter = filter
        self.tblAmbCardAnalysesActions.setIdList(self.selectAmbCardActions(filter, 4), None)

    def focusAmbCardAnalysesActions(self):
        self.tblAmbCardAnalysesActions.setFocus(QtCore.Qt.TabFocusReason)

#### AmbCard page: Diagnostics page ##############

    @QtCore.pyqtSlot(int)
    def on_cmbAmbCardDiagnosticsSpeciality_currentIndexChanged(self, index):
        self.cmbAmbCardDiagnosticsPerson.setSpecialityId(self.cmbAmbCardDiagnosticsSpeciality.value())

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_cmdAmbCardDiagnosticsButtonBox_clicked(self, button):
        buttonCode = self.cmdAmbCardDiagnosticsButtonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_cmdAmbCardDiagnosticsButtonBox_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_cmdAmbCardDiagnosticsButtonBox_reset()

    def on_cmdAmbCardDiagnosticsButtonBox_reset(self):
        self.edtAmbCardDiagnosticsBegDate.setDate(QtCore.QDate())
        self.edtAmbCardDiagnosticsEndDate.setDate(QtCore.QDate())
        self.cmbAmbCardDiagnosticsPurpose.setValue(None)
        self.cmbAmbCardDiagnosticsSpeciality.setValue(None)
        self.cmbAmbCardDiagnosticsPerson.setValue(None)
        self.cmbAmbOrgStructure.setValue(None)

    def on_cmdAmbCardDiagnosticsButtonBox_apply(self):
        filter = {}
        filter['begDate'] = self.edtAmbCardDiagnosticsBegDate.date()
        filter['endDate'] = self.edtAmbCardDiagnosticsEndDate.date()
        filter['eventPurposeId'] = self.cmbAmbCardDiagnosticsPurpose.value()
        filter['specialityId'] = self.cmbAmbCardDiagnosticsSpeciality.value()
        filter['personId'] = self.cmbAmbCardDiagnosticsPerson.value()
        filter['orgStructureId'] = self.cmbAmbOrgStructure.value()
        self.updateAmbCardDiagnostics(filter)
        self.focusAmbCardDiagnostics()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelAmbCardDiagnostics_currentRowChanged(self, current, previous):
        self.updateAmbCardDiagnosticsInfo()

    @QtCore.pyqtSlot(int)
    def on_tabAmbCardDiagnosticDetails_currentChanged(self, index):
        self.updateAmbCardDiagnosticsInfo()

    def updateAmbCardPropertiesTable(self, index, tbl):
        row = index.row()
        record = index.model().getRecordByRow(row) if row >= 0 else None
        action = None
        if record:
            action = CAction(record=record)
            actionType = action.getType()
            setActionPropertiesColumnVisible(actionType, tbl)
            tbl.model().setAction2(action, self.currentClientId())
            tbl.resizeRowsToContents()
        else:
            tbl.model().setAction2(None, None)

    def updateAmbCardPrintActionAction(self, index):
        row = index.row()
        record = index.model().getRecordByRow(row) if row >= 0 else None
        actionTypeId = forceRef(record.value('actionType_id')) if record else None
        actionType = CActionTypeCache.getById(actionTypeId) if actionTypeId else None
        context = actionType.context if actionType else None
        self.actAmbCardPrintAction.setContext(context, False)

    @QtCore.pyqtSlot()
    def on_btnShowSnapshots_clicked(self):
        postfix = '?action_id=%s' % self.tblAmbCardDiagnosticActions.currentItemId()
        openInDicomViewer(postfix)

    @QtCore.pyqtSlot()
    def on_btnCheckSurvey_clicked(self):
        db = QtGui.qApp.db
        actionId = self.tblAmbCardDiagnosticActions.currentItemId()
        record = db.getRecord('Action', '*', actionId)
        url = forceString(QtGui.qApp.preferences.appPrefs.get('LISAddress', ''))
        if not url:
            QtGui.QMessageBox.warning(None, u'Внимание!', u'Для просмотра исследования необходимо указать в настройках адрес сервера ЛИС.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            return
        takenTissueJournalId = forceRef(record.value('takenTissueJournal_id'))
        if takenTissueJournalId:
            record = db.getRecord('TakenTissueJournal', 'externalId', takenTissueJournalId)
            externalId = forceString(record.value('externalId'))
        else:
            externalId = None

        if not externalId:
            context = CInfoContext()
            actionInfo = context.getInstance(CActionInfo, actionId)
            clientInfo = actionInfo.event.client
            postfix = '?search=%s&bdate=%s' % (clientInfo.fullName, clientInfo.birthDate.toString('yyyy-MM-dd'))
        else:
            postfix = '?module=search&sid=%s' % externalId

        browserPath = forceString(QtGui.qApp.preferences.appPrefs.get('browserPath', ''))
        openURLinBrowser(url + postfix, browserPath)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelAmbCardDiagnosticsActions_currentRowChanged(self, current, previous):
        self.updateAmbCardPrintActionAction(current)

    @QtCore.pyqtSlot()
    def on_actDiagnosticsShowPropertyHistory_triggered(self):
        self.tblAmbCardDiagnosticsActionProperties.showHistory()

    @QtCore.pyqtSlot()
    def on_actDiagnosticsShowPropertiesHistory_triggered(self):
        self.tblAmbCardDiagnosticsActionProperties.showHistoryEx()

    @QtCore.pyqtSlot(int)
    def on_tabAmbCardContent_currentChanged(self, index):
        self.btnAmbCardPrint.setMenu(self.mnuAmbCardPrintEvents if index == 0 else self.mnuAmbCardPrintActions)
        self.btnAmbCardPrint.setEnabled(True if index != 6 else False)
        if index == 6:
            self.resetModelFiles()
        self.btnShowSnapshots.setVisible(index == 2 and QtGui.qApp.userHasRight('pictureViewAndFind'))
        self.btnCheckSurvey.setVisible(index == 2)

    @QtCore.pyqtSlot()
    def on_actAmbCardPrintEvents_triggered(self):
        filter = {'clientId':self.currentClientId()}
        if self.__ambCardDiagnosticsFilter:
            filter.update(self.__ambCardDiagnosticsFilter)
        CClientVisits(self).oneShot(filter)

    @QtCore.pyqtSlot(int)
    def on_actAmbCardPrintCaseHistory_printByTemplate(self, templateId):
        clientId = self.currentClientId()
        clientInfo = getClientInfo2(clientId)
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableDiagnostic = db.table('Diagnostic')
        table = tableEvent.leftJoin(tableDiagnostic, tableDiagnostic['event_id'].eq(tableEvent['id']))
        cond = tableDiagnostic['id'].inlist(self.modelAmbCardDiagnostics.idList())
        idList = db.getDistinctIdList(table, tableEvent['id'].name(), cond, [tableEvent['setDate'].name(), tableEvent['id'].name()])
        events = CLocEventInfoList(clientInfo.context, idList)
        diagnosises = CDiagnosisInfoList(clientInfo.context, clientId)
        getTempInvalidList = lambda begDate=None, endDate=None, types=None: CTempInvalidInfoList._get(clientInfo.context, clientId, begDate, endDate, types)
        data = {'client':clientInfo,
                'events':events,
                'diagnosises':diagnosises,
                'getTempInvalidList': getTempInvalidList,
                'tempInvalids':getTempInvalidList()}
        QtGui.qApp.call(self, applyTemplate, (self, templateId, data))

    @QtCore.pyqtSlot()
    def on_mnuAmbCardPrintActions_aboutToShow(self):
        index = self.tabAmbCardContent.currentIndex()
        if index:
            table = [self.tblAmbCardStatusActions,
                     self.tblAmbCardDiagnosticActions,
                     self.tblAmbCardCureActions,
                     self.tblAmbCardMiscActions,
                     self.tblAmbCardAnalysesActions,
                     ][index - 1]
            self.updateAmbCardPrintActionAction(table.currentIndex())

    @QtCore.pyqtSlot(int)
    def on_actAmbCardPrintAction_printByTemplate(self, templateId):
        index = self.tabAmbCardContent.currentIndex()
        if index:
            table = [self.tblAmbCardStatusActions,
                     self.tblAmbCardDiagnosticActions,
                     self.tblAmbCardCureActions,
                     self.tblAmbCardMiscActions,
                     self.tblAmbCardAnalysesActions,
                     ][index - 1]
            actionId = table.currentItemId()
            if actionId:
                eventId = forceRef(QtGui.qApp.db.translate('Action', 'id', actionId, 'event_id'))
                context = CInfoContext()
                eventInfo = context.getInstance(CEventInfo, eventId)
                eventActions = eventInfo.actions
                action = context.getInstance(CActionInfo, actionId)
                data = { 'event' : eventInfo,
                         'action': action,
                         'client': eventInfo.client,
                         'actions':eventActions,
                         'currentActionIndex': 0,
                         'tempInvalid': None
                       }
                QtGui.qApp.call(self, applyTemplate, (self, templateId, data))

    @QtCore.pyqtSlot()
    def on_actAmbCardPrintActions_triggered(self):
        index = self.tabAmbCardContent.currentIndex()
        if index:
            table, title = [(self.tblAmbCardStatusActions, u'статус'),
                            (self.tblAmbCardDiagnosticActions, u'диагностика'),
                            (self.tblAmbCardCureActions, u'лечение'),
                            (self.tblAmbCardMiscActions, u'прочие мероприятия'),
                            (self.tblAmbCardAnalysesActions, u'анализы')
                            ][index - 1]
            table.setReportHeader(u'Список мероприятий (%s) пациента' % title)
            table.setReportDescription(getClientBanner(self.currentClientId()))
            table.printContent()

    def on_actAmbCardPrintActionTemplate_triggered(self):
            index = self.tabAmbCardContent.currentIndex()
            if index:
                html, title = [(self._statusActionsHTML, u'статус'),
                                (self._diagnosticActionsHTML, u'диагностика'),
                                (self._cureActionsHTML, u'лечение'),
                                (self._miscActionsHTML, u'прочие мероприятия'),
                                (self._analysesActionsHTML, u'анализы'),
                                ][index - 1]
                view = CReportViewDialog(self)
                view.setWindowTitle(u'Просмотр Мед. карты')
                view.setText(html)
                view.exec_()

    @QtCore.pyqtSlot(int)
    def on_actAmbCardPrintActionsHistory_printByTemplate(self, templateId):
        index = self.tabAmbCardContent.currentIndex()
        if index:
            clientId = self.currentClientId()
            clientInfo = getClientInfo2(clientId)
            model = [self.modelAmbCardStatusActions,
                     self.modelAmbCardDiagnosticActions,
                     self.modelAmbCardCureActions,
                     self.modelAmbCardMiscActions,
                     self.modelAmbCardAnalysesActions,
                     ][index - 1]
            idList = model.idList()
            actions = CLocActionInfoList(clientInfo.context, idList, clientInfo.sexCode, clientInfo.ageTuple)
            diagnosises = CDiagnosisInfoList(clientInfo.context, clientId)
            getTempInvalidList = lambda begDate=None, endDate=None, types=None: CTempInvalidInfoList._get(clientInfo.context, clientId, begDate, endDate, types)
            data = {'client'            : clientInfo,
                    'actions'           : actions,
                    'diagnosises'       : diagnosises,
                    'getTempInvalidList': getTempInvalidList,
                    'tempInvalids'      : getTempInvalidList()}
            QtGui.qApp.call(self, applyTemplate, (self, templateId, data))

        #### AmbCard page: Status page ###################

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_cmdAmbCardStatusButtonBox_clicked(self, button):
        buttonCode = self.cmdAmbCardStatusButtonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_cmdAmbCardStatusButtonBox_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_cmdAmbCardStatusButtonBox_reset()

    def on_cmdAmbCardStatusButtonBox_reset(self):
        self.resetAmbCardFilter(self.edtAmbCardStatusBegDate,
                                self.edtAmbCardStatusEndDate,
                                self.cmbAmbCardStatusGroup,
                                self.edtAmbCardStatusOffice,
                                self.cmbAmbCardStatusOrgStructure
                                )

    def on_cmdAmbCardStatusButtonBox_apply(self):
        filter = self.getAmbCardFilter(
                        self.edtAmbCardStatusBegDate,
                        self.edtAmbCardStatusEndDate,
                        self.cmbAmbCardStatusGroup,
                        self.edtAmbCardStatusOffice,
                        self.cmbAmbCardStatusOrgStructure,
                        self.cmbAmbCardStatusEventType
                        )
        self.updateAmbCardStatus(filter)
        self.focusAmbCardStatusActions()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelAmbCardStatusActions_currentRowChanged(self, current, previous):
        self.updateAmbCardPrintActionAction(current)

    @staticmethod
    def getMedCardContent(actionsSet, model, contextName='medCard'):
        allContent = u''
        printTemplate = getFirstPrintTemplate(contextName)
        if printTemplate:
            template = getTemplate(printTemplate[1])
            for actIdx in actionsSet:
                action = CAction(record=model.getRecordByRow(actIdx))
                actionInfo = CActionInfo(CInfoContext(), forceRef(action._record.value('id')))
                data = {'action': actionInfo}
                content, _ = compileAndExecTemplate(template[1], data)
                allContent += (content + u'<br>')
        return allContent

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelAmbCardStatusActions_selectionChanged(self, selected, deselected):
        model = selected.indexes()[0].model() if selected.indexes() else deselected.indexes()[0].model()
        self._statusActionsSet = self._statusActionsSet.union(
            set([r.row() for r in selected.indexes()])).difference(
            set([r.row() for r in deselected.indexes()]))
        allContent = self.getMedCardContent(self._statusActionsSet, model)
        self.txtAmbCardStatusBrowser.setHtml(allContent)
        self._statusActionsHTML = allContent

    @QtCore.pyqtSlot()
    def on_actStatusShowPropertyHistory_triggered(self):
        self.tblAmbCardStatusActionProperties.showHistory()

    @QtCore.pyqtSlot()
    def on_actStatusShowPropertiesHistory_triggered(self):
        self.tblAmbCardStatusActionProperties.showHistoryEx()

#### AmbCard page: Diagnostic page ###################

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_cmdAmbCardDiagnosticButtonBox_clicked(self, button):
        buttonCode = self.cmdAmbCardDiagnosticButtonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_cmdAmbCardDiagnosticButtonBox_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_cmdAmbCardDiagnosticButtonBox_reset()

    def on_cmdAmbCardDiagnosticButtonBox_reset(self):
        self.resetAmbCardFilter(self.edtAmbCardDiagnosticBegDate,
                                self.edtAmbCardDiagnosticEndDate,
                                self.cmbAmbCardDiagnosticGroup,
                                self.edtAmbCardDiagnosticOffice,
                                self.cmbAmbCardDiagnosticOrgStructure
                                )

    def on_cmdAmbCardDiagnosticButtonBox_apply(self):
        filter = self.getAmbCardFilter(
                        self.edtAmbCardDiagnosticBegDate,
                        self.edtAmbCardDiagnosticEndDate,
                        self.cmbAmbCardDiagnosticGroup,
                        self.edtAmbCardDiagnosticOffice,
                        self.cmbAmbCardDiagnosticOrgStructure,
                        self.cmbAmbCardDiagnosticEventType
                        )
        self.updateAmbCardDiagnostic(filter)
        self.focusAmbCardDiagnosticActions()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelAmbCardDiagnosticActions_currentRowChanged(self, current, previous):
        self.btnShowSnapshots.setEnabled(current.isValid())
        self.btnCheckSurvey.setEnabled(False)
        if current.isValid():
            db = QtGui.qApp.db
            actionId = self.tblAmbCardDiagnosticActions.currentItemId()
            context = CInfoContext()
            actionTypeId = context.getInstance(CActionInfo, actionId).typeId
            tissueType = db.getRecordEx('ActionType_TissueType', 'id', where='master_id=' + forceString(actionTypeId))
            self.btnCheckSurvey.setEnabled(tissueType is not None)

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelAmbCardDiagnosticActions_selectionChanged(self, selected, deselected):
        model = selected.indexes()[0].model() if selected.indexes() else deselected.indexes()[0].model()
        self._diagnosticActionsSet = self._diagnosticActionsSet.union(set([r.row() for r in selected.indexes()])).difference(
            set([r.row() for r in deselected.indexes()]))
        allContent = self.getMedCardContent(self._diagnosticActionsSet, model)
        self.txtAmbCardDiagnosticBrowser.setHtml(allContent)
        self._diagnosticActionsHTML = allContent

    @QtCore.pyqtSlot()
    def on_actDiagnosticShowPropertyHistory_triggered(self):
        self.tblAmbCardDiagnosticActionProperties.showHistory()

    @QtCore.pyqtSlot()
    def on_actDiagnosticShowPropertiesHistory_triggered(self):
        self.tblAmbCardDiagnosticActionProperties.showHistoryEx()

#### AmbCard page: Cure page ###################

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_cmdAmbCardCureButtonBox_clicked(self, button):
        buttonCode = self.cmdAmbCardCureButtonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_cmdAmbCardCureButtonBox_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_cmdAmbCardCureButtonBox_reset()

    def on_cmdAmbCardCureButtonBox_reset(self):
        self.resetAmbCardFilter(self.edtAmbCardCureBegDate,
                                self.edtAmbCardCureEndDate,
                                self.cmbAmbCardCureGroup,
                                self.edtAmbCardCureOffice,
                                self.cmbAmbCardCureOrgStructure
                                )

    def on_cmdAmbCardCureButtonBox_apply(self):
        filter = self.getAmbCardFilter(
                        self.edtAmbCardCureBegDate,
                        self.edtAmbCardCureEndDate,
                        self.cmbAmbCardCureGroup,
                        self.edtAmbCardCureOffice,
                        self.cmbAmbCardCureOrgStructure,
                        self.cmbAmbCardCureEventType
                        )
        self.updateAmbCardCure(filter)
        self.focusAmbCardCureActions()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelAmbCardCureActions_currentRowChanged(self, current, previous):
        self.updateAmbCardPrintActionAction(current)

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelAmbCardCureActions_selectionChanged(self, selected, deselected):
        model = selected.indexes()[0].model() if selected.indexes() else deselected.indexes()[0].model()
        self._cureActionsSet = self._cureActionsSet.union(
            set([r.row() for r in selected.indexes()])).difference(
            set([r.row() for r in deselected.indexes()]))
        allContent = self.getMedCardContent(self._cureActionsSet, model)
        self.txtAmbCardCureBrowser.setHtml(allContent)
        self._cureActionsHTML = allContent

    @QtCore.pyqtSlot()
    def on_actCureShowPropertyHistory_triggered(self):
        self.tblAmbCardCureActionProperties.showHistory()

    @QtCore.pyqtSlot()
    def on_actCureShowPropertiesHistory_triggered(self):
        self.tblAmbCardCureActionProperties.showHistoryEx()

#### AmbCard page: Misc page ###################

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_cmdAmbCardMiscButtonBox_clicked(self, button):
        buttonCode = self.cmdAmbCardMiscButtonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_cmdAmbCardMiscButtonBox_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_cmdAmbCardMiscButtonBox_reset()

    def on_cmdAmbCardMiscButtonBox_reset(self):
        self.resetAmbCardFilter(self.edtAmbCardMiscBegDate,
                                self.edtAmbCardMiscEndDate,
                                self.cmbAmbCardMiscGroup,
                                self.edtAmbCardMiscOffice,
                                self.cmbAmbCardMiscOrgStructure
                                )

    def on_cmdAmbCardMiscButtonBox_apply(self):
        filter = self.getAmbCardFilter(
                        self.edtAmbCardMiscBegDate,
                        self.edtAmbCardMiscEndDate,
                        self.cmbAmbCardMiscGroup,
                        self.edtAmbCardMiscOffice,
                        self.cmbAmbCardMiscOrgStructure,
                        self.cmbAmbCardMiscEventType
                        )
        self.updateAmbCardMisc(filter)
        self.focusAmbCardMiscActions()

    # AmbCard page: Analyses

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_cmdAmbCardAnalysesButtonBox_clicked(self, button):
        buttonCode = self.cmdAmbCardAnalysesButtonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.on_cmdAmbCardAnalysesButtonBox_apply()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_cmdAmbCardAnalysesButtonBox_reset()

    def on_cmdAmbCardAnalysesButtonBox_reset(self):
        self.resetAmbCardFilter(self.edtAmbCardAnalysesBegDate,
                                self.edtAmbCardAnalysesEndDate,
                                self.cmbAmbCardAnalysesGroup,
                                self.edtAmbCardAnalysesOffice,
                                self.cmbAmbCardAnalysesOrgStructure
                                )

    def on_cmdAmbCardAnalysesButtonBox_apply(self):
        filter = self.getAmbCardFilter(
            self.edtAmbCardAnalysesBegDate,
            self.edtAmbCardAnalysesEndDate,
            self.cmbAmbCardAnalysesGroup,
            self.edtAmbCardAnalysesOffice,
            self.cmbAmbCardAnalysesOrgStructure,
            self.cmbAmbCardAnalysesEventType
        )
        self.updateAmbCardAnalyses(filter)
        self.focusAmbCardAnalysesActions()

    # @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    # def on_selectionModelAmbCardMiscActions_currentRowChanged(self, current, previous):
    #     pass

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelAmbCardMiscActions_selectionChanged(self, selected, deselected):
        model = selected.indexes()[0].model() if selected.indexes() else deselected.indexes()[0].model()
        self._miscActionsSet = self._miscActionsSet.union(
            set([r.row() for r in selected.indexes()])).difference(
            set([r.row() for r in deselected.indexes()]))
        allContent = self.getMedCardContent(self._miscActionsSet, model)
        self.txtAmbCardMiscBrowser.setHtml(allContent)
        self._miscActionsHTML = allContent

    @QtCore.pyqtSlot()
    def on_actMiscShowPropertyHistory_triggered(self):
        self.tblAmbCardMiscActionProperties.showHistory()

    @QtCore.pyqtSlot()
    def on_actMiscShowPropertiesHistory_triggered(self):
        self.tblAmbCardMiscActionProperties.showHistoryEx()

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelAmbCardAnalysesActions_selectionChanged(self, selected, deselected):
        model = selected.indexes()[0].model() if selected.indexes() else deselected.indexes()[0].model()
        self._analysesActionsSet = self._analysesActionsSet.union(
            set(r.row() for r in selected.indexes())).difference(
            set(r.row() for r in deselected.indexes()))
        allContent = self.getMedCardContent(self._analysesActionsSet, model, 'analyses')
        self.txtAmbCardAnalysesBrowser.setHtml(allContent)
        self._analysesActionsHTML = allContent

    @QtCore.pyqtSlot()
    def on_actAnalysesShowPropertyHistory_triggered(self):
        self.tblAmbCardAnalysesActionProperties.showHistory()

    @QtCore.pyqtSlot()
    def on_actAnalysesShowPropertiesHistory_triggered(self):
        self.tblAmbCardAnalysesActionProperties.showHistoryEx()

#### AmbCard page: Client files page ###################

    def resetModelFiles(self):
        self.modelAmbCardClientFiles.updateContents()
        self.tblFiles.selectRow(0)

        self._statusActionsSet = set()
        self._diagnosticActionsSet = set()
        self._cureActionsSet = set()
        self._miscActionsSet = set()
        self._analysesActionsSet = set()

        self._statusActionsHTML = u''
        self._diagnosticActionsHTML = u''
        self._cureActionsHTML = u''
        self._miscActionsHTML = u''
        self._analysesActionsHTML = u''

    def uploadFile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, u"Укажите файл с данными", '')

        if fileName != '':
            file_ = QtCore.QFile(fileName)
            fileInfo = QtCore.QFileInfo(fileName)
            simpleFileName = fileInfo.fileName()
            if not file_.open(QtCore.QIODevice.ReadOnly): return
            blob = file_.readAll()
            file_.close()
            db = QtGui.qApp.db
            table = db.table('ClientFile')
            record = table.newRecord()
            record.setValue('client_id', toVariant(QtGui.qApp.currentClientId()))
            record.setValue('name', simpleFileName)
            record.setValue('file', blob)
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            recordId = db.insertRecord(table, record)
            self.modelAmbCardClientFiles.updateContents()
            index = self.modelAmbCardClientFiles.findItemIdIndex(recordId)
            self.tblFiles.selectRow(index)
            QtGui.qApp.restoreOverrideCursor()

    def deleteFile(self):
        index = self.tblFiles.currentIndex()
        self.modelAmbCardClientFiles.removeRow(index.row(), index)
        self.modelAmbCardClientFiles.reset()
        if not self.tblFiles.selectedIndexes():
            self.tblFiles.selectRow(0)

    def downloadFile(self):
        dir = QtCore.QDir.toNativeSeparators(QtGui.QFileDialog.getExistingDirectory(self,
                u'Выберите директорию для сохранения файла',
                 '',
                 QtGui.QFileDialog.ShowDirsOnly))

        if dir != '':
            index = self.tblFiles.currentIndex()
            row = index.row()
            itemId = self.modelAmbCardClientFiles.idList()[row]

            fileName = QtGui.qApp.db.translate('ClientFile', 'id', itemId, 'name')
            fullName = os.path.join(forceStringEx(dir),
                                    forceString(fileName))
            file_ = QtCore.QFile(fullName)
            if not file_.open(QtCore.QIODevice.WriteOnly): return
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            data = QtGui.qApp.db.translate('ClientFile', 'id', itemId, 'file')
            file_.write(data.toByteArray())
            file_.close()
            QtGui.qApp.restoreOverrideCursor()

    def openClientFile(self):
        dir = QtGui.qApp.getTmpDir('ClientFiles')
        index = self.tblFiles.currentIndex()
        row = index.row()
        itemId = self.modelAmbCardClientFiles.idList()[row]

        fileName = QtGui.qApp.db.translate('ClientFile', 'id', itemId, 'name')
        fullName = os.path.join(forceStringEx(dir),
                                forceString(fileName))
        file_ = QtCore.QFile(fullName)
        if not file_.open(QtCore.QIODevice.WriteOnly): return
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        data = QtGui.qApp.db.translate('ClientFile', 'id', itemId, 'file')
        file_.write(data.toByteArray())
        file_.close()
        QtGui.qApp.restoreOverrideCursor()
        if sys.platform == 'win32':
            os.startfile(fullName)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, fullName])

    @QtCore.pyqtSlot()
    def on_btnAddFile_clicked(self):
        self.uploadFile()

    @QtCore.pyqtSlot()
    def on_actAmbCardUploadFile_triggered(self):
        self.uploadFile()

    @QtCore.pyqtSlot()
    def on_btnDownloadFile_clicked(self):
        self.downloadFile()

    @QtCore.pyqtSlot()
    def on_actAmbCardDownloadFile_triggered(self):
        self.downloadFile()

    @QtCore.pyqtSlot()
    def on_btnOpenFile_clicked(self):
        self.openClientFile()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblFiles_doubleClicked(self, index):
        self.openClientFile()

    @QtCore.pyqtSlot()
    def on_actAmbCardOpenFile_triggered(self):
        self.openClientFile()

    @QtCore.pyqtSlot()
    def on_btnDeleteFile_clicked(self):
        self.deleteFile()

    @QtCore.pyqtSlot()
    def on_actAmbCardDeleteFile_triggered(self):
        self.deleteFile()
