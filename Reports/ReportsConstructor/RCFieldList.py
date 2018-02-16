# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore
import re

from library.Utils import forceRef, forceString, forceBool, forceStringEx, toVariant, forceInt

from library.TableModel                  import CTextCol, CBoolCol, CDesignationCol
from library.ItemsListDialog             import CItemEditorBaseDialog, CItemsSplitListDialogEx
from library.interchange                 import setLineEditValue, getLineEditValue, getTextEditValue, setTextEditValue, setCheckBoxValue, getCheckBoxValue
from library.exception import CDatabaseException

from Reports.ReportsConstructor.Ui_TableEditorDialog import Ui_TableDialog
from Reports.ReportsConstructor.Ui_FieldEditorDialog import Ui_FieldDialog


class CRCTableList(CItemsSplitListDialogEx):
    def __init__(self, parent):
        CItemsSplitListDialogEx.__init__(self, parent,
            'rcTable',
            [
                CTextCol(u'Наименование', ['name'], 50),
                CTextCol(u'Таблица', ['table'], 50),
            ],
            ['name'],
            'rcField',
            [
                CTextCol(u'Наименование', ['name'], 50),
                CTextCol(u'Поле', ['field'], 50),
                CBoolCol(u'Видимость', ['visible'], 10),
                CDesignationCol(u'Ссылка', ['ref_id'], (u"Select rcField.id as id, Concat_WS('.', rcTable.name, rcField.name) as name From rcField inner join rcTable on rcField.rcTable_id = rcTable.id", 'name'), 10),
            ],
            'rcTable_id', 'rcTable_id')
        self.setWindowTitleEx(u'Услуги')

    def preSetupUi(self):
        CItemsSplitListDialogEx.preSetupUi(self)
        self.btnNewGroupItem =  QtGui.QPushButton(u'Вставка поля', self)
        self.btnNewGroupItem.setObjectName('btnNewGroupItem')
        self.btnEditGroupItem =  QtGui.QPushButton(u'Правка поля', self)
        self.btnEditGroupItem.setObjectName('btnEditGroupItem')
        self.btnInitGroupItems =  QtGui.QPushButton(u'Инициализировать поля', self)
        self.btnInitGroupItems.setObjectName('btnInitGroupItems')

    def postSetupUi(self):
        CItemsSplitListDialogEx.postSetupUi(self)
        self.buttonBox.addButton(self.btnNewGroupItem, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnEditGroupItem, QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btnInitGroupItems, QtGui.QDialogButtonBox.ActionRole)
        self.disconnect(self.tblItemGroups, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.on_tblItemGroups_doubleClicked)

    def getItemEditor(self):
        return CRCTableEditor(self)

    def getItemEditorGroup(self):
        return CRCFieldEditor(self)

    @QtCore.pyqtSlot()
    def on_btnNewGroupItem_clicked(self):
        dialog = self.getItemEditorGroup()
        dialog.setTableId(self.currentItemId())
        if dialog.exec_():
            itemId = dialog.itemId()
            self.renewListAndSetTo(itemId)

    @QtCore.pyqtSlot()
    def on_btnEditGroupItem_clicked(self):
        itemId = self.tblItemGroups.itemId(self.tblItemGroups.currentIndex())
        if itemId:
            dialog = self.getItemEditorGroup()
            dialog.load(itemId)
            if dialog.exec_():
                itemId = dialog.itemId()
                self.renewListAndSetTo(itemId)
        else:
            self.on_btnNew_clicked()

    def on_tblItemGroups_doubleClicked(self, index):
        id = self.tblItemGroups.itemId(index)
        if id:
            self.on_btnEditGroupItem_clicked()
        else:
            self.on_btnNewGroupItem_clicked()

    @QtCore.pyqtSlot()
    def on_btnInitGroupItems_clicked(self):
        itemId = self.currentItemId()
        self.initFields(itemId)

    def initFields(self, tableId):
        db = QtGui.qApp.db
        tableName = forceString(db.translate('rcTable', 'id', tableId, '`table`'))
        hasFields = forceBool(len(db.getRecordList('rcField', 'id', "rcTable_id = '%s'" %forceString(tableId))))
        if hasFields:
            ok = QtGui.QMessageBox.question(self, u'Внимание!', u'Все поля таблицы %s будут удалены и заполнены новыми данными.'
                                                                u'Все отчёты перестанут работа.'
                                                                u'Уверены что хотите продолжить?' % tableName,
                                        QtGui.QMessageBox.Ok|QtGui.QMessageBox.Close, QtGui.QMessageBox.Close)
            if ok != QtGui.QMessageBox.Ok:
                return
            db.query(u"Delete From rcField where rcTable_id = '%s'" % forceString(tableId))
        initFields = CRCInitFields(self)
        fields = initFields.getTableFields(tableName)
        initFields.insertTableFields(tableId, fields)
        self.renewListAndSetTo(tableId)

