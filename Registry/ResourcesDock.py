# -*- coding: utf-8 -*-
import math
import sip
from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import QVariant

from Events.Action import CAction
from Events.CreateEvent import requestNewEvent
from Events.Utils import getDeathDate, getEventType
from Orgs.OrgPersonnel import CFlatOrgPersonnelModel, COrgPersonnelModel
from Orgs.OrgStructComboBoxes import COrgStructureModel
from Orgs.PersonInfo import CPersonInfo
from Orgs.Utils import findOrgStructuresByAddress, getOrgStructurePersonIdList, getPersonInfo
from Registry.BeforeRecordClient import CQueue, printOrder
from Registry.ComplaintsEditDialog import CComplaintsEditDialog
from Registry.Utils import CCheckNetMixin, CClientInfo, assignTodayQueueNumberToClient, formatAttachesAsText, getAllClientAttaches, \
    getAvailableQueueShare, getClientAddressEx, getClientInfoEx, getClientMiniInfo, getClientQueueNumber, getLocationCard
from Registry.VisitBeforeRecordClient import CVisitByQueue
from Reports.ReportBase import CReportBase, createTable
from Reports.ReportView import CReportViewDialog
from Timeline.TimeTable import formatTimeRange
from Ui_ResourcesDockContent import Ui_Form
from Users.Rights import urAccessViewFullOrgStructure, urAdmin, urEQAccess, urQueueCancelMaxDateLimit, \
    urQueueCancelMinDateLimit, urQueueDeletedTime, urQueueOverTime, urQueueToSelfDeletedTime, urQueueToSelfOverTime, \
    urQueueWithEmptyContacts, urQueueingOutreaching, urRegTabWriteEvents, urSignedUpClientMoreOneTime
from Users.UserInfo import CUserInfo
from library import constants
from library.DbComboBox import CDbDataCache
from library.DialogBase import CConstructHelperMixin
from library.DockWidget import CDockWidget
from library.PreferencesMixin import CContainerPreferencesMixin, CPreferencesMixin
from library.PrintInfo import CDateInfo, CInfo, CInfoContext, CTimeInfo
from library.PrintTemplates import applyTemplate, getPrintAction
from library.RecordLock import CRecordLockMixin
from library.TreeModel import CTreeItemWithId, CTreeModel
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, formatTime, getPref, getVal, setPref, toVariant
from library.crbcombobox import CRBComboBox, CRBModelDataCache


class CResourcesDockWidget(CDockWidget):
    def __init__(self, parent):
        CDockWidget.__init__(self, parent)
        self.setWindowTitle(u'График')
        self.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.content = None
        self.contentPreferences = {}
        self.connect(QtGui.qApp, QtCore.SIGNAL('dbConnectionChanged(bool)'), self.onConnectionChanged)

    def loadPreferences(self, preferences):
        self.contentPreferences = getPref(preferences, 'content', {})
        CDockWidget.loadPreferences(self, preferences)
        if isinstance(self.content, CPreferencesMixin):
            self.content.loadPreferences(self.contentPreferences)

    def resizeEvent(self, *args, **kwargs):
        preferences = self.savePreferences()
        setPref(QtGui.qApp.preferences.windowPrefs, self.objectName(), preferences)

    def savePreferences(self):
        result = CDockWidget.savePreferences(self)
        self.updateContentPreferences()
        setPref(result, 'content', self.contentPreferences)
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
        self.content = CResourcesDockContent(self)
        self.content.loadPreferences(self.contentPreferences)
        self.setWidget(self.content)

    def onDBDisconnected(self):
        self.setWidget(None)
        if self.content:
            self.updateContentPreferences()
            self.content.setParent(None)
            sip.delete(self.content)
        self.content = QtGui.QLabel(u'необходимо\nподключение\nк базе данных', self)
        self.content.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.content.setDisabled(True)
        self.setWidget(self.content)


