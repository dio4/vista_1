# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui
from library.DialogBase                     import CDialogBase
from library.Utils                          import forceRef, forceString, forceInt, forceDate, forceDouble
from library.TreeModel                      import CTreeModel, CTreeItem
from library.DateEdit                       import CDateEdit
from library.crbcombobox                    import CRBComboBox
from Reports.ReportsConstructor.RCComboBox  import CRCFieldsComboBox, CRCComboBox

from RCTableModel import CRCItemModel, CRCConditionTypeItemModel

from Reports.ReportsConstructor.Ui_RCConditionItemEditor               import Ui_RCConditionItemEditorDialog

class CRCConditionTreeModel(CTreeModel):
    u'''
        Модель для дерева условий
    '''
    def __init__(self, parent, baseModel, modelParams):
        CTreeModel.__init__(self, parent, CRCConditionTreeItem(None, '', 0,  self, name=u'Все'))
        self._table = 'rcQuery_Conditions'
        self.idColName    = 'id'
        self.groupColName = 'parent_id'
        self.nameColName  = 'field'
        self._masterIdFieldName = 'master_id'
        self._parent = parent
        self._baseModel = baseModel
        self._items = {}
        self._modelConditionType = CRCConditionTypeItemModel (self, ['code', 'name', 'sign'], 'rcConditionType')
        self._modelValueType = CRCItemModel(self, ['code', 'name'], 'rcValueType')
        self._modelParams = modelParams
        self._modelConditionType.loadItems()
        self._modelValueType.loadItems()
        self._maxId = None
        self.rootItemVisible = False
        self.loadDefault()

    def update(self):
        self.getRootItem().update()
        #self.reset()

    def getItemEditor(self):
        editor = CConditionItemEditor(self._parent)
        editor.setFieldsModel(self._baseModel)
        editor.setConditionsModel(self)
        editor.setParamsModel(self._modelParams)
        return editor

    def getNewId(self):
        self._maxId += 1
        return self._maxId

    def markItemToDelete(self, index, value):
        u'''
            Помечаем элементы по index. Помеченные элементы не будут сохранятся.
        '''
        item = index.internalPointer()
        item.setDeleted(value)

    def addItem(self, id, item):
        if not id or not self._items.get(id, None):
            id = self.getNewId()
            parent_item = self.getItemById(item.get('parent_id', 0))
            if not self._items.get(item.get('parent_id', 0), {}).get('conditionType_id') in [self._modelConditionType.AND, self._modelConditionType.OR]:
                parent_item = parent_item.parent()
            self._items[id] = item
            if parent_item:
                parent_item._items.append(CRCConditionTreeItem(parent_item, item.get('field', u''), id, self))
        else:
            old_item = self.getItemById(id)
            old_item._field = item.get('field', u'')
            self._items[id] = item
            old_item.initName()
        return id

    def addCond(self, conditionType_id, index=None):
        id = self.getNewId()
        conditionType = self._modelConditionType.getItem(conditionType_id)
        if not index:
            parent_item = self._rootItem
        else:
            if self._items.get(index.internalPointer().id(), {}).get('conditionType_id', None) in [self._modelConditionType.OR, self._modelConditionType.AND]:
                parent_item = index.internalPointer()
            else:
                parent_item = index.internalPointer().parent()

        new_item = {'field': u'',
                'value': u'',
                'parent_id': parent_item.id(),
                'conditionType_id': conditionType_id,
                'valueType_id': None}
        self._items[id] = new_item
        if not parent_item._items:
            parent_item._items = []
        parent_item._items.append(CRCConditionTreeItem(parent_item, new_item.get('field', u''), id, self))

    def addCondOr(self, index=None):
        self.addCond(self._modelConditionType.OR, index)

    def addCondAnd(self, index=None):
        self.addCond(self._modelConditionType.AND, index)

    def changeCond(self, conditionType_id, index):
        item = index.internalPointer()
        conditionType = self._modelConditionType.getItem(conditionType_id)
        update = {'name': conditionType.get('sign', u''),
                  'conditionType_id': conditionType_id}
        item._name = update['name']
        self._items.get(item.id(), {}).update(update)

    def changeCondOr(self, index):
        self.changeCond(self._modelConditionType.AND, index)

    def changeCondAnd(self, index):
        self.changeCond(self._modelConditionType.OR, index)

    def loadChildrenItems(self, parent_item):
        children = []
        for id, item in self._items.items():
            if item.get(self.groupColName, 0) == parent_item.id():
                children.append(CRCConditionTreeItem(parent_item, item.get('field', ''), id, self))
        return children

    def loadDefault(self):
        u'''
        Загрузка условий по умолчанию при создании нового отчёта
        '''
        self._maxId = 1
        if not self._items:
            self.addCondAnd()
        self.getRootItem().items()

    def loadItems(self, masterId):
        self._items = {}
        db = QtGui.qApp.db
        table = db.table(self._table)
        filterCond = [table[self._masterIdFieldName].eq(masterId)]
        cols = [self.idColName, 'parentCondition_id', self.nameColName, 'conditionType_id', 'valueType_id', 'value']
        records = db.getRecordList(table, cols, filterCond)
        for record in records:
            id = forceRef(record.value(self.idColName))
            parent_id = forceInt(record.value('parentCondition_id'))
            conditionType_id = forceRef(record.value('conditionType_id'))
            valueType_id = forceRef(record.value('valueType_id'))
            value = forceString(record.value('value'))
            field = forceString(record.value(self.nameColName))
            self._items[id] = {'field': field,
                              'value': value,
                              'parent_id': parent_id,
                              'conditionType_id': conditionType_id,
                              'valueType_id': valueType_id}
        self._maxId = max(self._items.keys()) if self._items.keys() else 1
        self.getRootItem()._items = None
        self.getRootItem().items()

    def saveItems(self, masterId):
        u'''
        Сохранение элементов.
        Вначале удаля.тся из базы все условия к данному отчёту. Затем запускается рекурсивное схоранение.
        '''
        db = QtGui.qApp.db
        table = db.table(self._table)
        filterCond = [table[self._masterIdFieldName].eq(masterId)]
        db.deleteRecord(table, filterCond)
        for item in self._rootItem.items():
            item.saveItem(table, masterId, None)

    def getDataItemById(self, itemId):
        return self._items.get(itemId, None)

    def getItemById(self, itemId):
        return self._rootItem.getItemById(itemId)

    def getTreeId(self, item=None, function=None):
        def getKey(key):
            if function:
                key = function(key)
            return key

        if not item:
            item = self.getRootItem()
        itemId = item.id()
        children = {}
        for child in item.items():
            children[getKey(child.id())] = self.getTreeId(child, function)

        return children

    def getConditionForReport(self, id):
        item = self._items.get(id, {})
        return (self._baseModel.parcePath(item['field'])[0],
                self._modelConditionType.getItem(item['conditionType_id']).get('code', u''),
                self._modelValueType._items.get(item['valueType_id'], {}).get('code', u''),
                item['value'])

