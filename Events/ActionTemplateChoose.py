# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from library.AgeSelector         import checkAgeSelector, parseAgeSelector
from library.TreeModel           import CTreeModel, CDBTreeItem, CTreeItemWithId
from library.Utils               import forceInt, forceRef, forceString, forceStringEx

class CActionTemplateTreeItem(CDBTreeItem):
    def __init__(self, parent, name, id, model, actionId, filter):
        CDBTreeItem.__init__(self, parent, name, id, model)
        CTreeItemWithId.__init__(self, parent, name, id)
        self._actionId = actionId
        self._filter = filter


    def flags(self):
        flags = QtCore.Qt.ItemIsEnabled
        if self._actionId or not self._filter.removeEmptyNodes:
            flags |= QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        return flags

    def isEmpty(self):
        if self._actionId != None:
            return False
        for child in self.items():
            if not child.isEmpty():
                return False
        return True

    def loadChildren(self):
        result = []
        db = QtGui.qApp.db
        table = db.table('ActionTemplate')

        tableAction = db.table('Action')
        cond = [
            table['group_id'].eq(self._id),
            table['deleted'].eq(0)
        ]
        if self._filter.actionTypeId:
            cond.append(db.joinOr([tableAction['actionType_id'].eq(self._filter.actionTypeId), table['action_id'].isNull()]))
        if self._filter.personId:
            cond.append(db.joinOr([table['owner_id'].eq(self._filter.personId), table['owner_id'].isNull()]))
        if self._filter.specialityId:
            cond.append(db.joinOr([table['speciality_id'].eq(self._filter.specialityId), table['speciality_id'].isNull()]))
        if self._filter.clientSex:
            cond.append(table['sex'].inlist([self._filter.clientSex, 0]))

        query = db.query(db.selectStmt(table.leftJoin(tableAction, tableAction['id'].eq(table['action_id'])),
                         [table['id'].name(),
                          table['name'].name(),
                          table['action_id'].name(),
                          table['age'].name()], where=cond, order=table['name'].name()))
        while query.next():
            record = query.record()
            age = forceString(record.value('age'))
            if age and self._filter.clientAge:
                if not checkAgeSelector(parseAgeSelector(age), self._filter.clientAge):
                    continue
            id   = forceInt(record.value('id'))
            name = forceString(record.value('name'))
            actionId = forceRef(record.value('action_id'))
            child = CActionTemplateTreeItem(self, name, id, self.model, actionId, self._filter)
            if not self._filter.removeEmptyNodes or not child.isEmpty():
                result.append(child)
        return result

    def setValue(self, value):
        db = QtGui.qApp.db
        table = db.table('ActionTemplate')
        record = db.getRecord(table, ['id', 'name'], self.id())
        if record:
            record.setValue('name', value)
            if db.updateRecord(table, record):
                return True
        return False


class CActionTemplateRootTreeItem(CActionTemplateTreeItem):
    def __init__(self, model, filter):
        CActionTemplateTreeItem.__init__(self, None, u'-', None, model, None, filter)



class CActionTemplateModel(CTreeModel):
    class CFilter:
        def __init__(self, actionTypeId, personId, specialityId, clientSex, clientAge, removeEmptyNodes):
            self.actionTypeId = actionTypeId
            self.personId = personId
            self.specialityId = specialityId
            self.clientSex = clientSex
            self.clientAge = clientAge
            self.removeEmptyNodes = removeEmptyNodes

    def __init__(self, parent, actionTypeId, personId, specialityId, clientSex, clientAge, removeEmptyNodes=True):
        CTreeModel.__init__(self, parent, CActionTemplateRootTreeItem(self, CActionTemplateModel.CFilter(actionTypeId, personId, specialityId, clientSex, clientAge, removeEmptyNodes)))
        self.rootItemVisible = False


    def setFilter(self, actionTypeId, personId, specialityId, clientSex, clientAge, removeEmptyNodes=True):
        self.getRootItem()._filter = CActionTemplateModel.CFilter(actionTypeId, personId, specialityId, clientSex, clientAge, removeEmptyNodes)
        self.update()


    def filter(self):
        return self.getRootItem()._filter


    def update(self):
        self.getRootItem().removeChildren()
        self.reset()


    def isEmpty(self):
        return self.getRootItem().isEmpty()

    def setData(self, index, value, role = None):
        if role == QtCore.Qt.EditRole and forceStringEx(value) != '':
            column = index.column()
            row = index.row()
            item = index.internalPointer()
            if item.setValue(value):
                self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
                return True
        return False

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()

        column = index.column()
        if role == QtCore.Qt.EditRole:
            item = index.internalPointer()
            if item:
                return item.data(index.column())
        else:
            return CTreeModel.data(self, index, role)

