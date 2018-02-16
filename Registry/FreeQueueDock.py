# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import sip
from PyQt4 import QtCore, QtGui

from Events.Action import CActionTypeCache, CAction
from Events.Utils import getEventType, getDeathDate
from Orgs.OrgStructComboBoxes import COrgStructureModel
from Orgs.Utils import findOrgStructuresByAddress
from Registry.BeforeRecordClient import printOrder
from Registry.ResourcesDock import CActivityModel, CResourcesPersonnelModel, createQueueEvent, getQuota, \
    CFlatResourcesPersonnelModel
from Registry.Utils import getClientMiniInfo, getClientAddressEx, CCheckNetMixin
from Timeline.TimeTable import formatTimeRange
from Ui_FreeQueueDockContent import Ui_Form
from Users.Rights import urQueueCancelMaxDateLimit, urQueueWithEmptyContacts
from library.DialogBase import CConstructHelperMixin
from library.DockWidget import CDockWidget
from library.PreferencesMixin import CPreferencesMixin, CContainerPreferencesMixin
from library.RecordLock import CRecordLockMixin
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, forceTime, toVariant, \
    getPref, setPref, formatNum
from library.constants import etcTimeTable


class CFreeQueueDockWidget(CDockWidget):
    def __init__(self, parent):
        CDockWidget.__init__(self, parent)
        self.setWindowTitle(u'Номерки')
        self.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.content = None
        self.contentPreferences = {}
        self.connect(QtGui.qApp, QtCore.SIGNAL('dbConnectionChanged(bool)'), self.onConnectionChanged)
        self.setVisible(False)


    def loadPreferences(self, preferences):
        self.contentPreferences = getPref(preferences, 'content', {})
        CDockWidget.loadPreferences(self, preferences)
        if isinstance(self.content, CPreferencesMixin):
            self.content.loadPreferences(self.contentPreferences)


    def savePreferences(self):
        result = CDockWidget.savePreferences(self)
        self.updateContentPreferences()
        setPref(result,'content',self.contentPreferences)
        return result


    def updateContentPreferences(self):
        if isinstance(self.content, CPreferencesMixin):
            self.contentPreferences = self.content.savePreferences()


    def onConnectionChanged(self, value):
        if value:
            self.onDBConnected()
        else:
            self.onDBDisconnected()


    def onDBConnected(self):
        self.setWidget(None)
        if self.content:
            self.content.setParent(None)
            sip.delete(self.content)
            self.content = None
        if self.isVisible():
            self.content = CFreeQueueDockContent(self)
            self.content.loadPreferences(self.contentPreferences)
            self.setWidget(self.content)


    def onDBDisconnected(self):
        self.setWidget(None)
        if self.content:
            self.updateContentPreferences()
            self.content.setParent(None)
            sip.delete(self.content)
            self.content = None
        if self.isVisible():
            self.content = QtGui.QLabel(u'необходимо\nподключение\nк базе данных', self)
            self.content.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            self.content.setDisabled(True)
            self.setWidget(self.content)


    def showEvent(self, event):
        if not self.content:
            self.onConnectionChanged(bool(QtGui.qApp.db))


class CFreeQueueDockContent(QtGui.QWidget, Ui_Form, CConstructHelperMixin, CContainerPreferencesMixin, CCheckNetMixin, CRecordLockMixin):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        CCheckNetMixin.__init__(self)
        CRecordLockMixin.__init__(self)

        self.groupingSpeciality = forceBool(QtGui.qApp.preferences.appPrefs.get('groupingSpeciality', True))
        self.activityListIsShown = forceBool(QtGui.qApp.preferences.appPrefs.get('activityListIsShown', False))

        self.addModels('OrgStructure', COrgStructureModel(self, QtGui.qApp.currentOrgId()))
        self.addModels('Activity',     CActivityModel(self))
        self.addModels('AmbQueue',     CQueueModel(self))

        self.actFindArea =       QtGui.QAction(u'Найти участок', self)

        self.actFindArea.setObjectName('actFindArea')
        self.actAmbCreateOrder = QtGui.QAction(u'Поставить в очередь', self)
        self.actAmbCreateOrder.setObjectName('actAmbCreateOrder')
        self.actAmbReservedOrder = QtGui.QAction(u'Выполнить бронирование', self)
        self.actAmbReservedOrder.setObjectName('actAmbReservedOrder')
        self.actAmbUnreservedOrder = QtGui.QAction(u'Отменить бронирование', self)
        self.actAmbUnreservedOrder.setObjectName('actAmbUnreservedOrder')

        self.timer = QtCore.QTimer(self)
        self.timer.setObjectName('timer')
        self.timer.setInterval(60*1000) # раз в минуту
        self.timerCountMinute = 0
        self.appLockIdList = []
        self.reservedRowList = []

        self.setupUi(self)
        for treeWidget in [self.treeOrgStructure, self.treeOrgPersonnel]:
            treeWidget.setIndentation(12)
            treeWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        verticalHeader = self.tblAmbQueue.verticalHeader()
#        verticalHeader.show()
        verticalHeader.setResizeMode(QtGui.QHeaderView.Fixed)
#        self.setModels(self.treeOrgStructure, self.modelOrgStructure, self.selectionModelOrgStructure)
        self.setModels(self.tblAmbQueue,      self.modelAmbQueue,     self.selectionModelAmbQueue)

        self.onTreePersonnelSectionClicked(0, False)

        self.treeOrgStructure.createPopupMenu([self.actFindArea])
        self.tblAmbQueue.createPopupMenu([self.actAmbCreateOrder, self.actAmbReservedOrder, self.actAmbUnreservedOrder])

        self.onheaderTreeOSClicked(0, False)
#        orgStructureIndex = self.modelOrgStructure.findItemId(QtGui.qApp.currentOrgStructureId())
#        if orgStructureIndex and orgStructureIndex.isValid():
#            self.treeOrgStructure.setCurrentIndex(orgStructureIndex)
#            self.treeOrgStructure.setExpanded(orgStructureIndex, True)

        self.setDateRange()
#        self.updatePersonnel()
        self.onCurrentUserIdChanged()

