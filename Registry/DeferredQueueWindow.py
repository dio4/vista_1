# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants
from Registry.FindClient import findClient, findClientRecord
from Registry.RegistryQueueModels import CQueueModel, CVisitByQueueModel
from Registry.Utils import formatAddressInt, getAddress, getClientAddress, getClientInfo, getClientPhonesEx
from Reports.ReportBase import CReportBase, createTable
from Reports.ReportResultClientList import CResultClientList
from Reports.ReportView import CReportViewDialog
from Ui_CreateDeferredQueue import Ui_CreateDeferredQueueDialog
from Ui_DeferredQueueWindow import Ui_DeferredQueueWidget
from Users.Rights import urAddDeferredQueueItems, urEditDeferredQueueItems
from library.DateEdit import CDateEdit
from library.DialogBase import CDialogBase, CConstructHelperMixin
from library.KeyValueTable import CKeyValueModel
from library.PreferencesMixin import CDialogPreferencesMixin
from library.TableModel import CSortFilterProxyTableModel, CTableModel, CCol, CDateCol, CRefBookCol, \
    CTextCol
from library.TableView import CTableView
from library.Utils import forceBool, forceDate, forceDateTime, forceInt, forceRef, forceString, \
    forceStringEx, toVariant, getVal, calcAgeTuple, formatAgeTuple, formatName
from library.crbcombobox import CRBComboBox
from library.database import CTableRecordCache

EDITABLE_STATUS = [1, 2]


