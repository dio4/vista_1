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

from Ui_ExportRbThesaurus_Wizard_1 import Ui_ExportRbThesaurus_Wizard_1
from Ui_ExportRbThesaurus_Wizard_2 import Ui_ExportRbThesaurus_Wizard_2

rbThesaurusFields = ('code', 'name',  'template')


def ExportRbThesaurus(parent):
    fileName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportRbThesaurusFileName', ''))
    exportAll = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportRbThesaurusExportAll', 'False'))
    compressRAR = forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ExportRbThesaurusCompressRAR', 'False'))
    dlg = CExportRbThesaurus(fileName, exportAll,  compressRAR,  parent)
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ExportRbThesaurusFileName'] = toVariant(dlg.fileName)
    QtGui.qApp.preferences.appPrefs['ExportRbThesaurusExportAll'] = toVariant(dlg.exportAll)
    QtGui.qApp.preferences.appPrefs['ExportRbThesaurusCompressRAR'] = toVariant(dlg.compressRAR)



class CMyXmlStreamWriter(QXmlStreamWriter):
    def __init__(self,  parent, idList):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self._idList = idList
        self.nestedGroups = []
        self.templatesMap = {}


    def createQuery(self,  idList):
        db = QtGui.qApp.db
        stmt = """
        SELECT  id,
                    code,
                    name,
                    template,
                    group_id
        FROM rbThesaurus
        """
        if idList:
            stmt+=' WHERE id in ('+', '.join([str(et) for et in idList])+')'

        query = db.query(stmt)
        return query


    def writeRecord(self, record):
        self.writeStartElement("ThesaurusElement")

        # все свойства действия экспортируем как атрибуты
        for x in rbThesaurusFields:
            self.writeAttribute(x, forceString(record.value(x)))

        # все, что определяется ссылками на другие таблицы - как элементы
        # группа экспортируемого элемента:
        group_id = forceInt(record.value("group_id"))
        id  = forceInt(record.value("id"))

        if id == group_id:
            QtGui.QMessageBox.critical (self.parent,
                u'Ошибка в логической структуре данных',
                u'Элемент id=%d: (%s) "%s", group_id=%d является сам себе группой' % \
                (id, forceString(record.value("code")),
                      forceString(record.value("name")), group_id),
                QtGui.QMessageBox.Close)
        elif group_id in self.nestedGroups:
            QtGui.QMessageBox.critical (self.parent,
                u'Ошибка в логической структуре данных',
                u'Элемент id=%d: group_id=%d обнаружен в списке родительских групп "%s"' % \
                (id,  group_id,  u'(' + '-> '.join([str(et) for et in self.nestedGroups])+ ')'),
                QtGui.QMessageBox.Close)
        elif group_id != 0: # все в порядке
            self.writeStartElement("group")
            query = self.createQuery([group_id])
            while (query.next()):
                self.nestedGroups.append(group_id)
                self.writeRecord(query.record()) # рекурсия
                self.nestedGroups.remove(group_id)
            self.writeEndElement() # group

        self.writeEndElement() # ThesaurusElement

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
            self.writeDTD("<!DOCTYPE xRbThesaurus>")
            self.writeStartElement("RbThesaurusExport")
            self.writeAttribute("SAMSON",
                                "2.0 revision(%s, %s)" %(lastChangedRev, lastChangedDate))
            self.writeAttribute("version", "1.00")
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

