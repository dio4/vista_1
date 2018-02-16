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

from Utils import *

from Ui_ExportActions_Wizard_1 import Ui_ExportActions_Wizard_1
from Ui_ExportActions_Wizard_2 import Ui_ExportActions_Wizard_2

actionClasses = {0 : u'Статус',
                 1 : u'Диагностика',
                 2 : u'Лечение',
                 3 : u'Прочие мероприятия',
                 4 : u'Анализы'}

# поля для выгрузки, без ссылок. используется для формирования запросов
# и поименной записи в xml

actionTypeFields = (
        'class',  'code', 'name', 'flatCode', 'sex', 'age', 'office',
        'showInForm', 'genTimetable', 'context', 'amount', 'amountEvaluation',
        'defaultStatus', 'defaultEndDate', 'defaultPersonInEvent', 'defaultPersonInEditor',
        'showTime', 'maxOccursInEvent', 'isMES'
    )

actionPropertyTypeFields = (
        'idx', 'name', 'descr', 'typeName', 'valueDomain',
        'defaultValue', 'isVector', 'norm', 'sex', 'age', 'penalty',
        'visibleInJobTicket', 'isAssignable'
    )

serviceFields = (
        'code', 'name', 'eisLegacy', 'nomenclatureLegacy', 'license',
        'infis', 'begDate', 'endDate'
    )

serviceDateFields = (
        'begDate', 'endDate'
    )

unitFields = (
        'code', 'name'
    )

exportFormatVersion = '1.2'

# Экспорт в формате версии 1.01 - Изменен формат выгрузки шаблонов
# Экспорт в формате версии 1.02 - Изменено поле amountByVisits на amountEvaluation
# Экспорт в формате версии 1.1 - Добавлены новые поля, таблица nomenclativeService
# Экспорт в формате версии 1.2 - Добавлены новые поля

def ExportActionType():
    fileName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportActionTypeFileName', ''))
    exportAll = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportActionTypeExportAll', 'False'))
    compressRAR = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportActionTypeCompressRAR', 'False'))
    dlg = CExportActionType(fileName, exportAll,  compressRAR)
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ExportActionTypeFileName'] = toVariant(
                                                                            dlg.fileName)
    QtGui.qApp.preferences.appPrefs['ExportActionTypeExportAll'] = toVariant(
                                                                            dlg.exportAll)
    QtGui.qApp.preferences.appPrefs['ExportActionTypeCompressRAR'] = toVariant(
                                                                            dlg.compressRAR)


class CActionTypeTreeItem(CDBTreeItem):
    def __init__(self, parent, name, id, dbTreeModel, actionClass, childrenCount=None):
        CDBTreeItem.__init__(self, parent, name, id, dbTreeModel, childrenCount=childrenCount)
        self.actionClass = actionClass


class CActionTypeTreeModel(CDBTreeModel):
    def __init__(self, parent, tableName, idColName, groupColName, nameColName,
                            classColName, order=None):
        CTreeModel.__init__(self, parent, CActionTypeTreeItem(None, u'все', None, self,  -1))
        self.setRootItemVisible(False)
        self.tableName = tableName
        self.idColName    = idColName
        self.groupColName = groupColName
        self.classColName = classColName
        self.nameColName  = nameColName
        self.order = order if order else nameColName


    def loadChildrenItems(self, group):
        result = []
        if group.actionClass == -1:  # корень, нужно добавить классы вручную
            for key,  val in actionClasses.items():
                result.append(CActionTypeTreeItem(group, val, None, self, key))
        else:
            db = QtGui.qApp.db
            table = db.table(self.tableName)
            alias = table.alias(self.tableName+'2')
            children = table.alias(self.tableName + '_children')
            children_alias = table.alias(self.tableName+'_children2')
            cond = [table[self.groupColName].eq(group.id()),
                    table[self.classColName].eq(group.actionClass),
                    db.existsStmt(alias, alias[self.groupColName].eq(table[self.idColName]))]
            for record in db.getRecordList(table,
                                           [self.idColName, self.nameColName,
                                            '(' + db.selectStmt(children,
                                                                db.count('*'),
                                                                [
                                                                    table[self.idColName].eq(children[self.groupColName]),
                                                                    children[self.classColName].eq(group.actionClass),
                                                                    db.existsStmt(children_alias, children_alias[self.groupColName].eq(children[self.idColName]))
                                                                ]) + ')'],
                                           cond,
                                           self.order):
                id = forceRef(record.value(0))
                name = forceString(record.value(1))
                childrenCount = forceInt(record.value(2))
                result.append(CActionTypeTreeItem(group, name, id, self, group.actionClass, childrenCount=childrenCount))
        return result

    def classId(self,  index):
        item = index.internalPointer()
        return item.actionClass if item else None


