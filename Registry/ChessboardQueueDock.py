# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import sip
from PyQt4 import QtCore, QtGui

from Events.Action import CActionTypeCache, CAction
from Events.CreateEvent import requestNewEvent
from Events.Utils import getEventType, getDeathDate
#
from Orgs.OrgStructComboBoxes import COrgStructureModel
from Orgs.Utils import getPersonInfo  # findOrgStructuresByAddress
#
from Registry.BeforeRecordClient import printOrder
from Registry.ComplaintsEditDialog import CComplaintsEditDialog
from Registry.ResourcesDock import createQueueEvent, getQuota
from Registry.Utils import getClientInfoEx, getClientAddressEx, getLocationCard, CCheckNetMixin
from Reports.ReportBase import createTable, CReportBase
from Reports.ReportView import CReportViewDialog
#
from Timeline.TimeTable import formatTimeRange
from Ui_ChessboardQueueDock import Ui_Form
#
from Users.Rights import urQueueToSelfDeletedTime, urQueueDeletedTime, \
    urQueueWithEmptyContacts
from Users.UserInfo import CUserInfo
from library.DialogBase import CConstructHelperMixin
from library.DockWidget import CDockWidget
from library.PreferencesMixin import CPreferencesMixin, CContainerPreferencesMixin
from library.RecordLock import CRecordLockMixin
from library.TableModel import CTableModel, CNameCol
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, forceTime, toVariant, \
    getPref, setPref, formatName, formatNum, pyDate, pyTime, calcAge, smartDict
#
from library.constants import atcAmbulance, atcTimeLine, etcTimeTable


#TODO: фильтр по дате
#TODO: выделение нового дня
#TODO: поиск участка

class CChessboardQueueDockWidget(CDockWidget):
    def __init__(self, parent):
        CDockWidget.__init__(self, parent)
        self.setWindowTitle(u'График (шахматка)')
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
        if self.isVisible(): # TODO: When invisible?
            self.content = CChessboardQueueDockContent(self)
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


class CChessboardQueueDockContent(QtGui.QWidget, Ui_Form, CConstructHelperMixin, CContainerPreferencesMixin, CCheckNetMixin, CRecordLockMixin):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        CCheckNetMixin.__init__(self)
        CRecordLockMixin.__init__(self)

        self.activityListIsShown = forceBool(QtGui.qApp.preferences.appPrefs.get('activityListIsShown', False))

        self.addModels('OrgStructure', COrgStructureModel(self, QtGui.qApp.currentOrgId()))
        self.addModels('ChessboardAmbQueue',     CChessboardQueueModel(self))
        #self.addModels('Personnel',       CChessboardPersonnelModel(self, tableName='vrbPerson'))

        self.actAmbCreateOrder = QtGui.QAction(u'Поставить в очередь', self)

        self.actAmbCreateOrder.setObjectName('actAmbCreateOrder')
        self.actAmbDeleteOrder = QtGui.QAction(u'Удалить из очереди', self)
        self.actAmbDeleteOrder.setObjectName('actAmbDeleteOrder')
        self.actChangeNotes =    QtGui.QAction(u'Изменить жалобы/примечания', self)
        self.actChangeNotes.setObjectName('actChangeNotes')
        self.actAmbPrintOrder =  QtGui.QAction(u'Напечатать направление', self)
        self.actAmbPrintOrder.setObjectName('actAmbPrintOrder')
        self.actAmbPrintQueue =  QtGui.QAction(u'Напечатать полный список', self)
        self.actAmbPrintQueue.setObjectName('actAmbPrintQueue')
        self.actAmbFindClient =  QtGui.QAction(u'Перейти в картотеку', self)
        self.actAmbFindClient.setObjectName('actAmbFindClient')
        self.actCreateEvent =    QtGui.QAction(u'Создать обращение', self)
        self.actCreateEvent.setObjectName('actCreateEvent')
        self.actAmbInfo =        QtGui.QAction(u'Свойства записи', self)
        self.actAmbInfo.setObjectName('actAmbInfo')


        self.timer = QtCore.QTimer(self)
        self.timer.setObjectName('timer')
        self.timer.setInterval(60*1000) # раз в минуту
        self.timerCountMinute = 0
        self.appLockIdList = []     # TODO: нужно ли?
        self.reservedRowList = []   # TODO: нужно ли?

        self.setupUi(self)
        for treeWidget in [self.treeOrgStructure]:
            treeWidget.setIndentation(12)
            treeWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        verticalHeader = self.tblChessboardAmbQueue.verticalHeader()
