# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from Forms.F003.Ui_MenuContent import Ui_MenuContent
from Forms.F003.Ui_MenuDialog import Ui_MenuDialog
from RefBooks.Tables            import rbCode, rbName
from Reports.ReportView         import CReportViewDialog
from Ui_RBMenu                  import Ui_RBMenu
from library.DialogBase         import CDialogBase
from library.InDocTable         import CInDocTableModel, CRBInDocTableCol
from library.ItemsListDialog    import CItemEditorBaseDialog, CItemsListDialogEx
from library.TableModel         import CTableModel, CTextCol, CRefBookCol
from library.Utils              import forceRef, forceString, forceStringEx, toVariant, forceInt, forceBool


class CRBMenu(CItemsListDialogEx):
    def __init__(self, parent):
        CItemsListDialogEx.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            CRefBookCol(u'Диета', ['diet_id'], 'rbDiet', 40),
            CRefBookCol(u'Диета ухаживающего', ['courtingDiet_id'], 'rbDiet', 40)
            ], 'rbMenu', [rbCode, rbName])
        self.setWindowTitleEx(u'Шаблоны питания')

    def getItemEditor(self):
        return CRBMenuEditor(self)


class CRBMenuEditor(CItemEditorBaseDialog, Ui_RBMenu):
    def __init__(self,  parent):
        CItemEditorBaseDialog.__init__(self, parent, 'rbMenu')
        self.addModels('MenuContent', CMenuContent(self))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitleEx(u'Шаблон питания')
        self.setModels(self.tblMenuContent, self.modelMenuContent, self.selectionModelMenuContent)
        self.setupDirtyCather()
        self.cmbDiet.setTable('rbDiet')
        self.cmbCourtingDiet.setTable('rbDiet')

        # self.addObject('actDelRows', QtGui.QAction(u'Удалить выделенные строки', self))
        # self.addObject('mnuMenuContent', QtGui.QMenu(self))
        # self.mnuMenuContent.addAction(self.actDelRows)
        # self.tblMenuContent.setPopupMenu(self.mnuMenuContent)
        db = QtGui.qApp.db
        tableRBDiet = db.table('rbDiet')
        records = db.getRecordList(tableRBDiet)
        self.dietMap = {}
        for record in records:
            dietId = forceInt(record.value('id'))
            dietCode = forceString(record.value('code'))
            dietName = forceString(record.value('name'))
            allowMeals = forceBool(record.value('allow_meals'))
            self.dietMap[dietId] = {'code': dietCode, 'name': dietName, 'allow_meals': allowMeals}
        self.tblMenuContent.addPopupDelRow()

    def save(self):
        menu_id = CItemEditorBaseDialog.save(self)
        if menu_id:
            self.modelMenuContent.saveItems(menu_id)
        return menu_id

    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        self.edtCode.setText(forceString(record.value(rbCode)))
        self.edtName.setText(forceString(record.value(rbName)))
        self.cmbCourtingDiet.setValue(forceRef(record.value('courtingDiet_id')))
        self.modelMenuContent.loadItems(self.itemId())
        self.tblMenuContent.setEnabled(True if self.cmbDiet.value() is None or self.dietMap[self.cmbDiet.value()]['allow_meals'] else False)
        self.cmbDiet.setFilter('allow_meals = 1' if self.modelMenuContent.rowCount() > 1 else '')
        self.cmbDiet.setValue(forceRef(record.value('diet_id')))

    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue(rbCode,             toVariant(forceStringEx(self.edtCode.text())))
        record.setValue(rbName,             toVariant(forceStringEx(self.edtName.text())))
        record.setValue('diet_id',          toVariant(self.cmbDiet.value()))
        record.setValue('courtingDiet_id',  toVariant(self.cmbCourtingDiet.value()))
        return record

    def checkDataEntered(self):
        if not CItemEditorBaseDialog.checkDataEntered(self):
            return False
        for row, record in enumerate(self.modelMenuContent.items()):
            if not self.checkMenuContentEntered(row, record):
                return False
        return True

    def checkMenuContentEntered(self, row, record):
        result = True
        result = result and (forceRef(record.value('mealTime_id')) or self.checkInputMessage(u'период питания', False, self.tblMenuContent, row, record.indexOf('mealTime_id')))
        result = result and (forceRef(record.value('meal_id')) or self.checkInputMessage(u'еда', False, self.tblMenuContent, row, record.indexOf('meal_id')))
        return result

    @QtCore.pyqtSlot(int)
    def on_cmbDiet_currentIndexChanged(self, index):
        self.tblMenuContent.setEnabled(True if self.cmbDiet.value() is None or self.dietMap[self.cmbDiet.value()]['allow_meals'] else False)


    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def on_modelMenuContent_dataChanged(self, topLeft, bottomRight):
        value = self.cmbDiet.value()
        self.cmbDiet.setFilter('allow_meals = 1' if self.modelMenuContent.rowCount() > 1 else '')
        self.cmbDiet.setValue(value)


