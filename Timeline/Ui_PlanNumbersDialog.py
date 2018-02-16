# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Timeline\PlanNumbersDialog.ui'
#
# Created: Fri Jun 15 12:16:30 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PlanNumbersDialog(object):
    def setupUi(self, PlanNumbersDialog):
        PlanNumbersDialog.setObjectName(_fromUtf8("PlanNumbersDialog"))
        PlanNumbersDialog.resize(772, 415)
        self.verticalLayout_5 = QtGui.QVBoxLayout(PlanNumbersDialog)
        self.verticalLayout_5.setSpacing(4)
        self.verticalLayout_5.setMargin(4)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.splitter_2 = QtGui.QSplitter(PlanNumbersDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_2.sizePolicy().hasHeightForWidth())
        self.splitter_2.setSizePolicy(sizePolicy)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setChildrenCollapsible(False)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.grpAmbNumbers = QtGui.QGroupBox(self.splitter_2)
        self.grpAmbNumbers.setObjectName(_fromUtf8("grpAmbNumbers"))
        self.verticalLayout = QtGui.QVBoxLayout(self.grpAmbNumbers)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tblAmbNumbers = CTableView(self.grpAmbNumbers)
        self.tblAmbNumbers.setObjectName(_fromUtf8("tblAmbNumbers"))
        self.verticalLayout.addWidget(self.tblAmbNumbers)
        self.grpHomeNumbers = QtGui.QGroupBox(self.splitter_2)
        self.grpHomeNumbers.setObjectName(_fromUtf8("grpHomeNumbers"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.grpHomeNumbers)
        self.verticalLayout_2.setSpacing(4)
        self.verticalLayout_2.setMargin(4)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tblHomeNumbers = CTableView(self.grpHomeNumbers)
        self.tblHomeNumbers.setObjectName(_fromUtf8("tblHomeNumbers"))
        self.verticalLayout_2.addWidget(self.tblHomeNumbers)
        self.splitter = QtGui.QSplitter(self.splitter_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.grpOrgStructureGaps = QtGui.QGroupBox(self.splitter)
        self.grpOrgStructureGaps.setObjectName(_fromUtf8("grpOrgStructureGaps"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.grpOrgStructureGaps)
        self.verticalLayout_3.setSpacing(4)
        self.verticalLayout_3.setMargin(4)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.tblOrgStructureGaps = CTableView(self.grpOrgStructureGaps)
        self.tblOrgStructureGaps.setObjectName(_fromUtf8("tblOrgStructureGaps"))
        self.verticalLayout_3.addWidget(self.tblOrgStructureGaps)
        self.grpPersonGaps = QtGui.QGroupBox(self.splitter)
        self.grpPersonGaps.setObjectName(_fromUtf8("grpPersonGaps"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.grpPersonGaps)
        self.verticalLayout_4.setSpacing(4)
        self.verticalLayout_4.setMargin(4)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.tblPersonGaps = CTableView(self.grpPersonGaps)
        self.tblPersonGaps.setObjectName(_fromUtf8("tblPersonGaps"))
        self.verticalLayout_4.addWidget(self.tblPersonGaps)
        self.verticalLayout_5.addWidget(self.splitter_2)
        self.buttonBox = QtGui.QDialogButtonBox(PlanNumbersDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_5.addWidget(self.buttonBox)

        self.retranslateUi(PlanNumbersDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PlanNumbersDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PlanNumbersDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PlanNumbersDialog)
        PlanNumbersDialog.setTabOrder(self.tblAmbNumbers, self.tblHomeNumbers)
        PlanNumbersDialog.setTabOrder(self.tblHomeNumbers, self.tblOrgStructureGaps)
        PlanNumbersDialog.setTabOrder(self.tblOrgStructureGaps, self.tblPersonGaps)
        PlanNumbersDialog.setTabOrder(self.tblPersonGaps, self.buttonBox)

    def retranslateUi(self, PlanNumbersDialog):
        PlanNumbersDialog.setWindowTitle(QtGui.QApplication.translate("PlanNumbersDialog", "Номерки", None, QtGui.QApplication.UnicodeUTF8))
        self.grpAmbNumbers.setTitle(QtGui.QApplication.translate("PlanNumbersDialog", "Амбулаторный прием", None, QtGui.QApplication.UnicodeUTF8))
        self.grpHomeNumbers.setTitle(QtGui.QApplication.translate("PlanNumbersDialog", "Вызовы на дом", None, QtGui.QApplication.UnicodeUTF8))
        self.grpOrgStructureGaps.setTitle(QtGui.QApplication.translate("PlanNumbersDialog", "Перерывы подразделения", None, QtGui.QApplication.UnicodeUTF8))
        self.grpPersonGaps.setTitle(QtGui.QApplication.translate("PlanNumbersDialog", "Перерывы сотрудника", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    PlanNumbersDialog = QtGui.QDialog()
    ui = Ui_PlanNumbersDialog()
    ui.setupUi(PlanNumbersDialog)
    PlanNumbersDialog.show()
    sys.exit(app.exec_())