class CResourcesDockContent(QtGui.QWidget, Ui_Form, CConstructHelperMixin, CContainerPreferencesMixin, CCheckNetMixin, CRecordLockMixin):
    __pyqtSignals__ = ('alertNextEQPatient(int)',
                       'alertNoneEQPatient()',
                       'updatedTimeTable()',
                       'createdOrder()')

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        CCheckNetMixin.__init__(self)
        CRecordLockMixin.__init__(self)
        font = QtGui.QFont()
        font.setBold(True)

        self.groupingSpeciality = forceBool(QtGui.qApp.preferences.appPrefs.get('groupingSpeciality', True))
        self.activityListIsShown = forceBool(QtGui.qApp.preferences.appPrefs.get('activityListIsShown', False))

        self.addModels('OrgStructure', COrgStructureModel(self, QtGui.qApp.currentOrgId()))
        self.addModels('Activity', CActivityModel(self))
        self.addModels('AmbTimeTable', CTimeTableModel(self, constants.atcAmbulance))
        self.addModels('AmbQueue', CQueueModel(self, constants.atcAmbulance))
        self.addModels('HomeTimeTable', CTimeTableModel(self, constants.atcHome))
        self.addModels('HomeQueue', CQueueModel(self, constants.atcHome))

        self.actFindArea = QtGui.QAction(u'Найти участок', self)
        self.actFindArea.setObjectName('actFindArea')
        self.actAmbCreateOrder = QtGui.QAction(u'Поставить в очередь', self)
        self.actAmbCreateOrder.setObjectName('actAmbCreateOrder')
        self.actAmbDeleteOrder = QtGui.QAction(u'Удалить из очереди', self)
        self.actAmbDeleteOrder.setFont(font)
        self.actAmbDeleteOrder.setObjectName('actAmbDeleteOrder')
        self.actAmbChangeNotes = QtGui.QAction(u'Изменить жалобы/примечания', self)
        self.actAmbChangeNotes.setObjectName('actAmbChangeNotes')
        self.actAmbPrintOrder = QtGui.QAction(u'Напечатать направление', self)
        self.actAmbPrintOrder.setObjectName('actAmbPrintOrder')
        self.actAmbPrintQueue = QtGui.QAction(u'Напечатать полный список', self)
        self.actAmbPrintQueue.setObjectName('actAmbPrintQueue')
        self.actAmbPrintQueuePass = QtGui.QAction(u'Напечатать список подтвержденных записей', self)
        self.actAmbPrintQueuePass.setObjectName('actAmbPrintQueuePass')
        self.actAmbPrintQueueNoPass = QtGui.QAction(u'Напечатать список неподтвержденных записей', self)
        self.actAmbPrintQueueNoPass.setObjectName('actAmbPrintQueueNoPass')
        self.actAmbPrintQueueByTemplate = getPrintAction(self, 'ambQueue', u'Напечатать список по шаблону', False)
        self.actAmbPrintQueueByTemplate.setObjectName('actAmbPrintQueueByTemplate')
        self.actAmbFindClient = QtGui.QAction(u'Перейти в картотеку', self)
        self.actAmbFindClient.setObjectName('actAmbFindClient')
        self.actAmbCreateEvent = QtGui.QAction(u'Новое обращение', self)
        self.actAmbCreateEvent.setObjectName('actAmbCreateEvent')
        self.actAmbInfo = QtGui.QAction(u'Свойства записи', self)
        self.actAmbInfo.setObjectName('actAmbInfo')

        self.actHomeCreateOrder = QtGui.QAction(u'Поставить в очередь', self)
        self.actHomeCreateOrder.setObjectName('actHomeCreateOrder')
        self.actHomeDeleteOrder = QtGui.QAction(u'Удалить из очереди', self)
        self.actHomeDeleteOrder.setFont(font)
        self.actHomeDeleteOrder.setObjectName('actHomeDeleteOrder')
        self.actHomeChangeNotes = QtGui.QAction(u'Изменить жалобы/примечания', self)
        self.actHomeChangeNotes.setObjectName('actHomeChangeNotes')
        self.actHomePrintOrder = QtGui.QAction(u'Напечатать направление', self)
        self.actHomePrintOrder.setObjectName('actHomePrintOrder')
        self.actHomePrintQueue = QtGui.QAction(u'Напечатать полный список', self)
        self.actHomePrintQueue.setObjectName('actHomePrintQueue')
        self.actHomePrintQueuePass = QtGui.QAction(u'Напечатать список переданных врачу', self)
        self.actHomePrintQueuePass.setObjectName('actHomePrintQueuePass')
        self.actHomePrintQueueNoPass = QtGui.QAction(u'Напечатать список непереданных врачу', self)
        self.actHomePrintQueueNoPass.setObjectName('actHomePrintQueueNoPass')
        self.actHomePrintQueueByTemplate = getPrintAction(self, 'homeQueue', u'Напечатать список по шаблону', False)
        self.actHomePrintQueueByTemplate.setObjectName('actHomePrintQueueByTemplate')
        self.actHomeFindClient = QtGui.QAction(u'Перейти в картотеку', self)
        self.actHomeFindClient.setObjectName('actHomeFindClient')
        self.actHomeCreateEvent = QtGui.QAction(u'Новое обращение', self)
        self.actHomeCreateEvent.setObjectName('actHomeCreateEvent')
        self.actHomeInfo = QtGui.QAction(u'Свойства записи', self)
        self.actHomeInfo.setObjectName('actHomeInfo')

        self.actServiceReport = QtGui.QAction(u'Сводка об обслуживании', self)
        self.actServiceReport.setObjectName('actServiceReport')
        self.actEQProcessPatient = QtGui.QAction(u'Пригласить пациента', self)
        self.actEQProcessPatient.setObjectName('actEQProcessPatient')
        self.actEQFinishPatient = QtGui.QAction(u'Завершить прием пациента', self)
        self.actEQFinishPatient.setObjectName('actEQFinishPatient')

        self.timer = QtCore.QTimer(self)
        self.timer.setObjectName('timer')
        self.timer.setInterval(60*1000) # раз в минуту

        self.setupUi(self)
        for treeWidget in [self.treeOrgStructure, self.treeOrgPersonnel]:
            treeWidget.setIndentation(12)
            treeWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        for tableWidget in [self.tblAmbTimeTable, self.tblAmbQueue, self.tblHomeTimeTable, self.tblHomeQueue]:
            verticalHeader = tableWidget.verticalHeader()
            verticalHeader.show()
            verticalHeader.setResizeMode(QtGui.QHeaderView.Fixed)
        self.setModels(self.treeOrgStructure, self.modelOrgStructure, self.selectionModelOrgStructure)
        self.setModels(self.tblAmbTimeTable, self.modelAmbTimeTable, self.selectionModelAmbTimeTable)
        self.setModels(self.tblAmbQueue, self.modelAmbQueue, self.selectionModelAmbQueue)
        self.setModels(self.tblHomeTimeTable, self.modelHomeTimeTable, self.selectionModelHomeTimeTable)
        self.setModels(self.tblHomeQueue, self.modelHomeQueue, self.selectionModelHomeQueue)

        self.onTreePersonnelSectionClicked(0, False)

        self.tblHomeTimeTable.setColumnHidden(1,True) # кабинет в вызовах на дом

        self.treeOrgStructure.createPopupMenu([self.actFindArea])
        self.tblAmbQueue.createPopupMenu([self.actAmbCreateOrder,
                                          self.actAmbDeleteOrder,
                                          '-',
                                          self.actAmbChangeNotes,
                                          '-',
                                          self.actAmbPrintOrder,
                                          '-',
                                          self.actAmbPrintQueue,
                                          self.actAmbPrintQueuePass,
                                          self.actAmbPrintQueueNoPass,
                                          self.actAmbPrintQueueByTemplate,
                                          '-',
                                          self.actAmbFindClient,
                                          self.actAmbCreateEvent,
                                          '-',
                                          self.actServiceReport,
                                          self.actAmbInfo,
                                          '-',
                                          self.actEQProcessPatient,
                                          self.actEQFinishPatient
                                          ])
        self.tblHomeQueue.createPopupMenu([self.actHomeCreateOrder,
                                           self.actHomeDeleteOrder,
                                           '-',
                                           self.actHomeChangeNotes,
                                           '-',
                                           self.actHomePrintOrder,
                                           '-',
                                           self.actHomePrintQueue,
                                           self.actHomePrintQueuePass,
                                           self.actHomePrintQueueNoPass,
                                           self.actHomePrintQueueByTemplate,
                                           '-',
                                           self.actHomeFindClient,
                                           self.actHomeCreateEvent,
                                           '-',
                                           self.actServiceReport,
                                           self.actHomeInfo])

        self.onTreeOSSectionClicked(0, False)

        self.onCurrentUserIdChanged()

        self.calendarWidget.setList(QtGui.qApp.calendarInfo)
        self.connect(self.treeOrgStructure.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuTreeOrgStructureAboutToShow)
        self.connect(self.tblAmbQueue.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAmbAboutToShow)
        self.connect(self.tblHomeQueue.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuHomeAboutToShow)
        self.connect(QtGui.qApp, QtCore.SIGNAL('createdOrder()'), self.updateTimeTable)

        self.headerTreeOS = self.treeOrgStructure.header()
        self.headerTreeOS.setClickable(True)
        QtCore.QObject.connect(self.headerTreeOS, QtCore.SIGNAL('sectionClicked(int)'), self.onTreeOSSectionClicked)

        self.headerTreePersonnel = self.treeOrgPersonnel.header()
        self.headerTreePersonnel.setClickable(True)
        QtCore.QObject.connect(self.headerTreePersonnel, QtCore.SIGNAL('sectionClicked(int)'),
                               self.onTreePersonnelSectionClicked)

        self.connect(QtGui.qApp, QtCore.SIGNAL('currentOrgIdChanged()'), self.onCurrentOrgIdChanged)
        self.connect(QtGui.qApp, QtCore.SIGNAL('currentOrgStructureIdChanged()'), self.onCurrentOrgStructureIdChanged)
        self.connect(QtGui.qApp, QtCore.SIGNAL('currentUserIdChanged()'), self.onCurrentUserIdChanged)

        self.prevClientId = None
        self.prevComplaints = ''

        self.timer.start()
        self.updateTimeTable()

        self.eqPanelWidget.setVisible(False)

        self.connect(QtGui.qApp, QtCore.SIGNAL('currentUserIdChanged()'), self.userIdChanged)

    def isEQControl(self):
        return bool(QtGui.qApp.userHasRight(urEQAccess) and self.eqPanelWidget.isControl())

    @QtCore.pyqtSlot()
    def userIdChanged(self):
        self.eqPanelWidget.setVisible(QtGui.qApp.userHasRight(urEQAccess))

        if not QtGui.qApp.userHasRight(urEQAccess):
            return

        self.eqPanelWidget.configureEQPanel(QtGui.qApp.userId,
                                            QtGui.qApp.db.getTheseAndParents('OrgStructure',
                                                                             'parent_id',
                                                                             [QtGui.qApp.userOrgStructureId]) if QtGui.qApp.userId else [None])
        self.modelAmbQueue.setEQControl(self.isEQControl())

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
            self.updatePersonnelByActivity()
        else:
            self.updatePersonnelByOrgStructure()

    def onTreeOSSectionClicked(self, col, reverse=True):
        if reverse:
            self.activityListIsShown = not self.activityListIsShown

        if not self.activityListIsShown:
            self.treeOrgStructure.setModel(None)
            self.setModels(self.treeOrgStructure, self.modelOrgStructure, self.selectionModelOrgStructure)
            orgStructureIndex = self.modelOrgStructure.findItemId(QtGui.qApp.currentOrgStructureId())
            if orgStructureIndex and orgStructureIndex.isValid():
                self.treeOrgStructure.setCurrentIndex(orgStructureIndex)
                self.treeOrgStructure.setExpanded(orgStructureIndex, True)
            self.updatePersonnelByOrgStructure()
        else:
            self.treeOrgStructure.setModel(None)
            self.setModels(self.treeOrgStructure, self.modelActivity, self.selectionModelActivity)
            self.updatePersonnelByActivity()

        QtGui.qApp.preferences.appPrefs['activityListIsShown'] = self.activityListIsShown

    def sizeHint(self):
        return QtCore.QSize(10, 10)

    def onCurrentOrgIdChanged(self):
        self.modelOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.updatePersonnelByOrgStructure()
        self.updateTimeTable()

    def onCurrentOrgStructureIdChanged(self):
        if QtGui.qApp.currentOrgStructureId() and not QtGui.qApp.userHasRight(urAccessViewFullOrgStructure):
            self.modelOrgStructure.setOrgId(QtGui.qApp.currentOrgId(), QtGui.qApp.currentOrgStructureId())
            self.modelActivity.setOrgId(QtGui.qApp.currentOrgId(), QtGui.qApp.currentOrgStructureId())
        elif QtGui.qApp.currentOrgId():
            self.modelOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
            self.modelActivity.setOrgId(QtGui.qApp.currentOrgId())
        self.updatePersonnelByOrgStructure()
        self.updateTimeTable()

    def onCurrentUserIdChanged(self):
        if QtGui.qApp.db.db.isOpen():
            if QtGui.qApp.currentOrgStructureId() and not QtGui.qApp.userHasRight(urAccessViewFullOrgStructure):
                self.modelOrgStructure.setOrgId(QtGui.qApp.currentOrgId(), QtGui.qApp.currentOrgStructureId())
                self.modelActivity.setOrgId(QtGui.qApp.currentOrgId(), QtGui.qApp.currentOrgStructureId())
            elif QtGui.qApp.currentOrgId():
                self.modelOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
                self.modelActivity.setOrgId(QtGui.qApp.currentOrgId())
            self.updatePersonnelByOrgStructure()
            self.updateTimeTable()

        if QtGui.qApp.userOrgStructureId:
            index = self.modelOrgStructure.findItemId(QtGui.qApp.userOrgStructureId)
            if index and index.isValid():
                self.treeOrgStructure.setCurrentIndex(index)
        if QtGui.qApp.drOrUserSpecialityId:
            index = self.treeOrgPersonnel.model().findPersonId(QtGui.qApp.getDrId())
            if index and index.isValid():
                self.treeOrgPersonnel.setCurrentIndex(index)
        self.setCalendarDataRange()

    def setCalendarDataRange(self):
        # Врач - тот, к кому записывают. Пользователь - тот, кто записывает.
        today = QtCore.QDate.currentDate()
        if QtGui.qApp.userHasRight(urQueueCancelMinDateLimit):
            minDate = today.addYears(-10)
        else:
            minDate = today.addDays(-7)
        if QtGui.qApp.userHasRight(urQueueCancelMaxDateLimit):
            # Если есть право, снимаем любые ограничения
            maxDate = today.addYears(10)
        else:
            # Если нет дополнительных ограничений, ограничение по умолчанию - 2 месяца.
            maxDate = None
            defaultMaxDate = today.addMonths(2)
            personId = self.getCurrentPersonId()
            userId = QtGui.qApp.userId
            db = QtGui.qApp.db
            canSeeDays = forceInt(db.translate('Person', 'id', userId, 'canSeeDays'))
            userMaxDate = today.addDays(canSeeDays) if canSeeDays else None
            # Может ли случиться, что нет userId??
            if personId and userId and QtGui.qApp.isTimelineAccessibilityDays() == 1:
                table = db.table('Person')
                record = db.getRecordEx(table, [table['lastAccessibleTimelineDate'], table['timelineAccessibleDays']], table['id'].eq(personId))
                if record:
                    lastAccessibleTimelineDate = forceDate(record.value('lastAccessibleTimelineDate'))
                    timelineAccessibleDays = forceInt(record.value('timelineAccessibleDays'))
                    personMaxDate = today.addDays(timelineAccessibleDays) if timelineAccessibleDays else None
                    if userMaxDate:
                        # Если указано ограничение количества дней для пользователя, _количество_ дней для врача игнорируется.
                        # "Расписание видимо до" при этом действует, выбирается наиболее жесткое из условий.
                        maxDate = min(userMaxDate, lastAccessibleTimelineDate) if lastAccessibleTimelineDate else userMaxDate
                    else:
                        # Выбирается наиболее жесткое из ограничений по врачу
                        if lastAccessibleTimelineDate and personMaxDate:
                            maxDate = min(lastAccessibleTimelineDate, personMaxDate)
                        else:
                            maxDate = lastAccessibleTimelineDate or personMaxDate
            if not maxDate:
                maxDate = userMaxDate if userMaxDate else defaultMaxDate
        self.calendarWidget.setDateRange(minDate, maxDate)

    def getCurrentPersonId(self):
        treeIndex = self.treeOrgPersonnel.currentIndex()
        personIdList = self.treeOrgPersonnel.model().getItemIdList(treeIndex)
        if personIdList and len(personIdList) == 1:
            return personIdList[0]
        else:
            return None

    def checkNetApplicable(self, clientId, date):
        personId = self.getCurrentPersonId()
        return (self.checkClientAttach(personId, clientId, date, True) and
                (self.checkClientAttendace(personId, clientId) or
                 self.confirmClientAttendace(self, personId, clientId)) and
                self.confirmClientPolicyConstraint(self, clientId, date))

    def updatePersonnelByOrgStructure(self):
        treeIndex = self.treeOrgStructure.currentIndex()
        orgStructureIdList = self.modelOrgStructure.getItemIdList(treeIndex)
        date = self.calendarWidget.selectedDate()
        self.modelPersonnel.setOrgStructureIdList(self.modelOrgStructure.orgId, orgStructureIdList, date)
        if self.modelOrgStructure.isLeaf(treeIndex):
            self.treeOrgPersonnel.expandAll()
            self.treeOrgPersonnel.setCurrentIndex(self.treeOrgPersonnel.model().getFirstLeafIndex())
        self.updateTimeTable()

        if self.modelOrgStructure.dropOtherBranch():
            self.treeOrgStructure.reset()
            self.treeOrgStructure.expand(self.treeOrgStructure.model().index(0, 0, QtCore.QModelIndex()))

    def updatePersonnelByActivity(self):
        treeIndex = self.treeOrgStructure.currentIndex()
        activityIdList = self.treeOrgPersonnel.model().getItemIdList(treeIndex)
        date = self.calendarWidget.selectedDate()
        self.treeOrgPersonnel.model().setActivityIdList(self.modelOrgStructure.orgId, activityIdList, date)
        # перестао быть актуальным после изменения иницализации модели modelActivity
        # if self.modelActivity.isLeaf(treeIndex):
        #     self.treeOrgPersonnel.expandAll()
        #     self.treeOrgPersonnel.setCurrentIndex(self.treeOrgPersonnel.model().getFirstLeafIndex())
        self.updateTimeTable()

    def updateTimeTable(self):
        self.timer.stop()
        try:
            self.setCalendarDataRange()
            personId = self.getCurrentPersonId()
            enableQueueing = bool(personId)
            date = self.calendarWidget.selectedDate()
            place = self.tabPlace.currentIndex()
            if place == 0:
                self.modelAmbTimeTable.setPersonAndDate(personId, date)
                row = self.modelAmbTimeTable.begDate.daysTo(date)
                self.modelAmbQueue.setPersonAndDate(
                    personId,
                    date,
                    self.modelAmbTimeTable.getTimeTableEventId(row),
                    self.tblAmbTimeTable.model().dayInfoList[row]
                )
                self.modelAmbQueue.setHiddenRows()
                self.hideQueueRows()
                self.tblAmbTimeTable.setCurrentIndex(self.modelAmbTimeTable.index(row, 0))
                self.tblAmbTimeTable.setEnabled(enableQueueing)
            elif place == 1:
                self.modelHomeTimeTable.setPersonAndDate(personId, date)
                row = self.modelHomeTimeTable.begDate.daysTo(date)
                self.modelHomeQueue.setPersonAndDate(personId, date, self.modelHomeTimeTable.getTimeTableEventId(row))
                self.tblHomeTimeTable.setCurrentIndex(self.modelHomeTimeTable.index(row, 0))
                self.tblHomeTimeTable.setEnabled(enableQueueing)
                self.tblHomeQueue.setEnabled(enableQueueing)
            self.emit(QtCore.SIGNAL('updatedTimeTable()'))
        finally:
            self.timer.start()

    def createVisitBeforeRecordClient(self, clientId=None):
        specialityId = None
        orgStructureId = None
        personId = self.getCurrentPersonId()
        if personId:
            specialityId = forceRef(QtGui.qApp.db.translate('Person', 'id', personId, 'speciality_id'))
            if specialityId:
                indexTree = self.treeOrgStructure.currentIndex()
                orgStructureId = self.modelOrgStructure.itemId(indexTree)
            else:
                personId = None
        if clientId:
            CVisitByQueue(self, clientId, orgStructureId, specialityId, personId).exec_()

    def showQueueItem(self, orgStructureId, specialityId, personId, date, actionId):
        self.setPersonAttributes(orgStructureId, specialityId, personId)
        if date >= QtCore.QDate.currentDate():
            self.calendarWidget.setSelectedDate(date)
        if actionId:
            self.selectQueueAction(actionId)

    def setPersonAttributes(self, orgStructureId, specialityId, personId):
        if orgStructureId:
            index = self.modelOrgStructure.findItemId(orgStructureId)
            if index and index.isValid():
                self.treeOrgStructure.setCurrentIndex(index)
        if specialityId and personId:
            index = self.treeOrgPersonnel.model().findPersonId(personId)
            if index and index.isValid():
                self.treeOrgPersonnel.setCurrentIndex(index)

    def selectQueueAction(self, actionId):
        db = QtGui.qApp.db
        tableActionProperty_Action = db.table('ActionProperty_Action')
        tableActionProperty = db.table('ActionProperty')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        table = tableActionProperty_Action.leftJoin(tableActionProperty, tableActionProperty['id'].eq(tableActionProperty_Action['id']))
        table = table.leftJoin(tableAction,     tableAction['id'].eq(tableActionProperty['action_id']))
        table = table.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        cond = tableActionProperty_Action['value'].eq(actionId)
        record = db.getRecordEx(table, [tableActionType['code']], cond)
        code = forceString(record.value(0)) if record else ''
        if code == constants.atcAmbulance:
            self.tabPlace.setCurrentIndex(0)
        elif code == constants.atcHome:
            self.tabPlace.setCurrentIndex(1)
        self.updateTimeTable()
        place = self.tabPlace.currentIndex()
        if place == 0:
            self.tblAmbQueue.selectRow(self.modelAmbQueue.findActionIdRow(actionId))
        elif place == 1:
            self.tblHomeQueue.selectRow(self.modelHomeQueue.findActionIdRow(actionId))

    @staticmethod
    def getActionIdListForClient(date, specialityId, clientId):
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
        tableQuery = tableQuery.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        tableQuery = tableQuery.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        tableQuery = tableQuery.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        tableQuery = tableQuery.innerJoin(tableActionProperty_Action, tableActionProperty_Action['value'].eq(tableAction['id']))
        tableQuery = tableQuery.innerJoin(tablePerson, tablePerson['id'].eq(tableAction['person_id']))
        tableQuery = tableQuery.innerJoin(tableRBSpeciality, tableRBSpeciality['id'].eq(tablePerson['speciality_id']))
        cols = [tableAction['id']]
        currentDate = QtCore.QDate.currentDate()
        cond = [tableAction['deleted'].eq(0),
                tableAction['status'].ne(0),
                # tableAction['event_id'].eq(0),
                tableEvent['deleted'].eq(0),
                tableEventType['deleted'].eq(0),
                tablePerson['deleted'].eq(0),
                tableEvent['client_id'].eq(clientId),
                tableEvent['setDate'].dateGe(currentDate),
                tableEventType['code'].eq(etcQueue),
                tableActionType['code'].eq(atcQueue),
                u"""
                NOT EXISTS (
                    SELECT 
                        * 
                    FROM 
                        Event e 
                        INNER JOIN Visit v ON v.event_id = e.id
                        INNER JOIN vrbPersonWithSpeciality vrb ON vrb.`id` = v.`person_id`
                    WHERE 
                        DATE(e.`setDate`) = DATE({eventSetDate})  # Event.`setDate`
                        AND e.id != {eventId}  # Event.`id`
                        AND e.client_id = {clientId}  # Event.`client_id`
                        AND vrb.speciality_id = {specialityId}
                        AND e.deleted = 0
                        AND v.deleted = 0
                )
                """.format(
                    eventSetDate=tableEvent['setDate'],
                    eventId=tableEvent['id'],
                    clientId=clientId,
                    specialityId=specialityId
                )
                #tablePerson['speciality_id'].eq(specialityId)
                ]
        OKSOCode = forceString(db.translate('rbSpeciality', 'id', specialityId, 'OKSOCode'))
        OKSOCodeList = [u'040122', u'040819', u'040110']
        if OKSOCode in OKSOCodeList:
            cond.append(tableRBSpeciality['OKSOCode'].inlist(OKSOCodeList))
        else:
            cond.append(tablePerson['speciality_id'].eq(specialityId))
        return db.getIdList(tableQuery, cols, cond, 'Action.directionDate')

    def queueingEnabled(self, date, orgStructureId, specialityId, personId, queueWidget, row, clientId):
        queueModel = queueWidget.model()
        if queueModel.getClientId(row):
            return False # кто-то уже записан
        reasonOfAbsenceId = CAction.getAction(queueModel.timeTableEventId, constants.atcTimeLine)['reasonOfAbsence']
        if reasonOfAbsenceId:
            reasonOfAbsence = forceString(QtGui.qApp.db.translate('rbReasonOfAbsence', 'id', reasonOfAbsenceId, 'name'))
            QtGui.QMessageBox.warning(self, u'Внимание!', u'Пациент не может быть записан к врачу,\nпотому что врач отсутствует в указанный день по причине:\n"%s"' % reasonOfAbsence)
            return False
        deathDate = getDeathDate(clientId)
        if deathDate:
                QtGui.QMessageBox.warning(self, u'Внимание!', u'Этот пациент не может быть записан к врачу, потому что есть отметка что он уже умер %s' % forceString(deathDate))
                return False
        actionIdList = self.getActionIdListForClient(date, specialityId, clientId)
        if actionIdList:
            messageBox = QtGui.QMessageBox(QtGui.QMessageBox.Warning, u'Внимание!', u'Этот пациент уже записан к врачу этой специальности\nПодтвердите повторную запись')
            dec = 1
            if QtGui.qApp.userHasRight(urSignedUpClientMoreOneTime):
                messageBox.addButton(u'Ок', QtGui.QMessageBox.YesRole)  # 0
                dec = 0

            messageBox.addButton(u'Отмена', QtGui.QMessageBox.NoRole)  # 1
            messageBox.setDefaultButton(messageBox.addButton(u'Просмотр', QtGui.QMessageBox.ActionRole))  # 2
            confirmation = messageBox.exec_()
            if confirmation == 1 - dec:
                return False
            if confirmation == 2 - dec:
                place = self.tabPlace.currentIndex()
                result = CQueue(
                    self,
                    clientId,
                    actionIdList,
                    visibleOkButton=QtGui.qApp.userHasRight(urSignedUpClientMoreOneTime)
                ).exec_()
                if not result:
                    return False
                self.tabPlace.setCurrentIndex(place)
                self.showQueueItem(orgStructureId, specialityId, personId, date, None)
                queueWidget.selectRow(row)
        if not QtGui.qApp.userHasRight(urQueueWithEmptyContacts):
            db = QtGui.qApp.db
            stmt = u"Select id From ClientContact where client_id = %s and deleted = 0 Limit 0, 1" %forceString(clientId)
            query = db.query(stmt)
            query.first()
            if not forceInt(query.record().value('id')):
                QtGui.QMessageBox.warning(self, u'Внимание!', u'Невозможно создать обращение. У данного пациента не указаны контакты')
                return False

        quota, quotaName = getQuota(personId, queueModel.plan)
        queued = queueModel.getQueuedCount()
        queueTime = queueModel.getTime(row)
        # Если записываем сверх очереди, ограничение по квотам не применяется.
        if quota <= queued and (queueTime.isValid() or not
                (personId == QtGui.qApp.userId and QtGui.qApp.userHasRight(urQueueToSelfOverTime))):
            message = u'Квота на запись исчерпана! (%s)' % quotaName
            if QtGui.qApp.userHasRight(urQueueingOutreaching):
                message += u'\nВсё равно продолжить?'
                buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
            else:
                buttons = QtGui.QMessageBox.Ok
            return QtGui.QMessageBox.critical(self,
                                              u'Внимание!',
                                              message,
                                              buttons) == QtGui.QMessageBox.Yes
        return True

    def hideQueueRows(self):
        invisible = self.tblAmbQueue.model().getHiddenRows()[1]
        for row in range(self.tblAmbQueue.model().rowCount()):
            if row in invisible:
                self.tblAmbQueue.setRowHidden(row, True)
            else:
                self.tblAmbQueue.setRowHidden(row, False)
        self.tblAmbQueue.resizeRowsToContents() #atronah: для того, чтобы восстановить ненулевую высоту скрытык в другом расписании строк

    def checkValueMessage(self, message, skipable=False):
        buttons = QtGui.QMessageBox.Ok
        if skipable:
            buttons = buttons | QtGui.QMessageBox.Ignore
        res = QtGui.QMessageBox.warning(
            self,
            u'Внимание!',
            message,
            buttons,
            QtGui.QMessageBox.Ok
        )
        if res == QtGui.QMessageBox.Ok:
            return False
        return True

    def createOrder(self, timeTableWidget, queueWidget, clientId):
        date = self.calendarWidget.selectedDate()
        if self.checkNetApplicable(clientId, date):
            db = QtGui.qApp.db
            personId = self.getCurrentPersonId()
            specialityId = self.getPersonSpecialityId(personId)
            orgStructureId = self.getPersonOrgStructureId(personId)
            model = queueWidget.model()
            timeTableRow = timeTableWidget.currentIndex().row()
            office = timeTableWidget.model().getOffice(timeTableRow)
            row = queueWidget.currentIndex().row()
            time = queueWidget.model().getTime(row) if row >= 0 else None
            timeTableEventId = model.timeTableEventId
            timeTableActionId = model.timeTableAction.getId()
            if (personId
                and specialityId
                and orgStructureId
                and clientId
                and timeTableEventId
                and timeTableActionId
                and self.queueingEnabled(date, orgStructureId, specialityId, personId, queueWidget, row, clientId)):
                if model.complaintsRequired():
                    dlg = CComplaintsEditDialog(self)
                    if self.prevClientId == clientId:
                        dlg.setComplaints(self.prevComplaints)
                    dlg.disableCancel()
                    dlg.exec_()
                    complaints = dlg.getComplaints()
                    self.prevClientId = clientId
                    self.prevComplaints = complaints
                else:
                    complaints = ''

                #start changes by atronah 01.06.2012 for issue #350
                if QtGui.qApp.isNeedAddComent():
                    complaints += '---\n' + QtGui.qApp.personCommentText()
                #end changes by atronah

                if self.lock('Action', timeTableActionId):
                    dataChanged = False
                    try:
                        model.updateData()
                        # if checkPersonGapsByTime(personId, time):
                        #     stmt = u"""
                        #     SELECT
                        #         osg.begTime,
                        #         osg.endTime
                        #     FROM
                        #         OrgStructure_Gap osg
                        #     WHERE
                        #         osg.person_id = {personId}
                        #     """.format(personId=personId)
                        #     rec = QtGui.qApp.db.getRecordList(stmt=stmt)
                        #     gaps = u''
                        #     for x in rec:
                        #         gaps += u'c %s до %s\n' % (
                        #             forceTime(x.value('begTime')).toString('hh:mm'),
                        #             forceTime(x.value('endTime')).toString('hh:mm')
                        #         )
                        #
                        #     self.checkValueMessage(
                        #         u'Запись на это время невозможна.'
                        #         u'У данного врача перерыв. График перерывов: \n{gaps}'.format(gaps=gaps),
                        #         False
                        #     )
                        # el
                        if timeTableActionId != model.timeTableAction.getId() or model.getActionId(row):
                            dataChanged = True
                        else:
                            # if QtGui.qApp.isReferralRequiredInPreRecord():
                            #     referralDlg = CReferralEditDialog(QtGui.qApp.currentClientId(), date, self)
                            #     if not referralDlg.exec_():
                            #         return False
                            #     referral_ids = referralDlg.itemIds()
                            # else:
                            referral_ids = {}
                            db.transaction()
                            try:
                                queueEventId, queueActionId = createQueueEvent(personId, date, time, clientId, complaints, office, referral_ids)
                                model.queueClient(row, queueEventId, queueActionId, clientId)
                                queue = model.getActionList()
                                model.timeTableAction['queue'] = queue
                                model.timeTableAction.save()
                                self.updateTimeTableRow(date, timeTableWidget, queue)
                                model.setHiddenRows()
                                self.hideQueueRows()
                                db.commit()
                                self.emit(QtCore.SIGNAL('createdOrder()'))
                                return True
                            except:
                                db.rollback()
                                raise
                    finally:
                        self.releaseLock()
                    if dataChanged:
                        QtGui.QMessageBox.warning(self,
                                                  u'Внимание!',
                                                  u'Запись на это время невозможна, так как оно уже занято',
                                                  QtGui.QMessageBox.Ok,
                                                  QtGui.QMessageBox.Ok)
        return False

    def deleteOrder(self, timeTableWidget, queueWidget):
        model = queueWidget.model()
        personId = self.getCurrentPersonId()
        date = self.calendarWidget.selectedDate()
        row = queueWidget.currentIndex().row()
        if personId and row >= 0:
            actionId = model.getActionId(row)
            if actionId:
                db = QtGui.qApp.db

                confirmation = QtGui.QMessageBox.warning(self,
                                                         u'Внимание!',
                                                         u'Подтвердите удаление записи к врачу',
                                                         QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                                         QtGui.QMessageBox.Cancel)
                if confirmation != QtGui.QMessageBox.Ok:
                    return

                timeTableActionId = model.timeTableAction.getId()
                if self.lock('Action', timeTableActionId):
                    try:
                        model.updateData()
                        if timeTableActionId == model.timeTableAction.getId() and actionId == model.getActionId(row):
                            try:
                                db.transaction()
                                queueWidget.model().dequeueClient(row)
                                queue = model.getActionList()
                                model.timeTableAction['queue'] = queue
                                model.timeTableAction.save()
                                self.updateTimeTableRow(date, timeTableWidget, queue)
                                db.commit()
                            except:
                                db.rollback()
                                QtGui.qApp.logCurrentException()
                                raise
                    finally:
                        self.releaseLock()

    def changeNotes(self, queueWidget):
        model = queueWidget.model()
        model.updateData()
        row = queueWidget.currentIndex().row()
        actionId = model.getActionId(row)
        clientId = model.getClientId(row)
        if actionId:
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            actionRecord = db.getRecord(tableAction, 'id, note, isUrgent', actionId)

            dlg = CComplaintsEditDialog(self)
            dlg.setComplaints(forceString(actionRecord.value('note')))
            dlg.setCito(forceInt(actionRecord.value('isUrgent')))
            if dlg.exec_():
                complaints = dlg.getComplaints()
                isUrgent = dlg.getCito()
                actionRecord.setValue('note', QtCore.QVariant(complaints))
                actionRecord.setValue('isUrgent', QtCore.QVariant(isUrgent))
                db.updateRecord(tableAction, actionRecord)

                if clientId and forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'addNotes', QVariant())):
                    tableClient = db.table('Client')
                    clientRecord = db.getRecord(tableClient, 'id, notes', clientId)
                    # i3091: старые записи не нужны
                    oldNotes = forceString(clientRecord.value('notes'))
                    #clientRecord.setValue('notes', QtCore.QVariant(complaints))#u'{0}\n{1}'.format(oldNotes, complaints) if oldNotes else complaints)
                    clientRecord.setValue('notes', u'{0}<br>{1}'.format(oldNotes, complaints) if oldNotes else complaints)
                    db.updateRecord(tableClient, clientRecord)

                QtGui.qApp.findClient(clientId)

    @staticmethod
    def updateTimeTableRow(date, timeTableWidget, queue):
        timeTableWidget.model().updateAvail(date, queue)

    @staticmethod
    def getCurrentQueuedClientId(queueWidget):
        row = queueWidget.currentIndex().row()
        if row >= 0:
            return queueWidget.model().getClientId(row)
        else:
            return None

    def getCurrentQueuedClientInfo(self, queueWidget):
        row = queueWidget.currentIndex().row()
        if row < 0:
            return None, None, None

        clientId = queueWidget.model().getClientId(row)
        queueTime = queueWidget.model().getTime(row)
        queueDate = self.calendarWidget.selectedDate()
        queueNumber = row + 1
        if QtGui.qApp.isUseUnifiedDailyClientQueueNumber():
            queueNumber = getClientQueueNumber(clientId, queueDate)
            if not queueNumber:
                isAssignClientQueueNumber = QtGui.QMessageBox.question(QtGui.qApp.mainWindow,
                                                                       u'У пациента отсутствует номерок!',
                                                                       u'Назначить номерок на выбранную дату для пациента?',
                                                                       buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                                       defaultButton=QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes
                if isAssignClientQueueNumber:
                    queueNumber = assignTodayQueueNumberToClient(clientId, queueDate)
                    self.modelAmbQueue.queueNumber[row] = queueNumber
            if queueNumber is None:
                queueNumber = u'<небходимо получить сквозной суточный номер пациента>'
        return queueNumber, queueTime, clientId

    @staticmethod
    def getQueuedClientsCount(queueWidget):
        return queueWidget.model().getQueuedClientsCount()

    def printQueue(self, timeTableWidget, queueWidget, variantPrint, nameMenuPrintQueue=u''):
        cacheAttachShortName = dict()

        def getAttachOrgName(id):
            if id not in cacheAttachShortName:
                # attaches = getClientAttaches(id)
                attaches = getAllClientAttaches(id)
                cacheAttachShortName[id] = formatAttachesAsText(attaches)
            return cacheAttachShortName[id]

        receptionInfo = self.getReceptionInfo(timeTableWidget)
        personId = receptionInfo['personId']

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        queueModel = queueWidget.model()
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        if timeTableWidget == self.tblAmbTimeTable:
            cursor.insertText(u'запись на амбулаторный приём' + nameMenuPrintQueue)
            office = u'к. ' + receptionInfo['office']
        else:
            cursor.insertText(u'вызовы на дом' + nameMenuPrintQueue)
            office = ''
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportTitle)
        personInfo = self.getPersonInfo(personId)
        cursor.insertText(personInfo['fullName'])
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(personInfo['specialityName'])
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(forceString(receptionInfo['date']) + ' ' + receptionInfo['timeRange'] + ' ' + office)
        #        complaintsRequired = queueModel.complaintsRequired()
        cols = [('5%', [u'№'], CReportBase.AlignRight),
                ('5%', [u'Время'], CReportBase.AlignRight),
                ('10%', [u'Прикрепление'], CReportBase.AlignRight),
                ('70%', [u'Пациент'], CReportBase.AlignLeft),
                ('20%', [u'Жалобы/Примечания'], CReportBase.AlignLeft),
                ]

        table = createTable(cursor, cols)
        cnt = 0
        for row in xrange(queueModel.realRowCount()):
            if queueModel.getClientId(row):
                queueTime = queueModel.getTime(row)
                clientId = queueModel.getClientId(row)
                if clientId:
                    attachOrgName = getAttachOrgName(clientId)

                    if (((variantPrint == 0 or variantPrint == 1) and queueWidget == self.tblHomeQueue) or
                            ((variantPrint == 0 or variantPrint == 1) and (queueWidget == self.tblAmbQueue and
                                                                               QtGui.qApp.ambulanceUserCheckable()))):
                        status = queueModel.getStatus(row)
                        if status == variantPrint:
                            clientInfo = getClientInfoEx(clientId, self.calendarWidget.selectedDate())
                            clientText = u'%(fullName)s, %(birthDate)s (%(age)s), %(sex)s, СНИЛС: %(SNILS)s\n' \
                                         u'документ %(document)s, полис %(policy)s\n' \
                                         u'адр.рег. %(regAddress)s\n' \
                                         u'адр.прож. %(locAddress)s\n' \
                                         u'%(phones)s' % clientInfo
                            i = table.addRow()
                            cnt += 1
                            table.setText(i, 0, cnt)
                            table.setText(i, 1, locFormatTime(queueTime))
                            table.setText(i, 2, attachOrgName)
                            table.setText(i, 3, clientText)
                            table.setText(i, 4, queueModel.getComplaints(row))
                    else:
                        if variantPrint == 2:
                            clientInfo = getClientInfoEx(clientId, self.calendarWidget.selectedDate())
                            clientText = u'%(fullName)s, %(birthDate)s (%(age)s), %(sex)s, СНИЛС: %(SNILS)s\n' \
                                         u'документ %(document)s, полис %(policy)s\n' \
                                         u'адр.рег. %(regAddress)s\n' \
                                         u'адр.прож. %(locAddress)s\n' \
                                         u'%(phones)s' % clientInfo
                            i = table.addRow()
                            cnt += 1
                            table.setText(i, 0, cnt)
                            table.setText(i, 1, locFormatTime(queueTime))
                            table.setText(i, 2, attachOrgName)
                            table.setText(i, 3, clientText)
                            table.setText(i, 4, queueModel.getComplaints(row))
                            table.setText(i, 4, '\n' + u'A/карта: ' + getLocationCard(clientId)[0] if getLocationCard(clientId) else '')
        reportView = CReportViewDialog(self)
        reportView.setWindowTitle(u'Очередь')
        reportView.setText(doc)
        reportView.exec_()

    def printQueueByTemplate(self, timeTableWidget, queueWidget, templateId):
        receptionInfo = self.getReceptionInfo(timeTableWidget)
        queueModel = queueWidget.model()
        context = CInfoContext()
        queue = []
        for row in xrange(queueModel.realRowCount()):
            queueTime = queueModel.getTime(row)
            clientId = queueModel.getClientId(row)
            if clientId:
                checked = queueModel.getStatus(row) == 0
                complaints = queueModel.getComplaints(row)
                setPersonId = queueModel.getSetPersonId(row)
            else:
                checked = False
                complaints = ''
                setPersonId = None
            queue.append(CQueueItemInfo(context, queueTime, clientId, checked, complaints, setPersonId))

        data = {
            'date'     : CDateInfo(receptionInfo['date']),
            'office'   : receptionInfo['office'],
            'person'   : context.getInstance(CPersonInfo, receptionInfo['personId']),
            'timeRange': receptionInfo['timeRange'],
            'queue'    : queue
        }
        applyTemplate(self, templateId, data)

    def getReceptionInfo(self, timeTableWidget):
        timeTableModel = timeTableWidget.model()
        timeTableRow = timeTableWidget.currentIndex().row()
        timeRange = unicode(formatTimeRange(timeTableModel.getTimeRange(timeTableRow)))
        return {
            'date'     : self.calendarWidget.selectedDate(),
            'office'   : timeTableModel.getOffice(timeTableRow),
            'personId' : timeTableModel.personId,
            'timeRange': timeRange
        }

    @staticmethod
    def getPersonInfo(personId): #atronah: Гениально ><
        return getPersonInfo(personId)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelOrgStructure_currentChanged(self, current, previous):
        if not hasattr(self, 'groupingSpeciality'):
            self.groupingSpeciality = forceBool(QtGui.qApp.preferences.appPrefs.get('groupingSpeciality', True))
        self.updatePersonnelByOrgStructure()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActivity_currentChanged(self, current, previous):
        if not hasattr(self, 'groupingSpeciality'):
            self.groupingSpeciality = forceBool(QtGui.qApp.preferences.appPrefs.get('groupingSpeciality', True))
        self.updatePersonnelByActivity()

