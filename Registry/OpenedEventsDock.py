# -*- coding: utf-8 -*-

import sip
from PyQt4 import QtCore, QtGui

from Events.CreateEvent       import editEvent
from library.DialogBase       import CConstructHelperMixin
from library.DockWidget       import CDockWidget
from library.PreferencesMixin import CContainerPreferencesMixin
from library.RecordLock       import CRecordLockMixin
from library.TableModel       import CTableModel,  CCol,  CDateCol, CRefBookCol
from library.Utils            import forceRef, forceString, toVariant, formatName, formatSex
from Registry.ClientEditDialog import CClientEditDialog
from Registry.Utils           import CCheckNetMixin
from Users.Rights              import *
from Ui_OpenedEventsDock      import Ui_Form


class COpenedEventsDockWidget(CDockWidget):
    def __init__(self, parent):
        CDockWidget.__init__(self, parent)
        self.setWindowTitle(u'Открытые обращения')
        self.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.content = None
        self.contentPreferences = {}
        self.connect(QtGui.qApp, QtCore.SIGNAL('dbConnectionChanged(bool)'), self.onConnectionChanged)


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
        self.content = COpenedEventsDockContent(self)
        self.content.loadPreferences(self.contentPreferences)
        self.setWidget(self.content)


    def onDBDisconnected(self):
        self.setWidget(None)
        if self.content:
            #self.updateContentPreferences()
            self.content.setParent(None)
            sip.delete(self.content)
        self.content = QtGui.QLabel(u'необходимо\nподключение\nк базе данных', self)
        self.content.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.content.setDisabled(True)
        self.setWidget(self.content)


class COpenedEventsDockContent(QtGui.QWidget, Ui_Form, CConstructHelperMixin, CContainerPreferencesMixin, CCheckNetMixin, CRecordLockMixin):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        CCheckNetMixin.__init__(self)
        CRecordLockMixin.__init__(self)

        self.addModels('Events',  COpenedEventsTableModel(self, QtGui.qApp.currentOrgId()))

        self.setupUi(self)

        self.updateList()
        self.setModels(self.tblEvents, self.modelEvents, self.selectionModelEvents)

        #self.onCurrentUserIdChanged()

        self.actFindClient = QtGui.QAction(u'Перейти в картотеку', self)

        self.actFindClient.setObjectName('actFindClient')
        self.actCreateEvent = QtGui.QAction(u'Новое обращение', self)
        self.actCreateEvent.setObjectName('actCreateEvent')
        self.actOpenClientCard = QtGui.QAction(u'Открыть амб. карту', self)
        self.actOpenClientCard.setObjectName('actOpenClientCard')
        self.tblEvents.createPopupMenu([self.actFindClient,
                                        self.actCreateEvent,
                                        self.actOpenClientCard])
        self.connect(self.tblEvents.popupMenu(), QtCore.SIGNAL('aboutToShow()'), self.popupMenuAboutToShow)
        self.connect(self.actFindClient, QtCore.SIGNAL('triggered()'), self.onActFindClient)
        self.connect(self.actCreateEvent, QtCore.SIGNAL('triggered()'), self.onActCreateEvent)
        self.connect(self.actOpenClientCard, QtCore.SIGNAL('triggered()'), self.onActOpenClientCard)

        self.connect(QtGui.qApp, QtCore.SIGNAL('currentOrgIdChanged()'), self.onCurrentOrgIdChanged)
        self.connect(QtGui.qApp, QtCore.SIGNAL('currentUserIdChanged()'), self.onCurrentUserIdChanged)

    def sizeHint(self):
        return QtCore.QSize(10, 10)

    def updateList(self):
        person = QtGui.qApp.userId
        if person:
            self.modelEvents.setIdList(QtGui.qApp.db.getIdList('Event', where = 'execDate IS NULL AND execPerson_id=%s and deleted = 0' % person ))

    def onCurrentOrgIdChanged(self):
        self.updateList()

    def onCurrentUserIdChanged(self):
        self.updateList()

    def getCurrentQueuedClientId(self):
        row = self.tblEvents.currentIndex().row()
        if row >= 0:
            return forceRef(self.tblEvents.model().getRecordByRow(row).value('client_id'))
        return None

    def popupMenuAboutToShow(self):
        clientId = self.getCurrentQueuedClientId()
        self.actFindClient.setEnabled(bool(clientId) and QtGui.qApp.canFindClient())
        self.actCreateEvent.setEnabled(bool(clientId) and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteEvents]))
        self.actOpenClientCard.setEnabled(bool(clientId) and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]))

    @QtCore.pyqtSlot()
    def onActFindClient(self):
        clientId = self.getCurrentQueuedClientId()
        QtGui.qApp.findClient(clientId)

    @QtCore.pyqtSlot()
    def onActCreateEvent(self):
        clientId = self.getCurrentQueuedClientId()
        QtGui.qApp.requestNewEvent(clientId)

    @QtCore.pyqtSlot()
    def onActOpenClientCard(self):
        clientId = self.getCurrentQueuedClientId()
        if clientId:
            dialog = CClientEditDialog(self)
            dialog.load(clientId)
            dialog.exec_()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblEvents_doubleClicked(self, index):
        if index.isValid():
            row = index.row()
            column = index.column()
            model = self.tblEvents.model()
            eventId = forceRef(model.getRecordByRow(row).value('id'))
            if eventId and not eventId in QtGui.qApp.openedEvents:
                editEvent(self, eventId)