class CDeferredQueueModel(CTableModel):
    class CLocClientColumn(CCol):
        def __init__(self, title, fields, defaultWidth, cache):
            CCol.__init__(self, title, fields, defaultWidth, 'l')

            self.clientCache = cache

        def format(self, values):
            clientId = forceRef(values[0])
            record = self.clientCache.get(clientId)
            if record:
                name = formatName(record.value('lastName'),
                                  record.value('firstName'),
                                  record.value('patrName'))
                return toVariant(name)
            else:
                return CCol.invalid

    class CLocOrgColumn(CCol):
        def __init__(self, title, fields, defaultWidth, cache):
            CCol.__init__(self, title, fields, defaultWidth, 'l')
            db = QtGui.qApp.db
            self.clientCache = cache
            self.personCache = CTableRecordCache(db, db.table('Person'), 'id, orgStructure_id')
            self.orgCache = CTableRecordCache(db, db.table('OrgStructure'), 'id, code')
            self.clientCache = cache

        def format(self, values):
            clientId = forceRef(values[0])
            record = self.clientCache.get(clientId)
            if record:
                person_id = forceRef(record.value('person_id'))
                if person_id:
                    return toVariant(
                        self.orgCache.get(
                            forceRef(
                                self.personCache.get(person_id).value('orgStructure_id')
                            )
                        ).value('code')
                    )
                else:
                    orgStructure_id = forceRef(record.value('orgStructure_id'))
                    if orgStructure_id:
                        return toVariant(
                            self.orgCache.get(orgStructure_id).value('code')
                        )
                    else:
                        return CCol.invalid
            else:
                return CCol.invalid

    class CLocClientId(CCol):
        def __init__(self, title, fields, defaultWidth, cache):
            CCol.__init__(self, title, fields, defaultWidth, 'l')

            self.clientCache = cache

        def format(self, values):
            clientId = forceRef(values[0])

            if clientId:
                return toVariant(clientId)
            else:
                CCol.invalid

    class CLocClientAgeColumn(CCol):
        mapClientIdToAgeTuple = {}

        def __init__(self, title, fields, defaultWidth, cache):
            CCol.__init__(self, title, fields, defaultWidth, 'l')
            self.clientCache = cache

        def format(self, values):
            clientId = forceRef(values[0])
            ageTuple, birthDate = self.getAgeById(clientId)
            if ageTuple and birthDate:
                age = formatAgeTuple(ageTuple, birthDate, None)
                stringBirthDate = birthDate.toString("dd.MM.yyyy")
                stringBirthAge = "%s (%s)" % (stringBirthDate, age)
                return stringBirthAge
            else:
                return CCol.invalid

        def getAgeById(self, clientId):
            record = self.clientCache.get(clientId)
            if record:
                if clientId in self.mapClientIdToAgeTuple:
                    ageTuple, birthDate = self.mapClientIdToAgeTuple[clientId]
                else:
                    birthDate = forceDate(record.value('birthDate'))
                    ageTuple = calcAgeTuple(birthDate, None)
                    self.mapClientIdToAgeTuple[clientId] = (ageTuple, birthDate)
                return ageTuple, birthDate
            else:
                return None, None

    ciCode = 0
    ciStatus = 1
    ciClientName = 2
    ciClientAge = 3
    ciPersonOrgStructure = 4
    ciSpeciality = 5
    ciPerson = 6
    ciMaxDate = 7
    ciNote = 8

    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        db = QtGui.qApp.db

        self.clientCache = CTableRecordCache(db, db.table('Client'),
                                             'lastName, firstName, patrName, birthDate, sex, SNILS')
        self.defCache = CTableRecordCache(db, db.table('DeferredQueue'), 'id, person_id, orgStructure_id, client_id')

        self.addColumn(CDeferredQueueModel.CLocClientId(u'Код', ['client_id'], 15, self.clientCache))  # Temp

        self.addColumn(CRefBookCol(u'Статус', ['status_id'], 'rbDeferredQueueStatus', 300))
        self.addColumn(CDeferredQueueModel.CLocClientColumn(u'Ф.И.О. пациента', ['client_id'], 20, self.clientCache))
        self.addColumn(CDeferredQueueModel.CLocClientAgeColumn(u'Возраст', ['client_id'], 20, self.clientCache))
        self.addColumn(CDeferredQueueModel.CLocOrgColumn(u'Подразделение', ['id'], 20, self.defCache))

        # self.addColumn(CDesignationCol(u'Подразделение', ['person_id'],[('Person', 'orgStructure_id'), ('OrgStructure', 'code')], 10))
        # self.addColumn(
        #    CRefDeferredQueueOrgCol(u'Подразделение', ['orgStructure_id'], 'OrgStructure',
        #                    10))

        self.addColumn(CRefBookCol(u'Специальность', ['speciality_id'], 'rbSpeciality', 20))
        self.addColumn(CRefBookCol(u'Врач', ['person_id'], 'vrbPerson', 15))

        self.addColumn(CDateCol(u'Максимальная дата', ['maxDate'], 10))
        self.addColumn(CTextCol(u'Комментарий', ['comment'], 5))

        self.loadField('createDatetime')
        self.loadField('createPerson_id')

        self.loadField('modifyDatetime')
        self.loadField('modifyPerson_id')

        self.loadField('action_id')
        self.loadField('orgStructure_id')
        self.setTable('DeferredQueue')

        self._personToColorCache = {}
        self._specialityToColorCache = {}

    def data(self, index, role=QtCore.Qt.DisplayRole):

        if not index.isValid():
            return QtCore.QVariant()

        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:  ### or role == Qt.EditRole:
            (col, values) = self.getRecordValues(column, row)
            return col.format(values)
        elif role == QtCore.Qt.TextAlignmentRole:
            col = self._cols[column]
            return col.alignment()
        elif role == QtCore.Qt.CheckStateRole:
            (col, values) = self.getRecordValues(column, row)
            return col.checked(values)
        elif role == QtCore.Qt.ForegroundRole:
            (col, values) = self.getRecordValues(column, row)
            return col.getForegroundColor(values)
        elif role == QtCore.Qt.BackgroundRole:
            db = QtGui.qApp.db
            record = self.getRecordByRow(row)
            if not forceRef(record.value('status_id')) in [1, 2]:
                return CCol.invalid
            if column == self.ciSpeciality:
                (col, values) = self.getRecordValues(column, row)
                id = forceRef(values[0])

                if id not in self._specialityToColorCache:
                    stmt = '''SELECT id FROM Person WHERE Person.speciality_id = %s AND Person.ambPlan > 0''' % id
                    query = db.query(stmt)
                    if query.next():
                        self._specialityToColorCache[id] = QtCore.QVariant(QtGui.QBrush(QtGui.QColor(0, 255, 0)))
                    else:
                        self._specialityToColorCache[id] = QtCore.QVariant(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                return self._specialityToColorCache[id]
            elif column == self.ciPerson:
                (col, values) = self.getRecordValues(column, row)
                id = forceRef(values[0])
                if id:
                    if id not in self._personToColorCache:
                        stmt = '''SELECT id FROM Person WHERE Person.id = %s AND Person.ambPlan > 0''' % id
                        query = db.query(stmt)
                        if query.next():
                            self._personToColorCache[id] = QtCore.QVariant(QtGui.QBrush(QtGui.QColor(0, 255, 0)))
                        else:
                            self._personToColorCache[id] = QtCore.QVariant(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                    return self._personToColorCache[id]
                return CCol.invalid
        return QtCore.QVariant()


class CDeferredQueueSortFilterProxyModel(CSortFilterProxyTableModel):
    # Переопределяем метод сравнения, использующийся при сортировке.
    def lessThan(self, left, right=u''):
        (col, leftValues) = self.getRecordValues(left.column(), left.row())
        (col2, rightValues) = self.getRecordValues(right.column(), right.row())
        if forceInt(left.column()) == CDeferredQueueModel.ciClientAge:
            leftClient = forceRef(leftValues[0])
            leftAge, leftBirthDate = col.getAgeById(leftClient)
            rightClient = forceRef(rightValues[0])
            rightAge, rightBirthDate = col2.getAgeById(rightClient)
            if leftAge and rightAge:
                return leftAge[0] < rightAge[0]
            record = leftValues[1]

        elif left.column() == CDeferredQueueModel.ciMaxDate:
            leftValue = leftValues[0]
            rightValue = rightValues[0]
            if leftValue and rightValue and leftValue.type() in (
            QtCore.QVariant.Date, QtCore.QVariant.DateTime) and rightValue.type() in (
            QtCore.QVariant.Date, QtCore.QVariant.DateTime):
                rightDate = rightValue.toDate()
                leftDate = leftValue.toDate()
                return leftDate < rightDate

        return super(CSortFilterProxyTableModel, self).lessThan(left, right)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        return self.sourceModel().data(self.mapToSource(index), role)


class CDeferredQueueWindow(QtGui.QScrollArea, Ui_DeferredQueueWidget, CDialogPreferencesMixin, CConstructHelperMixin):
    u"""
        Окно для просмотра записей в журнале отложенного спроса,
        обеспечивает возможность фильтрации, сортировки, редактирования
        записей в журнале и создания новых записей.
    """

    def __init__(self, parent):
        QtGui.QScrollArea.__init__(self, parent)
        self.updateDeferredQueueRequest = False
        # self.currentRecordId = None
        # self.currentRecordStatus = None
        self.currentRecord = None
        self.__filter = {}

        self.addModels('DeferredQueue', CDeferredQueueModel(self))
        self.addModels('KeyValue', CKeyValueModel(self))
        self.addModels('Queue', CQueueModel(self))
        self.addModels('VisitByQueue', CVisitByQueueModel(self))

        self.setWidgetResizable(True)
        self.setupUi(self)

        self.cmbFilterSpeciality.setTable('rbSpeciality', False)
        self.cmbFilterSpeciality.setShowFields(CRBComboBox.showName)

        self.cmbStatus.setTable('rbDeferredQueueStatus', False, filter='deleted=0 AND isSelectable=1')
        self.cmbStatus.setShowFields(CRBComboBox.showName)

        self.cmbFilterStatus.setTable('rbDeferredQueueStatus', False, filter='deleted=0 AND isSelectable=1')
        self.cmbFilterStatus.setShowFields(CRBComboBox.showName)

        self.btnCheckAll.setEnabled(QtGui.qApp.userHasRight(urEditDeferredQueueItems))
        self.btnResetRecord.setEnabled(QtGui.qApp.userHasRight(urEditDeferredQueueItems))
        self.btnSaveRecord.setEnabled(QtGui.qApp.userHasRight(urEditDeferredQueueItems))
        self.btnAddRecord.setEnabled(QtGui.qApp.userHasRight(urAddDeferredQueueItems))

        # self.cmbFilterCreatePerson.setTable('DeferredQueue', True)

        createPersonIdList = list(set(QtGui.qApp.db.getDistinctIdList('DeferredQueue', 'createPerson_id')))
        stringList = map(str, createPersonIdList)
        self.cmbFilterCreatePerson.addItems([''] + stringList)

        # self.cmbFilterCreatePerson.setNameField('createPerson_id')
        # self.cmbFilterCreatePerson.setFilter('id IN MAX(SELECT DISTINCT createPerson_id FROM DeferredQueue)')

        self.filterModelProxy = CDeferredQueueSortFilterProxyModel(self)
        self.filterModelProxy.setSourceModel(self.modelDeferredQueue)
        self.filterModelProxy.setFilterKeyColumn(1)
        self.filterModelProxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        tableSelectionModel = QtGui.QItemSelectionModel(self.filterModelProxy, self)
        self.__setattr__('tableSelectionModel', tableSelectionModel)
        tableSelectionModel.setObjectName('tableSelectionModel')
        self.tblDeferredQueue.viewport().installEventFilter(CDeferredQueueWindow.CLocSelectionFilter(self, 'mouse'))
        self.tblDeferredQueue.installEventFilter(CDeferredQueueWindow.CLocSelectionFilter(self, 'key'))
        self.setModels(self.tblDeferredQueue, self.filterModelProxy, self.tableSelectionModel)
        self.setModels(self.tblComments, self.modelKeyValue, self.selectionModelKeyValue)
        self.setModels(self.tblQueue, self.modelQueue, self.selectionModelQueue)
        self.setModels(self.tblVisitByQueue, self.modelVisitByQueue, self.selectionModelVisitByQueue)
        self.tblDeferredQueue.setSortingEnabled(True)

        initialFilter = {'listLength': 250}
        defaultOrgStructureId = QtGui.qApp.currentOrgStructureId()
        if defaultOrgStructureId:
            self.chkFilterPersonOrgStructure.setChecked(True)
            self.cmbFilterPersonOrgStructure.setEnabled(True)
            self.cmbFilterPersonOrgStructure.setValue(defaultOrgStructureId)
            initialFilter['personOrgStructure_id'] = defaultOrgStructureId
            self.orgStructures = getOrgStructureDescendants(QtGui.qApp.currentOrgStructureId())
        else:
            self.orgStructures = []

        if QtGui.qApp.isRestrictByUserOS() and QtGui.qApp.userOrgStructureId:
            self.userOrgStructures = getOrgStructureDescendants(QtGui.qApp.userOrgStructureId)
        else:
            self.userOrgStructures = None

        self.oldRecordValues = [forceInt(self.cmbStatus.value()),
                                forceString(self.edtAction.text()),
                                forceString(self.edtMaxDate.text()),
                                self.tblComments.model().items()
                                ]

        self.updateTableDeferredQueue(initialFilter)

        self.loadDialogPreferences()

        self.chkList = [
            # (self.chkFilterId,        [self.edtFilterId]),
            (self.chkFilterStatus, [self.cmbFilterStatus]),
            (self.chkFilterClient, [self.edtFilterClient, self.btnFilterClient]),
            (self.chkFilterSpeciality, [self.cmbFilterSpeciality]),
            (self.chkFilterOrgStructure, [self.cmbFilterOrgStructure]),
            (self.chkFilterPersonOrgStructure, [self.cmbFilterPersonOrgStructure]),
            (self.chkFilterPerson, [self.cmbFilterPerson]),
            (self.chkFilterMaxDate, [self.edtFilterBegMaxDate, self.edtFilterEndMaxDate]),
            (self.chkFilterCreateDate, [self.edtFilterBegCreateDate, self.edtFilterEndCreateDate]),
            (self.chkFilterCreatePerson, [self.cmbFilterCreatePerson]),
            (self.chkFilterModifyDate, [self.edtFilterBegModifyDate, self.edtFilterEndModifyDate]),
            (self.chkFilterModifyPerson, [self.cmbFilterModifyPerson]),
            (self.chkFilterAge, [self.edtFilterAgeFrom, self.edtFilterAgeTo, self.lblFilterAge1, self.lblFilterAge2])
        ]

        self.connect(self.tableSelectionModel, QtCore.SIGNAL('currentRowChanged(QModelIndex, QModelIndex)'),
                     self.on_tableSelectionModel_currentRowChanged)
        self.connect(QtGui.qApp, QtCore.SIGNAL('currentClientInfoChanged()'), self.checkCurrentRecord)
        self.connect(self.edtFilterAgeFrom, QtCore.SIGNAL('editingFinished()'), self.on_edtAgeFrom_editingFinished)
        self.connect(self.edtFilterAgeTo, QtCore.SIGNAL('editingFinished()'), self.on_edtAgeTo_editingFinished)

        self.actResultClientList = QtGui.QAction(u'Результаты записи', self)

        self.actResultClientList.setObjectName('actResultClientList')
        self.actClientList = QtGui.QAction(u'Список пациентов', self)
        self.actClientList.setObjectName('actClientList')
        self.mnuPrint = QtGui.QMenu(self)
        self.mnuPrint.setObjectName('mnuPrint')
        self.mnuPrint.addAction(self.actResultClientList)
        self.mnuPrint.addAction(self.actClientList)
        self.btnPrintTable.setMenu(self.mnuPrint)

        QtCore.QObject.connect(
            self.actClientList, QtCore.SIGNAL('triggered()'), self.on_actClientList_triggered)
        QtCore.QObject.connect(
            self.actResultClientList, QtCore.SIGNAL('triggered()'), self.on_actResultClientList_triggered)

    def closeEvent(self, event):
        self.saveDialogPreferences()
        QtGui.QScrollArea.closeEvent(self, event)
        QtGui.qApp.mainWindow.deferredQueue = None

    def setCurrentQueueId(self, queueId):
        self.tblDeferredQueue.setCurrentItemId(queueId)

    def addEqCond(self, cond, table, fieldName, filter, name):
        if name in filter:
            cond.append(table[fieldName].eq(filter[name]))

    def addDateCond(self, cond, table, fieldName, filter, begDateName, endDateName):
        begDate = filter.get(begDateName, None)
        if begDate and not begDate.isNull():
            cond.append(table[fieldName].ge(begDate))
        endDate = filter.get(endDateName, None)
        if endDate and not endDate.isNull():
            cond.append(table[fieldName].lt(endDate.addDays(1)))

    def updateTableDeferredQueue(self, filter, posToId=None):
        """
            Обновление содержимого таблицы в соответствии с фильтром.
        """
        db = QtGui.qApp.db

        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

            self.__filter = filter

            tableDeferredQueue = db.table('DeferredQueue')

            table = tableDeferredQueue

            cond = []

            self.addEqCond(cond, tableDeferredQueue, 'id', filter, 'id')
            statusPreference = forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'HideFinishedDeferred', False))
            if 'status' in filter:
                self.addEqCond(cond, tableDeferredQueue, 'status_id', filter, 'status')
            elif statusPreference:
                cond.append(tableDeferredQueue['status_id'].inlist([1, 2]))
            self.addEqCond(cond, tableDeferredQueue, 'client_id', filter, 'client')
            self.addEqCond(cond, tableDeferredQueue, 'speciality_id', filter, 'speciality')
            self.addEqCond(cond, tableDeferredQueue, 'person_id', filter, 'person')
            endDatePreference = forceInt(getVal(QtGui.qApp.preferences.appPrefs, 'DeferredDaysAfter', 0))
            if 'begMaxDate' in filter or 'endMaxDate' in filter:
                self.addDateCond(cond, tableDeferredQueue, 'maxDate', filter, 'begMaxDate', 'endMaxDate')
            elif endDatePreference:
                cond.append(tableDeferredQueue['maxDate'].dateLe(QtCore.QDate.currentDate().addDays(endDatePreference)))

            self.addEqCond(cond, tableDeferredQueue, 'createPerson_id', filter, 'createPersonIdEx')
            begDatePreference = forceInt(getVal(QtGui.qApp.preferences.appPrefs, 'DeferredDaysBefore', 0))
            if 'begCreateDateEx' in filter or 'endCreateDateEx' in filter:
                self.addDateCond(cond, tableDeferredQueue, 'createDatetime', filter, 'begCreateDateEx',
                                 'endCreateDateEx')
            elif begDatePreference:
                cond.append(
                    tableDeferredQueue['createDatetime'].dateGe(QtCore.QDate.currentDate().addDays(begDatePreference)))
            self.addEqCond(cond, tableDeferredQueue, 'modifyPerson_id', filter, 'modifyPersonIdEx')
            self.addDateCond(cond, tableDeferredQueue, 'modifyDatetime', filter, 'begModifyDateEx', 'endModifyDateEx')
            if self.userOrgStructures:
                tableVRBPerson = db.table('vrbPerson')
                table = table.leftJoin(tableVRBPerson, tableVRBPerson['id'].eq(tableDeferredQueue['person_id']))
                cond.append(tableVRBPerson['orgStructure_id'].inlist(self.userOrgStructures))

            if 'ageFrom' in filter:
                tableClient = db.table('Client')
                table = table.leftJoin(tableClient, tableClient['id'].eq(tableDeferredQueue['client_id']))
                currentDate = db.formatDate(QtCore.QDate.currentDate())
                cond.append('%s >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)' % (currentDate, filter['ageFrom']))
                cond.append('%s < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)' % (
                currentDate, (filter['ageTo'] + 1)))

            if filter.get('personOrgStructure_id', None):
                if not self.userOrgStructures:
                    tableVRBPerson = db.table('vrbPerson')
                    table = table.leftJoin(tableVRBPerson, tableVRBPerson['id'].eq(tableDeferredQueue['person_id']))
                cond.append(db.joinOr([
                    tableDeferredQueue['orgStructure_id'].inlist(getOrgStructureDescendants(filter['personOrgStructure_id'])),
                    tableVRBPerson['orgStructure_id'].eq(filter['personOrgStructure_id'])
                ]))

            if filter.get('orgStructure_id', None):
                tableClientAttach = db.table('ClientAttach')
                table = table.leftJoin(tableClientAttach,
                                       tableClientAttach['client_id'].eq(tableDeferredQueue['client_id']))
                orgStructIdList = getOrgStructureDescendants(filter['orgStructure_id'])
                cond.append(tableClientAttach['orgStructure_id'].inlist(orgStructIdList))

            if self.orgStructures and not self.chkFilterOrgStructure and not self.chkFilterPersonOrgStructure:
                tableClientAttach = db.table('ClientAttach')
                table = table.leftJoin(tableClientAttach,
                                       tableClientAttach['client_id'].eq(tableDeferredQueue['client_id']))
                subCond = [tableClientAttach['orgStructure_id'].inlist(self.orgStructures),
                           tableClientAttach['orgStructure_id'].isNull()]
                cond.append(db.joinOr(subCond))
                cond.append(tableClientAttach['deleted'].eq(0))

            if 'listLength' in filter:
                recordsLimit = filter['listLength']
            else:
                recordsLimit = None

            getIdList = db.getDistinctIdList
            idList = getIdList(table,
                               tableDeferredQueue['id'].name(),
                               cond,
                               [tableDeferredQueue['status_id'].name(), tableDeferredQueue['maxDate'].name()],
                               limit=recordsLimit)
            if len(idList) < recordsLimit:
                recordsCount = len(idList)
            else:
                getCount = db.getCount
                recordsCount = getCount(table, tableDeferredQueue['id'].name(), cond)

            tmplist = []
            self.tblDeferredQueue.setIdList(idList, posToId, recordsCount)

        finally:
            QtGui.QApplication.restoreOverrideCursor()

        if not len(idList):
            # self.curentRecordId = None
            # self.currentRecurdStatus = None
            self.btnCheckRecord.setEnabled(False)
            self.updateRecordDetails()
        self.focusDeferredQueue()
        self.updateDeferredQueueRequest = False
        self.on_tableSelectionModel_currentRowChanged(self.tblDeferredQueue.currentIndex(), None)

    def focusDeferredQueue(self):
        self.tblDeferredQueue.setFocus(QtCore.Qt.TabFocusReason)

    def findControlledByChk(self, chk):
        for s in self.chkList:
            if s[0] == chk:
                return s[1]
        return None

    def activateFilterWidgets(self, alist):
        if alist:
            for s in alist:
                s.setEnabled(True)
                if isinstance(s, (QtGui.QLineEdit, CDateEdit)):
                    s.selectAll()
            alist[0].setFocus(QtCore.Qt.ShortcutFocusReason)
            alist[0].update()

    def deactivateFilterWidgets(self, alist):
        for s in alist:
            s.setEnabled(False)

    def onChkFilterClicked(self, chk, checked):
        controlled = self.findControlledByChk(chk)
        if checked:
            self.activateFilterWidgets(controlled)
        else:
            self.deactivateFilterWidgets(controlled)

    def recordId(self, index):
        return self.tblDeferredQueue.itemId(index)

    def getRecordByRow(self, row):
        return self.tblDeferredQueue.model().getRecordByRow(row)

    def currentRecordStatus(self):
        return forceRef(self.currentRecord.value('status_id'))

    def currentRecordId(self):
        return forceInt(self.currentRecord.value('id'))

    def updateRecordDetails(self):
        db = QtGui.qApp.db
        table = db.table('DeferredQueue')
        record = self.currentRecord

        self.tblDeferredQueue

        if record:
            self.lblCreateDate.setText(forceString(record.value('createDatetime')))
            self.lblCreatePerson.setText(forceString(record.value('createPerson_id')))
            self.lblModifyDate.setText(forceString(record.value('modifyDatetime')))
            modifyPerson = forceInt(forceString(record.value('modifyPerson_id')))
            self.lblModifyPerson.setText(forceString(
                db.translate('vrbPersonWithSpeciality', 'id', modifyPerson, 'name')) if modifyPerson else '')
            self.cmbStatus.setValue(forceInt(record.value('status_id')))
            actionId = forceRef(record.value('action_id'))
            if actionId:
                self.edtAction.setText(forceString(actionId))
                self.edtAction.setReadOnly(True)
            else:
                self.edtAction.setText('')
                # self.lblAction_id.setText(forceString(actionId) if actionId else '')
            maxDate = forceDate(record.value('maxDate'))
            if maxDate:
                self.edtMaxDate.setDate(maxDate)
            else:
                self.edtMaxDate.lineEdit.setText('')
            specialityId = forceInt(record.value('speciality_id'))
            speciality = forceString(db.translate('rbSpeciality', 'id', specialityId, 'name')) if specialityId else ''
            self.lblSpeciality.setText(speciality)
            person = forceInt(forceString(record.value('person_id')))
            self.lblPerson.setText(
                forceString(db.translate('vrbPersonWithSpeciality', 'id', person, 'name')) if person else '')
            comments = self.parseComments(forceString(record.value('comment')))
            self.tblComments.model().setItems(comments)
            # self.edtComments.setText(forceString(record.value('comment')))
            clientId = forceRef(record.value('client_id'))

            client = self.tblDeferredQueue.model().sourceModel().clientCache.get(clientId)
            if client:
                name = formatName(client.value('lastName'),
                                  client.value('firstName'),
                                  client.value('patrName'))
                self.edtClient.setText(name)
            editable = self.cmbStatus.value() in EDITABLE_STATUS and QtGui.qApp.userHasRight(urEditDeferredQueueItems)
            self.cmbStatus.setEnabled(editable)
            self.edtMaxDate.setEnabled(editable)
            self.tblComments.model().setEditable(editable)
            # self.edtComments.setEnabled(editable)
            if not actionId:
                self.edtAction.setReadOnly(False)
                self.edtAction.setEnabled(editable)
            else:
                self.edtAction.setEnabled(True)
                if editable:
                    self.edtAction.setReadOnly(False)
                else:
                    self.edtAction.setReadOnly(True)
            regAddrRecord = getClientAddress(clientId, 0)

            regAddr = formatAddressInt(getAddress(regAddrRecord.value('address_id'),
                                                  regAddrRecord.value('freeInput'))) if regAddrRecord else None
            locAddrRecord = getClientAddress(clientId, 1)
            locAddr = formatAddressInt(getAddress(locAddrRecord.value('address_id'),
                                                  locAddrRecord.value('freeInput'))) if locAddrRecord else None

            self.lblLocAddress.setText(locAddr if locAddr else u'не указано')
            self.lblRegAddress.setText(regAddr if regAddr else u'не указано')

            clientContacts = getClientPhonesEx(clientId)
            self.lblContacts.setText(clientContacts if clientContacts else u'')

            self.oldRecordValues = [forceInt(record.value('status_id')),
                                    forceString(actionId) if actionId else '',
                                    forceString(self.edtMaxDate.text()),
                                    comments
                                    ]
        else:
            self.lblCreateDate.setText('')
            self.lblCreatePerson.setText('')
            self.lblModifyDate.setText('')
            self.lblModifyPerson.setText('')
            self.lblSpeciality.setText('')
            self.lblPerson.setText('')
            self.edtMaxDate.lineEdit.setText('')
            self.edtClient.setText('')
            # self.edtComments.setText('')
            self.tblComments.model().setItems([])
            self.cmbStatus.setValue(None)
            self.edtAction.setText('')
            self.edtMaxDate.setEnabled(False)
            self.cmbStatus.setEnabled(False)
            # self.edtComments.setEnabled(False)
            self.tblComments.model().setEditable(False)
            self.edtAction.setEnabled(False)
            self.lblContacts.setText('')
            self.lblLocAddress.setText('')
            self.lblRegAddress.setText('')
            self.oldRecordValues = ['', '', '', '']

    def parseComments(self, comments):
        lines = comments.split('\n')
        pairs = []
        prevPair = None
        for line in lines:
            delimiterPos = line.find(':')
            if delimiterPos >= 0:
                key = line[:delimiterPos].strip()
                value = line[delimiterPos + 1:].strip()
                if prevPair:
                    pairs.append(prevPair)
                prevPair = (key, value)
            elif prevPair:
                key, value = prevPair
                prevPair = (key, value + line.strip())
            else:
                prevPair = (line, '')
        if prevPair:
            pairs.append(prevPair)
        return pairs

    def checkAllRecords(self):
        acceptAll = False
        model = self.tblDeferredQueue.model().sourceModel()
        userId = toVariant(QtGui.qApp.userId)
        db = QtGui.qApp.db
        statusId = db.translate('rbDeferredQueueStatus', 'code', 2, 'id')
        for id in model.idList():
            record = model.getRecordById(id)
            if forceRef(record.value('status_id')) in [1, 2]:
                accept = False
                specialityId = forceRef(record.value('speciality_id'))
                clientId = forceRef(record.value('client_id'))
                maxDate = forceDate(record.value('maxDate'))
                personId = forceRef(record.value('person_id'))
                recordCreateDateTime = forceDateTime(record.value('createDatetime'))
                actionId, fullMatch = self.findSameAction(specialityId, clientId, recordCreateDateTime, maxDate,
                                                          personId)
                if not fullMatch and not acceptAll:
                    clientRecord = self.clientCache.get(clientId)
                    clientName = formatName(forceString(clientRecord.value('lastName')),
                                            forceString(clientRecord.value('firstName')),
                                            forceString(clientRecord.value('patrName')))
                    messageBox = QtGui.QMessageBox.question(self, u'Внимание!',
                                                            u'Обнаружена запись пациента %s к другому врачу той же специальности. Принять?' % clientName,
                                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.YesToAll | QtGui.QMessageBox.No,
                                                            QtGui.QMessageBox.No)
                    if messageBox == QtGui.QMessageBox.YesToAll:
                        accept = True
                        acceptAll = True
                    elif messageBox == QtGui.QMessageBox.Yes:
                        accept = True
                else:
                    accept = True
                if actionId and (accept or acceptAll):
                    now = toVariant(QtCore.QDateTime.currentDateTime())
                    record.setValue('status_id', forceRef(statusId))
                    record.setValue('action_id', actionId)
                    record.setValue('modifyDatetime', now)
                    record.setValue('modifyPerson_id', userId)
                    db.updateRecord('DeferredQueue', record)
                    self.updateTableDeferredQueue(self.__filter)

    def checkCurrentRecord(self):
        if not QtGui.qApp.mainWindow.deferredQueue:
            return
        record = self.currentRecord
        specialityId = forceRef(record.value('speciality_id'))
        clientId = forceRef(record.value('client_id'))
        recordCreateDateTime = forceDateTime(record.value('createDatetime'))
        maxDate = forceDate(record.value('maxDate'))
        personId = forceRef(record.value('person_id'))
        actionId, fullMatch = self.findSameAction(specialityId, clientId, recordCreateDateTime, maxDate, personId)
        if actionId and not fullMatch:
            accept = QtGui.QMessageBox.question(self, u'Внимание!',
                                                u'Обнаружена запись к другому врачу той же специальности. Принять?',
                                                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                                QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes
        else:
            accept = True
        if actionId and accept:
            db = QtGui.qApp.db
            now = toVariant(QtCore.QDateTime.currentDateTime())
            userId = toVariant(QtGui.qApp.userId)
            statusId = db.translate('rbDeferredQueueStatus', 'code', 2, 'id')
            record.setValue('status_id', forceRef(statusId))
            record.setValue('action_id', actionId)
            record.setValue('modifyDatetime', now)
            record.setValue('modifyPerson_id', userId)
            db.updateRecord('DeferredQueue', record)
            self.updateTableDeferredQueue(self.__filter)

    def findSameAction(self, specialityId, clientId, recordCreateDateTime, maxDate, personId=None):
        if specialityId and clientId and recordCreateDateTime:
            db = QtGui.qApp.db
            etcQueue = 'queue'
            atcQueue = 'queue'
            tableEvent = db.table('Event')
            tableAction = db.table('Action')
            tablePerson = db.table('Person')
            tableEventType = db.table('EventType')
            tableAPAction = db.table('ActionProperty_Action')
            cols = [tableAction['id'].name(),
                    '(Action.person_id = %s) as fullMatch' % personId if personId else '1 as fullMatch']
            cond = [tableEvent['client_id'].eq(clientId),
                    tableEventType['code'].eq('queue'),
                    tableEvent['deleted'].eq(0),
                    tableAction['deleted'].eq(0)
                    ]
            # if personId:
            #    cond.append(tableAction['person_id'].eq(personId))
            # else:
            cond.append(tablePerson['speciality_id'].eq(specialityId))
            cond.append(tableAction['createDatetime'].ge(recordCreateDateTime))
            if maxDate:
                cond.append(tableAction['directionDate'].dateLe(maxDate))
            table = tableEvent.leftJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
            table = table.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
            table = table.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
            table = table.innerJoin(tableAPAction, tableAPAction['value'].eq(tableAction['id']))
            recordList = db.getRecordList(table, cols, cond, 'fullMatch DESC, `Action`.`createDatetime`')

            if recordList:
                for record in recordList:
                    actionId = forceRef(record.value('id'))
                    if forceBool(record.value('fullMatch')):
                        return actionId, True
                return actionId, False
        return None, True
        ### FILTER SLOTS ###
        # NOT ADDED TO GUI

    #    @pyqtSlot(bool)
    #    def on_chkFilterId_clicked(self, checked):
    #        self.onChkFilterClicked(self.chkFilterId, checked)
    #        if self.chkFilterStatus.isChecked():
    #            self.setChkFilterChecked(self.chkFilterStatus, False)
    #        if self.chkFilterClient.isChecked():
    #            self.setChkFilterChecked(self.chkFilterClient, False)
    #        if self.chkFilterSpeciality.isChecked():
    #            self.setChkFilterChecked(self.chkFilterSpeciality, False)
    #        if self.chkFilterPerson.isChecked():
    #            self.setChkFilterChecked(self.chkFilterPerson, False)
    #        if self.chkFilterMaxDate.isChecked():
    #            self.setChkFilterChecked(self.chkFilterMaxDate, False)
    #        if self.chkFilterCreateDate.isChecked():
    #            self.setChkFilterChecked(self.chkFilterCreateDate, False)
    #        if self.chkFilterCreatePerson.isChecked():
    #            self.setChkFilterChecked(self.chkCreatePerson, False)
    #        if self.chkFilterModifyDate.isChecked():
    #            self.setChkFilterChecked(self.chkFilterModifyDate, False)
    #        if self.chkFilterModifyPerson.isChecked():
    #            self.setChkFilterChecked(self.chkFilterModifyPerson, False)

    def getReportHeader(self):
        return u'Журнал отложенного спроса'

    def getFilterAsText(self):
        return u''

    def contentToHTML(self):
        model = self.tblDeferredQueue.model()
        cols = model.cols()
        showMask = [None] * len(cols)
        _showMask = [not self.tblDeferredQueue.isColumnHidden(iCol) if v is None else v
                     for iCol, v in enumerate(showMask)
                     ]
        QtGui.qApp.startProgressBar(model.rowCount())
        try:
            #            report = CReportBase()
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)

            cursor.setCharFormat(CReportBase.ReportTitle)
            header = self.getReportHeader()
            if QtCore.Qt.mightBeRichText(header):
                cursor.insertHtml(header)
            else:
                cursor.insertText(header)
            cursor.insertBlock()
            cursor.setCharFormat(CReportBase.ReportBody)
            description = self.getFilterAsText()
            if QtCore.Qt.mightBeRichText(description):
                cursor.insertHtml(description)
            else:
                cursor.insertText(description)
            cursor.insertBlock()

            colWidths = [self.tblDeferredQueue.columnWidth(i) for i in xrange(len(cols))]
            colWidths.insert(0, 10)
            totalWidth = sum(colWidths)
            tableColumns = []
            for iCol, colWidth in enumerate(colWidths):
                widthInPercents = str(max(1, colWidth * 90 / totalWidth)) + '%'
                if iCol == 0:
                    tableColumns.append((widthInPercents, [u'№'], CReportBase.AlignRight))
                else:
                    if not _showMask[iCol - 1]:
                        continue
                    col = cols[iCol - 1]
                    colAlingment = QtCore.Qt.AlignHorizontal_Mask & forceInt(col.alignment())
                    format = QtGui.QTextBlockFormat()
                    format.setAlignment(QtCore.Qt.AlignmentFlag(colAlingment))
                    tableColumns.append((widthInPercents, [forceString(col.title())], format))

            table = createTable(cursor, tableColumns)
            for iModelRow in xrange(model.rowCount()):
                QtGui.qApp.stepProgressBar()
                QtGui.qApp.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)
                iTableRow = table.addRow()
                table.setText(iTableRow, 0, iModelRow + 1)
                iTableCol = 1
                for iModelCol in xrange(len(cols)):
                    if not _showMask[iModelCol]:
                        continue
                    index = model.index(iModelRow, iModelCol)
                    text = forceString(model.data(index))
                    if iModelCol == len(cols) - 1:
                        clientId = forceRef(self.tblDeferredQueue.model().getRecordByRow(iModelRow).value('client_id'))
                        contacts = getClientPhonesEx(clientId)
                        if contacts:
                            if text:
                                text = u'\n'.join([text, contacts])
                            else:
                                text = contacts
                    table.setText(iTableRow, iTableCol, text)
                    iTableCol += 1
            return doc
        finally:
            QtGui.qApp.stopProgressBar()
            # return self.tblDeferredQueue.contentToHTML()

    @QtCore.pyqtSlot()
    def on_btnSaveRecord_clicked(self):
        db = QtGui.qApp.db
        now = toVariant(QtCore.QDateTime.currentDateTime())
        userId = toVariant(QtGui.qApp.userId)
        record = db.getRecord('DeferredQueue', 'id,status_id, maxDate, comment, modifyDatetime, modifyPerson_id',
                              self.currentRecordId())
        record.setValue('status_id', forceRef(self.cmbStatus.value()))
        record.setValue('maxDate', forceDate(self.edtMaxDate.date()))
        comments = self.tblComments.model().items()
        record.setValue('comment', u'\n'.join(forceString(key) + ':' + forceString(value) for (key, value) in comments))
        # record.setValue('comment', forceString(self.edtComments.toPlainText()))
        record.setValue('modifyDatetime', now)
        record.setValue('modifyPerson_id', userId)
        db.updateRecord('DeferredQueue', record)
        self.updateTableDeferredQueue(self.__filter)

    @QtCore.pyqtSlot()
    def on_btnResetRecord_clicked(self):
        self.updateRecordDetails()

    @QtCore.pyqtSlot()
    def on_btnCheckRecord_clicked(self):
        self.checkCurrentRecord()

    @QtCore.pyqtSlot()
    def on_btnCheckAll_clicked(self):
        self.checkAllRecords()

    @QtCore.pyqtSlot()
    def on_btnApplyFilter_clicked(self):
        filter = {}
        # if self.chkFilterId.isChecked():
        #    filter['id'] = forceStringEx(self.edtFilterId.text())
        if self.chkFilterStatus.isChecked():
            filter['status'] = self.cmbFilterStatus.value()
        if self.chkFilterClient.isChecked():
            filter['client'] = forceStringEx(self.edtFilterClient.text())
        if self.chkFilterSpeciality.isChecked():
            filter['speciality'] = self.cmbFilterSpeciality.value()
        if self.chkFilterOrgStructure.isChecked():
            filter['orgStructure_id'] = self.cmbFilterOrgStructure.value()
        if self.chkFilterPersonOrgStructure.isChecked():
            filter['personOrgStructure_id'] = self.cmbFilterPersonOrgStructure.value()
        if self.chkFilterPerson.isChecked():
            filter['person'] = self.cmbFilterPerson.value()
        if self.chkFilterMaxDate.isChecked():
            filter['begMaxDate'] = self.edtFilterBegMaxDate.date()
            filter['endMaxDate'] = self.edtFilterEndMaxDate.date()
        if self.chkFilterCreatePerson.isChecked():
            filter['createPersonIdEx'] = forceStringEx(self.cmbFilterCreatePerson.lineEdit().text())
        if self.chkFilterCreateDate.isChecked():
            filter['begCreateDateEx'] = self.edtFilterBegCreateDate.date()
            filter['endCreateDateEx'] = self.edtFilterEndCreateDate.date()
        if self.chkFilterModifyPerson.isChecked():
            filter['modifyPersonIdEx'] = self.cmbFilterModifyPerson.value()
        if self.chkFilterModifyDate.isChecked():
            filter['begModifyDateEx'] = self.edtFilterBegModifyDate.date()
            filter['endModifyDateEx'] = self.edtFilterEndModifyDate.date()
        if self.chkFilterAge.isChecked():
            filter['ageFrom'] = self.edtFilterAgeFrom.value()
            filter['ageTo'] = self.edtFilterAgeTo.value()
        if self.chkFilterListLength.isChecked():
            filter['listLength'] = self.edtFilterListLength.value()
        self.updateTableDeferredQueue(filter)
        self.focusDeferredQueue()

    @QtCore.pyqtSlot()
    def on_btnResetFilter_clicked(self):
        for s in self.chkList:
            chk = s[0]
            if chk.isChecked():
                self.deactivateFilterWidgets(s[1])
                chk.setChecked(False)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterStatus_clicked(self, checked):
        #        if self.chkFilterId.isChecked():
        #            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterClient_clicked(self, checked):
        #        if self.chkFilterId.isChecked():
        #            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterSpeciality_clicked(self, checked):
        #        if self.chkFilterId.isChecked():
        #            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterPerson_clicked(self, checked):
        #        if self.chkFilterId.isChecked():
        #            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterMaxDate_clicked(self, checked):
        #        if self.chkFilterId.isChecked():
        #            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterCreatePerson_clicked(self, checked):
        #        if self.chkFilterId.isChecked():
        #            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterCreateDate_clicked(self, checked):
        #        if self.chkFilterId.isChecked():
        #            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterModifyPerson_clicked(self, checked):
        #        if self.chkFilterId.isChecked():
        #            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterModifyDate_clicked(self, checked):
        #        if self.chkFilterId.isChecked():
        #            self.setChkFilterChecked(self.chkFilterId, False)
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterAge_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterOrgStructure_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterPersonOrgStructure_clicked(self, checked):
        self.onChkFilterClicked(self.sender(), checked)

    @QtCore.pyqtSlot(int)
    def on_edtAgeTo_editingFinished(self):
        value = self.edtFilterAgeTo.value()
        if value < self.edtFilterAgeFrom.value():
            self.edtFilterAgeFrom.setValue(value)

    @QtCore.pyqtSlot(int)
    def on_edtAgeFrom_editingFinished(self):
        value = self.edtFilterAgeFrom.value()
        if value > self.edtFilterAgeTo.value():
            self.edtFilterAgeTo.setValue(value)

    @QtCore.pyqtSlot(int)
    def on_cmbFilterSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbFilterSpeciality.value()
        self.cmbFilterPerson.setSpecialityId(specialityId)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_tableSelectionModel_currentRowChanged(self, current, previous):
        current = self.filterModelProxy.mapToSource(current)
        row = current.row()
        if row >= 0:
            self.currentRecord = self.getRecordByRow(row)
            QtGui.qApp.setCurrentClientId(forceRef(self.currentRecord.value('client_id')))
            if self.currentRecordStatus() in [1, 2]:
                self.btnCheckRecord.setEnabled(QtGui.qApp.userHasRight(urEditDeferredQueueItems))
            else:
                self.btnCheckRecord.setEnabled(False)
            self.updateRecordDetails()

        else:
            self.on_btnResetRecord_clicked()
        clientId = QtGui.qApp.currentClientId()
        self.modelQueue.loadData(clientId)
        self.modelVisitByQueue.loadData(clientId)

    @QtCore.pyqtSlot()
    def on_btnAddRecord_clicked(self):
        dialog = CCreateDeferredQueue(self)
        dialog.setCheckedReturnTo(0)
        self.connect(dialog, QtCore.SIGNAL('showRegistry(int)'), QtGui.qApp.mainWindow.on_actRegistry_triggered)
        self.connect(dialog, QtCore.SIGNAL('showDeferredQueue(int)'),
                     QtGui.qApp.mainWindow.on_actDeferredQueue_triggered)
        if dialog.exec_():
            self.updateTableDeferredQueue(self.__filter)

    @QtCore.pyqtSlot()
    def on_btnFilterClient_clicked(self):
        clientId = findClient(self)
        if clientId:
            self.edtFilterClient.setText(forceString(clientId))
        else:
            self.edtFilterClient.setText('')

    @QtCore.pyqtSlot()
    def on_actClientList_triggered(self):
        html = self.contentToHTML()
        view = CReportViewDialog(self)
        view.setText(html)
        view.exec_()

    @QtCore.pyqtSlot()
    def on_actResultClientList_triggered(self):
        CResultClientList(self).exec_()

    class CLocSelectionFilter(QtCore.QObject):
        def __init__(self, parent, type='key'):
            QtCore.QObject.__init__(self, parent)
            self.parent = parent
            if type == 'key':
                self.type = 1
                self.events = (QtCore.QEvent.KeyPress)
            elif type == 'mouse':
                self.type = 2
                self.events = (QtCore.QEvent.MouseButtonPress)

        def eventFilter(self, obj, event):
            if event.type() == self.events:
                if self.type == 2:
                    newRow = self.parent.tblDeferredQueue.rowAt(event.pos().y())
                    currentRow = self.parent.tblDeferredQueue.currentRow()
                    if newRow == currentRow:
                        return CTableView.eventFilter(self, obj, event)
                if self.type == 1:
                    if event.key() not in (QtCore.Qt.Key_Up, QtCore.Qt.Key_Down):
                        return QtCore.QObject.eventFilter(self, obj, event)
                newRecordValues = [forceInt(self.parent.cmbStatus.value()),
                                   forceString(self.parent.edtAction.text()),
                                   forceString(self.parent.edtMaxDate.text()),
                                   self.parent.tblComments.model().items()
                                   ]
                if newRecordValues != self.parent.oldRecordValues:
                    result = QtGui.QMessageBox.warning(
                        self.parent,
                        u'Внимание!',
                        u'Имеются несохраненные изменения. Сохранить?',
                        QtGui.QMessageBox.Ok | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel,
                        QtGui.QMessageBox.Ok
                    )
                    if result == QtGui.QMessageBox.Ok:
                        self.parent.on_btnSaveRecord_clicked()
                    elif result == QtGui.QMessageBox.Cancel:
                        # self.tableSelectionModel.setCurrentIndex(previous, QItemSelectionModel.Select)
                        return True
            return QtCore.QObject.eventFilter(self, obj, event)


