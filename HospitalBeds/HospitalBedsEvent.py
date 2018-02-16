# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.EditDispatcher  import getEventFormClass

from library.DialogBase     import CDialogBase
from library.Utils          import forceDate, forceInt, forceRef, forceString, toVariant

from Ui_HospitalBedsEvent import  Ui_dialogHospitalBedsEvent


class CHospitalBedsEventDialog(CDialogBase, Ui_dialogHospitalBedsEvent):
    def __init__(self, parent, hospitalBedId = None):
        CDialogBase.__init__(self, parent)
        self.addModels('HospitalBedEvent', CHospitalBedsEventModel(self, hospitalBedId))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setModels(self.tblHospitalBedEvent,  self.modelHospitalBedEvent, self.selectionModelHospitalBedEvent)
        self.hospitalBedId = hospitalBedId
        self.modelHospitalBedEvent.loadData()

    def selectItem(self):
        return self.exec_()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblHospitalBedEvent_doubleClicked(self, index):
        row = index.row()
        if row >= 0:
            event_id = self.modelHospitalBedEvent.items[row][8]
        if event_id:
            self.editEvent(event_id)

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.close()

    def editEvent(self, eventId):
        formClass = getEventFormClass(eventId)
        dialog = formClass(self)
        dialog.load(eventId)
        return dialog.exec_()


class CHospitalBedsEventModel(QtCore.QAbstractTableModel):
    column = [u'Номер', u'ФИО', u'Пол', u'Дата рождения', u'Назначен', u'Выполнен', u'Тип', u'Врач']
    sex = [u'', u'М', u'Ж']

    def __init__(self, parent, hospitalBedId = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.hospitalBedId = hospitalBedId
        self.items = []


    def columnCount(self, index = QtCore.QModelIndex()):
        return 8


    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self.items)


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.column[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            return toVariant(item[column])
        return QtCore.QVariant()


    def loadData(self):
        self.items = []
        db = QtGui.qApp.db
        tableAPHB = db.table('ActionProperty_HospitalBed')
        tableAP = db.table('ActionProperty')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableEventType = db.table('EventType')
        tablePersonWithSpeciality = db.table('vrbPersonWithSpeciality')
        queryTable = tableAPHB.leftJoin(tableAP, tableAPHB['id'].eq(tableAP['id']))
        queryTable = queryTable.leftJoin(tableAction, tableAction['id'].eq(tableAP['action_id']))
        queryTable = queryTable.leftJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
        queryTable = queryTable.leftJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        queryTable = queryTable.leftJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        queryTable = queryTable.leftJoin(tablePersonWithSpeciality, tableEvent['execPerson_id'].eq(tablePersonWithSpeciality['id']))
        cols = [tableEvent['id'].alias('eventId'),
                tableEvent['client_id'],
                tableClient['lastName'],
                tableClient['firstName'],
                tableClient['patrName'],
                tableClient['sex'],
                tableClient['birthDate'],
                tableEvent['setDate'],
                tableEvent['execDate'],
                tablePersonWithSpeciality['name'],
                tableEventType['name'].alias('eventType')
               ]
        cond = [ tableAPHB['value'].eq(self.hospitalBedId),
                 tableAction['deleted'].eq(0),
                 tableAction['status'].inlist([0, 1]),
                 tableEvent['deleted'].eq(0),
               ]
        records = db.getRecordList(queryTable, cols, cond)
        for record in records:
            clientId = forceRef(record.value('client_id'))
            sexClient = self.sex[forceInt(record.value('sex'))]
            item = [clientId,
                    forceString(record.value('lastName')) + u' ' + forceString(record.value('firstName')) + u' ' + forceString(record.value('patrName')),
                    sexClient,
                    forceDate(record.value('birthDate')),
                    forceDate(record.value('setDate')),
                    forceDate(record.value('execDate')),
                    forceString(record.value('eventType')),
                    forceString(record.value('name')),
                    forceRef(record.value('eventId'))
                   ]
            self.items.append(item)
        self.reset()