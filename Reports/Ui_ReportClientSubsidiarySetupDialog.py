# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Reports\ReportClientSubsidiarySetupDialog.ui'
#
# Created: Fri Jun 15 12:17:52 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ReportClientSubsidiarySetupDialog(object):
    def setupUi(self, ReportClientSubsidiarySetupDialog):
        ReportClientSubsidiarySetupDialog.setObjectName(_fromUtf8("ReportClientSubsidiarySetupDialog"))
        ReportClientSubsidiarySetupDialog.resize(336, 93)
        self.gridLayout = QtGui.QGridLayout(ReportClientSubsidiarySetupDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(ReportClientSubsidiarySetupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 5)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 3, 1, 1)
        self.lblPayeded = QtGui.QLabel(ReportClientSubsidiarySetupDialog)
        self.lblPayeded.setObjectName(_fromUtf8("lblPayeded"))
        self.gridLayout.addWidget(self.lblPayeded, 1, 0, 1, 1)
        self.cmbPayeded = COrgComboBox(ReportClientSubsidiarySetupDialog)
        self.cmbPayeded.setEditable(True)
        self.cmbPayeded.setObjectName(_fromUtf8("cmbPayeded"))
        self.gridLayout.addWidget(self.cmbPayeded, 1, 1, 1, 4)
        self.lblDiagnosis = QtGui.QLabel(ReportClientSubsidiarySetupDialog)
        self.lblDiagnosis.setObjectName(_fromUtf8("lblDiagnosis"))
        self.gridLayout.addWidget(self.lblDiagnosis, 2, 0, 1, 1)
        self.edtDiagnosis = CICDCodeComboBoxEx(ReportClientSubsidiarySetupDialog)
        self.edtDiagnosis.setObjectName(_fromUtf8("edtDiagnosis"))
        self.gridLayout.addWidget(self.edtDiagnosis, 2, 1, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 3, 1, 2)

        self.retranslateUi(ReportClientSubsidiarySetupDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ReportClientSubsidiarySetupDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ReportClientSubsidiarySetupDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReportClientSubsidiarySetupDialog)

    def retranslateUi(self, ReportClientSubsidiarySetupDialog):
        ReportClientSubsidiarySetupDialog.setWindowTitle(QtGui.QApplication.translate("ReportClientSubsidiarySetupDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPayeded.setText(QtGui.QApplication.translate("ReportClientSubsidiarySetupDialog", "Плательщик", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDiagnosis.setText(QtGui.QApplication.translate("ReportClientSubsidiarySetupDialog", "Диагноз", None, QtGui.QApplication.UnicodeUTF8))

from Orgs.OrgComboBox import COrgComboBox
from library.ICDCodeEdit import CICDCodeComboBoxEx

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ReportClientSubsidiarySetupDialog = QtGui.QDialog()
    ui = Ui_ReportClientSubsidiarySetupDialog()
    ui.setupUi(ReportClientSubsidiarySetupDialog)
    ReportClientSubsidiarySetupDialog.show()
    sys.exit(app.exec_())