#    @QtCore.pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModelPersonnel_currentChanged(self, current, previous):
        self.updateTimeTable()

    @QtCore.pyqtSlot()
    def on_btnRefreshAmb_clicked(self):
        self.updateTimeTable()

    @QtCore.pyqtSlot()
    def on_btnRefreshHome_clicked(self):
        self.updateTimeTable()

    @QtCore.pyqtSlot()
    def on_timer_timeout(self):
        self.timer.stop()
        try:
            self.setCalendarDataRange()
            place = self.tabPlace.currentIndex()
            if place == 0:
                if self.tblAmbTimeTable.isEnabled():
                    self.modelAmbTimeTable.updateData()
                    self.modelAmbQueue.updateData()
            elif place == 1:
                if self.tblHomeTimeTable.isEnabled():
                    self.modelHomeTimeTable.updateData()
                    self.modelHomeQueue.updateData()
        finally:
            self.timer.start()

    @QtCore.pyqtSlot()
    def on_calendarWidget_selectionChanged(self):
        self.updateTimeTable()

    @QtCore.pyqtSlot(int)
    def on_tabPlace_currentChanged(self, index):
        self.updateTimeTable()

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelAmbTimeTable_currentChanged(self, current, previous):
        begDate = self.modelAmbTimeTable.begDate
        row = current.row()
        if begDate and row != previous.row():
            date = begDate.addDays(row)
            self.calendarWidget.setSelectedDate(date)

    @QtCore.pyqtSlot()
    def on_actEQProcessPatient_triggered(self):
        row = self.tblAmbQueue.currentIndex().row()
        clientId = self.modelAmbQueue.getClientId(row)
        if QtGui.qApp.isUseUnifiedDailyClientQueueNumber():
            queueNumber = getClientQueueNumber(clientId, self.calendarWidget.selectedDate())
        else:
            queueNumber = self.tblAmbQueue.model().getClientQueueNumber(row)

        clientQueueNumber = '%04d' % queueNumber
        if self.eqPanelWidget.showOnPanel(clientQueueNumber, False):
            self.modelAmbQueue.setStatusByRow(row, 0)

    @QtCore.pyqtSlot()
    def on_actEQFinishPatient_triggered(self):
        row = self.tblAmbQueue.currentIndex().row()
        if self.eqPanelWidget.showOnPanel('', False):
            self.modelAmbQueue.setStatusByRow(row, 2)

    @QtCore.pyqtSlot()
    def on_btnEQCall_clicked(self):
        pass

    @QtCore.pyqtSlot()
    def on_btnEQFinish_clicked(self):
        pass

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
                QtGui.QMessageBox.warning(self.parent(),
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
            clientSex, clientAge = self.getClientSexAndAge(QtGui.qApp.currentClientId())
            for id in filteredList:
                net = self.getOrgStructureNet(id)
                if net.applicable(clientSex, clientAge):
                    return id
        return None

    def getQueueModel(self):
        u"""
        Возвращает текущую модель очереди (амбулаторную или на дому)
        Проверяет, какая вкладка выбрана "Амбулаторно" или "На дому"
        и в зависимости от этого возвращает ссылку на модель очереди
        :rtype: CQueueModel
        """
        place = self.tabPlace.currentIndex()
        if place == 0:
            model = self.modelAmbQueue
        elif place == 1:
            model = self.modelHomeQueue
        return model

    def addQuotaStateToActionCaption(self, actCreateOrder):
        u"""
        Добавляет в конец названия пункта меню "Поставить в очередь" статистику по квотам
        :param actCreateOrder: пункт меню/действие отвечающий за постановку в очередь
        :type actCreateOrder: QtGui.QAction
        """
        #[1]atronah: обработка дописывания оставшейся квоты в пункт меню "Поставить в очередь"
        mainCaption = u'Поставить в очередь'
        quotingState = u''
        queueModel = self.getQueueModel()
        personId = self.getCurrentPersonId()
        if personId:
            quota, quotaName = getQuota(personId, queueModel.plan)
            queued = queueModel.getQueuedCount()
            remain = quota - queued
            if remain < 0:
                remain = 0
            quotingState = u' (%s квота: осталось %d из %d)' % (quotaName, remain, quota)
        actCreateOrder.setText(mainCaption + quotingState)
        #[/1]

    def popupMenuAboutToShow(self,
                             queueWidget,
                             actCreateOrder,
                             actDeleteOrder,
                             actChangeNotes,
                             actPrintOrder,
                             actPrintQueue,
                             actPrintQueuePass,
                             actPrintQueueNoPass,
                             actPrintQueueByTemplate,
                             actFindClient,
                             actCreateEvent,
                             actServiceReport,
                             actInfo,
                             actProcessEQ=None,
                             actFinishEQ=None):
        db = QtGui.qApp.db
        tableAction = db.table('Action')

        queueModel = self.getQueueModel()
        allMenuEnabled = queueModel.rowCount()
        currentClientId = QtGui.qApp.currentClientId()
        orderPresent = bool(self.getCurrentQueuedClientId(queueWidget))
        anyOrderPresent = bool(self.getQueuedClientsCount(queueWidget))
        variantPrintQueue = QtGui.qApp.ambulanceUserCheckable()
        canFindClient = QtGui.qApp.canFindClient()
        hasAvailableQueueAmount = queueModel.hasAvailableQueueAmount()

        actCreateOrder.setEnabled(bool(currentClientId)
                                  and not orderPresent
                                  and allMenuEnabled
                                  and hasAvailableQueueAmount)
        self.addQuotaStateToActionCaption(actCreateOrder)

        row = queueWidget.currentIndex().row()
        actionId = queueModel.getActionId(row)
        createPersonId = forceRef(db.translate(tableAction, 'id', actionId, 'createPerson_id'))
        setPersonId = forceRef(db.translate(tableAction, 'id', actionId, 'setPerson_id'))
        nurseOwnerId = QtGui.qApp.nurseOwnerId()

        # текущий пользователь - врач, назначивший услугу и имеющий право отменять свои назначения
        currentUserIsSetPerson = (not setPersonId is None
                                  and setPersonId == QtGui.qApp.userId
                                  and QtGui.qApp.userHasRight(urQueueToSelfDeletedTime))
        # текущий пользователь - медсестра, и она работает с врачом, назначившим услугу и имеющим право отменять свои назначения, а так же она создала эту запись
        currentUserIsNurseOfSetPerson = (QtGui.qApp.isNurse()
                                         and not setPersonId is None
                                         and setPersonId == nurseOwnerId  # Назначено врачом, с которым работает медстестра
                                         and createPersonId == QtGui.qApp.userId  # Создано текущей медсестрой
                                         and CUserInfo(nurseOwnerId).hasRight(urQueueToSelfDeletedTime))
        userHasRightToDeleteOrder = (QtGui.qApp.userHasRight(urQueueDeletedTime)
                                     or currentUserIsSetPerson
                                     or currentUserIsNurseOfSetPerson)

        actDeleteOrder.setEnabled(orderPresent and allMenuEnabled and userHasRightToDeleteOrder)
        actChangeNotes.setEnabled(orderPresent and allMenuEnabled)
        actPrintOrder.setEnabled(orderPresent and allMenuEnabled)
        if actProcessEQ and actFinishEQ:
            if self.isEQControl():
                status = queueModel.getStatus(row)
                processEQCaption = u''
                processEQActionEnabled = False
                finishEQActionEnabled = False

                if not orderPresent:
                    processEQCaption = u'Нет записи'
                elif status == 2: # Закончено
                    processEQCaption = u'Закончено'
                elif self.eqPanelWidget.isPersonControl() and self.getCurrentPersonId() != QtGui.qApp.getDrId():
                    processEQCaption = u'Выбран другой врач'
                elif self.eqPanelWidget.isDateControl() and self.calendarWidget.selectedDate() != QtCore.QDate.currentDate():
                    processEQCaption = u'Вызов возможен только для текущего дня'
                elif QtGui.qApp.isUseUnifiedDailyClientQueueNumber() and not queueModel.getClientQueueNumber(row):
                    processEQCaption = u'Пациенту необходимо получить номерок'
                elif not self.eqPanelWidget.eqPanel().isWork():
                    processEQCaption = u'Табло не работает'
                    self.eqPanelWidget.showError(self.eqPanelWidget.eqPanel().lastError())
                elif status == 1: # Ожидание
                    processEQCaption = u'Пригласить в кабинет'
                    processEQActionEnabled = True
                elif status == 0: # Начато
                    processEQCaption = u'Повторно пригласить пациента'
                    processEQActionEnabled = True
                    finishEQActionEnabled = True
                elif status == 3: # Отменено
                    processEQCaption = u'Отменено'

                actProcessEQ.setText(u'Эл.очередь: %s' % processEQCaption)
                actProcessEQ.setEnabled(processEQActionEnabled and allMenuEnabled)
                actFinishEQ.setEnabled(finishEQActionEnabled and allMenuEnabled)
                actProcessEQ.setVisible(True)
                actFinishEQ.setVisible(True)
            else:
                actProcessEQ.setVisible(False)
                actFinishEQ.setVisible(False)

        actPrintQueue.setEnabled(anyOrderPresent)
        if queueWidget == self.tblAmbQueue:
            actPrintQueuePass.setEnabled(anyOrderPresent and variantPrintQueue and allMenuEnabled)
            actPrintQueueNoPass.setEnabled(anyOrderPresent and variantPrintQueue and allMenuEnabled)
        else:
            actPrintQueuePass.setEnabled(anyOrderPresent and allMenuEnabled)
            actPrintQueueNoPass.setEnabled(anyOrderPresent and allMenuEnabled)
        actPrintQueueByTemplate.setEnabled(anyOrderPresent and allMenuEnabled)
        actFindClient.setEnabled(canFindClient and allMenuEnabled)
        actCreateEvent.setEnabled(orderPresent
                                  and bool(currentClientId)
                                  and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteEvents])
                                  and allMenuEnabled)
        actServiceReport.setEnabled(anyOrderPresent and allMenuEnabled)
        actInfo.setEnabled(orderPresent and allMenuEnabled)

    def popupMenuAmbAboutToShow(self):
        self.popupMenuAboutToShow(self.tblAmbQueue,
                                  self.actAmbCreateOrder,
                                  self.actAmbDeleteOrder,
                                  self.actAmbChangeNotes,
                                  self.actAmbPrintOrder,
                                  self.actAmbPrintQueue,
                                  self.actAmbPrintQueuePass,
                                  self.actAmbPrintQueueNoPass,
                                  self.actAmbPrintQueueByTemplate,
                                  self.actAmbFindClient,
                                  self.actAmbCreateEvent,
                                  self.actServiceReport,
                                  self.actAmbInfo,
                                  self.actEQProcessPatient,
                                  self.actEQFinishPatient)

    def popupMenuHomeAboutToShow(self):
        self.popupMenuAboutToShow(self.tblHomeQueue,
                                  self.actHomeCreateOrder,
                                  self.actHomeDeleteOrder,
                                  self.actHomeChangeNotes,
                                  self.actHomePrintOrder,
                                  self.actHomePrintQueue,
                                  self.actHomePrintQueuePass,
                                  self.actHomePrintQueueNoPass,
                                  self.actHomePrintQueueByTemplate,
                                  self.actHomeFindClient,
                                  self.actHomeCreateEvent,
                                  self.actServiceReport,
                                  self.actHomeInfo,
                                  None)

    def printOrder(self, timeTableWidget, queueWidget):
        num, time, clientId = self.getCurrentQueuedClientInfo(queueWidget)
        if clientId:
            visitInfo = self.getReceptionInfo(timeTableWidget)
            queueModel = queueWidget.model()
            queueRow = queueWidget.currentIndex().row()
            eventId = queueModel.getEventId(queueRow)
            printOrder(self,
                       clientId,
                       timeTableWidget != self.tblAmbTimeTable,
                       visitInfo['date'],
                       visitInfo['office'],
                       visitInfo['personId'],
                       eventId,
                       num,
                       time,
                       visitInfo['timeRange'],
                       )

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblAmbQueue_doubleClicked(self, index):
        clientId = self.getCurrentQueuedClientId(self.tblAmbQueue)
        if clientId:
            if QtGui.qApp.doubleClickQueuePerson() == 0:
                self.on_actAmbChangeNotes_triggered()
            elif QtGui.qApp.doubleClickQueuePerson() == 1:
                self.on_actAmbFindClient_triggered()
            elif QtGui.qApp.doubleClickQueuePerson() == 2:
                self.on_actAmbCreateEvent_triggered()
        else:
            self.on_actAmbCreateOrder_triggered()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblHomeQueue_doubleClicked(self, index):
        clientId = self.getCurrentQueuedClientId(self.tblHomeQueue)
        if clientId:
            if QtGui.qApp.doubleClickQueuePerson() == 0:
                self.on_actHomeChangeNotes_triggered()
            elif QtGui.qApp.doubleClickQueuePerson() == 1:
                self.on_actHomeFindClient_triggered()
            elif QtGui.qApp.doubleClickQueuePerson() == 2:
                self.on_actHomeCreateEvent_triggered()
        else:
            self.on_actHomeCreateOrder_triggered()

    @QtCore.pyqtSlot()
    def on_actAmbCreateOrder_triggered(self):
        if self.createOrder(self.tblAmbTimeTable, self.tblAmbQueue, QtGui.qApp.currentClientId()):
            if QtGui.qApp.doubleClickQueuing() == 1:
                self.printOrder(self.tblAmbTimeTable, self.tblAmbQueue)
            elif QtGui.qApp.doubleClickQueuing() == 2:
                self.changeNotes(self.tblAmbQueue)
            elif QtGui.qApp.doubleClickQueuing() == 3:
                self.changeNotes(self.tblAmbQueue)
                self.printOrder(self.tblAmbTimeTable, self.tblAmbQueue)

    @QtCore.pyqtSlot()
    def on_actAmbDeleteOrder_triggered(self):
        self.deleteOrder(self.tblAmbTimeTable, self.tblAmbQueue)
        self.updateTimeTable()
        QtGui.qApp.emitCurrentClientInfoChanged()

    @QtCore.pyqtSlot()
    def on_actAmbChangeNotes_triggered(self):
        self.changeNotes(self.tblAmbQueue)

    @QtCore.pyqtSlot()
    def on_actAmbPrintOrder_triggered(self):
        self.printOrder(self.tblAmbTimeTable, self.tblAmbQueue)

    @QtCore.pyqtSlot()
    def on_actAmbPrintQueue_triggered(self):
        self.printQueue(self.tblAmbTimeTable, self.tblAmbQueue, 2)

    @QtCore.pyqtSlot()
    def on_actAmbPrintQueuePass_triggered(self):
        nameMenuPrintQueue = u', список подтвержденных записей'
        self.printQueue(self.tblAmbTimeTable, self.tblAmbQueue, 0, nameMenuPrintQueue)

    @QtCore.pyqtSlot()
    def on_actAmbPrintQueueNoPass_triggered(self):
        nameMenuPrintQueue = u', список неподтвержденных записей'
        self.printQueue(self.tblAmbTimeTable, self.tblAmbQueue, 1, nameMenuPrintQueue)

    @QtCore.pyqtSlot(int)
    def on_actAmbPrintQueueByTemplate_printByTemplate(self, templateId):
        self.printQueueByTemplate(self.tblAmbTimeTable, self.tblAmbQueue, templateId)

    @QtCore.pyqtSlot()
    def on_actAmbCreateEvent_triggered(self):
        clientId = self.getCurrentQueuedClientId(self.tblAmbQueue)
        personId = self.getCurrentPersonId()
        specialityId = self.getPersonSpecialityId(personId)
        row = self.tblAmbQueue.currentIndex().row()
        time = self.tblAmbQueue.model().getTime(row) if row >= 0 else None
        date = self.calendarWidget.selectedDate()
        if specialityId:
            requestNewEvent(self, clientId, False, None, [], None, QtCore.QDateTime(date, time if time else QtCore.QTime()), personId)
        else:
            QtGui.qApp.requestNewEvent(clientId)

    @QtCore.pyqtSlot()
    def on_actHomeCreateEvent_triggered(self):
        clientId = self.getCurrentQueuedClientId(self.tblHomeQueue)
        personId = self.getCurrentPersonId()
        specialityId = self.getPersonSpecialityId(personId)
        row = self.tblHomeQueue.currentIndex().row()
        time = self.tblHomeQueue.model().getTime(row) if row >= 0 else None
        date = self.calendarWidget.selectedDate()
        if specialityId:
            requestNewEvent(self, clientId, False, None, [], None, QtCore.QDateTime(date, time if time else QtCore.QTime()), personId, None, None, None, None, [], '', False)
        else:
            QtGui.qApp.requestNewEvent(clientId)

    @QtCore.pyqtSlot()
    def on_actAmbFindClient_triggered(self):
        clientId = self.getCurrentQueuedClientId(self.tblAmbQueue)
        QtGui.qApp.findClient(clientId)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelHomeTimeTable_currentChanged(self, current, previous):
        begDate = self.modelHomeTimeTable.begDate
        row = current.row()
        if begDate and row != previous.row():
            date = begDate.addDays(row)
            self.calendarWidget.setSelectedDate(date)

    @QtCore.pyqtSlot()
    def on_actHomeCreateOrder_triggered(self):
        self.createOrder(self.tblHomeTimeTable, self.tblHomeQueue, QtGui.qApp.currentClientId())

    @QtCore.pyqtSlot()
    def on_actHomeDeleteOrder_triggered(self):
        self.deleteOrder(self.tblHomeTimeTable, self.tblHomeQueue)

    @QtCore.pyqtSlot()
    def on_actHomeChangeNotes_triggered(self):
        self.changeNotes(self.tblHomeQueue)

    @QtCore.pyqtSlot()
    def on_actHomePrintOrder_triggered(self):
        self.printOrder(self.tblHomeTimeTable, self.tblHomeQueue)

    @QtCore.pyqtSlot()
    def on_actHomePrintQueue_triggered(self):
        self.printQueue(self.tblHomeTimeTable, self.tblHomeQueue, 2)

    @QtCore.pyqtSlot()
    def on_actHomePrintQueuePass_triggered(self):
        nameMenuPrintQueue = u', список переданных врачу'
        self.printQueue(self.tblHomeTimeTable, self.tblHomeQueue, 0, nameMenuPrintQueue)

    @QtCore.pyqtSlot()
    def on_actHomePrintQueueNoPass_triggered(self):
        nameMenuPrintQueue = u', список непереданных врачу'
        self.printQueue(self.tblHomeTimeTable, self.tblHomeQueue, 1, nameMenuPrintQueue)

    @QtCore.pyqtSlot(int)
    def on_actHomePrintQueueByTemplate_printByTemplate(self, templateId):
        self.printQueueByTemplate(self.tblHomeTimeTable, self.tblHomeQueue, templateId)

    @QtCore.pyqtSlot()
    def on_actHomeFindClient_triggered(self):
        clientId = self.getCurrentQueuedClientId(self.tblHomeQueue)
        QtGui.qApp.findClient(clientId)

    @QtCore.pyqtSlot()
    def on_actServiceReport_triggered(self):
        db = QtGui.qApp.db
        tableVisit = db.table('Visit')
        personId = self.getCurrentPersonId()

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Сводка об обслуживании на ' + self.calendarWidget.selectedDate().toString('dd.MM.yyyy') + '\n')
        cursor.insertBlock()

        cursor.setCharFormat(CReportBase.ReportBody)
        personInfo = self.getPersonInfo(personId)
        speciality_id = personInfo['speciality_id']
        orgStructure_id = forceInt(db.translate('Person', 'id', personId, 'orgStructure_id'))
        orgStructureName = forceString(db.translate('OrgStructure', 'id', orgStructure_id, 'name'))
        cursor.insertText(u'врач: %s, %s\n' % (personInfo['fullName'], personInfo['specialityName']))
        cursor.insertText(u'подразделение: %s, %s\n' % (orgStructureName, personInfo['postName']))
        cursor.insertText(u'дата формирования: %s\n' % QtCore.QDate.currentDate().toString('dd.MM.yyyy'))
        cursor.insertBlock()

        cols = [
            ('2%', [u'№'], CReportBase.AlignRight),
            ('4%', [u'Время записи'], CReportBase.AlignLeft),
            ('10%', [u'ФИО'], CReportBase.AlignLeft),
            ('4%', [u'Д/р'], CReportBase.AlignLeft),
            ('3%', [u'Возраст'], CReportBase.AlignLeft),
            ('1%', [u'Пол'], CReportBase.AlignLeft),
            ('15%', [u'Адрес'], CReportBase.AlignLeft),
            ('25%', [u'Полис'], CReportBase.AlignLeft),
            ('10%', [u'Паспорт'], CReportBase.AlignLeft),
            ('10%', [u'СНИЛС'], CReportBase.AlignLeft),
            ('10%', [u'Врач'], CReportBase.AlignLeft),
            ('4%', [u'Время обслуживания'], CReportBase.AlignLeft),
            ('10%', [u'Тип'], CReportBase.AlignLeft),
            ('5%', [u'Диагноз'], CReportBase.AlignLeft),
            ('10%', [u'Результат'], CReportBase.AlignLeft),
        ]
        table = createTable(cursor, cols)
        cnt = 0

        clients = []
        for (timeTableWidget, queueWidget) in [(self.tblAmbTimeTable, self.tblAmbQueue), (self.tblHomeTimeTable, self.tblHomeQueue)]:
            queueModel = queueWidget.model()
            for row in xrange(queueModel.realRowCount()):
                if queueModel.getClientId(row):
                    time = queueModel.getTime(row)
                    clientId = queueModel.getClientId(row)
                    if clientId:
                        clients.append((clientId, self.calendarWidget.selectedDate(), time))

        num_same = 0
        num_other = 0
        num_no = 0
        for (clientId, day, time) in clients:#TODO: Возможно сделать вывод данных по другому
            i = table.addRow()
            cnt += 1
            table.setText(i, 0, i)
            clientInfo = getClientInfoEx(clientId, self.calendarWidget.selectedDate())
            table.setText(i, 2, clientInfo['fullName'])
            table.setText(i, 3, clientInfo['birthDate'])
            table.setText(i, 4, clientInfo['age'])
            table.setText(i, 5, clientInfo['sex'])
            table.setText(i, 6, clientInfo['regAddress'])
            table.setText(i, 7, clientInfo['policy'])
            table.setText(i, 8, clientInfo['document'])
            table.setText(i, 9, clientInfo['SNILS'])
            stmt = """
                select
                    Person.id as person_id, Diagnosis.MKB, Visit.date, Event.result_id, rbDiagnosticResult.name AS result, rbScene.name AS scene, Visit.createDatetime, Person.speciality_id
                from
                    Visit
                    join Event on Event.id=Visit.event_id
                    left join Person on Person.id=Visit.person_id
                    left join Diagnosis on Diagnosis.id=getEventPersonDiagnosis(Event.id, Person.id)
                    LEFT JOIN Diagnostic ON Diagnosis.id = Diagnostic.diagnosis_id
                    LEFT JOIN rbDiagnosticResult ON rbDiagnosticResult.id=Diagnostic.result_id
                    LEFT JOIN rbScene ON rbScene.id = Visit.scene_id
                where
                    %s and
                    Event.client_id=%d
                    and (Person.id=%d or Person.speciality_id=%d)
            """ % (tableVisit['date'].dateEq(day), clientId, personId, speciality_id)
            query = db.query(stmt)
            no_visit = 1
            table.setText(i, 1, formatTime(time) if time else '--:--')
            if query.next():
                record = query.record()
                personId1 = forceInt(record.value('person_id'))
                if personId1:
                    personInfo1 = self.getPersonInfo(personId1)
                    if personInfo1:
                        table.setText(i, 10, personInfo1['fullName'])
                    table.setText(i, 11, formatTime(record.value('createDatetime').toTime()))
                    table.setText(i, 12, forceString(record.value('scene')))
                    table.setText(i, 13, forceString(record.value('MKB')))
                    table.setText(i, 14, forceString(record.value('result')))
                    if personId == personId1:
                        num_same += 1
                        no_visit = 0
                    elif forceInt(record.value('speciality_id')) == speciality_id:
                        num_other += 1
                        no_visit = 0
            if no_visit:
                num_no += 1
                #                table.setText(i, 1, '-')
                table.setText(i, 10, '-')
                table.setText(i, 11, '-')
                table.setText(i, 12, '-')
                table.setText(i, 13, '-')
                table.setText(i, 14, '-')

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(u'обслужено врачом к которому была запись: %d; обслужено коллегами: %d; не было обслужено: %d\n' % (num_same, num_other, num_no))

        reportView = CReportViewDialog(self)
        reportView.setWindowTitle(u'Сводка об обслуживании')
        reportView.setText(doc)
        reportView.exec_()

    @QtCore.pyqtSlot()
    def on_actAmbInfo_triggered(self):
        self.showInfo(self.tblAmbTimeTable, self.tblAmbQueue)

    @QtCore.pyqtSlot()
    def on_actHomeInfo_triggered(self):
        self.showInfo(self.tblHomeTimeTable, self.tblHomeQueue)

    def showInfo(self, timeTableWidget, queueWidget):
        db = QtGui.qApp.db
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Свойства записи')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)

        cursor.insertText(u'дата записи: %s\n' % self.calendarWidget.selectedDate().toString('dd.MM.yyyy'))
        personId = self.getCurrentPersonId()
        if personId:
            personInfo = self.getPersonInfo(personId)
            orgStructure_id = forceInt(db.translate('Person', 'id', personId, 'orgStructure_id'))
            orgStructureName = forceString(db.translate('OrgStructure', 'id', orgStructure_id, 'name'))
            cursor.insertText(u'врач: %s, %s\n' % (personInfo['fullName'], personInfo['specialityName']))
            cursor.insertText(u'подразделение: %s, %s\n' % (orgStructureName, personInfo['postName']))

        date = self.calendarWidget.selectedDate()
        queueModel = queueWidget.model()
        row = queueWidget.currentIndex().row()
        if row >= 0:
            clientId = queueModel.getClientId(row)
            clientInfo = getClientInfoEx(clientId, date)
            cursor.insertText(u'пациент: %s\n' % clientInfo['fullName'])
            cursor.insertText(u'д/р: %s\n' % clientInfo['birthDate'])
            cursor.insertText(u'возраст: %s\n' % clientInfo['age'])
            cursor.insertText(u'пол: %s\n' % clientInfo['sex'])
            cursor.insertText(u'адрес: %s\n' % clientInfo['regAddress'])
            cursor.insertText(u'полис: %s\n' % clientInfo['policy'])
            cursor.insertText(u'паспорт: %s\n' % clientInfo['document'])
            cursor.insertText(u'СНИЛС: %s\n' % clientInfo['SNILS'])
            actionId = queueModel.getActionId(row)
            tableAction = db.table('Action')
            record = db.getRecord(tableAction, '*', actionId)
            note = forceString(record.value('note'))
            cursor.insertText(u'жалобы/примечания: %s\n' % note)
            receptionInfo = self.getReceptionInfo(timeTableWidget)
            if timeTableWidget == self.tblAmbTimeTable:
                cursor.insertText(u'запись на амбулаторный приём ')
                office = u'к. ' + receptionInfo['office']
            else:
                cursor.insertText(u'вызов на дом ')
                office = ''
            cursor.insertText(forceString(receptionInfo['date']) + ' ' + receptionInfo['timeRange'] + ' ' + office)

            cursor.movePosition(QtGui.QTextCursor.PreviousBlock,
                                QtGui.QTextCursor.MoveAnchor,
                                cursor.blockNumber() - 1)
            createPerson_id = forceRef(record.value('createPerson_id'))
            createPersonName = ''
            if createPerson_id:
                createPersonRecord = db.getRecord('vrbPersonWithSpeciality', '*', createPerson_id)
                if createPersonRecord:
                    createPersonName = forceString(createPersonRecord.value('name'))
            cursor.insertText(u'Создатель записи: %s\n' % createPersonName)
            createDatetime = forceString(record.value('createDatetime'))
            createDatetime = createDatetime if createDatetime else ''
            cursor.insertText(u'Дата создания записи: %s\n' % createDatetime)
            modifyPerson_id = forceRef(record.value('modifyPerson_id'))
            modifyPersonName = ''
            if modifyPerson_id:
                modifyPersonRecord = db.getRecord('vrbPersonWithSpeciality', '*', modifyPerson_id)
                if modifyPersonRecord:
                    modifyPersonName = forceString(modifyPersonRecord.value('name'))
            cursor.insertText(u'Редактор записи: %s\n' % modifyPersonName)
            modifyDatetime = forceString(record.value('modifyDatetime'))
            modifyDatetime = modifyDatetime if modifyDatetime else ''
            cursor.insertText(u'Дата редактирования записи: %s\n' % modifyDatetime)

        cursor.insertBlock()
        reportView = CReportViewDialog(self)
        reportView.setWindowTitle(u'Свойства записи')
        reportView.setText(doc)
        reportView.exec_()


