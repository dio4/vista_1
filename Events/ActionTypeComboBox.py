# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFont

from Accounting.Utils import CTariff
from Events.Action import ActionClass
from Events.Utils import recordAcceptable
from library.InDocTable import CInDocTableCol
from library.PreferencesMixin import CPreferencesMixin
from library.TreeModel import CTreeItemWithId, CTreeModel
from library.Utils import forceBool, forceInt, forceRef, forceString, forceStringEx, getPref, setPref, toVariant, \
    forceDate
from library.crbcombobox import CRBComboBox, CRBModelDataCache


class CActionTypeTreeItem(CTreeItemWithId):
    def __init__(self, parent, id, code, name, model, class_):
        CTreeItemWithId.__init__(self, parent, name, id)
        self._model = model
        self._code = code
        self._class = class_

    def class_(self):
        return self._class

    def code(self):
        return self._code

    def loadChildren(self):
        return self._model.loadChildrenItems(self)

    def flags(self):
        if self.childCount() > 0 and not self._model._allSelectable:
            return QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, column):
        if column == 0:
            return toVariant(self._code)
        elif column == 1:
            return toVariant(self._name)
        return QtCore.QVariant(self._name)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 2


class CActionTypeClassTreeItem(CActionTypeTreeItem):
    def __init__(self, parent, class_, model):
        CActionTypeTreeItem.__init__(self, parent, None, '', ActionClass.nameList[class_], model, class_)

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


class CActionTypeRootTreeItem(CActionTypeTreeItem):
    def __init__(self, model):
        CActionTypeTreeItem.__init__(self, None, None, '', u'-', model, None)

    def loadChildren(self):
        if self._model._classesVisible:
            result = []
            for class_ in self._model._classes:
                result.append(CActionTypeClassTreeItem(self, class_, self._model))
            return result
        else:
            return self._model.loadChildrenItems(self)

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def reset(self):
        if self._items is None:
            return False
        else:
            self._items = None
            return True

    def data(self, col, variant=None):
        return QtCore.QVariant('-')