#    def headerData(self, section, orientation, role):
#        if role == QtCore.Qt.DisplayRole:
#            return QtCore.QVariant(u'Шаблоны свойств')
#        return QtCore.QVariant()


class CActionTemplateTreeView(QtGui.QTreeView):
    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)
        self.header().hide()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        self.setMinimumHeight(300)
        self.connect(self, QtCore.SIGNAL('expanded(QModelIndex)'), self.onExpanded)
#        self.connect(self, QtCore.SIGNAL('collapsed(QModelIndex)'), self.onCollapsed)
        self.searchString = ''
        self.searchParent = None
        self.keyEnabled = False


    def setModel(self, model):
        QtGui.QTreeView.setModel(self, model)
        #self.connect(self.model(), QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), self.on_dataChanged)
        self.expandAll()


    def setRootIndex(self, index):
        pass


    def setRealRootIndex(self, index):
        QtGui.QTreeView.setRootIndex(self, index)
#        self.expandAll()


    def onExpanded(self, index):
        self.scrollTo(index, QtGui.QAbstractItemView.PositionAtTop)

    def selectionChanged(self, QItemSelection, QItemSelection_1):
        QtGui.QTreeView.selectionChanged(self, QItemSelection, QItemSelection_1)
        self.emit(QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'), QItemSelection, QItemSelection_1)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left or event.key() == QtCore.Qt.Key_Minus:
            current = self.currentIndex()
            if self.isExpanded(current) and self.model().rowCount(current):
                self.collapse(current)
            else:
                self.setCurrentIndex(current.parent())
                current = self.currentIndex()
                self.collapse(current)
                self.scrollTo(current, QtGui.QAbstractItemView.PositionAtTop)
            event.accept()
            return
        if (event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return) and (not self.state() == self.EditingState):
            event.accept()
            self.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.currentIndex())
            return
        if event.key() == QtCore.Qt.Key_Delete and not self.state() == self.EditingState and self.keyEnabled:
            event.accept()
            self.emit(QtCore.SIGNAL('deleteItem()'))
            return
        if event.key() == QtCore.Qt.Key_Space and not self.state() == self.EditingState and self.keyEnabled:
            event.accept()
            self.emit(QtCore.SIGNAL('renameItem()'))
            return
        return QtGui.QTreeView.keyPressEvent(self, event)

    def dataChanged(self, index, index_1):
        self.emit(QtCore.SIGNAL('updateTreeView(QModelIndex)'), index)

    def editItem(self, index):
        self.edit(index)

    def closeEditor(self, editor, hint):
        id = self.currentIndex().internalPointer().id()
        QtGui.QTreeView.closeEditor(self, editor, 0)


