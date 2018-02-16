# -*- coding: utf-8 -*-

import os
from PyQt4 import QtCore, QtGui

from Events.CreateEvent import editEvent
from Exchange.R23.ExamPlan.CreateDialog import CCreateDialog
from Exchange.R23.ExamPlan.Data import CExamPlanData
from Exchange.R23.ExamPlan.Service import CExamPlanServiceTFOMS
from Exchange.R23.ExamPlan.Types import FactInfo, Identifiable, OrgContact, PlanDate, PlanQuantity
from Exchange.R23.ExamPlan.Utils import ExamKind, ExamKindSpecials, ExamMethod, ExamStatus, ExamStep, InfoMethod, InfoStep, Month, PersonCategory, Quarter
from Exchange.R23.ExamPlan.ui.Ui_ExchangeDialog import Ui_ExchangeDialog
from Exchange.R23.TFOMS.Service import CServiceTFOMSException
from Orgs.Utils import getOrganisationSections
from Users.Rights import urAdmin, urRegTabWriteRegistry
from library.DialogBase import CDialogBase
from library.ItemListModel import CDateAttribCol, CEnumAttribCol, CItemAttribCol, CItemListModel, CItemProxyCol, CStringAttribCol
from library.ListModel import CMultiSelectionListModel
from library.TableModel import CDateCol, CDateTimeCol, CEnumCol, CIntCol, CNameCol, CTableModel, CTableRecordCache, CTextCol
from library.Utils import forceDate, forceInt, forceRef, forceString, formatName, getPref, setPref, splitBy


class CPlanQuantitiesModel(CItemListModel):
    u""" Плановые объемы проф. мероприятий от МЗ КК """

    def __init__(self, parent):
        super(CPlanQuantitiesModel, self).__init__(parent, cols=[
            CItemAttribCol(u'Код МО', 'orgCode'),
            CEnumAttribCol(u'Вид мероприятия', 'kind', ExamKind),
            CItemAttribCol(u'Год', 'year'),
            CEnumAttribCol(u'Месяц', 'month', Month),
            CItemAttribCol(u'Количество', 'quantity')
        ], itemType=PlanQuantity)


class CIdentifiableItemModel(CItemListModel):
    def _nextRid(self):
        rids = [item.rid for item in self.items() if item.rid]
        return (max(rids) if rids else 0) + 1

    def _getOrgCode(self):
        if self._orgCode is None:
            self._orgCode = QtGui.qApp.currentOrgInfis()
        return self._orgCode

    def setDefaults(self, item):
        u""" :type item: Identifiable """
        item.rid = self._nextRid()


class CPlanDatesModel(CIdentifiableItemModel):
    u""" Даты/место запланированных проф. мероприятий """

    def __init__(self, parent):
        super(CPlanDatesModel, self).__init__(parent, cols=[
            CStringAttribCol(u'Код МО', 'orgCode', editable=True),
            CEnumAttribCol(u'Вид мероприятия', 'kind', ExamKind, editable=True),
            CEnumAttribCol(u'Метод осуществления', 'method', ExamMethod, editable=True),
            CDateAttribCol(u'Дата', 'date', editable=True),
            CStringAttribCol(u'Адрес', 'address', editable=True),
            CStringAttribCol(u'Комментарий', 'comment', editable=True)
        ], editable=True, extendable=True, itemType=PlanDate)
        self._orgCode = None

    def setDefaults(self, item):
        u""" :type item: PlanDate """
        super(CPlanDatesModel, self).setDefaults(item)
        item.orgCode = self._getOrgCode()


class CContactsModel(CIdentifiableItemModel):
    u""" Контактные телефоны МО """

    def __init__(self, parent):
        super(CContactsModel, self).__init__(parent, cols=[
            CStringAttribCol(u'Код МО', 'orgCode', editable=True),
            CStringAttribCol(u'Номер телефона', 'phone', editable=True),
            CStringAttribCol(u'Комментарий', 'comment', editable=True)
        ], editable=True, extendable=True, itemType=OrgContact)
        self._orgCode = None

    def setDefaults(self, item):
        u""" :type item: OrgContact """
        super(CContactsModel, self).setDefaults(item)
        item.orgCode = self._getOrgCode()