class CTimeTableModel(QtCore.QAbstractTableModel):
    headerText = [u'Время', u'Каб', u'План', u'Готов']

    def __init__(self, parent, actionTypeCode):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.actionTypeCode = actionTypeCode
        self.personId = None
        self.begDate = None
        self.endDate = None
        self.dayInfoList = [(None,) * 6] * 7
        self.redBrush = QtGui.QBrush(QtGui.QColor(255, 0, 0))

    def columnCount(self, index=QtCore.QModelIndex()):
        return 4

    def rowCount(self, index=QtCore.QModelIndex()):
        return 7

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        if orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(QtCore.QDate.shortDayName(section + 1))
            elif role == QtCore.Qt.ToolTipRole:
                if self.begDate:
                    return QtCore.QVariant(forceString(self.begDate.addDays(section)))
            elif role == QtCore.Qt.ForegroundRole:
                if section >= 5:
                    return QtCore.QVariant(self.redBrush)
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            dayInfo = self.dayInfoList[row]
            value = dayInfo[column]
            if column == 0:
                if value:
                    if dayInfo[5]: # code of reasonOfAbsence
                        return QtCore.QVariant(dayInfo[5])
                    else:
                        return QtCore.QVariant(formatTimeRange(value))
                else:
                    if dayInfo[5]: # code of reasonOfAbsence
                        return QtCore.QVariant(dayInfo[5])
                    else:
                        return QtCore.QVariant()
            else:
                return toVariant(value)
        return QtCore.QVariant()

    def setPersonAndDate(self, personId, date):
        if self.personId == personId and self.begDate <= date <= self.endDate:
            self.updateData()
        else:
            self.personId = personId
            self.begDate = date.addDays(1 - date.dayOfWeek())
            self.endDate = self.begDate.addDays(6)
            self.loadData()
            self.reset()

    @staticmethod
    def getTimeTableEvents(begDate, endDate, personId):
        if begDate and endDate and personId:
            db = QtGui.qApp.db
            eventTypeId = getEventType(constants.etcTimeTable).eventTypeId
            tableEvent = db.table('Event')
            tablePerson = db.table('Person')
            table = tableEvent.leftJoin(tablePerson, tablePerson['id'].eq(tableEvent['execPerson_id']))
            cols = [
                tableEvent['id'],
                tableEvent['setDate']
            ]
            cond = [
                tableEvent['eventType_id'].eq(eventTypeId),
                tableEvent['setDate'].between(begDate, endDate),
                tableEvent['execPerson_id'].eq(personId),
                db.joinOr([
                    tablePerson['lastAccessibleTimelineDate'].isNull(),
                    tablePerson['lastAccessibleTimelineDate'].isZeroDate(),
                    tablePerson['lastAccessibleTimelineDate'].dateGe(tableEvent['setDate'])
                ])
            ]
            return db.getRecordList(table, cols, cond)
        else:
            return []

    def loadDataInt(self):
        events = self.getTimeTableEvents(self.begDate, self.begDate.addDays(6), self.personId)
        result = [None] * 7
        for event in events:
            date = forceDate(event.value('setDate'))
            i = self.begDate.daysTo(date)
            if result[i] is None:
                eventId = forceRef(event.value('id'))
                result[i] = self.getDayInfo(eventId)
        for i in xrange(7):
            if result[i] is None:
                result[i] = (None,) * 6
        return result

    def loadData(self):
        self.dayInfoList = self.loadDataInt()

    def updateData(self):
        dayInfoList = self.loadDataInt()
        for i in xrange(7):
            dayInfo = dayInfoList[i]
            prevDayInfo = self.dayInfoList[i]
            self.dayInfoList[i] = dayInfo
            for column in xrange(4):
                if prevDayInfo != dayInfo:
                    index = self.index(i, column)
                    self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def updateAvail(self, date, queue):
        row = self.begDate.daysTo(date)
        (timeRange, office, plan, available, eventId, reasonOfAbsenceCode) = self.dayInfoList[row]
        queueFilled = len(queue) - queue.count(None)
        available = (plan if plan else 0) - queueFilled
        self.dayInfoList[row] = (timeRange, office, plan, available, eventId, reasonOfAbsenceCode)
        index = self.index(row, 3)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def getDayInfo(self, eventId):
        action = CAction.getAction(eventId, constants.atcTimeLine)
        reasonOfAbsenceId = action['reasonOfAbsence']
        if reasonOfAbsenceId:
            reasonOfAbsenceCode = forceString(QtGui.qApp.db.translate('rbReasonOfAbsence', 'id', reasonOfAbsenceId, 'code'))
        else:
            reasonOfAbsenceCode = None

        action = CAction.getAction(eventId, self.actionTypeCode)
        begTime = action['begTime']
        endTime = action['endTime']
        if begTime and endTime:
            timeRange = (begTime, endTime)
        else:
            timeRange = None
        if self.actionTypeCode != constants.atcHome:
            office = action['office']
        else:
            office = None
        plan = len(action['times'])
        queue = action['queue']
        queueFilled = len(queue) - queue.count(None)
        available = (plan if plan else 0) - queueFilled
        return timeRange, office, plan, available, eventId, reasonOfAbsenceCode

    def getTimeRange(self, row):
        return self.dayInfoList[row][0]

    def getOffice(self, row):
        result = self.dayInfoList[row][1]
        return '' if result is None else result

    def getTimeTableEventId(self, row):
        return self.dayInfoList[row][4]

    def getTimeTableEventIdByDate(self, date):
        row = self.begDate.daysTo(date)
        if 0 <= row < 7:
            return self.getTimeTableEventId(row)
        else:
            return None


