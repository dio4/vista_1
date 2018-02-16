# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RecipeAnnulmentDialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_RecipeAnnulmentDialog(object):
    def setupUi(self, RecipeAnnulmentDialog):
        RecipeAnnulmentDialog.setObjectName(_fromUtf8("RecipeAnnulmentDialog"))
        RecipeAnnulmentDialog.resize(271, 109)
        self.gridLayout = QtGui.QGridLayout(RecipeAnnulmentDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(RecipeAnnulmentDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 1)
        self.cmbRecipeStatus = QtGui.QComboBox(RecipeAnnulmentDialog)
        self.cmbRecipeStatus.setObjectName(_fromUtf8("cmbRecipeStatus"))
        self.gridLayout.addWidget(self.cmbRecipeStatus, 1, 0, 1, 1)
        self.lblRecipeStatus = QtGui.QLabel(RecipeAnnulmentDialog)
        self.lblRecipeStatus.setObjectName(_fromUtf8("lblRecipeStatus"))
        self.gridLayout.addWidget(self.lblRecipeStatus, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)

        self.retranslateUi(RecipeAnnulmentDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RecipeAnnulmentDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RecipeAnnulmentDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RecipeAnnulmentDialog)

    def retranslateUi(self, RecipeAnnulmentDialog):
        RecipeAnnulmentDialog.setWindowTitle(_translate("RecipeAnnulmentDialog", "Изменение статуса рецепта", None))
        self.lblRecipeStatus.setText(_translate("RecipeAnnulmentDialog", "Установить статус:", None))

