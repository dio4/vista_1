# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.TableModel import CCol
from library.Utils      import forceDate, forceDateTime, forceRef, forceString, toVariant

from Registry.Utils     import getClientBanner

from Ui_VisitBeforeRecordClient import Ui_VisitBeforeRecordClient


class CVisitByQueue(CDialogBase, Ui_VisitBeforeRecordClient):
    def __init__(self,  parent, clientId = None, orgStructureId = None, specialityId = None, personId = None):
        CDialogBase.__init__(self, parent)
        self.addModels('VisitByQueueTable', CVisitByQueueTable(self))
        self.setupUi(self)
        self.clientId = clientId
        self.setup(orgStructureId, specialityId, personId)
        self.setModels(self.tblVisitByQueue, self.modelVisitByQueueTable, self.selectionModelVisitByQueueTable)


    def setup(self, orgStructureId = None, specialityId = None, personId = None):
        currentDate = forceDate(QtCore.QDate.currentDate())
        beginDate = QtCore.QDate(currentDate.year(), 1, 1)
        self.edtBeginDateVisitBeforeRecordClient.setDate(beginDate)
        self.edtEndDateVisitBeforeRecordClient.setDate(currentDate.addDays(- 1))
        if orgStructureId:
            self.cmbOrgStructureVisitBeforeRecordClient.setValue(orgStructureId)
        else:
            self.cmbOrgStructureVisitBeforeRecordClient.setValue(0)
        self.cmbSpecialityVisitBeforeRecordClient.setTable('rbSpeciality', order='name')
        if specialityId:
            self.cmbSpecialityVisitBeforeRecordClient.setValue(specialityId)
        else:
            self.cmbSpecialityVisitBeforeRecordClient.setValue(0)
        if personId:
            self.cmbPersonVisitBeforeRecordClient.setValue(personId)
        else:
            self.cmbPersonVisitBeforeRecordClient.setValue(0)
        if self.clientId:
            self.txtVisitBeforeRecordClient.setHtml(getClientBanner(self.clientId))
        else:
            self.txtVisitBeforeRecordClient.setText('')


    @QtCore.pyqtSlot()
    def on_btnCreateVisitBeforeRecordClient_clicked(self):
        if self.clientId:
            beginDate = forceDateTime(self.edtBeginDateVisitBeforeRecordClient.date())
            endDate = forceDateTime(self.edtEndDateVisitBeforeRecordClient.date())
            orgStructureId = self.cmbOrgStructureVisitBeforeRecordClient.value()
            specialityId = self.cmbSpecialityVisitBeforeRecordClient.getValue()
            personId = self.cmbPersonVisitBeforeRecordClient.getValue()
            self.modelVisitByQueueTable.loadData(self.chkNoVisitBeforeRecordClient.isChecked(), self.clientId, beginDate, endDate, orgStructureId, specialityId, personId)


    @QtCore.pyqtSlot()
    def on_btnPrintVisitBeforeRecordClient_clicked(self):
        if self.clientId and self.modelVisitByQueueTable.rowCount() > 0:
            self.tblVisitByQueue.setReportHeader(u'Протокол обращений пациента по предварительной записи')
            self.tblVisitByQueue.setReportDescription(getClientBanner(self.clientId))
            dataRoles = [QtCore.Qt.DisplayRole]*(self.tblVisitByQueue.model().columnCount())
            self.tblVisitByQueue.printContent(dataRoles)


    @QtCore.pyqtSlot()
    def on_btnCancelVisitBeforeRecordClient_clicked(self):
        self.tblVisitByQueue.setModel(None)
        self.close()


