# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

from Events.Utils               import getEventAidTypeCode, getEventSceneId, getEventServiceId, \
                                       getEventVisitServiceFilter, getExactServiceId, getEventGoalFilter

from library.crbcombobox        import CRBComboBox
from library.crbservicecombobox import CRBServiceComboBox
from library.InDocTable         import CInDocTableModel, CDateInDocTableCol, CRBInDocTableCol, \
    CActionPersonInDocTableColSearch
from library.Utils              import forceBool, forceRef, toVariant, variantEq

from RefBooks.Tables            import rbFinance, rbScene, rbVisitType


class CRBServiceInDocTableCol(CRBInDocTableCol):
    hospitalMedicalAidTypeCode = '7'
    def __init__(self, title, fieldName, width, tableName, **params):
        CRBInDocTableCol.__init__(self, title, fieldName, width, tableName, **params)
        self.eventEditor = params.get('eventEditor', None)

    def createEditor(self, parent):
        additionalIdList = []
        if self.eventEditor is not None:
            serviceId = getEventServiceId(self.eventEditor.eventTypeId)
            if serviceId:
                additionalIdList.append(serviceId)
        needFilter = getEventAidTypeCode(self.eventEditor.eventTypeId) == CRBServiceInDocTableCol.hospitalMedicalAidTypeCode
        editor = CRBServiceComboBox(parent, filterByHospitalBedsProfile=needFilter, additionalIdList=additionalIdList)
        if self.eventEditor is not None:
            visitServiceFilter = getEventVisitServiceFilter(self.eventEditor.eventTypeId)
            editor.setServiceFilterByCode(visitServiceFilter)
            editor.setSexAgeVars(self.eventEditor.realClientSex(), self.eventEditor.realClientBirthDate(), self.eventEditor.personSpecialityId)
            if getEventGoalFilter(self.eventEditor.eventTypeId) and hasattr(self.eventEditor, 'cmbGoal'):
                editor.setEventGoalFilter(self.eventEditor.cmbGoal.value())
        editor.loadData(addNone=self.addNone, filter=self.filter)

        editor.setShowFields(self.showFields)
        editor.setPrefferedWidth(self.prefferedWidth)
        return editor

    # def setEditorData(self, editor, value, record):
    #     editor.setValue(forceInt(value))
    #     # no longer needed here
    #     # if self.eventEditor is not None:
    #     #     visitServiceFilter = getEventVisitServiceFilter(self.eventEditor.eventTypeId)
    #     #     editor.setServiceFilterByCode(visitServiceFilter)

class CEventVisitsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'Visit', 'id', 'event_id', parent)
        self.colPerson = self.addCol(CActionPersonInDocTableColSearch(u'Врач', 'person_id', 20, 'vrbPersonWithSpeciality', order = 'name', parent=parent))
        self.colAssistant = self.addCol(CActionPersonInDocTableColSearch(u'Ассистент', 'assistant_id', 20, 'vrbPersonWithSpeciality', order = 'name', parent=parent))
        self.addCol(CRBInDocTableCol(    u'Место',         'scene_id',     10, rbScene, addNone=False, prefferedWidth=150))
        self.addCol(CDateInDocTableCol(  u'Дата',          'date',         20))
        self.addCol(CRBInDocTableCol(    u'Тип',           'visitType_id', 10, rbVisitType, addNone=False, showFields=CRBComboBox.showCodeAndName))
        self.addCol(CRBServiceInDocTableCol(u'Услуга',     'service_id',   50, 'rbService', addNone=False, showFields=CRBComboBox.showCodeAndName, prefferedWidth=150, eventEditor=parent))
        self.addCol(CRBInDocTableCol(    u'Тип финансирования', 'finance_id',  50, rbFinance, addNone=False, showFields=CRBComboBox.showCodeAndName, prefferedWidth=150))
        self.addHiddenCol('payStatus')
        self.hasAssistant = True
        self.defaultSceneId = None
        self.tryFindDefaultSceneId = True
        self.defaultVisitTypeId = None
        self.tryFindDefaultVisitTypeId = True
        self._parent = parent

    def loadItems(self, eventId):
        CInDocTableModel.loadItems(self, eventId)
        if self.items():
            lastItem = self.items()[-1]
            if self.defaultSceneId is None:
                self.defaultSceneId = forceRef(lastItem.value('scene_id'))
            if self.defaultVisitTypeId is None:
                self.defaultVisitTypeId = forceRef(lastItem.value('visitType_id'))
        eventEditor = QtCore.QObject.parent(self)
        eventTypeId = eventEditor.eventTypeId


    def getEmptyRecord(self, sceneId=None, personId=None):
        eventEditor = QtCore.QObject.parent(self)
        eventEditor.getPersonServiceId(personId)
        if not personId:
            if QtGui.qApp.userSpecialityId:
                personId = QtGui.qApp.userId
                if not eventEditor.getPersonServiceId(personId):
                    personId = None
        if not personId:
            execPersonId = eventEditor.getExecPersonId()
            if execPersonId:
                personId = execPersonId
        assistantId = eventEditor.getAssistantId() if self.hasAssistant and personId and personId == eventEditor.personId else None
        result = CInDocTableModel.getEmptyRecord(self)
        result.setValue('person_id',     toVariant(personId))
        result.setValue('assistant_id',  toVariant(assistantId))
        result.setValue('scene_id',      toVariant(sceneId if sceneId else self.getDefaultSceneId()))
        result.setValue('visitType_id',  toVariant(self.getDefaultVisitTypeId()))
        result.setValue('service_id',    toVariant(self.getServiceId(result)))
        result.setValue('finance_id',    self.getFinanceId())
        return result

    # Сейчас не используется, возможно стоит удалить.
    # mdldml: Кажется, все-таки используется в getEmptyRecord.
    def getServiceId(self, record):
        u"""Определяем подходящую услугу по врачу, месту и т.д. Если не находим, пытаемся скопировать услугу из последнего посещения.

        @param record: запись из таблицы Visit, на основе данных из которой пытаемся подобрать услугу.
        """
        serviceId = self.getExactServiceId(record)
        if serviceId.isNull() and self.items():
            lastItem = self.items()[-1]
            personId = forceRef(lastItem.value('person_id'))
            newPersonId = forceRef(record.value('person_id'))
            sceneId = forceRef(lastItem.value('scene_id'))
            newSceneId = forceRef(record.value('scene_id'))
            if personId and newPersonId:
                stmt = '''SELECT p1.speciality_id = p2.speciality_id
                FROM Person p1, Person p2 WHERE p1.id = %s AND p2.id = %s''' % (personId, newPersonId)
                query = QtGui.qApp.db.query(stmt)
                if query.first():
                    if not forceBool(query.record().value(0)):
                        return None
            if sceneId and newSceneId and sceneId != newSceneId:
                return None
            serviceId = forceRef(lastItem.value('service_id'))
        return serviceId

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        column = index.column()
        row = index.row()
        self.updateRetiredList()
        if not variantEq(self.data(index, role), value):
            personColIndex    = self.getColIndex('person_id')
            sceneColIndex     = self.getColIndex('scene_id')
            visitTypeColIndex = self.getColIndex('visitType_id')
            if column == personColIndex: # врач
                eventEditor = QtCore.QObject.parent(self)
                personId = forceRef(value)
                if not eventEditor.checkClientAttendaceEE(personId):
                    return False
            if column in [personColIndex, sceneColIndex, visitTypeColIndex]: # врач, место или тип
                result = CInDocTableModel.setData(self, index, value, role)
                if result:
                    item = self.items()[row]
                    item.setValue('service_id', toVariant(self.getExactServiceId(item)))
                    self.emitCellChanged(row, self.getColIndex('service_id')) # услуга
                return result
            else:
                return CInDocTableModel.setData(self, index, value, role)
        else:
            return True


    def getDefaultSceneId(self):
        if self.defaultSceneId is None:
            if self.tryFindDefaultSceneId:
                eventEditor = QtCore.QObject.parent(self)
                self.defaultSceneId = getEventSceneId(eventEditor.eventTypeId)
                if not self.defaultSceneId:
                    self.defaultSceneId = forceRef(QtGui.qApp.db.translate(rbScene, 'code', '1', 'id'))
                self.tryFindDefaultSceneId = False
        return self.defaultSceneId


    def setDefaultVisitTypeId(self, visitTypeId):
        self.defaultVisitTypeId = visitTypeId
        if visitTypeId is None:
            self.tryFindDefaultVisitTypeId = True


    def getDefaultVisitTypeId(self):
        if self.defaultVisitTypeId is None:
            if self.tryFindDefaultVisitTypeId:
                self.defaultVisitTypeId = forceRef(QtGui.qApp.db.translate(rbVisitType, 'code', '', 'id'))
                if self.defaultVisitTypeId is None:
                    self.defaultVisitTypeId = forceRef(QtGui.qApp.db.getRecordEx(rbVisitType, 'id').value(0))
                self.tryFindDefaultVisitTypeId = False
        return self.defaultVisitTypeId


    def getExactServiceId(self, record):
        eventEditor = QtCore.QObject.parent(self)
        eventTypeId     = eventEditor.eventTypeId
        diagnosisServiceId = eventEditor.getModelFinalDiagnostics().diagnosisServiceId()
        eventServiceId  = eventEditor.eventServiceId
        personId        = forceRef(record.value('person_id'))
        personServiceId = eventEditor.getPersonServiceId(personId)
        visitTypeId     = record.value('visitType_id')
        sceneId         = record.value('scene_id')
        serviceId       = getExactServiceId(diagnosisServiceId, eventServiceId, personServiceId, eventTypeId, visitTypeId, sceneId)
        return toVariant(serviceId)

    def getFinanceId(self):
        eventEditor = QtCore.QObject.parent(self)
        financeId = eventEditor.getVisitFinanceId()
        return toVariant(financeId)


    def addAbsentPersons(self, personIdList, eventDate = None):
        for item in self.items():
            personId = forceRef(item.value('person_id'))
            if personId in personIdList:
                personIdList.remove(personId)
        for personId in personIdList:
            item = self.getEmptyRecord(personId=personId)
            date = eventDate if eventDate else QtCore.QDate.currentDate()
            item.setValue('date',  toVariant(date))
            self.items().append(item)
        if personIdList:
            self.reset()


    def updatePersonAndService(self):
        personId = QtCore.QObject.parent(self).personId
        for row, item in enumerate(self.items()):
            item.setValue('person_id', toVariant(personId))
            item.setValue('service_id', self.getExactServiceId(item))
            self.emitCellChanged(row, self.getColIndex('service_id')) # услуга
            item.setValue('finance_id', self.getFinanceId())
            self.emitCellChanged(row, self.getColIndex('finance_id')) # тип финансирования

    def flags(self,  index = QtCore.QModelIndex()):
        if self.isEditable():
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