class CRCTableEditor(CItemEditorBaseDialog, Ui_TableDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rcTable')
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setWindowTitleEx(u'Редактирование таблицы')

    def preSetupUi(self):
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)

    def postSetupUi(self):
        pass

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtName, record, 'name')
        setLineEditValue(self.edtTable, record, 'table')
        setTextEditValue(self.edtDescription, record, 'description')
        setLineEditValue(self.edtGroup, record, 'group')

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtName, record, 'name')
        getLineEditValue(self.edtTable, record, 'table')
        getTextEditValue(self.edtDescription, record, 'description')
        getLineEditValue(self.edtGroup, record, 'group')
        return record

    def saveInternals(self, id):
        pass

    def checkDataEntered(self):
        result = True
        name = forceStringEx(self.edtName.text())
        table = forceStringEx(self.edtTable.text())
        isAvailableTable = False
        try:
            isAvailableTable = forceBool(QtGui.qApp.db.table(forceString(self.edtTable.text())))
        except CDatabaseException:
            pass
        result = result \
                 and (name or self.checkInputMessage(u'наименование', False, self.edtName))\
                 and (table or self.checkInputMessage(u'таблицу', False, self.edtTable))\
                 and (isAvailableTable or self.checkValueMessage(u'Таблица с таким именем не существует.', False, self.edtTable))
        return result

    def on_edtName_textEdited(self, text):
        self.edtName.setText(text.replace(' ', '_'))