#        verticalHeader.show()
        verticalHeader.setResizeMode(QtGui.QHeaderView.Fixed)
        self.setModels(self.treeOrgStructure, self.modelOrgStructure, self.selectionModelOrgStructure)
        #self.setModels(self.treeOrgPersonnel, self.modelPersonnel, self.selectionModelPersonnel)
        self.setModels(self.tblChessboardAmbQueue,      self.modelChessboardAmbQueue,     self.selectionModelChessboardAmbQueue)
        self.treeOrgStructure.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.treeOrgStructure.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        #self.tb.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tblSpeciality.setTable('rbSpeciality')
        self.tblPersonnel.setTable('vrbPerson')
        self.modelSpeciality = self.tblSpeciality.model()
        self.selectionModelSpeciality = self.tblSpeciality.selectionModel()
        self.modelPersonnel = self.tblPersonnel.model()
        self.selectionModelPersonnel = self.tblPersonnel.selectionModel()
        self.connect(self.tblSpeciality.selectionModel(), QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'), self.on_selectionModelSpeciality_selectionChanged)
        self.connect(self.tblPersonnel.selectionModel(), QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'), self.on_selectionModelPersonnel_selectionChanged)

        self.tblChessboardAmbQueue.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        # TODO: изменить набор действий
        self.tblChessboardAmbQueue.createPopupMenu([self.actAmbCreateOrder,
                                                    self.actAmbDeleteOrder,
                                                    '-',
                                                    self.actChangeNotes,
                                                    '-',
                                                    self.actAmbPrintOrder,
                                                    '-',
                                                    self.actAmbFindClient,
                                                    self.actCreateEvent,
                                                    '-',
                                                    self.actAmbInfo,])
        # TODO: Review the following
        self.setDateRange()
        self.onCurrentUserIdChanged()

        # self.connect(self.treeOrgStructure.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuTreeOrgStructureAboutToShow)
        self.connect(self.tblChessboardAmbQueue.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAmbAboutToShow)

        self.headerTreeOS = self.treeOrgStructure.header()
        self.headerTreeOS.setClickable(True)


        self.connect(QtGui.qApp, QtCore.SIGNAL('currentOrgIdChanged()'), self.onCurrentOrgIdChanged)
        self.connect(QtGui.qApp, QtCore.SIGNAL('currentUserIdChanged()'), self.onCurrentUserIdChanged)
        self.activityListIsShown = False
        self.prevClientId = None
        self.prevComplaints = ''
        self.reservedRow = -1
        self.timer.start()
        self.edtEndDate.setDate(QtCore.QDate.currentDate().addMonths(1))
        self.tblChessboardAmbQueue.horizontalHeader().setStretchLastSection(False)
        self.tblChessboardAmbQueue.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)

    #
    # def sizeHint(self):
    #     return QtCore.QSize(10, 10)


    def onCurrentOrgIdChanged(self):
        self.modelOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.updatePersonnel()


    def onCurrentUserIdChanged(self):
        if QtGui.qApp.userOrgStructureId:
            index = self.modelOrgStructure.findItemId(QtGui.qApp.userOrgStructureId)
            if index and index.isValid():
                self.treeOrgStructure.setCurrentIndex(index)
        if QtGui.qApp.userSpecialityId and hasattr(self.tblPersonnel.model(), "findPersonId"):
            index = self.tblPersonnel.model().findPersonId(QtGui.qApp.getDrId())
            if index and index.isValid():
                self.tblPersonnel.setCurrentIndex(index)


    def setDateRange(self):
        today = QtCore.QDate.currentDate()
        self.edtBegDate.setDateRange(today, today.addYears(1))
        self.edtEndDate.setDateRange(today, today.addYears(1))


    def getPersonIdList(self):
        return self.tblPersonnel.values()


    def checkNetApplicable(self, personId, clientId, date):
        return self.checkClientAttach(personId, clientId, date, True) and \
              (self.checkClientAttendace(personId, clientId) or \
               self.confirmClientAttendace(self, personId, clientId)) and \
               self.confirmClientPolicyConstraint(self, clientId, date)

    def updateSpecialities(self):
        oldSelection = self.tblSpeciality.values()
        orgStructureIdList = []
        for treeIndex in self.selectionModelOrgStructure.selectedIndexes():
            orgStructureIdList.extend(self.modelOrgStructure.getItemIdList(treeIndex))
        begDate = self.edtBegDate.date()

        db = QtGui.qApp.db
        tablePerson = db.table('Person')
        tableSpeciality = db.table('rbSpeciality')
        cond = [tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()),
                tablePerson['speciality_id'].isNotNull(),
               ]
        if orgStructureIdList:
            cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
        if begDate:
            cond.append(db.joinOr([tablePerson['retireDate'].isNull(),
                                   tablePerson['retireDate'].dateGe(begDate)
                               ]))
        specialityIdList = db.getDistinctIdList(tablePerson, 'speciality_id', cond)
        self.tblSpeciality.setFilter(tableSpeciality['id'].inlist(specialityIdList))
        self.tblSpeciality.setValues(oldSelection)


    def updatePersonnel(self):
        oldSelection = self.tblPersonnel.values()
        orgStructureIdList = []
        for treeIndex in self.selectionModelOrgStructure.selectedIndexes():
            orgStructureIdList.extend(self.modelOrgStructure.getItemIdList(treeIndex))
        specialityIdList = self.tblSpeciality.values()
        begDate = self.edtBegDate.date()
        db = QtGui.qApp.db
        tablePerson = db.table('Person')
        tableVRBPerson = db.table('vrbPerson')
        cond = [tablePerson['org_id'].eq(QtGui.qApp.currentOrgId()),
               ]
        if orgStructureIdList:
            cond.append(tablePerson['orgStructure_id'].inlist(orgStructureIdList))
        if specialityIdList:
            cond.append(tablePerson['speciality_id'].inlist(specialityIdList))
        else:
            cond.append(tablePerson['speciality_id'].isNotNull())
        if begDate:
            cond.append(db.joinOr([tablePerson['retireDate'].isNull(),
                                   tablePerson['retireDate'].dateGe(begDate)
                               ]))
        personIdList = db.getDistinctIdList(tablePerson, 'id', cond)
        self.tblPersonnel.setFilter(tableVRBPerson['id'].inlist(personIdList))
        self.tblPersonnel.setValues(oldSelection)
        self.updateQueueTable()

    def updateQueueTable(self):
        #self.timer.stop()
        personIdList = self.getPersonIdList()
        begDate = self.edtBegDate.date()
        endDate = self.edtEndDate.date()
        self.modelChessboardAmbQueue.setPersonAndDate(personIdList, begDate, endDate)
        # self.tblChessboardAmbQueue.resizeColumnsToContents()
        return



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
        # Взято из FreeQueueDock в июле 2014. Возможно, устарело и не работает.
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
                                self.releaseLock()
                                return queueEventId
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


    def printQueue(self):#, №timeTableWidget, queueWidget, variantPrint, nameMenuPrintQueue = u''):
        # receptionInfo = self.getReceptionInfo(timeTableWidget)
        # personId = receptionInfo['personId']
        # Подготовка данных
        model = self.tblChessboardAmbQueue.model()
        personList = model.itemsByPerson.keys()
        personInfoMap = {}
        for personId in personList:
            personInfoMap[personId] = getPersonInfo(personId)
        db = QtGui.qApp.db
        tblClient = db.table('Client')
        cond = tblClient['id'].inlist(model.clientIdList)
        cols = [tblClient['id'].alias('clientId'),
                tblClient['lastName'],
                tblClient['firstName'],
                tblClient['patrName'],
                tblClient['birthDate'],
                tblClient['sex'],
                tblClient['SNILS'],
                'getClientPolicy(Client.id, 1) as policy',
                'getClientDocument(Client.id) as document',
                'getClientRegAddress(Client.id) as regAddress',
                'getClientLocAddress(Client.id) as locAddress',
                'getClientContacts(Client.id) as contacts'
                ]
        clientInfo = {}
        for record in db.getRecordList(tblClient, cols, cond):
            info = {}
            clientId = forceRef(record.value('clientId'))
            clientInfo[clientId] = info
            info['name'] = formatName(record.value('lastName'), record.value('firstName'), record.value('patrName'))
            info['sex'] = forceInt(record.value('sex'))
            info['birthDate'] = forceDate(record.value('birthDate'))
            info['age'] = calcAge(forceDate(record.value('birthDate')))
            info['SNILS'] = forceString(record.value('SNILS'))
            info['policy'] = forceString(record.value('policy'))
            info['document'] = forceString(record.value('document'))
            info['regAddress'] = forceString(record.value('regAddress'))
            info['locAddress'] = forceString(record.value('locAddress'))
            info['contacts'] = forceString(record.value('locAddress'))

        # Формирование отчета
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        # queueModel = queueWidget.model()
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(u'запись на амбулаторный приём')# + nameMenuPrintQueue)
        cols = [('5%',  [u'Врач'],       CReportBase.AlignLeft)
                ('5%',  [u'время'],      CReportBase.AlignRight),
                ('70%', [u'пациент'], CReportBase.AlignLeft),
                ('20%', [u'жалобы/примечания'],  CReportBase.AlignLeft),
               ]
        table = createTable(cursor, cols)
        for date in sorted(model.itemsByDate.keys()):
            dayInfo = model.itemsByDate[date]
            i = table.addRow()