class CQueueModel(QtCore.QAbstractTableModel):
    class CActionInfo:
        def __init__(self, actionId, eventId, clientId, clientText, status, setPersonId, setPersonSpecialityId):
            self.actionId = actionId
            self.eventId = eventId
            self.clientId = clientId
            self.clientText = clientText
            self.status = status
            self.setPersonId = setPersonId
            self.setPersonSpecialityId = setPersonSpecialityId

    def __init__(self, parent, actionTypeCode):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.actionTypeCode = actionTypeCode
        self.personId = None
        self.personSpecialityId = None
        self.timeTableEventId = None
        self.timeTableAction = None  # type: CAction
        self.date = None
        self.plan = 0
        self.availableShare = 100
        self.timeList = []  # type: list[QtCore.QTime]
        self.colorList = []  # type: list[unicode]
        self.actionInfoList = []  # type: list[CQueueModel.CActionInfo]
        self.canQueueOverTime = False
        self.extraTime = []
        self.visibleExtraTime = []
        self.extraStartIndex = 0
        self.queueNumber = []  # type: list[int]
        self._isEqControl = False

    def setEQControl(self, enabled):
        self._isEqControl = enabled

    def complaintsRequired(self):
        return self.actionTypeCode == constants.atcHome

    def columnCount(self, index=QtCore.QModelIndex()):
        return 1

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.timeList) + (1 if self.canQueueOverTime else 0)

    def realRowCount(self, index=QtCore.QModelIndex()):
        return len(self.timeList)

    def hasAvailableQueueAmount(self):
        queued = sum(1 for info in self.actionInfoList if info.actionId is not None)
        amount = max(1, self.availableShare * self.plan / 100) if self.availableShare else 0
        return queued < amount

    def flags(self, index = QtCore.QModelIndex()):
        row = index.row()
        if (0 <= row < len(self.actionInfoList)
                and self.actionInfoList[row].actionId is None
                and not self.hasAvailableQueueAmount()):
            result = QtCore.Qt.NoItemFlags
        else:
            result = QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled
        if self.actionTypeCode == constants.atcHome or (self.actionTypeCode == constants.atcAmbulance and QtGui.qApp.ambulanceUserCheckable()):
            row = index.row()
            if row < len(self.actionInfoList):
                info = self.actionInfoList[row]
                if info and info.actionId:
                    result = result | QtCore.Qt.ItemIsUserCheckable
        return result

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(u'ФИО')
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                if QtGui.qApp.hideTimeInQueueTable():
                    return QtCore.QVariant(section + 1)
                else:
                    time = self.timeList[section] if section < len(self.timeList) else None
                    return QtCore.QVariant(locFormatTime(time))
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.QVariant(QtCore.Qt.AlignRight)
            elif role == QtCore.Qt.BackgroundRole:
                color = self.colorList[section] if section < len(self.colorList) else None
                if color:
                    return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(color)))
                if (self.extraStartIndex
                        and self.extraStartIndex <= section < self.extraStartIndex + len(self.visibleExtraTime)):
                    return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
            elif role == QtCore.Qt.TextColorRole:
                if (self.extraStartIndex
                        and self.extraStartIndex <= section < self.extraStartIndex + len(self.visibleExtraTime)
                        and not (self.colorList[section] if section < len(self.colorList) else None)):
                    return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(255,255,255)))
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            if row < len(self.actionInfoList):
                info = self.actionInfoList[row]
                if info:
                    return QtCore.QVariant(info.clientText)
        elif role == QtCore.Qt.CheckStateRole and (self.actionTypeCode == constants.atcHome or
                                                   (self.actionTypeCode == constants.atcAmbulance and
                                                    QtGui.qApp.ambulanceUserCheckable())):
            if row < len(self.actionInfoList):
                info = self.actionInfoList[row]
                if info and info.eventId:
                    return QtCore.QVariant(QtCore.Qt.Checked if info.status == 0 else QtCore.Qt.Unchecked)
        elif role == QtCore.Qt.ToolTipRole:
            if row < len(self.actionInfoList):
                info = self.actionInfoList[row]
                if info:
                    cache = CRBModelDataCache.getData('vrbPersonWithSpeciality', True)
                    text = cache.getStringById(info.setPersonId, CRBComboBox.showName)
                    return QtCore.QVariant(text)
        elif role == QtCore.Qt.FontRole:
            if row < len(self.actionInfoList):
                info = self.actionInfoList[row]
                if info:
                    setPersonId = info.setPersonId
                    setPersonSpecialityId = info.setPersonSpecialityId
                    result = QtGui.QFont()
                    if self.personId == setPersonId:
                        result.setBold(True)
                    elif self.personSpecialityId == setPersonSpecialityId:
                        result.setBold(True)
                        result.setItalic(True)
                    elif setPersonSpecialityId:
                        result.setItalic(True)
                    return QtCore.QVariant(result)
        elif role == QtCore.Qt.BackgroundRole:
            if row < len(self.actionInfoList):
                info = self.actionInfoList[row]
                if info and info.actionId:
                    cache = CDbDataCache.getData('Action', 'isUrgent', 'id = %d' % info.actionId)
                    if forceInt(cache.first) == 1:
                        return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(246, 74, 74)))
                elif not self.hasAvailableQueueAmount():
                    return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(192, 192, 192)))
        elif role == QtCore.Qt.DecorationRole and self._isEqControl:
            status = self.getStatus(row)
            if status == 2:
                return QtCore.QVariant(QtGui.QIcon(':/new/prefix1/icons/eq/clientComplete.png'))
            elif self.getClientQueueNumber(row):
                if status == 0:
                    return QtCore.QVariant(QtGui.QIcon(':/new/prefix1/icons/eq/clientProcessed.png'))
                elif status == 1:
                    return QtCore.QVariant(QtGui.QIcon(':/new/prefix1/icons/eq/clientAvailable.png'))
            return QtCore.QVariant(QtGui.QIcon(':/new/prefix1/icons/eq/clientNotAvailable.png'))
        return QtCore.QVariant()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row = index.row()
        if (role == QtCore.Qt.CheckStateRole and (self.actionTypeCode == constants.atcHome or
                                                  (self.actionTypeCode == constants.atcAmbulance and
                                                   QtGui.qApp.ambulanceUserCheckable()))):
            if row < len(self.actionInfoList):
                info = self.actionInfoList[row]
                status = info.status
                if status in (0, 1):
                    status = 0 if forceBool(value) else 1
                    return self.setStatusByRow(row, status)
        return False

    def setStatusByRow(self, row, status):
        if len(self.actionInfoList) <= row < 0:
            return False
        info = self.actionInfoList[row]
        actionId = info.actionId
        if not actionId:
            return False
        db = QtGui.qApp.db
        table = db.table('Action')
        record = table.newRecord(['id', 'status'])
        record.setValue('id', QtCore.QVariant(actionId))
        record.setValue('status', QtCore.QVariant(status))
        try:
            db.updateRecord(table, record)
            info.status = status
            self.emitDataChanged(row)
        except:
            QtGui.qApp.logCurrentException()
            return False
        return True

    def setPersonAndDate(self, personId, date, timeTableEventId, dayInfo=None):
        self.dayInfo = dayInfo
        self.availableShare = getAvailableQueueShare(date, personId=personId)
        if self.personId == personId and self.date == date and self.timeTableEventId == timeTableEventId:
            self.updateData()
        else:
            self.timeTableEventId = timeTableEventId
            self.timeTableAction = None
            if self.personId != personId:
                self.personSpecialityId = forceRef(QtGui.qApp.db.translate('Person', 'id', personId, 'speciality_id'))
                self.personId = personId
            self.date = date
            self.loadData()

    def getPlan(self, begTime, endTime, interval):
        if begTime and endTime and interval:
            diffTime = abs(endTime.secsTo(begTime) / 60)
            return diffTime / interval

    def setHiddenRows(self):
        if self.timeTableEventId:
            action = self.timeTableAction
            try:
                planInter = self.getPlan(action['endTime1'], action['begTime2'], action['planInter'])
                if planInter:
                    plan1 = self.getPlan(action['begTime1'], action['endTime1'], action['plan1'])
                    self.extraStartIndex = plan1
                    self.extraTime = self.timeList[plan1:plan1 + planInter]
                    self.visibleExtraTime = self.extraTime[:]
                    if self.extraTime:
                        queue = action['queue']
                        cutQueue = queue[plan1:plan1 + planInter]
                        deletePrev = False
                        for queueItem in cutQueue[::-1]:
                            if not queueItem:
                                if deletePrev:
                                    self.visibleExtraTime.pop()
                                else:
                                    deletePrev = True
                            else:
                                break
                    return
            except KeyError:
                pass
        self.extraStartIndex = 0
        self.extraTime = []
        self.visibleExtraTime = []

    # def isTimeInTimeRange(self, time, gaps, delta=0):
    #     for x in gaps:
    #         if x['begTime'].addSecs(-delta) <= time < x['endTime']:
    #             return True
    #     return False
    #
    # def recreateTimeByPersonGaps(self):
    #     """
    #         Исключает те номерки, чье время попадает в рамки назначенных специалисту перерывов
    #     """
    #
    #     def clearList(lst, removeLst):
    #         for x in removeLst:
    #             lst.remove(x)
    #
    #     self.timeTableAction = CAction.getAction(self.timeTableEventId, self.actionTypeCode)
    #     self.plan = len(self.timeTableAction['times'])
    #     times = self.timeTableAction['times']
    #     if self.actionTypeCode == constants.atcAmbulance:
    #         colors = self.timeTableAction['colors']
    #     else:
    #         colors = []
    #     queue = self.timeTableAction['queue']
    #
    #     gaps = getPersonGaps(getGapList(self.personId))
    #
    #     removeList = {
    #         'times': [],
    #         'colors': [],
    #         'queue': []
    #     }
    #     if len(times) > 1:
    #         delta = times[0].secsTo(times[1])
    #     else:
    #         delta = 0
    #
    #     for i, x in enumerate(times):
    #         if self.isTimeInTimeRange(x, gaps, delta):
    #             if times:
    #                 removeList['times'].append(times[i])
    #             if colors:
    #                 removeList['colors'].append(colors[i])
    #             if queue:
    #                 removeList['queue'].append(queue[i])
    #
    #     clearList(times, removeList['times'])
    #     clearList(colors, removeList['colors'])
    #     clearList(queue, removeList['queue'])
    #     for i, gap in enumerate(gaps):
    #         firstTime = None
    #         for x in times:
    #             endTime = gaps[i+1]['begTime'] if i+1 < len(gaps) else self.dayInfo[0][1]
    #             if gap['endTime'].addSecs(-delta) <= x < endTime:
    #                 if firstTime is None:
    #                     firstTime = x.minute()
    #
    #                 # tempTimeList = []
    #                 lstLen = len(times[times.index(x):])
    #                 for id, t in enumerate(times[times.index(x):]):
    #                     if t <= endTime:
    #                         times[times.index(t)] = t.addSecs(-60*firstTime)
    #                     if t > endTime.addSecs(-delta) or id + 1 == lstLen:
    #                         prevTime = times[times.index(t)-1] if t in times else times[-1]
    #                         for t1 in times[times.index(prevTime):]:
    #                             if t1.secsTo(endTime) - delta > delta and t1 <= endTime:
    #                                 # tempTimeList.insert(times.index(t1)+1, t1.addSecs(delta))
    #                                 temp = t1.addSecs(delta)
    #                                 if temp not in times:
    #                                     times.insert(times.index(t1) + 1, temp)
    #                         break
    #                 break
    #
    #     return times, colors, queue

    def loadData(self):
        if self.timeTableEventId:
            # times, colors, queue = self.recreateTimeByPersonGaps()
            self.timeTableAction = CAction.getAction(self.timeTableEventId, self.actionTypeCode)
            self.plan = len(self.timeTableAction['times'])
            times = self.timeTableAction['times']
            if self.actionTypeCode == constants.atcAmbulance:
                colors = self.timeTableAction['colors']
            else:
                colors = []
            queue = self.timeTableAction['queue']
        else:
            self.timeTableAction = None
            self.plan = 0
            times = []
            colors = []
            queue = []
        prevBlockSignals = self.blockSignals(True)
        try:
            self.updateQueue(times, queue, colors)
        finally:
            self.setHiddenRows()
            self.blockSignals(prevBlockSignals)
            self.reset()

    def updateData(self):
        if self.timeTableEventId:
            self.timeTableAction = CAction.getAction(self.timeTableEventId, self.actionTypeCode)
            self.plan = len(self.timeTableAction['times'])
            times = self.timeTableAction['times']
            if self.actionTypeCode == constants.atcAmbulance:
                colors = self.timeTableAction['colors']
            else:
                colors = []
            queue = self.timeTableAction['queue']
        else:
            self.timeTableAction = None
            self.plan = 0
            times = []
            colors = []
            queue = []
        self.updateQueue(times, queue, colors)
        self.setHiddenRows()

    def updateQueue(self, times, queue, colors):
        diff = len(times) - len(queue)
        if diff < 0:
            times.extend([None] * (-diff))
        elif diff > 0:
            queue.extend([None] * diff)
        oldLenQueue = len(self.actionInfoList)
        newLenQueue = len(queue)
        for row in xrange(min(newLenQueue, oldLenQueue)):
            actionId = queue[row] if row < len(queue) else None
            info = self.actionInfoList[row]
            if info.actionId != actionId:
                self.actionInfoList[row] = self.getActionInfo(actionId)
                self.queueNumber[row] = None
            self.queueNumber[row] = getClientQueueNumber(self.actionInfoList[row].clientId, self.date)
            self.emitDataChanged(row)
        if oldLenQueue < newLenQueue:
            self.beginInsertRows(QtCore.QModelIndex(), oldLenQueue, newLenQueue - 1)
            try:
                for row in xrange(oldLenQueue, newLenQueue):
                    actionId = queue[row] if row < len(queue) else None
                    actionInfo = self.getActionInfo(actionId)
                    self.actionInfoList.append(actionInfo)
                    self.queueNumber.append(getClientQueueNumber(actionInfo.clientId, self.date))
            finally:
                self.endInsertRows()
        elif newLenQueue < oldLenQueue:
            self.beginRemoveRows(QtCore.QModelIndex(), newLenQueue, oldLenQueue - 1)
            del self.actionInfoList[newLenQueue:oldLenQueue]
            del self.queueNumber[newLenQueue:oldLenQueue]
            self.endRemoveRows()
        self.timeList = times
        self.colorList = colors
        self.canQueueOverTime = (len(times) > 0 and
                                 (QtGui.qApp.userHasRight(urQueueOverTime) or
                                  self.personId == QtGui.qApp.userId and
                                  QtGui.qApp.userHasRight(urQueueToSelfOverTime)))

    @staticmethod
    def getActionInfo(actionId):
        if actionId:
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            tableEvent = db.table('Event')
            tablePerson = db.table('Person')
            table = tableAction.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
            table = table.leftJoin(tablePerson, tablePerson['id'].eq(tableAction['setPerson_id']))
            cols = [tableAction['event_id'],
                    tableEvent['client_id'],
                    tableAction['status'],
                    tableAction['setPerson_id'],
                    tablePerson['speciality_id']]
            record = db.getRecordEx(table, cols, tableAction['id'].eq(actionId))
            if record:
                clientId = forceRef(record.value('client_id'))
                return CQueueModel.CActionInfo(actionId,
                                               forceRef(record.value('event_id')),
                                               clientId,
                                               getClientMiniInfo(clientId) if clientId else None,
                                               forceInt(record.value('status')),
                                               forceRef(record.value('setPerson_id')),
                                               forceRef(record.value('speciality_id')))

        return CQueueModel.CActionInfo(None, None, None, None, None, None, None)

    def queueClient(self, row, eventId, actionId, clientId):
        actionInfo = CQueueModel.CActionInfo(actionId,
                                             eventId,
                                             clientId,
                                             getClientMiniInfo(clientId),
                                             1,
                                             QtGui.qApp.getDrId(),
                                             QtGui.qApp.drOrUserSpecialityId())
        if row >= len(self.timeList):
            self.beginInsertRows(QtCore.QModelIndex(), row + 1, row + 1)
            self.timeList.append(None)
            self.actionInfoList.append(actionInfo)
            self.queueNumber.append(getClientQueueNumber(actionInfo.clientId, self.date))
            self.endInsertRows()
        else:
            self.actionInfoList[row] = actionInfo
            self.emitDataChanged(row)

    def getHiddenRows(self):
        visibleRows = xrange(self.extraStartIndex, self.extraStartIndex + len(self.visibleExtraTime))
        invisibleRows = xrange(self.extraStartIndex + len(self.visibleExtraTime), self.extraStartIndex + len(self.extraTime))
        return visibleRows, invisibleRows

    def dequeueClient(self, row):
        if self.timeList[row]:
            db = QtGui.qApp.db
            table = db.table('Action')
            actionId = self.getActionId(row)
            db.updateRecords(table,
                             expr=[table['deleted'].eq(1),
                                   table['status'].eq(3)],
                             where=table['id'].eq(actionId))
            self.actionInfoList[row] = CQueueModel.CActionInfo(None, None, None, None, 0, None, None)
            self.emitDataChanged(row)
        else:
            self.beginRemoveRows(QtCore.QModelIndex(), row, row)
            del self.timeList[row]
            del self.actionInfoList[row]
            self.endRemoveRows()

    def emitDataChanged(self, row):
        index = self.index(row, 0)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)

    def getTime(self, row):
        return self.timeList[row] if row in xrange(len(self.timeList)) and self.timeList[row] is not None \
                                  else QtCore.QTime()

    def getActionId(self, row):
        return self.actionInfoList[row].actionId if 0 <= row < len(self.actionInfoList) else None

    def getEventId(self, row):
        return self.actionInfoList[row].eventId if 0 <= row < len(self.actionInfoList) else None

    def getClientId(self, row):
        return self.actionInfoList[row].clientId if 0 <= row < len(self.actionInfoList) else None

    def getClientQueueNumber(self, row):
        if 0 <= row < len(self.actionInfoList):
            return self.queueNumber[row] if QtGui.qApp.isUseUnifiedDailyClientQueueNumber() else row + 1
        return None

    def getSetPersonId(self, row):
        return self.actionInfoList[row].setPersonId if 0 <= row < len(self.actionInfoList) else None

    def getStatus(self, row):
        return self.actionInfoList[row].status if 0 <= row < len(self.actionInfoList) else None

    def setStatus(self, clientId, actionId, status):
        for row, actionInfo in enumerate(self.actionInfoList):
            if actionInfo.actionId == actionId and actionInfo.clientId == clientId:
                self.actionInfoList[row].status = status
                return

    def getClientText(self, row):
        return self.actionInfoList[row].clientText if 0 <= row < len(self.actionInfoList) else None

    def getComplaints(self, row):
        actionId = self.getActionId(row)
        if actionId:
            note = forceString(QtGui.qApp.db.translate('Action', 'id', actionId, 'note'))
            if note:
                return note

        personId = self.getSetPersonId(row)
        if personId:
            note = u'Назначивший врач: ' + forceString(
                QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name')
            )
            if note:
                return note

        return u''

    def getQueuedClientsCount(self):
        return len(self.actionInfoList) - self.getActionList().count(None)

    def getActionList(self):
        return [info.actionId for info in self.actionInfoList]

    def findClientRow(self, clientId):
        for row, actionInfo in enumerate(self.actionInfoList):
            if actionInfo.clientId == clientId:
                return row
        return -1

    def findActionIdRow(self, actionId):
        for row, actionInfo in enumerate(self.actionInfoList):
            if actionInfo.actionId == actionId:
                return row
        return -1

    def getPrimaryQueuedCount(self):
        db = QtGui.qApp.db
        infomatId = forceRef(db.translate('Person', 'login', 'infomat', 'id'))
        externalIds = (None, infomatId)
        result = 0
        for actionInfo in self.actionInfoList:
            if (actionInfo.actionId
                and actionInfo.setPersonSpecialityId is None
                and actionInfo.setPersonId not in externalIds
                and not QtGui.qApp.personAddingCommentState(actionInfo.setPersonId)[0]):
                result += 1
        return result

    def getOwnQueuedCount(self):
        result = 0
        for actionInfo in self.actionInfoList:
            if actionInfo.actionId and actionInfo.setPersonId == QtGui.qApp.getDrId():
                result += 1
        return result

    def getConsultancyQueuedCount(self):
        result = 0
        for actionInfo in self.actionInfoList:
            if (actionInfo.actionId
                and actionInfo.setPersonSpecialityId
                and actionInfo.setPersonId != self.personId
                ):
                result += 1
        return result

    def getExternalQueuedCount(self):
        result = 0
        db = QtGui.qApp.db
        infomatId = forceRef(db.translate('Person', 'login', 'infomat', 'id'))
        internalIds = (None, infomatId)
        for actionInfo in self.actionInfoList:
            if (actionInfo.actionId
                and (QtGui.qApp.personAddingCommentState(actionInfo.setPersonId)[0]
                     or actionInfo.setPersonId in internalIds)
                ):
                result += 1
        return result

    def getQueuedCount(self):
        # количество записанных
        if QtGui.qApp.isNeedAddComent():
            return self.getExternalQueuedCount()
        elif QtGui.qApp.drOrUserSpecialityId():
            if self.personId == QtGui.qApp.getDrId():
                return self.getOwnQueuedCount()
            else:
                return self.getConsultancyQueuedCount()
        else:
            return self.getPrimaryQueuedCount()