class CRCFieldEditor(CItemEditorBaseDialog, Ui_FieldDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rcField')
        self.refTables = []
        self.fields = []
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setWindowTitleEx(u'Редактирование поля таблицы')
        self.tableId = None
        self.oldRefId = 0


    def preSetupUi(self):
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowMaximizeButtonHint)

    def postSetupUi(self):
        self.chkVisible.setChecked(True)
        self.groupReference.setEnabled(False)
        self.loadReferenceData()

    def setTableId(self, tableId):
        self.tableId = tableId
        self.loadAvaliableFields(self.tableId)

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.tableId = forceInt(record.value('rcTable_id'))
        self.loadAvaliableFields(self.tableId)

        setLineEditValue(self.edtName, record, 'name')
        setTextEditValue(self.edtDescription, record, 'description')
        setCheckBoxValue(self.chkVisible, record, 'visible')
        currentField = forceString(record.value('field'))
        for index, field in enumerate(self.fields):
            if field == currentField:
                self.cmbField.setCurrentIndex(index)
                break
        ref_id = forceInt(record.value('ref_id'))
        self.chkHasReference.setChecked(forceBool(ref_id))
        self.setReferenceValue(ref_id)

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtName, record, 'name')
        getTextEditValue(self.edtDescription, record, 'description')
        getCheckBoxValue(self.chkVisible, record, 'visible')
        record.setValue('rcTable_id', toVariant(self.tableId))
        record.setValue('ref_id', toVariant(self.getReferenceValue()))
        record.setValue('field', toVariant((self.fields[self.cmbField.currentIndex()])))
        return record

    def saveInternals(self, id):
        newRefId = forceInt(QtGui.qApp.db.translate('rcField', 'id', id, 'ref_id'))
        self.updateLink(newRefId, self.oldRefId, id)

    def checkDataEntered(self):
        result = True
        name = forceStringEx(self.edtName.text())
        field = len(self.fields)
        result = result \
                 and (name or self.checkInputMessage(u'наименование', False, self.edtName)) \
                 and (field or self.checkValueMessage(u'Нет доступных полей', False, self.cmbField))
        return result

    def on_edtName_textEdited(self, text):
        self.edtName.setText(text.replace(' ', '_'))

    def loadAvaliableFields(self, tableId):
        db = QtGui.qApp.db
        tableName = forceString(db.translate('rcTable', 'id', tableId, '`table`'))
        existFields = [forceString(record.value('field')) for record in db.getRecordList('rcField', 'field', 'rcTable_id = %s' % forceString(tableId), isDistinct=True)]
        currentField = forceString(db.translate('rcField', 'id', self._id, 'field'))

        stmt = u'show full columns from %s' %tableName
        query = db.query(stmt)
        self.fields = []
        while query.next():
            record = query.record()
            field = forceString(record.value('Field'))
            if (not field in existFields) or (currentField and field == currentField):
                self.fields.append(field)
        self.resetCmb(self.cmbField, self.fields)

    def loadReferenceData(self):
        db = QtGui.qApp.db
        self.refTables = []
        for record in db.getRecordList('rcTable', ['id', 'name', '`table`']):
            id = forceInt(record.value('id'))
            fields = []
            for fieldRecord in db.getRecordList('rcField', ['id', 'name'], 'rcTable_id = %s' % id):
                fields.append((
                    forceInt(fieldRecord.value('id')), forceString(fieldRecord.value('name'))
                ))
            self.refTables.append((
                id, u'|'.join([forceString(record.value('name')), forceString(record.value('table'))]), fields
            ))

        self.resetCmb(self.cmbRefTable, [item[1] for item in self.refTables])

    def setReferenceValue(self, refId):
        self.oldRefId = refId
        for index, table in enumerate(self.refTables):
            id, name, fields = table
            for fieldIndex, field in enumerate(fields):
                fieldId, fieldName = field
                if fieldId == refId:
                    self.cmbRefTable.setCurrentIndex(index)
                    self.cmbRefField.setCurrentIndex(fieldIndex)

    def getReferenceValue(self):
        if self.chkHasReference.isChecked():
            tableIndex = self.cmbRefTable.currentIndex()
            fieldIndex = self.cmbRefField.currentIndex()
            curRefId = 0
            if tableIndex < len(self.refTables):
                fields = self.refTables[tableIndex][2]
                if fieldIndex < len(fields):
                    curRefId, name = fields[fieldIndex]
                    return curRefId
        return None

    def updateLink(self, newRefId, oldRefId, id):
        db = QtGui.qApp.db
        tableId = forceString(db.translate('rcField', 'id', id, 'rcTable_id'))
        newTableId = forceString(db.translate('rcField', 'id', newRefId, 'rcTable_id'))
        oldTableId = forceString(db.translate('rcField', 'id', oldRefId, 'rcTable_id'))
        tableName = forceString(db.translate('rcTable', 'id', db.translate('rcField', 'id', id, 'rcTable_id'), 'name'))
        if not tableName:
            return
        if newRefId == oldRefId:
            return
        if forceInt(newRefId) != 0:
            self.createLink(tableId, tableName, id, newTableId)
        if forceInt(oldRefId) != 0:
            self.deleteLink(tableId, tableName, id, oldTableId, oldRefId)

    def createLink(self, tableId, tableName, id, newTableId):
        db = QtGui.qApp.db
        if not db.getRecordEx('rcField', 'id', u'''
            rcTable_id = '%s' and name = '%s' and field = 'id' ''' %
                                       (newTableId, tableName)):
            stmt = u'''Insert Into rcField (`name`, `field`, `rcTable_id`, `ref_id`, `description`)
                values ('%s', '%s', '%s', '%s', '%s')''' % (tableName,
                                                            'id',
                                                            forceString(newTableId),
                                                            id,
                                                            u'%s: %s' % (forceString(db.translate('rcField', 'id', id, 'field')), tableName))
            db.query(stmt)

    def deleteLink(self, tableId, tableName, id, oldTableId, oldRefId):
        db = QtGui.qApp.db
        if not db.getRecordEx('rcField', 'id', u'''
            rcTable_id = '%s' and ref_id = '%s' ''' %
                                       (tableId, oldRefId)):
            stmt = u'''
            Delete From rcField
            Where rcTable_id = '%s' and name = '%s' and field = 'id' and ref_id = '%s' ''' % (oldTableId, tableName, id)
            db.query(stmt)

    def getRecordInfo(self, stmt, fields):
        db = QtGui.qApp.db
        query = db.query(stmt)
        result = {}
        if query.next():
            record = query.record()
            for field in fields:
                result[field] = forceString(record.value(field))
        return result

    def resetCmb(self, cmb, items):
        cmb.clear()
        for item in items:
            cmb.addItem(item)

    @QtCore.pyqtSlot(int)
    def on_chkHasReference_stateChanged(self, value):
        self.groupReference.setEnabled(value)

    def on_cmbRefTable_currentIndexChanged(self):
        index = self.cmbRefTable.currentIndex()
        if index < len(self.refTables):
            fields = self.refTables[index][2]
            self.resetCmb(self.cmbRefField, [field[1] for field in fields])


