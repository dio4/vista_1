# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/artiom/s11/s11/Reports/StationaryF016Setup.ui'
#
# Created: Fri Aug  3 14:47:43 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_StationaryF016SetupDialog(object):
    def setupUi(self, StationaryF016SetupDialog):
        StationaryF016SetupDialog.setObjectName(_fromUtf8("StationaryF016SetupDialog"))
        StationaryF016SetupDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        StationaryF016SetupDialog.resize(291, 236)
        StationaryF016SetupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(StationaryF016SetupDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblYear = QtGui.QLabel(StationaryF016SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblYear.sizePolicy().hasHeightForWidth())
        self.lblYear.setSizePolicy(sizePolicy)
        self.lblYear.setObjectName(_fromUtf8("lblYear"))
        self.gridLayout.addWidget(self.lblYear, 0, 0, 1, 1)
        self.edtYear = QtGui.QLineEdit(StationaryF016SetupDialog)
        self.edtYear.setMaxLength(4)
        self.edtYear.setObjectName(_fromUtf8("edtYear"))
        self.gridLayout.addWidget(self.edtYear, 0, 2, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(StationaryF016SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblOrgStructure.sizePolicy().hasHeightForWidth())
        self.lblOrgStructure.setSizePolicy(sizePolicy)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 1, 0, 1, 2)
        self.cmbOrgStructure = COrgStructureComboBox(StationaryF016SetupDialog)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 1, 2, 1, 1)
        self.lblProfilBed = QtGui.QLabel(StationaryF016SetupDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblProfilBed.sizePolicy().hasHeightForWidth())
        self.lblProfilBed.setSizePolicy(sizePolicy)
        self.lblProfilBed.setObjectName(_fromUtf8("lblProfilBed"))
        self.gridLayout.addWidget(self.lblProfilBed, 2, 0, 1, 2)
        self.cmbProfilBed = CRBComboBox(StationaryF016SetupDialog)
        self.cmbProfilBed.setObjectName(_fromUtf8("cmbProfilBed"))
        self.gridLayout.addWidget(self.cmbProfilBed, 2, 2, 1, 1)
        self.lblSocStatusClass = QtGui.QLabel(StationaryF016SetupDialog)
        self.lblSocStatusClass.setObjectName(_fromUtf8("lblSocStatusClass"))
        self.gridLayout.addWidget(self.lblSocStatusClass, 3, 0, 1, 2)
        self.cmbSocStatusClass = CSocStatusComboBox(StationaryF016SetupDialog)
        self.cmbSocStatusClass.setObjectName(_fromUtf8("cmbSocStatusClass"))
        self.gridLayout.addWidget(self.cmbSocStatusClass, 3, 2, 1, 1)
        self.lblSocStatusType = QtGui.QLabel(StationaryF016SetupDialog)
        self.lblSocStatusType.setObjectName(_fromUtf8("lblSocStatusType"))
        self.gridLayout.addWidget(self.lblSocStatusType, 4, 0, 1, 2)
        self.cmbSocStatusType = CRBComboBox(StationaryF016SetupDialog)
        self.cmbSocStatusType.setObjectName(_fromUtf8("cmbSocStatusType"))
        self.gridLayout.addWidget(self.cmbSocStatusType, 4, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(129, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(StationaryF016SetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 1, 1, 2)
        self.lblOrgStructure.setBuddy(self.cmbOrgStructure)
        self.lblSocStatusClass.setBuddy(self.cmbSocStatusClass)
        self.lblSocStatusType.setBuddy(self.cmbSocStatusType)

        self.retranslateUi(StationaryF016SetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StationaryF016SetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StationaryF016SetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StationaryF016SetupDialog)
        StationaryF016SetupDialog.setTabOrder(self.cmbOrgStructure, self.buttonBox)

    def retranslateUi(self, StationaryF016SetupDialog):
        StationaryF016SetupDialog.setWindowTitle(QtGui.QApplication.translate("StationaryF016SetupDialog", "параметры отчёта", None, QtGui.QApplication.UnicodeUTF8))
        self.lblYear.setText(QtGui.QApplication.translate("StationaryF016SetupDialog", "Год", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("StationaryF016SetupDialog", "&Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblProfilBed.setText(QtGui.QApplication.translate("StationaryF016SetupDialog", "Профиль койки", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSocStatusClass.setText(QtGui.QApplication.translate("StationaryF016SetupDialog", "Класс соц.статуса", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSocStatusType.setText(QtGui.QApplication.translate("StationaryF016SetupDialog", "Тип соц.статуса", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from Registry.SocStatusComboBox import CSocStatusComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    StationaryF016SetupDialog = QtGui.QDialog()
    ui = Ui_StationaryF016SetupDialog()
    ui.setupUi(StationaryF016SetupDialog)
    StationaryF016SetupDialog.show()
    sys.exit(app.exec_())