class CMenuContent(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbMenu_Content', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Периоды питания', 'mealTime_id', 30, 'rbMealTime', addNone=False))
        self.addCol(CRBInDocTableCol(u'Рацион', 'meal_id', 30, 'rbMeal', addNone=False))


class CMenuDialog(CDialogBase, Ui_MenuDialog):
    def __init__(self, parent, cols, tableName, order, forSelect=False, filterClass=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.setup(cols, tableName, order, forSelect, filterClass)


    def setup(self, cols, tableName, order, forSelect=False, filterClass=None):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.forSelect = forSelect
        self.filterClass = filterClass
        self.props = {}
        self.order = order
        self.model = CTableModel(self, cols, tableName)
        idList = self.select(self.props)
        self.model.setIdList(idList)
        self.tblItems.setModel(self.model)
        if idList:
            self.tblItems.selectRow(0)
        self.btnEdit.setDefault(not self.forSelect)
        self.tblItems.setFocus(QtCore.Qt.OtherFocusReason)
        self.label.setText(u'всего: %d' % len(idList))

        QtCore.QObject.connect(
            self.tblItems.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'), self.setSort)


    def select(self, props):
        table = self.model.table()
        return QtGui.qApp.db.getIdList(table.name(), 'id', '', self.order)


    def selectItem(self):
        return self.exec_()


    def setCurrentItemId(self, itemId):
        self.tblItems.setCurrentItemId(itemId)


    def currentItemId(self):
        return self.tblItems.currentItemId()


    def renewListAndSetTo(self, itemId=None):
        idList = self.select(self.props)
        self.tblItems.setIdList(idList, itemId)
        self.label.setText(u'всего: %d' % len(idList))


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblItems_doubleClicked(self, index):
        self.selected = True
        self.close()


    @QtCore.pyqtSlot()
    def on_btnSelected_clicked(self):
        self.selected = True
        self.close()


    @QtCore.pyqtSlot()
    def on_btnEdit_clicked(self):
        itemId = self.currentItemId()
        if itemId:
            dialog = self.getItemEditor()
            dialog.load(itemId)
            if dialog.exec_():
                itemId = dialog.itemId()
                self.renewListAndSetTo(itemId)

    def getReportHeader(self):
        return self.objectName()

    def getFilterAsText(self):
        return u''

    def contentToHTML(self):
        reportHeader=self.getReportHeader()
        self.tblItems.setReportHeader(reportHeader)
        reportDescription=self.getFilterAsText()
        self.tblItems.setReportDescription(reportDescription)
        return self.tblItems.contentToHTML()

    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        html = self.contentToHTML()
        view = CReportViewDialog(self)
        view.setText(html)
        view.exec_()


    def setSort(self, col):
        name=self.model.cols()[col].fields()[0]
        self.order = name
        header=self.tblItems.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.setSortIndicator(col, QtCore.Qt.AscendingOrder)
        self.renewListAndSetTo(self.currentItemId())


class CGetRBMenu(CMenuDialog):
    def __init__(self, parent):
        CMenuDialog.__init__(self, parent, [
            CTextCol(u'Код',          [rbCode], 20),
            CTextCol(u'Наименование', [rbName], 40),
            ], 'rbMenu', [rbCode, rbName])
        self.setWindowTitleEx(u'Шаблоны питания')
        self.selected = False

    def getItemEditor(self):
        return CRBMenuContentView(self)

    def exec_(self):
        result = CMenuDialog.exec_(self)
        if self.selected:
            result = self.currentItemId()
        return result


class CRBMenuContentView(QtGui.QDialog, Ui_MenuContent):
    def __init__(self,  parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.tblMenuContent.setModel(CRBMenuContentViewModel(self))
        self.itemId = None

    def load(self, itemId):
        self.itemId = itemId
        if itemId:
            record = QtGui.qApp.db.getRecordEx('rbMenu', '*', 'id = %d'%(itemId))
            if record:
                self.edtCode.setText(forceString(record.value(rbCode)))
                self.edtName.setText(forceString(record.value(rbName)))
                self.tblMenuContent.model().loadItems(itemId)

    def itemId(self):
        return self.itemId


class CRBMenuContentViewModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'rbMenu_Content', 'id', 'master_id', parent)
        self.addCol(CRBInDocTableCol(u'Периоды питания', 'mealTime_id', 30, 'rbMealTime', addNone=False)).setReadOnly(True)
        self.addCol(CRBInDocTableCol(u'Рацион', 'meal_id', 30, 'rbMeal', addNone=False)).setReadOnly(True)