def createQueueEvent(personId, date, time, clientId, complaints='', office='', referral_ids=None):
    """
        return (eventId, actionId) tuple
    """
    if not referral_ids:
        referral_ids = {}
    etcQueue = 'queue'
    atcQueue = 'queue'

    queueDatetime = QtCore.QDateTime(date, time) if time else QtCore.QDateTime(date)
    db = QtGui.qApp.db
    eventTable = db.table('Event')
    actionTable = db.table('Action')

    eventTypeId = getEventType(etcQueue).eventTypeId
    assert eventTypeId, 'EventType with code "%s" does not exist' % etcQueue
    actionTypeId = db.translate('ActionType', 'code', atcQueue, 'id')
    assert actionTypeId, 'ActionType with code "%s" does not exist' % atcQueue

    eventRecord = eventTable.newRecord()
    eventRecord.setValue('eventType_id', eventTypeId)
    eventRecord.setValue('org_id', QtCore.QVariant(QtGui.qApp.currentOrgId()))
    eventRecord.setValue('client_id', QtCore.QVariant(clientId))
    eventRecord.setValue('setDate', QtCore.QVariant(queueDatetime))
    eventRecord.setValue('isPrimary', QtCore.QVariant(1))
    if referral_ids.get(1, None):
        eventRecord.setValue('referral_id', QtCore.QVariant(referral_ids[1]))
    if referral_ids.get(2, None):
        eventRecord.setValue('armyReferral_id', QtCore.QVariant(referral_ids[2]))
    eventId = db.insertRecord(eventTable, eventRecord)

    actionRecord = actionTable.newRecord()  # 'queue' action
    actionRecord.setValue('actionType_id', actionTypeId)
    actionRecord.setValue('event_id', QtCore.QVariant(eventId))
    actionRecord.setValue('directionDate', QtCore.QVariant(queueDatetime))
    actionRecord.setValue('status', QtCore.QVariant(1))  # ожидание
    actionRecord.setValue('person_id', QtCore.QVariant(personId))
    actionRecord.setValue('setPerson_id', QtCore.QVariant(QtGui.qApp.getDrId()))
    actionRecord.setValue('note', QtCore.QVariant(complaints))
    actionRecord.setValue('office', QtCore.QVariant(office))
    actionId = db.insertRecord(actionTable, actionRecord)

    return eventId, actionId