#         # office = u'к. '+receptionInfo['office']
#         #
#         # cursor.insertBlock()
#         # cursor.setCharFormat(CReportBase.ReportTitle)
#         #
#         # cursor.insertText(personInfo['fullName'])
#         # cursor.insertBlock()
#         # cursor.setCharFormat(CReportBase.ReportSubTitle)
#         # cursor.insertText(personInfo['specialityName'])
#         # cursor.insertBlock()
#         # cursor.setCharFormat(CReportBase.ReportSubTitle)
#         cursor.insertText(forceString(receptionInfo['date']) +' '+receptionInfo['timeRange']+' '+office)
# #        complaintsRequired = queueModel.complaintsRequired()
#         cols = [('5%',  [u'№'],       CReportBase.AlignRight),
#                 ('5%',  [u'время'],   CReportBase.AlignRight),
#                 ('70%', [u'пациент'], CReportBase.AlignLeft),
#                 ('20%', [u'жалобы/примечания'],  CReportBase.AlignLeft),
#                ]

        table = createTable(cursor, cols)
        cnt = 0
        for row in xrange(queueModel.realRowCount()):
            if queueModel.getClientId(row):
                queueTime = queueModel.getTime(row)
                clientId   = queueModel.getClientId(row)
                if clientId:
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
                            cnt+=1
                            table.setText(i, 0, cnt)
                            table.setText(i, 1, locFormatTime(queueTime))
                            table.setText(i, 2, clientText)
                            table.setText(i, 3, queueModel.getComplaints(row))
                    else:
                        if variantPrint == 2:
                            clientInfo = getClientInfoEx(clientId, self.calendarWidget.selectedDate())
                            clientText = u'%(fullName)s, %(birthDate)s (%(age)s), %(sex)s, СНИЛС: %(SNILS)s\n' \
                                         u'документ %(document)s, полис %(policy)s\n' \
                                         u'адр.рег. %(regAddress)s\n' \
                                         u'адр.прож. %(locAddress)s\n' \
                                         u'%(phones)s' % clientInfo
                            i = table.addRow()
                            cnt+=1
                            table.setText(i, 0, cnt)
                            table.setText(i, 1, locFormatTime(queueTime))
                            table.setText(i, 2, clientText)
                            table.setText(i, 3, queueModel.getComplaints(row))
                            table.setText(i, 3, '\n' + u'A/карта: ' + getLocationCard(clientId)[0] if getLocationCard(clientId) else '')
        reportView = CReportViewDialog(self)
        reportView.setWindowTitle(u'Очередь')
        reportView.setText(doc)
        reportView.exec_()

    def releaseLock(self):
        for appLockId in self.appLockIdList:
            self._timerProlongLock.stop()
            db = QtGui.qApp.db
            query = db.query('CALL ReleaseAppLock(%d)' % (appLockId))
        self.appLockIdList = []
        self.reservedRowList = []
        self._appLockId = None
        self.reservedRow = -1
        self.timerCountMinute = 0


    @QtCore.pyqtSlot()
    def on_timer_timeout(self):
        if self.timerCountMinute > 2:
            self.releaseLock()
        else:
            self.timerCountMinute += 1
        self.setDateRange()
        if self.isVisible():
            self.modelChessboardAmbQueue.updateData()
            # self.tblChessboardAmbQueue.resizeColumnsToContents()


    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtBegDate_dateChanged(self, date):
        self.updateQueueTable()

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_edtEndDate_dateChanged(self, date):
        self.updateQueueTable()

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelOrgStructure_selectionChanged(self, current, previous):
        self.updateSpecialities()


    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelSpeciality_selectionChanged(self, current, previous):
        self.updatePersonnel()

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelPersonnel_selectionChanged(self, current, previous):
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
        canFindClient = QtGui.qApp.canFindClient()
        isBusy = self.tblChessboardAmbQueue.model().isBusy(self.tblChessboardAmbQueue.currentIndex())
        isValid = self.tblChessboardAmbQueue.model().isTimeValid(self.tblChessboardAmbQueue.currentIndex())
        currentClientId = QtGui.qApp.currentClientId()
        self.actAmbCreateOrder.setEnabled(bool(currentClientId) and not isBusy and isValid)
        self.actAmbPrintOrder.setEnabled(isBusy)
        self.actAmbFindClient.setEnabled(isBusy and canFindClient)
        self.actChangeNotes.setEnabled(isBusy)
        self.actAmbDeleteOrder.setEnabled(isBusy)
        self.actCreateEvent.setEnabled(isBusy)
        self.actAmbInfo.setEnabled(isBusy)

    @QtCore.pyqtSlot()
    def on_actAmbFindClient_triggered(self):
        index = self.tblChessboardAmbQueue.currentIndex()
        item = self.tblChessboardAmbQueue.model().getItemByIndex(index)
        if item:
            QtGui.qApp.findClient(item.clientId)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblChessboardAmbQueue_doubleClicked(self, index):
        self.ambCreateOrder(index, QtGui.qApp.currentClientId())

    @QtCore.pyqtSlot()
    def on_actAmbCreateOrder_triggered(self):
        index = self.tblChessboardAmbQueue.currentIndex()
        self.ambCreateOrder(index, QtGui.qApp.currentClientId())

    @QtCore.pyqtSlot()
    def on_actAmbDeleteOrder_triggered(self):
        self.ambDeleteOrder(self.tblChessboardAmbQueue.currentIndex())
        #self.deleteOrder(self.tblAmbTimeTable, self.tblAmbQueue)
        self.updateQueueTable()
        QtGui.qApp.emitCurrentClientInfoChanged()

    @QtCore.pyqtSlot()
    def on_actChangeNotes_triggered(self):
        index = self.tblChessboardAmbQueue.currentIndex()
        item = self.tblChessboardAmbQueue.model().getItemByIndex(index)

        actionId = item.actionId
        if actionId:
            db = QtGui.qApp.db
            table = db.table('Action')
            record = db.getRecord(table, 'id, note', actionId)
            dlg = CComplaintsEditDialog(self)
            dlg.setComplaints(forceString(record.value('note')))
            if dlg.exec_():
                record.setValue('note', QtCore.QVariant(dlg.getComplaints()))
                db.updateRecord(table, record)

    @QtCore.pyqtSlot()
    def on_actCreateEvent_triggered(self):
        index = self.tblChessboardAmbQueue.currentIndex()
        item = self.tblChessboardAmbQueue.model().getItemByIndex(index)
        clientId = item.clientId
        time = item.queueTime
        personId = item.personId
        specialityId = self.getPersonSpecialityId(personId)
        date = item.date
        if specialityId:
            requestNewEvent(self, clientId, False, None, [], None, QtCore.QDateTime(date, time if time else QtCore.QTime()), personId)
        else:
            QtGui.qApp.requestNewEvent(clientId)

    @QtCore.pyqtSlot()
    def on_actAmbInfo_triggered(self):
        index = self.tblChessboardAmbQueue.currentIndex()
        item = self.tblChessboardAmbQueue.model().getItemByIndex(index)

        db = QtGui.qApp.db
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Свойства записи')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)

        cursor.insertText(u'дата записи: %s\n' % item.date.toString('dd.MM.yyyy'))
        personId = item.personId
        if personId:
            personInfo = getPersonInfo(personId)
            orgStructure_id = forceInt(db.translate('Person', 'id', personId, 'orgStructure_id'))
            orgStructureName = forceString(db.translate('OrgStructure', 'id', orgStructure_id, 'name'))
            cursor.insertText(u'врач: %s, %s\n' % (personInfo['fullName'], personInfo['specialityName']))
            cursor.insertText(u'подразделение: %s, %s\n' % (orgStructureName, personInfo['postName']))

        date = item.date
        if item.actionId:
            clientId=item.clientId
            clientInfo = getClientInfoEx(clientId, date)
            cursor.insertText(u'пациент: %s\n' % clientInfo['fullName'])
            cursor.insertText(u'д/р: %s\n' % clientInfo['birthDate'])
            cursor.insertText(u'возраст: %s\n' % clientInfo['age'])
            cursor.insertText(u'пол: %s\n' % clientInfo['sex'])
            cursor.insertText(u'адрес: %s\n' % clientInfo['regAddress'])
            cursor.insertText(u'полис: %s\n' % clientInfo['policy'])
            cursor.insertText(u'паспорт: %s\n' % clientInfo['document'])
            cursor.insertText(u'СНИЛС: %s\n' % clientInfo['SNILS'])
            actionId = item.actionId
            tableAction = db.table('Action')
