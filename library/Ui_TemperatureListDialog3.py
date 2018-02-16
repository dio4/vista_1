# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\library\TemperatureListDialog3.ui'
#
# Created: Fri Jun 15 12:17:32 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TemperatureListDialog(object):
    def setupUi(self, TemperatureListDialog):
        TemperatureListDialog.setObjectName(_fromUtf8("TemperatureListDialog"))
        TemperatureListDialog.resize(730, 551)
        self.gridLayout = QtGui.QGridLayout(TemperatureListDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(TemperatureListDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 2)
        self.scrollArea = QtGui.QScrollArea(TemperatureListDialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 712, 504))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_2 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.widget1 = QtGui.QWidget(self.scrollAreaWidgetContents)
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.gridLayout_2.addWidget(self.widget1, 0, 0, 1, 1)
        self.widget2 = QtGui.QWidget(self.scrollAreaWidgetContents)
        self.widget2.setObjectName(_fromUtf8("widget2"))
        self.gridLayout_2.addWidget(self.widget2, 1, 0, 1, 1)
        self.widget3 = QtGui.QWidget(self.scrollAreaWidgetContents)
        self.widget3.setObjectName(_fromUtf8("widget3"))
        self.gridLayout_2.addWidget(self.widget3, 2, 0, 1, 1)
        self.widget4 = QtGui.QWidget(self.scrollAreaWidgetContents)
        self.widget4.setObjectName(_fromUtf8("widget4"))
        self.gridLayout_2.addWidget(self.widget4, 3, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(TemperatureListDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TemperatureListDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TemperatureListDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TemperatureListDialog)

    def retranslateUi(self, TemperatureListDialog):
        TemperatureListDialog.setWindowTitle(QtGui.QApplication.translate("TemperatureListDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TemperatureListDialog = QtGui.QDialog()
    ui = Ui_TemperatureListDialog()
    ui.setupUi(TemperatureListDialog)
    TemperatureListDialog.show()
    sys.exit(app.exec_())

