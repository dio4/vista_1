# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\Export131_Wizard_1.ui'
#
# Created: Fri Jun 15 12:15:07 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Export131_Wizard_1(object):
    def setupUi(self, Export131_Wizard_1):
        Export131_Wizard_1.setObjectName(_fromUtf8("Export131_Wizard_1"))
        Export131_Wizard_1.resize(473, 394)
        self.gridlayout = QtGui.QGridLayout(Export131_Wizard_1)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(Export131_Wizard_1)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.dateEdit_1 = QtGui.QDateEdit(Export131_Wizard_1)
        self.dateEdit_1.setCalendarPopup(True)
        self.dateEdit_1.setDate(QtCore.QDate(2008, 1, 1))
        self.dateEdit_1.setObjectName(_fromUtf8("dateEdit_1"))
        self.hboxlayout.addWidget(self.dateEdit_1)
        self.label_2 = QtGui.QLabel(Export131_Wizard_1)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.hboxlayout.addWidget(self.label_2)
        self.dateEdit_2 = QtGui.QDateEdit(Export131_Wizard_1)
        self.dateEdit_2.setCalendarPopup(True)
        self.dateEdit_2.setDate(QtCore.QDate(2008, 12, 31))
        self.dateEdit_2.setObjectName(_fromUtf8("dateEdit_2"))
        self.hboxlayout.addWidget(self.dateEdit_2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.gridlayout.addLayout(self.hboxlayout, 0, 0, 1, 1)
        self.checkFinished = QtGui.QCheckBox(Export131_Wizard_1)
        self.checkFinished.setChecked(True)
        self.checkFinished.setObjectName(_fromUtf8("checkFinished"))
        self.gridlayout.addWidget(self.checkFinished, 1, 0, 1, 1)
        self.checkPayed = QtGui.QCheckBox(Export131_Wizard_1)
        self.checkPayed.setChecked(True)
        self.checkPayed.setObjectName(_fromUtf8("checkPayed"))
        self.gridlayout.addWidget(self.checkPayed, 2, 0, 1, 1)
        self.checkRAR = QtGui.QCheckBox(Export131_Wizard_1)
        self.checkRAR.setChecked(True)
        self.checkRAR.setObjectName(_fromUtf8("checkRAR"))
        self.gridlayout.addWidget(self.checkRAR, 3, 0, 1, 1)
        self.splitter = QtGui.QSplitter(Export131_Wizard_1)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tblEventType = CRBListBox(self.splitter)
        self.tblEventType.setObjectName(_fromUtf8("tblEventType"))
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.vboxlayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.progressBar = CProgressBar(self.layoutWidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.vboxlayout.addWidget(self.progressBar)
        self.tableWidget = QtGui.QTableWidget(self.layoutWidget)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.vboxlayout.addWidget(self.tableWidget)
        self.gridlayout.addWidget(self.splitter, 6, 0, 1, 1)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.btnExport = QtGui.QPushButton(Export131_Wizard_1)
        self.btnExport.setObjectName(_fromUtf8("btnExport"))
        self.hboxlayout1.addWidget(self.btnExport)
        self.btnClose = QtGui.QPushButton(Export131_Wizard_1)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.hboxlayout1.addWidget(self.btnClose)
        self.gridlayout.addLayout(self.hboxlayout1, 7, 0, 1, 1)
        self.checkXML = QtGui.QCheckBox(Export131_Wizard_1)
        self.checkXML.setObjectName(_fromUtf8("checkXML"))
        self.gridlayout.addWidget(self.checkXML, 4, 0, 1, 1)
        self.chkUseDefaultAnalysisValue = QtGui.QCheckBox(Export131_Wizard_1)
        self.chkUseDefaultAnalysisValue.setObjectName(_fromUtf8("chkUseDefaultAnalysisValue"))
        self.gridlayout.addWidget(self.chkUseDefaultAnalysisValue, 5, 0, 1, 1)

        self.retranslateUi(Export131_Wizard_1)
        QtCore.QMetaObject.connectSlotsByName(Export131_Wizard_1)
        Export131_Wizard_1.setTabOrder(self.dateEdit_1, self.dateEdit_2)
        Export131_Wizard_1.setTabOrder(self.dateEdit_2, self.checkFinished)
        Export131_Wizard_1.setTabOrder(self.checkFinished, self.checkPayed)
        Export131_Wizard_1.setTabOrder(self.checkPayed, self.checkRAR)
        Export131_Wizard_1.setTabOrder(self.checkRAR, self.tblEventType)
        Export131_Wizard_1.setTabOrder(self.tblEventType, self.tableWidget)
        Export131_Wizard_1.setTabOrder(self.tableWidget, self.btnExport)
        Export131_Wizard_1.setTabOrder(self.btnExport, self.btnClose)

    def retranslateUi(self, Export131_Wizard_1):
        Export131_Wizard_1.setWindowTitle(QtGui.QApplication.translate("Export131_Wizard_1", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Export131_Wizard_1", "с", None, QtGui.QApplication.UnicodeUTF8))
        self.dateEdit_1.setDisplayFormat(QtGui.QApplication.translate("Export131_Wizard_1", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Export131_Wizard_1", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.dateEdit_2.setDisplayFormat(QtGui.QApplication.translate("Export131_Wizard_1", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.checkFinished.setText(QtGui.QApplication.translate("Export131_Wizard_1", "только законченные", None, QtGui.QApplication.UnicodeUTF8))
        self.checkPayed.setText(QtGui.QApplication.translate("Export131_Wizard_1", "только подтверждённые", None, QtGui.QApplication.UnicodeUTF8))
        self.checkRAR.setText(QtGui.QApplication.translate("Export131_Wizard_1", "архивировать в RAR", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExport.setText(QtGui.QApplication.translate("Export131_Wizard_1", "начать экспорт", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("Export131_Wizard_1", "прервать", None, QtGui.QApplication.UnicodeUTF8))
        self.checkXML.setText(QtGui.QApplication.translate("Export131_Wizard_1", "экспорт в формате XML", None, QtGui.QApplication.UnicodeUTF8))
        self.chkUseDefaultAnalysisValue.setText(QtGui.QApplication.translate("Export131_Wizard_1", "использовать \"норму\" по умолчанию для отсутствующих результатов", None, QtGui.QApplication.UnicodeUTF8))

from library.RBListBox import CRBListBox
from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Export131_Wizard_1 = QtGui.QDialog()
    ui = Ui_Export131_Wizard_1()
    ui.setupUi(Export131_Wizard_1)
    Export131_Wizard_1.show()
    sys.exit(app.exec_())