#            record = db.getRecord(tableAction, 'id, note', actionId)
            record = db.getRecord(tableAction, '*', actionId)
            note=forceString(record.value('note'))
            cursor.insertText(u'жалобы/примечания: %s\n' % note)
            cursor.insertText(u'запись на амбулаторный приём ')
            office = u'к. '+item.office
            cursor.insertText(forceString(date) +' '+formatTimeRange((item.begTime, item.endTime))+' '+office)

            cursor.movePosition(QtGui.QTextCursor.PreviousBlock,
                                      QtGui.QTextCursor.MoveAnchor,
                                      cursor.blockNumber()-1)
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

#            cursor.insertText(u': %s\n' % )

        cursor.insertBlock()
        reportView = CReportViewDialog(self)
        reportView.setWindowTitle(u'Свойства записи')
        reportView.setText(doc)
        reportView.exec_()

    @QtCore.pyqtSlot()
    def on_btnRefresh_clicked(self):
        self.updateQueueTable()

    def ambCreateOrder(self, index, clientId):
        # row = index.row()
        col = index.column()
        model = self.tblChessboardAmbQueue.model()
        if clientId and index.isValid() and col > 0: # Первый столбец - даты
            personId = model.getPersonIdByCol(col)
            item = model.getItemByIndex(index)

            date = item.date
            queueTime = item.queueTime
            self.updateQueueTable()
            temp = [x for _, x in model.items if x.date == date and x.queueTime == queueTime]
            if temp:
                item = temp[0]

                curIndex = item.index
                time  = item.queueTime
                office = item.office
                begTime = item.begTime
                endTime = item.endTime
                eventId = item.eventId
                date = item.date

                eventId = self.createOrder(eventId, date, curIndex, time, personId, office, clientId)
                if eventId:
                    printOrder(self, clientId, 0, date, office, personId, eventId, curIndex+1, time, unicode(formatTimeRange((begTime, endTime))))

        QtGui.qApp.emitCurrentClientInfoChanged()
        self.updateQueueTable()

    def ambDeleteOrder(self, index):
        model = self.tblChessboardAmbQueue.model()
        item = model.getItemByIndex(index)
        if item is None or item.isFree:
            return

        actionId = item.actionId
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        createPersonId = forceRef(db.translate(tableAction, 'id', actionId, 'createPerson_id'))
        setPersonId = forceRef(db.translate(tableAction, 'id', actionId, 'setPerson_id'))
        nurseOwnerId = QtGui.qApp.nurseOwnerId()
        #текущий пользователь - врач, назначивший услугу и имеющий право отменять свои назначения
        currentUserIsSetPerson = (setPersonId
                                  and setPersonId == QtGui.qApp.userId
                                  and QtGui.qApp.userHasRight(urQueueToSelfDeletedTime))
        #текущий пользователь - медсестра, и она работает с врачом, назначившим услугу и имеющим право отменять свои назначения, а так же она создала эту запись
        currentUserIsNurseOfSetPerson = (QtGui.qApp.isNurse()
                                         and setPersonId
                                         and setPersonId == nurseOwnerId #Назначено врачом, с которым работает медстестра
                                         and createPersonId == QtGui.qApp.userId #Создано текущей медсестрой
                                         and CUserInfo(nurseOwnerId).hasRight(urQueueToSelfDeletedTime))
        if (QtGui.qApp.userHasRight(urQueueDeletedTime)
            or currentUserIsSetPerson
            or currentUserIsNurseOfSetPerson
            ):
            confirmation = QtGui.QMessageBox.warning( self,
                u'Внимание!',
                u'Подтвердите удаление записи к врачу',
                QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
                QtGui.QMessageBox.Cancel)
            if confirmation != QtGui.QMessageBox.Ok:
                return

            # Нужна ли такая перестраховка?
            timeTableActionId = item.timetableActionId
            if self.lock('Action', timeTableActionId):
                try:
                    model.updateData()
                    item = model.getItemByIndex(index)
                    if item is not None and not item.isFree \
                        and timeTableActionId == item.timetableActionId and actionId == item.actionId:
                        try:
                            db.transaction()
                            table = db.table('Action')
                            record = db.getRecordEx(table, 'id, deleted, status', table['id'].eq(actionId))
                            record.setValue('deleted', QtCore.QVariant(1))
                            record.setValue('status', QtCore.QVariant(3))
                            db.updateRecord(table, record)

                            db.query('UPDATE ActionProperty_Action apa SET apa.value = NULL WHERE apa.index = %s AND apa.value = %s' % (item.index, item.actionId)).exec_()
                            #self.updateTimeTableRow(date, timeTableWidget, queue)
                            #self.emitDataChanged(row)
                            db.commit()
                        except:
                            db.rollback()
                            QtGui.qApp.logCurrentException()
                            raise
                finally:
                    self.releaseLock()

    @QtCore.pyqtSlot()
    def on_actAmbPrintOrder_triggered(self):
        index = self.tblChessboardAmbQueue.currentIndex()
        model = self.tblChessboardAmbQueue.model()
        personId = model.getPersonIdByCol(index.column())
        item = model.getItemByIndex(index)
        printOrder(self, item.clientId, 0, item.date, item.office, personId, item.queueEventId, item.index+1, item.queueTime, unicode(formatTimeRange((item.begTime, item.endTime))))

    @QtCore.pyqtSlot()
    def on_actAmbPrintQueue_triggered(self):
        item = self.tblChessboardAmbQueue.model().getItemByIndex(self.tblChessboardAmbQueue.currentIndex)
        timeRange = unicode(formatTimeRange((item.begTime, item.endTime)))
        personId = item.personId

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        queueModel = self.tblChessboardAmbQueue.model()
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(u'запись на амбулаторный приём')
        office = u'к. '+item.office
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportTitle)
        personInfo = getPersonInfo(personId)
        cursor.insertText(personInfo['fullName'])
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(personInfo['specialityName'])
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(forceString(item.date) +' '+timeRange+' '+office)
#        complaintsRequired = queueModel.complaintsRequired()
        cols = [('5%',  [u'№'],       CReportBase.AlignRight),
                ('5%',  [u'время'],   CReportBase.AlignRight),
                ('70%', [u'пациент'], CReportBase.AlignLeft),
                ('20%', [u'жалобы/примечания'],  CReportBase.AlignLeft),
               ]

        table = createTable(cursor, cols)
        cnt = 0
        #TODO: Доработать отсюда (queueModel изменилась по сравнению с оригинальным методом)
        for row in xrange(queueModel.realRowCount()):
            if queueModel.getClientId(row):
                queueTime = queueModel.getTime(row)
                clientId   = queueModel.getClientId(row)
                if clientId:
                    clientInfo = getClientInfoEx(clientId, item.date)
                    clientText = u'%(fullName)s, %(birthDate)s (%(age)s), %(sex)s, СНИЛС: %(SNILS)s\n' \
                                 u'документ %(document)s, полис %(policy)s\n' \
                                 u'адр.рег. %(regAddress)s\n' \
                                 u'адр.прож. %(locAddress)s\n' \
                                 u'%(phones)s' % clientInfo
                    i = table.addRow()
                    cnt+=1
                    table.setText(i, 0, cnt)
                    table.setText(i, 1, locFormatTime(queueTime))
                    table.setText(i, 2, clientText)
                    table.setText(i, 3, queueModel.getComplaints(row))
                    table.setText(i, 3, '\n' + u'A/карта: ' + getLocationCard(clientId)[0] if getLocationCard(clientId) else '')
        reportView = CReportViewDialog(self)
        reportView.setWindowTitle(u'Очередь')
        reportView.setText(doc)
        reportView.exec_()


    @QtCore.pyqtSlot(int)
    def on_modelChessboardAmbQueue_dataLoadDone(self, count):
        if count == 0:
            text = u'Список пуст'
        else:
            text = u'В списке '+formatNum(count, (u'номерок', u'номерка', u'номерков'))
        self.lblQueueItemsCount.setText(text)


