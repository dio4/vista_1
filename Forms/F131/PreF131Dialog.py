# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

"""
F131 (periodic event) planer
"""

from PyQt4 import QtCore, QtGui, QtSql

from Events.Utils import recordAcceptable
from Orgs.OrgComboBox import CPolyclinicExtendedInDocTableCol
from Ui_PreF131 import Ui_PreF131Dialog
from library.DialogBase import CDialogBase
from library.InDocTable import CInDocTableModel, CBoolInDocTableCol, CIntInDocTableCol, CRBInDocTableCol
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, forceStringEx, \
    calcAgeTuple, formatName, formatSex
from library.crbcombobox import CRBComboBox


class CPreF131Dialog(CDialogBase, Ui_PreF131Dialog):
    def __init__(self, parent, personSpecialityId = None):
        CDialogBase.__init__(self,  parent)
        self.__modelDiagnostics = CDiagnosticsModel(self)
        self.__modelDiagnostics.setObjectName('__modelDiagnostics')
        self.__modelActions     = CActionsModel(self)
        self.__modelActions.setObjectName('__modelActions')
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Планирование осмотра Ф.131')
        self.__clientName      = None
        self.__clientSex       = None
        self.__clientBirthDate = None
        self.__clientAge       = None
        self.tissueTypeId      = None
        
        self._clientWorkHurtCodeList       = []
        self._clientWorkHurtFactorCodeList = []
        self.unconditionalActionList = []

        self.personSpecialityId = personSpecialityId
        self.boolPersonSpecialityId = False
        self.tblDiagnostics.setModel(self.__modelDiagnostics)
        self.tblDiagnostics.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblDiagnostics.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblActions.setModel(self.__modelActions)
        self.tblActions.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblActions.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def prepare(self, clientId, eventTypeId, eventDate, tissueTypeId=None, recommendationList=None, useDiagnosticsAndActionsPresets=True):
        if recommendationList is None:
            recommendationList = []
        self.tissueTypeId = tissueTypeId
        self.setClientInfo(clientId, eventDate)
        self.setEventTypeId(eventTypeId, recommendationList, useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets)

    def setClientInfo(self, clientId, eventDate):
        db = QtGui.qApp.db
        table  = db.table('Client')
        record = db.getRecord(table, 'lastName, firstName, patrName, sex, birthDate', clientId)
        if record:
            lastName  = record.value('lastName')
            firstName = record.value('firstName')
            partName  = record.value('patrName')
            self.__clientName      = formatName(lastName, firstName, partName)
            self.__clientSex       = forceInt(record.value('sex'))
            self.__clientBirthDate = forceDate(record.value('birthDate'))
            self.__clientAge       = calcAgeTuple(self.__clientBirthDate, eventDate)
            if not self.__clientAge:
                self.__clientAge = (0, 0, 0, 0)
            
            self.setClientWorkHurtCodeList(clientId)
            self.setClientWorkHurtFactorCodeList(clientId)

    def setClientWorkHurtCodeList(self, clientId):
        db = QtGui.qApp.db
        
        tableCW       = db.table('ClientWork')
        tableCWH      = db.table('ClientWork_Hurt')
        tableHurtType = db.table('rbHurtType')
        
        queryTable = tableCW.leftJoin(tableCWH, tableCWH['master_id'].eq(tableCW['id']))
        queryTable = queryTable.leftJoin(tableHurtType, tableHurtType['id'].eq(tableCWH['hurtType_id']))
        cond = tableCW['client_id'].eq(clientId)
        fieldList = [tableHurtType['code'].name(), tableCWH['id'].name()]
        recordList = db.getRecordList(queryTable, fieldList, cond)
        
        for record in recordList:
            self._clientWorkHurtCodeList.append(forceStringEx(record.value('code')))

    def setClientWorkHurtFactorCodeList(self, clientId):
        db = QtGui.qApp.db
        
        tableCW             = db.table('ClientWork')
        tableCWHF           = db.table('ClientWork_Hurt_Factor')
        tableHurtFactorType = db.table('rbHurtFactorType')

        queryTable = tableCW.leftJoin(tableCWHF, tableCWHF['master_id'].eq(tableCW['id']))
        queryTable = queryTable.leftJoin(tableHurtFactorType, tableHurtFactorType['id'].eq(tableCWHF['factorType_id']))
        cond = tableCW['client_id'].eq(clientId)
        recordList = db.getRecordList(queryTable, tableHurtFactorType['code'].name(), cond)
        
        for record in recordList:
            self._clientWorkHurtFactorCodeList.append(forceString(record.value('code')))

    def setEventTypeId(self, eventTypeId, recommendationList, useDiagnosticsAndActionsPresets=True):
        eventTypeRecord = QtGui.qApp.db.getRecord('EventType', ['name'], eventTypeId)
        eventTypeName  = forceString(eventTypeRecord.value('name'))
        title = u'Планирование: %s, Пациент: %s, Пол: %s, ДР.: %s '% (eventTypeName, self.__clientName, formatSex(self.__clientSex), forceString(self.__clientBirthDate))
        QtGui.QDialog.setWindowTitle(self, title)

        self.prepareDiagnostics(eventTypeId)
        if useDiagnosticsAndActionsPresets:
            # self.prepareDiagnostics(eventTypeId)
            self.prepareActions(eventTypeId, recommendationList)

    def prepareDiagnostics(self, eventTypeId):
        includedGroups = []
        db = QtGui.qApp.db
        tableEventTypeDiagnostic = db.table('EventType_Diagnostic')
        tableEvenType = db.table('EventType')
        records = QtGui.qApp.db.getRecordList(tableEventTypeDiagnostic.innerJoin(tableEvenType, tableEvenType['id'].eq(tableEventTypeDiagnostic['eventType_id'])),
                                              cols=['EventType_Diagnostic.*', tableEvenType['scene_id']],
                                              where=tableEventTypeDiagnostic['eventType_id'].eq(eventTypeId),
                                              order=[tableEventTypeDiagnostic['idx'], tableEventTypeDiagnostic['id']])
        model = self.__modelDiagnostics
        self.boolPersonSpecialityId = False if len(records) else True
        for record in records:
            if self.recordAcceptable(record):
                target = model.getEmptyRecord()
                target.append(QtSql.QSqlField('scene_id', QtCore.QVariant.Int))
                target.append(QtSql.QSqlField('defaultHealthGroup_id', QtCore.QVariant.Int))
                target.append(QtSql.QSqlField('defaultMedicalGroup_id', QtCore.QVariant.Int))
                target.append(QtSql.QSqlField('defaultMKB', QtCore.QVariant.String))
                target.setValue('speciality_id',  record.value('speciality_id'))
                target.setValue('visitType_id',   record.value('visitType_id'))
                target.setValue('actuality',      record.value('actuality'))
                target.setValue('selectionGroup', record.value('selectionGroup'))
                target.setValue('defaultHealthGroup_id',  record.value('defaultHealthGroup_id'))
                target.setValue('defaultMedicalGroup_id', record.value('defaultMedicalGroup_id'))
                target.setValue('defaultMKB',  record.value('defaultMKB'))
                target.setValue('defaultGoal_id', record.value('defaultGoal_id'))
                target.setValue('service_id', record.value('service_id'))
                target.setValue('scene_id', record.value('scene_id'))

                selectionGroup = forceInt(record.value('selectionGroup'))
                if selectionGroup <= 0:
                    target.setValue('include',  QtCore.QVariant(0))
                elif selectionGroup == 1:
                    target.setValue('include',  QtCore.QVariant(1))
                elif selectionGroup in includedGroups :
                    target.setValue('include',  QtCore.QVariant(0))
                else:
                    if forceRef(record.value('speciality_id')) == self.personSpecialityId:
                        target.setValue('include',  QtCore.QVariant(1))
                        includedGroups.append(selectionGroup)
                if forceRef(record.value('speciality_id')) == self.personSpecialityId:
                    self.boolPersonSpecialityId = True
                model.items().append(target)
        model.reset()

    def prepareActions(self, eventTypeId, recommendationList):
        includedGroups = []

        db = QtGui.qApp.db
        table = db.table('EventType_Action')
        tableActionType = db.table('ActionType')
        join = table.leftJoin(tableActionType, tableActionType['id'].eq(table['actionType_id']))
        cond = [ table['eventType_id'].eq(eventTypeId), 
                tableActionType['deleted'].eq(0) ]
        records = db.getRecordList(join, 'EventType_Action.*', cond, 'ActionType.class, idx, id')
        for record in records:
            if self.recordAcceptable(record):
                tissueTypeId = forceRef(record.value('tissueType_id'))
                if tissueTypeId and self.tissueTypeId:
                    if self.tissueTypeId != tissueTypeId:
                        continue
                actionTypeId = forceRef(record.value('actionType_id'))
                if forceBool(db.translate('ActionType', 'id', actionTypeId, 'deleted')):
                    continue
                target = self.__modelActions.getEmptyRecord()
                target.setValue('actionType_id',  QtCore.QVariant(actionTypeId))
                target.setValue('actuality',      record.value('actuality'))
                target.setValue('selectionGroup', record.value('selectionGroup'))
                target.setValue('defaultOrg_id', record.value('defaultOrg_id'))
                selectionGroup = forceInt(record.value('selectionGroup'))
                if selectionGroup <= 0:
                    target.setValue('include',  QtCore.QVariant(0))
                elif selectionGroup == 1:
                    target.setValue('include',  QtCore.QVariant(1))
                elif selectionGroup in includedGroups :
                    target.setValue('include',  QtCore.QVariant(0))
                else:
                    target.setValue('include',  QtCore.QVariant(1))
                    includedGroups.append(selectionGroup)
                target.setValue('expose', record.value('expose'))
                self.__modelActions.items().append(target)

        actionTypeIdRecList = [forceInt(rec.value('actionType_id')) for rec in recommendationList]
        records = db.getRecordList(tableActionType, where=tableActionType['id'].inlist(actionTypeIdRecList))
        for record in records:
            actionTypeId = forceInt(record.value('id'))
            orgId = forceRef(record.value('defaultOrg_id'))
            self.unconditionalActionList.append((actionTypeId, 1.0, False, orgId))

        self.__modelActions.reset()

    def recordAcceptable(self, record):
        return recordAcceptable(self.__clientSex, self.__clientAge, record) and self.recordAcceptableByClientHurt(record)

    def recordAcceptableByClientHurt(self, record):
        resultWH  = True
        resultWHF = True

        listHurtForChecking = self._getHurtListForChecking(record, 'hurtType')
        if listHurtForChecking:
            resultWH  = False
            if self._clientWorkHurtCodeList:
                resultWH = bool(set(self._clientWorkHurtCodeList) & set(listHurtForChecking))
        
        listHurtFacrotForChecking = self._getHurtListForChecking(record, 'hurtFactorType')
        if listHurtFacrotForChecking:
            resultWHF = False
            if self._clientWorkHurtFactorCodeList:
                resultWHF = bool(set(self._clientWorkHurtFactorCodeList) & set(listHurtFacrotForChecking))
        
        return (resultWH or resultWHF) if listHurtForChecking and listHurtFacrotForChecking else (resultWH and resultWHF)

    def _getHurtListForChecking(self, record, fieldName):
        value = forceString(record.value(fieldName))
        result = [forceStringEx(val) for val in value.split(';') if val]
        return result

    def diagnostics(self):
        return self.__modelDiagnostics.items()

    def actions(self):
        result = []
        for record in self.__modelActions.items():
            if forceInt(record.value('include')) != 0:
                actionTypeId = forceRef(record.value('actionType_id'))
                org_id = forceRef(record.value('defaultOrg_id'))
                result.append((actionTypeId, 1.0, False, org_id))
        return result + self.unconditionalActionList

    def selectionPlanner(self, model, newSelect = 0):
        for i, item in enumerate(model.items()):
            selectionGroup = forceInt(item.value('selectionGroup'))
            if selectionGroup == 0:
                item.setValue('include', QtCore.QVariant(newSelect))
        model.reset()

    @QtCore.pyqtSlot()
    def on_btnSelectVisits_clicked(self):
        self.selectionPlanner(self.__modelDiagnostics, 1)

    @QtCore.pyqtSlot()
    def on_btnDeselectVisits_clicked(self):
        self.selectionPlanner(self.__modelDiagnostics, 0)

    @QtCore.pyqtSlot()
    def on_btnSelectActions_clicked(self):
        self.selectionPlanner(self.__modelActions, 1)

    @QtCore.pyqtSlot()
    def on_btnDeselectActions_clicked(self):
        self.selectionPlanner(self.__modelActions, 0)


