# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Registry\StatusObservationClientEditor.ui'
#
# Created: Fri Jun 15 12:17:46 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_StatusObservationClientEditor(object):
    def setupUi(self, StatusObservationClientEditor):
        StatusObservationClientEditor.setObjectName(_fromUtf8("StatusObservationClientEditor"))
        StatusObservationClientEditor.resize(374, 84)
        StatusObservationClientEditor.setSizeGripEnabled(False)
        self.gridLayout = QtGui.QGridLayout(StatusObservationClientEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(StatusObservationClientEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)
        self.label = QtGui.QLabel(StatusObservationClientEditor)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cmbStatusObservationType = CRBComboBox(StatusObservationClientEditor)
        self.cmbStatusObservationType.setObjectName(_fromUtf8("cmbStatusObservationType"))
        self.gridLayout.addWidget(self.cmbStatusObservationType, 0, 1, 1, 1)

        self.retranslateUi(StatusObservationClientEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StatusObservationClientEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StatusObservationClientEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(StatusObservationClientEditor)

    def retranslateUi(self, StatusObservationClientEditor):
        StatusObservationClientEditor.setWindowTitle(QtGui.QApplication.translate("StatusObservationClientEditor", "Статус наблюдения пациента", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("StatusObservationClientEditor", "Статус наблюдения пациента", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    StatusObservationClientEditor = QtGui.QDialog()
    ui = Ui_StatusObservationClientEditor()
    ui.setupUi(StatusObservationClientEditor)
    StatusObservationClientEditor.show()
    sys.exit(app.exec_())

