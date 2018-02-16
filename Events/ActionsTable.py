# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui, QtSql

from Events.Action import ActionPropertyCopyModifier, CAction
from Events.ActionEditDialog import CActionEditDialog
from Events.ActionPropertyCopyDialog import CActionPropertyCopyDialog
from Events.ActionPropertyMergeDialog import CActionPropertyMergeDialog
from Events.ActionTypeComboBox import CActionTypeComboBox
from Events.ActionsTemplatePrintDialog import CActionTemplatePrintWidget
from library.InDocTable import CInDocTableView
from library.PrintTemplates import getPrintTemplates
from library.Utils import forceBool, forceDate, forceDateTime, forceRef, forceString, toVariant
from library.vm_collections import OrderedDict


class CActionsTableView(CInDocTableView):
    def __init__(self, parent):
        CInDocTableView.__init__(self, parent)

        self.delegate = CActionTypeItemDelegate(self)
        self.setItemDelegate(self.delegate)
        self.setTabKeyNavigation(False)
        self._actOpenInRedactor = None
        self._isDirty = False
        self._parent = None

    def setModel(self, mdl):
        CInDocTableView.setModel(self, mdl)
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)

    def setIsDirty(self, dirty):
        self._isDirty = dirty

    def setParentWidget(self, parent):
        self._parent = parent

    def addOpenInRedactor(self):
        if self._popupMenu is None:
            self.createPopupMenu()
        self.connect(self._popupMenu, QtCore.SIGNAL('aboutToShow()'), self.on_actOpenInRedactorShow)
        self._actOpenInRedactor = QtGui.QAction(u'Открыть в редакторе', self)
        self._actOpenInRedactor.setShortcuts([QtGui.QKeySequence(QtCore.Qt.Key_F2)])
        self._popupMenu.addAction(self._actOpenInRedactor)
        self.connect(self._actOpenInRedactor, QtCore.SIGNAL('triggered()'), self.on_openInRedactor)
        self.addAction(self._actOpenInRedactor)

    def addPrintSelected(self):
        if self._popupMenu is None:
            self.createPopupMenu()
        self._actPrintSelected = QtGui.QAction(u'Напечатать выделенное', self)
        self._popupMenu.addAction(self._actPrintSelected)
        self.connect(self._actPrintSelected, QtCore.SIGNAL('triggered()'), self.on_printSelected)
        self.addAction(self._actPrintSelected)

    def addCopyFromPrevious(self):
        if self._popupMenu is None:
            self.createPopupMenu()
        self._actCopyFromPrevious = QtGui.QAction(u'Копировать значения из предыдущих', self)
        self._popupMenu.addAction(self._actCopyFromPrevious)
        self.connect(self._actCopyFromPrevious, QtCore.SIGNAL('triggered()'), self.on_copyFromPrevious)
        self.addAction(self._actCopyFromPrevious)

    def colKey(self, col):
        return unicode('width_%s' % forceString(col))

    def loadPreferences(self, preferences):
        pass

    def savePreferences(self):
        return {}

    def on_deleteRows(self):
        CInDocTableView.on_deleteRows(self)
        self.emitDelRows()

    def emitDelRows(self):
        self.emit(QtCore.SIGNAL('delRows()'))

    def on_actOpenInRedactorShow(self):
        if self._actOpenInRedactor:
            self._actOpenInRedactor.setEnabled(bool(self.model().items()))

    def on_openInRedactor(self):
        index = self.currentIndex()
        if index.isValid():
            row = index.row()
            items = self.model().items()
            if 0 <= row < len(items):
                oldRecord, oldAction = items[row]
                oldRecord.setValue('event_id', toVariant(self._parent.eventEditor.itemId()))  # Необходимо для шаблонов печати.

                dialog = CActionEditDialog(self)
                dialog.save = lambda: True
                dialog.setForceClientId(self._parent.clientId())
                dialog.setRecord(QtSql.QSqlRecord(oldRecord))
                dialog.setReduced(True)

                CAction.copyAction(oldAction, dialog.action)

                if dialog.exec_():
                    record = dialog.getRecord()
                    items[row] = (record, dialog.action)
                    self._parent.onActionCurrentChanged()

    def on_printSelected(self):
        items = self.model().items()
        rows = self.getSelectedRows()
        items = [(row, items[row]) for row in rows]
        temp = OrderedDict()
        for row, item in items:
            actionType = item[1]._actionType
            if not temp.has_key(actionType):
                temp[actionType] = []
            temp[actionType].append((row, forceDateTime(item[0].value('directionDate'))))

        data = OrderedDict()
        for actionType, actionData in temp.items():
            data[actionType.id] = {'name'      : actionType.name,
                                   'actionData': actionData,
                                   'templates' : getPrintTemplates(actionType.context)
                                   }
        dlg = CActionTemplatePrintWidget()
        self.connect(dlg, QtCore.SIGNAL('printActionTemplateList'), self.on_printActionTemplateList)
        dlg.setItems(data, self._isDirty, forceBool(QtGui.qApp.preferences.appPrefs.get('groupPrintWithoutDialog', QtCore.QVariant())))
        if dlg.model._items:
            dlg.exec_()
        else:
            dlg.printOnly()

    def on_printActionTemplateList(self, list):
        self.emit(QtCore.SIGNAL('printActionTemplateList'), list)

    def on_copyFromPrevious(self):
        row = self.currentIndex().row()
        record, action = self.model().items()[row]
        actionTypeId = forceRef(record.value('actionType_id'))
        begDate = forceDate(record.value('begDate'))

        if actionTypeId:
            dlg = CActionPropertyCopyDialog(self,
                                            clientId=self._parent.clientId(),
                                            actionTypeId=actionTypeId,
                                            begDate=begDate)
            dlg.load()
            if dlg.exec_():
                for propertyTypeId, propertyList in dlg.getSelectedProperties().iteritems():
                    destProperty = action.getPropertyById(propertyTypeId)

                    # if len(propertyList) == 1:
                    #     destProperty.setValue(propertyList[0].value)

                    if propertyList:
                        copyModifier = max(prop.copyModifier for prop in propertyList)
                        if copyModifier == ActionPropertyCopyModifier.Concat:
                            destValue = destProperty.getValue() if destProperty.getValue() else u''
                            destProperty.setValue(destValue + u''.join(prop.value for prop in propertyList))

                        elif copyModifier == ActionPropertyCopyModifier.Last:
                            if not destProperty.getValue():
                                lastProperty = max(propertyList, key=lambda item: item.endDate)
                                destProperty.setValue(lastProperty.value)

                        elif copyModifier == ActionPropertyCopyModifier.Merge:
                            propertyIdList = [prop.id for prop in propertyList]
                            mergeDialog = CActionPropertyMergeDialog(self)
                            mergeDialog.setData(destProperty.type().name, propertyIdList, destProperty.getValue())
                            if mergeDialog.exec_():
                                destProperty.setValue(mergeDialog.getValue())


class CActionTypeItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent):
        QtGui.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        if index.column() == 0:
            editor = CActionTypeComboBox(parent)
            editor.setClass(index.model().actionTypeClass)
            editor.setDisabledActionTypeIdList(index.model().disabledActionTypeIdList)
            editor.setEnabledActionTypeIdList(index.model().enabledActionTypeIdList)
            # prefferedWidth = self.parent().model().col.prefferedWidth
            # editor.setPrefferedWidth(prefferedWidth)
            dialog = index.model().eventEditor
            editor.setFilter(dialog.clientSex, dialog.clientAge)
            return editor

    def setEditorData(self, editor, index):
        model = index.model()
        editor.setValue(forceRef(model.data(index, QtCore.Qt.EditRole)))

    def setModelData(self, editor, model, index):
        model.setData(index, toVariant(editor.value()))

    def emitCommitDataAndClose(self, editor, hint=QtGui.QAbstractItemDelegate.NoHint):
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), editor)
        self.emit(QtCore.SIGNAL('closeEditor(QWidget *,QAbstractItemDelegate::EndEditHint)'), editor, hint)

    def eventFilter(self, editor, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Tab:
                if editor is not None:
                    self.emitCommitDataAndClose(editor)
                self.parent().focusNextChild()
                return True
            elif event.key() == QtCore.Qt.Key_Backtab:
                if editor is not None:
                    self.emitCommitDataAndClose(editor)
                self.parent().focusPreviousChild()
                return True
            elif event.key() == QtCore.Qt.Key_Return:
                if editor is not None:
                    self.emitCommitDataAndClose(editor)
                return True
        return QtGui.QItemDelegate.eventFilter(self, editor, event)


class CSupportServiceButtonBox():
    def __init__(self, parent):
        self._btns = {}
        self._btnsName = {}
        self.showingBtns = []

    def setVisible(self, bool):
        for btn in self._btns.values():
            btn.setVisible(False)
        if bool:
            for code in self.showingBtns:
                self._btns[code].setVisible(True)

    def addBtn(self, btn, code, name):
        self._btns[code] = btn
        self._btnsName[code] = name

    def cleartBtns(self):
        self.showingBtns = []

    def addShowingBtn(self, code):
        if self._btns.has_key(code):
            self.showingBtns.append(code)