class CCreateDeferredQueue(CDialogBase, Ui_CreateDeferredQueueDialog):
    """
        Диалог создания записи в журнале отложенного спроса.
    """
    showRegistry = QtCore.pyqtSignal(int)
    showDeferredQueue = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbSpeciality.setTable('rbSpeciality', False)
        self.cmbSpeciality.setFilter(
            'EXISTS(SELECT id FROM Person WHERE Person.speciality_id = rbSpeciality.id AND Person.ambPlan > 0)')
        self.edtClient.setReadOnly(True)
        defaultOrgStructureId = getVal(QtGui.qApp.preferences.appPrefs, 'orgStructureId', QtCore.QVariant())
        if defaultOrgStructureId:
            self.cmbOrgStructure.setValue(defaultOrgStructureId)
        self.selectedClientId = None
        self.setWindowTitleEx(u'Добавление записи в ЖОС')
        # self.cmbStatus.setTable('rbDeferredQueueStatus', False)
        self.cmbPerson.setOrgStructureId(self.cmbOrgStructure.value())

    def checkData(self):
        result = True
        # result = result and (self.cmbStatus.value() or self.checkInputMessage(u'статус заявки', False, self.cmbStatus))
        result = result and (
        self.selectedClientId or self.checkInputMessage(u'идентификатор пациента', False, self.btnClient))
        result = result and (
        QtCore.QDate(self.edtMaxDate.date()) > QtCore.QDate.currentDate() or self.checkInputMessage(
            u'корректную крайнюю допустимую дату', False, self.edtMaxDate))
        result = result and (
        self.cmbSpeciality.value() or self.checkInputMessage(u'специальность', False, self.cmbSpeciality))
        return result

    @QtCore.pyqtSlot()
    def on_buttonBox_accepted(self):
        if self.checkData():
            db = QtGui.qApp.db
            now = toVariant(QtCore.QDateTime.currentDateTime())
            userId = toVariant(QtGui.qApp.userId)

            tbl = db.table('DeferredQueue')
            record = tbl.newRecord()
            # record.setValue('status_id', forceRef(self.cmbStatus.value()))
            tblRB = db.table('rbDeferredQueueStatus')
            record.setValue('status_id', forceRef(db.translate(tblRB, 'code', 0, 'id')))
            record.setValue('maxDate', forceDate(self.edtMaxDate.date()))
            record.setValue('client_id', forceRef(self.selectedClientId))
            record.setValue('orgStructure_id', forceRef(self.cmbPerson.orgStructureId))
            record.setValue('speciality_id', forceRef(self.cmbSpeciality.value()))
            record.setValue('person_id', forceRef(self.cmbPerson.value()))
            record.setValue('comment', forceString(self.edtComments.toPlainText()))
            record.setValue('createDatetime', now)
            record.setValue('modifyDatetime', now)
            record.setValue('createPerson_id', userId)
            record.setValue('modifyPerson_id', userId)
            queueId = db.insertRecord(tbl, record)
            if self.rbReturnToDeferredQueue.isChecked():
                self.showDeferredQueue.emit(queueId)
            if self.rbReturnToRegistry.isChecked():
                self.showRegistry.emit(self.selectedClientId)
            self.accept()

    @QtCore.pyqtSlot(int)
    def setClient(self, clientId, name=None):
        if clientId:
            if name is None:
                clientInfo = getClientInfo(clientId)
                name = formatName(clientInfo.lastName, clientInfo.firstName, clientInfo.patrName)
            self.selectedClientId = clientId
            self.edtClient.setText(name)
            if forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'DeferredMaxDateByAttach', False)):
                db = QtGui.qApp.db
                stmt = u'''
                SELECT rbAttachType.name as name
                FROM ClientAttach
                INNER JOIN rbAttachType ON rbAttachType.id = ClientAttach.attachType_id AND ClientAttach.deleted = 0
                WHERE ClientAttach.client_id = %d AND rbAttachType.name LIKE 'Д-%%' AND ClientAttach.endDate IS NULL
                ''' % clientId
                query = db.query(stmt)
                if query.first():
                    record = query.record()
                    name = forceString(record.value('name'))
                    date = QtCore.QDate.currentDate()
                    maxDate = None
                    if name == u'Д-1':
                        maxDate = date.addDays(3)
                    elif name == u'Д-2':
                        maxDate = date.addDays(14)
                    elif name == u'Д-3':
                        maxDate = date.addDays(30)
                    elif name == u'Д-4':
                        maxDate = date.addMonths(3)
                    elif name == u'Д-5':
                        maxDate = date.addMonths(6)
                    elif name == u'Д-6':
                        maxDate = date.addYears(1)
                    if maxDate:
                        self.edtMaxDate.setDate(maxDate)
        else:
            self.selectedClientId = None
            self.edtClient.setText('')

    def setCheckedReturnTo(self, index):
        if index == 1:
            self.rbReturnToRegistry.setChecked(True)
        else:
            self.rbReturnToDeferredQueue.setChecked(True)

    def clientId(self):
        return self.selectedClientId

    @QtCore.pyqtSlot()
    def on_btnClient_clicked(self):
        # clientId = findClient(self)
        clientRecord = findClientRecord(self)
        if clientRecord:
            clientId = forceRef(clientRecord.value('id'))
            name = formatName(forceString(clientRecord.value('lastName')), forceString(clientRecord.value('firstName')),
                              forceString(clientRecord.value('patrName')))
            self.setClient(clientId, name)

    @QtCore.pyqtSlot(int)
    def on_cmbSpeciality_currentIndexChanged(self, index):
        specialityId = self.cmbSpeciality.value()
        self.cmbPerson.setSpecialityId(specialityId)
        self.cmbPerson.setCurrentIndex(0)

    @QtCore.pyqtSlot(int)
    def on_cmbOrgStructure_currentIndexChanged(self, index):
        orgStructureId = self.cmbOrgStructure.value()
        self.cmbPerson.setOrgStructureId(orgStructureId)

    @QtCore.pyqtSlot(int)
    def on_cmbPerson_currentIndexChanged(self, index):
        if self.cmbPerson.value():
            db = QtGui.qApp.db
            result = db.getRecordList(table=None, stmt=u'''
            SELECT
                p.orgStructure_id
              FROM
                Person p
              WHERE
                p.id = %i
                    ''' % self.cmbPerson.value())
            self.cmbOrgStructure.setValue(forceRef(result[0].value('orgStructure_id')))
            self.cmbPerson.setOrgStructureId(self.cmbOrgStructure.value())
