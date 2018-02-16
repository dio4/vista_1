# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\HospitalBeds\HospitalBedEditor.ui'
#
# Created: Fri Jun 15 12:17:48 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_HospitalBedEditor(object):
    def setupUi(self, HospitalBedEditor):
        HospitalBedEditor.setObjectName(_fromUtf8("HospitalBedEditor"))
        HospitalBedEditor.resize(400, 99)
        self.gridLayout = QtGui.QGridLayout(HospitalBedEditor)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.cmbHospitalBed = CHospitalBedFindComboBoxEditor(HospitalBedEditor)
        self.cmbHospitalBed.setEditable(True)
        self.cmbHospitalBed.setObjectName(_fromUtf8("cmbHospitalBed"))
        self.gridLayout.addWidget(self.cmbHospitalBed, 1, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(HospitalBedEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.lblHospitalBed = QtGui.QLabel(HospitalBedEditor)
        self.lblHospitalBed.setAlignment(QtCore.Qt.AlignCenter)
        self.lblHospitalBed.setObjectName(_fromUtf8("lblHospitalBed"))
        self.gridLayout.addWidget(self.lblHospitalBed, 0, 0, 1, 2)

        self.retranslateUi(HospitalBedEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), HospitalBedEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), HospitalBedEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(HospitalBedEditor)

    def retranslateUi(self, HospitalBedEditor):
        HospitalBedEditor.setWindowTitle(QtGui.QApplication.translate("HospitalBedEditor", "Редактор койки", None, QtGui.QApplication.UnicodeUTF8))
        self.lblHospitalBed.setText(QtGui.QApplication.translate("HospitalBedEditor", "Койка", None, QtGui.QApplication.UnicodeUTF8))

from HospitalBedFindComboBox import CHospitalBedFindComboBoxEditor

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    HospitalBedEditor = QtGui.QDialog()
    ui = Ui_HospitalBedEditor()
    ui.setupUi(HospitalBedEditor)
    HospitalBedEditor.show()
    sys.exit(app.exec_())

