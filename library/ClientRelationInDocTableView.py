# -*- coding: utf-8 -*-
import Registry
from Users.Rights import *
from library.InDocTable import CInDocTableView
from library.Utils import *


class CClientRelationInDocTableView(CInDocTableView):
    def __init__(self, parent):
        CInDocTableView.__init__(self, parent)
        self.__actRelativeClientEdit = None
        self.horizontalHeader().setStretchLastSection(False)

    def addRelativeClientEdit(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actRelativeClientEdit = QtGui.QAction(u'Регистрационная карточка связанного пациента', self)
        self.__actRelativeClientEdit.setObjectName('actRelativeClientEdit')
        self._popupMenu.addAction(self.__actRelativeClientEdit)
        self.connect(self.__actRelativeClientEdit, QtCore.SIGNAL('triggered()'), self.showRelativeClientEdit)

    def showRelativeClientEdit(self):
        row = self.currentIndex().row()
        items = self.model().items()

        if isinstance(self.model(), Registry.ClientEditDialog.CDirectRelationsModel):
            value = items[row].value('relative_id') if row < len(items) else None
        else:
            value = items[row].value('client_id') if row < len(items) else None

        if value and value.isValid() and QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteRegistry]):
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
            try:
                dialog = Registry.ClientEditDialog.CClientEditDialog(self)
                dialog.tabWidget.setTabEnabled(7, False)  # ;(
                dialog.tabRelations.setEnabled(False)
            finally:
                QtGui.qApp.restoreOverrideCursor()
            dialog.load(value)
            dialog.exec_()

    def createPopupMenu(self, actions=None):
        if not actions:
            actions = []
        self._popupMenu = QtGui.QMenu(self)
        self._popupMenu.setObjectName('popupMenu')
        self.connect(self._popupMenu, QtCore.SIGNAL('aboutToShow()'), self.on_popupMenuShow)
        for action in actions:
            if isinstance(action, QtGui.QAction):
                self._popupMenu.addAction(action)
            elif action == '-':
                self._popupMenu.addSeparator()
        return self._popupMenu

    def on_popupMenuShow(self):
        if self.__actRelativeClientEdit:
            row = self.currentIndex().row()
            rowCount = len(self.model().items())
            column = self.currentIndex().column()
            items = self.model().items()
            value = items[row].value(column) if row < len(items) else None
            self.__actRelativeClientEdit.setEnabled(forceBool(0 <= row < rowCount and (value and value.isValid())))
        self.on_popupMenu_aboutToShow()
