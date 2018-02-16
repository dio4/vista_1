# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\library\ModelPatientComboBoxPopup.ui'
#
# Created: Fri Jun 15 12:17:41 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ModelPatientComboBoxPopup(object):
    def setupUi(self, ModelPatientComboBoxPopup):
        ModelPatientComboBoxPopup.setObjectName(_fromUtf8("ModelPatientComboBoxPopup"))
        ModelPatientComboBoxPopup.resize(734, 315)
        self.gridlayout = QtGui.QGridLayout(ModelPatientComboBoxPopup)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.tabWidget = QtGui.QTabWidget(ModelPatientComboBoxPopup)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.South)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabModelPatient = QtGui.QWidget()
        self.tabModelPatient.setObjectName(_fromUtf8("tabModelPatient"))
        self.vboxlayout = QtGui.QVBoxLayout(self.tabModelPatient)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setMargin(4)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.tblModelPatient = CTableView(self.tabModelPatient)
        self.tblModelPatient.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tblModelPatient.setObjectName(_fromUtf8("tblModelPatient"))
        self.vboxlayout.addWidget(self.tblModelPatient)
        self.tabWidget.addTab(self.tabModelPatient, _fromUtf8(""))
        self.tabSearch = QtGui.QWidget()
        self.tabSearch.setObjectName(_fromUtf8("tabSearch"))
        self.gridlayout1 = QtGui.QGridLayout(self.tabSearch)
        self.gridlayout1.setMargin(4)
        self.gridlayout1.setSpacing(4)
        self.gridlayout1.setObjectName(_fromUtf8("gridlayout1"))
        self.buttonBox = QtGui.QDialogButtonBox(self.tabSearch)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout1.addWidget(self.buttonBox, 5, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout1.addItem(spacerItem, 5, 1, 1, 1)
        self.cmbQuoting = CClientQuotingModelPatientComboBox(self.tabSearch)
        self.cmbQuoting.setObjectName(_fromUtf8("cmbQuoting"))
        self.gridlayout1.addWidget(self.cmbQuoting, 0, 1, 1, 2)
        self.label = QtGui.QLabel(self.tabSearch)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout1.addWidget(self.label, 0, 0, 1, 1)
        self.chkPreviousMKB = QtGui.QCheckBox(self.tabSearch)
        self.chkPreviousMKB.setChecked(True)
        self.chkPreviousMKB.setObjectName(_fromUtf8("chkPreviousMKB"))
        self.gridlayout1.addWidget(self.chkPreviousMKB, 2, 1, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 141, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem1, 4, 1, 1, 1)
        self.chkQuotingPatientOnly = QtGui.QCheckBox(self.tabSearch)
        self.chkQuotingPatientOnly.setObjectName(_fromUtf8("chkQuotingPatientOnly"))
        self.gridlayout1.addWidget(self.chkQuotingPatientOnly, 1, 1, 1, 2)
        self.chkQuotingEvent = QtGui.QCheckBox(self.tabSearch)
        self.chkQuotingEvent.setChecked(True)
        self.chkQuotingEvent.setObjectName(_fromUtf8("chkQuotingEvent"))
        self.gridlayout1.addWidget(self.chkQuotingEvent, 3, 1, 1, 2)
        self.tabWidget.addTab(self.tabSearch, _fromUtf8(""))
        self.gridlayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(ModelPatientComboBoxPopup)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ModelPatientComboBoxPopup)
        ModelPatientComboBoxPopup.setTabOrder(self.tabWidget, self.buttonBox)
        ModelPatientComboBoxPopup.setTabOrder(self.buttonBox, self.tblModelPatient)

    def retranslateUi(self, ModelPatientComboBoxPopup):
        ModelPatientComboBoxPopup.setWindowTitle(QtGui.QApplication.translate("ModelPatientComboBoxPopup", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabModelPatient), QtGui.QApplication.translate("ModelPatientComboBoxPopup", "Результат поиска", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ModelPatientComboBoxPopup", "Квота", None, QtGui.QApplication.UnicodeUTF8))
        self.chkPreviousMKB.setText(QtGui.QApplication.translate("ModelPatientComboBoxPopup", "Учитывать предварительный диагноз", None, QtGui.QApplication.UnicodeUTF8))
        self.chkQuotingPatientOnly.setText(QtGui.QApplication.translate("ModelPatientComboBoxPopup", "Учитывать только квоты пациента", None, QtGui.QApplication.UnicodeUTF8))
        self.chkQuotingEvent.setText(QtGui.QApplication.translate("ModelPatientComboBoxPopup", "Учитывать квоту, определенную в Событии", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSearch), QtGui.QApplication.translate("ModelPatientComboBoxPopup", "&Поиск", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView
from Quoting.QuotaTypeComboBox import CClientQuotingModelPatientComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ModelPatientComboBoxPopup = QtGui.QWidget()
    ui = Ui_ModelPatientComboBoxPopup()
    ui.setupUi(ModelPatientComboBoxPopup)
    ModelPatientComboBoxPopup.show()
    sys.exit(app.exec_())

