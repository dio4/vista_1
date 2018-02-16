# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from collections import defaultdict

from PyQt4.QtCore import Qt

from Events.Action import ActionPropertyCopyModifier, ActionStatus
from Ui_ActionPropertyCopyDialog import Ui_ActionPropertyCopyDialog
from library.DialogBase import CDialogBase
from library.TableModel import CDateCol, CTableModel, CTextCol
from library.Utils import forceDate, forceInt, forceRef, forceString
from library.database import CTableRecordCache


class CCheckedPropertiesMixin(object):
    def __init__(self):
        self._propertyMap = {}  # { Action.id: { ActionProperty.id: bool, ... } }
        self._propertyActionMap = {}  # { ActionProperty.id: Action.id }

    def setPropertyMap(self, propertyMap):
        self._propertyMap = propertyMap
        self._propertyActionMap = {}
        for actionId, actionProperties in propertyMap.iteritems():
            for propertyId in actionProperties:
                self._propertyActionMap[propertyId] = actionId

    def getActionCheckState(self, actionId):
        if all(self._propertyMap[actionId].values()):
            return Qt.Checked
        if any(self._propertyMap[actionId].values()):
            return Qt.PartiallyChecked
        return Qt.Unchecked

    def setActionCheckState(self, actionId, state):
        checked = state == Qt.Checked
        self._propertyMap[actionId] = dict((propertyId, checked) for propertyId in self._propertyMap[actionId])

    def getPropertyCheckState(self, propertyId):
        return Qt.Checked if self._propertyMap[self._propertyActionMap[propertyId]][propertyId] else Qt.Unchecked

    def setPropertyCheckState(self, propertyId, state):
        checked = state == Qt.Checked
        self._propertyMap[self._propertyActionMap[propertyId]][propertyId] = checked


class CCheckedActionsModel(CTableModel, CCheckedPropertiesMixin):
    __pyqtSignals__ = ('actionCheckStateChanged()',
                       )

    def __init__(self, parent):
        CCheckedPropertiesMixin.__init__(self)
        CTableModel.__init__(self, parent, cols=[
            CTextCol(u'Тип действия', ['name'], 15),
            CTextCol(u'Исполнитель', ['personName'], 10),
            CDateCol(u'Дата выполнения', ['endDate'], 10)
        ])
        self.setTable('Action')

    def emitActionCheckStateChanged(self):
        self.emit(QtCore.SIGNAL('actionCheckStateChanged()'))

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsTristate

    def data(self, index, role=Qt.DisplayRole):
        row, column = index.row(), index.column()
        if index.isValid() and role == Qt.CheckStateRole and column == 0 and 0 <= row < self.rowCount():
            actionId = self._idList[row]
            return self.getActionCheckState(actionId)
        return CTableModel.data(self, index, role)

    def setData(self, index, value, role=Qt.EditRole):
        row, column = index.row(), index.column()
        if index.isValid() and role == Qt.CheckStateRole and column == 0 and 0 <= row < self.rowCount():
            actionId = self._idList[row]
            self.setActionCheckState(actionId, forceInt(value))
            self.emitActionCheckStateChanged()
            return True
        return CTableModel.setData(index, value, role)

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableVPerson = db.table('vrbPerson')

        table = tableAction.leftJoin(tableVPerson, tableVPerson['id'].eq(tableAction['person_id']))
        table = table.leftJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
        cols = [
            tableAction['actionType_id'],
            tableAction['specifiedName'],
            tableAction['endDate'],
            tableActionType['name'],
            tableVPerson['name'].alias('personName')
        ]
        self._table = table
        self._recordsCache = CTableRecordCache(db, self._table, cols, recordCacheCapacity)