class CExportRbThesaurusWizardPage1(QtGui.QWizardPage, Ui_ExportRbThesaurus_Wizard_1, CConstructHelperMixin):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.cols = [
            CTextCol(   u'Код',          ['code'], 20),
            CTextCol(   u'Наименование', ['name'],   40)
            ]
        self.tableName = "rbThesaurus"
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
                if self.parent.selectedItems[key]:
                    return True
            return False


    def preSetupUi(self):
        self.addModels('Tree', CDBTreeModel(self, 'rbThesaurus', 'id', 'group_id', 'name', order='code'))
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
                if idList.count(id) > 0:
                    row = idList.index(id)
                    rows.append(row)
            for row in rows:
                index = self.modelTable.index(row, 0)
                self.selectionModelTable.select(index, QtGui.QItemSelectionModel.Select|
                                                                    QtGui.QItemSelectionModel.Rows)


    def selectNestedElements(self,  id,  selectedItems,  select):
        if not select:
            # рекурсивно убираем выделение с дочерних элементов
            item = self.modelTree.findItemId(id).internalPointer()
            if True: #id in selectedItems:
                for x in item.items(): #selectedItems[id]:
                    self.selectNestedElements(x.id(),  selectedItems,  select)

                if id in selectedItems:
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

    def selectElement(self, id, selectedItems, select):
        if not select:
            if selectedItems.has_key(id):
                selectedItems.pop(id)
            return

        itemIndex = self.modelTree.findItemId(id)

        if itemIndex:
            table = self.modelTable.table()
            leafList =QtGui.qApp.db.getIdList(table.name(),
                            'id',
                            table['group_id'].eq(id),
                            self.order)

            if not selectedItems.has_key(id):
                selectedItems[id] = []

            if leafList and leafList != []:
                selectedItems[id].extend(leafList)

    @QtCore.pyqtSlot(QModelIndex, QModelIndex)
    def on_selectionModelTree_currentChanged(self, current, previous):
        # сохраняем индексы выбранных элементов в таблице
        if previous is not None:
            previousId = self.modelTree.itemId(previous)
            self.parent.selectedItems[previousId] = self.tblItems.selectedItemIdList()
        self.renewListAndSetTo(None)


    @QtCore.pyqtSlot(QModelIndex)
    def on_tblItems_clicked(self, index):
        # self.parent.selectedItems[self.currentGroupId()] = self.tblItems.selectedItemIdList()
        self.selectElement(self.currentItemId(), self.parent.selectedItems, self.selectionModelTable.isSelected(index))

        # если стоит галка "выделять дочерние элементы", рекурсивно
        # выделаем все ветки выбранных элементов
        if self.chkRecursiveSelection.isChecked():
            self.selectNestedElements(self.currentItemId(),  self.parent.selectedItems,
                                                self.selectionModelTable.isSelected(index))

        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnSelectAll_clicked(self):
        selectionList = self.modelTable.idList()
        self.parent.selectedItems[self.currentGroupId()] = selectionList

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


class CExportRbThesaurusWizardPage2(QtGui.QWizardPage, Ui_ExportRbThesaurus_Wizard_2):
    def __init__(self,  parent):
        self.done = False
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
        self.checkRAR.setText(QtGui.QApplication.translate("ExportRbThesaurus_Wizard_2", "Архивировать", None, QtGui.QApplication.UnicodeUTF8))

    def initializePage(self):
        self.btnExport.setEnabled(self.parent.fileName != '')
        self.done = False

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
            if not idList:
                QtGui.QMessageBox.warning(self, u'Экспорт Тезауруса',
                                      u'Не выбрано ни одного элемента для выгрузки')
                self.parent.back() # вернемся на пред. страницу. пусть выбирают
                return


        outFile = QtCore.QFile(fileName)
        if not outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, self.tr(u'Экспорт Тезауруса'),
                                      self.tr(u'Не могу открыть файл для записи %1:\n%2.')
                                      .arg(fileName)
                                      .arg(outFile.errorString()))

        myXmlStreamWriter = CMyXmlStreamWriter(self, idList)
        if myXmlStreamWriter.writeFile(outFile,  self.progressBar):
            self.progressBar.setText(u'Готово')
        else:
            self.progressBar.setText(u'Прервано')
        outFile.close()

        if self.checkRAR.isChecked():
            self.progressBar.setText(u'Сжатие')
            if compressFileInZip(fileName):
                self.progressBar.setText(u'Сжато в "%s"' % (fileName+'.zip'))
            else:
                self.progressBar.setText(u"Сжать файл не удалось")

        self.done = True
        self.btnExport.setEnabled(False)
        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_checkRAR_clicked(self):
        self.parent.compressRAR = self.checkRAR.isChecked()


    @QtCore.pyqtSlot(QString)
    def on_edtFileName_textChanged(self):
        self.parent.fileName = self.edtFileName.text()
        self.btnExport.setEnabled(self.parent.fileName != '')
        self.emit(QtCore.SIGNAL('completeChanged()'))


class CExportRbThesaurus(QtGui.QWizard):
    def __init__(self, fileName,  exportAll, compressRAR,  parent=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Экспорт Тезауруса')
        self.selectedItems = {}
        self.fileName= fileName
        self.exportAll = exportAll
        self.compressRAR = compressRAR
        self.addPage(CExportRbThesaurusWizardPage1(self))
        self.addPage(CExportRbThesaurusWizardPage2(self))
