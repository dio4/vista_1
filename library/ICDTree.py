# -*- coding: utf-8 -*-
from PyQt4.QtGui import *

from Ui_ICDTree import Ui_ICDTreePopup
from library.InDocTable import CRecordListModel, CInDocTableCol
from library.TableModel import *

u"""Выпадающая таблица с деревом для выбора кода МКБ"""


class CICDSheartResultTableModel(CRecordListModel):
    def __init__(self, parent=None):
        CRecordListModel.__init__(self, parent)
        self.addExtCol(CInDocTableCol(u'Код', 'DiagID', 40).setReadOnly(), QtCore.QVariant.String)
        self.addExtCol(CInDocTableCol(u'Наименование', 'DiagName', 40).setReadOnly(), QtCore.QVariant.String)
        self.table = QtGui.qApp.db.table('MKB_Tree')


class CICDTreePopup(QtGui.QFrame, Ui_ICDTreePopup):
    __pyqtSignals__ = ('diagSelected(QString)',
                       )

    def __init__(self, parent = None):
        QFrame.__init__(self, parent, Qt.Popup)
        self.setFrameShape(QFrame.StyledPanel)
        self.setAttribute(Qt.WA_WindowPropagation)
        self.treeModel = CICDTreeModel(self)
        self.tableModel = CICDSheartResultTableModel(self)
        self.tableSelectionModel = QtGui.QItemSelectionModel(self.tableModel,  self)
        self.tableSelectionModel.setObjectName('tableSelectionModel')
        self.setupUi(self)
        self.treeView.setModel(self.treeModel)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setAllColumnsShowFocus(True)
        self.connect(self.treeView, SIGNAL('hide()'), self.close)
        textWidth = self.treeView.fontMetrics().width('W00.000')
        self.treeView.setColumnWidth(0, self.treeView.indentation()*5+textWidth)
        self.tblSearchResult.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblSearchResult.setModel(self.tableModel)
        self.tblSearchResult.setSelectionModel(self.tableSelectionModel)
        self.connect(self.tblSearchResult, SIGNAL('hide()'), self.close)
        self.treeView.setFocus()
        self.diag = None
        self.filter = None
        
        self._applyFilterTimer = QtCore.QTimer(self)
        self._applyFilterTimer.setSingleShot(True)
        self.connect(self._applyFilterTimer, SIGNAL('timeout()'), self.on_btnSearch_clicked)
        
    def hideEvent(self, event):
        QtGui.qApp.preferences.appPrefs['CICDTreePopup_currentTab'] = self.tabWidget.currentIndex()
        super(CICDTreePopup, self).hideEvent(event)
    
    def showEvent(self, event):
        self.tabWidget.setCurrentIndex(forceInt(QtGui.qApp.preferences.appPrefs.get('CICDTreePopup_currentTab', 0)))
        self.on_btnSearch_clicked()
        super(CICDTreePopup, self).showEvent(event)
        
    def mousePressEvent(self, event):
        parent = self.parentWidget()
        if parent!=None:
            opt=QStyleOptionComboBox()
            opt.init(parent)
            arrowRect = parent.style().subControlRect(
                QStyle.CC_ComboBox, opt, QStyle.SC_ComboBoxArrow, parent)
            arrowRect.moveTo(parent.mapToGlobal(arrowRect.topLeft()))
            if (arrowRect.contains(event.globalPos()) or self.rect().contains(event.pos())):
                self.setAttribute(Qt.WA_NoMouseReplay)
        QFrame.mousePressEvent(self, event)

    def setCurrentDiag(self, diag):
        self.treeView.collapseAll()
        self.diag = forceString(diag)
        if self.diag:
            index = self.treeModel.findDiag(self.diag)
            self.treeView.scrollTo(index)
            self.treeView.setCurrentIndex(index)
            self.treeView.setExpanded(index, True)

    def setMKBFilter(self, filter):
        if filter:
            table = self.tableModel.table
            filterCond = []
            if filter['clientId'] and filter['begDate']:
                recordRegional = QtGui.qApp.db.getRecordEx('ClientPolicy INNER JOIN Organisation policyOKATO ON ClientPolicy.insurer_id = policyOKATO.id  JOIN Organisation ON Organisation.id = %s' % QtGui.qApp.currentOrgId(),
                                                    'if(Organisation.OKATO = policyOKATO.OKATO, 1, if(ClientPolicy.insuranceArea = policyOKATO.OKATO, 1, 0)) AS isClientRegional',
                                                    u'''(SELECT MAX(tmpCP.id)
                                                         FROM ClientPolicy tmpCP
                                                            LEFT JOIN rbPolicyType tmpPT ON tmpPT.id = tmpCP.policyType_id
                                                         WHERE tmpPT.name LIKE 'ОМС%%'
                                                            AND tmpCP.client_id = %(clientId)s
                                                            AND tmpCP.deleted = 0
                                                            AND tmpCP.begDate <= DATE('%(date)s')
                                                            AND (tmpCP.endDate IS NULL OR DATE('%(date)s') <= tmpCP.endDate)) AND (policyOKATO.OKATO OR ClientPolicy.insuranceArea)''' % {'clientId': filter['clientId'], 'date': filter['begDate'].toString(QtCore.Qt.ISODate)})
                if recordRegional:
                    isClientRegional = forceBool(recordRegional.value('isClientRegional'))
                    filterCond.append(table['OMS'].eq(1) if isClientRegional else table['MTR'].eq(1))
            if filter['begDate']:
                filterCond.extend([table['begDate'].dateLe(filter['begDate']), table['endDate'].dateGe(filter['begDate'])])
            self.treeModel.setFilter(filterCond)
            self.filter = filterCond

    def selectDiag(self, diag):
        self.diag = diag
        self.emit(QtCore.SIGNAL('diagSelected(QString)'), diag)
        self.close()

    def getCurrentDiag(self):
        try:
            item = self.tableModel.items()[self.tblSearchResult.currentIndex().row()]
            if item:
                diag = forceString(item.value('DiagID'))
                return diag
        except IndexError:
            pass
        return ''

    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self,  index):
        if index == 0:
            diag = self.getCurrentDiag()
            self.setCurrentDiag(diag)

    @QtCore.pyqtSlot(QModelIndex)
    def on_treeView_doubleClicked(self, index):
        flags = self.treeModel.flags(index)
        if flags & QtCore.Qt.ItemIsSelectable:
            diag = forceString(self.treeModel.diag(index))
            self.selectDiag(diag)

    @QtCore.pyqtSlot()
    def on_btnSearch_clicked(self):
        db = QtGui.qApp.db
        words = forceStringEx(self.edtWords.text()).split()
        table = self.tableModel.table
        cond  = [table['DiagName'].like('%%%s%%' % word) for word in words]
        if self.filter:
            cond.extend(self.filter)
        fromQuery = u'''MKB_Tree'''

        recordList = db.getRecordList(fromQuery,
                                    where=cond,
                                    order='DiagID')
        self.tableModel.setItems(recordList)

    @QtCore.pyqtSlot(QModelIndex)
    def on_tblSearchResult_doubleClicked(self, index):
        diag = self.getCurrentDiag()
        self.selectDiag(diag)
        
    @QtCore.pyqtSlot(QString)
    def on_edtWords_textChanged(self, text):
        minCharCount = forceInt(QtGui.qApp.preferences.appPrefs.get('completerReduceCharCount', 3))
        charCount = text.size()
        if charCount == 0:
            self._applyFilterTimer.start(0)
        elif charCount >= minCharCount:
            idleTimeout = forceInt(QtGui.qApp.preferences.appPrefs.get('completerReduceIdleTimeout', 3))
            self._applyFilterTimer.start(idleTimeout * 1000)


