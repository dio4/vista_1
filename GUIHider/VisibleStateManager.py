# -*- coding: utf-8 -*-
from PyQt4 import QtCore

from GUIHider.GUITreeModel  import CGuiHidderTreeModel, CGUITreeModelItem
from GUIHider.VisibleControlMixin import CVisibleControlMixin
from library.Utils          import forceString, MQSingleton

'''
Created on 03.04.2014

@author: atronah
'''


class CVisibleStateManager(QtCore.QObject):
    u"""Хранит информацию о всех элементах интерфейса, для которых доступно скрытие."""
    __metaclass__ = MQSingleton
    
    def __init__(self, parent = None):
        super(CVisibleStateManager, self).__init__(parent)
        self._model = CGuiHidderTreeModel(self)

    def model(self):
        return self._model

    def registerModuleClass(self, moduleClass):
        if not issubclass(moduleClass, CVisibleControlMixin):
            return False
        self.registerObject(fullName=moduleClass.moduleName(),
                            title=moduleClass.moduleTitle())
        for objName, title, buddies in moduleClass.hiddableChildren():
            self.registerObject(fullName=objName,
                                title=title,
                                buddies=buddies)
        return True

    def registerObject(self, fullName, title, buddies=None, defaultState=QtCore.Qt.Checked):
        u"""Регистрирует элемент интерфейса как доступный для скрытия"""
        rootItem = self.model().getRootItem()
        
        if not isinstance(fullName, basestring):
            fullName = forceString(fullName)
        
        parentItem = rootItem
        nameParts = fullName.split('.')
        for namePart in nameParts:
            childItem = parentItem.findItem(lambda item: forceString(item.data(CGuiHidderTreeModel.ciName)) == namePart,
                                             depth=1)
            if not childItem:
                childItem = CGUITreeModelItem(parentItem=parentItem,
                                              itemData=[None, namePart],
                                              buddies=buddies,
                                              checkState=defaultState,
                                              canBeHidden=bool(parentItem != rootItem))
                parentItem.addChildren(childItem)
            parentItem = childItem
                    
        parentItem.setCheckState(defaultState)
        if title is not None:
            parentItem.setData(CGuiHidderTreeModel.ciTitle, title)
