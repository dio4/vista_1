# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\library\TextItemRedactorDialog.ui'
#
# Created: Fri Jun 15 12:16:48 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TextItemRedactorDialog(object):
    def setupUi(self, TextItemRedactorDialog):
        TextItemRedactorDialog.setObjectName(_fromUtf8("TextItemRedactorDialog"))
        TextItemRedactorDialog.resize(248, 127)
        self.gridLayout = QtGui.QGridLayout(TextItemRedactorDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblText = QtGui.QLabel(TextItemRedactorDialog)
        self.lblText.setObjectName(_fromUtf8("lblText"))
        self.gridLayout.addWidget(self.lblText, 0, 0, 1, 1)
        self.edtText = QtGui.QLineEdit(TextItemRedactorDialog)
        self.edtText.setObjectName(_fromUtf8("edtText"))
        self.gridLayout.addWidget(self.edtText, 0, 1, 1, 1)
        self.lblTextSize = QtGui.QLabel(TextItemRedactorDialog)
        self.lblTextSize.setObjectName(_fromUtf8("lblTextSize"))
        self.gridLayout.addWidget(self.lblTextSize, 1, 0, 1, 1)
        self.edtTextSize = QtGui.QSpinBox(TextItemRedactorDialog)
        self.edtTextSize.setMinimum(1)
        self.edtTextSize.setMaximum(10)
        self.edtTextSize.setObjectName(_fromUtf8("edtTextSize"))
        self.gridLayout.addWidget(self.edtTextSize, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(TextItemRedactorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 2)
        self.lblRotation = QtGui.QLabel(TextItemRedactorDialog)
        self.lblRotation.setObjectName(_fromUtf8("lblRotation"))
        self.gridLayout.addWidget(self.lblRotation, 2, 0, 1, 1)
        self.edtRotation = QtGui.QSpinBox(TextItemRedactorDialog)
        self.edtRotation.setMinimum(-360)
        self.edtRotation.setMaximum(360)
        self.edtRotation.setObjectName(_fromUtf8("edtRotation"))
        self.gridLayout.addWidget(self.edtRotation, 2, 1, 1, 1)

        self.retranslateUi(TextItemRedactorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TextItemRedactorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TextItemRedactorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TextItemRedactorDialog)

    def retranslateUi(self, TextItemRedactorDialog):
        TextItemRedactorDialog.setWindowTitle(QtGui.QApplication.translate("TextItemRedactorDialog", "Редактор текстовых отметок", None, QtGui.QApplication.UnicodeUTF8))
        self.lblText.setText(QtGui.QApplication.translate("TextItemRedactorDialog", "Текст", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTextSize.setText(QtGui.QApplication.translate("TextItemRedactorDialog", "Размер текста", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRotation.setText(QtGui.QApplication.translate("TextItemRedactorDialog", "Поворот", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TextItemRedactorDialog = QtGui.QDialog()
    ui = Ui_TextItemRedactorDialog()
    ui.setupUi(TextItemRedactorDialog)
    TextItemRedactorDialog.show()
    sys.exit(app.exec_())

