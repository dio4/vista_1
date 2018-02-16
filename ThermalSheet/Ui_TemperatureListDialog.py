# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\ThermalSheet\TemperatureListDialog.ui'
#
# Created: Fri Jun 15 12:17:35 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TemperatureListDialog(object):
    def setupUi(self, TemperatureListDialog):
        TemperatureListDialog.setObjectName(_fromUtf8("TemperatureListDialog"))
        TemperatureListDialog.resize(681, 796)
        self.gridLayout = QtGui.QGridLayout(TemperatureListDialog)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidget = QtGui.QTabWidget(TemperatureListDialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabGraphs = QtGui.QWidget()
        self.tabGraphs.setObjectName(_fromUtf8("tabGraphs"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tabGraphs)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.scrollArea = QtGui.QScrollArea(self.tabGraphs)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 671, 735))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabGraphs, _fromUtf8(""))
        self.tabTable = QtGui.QWidget()
        self.tabTable.setObjectName(_fromUtf8("tabTable"))
        self.gridLayout_3 = QtGui.QGridLayout(self.tabTable)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.tblTemperatureSheet = CTableView(self.tabTable)
        self.tblTemperatureSheet.setObjectName(_fromUtf8("tblTemperatureSheet"))
        self.gridLayout_3.addWidget(self.tblTemperatureSheet, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabTable, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 4)
        spacerItem = QtGui.QSpacerItem(418, 24, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.btnPrint = QtGui.QPushButton(TemperatureListDialog)
        self.btnPrint.setObjectName(_fromUtf8("btnPrint"))
        self.gridLayout.addWidget(self.btnPrint, 1, 1, 1, 1)
        self.btnRetry = QtGui.QPushButton(TemperatureListDialog)
        self.btnRetry.setObjectName(_fromUtf8("btnRetry"))
        self.gridLayout.addWidget(self.btnRetry, 1, 2, 1, 1)
        self.btnClose = QtGui.QPushButton(TemperatureListDialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 1, 3, 1, 1)

        self.retranslateUi(TemperatureListDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(TemperatureListDialog)
        TemperatureListDialog.setTabOrder(self.scrollArea, self.btnClose)
        TemperatureListDialog.setTabOrder(self.btnClose, self.btnRetry)
        TemperatureListDialog.setTabOrder(self.btnRetry, self.btnPrint)

    def retranslateUi(self, TemperatureListDialog):
        TemperatureListDialog.setWindowTitle(QtGui.QApplication.translate("TemperatureListDialog", "Температурный лист", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabGraphs), QtGui.QApplication.translate("TemperatureListDialog", "Графики", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabTable), QtGui.QApplication.translate("TemperatureListDialog", "Таблица", None, QtGui.QApplication.UnicodeUTF8))
        self.btnPrint.setText(QtGui.QApplication.translate("TemperatureListDialog", "Печать", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRetry.setText(QtGui.QApplication.translate("TemperatureListDialog", "Повторить", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("TemperatureListDialog", "Отмена", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TemperatureListDialog = QtGui.QDialog()
    ui = Ui_TemperatureListDialog()
    ui.setupUi(TemperatureListDialog)
    TemperatureListDialog.show()
    sys.exit(app.exec_())