class CChessboardPersonnelModel(CTableModel):
    def __init__(self, parent, cols, tableName):
        super(CChessboardQueueModel, self).__init__(parent, cols, tableName)
        self.addColumn(CNameCol(u'Врач', ['name'], 100))


class CChessboardQueueModel(QtCore.QAbstractTableModel):
    __pyqtSignals__ = ('beforeReset()',
                       'afterReset()',
                       'dataLoadDone(int)',
                      )

    headerText = [u'Дата', u'Время', u'Врач', u'Каб']

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.itemsByPerson = {}
        self.itemsByDate = {}
        self.personHeaders = []
        self.items = []
        self.clientIdList = [] # Список всех записанных клиентов, видимых в данной шахматке. Используется при построении отчетов.
        self.mapKeyToIndex = {}

        self.personIdList = []
        self.begDate = None

        self.etiTimeTable    = None
        self.atiAmb          = None # ati == ActionTypeId, atiAmb == ActionTypeId with code = 'amb'
        self.aptiAmbTimes    = None # apti == ActionPropertyTypeId, aptiAmbTimes == ActionPropertyTypeId with ActionType.code = 'amb' and ActionPropertyType.name = 'times'
        self.aptiAmbQueue    = None # like prev.
        self.aptiAmbColors   = None
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
        self.oddDates = set()

