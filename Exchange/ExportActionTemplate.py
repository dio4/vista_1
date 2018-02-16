#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.TableModel import *
from library.TreeModel import *
from library.DialogBase import CConstructHelperMixin
from Orgs.Utils import getPersonInfo

from Utils import *

from Ui_ExportActionTemplate_Wizard_1 import Ui_ExportActionTemplate_Wizard_1
from Ui_ExportActionTemplate_Wizard_2 import Ui_ExportActionTemplate_Wizard_2


def ExportActionTemplate():
    fileName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportActionTemplateFileName', ''))
    exportAll = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportActionTemplateExportAll', 'False'))
    compressRAR = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportActionTemplateCompressRAR', 'False'))
    dlg = CExportActionTemplate(fileName, exportAll,  compressRAR)
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ExportActionTemplateFileName'] = toVariant(dlg.fileName)
    QtGui.qApp.preferences.appPrefs['ExportActionTemplateExportAll'] = toVariant(dlg.exportAll)
    QtGui.qApp.preferences.appPrefs['ExportActionTemplateCompressRAR'] = toVariant(dlg.compressRAR)


actionPropertyTypeFields = ('id', 'idx', 'name', 'descr', 'typeName', 'valueDomain',
                        'defaultValue', 'isVector', 'norm', 'sex', 'age', 'penalty', 'visibleInJobTicket', 'isAssignable')

actionPropertyTypeRefFields = ('actionType_id', 'template_id', 'unit_id')

actionPropertyTemplateFields = ('parentCode', 'code', 'federalCode', 'regionalCode',
                        'name')

actionTemplateFields = ('code', 'name', 'sex',  'age')
actionFields = ('status', 'note', 'office', 'amount')
actionRefFields = ('actionType_id', )
actionTypeFields = ('code',  'name',  'class')
actionTypeRefFields = ('id', 'group_id')

unitFields = ('code',  'name')
specialityFields = ('code',  'name')
ownerFields = ('lastName',  'firstName',  'patrName',
                            'specialityName',  'postName')


def getActionPropertyValue(id, typeName):
    db = QtGui.qApp.db

    if typeName in ('Text', 'Constructor', u'Жалобы'):
        typeName = 'String'

    if typeName == 'RLS':
        typeName = 'Integer'

    record = db.getRecord('ActionProperty_%s' % typeName, 'value', id)
    if record:
        return forceString(record.value('value'))
    return None


