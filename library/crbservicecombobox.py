# -*- coding: utf-8 -*-

from Ui_RBServiceComboBoxPopup import Ui_RBServiceComboBoxPopup
from library.Utils import *
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.crbcombobox import CRBComboBox, CRBSelectionModel


class CRBServiceComboBoxPopup(QtGui.QFrame, Ui_RBServiceComboBoxPopup):
    __pyqtSignals__ = ('serviceSelected(int)',
                      )
    def __init__(self, parent):
        QtGui.QFrame.__init__(self, parent, Qt.Popup)
        self.setupUi(self)
        self._parent = parent
        self._model = parent._model
        self._selectionModel = CRBSelectionModel(self._model)
        self.tblService.setModel(self._model)
        self._addNone      = True
        self._staticFilter = None
        self._order        = ''
        self.id            = None
        self._filter       = ''
        self.tblService.setSelectionModel(self._selectionModel)

        self.cmbSection.setTable('rbServiceSection')
        self.cmbSection.setFilter(order='id')
        self.cmbType.setTable('rbServiceType')
        self.cmbClass.setTable('rbServiceClass')
        self.table = QtGui.qApp.db.table('rbService')
        self.edtBegDate.canBeEmpty(True)
        self.edtEndDate.canBeEmpty(True)
        self.edtCode.setFocus(Qt.ShortcutFocusReason)
        self.resetEdits()
        self.cmbSection.installEventFilter(self)
        self.cmbType.installEventFilter(self)
        self.cmbClass.installEventFilter(self)
        self.edtCode.installEventFilter(self)
        self.edtName.installEventFilter(self)
        self.edtBegDate.installEventFilter(self)
        self.edtEndDate.installEventFilter(self)
        self.tblServiceSettings()
        self.updateTypesClasses()
        self.chkIsFilterServiceByCurrentCode.setVisible(False)  # Логика проверки кода изменена, данный чекбокс более не применим. Если не будет отката - удалить совсем после середины 2015 года.

    def tblServiceSettings(self):
        pass

    def setTableFocus(self):
        self.tblService.setFocus()

    def resetEdits(self):
        self.cmbSection.setValue(0)
        self.cmbType.setValue(0)
        self.cmbClass.setValue(0)
        self.edtCode.setText('')
        self.edtName.setText('')
        self.chkEIS.setCheckState(Qt.PartiallyChecked)
        self.chkNomenclature.setCheckState(Qt.PartiallyChecked)
        self.edtBegDate.setDate(QDate())
        self.edtEndDate.setDate(QDate())

    def hideColumn(self, index):
        self.tblService.hideColumn(index)

    def show(self):
        scrollBar = self.tblService.horizontalScrollBar()
        scrollBar.setValue(0)
        QtGui.QFrame.show(self)

    def rowCount(self, index=None):
        return self._model.rowCount()

    def searchCodeEx(self, searchString):
        return self._model.searchCodeEx(searchString)


    def setCurrentIndex(self, rowIndex):
        index = self._model.index(rowIndex, 0)
        self.tblService.setCurrentIndex(index)

    def currentIndex(self):
        return self.tblService.currentIndex()

    def setSelectionCurrentIndex(self, index, selectionFlags):
        self._selectionModel.setCurrentIndex(index, selectionFlags)

    def model(self):
        return self.tblService.model()


    def setViewFocus(self):
        self.tblService.setFocus()

    def view(self):
        return self.tblService

    def loadData(self, addNone=True, filter='', order=None):
        self._addNone   = addNone
        self._filter    = filter
        self._order     = order
        self._model.loadData(addNone, filter, order)

    def setFilter(self, filter='', order=None):
        self._filter    = filter
        self._order     = order
        self.loadData(self._addNone, filter, order)

    def reloadData(self):
        self._model.loadData(self._addNone, self._filter, self._order)

    def setModel(self, model):
        self._model = model
        self.tblService.setModel(model)

    def on_buttonBox_apply(self):
        table = self.table
        db = QtGui.qApp.db
        cond = []
        properties = {}
        properties['section'] = forceRef(self.cmbSection.value())
        properties['type'] = forceRef(self.cmbType.value())
        properties['class'] = forceRef(self.cmbClass.value())
        properties['code'] = forceStringEx(self.edtCode.text())
        properties['name'] = forceStringEx(self.edtName.text())
        properties['EIS'] = self.chkEIS.checkState()
        properties['nomenclature'] = self.chkNomenclature.checkState()
        properties['begDate'] = forceDate(self.edtBegDate.date())
        properties['endDate'] = forceDate(self.edtEndDate.date())

        section = properties.get('section', 0)
        if section:
            cond.append("""(select code
                            from rbServiceSection
                            where id = %s)
                            = left(rbService.code, 1)"""%section)

        type = properties.get('type', 0)
        if type:
            cond.append("""(select code
                            from rbServiceType
                            where id = %s)
                            = substr(rbService.code from 2 for 2)"""%type)

        class_ = properties.get('class', 0)
        if class_:
            cond.append("""rbService.code like concat("___.",
            (select code
                            from rbServiceClass
                            where id = %s), "%%")
                            """%class_)

        code= properties.get('code', '')
        if code:
            cond.append(table['code'].like(addDots(code)))

        name = properties.get('name', '')
        if name:
            cond.append(table['name'].like(addDotsEx(name)))

        flagEIS = properties.get('EIS', Qt.PartiallyChecked)
        if flagEIS != Qt.PartiallyChecked:
            cond.append(table['eisLegacy'].eq( \
                flagEIS != Qt.Unchecked))

        flagNomenclature = properties.get('nomenclature', Qt.PartiallyChecked)
        if flagNomenclature != Qt.PartiallyChecked:
            cond.append(table['nomenclatureLegacy'].eq( \
                flagNomenclature!= Qt.Unchecked))

        begDate = properties.get('begDate',  QDate())
        if not begDate.isNull():
            cond.append(table['begDate'].dateGe(begDate))

        endDate = properties.get('endDate',  QDate())
        if not endDate.isNull():
            cond.append(table['endDate'].dateLe(endDate))
        f = db.joinAnd(cond)
        self.setFilter(f)
        if self.rowCount():
            self.tabWidget.setCurrentIndex(0)


    def on_buttonBox_reset(self):
        self.resetEdits()
        self.setFilter('')

    def selectItemByIndex(self, index):
        row = index.row()
        self.emit(SIGNAL('serviceSelected(int)'), row)
        self.hide()

    def callWithIdSave(self, func):
        rowIndex = self.currentIndex().row()
        id = self._model.getId(rowIndex)
        func()
        self.id = id
        rowIndex = self._model.searchId(id)
        if rowIndex > -1 and rowIndex < self._model.rowCount():
            self.emit(SIGNAL('serviceSelected(int)'), rowIndex)


    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        rowIndex = self.currentIndex().row()
        id = self._model.getId(rowIndex)
        if not self.id:
            self.id = id
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply or button == 'enter':
            self.on_buttonBox_apply()
            rowIndex = self._model.searchId(id)
            self.id = id
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.on_buttonBox_reset()
            rowIndex = self._model.searchId(self.id)
        if rowIndex > -1 and rowIndex < self._model.rowCount():
            self.emit(SIGNAL('serviceSelected(int)'), rowIndex)

    @pyqtSlot(QModelIndex)
    def on_tblService_clicked(self, index):
        self.selectItemByIndex(index)

    def updateTypesClasses(self):
        code = self.cmbSection.code()
        if code and code != "0":
            self.edtCode.setText(code)
            self.cmbType.setEnabled(True)
            self.cmbType.setFilter('section="%s"'%code)
            if code in (u'А', u'В'):
                self.cmbClass.setEnabled(True)
                self.cmbClass.setFilter('section="%s"'%code)
            else:
                self.cmbClass.setEnabled(False)
        else:
            self.cmbType.setValue(0)
            self.cmbType.setEnabled(False)
            self.cmbClass.setValue(0)
            self.cmbClass.setEnabled(False)


    @pyqtSlot(int)
    def on_cmbSection_currentIndexChanged(self, val):
        self.updateTypesClasses()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key in [Qt.Key_Return, Qt.Key_Enter, Qt.Key_E, Qt.Key_G]:
                if key == Qt.Key_E:
                    obj.keyPressEvent(event)
                if key in [Qt.Key_Return, Qt.Key_Enter]:
                    return False
                self.keyPressEvent(event)
                return False
            if  key == Qt.Key_Tab:
                self.focusNextPrevChild(True)
                return True
        return False


    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            if self.tabWidget.currentIndex():
                self.callWithIdSave(self.on_buttonBox_applied)
            else:
                index = self.tblService.selectedIndexes()
                if index:
                    self.selectItemByIndex(index[0])
        if (event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_E):
            self.tabWidget.setCurrentIndex(0)
        if (event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_G):
            self.tabWidget.setCurrentIndex(1)
        QtGui.QFrame.keyPressEvent(self, event)


