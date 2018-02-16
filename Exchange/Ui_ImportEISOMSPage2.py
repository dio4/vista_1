# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Exchange\ImportEISOMSPage2.ui'
#
# Created: Fri Jun 15 12:15:19 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImportEISOMSPage2(object):
    def setupUi(self, ImportEISOMSPage2):
        ImportEISOMSPage2.setObjectName(_fromUtf8("ImportEISOMSPage2"))
        ImportEISOMSPage2.resize(410, 300)
        self.gridlayout = QtGui.QGridLayout(ImportEISOMSPage2)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.progressBar = CProgressBar(ImportEISOMSPage2)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridlayout.addWidget(self.progressBar, 0, 0, 1, 4)
        self.lblAcceptedLabel = QtGui.QLabel(ImportEISOMSPage2)
        self.lblAcceptedLabel.setObjectName(_fromUtf8("lblAcceptedLabel"))
        self.gridlayout.addWidget(self.lblAcceptedLabel, 1, 0, 1, 1)
        self.lblAccepted = QtGui.QLabel(ImportEISOMSPage2)
        self.lblAccepted.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblAccepted.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblAccepted.setTextFormat(QtCore.Qt.PlainText)
        self.lblAccepted.setScaledContents(False)
        self.lblAccepted.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblAccepted.setObjectName(_fromUtf8("lblAccepted"))
        self.gridlayout.addWidget(self.lblAccepted, 1, 1, 1, 1)
        self.lblIntegrityErrorLabel = QtGui.QLabel(ImportEISOMSPage2)
        self.lblIntegrityErrorLabel.setObjectName(_fromUtf8("lblIntegrityErrorLabel"))
        self.gridlayout.addWidget(self.lblIntegrityErrorLabel, 1, 2, 1, 1)
        self.lblIntegrityError = QtGui.QLabel(ImportEISOMSPage2)
        self.lblIntegrityError.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblIntegrityError.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblIntegrityError.setTextFormat(QtCore.Qt.PlainText)
        self.lblIntegrityError.setScaledContents(False)
        self.lblIntegrityError.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblIntegrityError.setObjectName(_fromUtf8("lblIntegrityError"))
        self.gridlayout.addWidget(self.lblIntegrityError, 1, 3, 1, 1)
        self.lblRefusedLabel = QtGui.QLabel(ImportEISOMSPage2)
        self.lblRefusedLabel.setObjectName(_fromUtf8("lblRefusedLabel"))
        self.gridlayout.addWidget(self.lblRefusedLabel, 2, 0, 1, 1)
        self.lblRefused = QtGui.QLabel(ImportEISOMSPage2)
        self.lblRefused.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblRefused.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblRefused.setTextFormat(QtCore.Qt.PlainText)
        self.lblRefused.setScaledContents(False)
        self.lblRefused.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblRefused.setObjectName(_fromUtf8("lblRefused"))
        self.gridlayout.addWidget(self.lblRefused, 2, 1, 1, 1)
        self.lblChangeDisabledLabel = QtGui.QLabel(ImportEISOMSPage2)
        self.lblChangeDisabledLabel.setObjectName(_fromUtf8("lblChangeDisabledLabel"))
        self.gridlayout.addWidget(self.lblChangeDisabledLabel, 2, 2, 1, 1)
        self.lblChangeDisabled = QtGui.QLabel(ImportEISOMSPage2)
        self.lblChangeDisabled.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblChangeDisabled.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblChangeDisabled.setTextFormat(QtCore.Qt.PlainText)
        self.lblChangeDisabled.setScaledContents(False)
        self.lblChangeDisabled.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblChangeDisabled.setObjectName(_fromUtf8("lblChangeDisabled"))
        self.gridlayout.addWidget(self.lblChangeDisabled, 2, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(151, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 3, 0, 1, 2)
        self.lblUncheckedLabel = QtGui.QLabel(ImportEISOMSPage2)
        self.lblUncheckedLabel.setObjectName(_fromUtf8("lblUncheckedLabel"))
        self.gridlayout.addWidget(self.lblUncheckedLabel, 3, 2, 1, 1)
        self.lblUnchecked = QtGui.QLabel(ImportEISOMSPage2)
        self.lblUnchecked.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblUnchecked.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblUnchecked.setTextFormat(QtCore.Qt.PlainText)
        self.lblUnchecked.setScaledContents(False)
        self.lblUnchecked.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblUnchecked.setObjectName(_fromUtf8("lblUnchecked"))
        self.gridlayout.addWidget(self.lblUnchecked, 3, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(392, 111, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 4, 0, 1, 4)

        self.retranslateUi(ImportEISOMSPage2)
        QtCore.QMetaObject.connectSlotsByName(ImportEISOMSPage2)

    def retranslateUi(self, ImportEISOMSPage2):
        ImportEISOMSPage2.setWindowTitle(QtGui.QApplication.translate("ImportEISOMSPage2", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAcceptedLabel.setText(QtGui.QApplication.translate("ImportEISOMSPage2", "принято", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAccepted.setText(QtGui.QApplication.translate("ImportEISOMSPage2", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.lblIntegrityErrorLabel.setText(QtGui.QApplication.translate("ImportEISOMSPage2", "нет в реестре", None, QtGui.QApplication.UnicodeUTF8))
        self.lblIntegrityError.setText(QtGui.QApplication.translate("ImportEISOMSPage2", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRefusedLabel.setText(QtGui.QApplication.translate("ImportEISOMSPage2", "отказано", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRefused.setText(QtGui.QApplication.translate("ImportEISOMSPage2", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.lblChangeDisabledLabel.setText(QtGui.QApplication.translate("ImportEISOMSPage2", "не подлежит изменению", None, QtGui.QApplication.UnicodeUTF8))
        self.lblChangeDisabled.setText(QtGui.QApplication.translate("ImportEISOMSPage2", "0", None, QtGui.QApplication.UnicodeUTF8))
        self.lblUncheckedLabel.setText(QtGui.QApplication.translate("ImportEISOMSPage2", "не обработано ЕИС-ОМС", None, QtGui.QApplication.UnicodeUTF8))
        self.lblUnchecked.setText(QtGui.QApplication.translate("ImportEISOMSPage2", "0", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImportEISOMSPage2 = QtGui.QWidget()
    ui = Ui_ImportEISOMSPage2()
    ui.setupUi(ImportEISOMSPage2)
    ImportEISOMSPage2.show()
    sys.exit(app.exec_())

