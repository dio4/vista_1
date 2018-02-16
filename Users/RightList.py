# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from GUIHider.GUITreeModel import CGuiHidderTreeModel
from GUIHider.VisibleStateManager import CVisibleStateManager
from Ui_RightsEdit import Ui_UserRightsEditDialog
from library.InDocTable import CInDocTableModel, CRBInDocTableCol
from library.ItemsListDialog import CItemEditorBaseDialog, CItemEditorDialog, CItemsListDialog, CItemsListDialogEx
from library.TableModel import CTextCol
from library.Utils import forceRef, forceString, forceStringEx, forceDateTime, toVariant
from library.crbcombobox import CRBComboBox


class CUserRightListDialog(CItemsListDialog):
    """ Диалог со списоком всех возможных прав, которыми может обладать
        пользователь. Позволяет добавлять, изменять права (код и имя)"""

    def __init__(self, parent):
        CItemsListDialog.__init__(self, parent, [
            CTextCol(u'Код', ['code'], 10),
            CTextCol(u'Название', ['name'], 50)],
                                  'rbUserRight', ['name'])
        self.setWindowTitle(u'Список привилегий пользователей системы')

    def getItemEditor(self):
        editor = CItemEditorDialog(self, 'rbUserRight')
        editor.setWindowTitle(u'Привилегия пользователя')
        return editor


class CUserRightProfileListDialog(CItemsListDialogEx):
    """ Диалог со списоком всех возможных профилей прав, которые можно
        присваивать пользователям. Позволяет добавлять, изменять профили. """

    def __init__(self, parent):
        super(CUserRightProfileListDialog, self).__init__(parent,
                                                          [CTextCol(u'Название профиля', ['name'], 10)],
                                                          'rbUserProfile',
                                                          ['name'],
                                                          multiSelect=False)
        self.setWindowTitle(u'Список профилей прав пользователей системы')

    def getItemEditor(self):
        return CUserProfileEditDialog(self)

    def duplicateCurrentRow(self):
        currentItemId = self.tblItems.currentItemId()
        newItemId = super(CUserRightProfileListDialog, self).duplicateCurrentRow()
        db = QtGui.qApp.db
        for slaveTable in [db.table('rbUserProfile_Hidden'),
                           db.table('rbUserProfile_Right')]:
            db.transaction()
            try:
                newRecords = []
                for record in db.iterRecordList(slaveTable, '*', slaveTable['master_id'].eq(currentItemId)):
                    record.setValue('master_id', toVariant(newItemId))
                    record.setValue('id', toVariant(None))
                    newRecords.append(record)
                db.insertMultipleRecords(slaveTable, newRecords)
                db.commit()
            except:
                db.rollback()
        return newItemId