#        self.updateQueueTable()
        self.connect(self.treeOrgStructure.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuTreeOrgStructureAboutToShow)
        self.connect(self.tblAmbQueue.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAmbAboutToShow)

        self.headerTreeOS = self.treeOrgStructure.header()
        self.headerTreeOS.setClickable(True)
        QtCore.QObject.connect(self.headerTreeOS, QtCore.SIGNAL('sectionClicked(int)'), self.onheaderTreeOSClicked)

        self.headerTreePersonnel = self.treeOrgPersonnel.header()
        self.headerTreePersonnel.setClickable(True)
        QtCore.QObject.connect(self.headerTreePersonnel, QtCore.SIGNAL('sectionClicked(int)'),
                               self.onTreePersonnelSectionClicked)

        self.connect(QtGui.qApp, QtCore.SIGNAL('currentOrgIdChanged()'), self.onCurrentOrgIdChanged)
        self.connect(QtGui.qApp, QtCore.SIGNAL('currentUserIdChanged()'), self.onCurrentUserIdChanged)
        self.activityListIsShown = False
        self.prevClientId = None
        self.prevComplaints = ''
        self.reservedRow = -1
        self.timer.start()


    def onTreePersonnelSectionClicked(self, col, reverse=True):
        if reverse:
            self.groupingSpeciality = not self.groupingSpeciality

        if hasattr(self, 'selectionModelPersonnel'):
            self.disconnect(self.selectionModelPersonnel,
                            QtCore.SIGNAL('currentChanged(QModelIndex, QModelIndex)'),
                            self.on_selectionModelPersonnel_currentChanged)

        self.treeOrgPersonnel.setModel(None)
        if self.groupingSpeciality:
            self.addModels('Personnel', CResourcesPersonnelModel([], self))
        else:
            self.addModels('Personnel', CFlatResourcesPersonnelModel([], self))

        self.setModels(self.treeOrgPersonnel, self.modelPersonnel, self.selectionModelPersonnel)
        self.connect(self.selectionModelPersonnel,
                     QtCore.SIGNAL('currentChanged(QModelIndex, QModelIndex)'),
                     self.on_selectionModelPersonnel_currentChanged)

        QtGui.qApp.preferences.appPrefs['groupingSpeciality'] = self.groupingSpeciality

        if self.activityListIsShown:
            self.updatePersonnelActivity()
        else:
            self.updatePersonnel()



    def onheaderTreeOSClicked(self, col, reverse=True):
        if reverse:
            self.activityListIsShown = not self.activityListIsShown

        if not self.activityListIsShown:
            self.treeOrgStructure.setModel(None)
            self.setModels(self.treeOrgStructure, self.modelOrgStructure, self.selectionModelOrgStructure)
            orgStructureIndex = self.modelOrgStructure.findItemId(QtGui.qApp.currentOrgStructureId())
            if orgStructureIndex and orgStructureIndex.isValid():
                self.treeOrgStructure.setCurrentIndex(orgStructureIndex)
                self.treeOrgStructure.setExpanded(orgStructureIndex, True)
            self.updatePersonnel()
        else:
             self.treeOrgStructure.setModel(None)
             self.setModels(self.treeOrgStructure, self.modelActivity, self.selectionModelActivity)
             self.updatePersonnelActivity()


        QtGui.qApp.preferences.appPrefs['activityListIsShown'] = self.activityListIsShown

    def sizeHint(self):
        return QtCore.QSize(10, 10)


    def onCurrentOrgIdChanged(self):
        self.modelOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.updatePersonnel()


    def onCurrentUserIdChanged(self):
        if QtGui.qApp.userOrgStructureId:
            index = self.modelOrgStructure.findItemId(QtGui.qApp.userOrgStructureId)
            if index and index.isValid():
                self.treeOrgStructure.setCurrentIndex(index)
        if QtGui.qApp.userSpecialityId:
            index = self.modelPersonnel.findPersonId(QtGui.qApp.getDrId())
            if index and index.isValid():
                self.treeOrgPersonnel.setCurrentIndex(index)


    def setDateRange(self):
        today = QtCore.QDate.currentDate()
        self.edtBegDate.setDateRange(today, today.addYears(1))


    def getPersonIdList(self):
        treeIndex = self.treeOrgPersonnel.currentIndex()
        personIdList = self.modelPersonnel.getItemIdList(treeIndex)
        return personIdList


    def checkNetApplicable(self, personId, clientId, date):
        return self.checkClientAttach(personId, clientId, date, True) and \
              (self.checkClientAttendace(personId, clientId) or \
               self.confirmClientAttendace(self, personId, clientId)) and \
               self.confirmClientPolicyConstraint(self, clientId)


    def updatePersonnel(self):
        treeIndex = self.treeOrgStructure.currentIndex()
        orgStructureIdList = self.modelOrgStructure.getItemIdList(treeIndex)
        begDate = self.edtBegDate.date()
        self.modelPersonnel.setOrgStructureIdList(self.modelOrgStructure.orgId, orgStructureIdList, begDate)
        if self.modelOrgStructure.isLeaf(treeIndex):
            self.treeOrgPersonnel.expandAll()
            self.treeOrgPersonnel.setCurrentIndex(self.modelPersonnel.getFirstLeafIndex())
        self.updateQueueTable()


    def updatePersonnelActivity(self):
        treeIndex = self.treeOrgStructure.currentIndex()
        activityIdList = self.modelActivity.getItemIdList(treeIndex)
        begDate = self.edtBegDate.date()
        self.modelPersonnel.setActivityIdList(QtGui.qApp.currentOrgId(), activityIdList, begDate)
        if self.modelActivity.isLeaf(treeIndex):
            self.treeOrgPersonnel.expandAll()
            self.treeOrgPersonnel.setCurrentIndex(self.modelPersonnel.getFirstLeafIndex())
        self.updateQueueTable()


    def updateQueueTable(self):
        self.timer.stop()
        try:
            personIdList = self.getPersonIdList()
            begDate = self.edtBegDate.date()
            
            endDateForPerson = {}
            if not QtGui.qApp.userHasRight(urQueueCancelMaxDateLimit):
                for personId in personIdList:
                    endDate = begDate.addMonths(2)
                    db = QtGui.qApp.db
                    table = db.table('Person')
                    record = db.getRecordEx(table, 
                                            [table['lastAccessibleTimelineDate'], 
                                             table['timelineAccessibleDays']], 
                                            [table['deleted'].eq(0), table['id'].eq(personId)])
                    if record:
                        lastAccessibleTimelineDate = forceDate(record.value('lastAccessibleTimelineDate'))
                        timelineAccessibleDays = forceInt(record.value('timelineAccessibleDays'))
                        if lastAccessibleTimelineDate:
                            endDate = lastAccessibleTimelineDate
                        if timelineAccessibleDays:
                            accessibleDays = begDate.addDays(timelineAccessibleDays)
                            if accessibleDays < endDate:
                                endDate = accessibleDays
                    endDateForPerson[personId] = endDate
            
            timeRange = None
            if self.chkEnableTime:
                begTime = self.edtBegTime.time()
                endTime = self.edtEndTime.time()
                if begTime<endTime:
                    timeRange = begTime, endTime
            self.modelAmbQueue.setPersonAndDate(personIdList, begDate, timeRange, endDateForPerson)
        finally:
            self.timer.start()


    def getQueueActionIdListForClient(self, date, specialityId, clientId):
        etcQueue = 'queue'
        atcQueue = 'queue'
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableEventType = db.table('EventType')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tablePerson = db.table('Person')
        tableActionProperty_Action = db.table('ActionProperty_Action')
        tableRBSpeciality = db.table('rbSpeciality')
        tableQuery = tableAction
        tableQuery = tableQuery.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        tableQuery = tableQuery.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        tableQuery = tableQuery.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        tableQuery = tableQuery.leftJoin(tableActionProperty_Action, tableActionProperty_Action['value'].eq(tableAction['id']))
        tableQuery = tableQuery.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
        tableQuery = tableQuery.leftJoin(tableRBSpeciality, tableRBSpeciality['id'].eq(tablePerson['speciality_id']))
        cols = [tableAction['id']]
        currentDate = QtCore.QDate.currentDate()
        cond = [tableAction['deleted'].eq(0),
                tableAction['status'].ne(0),
                tableEvent['deleted'].eq(0),
                tableEventType['deleted'].eq(0),
                tablePerson['deleted'].eq(0),
                tableEvent['client_id'].eq(clientId),
                tableEvent['setDate'].dateGe(currentDate),
                tableEventType['code'].eq(etcQueue),
                tableActionType['code'].eq(atcQueue),
                #tablePerson['speciality_id'].eq(specialityId)
                ]
        OKSOCode = forceString(db.translate('rbSpeciality', 'id', specialityId, 'OKSOCode'))
        OKSOCodeList = [u'040122', u'040819', u'040110']
        if OKSOCode in OKSOCodeList:
            cond.append(tableRBSpeciality['OKSOCode'].inlist(OKSOCodeList))
        else:
            cond.append(tablePerson['speciality_id'].eq(specialityId))
        return db.getIdList(tableQuery, cols, cond, 'Action.directionDate')


    def queueingEnabled(self, date, personId, specialityId, orgStructureId, clientId):
        deathDate = getDeathDate(clientId)
        if deathDate:
            QtGui.QMessageBox.warning(self, u'Внимание!', u'Этот пациент не может быть записан к врачу, потому что есть отметка что он уже умер %s' % forceString(deathDate))
            return False
        actionIdList = self.getQueueActionIdListForClient(date, specialityId, clientId)
        if actionIdList:
            messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, u'Внимание!', u'Этот пациент уже записан к врачу этой специальности\nПодтвердите повторную запись')
            messageBox.addButton(u'Ок', QtGui.QMessageBox.YesRole)
            messageBox.addButton(u'Отмена', QtGui.QMessageBox.NoRole)
            confirmation = messageBox.exec_()
            if confirmation == 1:
                return False
        if not QtGui.qApp.userHasRight(urQueueWithEmptyContacts):
            db = QtGui.qApp.db
            stmt = u"Select id From ClientContact where client_id = %s and deleted = 0 Limit 0, 1" %forceString(clientId)
            query = db.query(stmt)
            query.first()
            if not forceInt(query.record().value('id')):
                QtGui.QMessageBox.warning(self, u'Внимание!', u'Невозможно создать обращение. У данного пациента не указаны контакты')
                return False
        plan, busy = getQueueSize(personId, date)
        quota, quotaName = getQuota(personId, plan)
        if quota<=busy:
            message = u'Квота на запись исчерпана (%s).\nВсё равно продолжить?'  % quotaName
            if QtGui.QMessageBox.critical(self,
                                    u'Внимание!',
                                    message,
                                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                                    QtGui.QMessageBox.No) == QtGui.QMessageBox.No: return False
        return True


    def createOrder(self, timeTableEventId, date, index, time, personId, office, clientId):
        if self.checkNetApplicable(personId, clientId, date):
            db = QtGui.qApp.db
            specialityId = self.getPersonSpecialityId(personId)
            orgStructureId = self.getPersonOrgStructureId(personId)
            if ( personId
                and specialityId
                and orgStructureId
                and clientId
                and timeTableEventId
                and time is not None
                and self.queueingEnabled(date, personId, specialityId, orgStructureId, clientId)):
                action = CAction.getAction(timeTableEventId, 'amb')
                if action.getId() and self.lock('Action', action.getId()):
                    if self._appLockId and self._appLockId not in self.appLockIdList:
                        self.appLockIdList.append(self._appLockId)
                    dataChanged = False
                    try:
                        complaints = ''
                        #start changes by atronah 04.06.2012 for issue#350
                        record = db.getRecord(db.table('Person'),  ('addComment',  'commentText'),  personId)
                        if forceBool(record.value('addComment')):
                            complaints += '---\n' + forceString(record.value('commentText'))
                        #end changes by atronah
                        queueActionIdList = action['queue']
                        if 0<=index<len(queueActionIdList) and queueActionIdList[index]:
                            dataChanged = True
                        else:
                            db.transaction()
                            try:
                                queueEventId, queueActionId = createQueueEvent(personId, date, time, clientId, complaints, office)
                                count = index-len(queueActionIdList)+1
                                if count>0:
                                    queueActionIdList.extend([None]*count)
                                queueActionIdList[index] = queueActionId
                                action['queue'] = queueActionIdList
                                action.save()
                                db.commit()
                                return True
                            except:
                                db.rollback()
                                raise
                    finally:
                        pass
                    if dataChanged:
                        QtGui.QMessageBox.warning( self,
                            u'Внимание!',
                            u'Запись на это время невозможно, так как оно уже занято',
                            QtGui.QMessageBox.Ok,
                            QtGui.QMessageBox.Ok)
        return False


    def reservedOrder(self, time, personId, actionPropertyId, actionPropertyIndex, row):
        self.releaseLock()
        specialityId = self.getPersonSpecialityId(personId)
        orgStructureId = self.getPersonOrgStructureId(personId)
        countTickets = self.edtCountTickets.value()
        reservedRowList = []
        if ( personId
            and specialityId
            and orgStructureId
            and actionPropertyId
            and time is not None):
            if countTickets > 1:
                items = self.modelAmbQueue.items
                item = items[row]
                currentDate = forceDate(item.value('date'))
                personIdItem = forceRef(item.value('person_id'))
                actionPropertyIndexItem = forceInt(item.value('actionPropertyIndex'))
                actionPropertyIndexFirst = actionPropertyIndexItem
                lenItems = len(items)
                countTicketsItem = countTickets - 1
                if row not in reservedRowList:
                    reservedRowList.append(row)
                for rowItem in range(row + 1, lenItems):
                    item = items[rowItem]
                    date = forceDate(item.value('date'))
                    personId = forceRef(item.value('person_id'))
                    actionPropertyIndex = forceInt(item.value('actionPropertyIndex'))
                    if personId == personIdItem and actionPropertyIndex == (actionPropertyIndexItem + 1) and countTicketsItem > 0 and currentDate == date:
                        if rowItem not in reservedRowList:
                            reservedRowList.append(rowItem)
                        actionPropertyIndexItem = actionPropertyIndex
                        countTicketsItem -= 1
                        if countTicketsItem == 0 or actionPropertyIndexItem > (len(items) - 1):
                            break
                rowTicket = row - 1
                while countTicketsItem > 0:
                    if rowTicket < 0:
                        break
                    item = items[rowTicket]
                    date = forceDate(item.value('date'))
                    personId = forceRef(item.value('person_id'))
                    actionPropertyIndex = forceInt(item.value('actionPropertyIndex'))
                    if personId == personIdItem and actionPropertyIndex == (actionPropertyIndexFirst - 1) and countTicketsItem > 0 and currentDate == date:
                        if rowTicket not in reservedRowList:
                            reservedRowList.append(rowTicket)
                        actionPropertyIndexFirst = actionPropertyIndex
                        countTicketsItem -= 1
                        if countTicketsItem == 0 or actionPropertyIndexFirst < 0:
                            break
                    rowTicket -= 1
                if countTicketsItem == 0 and countTickets == len(reservedRowList):
                    for reservedRow in reservedRowList:
                        item = items[reservedRow]
                        actionPropertyId = forceRef(item.value('actionProperty_id'))
                        actionPropertyIndex = forceInt(item.value('actionPropertyIndex'))
                        if actionPropertyId and actionPropertyIndex:
                            if self.lock(u'ActionProperty_Time', actionPropertyId, actionPropertyIndex):
                                if self._appLockId:
                                    if self._appLockId not in self.appLockIdList:
                                        self.appLockIdList.append(self._appLockId)
                                    if reservedRow not in self.reservedRowList:
                                        self.reservedRowList.append(reservedRow)
                                    self.reservedRow = row
                                    self.lblReservedOrder.setText(u'БРОНЬ')
                    self.reservedRowList.sort()
            elif self.lock(u'ActionProperty_Time', actionPropertyId, actionPropertyIndex):
                if self._appLockId:
                    self.appLockIdList = [self._appLockId]
                    self.reservedRowList = [row]
                    self.reservedRow = row
                    self.lblReservedOrder.setText(u'БРОНЬ')


    def releaseLock(self):
        for appLockId in self.appLockIdList:
            self._timerProlongLock.stop()
            db = QtGui.qApp.db
            query = db.query('CALL ReleaseAppLock(%d)' % (appLockId))
        self.appLockIdList = []
        self.reservedRowList = []
        self._appLockId = None
        self.reservedRow = -1
        self.lblReservedOrder.setText(u'')
        self.timerCountMinute = 0


    @QtCore.pyqtSlot()
    def on_timer_timeout(self):
        if self.timerCountMinute > 2:
            self.releaseLock()
        else:
            self.timerCountMinute += 1
        self.setDateRange()
        if self.isVisible():
            self.modelAmbQueue.updateData()


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self):
        self.updateQueueTable()


    @QtCore.pyqtSlot()
    def on_btnSetToday_clicked(self):
        today = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(today)


    @QtCore.pyqtSlot(bool)
    def on_chkEnableTime_toogled(self, value):
        self.updateQueueTable()


    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtBegTime_timeChanged(self, value):
        self.updateQueueTable()


    @QtCore.pyqtSlot(QtCore.QTime)
    def on_edtEndTime_timeChanged(self, value):
        self.updateQueueTable()


    @QtCore.pyqtSlot(int)
    def on_edtCountTickets_valueChanged(self, value):
        self.on_actAmbUnreservedOrder_triggered()
        self.modelAmbQueue.countTickets = value
        self.updateQueueTable()


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelOrgStructure_currentChanged(self, current, previous):
        if not hasattr(self, 'groupingSpeciality'):
            self.groupingSpeciality = forceBool(QtGui.qApp.preferences.appPrefs.get('groupingSpeciality', True))
        self.updatePersonnel()


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActivity_currentChanged(self, current, previous):
        if not hasattr(self, 'groupingSpeciality'):
            self.groupingSpeciality = forceBool(QtGui.qApp.preferences.appPrefs.get('groupingSpeciality', True))
        self.updatePersonnelActivity()


