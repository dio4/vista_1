# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.TableView import CTableView
from library.Utils import forceString, toVariant


class CJobTicketsView(CTableView):

    def __init__(self, parent):
        CTableView.__init__(self, parent)
        self.setItemDelegate(CJobTicketsItemDelegate(self))
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setEditTriggers(QtGui.QAbstractItemView.AnyKeyPressed | QtGui.QAbstractItemView.EditKeyPressed | QtGui.QAbstractItemView.SelectedClicked | QtGui.QAbstractItemView.DoubleClicked)

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            event.accept()
            self.update(self.currentIndex())
        else:
            CTableView.keyPressEvent(self, event)


class CJobTicketsItemDelegate(QtGui.QItemDelegate):

    def __init__(self, parent):
        super(CJobTicketsItemDelegate, self).__init__(parent)

    def emitCommitDataAndClose(self, editor, hint=QtGui.QAbstractItemDelegate.NoHint):
        self.emit(QtCore.SIGNAL('commitData(QWidget *)'), editor)
        self.emit(QtCore.SIGNAL('closeEditor(QWidget *,QAbstractItemDelegate::EndEditHint)'), editor, hint)

    def createEditor(self, parent, option, index):
        editor = QtGui.QLineEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        editor.setText(forceString(model.data(index, QtCore.Qt.DisplayRole)))

    def setModelData(self, editor, model, index):
        model.setData(index, toVariant(editor.text()))
        model.invalidateRecordsCache()
        model.reset()

    def eventFilter(self, editor, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                if editor is not None:
                    self.emitCommitDataAndClose(editor)
                return True

            elif key == QtCore.Qt.Key_Tab:
                if editor is not None:
                    self.emitCommitDataAndClose(editor)
                self.parent().focusNextChild()
                return True

            elif key == QtCore.Qt.Key_Backtab:
                if editor is not None:
                    self.emitCommitDataAndClose(editor)
                self.parent().focusPreviousChild()
                return True

        return super(CJobTicketsItemDelegate, self).eventFilter(editor, event)