def locFormatTime(t):
    return t.toString('H:mm') if t else '--:--'


def getQuota(personId, count):
    db = QtGui.qApp.db
    tablePersonPrerecordQuota = db.table('PersonPrerecordQuota')
    if QtGui.qApp.isNeedAddComent():
        quotaTypeCode = 'external'
        quotaName = u'Внешняя'
    elif personId == QtGui.qApp.getDrId():
        quotaTypeCode = 'own'
        quotaName = u'Врачебная'
    elif QtGui.qApp.drOrUserSpecialityId():
        quotaTypeCode = 'consultancy'
        quotaName = u'Консультационная'
    else:
        quotaTypeCode = 'primary'
        quotaName = u'Первичная'

    #Если код квоты задан как LIKE-шаблон группы кодов с общим префиксом
    if quotaTypeCode[-1] == '%':
        tablePrerecordQuotaType = db.table('rbPrerecordQuotaType')
        quotaTypeIdList = db.getIdList(tablePrerecordQuotaType, 'id', where=tablePrerecordQuotaType['code'].like(quotaTypeCode))
        recordList = db.getRecordList(tablePersonPrerecordQuota, ['value'], where=[tablePersonPrerecordQuota['person_id'].eq(personId),
                                                                                   tablePersonPrerecordQuota['quotaType_id'].inlist(quotaTypeIdList)])
        quota = 0
        for record in recordList:
            quota += forceInt(record.value(0)) if record else 0
    else:
        quotaTypeId = db.translate('rbPrerecordQuotaType', 'code', quotaTypeCode, 'id')
        record = db.getRecordEx(tablePersonPrerecordQuota, ['value'], where=[tablePersonPrerecordQuota['person_id'].eq(personId),
                                                                             tablePersonPrerecordQuota['quotaType_id'].eq(quotaTypeId)])
        quota = forceInt(record.value(0)) if record else 0
    return math.ceil(quota * count / 100.0), quotaName