# ---------------- Override methods --------------------------
    def columnCount(self, index = None):
        return len(self.personHeaders) + 1


    def rowCount(self, index = None):
        return len(self.items)


    def flags(self, index):
        result = QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled
        return result


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.personHeaders[section-1][1] if section > 0 else u'Дата')
        return QtCore.QVariant()

    def rowSpanInfo(self):
        result = []
        for i, spanRow in enumerate(self.mergeDateRows):
            nextRow = self.mergeDateRows[i+1] if i < len(self.mergeDateRows) - 1 else self.rowCount()
            spanCount = nextRow - spanRow
            result.append((spanRow, spanCount))
        return result

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:

            row = index.row()
            if row<len(self.items):
                column = index.column()
                value = self.items[row][column]
                if column == 0:
                    return toVariant(value)
                else:
                    if value:
                        return toVariant(value.queueTime.toString('hh:mm') + u' (к. ' + value.office + ')')
                    else:
                        return toVariant(u'--:--')
        elif role == QtCore.Qt.BackgroundRole:
            row = index.row()
            if row<len(self.items):
                column = index.column()
                value = self.items[row][column]
                if value:
                    if column == 0:
                        return toVariant(QtGui.QColor(156, 156, 156) if value in self.oddDates else QtGui.QColor(255, 255, 255))
                    else:

                        if not value.actionId:
                            if value.color:
                                return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(value.color)))
                            return toVariant(QtGui.QColor(QtCore.Qt.green))
                        else:
                            return toVariant(QtGui.QColor(QtCore.Qt.red))
        elif role == QtCore.Qt.ToolTipRole:
            row = index.row()
            if row < len(self.items):
                column = index.column()
                value = self.items[row][column]
                if column > 0 and value:
                    if value.actionId:
                        tooltip = formatName(value.clientLastName, value.clientFirstName, value.clientPatrName)
                        year = value.clientBirthDate.year() if value.clientBirthDate.isValid() else 0
                        if year:
                            tooltip += u', %s г.р.' % year
                        contacts = value.clientContacts
                        if contacts:
                            tooltip += u'\nКонтакты: %s' % contacts
                        return QtCore.QVariant(tooltip)
        elif role == QtCore.Qt.TextAlignmentRole:
            if index.column() == 0:
                return QtCore.QVariant(QtCore.Qt.AlignTop)
            return QtCore.QVariant(QtCore.Qt.AlignCenter)
        return QtCore.QVariant()