class CPreModel(CInDocTableModel):
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.CheckStateRole:
            column = index.column()
            row = index.row()
            group = forceInt(self.items()[row].value('selectionGroup'))
            newState = 1 if forceInt(value) == QtCore.Qt.Checked else 0
            if group>0:
                newState = 1
            if group == 0:  # нулевая группа - всегда переключается
                return CInDocTableModel.setData(self, index, value, role)
            if group == 1:  # первая группа - никогда не переключается
                return False
            for itemIndex, item in enumerate(self.items()):
                itemGroup = forceInt(item.value('selectionGroup'))
                if itemGroup == group:
                    item.setValue('include',  QtCore.QVariant(newState if itemIndex == row else 0))
                    self.emitCellChanged(itemIndex, 0)
            self.emitColumnChanged(0)
            return True
        return CInDocTableModel.setData(self, index, value, role)

#    def emitDataChanged(self, index):
##        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex&, QModelIndex&)'), index, index)
#        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)



class CDiagnosticsModel(CPreModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'EventType_Diagnostic', 'id', 'eventType_id', parent)
        self.addExtCol(CBoolInDocTableCol( u'Включить',       'include', 10), QtCore.QVariant.Int)
        self.addCol(CRBInDocTableCol(   u'Специальность',  'speciality_id', 20, 'rbSpeciality')).setReadOnly()
        self.addCol(CRBInDocTableCol(      u'Услуга',         'service_id', 10, 'rbService', prefferedWidth=300, showFields=CRBComboBox.showCodeAndName)).setReadOnly()
        self.addCol(CRBInDocTableCol(   u'Тип визита',  'visitType_id', 20, 'rbVisitType')).setReadOnly()
        self.addCol(CIntInDocTableCol(  u'Срок годности',  'actuality',      5)).setReadOnly()
        self.addCol(CRBInDocTableCol(   u'Цель обращения', 'defaultGoal_id', 15, 'rbEventGoal')).setReadOnly()
        self.addCol(CIntInDocTableCol(  u'Группа выбора',  'selectionGroup', 5)).setReadOnly()
#        self.addCol(CRBInDocTableCol(   u'Г.З.',           'defaultHealthGroup_id', 20, 'rbHealthGroup')).setReadOnly()
#        self.addCol(CInDocTableCol(     u'МКБ',            'defaultMKB', 5)).setReadOnly()
        self.setEnableAppendLine(False)



class CActionsModel(CPreModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'EventType_Action', 'id', 'eventType_id', parent)
        self.addExtCol(CBoolInDocTableCol( u'Включить',       'include', 10), QtCore.QVariant.Int)
        self.addCol(CRBInDocTableCol(   u'Наименование',    'actionType_id',20, 'ActionType')).setReadOnly()
        self.addCol(CIntInDocTableCol(  u'Срок годности',  'actuality',      5)).setReadOnly()
        self.addCol(CIntInDocTableCol(  u'Группа выбора',  'selectionGroup', 5)).setReadOnly()
        self.addCol(CBoolInDocTableCol( u'Выставлять',  'expose', 10)).setReadOnly()
        self.addCol(CPolyclinicExtendedInDocTableCol(u'Место проведения', 'defaultOrg_id', 20)).setReadOnly()
        self.setEnableAppendLine(False)
