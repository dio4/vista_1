# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Orgs\IntroducePercentDialog.ui'
#
# Created: Fri Jun 15 12:17:19 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_IntroducePercentDialog(object):
    def setupUi(self, IntroducePercentDialog):
        IntroducePercentDialog.setObjectName(_fromUtf8("IntroducePercentDialog"))
        IntroducePercentDialog.resize(400, 300)
        self.gridLayout = QtGui.QGridLayout(IntroducePercentDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblIntroducePercent = CTableView(IntroducePercentDialog)
        self.tblIntroducePercent.setObjectName(_fromUtf8("tblIntroducePercent"))
        self.gridLayout.addWidget(self.tblIntroducePercent, 0, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(IntroducePercentDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 1)
        self.lblSelectionRows = QtGui.QLabel(IntroducePercentDialog)
        self.lblSelectionRows.setText(_fromUtf8(""))
        self.lblSelectionRows.setObjectName(_fromUtf8("lblSelectionRows"))
        self.gridLayout.addWidget(self.lblSelectionRows, 1, 0, 1, 1)

        self.retranslateUi(IntroducePercentDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), IntroducePercentDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), IntroducePercentDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(IntroducePercentDialog)

    def retranslateUi(self, IntroducePercentDialog):
        IntroducePercentDialog.setWindowTitle(QtGui.QApplication.translate("IntroducePercentDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

from library.TableView import CTableView

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    IntroducePercentDialog = QtGui.QDialog()
    ui = Ui_IntroducePercentDialog()
    ui.setupUi(IntroducePercentDialog)
    IntroducePercentDialog.show()
    sys.exit(app.exec_())

