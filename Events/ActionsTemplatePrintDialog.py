# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from Ui_ActionsTemplatePrintDialog import Ui_ActionsTemplatePrintDialog
from library.ActionsTemplatePrint import CActionTemplatePrintTableModel


class CActionTemplatePrintWidget(QtGui.QDialog, Ui_ActionsTemplatePrintDialog):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.btnPrint = QtGui.QPushButton(u'Печать')
        self.btnPrint.clicked.connect(self.on_btnPrint_clicked)
        self.buttonBox.addButton(self.btnPrint, QtGui.QDialogButtonBox.AcceptRole)
        self.model = CActionTemplatePrintTableModel(self)
        self.tblTemplate.setModel(self.model)

    def setItems(self, items, dirty=False, lazy=False):
        self.model.setItems(items, dirty, lazy)
        self.model.dataChanged.connect(self.on_model_dataChanged)

    def on_model_dataChanged(self, index1, index2):
        self.btnPrint.setEnabled(self.model.dataIsValid)

    def printOnly(self):
        self.on_btnPrint_clicked()

    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        result = []
        for item in self.model._items:
            if item['print']:
                for row, dateTime in item['actionData']:
                    result.append((item['templateId'], row, dateTime))

        def sortByDateTime(inn):
            return inn[2]

        result = sorted(result, key=sortByDateTime)
        self.emit(QtCore.SIGNAL('printActionTemplateList'), result)
