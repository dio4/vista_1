# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Orgs\SuiteReagentComboBoxPopup.ui'
#
# Created: Fri Jun 15 12:17:39 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SuiteReagentPopupForm(object):
    def setupUi(self, SuiteReagentPopupForm):
        SuiteReagentPopupForm.setObjectName(_fromUtf8("SuiteReagentPopupForm"))
        SuiteReagentPopupForm.resize(497, 315)
        self.verticalLayout = QtGui.QVBoxLayout(SuiteReagentPopupForm)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(SuiteReagentPopupForm)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabSuiteReagent = QtGui.QWidget()
        self.tabSuiteReagent.setObjectName(_fromUtf8("tabSuiteReagent"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tabSuiteReagent)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tblSuiteReagent = CTableView(self.tabSuiteReagent)
        self.tblSuiteReagent.setObjectName(_fromUtf8("tblSuiteReagent"))
        self.verticalLayout_2.addWidget(self.tblSuiteReagent)
        self.tabWidget.addTab(self.tabSuiteReagent, _fromUtf8(""))
        self.tabFind = QtGui.QWidget()
        self.tabFind.setObjectName(_fromUtf8("tabFind"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tabFind)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.chkOnlyByTest = QtGui.QCheckBox(self.tabFind)
        self.chkOnlyByTest.setChecked(True)
        self.chkOnlyByTest.setObjectName(_fromUtf8("chkOnlyByTest"))
        self.verticalLayout_3.addWidget(self.chkOnlyByTest)
        self.chkNotOverdue = QtGui.QCheckBox(self.tabFind)
        self.chkNotOverdue.setChecked(True)
        self.chkNotOverdue.setObjectName(_fromUtf8("chkNotOverdue"))
        self.verticalLayout_3.addWidget(self.chkNotOverdue)
        self.chkStartOperation = QtGui.QCheckBox(self.tabFind)
        self.chkStartOperation.setChecked(True)
        self.chkStartOperation.setObjectName(_fromUtf8("chkStartOperation"))
        self.verticalLayout_3.addWidget(self.chkStartOperation)
        self.chkNotOverLimit = QtGui.QCheckBox(self.tabFind)
        self.chkNotOverLimit.setChecked(True)
        self.chkNotOverLimit.setObjectName(_fromUtf8("chkNotOverLimit"))
        self.verticalLayout_3.addWidget(self.chkNotOverLimit)
        spacerItem = QtGui.QSpacerItem(20, 123, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.buttonBox = CApplyResetDialogButtonBox(self.tabFind)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Reset)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)
        self.tabWidget.addTab(self.tabFind, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi(SuiteReagentPopupForm)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(SuiteReagentPopupForm)

    def retranslateUi(self, SuiteReagentPopupForm):
        SuiteReagentPopupForm.setWindowTitle(QtGui.QApplication.translate("SuiteReagentPopupForm", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSuiteReagent), QtGui.QApplication.translate("SuiteReagentPopupForm", "&Наборы", None, QtGui.QApplication.UnicodeUTF8))
        self.chkOnlyByTest.setText(QtGui.QApplication.translate("SuiteReagentPopupForm", "Только наборы относяшиеся к тесту", None, QtGui.QApplication.UnicodeUTF8))
        self.chkNotOverdue.setText(QtGui.QApplication.translate("SuiteReagentPopupForm", "Не просрочены", None, QtGui.QApplication.UnicodeUTF8))
        self.chkStartOperation.setText(QtGui.QApplication.translate("SuiteReagentPopupForm", "Введены в работу", None, QtGui.QApplication.UnicodeUTF8))
        self.chkNotOverLimit.setText(QtGui.QApplication.translate("SuiteReagentPopupForm", "Не превышен плановое количество", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFind), QtGui.QApplication.translate("SuiteReagentPopupForm", "&Поиск", None, QtGui.QApplication.UnicodeUTF8))

from library.DialogButtonBox import CApplyResetDialogButtonBox
from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SuiteReagentPopupForm = QtGui.QWidget()
    ui = Ui_SuiteReagentPopupForm()
    ui.setupUi(SuiteReagentPopupForm)
    SuiteReagentPopupForm.show()
    sys.exit(app.exec_())