# ------------------- End override methods --------------------------

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

    def getItemByIndex(self, index):
        if index.isValid():
            return self.items[index.row()][index.column()]
        return None

    def lookupRowByKey(self, key):
        lookupDate, lookupTime, lookupPerson = key
        for row, item in enumerate(self.items):
            date = forceDate(item.value(0))
            time = forceTime(item.value(1))
            person = forceString(item.value(2))
            if date>lookupDate or date==lookupDate and (time>lookupTime or lookupTime==time and person>=lookupPerson):
                return row
        return len(self.items)-1

    def getPersonIdByCol(self, col):
        if col <= len(self.personHeaders):
            return self.personHeaders[col-1][0]

    def setPersonAndDate(self, personIdList, begDate, endDate):
        if ( self.personIdList != personIdList
             or self.begDate != begDate or self.endDate != endDate):
            self.personIdList = personIdList
            self.begDate = begDate
            self.endDate = endDate
            self.loadData()
            self.transformData()
            self.reset()
        else:
            self.updateData()


    def loadData(self):
        """Получить данные из БД, преобразовать в удобные для последующей обработки объекты.


        """
        if self.atiAmb is None:
            try:
                self.etiTimeTable = getEventType(etcTimeTable).eventTypeId
                actionType = CActionTypeCache.getByCode(atcAmbulance)
                self.atiAmb = actionType.id
                self.aptiAmbTimes = actionType.getPropertyType('times').id
                self.aptiAmbQueue = actionType.getPropertyType('queue').id
                self.aptiAmbColors = actionType.getPropertyType('colors').id
                self.aptiAmbOffice = actionType.getPropertyType('office').id
                self.aptiAmbOffice1 = actionType.getPropertyType('office1').id
                self.aptiAmbOffice2 = actionType.getPropertyType('office2').id

                self.aptiAmbBegTime  = actionType.getPropertyType('begTime').id
                self.aptiAmbBegTime1 = actionType.getPropertyType('begTime1').id
                self.aptiAmbBegTime2 = actionType.getPropertyType('begTime2').id

                self.aptiAmbEndTime  = actionType.getPropertyType('endTime').id
                self.aptiAmbEndTime1 = actionType.getPropertyType('endTime1').id
                self.aptiAmbEndTime2 = actionType.getPropertyType('endTime2').id

                actionType = CActionTypeCache.getByCode(atcTimeLine)
                self.atiTimeLine = actionType.id
                self.aptiTimeLineReasonOfAbsence = actionType.getPropertyType('reasonOfAbsence').id
            except:
                QtGui.qApp.logCurrentException()

        self.itemsByPerson = {}
        self.itemsByDate   = {}
        self.clientIdList  = []

        if self.atiAmb and self.personIdList:
            db = QtGui.qApp.db
            now = QtCore.QDateTime.currentDateTime()
            currentDate = now.date()
            currentTime = now.time()

            stmt = u'SELECT Event.setDate   AS date,'\
                   u' APTimesValue.value    AS time,'\
                   u' vrbPersonWithSpeciality.name AS personName,'\
                   u' APQueueValue.value    AS queueId,' \
                   u' APColorsValue.value    AS color,' \
                   u' Client.id             AS clientId,' \
                   u' Client.lastName       AS clientLastName,' \
                   u' Client.firstName      AS clientFirstName,' \
                   u' Client.patrName       AS clientPatrName,' \
                   u' Client.birthDate      AS clientBirthDate,'\
                   u' getClientContacts(Client.id) AS clientContacts,'\
                   u' APTimesValue.id       AS actionProperty_id,'\
                   u' APTimesValue.index    AS actionPropertyIndex,'\
                   u' APOfficeValue.value   AS office,'\
                   u' APBegTimeValue.value  AS begTime,'\
                   u' APEndTimeValue.value  AS endTime,'\
                   u' APOffice1Value.value  AS office1,'\
                   u' APBegTime1Value.value AS begTime1,'\
                   u' APEndTime1Value.value AS endTime1,'\
                   u' APOffice2Value.value  AS office2,'\
                   u' APBegTime2Value.value AS begTime2,'\
                   u' APEndTime2Value.value AS endTime2,'\
                   u' Event.id AS event_id, Event.setPerson_id AS person_id, ' \
                   u' Action.id AS timetableAction_id, ' \
                   u' APTimesValue.`index` AS `index`, ' \
                   u' QueueEvent.id AS queueEventId, ' \
                   u' QueueAction.note AS queueNote'\
                   u' FROM Action'\
                   u' LEFT JOIN Event ON Event.id = Action.event_id'\
                   u' LEFT JOIN Person ON Person.id = Event.setPerson_id'\
                   u' LEFT JOIN vrbPersonWithSpeciality ON vrbPersonWithSpeciality.id = Event.setPerson_id'\
                   u' LEFT JOIN ActionProperty        AS APTimes         ON APTimes.action_id = Action.id AND APTimes.type_id = %(aptiAmbTimes)d'\
                   u' LEFT JOIN ActionProperty_Time   AS APTimesValue    ON APTimesValue.id = APTimes.id'\
                   u' LEFT JOIN ActionProperty        AS APQueue         ON APQueue.action_id = Action.id AND APQueue.type_id = %(aptiAmbQueue)d'\
                   u' LEFT JOIN ActionProperty_Action AS APQueueValue    ON APQueueValue.id = APQueue.id AND APTimesValue.`index` = APQueueValue.`index`'\
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
                   u' LEFT JOIN ActionProperty        AS APColors        ON APColors.action_id = Action.id AND APColors.type_id = %(aptiAmbColors)d' \
                   u' LEFT JOIN ActionProperty_String AS APColorsValue   ON APColorsValue.id = APColors.id AND APColorsValue.`index` = APQueueValue.`index`' \
                   u' LEFT JOIN Action                AS QueueAction     ON QueueAction.id = APQueueValue.value' \
                   u' LEFT JOIN Event                 AS QueueEvent      ON QueueEvent.id = QueueAction.event_id' \
                   u' LEFT JOIN Client                AS Client          ON Client.id = QueueEvent.client_id' \
                   u' WHERE Action.deleted=0 AND Event.deleted=0 AND Event.eventType_id=%(eventTypeId)d AND (TimeLineAction.id IS NULL OR TimeLineAction.deleted=0)'\
                   u' AND Action.actionType_id = %(atiAmb)d'\
                   u' AND Event.setDate>=%(begDate)s'\
                   u' AND Event.setDate<=%(endDate)s'\
                   u' AND Event.setPerson_id IN (%(personIdList)s)'\
                   u'\n-- AND APQueueValue.value IS NULL\n'\
                   u' AND APTimesValue.value IS NOT NULL'\
                   u' AND APROAValue.value IS NULL'\
                   u' AND (Event.setDate>%(currentDate)s OR APTimesValue.value>%(currentTime)s)'\
                   u' AND (Person.lastAccessibleTimelineDate IS NULL OR Person.lastAccessibleTimelineDate = \'0000-00-00\' OR DATE(Event.setDate)<=Person.lastAccessibleTimelineDate)' \
                   u' ORDER BY Event.setDate, time, vrbPersonWithSpeciality.name, Event.setPerson_id'\
                   u' LIMIT 0, 50000' % {
                        'eventTypeId'    : self.etiTimeTable,
                        'aptiAmbTimes'   : self.aptiAmbTimes,
                        'aptiAmbQueue'   : self.aptiAmbQueue,
                        'aptiAmbColors'  : self.aptiAmbColors,
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
                        'endDate'        : db.formatDate(self.endDate if self.endDate else currentDate),
                        'personIdList'   : ', '.join([str(id) for id in self.personIdList]) if self.personIdList else 'NULL',
                        'currentDate'    : db.formatDate(currentDate),
                        'currentTime'    : db.formatTime(currentTime)
                    }
            query = db.query(stmt)
            self.oddDates = set()
            prevDate = None
            isNextDateOdd = False
            while query.next():
                record = query.record()

                personId = forceRef(record.value('person_id'))
                personName = forceString(record.value('personName'))
                date = forceDate(record.value('date'))
                time = forceTime(record.value('time'))
                queueId = forceRef(record.value('queueId'))

                personTimetable = self.itemsByPerson.setdefault((personId, personName), {})
                personDayTimetable = personTimetable.setdefault(pyDate(date), {})
                dayTimetable = self.itemsByDate.setdefault(pyDate(date), {})
                orderInfo = smartDict()
                orderInfo.isFree = True if queueId is None else False
                orderInfo.actionId = queueId
                orderInfo.color = forceString(record.value('color'))
                orderInfo.queueEventId = forceRef(record.value('queueEventId'))
                orderInfo.eventId = forceRef(record.value('event_id'))
                orderInfo.timetableActionId = forceRef(record.value('timetableAction_id'))
                orderInfo.begTime = forceTime(record.value('begTime'))
                orderInfo.endTime = forceTime(record.value('endTime'))
                orderInfo.office  = forceString(record.value('office'))
                orderInfo.date    = date
                orderInfo.queueTime = time
                orderInfo.clientId = forceRef(record.value('clientId'))
                orderInfo.clientLastName = forceString(record.value('clientLastName'))
                orderInfo.clientFirstName = forceString(record.value('clientFirstName'))
                orderInfo.clientPatrName = forceString(record.value('clientPatrName'))
                orderInfo.clientBirthDate = forceDate(record.value('clientBirthDate'))
                orderInfo.clientContacts = forceString(record.value('clientContacts'))
                orderInfo.index = forceInt(record.value('index'))
                orderInfo.note = forceString(record.value('queueNote'))
                orderInfo.personId = personId
                if orderInfo.clientId:
                    self.clientIdList.append(orderInfo.clientId)


                personDayTimetable[pyTime(time)] = orderInfo
                orderInfo2 = orderInfo.copy()
                orderInfo2.personName = personName
                timeInfo = dayTimetable.setdefault(pyTime(time), [])
                timeInfo.append(orderInfo2)

                if prevDate is None:
                    prevDate = date
                elif prevDate != date:
                    prevDate = date
                    if not isNextDateOdd: # current is odd
                        self.oddDates.add(pyDate(date))
                    isNextDateOdd = not isNextDateOdd
        #self.emit(QtCore.SIGNAL('dataLoadDone(int)'), len(self.items))

    def transformData(self):
        """Преобразовать данные из БД, сгруппированные по врачу-дате-времени в удобную для представления форму. Рассчитать


        """
        self.personHeaders = sorted(self.itemsByPerson.keys(), key=lambda x: x[1])
        self.items = []
        self.mergeDateRows = []
        currentItemNum = 0
        for day in sorted(self.itemsByDate.keys()):
            dayInfo = self.itemsByDate[day]
            # self.mergeDateRows.append(currentItemNum)
            prevTime = None
            for time in sorted(dayInfo.keys()):
                rowData = [None] * (len(self.personHeaders) + 1)

                if prevTime is None or prevTime.hour != time.hour:
                    self.mergeDateRows.append(currentItemNum)
                    rowData[0] = day
                    prevTime = time

                timeInfo = dayInfo[time]
                for orderInfo in timeInfo:
                    key = filter(lambda x: x[1] == orderInfo.personName, self.personHeaders)
                    if key:
                        key = key[0]
                        rowData[self.personHeaders.index(key)+1] = orderInfo

                currentItemNum += 1
                self.items.append(rowData)




    def updateData(self):
        self.emit(QtCore.SIGNAL('beforeReset()'))
        self.loadData()
        self.transformData()
        self.reset()
        self.emit(QtCore.SIGNAL('afterReset()'))

    def isBusy(self, index):
        item = self.getItemByIndex(index)
        if item and item.actionId:
            return True
        return False

    def isTimeValid(self, index):
        item = self.getItemByIndex(index)
        if item and item.queueTime:
            return True
        return False

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


if __name__=='__main__':
    import sys
    from library.TreeView import CTreeView
    from library.TreeModel import CTreeModel, CTreeItem
    qApp = QtGui.QApplication(sys.argv)
    dialog = QtGui.QDialog()
    layout = QtGui.QGridLayout()
    dialog.setLayout(layout)
    tree = CTreeView(dialog)
    #tree.setHeaderLabel('Testme')
    tree.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
    root = CTreeItem(None, 'Root item')
    child1 = CTreeItem(root, 'child 1')
    child2 = CTreeItem(root, 'child 2')
    treeModel = CTreeModel(None, root)

    tree.setModel(treeModel)
    layout.addWidget(tree)

    dialog.exec_()