class CRCConditionTreeItem(CTreeItem):
    u'''
        Элемент дерева условий
    '''
    def __init__(self, parent, field, id, model, name=None):
        CTreeItem.__init__(self, parent, '')
        self.model = model
        self._field = field
        self._id = id
        self._deleted = 0
        if name:
            self._name = name
        else:
            self.initName()

    def initName(self):
        u'''
        После сохранения собираем наименование для элемента по другим его параметрам.
        '''
        item = self.model.getDataItemById(self._id)
        modelFields = self.model._baseModel
        modelConditionType = self.model._modelConditionType
        modelValueType = self.model._modelValueType
        modelParams = self.model._modelParams
        name = [modelFields.parcePathToTableNames(item['field']),
                modelConditionType.getItem(item['conditionType_id']).get('sign', '')]
        valueTypeCode = modelValueType.getItem(item['valueType_id']).get('code', '')
        condTypeCode = modelConditionType.getItem(item['conditionType_id']).get('code', '')
        if condTypeCode == 'true':
            pass
        elif condTypeCode == 'false':
            name = ['NOT'] + name
        elif valueTypeCode == 'param':
            name.append(u'@%s' % forceString(modelParams.getCol('param_id').toString(item['value'], None)))
        elif valueTypeCode == 'field':
            name.append(modelFields.parcePathToTableNames(item['value']))
        elif valueTypeCode == 'custom':
            name = [modelFields.parcePathToTableNames(item['value'])]
        else:
            name.append(item['value'])
        item['name'] = u' '.join(name)
        self._name = item['name']

    def loadChildren(self):
        return self.model.loadChildrenItems(self)

    def getChildrenIdList(self):
        result = []
        for item in self._items:
            result.append(item.id())
            result.append(item.getChildrenIdList())
        return result

    def saveItem(self, table, masterId, parentId):
        db = QtGui.qApp.db
        item = self.model.getDataItemById(self._id)
        if self._deleted == 1:
            return
        record = table.newRecord()
        record.setValue('field', item.get('field', ''))
        record.setValue('conditionType_id', item.get('conditionType_id', ''))
        record.setValue('value', item.get('value', ''))
        if item.get('valueType_id', ''):
            record.setValue('valueType_id', item.get('valueType_id', ''))
        record.setValue('parentCondition_id', parentId)
        record.setValue('master_id', masterId)
        id = db.insertRecord(table, record)
        for item in self.items():
            item.saveItem(table, masterId, id)

    def id(self):
        return self._id

    def field(self):
        return self._field

    def flags(self):
        flags = CTreeItem.flags(self)
        if self._deleted == 1:
            flags = flags & ~QtCore.Qt.ItemIsEnabled
        return flags

    def setDeleted(self, value):
        if value:
            self._deleted = 1
        else:
            self._deleted = 0
        for child in self._items:
            child.setDeleted(value)

    def getItemById(self, itemId):
        if self._id == itemId:
            return self
        if not self._items:
            return None
        for item in self._items:
            value = item.getItemById(itemId)
            if value:
                return value
        return None