class CActivityTreeItem(CTreeItemWithId):
    def __init__(self, parent, name, itemId):
        CTreeItemWithId.__init__(self, parent, name, itemId)

    def loadChildren(self):
        return []


class CActivityRootTreeItem(CActivityTreeItem):
    def __init__(self, orgId=None, orgStructureId=None):
        self.orgId = orgId
        self.orgStructureId = orgStructureId
        CActivityTreeItem.__init__(self, None, u'-', None)

    def loadChildren(self):
        items = []
        db = QtGui.qApp.db
        tableRBActivity = db.table('rbActivity')
        tablePerson = db.table('Person')
        tablePersonActivity = db.table('Person_Activity')
        cond = []
        table = tablePerson
        table = table.innerJoin(tablePersonActivity, tablePerson['id'].eq(tablePersonActivity['master_id']))
        table = table.innerJoin(tableRBActivity, tablePersonActivity['activity_id'].eq(tableRBActivity['id']))
        if self.orgId:
            cond.append(tablePerson['org_id'].eq(self.orgId))
        if self.orgStructureId:
            personIdList = getOrgStructurePersonIdList(self.orgStructureId)
            cond.append(tablePerson['id'].inlist(personIdList))
        order = [tableRBActivity['code'], tableRBActivity['name']]
        group = [tableRBActivity['code']]
        query = db.query(db.selectStmt(table, [tableRBActivity['id'], tableRBActivity['code'], tableRBActivity['name']], where=cond, order=order, group=group))
        while query.next():
            record = query.record()
            itemId = forceInt(record.value('id'))
            name = forceString(record.value('name'))
            items.append(CActivityTreeItem(self, name, itemId))
        return items


class CActivityModel(CTreeModel):
    def __init__(self, parent=None, orgId=None, orgStructureId=None):
        self.orgId = orgId
        self.orgStructureId = orgStructureId
        CTreeModel.__init__(self, parent, CActivityRootTreeItem(self.orgId, self.orgStructureId))
        self.rootItemVisible = False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(u'Виды деятельности')
        return QtCore.QVariant()

    def setOrgId(self, orgId=None, orgStructureId=None):
        if ( self.orgId != orgId
             or self.orgStructureId != orgStructureId
           ):
            self.orgId = orgId
            self.orgStructureId = orgStructureId
            if self._rootItem:
                self._rootItem = CActivityRootTreeItem(self.orgId, self.orgStructureId)
                self.reset()


class CResourcesPersonnelModelMixin(object):
    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        if role != QtCore.Qt.DisplayRole:
            if role == QtCore.Qt.ToolTipRole:
                personIdList = self.getItemIdList(index)
                if personIdList and len(personIdList) == 1:
                    text = self.getPersonInfo(personIdList[0])
                    return QtCore.QVariant(text)
            else:
                return QtCore.QVariant()
        item = index.internalPointer()
        return item.data(index.column())

    @staticmethod
    def getPersonInfo(personId):
        academicDegree = [u'неопределено', u'к.м.н', u'д.м.н']
        namePerson = u''
        if personId:
            db = QtGui.qApp.db
            table = db.table('Person')
            tablePersonWithSpeciality = db.table('vrbPersonWithSpeciality')
            tableOrgStructure = db.table('OrgStructure')
            record = db.getRecordEx(tablePersonWithSpeciality, '*', [tablePersonWithSpeciality['id'].eq(personId)])
            if record:
                namePerson = forceString(record.value('name'))
                orgStructureId = forceRef(record.value('orgStructure_id'))
                recordOS = db.getRecordEx(tableOrgStructure, 'name', [tableOrgStructure['id'].eq(orgStructureId), tableOrgStructure['deleted'].eq(0)])
                if recordOS:
                    namePerson += u', подразделение: ' + forceString(recordOS.value('name'))
            recordPerson = db.getRecordEx(table, '*', [table['id'].eq(personId), table['deleted'].eq(0)])
            if recordPerson:
                postId = forceRef(recordPerson.value('post_id'))
                namePerson += u', должность: ' + forceString(db.translate('rbPost', 'id', postId, 'name'))
                namePerson += u', ученая степень: ' + academicDegree[forceInt(recordPerson.value('academicDegree'))]
        return namePerson


class CFlatResourcesPersonnelModel(CResourcesPersonnelModelMixin, CFlatOrgPersonnelModel):
    pass


class CResourcesPersonnelModel(CResourcesPersonnelModelMixin, COrgPersonnelModel):
    pass


class CQueueItemInfo(CInfo):
    """
        Информация о записи пациента на прием к врачу.
    """

    def __init__(self, context, queueTime, clientId, checked, complaints, setPersonId):
        CInfo.__init__(self, context)
        self.setOkLoaded()
        self._clientId = clientId
        self._time = CTimeInfo(queueTime)
        self._client = self.getInstance(CClientInfo, clientId)
        self._checked = checked
        self._complaints = complaints
        self._setPerson = self.getInstance(CPersonInfo, setPersonId)

    time = property(lambda self: self._time,
                    doc=u"""
                        Время записи.
                        :rtype: CTimeInfo
                    """)
    client = property(lambda self: self._client,
                      doc=u"""
                        Записанный пациент.
                        :rtype: CClientInfo
                      """)
    checked = property(lambda self: self._checked,
                       doc=u"""
                            Флаг "начато" у записи.
                            :rtype: bool
                       """)
    complaints = property(lambda self: self._complaints,
                          doc=u"""
                            Примечания
                            :rtype: unicode
                          """)
    setPerson = property(lambda self: self._setPerson,
                         doc=u"""
                            Записавший врач.
                            :rtype: CPersonInfo
                         """)

    def __nonzero__(self):
        return self._clientId is not None