class CMyXmlStreamWriter(QXmlStreamWriter):
    def __init__(self,  parent, idList):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self._idList = idList
        self.nestedGroups = []
        self.templatesMap = {}
        self.specialityMap = {}
        self.actionPropertyTypeMap = {}
        self.actionPropertyTemplateMap = {}
        self.unitMap = {}
        self.ownerMap = {}
        self.db = QtGui.qApp.db
        self.actionTypeRecursionLevel = 0


    def getAbstractRecordInfo(self,  id,  cache, tableName,  fieldsList):
        if cache.has_key(id):
            return cache[id]

        record = self.db.getRecord(tableName,'*',  id)

        if record:
            info = {}
            for x in fieldsList:
                info[x] = forceString(record.value(x))

            cache[id] = info
            return info

        return None


    def getActionPropertyTypeInfo(self,  id):
        return self.getAbstractRecordInfo(id,  self.actionPropertyTypeMap,
            'ActionPropertyType',  actionPropertyTypeFields+actionPropertyTypeRefFields)


    def getUnitInfo(self,  id):
        return self.getAbstractRecordInfo(id,  self.unitMap,  'rbUnit',  unitFields)


    def getSpecialityInfo(self,  id):
        return self.getAbstractRecordInfo(id, self.specialityMap, 'rbSpeciality', specialityFields)


    def getActionPropertyTemplateInfo(self,  id):
        return self.getAbstractRecordInfo(id,  self.actionPropertyTemplateMap,
            'ActionPropertyTemplate',  actionPropertyTemplateFields)


    def writeActionProperty(self,  record):
        self.writeStartElement('ActionProperty')
        self.writeAttribute('norm',  forceString(record.value('norm')))
        typeId = forceRef(record.value('type_id'))
        unitId = forceRef(record.value('unit_id'))
        id = forceRef(record.value('id'))

        if typeId:
            typeInfo = self.getActionPropertyTypeInfo(typeId)

            if typeInfo:

                templateId = forceRef(typeInfo['template_id'])
                typeId = forceRef(typeInfo['actionType_id'])
                typeName = typeInfo['typeName']
                if typeName == 'JobTicket': typeName = 'Job_Ticket'
                propertyValue = getActionPropertyValue(id,  typeName)

                if propertyValue:
                    self.writeAttribute('value',  propertyValue)

                self.writeStartElement('ActionPropertyType')

                for x in actionPropertyTypeFields:
                    if typeInfo.has_key(x):
                        self.writeAttribute(x,  typeInfo[x])

                if templateId:
                    self.writeTemplateInfo(templateId)

                if typeId:
                    self.writeActionType(typeId)

                self.writeEndElement() # ActionPropertyType

        if unitId:
            unitInfo = self.getUnitInfo(unitId)

            if unitInfo:
                self.writeStartElement('Unit')

                for x in unitFields:
                    if unitInfo.has_key(x):
                        self.writeAttribute(x, unitInfo[x])

                self.writeEndElement()

        self.writeEndElement()


    def writeTemplateInfo(self,  templateId):
        u""" Двигается по дереву шаблонов к корню и пишет все коды.
            Для однозначной идентификации шаблона.
            Код класса: подгруппа [, ...], шаблон """

        groupId = templateId
        groupsList = []

        while groupId:
            if self.templatesMap.has_key(groupId):
                (groupCode,  groupId) = self.templatesMap[groupId]
            else:
                record = self.db.getRecord('ActionPropertyTemplate',  \
                    'group_id, code',  groupId)
                if not record:
                    break

                oldGroupId = groupId
                groupId = forceInt(record.value('group_id'))
                groupCode = u''+forceString(record.value('code'))
                if groupId:
                    self.templatesMap[oldGroupId] = (groupCode,  groupId)

            groupsList.insert(0, groupCode)

        self.writeStartElement('PropertyTemplate')
        self.writeAttribute('fullCode',  u'|'.join([et for et in groupsList]))

        templateInfo = self.getActionPropertyTemplateInfo(templateId)

        if templateInfo:
            for x in actionPropertyTemplateFields:
                if templateInfo.has_key(x):
                    self.writeAttribute(x, templateInfo[x])

        self.writeEndElement()


    def createQuery(self,  idList):
        db = QtGui.qApp.db
        tableAccountItem = db.table('ActionTemplate')
        stmt = u'''
        SELECT  a.code AS `code`,
                a.name AS `name`,
                a.sex AS `sex`,
                a.age AS age,
                a.id AS id,
                a.group_id AS group_id,
                a.owner_id AS owner_id,
                a.speciality_id AS speciality_id,
                a.action_id AS action_id
        FROM ActionTemplate AS a
        WHERE a.deleted = 0'''

        if idList:
            stmt+=u' AND a.id in ('+', '.join([str(et) for et in idList])+')'

        query = db.query(stmt)
        return query


    def getActionPropertyList(self, action_id):
