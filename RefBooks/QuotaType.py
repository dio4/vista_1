# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Ui_QuotaTypeEditor import Ui_QuotaTypeEditorDialog
from library.HierarchicalItemsListDialog import CHierarchicalItemsListDialog
from library.ItemsListDialog import CItemEditorBaseDialog
from library.TableModel import CTableModel, CCol, CBoolCol, CEnumCol, CRefBookCol, CTextCol
from library.TreeModel import CDBTreeItemWithClass, CDragDropDBTreeModelWithClassItems
from library.Utils import forceInt, forceRef, forceString, forceStringEx, toVariant, formatRecordsCount
from library.interchange import getComboBoxValue, getLineEditValue, setComboBoxValue, setLineEditValue, setTextEditValue


class CQuotaTypeList(CHierarchicalItemsListDialog):
    def __init__(self, parent):
        CHierarchicalItemsListDialog.__init__(self, parent, [
            CEnumCol(u'Класс', ['class'], getQuotaTypeClassNameList(), 10),
            CQuotaTypeRefBookCol(u'Вид', ['group_code'], 'QuotaType', 10),
            CTextCol(u'Код', ['code'], 20),
            CBoolCol(u'Устаревший', ['isObsolete'], 10),
            CTextCol(u'Наименование', ['name'], 40)
        ], 'QuotaType', ['class', 'group_code', 'code', 'name', 'id'])
        self.setWindowTitleEx(u'Виды квот')
        self.expandedItemsState = {}
        self.setSettingsTblItems()
        self.additionalPostSetupUi()
        self.tblItems.addPopupDelSelectedRow()

    def setSettingsTblItems(self):
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

    def preSetupUi(self):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.addModels('Tree', CQuotaTypeTreeModel(self, self.tableName, 'id', 'group_code', 'name', 'class', self.order))
        self.addModels('Table', CTableModel(self, self.cols, self.tableName))
        self.modelTree.setLeavesVisible(True)
        self.actDelete = QtGui.QAction(u'Удалить', self)
        self.actDelete.setObjectName('actDelete')

    def additionalPostSetupUi(self):
        self.treeItems.expand(self.modelTree.index(0, 0))
        # drag-n-drop support
        self.treeItems.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.connect(self.modelTree, QtCore.SIGNAL('saveExpandedState()'), self.saveExpandedState)
        self.connect(self.modelTree, QtCore.SIGNAL('restoreExpandedState()'), self.restoreExpandedState)

    def select(self, props=None):
        db = QtGui.qApp.db
        table = self.modelTable.table()
        groupId = self.currentGroupId()
        groupCond = db.translate(table, 'id', groupId, 'code')
        className = self.currentClass()
        cond = [table['group_code'].eq(groupCond)]
        cond.append(table['deleted'].eq(0))
        cond.append(table['class'].eq(className))
        idList = QtGui.qApp.db.getIdList(table.name(), 'id', cond, self.order)
        self.lblCountRows.setText(formatRecordsCount(len(idList)))
        return idList

    def currentClass(self):
        return self.modelTree.itemClass(self.treeItems.currentIndex())

    def currentItem(self):
        return self.treeItems.currentIndex().internalPointer()

    def getItemEditor(self):
        return CQuotaTypeEditor(self)

    @QtCore.pyqtSlot()
    def on_btnNew_clicked(self):
        dialog = self.getItemEditor()
        dialog.setClass(self.currentClass())
        dialog.setGroupId(self.currentGroupId())
        dialog.setIsNew(True)
        dialog.setInputCodeSettings()
        if dialog.exec_():
            itemId = dialog.itemId()
            self.modelTree.update()
            self.renewListAndSetTo(itemId)


class CQuotaTypeRefBookCol(CRefBookCol):
    def format(self, values):
        parentCode = forceString(values[0])
        if parentCode:
            return QtGui.qApp.db.translate('QuotaType', 'code', parentCode, 'name')
        else:
            return CCol.invalid