class CVisitByQueueTable(QtCore.QAbstractTableModel):
    headerText = [u'Дата и время приема', u'Тип', u'Назначил', u'Специалист', u'Каб', u'Визит', u'Примечания']

    def __init__(self,  parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._cols = []
        self.items = []


    def cols(self):
        self._cols = [CCol(u'Дата и время приема', ['directionDate'], 20, 'l'),
                      CCol(u'Тип',        ['actionType_id'], 15, 'l'),
                      CCol(u'Назначил',   ['setPerson_id'], 20, 'l'),
                      CCol(u'Специалист', ['person_id'], 20, 'l'),
                      CCol(u'Каб',        ['office'], 6, 'l'),
                      CCol(u'Визит',      ['person_id', 'scene_id'], 30, 'l'),
                      CCol(u'Примечания', ['note'], 6, 'l')
                      ]
        return self._cols


    def columnCount(self, index = QtCore.QModelIndex()):
        return 7


    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self.items)


    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled


    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
        return QtCore.QVariant()


    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            return toVariant(item[column])
        return QtCore.QVariant()


    def loadData(self, booleanIsChecked = False, clientId = None, beginDate = None, endDate = None, orgStructureId = None, specialityId = None, personId = None):
        self.items = []
        if clientId and beginDate and endDate:
            etcQueue = 'queue'
            atcQueue = 'queue'
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableEventType = db.table('EventType')
            tableAction = db.table('Action')
            tableActionType = db.table('ActionType')
            tableVisit = db.table('Visit')
            tablePersonWithSpeciality = db.table('vrbPersonWithSpeciality')
            tableActionProperty_Action = db.table('ActionProperty_Action')
            tableOrgStructure = db.table('OrgStructure')
            cols = [tableAction['id'],
                    tableActionType['name'],
                    tableAction['directionDate'],
                    tableAction['setPerson_id'],
                    tableAction['person_id'],
                    tableAction['office'],
                    tableAction['note']
                    ]
            tableQuery = tableAction
            tableQuery = tableQuery.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            tableQuery = tableQuery.innerJoin(tableEvent, tableEvent['id'].eq(tableAction['event_id']))
            tableQuery = tableQuery.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
            tableQuery = tableQuery.innerJoin(tableActionProperty_Action, tableActionProperty_Action['value'].eq(tableAction['id']))
            tableQuery = tableQuery.innerJoin(tablePersonWithSpeciality, tablePersonWithSpeciality['id'].eq(tableAction['person_id']))

            recordsOrgStructure = []
            cond = [tableEvent['client_id'].eq(clientId),
                    tableAction['directionDate'].between(beginDate, endDate.addDays(1)),
                    tableEventType['code'].eq(etcQueue),
                    tableActionType['code'].eq(atcQueue)
                    ]
            recordsOrgStructure = []
            recordsOrgStructure.append(orgStructureId)
            bufferOrgStructure = [orgStructureId]
            orgStructure = True
            while orgStructure:
                stmt = db.selectStmt(tableOrgStructure, 'id', [tableOrgStructure['parent_id'].inlist(bufferOrgStructure)])
                query = db.query(stmt)
                bufferOrgStructure = []
                while query.next():
                    recordsOrgStructure.append(forceRef(query.value(0).toInt()[0]))
                    bufferOrgStructure.append(forceRef(query.value(0).toInt()[0]))
                if bufferOrgStructure == []:
                    orgStructure = False
            if personId:
                cond.append(tableAction['person_id'].eq(personId))
            if recordsOrgStructure != []:
                    cond.append(tablePersonWithSpeciality['orgStructure_id'].inlist(recordsOrgStructure))
            elif orgStructureId:
                    cond.append(tablePersonWithSpeciality['orgStructure_id'].eq(orgStructureId))
            if specialityId:
                cond.append(tablePersonWithSpeciality['speciality_id'].eq(specialityId))
            recordBufferAction = db.getRecordList(tableQuery, cols, cond, 'Action.directionDate')

            listDirectionDateAction = []
            for recordDirectionDateAction in recordBufferAction:
               listDirectionDateAction.append(forceDate(recordDirectionDateAction.value('directionDate')))
            if listDirectionDateAction:
                tableRbScene = db.table('rbScene')
                cols = [tableVisit['date'],
                        tablePersonWithSpeciality['name'].alias('personName'),
                        tableRbScene['name']
                        ]

                condVisit = [tableVisit['date'].inlist(listDirectionDateAction),
                             tableEvent['client_id'].eq(clientId),
                             tableVisit['deleted'].eq(0)
                             ]
                if specialityId:
                    condVisit.append(tablePersonWithSpeciality['speciality_id'].eq(specialityId))
                if recordsOrgStructure != []:
                    condVisit.append(tablePersonWithSpeciality['orgStructure_id'].inlist(recordsOrgStructure))
                elif orgStructureId:
                    condVisit.append(tablePersonWithSpeciality['orgStructure_id'].eq(orgStructureId))
                tableQueryVisit = tableVisit
                tableQueryVisit = tableQueryVisit.innerJoin(tableEvent, tableEvent['id'].eq(tableVisit['event_id']))
                tableQueryVisit = tableQueryVisit.innerJoin(tableRbScene, tableRbScene['id'].eq(tableVisit['scene_id']))
                tableQueryVisit = tableQueryVisit.innerJoin(tablePersonWithSpeciality, tablePersonWithSpeciality['id'].eq(tableVisit['person_id']))
                recordVisit = db.getRecordList(tableQueryVisit, cols, condVisit, 'Visit.date')
            for record in recordBufferAction:
                directionDateTime = u''
                nameActionType = u''
                setPersonName = u''
                personName = u''
                visit = u''
                office = u''
                note = u''
                directionDate = forceDate(record.value('directionDate'))
                setPerson_id = forceRef(record.value('setPerson_id'))
                if setPerson_id:
                    setPersonName = forceString(db.translate(tablePersonWithSpeciality, tablePersonWithSpeciality['id'], setPerson_id, 'name'))
                person_id = forceRef(record.value('person_id'))
                if person_id:
                    personName = forceString(db.translate(tablePersonWithSpeciality, tablePersonWithSpeciality['id'], person_id, 'name'))
                directionDateTime = forceDateTime(record.value('directionDate'))
                nameActionType = forceString(record.value('name'))
                office = forceString(record.value('office'))
                note = forceString(record.value('note'))
                visit = self.getVisit(directionDate, personName, recordVisit)
                if not booleanIsChecked and visit != u'':
                    item = [directionDateTime.toString('dd.MM.yyyy hh:mm'),
                            nameActionType,
                            setPersonName,
                            personName,
                            office,
                            visit,
                            note
                            ]
                    self.items.append(item)
                if booleanIsChecked and visit == u'':
                    item = [directionDateTime.toString('dd.MM.yyyy hh:mm'),
                            nameActionType,
                            setPersonName,
                            personName,
                            office,
                            visit,
                            note
                            ]
                    self.items.append(item)
        self.reset()


    def getVisit(self, directionDate=None, personName=None, recordVisit=None):
        if not recordVisit:
            recordVisit = []
        visit = u''
        for recordVisitData in recordVisit:
            if directionDate and personName:
                if directionDate == forceDate(recordVisitData.value('date')):
                    if personName != forceString(recordVisitData.value('personName')):
                        visit += u'' + forceString(recordVisitData.value('personName')) + u', ' + forceString(recordVisitData.value('name')) + u'\n '
                    else:
                        visit = u'' + forceString(recordVisitData.value('personName')) + u', ' + forceString(recordVisitData.value('name'))
                        return visit
        return visit

