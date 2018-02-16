# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\F003\MenuContent.ui'
#
# Created: Fri Jun 15 12:16:43 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MenuContent(object):
    def setupUi(self, MenuContent):
        MenuContent.setObjectName(_fromUtf8("MenuContent"))
        MenuContent.resize(540, 307)
        MenuContent.setSizeGripEnabled(False)
        self.gridLayout = QtGui.QGridLayout(MenuContent)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCode = QtGui.QLabel(MenuContent)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLabel(MenuContent)
        self.edtCode.setText(_fromUtf8(""))
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(422, 13, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.lblName = QtGui.QLabel(MenuContent)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 1, 0, 1, 1)
        self.edtName = QtGui.QLabel(MenuContent)
        self.edtName.setText(_fromUtf8(""))
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 1, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(422, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 2, 1, 1)
        self.tblMenuContent = CInDocTableView(MenuContent)
        self.tblMenuContent.setObjectName(_fromUtf8("tblMenuContent"))
        self.gridLayout.addWidget(self.tblMenuContent, 2, 0, 1, 3)
        spacerItem2 = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 3, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(MenuContent)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 3)

        self.retranslateUi(MenuContent)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), MenuContent.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), MenuContent.reject)
        QtCore.QMetaObject.connectSlotsByName(MenuContent)

    def retranslateUi(self, MenuContent):
        MenuContent.setWindowTitle(QtGui.QApplication.translate("MenuContent", "Шаблон питания", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("MenuContent", "Код: ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("MenuContent", "Наименование: ", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MenuContent = QtGui.QDialog()
    ui = Ui_MenuContent()
    ui.setupUi(MenuContent)
    MenuContent.show()
    sys.exit(app.exec_())