class CBaseTreeItem:
    subclasses = {}

    @staticmethod
    def loadSubclassItems(subclassId):
        if not hasattr(QtGui.qApp, 'MKBSubclass'):
            QtGui.qApp.MKBSubclass = {}
        if subclassId not in QtGui.qApp.MKBSubclass:
            result = []
            stmt   = 'SELECT code, name FROM rbMKBSubclass_Item WHERE master_id=%d ORDER BY code' % subclassId
            query = QtGui.qApp.db.query(stmt)

            while query.next():
                record = query.record()
                code   = forceString(record.value('code'))
                name   = forceString(record.value('name'))
                result.append( (code, name) )

            QtGui.qApp.MKBSubclass[subclassId] = result
            return result
        else:
            return QtGui.qApp.MKBSubclass[subclassId]

    @staticmethod
    def getSubclassItems(subclassId):
        result = CBaseTreeItem.subclasses.get(subclassId, None)
        if result is None:
            result = CBaseTreeItem.loadSubclassItems(subclassId)
            CBaseTreeItem.subclasses[subclassId] = result
        return result

    def __init__(self, code, name, index, subclassId, parent=None, filter=None):
        self.parent = parent
        self.code = code
        self.name = name
        self.index = index
        self.subclassId = subclassId
        self.items = None
        self.itemsCount = None
        self.filter = filter

    def setFilter(self, filter):
        if self.filter != filter:
            self.filter = filter
            self.updateItems()

    def updateItems(self):
        self.items = self.loadChilds()
        self.itemsCount = len(self.items)

    def child(self, row):
        if self.items is None:
            self.updateItems()
        if row < self.childCount():
            return self.items[row]
        else:
            return None

    def childCount(self):
        if self.itemsCount is None:
            self.itemsCount = self.countChilds()
        return self.itemsCount

    def columnCount(self):
        return 2

    def selectable(self):
        return True

    def data(self, column):
        if column == 0 :
            return self.code
        if column == 1 :
            return self.name
        return QtCore.QVariant()

    def parent(self):
        return self.parent

    def row(self):
        if self.parent:
            return self.parent.items.index(self)
        return 0

    def loadChilds(self):
        return []

    def findChildByCode(self, code):
        if self.items is None:
            self.items = self.loadChilds()
            self.itemsCount = len(self.items)
        for child in self.items:
            if child.code == code:
                return child
        return None

    def isDiagSelectable(self):
        return True