#        u''' Создает запрос для обработки свойств типа действия.
#            Здесь считаем что элемент таблицы едниц измерения (rbUnit)
#            однозначно определяется по коду и имени, а элемент таблицы
#            шаблонов типов действий (ActionPropertyTemplate) - по коду.'''

        table = self.db.table('ActionProperty')
        recordList = self.db.getRecordList(table, where=\
            table['action_id'].eq(action_id))
        return recordList


    def processActionProperties(self, action_id):
        propertyList = self.getActionPropertyList(action_id)
        for record in propertyList:
            self.writeActionProperty(record)


    def writeAction(self,  id):
        record = self.db.getRecord('Action', actionFields + actionRefFields,   id)

        if record:
            self.writeStartElement('Action')

            for x in actionFields:
                self.writeAttribute(x, forceString(record.value(x)))

            actionTypeId = forceRef(record.value('actionType_id'))

            if actionTypeId:
                self.writeActionType(actionTypeId)

            self.processActionProperties(id)
            self.writeEndElement()


    def writeActionType(self,  id):
        record = self.db.getRecord('ActionType', actionTypeFields+actionTypeRefFields,   id)

        if record:
            self.writeStartElement('ActionType')

            for x in actionTypeFields:
                self.writeAttribute(x, forceString(record.value(x)))

            groupId = forceRef(record.value('group_id'))

            if groupId:
                if self.actionTypeRecursionLevel < 30:
                    self.actionTypeRecursionLevel += 1
                    self.writeActionType(groupId)
                    self.actionTypeRecursionLevel -= 1

            self.writeEndElement()


    def writeRecord(self, record):
        self.writeStartElement('ActionTemplate')

        # все свойства экспортируем как атрибуты
        for x in actionTemplateFields:
            self.writeAttribute(x, forceString(record.value(x)))

        # все, что определяется ссылками на другие таблицы - как элементы
        # группа экспортируемого элемента:
        groupId = forceRef(record.value('group_id'))
        ownerId = forceRef(record.value('owner_id'))
        specialityId = forceRef(record.value('speciality_id'))
        actionId = forceRef(record.value('action_id'))
        id  = forceRef(record.value('id'))

        if id == groupId:
            QtGui.QMessageBox.critical (self.parent,
                u'Ошибка в логической структуре данных',
                u'Элемент id=%d: (%s) "%s", group_id=%d является сам себе группой' % \
                (id, forceString(record.value('code')),
                      forceString(record.value('name')), groupId),
                QtGui.QMessageBox.Close)
        elif groupId in self.nestedGroups:
            QtGui.QMessageBox.critical (self.parent,
                u'Ошибка в логической структуре данных',
                u'Элемент id=%d: group_id=%d обнаружен в списке родительских групп "%s"' % \
                (id,  groupId,  u'(' + '-> '.join([str(et) for et in self.nestedGroups])+ ')'),
                QtGui.QMessageBox.Close)
        elif groupId: # все в порядке
            self.writeStartElement('Group')
            query = self.createQuery([groupId])
            while (query.next()):
                self.nestedGroups.append(groupId)
                self.writeRecord(query.record()) # рекурсия
                self.nestedGroups.remove(groupId)
            self.writeEndElement()

        if ownerId:
            if self.ownerMap.has_key(ownerId):
                ownerInfo = self.ownerMap[ownerId]
            else:
                ownerInfo = getPersonInfo(ownerId)
                self.ownerMap[ownerId] = ownerInfo

            if ownerInfo:
                self.writeStartElement('Owner')

                for x in ownerFields:
                    if ownerInfo.has_key(x):
                        self.writeAttribute(x,  ownerInfo[x])

                self.writeEndElement()

        if specialityId:
            specialityInfo = self.getSpecialityInfo(specialityId)
            self.writeStartElement('Speciality')

            for x in specialityFields:
                if specialityInfo.has_key(x):
                    self.writeAttribute(x, specialityInfo[x])

            self.writeEndElement()

        if actionId:
            self.writeAction(actionId)

        self.writeEndElement()


    def writeFile(self,  device,  progressBar):
        global lastChangedRev
        global lastChangedDate
        try:
            from buildInfo import lastChangedRev, lastChangedDate
        except:
            lastChangedRev  = 'unknown'
            lastChangedDate = 'unknown'

        try:
            progressBar.setText(u'Запрос данных')
            query = self.createQuery(self._idList)
            self.setDevice(device)
            progressBar.setMaximum(max(query.size(), 1))
            progressBar.reset()
            progressBar.setValue(0)

            self.writeStartDocument()
            self.writeDTD('<!DOCTYPE xActionTemplate>')
            self.writeStartElement('ActionTemplateExport')
            self.writeAttribute('SAMSON',
                                '2.0 revision(%s, %s)' %(lastChangedRev, lastChangedDate))
            self.writeAttribute('version', '1.01')
            while (query.next()):
                self.writeRecord(query.record())
                progressBar.step()

            self.writeEndDocument()

        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            return False

        return True


