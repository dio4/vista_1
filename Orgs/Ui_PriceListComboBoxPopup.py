# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Orgs\PriceListComboBoxPopup.ui'
#
# Created: Fri Jun 15 12:17:08 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PriceListComboBoxPopup(object):
    def setupUi(self, PriceListComboBoxPopup):
        PriceListComboBoxPopup.setObjectName(_fromUtf8("PriceListComboBoxPopup"))
        PriceListComboBoxPopup.resize(400, 272)
        self.gridLayout = QtGui.QGridLayout(PriceListComboBoxPopup)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblPriceList = CTableView(PriceListComboBoxPopup)
        self.tblPriceList.setObjectName(_fromUtf8("tblPriceList"))
        self.gridLayout.addWidget(self.tblPriceList, 0, 0, 1, 1)

        self.retranslateUi(PriceListComboBoxPopup)
        QtCore.QMetaObject.connectSlotsByName(PriceListComboBoxPopup)

    def retranslateUi(self, PriceListComboBoxPopup):
        PriceListComboBoxPopup.setWindowTitle(QtGui.QApplication.translate("PriceListComboBoxPopup", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    PriceListComboBoxPopup = QtGui.QDialog()
    ui = Ui_PriceListComboBoxPopup()
    ui.setupUi(PriceListComboBoxPopup)
    PriceListComboBoxPopup.show()
    sys.exit(app.exec_())

