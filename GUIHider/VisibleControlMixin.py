# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################
from itertools import chain

from PyQt4 import QtGui, QtCore

from library.Utils import forceString

'''
Created on 04.04.2014

@author: atronah
'''
class CVisibleControlMixin:
#    skippedWidgetTypes = (QtGui.QStackedWidget, QtGui.QTabBar, QtGui.QTabWidget, QtGui.QScrollArea)

    @staticmethod
    def moduleName():
        raise NotImplementedError

    
    @staticmethod
    def moduleTitle():
        raise NotImplementedError


    @classmethod
    def normalizeHiddableChildren(cls, descriptionList = []):
        """
        Производит нормализацию переданного списка описаний скрываемых элементов.
        Принимает на вход более произвольно оформленное описание скрываемых элементов и приводит к формату, ожидаемому
        на выходе метода hiddableChildren

        :param descriptionList: список формальных описаний скрываемых элементов в формате:
            (inplaceObjectName, title, [buddiesList]), где
                inplaceObjectName - имя скрываемого объекта с учетом иерархии, но имя модуля может быть опущено,
                title - отображаемое название элемента
                buddiesList - список дополнительных элементов, которые надо скрыть вместе с основным (может быть опущено)
        :return:
        """
        return [((u'' if childItem[0].startswith(cls.moduleName())
                      else cls.moduleName() + '.') + childItem[0],  # имя компонента с учетом имени модуля (если он пропущен)
                 childItem[1],                                      # Отображаемое название компонента
                 childItem[2] if len(childItem) > 2 else [])        # Дополнительные объекты, которые надо скрывать вместе с основным компонентом
                for childItem in descriptionList]
    
    
    ## Возвращает список кортежей с описанием объектов, скрываемых в данном модуле.
    #    элемент списка (кортеж) должен иметь вид: ('<hierarchy_as_objectNames_separated_by_dot>', 
    #                                               '<title>')
    # Необходимо, чтобы на этапе загрузки модуля при запуске приложения, 
    # основной класс приложения мог узнать и зарегистрировать все доступные для скрытия объекты.
    @classmethod
    def hiddableChildren(cls):
        return []
    
    
    @classmethod
    def reduceNames(cls, nameList):
        """
        Преобразует список имен элементов с учетом иерархии, в список имен без учета иерархии.
        В каждом элементе переданного списка оставляет только последнюю часть имени, после последней точки.

        raipc: Добавил к записанным в БД objectName те, которые прописываются разделяемыми .ui файлами. Должно решить
        проблему с нерабочими настройками отключения вкладок.

        :param nameList: список имен с учетом иерархии
        :return: Список имен объектов без учета иерархии
        """
        reducedNames = [name.split('.')[-1] for name in nameList]
        hiddableChildrenDict = dict([(s[0].split('.')[-1], s[1:]) for s in cls.hiddableChildren()])
        additionalNames = list(chain.from_iterable([hiddableChildrenDict[i][1] for i in reducedNames if i in hiddableChildrenDict]))
        return reducedNames + additionalNames




    def isVisibleObject(self, obj):
        return forceString(obj.objectName()) not in self._invisibleObjectsNameList
        
    
    @staticmethod
    def hideTabWidgets(tabWidget, invisibleObjectsNameList):
        processedNameList = []
        currentWidget = tabWidget.currentWidget()
        currentIndex = tabWidget.currentIndex()
        for tabIdx in range(tabWidget.count())[::-1]:
            tabObjectName = forceString(tabWidget.widget(tabIdx).objectName())
            if tabObjectName in invisibleObjectsNameList:
                if currentWidget == tabWidget.widget(tabIdx):
                    currentWidget = None
                tabWidget.removeTab(tabIdx)
                processedNameList.append(tabObjectName)

        if currentWidget != tabWidget.currentWidget():
            newIndex = 0  # if currentWidget is None else tabWidget.indexOf(currentWidget)
            tabWidget.setCurrentIndex(newIndex)
            if currentIndex == newIndex:
                tabWidget.currentChanged.emit(newIndex)
            else:
                tabWidget.setCurrentIndex(newIndex)

        return processedNameList

    @classmethod
    def updateVisibleState(cls, obj, invisibleObjectsNameList):
        """
        Обновляет состояние видимости всех объектов из списка children и их дочерних подобъектов.

        :param obj: объект, для потомков которого необходимо обновить состояние видимости
        :type obj: QObject
        :param invisibleObjectsNameList: список имен объектов, которые необходимо скрыть
                                        формат формат элементов списка:
                                         <Название> - Название виджета, который необходимо скрыть;
                                         <НазваниеТаблицы:НазваниеКолонки> - Название столбца в таблице, который необходимо скрыть;
                                         <НазваниеButtonBox:НазваниеСтандартнойКнопки> - Название стандартной кнопки, которую необходимо скрыть. Кастомные кнопки скрывать как обычный элемент
                                            Для buttonBox желательно задавать уникальные имена, чтобы скрывалось только в определённом, а не во всех;
        :type invisibleObjectsNameList: list (of string)
        """
        parentChildrenDict = {}
        i = 0
        while i in range(len(invisibleObjectsNameList)):
            if ':' in invisibleObjectsNameList[i]:
                parentChildrenTuple = invisibleObjectsNameList[i].split(':')
                parentChildrenDict.setdefault(parentChildrenTuple[0], []).append(parentChildrenTuple[-1])
                invisibleObjectsNameList.remove(invisibleObjectsNameList[i])
            else:
                i += 1

        standardButtons = cls.getStandardButtons()

        for objectName in invisibleObjectsNameList:
            for child in obj.findChildren(QtCore.QObject, objectName):
                child.setVisible(False)

                if isinstance(child, QtGui.QLabel):
                    buddy = child.buddy()
                    if isinstance(buddy, QtGui.QWidget):
                        buddy.setVisible(False)

        for tabWidget in obj.findChildren(QtGui.QTabWidget):
            cls.hideTabWidgets(tabWidget, invisibleObjectsNameList)

        for objectName, children in parentChildrenDict.iteritems():
            for child in obj.findChildren(QtCore.QObject, objectName):
                if isinstance(child, QtGui.QTableView):
                    columns = set(children)
                    for i, col in enumerate(child.model().cols()):
                        if set(col.fields()) & columns:
                            child.hideColumn(i)

                if isinstance(child, QtGui.QDialogButtonBox):
                    buttons = children
                    for button in buttons:
                        child.removeButton(child.button(standardButtons.get(button)))

        # needProcessingList = [children]
        # processedNameList = []
        # while needProcessingList:
        #     objList = needProcessingList.pop(0)
        #     for obj in objList:
        #         if isinstance(obj, QtGui.QTabWidget):
        #             processedNameList.extend(cls.hideTabWidgets(obj, invisibleObjectsNameList))
        #
        #         if isinstance(obj, QtGui.QWidget):
        #             objectName = forceString(obj.objectName())
        #
        #             if objectName in processedNameList:
        #                 continue
        #
        #             if objectName in invisibleObjectsNameList:
        #                 obj.setVisible(False)
        #                 if isinstance(obj, QtGui.QLabel):
        #                     buddy = obj.buddy()
        #                     if isinstance(buddy, QtGui.QWidget):
        #                         buddy.setVisible(False)
        #                 continue
        #
        #             if isinstance(obj, QtGui.QTableView):
        #                 if parentChildrenDict.has_key(objectName):
        #                     columns = set(parentChildrenDict[objectName])
        #                     cols = obj.model().cols()
        #                     for i in range(len(cols)):
        #                         if set(cols[i].fields()) & columns:
        #                             obj.hideColumn(i)
        #
        #             if isinstance(obj, QtGui.QDialogButtonBox):
        #                 if parentChildrenDict.has_key(objectName):
        #                     buttons = parentChildrenDict[objectName]
        #                     for i in range(len(buttons)):
        #                         obj.removeButton(obj.button(standardButtons.get(buttons[i])))
        #                     del parentChildrenDict[objectName]
        #
        #         objChildren = obj.children()
        #         if objChildren: # добавить в стек просмотра дочерние элементы текущего виджета с обновлением частей имени
        #             needProcessingList.append(objChildren)

    @staticmethod
    def getStandardButtons():
        return {'Ok':             QtGui.QDialogButtonBox.Ok,
               'Open':            QtGui.QDialogButtonBox.Open,
               'Save':            QtGui.QDialogButtonBox.Save,
               'Cancel':          QtGui.QDialogButtonBox.Cancel,
               'Close':           QtGui.QDialogButtonBox.Close,
               'Discard':         QtGui.QDialogButtonBox.Discard,
               'Apply':           QtGui.QDialogButtonBox.Apply,
               'Reset':           QtGui.QDialogButtonBox.Reset,
               'RestoreDefaults': QtGui.QDialogButtonBox.RestoreDefaults,
               'Help':            QtGui.QDialogButtonBox.Help,
               'SaveAll':         QtGui.QDialogButtonBox.SaveAll,
               'Yes':             QtGui.QDialogButtonBox.Yes,
               'YesToAll':        QtGui.QDialogButtonBox.YesToAll,
               'No':              QtGui.QDialogButtonBox.No,
               'NoToAll':         QtGui.QDialogButtonBox.NoToAll,
               'Abort':           QtGui.QDialogButtonBox.Abort,
               'Retry':           QtGui.QDialogButtonBox.Retry,
               'Ignore':          QtGui.QDialogButtonBox.Ignore
               }