class CMyXmlStreamWriter(QXmlStreamWriter):
    def __init__(self,  parent, idList):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self._idList = idList
        self.nestedGroups = []
        self.templatesMap = {}

    def writeActionProperty(self,  record):
        self.writeStartElement('ActionPropertyType')
        # все свойства действия экспортируем как атрибуты
        for x in actionPropertyTypeFields:
            self.writeAttribute(x, forceString(record.value(x)))

        # обработка кода шаблона типа действия
        self.writeTemplateInfo(forceInt(record.value('template_id')))

        subTables = (
                     ('unit',  unitFields,  None),
                     )

        self.writeSubElements(subTables, record)
        self.writeEndElement()


    def writeSubElements(self, subTables, record):
        for (tableName, fieldsList,  datesList) in subTables:
            if (forceString(record.value('%s_name' % tableName))!= ''):
                self.writeStartElement(tableName)
                for x in fieldsList:
                    if datesList and (x in datesList):
                        self.writeAttribute(x, forceDate(record.value('%s_%s' % (tableName, x))).toString(Qt.ISODate))
                    else:
                        self.writeAttribute(x, forceString(record.value('%s_%s' % (tableName,  x))))
                self.writeEndElement()


    def writeTemplateInfo(self,  templateId):
        u""" Двигается по дереву шаблонов к корню и пишет все коды.
            Для однозначной идентификации шаблона.
            Код класса: подгруппа [, ...], шаблон """

        db = QtGui.qApp.db
        stmt = u'''
                SELECT  a.code AS code,
                            a.group_id AS group_id
                FROM    ActionPropertyTemplate a
                WHERE   a.id = '%s'
                '''
        groupId = templateId
        groupsList = []

        while groupId:
            if self.templatesMap.has_key(groupId):
                (groupCode,  groupId) = self.templatesMap[groupId]
            else:
                q = db.query(stmt % groupId)
                q.next()
                record = q.record()
                oldGroupId = groupId
                groupId = forceInt(record.value('group_id'))
                groupCode = forceString(record.value('code'))
                if groupId:
                    self.templatesMap[oldGroupId] = (groupCode,  groupId)

            groupsList.insert(0, groupCode)

        for x in groupsList:
            self.writeStartElement('template')
            self.writeAttribute('code',  forceString(x))
            self.writeEndElement()


    def createQuery(self,  idList):
        db = QtGui.qApp.db
        stmt = '''
        SELECT  ActionType.id AS id,
                    ActionType.group_id AS group_id'''
        stmt+=', '+', '.join([('ActionType.`%s`' % et) for et in actionTypeFields])
        stmt+=', '+ ', '.join([('nService.`%s` AS `nomenclativeService_%s`'  % (et,  et)) for et in serviceFields])
        stmt += ''' FROM ActionType
        LEFT JOIN rbService AS nService ON ActionType.nomenclativeService_id = nService.id
        WHERE ActionType.`deleted` = 0'''

        if idList and idList != []:
            stmt+=' AND ActionType.id IN ('+', '.join([str(et) for et in idList])+')'

        query = db.query(stmt)
        return query


    def createActionPropertyQuery(self, action_id):
        u""" Создает запрос для обработки свойств типа действия.
            Здесь считаем что элемент таблицы едниц измерения (rbUnit)
            однозначно определяется по коду и имени, а элемент таблицы
            шаблонов типов действий (ActionPropertyTemplate) - по коду. """
        db = QtGui.qApp.db
        stmt = 'SELECT  a.template_id AS template_id'
        stmt +=', '+ ', '.join([('a.%s' % et) for et in actionPropertyTypeFields])
        stmt +=', '+ ', '.join([('rbUnit.%s AS unit_%s' % (et,  et)) for et in unitFields])
        stmt +=  ''' FROM ActionPropertyType a
        LEFT JOIN rbUnit ON a.unit_id = rbUnit.id
        WHERE a.actionType_id = %d AND a.deleted = 0
        ''' % action_id
        query = db.query(stmt)
        return query


    def processActionProperties(self, action_id):
        query = self.createActionPropertyQuery(action_id)
        while (query.next()):
            self.writeActionProperty(query.record())


    def writeRecord(self, record):
        self.writeStartElement('ActionType')

        # все свойства действия экспортируем как атрибуты
        for x in actionTypeFields:
            self.writeAttribute(x, forceString(record.value(x)))

        # все, что определяется ссылками на другие таблицы - как элементы
        # группа экспортируемого элемента:
        group_id = forceRef(record.value('group_id'))
        id  = forceRef(record.value('id'))

        if id == group_id:
            QtGui.QMessageBox.critical (self.parent,
                u'Ошибка в логической структуре данных',
                u'Элемент id=%d: (%s) "%s", group_id=%d является сам себе группой' % \
                (id, forceString(record.value('code')),
                      forceString(record.value('name')), group_id),
                QtGui.QMessageBox.Close)
        elif group_id in self.nestedGroups:
            QtGui.QMessageBox.critical (self.parent,
                u'Ошибка в логической структуре данных',
                u'Элемент id=%d: group_id=%d обнаружен в списке родительских групп "%s"' % \
                (id,  group_id,  u'(' + '-> '.join([str(et) for et in self.nestedGroups])+ ')'),
                QtGui.QMessageBox.Close)
        elif group_id: # все в порядке
            self.writeStartElement('group')
            query = self.createQuery([group_id])
            while query.next():
                self.nestedGroups.append(group_id)
                self.writeRecord(query.record()) # рекурсия
                self.nestedGroups.remove(group_id)
            self.writeEndElement()

        subTables = (
                     ('nomenclativeService',  serviceFields,  serviceDateFields),
                     )

        self.writeSubElements(subTables, record)

        # Выгружаем свойства типа действия
        self.processActionProperties(id)
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
            self.writeDTD('<!DOCTYPE xActionType>')
            self.writeStartElement('ActionTypeExport')
            self.writeAttribute('SAMSON',
                                '2.0 revision(%s, %s)' %(lastChangedRev, lastChangedDate))
            self.writeAttribute('version', exportFormatVersion)
            while query.next():
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