class CConditionItemEditor(CDialogBase, Ui_RCConditionItemEditorDialog):
    u'''
        Диалог редактирования элемента дерева условий
    '''
    def __init__(self,  parent):
        CDialogBase.__init__(self, parent)
        self._table = 'rcQuery_Conditions'
        self.setupUi(self)
        self.setWindowTitleEx(u'Условие')
        self.setupDirtyCather()
        self.groupId = 0
        self.modelFields = None
        self._item = {}
        self._itemId = None
        self.custom = False
        self.initValueInputs()
        self.cmbConditionType.setTable('rcConditionType', filter="not code in ('or', 'and')")
        self.cmbConditionType.setCode('eq')
        self.cmbValueType.setTable('rcValueType')
        self.cmbValueType.setValue(1)

    def setCustomValue(self, value):
        if self.modelFields and self.isCustom():
            return self.modelFields.parcePathToTableNames(forceString(value))
        return value

    def getCustomValue(self, value):
        if self.modelFields and self.isCustom():
            return self.modelFields.parceTableNamesToPath(forceString(value))
        return value

    def initValueInputs(self):
        u'''
            Определяем список возможных полей ввода для ввода значения
        '''
        self.valueInputs = {'int': self.edtValueInt,
                            'double': self.edtValueDouble,
                            'unicode': self.edtValue,
                            'date': self.edtDate,
                            'param': self.cmbParams,
                            'field': self.cmbValueField,
                            'custom': self.edtCustom
                            }
        self.hideValueInputs()

    def getValue(self, code):
        u'''
            Получение значения поля ввода по коду
        '''
        code = str(code)
        input = self.valueInputs.get(code, None)
        value = None
        if not input == None and input.isEnabled():
            if isinstance(input, (CDateEdit, QtGui.QDateEdit)):
                value = forceString(input.date().toString('yyyy-MM-dd'))
            elif isinstance(input, CRCFieldsComboBox):
                value = input.value()[0]
            elif isinstance(input, (CRBComboBox, CRCComboBox)):
                value = input.value()
            elif isinstance(input, QtGui.QComboBox):
                value = input.currentIndex()
            elif isinstance(input, QtGui.QLineEdit):
                value = input.text()
            elif isinstance(input, QtGui.QSpinBox):
                value = input.value()
            value = self.getCustomValue(value)
        return forceString(value)

    def setValue(self, code, value):
        u'''
            Установка значения value для поля ввода с кодом code
        '''
        code = str(code)
        input = self.valueInputs.get(code, None)
        value = self.setCustomValue(value)
        if not input == None:
            if isinstance(input, (CDateEdit, QtGui.QDateEdit)):
                input.setDate(forceDate(QtCore.QDate.fromString(value, 'yyyy-MM-dd')))
            elif isinstance(input, CRCFieldsComboBox):
                input.setValue(forceString(value))
            elif isinstance(input, (CRBComboBox, CRCComboBox)):
                input.setValue(forceInt(value))
            elif isinstance(input, QtGui.QComboBox):
                input.setCurrentIndex(forceInt(value))
            elif isinstance(input, QtGui.QLineEdit):
                input.setText(forceString(value))
            elif isinstance(input, QtGui.QDoubleSpinBox):
                input.setValue(forceDouble(value))
            elif isinstance(input, QtGui.QSpinBox):
                input.setValue(forceInt(value))

    def hideValueInputs(self):
        for valueInput in self.valueInputs.values():
            valueInput.setVisible(False)

    def showValueInput(self, code):
        code = str(code)
        valueInput = self.valueInputs.get(code, None)
        if valueInput == None:
            return
        self.hideValueInputs()
        valueInput.setVisible(True)
        self.setCustom(code in ['custom'])
        self.cmbConditionType.setEnabled(not self.isCustom())
        self.cmbField.setEnabled(not self.isCustom())

    def showConditionInput(self, code):
        code = str(code)
        self.cmbValueType.setEnabled(not code in ['true', 'false'])
        if not self.cmbValueType._model.d:
            return
        valueInput = self.valueInputs.get(self.cmbValueType.code())
        if valueInput != None:
            valueInput.setEnabled(not code in ['true', 'false'])

    def setCustom(self, val):
        self.custom = val

    def isCustom(self):
        return self.custom

    def setGroupId(self, id):
        self.groupId = id

    def setFieldsModel(self, modelFields):
        self.modelFields = modelFields
        self.cmbField.setModel(self.modelFields)
        self.cmbValueField.setModel(self.modelFields)
        self.edtCustom.setModel(self.modelFields)

    def setConditionsModel(self, modelConditions):
        self.modelConditions = modelConditions

    def setParamsModel(self, modelParams):
        self.modelParams = modelParams
        self.cmbParams.setModel(self.modelParams)

    def load(self, id):
        self._itemId = id
        self._item = self.modelConditions.getDataItemById(id)
        self.setItem(self._item)

    def setItem(self, item):
        self.cmbField.setValue(item.get('field', ''))
        self.cmbConditionType.setValue(item.get('conditionType_id', 0))
        self.cmbValueType.setValue(item.get('valueType_id', 0))
        self.setValue(self.cmbValueType.code(), item.get('value', ''))
        self.groupId = item.get('parentCondition_id', 0)
        self.setIsDirty(False)

    def getItem(self):
        u'''
            Получение значений для элемента из всех активных полей редактирования.
        '''
        item = self._item
        valueTypeCode = self.cmbValueType.code()
        item['field'] = self.cmbField.value()[0] if self.cmbField.isEnabled() else None
        item['conditionType_id'] = self.cmbConditionType.value() if self.cmbConditionType.isEnabled() else None
        item['valueType_id'] = self.cmbValueType.value() if self.cmbValueType.isEnabled() else None
        item['value'] = self.getValue(valueTypeCode)
        item['parent_id'] = forceInt(self.groupId)
        return item

    def saveData(self):
        return self.checkDataEntered() and self.save()

    def checkDataEntered(self):
        result = True
        return result

    def save(self):
        return self.modelConditions.addItem(self._itemId, self.getItem())

    def on_cmbValueType_currentIndexChanged(self):
        self.showValueInput(self.cmbValueType.code())

    def on_cmbConditionType_currentIndexChanged(self):
        if self.cmbConditionType._model.d:
            self.showConditionInput(self.cmbConditionType.code())