class CUserProfileEditDialog(CItemEditorBaseDialog, Ui_UserRightsEditDialog):
    """ Диалог для редактирования профиля - позволяет изменить имя профиля,
        а так же добавить в него различные права"""

    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbUserProfile')
        self.setupUi(self)
        self.addModels('Rights', CRightsModel(self))
        self.addModels(u'GUIHiddenWidgets', CVisibleStateManager().model())
        self.modelGUIHiddenWidgets.setEditable(False)
        self.setModels(self.tblRights, self.modelRights, self.selectionModelRights)
        self.setModels(self.tvVisibleGUIElements,
                       self.modelGUIHiddenWidgets,
                       self.selectionModelGUIHiddenWidgets)
        self.tblRights.addPopupDelRow()
        self.tvVisibleGUIElements.hideColumn(CGuiHidderTreeModel.ciName)
        self.setupDirtyCather()

    ## Обновляет иерархический список скрываемых элементов для этого профиля
    def updateGUIHiddenWidgetsModel(self):
        db = QtGui.qApp.db
        tableUPH = db.table('rbUserProfile_Hidden')

        hiddenNameList = [forceString(record.value('objectName'))
                          for record in db.iterRecordList(tableUPH, tableUPH['objectName'], tableUPH['master_id'].eq(self.itemId()))]
        self.modelGUIHiddenWidgets.updateCheckStateByNameList(hiddenNameList, newCheckState=QtCore.Qt.Unchecked)
        self.modelGUIHiddenWidgets.reset()

    ## Сохраняет настройки скрытия элементов интерфейса для текущего профиля прав
    def saveGUIHiddenWidgets(self):
        if not self.itemId():
            return False

        db = QtGui.qApp.db
        tableUPH = db.table('rbUserProfile_Hidden')

        try:
            db.transaction()
            db.deleteRecord(tableUPH, where=[tableUPH['master_id'].eq(self.itemId())])

            curDatetime = QtCore.QDateTime.currentDateTime()
            userProfileId = self.itemId()

            fields = ['master_id', 'objectName', 'createDatetime', 'modifyDatetime']
            values = [(userProfileId,
                       objectName,
                       curDatetime,
                       curDatetime) for objectName in self.modelGUIHiddenWidgets.itemNameList(checkState=QtCore.Qt.Unchecked)]
            db.insertValues(tableUPH, fields, values)
            db.commit()
        except:
            db.rollback()
            QtGui.qApp.logCurrentException()
            return False

        return True

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtName.setText(forceString(record.value('name')))
        self.modelRights.loadItems(self.itemId())
        self.updateGUIHiddenWidgetsModel()
        self.setIsDirty(False)

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        name = forceStringEx(self.edtName.text())
        record.setValue('name', toVariant(name))
        return record

    def saveInternals(self, id):
        self.modelRights.saveItems(id)
        self.saveGUIHiddenWidgets()

    def afterSave(self):
        if QtGui.qApp.userInfo and QtGui.qApp.userHasProfile(self.itemId()):
            QtGui.qApp.userInfo.reloadRightsAndHiddenUI()
        super(CUserProfileEditDialog, self).afterSave()

    def checkDataEntered(self):
        result = True
        name = forceStringEx(self.edtName.text())
        result = result and (name or self.checkInputMessage(u'название профиля прав', True, self.edtName))
        if result:
            presentRights = []
            for row, record in enumerate(self.modelRights.items()):
                result = self.checkAccountDataEntered(row, record, presentRights)
                if not result:
                    break
        return result

    def checkAccountDataEntered(self, row, record, presentRights):
        result = True
        rightId = forceRef(record.value('userRight_id'))
        if not rightId:
            result = self.checkValueMessage(u'Необходимо указать привилегию пользователя', False, self.tblRights, row, 0)
        if result and rightId in presentRights:
            result = self.checkValueMessage(u'Привилегия уже есть в профиле', False, self.tblRights, row, 0)
        if result:
            presentRights.append(rightId)
        return result


class CRightsModel(CInDocTableModel):
    __pyqtSignals__ = ('documentChanged(int)',
                       )

    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbUserProfile_Right', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Код', 'userRight_id', 10, 'rbUserRight', showFields = CRBComboBox.showCode))
        self.addCol(CRBInDocTableCol(u'Название привилегии пользователя', 'userRight_id', 30, 'rbUserRight'))
        self.addHiddenCol('createDatetime')
        self.addHiddenCol('createPerson_id')

    def saveItems(self, masterId):
        if self._items is not None:
            db = QtGui.qApp.db
            table = self._table

            db.transaction()
            try:
                db.deleteRecord(table, table[self.masterIdFieldName].eq(masterId))

                curDatetime = QtCore.QDateTime.currentDateTime()

                updateFields = ['createDatetime', 'createPerson_id', 'modifyDatetime', 'modifyPerson_id',   'master_id', 'userRight_id']
                fields = ['id'] + updateFields
                values = [
                    (forceRef(rec.value('id')),
                     forceDateTime(rec.value('createDatetime')) or curDatetime,
                     forceRef(rec.value('createPerson_id')) or QtGui.qApp.userId,
                     curDatetime,
                     QtGui.qApp.userId,
                     masterId,
                     forceRef(rec.value('userRight_id'))
                     )
                    for rec in self._items
                ]
                db.insertValues(table, fields, values, updateFields=updateFields)
                db.commit()
            except Exception:
                db.rollback()

            self.setDirty(False)