class CActionTemplatePopup(QtGui.QFrame):
    __pyqtSignals__ = ('templateSelected(int)',
                       'closePopup()',
                      )

    def __init__(self, parent = None):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setAttribute(QtCore.Qt.WA_WindowPropagation)
        self.treeView=CActionTemplateTreeView(self)
        self.widgetLayout = QtGui.QVBoxLayout(self)
        self.widgetLayout.setMargin(0)
        self.widgetLayout.setSpacing(0)
        self.widgetLayout.addWidget(self.treeView)

        self.btnSelect = QtGui.QPushButton(u'Выбрать', self)
        self.btnRename = QtGui.QPushButton(u'Переименовать', self)
        self.btnDelete = QtGui.QPushButton(u'Удалить', self)
        self.btnBox = QtGui.QDialogButtonBox(self)
        self.btnBox.setEnabled(False)
        self.btnBox.setOrientation(QtCore.Qt.Horizontal)
        self.btnBox.addButton(self.btnSelect, QtGui.QDialogButtonBox.ActionRole)
        self.btnBox.addButton(self.btnRename, QtGui.QDialogButtonBox.ActionRole)
        self.btnBox.addButton(self.btnDelete, QtGui.QDialogButtonBox.ActionRole)
        self.widgetLayout.addWidget(self.btnBox)

        self.connect(self.treeView, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.on_doubleClicked)
        self.connect(self.treeView, QtCore.SIGNAL('selectionChanged(QItemSelection, QItemSelection)'), self.on_currentChanged)
        self.connect(self.treeView, QtCore.SIGNAL('deleteItem()'), self.on_clickedDelete)
        self.connect(self.treeView, QtCore.SIGNAL('renameItem()'), self.on_clickedRename)
        self.connect(self.treeView, QtCore.SIGNAL('updateTreeView(QModelIndex)'), self.updateTreeView)
        self.connect(self.btnSelect, QtCore.SIGNAL('clicked()'), self.on_clickedSelect)
        self.connect(self.btnRename, QtCore.SIGNAL('clicked()'), self.on_clickedRename)
        self.connect(self.btnDelete, QtCore.SIGNAL('clicked()'), self.on_clickedDelete)
        self.setLayout(self.widgetLayout)
        self.treeView.setFocus()

    def btnsSetEnabeled(self, enable):
        self.btnBox.setEnabled(enable)
        self.treeView.keyEnabled = enable

    def on_doubleClicked(self, index):
        item = index.internalPointer()
        self.emit(QtCore.SIGNAL('templateSelected(int)'), item.id())
        self.close()

    def on_currentChanged(self, newIndexes, oldIndexes):
        enable = bool(len(newIndexes.indexes()) == 1)
        self.btnsSetEnabeled(enable)

    def on_clickedSelect(self):
        item = self.treeView.currentIndex().internalPointer()
        self.emit(QtCore.SIGNAL('templateSelected(int)'), item.id())
        self.close()

    def on_clickedRename(self):
        index = self.treeView.currentIndex()
        if index.internalPointer():
            self.treeView.edit(index)

    def on_clickedDelete(self):
        self.btnsSetEnabeled(False)
        def deleteCurrentInternal():
            index = self.treeView.currentIndex()
            model = self.treeView.model()
            item = model.itemId(index)
            if item:
                db = QtGui.qApp.db
                table = db.table('ActionTemplate')
                db.markRecordsDeleted(table, table['id'].eq(item))
                self.updateTreeView(index)
        QtGui.qApp.call(self, deleteCurrentInternal)

    def updateTreeView(self, index):
        model = self.treeView.model()
        id = index.internalPointer().id()
        if model.parent(index):
            model.updateItem(model.parent(index))
        else:
            model.update()
        self.treeView.setModel(model)
        newIndex = model.findItemId(id)
        if (newIndex):
            self.treeView.setCurrentIndex(newIndex)
            self.treeView.scrollTo(newIndex)
        if model.isEmpty():
            self.emit(QtCore.SIGNAL('closePopup()'))
            self.emit(QtCore.SIGNAL('disable()'))
        self.treeView.repaint()


    def mousePressEvent(self, event):
        p = self.parentWidget()
        if p!=None:
            rect = p.rect()
            rect.moveTo(p.mapToGlobal(rect.topLeft()))
            if (rect.contains(event.globalPos()) or self.rect().contains(event.pos())):
                self.setAttribute(QtCore.Qt.WA_NoMouseReplay)
        QtGui.QFrame.mousePressEvent(self, event)


    def mouseReleaseEvent(self, event):
#        self.emit(QtCore.SIGNAL('resetButton()'))
        self.parent().mouseReleaseEvent(event)
        pass


#    def event(self, event):
#        if event.type()==QEvent.KeyPress:
#            if event.key()==Qt.Key_Escape:
#                self.dateChanged = False
#        return QFrame.event(self, event)

    def hideEvent(self, event):
        self.emit(QtCore.SIGNAL('closePopup()'))

class CActionTemplateChooseButton(QtGui.QPushButton):
    __pyqtSignals__ = ('templateSelected(int)',
                      )

    def __init__(self,  parent = None):
        QtGui.QPushButton.__init__(self, parent)
        self.popup = None
        self._modelCallback = None
#        self.setMenu(QtGui.QMenu(self))
#        self.setMenu(CActionTemplateChooseMenu(self))
        self.connect(self, QtCore.SIGNAL('pressed()'), self._popupPressed)
        self._model = None


    def setModel(self, model):
        self._model = model
        self.setEnabled( not self._model.isEmpty() )


    def initStyleOption(self, option):
        QtGui.QPushButton.initStyleOption(self, option)
        option.features |= QtGui.QStyleOptionButton.HasMenu

    def sizeHint(self):
        self.ensurePolished()
        w = 0
        h = 0
        opt = QtGui.QStyleOptionButton()
        self.initStyleOption(opt)

        if not opt.icon.isNull():
            ih = opt.iconSize.height()
            iw = opt.iconSize.width() + 4
            w += iw
            h = max(h, ih)

        if opt.features & QtGui.QStyleOptionButton.HasMenu:
            w += self.style().pixelMetric(QtGui.QStyle.PM_MenuButtonIndicator, opt, self)

        empty = opt.text.isEmpty()
        fm = self.fontMetrics()
        sz = fm.size(QtCore.Qt.TextShowMnemonic, "XXXX" if empty else opt.text)
        if not empty or not w:
            w += sz.width()
        if not empty or not h:
            h = max(h, sz.height())
        result = self.style().sizeFromContents(QtGui.QStyle.CT_PushButton, opt, QtCore.QSize(w, h), self).expandedTo(QtGui.qApp.globalStrut())
        return result


    def paintEvent(self, paintEvent):
        p = QtGui.QStylePainter(self)
        option = QtGui.QStyleOptionButton()
        self.initStyleOption(option)
        p.drawControl(QtGui.QStyle.CE_PushButton, option)

    def setModelCallback(self, func):
        self._modelCallback = func

    def _popupPressed(self):
        self.setDown(True)
        if not self.popup:
            self.popup = CActionTemplatePopup(self)