class CRBServiceComboBox(CRBComboBox):
    def __init__(self, parent, filterByHospitalBedsProfile=False, additionalIdList=None):
        if not additionalIdList:
            additionalIdList = []
        QtGui.QComboBox.__init__(self, parent)
        self._model = CRBServiceComboBoxModel(self, filterByHospitalBedsProfile, additionalIdList)
        self._searchString = ''
        self._staticFilter = None
        self._selectionModel = CRBSelectionModel(self._model)
        self.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        self.prefferedWidth = None
        self.popupView = CRBServiceComboBoxPopup(self)
        self.setModel(self._model)
        self.connect(self.popupView,SIGNAL('serviceSelected(int)'), self.setValueByRow)
        self.setModelColumn(0)


    def model(self):
        return self._model
    
    def setStaticFilter(self, filter):
        if filter != self._staticFilter:
            self.__staticFilter = filter
            self._model.setStaticFilter(filter)
            self.reloadData()

    def loadData(self, addNone=True, filter='', order=None):
        self.popupView.loadData(addNone, filter, order)

    def setFilter(self, filter='', order=None):
        self.popupView.setFilter(filter, order)

    def reloadData(self):
        self.popupView.reloadData()

    def setModel(self, model):
        self.popupView.setModel(model)
        CRBComboBox.setModel(self, model)


    def showPopup(self) :
        if not self.dataLoaded():
            self.reloadData()
        self._searchString = ''
        pos = self.rect().bottomLeft()
        pos2 = self.rect().topLeft()
        pos = self.mapToGlobal(pos)
        pos2 = self.mapToGlobal(pos2)
        size = self.popupView.sizeHint()
        width= max(size.width(), self.width())
        size.setWidth(width)
        screen = QtGui.QApplication.desktop().availableGeometry(pos)
        pos.setX( max(min(pos.x(), screen.right()-size.width()), screen.left()) )
        pos.setY( max(min(pos.y(), screen.bottom()-size.height()), screen.top()) )
        self.popupView.move(pos)
        self.popupView.resize(size)
        self.popupView.setTableFocus()
        self.popupView.show()

    def currentIndex(self):
        return self.popupView.currentIndex()

    def lookup(self):
        i, self._searchString = self.popupView.searchCodeEx(self._searchString)
        if i>=0 and i!=self.currentIndex() :
            self.setIndex(i)

    def setValue(self, itemId):
        if not self.dataLoaded():
            self.reloadData()
        if itemId is None:
            self.resetValue()
        else:
            rowIndex = self._model.searchId(itemId)
            self.setIndex(rowIndex)

    def resetValue(self):
        self.setIndex(0)

    def setValueByRow(self, rowIndex):
        itemId = self._model.getId(rowIndex)
        self.setValue(itemId)

    def value(self):
        rowIndex = self.currentIndex().row()
        value = self._model.getId(rowIndex)
        return value

    def setCode(self, code):
        if not self.dataLoaded():
            self.reloadData()
        rowIndex = self._model.searchCode(code)
        self.setIndex(rowIndex)

    def setIndex(self, rowIndex):
        if not self.dataLoaded():
            self.reloadData()
        if rowIndex is None:
            return
        self.popupView.setCurrentIndex(rowIndex)
        self.setCurrentIndex(rowIndex)

    def code(self):
        rowIndex = self.currentIndex().row()
        if rowIndex > -1:
            return self.model().getCode(rowIndex)
        return None

    def setShowFields(self, showFields):
        pass

    def setPrefferedWidth(self, prefferedWidth):
        pass

    def setServiceFilterByCode(self, visitServiceFilter):
        self.model().setCodeRegexp(visitServiceFilter)

    def setSexAgeVars(self, sex, birthDate, specialityId):
        self.model().setSexAgeVars(sex, birthDate, specialityId)

    def setEventGoalFilter(self, goalId):
        self.model().setEventGoalFilter(goalId)

    def setTable(self, tableName, addNone=True, filter='', order=None):
        self.loadData(addNone, filter, order)

    def dataLoaded(self):
        return self._model._dataLoaded
