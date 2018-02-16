# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Resources\JobPlanNumbersDialog.ui'
#
# Created: Fri Jun 15 12:16:38 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_JobPlanNumbersDialog(object):
    def setupUi(self, JobPlanNumbersDialog):
        JobPlanNumbersDialog.setObjectName(_fromUtf8("JobPlanNumbersDialog"))
        JobPlanNumbersDialog.resize(608, 470)
        self.verticalLayout_3 = QtGui.QVBoxLayout(JobPlanNumbersDialog)
        self.verticalLayout_3.setSpacing(4)
        self.verticalLayout_3.setMargin(4)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.splitter = QtGui.QSplitter(JobPlanNumbersDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.grplJobAmbNumbers = QtGui.QGroupBox(self.splitter)
        self.grplJobAmbNumbers.setObjectName(_fromUtf8("grplJobAmbNumbers"))
        self.verticalLayout = QtGui.QVBoxLayout(self.grplJobAmbNumbers)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tblJobAmbNumbers = CTableView(self.grplJobAmbNumbers)
        self.tblJobAmbNumbers.setObjectName(_fromUtf8("tblJobAmbNumbers"))
        self.verticalLayout.addWidget(self.tblJobAmbNumbers)
        self.grpOrgStructureGaps = QtGui.QGroupBox(self.splitter)
        self.grpOrgStructureGaps.setObjectName(_fromUtf8("grpOrgStructureGaps"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.grpOrgStructureGaps)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setMargin(4)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tblJobOrgStructureGaps = CTableView(self.grpOrgStructureGaps)
        self.tblJobOrgStructureGaps.setObjectName(_fromUtf8("tblJobOrgStructureGaps"))
        self.verticalLayout_2.addWidget(self.tblJobOrgStructureGaps)
        self.verticalLayout_3.addWidget(self.splitter)
        self.buttonBox = QtGui.QDialogButtonBox(JobPlanNumbersDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(JobPlanNumbersDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), JobPlanNumbersDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), JobPlanNumbersDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(JobPlanNumbersDialog)
        JobPlanNumbersDialog.setTabOrder(self.tblJobAmbNumbers, self.tblJobOrgStructureGaps)
        JobPlanNumbersDialog.setTabOrder(self.tblJobOrgStructureGaps, self.buttonBox)

    def retranslateUi(self, JobPlanNumbersDialog):
        JobPlanNumbersDialog.setWindowTitle(QtGui.QApplication.translate("JobPlanNumbersDialog", "Номерки", None, QtGui.QApplication.UnicodeUTF8))
        self.grplJobAmbNumbers.setTitle(QtGui.QApplication.translate("JobPlanNumbersDialog", "Амбулаторный прием", None, QtGui.QApplication.UnicodeUTF8))
        self.grpOrgStructureGaps.setTitle(QtGui.QApplication.translate("JobPlanNumbersDialog", "Перерывы подразделения", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    JobPlanNumbersDialog = QtGui.QDialog()
    ui = Ui_JobPlanNumbersDialog()
    ui.setupUi(JobPlanNumbersDialog)
    JobPlanNumbersDialog.show()
    sys.exit(app.exec_())

