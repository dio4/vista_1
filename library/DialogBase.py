# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006,2010 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

from PyQt4.QtCore import *

from library.DateEdit import CDateEdit
from library.LoggingModule import Logger
from library.PreferencesMixin import CDialogPreferencesMixin


class CConstructHelperMixin:
    def getModelAttributeName(self, name, isSelectionModel = False):
        return ('model' if not isSelectionModel else 'selectionModel') + name

    ## Добавляет модель в объект под указанным именем. 
    # Т.е. устанавливает атрибуты для основной модели и модели выбора, 
    # а так же устанавливает имена объектов для этих моделей для корректной работы мета объектной системы Qt
    # @param name: имя модели, которое будет использоватья для формирования имен объектов 
    #             путем добавления разных префиксов для основной модели и модели выбора.
    # @param model: объект добавляемой модели, cсылка на который будет сохранена в классе. 
    #                А так же на его основе будет сформирована модель выбора.
    def addModels(self, name, model):
        modelName = self.getModelAttributeName(name, False)
        self.__setattr__(modelName, model)
        model.setObjectName(modelName)
        selectionModelName = self.getModelAttributeName(name, True)
        selectionModel = QtGui.QItemSelectionModel(model, self)
        self.__setattr__(selectionModelName, selectionModel)
        selectionModel.setObjectName(selectionModelName)
        
    def isModelExists(self, name):
        u"""Проверяет наличие у объекта модели-атрибута с указанным именем"""
        return hasattr(self, self.getModelAttributeName(name, False)) and hasattr(self, self.getModelAttributeName(name, True))
    
    def addObject(self, name, obj):
        self.__setattr__(name, obj)
        obj.setObjectName(name)


    def setModels(self, widget, dataModel, selectionModel=None):
        widget.setModel(dataModel)
        if selectionModel:
            widget.setSelectionModel(selectionModel)

    def setModelsEx(self, widget, dataModel, selectionModel=None):
        widget.setModelEx(dataModel)
        if selectionModel:
            widget.setSelectionModelEx(selectionModel)

    def addBarcodeScanAction(self, name):
        action = QtGui.QAction(self)
        setattr(self, name, action)
        getattr(self, name).setObjectName(name)
        action.setShortcuts([QtGui.QKeySequence(Qt.CTRL+Qt.Key_B),
                             QtGui.QKeySequence(Qt.CTRL+Qt.SHIFT+Qt.Key_B), ])
        # для регистрации hotkey в заданном widget
        # не забываем сделать widget.addAction(action) или self.addAction(action)


