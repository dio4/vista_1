# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\F131\PreF131.ui'
#
# Created: Fri Jun 15 12:15:26 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PreF131Dialog(object):
    def setupUi(self, PreF131Dialog):
        PreF131Dialog.setObjectName(_fromUtf8("PreF131Dialog"))
        PreF131Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        PreF131Dialog.resize(530, 700)
        self.gridlayout = QtGui.QGridLayout(PreF131Dialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.grpActions = QtGui.QGroupBox(PreF131Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpActions.sizePolicy().hasHeightForWidth())
        self.grpActions.setSizePolicy(sizePolicy)
        self.grpActions.setMinimumSize(QtCore.QSize(100, 0))
        self.grpActions.setObjectName(_fromUtf8("grpActions"))
        self.gridLayout_2 = QtGui.QGridLayout(self.grpActions)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.tblActions = CInDocTableView(self.grpActions)
        self.tblActions.setObjectName(_fromUtf8("tblActions"))
        self.gridLayout_2.addWidget(self.tblActions, 0, 0, 1, 4)
        spacerItem = QtGui.QSpacerItem(561, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 1, 2, 1, 1)
        self.btnSelectActions = QtGui.QPushButton(self.grpActions)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSelectActions.sizePolicy().hasHeightForWidth())
        self.btnSelectActions.setSizePolicy(sizePolicy)
        self.btnSelectActions.setMinimumSize(QtCore.QSize(100, 0))
        self.btnSelectActions.setAutoDefault(False)
        self.btnSelectActions.setDefault(False)
        self.btnSelectActions.setObjectName(_fromUtf8("btnSelectActions"))
        self.gridLayout_2.addWidget(self.btnSelectActions, 1, 0, 1, 1)
        self.btnDeselectActions = QtGui.QPushButton(self.grpActions)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDeselectActions.sizePolicy().hasHeightForWidth())
        self.btnDeselectActions.setSizePolicy(sizePolicy)
        self.btnDeselectActions.setMinimumSize(QtCore.QSize(100, 0))
        self.btnDeselectActions.setAutoDefault(False)
        self.btnDeselectActions.setDefault(False)
        self.btnDeselectActions.setObjectName(_fromUtf8("btnDeselectActions"))
        self.gridLayout_2.addWidget(self.btnDeselectActions, 1, 1, 1, 1)
        self.gridlayout.addWidget(self.grpActions, 1, 0, 1, 1)
        self.grpInspections = QtGui.QGroupBox(PreF131Dialog)
        self.grpInspections.setObjectName(_fromUtf8("grpInspections"))
        self.gridLayout = QtGui.QGridLayout(self.grpInspections)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblDiagnostics = CInDocTableView(self.grpInspections)
        self.tblDiagnostics.setObjectName(_fromUtf8("tblDiagnostics"))
        self.gridLayout.addWidget(self.tblDiagnostics, 0, 0, 1, 4)
        self.btnSelectVisits = QtGui.QPushButton(self.grpInspections)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSelectVisits.sizePolicy().hasHeightForWidth())
        self.btnSelectVisits.setSizePolicy(sizePolicy)
        self.btnSelectVisits.setMinimumSize(QtCore.QSize(100, 0))
        self.btnSelectVisits.setAutoDefault(False)
        self.btnSelectVisits.setDefault(False)
        self.btnSelectVisits.setObjectName(_fromUtf8("btnSelectVisits"))
        self.gridLayout.addWidget(self.btnSelectVisits, 1, 1, 1, 1)
        self.btnDeselectVisits = QtGui.QPushButton(self.grpInspections)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDeselectVisits.sizePolicy().hasHeightForWidth())
        self.btnDeselectVisits.setSizePolicy(sizePolicy)
        self.btnDeselectVisits.setMinimumSize(QtCore.QSize(100, 0))
        self.btnDeselectVisits.setAutoDefault(False)
        self.btnDeselectVisits.setDefault(False)
        self.btnDeselectVisits.setObjectName(_fromUtf8("btnDeselectVisits"))
        self.gridLayout.addWidget(self.btnDeselectVisits, 1, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(561, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 3, 1, 1)
        self.gridlayout.addWidget(self.grpInspections, 0, 0, 1, 1)
        self.buttonBox_3 = QtGui.QDialogButtonBox(PreF131Dialog)
        self.buttonBox_3.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox_3.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox_3.setObjectName(_fromUtf8("buttonBox_3"))
        self.gridlayout.addWidget(self.buttonBox_3, 2, 0, 1, 1)

        self.retranslateUi(PreF131Dialog)
        QtCore.QObject.connect(self.buttonBox_3, QtCore.SIGNAL(_fromUtf8("accepted()")), PreF131Dialog.accept)
        QtCore.QObject.connect(self.buttonBox_3, QtCore.SIGNAL(_fromUtf8("rejected()")), PreF131Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PreF131Dialog)
        PreF131Dialog.setTabOrder(self.tblDiagnostics, self.btnSelectVisits)
        PreF131Dialog.setTabOrder(self.btnSelectVisits, self.btnDeselectVisits)
        PreF131Dialog.setTabOrder(self.btnDeselectVisits, self.tblActions)
        PreF131Dialog.setTabOrder(self.tblActions, self.btnSelectActions)
        PreF131Dialog.setTabOrder(self.btnSelectActions, self.btnDeselectActions)
        PreF131Dialog.setTabOrder(self.btnDeselectActions, self.buttonBox_3)

    def retranslateUi(self, PreF131Dialog):
        PreF131Dialog.setWindowTitle(QtGui.QApplication.translate("PreF131Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.grpActions.setTitle(QtGui.QApplication.translate("PreF131Dialog", "Мероприятия", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectActions.setText(QtGui.QApplication.translate("PreF131Dialog", "Выбрать все", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDeselectActions.setText(QtGui.QApplication.translate("PreF131Dialog", "Очистить выбор", None, QtGui.QApplication.UnicodeUTF8))
        self.grpInspections.setTitle(QtGui.QApplication.translate("PreF131Dialog", "Осмотры", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectVisits.setText(QtGui.QApplication.translate("PreF131Dialog", "Выбрать все", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDeselectVisits.setText(QtGui.QApplication.translate("PreF131Dialog", "Очистить выбор", None, QtGui.QApplication.UnicodeUTF8))

from library.InDocTable import CInDocTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    PreF131Dialog = QtGui.QDialog()
    ui = Ui_PreF131Dialog()
    ui.setupUi(PreF131Dialog)
    PreF131Dialog.show()
    sys.exit(app.exec_())