class CExportActionTemplateWizardPage1(QtGui.QWizardPage, \
            Ui_ExportActionTemplate_Wizard_1, CConstructHelperMixin):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.cols = [
            CTextCol(   u'Код',          ['code'], 20),
            CTextCol(   u'Наименование', ['name'],   40)
            ]
        self.tableName = 'ActionTemplate'
        self.order = ['code', 'name', 'id']
        self.parent = parent
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()
        self.setTitle(u'Параметры экспорта')
        self.setSubTitle(u'Выбор записей для экспорта')


    def isComplete(self):
        # проверим пустой ли у нас список выбранных элементов
        if self.parent.exportAll:
            return True
        else:
            for key in self.parent.selectedItems.keys():
                if self.parent.selectedItems[key] != []:
                    return True
            return False


    def preSetupUi(self):
        self.addModels('Tree', CDBTreeModel(self, self.tableName, 'id', 'group_id', 'name',  self.order))
        self.addModels('Table',CTableModel(self, self.cols, self.tableName))


    def postSetupUi(self):
        self.setModels(self.treeItems,  self.modelTree,  self.selectionModelTree)
        self.setModels(self.tblItems,   self.modelTable, self.selectionModelTable)
        self.tblItems.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.treeItems.header().hide()
        idList = self.select()
        self.modelTable.setIdList(idList)
        self.selectionModelTable.clearSelection()
        self.tblItems.setFocus(Qt.OtherFocusReason)
        self.tblItems.setEnabled(not self.parent.exportAll)
        self.treeItems.setEnabled(not self.parent.exportAll)
        self.btnSelectAll.setEnabled(not self.parent.exportAll)
        self.btnClearSelection.setEnabled(not self.parent.exportAll)
        self.checkExportAll.setChecked(self.parent.exportAll)


    def select(self):
        table = self.modelTable.table()
        groupId = self.currentGroupId()
        return QtGui.qApp.db.getIdList(table.name(),
                            'id',
                            table['group_id'].eq(groupId),
                            self.order)


    def selectItem(self):
        return self.exec_()


    def setCurrentItemId(self, itemId):
        self.tblItems.setCurrentItemId(itemId)


    def currentItemId(self):
        return self.tblItems.currentItemId()


    def currentGroupId(self):
        return self.modelTree.itemId(self.treeItems.currentIndex())


    def renewListAndSetTo(self, itemId=None):
        if not itemId:
            itemId = self.tblItems.currentItemId()
        idList = self.select()
        self.tblItems.setIdList(idList, itemId)
        self.selectionModelTable.clearSelection()
        # восстанавливаем выбранные элементы в таблице
        groupId = self.currentGroupId()

        if groupId in self.parent.selectedItems.keys():
            rows = []
            for id in self.parent.selectedItems[groupId]:
                if idList.count(id)>0:
                    row = idList.index(id)
                    rows.append(row)
            for row in rows:
                index = self.modelTable.index(row, 0)
                self.selectionModelTable.select(index, QtGui.QItemSelectionModel.Select|
                                                                    QtGui.QItemSelectionModel.Rows)


    def selectNestedElements(self,  id,  selectedItems,  select):
        if not select:
            # рекурсивно убираем выделение с дочерних элементов
            if selectedItems.has_key(id):
                for x in selectedItems[id]:
                    self.selectNestedElements(x,  selectedItems,  select)

                selectedItems.pop(id)

            return

        itemIndex = self.modelTree.findItemId(id)

        if itemIndex:
            table = self.modelTable.table()
            item = itemIndex.internalPointer()
            leafList =QtGui.qApp.db.getIdList(table.name(),
                            'id',
                            table['group_id'].eq(id),
                            self.order)

            if not selectedItems.has_key(id):
                selectedItems[id] = []

            if leafList and leafList != []:
                selectedItems[id].extend(leafList)

            for x in item.items():
                self.selectNestedElements(x.id(),  selectedItems,  select)

    @QtCore.pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModelTree_currentChanged(self, current, previous):
        # сохраняем индексы выбранных элементов в таблице
        if previous != None:
            previousId = self.modelTree.itemId(previous)
            self.parent.selectedItems[previousId] = self.tblItems.selectedItemIdList()
        self.renewListAndSetTo(None)


    @QtCore.pyqtSlot(QModelIndex)
    def on_tblItems_clicked(self, index):
        self.parent.selectedItems[self.currentGroupId()] =self.tblItems.selectedItemIdList()

        # если стоит галка "выделять дочерние элементы", рекурсивно
        # выделаем все ветки выбранных элементов
        if self.chkRecursiveSelection.isChecked():
            self.selectNestedElements(self.currentItemId(),  self.parent.selectedItems,
                                                self.selectionModelTable.isSelected(index))

        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnSelectAll_clicked(self):
        selectionList = self.modelTable.idList()
        self.parent.selectedItems[self.currentGroupId()]=selectionList

        if self.chkRecursiveSelection.isChecked():
            for x in selectionList:
                self.selectNestedElements(x,  self.parent.selectedItems,  True)

        for id in selectionList:
            index = self.modelTable.index(selectionList.index(id), 0)
            self.selectionModelTable.select(index, QtGui.QItemSelectionModel.Select|
                                                                    QtGui.QItemSelectionModel.Rows)
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnClearSelection_clicked(self):
        if self.chkRecursiveSelection.isChecked():
            for x in self.modelTable.idList():
                self.selectNestedElements(x,  self.parent.selectedItems,  False)

        self.parent.selectedItems.pop(self.currentGroupId())
        self.selectionModelTable.clearSelection()
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_checkExportAll_clicked(self):
        self.parent.exportAll = self.checkExportAll.isChecked()
        self.tblItems.setEnabled(not self.parent.exportAll)
        self.treeItems.setEnabled(not self.parent.exportAll)
        self.btnSelectAll.setEnabled(not self.parent.exportAll)
        self.btnClearSelection.setEnabled(not self.parent.exportAll)
        self.emit(QtCore.SIGNAL('completeChanged()'))