class CRCInitFields(object):
    """
    Create and fill table rcField depending on data from table rcTable
    """

    def __init__(self, parent):
        db = QtGui.qApp.db
        self.parent = parent
        self.existTables = self.getAllTablesFromDb()
        self.setTable()

    def setTable(self, tryCount=0):
        db = QtGui.qApp.db
        if tryCount == 2:
            raise ValueError(u"Can't create table `rcField`")
        try:
            self.table = db.table('rcField')
        except CDatabaseException:
            self.createTableRbField()
            if not tryCount:
                self.setTable(tryCount+1)


    def process(self):
        self.createTableRbField()
        self.tables = self.getTables()
        self.tableFields = self.getTablesFields()
        self.tableReferences = self.getTableReferences()
        self.tableFields = self.insertFields()
        self.insertReferences()
        self.postSetupRef()
        self.postSetupField()

    def createTableRbField(self):
        """
        Creation table rcField
        :return:
        """
        stmt = u"""
        Drop Table If exists rcField;
        CREATE TABLE rcField (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `createDatetime` datetime NOT NULL COMMENT 'Дата создания записи',
            `createPerson_id` int(11) DEFAULT NULL COMMENT 'Автор записи {Person}',
            `modifyDatetime` datetime NOT NULL COMMENT 'Дата изменения записи',
            `modifyPerson_id` int(11) DEFAULT NULL COMMENT 'Автор изменения записи {Person}',
            `deleted` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'Отметка удаления записи',
            `name` varchar(256) NOT NULL DEFAULT '' COMMENT 'Название',
            `field` varchar(256) NOT NULL DEFAULT '' COMMENT 'Поле',
            `ref_id` int(11) DEFAULT NULL COMMENT 'Автор изменения записи {rcField}',
            `rcTable_id` int(11) DEFAULT NULL COMMENT 'Таблица {rcTable}',
            `description` text COMMENT 'Описание поля',
            `visible` tinyint(1) DEFAULT 1 COMMENT 'Видимость',
            PRIMARY KEY (`id`),
            CONSTRAINT FOREIGN KEY (`ref_id`) REFERENCES `rcField` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
            CONSTRAINT FOREIGN KEY (`rcTable_id`) REFERENCES `rcTable` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Поля для запросов в конструкторе отчётов';
        """
        db = QtGui.qApp.db
        db.query(stmt)

    def postSetupField(self):
        db = QtGui.qApp.db
        fieldsInfo = []
        fieldsInfo.append({
            'name': u'Дней_в_неделе',
            'field': 'weekdays',
            'tableId': db.getIdList('rcTable', where="`table` = 'EventType'")[0],
            'description': u'weekdays: Количество дней в неделе'
        })
        fieldsInfo.append({
            'name': u'Код_ИНФИС',
            'field': 'infis',
            'tableId': db.getIdList('rcTable', where="`table` = 'rbService'")[0],
            'description': u'infis: Код_ИНФИС'
        })
        for fieldInfo in fieldsInfo:
            self.insertFieldRecord(fieldInfo)

    def postSetupInsertRef(self, table, field, refTable):
        """
        Insert into rcField in `ref_id` reference to refTable `id` field
        :param table:type unicode - table's name
        :param field:type unicode - referenced field
        :param refTable:type unicode - table's name reference to
        :return:
        """
        stmt = """
            set @id = (select id from rcField f where f.rcTable_id in (select t.id From rcTable t where t.`table` = '%s') and f.field = 'id' and name = 'id');
            Update rcField
            set ref_id = @id
            where field = '%s'
                and rcTable_id = (select t.id From rcTable t where t.`table` = '%s')
        """ % (refTable, field, table)
        db = QtGui.qApp.db
        db.query(stmt)

    def postSetupRef(self):
        """
        Insert references, which not announced in db
        :return:
        """
        self.postSetupInsertRef(u'Event', u'ksgService_id', u'rbService')
        self.postSetupInsertRef(u'ClientPolicy', u'insurer_id', u'Organisation')
        self.postSetupInsertRef(u'Event', u'MES_id', u'mes.mes')
        self.postSetupInsertRef(u'Contract', u'typeId', u'rbContractType')
        self.postSetupInsertRef(u'Account_item', u'service_id', u'rbService')
        self.postSetupInsertRef(u'Account', u'payer_id', u'Organisation')

    def getTables(self):
        """
        Getting table's info from table rcTable
        :return:
        dictionary {id: {'table': string,
                         'name': string,
                         'id': integer}}
        """
        db = QtGui.qApp.db
        self.updateTableNames()
        recordList = db.getRecordList(u'rcTable', [u'`id`', u'`table`', u'`name`'], 'deleted = 0')
        tables = {}
        for record in recordList:
            tables[forceRef(record.value('id'))] = {'table': forceString(record.value('table')),
                                                    'name': forceString(record.value('name')),
                                                    'id': forceRef(record.value('id'))}
        return tables

    def getAllTablesFromDb(self):
        db = QtGui.qApp.db
        dataBaseNames = [u'', u'mes', u'kladr']
        tables = []
        for dataBaseName in dataBaseNames:
            stmt = u'Show tables'
            if dataBaseName:
                stmt = u'Show tables From %s' % dataBaseName
            query = db.query(stmt)
            while query.next():
                record = query.record()
                tableName = forceString(record.value(0))
                if dataBaseName:
                    tableName = u'%s.%s' % (dataBaseName, tableName)
                tables.append(tableName)
        return tables

    def checkTableExists(self, tableName):
        for table in self.existTables:
            if table.lower() == tableName.lower():
                return table
        return None

    def updateTableNames(self):
        '''
        Update table's name in table 'rcTable'
        :return:
        '''
        db = QtGui.qApp.db
        recordList = db.getRecordList(u'rcTable', where='deleted = 0')
        tables = {}
        for record in recordList:
            tableName = forceString(record.value('table'))
            newTableName = self.checkTableExists(tableName)
            if tableName == newTableName:
                continue
            if newTableName:
                record.setValue('table', toVariant(newTableName))
            else:
                record.setValue('delete', toVariant(1))
            db.updateRecord(u'rcTable', record)

    def getTablesFields(self):
        """
        Getting field's info from database
        :return:
        dictionary {tableId:
                        {field:
                            {'name': first part from comment from db
                             'description': comment from db + field name
                             }
                        }
                    }
        """
        db = QtGui.qApp.db
        tablesFields = {}
        for id, table in self.tables.items():
            tableName = table.get('table', u'')
            tablesFields[id] = self.getTableFields(tableName)
        return tablesFields

    def getTableFields(self, tableName):
        if not tableName:
            return {}
        db = QtGui.qApp.db
        stmt = u'show full columns from %s' %tableName
        query = None
        try:
            query = db.query(stmt)
        except CDatabaseException:
            return {}
        fields = {}
        while query.next():
            record = query.record()
            fieldInfo = self.getFieldInfo(record)
            fields[fieldInfo.get('field', u'')] = fieldInfo
        return fields

    def getFieldInfo(self, record):
        '''
        Get field info from QRecord
        :param record:
        :return: dict:{'field': str,
                       'name': str,
                       'description': str}
        '''
        name = forceString(record.value('Comment'))
        field = forceString(record.value('Field'))
        description = u'%s: %s' % (field, name)
        nameList = [item for item in re.split('[\\\{\}\(\):;/\+-=\*]', name) if item]
        if len(nameList):
            name = nameList[0].strip()
        additionalInfo = re.search('(\d+ ?\- ?)', name, re.U)
        if additionalInfo:
            name = field
        name = re.sub('[ \.,]', '_', forceStringEx(name))
        if field == u'id':
            name = u'id'
        if not name:
            name = field
        return {
            'field': field,
            'name': name,
            'description': description}

    def getTableReferences(self):
        """
        Getting references between tables from create query
        :return:
        dictionary {tableId: {
                        'filed': referenced field
                        'refTable': table reference to
                        'refField': field reference to
                        }
                    }
        """
        db = QtGui.qApp.db
        tableReferences = {}
        for id, table in self.tables.items():
            tableName = table.get('table', u'')
            if not tableName:
                break
            query = None
            try:
                query = db.query('SHOW CREATE TABLE %s;' %tableName)
            except CDatabaseException:
                continue
            while query.next():
                record = query.record()
                text = forceString(record.value('Create Table'))
                text = re.sub('[\n]', ' ', text)
                lines = [line.strip() for line in text.split(',')]
                references = []
                for line in lines:
                    ref = {}
                    if re.search('constraint', line, re.IGNORECASE):
                        ref['field'] = re.search('foreign key \(`\w+`\)', line, re.IGNORECASE).group().split('`')[1]
                        ref['refTable'] = re.search('references `\w+` \(`\w+`\)', line, re.IGNORECASE).group().split('`')[1]
                        ref['refField'] = re.search('references `\w+` \(`\w+`\)', line, re.IGNORECASE).group().split('`')[3]
                    if ref:
                        references.append(ref)
            tableReferences[id] = references
        return tableReferences

    def insertFieldRecord(self, recordInfo):
        db = QtGui.qApp.db
        record = self.table.newRecord()
        name = recordInfo.get('name')
        field = recordInfo.get('field')
        tableId = recordInfo.get('tableId')
        description = recordInfo.get('description')
        visible = recordInfo.get('visible')
        record.setValue('name', toVariant(name))
        record.setValue('field', toVariant(field))
        record.setValue('rcTable_id', toVariant(tableId))
        record.setValue('description', toVariant(description))
        record.setValue('visible', toVariant(visible))
        field_id = db.insertRecord(self.table, record)
        return {
            field_id:
            {
                'field': field,
                'name': name,
                'id': field_id,
                'description': description,
                'visible': visible
            }
        }

    def insertFields(self):
        result = {}
        for id, table in self.tables.items():
            fields = self.tableFields.get(id, {})
            result[id] = self.insertTableFields(id, fields)
        return result

    def insertTableFields(self, tableId, fields):
        newFields = {}
        for field, value in sorted(fields.items(), key=lambda tup: tup[1].get('name', u'')):
            fieldInfo = {'name': value.get('name', u''),
                         'field': field,
                         'tableId': tableId,
                         'description': value.get('description', u'')
                         }
            newFields.update(self.insertFieldRecord(fieldInfo))
        return newFields

    def insertReference(self, idFrom, idTo):
        db = QtGui.qApp.db
        if idFrom and idTo:
            stmt = u"""
                Update %s
                    set ref_id = %d
                Where id = %d;""" %(self.table.name(), idFrom, idTo)
            db.query(stmt)

    def insertReferences(self):
        insertedReferences = {}
        for id, table in self.tables.items():
            references = self.tableReferences.get(id, [])
            fields = self.tableFields.get(id, {})
            for ref in references:
                fieldId = self.getFieldId(fields, ref.get('field', u''))
                refTableId = self.getTableId(self.tables, ref.get('refTable', u''))
                refFieldId = self.getFieldId(self.tableFields.get(refTableId, {}), ref.get('refField', u''))
                self.insertReference(refFieldId, fieldId)
                self.tableFields.get(refTableId, {})
                if refFieldId and refTableId and fieldId and not insertedReferences.get((id, refFieldId, refTableId), 0):
                    fieldInfo = {'name': table.get('name', u''),
                                 'field': u'id',
                                 'tableId': refTableId,
                                 'description': u'id: ссылка на %s.%s' %(ref.get('table', u''), ref.get('field, u''')),
                                 'visible': 0 if ref.get('field') in ['createPerson_id', 'modifyPerson_id'] else 1}
                    newField = self.insertFieldRecord(fieldInfo)
                    fields.update(newField)
                    if newField:
                        newFieldId = newField.keys()[0]
                        self.insertReference(fieldId, newFieldId)
                        insertedReferences[(id, refFieldId, refTableId)] = insertedReferences.get((id, refFieldId, refTableId), 0) + 1
                insertedReferences[(id, refFieldId, refTableId)] = insertedReferences.get((id, refFieldId, refTableId), 0) + 1

    def getTableId(self, tables, value):
        return self.getItem(tables, 'table', value).get('id', 0)

    def getFieldId(self, fields, value):
        return self.getItem(fields, 'field', value).get('id', 0)

    def getItem(self, items, key, value):
        for id, item in sorted(items.items(), key=lambda t: t[0]):
            if item.get(key, u'').lower() == value.lower():
                return item
        return {}