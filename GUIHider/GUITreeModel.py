# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from library.database import connectDataBaseByInfo
from library.Preferences import CPreferences
from library.Utils import toVariant, forceString
from library.exception import CException

from preferences.connection import CConnectionDialog

'''
Created on 03.02.2014

@author: atronah
'''


class CEditableTreeItem(object):
    _defaultAttrNameTemplate = u'__nonameAttr%s'

    def __init__(self, parentItem, itemData, checkState=QtCore.Qt.Unchecked):
        self._parentItem = parentItem
        self._itemData = []
        self._childItems = []
        self._checkState = QtCore.Qt.Unchecked

        self.setItemData(itemData)
        self.setCheckState(checkState)

    def setItemData(self, itemData):
        self._itemData = QtCore.QVariant(itemData if isinstance(itemData, list) else [itemData]).toList()
        return True

    def columnCount(self):
        return len(self._itemData)

    def hasChildren(self):
        return bool(self._childItems)

    def childCount(self):
        return len(self._childItems)

    ## Возвращает список дочерних элементов
    def children(self):
        return self._childItems

    def displayData(self, column):
        return QtCore.QVariant(self._itemData[column])

    def indexOf(self, item):
        return self._childItems.index(item)

    def positionInParent(self):
        if self._parentItem:
            return self._parentItem.indexOf(self)
        return 0

    def data(self, column, role=QtCore.Qt.DisplayRole):
        if column not in xrange(self.columnCount()):
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole:
            return self.displayData(column)
        elif role == QtCore.Qt.EditRole:
            return QtCore.QVariant(self._itemData[column])
        elif role == QtCore.Qt.CheckStateRole and column == 0:
            return QtCore.QVariant(self._checkState)

        return QtCore.QVariant()

    def setData(self, column, value, role=QtCore.Qt.EditRole):
        if column not in xrange(self.columnCount()):
            return False

        if role == QtCore.Qt.EditRole:
            self._itemData[column] = toVariant(value)
        elif role == QtCore.Qt.CheckStateRole and column == 0:
            self.setCheckState(value)
        else:
            return False

        return True

    def setCheckState(self, checkState, isUpdateParentCheckState=True):
        if isinstance(checkState, QtCore.QVariant):
            self._checkState = QtCore.Qt.CheckState(checkState.toInt()[0])
        elif isinstance(checkState, QtCore.Qt.CheckState):
            self._checkState = checkState
        elif bool(checkState):
            self._checkState = QtCore.Qt.Checked
        else:
            self._checkState = QtCore.Qt.Unchecked

        if self.checkState() in [QtCore.Qt.Unchecked, QtCore.Qt.Checked]:
            for child in self.children():
                child.setCheckState(self.checkState(), isUpdateParentCheckState=False)

        if isUpdateParentCheckState:
            parentItem = self.parent()
            while parentItem:
                parentItem.updateCheckState()
                parentItem = parentItem.parent()

    def updateCheckState(self):
        if not self._childItems:
            return
        isAllChildrenChecked = True
        for child in self._childItems:
            if isAllChildrenChecked and child.checkState() != QtCore.Qt.Checked:
                isAllChildrenChecked = False

            if self.checkState() != child.checkState():
                self._checkState = QtCore.Qt.PartiallyChecked
                if not isAllChildrenChecked:
                    break

        if isAllChildrenChecked:
            self._checkState = QtCore.Qt.Checked

    def isChecked(self):
        return bool(self._checkState)

    def checkState(self):
        return self._checkState

    def isPartiallyChecked(self):
        return self._checkState == QtCore.Qt.PartiallyChecked

    def parent(self):
        return self._parentItem

    def child(self, position):
        if position not in xrange(self.childCount()):
            return None

        return self._childItems[position]

    def addChildren(self, item, idx=None):
        if not isinstance(item, CEditableTreeItem):
            return -1

        if idx not in xrange(self.childCount()):
            idx = len(self._childItems)

        self._childItems.insert(idx, item)
        return idx

    def insertChildren(self, position, count=1, itemData=None):
        if position < 0:
            position = 0
        elif position > self.childCount():
            position = self.childCount() - 1

        if count < 0:
            return self.removeChildren(position, -count)

        itemData = itemData if isinstance(itemData, list) else ([None] * self.columnCount())
        itemData += [None] * (
        self.columnCount() - len(itemData))  # atronah: выравнивание длины списка под кол-во столбцов
        while count > 0:
            if itemData and itemData[0] is None:
                itemData[0] = u'Noname item'
            child = self.__class__(parent=self, itemData=itemData)
            self.addChildren(child,
                             position)
            count -= 1

        return True

    def removeChildren(self, position, count=1):
        if position < 0:
            position = 0
        elif position > self.childCount():
            position = self.childCount()

        if position not in xrange(self.childCount()):
            return False

        while count > 0 and self._childItems[position:]:
            count -= 1
            removeChild = self._childItems.pop(position)
            removeChild.removeChildren(0, removeChild.childCount())

        return True

    def insertColumns(self, position, count):
        if position < 0:
            position = 0
        elif position >= self.columnCount():
            position = self.columnCount() - 1

        # TODO: atronah: проверить, надо ли обновлять число столбцов и у родителей? Или в одной моделе могут быть элементы с разным числом столбцов
        if position not in xrange(self.columnCount()):
            return False

        if count < 0:
            return self.removeColumns(position, - count)

        for child in self._childItems:
            if not child.insertColumns(position, count):
                return False

        while count > 0:
            count -= 1
            self._itemData.insert(position, None)

        return True

    def removeColumns(self, position, count):
        if position < 0:
            position = 0
        elif position > self.columnCount()():
            position = self.columnCount()

        if position not in xrange(self.columnCount()):
            return False

        for child in self._childItems:
            if not child.removeColumns(position, count):
                return False

        while count > 0 and self._itemData[position:]:
            count -= 1
            self._itemData.pop(position)

        return False

    def swapChildren(self, firstIdx, secondIdx):
        if firstIdx not in xrange(self.childCount()) or secondIdx not in xrange(self.childCount()):
            return False
        if firstIdx > secondIdx:
            firstIdx, secondIdx = secondIdx, firstIdx

        firstItem = self._childItems.pop(firstIdx)
        self._childItems.insert(firstIdx, self._childItems.pop(secondIdx))
        self._childItems.insert(secondIdx, firstItem)
        return True

    ## Ищет элемент в дереве (текущем и дочерних элементах), для которого будет истинным значение переданного предиката сравнения.
    # @param predicate: функция или метод класса от одного аргумента, которая возвращает True, 
    #                   если переданный в нее аргумент удовлетворяет условию поиска, иначе возвращает False
    # @return: найденный объект или None, если не один из дочерних элементов не удовлетворяет предикату сравнения.
    def findItem(self, predicate, depth=None):
        if callable(predicate):
            if predicate(self):
                return self

            if depth is None or depth > 0:
                for child in self.children():
                    result = child.findItem(predicate,
                                            depth - 1 if depth is not None else None)
                    if result is not None:
                        return result
        return None

    ## Читает элемент из XML
    # @param xmlReader: ссылка на QtCore.QXmlStreamReader, который осуществляет чтение из XML
    # @param withCheckState: Считывать из XML также и check states (а не только структуру)
    def readFromXml(self, xmlReader, withCheckState=True, xmlInfo=None):
        if not xmlInfo:
            xmlInfo = {'tagName': 'item',
                       'attributesNameList': [],
                       'checkStateAttributeName': 'checkState'}
        if not isinstance(xmlReader, QtCore.QXmlStreamReader):
            return False

        if not (xmlReader.isStartElement() and xmlReader.name() == xmlInfo.get('tagName', 'item')):
            return False

        # инициализация пустыми данными
        self._itemData = [None] * self.columnCount()
        success = True
        checkState = None
        attributesNameList = xmlInfo.get('attributesNameList', [])
        for attr in xmlReader.attributes():
            attrName = unicode(attr.name())
            if attr.name() == xmlInfo.get('checkStateAttributeName', 'checkState'):
                checkState = bool(int(attr.value().toString().toInt()[0]))
                continue

            dataIdx = attributesNameList.index(attrName) if attrName in attributesNameList else None
            if dataIdx not in xrange(len(self._itemData)):
                # Получение части без номера (общей) для шаблона имени аттрибута
                templatePart = self._defaultAttrNameTemplate.replace(u'%s', u'')
                # Получение номера атрибута методом отсечения общей шаблонной части
                idxPart = unicode(attr.name()).replace(templatePart, u'')
                # Приведение номера к числовому виду, если он не содержит ничего кроме цифр
                dataIdx = int(idxPart) if idxPart.isdigit() else None

            if dataIdx in xrange(len(self._itemData)):
                self._itemData[dataIdx] = unicode(attr.value())

        xmlReader.readNext()
        while not xmlReader.isEndElement():
            if xmlReader.isStartElement() and xmlReader.name() == xmlInfo.get('tagName', 'item'):
                newItemIdx = self.childCount()
                if self.insertChildren(position=newItemIdx, count=1, itemData=[]):
                    childItem = self.children()[newItemIdx]
                    success &= childItem.readFromXml(xmlReader, xmlInfo=xmlInfo)

            xmlReader.readNext()

        if checkState is not None:
            self.setCheckState(checkState)

        self.updateCheckState()

        if not (xmlReader.isEndElement() and xmlReader.name() == xmlInfo.get('tagName', 'item')):
            return False

        return success

    ## Записывает элемент в XML
    # @param xmlWriter: ссылка на QtCore.QXmlStreamWrtiter, который осуществляет запись в XML
    # @param withCheckState: Записывать в XML также и check states (а не только структуру)
    def writeToXml(self, xmlWriter, withCheckState=True, xmlInfo=None):
        if not xmlInfo:
            xmlInfo = {'tagName': 'item',
                       'attributesNameList': [],
                       'checkStateAttributeName': 'checkState'}
        if not isinstance(xmlWriter, QtCore.QXmlStreamWriter):
            return False

        xmlWriter.writeStartElement(xmlInfo.get('tagName', 'item'))
        attributesNameList = xmlInfo.get('attributesNameList', [])
        for idx, data in enumerate(self._itemData):
            attrName = attributesNameList[idx] if idx in xrange(len(attributesNameList)) \
                else self._defaultAttrNameTemplate % idx
            xmlWriter.writeAttribute(attrName, unicode(data))
        success = True

        if withCheckState and xmlInfo.get('checkStateAttributeName', 'checkState'):
            xmlWriter.writeAttribute(xmlInfo.get('checkStateAttributeName', 'checkState'),
                                     QtCore.QString.number(self._checkState))

        for child in self._childItems:
            success &= child.writeToXml(xmlWriter, xmlInfo=xmlInfo)
        xmlWriter.writeEndElement()
        return success


class CEditableTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(CEditableTreeModel, self).__init__(parent)
        self._rootItem = None
        self.initRootItem()
        self._editable = True
        self._xmlInfo = {}

    def setXmlInfo(self, xmlInfo):
        self._xmlInfo = dict(xmlInfo)

    def isEditable(self):
        return self._editable

    def setEditable(self, editable):
        self._editable = editable

    # Очистка модели
    def clear(self):
        self._rootItem.removeChildren(0, self._rootItem.childCount())

    ## Инициализация корневого элемента
    def initRootItem(self):
        self._rootItem = CEditableTreeItem(None, [u''], QtCore.Qt.Unchecked)

    def columnEditable(self, column):
        return True


        # TODO: atronah:

    #    def setHeaderData():

    def isCheckable(self):
        return True

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        column = index.column()

        flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        if column == 0 and self.isCheckable():
            flags |= QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate
        if self.columnEditable(column) and self.isEditable():
            flags |= QtCore.Qt.ItemIsEditable

        return flags

    def getRootItem(self):
        return self.getItem()

    def getItem(self, index=QtCore.QModelIndex()):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self._rootItem

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        item = self.getItem(index)
        parentItem = item.parent()
        if parentItem == self._rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.positionInParent(), index.column(), parentItem)

    def index(self, row, column, parentIndex=QtCore.QModelIndex()):
        parentItem = self.getItem(parentIndex)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return QtCore.QModelIndex()

    def rowCount(self, parentIndex=QtCore.QModelIndex()):
        return self.getItem(parentIndex).childCount()

    def columnCount(self, parentIndex=QtCore.QModelIndex()):
        return self._rootItem.columnCount()

    def hasChildren(self, index=QtCore.QModelIndex()):
        return self.getItem(index).hasChildren()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()

        item = self.getItem(index)
        return item.data(index.column(), role)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False

        if role == QtCore.Qt.CheckStateRole:
            if value in [QtCore.Qt.Checked, QtCore.Qt.Unchecked]:
                # atronah: update check state for all children
                for row in xrange(self.rowCount(index)):
                    childIdx = self.index(row, index.column(), index)
                    self.dataChanged.emit(childIdx, childIdx)

        item = self.getItem(index)
        success = item.setData(index.column(), value, role)
        self.dataChanged.emit(index, index)

        if success and role == QtCore.Qt.CheckStateRole:
            # atronah: update check state for all parents
            parentIndex = index.parent()
            while parentIndex.isValid():
                self.dataChanged.emit(parentIndex, parentIndex)
                parentIndex = parentIndex.parent()

        return success

    def headerData(self, *args, **kwargs):
        return QtCore.QVariant('test')
        # TODO: atronah: implement
        return QtCore.QAbstractItemModel.headerData(self, *args, **kwargs)

    def setHeaderData(self, *args, **kwargs):
        return QtCore.QAbstractItemModel.setHeaderData(self, *args, **kwargs)

    def insertColumns(self, position, columns, parent=QtCore.QModelIndex()):
        self.beginInsertColumns(parent, position, position + columns - 1)
        success = self._rootItem.insertColumns(position, columns)
        self.endInsertColumns()
        return success

    def removeColumns(self, position, columns, parent=QtCore.QModelIndex()):
        self.beginRemoveColumns(parent, position, position + columns - 1)
        success = self._rootItem.removeColumns(position, columns)
        self.endRemoveColumns()
        return success

    def insertChildren(self, position, count, parent, itemData=None):
        item = self.getItem(parent)
        self.beginInsertRows(parent, position, position + count - 1)
        success = item.insertChildren(position, count, itemData)
        self.endInsertRows()
        return success

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        return self.insertChildren(position, rows, parent)

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        item = self.getItem(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        success = item.removeChildren(position, rows)
        self.endRemoveRows()
        return success

    ## Загрузка дерева из XML
    # @param source: источник данных XML, представленный либо в виде строки (QString) либо в виде устройства ввода-вывода (QIODevice)
    def readFromXml(self, source):
        if not isinstance(source, (QtCore.QIODevice, QtCore.QString)):
            return False

        self.clear()
        result = False
        xmlReader = QtCore.QXmlStreamReader(source)
        while not xmlReader.atEnd():
            xmlReader.readNext()
            # Если найден стартовый элемент и еще не было успешного чтения модели
            if xmlReader.isStartElement() and not result:
                result = self._rootItem.readFromXml(xmlReader, xmlInfo=self._xmlInfo)
        self.reset()
        return result

    ## Запись дерева в XML
    # @param destination: хранилище для записи данных XML, представленный либо в виде строки (QString) либо в виде устройства ввода-вывода (QIODevice)
    def writeToXml(self, destination):
        xmlWriter = QtCore.QXmlStreamWriter(destination)
        xmlWriter.setAutoFormatting(True)
        xmlWriter.writeStartDocument()
        result = self._rootItem.writeToXml(xmlWriter, xmlInfo=self._xmlInfo)
        xmlWriter.writeEndDocument()

        return result


class CGUITreeModelItem(CEditableTreeItem):
    def __init__(self, parentItem, itemData, buddies=None, checkState=True, canBeHidden=True):
        super(CGUITreeModelItem, self).__init__(parentItem, itemData, checkState)
        self._canBeHidden = canBeHidden
        self._buddies = buddies if isinstance(buddies, list) else []

    def canBeHidden(self):
        return self._canBeHidden

    def getFullParentName(self, nameColumn):
        nameParts = []
        parent = self.parent()
        while parent:
            nameParts.append(forceString(parent.data(nameColumn)))
            parent = parent.parent()
        return '.'.join(nameParts[::-1][1:])

    def getFullName(self, nameColumn):
        resultName = forceString(self.data(nameColumn))
        parentNamePart = self.getFullParentName(nameColumn)
        return resultName if not parentNamePart else (parentNamePart + '.' + resultName)

    def getBuddiesNameList(self, nameColumn):
        resultNameList = []
        parentNamePart = self.getFullParentName(nameColumn)
        for buddyName in self._buddies:
            resultNameList.append(buddyName if not parentNamePart else (parentNamePart + '.' + buddyName))
        return resultNameList

    def getLevel(self, noMoreThan=None):
        level = 0
        parent = self.parent()
        while parent:
            level += 1
            if noMoreThan and level >= noMoreThan:
                break
            parent = parent.parent()

        return level

    ## Возвращает список имен всех (если checkState = None) дочерних объектов, 
    #     либо только тех, чей статус соответствует указанному.
    # @param checkState: состояние элементов (Qt.CheckState), чьи имена добавлять в результат. 
    #                    dafault: None (т.е. добавляются имена всех элементов)
    def getChildrenNameList(self, nameColumn, checkState=None):
        resultList = []
        for child in self.children():
            # atronah: мне влом описывать логику ниже, но она позволяет не пропускать "включенный" элемент
            # при поиске "выключенных", если у него один из детей "выключен"
            if checkState is not None and child.isChecked() != bool(
                    checkState) and child.checkState() != QtCore.Qt.PartiallyChecked:
                continue

            resultList.extend(child.getChildrenNameList(nameColumn, checkState))

            if checkState is not None and checkState != child.checkState():  # более точная проверка, нежели выше.
                continue

            if child.canBeHidden():  # Не разрешать скрытие первого уровня объектов
                resultList.append(child.getFullName(nameColumn))
                resultList.extend(child.getBuddiesNameList(nameColumn))

        return resultList

    ## Устанавливает состояние всех дочерних элементов в указанное состояние newCheckState, 
    #    если их имя есть в указаном списке имен nameList
    #    @param nameList: список имен элементов, чье состояние надо обновить
    #    @param newCheckState: новое состояние
    def updateChildrenCheckStateByNameList(self, nameList, nameColumn, newCheckState=QtCore.Qt.Unchecked):
        if newCheckState not in [QtCore.Qt.Unchecked, QtCore.Qt.PartiallyChecked, QtCore.Qt.Checked]:
            return

        for child in self.children():
            if child.getFullName(nameColumn) in nameList:
                child.setCheckState(newCheckState)
            else:
                child.setCheckState(not bool(newCheckState))
            if child.isChecked():
                child.updateChildrenCheckStateByNameList(nameList, nameColumn, newCheckState)


class CGuiHidderTreeModel(CEditableTreeModel):
    xmlTagName = 'item'
    xmlAttributesNameList = [u'title', u'objectName']
    xmlCheckStateAttributeName = 'checkState'

    ciTitle = 0
    ciName = 1

    def __init__(self, parent=None):
        super(CGuiHidderTreeModel, self).__init__(parent)
        self.setXmlInfo({'tagName': self.xmlTagName,
                         'attributesNameList': self.xmlAttributesNameList,
                         'checkStateAttributeName': self.xmlCheckStateAttributeName})

    def flags(self, index):
        flags = super(CGuiHidderTreeModel, self).flags(index)
        return flags

    ## Инициализация корневого элемента
    def initRootItem(self):
        self._rootItem = CGUITreeModelItem(parentItem=None,
                                           itemData=[u'Вистамед', u's11App'],
                                           buddies=None,
                                           checkState=QtCore.Qt.Checked,
                                           canBeHidden=False)
        self._rootItem.insertColumns(self.columnCount(), 2 - self.columnCount())

    ## Получение списка имен всех объектов (или только с указанынм состоянием)
    def itemNameList(self, checkState=None, parentObjectName=None):
        item = self._rootItem
        if isinstance(parentObjectName, basestring):
            nameParts = parentObjectName.split('.')
            for objectName in nameParts:
                item = item.findItem(lambda i: forceString(i.data(self.ciName)) == objectName)
                if item is None:
                    return []
        return item.getChildrenNameList(self.ciName, checkState)

    ## Устанавливает состояние всех элементов с именем из nameList в указанное состояние newCheckState, 
    #    а остальным устанавливает противоположное состояние
    #    @param nameList: список имен элементов
    #    @param newCheckState: новое состояние
    def updateCheckStateByNameList(self, nameList, newCheckState=QtCore.Qt.Unchecked):
        self.getRootItem().updateChildrenCheckStateByNameList(nameList, self.ciName, newCheckState)

    ## Получает список всех описанных имен из исходного XML файла
    # atronah: deprecated
    @staticmethod
    def allNamesFromXml(xmlSource):
        result = set()

        if not isinstance(xmlSource, (QtCore.QIODevice, QtCore.QString)):
            return result

        if len(CGuiHidderTreeModel.xmlAttributesNameList) <= 1:
            return result

        xmlReader = QtCore.QXmlStreamReader(xmlSource)
        xmlReader.readNext()
        while not xmlReader.atEnd():
            if xmlReader.isStartElement() and xmlReader.name() == CGuiHidderTreeModel.xmlTagName:
                objectName = unicode(xmlReader.attributes().value(CGuiHidderTreeModel.xmlAttributesNameList[1]))
                if objectName:
                    result.add(objectName)
            xmlReader.readNext()

        return result

    ## Формирует текст для вставки в вики-статью 
    # со списком всех доступных для скрытия элементов в виде иерархического маркированного списка
    def exportItemsForWiki(self):
        descriptionLinePattern = "%s '''%s''' (''%s'')"

        def exportItemWithChildren(item, depth):
            resultLines = []
            if item:
                title = forceString(item.data(self.ciTitle)).replace('\n', ' ')
                objectNameParts = [forceString(item.data(self.ciName))]
                parentItem = item.parent()
                while parentItem and parentItem != self._rootItem:
                    objectNameParts.append(forceString(parentItem.data(self.ciName)))
                    parentItem = parentItem.parent()

                resultLines.append(descriptionLinePattern % ('*' * depth,
                                                             title,
                                                             '.'.join(objectNameParts[::-1])))
                for child in item.children():
                    resultLines.extend(exportItemWithChildren(child, depth + 1))
            return resultLines

        return '\n'.join(exportItemWithChildren(self._rootItem, 0))


class CConfigureWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(CConfigureWindow, self).__init__(parent)
        from PyQt4 import uic
        self.ui = uic.loadUi("ConfigureWindow.ui", self)
        self.setTreeModel(CGuiHidderTreeModel())
        self._preferences = CPreferences('S11App.ini')

    def setTreeModel(self, model):
        self.ui.treeView.setModel(model)

    def treeModel(self):
        return self.ui.treeView.model()

    @QtCore.pyqtSlot()
    def on_btnAdd_clicked(self):
        idx = self.ui.treeView.currentIndex()
        if idx.isValid():
            idx.model().insertChildren(-1, 1, parent=idx, itemData=[u'New item'])

    @QtCore.pyqtSlot()
    def on_btnDelete_clicked(self):
        idx = self.ui.treeView.currentIndex()
        if idx.isValid():
            idx.model().removeRows(position=idx.row(),
                                   rows=1,
                                   parent=idx.parent())

    @QtCore.pyqtSlot()
    def on_btnOpenFromFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(parent=self,
                                                     caption=u'Выберите файл для открытия',
                                                     directory=QtCore.QDir.homePath(),
                                                     filter=u'XML files (*.xml)')
        inpXmlFile = QtCore.QFile(fileName)
        if inpXmlFile.open(QtCore.QFile.ReadOnly):
            self.treeModel().readFromXml(inpXmlFile)
        else:
            raise CException(u'error save to file')

    @QtCore.pyqtSlot()
    def on_btnSaveToFile_clicked(self):
        fileName = QtGui.QFileDialog.getSaveFileName(parent=self,
                                                     caption=u'Выберите файл для сохранения',
                                                     directory=QtCore.QDir.homePath(),
                                                     filter=u'XML files (*.xml)')

        outXmlFile = QtCore.QFile(fileName)
        if outXmlFile.open(QtCore.QFile.WriteOnly):
            self.treeModel().writeToXml(outXmlFile)
        else:
            raise CException(u'error save to file')

    def getDbConnection(self):
        dlg = CConnectionDialog(self)
        db = None

        self._preferences.load(onlyTheseGroups=[u'db'])
        dlg.setDriverName(self._preferences.dbDriverName)
        dlg.setServerName(self._preferences.dbServerName)
        dlg.setServerPort(self._preferences.dbServerPort)
        dlg.setDatabaseName(self._preferences.dbDatabaseName)
        dlg.setCompressData(self._preferences.dbCompressData)
        dlg.setUserName(self._preferences.dbUserName)
        dlg.setPassword(self._preferences.dbPassword)
        dlg.setNewAuthorizationScheme(self._preferences.dbNewAuthorizationScheme)
        if dlg.exec_():
            connectionInfo = {'driverName': dlg.driverName(),
                              'host': dlg.serverName(),
                              'port': dlg.serverPort(),
                              'database': dlg.databaseName(),
                              'user': dlg.userName(),
                              'password': dlg.password(),
                              'connectionName': u'guiHidder',
                              'compressData': dlg.compressData(),
                              'afterConnectFunc': None}
            db = connectDataBaseByInfo(connectionInfo)

        return db

    @QtCore.pyqtSlot()
    def on_btnOpenFromDb_clicked(self):
        db = self.getDbConnection()
        if not db:
            return
        try:

            tableGloabalPreferenes = db.table(u'GlobalPreferences')
            record = db.getRecordEx(table=tableGloabalPreferenes,
                                    cols=u'*',
                                    where=[tableGloabalPreferenes['code'].like(u'guiHidderTree')])
            if not record:
                return

            inpXML = record.value('extendedValue').toString()
            self.treeModel().readFromXml(inpXML)
        except:
            pass

    @QtCore.pyqtSlot()
    def on_btnSaveToDb_clicked(self):
        db = self.getDbConnection()
        if not db:
            return
        tableGloabalPreferenes = db.table(u'GlobalPreferences')
        record = db.getRecordEx(table=tableGloabalPreferenes,
                                cols=u'*',
                                where=[tableGloabalPreferenes['code'].like(u'guiHidderTree')])
        if not record:
            record = tableGloabalPreferenes.newRecord()
            record.setValue('code', QtCore.QVariant(u'guiHidderTree'))
            record.setValue('name', QtCore.QVariant(u'Дерево настроек видимости элементов интерфейса'))

        outXML = QtCore.QString(u'')
        self.treeModel().writeToXml(outXML)
        record.setValue('extendedValue', QtCore.QVariant(outXML))
        db.insertOrUpdate(tableGloabalPreferenes, record)


def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    window = CConfigureWindow()
    window.show()
    return app.exec_()


if __name__ == '__main__':
    main()