class CExportActionTemplateWizardPage2(QtGui.QWizardPage, \
            Ui_ExportActionTemplate_Wizard_2):
    def __init__(self,  parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.parent=parent
        self.setTitle(u'Параметры сохранения')
        self.setSubTitle(u'Выбор места для сохранения')
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.edtFileName.setText(self.parent.fileName)
        self.btnExport.setEnabled(self.parent.fileName != '')
        self.checkRAR.setChecked(self.parent.compressRAR)
        self.done = False

#    def validatePage(self):
#        return self.done

    def isComplete(self):
        return self.done

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getSaveFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (*.xml)')
        if fileName != '' :
            self.edtFileName.setText(fileName)
            self.parent.fileName = fileName
            self.btnExport.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        fileName = self.edtFileName.text()

        if fileName.isEmpty():
            return

        idList = []
        if not self.parent.exportAll:
            for key in self.parent.selectedItems.keys():
                if key and (not (key in idList)):
                    idList.append(key)
                for id in self.parent.selectedItems[key]:
                    if not (id in idList):
                        idList.append(id)
            if idList == []:
                QtGui.QMessageBox.warning(self, u'Экспорт типов действий',
                                      u'Не выбрано ни одного действия для выгрузки')
                self.parent.back() # вернемся на пред. страницу. пусть выбирают
                return


        outFile = QtCore.QFile(fileName)
        if not outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Экспорт типов действий',
                                      u'Не могу открыть файл для записи %s:\n%s.' \
                                      % (fileName, outFile.errorString()))

        myXmlStreamWriter = CMyXmlStreamWriter(self, idList)
        if (myXmlStreamWriter.writeFile(outFile,  self.progressBar)):
            self.progressBar.setText(u'Готово')
        else:
            self.progressBar.setText(u'Прервано')
        outFile.close()

        if self.checkRAR.isChecked():
            self.progressBar.setText(u'Сжатие')
            try:
                compressFileInRar(fileName, fileName+'.rar')
                self.progressBar.setText(u'Сжато в "%s"' % (fileName+'.rar'))
            except CRarException as e:
                self.progressBar.setText(unicode(e))
                QtGui.QMessageBox.critical(self, e.getWindowTitle(), unicode(e), QtGui.QMessageBox.Close)

        self.done = True
        self.btnExport.setEnabled(False)
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_checkRAR_clicked(self):
        self.parent.compressRAR = self.checkRAR.isChecked()


class CExportActionTemplate(QtGui.QWizard):
    def __init__(self, fileName,  exportAll, compressRAR,  parent=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Экспорт шаблонов свойств действий')
        self.selectedItems = {}
        self.fileName= fileName
        self.exportAll = exportAll
        self.compressRAR = compressRAR
        self.addPage(CExportActionTemplateWizardPage1(self))
        self.addPage(CExportActionTemplateWizardPage2(self))
