# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EQPanelWidget.ui'
#
# Created: Fri Nov 08 13:25:49 2013
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_EQPanelWidget(object):
    def setupUi(self, EQPanelWidget):
        EQPanelWidget.setObjectName(_fromUtf8("EQPanelWidget"))
        EQPanelWidget.resize(162, 50)
        self.gridLayout = QtGui.QGridLayout(EQPanelWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblOfficeCaption = QtGui.QLabel(EQPanelWidget)
        self.lblOfficeCaption.setObjectName(_fromUtf8("lblOfficeCaption"))
        self.gridLayout.addWidget(self.lblOfficeCaption, 0, 0, 1, 1)
        self.eqGuiPanel = CEQGuiPanel(EQPanelWidget)
        self.eqGuiPanel.setMinimumSize(QtCore.QSize(80, 0))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Tahoma"))
        font.setPointSize(16)
        self.eqGuiPanel.setFont(font)
        self.eqGuiPanel.setStyleSheet(_fromUtf8("color: red"))
        self.eqGuiPanel.setFrameShape(QtGui.QFrame.Box)
        self.eqGuiPanel.setFrameShadow(QtGui.QFrame.Raised)
        self.eqGuiPanel.setText(_fromUtf8(""))
        self.eqGuiPanel.setTextFormat(QtCore.Qt.AutoText)
        self.eqGuiPanel.setAlignment(QtCore.Qt.AlignCenter)
        self.eqGuiPanel.setObjectName(_fromUtf8("eqGuiPanel"))
        self.gridLayout.addWidget(self.eqGuiPanel, 0, 1, 2, 1)
        self.btnConfig = QtGui.QToolButton(EQPanelWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/new/prefix1/icons/oxygen_system.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnConfig.setIcon(icon)
        self.btnConfig.setObjectName(_fromUtf8("btnConfig"))
        self.gridLayout.addWidget(self.btnConfig, 0, 3, 2, 1)
        self.lblOffice = QtGui.QLabel(EQPanelWidget)
        self.lblOffice.setObjectName(_fromUtf8("lblOffice"))
        self.gridLayout.addWidget(self.lblOffice, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(60, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 2, 1)

        self.retranslateUi(EQPanelWidget)
        QtCore.QMetaObject.connectSlotsByName(EQPanelWidget)

    def retranslateUi(self, EQPanelWidget):
        EQPanelWidget.setWindowTitle(_translate("EQPanelWidget", "Табло эл. очереди", None))
        self.lblOfficeCaption.setText(_translate("EQPanelWidget", "Каб.", None))
        self.btnConfig.setText(_translate("EQPanelWidget", "...", None))
        self.lblOffice.setText(_translate("EQPanelWidget", "---", None))

from library.ElectronicQueue.EQPanel import CEQGuiPanel
import s11main_rc