class CQuotaTypeEditor(CItemEditorBaseDialog, Ui_QuotaTypeEditorDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'QuotaType')
        self.setupUi(self)
        self._applyQuotaTypeClassComboBox()
        self.setWindowTitleEx(u'Вид квоты')
        self.isNew = False
        self.oldCode = None
        self.cmbGroup.setTable('QuotaType')
        self.setupDirtyCather()

    def _applyQuotaTypeClassComboBox(self):
        self.cmbClass.blockSignals(True)
        for className, value in quotaTypeClassItems:
            self.cmbClass.addItem(className)
        self.cmbClass.blockSignals(False)

    def exec_(self):
        result = CItemEditorBaseDialog.exec_(self)
        return result

    def setIsNew(self, val):
        self.isNew = val

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setTextEditValue(self.edtName, record, 'name')
        setComboBoxValue(self.cmbClass, record, 'class')
        self.cmbGroup.setCode(forceString(record.value('group_code')))
        self.setInputCodeSettings()
        setLineEditValue(self.edtCode, record, 'code')
        self.oldCode = self.edtCode.text()
        self.setIsDirty(False)

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        getLineEditValue(self.edtCode, record, 'code')
        record.setValue('name', QtCore.QVariant(self.edtName.toPlainText().replace('\n', ' ')))
        group_code = self.cmbGroup.code()
        if group_code != '0':
            record.setValue('group_code', QtCore.QVariant(group_code))
        else:
            record.setValue('group_code', QtCore.QVariant())
        getComboBoxValue(self.cmbClass, record, 'class')
        return record

    def setInputCodeSettings(self):
        # parentCode = self.cmbGroup.code()
        # if parentCode:
        #     if parentCode != '0':
        #         inputMask = parentCode+'.'+'9'*(15-len(parentCode))
        #     else:
        #         inputMask = '9'*16
        # else:
        #     inputMask = ''
        # self.edtCode.setInputMask(inputMask)
        pass

    def setClass(self, _class):
        self.cmbClass.setCurrentIndex(_class)

    def setGroupId(self, groupId):
        self.cmbGroup.setValue(groupId)

    def checkDataEntered(self):
        result = True
        code = forceStringEx(self.edtCode.text())
        name = forceStringEx(self.edtName.toPlainText())
        result = result and (code or self.checkInputMessage(u'код', False, self.edtCode))
        result = result and (name or self.checkInputMessage(u'наименование', False, self.edtName))
        if self.isNew or code != self.oldCode:
            result = result and self.checkUniqueCode(code)
        return result

    def checkUniqueCode(self, code):
        db = QtGui.qApp.db
        parentCode = self.cmbGroup.code()
        if parentCode == '0':
            stmt = db.selectStmt(self._tableName, 'code', 'group_code IS NULL')
        else:
            stmt = db.selectStmt(self._tableName, 'code', 'group_code=%s' % parentCode)
        query = db.query(stmt)
        result = []
        while query.next():
            result.append(query.value(0).toString())
        if code in result:
            QtGui.QMessageBox.warning(self,
                                      u'Внимание!',
                                      u'Данный код уже существует',
                                      QtGui.QMessageBox.Ok,
                                      QtGui.QMessageBox.Ok)
            return False
        return True

    @QtCore.pyqtSlot(int)
    def on_cmbClass_currentIndexChanged(self, classCode):
        fiter = 'class=%d and deleted = 0' % classCode
        self.cmbGroup.setFilter(fiter)


quotaTypeClassItems = (
    (u'ВТМП', 0),
    (u'СМП', 1),
    (u'Родовой сертификат', 2),
    (u'Платные', 3),
    (u'ОМС', 4),
    (u'ВМП из ОМС', 5),
    (u'ВМП сверх базового', 6),
    (u'АКИ', 7)
)
quotaTypeClassItemsByExists = None


def getQuotaTypeClassItemsByExists():
    global quotaTypeClassItemsByExists
    if quotaTypeClassItemsByExists is None:
        quotaTypeClassItemsByExists = []
        db = QtGui.qApp.db
        table = db.table('QuotaType')
        for name, _class in quotaTypeClassItems:
            if bool(db.getCount(table, table['id'].name(), table['class'].eq(_class))):
                quotaTypeClassItemsByExists.append((name, _class))
        quotaTypeClassItemsByExists = tuple(quotaTypeClassItemsByExists)
    return quotaTypeClassItemsByExists


def getQuotaTypeClassNameList():
    return [name for name, _class in quotaTypeClassItems]


