# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Registry\LocationCardEditor.ui'
#
# Created: Fri Jun 15 12:17:47 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_LocationCardEditor(object):
    def setupUi(self, LocationCardEditor):
        LocationCardEditor.setObjectName(_fromUtf8("LocationCardEditor"))
        LocationCardEditor.resize(374, 84)
        LocationCardEditor.setSizeGripEnabled(False)
        self.gridLayout = QtGui.QGridLayout(LocationCardEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(LocationCardEditor)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)
        self.label = QtGui.QLabel(LocationCardEditor)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cmbLocationCardType = CRBComboBox(LocationCardEditor)
        self.cmbLocationCardType.setObjectName(_fromUtf8("cmbLocationCardType"))
        self.gridLayout.addWidget(self.cmbLocationCardType, 0, 1, 1, 1)

        self.retranslateUi(LocationCardEditor)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), LocationCardEditor.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), LocationCardEditor.reject)
        QtCore.QMetaObject.connectSlotsByName(LocationCardEditor)

    def retranslateUi(self, LocationCardEditor):
        LocationCardEditor.setWindowTitle(QtGui.QApplication.translate("LocationCardEditor", "Место нахождения амбулаторной карты", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("LocationCardEditor", "Место нахождения амбулаторной карты", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    LocationCardEditor = QtGui.QDialog()
    ui = Ui_LocationCardEditor()
    ui.setupUi(LocationCardEditor)
    LocationCardEditor.show()
    sys.exit(app.exec_())