class CICDRootTreeItem(CBaseTreeItem):
    def __init__(self, viewAll=False):
        CBaseTreeItem.__init__(self, '', '', 0, None, parent=None)
        if QtGui.qApp.currentOrgInfis() == u'онко':
            self.viewAll = viewAll
        else:
            self.viewAll = True

    def selectable(self):
        return False

    def countChilds(self):
        if not hasattr(QtGui.qApp, 'MKBRootChildsCount') or self.viewAll:
            QtGui.qApp.MKBRootChildsCount = {}

        if self.filter not in QtGui.qApp.MKBRootChildsCount:
            result = 0
            cond = ['parent_code is NULL']
            if self.filter:
                cond.extend(self.filter)
            stmt = 'SELECT COUNT(DiagID) FROM MKB_Tree WHERE {mainCond} {viewCond}'.format(
                mainCond=QtGui.qApp.db.joinAnd(cond),
                viewCond='AND endDate >= CURRENT_TIMESTAMP()' if not self.viewAll else ''
            )
            query = QtGui.qApp.db.query(stmt)
            if query.next():
                record = query.record()
                result = record.value(0).toInt()[0]

            QtGui.qApp.MKBRootChildsCount[self.filter] = result
            return result
        else:
            return QtGui.qApp.MKBRootChildsCount[self.filter]


    def loadChilds(self):
        if not hasattr(QtGui.qApp, 'MKBRootChilds') or self.viewAll:
            QtGui.qApp.MKBRootChilds = {}

        cond = ['parent_code is NULL']
        if self.filter:
            cond.extend(self.filter)

        index = QtGui.qApp.db.joinAnd(cond)

        if index not in QtGui.qApp.MKBRootChilds:
            result = []
            stmt   = 'SELECT DiagID, DiagName FROM MKB_Tree WHERE {mainCond} {viewCond}'.format(
                mainCond=index,
                viewCond='AND endDate >= CURRENT_TIMESTAMP()' if not self.viewAll else ''
            )
            QtCore.debug = stmt
            query = QtGui.qApp.db.query(stmt)
            i = 0
            while query.next():
                record = query.record()
                code   = forceString(record.value('DiagID'))
                name   = forceString(record.value('DiagName'))
                result.append(CICDTreeItem(code, name, i, None, self, self.filter, viewAll=self.viewAll))
                i += 1
            QtGui.qApp.MKBRootChilds[index] = result
            return result
        else:
            return QtGui.qApp.MKBRootChilds[index]

    def findChild(self, path):
        child = self.findChildByCode(path[-1])
        if child:
            return child.findChild(path[:-1])
        else:
            return self

    def findDiag(self, diag):
        if not hasattr(QtGui.qApp, 'MKBRootParentCode') or self.viewAll:
            QtGui.qApp.MKBRootParentCode = {}

        normDiag = diag

        if diag not in QtGui.qApp.MKBRootParentCode:
            db = QtGui.qApp.db
            table = db.table('MKB_Tree')
            record = db.getRecordEx(table, 'parent_code', table['DiagID'].eq(normDiag))
            if not record:
                normDiag = diag[:3]
                record = db.getRecordEx(table, 'parent_code', table['DiagID'].eq(normDiag))
            if record:
                path = []
                parent_code = normDiag
                while parent_code:
                    path.append(parent_code)
                    parent_code = forceString(db.translate(table, 'DiagID', parent_code, 'parent_code'))

                QtGui.qApp.MKBRootParentCode[diag] = path
                return self.findChild(path)

            QtGui.qApp.MKBRootParentCode[diag] = self
            return self
        else:
            return self.findChild(QtGui.qApp.MKBRootParentCode[diag])


