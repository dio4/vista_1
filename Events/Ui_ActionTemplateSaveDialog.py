# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Events\ActionTemplateSaveDialog.ui'
#
# Created: Fri Jun 15 12:15:04 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ActionTemplateSaveDialog(object):
    def setupUi(self, ActionTemplateSaveDialog):
        ActionTemplateSaveDialog.setObjectName(_fromUtf8("ActionTemplateSaveDialog"))
        ActionTemplateSaveDialog.resize(381, 234)
        ActionTemplateSaveDialog.setSizeGripEnabled(False)
        self.gridLayout = QtGui.QGridLayout(ActionTemplateSaveDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.frame = QtGui.QFrame(ActionTemplateSaveDialog)
        self.frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame.setFrameShadow(QtGui.QFrame.Plain)
        self.frame.setLineWidth(0)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtGui.QSplitter(self.frame)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.treeItems = QtGui.QTreeView(self.splitter)
        self.treeItems.setAutoScroll(True)
        self.treeItems.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.treeItems.setObjectName(_fromUtf8("treeItems"))
        self.tblItems = CTableView(self.splitter)
        self.tblItems.setTabKeyNavigation(False)
        self.tblItems.setAlternatingRowColors(True)
        self.tblItems.setObjectName(_fromUtf8("tblItems"))
        self.verticalLayout.addWidget(self.splitter)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ActionTemplateSaveDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(ActionTemplateSaveDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ActionTemplateSaveDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ActionTemplateSaveDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ActionTemplateSaveDialog)

    def retranslateUi(self, ActionTemplateSaveDialog):
        ActionTemplateSaveDialog.setWindowTitle(QtGui.QApplication.translate("ActionTemplateSaveDialog", "Сохранение шаблона действия", None, QtGui.QApplication.UnicodeUTF8))
        self.tblItems.setWhatsThis(QtGui.QApplication.translate("ActionTemplateSaveDialog", "список записей", "ура!", QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ActionTemplateSaveDialog = QtGui.QDialog()
    ui = Ui_ActionTemplateSaveDialog()
    ui.setupUi(ActionTemplateSaveDialog)
    ActionTemplateSaveDialog.show()
    sys.exit(app.exec_())