class CActionTypeModel(CTreeModel):
    def __init__(self, parent=None, enabledActionTypeIdList=None):
        CTreeModel.__init__(self, parent, CActionTypeRootTreeItem(self))
        self._enabledActionTypeIdList = enabledActionTypeIdList
        self._classes = ActionClass.All
        self._classesVisible = False
        self._allSelectable = False
        self._leavesVisible = True
        self._disabledActionTypeIdList = self.getDisabledForProfileActionTypeIdList()
        self._clientSex = 0
        self._clientAge = None

    def match(self, start, role, value, hits=1, flags=None, *args, **kwargs):
        start = self.index(start.row(), 1, start.parent())
        return CTreeModel.match(self, start, role, value, hits, flags, *args, **kwargs)

    def setClasses(self, classes):
        if self._classes != classes:
            self._classes = classes
            if self.getRootItem().reset():
                self.reset()

    def setClassesVisible(self, value):
        if self._classesVisible != value:
            self._classesVisible = value
            if self.getRootItem().reset():
                self.reset()

    def data(self, index, role):
        if index.isValid() and (role == QtCore.Qt.DisplayRole or role == QtCore.Qt.ToolTipRole):
            item = index.internalPointer()
            if item:
                return item.data(index.column())

        if index.isValid() and role == Qt.FontRole and index.column() == 1 and not index.parent().parent().isValid():
            boldFont = QFont()
            boldFont.setBold(True)
            return boldFont

        return QtCore.QVariant()

    def setAllSelectable(self, value):
        if self._allSelectable != value:
            self._allSelectable = value

    def getDisabledForProfileActionTypeIdList(self):
        return list(QtGui.qApp.db.getIdList(
            '',
            stmt=u'SELECT id '
                 u'FROM ActionType at '
                 u'WHERE '
                 u'  (at.filterSpecialities = 1 AND '
                 u'    NOT EXISTS(SELECT * '
                 u'               FROM ActionType_PersonSpeciality atps '
                 u'               WHERE atps.actionType_id = at.id AND '
                 u'                     atps.speciality_id = %(sid)s)) OR '
                 u'  (at.filterPosts = 1 AND '
                 u'    NOT EXISTS(SELECT * '
                 u'               FROM ActionType_PersonPost atpp '
                 u'               WHERE atpp.actionType_id = at.id AND '
                 u'                     atpp.post_id = %(pid)s))' %
                 {
                     'sid': QtGui.qApp.userSpecialityId or 'NULL',
                     'pid': QtGui.qApp.userPostId or 'NULL'
                 }
        ))

    def setDisabledActionTypeIdList(self, disabledActionTypeIdList):
        if self._disabledActionTypeIdList != disabledActionTypeIdList:
            self._disabledActionTypeIdList = (disabledActionTypeIdList or []) + \
                                             self.getDisabledForProfileActionTypeIdList()
            if self.getRootItem().reset():
                self.reset()

    def setEnabledActionTypeIdList(self, enabledActionTypeIdList):
        if self._enabledActionTypeIdList != enabledActionTypeIdList:
            self._enabledActionTypeIdList = enabledActionTypeIdList
            if self.getRootItem().reset():
                self.reset()

    def setFilter(self, clientSex, clientAge):
        if self._clientSex != clientSex or self._clientAge != clientAge:
            self._clientSex = clientSex
            self._clientAge = clientAge
            if self.getRootItem().reset():
                self.reset()

    def setLeavesVisible(self, leavesVisible):
        if self._leavesVisible != leavesVisible:
            self._leavesVisible = leavesVisible
            if self.getRootItem().reset():
                self.reset()

    def flags(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item.flags()
            return QtCore.Qt.NoItemFlags

    def loadChildrenItems(self, group):
        db = QtGui.qApp.db

        tableActionType = db.table('ActionType')
        cond = [
            tableActionType['showInForm'].eq(1),
            tableActionType['deleted'].eq(0)
        ]
        if isinstance(group, CActionTypeClassTreeItem):
            cond.append(tableActionType['class'].eq(group._class))
        elif group.id() is None:
            cond.append(tableActionType['class'].inlist(self._classes))
        if self._enabledActionTypeIdList is not None:
            cond.append(tableActionType['id'].inlist(set(self._enabledActionTypeIdList)))
        if self._disabledActionTypeIdList:
            cond.append(tableActionType['id'].notInlist(self._disabledActionTypeIdList))

        mapGroupIdToItems = {}
        mapIdToItems = {}

        cols = ['id', 'class', 'group_id', 'code', 'name', 'sex', 'age']
        for record in db.iterRecordList(tableActionType, cols, cond, order='code'):
            if recordAcceptable(self._clientSex, self._clientAge, record):
                id = forceInt(record.value('id'))
                code = forceStringEx(record.value('code'))
                name = forceStringEx(record.value('name'))
                groupId = forceRef(record.value('group_id'))
                class_ = forceInt(record.value('class'))
                item = CActionTypeTreeItem(group, id, code, name, self, class_)
                item._items = []
                items = mapGroupIdToItems.setdefault(groupId, [])
                items.append(item)
                mapIdToItems[id] = item

        if not self._leavesVisible:
            leavesIdSet = set(mapIdToItems.keys()) - set(mapGroupIdToItems.keys())
            filterFunc = lambda item: item._id not in leavesIdSet
        else:
            filterFunc = None
        for groupId, items in mapGroupIdToItems.iteritems():
            groupItem = mapIdToItems.get(groupId, None)
            if groupItem:
                if filterFunc:
                    items = filter(filterFunc, items)
                for item in items:
                    item._parent = groupItem
                groupItem._items = items
        return mapGroupIdToItems.get(group.id(), [])

    def headerData(self, section, orientation, role=None):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            if section == 0:
                return QtCore.QVariant(u'Код')
            return QtCore.QVariant(u'Наименование')
        return QtCore.QVariant()

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 2


class CActionTypePopupView(QtGui.QTreeView):
    def __init__(self, parent):
        QtGui.QTreeView.__init__(self, parent)
        self.header().hide()
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setMinimumHeight(150)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
        self.connect(self, QtCore.SIGNAL('expanded(QModelIndex)'), self.onExpanded)
        #        self.connect(self, QtCore.SIGNAL('collapsed(QModelIndex)'), self.onCollapsed)
        self.searchString = ''
        self.searchParent = None
        self.listKeyNavigation = [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down, QtCore.Qt.Key_Right, QtCore.Qt.Key_Left,
                                  QtCore.Qt.Key_Home, QtCore.Qt.Key_End, QtCore.Qt.Key_PageUp, QtCore.Qt.Key_PageDown,
                                  QtCore.Qt.Key_Tab, QtCore.Qt.Key_Backtab]
        self.setAllColumnsShowFocus(True)
        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setHeaderHidden(False)

    def setRootIndex(self, index):
        pass

    def setRealRootIndex(self, index):
        QtGui.QTreeView.setRootIndex(self, index)
        self.expandAll()

    def onExpanded(self, index):
        self.scrollTo(index, QtGui.QAbstractItemView.PositionAtTop)
        self.searchString = ''

    def onCollapsed(self, index):
        self.collapseAll()
        QtGui.QTreeView.collapseAll(self)

    #        self.searchString = ''


    # def resizeEvent(self, event):
    #     QtGui.QTreeView.resizeEvent(self, event)
    #        self.resizeColumnToContents(0)

    #    def keyPressEvent(self, event):
    #        if event.key() == Qt.Key_Left or event.key() == Qt.Key_Minus:
    #            current = self.currentIndex()
    #            if self.isExpanded(current) and self.model().rowCount(current):
    #                self.collapse(current)
    #            else:
    #                self.setCurrentIndex(current.parent())
    #                current = self.currentIndex()
    #                self.collapse(current)
    #                self.scrollTo(current, QtGui.QAbstractItemView.PositionAtTop)
    #            event.accept()
    #            return
    #        if event.key() == Qt.Key_Back:
    #            self.searchString = self.searchString[:-1]
    #            event.accept()
    #            return
    #        return QtGui.QTreeView.keyPressEvent(self, event)
    #
    #
    #    def keyboardSearch(self, search):
    #        current = self.currentIndex()
    #        if current.parent() != self.searchParent:
    #            self.searchString = u''
    #        searchString = self.searchString + unicode(search)
    #        QtGui.QTreeView.keyboardSearch(self, searchString)
    #        if current != self.currentIndex():
    #            self.searchString = searchString
    #        self.searchParent = self.currentIndex().parent()
    #        rowIndex = self.model().searchCode(search)
    #        if rowIndex>=0 :
    #            index = self.model().index(rowIndex, 1)
    #            self.setCurrentIndex(index);

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self.searchString = ''
            event.ignore()
        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            self.searchString = ''
            event.ignore()
        if key == QtCore.Qt.Key_Delete:
            self.searchString = ''
            self.searchStringEx('-')
            event.accept()
            return
        elif key in self.listKeyNavigation:
            self.searchString = ''
            QtGui.QTreeView.keyPressEvent(self, event)
            return
        elif key == QtCore.Qt.Key_Backspace:  # BS
            self.searchString = self.searchString[:-1]
            self.searchStringEx(self.searchString)
            event.accept()
            return
        elif key == QtCore.Qt.Key_Space:
            self.emit(QtCore.SIGNAL('hide()'))
            event.accept()
            return
        elif not event.text().isEmpty():
            char = event.text().at(0)
            if char.isPrint():
                self.searchString = self.searchString + unicode(QtCore.QString(char)).upper()
                self.searchStringEx(self.searchString)
                event.accept()
                return
            else:
                QtGui.QTreeView.keyPressEvent(self, event)
        else:
            QtGui.QTreeView.keyPressEvent(self, event)

    def searchStringEx(self, search):
        if not search:
            return
        self.keyboardSearch(search)

        if search == '-':
            self.searchString = ''
        else:
            self.searchString = search

    def selectionChanged(self, selected, deselected):
        self.searchString = ''


class CActionTypeComboBox(QtGui.QComboBox):
    def __init__(self, parent, enabledActionTypeIdList=None):
        QtGui.QComboBox.__init__(self, parent)
        self.SizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.setModelColumn(1)

        self._model = CActionTypeModel(self, enabledActionTypeIdList)
        self.setModel(self._model)

        self._popupView = CActionTypePopupView(self)
        self.connect(self._popupView, QtCore.SIGNAL('hide()'), self.hidePopup)
        self._popupView.setObjectName('popupView')
        self._popupView.setModel(self._model)

        self.setView(self._popupView)
        self._popupView.installEventFilter(self)
        self._popupView.viewport().installEventFilter(self)
        QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('activated(QModelIndex)'), self.on_ItemActivated)
        # QtCore.QObject.connect(self._popupView, QtCore.SIGNAL('entered(QModelIndex)'), self.setCurrentIndex)

        if QtGui.qApp.preferences.decorStyle not in ('Cleanlooks', 'GTK+'):
            self._popupView.expanded.connect(self.update_height)
            self._popupView.collapsed.connect(self.update_height)

        self.row_height = 0
        self._root_index = None

    def setPrefferedWidth(self, prefferedWidth):
        self.prefferedWidth = prefferedWidth

    def setClass(self, class_):
        if class_ is not None:
            self.setClasses(class_ if isinstance(class_, list) else [class_])
        else:
            self.setClasses(ActionClass.All)

    def setClasses(self, classes):
        self._model.setClasses(classes)

    def setClassesVisible(self, value):
        self._model.setClassesVisible(value)

    def setAllSelectable(self, value):
        self._model.setAllSelectable(value)

    def setDisabledActionTypeIdList(self, disabledActionTypeIdList):
        self._model.setDisabledActionTypeIdList(disabledActionTypeIdList)

    def setEnabledActionTypeIdList(self, enabledActionTypeIdList):
        self._model.setEnabledActionTypeIdList(enabledActionTypeIdList)

    def setFilter(self, sex, age):
        self._model.setFilter(sex, age)

    def setValue(self, id):
        index = self._model.findItemId(id)
        self.setCurrentIndex(index)

    def value(self):
        idx = self.model().index(self.currentIndex(), 0, self.rootModelIndex())
        if idx.isValid():
            return idx.internalPointer().id()
        return None

    def descendantValues(self):
        result = []

        def get_children(group_id):
            children = QtGui.qApp.db.getRecordList(
                stmt='SELECT at.id, not exists(select id from ActionType WHERE group_id = at.id) as isLeaf '
                     'FROM ActionType at '
                     'WHERE at.deleted = 0 AND at.group_id = %d' % group_id
            )
            if not children:
                result.append(group_id)
            for child in children:
                child_id, is_leaf = forceRef(child.value('id')), forceBool(child.value('isLeaf'))
                if is_leaf:
                    result.append(child_id)
                else:
                    get_children(child_id)

        idx = self.model().index(self.currentIndex(), 0, self.rootModelIndex())
        if idx.isValid() and idx.internalPointer().id():
            get_children(idx.internalPointer().id())
        return result

    def on_ItemActivated(self, index):
        if index.isValid():
            if (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0:
                self.hidePopup()
                self.setCurrentIndex(index)
                self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
            else:
                self._popupView.setExpanded(index, not self._popupView.isExpanded(index))

    def showPopup(self):
        self._root_index = QtCore.QModelIndex()
        self.view().setRealRootIndex(self._root_index)
        # i2889: pirozhok: СПб ПНД6 не умеет F9, поэтому сворачиваем все списки
        # self._popupView.expandAll()
        self._popupView.collapseAll()
        root = self._popupView.model().index(0, 0, QtCore.QModelIndex())
        self._popupView.expand(root)
        self._popupView.setCurrentIndex(root)

        below = self.mapToGlobal(self.rect().bottomLeft())
        screen = QtGui.qApp.desktop().availableGeometry(below)
        if QtGui.qApp.preferences.decor_crb_width_unlimited:
            prefferedWidth = screen.width()
        else:
            prefferedWidth = 300

        if prefferedWidth:
            if self.width() < prefferedWidth:
                self._popupView.setFixedWidth(prefferedWidth)

        QtGui.QComboBox.showPopup(self)
        scrollBar = self._popupView.horizontalScrollBar()
        scrollBar.setValue(0)
        self._popupView.setTabKeyNavigation(True)
        self.update_height()

    def visible_items_count(self, parent=None):
        count = 0
        for i in range(0, self.model().rowCount(parent or self._root_index)):
            count += 1
            idx = self.model().index(i, 0, parent or self._root_index)
            if self.view().isExpanded(idx) or not parent:
                count += self.visible_items_count(idx)
        return count

    def screen_size(self):
        desktop = QtGui.qApp.desktop()  # type: QtGui.QDesktopWidget
        return desktop.availableGeometry(self._popupView)

    def max_popup_height(self):
        return self.screen_size().height() / 2

    def min_popup_height(self):
        return self.screen_size().height() / 5

    def update_height(self):
        if QtGui.qApp.currentOrgInfis() in (u'ПНД3', u'ПНД6'): return

        min_height = self.min_popup_height()
        max_height = self.max_popup_height()
        row_height = self._popupView.rowHeight(self._popupView.model().index(0, 0))
        rows_height = row_height * self.visible_items_count() + self._popupView.header().height()

        if min_height <= rows_height <= max_height:
            result = rows_height
        elif rows_height < min_height:
            result = min_height
        else:
            result = max_height
        self._popupView.setFixedHeight(result)
        frame = self._popupView.parent()
        frame.setFixedHeight(result + 2 * frame.frameWidth())
        # if self.mapToGlobal(QtCore.QPoint(0, 0)).x() + frame.width() > self.screen_size().width():
        #     left = self.mapToGlobal(QtCore.QPoint(-self.mapToGlobal(QtCore.QPoint(0, 0)).x()))

        # if self.mapToGlobal(QtCore.QPoint(0, 0)).y() + frame.height() + self.height() > self.screen_size().height():
        #     frame.move(self.mapToGlobal(QtCore.QPoint(left, -frame.height())))
        # else:
        #     frame.move(self.mapToGlobal(QtCore.QPoint(left, self.height())))

    def setCurrentIndex(self, index):
        if not index:
            index = QtCore.QModelIndex()
        if index:
            self.setRootModelIndex(index.parent())
            QtGui.QComboBox.setCurrentIndex(self, index.row())

            # self.emit(QtCore.SIGNAL('codeSelected(QString)'), self._model.code(index))

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:  # and obj == self.__popupView :
            if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Select]:
                index = self._popupView.currentIndex()
                if index.isValid() and (int(index.flags()) & QtCore.Qt.ItemIsSelectable) != 0:
                    self.hidePopup()
                    self.setCurrentIndex(index)
                    self.emit(QtCore.SIGNAL('itemSelected(QModelIndex)'), index)
                return True
            return False
        if event.type() == QtCore.QEvent.MouseButtonRelease and obj == self._popupView.viewport():
            self._popupView.mouseReleaseEvent(event)  # i1883.c12401 - нужна реакция на mouseRelease от QTreeView
            return True
        return False