class CInformatedClientsModel(CIdentifiableItemModel):
    u""" Данные об информировании граждан """

    def __init__(self, parent):
        self.personCol = CItemAttribCol(u'Гражданин', 'person')
        super(CInformatedClientsModel, self).__init__(parent, cols=[
            CItemProxyCol(u'ФИО', self.personCol, 'name'),
            CItemProxyCol(u'Дата рождения', self.personCol, 'birthDate'),
            CItemAttribCol(u'Код МО', 'orgCode'),
            CItemAttribCol(u'Дата информирования', 'date'),
            CEnumAttribCol(u'Метод', 'method', InfoMethod),
            CEnumAttribCol(u'Этап', 'step', InfoStep)
        ], itemType=FactInfo)


class CClientExaminationPlanModel(CTableModel):
    u""" Списки на проф. мероприятия """

    def __init__(self, parent):
        super(CClientExaminationPlanModel, self).__init__(parent, cols=[
            CTextCol(u'Текст ошибки', ['error'], 10),
            CNameCol(u'Фамилия', ['lastName'], 20),
            CNameCol(u'Имя', ['firstName'], 20),
            CNameCol(u'Отчество', ['patrName'], 20),
            CDateCol(u'Дата рождения', ['birthDate'], 5),
            CIntCol(u'Год', ['year'], 5),
            CEnumCol(u'Месяц', ['month'], Month, 5),
            CEnumCol(u'Тип', ['kind'], ExamKind, 5),
            CEnumCol(u'Категория', ['category'], PersonCategory, 5),
            CEnumCol(u'Статус отправки cписков', ['status'], ExamStatus, 5),
            CEnumCol(u'Шаг выполнения', ['step'], ExamStep, 5, notPresentValue=u'-'),
            CEnumCol(u'Передано в ТФОМС', ['stepStatus'], ExamStatus, 5),
            CDateCol(u'Дата прохождения', ['date'], 5),
            CDateTimeCol(u'Дата отправки', ['sendDate'], 5),
            CTextCol(u'Код выполнившей МО', ['orgCode'], 5),
            CTextCol(u'Код СМО', ['insurerCode'], 5),
            CDateCol(u'Дата информирования', ['infoDate'], 5),
            CEnumCol(u'Метод информирования', ['infoMethod'], InfoMethod, 5, notPresentValue=u'-'),
            CEnumCol(u'Шаг информирования', ['infoStep'], InfoStep, 5, notPresentValue=u'-')
        ])
        self.setTable('ClientExaminationPlan')
        self._parent = parent  # type: CPlannedExaminationExchangeDialog

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        tableClientExamPlan = db.table('ClientExaminationPlan')
        tableClientPolicy = db.table('ClientPolicy')
        tableEvent = db.table('Event')
        tableInsurer = db.table('Organisation')

        table = tableClientExamPlan
        table = table.innerJoin(tableClient, tableClient['id'].eq(tableClientExamPlan['client_id']))
        table = table.leftJoin(tableClientPolicy, tableClientPolicy['id'].eq(db.func.getClientPolicyId(tableClient['id'], 1)))
        table = table.leftJoin(tableInsurer, tableInsurer['id'].eq(tableClientPolicy['insurer_id']))
        table = table.leftJoin(tableEvent, tableEvent['id'].eq(tableClientExamPlan['event_id']))

        cols = [
            tableClientExamPlan['*'],
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['birthDate'],
            tableInsurer['infisCode'].alias('insurerCode')
        ]

        self._table = table
        self._recordsCache = CTableRecordCache(db, table, cols, capacity=recordCacheCapacity)

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        if column != self._sortColumn:
            self._sortColumn = column
            self._isSorted = False
        if order != self._sortOrder:
            self._sortOrder = order
            self._isSorted = False
        if self._idList and not self._isSorted:
            self._parent.reloadClientExaminationPlan(order=self.cols()[column].fields(),
                                                     reverse=order != QtCore.Qt.AscendingOrder)
            self._isSorted = True

    def deleteRecord(self, table, itemId):
        db = QtGui.qApp.db
        tableClientExamPlan = db.table('ClientExaminationPlan')
        db.deleteRecord(tableClientExamPlan, tableClientExamPlan['id'].eq(itemId))

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.ToolTipRole:
            return super(CClientExaminationPlanModel, self).data(index, QtCore.Qt.DisplayRole)
        return super(CClientExaminationPlanModel, self).data(index, role)