#    @QtCore.pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModelPersonnel_currentChanged(self, current, previous):
        self.updateQueueTable()


    def popupMenuTreeOrgStructureAboutToShow(self):
        currentClientId = QtGui.qApp.currentClientId()
        self.actFindArea.setEnabled(bool(currentClientId))


    @QtCore.pyqtSlot()
    def on_actFindArea_triggered(self):
        currentClientId = QtGui.qApp.currentClientId()
        if currentClientId:
            r = getClientAddressEx(currentClientId)
            addressId = forceRef(r.value('address_id')) if r else None
            idList = findOrgStructuresByAddress(addressId, QtGui.qApp.currentOrgId())
            id = self.filterStructureId(idList, QtGui.qApp.currentOrgStructureId())
            if id:
                index = self.modelOrgStructure.findItemId(id)
                self.treeOrgStructure.setCurrentIndex(index)
            else:
                msg = u'Адрес пациента не соответствует никакому участку' if addressId else u'Адрес пациента пуст'
                QtGui.QMessageBox.warning( self.parent(),
                                           u'Поиск участка',
                                           msg,
                                           QtGui.QMessageBox.Ok,
                                           QtGui.QMessageBox.Ok)


    def filterStructureId(self, idList, topOrgStructureId):
        index = self.modelOrgStructure.findItemId(topOrgStructureId)
        childrenIdList = self.modelOrgStructure.getItemIdList(index)
        filteredList = list(set(childrenIdList).intersection(set(idList)))
        if filteredList:
            filteredList.sort()
            return filteredList[0]
        else:
            return None


    def popupMenuAmbAboutToShow(self):
        currentClientId = QtGui.qApp.currentClientId()
        self.actAmbCreateOrder.setEnabled(bool(currentClientId))
        self.actAmbReservedOrder.setEnabled(bool(currentClientId))
        self.actAmbUnreservedOrder.setEnabled(bool(currentClientId and self._appLockId))


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblAmbQueue_doubleClicked(self, index):
        if QtGui.qApp.doubleClickQueueFreeOrder() == 2:
            self.on_actAmbReservedOrder_triggered()
        else:
            self.on_actAmbCreateOrder_triggered()


    @QtCore.pyqtSlot()
    def on_actAmbCreateOrder_triggered(self):
        clientId = QtGui.qApp.currentClientId()
        if not self.reservedRowList:
            row = self.tblAmbQueue.currentIndex().row()
            self.ambCreateOrder(row, clientId)
        else:
            for row in self.reservedRowList:
                self.ambCreateOrder(row, clientId)
        self.on_actAmbUnreservedOrder_triggered()
        QtGui.qApp.emitCurrentClientInfoChanged()
        self.updateQueueTable()


    def ambCreateOrder(self, row, clientId):
        if clientId and row > -1:
            self.updateQueueTable()
            timeTableEventId, date, index, time, personId, office, begTime, endTime, actionPropertyId, actionPropertyIndex = self.modelAmbQueue.getTimeTableDetails(row)
            if clientId and self.createOrder(timeTableEventId, date, index, time, personId, office, clientId):
                printOrder(self, clientId, 0, date, office, personId, index+1, time, unicode(formatTimeRange((begTime, endTime))))


    @QtCore.pyqtSlot()
    def on_actAmbReservedOrder_triggered(self):
        row = self.tblAmbQueue.currentIndex().row()
        timeTableEventId, date, index, time, personId, office, begTime, endTime, actionPropertyId, actionPropertyIndex = self.modelAmbQueue.getTimeTableDetails(row)
        self.reservedOrder(time, personId, actionPropertyId, actionPropertyIndex, row)
        self.updateQueueTable()


    @QtCore.pyqtSlot()
    def on_actAmbUnreservedOrder_triggered(self):
        self.releaseLock()


    @QtCore.pyqtSlot(int)
    def on_modelAmbQueue_dataLoadDone(self, count):
        if count == 0:
            text = u'Список пуст'
        else:
            text = u'В списке '+formatNum(count, (u'номерок', u'номерка', u'номерков'))
        self.lblQueueItemsCount.setText(text)



