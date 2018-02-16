# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Blank\BlankComboBoxPopup.ui'
#
# Created: Fri Jun 15 12:17:17 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_BlankComboBoxPopup(object):
    def setupUi(self, BlankComboBoxPopup):
        BlankComboBoxPopup.setObjectName(_fromUtf8("BlankComboBoxPopup"))
        BlankComboBoxPopup.resize(282, 207)
        self.gridLayout = QtGui.QGridLayout(BlankComboBoxPopup)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblBlank = CTableView(BlankComboBoxPopup)
        self.tblBlank.setObjectName(_fromUtf8("tblBlank"))
        self.gridLayout.addWidget(self.tblBlank, 0, 0, 1, 1)

        self.retranslateUi(BlankComboBoxPopup)
        QtCore.QMetaObject.connectSlotsByName(BlankComboBoxPopup)

    def retranslateUi(self, BlankComboBoxPopup):
        BlankComboBoxPopup.setWindowTitle(QtGui.QApplication.translate("BlankComboBoxPopup", "Form", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    BlankComboBoxPopup = QtGui.QWidget()
    ui = Ui_BlankComboBoxPopup()
    ui.setupUi(BlankComboBoxPopup)
    BlankComboBoxPopup.show()
    sys.exit(app.exec_())

