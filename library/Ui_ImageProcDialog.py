# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\library\ImageProcDialog.ui'
#
# Created: Fri Jun 15 12:15:29 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImageProcDialog(object):
    def setupUi(self, ImageProcDialog):
        ImageProcDialog.setObjectName(_fromUtf8("ImageProcDialog"))
        ImageProcDialog.resize(400, 300)
        ImageProcDialog.setSizeGripEnabled(True)
        ImageProcDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(ImageProcDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.grpView = QtGui.QGraphicsView(ImageProcDialog)
        self.grpView.setObjectName(_fromUtf8("grpView"))
        self.gridLayout.addWidget(self.grpView, 0, 0, 1, 1)
        self.scrSize = QtGui.QSlider(ImageProcDialog)
        self.scrSize.setMinimum(-10)
        self.scrSize.setMaximum(10)
        self.scrSize.setProperty("value", 0)
        self.scrSize.setOrientation(QtCore.Qt.Vertical)
        self.scrSize.setInvertedAppearance(False)
        self.scrSize.setTickPosition(QtGui.QSlider.TicksBelow)
        self.scrSize.setTickInterval(2)
        self.scrSize.setObjectName(_fromUtf8("scrSize"))
        self.gridLayout.addWidget(self.scrSize, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ImageProcDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 2)

        self.retranslateUi(ImageProcDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ImageProcDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ImageProcDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ImageProcDialog)
        ImageProcDialog.setTabOrder(self.grpView, self.scrSize)
        ImageProcDialog.setTabOrder(self.scrSize, self.buttonBox)

    def retranslateUi(self, ImageProcDialog):
        ImageProcDialog.setWindowTitle(QtGui.QApplication.translate("ImageProcDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ImageProcDialog = QtGui.QDialog()
    ui = Ui_ImageProcDialog()
    ui.setupUi(ImageProcDialog)
    ImageProcDialog.show()
    sys.exit(app.exec_())