class CExportActionTypeWizardPage1(QtGui.QWizardPage, Ui_ExportActions_Wizard_1, CConstructHelperMixin):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.cols = [
            CTextCol(   u'Код',          ['code'], 20),
            CTextCol(   u'Наименование', ['name'],   40)
            ]
        self.tableName = 'ActionType'
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
        self.addModels('Tree', CActionTypeTreeModel(self, self.tableName, 'id', 'group_id', 'name', 'class', self.order))
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
        classId = self.currentClassId()
        return QtGui.qApp.db.getIdList(table.name(),
                            'id',
                            QtGui.qApp.db.joinAnd([
                            table['group_id'].eq(groupId),
                            table['deleted'].eq(0)]),
                            self.order) if groupId != None else QtGui.qApp.db.getIdList(table.name(),
                            'id',
                            QtGui.qApp.db.joinAnd([
                            table['group_id'].eq(None),
                            table['class'].eq(classId),
                            table['deleted'].eq(0)]),
                            self.order)


    def selectItem(self):
        return self.exec_()


    def setCurrentItemId(self, itemId):
        self.tblItems.setCurrentItemId(itemId)


    def currentItemId(self):
        return self.tblItems.currentItemId()


    def currentGroupId(self):
        return self.modelTree.itemId(self.treeItems.currentIndex())

    def currentClassId(self):
        return self.modelTree.classId(self.treeItems.currentIndex())

    def renewListAndSetTo(self, itemId=None):
        if not itemId:
            itemId = self.tblItems.currentItemId()
        idList = self.select()
        self.tblItems.setIdList(idList, itemId)
        self.selectionModelTable.clearSelection()
        # восстанавливаем выбранные элементы в таблице
        groupId = self.currentGroupId()

        if groupId == None: # экспорт самих групп
            groupId = '$class$'+forceString(self.currentClassId())

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
                    self.selectNestedElements(x, selectedItems, select)

                selectedItems.pop(id)

            return

        itemIndex = self.modelTree.findItemId(id)

        if itemIndex:
            table = self.modelTable.table()
            item = itemIndex.internalPointer()
            leafList =QtGui.qApp.db.getIdList(table.name(),
                            'id',
                            QtGui.qApp.db.joinAnd([
                            table['group_id'].eq(id),
                            table['deleted'].eq(0)]),
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
            # если выбираем группы для экспорта
            if previousId == None:
                previousId = '$class$'+forceString(self.modelTree.classId(previous))
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

class CExportActionTypeWizardPage2(QtGui.QWizardPage, Ui_ExportActions_Wizard_2):
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
            fileName = QtCore.QDir.toNativeSeparators(fileName)
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
                if (key not in [None,  '$class$', '$class$0', '$class$1', '$class$2', '$class$3' ]) \
                        and not (key in idList):
                    idList.append(key)
                for id in self.parent.selectedItems[key]:
                    if not (id in idList):
                        idList.append(id)
            if idList == []:
                QtGui.QMessageBox.warning(self, u'Экспорт типов действий',
                                      u'Не выбрано ни одного дейсвия для выгрузки')
                self.parent.back() # вернемся на пред. страницу. пусть выбирают
                return


        outFile = QtCore.QFile(fileName)
        if not outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Экспорт типов действий',
                u'Не могу открыть файл для записи %1s\n%s.' % \
                (fileName, outFile.errorString()))
            return

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

class CExportActionType(QtGui.QWizard):
    def __init__(self, fileName,  exportAll, compressRAR,  parent=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Экспорт типов действий')
        self.selectedItems = {}
        self.fileName= fileName
        self.exportAll = exportAll
        self.compressRAR = compressRAR
        self.addPage(CExportActionTypeWizardPage1(self))
        self.addPage(CExportActionTypeWizardPage2(self))
