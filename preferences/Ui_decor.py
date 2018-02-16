# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'decor.ui'
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

class Ui_decorDialog(object):
    def setupUi(self, decorDialog):
        decorDialog.setObjectName(_fromUtf8("decorDialog"))
        decorDialog.resize(439, 221)
        decorDialog.setSizeGripEnabled(False)
        self.gridLayout = QtGui.QGridLayout(decorDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkFullScreenMainWindow = QtGui.QCheckBox(decorDialog)
        self.chkFullScreenMainWindow.setText(_fromUtf8(""))
        self.chkFullScreenMainWindow.setObjectName(_fromUtf8("chkFullScreenMainWindow"))
        self.gridLayout.addWidget(self.chkFullScreenMainWindow, 3, 2, 1, 1)
        self.chkMaximizeMainWindow = QtGui.QCheckBox(decorDialog)
        self.chkMaximizeMainWindow.setText(_fromUtf8(""))
        self.chkMaximizeMainWindow.setObjectName(_fromUtf8("chkMaximizeMainWindow"))
        self.gridLayout.addWidget(self.chkMaximizeMainWindow, 2, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(decorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 7, 0, 1, 3)
        self.sbFontSize = QtGui.QSpinBox(decorDialog)
        self.sbFontSize.setMinimum(4)
        self.sbFontSize.setMaximum(32)
        self.sbFontSize.setObjectName(_fromUtf8("sbFontSize"))
        self.gridLayout.addWidget(self.sbFontSize, 4, 2, 1, 1)
        self.lblFontSize = QtGui.QLabel(decorDialog)
        self.lblFontSize.setObjectName(_fromUtf8("lblFontSize"))
        self.gridLayout.addWidget(self.lblFontSize, 4, 0, 1, 1)
        self.lblStyle = QtGui.QLabel(decorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblStyle.sizePolicy().hasHeightForWidth())
        self.lblStyle.setSizePolicy(sizePolicy)
        self.lblStyle.setObjectName(_fromUtf8("lblStyle"))
        self.gridLayout.addWidget(self.lblStyle, 0, 0, 1, 1)
        self.lblStandartPalette = QtGui.QLabel(decorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblStandartPalette.sizePolicy().hasHeightForWidth())
        self.lblStandartPalette.setSizePolicy(sizePolicy)
        self.lblStandartPalette.setObjectName(_fromUtf8("lblStandartPalette"))
        self.gridLayout.addWidget(self.lblStandartPalette, 1, 0, 1, 1)
        self.cmbFontName = QtGui.QFontComboBox(decorDialog)
        self.cmbFontName.setObjectName(_fromUtf8("cmbFontName"))
        self.gridLayout.addWidget(self.cmbFontName, 4, 1, 1, 1)
        self.lblFullScreenMainWindow = QtGui.QLabel(decorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFullScreenMainWindow.sizePolicy().hasHeightForWidth())
        self.lblFullScreenMainWindow.setSizePolicy(sizePolicy)
        self.lblFullScreenMainWindow.setObjectName(_fromUtf8("lblFullScreenMainWindow"))
        self.gridLayout.addWidget(self.lblFullScreenMainWindow, 3, 0, 1, 2)
        self.lblMaximizeMainWindow = QtGui.QLabel(decorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblMaximizeMainWindow.sizePolicy().hasHeightForWidth())
        self.lblMaximizeMainWindow.setSizePolicy(sizePolicy)
        self.lblMaximizeMainWindow.setObjectName(_fromUtf8("lblMaximizeMainWindow"))
        self.gridLayout.addWidget(self.lblMaximizeMainWindow, 2, 0, 1, 2)
        self.cmbStyle = QtGui.QComboBox(decorDialog)
        self.cmbStyle.setObjectName(_fromUtf8("cmbStyle"))
        self.gridLayout.addWidget(self.cmbStyle, 0, 1, 1, 2)
        self.chkStandartPalette = QtGui.QCheckBox(decorDialog)
        self.chkStandartPalette.setText(_fromUtf8(""))
        self.chkStandartPalette.setObjectName(_fromUtf8("chkStandartPalette"))
        self.gridLayout.addWidget(self.chkStandartPalette, 1, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 0, 1, 1)
        self.chkCRBWidthUnlimited = QtGui.QCheckBox(decorDialog)
        self.chkCRBWidthUnlimited.setText(_fromUtf8(""))
        self.chkCRBWidthUnlimited.setObjectName(_fromUtf8("chkCRBWidthUnlimited"))
        self.gridLayout.addWidget(self.chkCRBWidthUnlimited, 5, 2, 1, 1)
        self.lblCRBWidthUnlimited = QtGui.QLabel(decorDialog)
        self.lblCRBWidthUnlimited.setObjectName(_fromUtf8("lblCRBWidthUnlimited"))
        self.gridLayout.addWidget(self.lblCRBWidthUnlimited, 5, 0, 1, 2)
        self.lblStyle.setBuddy(self.cmbStyle)
        self.lblStandartPalette.setBuddy(self.chkStandartPalette)
        self.lblFullScreenMainWindow.setBuddy(self.chkFullScreenMainWindow)
        self.lblMaximizeMainWindow.setBuddy(self.chkMaximizeMainWindow)

        self.retranslateUi(decorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), decorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), decorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(decorDialog)
        decorDialog.setTabOrder(self.cmbStyle, self.chkStandartPalette)
        decorDialog.setTabOrder(self.chkStandartPalette, self.chkMaximizeMainWindow)
        decorDialog.setTabOrder(self.chkMaximizeMainWindow, self.chkFullScreenMainWindow)
        decorDialog.setTabOrder(self.chkFullScreenMainWindow, self.buttonBox)

    def retranslateUi(self, decorDialog):
        decorDialog.setWindowTitle(_translate("decorDialog", "Внешний вид", None))
        self.lblFontSize.setText(_translate("decorDialog", "Шрифт", None))
        self.lblStyle.setText(_translate("decorDialog", "&Стиль", None))
        self.lblStandartPalette.setText(_translate("decorDialog", "&Палитра из стиля", None))
        self.lblFullScreenMainWindow.setText(_translate("decorDialog", "Полно&экранный режим", None))
        self.lblMaximizeMainWindow.setText(_translate("decorDialog", "&Максимизировать", None))
        self.lblCRBWidthUnlimited.setText(_translate("decorDialog", "Не ограничивать ширину выпадающих списков", None))

