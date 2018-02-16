# -*- coding: utf-8 -*-

import csv
from PyQt4 import QtCore, QtGui

from Exchange.R23.attach.AttachExchange import CR23AttachExchange
from Exchange.R23.attach.ClientAttachSyncDialog import CClientAttachSyncDialog
from Exchange.R23.attach.Service import CR23ClientAttachService, CR23PersonAttachService
from Exchange.R23.attach.Types import AttachInfo, AttachedClientInfo, DeAttachQuery, DocumentInfo, PersonAttachInfo, PolicyInfo
from Exchange.R23.attach.Utils import CAttachPolicyType, CAttachSentToTFOMS, CAttachType, CAttachedClientInfoSyncStatus, CAttachedInfoTable, CBookkeeperCode, \
    CClientAttachFound, CDeAttachReason, CDocumentType, CInsuranceArea, CPersonCategory, findClient, findClientAttach, getDeAttachQueryLogTable, insertAttachLog
from Orgs.Utils import getOrgStructureDescendants, getOrgStructureName, COrgStructureAreaInfo
from Orgs.ClientAttachReport import CAttachedClientsCountReport
from Registry.RegistryTable import CSNILSCol
from Ui_AttachExchangeDialog import Ui_AttachExchangeDialog
from Users.Rights import urAccessRefPersonPersonal, urAdmin, urRegTabWriteRegistry
from library.DialogBase import CDialogBase
from library.InDocTable import CBoolInDocTableCol, CDateInDocTableCol, CEnumInDocTableCol, CInDocTableCol, CRecordListModel
from library.TableModel import CBoolCol, CCol, CDateCol, CEnumCol, CNameCol, CTableModel, CTextCol
from library.Utils import CChunkProcessor, agreeNumberAndWord, forceBool, forceDate, forceInt, forceRef, forceString, formatSNILS, getPref, nameCase, setPref, \
    toVariant, formatSex
from library.database import CTableFilteredRecordCache, CTableRecordCache
from library.exception import CSynchronizeAttachException