class CCheckedPropertiesModel(CTableModel, CCheckedPropertiesMixin):
    __pyqtSignals__ = ('propertyCheckStateChanged()',)

    def __init__(self, parent):
        CCheckedPropertiesMixin.__init__(self)
        CTableModel.__init__(self, parent, cols=[
            CTextCol(u'Название', ['name'], 15),
            CTextCol(u'Значение', ['value'], 10)
        ])
        self.setTable('ActionProperty')

    def setTable(self, tableName, recordCacheCapacity=300):
        db = QtGui.qApp.db
        tableAP = db.table('ActionProperty')
        tableAPD = db.table('ActionProperty_Double')
        tableAPI = db.table('ActionProperty_Integer')
        tableAPS = db.table('ActionProperty_String')
        tableAPT = db.table('ActionPropertyType')

        table = tableAP
        table = table.innerJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
        table = table.leftJoin(tableAPD, tableAPD['id'].eq(tableAP['id']))
        table = table.leftJoin(tableAPI, tableAPI['id'].eq(tableAP['id']))
        table = table.leftJoin(tableAPS, tableAPS['id'].eq(tableAP['id']))
        cols = [
            tableAPT['name'],
            db.coalesce(tableAPD['value'],
                        tableAPI['value'],
                        tableAPS['value']).alias('value')
        ]
        self._table = table
        self._recordsCache = CTableRecordCache(db, self._table, cols, recordCacheCapacity)

    def emitPropertyCheckStateChanged(self):
        self.emit(QtCore.SIGNAL('propertyCheckStateChanged()'))

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

    def data(self, index, role=Qt.DisplayRole):
        row, column = index.row(), index.column()
        if index.isValid() and role == Qt.CheckStateRole and column == 0 and 0 <= row < self.rowCount():
            propertyId = self._idList[row]
            return self.getPropertyCheckState(propertyId)
        return CTableModel.data(self, index, role)

    def setData(self, index, value, role=Qt.EditRole):
        row, column = index.row(), index.column()
        if index.isValid() and role == Qt.CheckStateRole and column == 0 and 0 <= row < self.rowCount():
            propertyId = self._idList[row]
            self.setPropertyCheckState(propertyId, forceInt(value))
            self.emitPropertyCheckStateChanged()
            return True
        return CTableModel.setData(index, value, role)


class CCopyiedActionPropertyInfo(object):
    def __init__(self, propertyId, propertyTypeId, copyModifier, endDate, value):
        self.id = propertyId
        self.typeId = propertyTypeId
        self.copyModifier = copyModifier
        self.endDate = endDate
        self.value = value

    def __repr__(self):
        return u'<CopyiedActionProperty ({0}, {1}, {2}, {3})>'.format(self.id, self.copyModifier, self.endDate, self.value)


