# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\ThermalSheet\TemperatureListParameters.ui'
#
# Created: Fri Jun 15 12:17:34 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TemperatureListParameters(object):
    def setupUi(self, TemperatureListParameters):
        TemperatureListParameters.setObjectName(_fromUtf8("TemperatureListParameters"))
        TemperatureListParameters.resize(386, 159)
        self.gridLayout = QtGui.QGridLayout(TemperatureListParameters)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(TemperatureListParameters)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.edtBegDate = CDateEdit(TemperatureListParameters)
        self.edtBegDate.setCalendarPopup(True)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.gridLayout.addWidget(self.edtBegDate, 0, 1, 1, 1)
        self.edtEndDate = CDateEdit(TemperatureListParameters)
        self.edtEndDate.setCalendarPopup(True)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.gridLayout.addWidget(self.edtEndDate, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.chkTemperature = QtGui.QCheckBox(TemperatureListParameters)
        self.chkTemperature.setChecked(True)
        self.chkTemperature.setObjectName(_fromUtf8("chkTemperature"))
        self.gridLayout.addWidget(self.chkTemperature, 1, 0, 1, 1)
        self.chkPulse = QtGui.QCheckBox(TemperatureListParameters)
        self.chkPulse.setObjectName(_fromUtf8("chkPulse"))
        self.gridLayout.addWidget(self.chkPulse, 1, 1, 1, 2)
        self.chkAPMax = QtGui.QCheckBox(TemperatureListParameters)
        self.chkAPMax.setObjectName(_fromUtf8("chkAPMax"))
        self.gridLayout.addWidget(self.chkAPMax, 2, 0, 1, 1)
        self.chkAPMin = QtGui.QCheckBox(TemperatureListParameters)
        self.chkAPMin.setObjectName(_fromUtf8("chkAPMin"))
        self.gridLayout.addWidget(self.chkAPMin, 2, 1, 1, 2)
        self.lblMultipleDimension = QtGui.QLabel(TemperatureListParameters)
        self.lblMultipleDimension.setObjectName(_fromUtf8("lblMultipleDimension"))
        self.gridLayout.addWidget(self.lblMultipleDimension, 3, 0, 1, 1)
        self.edtMultipleDimension = QtGui.QSpinBox(TemperatureListParameters)
        self.edtMultipleDimension.setMinimum(1)
        self.edtMultipleDimension.setMaximum(4)
        self.edtMultipleDimension.setObjectName(_fromUtf8("edtMultipleDimension"))
        self.gridLayout.addWidget(self.edtMultipleDimension, 3, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(136, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 3, 2, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(20, 23, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(TemperatureListParameters)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 1, 1, 3)

        self.retranslateUi(TemperatureListParameters)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TemperatureListParameters.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TemperatureListParameters.reject)
        QtCore.QMetaObject.connectSlotsByName(TemperatureListParameters)

    def retranslateUi(self, TemperatureListParameters):
        TemperatureListParameters.setWindowTitle(QtGui.QApplication.translate("TemperatureListParameters", "Параметры", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("TemperatureListParameters", "Период", None, QtGui.QApplication.UnicodeUTF8))
        self.chkTemperature.setText(QtGui.QApplication.translate("TemperatureListParameters", "Температура", None, QtGui.QApplication.UnicodeUTF8))
        self.chkPulse.setText(QtGui.QApplication.translate("TemperatureListParameters", "Пульс", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAPMax.setText(QtGui.QApplication.translate("TemperatureListParameters", "Максимальное давление", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAPMin.setText(QtGui.QApplication.translate("TemperatureListParameters", "Минимальное давление", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMultipleDimension.setText(QtGui.QApplication.translate("TemperatureListParameters", "Кратность измерений", None, QtGui.QApplication.UnicodeUTF8))

from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TemperatureListParameters = QtGui.QDialog()
    ui = Ui_TemperatureListParameters()
    ui.setupUi(TemperatureListParameters)
    TemperatureListParameters.show()
    sys.exit(app.exec_())