# ######################################################################

class COpenedEventsTableModel(CTableModel):
    class CLocClientColumn(CCol):
        def __init__(self, title, fields, defaultWidth):
            CCol.__init__(self, title, fields, defaultWidth, 'l')

        def format(self, values):
            val = values[0]
            clientId  = forceRef(val)
            clientRecord = QtGui.qApp.db.getRecord('Client', '*',  clientId)
            if clientRecord:
                name  = formatName(clientRecord.value('lastName'),
                                   clientRecord.value('firstName'),
                                   clientRecord.value('patrName'))
                return toVariant(name)
            return CCol.invalid


    class CLocClientBirthDateColumn(CCol):
        def __init__(self, title, fields, defaultWidth):
            CCol.__init__(self, title, fields, defaultWidth, 'l')

        def format(self, values):
            val = values[0]
            clientId  = forceRef(val)
            clientRecord = QtGui.qApp.db.getRecord('Client', '*', clientId)
            if clientRecord:
                return toVariant(forceString(clientRecord.value('birthDate')))
            return CCol.invalid


    class CLocClientSexColumn(CCol):
        def __init__(self, title, fields, defaultWidth):
            CCol.__init__(self, title, fields, defaultWidth, 'l')

        def format(self, values):
            val = values[0]
            clientId  = forceRef(val)
            clientRecord = QtGui.qApp.db.getRecord('Client', '*',  clientId)
            if clientRecord:
                return toVariant(formatSex(clientRecord.value('sex')))
            return CCol.invalid


    def __init__(self, parent, clientCache):
        CTableModel.__init__(self, parent)
        clientCol   = COpenedEventsTableModel.CLocClientColumn( u'Ф.И.О.', ['client_id'], 60)
        clientBirthDateCol = COpenedEventsTableModel.CLocClientBirthDateColumn(u'Дата рожд.', ['client_id'], 20)
        clientSexCol = COpenedEventsTableModel.CLocClientSexColumn(u'Пол', ['client_id'], 5)
        self.addColumn(clientCol)
        self.addColumn(clientBirthDateCol)
        self.addColumn(clientSexCol)
        self.addColumn(CDateCol(u'Назначен', ['setDate'],  10))
        self.addColumn(CRefBookCol(u'Тип',  ['eventType_id'], 'EventType', 15))
        self.loadField('createPerson_id')
        self.setTable('Event')