class CActionTypeTableCol(CInDocTableCol):
    tableName = 'ActionType'
    showFields = CRBComboBox.showCodeAndName

    def __init__(self, title, fieldName, width, actionTypeClass, descendants=False, model=None, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.actionTypeClass = actionTypeClass
        self.classesVisible = params.get('classesVisible', False)
        self.contractId = None
        self.enabledActionTypeIdList = None
        self.descendants = descendants
        self.model = model
        self.foregroundColorCache = {}

    def toString(self, val, record):
        cache = CRBModelDataCache.getData(self.tableName, True)
        text = cache.getStringById(forceRef(val), self.showFields)
        specifiedName = forceString(record.value('specifiedName'))
        if specifiedName:
            text = text + ' ' + specifiedName
        return toVariant(text)

    def toStatusTip(self, val, record):
        cache = CRBModelDataCache.getData(self.tableName, True)
        text = cache.getStringById(forceRef(val), CRBComboBox.showName)
        specifiedName = forceString(record.value('specifiedName'))
        if specifiedName:
            text = text + ' ' + specifiedName
        return toVariant(text)

    def setContractId(self, newValue):
        if self.contractId != newValue:
            self.contractId = newValue
            self.enabledActionTypeIdList = None

    def createEditor(self, parent):
        enabledActionTypeIdList = None
        keyboardModifiers = QtGui.qApp.keyboardModifiers()
        if keyboardModifiers & QtCore.Qt.ControlModifier == QtCore.Qt.ControlModifier:
            if self.contractId:
                if self.enabledActionTypeIdList is None:
                    idList = getActionTypeIdListByContract(self.contractId)
                    idList = QtGui.qApp.db.getTheseAndParents(self.tableName, 'group_id', idList)
                    self.enabledActionTypeIdList = idList
                enabledActionTypeIdList = self.enabledActionTypeIdList
        editor = CActionTypeComboBox(parent, enabledActionTypeIdList)
        editor.setClass(self.actionTypeClass)
        editor.setClassesVisible(self.classesVisible)
        if self.descendants:
            editor.setAllSelectable(True)
        if parent.parent().currentIndex().row() == len(parent.parent().model().items()):  # CInDocTableView
            editor.isNewItem = True
        return editor

    def setEditorData(self, editor, value, record):
        editor.setValue(forceRef(value))

    def getEditorData(self, editor):
        if self.descendants:
            values = editor.descendantValues()
            if values:
                if hasattr(editor, 'isNewItem') and editor.isNewItem:
                    self.model.addRecord(self.model.getEmptyRecord())
                for item in values[1:]:
                    rec = self.model.getEmptyRecord()
                    rec.setValue('actionType_id', toVariant(item))
                    self.model.addRecord(rec)
                return toVariant(values[0])
            return toVariant(None)
        return toVariant(editor.value())

    def getForegroundColor(self, val, record):
        val = forceRef(val)
        if not val:
            return QtCore.QVariant()
        if val and val not in self.foregroundColorCache:
            statusRec = QtGui.qApp.db.getRecordEx(stmt='''
            SELECT s.begDate, s.endDate
            FROM ActionType at
              LEFT JOIN rbService s ON at.nomenclativeService_id = s.id
            WHERE at.id = %d
            ''' % val)
            begDate, endDate = forceDate(statusRec.value('begDate')), forceDate(statusRec.value('endDate'))
            if begDate and not endDate:
                status = begDate <= QtCore.QDate().currentDate()
            elif not begDate and endDate:
                status = QtCore.QDate().currentDate() <= endDate
            elif begDate and endDate:
                status = begDate <= QtCore.QDate().currentDate() <= endDate
            else:
                status = True
            self.foregroundColorCache[val] = status
        if self.foregroundColorCache[val]:
            return QtCore.QVariant()
        else:
            return QtCore.QVariant(QtGui.QColor(QtCore.Qt.darkRed))


def getActionTypeIdListByContract(contractId):
    idList = None
    if contractId:
        db = QtGui.qApp.db
        tableContract = db.table('Contract')
        tableContractTariff = db.table('Contract_Tariff')
        tableActionTypeService = db.table('ActionType_Service')
        tableActionType = db.table('ActionType')
        table = tableContract.leftJoin(
            tableContractTariff,
            [
                tableContractTariff['master_id'].eq(tableContract['id']),
                tableContractTariff['deleted'].eq(0),
                tableContractTariff['tariffType'].inlist([
                    CTariff.ttActionAmount,
                    CTariff.ttActionUET,
                    CTariff.ttHospitalBedService
                ])
            ]
        )
        table = table.leftJoin(
            tableActionTypeService, tableActionTypeService['service_id'].eq(tableContractTariff['service_id']))
        table = table.leftJoin(tableActionType, tableActionType['id'].eq(tableActionTypeService['master_id']))
        cond = [
            tableContract['id'].eq(contractId),
            tableActionType['deleted'].eq(0),
            '''
            IF(EXISTS(
                SELECT id FROM ActionType_Service AS ATS 
                WHERE ActionType.id = ATS.master_id AND Contract.finance_id = ATS.finance_id),
                ActionType_Service.finance_id = Contract.finance_id,
                ActionType_Service.finance_id IS NULL
            )
            '''
        ]
        idList = db.getDistinctIdList(table, tableActionType['id'], cond)
    return idList


class CActionTypeTreeView(QtGui.QTreeView, CPreferencesMixin):
    def __init__(self, parent=None):
        QtGui.QTreeView.__init__(self, parent)
        self._preferences = {}

    def updateExpandState(self):
        self.processPrefs(True)

    def processPrefs(self, load, parent=QtCore.QModelIndex(), prefix=''):
        model = self.model()
        for j in xrange(model.rowCount(parent)):
            index = model.index(j, 0, parent)
            if index.isValid():
                item = index.internalPointer()
                saveName = ''
                if isinstance(item, CActionTypeRootTreeItem):
                    saveName = 'rootitem'
                elif isinstance(item, CActionTypeClassTreeItem):
                    saveName = 'class%d' % item.class_()
                elif isinstance(item, CActionTypeTreeItem):
                    saveName = unicode(item.id())
                if saveName:
                    if load:
                        self.setExpanded(index, forceBool(getPref(self._preferences, saveName, True)))
                    else:
                        setPref(self._preferences, saveName, QtCore.QVariant(self.isExpanded(index)))
            if index.isValid():
                self.processPrefs(load, index, prefix)

    def loadPreferences(self, preferences):
        self._preferences = preferences
        if self.model() and isinstance(self.model(), CActionTypeModel):
            self.updateExpandState()

    def savePreferences(self):
        if self.model() and isinstance(self.model(), CActionTypeModel):
            self.processPrefs(False)
        return self._preferences


class CActionTypeAnalysesTreeView(CActionTypeTreeView):
    def __init__(self, parent=None):
        CActionTypeTreeView.__init__(self, parent)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            index = self.selectionModel().currentIndex()
            if key == QtCore.Qt.Key_Space:
                selectionDialog = self.parentWidget().parentWidget().parentWidget().parentWidget()
                selectionDialog.on_treeActionTypeGroups_doubleClicked(index)
                return True
        return CActionTypeTreeView.eventFilter(self, obj, event)