class CPlannedExaminationExchangeDialog(CDialogBase, Ui_ExchangeDialog):
    def __init__(self, parent):
        super(CPlannedExaminationExchangeDialog, self).__init__(parent)
        self._orgSections = None
        self.db = QtGui.qApp.db
        self.data = CExamPlanData(self.db, QtGui.qApp.currentOrgId())
        self._srv = None
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()

    def preSetupUi(self):
        self.actOpenClientEditor = QtGui.QAction(u'Открыть рег. карту', self)
        self.actOpenClientEditor.setObjectName('actOpenClientEditor')
        self.actOpenClientEditor.setEnabled(QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))
        self.actOpenEvent = QtGui.QAction(u'Открыть обращение', self)
        self.actOpenEvent.setObjectName('actOpenEvent')
        self.actRefusalOfExamination = QtGui.QAction(u'Отказался от проф. мероприятия', self)
        self.actRefusalOfExamination.setObjectName('actRefusalOfExamination')
        self.addModels('PlanQuantities', CPlanQuantitiesModel(self))
        self.addModels('PlanDates', CPlanDatesModel(self))
        self.addModels('Contacts', CContactsModel(self))
        self.addModels('ClientExaminationPlan', CClientExaminationPlanModel(self))

    def postSetupUi(self):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        # tab planning
        self.cmbPlanningMonth.setEnum(Month, addNone=True)
        self.setModels(self.tblPlanQuantities, self.modelPlanQuantities, self.selectionModelPlanQuantities)
        self.tblPlanQuantities.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.btnGetPlanQuantities.clicked.connect(self.onGetPlanQuantities)

        self.setModels(self.tblPlanDates, self.modelPlanDates, self.selectionModelPlanDates)
        self.tblPlanDates.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblPlanDates.addPopupDelRow()
        self.btnGetPlanDates.clicked.connect(self.onGetPlanDates)
        self.btnSendPlanDates.clicked.connect(self.onSendPlanDates)

        self.setModels(self.tblContacts, self.modelContacts, self.selectionModelContacts)
        self.tblContacts.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblContacts.addPopupDelRow()
        self.btnGetContacts.clicked.connect(self.onGetContacts)
        self.btnSendContacts.clicked.connect(self.onSendContacts)

        # tab creating
        currentYear = QtCore.QDate.currentDate().year()
        self.cmbYear.setValues(range(currentYear, currentYear + 4))
        self.cmbYear.setValue(currentYear)
        self.cmbQuarter.setEnum(Quarter, addNone=True)
        self.cmbMonth.setEnum(Month, addNone=True)

        self.cmbSocStatusClass.setTable('rbSocStatusClass')
        self.cmbSocStatusType.setTable('rbSocStatusType', filter=self.getSocStatusTypeFilter('socStatus'))
        self.cmbBenefitType.setTable('rbSocStatusType', filter=self.getSocStatusTypeFilter('benefits'))

        birthYearList = self.data.getExamBirthYears(self.cmbYear.value())
        self.cmbExtExamBirthYear.setModel(CMultiSelectionListModel(birthYearList))
        self.cmbExtExamBirthYear.selectAll()

        self.cmbPreventiveExamBirthYear.setModel(CMultiSelectionListModel(range(1923, 1996, 3)))
        self.cmbPreventiveExamBirthYear.selectAll()

        self.grpExtExam.toggled.connect(self.onExportGroupChecked)
        self.grpExtExamDisabled.toggled.connect(self.onExportGroupChecked)
        self.grpPreventiveExam.toggled.connect(self.onExportGroupChecked)

        self.btnCreate.clicked.connect(self.onCreate)
        self.btnShow.clicked.connect(self.onShow)

        # tab view/updating/exchange
        self.setModels(self.tblClientExaminationPlan, self.modelClientExaminationPlan, self.selectionModelClientExaminationPlan)
        self.tblClientExaminationPlan.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblClientExaminationPlan.createPopupMenu([self.actOpenClientEditor,
                                                       self.actOpenEvent,
                                                       self.actRefusalOfExamination])
        self.connect(self.tblClientExaminationPlan.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)
        self.tblClientExaminationPlan.addPopupDelRow()
        self.connect(self.tblClientExaminationPlan._actDeleteRow, QtCore.SIGNAL('triggered()'), self.onClientExaminationPlanDeleted)

        self.actOpenClientEditor.triggered.connect(self.onOpenClientEditor)
        self.actOpenEvent.triggered.connect(self.onOpenEvent)
        self.actRefusalOfExamination.triggered.connect(self.onRefusalOfExamination)

        self.cmbOrgStructureFilter.model().setFilter(self._getOrgSectionFilter())
        self.cmbExamKind.setEnum(ExamKind, addNone=True, specialValues=ExamKindSpecials.nameMap)
        self.cmbYearFilter.setValues(range(currentYear, currentYear + 4))
        self.cmbYearFilter.setValue(currentYear)
        self.cmbQuarterFilter.setEnum(Quarter, addNone=True)
        self.cmbMonthFilter.setEnum(Month, addNone=True)

        self.btnReload.clicked.connect(self.onReload)
        self.btnUpdateLists.clicked.connect(self.onUpdateLists)
        self.btnGetFactInvoices.clicked.connect(self.onGetFactInvoices)
        self.btnSendPlanList.clicked.connect(self.onSendPlanList)
        self.btnSendPlanExecs.clicked.connect(self.onSendPlanExecs)
        self.btnGetFactInfos.clicked.connect(self.onGetFactInfos)
        self.btnExportToFile.clicked.connect(self.onExportToFile)

        self.btnClose.clicked.connect(self.onClose)

    @property
    def srv(self):
        u""" :rtype: CExamPlanServiceTFOMS """
        if self._srv is None:
            try:
                QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                self._srv = CExamPlanServiceTFOMS.getInstance(
                    logFilename=os.path.join(QtGui.qApp.logDir, 'examplan.log'),
                    timeout=20 * 60
                )
            finally:
                QtGui.qApp.restoreOverrideCursor()
        return self._srv

    def showMessage(self, message=u'', msgType=None, title=None, buttons=None):
        msg = QtGui.QMessageBox()
        msg.setIcon(msgType or QtGui.QMessageBox.Information)
        msg.setWindowTitle(title or self.windowTitle())
        msg.setText(message)
        msg.setStandardButtons(buttons or QtGui.QMessageBox.Ok)
        msg.exec_()

    def getProgressBar(self):
        pbWidth, pbHeight = 400, 40
        progressBar = QtGui.QProgressBar(self)
        progressBar.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        progressBar.setGeometry(self.geometry().center().x() - pbWidth / 2, (self.geometry().height() - pbHeight) / 2, pbWidth, pbHeight)
        return progressBar

    @staticmethod
    def updateProgressBar(progressBar, value, max, format):
        progressBar.setValue(value)
        progressBar.setMaximum(max)
        progressBar.setFormat(format)
        QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

    def showWarning(self, message=u'', title=None):
        self.showMessage(message, QtGui.QMessageBox.Warning, title)

    def _getOrgSections(self):
        if self._orgSections is None:
            self._orgSections = getOrganisationSections()
        return self._orgSections

    def _getOrgSectionFilter(self):
        return self.db.makeField('id').inlist(self._getOrgSections())

    def onGetPlanQuantities(self):
        year = self.edtPlanningYear.value()
        month = self.cmbPlanningMonth.value()

        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            quantities = self.srv.getPlanQuantities(year, month)
        except Exception as e:
            error = unicode(e)
        else:
            error = None
            self.tblPlanQuantities.model().setItems(quantities)
        finally:
            QtGui.qApp.restoreOverrideCursor()

        if error:
            self.showWarning(error)

    def onGetPlanDates(self):
        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            planDates = self.srv.getPlanDates()
        except CServiceTFOMSException as e:
            self.showWarning(unicode(e))
        else:
            self.tblPlanDates.model().setItems(planDates)
        finally:
            QtGui.qApp.restoreOverrideCursor()

    def onSendPlanDates(self):
        planDates = self.tblPlanDates.model().items()
        if not planDates:
            return

        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            resp = self.srv.sendPlanDates(planDates)
            if resp.accepted:
                planDates = self.srv.getPlanDates()
                error = None
            else:
                error = resp.errorMessage
        except CServiceTFOMSException as e:
            error = unicode(e)
        finally:
            QtGui.qApp.restoreOverrideCursor()

        if error:
            self.showWarning(error)
        else:
            self.tblPlanDates.model().setItems(planDates)
            self.showMessage(u'Успешно отправлено')

    def onGetContacts(self):
        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            contacts = self.srv.getContacts()
        except CServiceTFOMSException as e:
            self.showWarning(unicode(e))
        else:
            self.tblContacts.model().setItems(contacts)
        finally:
            QtGui.qApp.restoreOverrideCursor()

    def onSendContacts(self):
        contacts = self.tblContacts.model().items()
        if not contacts:
            return

        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            resp = self.srv.sendContacts(contacts)
            if resp.accepted:
                error = None
            else:
                error = resp.errorMessage
        except CServiceTFOMSException as e:
            error = unicode(e)
        finally:
            QtGui.qApp.restoreOverrideCursor()

        if error:
            self.showWarning(error)
        else:
            self.showMessage(u'Успешно отправлено')

    def loadPreferences(self, preferences):
        self.tblClientExaminationPlan.loadPreferences(getPref(preferences, 'tblClientExamPlan', {}))
        return CDialogBase.loadPreferences(self, preferences)

    def savePreferences(self):
        preferences = CDialogBase.savePreferences(self)
        setPref(preferences, 'tblClientExamPlan', self.tblClientExaminationPlan.savePreferences())
        return preferences

    def getSosStatusTypes(self, classFlatCode):
        tableSSC = self.db.table('rbSocStatusClass')
        tableSSCTA = self.db.table('rbSocStatusClassTypeAssoc')
        table = tableSSC.innerJoin(tableSSCTA, tableSSCTA['class_id'].eq(tableSSC['id']))
        return self.db.getIdList(table, tableSSCTA['type_id'], tableSSC['flatCode'].eq(classFlatCode))

    def getSocStatusTypeFilter(self, classFlatCode):
        return self.db.table('rbSocStatusType')['id'].inlist(self.getSosStatusTypes(classFlatCode))

    def onExportGroupChecked(self):
        self.btnCreate.setEnabled(self.grpExtExam.isChecked() or
                                  self.grpExtExamDisabled.isChecked() or
                                  self.grpPreventiveExam.isChecked())

    @QtCore.pyqtSlot(int)
    def on_cmbYear_currentIndexChanged(self, index):
        self.cmbExtExamBirthYear.model().setValues(self.data.getExamBirthYears(self.cmbYear.value()))
        self.cmbExtExamBirthYear.selectAll()

    def onCreate(self):
        year = self.cmbYear.value()
        quarter = self.cmbQuarter.value()

        selectedMap = QtGui.qApp.callWithWaitCursor(self, self.createClientExamLists)
        existsCountMap = {}
        for examKind, category in ((ExamKind.Dispensary, PersonCategory.General),
                                   (ExamKind.Dispensary, PersonCategory.HasBenefits),
                                   (ExamKind.Preventive, PersonCategory.General)):
            existsCountMap[(examKind, category)] = self.data.getClientsCount(year=year,
                                                                             quarter=quarter,
                                                                             kind=examKind,
                                                                             category=category)

        dlg = CCreateDialog(self, selectedMap, existsCountMap)
        dlg.resize(100, 100)
        if dlg.exec_():
            addedCount = QtGui.qApp.callWithWaitCursor(self, self.data.createClientExamPlan, year, quarter, selectedMap)
            self.showMessage(message=u'Успешно добавлено' if addedCount else u'Нечего добавлять',
                             title=u'Создание списков на диспансеризацию')

    def createClientExamLists(self):
        year = self.cmbYear.value()
        quarter = self.cmbQuarter.value() if self.cmbQuarter.isEnabled() else None
        month = self.cmbMonth.value() if self.cmbMonth.isEnabled() else None
        attachSynced = self.chkClientAttachSynced.isChecked()

        selected = set()
        selectedMap = {}

        if self.grpExtExamDisabled.isChecked():
            examKind = ExamKind.Dispensary
            category = PersonCategory.HasBenefits
            socStatusClassList = self.cmbSocStatusClass.value()
            socStatusTypeList = self.cmbSocStatusType.value() + self.cmbBenefitType.value()
            clientIds = self.data.selectClients(
                examKind=examKind,
                year=year,
                quarter=quarter,
                month=month,
                isDisabled=True,
                socStatusClasses=socStatusClassList,
                socStatusTypes=socStatusTypeList,
                excludeClients=selected,
                attachSynced=attachSynced
            )
            selectedMap[(examKind, category)] = clientIds
            selected |= set(clientIds)

        if self.grpExtExam.isChecked():
            examKind = ExamKind.Dispensary
            category = PersonCategory.General
            birthYearList = self.cmbExtExamBirthYear.values()
            clientIds = self.data.selectClients(
                examKind=examKind,
                year=year,
                quarter=quarter,
                month=month,
                birthYearList=birthYearList,
                excludeClients=selected,
                attachSynced=attachSynced
            )
            selectedMap[(examKind, category)] = clientIds
            selected |= set(clientIds)

        if self.grpPreventiveExam.isChecked():
            examKind = ExamKind.Preventive
            category = PersonCategory.General
            birthYearList = self.cmbPreventiveExamBirthYear.values()
            clientIds = self.data.selectClients(
                examKind=ExamKind.Preventive,
                year=year,
                quarter=quarter,
                month=month,
                birthYearList=birthYearList,
                excludeClients=selected,
                attachSynced=attachSynced
            )
            selectedMap[(examKind, category)] = clientIds
            selected |= set(clientIds)

        return selectedMap

    def onSendPlanList(self):
        chunkSize = 250  # ТФОМС рекомендует отправлять по 1000
        selectedIds = self.tblClientExaminationPlan.model().idList() if self.chkSendSelected.isChecked() else None
        planIdList = self.data.getNotSentPlanItems(selectedIds=selectedIds)
        planItemCount = len(planIdList)
        itemCount = 0
        acceptedCount = 0

        progressBar = self.getProgressBar()
        ProgressMsg = u'Отправка списков: %v/%m'

        try:
            progressBar.show()
            self.updateProgressBar(progressBar, 0, planItemCount, ProgressMsg)
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

            for idList in splitBy(planIdList, chunkSize):
                items = self.data.toPlanItemList(idList)
                resp = self.srv.sendPlanItems(items)
                if resp.accepted:
                    accepted = idList[:]
                elif resp.rejected:
                    accepted = []
                    self.data.updatePlanItem(idList, error=resp.errorMessage)
                else:
                    accepted = list(set(idList).difference(set(resp.rejectedOrders)))
                    self.data.updatePlanItemErrors(resp.orderErrors)

                itemCount += len(idList)
                acceptedCount += len(accepted)
                self.data.updatePlanItem(accepted,
                                         status=ExamStatus.Sent,
                                         error='',
                                         sendDate=QtCore.QDateTime.currentDateTime())
                self.updateProgressBar(progressBar, itemCount, planItemCount, ProgressMsg)

        except CServiceTFOMSException as e:
            error = unicode(e)
        else:
            error = None
        finally:
            QtGui.qApp.restoreOverrideCursor()
            progressBar.hide()

        self.tblClientExaminationPlan.model().recordCache().invalidate(planIdList)

        if error:
            self.showWarning(error)
        else:
            self.showMessage(u'Отправлено записей: {0}\n(успешно: {1}, с ошибками: {2})'.format(
                planItemCount,
                acceptedCount,
                planItemCount - acceptedCount
            ))

    def onSendPlanExecs(self):
        chunkSize = 250  # ТФОМС рекомендует отправлять по 1000
        selectedIds = self.tblClientExaminationPlan.model().idList() if self.chkSendSelected.isChecked() else None
        planIdList = self.data.getNotSentFactExecs(selectedIds=selectedIds)
        itemCount = 0
        factExecCount = len(planIdList)
        acceptedCount = 0

        progressBar = self.getProgressBar()
        ProgressMsg = u'Отправка списков: %v/%m'

        try:
            progressBar.show()
            self.updateProgressBar(progressBar, 0, factExecCount, ProgressMsg)
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

            for idList in splitBy(planIdList, chunkSize):
                factExecs = self.data.toFactExecList(idList)
                resp = self.srv.sendFactExecs(factExecs)
                if resp.accepted:
                    accepted = idList[:]
                elif resp.rejected:
                    accepted = []
                    self.data.updatePlanItem(idList, error=resp.errorMessage)
                else:
                    accepted = list(set(idList).difference(set(resp.rejectedOrders)))
                    self.data.updatePlanItemErrors(resp.orderErrors)

                acceptedCount += len(accepted)
                self.data.updatePlanItem(accepted,
                                         stepStatus=ExamStatus.Sent,
                                         error='',
                                         sendDate=QtCore.QDateTime.currentDateTime())

                itemCount += len(idList)
                self.updateProgressBar(progressBar, itemCount, factExecCount, ProgressMsg)

        except CServiceTFOMSException as e:
            error = unicode(e)
        else:
            error = None
        finally:
            QtGui.qApp.restoreOverrideCursor()
            progressBar.hide()

        self.tblClientExaminationPlan.model().recordCache().invalidate(planIdList)

        if error:
            self.showWarning(error)
        else:
            self.showMessage(u'Отправлено записей: {0}\n(успешно: {1}, с ошибками: {2})'.format(
                factExecCount,
                acceptedCount,
                factExecCount - acceptedCount
            ))

    def onGetFactInvoices(self):
        curDate = QtCore.QDate.currentDate()
        updated = 0
        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            for factInvoices in self.srv.iterFactInvoices(curDate.year(), curDate.month()):
                updated += self.data.processFactInvoices(factInvoices)
        except CServiceTFOMSException as e:
            self.showWarning(unicode(e))
        finally:
            QtGui.qApp.restoreOverrideCursor()

        self.showMessage(u'Обновлено записей: {0}'.format(updated))

        self.reloadClientExaminationPlan()

    def onUpdateLists(self):
        year = self.cmbYearFilter.value()
        quarter = self.cmbQuarterFilter.value()
        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            deleted, started, finished = self.data.updateClientExaminationPlan(year, quarter)
        finally:
            QtGui.qApp.restoreOverrideCursor()

        self.reloadClientExaminationPlan()

        self.showMessage(u'Списки обновлены:\n'
                         u'{0} удалено;\n'
                         u'Диспансеризация: {1} начато, {2} завершено;\n'
                         u'Проф. осмотры: {3} начато, {4} завершено.'.format(
            deleted,
            started[ExamKind.Dispensary], finished[ExamKind.Dispensary],
            started[ExamKind.Preventive], finished[ExamKind.Preventive]
        ), title=u'Списки на проф. мероприятия')

    def onShow(self):
        self.cmbYearFilter.setValue(self.cmbYear.value())
        self.cmbQuarterFilter.setValue(self.cmbQuarter.value())
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tabShow))
        self.reloadClientExaminationPlan()

    def onReload(self):
        QtGui.qApp.callWithWaitCursor(self, self.reloadClientExaminationPlan)

    def onGetFactInfos(self):
        DateRangeFrom, DateRangeTo = -7, 0
        total = 0
        updated = 0

        progressBar = self.getProgressBar()

        try:
            progressBar.show()
            self.updateProgressBar(progressBar, 0, 1, u'Запрос к БД...')
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

            insurerList = self.data.getClientExamInsurerList()
            dateRange = range(DateRangeFrom, DateRangeTo + 1)
            requestCount = 0
            requestTotal = len(insurerList) * len(dateRange)

            ProgressMsg = u'Запрос информации от {insurer} за {date} ... %p%'
            for insurerCode, insurerName in insurerList:
                for days in dateRange:
                    infoDate = QtCore.QDate.currentDate().addDays(days)
                    self.updateProgressBar(progressBar, requestCount, requestTotal,
                                           ProgressMsg.format(insurer=insurerName,
                                                              date=forceString(infoDate.toString('dd.MM.yy'))))
                    QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
                    factInfos = self.srv.getFactInfos(insurerCode, infoDate.toPyDate())
                    total += len(factInfos)
                    updated += self.data.processFactInfos(factInfos)
                    requestCount += 1

        except CServiceTFOMSException as e:
            error = unicode(e)
        else:
            error = None
        finally:
            progressBar.hide()
            QtGui.qApp.restoreOverrideCursor()

        if error:
            self.showWarning(error)
        else:
            self.showMessage(u'Получено записей: {0}, обновлено: {1}'.format(total, updated))
            self.reloadClientExaminationPlan()

    def onClose(self):
        self.close()

    @QtCore.pyqtSlot()
    def popupMenuAboutToShow(self):
        row = self.tblClientExaminationPlan.currentIndex().row()
        record = self.tblClientExaminationPlan.model().getRecordByRow(row)
        eventId = forceRef(record.value('event_id'))
        examKind = forceInt(record.value('kind'))
        nameMap = {ExamKind.Dispensary: u'диспансеризации',
                   ExamKind.Preventive: u'проф. осмотра'}
        self.actOpenEvent.setEnabled(bool(eventId))
        self.actRefusalOfExamination.setText(u'Отказался от проведения {0}'.format(nameMap.get(examKind, u'')))

    def onOpenClientEditor(self):
        row = self.tblClientExaminationPlan.currentIndex().row()
        record = self.tblClientExaminationPlan.model().getRecordByRow(row)
        clientId = forceRef(record.value('client_id'))
        self.openClientEditor(clientId)

    def onOpenEvent(self):
        row = self.tblClientExaminationPlan.currentIndex().row()
        record = self.tblClientExaminationPlan.model().getRecordByRow(row)
        eventId = forceRef(record.value('event_id'))
        editEvent(self, eventId)

    def onRefusalOfExamination(self):
        row = self.tblClientExaminationPlan.currentIndex().row()
        record = self.tblClientExaminationPlan.model().getRecordByRow(row)
        planId = forceRef(record.value('id'))
        examKind = forceInt(record.value('kind'))
        self.data.updatePlanItem(
            idList=[planId],
            stepStatus=ExamStatus.NotSent,
            step=ExamStep.P_Refused if examKind == ExamKind.Preventive else ExamStep.D1_Refused,
            date=QtCore.QDate.currentDate()
        )
        self.tblClientExaminationPlan.model().recordCache().invalidate([planId])

    @QtCore.pyqtSlot()
    def on_actRemoveCurrentRow_triggered(self):
        row = self.tblClientExaminationPlan.currentIndex().row()
        self.tblClientExaminationPlan.model().removeRow(row)
        self.updateLblCount()

    def openClientEditor(self, clientId):
        from Registry.ClientEditDialog import CClientEditDialog
        dialog = CClientEditDialog(self)
        dialog.load(clientId)
        dialog.exec_()

    @QtCore.pyqtSlot()
    def onClientExaminationPlanDeleted(self):
        self.reloadClientExaminationPlan()

    def reloadClientExaminationPlan(self, order=None, reverse=False):
        idList = self.data.selectClientExamPlan(
            year=self.cmbYearFilter.value(),
            quarter=self.cmbQuarterFilter.value() if self.cmbQuarterFilter.isEnabled() else None,
            month=self.cmbMonthFilter.value() if self.cmbMonthFilter.isEnabled() else None,
            examKind=self.cmbExamKind.value(),
            orgStructureId=self.cmbOrgStructureFilter.value(),
            hasErrors=self.chkHasErrors.isChecked(),
            notFinished=self.chkNotFinished.isChecked(),
            order=order
        )
        if reverse:
            idList = idList[::-1]
        self.tblClientExaminationPlan.model().setIdList(idList)
        self.lblCount.setText(u'Записей в таблице: {0}'.format(len(idList)))

    def onExportToFile(self):
        from library import xlwt

        filename = forceString(QtGui.QFileDialog.getSaveFileName(self, u'Выберите имя файла', QtCore.QDir.homePath(), u'XLS файл (*.xls)'))
        if filename:
            if not filename.endswith(u'.xls'):
                filename += u'.xls'
        else:
            return

        progressBar = self.getProgressBar()
        ProgressMsg = u'Сохранение... %p%'

        try:
            progressBar.show()
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

            self.updateProgressBar(progressBar, 0, 1, u'Запрос к БД ...')
            idList = self.tblClientExaminationPlan.model().idList()
            itemCount = len(idList)

            wb = xlwt.Workbook(encoding='utf-8')
            sh = wb.add_sheet('List1')
            for col, name in enumerate((u'Код пациента',
                                        u'ФИО пациента',
                                        u'Дата рождения',
                                        u'Вид проф. мероприятия',
                                        u'Год прохождения',
                                        u'Месяц',
                                        u'Ошибка')):
                sh.write(0, col, name)

            self.updateProgressBar(progressBar, 0, itemCount, ProgressMsg)
            for row, rec in enumerate(self.data.toExportData(idList), start=1):
                progressBar.setValue(row)
                for col, value in enumerate((
                        forceInt(rec.value('clientId')),
                        formatName(rec.value('lastName'), rec.value('firstName'), rec.value('patrName')),
                        forceString(forceDate(rec.value('birthDate')).toString('dd.MM.yyyy')),
                        ExamKind.getName(forceRef(rec.value('kind'))),
                        forceInt(rec.value('year')),
                        Month.getName(forceRef(rec.value('month'))),
                        forceString(rec.value('error'))
                )):
                    sh.write(row, col, value)

            wb.save(filename)

        finally:
            progressBar.hide()
            QtGui.qApp.restoreOverrideCursor()