class CQuotaTypeTreeModel(CDragDropDBTreeModelWithClassItems):
    def __init__(self, parent, tableName, idColName, groupColName, nameColName, classColName, order=None):
        CDragDropDBTreeModelWithClassItems.__init__(self, parent, tableName, idColName, groupColName, nameColName,
                                                    classColName, order)
        self.setClassItems(quotaTypeClassItems)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(u'Вид квоты')
        return QtCore.QVariant()

    def loadChildrenItems(self, group):
        result = []
        if group == self.getRootItem():
            result = self.classItems
        else:
            db = QtGui.qApp.db
            table = db.table(self.tableName)
            children = table.alias(self.tableName + '_children')
            children_alias = table.alias(self.tableName + '_children2')
            alias = table.alias(self.tableName + '2')
            groupCond = db.translate(table, 'id', group._id, 'code')
            cond = [
                table[self.groupColName].eq(groupCond),
                table[self.classColName].eq(group.className)
            ]
            if table.hasField('deleted'):
                cond.append(table['deleted'].eq(0))
            if table.hasField('isObsolete'):
                cond.append(table['isObsolete'].eq(0))
            if not self.leavesVisible:
                cond.append(db.existsStmt(alias, alias[self.groupColName].eq(table['code'])))
            for record in db.getRecordList(
                    table,
                    [
                        self.idColName, self.nameColName,
                        '(' + db.selectStmt(
                            children,
                            db.count('*'),
                            [
                                 table['code'].eq(children[self.groupColName]),
                                children['deleted'].eq(0) if children.hasField('deleted') else '1=1',
                                children[self.classColName].eq(group.className),
                                children['isObsolete'].eq(0) if table.hasField('isObsolete') else '1=1',
                                '1=1' if self.leavesVisible else db.existsStmt(children_alias, children_alias[self.groupColName].eq(children['code']))
                            ]
                        ) + ')'
                     ],
                    cond,
                    self.order
            ):
                id = forceRef(record.value(0))
                name = forceString(record.value(1))
                childrenCount = forceInt(record.value(2))
                result.append(CDBTreeItemWithClass(group, name, id, group.className, self, childrenCount=childrenCount))
        return result

    def dropMimeData(self, data, action, row, column, parentIndex):
        if action == QtCore.Qt.IgnoreAction:
            return True

        if not data.hasText():
            return False

        dragId = forceRef(forceInt(data.text()))
        parentId = self.itemId(parentIndex)
        parentClass = self.itemClass(parentIndex)

        self.changeParent(dragId, parentId, parentClass)
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex,QModelIndex)'), parentIndex, parentIndex)
        return True

    def changeParent(self, id, parentId, parentClass):
        if not (parentId in self.getItemIdList(self.findItemId(id))):
            db = QtGui.qApp.db
            table = db.table(self.tableName)
            parentCode = forceString(db.translate(table, 'id', parentId, 'code'))
            oldCode = forceString(db.translate(table, 'id', id, 'code'))
            newCode = self.getNewCode(oldCode, parentCode)
            record = db.getRecord(table, [self.idColName, self.groupColName, self.classColName, 'code'], id)
            if record:
                self.emit(QtCore.SIGNAL('saveExpandedState()'))
                childIdList = db.getIdList(table, 'id', table['group_code'].eq(oldCode))
                variantParentCode = toVariant(parentCode) if parentCode else QtCore.QVariant()
                record.setValue(self.groupColName, variantParentCode)
                record.setValue(self.classColName, toVariant(parentClass))
                record.setValue('code', toVariant(newCode))
                db.updateRecord(table, record)
                for childId in childIdList:
                    self.changeChildren(childId, id, parentClass)
                self.reset()
                self.update()
                self.emit(QtCore.SIGNAL('restoreExpandedState()'))

    def changeChildren(self, id, parentId, parentClass):
        db = QtGui.qApp.db
        table = db.table(self.tableName)
        parentCode = forceString(db.translate(table, 'id', parentId, 'code'))
        oldCode = forceString(db.translate(table, 'id', id, 'code'))
        newCode = self.getNewCode(oldCode, parentCode)
        record = db.getRecord(table, [self.idColName, self.groupColName, self.classColName, 'code'], id)
        if record:
            variantParentCode = toVariant(parentCode) if parentCode else QtCore.QVariant()
            record.setValue(self.groupColName, variantParentCode)
            record.setValue(self.classColName, toVariant(parentClass))
            record.setValue('code', toVariant(newCode))
            db.updateRecord(table, record)
            self.reset()
            self.update()
            childIdList = db.getIdList(table, 'id', table['group_code'].eq(oldCode))
            for childId in childIdList:
                self.changeChildren(childId, id, parentClass)

    def getNewCode(self, oldCode, parentCode):
        db = QtGui.qApp.db
        table = db.table(self.tableName)
        codeList = db.getRecordList(table, 'code', table['group_code'].eq(parentCode))
        oldCodeParts = oldCode.split('.')
        lastPartOldCode = oldCodeParts[len(oldCodeParts) - 1]
        max = 0
        exists = False
        for code in codeList:
            codeParts = forceString(code.value('code')).split('.')
            lastCodePart = codeParts[len(codeParts) - 1]
            if lastPartOldCode == lastCodePart:
                exists = True
            if max < int(lastCodePart):
                max = int(lastCodePart)
        if exists:
            newCode = parentCode + '.' + str(max + 1) if parentCode else str(max + 1)
        else:
            newCode = parentCode + '.' + lastPartOldCode if parentCode else lastPartOldCode
        return newCode
