# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\DataCheck\LocalLogicalControlDiagnosisLUD.ui'
#
# Created: Fri Jun 15 12:16:13 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_LocalLogicalControlDiagnosisLUD(object):
    def setupUi(self, LocalLogicalControlDiagnosisLUD):
        LocalLogicalControlDiagnosisLUD.setObjectName(_fromUtf8("LocalLogicalControlDiagnosisLUD"))
        LocalLogicalControlDiagnosisLUD.resize(465, 551)
        self.gridLayout = QtGui.QGridLayout(LocalLogicalControlDiagnosisLUD)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkMKB = QtGui.QCheckBox(LocalLogicalControlDiagnosisLUD)
        self.chkMKB.setObjectName(_fromUtf8("chkMKB"))
        self.gridLayout.addWidget(self.chkMKB, 0, 0, 1, 1)
        self.edtMKBFrom = QtGui.QLineEdit(LocalLogicalControlDiagnosisLUD)
        self.edtMKBFrom.setEnabled(False)
        self.edtMKBFrom.setMaximumSize(QtCore.QSize(50, 16777215))
        self.edtMKBFrom.setObjectName(_fromUtf8("edtMKBFrom"))
        self.gridLayout.addWidget(self.edtMKBFrom, 0, 1, 1, 1)
        self.edtMKBTo = QtGui.QLineEdit(LocalLogicalControlDiagnosisLUD)
        self.edtMKBTo.setEnabled(False)
        self.edtMKBTo.setMaximumSize(QtCore.QSize(50, 16777215))
        self.edtMKBTo.setObjectName(_fromUtf8("edtMKBTo"))
        self.gridLayout.addWidget(self.edtMKBTo, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(177, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.splitter = QtGui.QSplitter(LocalLogicalControlDiagnosisLUD)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.txtClientInfoControlLocalLUD = QtGui.QTextBrowser(self.splitter)
        self.txtClientInfoControlLocalLUD.setObjectName(_fromUtf8("txtClientInfoControlLocalLUD"))
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.prbControlDiagnosisLocalLUD = CProgressBar(self.layoutWidget)
        self.prbControlDiagnosisLocalLUD.setObjectName(_fromUtf8("prbControlDiagnosisLocalLUD"))
        self.verticalLayout.addWidget(self.prbControlDiagnosisLocalLUD)
        self.listResultControlDiagnosisLocalLUD = QtGui.QListWidget(self.layoutWidget)
        self.listResultControlDiagnosisLocalLUD.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.EditKeyPressed|QtGui.QAbstractItemView.SelectedClicked)
        self.listResultControlDiagnosisLocalLUD.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listResultControlDiagnosisLocalLUD.setFlow(QtGui.QListView.TopToBottom)
        self.listResultControlDiagnosisLocalLUD.setObjectName(_fromUtf8("listResultControlDiagnosisLocalLUD"))
        self.verticalLayout.addWidget(self.listResultControlDiagnosisLocalLUD)
        self.gridLayout.addWidget(self.splitter, 1, 0, 1, 4)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.btnStartControlLocalLUD = QtGui.QPushButton(LocalLogicalControlDiagnosisLUD)
        self.btnStartControlLocalLUD.setMinimumSize(QtCore.QSize(100, 0))
        self.btnStartControlLocalLUD.setAutoDefault(True)
        self.btnStartControlLocalLUD.setObjectName(_fromUtf8("btnStartControlLocalLUD"))
        self.horizontalLayout_2.addWidget(self.btnStartControlLocalLUD)
        self.lblCountLineLocalLUD = QtGui.QLabel(LocalLogicalControlDiagnosisLUD)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblCountLineLocalLUD.sizePolicy().hasHeightForWidth())
        self.lblCountLineLocalLUD.setSizePolicy(sizePolicy)
        self.lblCountLineLocalLUD.setText(_fromUtf8(""))
        self.lblCountLineLocalLUD.setAlignment(QtCore.Qt.AlignCenter)
        self.lblCountLineLocalLUD.setObjectName(_fromUtf8("lblCountLineLocalLUD"))
        self.horizontalLayout_2.addWidget(self.lblCountLineLocalLUD)
        self.btnCorrectControlLocalLUD = QtGui.QPushButton(LocalLogicalControlDiagnosisLUD)
        self.btnCorrectControlLocalLUD.setEnabled(False)
        self.btnCorrectControlLocalLUD.setMinimumSize(QtCore.QSize(100, 0))
        self.btnCorrectControlLocalLUD.setObjectName(_fromUtf8("btnCorrectControlLocalLUD"))
        self.horizontalLayout_2.addWidget(self.btnCorrectControlLocalLUD)
        self.btnEndControlLocalLUD = QtGui.QPushButton(LocalLogicalControlDiagnosisLUD)
        self.btnEndControlLocalLUD.setMinimumSize(QtCore.QSize(100, 0))
        self.btnEndControlLocalLUD.setAutoDefault(True)
        self.btnEndControlLocalLUD.setObjectName(_fromUtf8("btnEndControlLocalLUD"))
        self.horizontalLayout_2.addWidget(self.btnEndControlLocalLUD)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 4)

        self.retranslateUi(LocalLogicalControlDiagnosisLUD)
        QtCore.QMetaObject.connectSlotsByName(LocalLogicalControlDiagnosisLUD)

    def retranslateUi(self, LocalLogicalControlDiagnosisLUD):
        LocalLogicalControlDiagnosisLUD.setWindowTitle(QtGui.QApplication.translate("LocalLogicalControlDiagnosisLUD", "Оперативный логический контроль ЛУДа", None, QtGui.QApplication.UnicodeUTF8))
        self.chkMKB.setText(QtGui.QApplication.translate("LocalLogicalControlDiagnosisLUD", "Коды диагнозов по &МКБ", None, QtGui.QApplication.UnicodeUTF8))
        self.edtMKBFrom.setInputMask(QtGui.QApplication.translate("LocalLogicalControlDiagnosisLUD", "a00.00; ", None, QtGui.QApplication.UnicodeUTF8))
        self.edtMKBFrom.setText(QtGui.QApplication.translate("LocalLogicalControlDiagnosisLUD", "A.", None, QtGui.QApplication.UnicodeUTF8))
        self.edtMKBTo.setInputMask(QtGui.QApplication.translate("LocalLogicalControlDiagnosisLUD", "a00.00; ", None, QtGui.QApplication.UnicodeUTF8))
        self.edtMKBTo.setText(QtGui.QApplication.translate("LocalLogicalControlDiagnosisLUD", "T99.9", None, QtGui.QApplication.UnicodeUTF8))
        self.prbControlDiagnosisLocalLUD.setFormat(QtGui.QApplication.translate("LocalLogicalControlDiagnosisLUD", "%p%", None, QtGui.QApplication.UnicodeUTF8))
        self.btnStartControlLocalLUD.setText(QtGui.QApplication.translate("LocalLogicalControlDiagnosisLUD", "начать выполнение", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCorrectControlLocalLUD.setText(QtGui.QApplication.translate("LocalLogicalControlDiagnosisLUD", "исправить", None, QtGui.QApplication.UnicodeUTF8))
        self.btnEndControlLocalLUD.setText(QtGui.QApplication.translate("LocalLogicalControlDiagnosisLUD", "прервать", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    LocalLogicalControlDiagnosisLUD = QtGui.QDialog()
    ui = Ui_LocalLogicalControlDiagnosisLUD()
    ui.setupUi(LocalLogicalControlDiagnosisLUD)
    LocalLogicalControlDiagnosisLUD.show()
    sys.exit(app.exec_())