class CActionPropertyCopyDialog(CDialogBase, Ui_ActionPropertyCopyDialog):
    def __init__(self, parent, clientId, actionTypeId, begDate):
        super(CActionPropertyCopyDialog, self).__init__(parent)

        self.addModels('Properties', CCheckedPropertiesModel(self))
        self.addModels('Actions', CCheckedActionsModel(self))

        self._clientId = clientId
        self._actionTypeId = actionTypeId
        self._propertyMap = defaultdict(dict)  # { Action.id: { ActionProperty.id: bool } }: свойства, сгруппированные по действию, и флаг выбора
        self._propertyInfoMap = {}  # { ActionProperty.id: CCopyiedActionPropertyInfo }

        self.setupUi(self)
        self.setWindowTitle(u'Выберите свойства для копирования')

        self.cmbPerson.setValue(None)
        self.cmbSpeciality.setTable('rbSpeciality')
        self.cmbSpeciality.setValue(None)

        self.modelActions.actionCheckStateChanged.connect(self.modelProperties.emitDataChanged)
        self.modelProperties.propertyCheckStateChanged.connect(self.modelActions.emitDataChanged)

        self.setModels(self.tblActions, self.modelActions, self.selectionModelActions)
        self.setModels(self.tblProperties, self.modelProperties, self.selectionModelProperties)

        self.edtDateFrom.setDate(begDate.addMonths(-1))
        self.edtDateTo.setDate(begDate)

        self.cmbPerson.currentIndexChanged.connect(self.load)
        self.cmbSpeciality.currentIndexChanged.connect(self.load)
        self.edtDateFrom.dateChanged.connect(self.load)
        self.edtDateTo.dateChanged.connect(self.load)

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_selectionModelActions_currentChanged(self, previous, current):
        actionId = self.tblActions.currentItemId()
        if actionId is not None:
            self.tblProperties.setIdList(self._propertyMap[actionId].keys(), resetCache=False)
            self.tblProperties.sortByColumn(0, self.tblProperties.horizontalHeader().sortIndicatorOrder())
        else:
            self.tblProperties.setIdList([])

    @QtCore.pyqtSlot()
    def load(self):
        personId = self.cmbPerson.value()
        specialityId = self.cmbSpeciality.value()
        begDate = self.edtDateFrom.date()
        endDate = self.edtDateTo.date()
        self.selectProperties(personId=personId, specialityId=specialityId, begDate=begDate, endDate=endDate)

        self.modelActions.setPropertyMap(self._propertyMap)
        self.modelProperties.setPropertyMap(self._propertyMap)

        self.tblActions.setIdList(self._propertyMap.keys())
        self.tblActions.sortByColumn(0, self.tblActions.horizontalHeader().sortIndicatorOrder())
        self.tblActions.setCurrentRow(0)

    def getSelectedProperties(self):
        u"""
        :return: { ActionPropertyType.id: [list of CCopyiedActionPropertyInfo] }: списки свойств, сгруппированные по типу
        """
        result = defaultdict(list)
        for propertyId in self.getCheckedProperties():
            propertyInfo = self._propertyInfoMap[propertyId]
            result[propertyInfo.typeId].append(propertyInfo)
        return result

    def getCheckedProperties(self):
        return list(propertyId
                    for actionProperties in self._propertyMap.itervalues()
                    for propertyId, checked in actionProperties.iteritems() if checked)

    def selectProperties(self, personId=None, specialityId=None, begDate=None, endDate=None):
        db = QtGui.qApp.db
        tableDestAPT = db.table('ActionPropertyType').alias('DestAPT')
        tableDestAT = db.table('ActionType').alias('DestAT')
        tableSrcAction = db.table('Action')
        tableSrcAP = db.table('ActionProperty')
        tableSrcAPD = db.table('ActionProperty_Double')
        tableSrcAPI = db.table('ActionProperty_Integer')
        tableSrcAPS = db.table('ActionProperty_String')
        tableSrcAPT = db.table('ActionPropertyType')
        tableSrcAT = db.table('ActionType')
        tableEvent = db.table('Event')
        tableVPerson = db.table('vrbPersonWithSpeciality')

        table = tableDestAT
        table = table.innerJoin(tableDestAPT, [tableDestAPT['actionType_id'].eq(tableDestAT['id']),
                                               tableDestAPT['deleted'].eq(0)])
        table = table.innerJoin(tableEvent, [tableEvent['client_id'].eq(self._clientId),
                                             tableEvent['deleted'].eq(0)])
        table = table.innerJoin(tableSrcAction, [tableSrcAction['event_id'].eq(tableEvent['id']),
                                                 tableSrcAction['actionType_id'].eq(tableDestAT['id']),
                                                 tableSrcAction['deleted'].eq(0)])
        table = table.leftJoin(tableVPerson, tableVPerson['id'].eq(tableSrcAction['person_id']))
        table = table.innerJoin(tableSrcAT, [tableSrcAT['id'].eq(tableSrcAction['actionType_id']),
                                             tableSrcAT['class'].eq(tableDestAT['class']),
                                             tableSrcAT['deleted'].eq(0)])
        table = table.innerJoin(tableSrcAP, [tableSrcAP['action_id'].eq(tableSrcAction['id']),
                                             tableSrcAP['deleted'].eq(0)])
        table = table.innerJoin(tableSrcAPT, [tableSrcAPT['id'].eq(tableSrcAP['type_id']),
                                              tableSrcAPT['name'].eq(tableDestAPT['name']),
                                              tableSrcAPT['deleted'].eq(0)])
        table = table.leftJoin(tableSrcAPD, tableSrcAPD['id'].eq(tableSrcAP['id']))
        table = table.leftJoin(tableSrcAPI, tableSrcAPI['id'].eq(tableSrcAP['id']))
        table = table.leftJoin(tableSrcAPS, tableSrcAPS['id'].eq(tableSrcAP['id']))

        cols = [
            tableDestAPT['id'].alias('propertyTypeId'),
            tableSrcAction['id'].alias('actionId'),
            tableSrcAction['endDate'].alias('actionEndDate'),
            tableSrcAP['id'].alias('propertyId'),
            tableSrcAPT['copyModifier'],
            db.coalesce(tableSrcAPD['value'],
                        tableSrcAPI['value'],
                        tableSrcAPS['value']).alias('value')
        ]

        # curDate = QtCore.QDate.currentDate()
        cond = [
            tableDestAT['id'].eq(self._actionTypeId),
            # tableEvent['execDate'].ge(curDate.addYears(-1)),
            tableSrcAction['status'].eq(ActionStatus.Done),

            tableSrcAPT['typeName'].inlist(['Constructor', 'Text', 'String', 'Integer', 'Double']),
            tableSrcAPT['copyModifier'].ne(ActionPropertyCopyModifier.NoCopy),

            tableDestAPT['typeName'].inlist(['Constructor', 'Text', 'String', 'Integer', 'Double']),
            tableDestAPT['copyModifier'].ne(ActionPropertyCopyModifier.NoCopy),

            db.joinOr([tableSrcAPD['value'].isNotNull(),
                       tableSrcAPI['value'].isNotNull(),
                       tableSrcAPS['value'].isNotNull()])
        ]

        if personId is not None:
            cond.append(tableVPerson['id'].eq(personId))

        if specialityId is not None:
            cond.append(tableVPerson['speciality_id'].eq(specialityId))

        if begDate is not None and not begDate.isNull():
            cond.append(tableSrcAction['endDate'].dateGe(begDate))

        if endDate is not None and not endDate.isNull():
            cond.append(tableSrcAction['endDate'].dateLe(endDate))

        order = [
            tableSrcAT['name'],
            tableSrcAPT['name']
        ]

        self._propertyMap.clear()
        self._propertyInfoMap.clear()

        for rec in db.iterRecordList(table, cols, cond, order):
            propertyTypeId = forceRef(rec.value('propertyTypeId'))
            actionId = forceRef(rec.value('actionId'))
            propertyId = forceRef(rec.value('propertyId'))
            copyModifier = forceInt(rec.value('copyModifier'))
            actionEndDate = forceDate(rec.value('actionEndDate'))
            value = forceString(rec.value('value'))

            self._propertyMap[actionId][propertyId] = False
            self._propertyInfoMap[propertyId] = CCopyiedActionPropertyInfo(propertyId, propertyTypeId, copyModifier, actionEndDate, value)

#
# if __name__ == '__main__':
#     import sys
#     from library.database import connectDataBaseByInfo
#     from s11main import CS11mainApp
#     from pprint import pprint
#
#     app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
#
#     QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))
#     connectionInfo = {'driverName'      : 'mysql',
#                       'host'            : 'pnd3',
#                       'port'            : 3306,
#                       'database'        : 's11',
#                       'user'            : 'dbuser',
#                       'password'        : 'dbpassword',
#                       'connectionName'  : 'vista-med',
#                       'compressData'    : True,
#                       'afterConnectFunc': None}
#     db = connectDataBaseByInfo(connectionInfo)
#
#     QtGui.qApp = app
#     QtGui.qApp.db = db
#     QtGui.qApp.currentOrgId = lambda: 386270
#
#     dlg = CActionPropertyCopyDialog(None, 80110, 27186, QtCore.QDate.currentDate())
#     dlg.load()
#     dlg.exec_()
#
#     print '\n'
#     for propertyTypeId, propertyList in dlg.getSelectedProperties().iteritems():
#         print(propertyTypeId)
#         pprint(propertyList)