#            m = CActionTemplateModel(self, None, None, None, 0, None, False)
        if self._modelCallback:
            self._model = self._modelCallback()
        self.popup.treeView.setModel(self._model)
        pos = self.rect().bottomLeft()
        pos = self.mapToGlobal(pos)
        size = self.popup.sizeHint()
        screen = QtGui.qApp.desktop().availableGeometry(pos)
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )
        self.popup.move(pos)
        self.connect(self.popup, QtCore.SIGNAL('templateSelected(int)'), self.on_templateSelected)
        self.connect(self.popup, QtCore.SIGNAL('closePopup()'), self.on_closePopup)
        self.connect(self.popup, QtCore.SIGNAL('disable(bool)'), self.on_disable)
        self.popup.show()

    def on_templateSelected(self, templateId):
        self.emit(QtCore.SIGNAL('templateSelected(int)'), templateId)

    def on_closePopup(self):
        self.setDown(False)

    def on_disable(self, enabled):
        self.setEnabled(False)


# ===================================================================================

class CActionTemplateComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(0)
        self._model = CActionTemplateModel(self, None, None, None, 0, None, False)
        self.setModel(self._model)
        self._popupView = CActionTemplateTreeView(self)
        self._popupView.setObjectName('popupView')
        self._popupView.setModel(self._model)
        self.setView(self._popupView)
        self._popupView.installEventFilter(self)
        self._popupView.viewport().installEventFilter(self)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentIndex)
        self.prefferedWidth = 0

    def setPrefferedWidth(self, prefferedWidth):
        self.prefferedWidth = prefferedWidth


    def setFilter(self, actionTypeId, personId, specialityId, clientSex, clientAge, removeEmptyNodes=True):
        self._model.setFilter(actionTypeId, personId, specialityId, clientSex, clientAge, removeEmptyNodes)


    def update(self):
        self._model.update()


    def setValue(self, id):
        index = self._model.findItemId(id)
        self.setCurrentIndex(index)


    def value(self):
        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())
        if modelIndex.isValid():
            return self._model.itemId(modelIndex)
        return None


    def on_ItemActivated(self, index):
        if index.isValid():
            if (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0 :
                self.hidePopup()
                self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
            else:
                self._popupView.setExpanded(index, not self._popupView.isExpanded(index))


    def showPopup(self):
#        self.__searchString = ''
        modelIndex = self._model.index(self.currentIndex(), 0, self.rootModelIndex())

        self._popupView.setRealRootIndex(QtCore.QModelIndex())
        self._popupView.expandAll()
        prefferedWidth = self._popupView.sizeHint().width()
        prefferedWidth = max(self.prefferedWidth if self.prefferedWidth else 0, self._popupView.sizeHint().width())
        if prefferedWidth:
            if self.width() < prefferedWidth:
                self._popupView.setFixedWidth(prefferedWidth)
        QtGui.QComboBox.showPopup(self)
        scrollBar = self._popupView.horizontalScrollBar()
        scrollBar.setValue(0)


    def setCurrentIndex(self, index):
        if not index:
            index = QtCore.QModelIndex()
        if index:
            self.setRootModelIndex(index.parent())
            QtGui.QComboBox.setCurrentIndex(self, index.row())

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress: # and obj == self.__popupView :
            if event.key() in [ QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Select ] :
                index = self._popupView.currentIndex()
                if index.isValid() and (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0 :
                    self.hidePopup()
                    self.setCurrentIndex(index)
                    self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
                return True
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and obj == self._popupView.viewport():
            self._popupView.mouseReleaseEvent(event)  # i1883.c12401 - нужна реакция на mouseRelease от QTreeView
            return True
        return False
