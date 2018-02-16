# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrgStructureDescendants, getOrgStructureName
from Ui_JobTicketChooserDialog import Ui_JobTicketChooserDialog
from Users.Rights import urAddJobTicketToSuperiorOrgStructure, urAddOvertimeJobTickets, \
    urIgnoreDurationVisibilityTimelineWorksInEvent
from library.DialogBase import CDialogBase
from library.ElectronicQueue.EQTicketModel import CEQTicketModel
from library.TableModel import CDateTimeCol, CDesignationCol, CIndexCol, CTableModel
from library.TreeModel import CDBTreeItem, CDBTreeModel
from library.Utils import forceBool, forceDateTime, forceDouble, forceInt, forceRef, forceString, forceTime, \
    toVariant
from library.crbcombobox import CRBComboBox, CRBModelDataCache
from library.vm_collections import OrderedDict


class CJobTicketChooserComboBox(QtGui.QComboBox):
    superviseUnitLimitPrecision = 0.001

    def __init__(self, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        self.setMinimumContentsLength(10)
        self._popup = None
        self._ticketIds = None
        self._defaultDate = QtCore.QDate.currentDate()
        self._defaultJobTypeCode = ''
        self._clientId = None
        self.addItem('')
        self._actionTypeIdList = []
        self._clientId = None
        self._serviceSuperviseUnitInfo = {}
        self.actionTypeLimitInfo = {}
        self._isVector = False

    @property
    def isVector(self):
        return self._isVector

    @isVector.setter
    def isVector(self, value):
        self._isVector = value

    @staticmethod
    def getTicketRecord(jobTicketId):
        db = QtGui.qApp.db
        tableJob = db.table('Job')
        tableJobTicket = db.table('Job_Ticket')

        table = tableJobTicket.leftJoin(tableJob, tableJob['id'].eq(tableJobTicket['master_id']))
        cols = [
            tableJobTicket['*'],
            tableJob['date'],
            tableJob['jobType_id'],
            tableJob['orgStructureJob_id'],
            tableJob['orgStructure_id']
        ]
        return db.getRecordEx(table, cols, tableJobTicket['id'].eq(jobTicketId))

    @staticmethod
    def getTicketAsText(jobTicketId):
        record = None
        if jobTicketId:
            record = CJobTicketChooserComboBox.getTicketRecord(jobTicketId)
        if record:
            jobTypeId = forceRef(record.value('jobType_id'))
            datetime = record.value('datetime')
            if forceTime(datetime) == QtCore.QTime(0, 0, 0):
                index = '---'
                datetimeString = u'%s вне очереди' % datetime.toDate().toString(QtCore.Qt.LocaleDate)
            else:
                datetimeString = datetime.toDateTime().toString(QtCore.Qt.LocaleDate)
                index = forceInt(record.value('idx')) + 1

            orgStructureJobId = forceRef(record.value('orgStructureJob_id'))
            orgStructureId = forceRef(QtGui.qApp.db.translate('OrgStructure_Job', 'id', orgStructureJobId, 'master_id'))
            cache = CRBModelDataCache.getData('rbJobType', True)

            return u'%s, %s, %s, %s' % (forceString(index),
                                        cache.getStringById(jobTypeId, CRBComboBox.showName),
                                        forceString(datetimeString),
                                        getOrgStructureName(orgStructureId))
        else:
            return u'Открыть график'

    def clientId(self):
        return self._clientId

    def setClientId(self, clientId):
        self._clientId = clientId

    def actionTypeIdList(self):
        return self._actionTypeIdList

    def setActionTypeIdList(self, actionTypeIdList):
        self._actionTypeIdList = actionTypeIdList

    def setDefaultDate(self, date):
        self._defaultDate = date

    def setDefaultJobTypeCode(self, code):
        self._defaultJobTypeCode = code

    def setValue(self, ticketIds):
        if self._ticketIds != ticketIds:
            self._ticketIds = ticketIds
            text = ''.join(self.getTicketAsText(ticketId) for ticketId in self._ticketIds) if self._ticketIds else u'не выбрано'
            self.setItemText(0, text)
            self.emit(QtCore.SIGNAL('textChanged(QString)'), text)
            self.setItemText(0, text)

    def serviceIdList(self):
        return self._serviceSuperviseUnitInfo.keys()

    def serviceSuperviseUnitInfo(self):
        return self._serviceSuperviseUnitInfo

    def setCurrentServiceIdList(self, serviceIdList):
        self._serviceSuperviseUnitInfo = {}
        for serviceId in serviceIdList:
            self._serviceSuperviseUnitInfo[serviceId] = forceDouble(QtGui.qApp.db.translate('rbService',
                                                                                            'id',
                                                                                            serviceId,
                                                                                            'superviseComplexityFactor'))

    def value(self):
        if self.isVector:
            return self._ticketIds
        else:
            return self._ticketIds[0] if self._ticketIds else None

    def text(self):
        return self.lineEdit.text()

    def showPopup(self):
        from Events.Action import CJobTicketActionPropertyValueType
        dlg = CJobTicketChooserDialog(self, self.clientId(), isVector=self.isVector)
        if self._ticketIds:
            dlg.setCurrentSuperviseUnitInfo(self.serviceSuperviseUnitInfo())
            dlg.setCurrentActionTypeIdList(self.actionTypeIdList())
            dlg.setTicketId(self._defaultJobTypeCode, self._ticketIds)
        else:
            dlg.setDefaults(self._defaultJobTypeCode, self._defaultDate, self.serviceSuperviseUnitInfo(), self.actionTypeIdList())
        if isinstance(self, CJobTicketActionPropertyValueType.CPropEditor) and dlg.status == 2:
            return
        if dlg.exec_():
            if self.isVector:
                self.setValue(dlg.getTicketIds())
            else:
                self.setValue([dlg.getTicketId()])
            self.actionTypeLimitInfo = dlg.actionTypeLimitInfo


class CJobTicketChooserDialog(CDialogBase, Ui_JobTicketChooserDialog):
    def __init__(self, parent, clientId, personId=None, isVector=False):
        CDialogBase.__init__(self, parent)

        self._userJobTypeIdList = None
        self.addModels('JobTypes', CDBTreeModel(self, 'rbJobType', 'id', 'group_id', 'name', order='code', filters=self.getJobTypeFilter()))
        self.addModels('ExistensTickets', CTicketsModel(self))
        self.addModels('Tickets', CTicketsModel(self))

        self.setupUi(self)
        self.clnCalendar.setList(QtGui.qApp.calendarInfo)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        self.modelJobTypes.setRootItemVisible(False)
        self.modelJobTypes.setLeavesVisible(True)

        self.setModels(self.treeJobTypes, self.modelJobTypes, self.selectionModelJobTypes)
        self.treeJobTypes.header().setVisible(False)
        self.setModels(self.tblOldTickets, self.modelExistensTickets, self.selectionModelExistensTickets)
        self.setModels(self.tblTickets, self.modelTickets, self.selectionModelTickets)
        self.orgStructureDelegate = CTicketsModelOrgStructureDelegate(self)
        self.tblTickets.setItemDelegateForColumn(1, self.orgStructureDelegate)
        if isVector:
            self.tblTickets.setSelectionMode(QtGui.QAbstractItemView.ContiguousSelection)

        self.clientId = clientId
        self.ticketId = None
        self.ticketIds = []
        self.jobTypeId = None
        self.date = None
        self.durationVisibility = None

        self.currentSuperviseUnitInfo = {}
        self.currentActionTypeIdList = []
        self._overtimeJobId = None
        self.jobSuperviseInfo = {}
        self.actionTypeLimitInfo = {}
        self.btnApplyFilter.clicked.connect(self.on_btnApplyFilter_clicked)
        self.setFilter = False
        self.status = None

        self.quotaId = None
        self.personId = personId
        self.wts = {'personId': 8, 'specialityId': 4, 'postId': 2, 'orgStructureId': 1}

        self.isVector = isVector

    def isExistQuotaForPerson(self):
        from Events.Action import CJobTicketActionPropertyValueType

        ticketInOtherEvent = u"""
        SELECT 
            Action.event_id
        FROM 
            ActionProperty_Job_Ticket
            INNER JOIN ActionProperty ON ActionProperty.id = ActionProperty_Job_Ticket.id
            INNER JOIN Action ON Action.id = ActionProperty.action_id AND Action.deleted = 0
            INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
        WHERE 
            ActionProperty_Job_Ticket.value = {jobTicketId}
            {cond}
        """

        # TODO: skkachaev: Заменить! Прокидывать personId
        personId = None
        currentJobTicketId = None
        parent = self.parent()
        while not personId and parent:
            if isinstance(parent, CJobTicketActionPropertyValueType.CPropEditor):
                currentJobTicketId = parent.value()
            if hasattr(parent, 'personId'):
                personId = parent.personId
            else:
                parent = parent.parent()

        if personId is None and parent is None:
            return True

        self.personId = personId

        record = QtGui.qApp.db.getRecordEx(table='Person', cols='post_id, speciality_id, orgStructure_id', where='id = %i' % personId)
        postId = forceRef(record.value('post_id'))
        specialityId = forceRef(record.value('speciality_id'))
        orgStructureId = forceRef(record.value('orgStructure_id'))
        data = {'personId': personId,
                'specialityId': specialityId,
                'postId': postId,
                'orgStructureId': orgStructureId}

        cond = [
            'master_id = %i' % self.jobTypeId,
            'person_id = %i' % self.personId
        ]

        if hasattr(parent, 'tabDiagnostic'):
            diagnosticActionModel = parent.tabDiagnostic.tblAPActions.model()
        elif hasattr(parent, 'wdgActions'):
            diagnosticActionModel = parent.wdgActions.tblAPActions.model()
        else:
            diagnosticActionModel = parent.tabActions.tblAPActions.model()

        # start shit
        countUsingJobTicketInOtherAction = 0
        countUsingChoosedJobTicketInOtherAction = 0

        for act in diagnosticActionModel.items():
            prop = act[1].getProperties()
            for x in prop:
                if x.type().tableName == u'ActionProperty_Job_Ticket':
                    if currentJobTicketId and x.getValue() == currentJobTicketId:
                        countUsingJobTicketInOtherAction += 1
                    if self.tblTickets.currentItemId() and x.getValue() == self.tblTickets.currentItemId():
                        countUsingChoosedJobTicketInOtherAction += 1
        # end shit

        recordList = QtGui.qApp.db.getRecordList(table='rbJobType_Quota', cols='*', where=cond)
        if not recordList:
            return True
        filters = dict()
        for record in recordList:
            cond = ['quota_id = %i' % forceRef(record.value('id'))]

            if countUsingChoosedJobTicketInOtherAction:
                cond.append('id != %i' %  self.tblTickets.currentItemId())

            if diagnosticActionModel.jobTicketsFromRemovedAction:
                cond.append('id NOT IN (%s)' % ', '.join(diagnosticActionModel.jobTicketsFromRemovedAction))

            if currentJobTicketId and countUsingJobTicketInOtherAction == 1:
                isTicketInOtherEvent = QtGui.qApp.db.getRecordList(
                    stmt=ticketInOtherEvent.format(
                        jobTicketId=currentJobTicketId,
                        cond=u'AND Action.event_id != %s ' % parent.itemId() if parent.itemId() else u''
                    )
                )
                if not isTicketInOtherEvent:
                    cond.append('id != %i' % currentJobTicketId)

            used = QtGui.qApp.db.getCount('Job_Ticket', 'id', cond)
            quotaCount = forceInt(record.value('count'))
            if quotaCount - used > 0 and quotaCount - len(self.tblOldTickets.model().idList()) > 0:
                filters[forceRef(record.value('id'))] = \
                    {'personId': forceRef(record.value('person_id')),
                     'specialityId': forceRef(record.value('speciality_id')),
                     'postId': forceRef(record.value('post_id')),
                     'orgStructureId': QtGui.qApp.db.getDescendants('OrgStructure', 'parent_id', forceRef(record.value('orgStructure_id')))}

        maxId = None
        maxSum = 0
        for quotaId, f in filters.items():
            currSum = 0
            match = True

            if f['personId'] is not None:
                if f['personId'] == data['personId']:
                    currSum += self.wts['personId']
                else:
                    break
            if f['specialityId'] is not None:
                if f['specialityId'] == data['specialityId']:
                    currSum += self.wts['specialityId']
                else:
                    break
            if f['postId'] is not None:
                if f['postId'] == data['postId']:
                    currSum += self.wts['postId']
                else:
                    break
            if f['orgStructureId'] != [None]:
                if data['orgStructureId'] in f['orgStructureId']:
                    currSum += self.wts['orgStructureId']
                else:
                    break

            if match and currSum > maxSum:
                maxId = quotaId
                maxSum = currSum

        if maxId:
            self.quotaId = maxId
            if currentJobTicketId and currentJobTicketId not in self.tblOldTickets.model().idList() and countUsingJobTicketInOtherAction == 1:
                QtGui.qApp.delJobTicketReservation(currentJobTicketId, checkReservation=False)

            return True
        else:
            return False

    @staticmethod
    def getJobTypeFilter():
        db = QtGui.qApp.db
        jobTypeIdList = QtGui.qApp.userAvailableJobTypeIdList()
        if jobTypeIdList:
            return db.table('rbJobType')['id'].inlist(db.getTheseAndParents('rbJobType', 'group_id', jobTypeIdList))
        return None

    def setDefaultJobType(self, jobTypeCode):
        db = QtGui.qApp.db
        jobTypeId = forceRef(db.translate('rbJobType', 'code', jobTypeCode, 'id'))
        if jobTypeId:
            self.setDefaultJobTypeId(jobTypeId)
        return jobTypeId

    def setDefaultJobTypeId(self, jobTypeId):
        db = QtGui.qApp.db
        jobTypeName = forceString(db.translate('rbJobType', 'id', jobTypeId, 'name'))
        self.modelJobTypes.setRootItem(CDBTreeItem(None, jobTypeName, jobTypeId, self.modelJobTypes))
        self.modelJobTypes.setRootItemVisible(True)
        self.treeJobTypes.setVisible(not self.modelJobTypes.getRootItem().isLeaf())

    def setCurrentSuperviseUnitInfo(self, superviseUnitInfo):
        self.currentSuperviseUnitInfo = superviseUnitInfo
        self.lblCurrentSuperviseUnitValue.setText(' + '.join([unicode(v) for v in self.currentSuperviseUnitInfo.values()])
                                                  + '(%s)' % sum(self.currentSuperviseUnitInfo.values()))
        self.updateTickets(self.jobTypeId, self.date)

    def setCurrentActionTypeIdList(self, currentActionTypeIdList):
        self.currentActionTypeIdList = currentActionTypeIdList

    def setDefaults(self, jobTypeCode, date, serviceSuperviseUnit=None, actionTypeIdList=None):
        if not serviceSuperviseUnit:
            serviceSuperviseUnit = {}
        if not actionTypeIdList:
            actionTypeIdList = []
        self.setCurrentSuperviseUnitInfo(serviceSuperviseUnit)
        self.setCurrentActionTypeIdList(actionTypeIdList)
        self.setDate(date)
        self.setJobTypeId(self.setDefaultJobType(jobTypeCode))
        self.tabWidget.setCurrentIndex(0 if self.modelExistensTickets.idList() and not self.isVector else 1)

    def setTicketId(self, jobTypeCode, ticketIds):
        self.ticketIds = ticketIds
        defaultJobTypeId = self.setDefaultJobType(jobTypeCode)
        # if ticketIds:
        #     record = CJobTicketChooserComboBox.getTicketRecord(ticketId)
        #     jobTypeId = forceRef(record.value('jobType_id'))
        #     date = forceDate(record.value('date'))
        #     self.status = forceRef(record.value('status'))
        #     self.setJobTypeId(jobTypeId)
        #     self.setDate(date)
        # else:
        self.setJobTypeId(defaultJobTypeId)
        self.setDate(QtCore.QDate.currentDate())
        self.tblOldTickets.setIdList(ticketIds)
        # if self.tblTickets.currentItemId() == ticketId:
        #     self.updateTickets(self.jobTypeId, self.date)
        # else:
        self.tblTickets.clearSelection()
        self.tblTickets.setSelectedItemIdList(ticketIds)

        self.tabWidget.setCurrentIndex(0 if self.modelExistensTickets.idList() and not self.isVector else 1)

    def getTicketId(self):
        return self.ticketId

    def getTicketIds(self):
        return self.ticketIds

    def setJobTypeId(self, jobTypeId):
        index = self.modelJobTypes.findItemId(jobTypeId)
        if index:
            self.treeJobTypes.setCurrentIndex(index)

    def setDate(self, date):
        if date:
            self.clnCalendar.setSelectedDate(date)

    def setCaliendarDataRange(self, jobTypeId):
        self.durationVisibility = forceInt(QtGui.qApp.db.translate('rbJobType', 'id', jobTypeId, 'durationVisibility'))
        minDate = QtCore.QDate.currentDate()
        if self.durationVisibility:
            maxDate = minDate.addDays(self.durationVisibility)
        else:
            maxDate = minDate.addYears(10)
            minDate = minDate.addYears(-10)
        self.clnCalendar.setDateRange(minDate, maxDate)

        if self.durationVisibility and not QtGui.qApp.userHasRight(urAddOvertimeJobTickets):
            y = minDate
            while y != maxDate.addDays(3):
                jobTicketIdList, existentJobTicketIdList, overtimeJobs, overtimeTicketId, self.jobSuperviseInfo, self.actionTypeLimitInfo = self.getJobTicketsInfo(
                    jobTypeId,
                    y,
                    self.clientId,
                    self.ticketId,
                    self.currentSuperviseUnitInfo,
                    self.currentActionTypeIdList)

                if len(jobTicketIdList) == 0:
                    self.clnCalendar.addIgnoredDate(y)
                y = y.addDays(1)

    @staticmethod
    def getJobTicketsInfo(jobTypeId, date, currentClientId, ticketId, currentSuperviseUnitInfo, currentActionTypeIdList):
        u"""
        Формирует набор данных по номеркам на работы в указанный день с учетом выбранного пациента.

        :param jobTypeId: идентификатор типа работ (rbJobType.id)
        :param date: дата, на которую необходимо получить сводку по номеркам
        :param currentClientId: идентификатор пациента, для которого формируются данные, для определения его прошлых номерков
        :param ticketId: текущий номерок пациента (atronah: вроде как)
        :param currentSuperviseUnitInfo: словарь с объемом УЕТ (единиц учета) по каждой услуге
        :param currentActionTypeIdList: список текущих типов действий
        :return: (freeIdList, busyIdList, overtimeJobs, overtimeTicketId, jobSuperviseInfo)
                , где
                    freeIdList - список идентификаторов всех свободных номерков (Job_Ticket.id);
                    busyIdList - список идентификаторов всех занятых номерков (Job_Ticket.id);
                    overtimeJobs - словарь, содержащий в качестве ключей идентификаторы работ (Job.id),
                                    для которых доступна запись сверх очереди,
                                    а в качетсве значений - кортежи из
                                        * код подразделения, к которому отсится работа
                                        * идентификатор типа используемой эл. очереди (rbEQueueType.id)
                    overtimeTicketId - идентификатор номерка, доступного для помещения туда записи "сверх очереди"
                    jobSuperviseInfo - словарь, содержащий доп. информацию по УЕТ (использовано, допустимый предел, квота и т.п.),
                    actionTypeLimitInfo -  словарь, содержащий доп. информацию по лимитам/квотам на типы действия
        """
        freeIdList = []
        busyIdList = []
        overtimeJobs = {}
        overtimeTicketId = None
        jobSuperviseInfo = {}
        onDayLimitInfo = {}
        if jobTypeId and date:

            db = QtGui.qApp.db
            tableJobTicket = db.table('Job_Ticket')
            tableJob = db.table('Job')
            tableJobType = db.table('rbJobType')
            tableOrgStructureJob = db.table('OrgStructure_Job')
            tableOrgStructure = db.table('OrgStructure')
            tableActionPropertyJobTicket = db.table('ActionProperty_Job_Ticket')
            tableActionProperty = db.table('ActionProperty')
            tableAction = db.table('Action')
            tableEvent = db.table('Event')
            tableActionType = db.table('ActionType')
            tableService = db.table('rbService')

            for currentActionTypeId in currentActionTypeIdList:
                parentActionTypeIdList = db.getTheseAndParents(tableActionType, 'group_id', [currentActionTypeId])
                if parentActionTypeIdList:
                    tableJobTypeActionTypes = db.table('rbJobType_ActionType')
                    onDayLimitRecordList = db.getRecordList(tableJobTypeActionTypes.innerJoin(tableActionType,
                                                                                              tableActionType['id'].eq(tableJobTypeActionTypes['actionType_id'])),
                                                            cols=['onDayLimit AS onDayLimit',
                                                                  tableActionType['id'].alias('baseActionTypeId'),
                                                                  tableActionType['name'].alias('baseActionTypeName')],
                                                            where=[tableJobTypeActionTypes['master_id'].eq(jobTypeId),
                                                                   tableJobTypeActionTypes['actionType_id'].inlist(parentActionTypeIdList)],
                                                            order='onDayLimit ASC',
                                                            limit=1)
                    if onDayLimitRecordList:
                        record = onDayLimitRecordList[0]
                        onDayLimit = forceInt(record.value('onDayLimit'))
                        if onDayLimit > 0:
                            baseActionTypeId = forceRef(record.value('baseActionTypeId'))
                            childrenList = db.getDescendants(tableActionType, 'group_id', baseActionTypeId)
                            onDayLimitInfo[baseActionTypeId] = {
                                'onDayLimit'    : onDayLimit,
                                'available'     : onDayLimit,
                                'name'          : forceString(record.value('baseActionTypeName')),
                                'childrenIdList': childrenList,
                                'required'      : len([itemId for itemId in currentActionTypeIdList if itemId in childrenList])
                            }

            tableEx = tableJobTicket.leftJoin(tableJob, tableJob['id'].eq(tableJobTicket['master_id']))
            tableEx = tableEx.leftJoin(tableOrgStructureJob, tableOrgStructureJob['id'].eq(tableJob['orgStructureJob_id']))
            tableEx = tableEx.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableOrgStructureJob['master_id']))
            tableEx = tableEx.leftJoin(tableActionPropertyJobTicket, tableActionPropertyJobTicket['value'].eq(tableJobTicket['id']))
            tableEx = tableEx.leftJoin(tableActionProperty, tableActionProperty['id'].eq(tableActionPropertyJobTicket['id']))
            tableEx = tableEx.leftJoin(tableAction, tableAction['id'].eq(tableActionProperty['action_id']))
            tableEx = tableEx.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
            tableEx = tableEx.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            tableEx = tableEx.leftJoin(tableService, tableService['code'].eq(tableActionType['code']))

            cond = [tableJob['deleted'].eq(0),
                    tableJob['jobType_id'].eq(jobTypeId),
                    tableJob['date'].dateEq(date),
                    tableJobTicket['datetime'].dateGe(date),
                    db.joinOr([tableAction['deleted'].eq(0), tableAction['deleted'].isNull()]),
                    db.joinOr([tableEvent['deleted'].eq(0), tableEvent['deleted'].isNull()])]

            currentOrgStructureId = QtGui.qApp.currentOrgStructureId()
            if currentOrgStructureId and not QtGui.qApp.userHasRight(urAddJobTicketToSuperiorOrgStructure):
                cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(currentOrgStructureId)))

            cols = [
                tableJobTicket['id'].alias('jobTicketId'),
                tableJobTicket['datetime'],
                tableJobTicket['status'],
                tableJob['id'].alias('jobId'),
                tableJob['isOvertime'].alias('jobIsOvertime'),
                tableJob['begTime'].alias('jobBegTime'),
                tableJob['endTime'].alias('jobEndTime'),
                tableJob['eQueueType_id'].alias('eQueueTypeId'),
                tableOrgStructure['code'],
                tableEvent['client_id'].alias('clientId'),
                db.makeField(
                    db.joinOr([tableJobTicket['id'].eq(ticketId),
                               db.joinAnd([tableActionPropertyJobTicket['id'].isNull(),
                                           db.not_(db.func.isReservedJobTicket(tableJobTicket['id']))])])
                ).alias('free'),
                tableService['superviseComplexityFactor'],
                tableJob['limitSuperviseUnit'],
                tableJob['personQuota'],
                tableJob['quantity'],
                tableActionProperty['modifyPerson_id'].alias('person'),
                tableActionType['id'].alias('actionTypeId')
            ]
            order = [
                tableOrgStructure['code'],
                tableJobTicket['datetime']
            ]

            jobTypeName = forceString(db.translate(tableJobType, tableJobType['id'], jobTypeId, 'name'))
            for record in db.iterRecordList(tableEx, cols, cond, order=order):
                jobTicketId = forceRef(record.value('jobTicketId'))
                jobTicketDateTime = forceDateTime(record.value('datetime'))
                isFree = forceBool(record.value('free'))
                jobIsOvertime = forceBool(record.value('jobIsOvertime'))
                jobId = forceRef(record.value('jobId'))
                orgStructureCode = forceString(record.value('code'))
                actionTypeId = forceRef(record.value('actionTypeId'))
                for baseActionTypeId, info in onDayLimitInfo.items():
                    if actionTypeId in info['childrenIdList']:
                        info['available'] -= 1

                jobSuperviseInfo.setdefault(jobId, {'used'              : 0.0,
                                                    'limit'             : 0,
                                                    'jobTickets'        : [],
                                                    'name'              : '',
                                                    'personQuotaPercent': 100,
                                                    'limitPersonQuota'  : 0,
                                                    'usedPersonQuota'   : 0})
                jobSuperviseInfo[jobId]['used'] += forceDouble(record.value('superviseComplexityFactor'))
                jobSuperviseInfo[jobId]['limit'] = forceDouble(record.value('limitSuperviseUnit'))
                jobSuperviseInfo[jobId]['jobTickets'].append(jobTicketId)
                jobSuperviseInfo[jobId]['name'] = u'%s\n(%s-%s, каб.%s)' % (jobTypeName,
                                                                            forceTime(record.value('jobBegTime')).toString('HH:mm'),
                                                                            forceTime(record.value('jobEndTime')).toString('HH:mm'),
                                                                            orgStructureCode)
                personQuotaPercent = forceInt(record.value('personQuota'))
                jobQuantity = forceInt(record.value('quantity'))
                jobSuperviseInfo[jobId]['personQuotaPercent'] = personQuotaPercent
                jobSuperviseInfo[jobId]['limitPersonQuota'] = personQuotaPercent * jobQuantity / 100
                jobSuperviseInfo[jobId]['usedPersonQuota'] += 1 if QtGui.qApp.userId == forceRef(record.value('person')) else 0

                if isFree and jobTicketDateTime >= date:
                    if jobTicketId not in freeIdList:
                        freeIdList.append(jobTicketId)
                else:
                    status = forceInt(record.value('status'))
                    clientId = forceRef(record.value('clientId'))
                    if status in (0, 1) and clientId == currentClientId and jobTicketId not in busyIdList:
                        busyIdList.append(jobTicketId)

                if jobIsOvertime:
                    if not overtimeJobs.has_key(jobId):
                        eQueueTypeId = forceRef(record.value('eQueueTypeId'))
                        overtimeJobs[jobId] = (orgStructureCode, eQueueTypeId)
                    if isFree and forceTime(record.value('datetime')) == QtCore.QTime(0, 0, 0):
                        overtimeTicketId = jobTicketId
                        if jobTicketId in freeIdList:
                            freeIdList.remove(jobTicketId)

            allActionTypeOverlimited = bool(onDayLimitInfo)
            for info in onDayLimitInfo.values():
                if info['available'] >= info['required']:
                    allActionTypeOverlimited = False
                    break

            if allActionTypeOverlimited:
                freeIdList = [] # Так как превышен лимит для всех типов действия

            summaryUsedSuperviseUnit = sum(currentSuperviseUnitInfo.values())
            if summaryUsedSuperviseUnit > CJobTicketChooserComboBox.superviseUnitLimitPrecision:
                for jobId, item in jobSuperviseInfo.items():
                    if item['limit'] > CJobTicketChooserComboBox.superviseUnitLimitPrecision and (summaryUsedSuperviseUnit + item['used'] - item['limit']) > CJobTicketChooserComboBox.superviseUnitLimitPrecision:
                        for jobTicketId in jobSuperviseInfo[jobId]['jobTickets']:
                            if jobTicketId in freeIdList:
                                freeIdList.remove(jobTicketId)

            ticketAssignWay = forceInt(QtGui.qApp.db.translate('rbJobType', 'id', jobTypeId, 'ticketAssignWay'))
            if ticketAssignWay:
                freeIdList = freeIdList[:1]

            cond = [
                tableJob['deleted'].eq(0),
                tableJob['jobType_id'].eq(jobTypeId),
                tableJob['date'].dateEq(date),
                tableJobTicket['datetime'].dateGe(QtCore.QDate.currentDate()),
                db.joinOr([tableAction['deleted'].eq(0), tableAction['deleted'].isNull()]),
                db.joinOr([tableEvent['deleted'].eq(0), tableEvent['deleted'].isNull()]),
                tableJobTicket['status'].eq(0)
            ]
            if currentClientId:
                cond.append(tableEvent['client_id'].eq(currentClientId))
            order = [
                tableOrgStructure['code'],
                tableJobTicket['datetime']
            ]
            for record in db.iterRecordList(tableEx, cols, cond, order=order):
                jobTicketId = forceRef(record.value('jobTicketId'))
                if jobTicketId not in busyIdList:
                    busyIdList.append(jobTicketId)

        return freeIdList, busyIdList, overtimeJobs, overtimeTicketId, jobSuperviseInfo, onDayLimitInfo

    def fillCmbSubdivFilter(self, jobTicketIdList):
        self.cmbSubdivFilter.clear()
        self.cmbSubdivFilter.addItem(u"- не задано -")
        if len(jobTicketIdList) > 0:
            db = QtGui.qApp.db

            setOfId = ''
            for x in jobTicketIdList:
                setOfId += ',' + str(x)

            OrgStructNames = db.getRecordList(table=None, stmt=u'''
            SELECT DISTINCT
              os.name as name
              FROM
                Job j,
                Job_Ticket jt,
                OrgStructure os
              WHERE
                j.orgStructure_id = os.id
              AND
                j.id = jt.master_id
              AND
                jt.id IN (%s)
            ''' % setOfId[1:])
            for x in OrgStructNames:
                self.cmbSubdivFilter.addItem(forceString(x.value('name')))

    def on_btnApplyFilter_clicked(self):
        self.updateTickets(self.jobTypeId, self.date)

    def updateTickets(self, jobTypeId, date):
        self.jobTypeId = jobTypeId
        self.date = date
        if date == QtCore.QDate.currentDate() and forceBool(self.durationVisibility):
            date = QtCore.QDateTime.currentDateTime()

        jobTicketIdList, \
            existentJobTicketIdList, \
            overtimeJobs, \
            overtimeTicketId, \
            self.jobSuperviseInfo, \
            self.actionTypeLimitInfo = self.getJobTicketsInfo(jobTypeId,
                                                              date,
                                                              self.clientId,
                                                              self.ticketId,
                                                              self.currentSuperviseUnitInfo,
                                                              self.currentActionTypeIdList)
        self.tblTickets.setIdList([])
        self.tblOldTickets.setIdList(existentJobTicketIdList)
        self.tabWidget.setTabEnabled(0, bool(existentJobTicketIdList) and not self.isVector)
        self.modelTickets.setOvertimeJobs(overtimeJobs)
        self.modelTickets.setOvertimeJobTicketId(overtimeTicketId)

        if self.cmbSubdivFilter.currentIndex() > 0:
            self.setFilter = False
            db = QtGui.qApp.db

            setOfId = ''
            for x in jobTicketIdList:
                setOfId += ',' + str(x)

            jobTicketIdList = [ forceRef(x.value('id')) for x in db.getRecordList(table=None, stmt=u'''
            SELECT DISTINCT
              jt.id as id
              FROM
                Job j,
                Job_Ticket jt,
                OrgStructure os
              WHERE
                j.orgStructure_id = os.id
              AND
                j.id = jt.master_id
              AND
                jt.id IN (%s)
              AND
                os.name = '%s'
            ''' % (setOfId[1:], self.cmbSubdivFilter.currentText()))
            ]

        self.tblTickets.setIdList(jobTicketIdList)
        if self.clnCalendar.prevDate != date:
            self.fillCmbSubdivFilter(jobTicketIdList)
        self.updateSuperviseUnitInfo(self.tblTickets.currentIndex())
        if date is not None:
            try:
                self.clnCalendar.prevDate = QtCore.QDate(date)
            except:
                self.clnCalendar.prevDate = QtCore.QDate(date.date())
        else:
            self.clnCalendar.prevDate = QtCore.QDate.currentDate()

    def saveData(self):
        self.ticketIds = []
        if self.isVector:
            tableWidget = self.tblTickets
            ticketIds = list(set([tableWidget.itemId(x) for x in self.selectionModelTickets.selectedIndexes()]))
        else:
            tableWidget = self.tblTickets if self.tabWidget.currentIndex() == 1 else self.tblOldTickets
            ticketIds = [tableWidget.currentItemId()]

        if (not ticketIds or None in ticketIds) and tableWidget == self.tblTickets:
            overtimeJobId = tableWidget.model().overtimeJobId()
            overtimeTicketId = tableWidget.model().overtimeTicketId()
            if overtimeJobId:
                db = QtGui.qApp.db
                tableJobTicket = db.table('Job_Ticket')
                record = db.getRecord(tableJobTicket, '*', overtimeTicketId)
                if not record:
                    record = tableJobTicket.newRecord()
                    record.setValue('datetime', toVariant(self.date))

                    overtimeJobs = tableWidget.model().overtimeJobs()
                    eQueueTypeId = overtimeJobs.get(overtimeJobId, (u'', None))[1]
                    if eQueueTypeId:
                        eQueueRecord = CEQTicketModel.getEQueueRecord(db.db, eQueueTypeId, self.date)
                        eQueueId = forceRef(eQueueRecord.value('id'))
                        eQueueTicketRecord = CEQTicketModel.getEQueueTicketRecord(db.db,
                                                                                  eQueueId,
                                                                                  None)
                        if eQueueTicketRecord and not eQueueTicketRecord.isEmpty():
                            eQueueTicketId = forceRef(eQueueTicketRecord.value('id'))
                            if not eQueueTicketId:
                                eQueueTicketId = db.insertOrUpdate(db.table('EQueueTicket'), eQueueTicketRecord)
                            record.setValue('eQueueTicket_id', toVariant(eQueueTicketId))

                record.setValue('master_id', toVariant(overtimeJobId))
                ticketIds.append(QtGui.qApp.db.insertOrUpdate(tableJobTicket, record))
                self.actionTypeLimitInfo = {}

        for ticketId in ticketIds:
            if ticketId is not None and ticketId not in self.tblOldTickets.model().idList():
                if (not QtGui.qApp.isReservedJobTicket(ticketId)) \
                        and QtGui.qApp.addJobTicketReservation(ticketId, self.personId, self.quotaId):
                    self.ticketId = ticketId
                    self.ticketIds.append(ticketId)
                else:
                    self.updateTickets(self.jobTypeId, self.clnCalendar.selectedDate())
                    return False
            else:
                self.ticketId = ticketId
                self.ticketIds.append(ticketId)

        if not ticketIds:
            self.updateTickets(self.jobTypeId, self.clnCalendar.selectedDate())
            return False

        return True

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelJobTypes_currentChanged(self, current, previous):
        jobTypeId = self.modelJobTypes.itemId(current) if current.isValid() else None
        if not QtGui.qApp.userHasRight(urIgnoreDurationVisibilityTimelineWorksInEvent):
            self.setCaliendarDataRange(jobTypeId)
        self.updateTickets(jobTypeId, self.clnCalendar.selectedDate())

    @QtCore.pyqtSlot()
    def on_clnCalendar_selectionChanged(self):
        if self.clnCalendar.selectedDate() in self.clnCalendar.ignoredDate:
            self.clnCalendar.setSelectedDate(self.clnCalendar.prevDate)
        else:
            self.updateTickets(self.jobTypeId, self.clnCalendar.selectedDate())

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblOldTickets_doubleClicked(self, index):
        self.accept(skipQuotaCheck=True)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblTickets_doubleClicked(self, index):
        if self.tblTickets.model().isOvertimeItem(index):
            return
        self.accept()

    def accept(self, skipQuotaCheck=False):
        db = QtGui.qApp.db
        skipQuotaCheck = skipQuotaCheck or self.tabWidget.currentIndex() == self.tabWidget.indexOf(self.tabOld)
        if not skipQuotaCheck and not self.isExistQuotaForPerson():
            QtGui.QMessageBox.critical(self, u'Внимание!', u'Лимит на выдачу номерков исчерпан.')
            return
        idx = self.tblTickets.currentIndex()
        mdl = self.tblTickets.model()  # type: CTicketsModel
        if self.isVector:
            tableWidget = self.tblTickets
            ticketIds = list(set([tableWidget.itemId(x) for x in self.selectionModelTickets.selectedIndexes()]))
            if ticketIds:
                tblJobTicket = db.table('Job_Ticket')
                ticketRecords = db.getRecordList(tblJobTicket, ['id', 'idx', 'master_id'], tblJobTicket['id'].inlist(ticketIds))
                ticketIndexes = list(sorted(forceInt(r.value('idx')) for r in ticketRecords))
                if ticketIndexes[-1] - ticketIndexes[0] != len(ticketIds) - 1:
                    QtGui.QMessageBox().critical(self, u'Ошибка', u'Выбраны не последовательные номерки')
                    return
                ticketOrgStructures = [forceRef(db.translate('Job', 'id', r.value('master_id'), 'orgStructure_id')) for r in ticketRecords]
                if not ticketOrgStructures.count(ticketOrgStructures[0]) == len(ticketOrgStructures):
                    QtGui.QMessageBox().critical(self, u'Ошибка', u'Выбраны номерки для разных подразделений')
                    return
        if mdl.isOvertimeItem(idx) and mdl._overtimeJobId is None:
            QtGui.QMessageBox.critical(self, u'Ошибка', u'Необходимо задать подразделение для номерка вне очереди')
        else:
            super(CJobTicketChooserDialog, self).accept()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelTickets_currentChanged(self, current, previous):
        self.updateSuperviseUnitInfo(current)

    def updateSuperviseUnitInfo(self, index):
        jobInfo = {}
        if index.isValid():
            jobInfo = self.jobSuperviseInfo.get(index.model().jobId(index), {})

        jobLimitUnit = jobInfo.get('limit', 0.0)
        jobUsedUnit = jobInfo.get('used', 0.0)
        self.lblJobDescription.setText(jobInfo.get('name', u''))
        if jobLimitUnit > CJobTicketChooserComboBox.superviseUnitLimitPrecision:
            self.lblFreeSuperviseUnitValue.setText(forceString(jobLimitUnit - jobUsedUnit))
            self.lblLimitSuperviseUnitValue.setText(forceString(jobLimitUnit))
            self.lblFromSuperviseUnit.setText(u' из ')
        else:
            self.lblFreeSuperviseUnitValue.setText(u'<без ограничения>')
            self.lblLimitSuperviseUnitValue.setText(u'')
            self.lblFromSuperviseUnit.setText(u'')

        jobLimitQuotaPercent = jobInfo.get('personQuotaPercent')
        if jobLimitQuotaPercent == 100:
            self.lblFreePersonQuota.setText(u'<без ограничения>')
            self.lblLimitPersonQuota.setText(u'')
            self.lblFromPersonQuota.setText(u'')
        else:
            jobLimitQuota = jobInfo.get('limitPersonQuota', 0)
            jobUsedQuota = jobInfo.get('usedPersonQuota', 0)
            self.lblFreePersonQuota.setText(forceString(jobLimitQuota - jobUsedQuota))
            self.lblLimitPersonQuota.setText(forceString(jobLimitQuota))
            self.lblFromPersonQuota.setText(u' из ')

        actionsTypesNames = []
        actionsTypesLimit = []
        for info in self.actionTypeLimitInfo.values():
            actionsTypesNames.append(info['name'])
            actionsTypesLimit.append(u'%s из %s' % (info['available'], info['onDayLimit']))
        self.lblOnDayActionTypes.setText('\n'.join(actionsTypesNames))
        self.lblOnDayLimits.setText('\n'.join(actionsTypesLimit))


class CTicketsModelOrgStructureDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None):
        QtGui.QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = QtGui.QComboBox(parent)
        for jobId, (orgCode, _) in index.model().overtimeJobs().items():
            editor.addItem(orgCode, toVariant(jobId))
        return editor

    def setEditorData(self, editor, index):
        jobIdData = index.data(QtCore.Qt.EditRole)
        editor.setCurrentIndex(editor.findData(jobIdData))

    def setModelData(self, editor, model, index):
        model.setOvertimeJobId(forceRef(editor.itemData(editor.currentIndex())), index)


class CTicketsModel(CTableModel):
    def __init__(self, parent):
        orgStructFilter = QtGui.qApp.isFilterJobTicketByOrgStructEnabled()
        CTableModel.__init__(self, parent, [
            CIndexCol(u'№', ['idx'], 10),
            CDesignationCol(u'Подразделение', ['master_id'], [('Job', 'orgStructureJob_id'), ('OrgStructure_Job', 'master_id'), ('OrgStructure', 'code')], 25, orgStructFilter=orgStructFilter),
            CDateTimeCol(u'Дата и время', ['datetime'], 25),
        ], 'Job_Ticket')
        self._enableOvertime = False  # возможность записывать сверх очереди
        self._overtimeTicketId = None  # id свободного сверхочередного номерка, если такой уже есть в базе
        self._overtimeJobId = None  # выбранная по умолчанию работа для номерка "сверх" очереди (в интерфесе - подразделение номерка)

        # словарь где каждой работе (jobId) сопоставляется кортеж из:
        #   * код подразделения, к которому относится работа
        #   * идентификатор типа используемой эл. очереди
        self._overtimeJobs = OrderedDict()

    def isOvertimeItem(self, index):
        if not index.isValid():
            return False
        if index.row() == self.rowCount() - 1 and self._enableOvertime and index.column() == 1:
            return True
        return False

    def setOvertimeJobId(self, jobId, index):
        if jobId:
            self._overtimeJobId = jobId
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
        self.reset()

    def overtimeJobId(self):
        return self._overtimeJobId

    def setOvertimeJobTicketId(self, jobTicketId):
        self._overtimeTicketId = jobTicketId

    def overtimeTicketId(self):
        return self._overtimeTicketId

    def overtimeJobs(self):
        return self._overtimeJobs

    def setOvertimeJobs(self, overtimeJobsDict):
        self._overtimeJobs = OrderedDict({None: (u'не выбрано', None)})
        self._overtimeJobs.update(overtimeJobsDict)
        self._enableOvertime = bool(self._overtimeJobs and QtGui.qApp.userHasRight(urAddOvertimeJobTickets))
        if self._enableOvertime and self._overtimeJobs:
            self._overtimeJobId = None

    def rowCount(self, parent=QtCore.QModelIndex()):
        return CTableModel.rowCount(self, parent) + (1 if self._enableOvertime else 0)

    def idList(self):
        return CTableModel.idList(self) + ([None] if self._enableOvertime else [])

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        row = index.row()
        column = index.column()

        if row == self.rowCount() - 1 and self._enableOvertime:
            isOvertime = True
            col, values = self.getRecordValues(2, 0) if self._idList  else (self._cols[2], [toVariant(QtCore.QTime(0, 0, 0))])
            if role == QtCore.Qt.EditRole:
                if column == 1:
                    return toVariant(self._overtimeJobId)
        else:
            col, values = self.getRecordValues(2, row)
            isOvertime = forceTime(values[0]) == QtCore.QTime(0, 0, 0)

        if isOvertime:
            if role == QtCore.Qt.DisplayRole:
                if column == 0:
                    return toVariant('---')
                elif column == 2:
                    values = [toVariant(values[0].toDate())] + values[1:]
                    return toVariant(u'%s вне очереди' % forceString(col.format(values)))

        if row == self.rowCount() - 1 and self._enableOvertime:
            if role == QtCore.Qt.DisplayRole:
                if column == 1:
                    return toVariant(self._overtimeJobs.get(self._overtimeJobId, ('', None))[0])
            return QtCore.QVariant()
        return CTableModel.data(self, index, role)

    def jobId(self, index):
        if not index.isValid():
            return 0
        row = index.row()
        if row == self.rowCount() - 1:
            return self._overtimeJobId
        values = self.getRecordValues(1, row)[1]
        if not values:
            return 0
        return forceRef(values[0])

    def flags(self, index):
        if not index.isValid():
            return QtCore.QVariant()
        row = index.row()
        if row == self.rowCount() - 1 and self._enableOvertime:
            return CTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled

        return CTableModel.flags(self, index)