class CAttachExchangeDialog(CDialogBase, Ui_AttachExchangeDialog):
    ProgressBarHeight = 36
    ProgressBarWidth = 440

    DeAttachQueryBegDateOffset = -4

    def __init__(self, parent=None):
        super(CAttachExchangeDialog, self).__init__(parent)
        self.attach = CR23AttachExchange(QtGui.qApp.db)
        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            self.preSetupUi()
            self.setupUi(self)
            self.postSetupUi()
        finally:
            QtGui.qApp.restoreOverrideCursor()
        self.setWindowTitle(u'Синхронизация с Web-сервисом «Регистр прикрепленного населения»')

    def preSetupUi(self):
        self.addModels('ClientAttach', CClientAttachModel(self))
        self.addModels('PersonAttach', CPersonAttachModel(self))
        self.addModels('AttachedClientInfo', CAttachedClientInfoModel(self))
        self.addModels('IncomeDeAttachQuery', CIncomeDeAttachQueryModel(self))
        self.addModels('OutcomeDeAttachQuery', COutcomeDeAttachQueryModel(self))

        self.actClientAttachOpenCard = QtGui.QAction(u'Открыть рег. карту', self)
        self.actClientAttachOpenCard.setObjectName('actClientAttachOpenCard')
        self.actAttachedClientInfoOpenCard = QtGui.QAction(u'Открыть рег. карту', self)
        self.actAttachedClientInfoOpenCard.setObjectName('actAttachedClientInfoOpenCard')
        self.actIncomeDeAttachQueryOpenCard = QtGui.QAction(u'Открыть рег. карту', self)
        self.actIncomeDeAttachQueryOpenCard.setObjectName('actIncomeDeAttachQueryOpenCard')
        self.actOutcomeDeAttachQueryOpenCard = QtGui.QAction(u'Открыть рег. карту', self)
        self.actOutcomeDeAttachQueryOpenCard.setObjectName('actOutcomeDeAttachQueryOpenCard')
        self.actPersonAttachOpenCard = QtGui.QAction(u'Открыть карту сотрудника', self)
        self.actPersonAttachOpenCard.setObjectName('actPersonAttachOpenCard')

        self.mnuClientAttach = QtGui.QMenu(self)
        self.mnuClientAttach.setObjectName('mnuClientAttach')
        self.mnuClientAttach.addAction(self.actClientAttachOpenCard)

        self.mnuPersonAttach = QtGui.QMenu(self)
        self.mnuPersonAttach.setObjectName('mnuPersonAttach')
        self.mnuPersonAttach.addAction(self.actPersonAttachOpenCard)

        self.mnuAttachedClientInfo = QtGui.QMenu(self)
        self.mnuAttachedClientInfo.setObjectName('mnuAttachedClientInfo')
        self.mnuAttachedClientInfo.addAction(self.actAttachedClientInfoOpenCard)

        self.mnuIncomeDeAttachQuery = QtGui.QMenu(self)
        self.mnuIncomeDeAttachQuery.setObjectName('mnuIncomeDeAttachQuery')
        self.mnuIncomeDeAttachQuery.addAction(self.actIncomeDeAttachQueryOpenCard)

        self.mnuOutcomeDeAttachQuery = QtGui.QMenu(self)
        self.mnuOutcomeDeAttachQuery.setObjectName('mnuOutcomeDeAttachQuery')
        self.mnuOutcomeDeAttachQuery.addAction(self.actOutcomeDeAttachQueryOpenCard)

    def postSetupUi(self):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        curDate = QtCore.QDate.currentDate()
        orgId = QtGui.qApp.currentOrgId()
        orgStructureId = QtGui.qApp.currentOrgStructureId()

        # tabMonitoring
        self.cmbMovingFromOrgStructure.model().setFilter(self.clientAttachMonitoring.getOrgStructureSectionFilter())
        self.cmbMovingToOrgStructure.model().setFilter(self.clientAttachMonitoring.getOrgStructureSectionFilter())
        self.btnMoveAttaches.clicked.connect(self.moveAttaches)
        self.btnPrintReport.clicked.connect(self.printReport)

        # tabClientAttach
        self.setModels(self.tblClientAttach, self.modelClientAttach, self.selectionModelClientAttach)
        self.tblClientAttach.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblClientAttach.setPopupMenu(self.mnuClientAttach)

        self.cmbOrgStructureClientAttach.setOrgId(orgId)
        self.cmbOrgStructureClientAttach.setValue(orgStructureId)
        self.edtBegDateClientAttach.setDate(curDate.addMonths(-1))
        self.edtEndDateClientAttach.setDate(curDate)

        self.cmbAttachTypeClientAttach.setEnum(CAttachType)
        self.cmbInsuranceAreaClientAttach.setEnum(CInsuranceArea)

        # # tabPersonAttach
        self.setModels(self.tblPersonAttach, self.modelPersonAttach, self.selectionModelPersonAttach)
        self.tblPersonAttach.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblPersonAttach.setPopupMenu(self.mnuPersonAttach)

        self.cmbOrgStructurePersonAttach.setOrgId(orgId)
        self.cmbOrgStructurePersonAttach.setValue(orgStructureId)
        self.edtBegDatePersonAttach.setDate(curDate.addMonths(-1))
        self.edtEndDatePersonAttach.setDate(curDate)

        # tabSync
        self.setModels(self.tblAttachedClientInfo, self.modelAttachedClientInfo, self.selectionModelAttachedClientInfo)
        self.tblAttachedClientInfo.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblAttachedClientInfo.setPopupMenu(self.mnuAttachedClientInfo)

        self.cmbOrgStructureSync.setOrgId(orgId)
        self.cmbOrgStructureSync.setValue(orgStructureId)
        self.edtBegDateFromSync.setDate(curDate.addMonths(-1))
        self.edtBegDateToSync.setDate(curDate)
        self.edtEndDateFromSync.setDate(curDate.addMonths(-1))
        self.edtEndDateToSync.setDate(curDate)
        self.cmbAttachTypeSync.setEnum(CAttachType)
        self.cmbAttachSyncStatus.setEnum(CAttachedClientInfoSyncStatus)
        self.cmbClientFound.setEnum(CClientAttachFound)
        self.cmbClientAttachFound.setEnum(CClientAttachFound)
        self.btnLoadAttachedTFOMS.setToolTip(u'Загрузка данных из ТФОМС доступна с 20:00')
        self.btnImportAttachedClientInfo.setToolTip(u'При обработке данных будет добавляться или обновляться информация по прикреплению пациентов.\n'
                                                    u'Если пациента в базе данных нет, то в столбце "Найден в БД" не будет проставлена галочка.')

        # tabDeAttachLog.tabGetDeAttach
        self.setModels(self.tblIncomeDeAttachQuery, self.modelIncomeDeAttachQuery, self.selectionModelIncomeDeAttachQuery)
        self.tblIncomeDeAttachQuery.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblIncomeDeAttachQuery.setPopupMenu(self.mnuIncomeDeAttachQuery)

        self.edtQueryDeAttachDate.setDate(curDate)
        self.edtQueryDeAttachDate.setMinimumDate(curDate.addDays(self.DeAttachQueryBegDateOffset))
        self.edtQueryDeAttachDate.setMaximumDate(curDate)

        # tabDeAttachLog.tabSendDeAttach
        self.setModels(self.tblOutcomeDeAttachQuery, self.modelOutcomeDeAttachQuery, self.selectionModelOutcomeDeAttachQuery)
        self.tblOutcomeDeAttachQuery.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblOutcomeDeAttachQuery.setPopupMenu(self.mnuOutcomeDeAttachQuery)

        self.edtQueryNumFrom.setValidator(QtGui.QIntValidator(0, 10 ** 8, self))
        self.edtQueryNumTo.setValidator(QtGui.QIntValidator(0, 10 ** 8, self))

        self.edtQueryDateFrom.setDate(curDate.addDays(-1))
        self.edtQueryDateTo.setDate(curDate)

    def loadPreferences(self, preferences):
        self.tblClientAttach.loadPreferences(getPref(preferences, 'tblClientAttach', {}))
        self.tblPersonAttach.loadPreferences(getPref(preferences, 'tblPersonAttach', {}))
        self.tblAttachedClientInfo.loadPreferences(getPref(preferences, 'tblAttachedClientInfo', {}))
        self.tblIncomeDeAttachQuery.loadPreferences(getPref(preferences, 'tblIncomeDeAttachQuery', {}))
        self.tblOutcomeDeAttachQuery.loadPreferences(getPref(preferences, 'tblOutcomeDeAttachQuery', {}))
        return CDialogBase.loadPreferences(self, preferences)

    def savePreferences(self):
        result = CDialogBase.savePreferences(self)
        setPref(result, 'tblClientAttach', self.tblClientAttach.savePreferences())
        setPref(result, 'tblPersonAttach', self.tblPersonAttach.savePreferences())
        setPref(result, 'tblAttachedClientInfo', self.tblAttachedClientInfo.savePreferences())
        setPref(result, 'tblIncomeDeAttachQuery', self.tblIncomeDeAttachQuery.savePreferences())
        setPref(result, 'tblOutcomeDeAttachQuery', self.tblOutcomeDeAttachQuery.savePreferences())
        return result

    def openAmbCardAttachTab(self, clientId):
        if QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]):
            from Registry.ClientEditDialog import CClientEditDialog
            dialog = CClientEditDialog(self)
            dialog.load(clientId)
            dialog.tabWidget.setCurrentWidget(dialog.tabAttach)
            dialog.exec_()

    def openPersonCardAttachTab(self, personId):
        if QtGui.qApp.userHasAnyRight([urAdmin, urAccessRefPersonPersonal]):
            from RefBooks.Person import CRBPersonEditor
            dialog = CRBPersonEditor(self)
            dialog.load(personId)
            dialog.tabMain.setCurrentWidget(dialog.tabPersonAttach)
            dialog.exec_()

    def getProgressBar(self):
        pbWidth, pbHeight = CAttachExchangeDialog.ProgressBarWidth, CAttachExchangeDialog.ProgressBarHeight
        progressBar = QtGui.QProgressBar(self)
        progressBar.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        progressBar.setGeometry(self.geometry().center().x() - pbWidth / 2, (self.geometry().height() - pbHeight) / 2, pbWidth, pbHeight)
        return progressBar

    # tabMonitoring
    def moveAttaches(self):
        sex = self.cmbMovingSex.currentIndex()
        ageCategory = self.cmbMovingAge.currentIndex()
        orgStructureFrom = self.cmbMovingFromOrgStructure.value()
        orgStructureTo = self.cmbMovingToOrgStructure.value()
        count = self.edtMovingCount.value()

        if not ((orgStructureFrom is not None or self.checkInputMessage(u'участок-источник', False, self.cmbMovingFromOrgStructure))
                and (orgStructureTo is not None or self.checkInputMessage(u'участок-приемник', False, self.cmbMovingToOrgStructure))
                and (orgStructureFrom != orgStructureTo or self.checkValueMessage(u'выбран один и тот же участок', False, self.cmbMovingToOrgStructure))
                and (count > 0 or self.checkInputMessage(u'кол-во прикрепленных для переноса', False, self.edtMovingCount))):
            return

        msg = None
        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            clientIdList = self.attach.getAttachedToOrgStructure(orgStructureFrom, sex=sex, ageCategory=ageCategory, limit=count)
            if clientIdList:
                attachCount = len(clientIdList)
                attachesWord = agreeNumberAndWord(attachCount, (u'прикрепление', u'прикрепления', u'прикреплений'))
                self.attach.moveAttachesToOrgStructure(clientIdList, orgStructureTo)
                msg = u'{0} {1} перенесено с участка "{2}" на участок "{3}"\n'.format(attachCount, attachesWord,
                                                                                      getOrgStructureName(orgStructureFrom),
                                                                                      getOrgStructureName(orgStructureTo))
            else:
                msg = u'Не найдено прикреплений для переноса'
        except Exception as e:
            msg = unicode(e)
        finally:
            QtGui.qApp.restoreOverrideCursor()
            QtGui.QMessageBox.information(self, u'Перенос прикреплений', msg, QtGui.QMessageBox.Ok)

        self.clientAttachMonitoring.clearCache()
        self.clientAttachMonitoring.updateTable()

    def printReport(self):
        CAttachedClientsCountReport(self).exec_()

    # tabClientAttach
    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelClientAttach_selectionChanged(self, selected, deselected):
        self.refreshStatusClientAttach()

    def refreshStatusClientAttach(self):
        countSelected = len(self.selectionModelClientAttach.selectedRows())
        countTotal = self.modelClientAttach.rowCount()
        self.btnSyncClientAttach.setEnabled(countSelected > 0)
        self.lblStatusClientAttach.setText(u'Записей в таблице выделено/всего: %s/%s' % (countSelected, countTotal))

    @QtCore.pyqtSlot()
    def on_actClientAttachOpenCard_triggered(self):
        row = self.tblClientAttach.currentIndex().row()
        record = self.tblClientAttach.model().getRecordByRow(row)
        clientId = forceRef(record.value('clientId'))
        self.openAmbCardAttachTab(clientId)
        self.reloadClientAttachItems()

    @QtCore.pyqtSlot()
    def on_btnLoadClientAttach_clicked(self):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.reloadClientAttachItems()
        QtGui.qApp.restoreOverrideCursor()

    @QtCore.pyqtSlot()
    def on_btnSelectAllClientAttach_clicked(self):
        self.tblClientAttach.selectAll()

    @QtCore.pyqtSlot()
    def on_btnDeselectAllClientAttach_clicked(self):
        self.tblClientAttach.clearSelection()

    @QtCore.pyqtSlot()
    def on_btnSyncClientAttach_clicked(self):
        u""" Выполнить операции по прикреплению/откреплению для выбранного списка пациентов """
        changeSection = self.chkChangeSection.isChecked()
        attachesToSync = map(self.modelClientAttach.getClientAttachInfo,
                             self.tblClientAttach.selectionModel().selectedRows())
        if attachesToSync:
            try:
                QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                connection = CR23ClientAttachService.getConnection()
                syncedList, syncErrors, attachErrorMap = CR23AttachExchange.syncClientAttaches(connection, attachesToSync, changeSection)
            finally:
                QtGui.qApp.restoreOverrideCursor()

            if syncErrors:
                QtGui.QMessageBox.warning(self, u'Синхронизация прикрепления с ТФОМС',
                                          u'<br/>'.join([u'<b>Ошибка в передаче данных:</b>'] + [u'<i>%s</i>' % error for error in syncErrors]))
            elif attachErrorMap:
                errorCount = len(attachErrorMap)
                QtGui.QMessageBox.warning(self, u'Синхронизация прикрепления с ТФОМС',
                                          u'Ошибка в передаче данных (<b>{count}</b> {records}): см. <i>"Описание ошибки"</i>'.format(
                                              count=errorCount,
                                              records=agreeNumberAndWord(errorCount, [u'запись', u'записи', u'записей'])
                                          ))
            elif syncedList:
                QtGui.QMessageBox.information(self, u'Синхронизация прикрепления с ТФОМС', u'Данные переданы успешно')

            self.reloadClientAttachItems()

    @QtCore.pyqtSlot()
    def on_btnCloseClientAttach_clicked(self):
        self.close()

    def reloadClientAttachItems(self, order=None):
        orgStructureId = self.cmbOrgStructureClientAttach.value()
        attachType = self.cmbAttachTypeClientAttach.value()
        begDate = self.edtBegDateClientAttach.date()
        endDate = self.edtEndDateClientAttach.date()
        insuranceArea = self.cmbInsuranceAreaClientAttach.value()

        db = QtGui.qApp.db
        tableAttach = db.table('ClientAttach')
        tableAttachType = db.table('rbAttachType')
        tableClient = db.table('Client')
        tableClientPolicy = db.table('ClientPolicy')
        tableOrgStructure = db.table('OrgStructure')

        table = tableAttach.innerJoin(tableAttachType, [tableAttach['attachType_id'].eq(tableAttachType['id'])])
        table = table.innerJoin(tableClient, [tableClient['id'].eq(tableAttach['client_id']), tableClient['deleted'].eq(0)])
        table = table.leftJoin(tableOrgStructure, [tableOrgStructure['id'].eq(tableAttach['orgStructure_id']), tableOrgStructure['deleted'].eq(0)])

        cond = [
            tableOrgStructure['isArea'].inlist([COrgStructureAreaInfo.Therapeutic,
                                                COrgStructureAreaInfo.Pediatric,
                                                COrgStructureAreaInfo.GeneralPractice]),
            tableAttach['sentToTFOMS'].eq(CAttachSentToTFOMS.NotSynced),
            tableAttach['deleted'].eq(0)
        ]

        if attachType:
            cond.append(tableAttachType['code'].eq(attachType))

        if insuranceArea == CInsuranceArea.Krasnodar:
            table = table.innerJoin(tableClientPolicy, [tableClientPolicy['client_id'].eq(tableClient['id']),
                                                        tableClientPolicy['insuranceArea'].like('23%'),
                                                        tableClientPolicy['deleted'].eq(0)])
        elif insuranceArea == CInsuranceArea.NonKrasnodar:
            table = table.innerJoin(tableClientPolicy, tableClientPolicy['id'].eq(db.func.getClientPolicyId(tableClient['id'], 1)))
            cond.extend([
                tableClientPolicy['insuranceArea'].ne(''),
                tableClientPolicy['insuranceArea'].notlike('23%')
            ])

        if orgStructureId:
            cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
        if self.chkBegDateClientAttach.isChecked():
            cond.append(tableAttach['begDate'].ge(begDate))
        if self.chkEndDateClientAttach.isChecked():
            cond.append(tableAttach['begDate'].le(endDate))

        attachIdList = db.getDistinctIdList(table, tableAttach['id'], cond, order=order)

        self.tblClientAttach.model().setIdList(attachIdList)
        self.refreshStatusClientAttach()

    # tabPersonAttach
    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelPersonAttach_selectionChanged(self, selected, deselected):
        self.refreshStatusPersonAttach()

    def refreshStatusPersonAttach(self):
        countSelected = len(self.selectionModelPersonAttach.selectedRows())
        countTotal = self.modelPersonAttach.rowCount()
        self.btnSyncPersonAttach.setEnabled(countSelected > 0)
        self.lblStatusPersonAttach.setText(u'Записей в таблице выделено/всего: %s/%s' % (countSelected, countTotal))

    @QtCore.pyqtSlot()
    def on_mnuPersonAttach_aboutToShow(self):
        row = self.tblPersonAttach.currentIndex().row()
        record = self.tblPersonAttach.model().getRecordByRow(row)
        personId = forceRef(record.value('personId')) if record is not None else None
        self.actPersonAttachOpenCard.setEnabled(personId is not None)

    @QtCore.pyqtSlot()
    def on_actPersonAttachOpenCard_triggered(self):
        row = self.tblPersonAttach.currentIndex().row()
        record = self.tblPersonAttach.model().getRecordByRow(row)
        personId = forceRef(record.value('personId')) if record is not None else None
        self.openPersonCardAttachTab(personId)
        self.reloadPersonAttachExportItems()

    @QtCore.pyqtSlot()
    def on_btnLoadPersonAttach_clicked(self):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.reloadPersonAttachExportItems()
        QtGui.qApp.restoreOverrideCursor()

    @QtCore.pyqtSlot()
    def on_btnSelectAllPersonAttach_clicked(self):
        self.tblPersonAttach.selectAll()

    @QtCore.pyqtSlot()
    def on_btnDeselectAllPersonAttach_clicked(self):
        self.tblPersonAttach.clearSelection()

    @QtCore.pyqtSlot()
    def on_btnSyncPersonAttach_clicked(self):
        u""" Выполнить операции по прикреплению/откреплению для выбранного списка сотрудников """
        attachesToSync = map(self.modelPersonAttach.getPersonAttachInfo,
                             self.tblPersonAttach.selectionModel().selectedRows())
        if attachesToSync:
            try:
                QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                connection = CR23PersonAttachService.getConnection()
                syncedList, syncErrors, attachErrorMap = CR23AttachExchange.syncPersonAttaches(connection, attachesToSync)
            finally:
                QtGui.qApp.restoreOverrideCursor()

            if syncErrors:
                errorMsg = u'<br/>'.join([u'<b>Ошибка в передаче данных:</b>'] +
                                         [u'<i>%s</i>' % error for error in syncErrors])
                QtGui.QMessageBox.warning(self, u'Синхронизация прикрепления с ТФОМС', errorMsg)
            elif attachErrorMap:
                errorCount = len(attachErrorMap)
                QtGui.QMessageBox.warning(self, u'Синхронизация прикрепления с ТФОМС',
                                          u'Ошибка в передаче данных (<b>{count}</b> {records}): см. <i>"Описание ошибки"</i>'.format(
                                              count=errorCount,
                                              records=agreeNumberAndWord(errorCount, [u'запись', u'записи', u'записей'])
                                          ))
            else:
                QtGui.QMessageBox.information(self, u'Синхронизация прикрепления с ТФОМС', u'Данные переданы успешно')

            self.reloadPersonAttachExportItems()

    @QtCore.pyqtSlot()
    def on_btnClosePersonAttach_clicked(self):
        self.close()

    def reloadPersonAttachExportItems(self):
        db = QtGui.qApp.db
        orgStructure = self.cmbOrgStructurePersonAttach.value()
        begDate = self.edtBegDatePersonAttach.date()
        endDate = self.edtEndDatePersonAttach.date()

        tableAttach = db.table('PersonAttach')
        tablePerson = db.table('Person')
        tableSpeciality = db.table('rbSpeciality')
        tableBookkeeperCode = db.table(CBookkeeperCode.getTableName()).alias('bkkeeper')
        tableOrgStructure = db.table('OrgStructure')
        tableOrg = db.table('Organisation')

        table = tableAttach.innerJoin(tablePerson, tableAttach['master_id'].eq(tablePerson['id']))
        table = table.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableAttach['orgStructure_id']))
        table = table.innerJoin(tableSpeciality, [tableSpeciality['id'].eq(tablePerson['speciality_id']),
                                                  db.left(tableSpeciality['federalCode'], 1).inlist(['1', '2'])])
        table = table.leftJoin(tableOrg, [tableOrgStructure['organisation_id'].eq(tableOrg['id'])])
        table = table.leftJoin(tableBookkeeperCode, tableBookkeeperCode['id'].eq(tableOrgStructure['id']))
        cond = [
            tableAttach['endDate'].isNull(),
            tableAttach['deleted'].eq(0),
            tablePerson['deleted'].eq(0),
            db.joinOr([tablePerson['retireDate'].isNull(),
                       tablePerson['retireDate'].gt(begDate)])
        ]
        if orgStructure:
            cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructure)))
        if self.chkBegDatePersonAttach.isChecked():
            cond.append(tableAttach['begDate'].ge(begDate))
        if self.chkEndDatePersonAttach.isChecked():
            cond.append(tableAttach['begDate'].le(endDate))

        idList = db.getIdList(table, tableAttach['id'], cond)
        self.tblPersonAttach.model().setIdList(idList)
        self.refreshStatusPersonAttach()

    # tabSync
    @QtCore.pyqtSlot()
    def on_mnuAttachedClientInfo_aboutToShow(self):
        row = self.tblAttachedClientInfo.currentIndex().row()
        record = self.tblAttachedClientInfo.model().getRecordByRow(row)
        clientId = forceRef(record.value('client_id')) if record is not None else None
        self.actAttachedClientInfoOpenCard.setEnabled(clientId is not None)

    @QtCore.pyqtSlot()
    def on_actAttachedClientInfoOpenCard_triggered(self):
        row = self.tblAttachedClientInfo.currentIndex().row()
        record = self.tblAttachedClientInfo.model().getRecordByRow(row)
        clientId = forceRef(record.value('client_id'))
        self.openAmbCardAttachTab(clientId)

    @QtCore.pyqtSlot()
    def on_btnLoadAttachedClientInfo_clicked(self):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.reloadAttachedClientInfoItems()
        QtGui.qApp.restoreOverrideCursor()

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelAttachedClientInfo_selectionChanged(self, selected, deselected):
        self.refreshStatusAttachedClientInfo()

    def refreshStatusAttachedClientInfo(self):
        countSelected = len(self.selectionModelAttachedClientInfo.selectedRows())
        countTotal = self.modelAttachedClientInfo.rowCount()
        self.btnImportAttachedClientInfo.setEnabled(countSelected > 0)
        self.btnSaveAttachedClientInfo.setEnabled(countTotal > 0)
        self.lblStatusAttachedClientInfo.setText(u'Записей в таблице выделено/всего: {0}/{1}'.format(countSelected, countTotal))

    def resetBtnLoadAttachDataEnabled(self):
        self.btnLoadAttachedTFOMS.setEnabled(self.chkLoadAttached.isChecked() or self.chkLoadDeAttached.isChecked())

    @QtCore.pyqtSlot(bool)
    def on_chkLoadAttached_toggled(self, checked):
        self.resetBtnLoadAttachDataEnabled()

    @QtCore.pyqtSlot(bool)
    def on_chkLoadDeAttached_toggled(self, checked):
        self.resetBtnLoadAttachDataEnabled()

    @staticmethod
    def updateProgressBar(progressBar, value, max, format):
        progressBar.setValue(value)
        progressBar.setMaximum(max)
        progressBar.setFormat(format)
        QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

    def clearAttachedClientInfoFilter(self):
        self.cmbOrgStructureSync.setValue(None)
        self.cmbAttachTypeSync.setCurrentIndex(0)
        self.chkBegDateFromSync.setChecked(False)
        self.chkEndDateFromSync.setChecked(False)
        self.chkBegDateToSync.setChecked(False)
        self.chkEndDateToSync.setChecked(False)
        self.cmbClientFound.setCurrentIndex(0)
        self.cmbClientAttachFound.setCurrentIndex(0)
        self.chkAttachSyncStatus.setChecked(False)
        self.cmbAttachSyncStatus.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def on_btnLoadAttachedTFOMS_clicked(self):
        u""" Предварительная загрузка списков прикрепленных/открепленных в таблицу AttachedClientInfo для последующей обработки """
        answer = QtGui.QMessageBox.question(self, u'Внимание', u'При загрузке будут сброшены статусы синхронизации, продолжить?',
                                            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if answer == QtGui.QMessageBox.No:
            return

        toDisableWidgets = (self.chkLoadDeAttached, self.chkLoadAttached)
        for widget in toDisableWidgets:
            widget.setEnabled(False)

        self.clearAttachedClientInfoFilter()

        connection = CR23ClientAttachService.createConnection()
        senderCode = connection.senderCode

        progressBar = self.getProgressBar()

        try:
            progressBar.show()
            self.updateProgressBar(progressBar, 0, 1, u'Очистка перед загрузкой ...')
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            CAttachedInfoTable.initTable(senderCode)
        finally:
            QtGui.qApp.restoreOverrideCursor()
            self.updateProgressBar(progressBar, 0, 1, u'Загрузка данных из ТФОМС ...')

        InsertChunkSize = 1000
        insertAttaches = CChunkProcessor(CAttachedInfoTable.insertAttaches, InsertChunkSize, senderCode)

        if self.chkLoadDeAttached.isChecked():
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            curDate = QtCore.QDate.currentDate()
            BaseMsg = u'Загрузка открепленных'
            AwaitMsg = u'{0}: ожидание ответа сервера ТФОМС'.format(BaseMsg)
            ProgressMsg = u'{0}: %v/%m'.format(BaseMsg)
            FinishedMsg = u'{0}: завершено'.format(BaseMsg)
            CancelledMsg = u'{0}: прервано'.format(BaseMsg)

            try:
                progressBar.show()
                self.updateProgressBar(progressBar, 0, 1, AwaitMsg)

                deattached = connection.getDeattachByDate(curDate)
                self.updateProgressBar(progressBar, 0, len(deattached), ProgressMsg)

                for i, attach in enumerate(deattached):
                    progressBar.setValue(i + 1)
                    insertAttaches.append(attach)
                insertAttaches.process()

            except MemoryError:
                QtGui.QMessageBox.warning(self, u'Внимание', u'Недостаточно памяти для продолжения процесса')
                self.updateProgressBar(progressBar, 1, 1, CancelledMsg)

            except Exception:
                QtGui.qApp.logCurrentException()
                self.updateProgressBar(progressBar, 1, 1, CancelledMsg)

            else:
                self.updateProgressBar(progressBar, 1, 1, FinishedMsg)

            finally:
                QtGui.qApp.restoreOverrideCursor()
                progressBar.hide()

        if self.chkLoadAttached.isChecked():
            BaseMsg = u'Загрузка прикрепленных'
            AwaitMsg = u'{0} [%s]: ожидание ответа сервера ТФОМС'.format(BaseMsg)
            ProgressMsg = u'{0} [%s]: %%v/%%m'.format(BaseMsg)
            FinishedMsg = u'{0}: завершено'.format(BaseMsg)
            CancelledMsg = u'{0}: прервано'.format(BaseMsg)

            try:
                requestNumber = 1

                progressBar.show()
                self.updateProgressBar(progressBar, 0, 1, AwaitMsg % requestNumber)

                QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

                for attachedCount, attaches in connection.getAttachedList():
                    self.updateProgressBar(progressBar, 0, attachedCount, ProgressMsg % requestNumber)

                    for i, attach in enumerate(attaches):
                        progressBar.setValue(i + 1)
                        if (i + 1) % InsertChunkSize == 0:
                            QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
                        insertAttaches.append(attach)
                    insertAttaches.process()

                    requestNumber += 1
                    self.updateProgressBar(progressBar, 0, 1, AwaitMsg % requestNumber)

            except MemoryError:
                QtGui.QMessageBox.warning(self, u'Внимание', u'Недостаточно памяти для продолжения процесса')
                self.updateProgressBar(progressBar, 1, 1, CancelledMsg)

            except Exception:
                QtGui.qApp.logCurrentException()
                self.updateProgressBar(progressBar, 1, 1, CancelledMsg)

            else:
                self.updateProgressBar(progressBar, 1, 1, FinishedMsg)

            finally:
                QtGui.qApp.restoreOverrideCursor()
                progressBar.hide()

        try:
            progressBar.show()
            self.updateProgressBar(progressBar, 0, 1, u'Поиск пациентов в БД ...')
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            CR23AttachExchange.findAttachedClientInfo(senderCode)
        finally:
            QtGui.qApp.restoreOverrideCursor()
            self.updateProgressBar(progressBar, 1, 1, u'Загрузка завершена')

        progressBar.hide()

        for widget in toDisableWidgets:
            widget.setEnabled(True)

        self.reloadAttachedClientInfoItems()

    @QtCore.pyqtSlot()
    def on_btnSelectAllAttachedClientInfo_clicked(self):
        self.tblAttachedClientInfo.selectAll()

    @QtCore.pyqtSlot()
    def on_btnDeselectAllAttachedClientInfo_clicked(self):
        self.tblAttachedClientInfo.clearSelection()

    @QtCore.pyqtSlot()
    def on_btnImportAttachedClientInfo_clicked(self):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        idList = self.tblAttachedClientInfo.model().idList()
        selectedIdList = [idList[index.row()] for index in self.tblAttachedClientInfo.selectionModel().selectedRows()]
        dlg = CClientAttachSyncDialog(self, selectedIdList)
        QtGui.qApp.restoreOverrideCursor()
        dlg.exec_()

        self.reloadAttachedClientInfoItems()

    @QtCore.pyqtSlot()
    def on_btnSaveAttachedClientInfo_clicked(self):
        self.saveAttachedClientInfoAsCSV()

    def saveAttachedClientInfoAsCSV(self):
        model = self.tblAttachedClientInfo.model()
        rowCount, columnCount = model.rowCount(), model.columnCount()

        fileName = forceString(QtGui.QFileDialog.getSaveFileName(self, u'Выберите имя файла', QtCore.QDir.homePath(), u'CSV файл (*.csv)'))
        if fileName:
            if not fileName.endswith(u'.csv'):
                fileName += u'.csv'
        else:
            return

        try:
            self.btnSaveAttachedClientInfo.setEnabled(False)
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

            outfile = open(fileName, mode='w+')
            writer = csv.writer(outfile)
            writer.writerow([forceString(col.title()).encode('utf-8') for col in model.cols()])

            progressBar = self.getProgressBar()
            progressBar.setMinimum(0)
            progressBar.setMaximum(rowCount)
            progressBar.setFormat(u'Сохранение: %p%')
            progressBar.show()
            QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

            for row in xrange(rowCount):
                progressBar.setValue(row + 1)
                if row % 100 == 0:
                    QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
                writer.writerow([forceString(model.data(model.index(row, col), QtCore.Qt.DisplayRole)).encode('utf-8') for col in xrange(columnCount)])
            outfile.close()
            progressBar.hide()

        finally:
            self.btnSaveAttachedClientInfo.setEnabled(True)
            QtGui.qApp.restoreOverrideCursor()

    @QtCore.pyqtSlot()
    def on_btnCloseAttachedClientInfo_clicked(self):
        self.close()

    def reloadAttachedClientInfoItems(self):
        orgStructureId = self.cmbOrgStructureSync.value()
        attachType = self.cmbAttachTypeSync.value()
        syncStatus = self.cmbAttachSyncStatus.value()
        clientFound = self.cmbClientFound.value()
        attachFound = self.cmbClientAttachFound.value()

        db = QtGui.qApp.db
        table = db.table(CAttachedInfoTable.getTableName())

        cond = []
        if orgStructureId:
            cond.append(table['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))

        if attachType:
            cond.append(table['attachType'].eq(attachType))

        if self.chkAttachSyncStatus.isChecked():
            if syncStatus == CAttachedClientInfoSyncStatus.NotSynced:
                cond.append(table['syncStatus'].inlist(CAttachedClientInfoSyncStatus.notSyncedList))
            else:
                cond.append(table['syncStatus'].eq(syncStatus))

        if clientFound == CClientAttachFound.Found:
            cond.append(table['client_id'].isNotNull())
        elif clientFound == CClientAttachFound.NotFound:
            cond.append(table['client_id'].isNull())

        if attachFound == CClientAttachFound.Found:
            cond.append(table['attach_id'].isNotNull())
        elif attachFound == CClientAttachFound.NotFound:
            cond.append(table['attach_id'].isNull())

        if self.chkBegDateFromSync.isChecked():
            cond.append(table['begDate'].ge(forceDate(self.edtBegDateFromSync.date())))
        if self.chkBegDateToSync.isChecked():
            cond.append(table['begDate'].le(forceDate(self.edtBegDateToSync.date())))
        if self.chkEndDateFromSync.isChecked():
            cond.append(table['endDate'].ge(forceDate(self.edtEndDateFromSync.date())))
        if self.chkEndDateToSync.isChecked():
            cond.append(table['endDate'].le(forceDate(self.edtEndDateToSync.date())))

        idList = db.getIdList(table, table['id'], cond)
        self.tblAttachedClientInfo.model().setIdList(idList)
        self.tblAttachedClientInfo.resizeColumnToContents(0)  # syncStatus
        self.refreshStatusAttachedClientInfo()

    # tabDeAttachLog.tabIncomeDeAttach
    @QtCore.pyqtSlot()
    def on_mnuIncomeDeAttachQuery_aboutToShow(self):
        row = self.tblIncomeDeAttachQuery.currentIndex().row()
        record = self.modelIncomeDeAttachQuery.getRecordByRow(row)
        clientId = forceRef(record.value('clientId')) if record is not None else None
        self.actIncomeDeAttachQueryOpenCard.setEnabled(clientId is not None)

    @QtCore.pyqtSlot()
    def on_actIncomeDeAttachQueryOpenCard_triggered(self):
        row = self.tblIncomeDeAttachQuery.currentIndex().row()
        record = self.modelIncomeDeAttachQuery.getRecordByRow(row)
        clientId = forceRef(record.value('clientId'))
        self.openAmbCardAttachTab(clientId)

    @QtCore.pyqtSlot()
    def on_btnGetDeAttachQuery_clicked(self):
        self.tblIncomeDeAttachQuery.model().clearItems()
        connection = CR23ClientAttachService.getConnection()

        date = QtCore.QDate.currentDate()
        error = None
        updated = False

        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            toDeattachList = connection.getDeAttachQuery(date)
            self.processToDeAttach(toDeattachList)
            updated = True

        except CSynchronizeAttachException as e:
            error = u'<i>%s</i>' % forceString(e)

        finally:
            QtGui.qApp.restoreOverrideCursor()

        if error:
            QtGui.QMessageBox.information(self, u'Внимание!', error)
        else:
            QtGui.QMessageBox.information(self, u'Статус', u'Оповещения обновлены' if updated else u'Оповещений нет')

    def processToDeAttach(self, toDeAttachList):
        u"""
        Поиск пациентов и прикреплений в БД по полученным уведомлениям о прикреплении
        :param toDeAttachList: [list of DeAttachQuery]
        :return: None
        """
        db = QtGui.qApp.db
        tableClientAttach = db.table('ClientAttach')

        curDateTme = QtCore.QDateTime.currentDateTime()

        incomeQueryData = []
        for deattachQuery in toDeAttachList:
            found, idList = findClient(deattachQuery.client)
            if found:
                clientId = idList[0]
                attachId = findClientAttach(clientId, orgCode=deattachQuery.destOrgCode, toDeAttach=True)
                if attachId:
                    attachRecord = db.getRecord(tableClientAttach, 'id, endDate', attachId)
                    endDate = forceDate(attachRecord.value('endDate'))
                    if endDate.isNull():
                        status = CAttachedClientInfoSyncStatus.Deattach_NotDeattached
                    else:
                        status = CAttachedClientInfoSyncStatus.Deattach_AlreadyDeattached
                else:
                    status = CAttachedClientInfoSyncStatus.Deattach_NoAttach

                insertAttachLog(clientId, status, curDateTme)
            else:
                clientId = None
                status = CAttachedClientInfoSyncStatus.Deattach_NoAttach

            incomeQueryData.append((clientId, deattachQuery.client, status, deattachQuery))

        for data in incomeQueryData:
            self.modelIncomeDeAttachQuery.addDeAttachedQuery(*data)

    # tablDeAttachLog.tabOutcomeDeAttach
    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelOutcomeDeAttachQuery_selectionChanged(self, selected, deselected):
        self.refreshStatusOutcomeDeAttachQuery()

    def refreshStatusOutcomeDeAttachQuery(self):
        countSelected = len(self.selectionModelOutcomeDeAttachQuery.selectedRows())
        countTotal = self.modelOutcomeDeAttachQuery.rowCount()
        self.btnSendNotSentDeAttachQuery.setEnabled(countSelected > 0)
        self.lblStatusOutcomeDeAttachQuery.setText(u'Записей в таблице выделено/всего: %s/%s' % (countSelected, countTotal))

    @QtCore.pyqtSlot()
    def on_mnuOutcomeDeAttachQuery_aboutToShow(self):
        row = self.tblOutcomeDeAttachQuery.currentIndex().row()
        record = self.modelOutcomeDeAttachQuery.getRecordByRow(row)
        clientId = forceRef(record.value('clientId')) if record is not None else None
        self.actOutcomeDeAttachQueryOpenCard.setEnabled(clientId is not None)

    @QtCore.pyqtSlot()
    def on_actOutcomeDeAttachQueryOpenCard_triggered(self):
        row = self.tblOutcomeDeAttachQuery.currentIndex().row()
        record = self.modelOutcomeDeAttachQuery.getRecordByRow(row)
        clientId = forceRef(record.value('clientId'))
        self.openAmbCardAttachTab(clientId)

    @QtCore.pyqtSlot()
    def on_btnUpdateDeAttachQueryLog_clicked(self):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.reloadDeAttachQueryLogItems()
        QtGui.qApp.restoreOverrideCursor()

    @QtCore.pyqtSlot()
    def on_btnSelectAllSendDeAttachQuery_clicked(self):
        self.tblOutcomeDeAttachQuery.selectAll()

    @QtCore.pyqtSlot()
    def on_btnDeselectAllSendDeAttachQuery_clicked(self):
        self.tblOutcomeDeAttachQuery.clearSelection()

    @QtCore.pyqtSlot()
    def on_btnSendNotSentDeAttachQuery_clicked(self):
        idList = []
        deattachQueries = []
        for index in self.selectionModelOutcomeDeAttachQuery.selectedRows():
            rec = self.modelOutcomeDeAttachQuery.getRecordByRow(index.row())
            if not forceBool(rec.value('sentToTFOMS')):
                idList.append(rec.value('id'))
                deattachQueries.append(COutcomeDeAttachQueryModel.getDeAttachQuery(rec))

        if not deattachQueries:
            QtGui.QMessageBox.information(self, u'Внимание', u'Нечего отправлять')
        else:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            connection = CR23ClientAttachService.createConnection()
            errors, errorMap = CR23AttachExchange.sendDeAttachQueries(connection, deattachQueries)
            QtGui.qApp.restoreOverrideCursor()
            if not errors and not errorMap:
                tableQueryLog = QtGui.qApp.db.table(getDeAttachQueryLogTable())
                QtGui.qApp.db.updateRecords(tableQueryLog, tableQueryLog['sentToTFOMS'].eq(1), tableQueryLog['id'].inlist(idList))

            title = u'Отправка уведомлений о прикреплении'
            if errors:
                QtGui.QMessageBox.warning(self, title, u'<br/>'.join([u'<b>Ошибка в передаче данных</b>:'] + errors))
            elif errorMap:
                QtGui.QMessageBox.warning(self, title, u'<br/>'.join([u'<b>Ошибка в передаче данных</b>:'] + errorMap.values()))
            else:
                QtGui.QMessageBox.information(self, title, u'Данные переданы успешно')

        self.reloadDeAttachQueryLogItems()

    @QtCore.pyqtSlot()
    def on_btnCloseDeAttachLog_clicked(self):
        self.close()

    def reloadDeAttachQueryLogItems(self):
        db = QtGui.qApp.db
        tableQueryLog = db.table(getDeAttachQueryLogTable())

        numFrom, numTo = forceInt(self.edtQueryNumFrom.text()), forceInt(self.edtQueryNumTo.text())
        dateFrom, dateTo = forceDate(self.edtQueryDateFrom.date()), forceDate(self.edtQueryDateTo.date())
        srcOrgCode, destOrgCode = forceString(self.edtSrcOrgCode.text()), forceString(self.edtDestOrgCode.text())

        cond = []

        if self.chkQueryNumFrom.isChecked():
            cond.append(tableQueryLog['number'].ge(numFrom))

        if self.chkQueryNumTo.isChecked():
            cond.append(tableQueryLog['number'].le(numTo))

        if self.chkQueryDateFrom.isChecked():
            cond.append(tableQueryLog['date'].ge(dateFrom))

        if self.chkQueryDateTo.isChecked():
            cond.append(tableQueryLog['date'].le(dateTo))

        if srcOrgCode:
            cond.append(tableQueryLog['srcMO'].eq(srcOrgCode))

        if destOrgCode:
            cond.append(tableQueryLog['destMO'].eq(destOrgCode))

        if self.chkNotSentDeAttachQuery.isChecked():
            cond.append(tableQueryLog['sentToTFOMS'].eq(0))

        idList = db.getDistinctIdList(tableQueryLog, tableQueryLog['id'], cond)
        self.tblOutcomeDeAttachQuery.model().setIdList(idList)


class CClientAttachModel(CTableModel):
    def __init__(self, parent):
        super(CClientAttachModel, self).__init__(parent, cols=[
            CTextCol(u'Описание ошибки', ['errorCode'], 100, 'l'),
            CTextCol(u'Код ЛПУ', ['orgCode'], 20, 'c'),
            CTextCol(u'Участок', ['location'], 20, 'l'),
            CEnumCol(u'Тип', ['attachType'], CAttachType, 20, 'l'),
            CDateCol(u'Дата', ['begDate'], 20, 'c'),
            CDateCol(u'Дата открепления', ['endDate'], 20, 'c'),
            CTextCol(u'Причина открепления', ['detachmentReason'], 20, 'c'),
            CNameCol(u'Фамилия', ['lastName'], 20, 'l'),
            CNameCol(u'Имя', ['firstName'], 20, 'l'),
            CNameCol(u'Отчество', ['patrName'], 20, 'l'),
            CEnumCol(u'Пол', ['sex'], [u'-', u'М', u'Ж'], 4, 'c'),
            CDateCol(u'Дата рождения', ['birthDate'], 20, 'c'),
            CSNILSCol(u'СНИЛС', ['SNILS'], 20, 'c'),
            CTextCol(u'Тип документа', ['docType'], 20, 'l'),
            CTextCol(u'Серия документа', ['docSerial'], 20, 'l'),
            CTextCol(u'Номер документа', ['docNumber'], 20, 'l'),
            CTextCol(u'Вид полиса', ['policyKindName'], 20, 'l'),
            CTextCol(u'Серия полиса', ['policySerial'], 20, 'l'),
            CTextCol(u'Номер полиса', ['policyNumber'], 20, 'l'),
            CTextCol(u'Код СМО', ['insurerCode'], 20, 'c'),
            CTextCol(u'Код территории страхования', ['insurerOKATO'], 20, 'c'),
        ])
        self.setTable('ClientAttach')
        self._parent = parent

    # Only for CInDocTableView.contextMenuEvent(event)
    def isEditable(self):
        return True

    def getClientAttachInfo(self, index):
        rec = self.getRecordByRow(index.row())
        if rec is not None:
            policy = PolicyInfo(forceString(rec.value('policySerial')) or None,
                                forceString(rec.value('policyNumber')) or None,
                                forceInt(rec.value('policyCode')),
                                insurerCode=forceString(rec.value('insurerCode') or None),
                                insurerOKATO=forceString(rec.value('insurerOKATO')) or None)
            doc = DocumentInfo(forceString(rec.value('docSerial')) or None,
                               forceString(rec.value('docNumber')) or None,
                               forceInt(rec.value('docCode')))

            attachType, attachReason = CR23AttachExchange.getAttachTypeInfo(forceRef(rec.value('attachTypeId')))
            attach = AttachInfo(id=forceRef(rec.value('id')),
                                orgCode=forceString(rec.value('orgCode')),
                                sectionCode=forceString(rec.value('sectionCode')),
                                begDate=forceDate(rec.value('begDate')),
                                endDate=forceDate(rec.value('endDate')) or None,
                                attachType=attachType,
                                attachReason=attachReason,
                                deattachReason=CR23AttachExchange.getDeAttachReason(forceRef(rec.value('detachmentReasonId'))),
                                doctorSNILS=formatSNILS(forceString(rec.value('doctorSNILS')).replace(' ', '').replace('-', '')) or None)

            return AttachedClientInfo(
                forceString(rec.value('lastName')),
                forceString(rec.value('firstName')),
                forceString(rec.value('patrName')),
                forceDate(rec.value('birthDate')),
                formatSex(rec.value('sex')),
                id=forceRef(rec.value('clientId')),
                SNILS=formatSNILS(forceString(rec.value('SNILS')).replace('-', '').replace(' ', '')) or None,
                policy=policy,
                doc=doc,
                attach=attach
            )

        return AttachedClientInfo()

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        tableAttach = db.table('ClientAttach')
        tableAttachType = db.table('rbAttachType')
        tableClient = db.table('Client')
        tablePolicyKind = db.table('rbPolicyKind')
        tablePolicyType = db.table('rbPolicyType')
        tablePolicyType1 = db.table('rbPolicyType').alias('rpt1')
        tableDetachmentReason = db.table('rbDetachmentReason')

        tableAttOrg = db.table('Organisation').alias('attOrg')
        tableInsOrg = db.table('Organisation').alias('insOrg')
        tableInsHeadOrg = db.table('Organisation').alias('insHeadOrg')
        tableOrgStructure = db.table('OrgStructure')
        tableBookkeeper = db.table(CBookkeeperCode.getTableName()).alias('bkkeeper')

        tablePerson = db.table('Person')
        tablePersonAttach = db.table('PersonAttach')
        tablePersonAttach1 = db.table('PersonAttach').alias('pa1')

        tableDocument = db.table('ClientDocument')
        tableDocument1 = db.table('ClientDocument').alias('cd1')
        tablePolicy = db.table('ClientPolicy')
        tablePolicy1 = db.table('ClientPolicy').alias('cp1')
        tableRDT = db.table('rbDocumentType')
        tableRDT1 = db.table('rbDocumentType').alias('rdt1')
        tableRDTG = db.table('rbDocumentTypeGroup')

        curDate = QtCore.QDate.currentDate()

        table = tableAttach.innerJoin(tableAttachType, [tableAttachType['id'].eq(tableAttach['attachType_id'])])
        table = table.innerJoin(tableClient, [tableClient['id'].eq(tableAttach['client_id'])])

        table = table.leftJoin(tablePersonAttach, [tablePersonAttach['orgStructure_id'].eq(tableAttach['orgStructure_id']),
                                                   tablePersonAttach['begDate'].dateLe(tableAttach['begDate']),
                                                   tablePersonAttach['deleted'].eq(0)])
        table = table.leftJoin(tablePerson, [tablePerson['id'].eq(tablePersonAttach['master_id'])])

        table = table.leftJoin(tablePersonAttach1, [tablePersonAttach1['orgStructure_id'].eq(tableAttach['orgStructure_id']),
                                                    tablePersonAttach1['begDate'].dateLe(tableAttach['begDate']),
                                                    tablePersonAttach1['id'].ge(tablePersonAttach['id']),
                                                    tablePersonAttach1['deleted'].eq(0)])

        table = table.leftJoin(tableAttOrg, [tableAttOrg['id'].eq(tableAttach['LPU_id'])])
        table = table.leftJoin(tableOrgStructure, [tableOrgStructure['id'].eq(tableAttach['orgStructure_id']),
                                                   tableOrgStructure['deleted'].eq(0)])
        table = table.leftJoin(tableBookkeeper, [tableBookkeeper['id'].eq(tableOrgStructure['id'])])
        table = table.leftJoin(tableDetachmentReason, [tableDetachmentReason['id'].eq(tableAttach['detachment_id'])])

        table = table.leftJoin(tableRDTG, [tableRDTG['code'].eq('1')])

        table = table.leftJoin(tableDocument, [tableDocument['client_id'].eq(tableClient['id']),
                                               tableDocument['deleted'].eq(0)])
        table = table.leftJoin(tableRDT, [tableRDT['group_id'].eq(tableRDTG['id']),
                                          tableRDT['id'].eq(tableDocument['documentType_id'])])

        table = table.leftJoin(tableDocument1, [tableDocument1['client_id'].eq(tableDocument['client_id']),
                                                tableDocument1['deleted'].eq(0),
                                                tableDocument1['id'].gt(tableDocument['id'])])
        table = table.leftJoin(tableRDT1, [tableRDT1['group_id'].eq(tableRDTG['id']),
                                           tableRDT1['id'].eq(tableDocument1['documentType_id'])])

        table = table.leftJoin(tablePolicy, [tablePolicy['client_id'].eq(tableClient['id']),
                                             tablePolicy['deleted'].eq(0),
                                             db.joinOr([tablePolicy['endDate'].isNull(),
                                                        tablePolicy['endDate'].gt(curDate)])])
        table = table.leftJoin(tablePolicyKind, [tablePolicy['policyKind_id'].eq(tablePolicyKind['id'])])
        table = table.leftJoin(tablePolicyType, [tablePolicyType['id'].eq(tablePolicy['policyType_id']),
                                                 tablePolicyType['name'].like(u'ОМС%')])
        table = table.leftJoin(tablePolicy1, [tablePolicy1['client_id'].eq(tableClient['id']),
                                              tablePolicy1['deleted'].eq(0),
                                              tablePolicy1['id'].gt(tablePolicy['id']),
                                              db.joinOr([tablePolicy1['endDate'].isNull(),
                                                         tablePolicy1['endDate'].gt(curDate)])
                                              ])
        table = table.leftJoin(tablePolicyType1, [tablePolicyType1['id'].eq(tablePolicy1['policyType_id']),
                                                  tablePolicyType1['name'].like(u'ОМС%')])

        table = table.leftJoin(tableInsOrg, [tableInsOrg['id'].eq(tablePolicy['insurer_id']),
                                             tableInsOrg['deleted'].eq(0)])
        table = table.leftJoin(tableInsHeadOrg, [tableInsHeadOrg['id'].eq(tableInsOrg['head_id']),
                                                 tableInsHeadOrg['deleted'].eq(0)])

        cols = [
            tableAttach['id'].alias('id'),
            tableAttach['errorCode'],
            tableBookkeeper['orgCode'].alias('orgCode'),
            db.concat(tableOrgStructure['infisInternalCode'], ' | ', tableOrgStructure['code']).alias('location'),
            tableOrgStructure['infisInternalCode'].alias('sectionCode'),
            tableAttachType['id'].alias('attachTypeId'),
            tableAttachType['code'].alias('attachType'),
            tableAttach['begDate'],
            tableAttach['endDate'],
            tableDetachmentReason['id'].alias('detachmentReasonId'),
            tableDetachmentReason['name'].alias('detachmentReason'),
            tableClient['id'].alias('clientId'),
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['sex'],
            tableClient['birthDate'],
            tableClient['SNILS'],
            tableRDT['name'].alias('docType'),
            tableRDT['code'].alias('docCode'),
            tableDocument['serial'].alias('docSerial'),
            tableDocument['number'].alias('docNumber'),
            tablePolicyKind['regionalCode'].alias('policyCode'),
            tablePolicyKind['name'].alias('policyKindName'),
            tablePolicy['serial'].alias('policySerial'),
            tablePolicy['number'].alias('policyNumber'),
            tableInsOrg['miacCode'].alias('insurerCode'),
            db.if_(tableInsOrg['head_id'].isNull(),
                   tableInsOrg['OKATO'],
                   tableInsHeadOrg['OKATO']).alias('insurerOKATO'),
            tablePerson['SNILS'].alias('doctorSNILS')
        ]
        cond = [
            tableAttach['sentToTFOMS'].ne(CAttachSentToTFOMS.Synced),
            tableAttach['deleted'].eq(0),
            tablePersonAttach1['id'].isNull(),
            tableDocument1['id'].isNull(),
            tablePolicy1['id'].isNull()
        ]

        self._table = table
        self._recordsCache = CTableFilteredRecordCache(QtGui.qApp.db, self._table, cols=cols, capacity=recordCacheCapacity, cond=cond)

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        if column != self._sortColumn:
            self._sortColumn = column
            self._isSorted = False
        if order != self._sortOrder:
            self._sortOrder = order
            self._isSorted = False
        if self._idList and not self._isSorted:
            self._parent.reloadClientAttachItems(order=self.cols()[column].fields())
            self._isSorted = True


class CPersonAttachModel(CTableModel):
    def __init__(self, parent):
        super(CPersonAttachModel, self).__init__(parent, cols=[
            CBoolCol(u'Синхронизировано', ['synced'], 10, 'l'),
            CTextCol(u'Описание ошибки', ['errorCode'], 80, 'l'),
            CTextCol(u'Код ЛПУ', ['orgCode'], 20, 'c'),
            CTextCol(u'Код участка', ['sectionCode'], 20, 'c'),
            CTextCol(u'Участок', ['sectionName'], 20, 'l'),
            CTextCol(u'Дата начала', ['begDate'], 20, 'c'),
            CNameCol(u'Фамилия', ['lastName'], 20, 'l'),
            CNameCol(u'Имя', ['firstName'], 20, 'l'),
            CNameCol(u'Отчество', ['patrName'], 20, 'l'),
            CEnumCol(u'Категория персонала', ['category'], CPersonCategory, 20, 'l'),
            CDateCol(u'Дата рождения', ['birthDate'], 20, 'c'),
            CTextCol(u'СНИЛС', ['SNILS'], 20, 'c'),
            CTextCol(u'Код специальности', ['specialityCode'], 20, 'c'),
            CTextCol(u'Специальность', ['specialityName'], 20, 'l'),
        ])
        self.setTable('PersonAttach')

    # Only for CInDocTableView.contextMenuEvent(event)
    def isEditable(self):
        return True

    def getPersonAttachInfo(self, index):
        rec = self.getRecordByRow(index.row())
        if rec is not None:
            return PersonAttachInfo(
                id=forceRef(rec.value('id')),
                orgCode=forceString(rec.value('orgCode')),
                sectionCode=forceString(rec.value('sectionCode')),
                begDate=forceDate(rec.value('begDate')),
                lastName=nameCase(forceString(rec.value('lastName'))),
                firstName=nameCase(forceString(rec.value('firstName'))),
                patrName=nameCase(forceString(rec.value('patrName'))),
                birthDate=forceDate(rec.value('birthDate')),
                SNILS=formatSNILS(forceString(rec.value('SNILS')).replace('-', '').replace(' ', '')) or None,
                specialityCode=forceInt(rec.value('specialityCode')) or None,
                category=forceInt(rec.value('category'))
            )

        return PersonAttachInfo()

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        tableAttach = db.table('PersonAttach')
        tablePerson = db.table('Person')
        tableSpeciality = db.table('rbSpeciality')
        tableBookkeeper = db.table(CBookkeeperCode.getTableName()).alias('bkkeeper')
        tableOrgStructure = db.table('OrgStructure')
        tableOrg = db.table('Organisation')

        table = tableAttach.innerJoin(tablePerson, [tablePerson['id'].eq(tableAttach['master_id']),
                                                    tablePerson['deleted'].eq(0)])
        table = table.innerJoin(tableOrgStructure, [tableOrgStructure['id'].eq(tableAttach['orgStructure_id'])])
        table = table.innerJoin(tableSpeciality, [tableSpeciality['id'].eq(tablePerson['speciality_id']),
                                                  db.joinOr([tableSpeciality['federalCode'].like("1%"),
                                                             tableSpeciality['federalCode'].like("2%")])])
        table = table.leftJoin(tableOrg, [tableOrgStructure['organisation_id'].eq(tableOrg['id'])])
        table = table.leftJoin(tableBookkeeper, tableBookkeeper['id'].eq(tableOrgStructure['id']))

        cols = [
            tableAttach['id'],
            (tableAttach['sentToTFOMS'] == CAttachSentToTFOMS.Synced).alias('synced'),
            tableAttach['errorCode'],
            tableBookkeeper['orgCode'].alias('orgCode'),
            tableOrgStructure['name'].alias('sectionName'),
            tableOrgStructure['infisInternalCode'].alias('sectionCode'),
            tablePerson['id'].alias('personId'),
            tablePerson['lastName'],
            tablePerson['firstName'],
            tablePerson['patrName'],
            tablePerson['birthDate'],
            tablePerson['SNILS'],
            tableAttach['begDate'],
            tableAttach['endDate'],
            tableSpeciality['regionalCode'].alias('specialityCode'),
            tableSpeciality['name'].alias('specialityName'),
            db.left(tableSpeciality['federalCode'], 1).alias('category')
        ]
        cond = [
            tableAttach['endDate'].isNull(),
            tableAttach['deleted'].eq(0)
        ]
        self._table = table
        self._recordsCache = CTableFilteredRecordCache(QtGui.qApp.db, self._table, cols=cols, capacity=recordCacheCapacity, cond=cond)


class CClientFoundInDocTableCol(CBoolInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CBoolInDocTableCol.__init__(self, title, fieldName, width, **params)

    def toString(self, val, record):
        clientId = forceString(val)
        return val if clientId else toVariant('-')


class CAddressInfoCol(CCol):
    def format(self, values):
        return toVariant(u', '.join(filter(bool, map(forceString, values[:7]))))

    def formatNative(self, values):
        return u', '.join(filter(bool, map(forceString, values[:7])))


class CAttachedClientInfoModel(CTableModel):
    fetchSize = 50

    def __init__(self, parent):
        CTableModel.__init__(self, parent, cols=[
            CEnumCol(u'Статус', ['syncStatus'], CAttachedClientInfoSyncStatus, 20, 'l'),
            CBoolCol(u'Найден в БД', ['client_id'], 10, 'l'),
            CNameCol(u'Фамилия', ['lastName'], 20, 'l'),
            CNameCol(u'Имя', ['firstName'], 20, 'l'),
            CNameCol(u'Отчество', ['patrName'], 20, 'l'),
            CEnumCol(u'Пол', ['sex'], [u'-', u'М', u'Ж'], 4, 'c'),
            CDateCol(u'Дата рождения', ['birthDate'], 20, 'c'),
            CEnumCol(u'Тип прикрепления', ['attachType'], CAttachType, 10, 'l'),
            CTextCol(u'Код МО', ['orgCode'], 10, 'c'),
            CTextCol(u'Код участка', ['sectionCode'], 10, 'c'),
            CTextCol(u'Подразделение', ['orgStructureCode'], 10, 'l'),
            CDateCol(u'Дата прикрепления', ['begDate'], 4, 'c'),
            CDateCol(u'Дата открепления', ['endDate'], 4, 'c'),
            CEnumCol(u'Причина открепления', ['deattachReason'], CDeAttachReason, 10, 'l'),
            CSNILSCol(u'СНИЛС', ['SNILS'], 20, 'l'),
            CAddressInfoCol(u'Адрес регистрации', ['regDistrict', 'regCity', 'regLocality', 'regStreet', 'regHouse', 'regCorpus', 'regFlat'], 10, 'l'),
            CAddressInfoCol(u'Адрес проживания', ['locDistrict', 'locCity', 'locLocality', 'locStreet', 'locHouse', 'locCorpus', 'locFlat'], 10, 'l'),
            CTextCol(u'Тип документа', ['docType'], 4, 'c'),
            CTextCol(u'Серия документа', ['docSerial'], 10, 'l'),
            CTextCol(u'Номер документа', ['docNumber'], 10, 'l'),
            CEnumCol(u'Тип полиса', ['policyType'], CAttachPolicyType, 10, 'l'),
            CTextCol(u'Серия полиса', ['policySerial'], 10, 'l'),
            CTextCol(u'Номер полиса', ['policyNumber'], 10, 'l'),
            CTextCol(u'Код СМО', ['insurerCode'], 10, 'c')
        ])
        self.setTable('AttachedClientInfo')
        self._parent = parent

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        tableOrgStructure = db.table('OrgStructure')
        tableACI = db.table(CAttachedInfoTable.getTableName())

        table = tableACI.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableACI['orgStructure_id']))
        cols = [
            tableACI['id'],
            tableACI['syncStatus'],
            tableACI['lastName'], tableACI['firstName'], tableACI['patrName'], tableACI['sex'], tableACI['birthDate'],
            tableACI['attachType'], tableACI['orgCode'], tableACI['sectionCode'],
            tableACI['begDate'], tableACI['endDate'],
            tableACI['deattachReason'],
            tableACI['SNILS'],
            tableACI['docType'], tableACI['docSerial'], tableACI['docNumber'],
            tableACI['policyType'], tableACI['policySerial'], tableACI['policyNumber'], tableACI['insurerCode'],
            tableOrgStructure['code'].alias('orgStructureCode'),
            tableACI['client_id'],
            tableACI['regDistrict'], tableACI['regCity'], tableACI['regLocality'], tableACI['regStreet'], tableACI['regHouse'], tableACI['regCorpus'], tableACI['regFlat'],
            tableACI['locDistrict'], tableACI['locCity'], tableACI['locLocality'], tableACI['locStreet'], tableACI['locHouse'], tableACI['locCorpus'], tableACI['locFlat']
        ]

        self._table = table
        self._recordsCache = CTableRecordCache(QtGui.qApp.db, table, cols, capacity=recordCacheCapacity)

    # Only for CInDocTableView.contextMenuEvent(event)
    def isEditable(self):
        return True

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        progressBar = self._parent.getProgressBar()
        progressBar.show()
        try:
            colTitle = forceString(self._cols[column].title()) if 0 <= column < len(self._cols) else u''
            self._parent.updateProgressBar(progressBar, 0, 1, u'Сортировка по столбцу "%s"' % colTitle)
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            CTableModel.sort(self, column, order)
        finally:
            QtGui.qApp.restoreOverrideCursor()
        progressBar.hide()


class CIncomeDeAttachQueryModel(CRecordListModel):
    def __init__(self, parent):
        CRecordListModel.__init__(self, parent, cols=[
            CClientFoundInDocTableCol(u'Найден в БД', 'clientId', 4, sortable=True, valueType=QtCore.QVariant.Bool),
            CEnumInDocTableCol(u'Статус', 'status', 20, CAttachedClientInfoSyncStatus, sortable=True, valueType=QtCore.QVariant.String),
            CInDocTableCol(u'Фамилия', 'lastName', 20, sortable=True, valueType=QtCore.QVariant.String),
            CInDocTableCol(u'Имя', 'firstName', 20, sortable=True, valueType=QtCore.QVariant.String),
            CInDocTableCol(u'Отчество', 'patrName', 20, sortable=True, valueType=QtCore.QVariant.String),
            CDateInDocTableCol(u'Дата рождения', 'birthDate', 20, alignment='c', valueType=QtCore.QVariant.Date),
            CInDocTableCol(u'Код ЛПУ', 'orgCode', 20, alignment='c', sortable=True, valueType=QtCore.QVariant.String),
            CInDocTableCol(u'Код запросившего ЛПУ', 'querySrcOrgCode', 20, alignment='c', sortable=True, valueType=QtCore.QVariant.String),
            CInDocTableCol(u'Тип документа УДЛ', 'docType', 20, sortable=True, valueType=QtCore.QVariant.String),
            CInDocTableCol(u'Серия документа УДЛ', 'docSerial', 20, valueType=QtCore.QVariant.String),
            CInDocTableCol(u'Номер документа УДЛ', 'docNumber', 20, valueType=QtCore.QVariant.String),
            CInDocTableCol(u'Вид полиса', 'policyType', 20, sortable=True, valueType=QtCore.QVariant.String),
            CInDocTableCol(u'Серия полиса', 'policySerial', 20, valueType=QtCore.QVariant.String),
            CInDocTableCol(u'Номер полиса', 'policyNumber', 20, valueType=QtCore.QVariant.String)
        ])
        for col in self.cols():
            col.setReadOnly(True)

        self.docTypeNameMap = CDocumentType.getCodeNameMap()

    def addDeAttachedQuery(self, clientId, client, status, deattachQuery):
        record = self.getEmptyRecord()

        record.setValue('clientId', toVariant(clientId))
        record.setValue('lastName', toVariant(client.lastName))
        record.setValue('firstName', toVariant(client.firstName))
        record.setValue('patrName', toVariant(client.patrName))
        record.setValue('birthDate', toVariant(client.birthDate))
        record.setValue('sex', toVariant(client.sex))

        record.setValue('docType', toVariant(self.docTypeNameMap.get(client.document.type, client.document.type) or None))
        record.setValue('docSerial', toVariant(client.document.serial))
        record.setValue('docNumber', toVariant(client.document.number))

        record.setValue('policyType', toVariant(CAttachPolicyType.nameMap.get(client.policy.type, client.policy.type) or None))
        record.setValue('policySerial', toVariant(client.policy.serial))
        record.setValue('policyNumber', toVariant(client.policy.number))

        record.setValue('status', toVariant(status))
        record.setValue('querySrcOrgCode', toVariant(deattachQuery.srcOrgCode))
        record.setValue('orgCode', toVariant(deattachQuery.destOrgCode))

        self.addRecord(record)

    # Only for CInDocTableView.contextMenuEvent(event)
    def isEditable(self):
        return True


class COutcomeDeAttachQueryModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent, cols=[
            CBoolCol(u'Отправлено', ['sentToTFOMS'], 5, 'c'),
            CTextCol(u'№ уведомления', ['number'], 5, 'c'),
            CDateCol(u'Дата уведомления', ['queryDate'], 20, 'c'),
            CTextCol(u'Код отправителя', ['srcMO'], 20, 'c'),
            CTextCol(u'Код получателя', ['destMO'], 20, 'c'),
            CTextCol(u'Фамилия', ['lastName'], 20),
            CTextCol(u'Имя', ['firstName'], 20),
            CTextCol(u'Отчество', ['patrName'], 20),
            CDateCol(u'Дата рождения', ['birthDate'], 20, 'c'),
            CEnumCol(u'Пол', ['sex'], [u'-', u'М', u'Ж'], 4, 'c'),
            CSNILSCol(u'СНИЛС', ['SNILS'], 20, 'c'),
            CTextCol(u'Код ЛПУ', ['orgCode'], 20, 'c'),
            CTextCol(u'Код участка', ['sectionCode'], 20, 'c'),
            CDateCol(u'Дата прикрепления', ['begDate'], 20, 'c'),
            CDateCol(u'Дата открепления', ['endDate'], 20, 'c')
        ])
        self.setTable('DeAttachQueryLog')

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        tableAttach = db.table('ClientAttach')
        tableBookkeeper = db.table(CBookkeeperCode.getTableName())
        tableClient = db.table('Client')
        tableOrgStructure = db.table('OrgStructure')
        tableQueryLog = db.table(getDeAttachQueryLogTable())

        table = tableQueryLog.leftJoin(tableClient, tableClient['id'].eq(tableQueryLog['client_id']))
        table = table.leftJoin(tableAttach, tableAttach['id'].eq(tableQueryLog['attach_id']))
        table = table.leftJoin(tableOrgStructure, [tableOrgStructure['id'].eq(tableAttach['orgStructure_id']),
                                                   tableOrgStructure['deleted'].eq(0)])
        table = table.leftJoin(tableBookkeeper, tableBookkeeper['id'].eq(tableOrgStructure['id']))

        cols = [
            tableQueryLog['id'].alias('id'),
            tableClient['id'].alias('clientId'),
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['birthDate'],
            tableClient['sex'],
            tableClient['SNILS'],
            tableAttach['id'].alias('attachId'),
            tableAttach['begDate'],
            tableAttach['endDate'],
            tableOrgStructure['infisInternalCode'].alias('sectionCode'),
            tableBookkeeper['orgCode'].alias('orgCode'),
            tableQueryLog['number'],
            tableQueryLog['date'].alias('queryDate'),
            tableQueryLog['srcMO'],
            tableQueryLog['destMO'],
            tableQueryLog['sentToTFOMS']
        ]
        self._table = table
        self._recordsCache = CTableFilteredRecordCache(QtGui.qApp.db, self._table, cols, recordCacheCapacity)

    # Only for CInDocTableView.contextMenuEvent(event)
    def isEditable(self):
        return True

    @staticmethod
    def getDeAttachQuery(rec):
        return DeAttachQuery(
            number=forceInt(rec.value('number')),
            date=forceDate(rec.value('queryDate')),
            id=forceRef(rec.value('attachId')),
            srcOrgCode=forceString(rec.value('srcMO')),
            destOrgCode=forceString(rec.value('destMO')),
            client=CR23AttachExchange.makeClientInfoById(forceRef(rec.value('clientId')))
        )