class CQueueModel(QtCore.QAbstractTableModel):
    __pyqtSignals__ = ('beforeReset()',
                       'afterReset()',
                       'dataLoadDone(int)',
                      )

    headerText = [u'Дата', u'Время', u'Врач', u'Каб']

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        self.mapKeyToIndex = {}

        self.personIdList = []
        self.begDate = None
        self.endDateForPerson = {}
        self.timeRange = None

        self.etiTimeTable    = None
        self.atiAmb          = None # ati == ActionTypeId, atiAmb == ActionTypeId with code = 'amb'
        self.aptiAmbTimes    = None # apti == ActionPropertyTypeId, aptiAmbTimes == ActionPropertyTypeId with ActionType.code = 'amb' and ActionPropertyType.name = 'times'
        self.aptiAmbQueue    = None # like prev.
        self.aptiAmbOffice   = None
        self.aptiAmbOffice1  = None
        self.aptiAmbOffice2  = None
        self.aptiAmbBegTime  = None
        self.aptiAmbBegTime1 = None
        self.aptiAmbBegTime2 = None
        self.aptiAmbEndTime  = None
        self.aptiAmbEndTime1 = None
        self.aptiAmbEndTime2 = None
        self.atiTimeLine     = None # ati with code TimeLine
        self.aptiTimeLineReasonOfAbsence = None
        self.countTickets = 1

    def columnCount(self, index = QtCore.QModelIndex()):
        return len(self.headerText)


    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self.items)


    def flags(self, index):
        result = QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled
        return result


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            if row<len(self.items):
                column = index.column()
                item = self.items[row]
                value = item.value(column)
                if column == 0:
                    return QtCore.QVariant(forceDate(value))
                if column == 1:
                    return QtCore.QVariant(forceTime(value).toString('H:mm'))
                elif column == 3:
                    office, begTime, endTime = self.getOfficeAndTimes(item)
                    return QtCore.QVariant(office)
                return value
        elif role == QtCore.Qt.ForegroundRole:
            row = index.row()
            item = self.items[row]
            currentRecordId = forceRef(item.value('actionProperty_id'))
            currentIndex = forceInt(item.value('actionPropertyIndex'))
            if currentRecordId:
                record = self.getLockInfo(currentRecordId, currentIndex)
                if record:
                    recordId = forceRef(record.value('recordId'))
                    if currentRecordId == recordId:
                        return toVariant(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
        elif role == QtCore.Qt.FontRole:
            row = index.row()
            item = self.items[row]
            currentRecordId = forceRef(item.value('actionProperty_id'))
            currentIndex = forceInt(item.value('actionPropertyIndex'))
            if currentRecordId:
                record = self.getLockInfo(currentRecordId, currentIndex)
                if record:
                    personId = forceRef(record.value('person_id'))
                    if personId:
                        font = QtGui.QFont()
                        if personId == QtGui.qApp.getDrId():
                            font.setBold(True)
                        else:
                            font.setItalic(True)
                        return QtCore.QVariant(font)
        return QtCore.QVariant()


    def getLockInfo(self, recordId, recordIndex):
        db = QtGui.qApp.db
        tableAppLock = db.table('AppLock')
        tableAppLock_Detail = db.table('AppLock_Detail')
        queryTable = tableAppLock.innerJoin(tableAppLock_Detail, tableAppLock_Detail['master_id'].eq(tableAppLock['id']))
        cond = [tableAppLock_Detail['recordIndex'].eq(recordIndex),
                tableAppLock_Detail['recordId'].eq(recordId)]
        cond.append(u'tableName = \'ActionProperty_Time\'')
        record = db.getRecordEx(queryTable, [tableAppLock['person_id'], tableAppLock_Detail['recordId']], cond)
        return record


    def getKey(self, row):
        item = self.items[row]
        result = (forceDate(item.value(0)),
                  forceTime(item.value(1)),
                  forceString(item.value(2)))
        return result


    @staticmethod
    def getOfficeAndTimes(item):
        time     = forceTime(item.value('time'))
        office   = forceString(item.value('office'))
        begTime  = forceTime(item.value('begTime'))
        endTime  = forceTime(item.value('endTime'))
        office1  = forceString(item.value('office1'))
        begTime1 = forceTime(item.value('begTime1'))
        endTime1 = forceTime(item.value('endTime1'))
        office2  = forceString(item.value('office2'))
        begTime2 = forceTime(item.value('begTime2'))
        endTime2 = forceTime(item.value('endTime2'))
        if office1 and begTime1 and endTime1 and begTime1<=time<endTime1:
            office = office1
            begTime = begTime1
            endTime = endTime1
        elif office2 and begTime2 and endTime2 and begTime2<=time<endTime2:
            office = office2
            begTime = begTime2
            endTime = endTime2
        return office, begTime, endTime


    def getTimeTableDetails(self, row):
        item = self.items[row]
        time     = forceTime(item.value('time'))
        office, begTime, endTime = self.getOfficeAndTimes(item)

        result = (forceRef(item.value('event_id')),
                  forceDate(item.value('date')),
                  forceInt(item.value('index')),     # seq.no
                  time,
                  forceRef(item.value('person_id')),
                  office,
                  begTime,
                  endTime,
                  forceRef(item.value('actionProperty_id')),
                  forceInt(item.value('actionPropertyIndex'))
                 )
        return result


    def lookupRowByKey(self, key):
        lookupDate, lookupTime, lookupPerson = key
        for row, item in enumerate(self.items):
            date = forceDate(item.value(0))
            time = forceTime(item.value(1))
            person = forceString(item.value(2))
            if date>lookupDate or date==lookupDate and (time>lookupTime or lookupTime==time and person>=lookupPerson):
                return row
        return len(self.items)-1


    def setPersonAndDate(self, personIdList, begDate, timeRange, endDateForPerson=None):
        if not endDateForPerson:
            endDateForPerson = {}
        if ( self.personIdList != personIdList
             or self.begDate != begDate
             or self.timeRange != timeRange):
            self.personIdList = personIdList
            self.begDate = begDate
            self.endDateForPerson  = endDateForPerson
            self.timeRange = timeRange
            self.loadData()
            self.reset()
        else:
            self.updateData()


    def loadData(self):
        if self.atiAmb is None:
            try:
                self.etiTimeTable = getEventType(etcTimeTable).eventTypeId
                actionType = CActionTypeCache.getByCode('amb')
                self.atiAmb = actionType.id
                self.aptiAmbTimes = actionType.getPropertyType('times').id
                self.aptiAmbQueue = actionType.getPropertyType('queue').id
                self.aptiAmbOffice = actionType.getPropertyType('office').id
                self.aptiAmbOffice1 = actionType.getPropertyType('office1').id
                self.aptiAmbOffice2 = actionType.getPropertyType('office2').id

                self.aptiAmbBegTime  = actionType.getPropertyType('begTime').id
                self.aptiAmbBegTime1 = actionType.getPropertyType('begTime1').id
                self.aptiAmbBegTime2 = actionType.getPropertyType('begTime2').id

                self.aptiAmbEndTime  = actionType.getPropertyType('endTime').id
                self.aptiAmbEndTime1 = actionType.getPropertyType('endTime1').id
                self.aptiAmbEndTime2 = actionType.getPropertyType('endTime2').id

                actionType = CActionTypeCache.getByCode('timeLine')
                self.atiTimeLine = actionType.id
                self.aptiTimeLineReasonOfAbsence = actionType.getPropertyType('reasonOfAbsence').id
            except:
                self.atiAmb = False

        self.items = []
        if self.atiAmb and self.personIdList:
            db = QtGui.qApp.db
            now = QtCore.QDateTime.currentDateTime()
            currentDate = now.date()
            currentTime = now.time()
            if self.timeRange:
                timeRangeCond = 'AND APTimesValue.value BETWEEN %s AND %s' % (db.formatTime(self.timeRange[0]), db.formatTime(self.timeRange[1]))
            else:
                timeRangeCond = ''
            strTickets = u''
            whereTickets = u''
            if self.countTickets > 1:
                for ticket in range(1, self.countTickets):
                    strTickets += u' LEFT JOIN ActionProperty_Action AS APQueueValue%s ON APQueueValue%s.id = APQueue.id AND APQueueValue%s.index = APQueueValue.index + %d'%(str(ticket), str(ticket), str(ticket), ticket)
                    whereTickets += u' AND APQueueValue%s.value IS NULL'%(str(ticket))
            stmt = u'SELECT Event.setDate AS date,'\
                   u' APTimesValue.value AS time,'\
                   u' vrbPersonWithSpeciality.name AS name,'\
                   u' APTimesValue.id AS actionProperty_id,'\
                   u' APTimesValue.index AS actionPropertyIndex,'\
                   u' APOfficeValue.value   AS office,'\
                   u' APBegTimeValue.value  AS begTime,'\
                   u' APEndTimeValue.value  AS endTime,'\
                   u' APOffice1Value.value  AS office1,'\
                   u' APBegTime1Value.value AS begTime1,'\
                   u' APEndTime1Value.value AS endTime1,'\
                   u' APOffice2Value.value  AS office2,'\
                   u' APBegTime2Value.value AS begTime2,'\
                   u' APEndTime2Value.value AS endTime2,'\
                   u' Event.id AS event_id, Event.setPerson_id AS person_id, Action.id AS action_id, APTimesValue.`index` AS `index`'\
                   u' FROM Action'\
                   u' LEFT JOIN Event ON Event.id = Action.event_id'\
                   u' LEFT JOIN Person ON Person.id = Event.setPerson_id'\
                   u' LEFT JOIN vrbPersonWithSpeciality ON vrbPersonWithSpeciality.id = Event.setPerson_id'\
                   u' LEFT JOIN ActionProperty        AS APTimes         ON APTimes.action_id = Action.id AND APTimes.type_id = %(aptiAmbTimes)d'\
                   u' LEFT JOIN ActionProperty_Time   AS APTimesValue    ON APTimesValue.id = APTimes.id'\
                   u' LEFT JOIN ActionProperty        AS APQueue         ON APQueue.action_id = Action.id AND APQueue.type_id = %(aptiAmbQueue)d'\
                   u' LEFT JOIN ActionProperty_Action AS APQueueValue    ON APQueueValue.id = APQueue.id AND APTimesValue.`index` = APQueueValue.`index`'\
                   u'%(strTickets)s'\
                   u' LEFT JOIN ActionProperty        AS APOffice        ON APOffice.action_id = Action.id AND APOffice.type_id = %(aptiAmbOffice)d'\
                   u' LEFT JOIN ActionProperty_String AS APOfficeValue   ON APOfficeValue.id = APOffice.id AND APOfficeValue.`index` = 0'\
                   u' LEFT JOIN ActionProperty        AS APOffice1       ON APOffice1.action_id = Action.id AND APOffice1.type_id = %(aptiAmbOffice1)d'\
                   u' LEFT JOIN ActionProperty_String AS APOffice1Value  ON APOffice1Value.id = APOffice1.id AND APOffice1Value.`index` = 0'\
                   u' LEFT JOIN ActionProperty        AS APOffice2       ON APOffice2.action_id = Action.id AND APOffice2.type_id = %(aptiAmbOffice2)d'\
                   u' LEFT JOIN ActionProperty_String AS APOffice2Value  ON APOffice2Value.id = APOffice2.id AND APOffice2Value.`index` = 0'\
                   u' LEFT JOIN ActionProperty        AS APBegTime       ON APBegTime.action_id = Action.id AND APBegTime.type_id = %(aptiAmbBegTime)d'\
                   u' LEFT JOIN ActionProperty_Time   AS APBegTimeValue  ON APBegTimeValue.id = APBegTime.id AND APBegTimeValue.`index` = 0'\
                   u' LEFT JOIN ActionProperty        AS APBegTime1      ON APBegTime1.action_id = Action.id AND APBegTime1.type_id = %(aptiAmbBegTime1)d'\
                   u' LEFT JOIN ActionProperty_Time   AS APBegTime1Value ON APBegTime1Value.id = APBegTime1.id AND APBegTime1Value.`index` = 0'\
                   u' LEFT JOIN ActionProperty        AS APBegTime2      ON APBegTime2.action_id = Action.id AND APBegTime2.type_id = %(aptiAmbBegTime2)d'\
                   u' LEFT JOIN ActionProperty_Time   AS APBegTime2Value ON APBegTime2Value.id = APBegTime2.id AND APBegTime2Value.`index` = 0'\
                   u' LEFT JOIN ActionProperty        AS APEndTime       ON APEndTime.action_id = Action.id AND APEndTime.type_id = %(aptiAmbEndTime)d'\
                   u' LEFT JOIN ActionProperty_Time   AS APEndTimeValue  ON APEndTimeValue.id = APEndTime.id AND APEndTimeValue.`index` = 0'\
                   u' LEFT JOIN ActionProperty        AS APEndTime1      ON APEndTime1.action_id = Action.id AND APEndTime1.type_id = %(aptiAmbEndTime1)d'\
                   u' LEFT JOIN ActionProperty_Time   AS APEndTime1Value ON APEndTime1Value.id = APEndTime1.id AND APEndTime1Value.`index` = 0'\
                   u' LEFT JOIN ActionProperty        AS APEndTime2      ON APEndTime2.action_id = Action.id AND APEndTime2.type_id = %(aptiAmbEndTime2)d'\
                   u' LEFT JOIN ActionProperty_Time   AS APEndTime2Value ON APEndTime2Value.id = APEndTime2.id AND APEndTime2Value.`index` = 0'\
                   u' LEFT JOIN Action AS TimeLineAction ON TimeLineAction.event_id = Event.id AND TimeLineAction.actionType_id = %(atiTimeLine)d'\
                   u' LEFT JOIN ActionProperty        AS APROA         ON APROA.action_id = TimeLineAction.id AND APROA.type_id = %(aptiTimeLineReasonOfAbsence)d'\
                   u' LEFT JOIN ActionProperty_rbReasonOfAbsence AS APROAValue ON APROAValue.id = APROA.id AND APROAValue.`index` = 0'\
                   u' WHERE Action.deleted=0 AND Event.deleted=0 AND Event.eventType_id=%(eventTypeId)d AND (TimeLineAction.id IS NULL OR TimeLineAction.deleted=0)'\
                   u' AND Action.actionType_id = %(atiAmb)d'\
                   u' AND Event.setDate>=%(begDate)s'\
                   u' AND Event.setPerson_id IN (%(personIdList)s)'\
                   u' AND APQueueValue.value IS NULL'\
                   u' %(whereTickets)s'\
                   u' AND APTimesValue.value IS NOT NULL'\
                   u' AND APROAValue.value IS NULL'\
                   u' AND (Event.setDate>%(currentDate)s OR APTimesValue.value>%(currentTime)s)'\
                   u' AND (Person.lastAccessibleTimelineDate IS NULL OR Person.lastAccessibleTimelineDate = \'0000-00-00\' OR DATE(Event.setDate)<=Person.lastAccessibleTimelineDate)' \
                   u' %(timeRange)s'\
                   u' ORDER BY Event.setDate, time, vrbPersonWithSpeciality.name, Event.setPerson_id'\
                   u' LIMIT 0, 500' % {
                        'eventTypeId'    : self.etiTimeTable,
                        'aptiAmbTimes'   : self.aptiAmbTimes,
                        'aptiAmbQueue'   : self.aptiAmbQueue,
                        'strTickets'     : strTickets,
                        'aptiAmbOffice'  : self.aptiAmbOffice,
                        'aptiAmbOffice1' : self.aptiAmbOffice1,
                        'aptiAmbOffice2' : self.aptiAmbOffice2,
                        'aptiAmbBegTime' : self.aptiAmbBegTime,
                        'aptiAmbBegTime1': self.aptiAmbBegTime1,
                        'aptiAmbBegTime2': self.aptiAmbBegTime2,
                        'aptiAmbEndTime' : self.aptiAmbEndTime,
                        'aptiAmbEndTime1': self.aptiAmbEndTime1,
                        'aptiAmbEndTime2': self.aptiAmbEndTime2,
                        'atiAmb'         : self.atiAmb,
                        'atiTimeLine'    : self.atiTimeLine,
                        'aptiTimeLineReasonOfAbsence': self.aptiTimeLineReasonOfAbsence,
                        'begDate'        : db.formatDate(self.begDate if self.begDate else currentDate),
                        'personIdList'   : ', '.join([str(id) for id in self.personIdList]) if self.personIdList else 'NULL',
                        'whereTickets'   : whereTickets,
                        'currentDate'    : db.formatDate(currentDate),
                        'currentTime'    : db.formatTime(currentTime),
                        'timeRange'      : timeRangeCond
                    }
            query = db.query(stmt)
            while query.next():
                record = query.record()
                isAppend = True
                
                personId = forceRef(record.value('person_id'))
                date = forceDate(record.value('date'))
                personEndDate = self.endDateForPerson.get(personId, None)
                #Если у персоны есть ограничение по верхней дате и дата номерка больше даты ограничения, 
                if personEndDate and  date > personEndDate:
                    #то не добавлять в список номерков
                    isAppend = False
                if isAppend:
                    self.items.append(record)
        self.emit(QtCore.SIGNAL('dataLoadDone(int)'), len(self.items))


    def updateData(self):
        self.emit(QtCore.SIGNAL('beforeReset()'))
        self.loadData()
        self.reset()
        self.emit(QtCore.SIGNAL('afterReset()'))


    def queueClient(self, row, eventId, actionId, clientId):
        actionInfo = CQueueModel.CActionInfo(actionId, eventId, clientId, getClientMiniInfo(clientId), 1, QtGui.qApp.getDrId(), QtGui.qApp.userSpecialityId)
        if row>=len(self.timeList):
            self.beginInsertRows(QtCore.QModelIndex(), row+1, row+1)
            self.timeList.append(None)
            self.actionInfoList.append(actionInfo)
            self.endInsertRows()
        else:
            self.actionInfoList[row] = actionInfo
            self.emitDataChanged(row)


# ######################################################################

def getQueueSize(personId, date):
    actionType = CActionTypeCache.getByCode('amb')
    atiAmb = actionType.id
    aptiAmbTimes = actionType.getPropertyType('times').id
    aptiAmbQueue = actionType.getPropertyType('queue').id
    db = QtGui.qApp.db

    stmt = u'SELECT count(APTimesValue.value), count(APQueueValue.value)'\
           u' FROM Action'\
           u' LEFT JOIN Event ON Event.id = Action.event_id'\
           u' LEFT JOIN Person ON Person.id = Event.setPerson_id'\
           u' LEFT JOIN ActionProperty        AS APTimes       ON APTimes.action_id = Action.id AND APTimes.type_id = %(aptiAmbTimes)d'\
           u' LEFT JOIN ActionProperty_Time   AS APTimesValue  ON APTimesValue.id = APTimes.id'\
           u' LEFT JOIN ActionProperty        AS APQueue       ON APQueue.action_id = Action.id AND APQueue.type_id = %(aptiAmbQueue)d'\
           u' LEFT JOIN ActionProperty_Action AS APQueueValue  ON APQueueValue.id = APQueue.id AND APTimesValue.`index` = APQueueValue.`index`'\
           u' WHERE Action.deleted=0 AND Event.deleted=0 AND Event.eventType_id=%(eventTypeId)d'\
           u' AND Action.actionType_id = %(atiAmb)d'\
           u' AND Event.setDate=%(date)s'\
           u' AND Event.setPerson_id = %(personId)d'\
           u' AND (Person.lastAccessibleTimelineDate IS NULL OR Person.lastAccessibleTimelineDate = \'0000-00-00\' OR DATE(Event.setDate)<=Person.lastAccessibleTimelineDate)' \
           u' AND APTimesValue.value IS NOT NULL' % {
                'eventTypeId'  : getEventType(etcTimeTable).eventTypeId,
                'aptiAmbTimes' : aptiAmbTimes,
                'aptiAmbQueue' : aptiAmbQueue,
                'atiAmb'       : atiAmb,
                'date'         : db.formatDate(date),
                'personId'     : personId
            }
    query = QtGui.qApp.db.query(stmt)
    query.next()
    record = query.record()
    return forceInt(record.value(0)), forceInt(record.value(1))


def locFormatTime(time):
    return time.toString('H:mm') if time else '--:--'