class CICDTreeItem(CBaseTreeItem):
    def __init__(self, code, name, index, subclassId, parent=None, filter=None, selectable=True, viewAll=False):
        CBaseTreeItem.__init__(self, code, name, index, subclassId, parent, filter)
        self._selectable = selectable
        if QtGui.qApp.currentOrgInfis() == u'онко':
            self.viewAll = viewAll
        else:
            self.viewAll = True

    def countChilds(self):
        if not hasattr(QtGui.qApp, 'MKBChildsCount') or self.viewAll:
            QtGui.qApp.MKBChildsCount = {}

        if self.code not in QtGui.qApp.MKBChildsCount:
            result = 0
            cond = ['parent_code = \'%s\'' % self.code]
            stmt = 'SELECT COUNT(DiagID) FROM MKB_Tree WHERE {mainCond} {viewCond}'.format(
                mainCond=QtGui.qApp.db.joinAnd(cond),
                viewCond='AND endDate >= CURRENT_TIMESTAMP()' if not self.viewAll else ''
            )
            query = QtGui.qApp.db.query(stmt)
            if query.next():
                record = query.record()
                result = record.value(0).toInt()[0]

            QtGui.qApp.MKBChildsCount[self.code] = result
            return result
        else:
            return QtGui.qApp.MKBChildsCount[self.code]

    def selectable(self):
        if not self._selectable:
            return False
        return True

    def isDiagSelectable(self):
        return self.selectable()

    def loadChilds(self):
        if not hasattr(QtGui.qApp, 'MKBChilds') or self.viewAll:
            QtGui.qApp.MKBChilds = {}

        if self.code not in QtGui.qApp.MKBChilds:
            result = []
            cond = ['parent_code = \'%s\'' % self.code]
            if self.filter:
                cond.extend(self.filter)
            enabledList = []
            stmt = 'SELECT DISTINCT DiagID, DiagName FROM MKB_Tree WHERE {mainCond} {viewCond} ORDER BY DiagID'.format(
                mainCond=QtGui.qApp.db.joinAnd(cond),
                viewCond='AND endDate >= CURRENT_TIMESTAMP()' if not self.viewAll else ''
            )
            query = QtGui.qApp.db.query(stmt)
            i = 0
            while query.next():
                record = query.record()
                code = forceString(record.value('DiagID'))
                enabledList.append(code)

            stmt = 'SELECT DISTINCT DiagID, DiagName FROM MKB_Tree WHERE parent_code = \'%s\' %s ORDER BY DiagID' % (
                self.code, 'AND endDate >= CURRENT_TIMESTAMP()' if not self.viewAll else ''
            )
            query = QtGui.qApp.db.query(stmt)
            i = 0
            while query.next():
                record = query.record()
                code = forceString(record.value('DiagID'))
                name = forceString(record.value('DiagName'))
                result.append(CICDTreeItem(
                    code, name, i, None, self, self.filter, code in enabledList, viewAll=self.viewAll
                ))
                i += 1

            QtGui.qApp.MKBChilds[self.code] = result
            return result
        else:
            return QtGui.qApp.MKBChilds[self.code]

    def findChild(self, path):
        if not path:
            return self
        child = self.findChildByCode(path[-1])
        if child:
            return child.findChild(path[:-1])
        else:
            return self


class CICDTreeModel(QtCore.QAbstractItemModel):
    chCode = QtCore.QVariant(u'Код')
    chName = QtCore.QVariant(u'Наименование')

    def __init__(self, parent=None, viewAll=False):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self._rootItem = CICDRootTreeItem(viewAll=viewAll)
        self.filter = None

    def getRootItem(self):
        return self._rootItem

    def setFilter(self, filter):
        self._rootItem.setFilter(filter)
        self.filter = filter

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.getRootItem().columnCount()

    def data(self, index, role):
        if role == QtCore.Qt.ToolTipRole:
            pass
        if index.isValid():
            column = index.column()
            if role == QtCore.Qt.DisplayRole or (column == 1 and role == QtCore.Qt.ToolTipRole):
                item = index.internalPointer()
                return toVariant(item.data(column))
            elif role == QtCore.Qt.TextColorRole:
                item = index.internalPointer()
                if not item.isDiagSelectable():
                    return QtCore.QVariant(QtGui.QBrush(QtGui.QColor(100,100,100)))
        return QtCore.QVariant()

    def diag(self, index):
        if index.isValid():
            item = index.internalPointer()
            return item.data(0)
        return ''

    def flags(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item.selectable():
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        return QtCore.Qt.ItemIsEnabled

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if section == 0 :
                return self.chCode
            if section == 1 :
                return self.chName
        return QVariant()

    def index(self, row, column, parent):
        if not parent.isValid():
            parentItem = self.getRootItem()
        else:
            parentItem = parent.internalPointer()
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent

        if parentItem == self.getRootItem() or parentItem is None:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if not parent.isValid():
            parentItem = self.getRootItem()
        else:
            parentItem = parent.internalPointer()
        return parentItem.childCount()

    def findDiag(self, code):
        item = self.getRootItem().findDiag(code)
        return self.createIndex(item.index, 0, item)