class CDialogBase(QtGui.QDialog, CDialogPreferencesMixin, CConstructHelperMixin):
    forListView  = 0
    forSelection = 1

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        Logger.logWindowAccess(windowName=type(self).__name__, notes=u'Диалог')
        self.__isDirty = False
        self.statusBar = None

    def setWindowTitle(self,  title):
        if unicode(title).find('[*]') == -1 :
            title = title + ' [*]'
        QtGui.QDialog.setWindowTitle(self,  title)

    def setWindowTitleEx(self, title):
        self.setWindowTitle(title)
        self.setObjectName(title)

    def isDirty(self):
        return self.__isDirty

    @QtCore.pyqtSlot()
    def markAsDirty(self):
        self.setIsDirty(True)

    def setIsDirty(self, dirty=True):
        self.__isDirty = dirty
        self.setWindowModified(dirty)
        if hasattr(self, 'buttonBox'):
            applyButton = self.buttonBox.button(QtGui.QDialogButtonBox.Apply)
            if applyButton:
                applyButton.setEnabled(dirty)

    def saveData(self):
        return True

    def setWidgetVisible(self, widget):
        u"""
        Делает виджет видимым для пользователя, активируя все виджеты-вкладки, внутри которых находится переданный виджет.
        :param widget: компонет, видимость которого необходимо обеспечить.
        """
        w = widget
        isWidget = isinstance(w, QtGui.QWidget)
        p = w.parent() if isWidget else None
        while isWidget and w != self:
            if p and hasattr(p, 'parent'):
                g = p.parent() if callable(p.parent) else p.parent
            else:
                g = None
            if isinstance(g, QtGui.QTabWidget):
                g.setCurrentIndex(g.indexOf(w))
            w = p
            p = g

    def setFocusToWidget(self, widget, row=None, column=None):
        if widget is not None:
            self.setWidgetVisible(widget)
            if widget.hasFocus():
                widget.clearFocus()
            widget.setFocus(Qt.ShortcutFocusReason)
            widget.update()
            if isinstance(widget, QtGui.QTableView) and isinstance(row, int) and isinstance(column, int) and widget.model():
                widget.setCurrentIndex(widget.model().index(row, column))

    def checkUpdateMessage(self, message, edtBegDate, widget, date, row=None, column=None):
        res = QtGui.QMessageBox.warning( self,
                                         u'Внимание!',
                                         message,
                                         QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel,
                                         QtGui.QMessageBox.Cancel)
        if res == QtGui.QMessageBox.Ok:
            if not date.isNull():
                edtBegDate.setDate(date)
            else:
                self.setFocusToWidget(widget, row, column)
            return False
        else:
            # TODO: skkachaev: А не True ли тут должно возвращаться?
            self.setFocusToWidget(widget, row, column)
            return False
        return True

    def checkValueMessage(
            self, message, skipable, widget, row=None, column=None, detailWidget=None, callback=None, btnOkName=None
    ):
        if btnOkName is None:
            buttons = QtGui.QMessageBox.Ok
            if skipable:
                buttons = buttons | QtGui.QMessageBox.Ignore
            res = QtGui.QMessageBox.warning(self, u'Внимание!', message, buttons, QtGui.QMessageBox.Ok)
            if res == QtGui.QMessageBox.Ok:
                callback and callback(False)
                self.setFocusToWidget(widget, row, column)
                if detailWidget:
                    self.setFocusToWidget(detailWidget, row, column)
                return False
            callback and callback(True)
            return True
        else:
            messageBox = QtGui.QMessageBox()
            messageBox.setWindowTitle(u'Внимание!')
            messageBox.setText(message)
            messageBox.addButton(QtGui.QPushButton(btnOkName), QtGui.QMessageBox.ActionRole)
            if skipable:
                messageBox.addButton(QtGui.QPushButton(u'Отмена'), QtGui.QMessageBox.ActionRole)
            res = messageBox.exec_()
            if res == 0:
                callback and callback(False)
                self.setFocusToWidget(widget, row, column)
                if detailWidget:
                    self.setFocusToWidget(detailWidget, row, column)
                return False
            callback and callback(True)
            return True

    def checkInputMessage(self, message, skipable, widget, row=None, column=None):
        return self.checkValueMessage(u'Необходимо указать %s' % message, skipable, widget, row, column)

    def checkValueMessageIgnoreAll(self, message, skipable, widget, row=None, column=None, detailWidget=None):
        messageBox = QtGui.QMessageBox()
        messageBox.setWindowTitle(u'Внимание!')
        messageBox.setText(message)
        messageBox.addButton(QtGui.QPushButton(u'ОК'), QtGui.QMessageBox.ActionRole)
        if skipable:
            messageBox.addButton(QtGui.QPushButton(u'Игнорировать'), QtGui.QMessageBox.ActionRole)
            messageBox.addButton(QtGui.QPushButton(u'Игнорировать все'), QtGui.QMessageBox.ActionRole)
        res = messageBox.exec_()
        if res == 0:
            self.setFocusToWidget(widget, row, column)
            if detailWidget:
                self.setFocusToWidget(detailWidget, row, column)
        return res

    def canClose(self):
        if self.isDirty():
            res = QtGui.QMessageBox.warning( self,
                                      u'Внимание!',
                                      u'Данные были изменены.\nВыход без сохранения?',
                                      QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel,
                                      QtGui.QMessageBox.Cancel)
            if res != QtGui.QMessageBox.Yes:
                return False
        if hasattr(QtGui.qApp, 'barCodethread'):
            QtGui.qApp.barCodethread.busyByEvent = False

        return True

    def done(self, result):
        if self.saveData() if result>0 else self.canClose():
            self.saveDialogPreferences()
            QtGui.QDialog.done(self, result)

    def setVisible(self, visible):
        QtGui.QDialog.setVisible(self, visible)
        if visible:
            widget = self.focusWidget()
            if widget is not None:
                widget.clearFocus()
                widget.setFocus(Qt.ShortcutFocusReason)
                widget.update()

    def closeEvent(self, event):
        self.saveDialogPreferences()
        if self.isVisible():
            self.setResult(-1)
            self.done(QtGui.QDialog.Rejected)
            if self.result() == QtGui.QDialog.Rejected:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def event(self, event):
       if event.type() == QEvent.StatusTip and self.statusBar:
           self.statusBar.showMessage(event.tip())
           event.accept()
           return True
       else:
           return QtGui.QDialog.event(self, event)

    def on_textEditChanged(self):
        self.setIsDirty()

    def on_lineEditChanged(self, text):
        self.setIsDirty()

    def on_dateEditChanged(self, date):
        self.setIsDirty()

    def on_comboBoxChanged(self, index):
        self.setIsDirty()

    def on_checkBoxChanged(self, state):
        self.setIsDirty()

    def on_spinBoxChanged(self, value):
        self.setIsDirty()

    def on_abstractdataModelDataChanged(self, topLeft,  bottomRight):
        self.setIsDirty()

    def setupDirtyCatherForObject(self, obj, exclude):
        if obj in exclude:
            return
        for child in filter(lambda x: isinstance(x, (
                CDateEdit, QtGui.QLineEdit, QtGui.QTextEdit, QtGui.QDateEdit, QtGui.QComboBox, QtGui.QCheckBox,
                QtGui.QSpinBox, QAbstractItemModel)), obj.findChildren(QtCore.QObject)):
            if child in exclude:
                pass
            elif isinstance(child, CDateEdit):
                self.connect(child, SIGNAL('dateChanged(QDate)'), self.on_dateEditChanged)
            elif isinstance(child, QtGui.QLineEdit):
                self.connect(child, SIGNAL('textChanged(QString)'), self.on_lineEditChanged)
            elif isinstance(child, QtGui.QTextEdit):
                self.connect(child, SIGNAL('textChanged()'), self.on_textEditChanged)
            elif isinstance(child, QtGui.QDateEdit):
                self.connect(child, SIGNAL('dateChanged(QDate)'), self.on_dateEditChanged)
            elif isinstance(child, QtGui.QComboBox):
                self.connect(child, SIGNAL('currentIndexChanged(int)'), self.on_comboBoxChanged)
            elif isinstance(child, QtGui.QCheckBox):
                self.connect(child, SIGNAL('stateChanged(int)'), self.on_checkBoxChanged)
            elif isinstance(child, QtGui.QSpinBox):
                self.connect(child, SIGNAL('valueChanged(int)'), self.on_spinBoxChanged)
            elif isinstance(child, QAbstractItemModel):
                self.connect(child, SIGNAL('dataChanged(QModelIndex, QModelIndex)'), self.on_abstractdataModelDataChanged)
                self.connect(child, SIGNAL('rowsInserted(QModelIndex, int, int)'), self.on_abstractdataModelDataChanged)
                self.connect(child, SIGNAL('rowsMoved(QModelIndex, int, int, QModelIndex, int)'), self.on_abstractdataModelDataChanged)
                self.connect(child, SIGNAL('rowsRemoved(QModelIndex, int, int)'), self.on_abstractdataModelDataChanged)
            # else:
            #     self.setupDirtyCatherForObject(child, exclude)

    def setupDirtyCather(self, exclude=None):
        if not exclude:
            exclude = {}
        self.setupDirtyCatherForObject(self, exclude)

    def exec_(self):
        self.loadDialogPreferences()
        self.connect(QtGui.qApp.db, SIGNAL('disconnected()'), self.reject)
        result = super(CDialogBase, self).exec_()
        self.disconnect(QtGui.qApp.db, SIGNAL('disconnected()'), self.reject)
        return result