#
# 
# ##############################################################################
#
#


class CRBServiceComboBoxModel(QAbstractTableModel):
    filterByHospitalBedsProfileIdList = None
    def __init__(self, parent, filterByHospitalBedsProfile=False, additionalIdList=None):
        if not additionalIdList:
            additionalIdList = []
        QAbstractTableModel.__init__(self, parent)
        self._filter       = u''
        self._staticFilter = None
        self._addNone      = True
        self._order        = None
        self._table        = QtGui.qApp.db.table('rbService')
        self._items        = []
        self._mapIdToRow   = {}
        self._mapCodeToRow = {}
        self._dataLoaded   = False
        self.sexAgeVars    = None, None, None
        self.codeRegexp    = None
        self.goalId     = None
        self._filterByHospitalBedsProfile = filterByHospitalBedsProfile
        self._additionalIdList = additionalIdList
        if filterByHospitalBedsProfile:
            self._createFilterByHospitalBedsProfile()
        
    @classmethod
    def _createFilterByHospitalBedsProfile(cls):
        if cls.filterByHospitalBedsProfileIdList is None:
            db = QtGui.qApp.db
            
            tableOrgStructure    = db.table('OrgStructure')
            tableOrgStructureHB  = db.table('OrgStructure_HospitalBed')
            tableOrgStructureHBP = db.table('rbHospitalBedProfile')
            
            queryTable = tableOrgStructure.innerJoin(tableOrgStructureHB, 
                                                     tableOrgStructure['id'].eq(tableOrgStructureHB['master_id']))
            queryTable = queryTable.innerJoin(tableOrgStructureHBP, 
                                              tableOrgStructureHB['profile_id'].eq(tableOrgStructureHBP['id']))
            
            cond = [tableOrgStructure['type'].eq(0), 
                    tableOrgStructure['deleted'].eq(0)]
                    
            field = tableOrgStructureHBP['service_id'].name()

            cls.filterByHospitalBedsProfileIdList = db.getDistinctIdList(queryTable, field, cond)
        
    def setAddNone(self, addNone=True):
        self._addNone  = addNone
        self.reloadData()
        
    def setStaticFilter(self, filter):
        self._staticFilter = filter
        
    def setFilter(self, filter):
        if isinstance(filter, (list, tuple)):
            filter = QtGui.qApp.db.joinAnd(filter)
        self._filter = filter
        self.reloadData()
        
    def setOrder(self, order):
        self._order = order
        self.reloadData()
        
    def columnCount(self, index=QtCore.QModelIndex()):
        return 2 # code, name
        
    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self._items)
        
    def items(self):
        return self._items

    def setSexAgeVars(self, sex, birthDate, specialityId):
        """Применяется только при наличии serviceCodeFilter"""
        self.sexAgeVars = sex, birthDate, specialityId

    def setEventGoalFilter(self, goalId):
        self.goalId = goalId

    def setCodeRegexp(self, regexp):
        self.codeRegexp = regexp

    def loadData(self, addNone=True, _filter=u'', order=None):
        items = []
        if addNone:
            items.append((0, '-', u'не задано'))
            self._mapIdToRow[0]     = 0
            self._mapCodeToRow['-'] = 0

        # Making query
        db = QtGui.qApp.db
        cond = []
        sex, birthDate, specialityId = self.sexAgeVars
        if self.codeRegexp:
            cond.append('rbService.`code` RLIKE \'%s\'' % self.codeRegexp)
        if _filter:
            cond.append(_filter)
        if self._staticFilter:
            cond.append(self._staticFilter)
        if self._filterByHospitalBedsProfile:
            filterIdList = []
            filterIdList.extend(CRBServiceComboBoxModel.filterByHospitalBedsProfileIdList)
            filterIdList.extend(self._additionalIdList)
            cond.append(self._table['id'].inlist(filterIdList))
        queryTable = self._table
        group = ''
        if self.codeRegexp and specialityId:
            tableServiceProfile = db.table('rbService_Profile')
            queryTable = queryTable.leftJoin(tableServiceProfile, db.joinAnd([tableServiceProfile['master_id'].eq(self._table['id']), tableServiceProfile['speciality_id'].eq(specialityId)]))
            currentDateStr = QDate.currentDate().toString(QtCore.Qt.ISODate)
            sexAgeParams = (
                sex,
                birthDate.toString(Qt.ISODate),
                currentDateStr)
            subCond = [
                'isSexAndAgeSuitable(%s, \'%s\', rbService_Profile.sex, rbService_Profile.age, \'%s\')' % sexAgeParams,
            ]
            cond.append(db.joinOr(subCond))
            group = self._table['id']
        if self.goalId is not None:
            tableServiceGoal = db.table('rbService_Goal')
            queryTable = queryTable.innerJoin(tableServiceGoal, tableServiceGoal['master_id'].eq(self._table['id']))
            cond.append(tableServiceGoal['goal_id'].eq(self.goalId))
        query = db.query(db.selectStmt(queryTable, [self._table['id'], self._table['code'], self._table['name']], cond, order, group))

        #Processing query result
        while query.next():
            record = query.record()
            id     = forceRef(record.value('id'))
            code   = forceString(record.value('code'))
            name   = forceString(record.value('name'))
            currentRowIndex          = len(items)
            self._mapIdToRow[id]     = currentRowIndex
            self._mapCodeToRow[code] = currentRowIndex
            items.append((id, code, name))

        #Some magic?
        additionalIdList = filter(lambda x: x in self._mapIdToRow, self._additionalIdList)
        firstId = additionalIdList[0] if additionalIdList else None
        if firstId:
            firstRow = 1 if addNone else 0
            row = self._mapIdToRow.get(firstId, 0)      # Если есть additionalIdList, то подставляем
            item = items[row]
            oldFirstItem = items[firstRow]
            self._mapIdToRow[oldFirstItem[0]]   = row
            self._mapCodeToRow[oldFirstItem[1]] = row

            self._mapIdToRow[item[0]]   = firstRow
            self._mapCodeToRow[item[1]] = firstRow

            items[firstRow], items[row] = items[row], items[firstRow]

        self._items = items
        self.reset()
        self._dataLoaded   = True
        
    def reloadData(self):
        self.loadData(self._addNone, self._filter, self._order)
        
        
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                if section == 0:
                    return toVariant(u'Код')
                elif section == 1:
                    return toVariant(u'Наименование')
        return QVariant()
        
        
    def data(self, index, role=Qt.DisplayRole):
        if not (index.isValid() and len(self._items)>0):
            return QVariant()
        row    = index.row()
        column = index.column()
        if row > len(self._items)-1:
            return QVariant()
        if role == Qt.DisplayRole:
            return QVariant(self._items[row][column+1])
        if role == Qt.ToolTipRole:
            return QVariant(self._items[row][column+1]) 
        return QVariant()
        
        
    def getId(self, row):
        if self.rowCount() > 0 and row > -1:
            return self._items[row][0]
        return None
        
    def searchId(self, id):
        return self._mapIdToRow.get(id, None)
        
    def searchCode(self, code):
        return self._mapCodeToRow.get(code, None)
        
    def getCode(self, row):
        if self.rowCount() > 0:
            return self._items[row][1]
        return ''
        
    def getName(self, row):
        if self.rowCount() > 0:
            return self._items[row][2]
        return ''
        
    def searchCodeEx(self, code):
        def maxCommonLen(c1, c2):
            n = min(len(c1), len(c2))
            for i in xrange(n):
                if c1[i] != c2[i]:
                    return i
            return n

        code = unicode(code).upper()
        lenCode = len(code)
        n = self.rowCount()
        maxLen = -1
        maxLenAt = -1
        for i in xrange( n ):
            commonLen = maxCommonLen(unicode(self.getCode(i)).upper(), code)
            if commonLen == lenCode:
                return i, code
            if commonLen > maxLen:
                maxLen, maxLenAt = commonLen, i
        for i in xrange( n ):
            commonLen = maxCommonLen(unicode(self.getName(i)).upper(), code)
            if commonLen == lenCode:
                return i, code
            if commonLen > maxLen:
                maxLen, maxLenAt = commonLen, i
        return maxLenAt, code[:maxLen]
