# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RadiationDosePage.ui'
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

class Ui_RadiationDosePage(object):
    def setupUi(self, RadiationDosePage):
        RadiationDosePage.setObjectName(_fromUtf8("RadiationDosePage"))
        RadiationDosePage.resize(687, 334)
        RadiationDosePage.setMinimumSize(QtCore.QSize(0, 200))
        self.gridLayout = QtGui.QGridLayout(RadiationDosePage)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblRecordCount = QtGui.QLabel(RadiationDosePage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblRecordCount.sizePolicy().hasHeightForWidth())
        self.lblRecordCount.setSizePolicy(sizePolicy)
        self.lblRecordCount.setObjectName(_fromUtf8("lblRecordCount"))
        self.gridLayout.addWidget(self.lblRecordCount, 1, 0, 1, 1)
        self.lblDoseSum = CRadiationDoseSumLabel(RadiationDosePage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblDoseSum.sizePolicy().hasHeightForWidth())
        self.lblDoseSum.setSizePolicy(sizePolicy)
        self.lblDoseSum.setObjectName(_fromUtf8("lblDoseSum"))
        self.gridLayout.addWidget(self.lblDoseSum, 1, 2, 1, 1)
        self.lblActionSum = QtGui.QLabel(RadiationDosePage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblActionSum.sizePolicy().hasHeightForWidth())
        self.lblActionSum.setSizePolicy(sizePolicy)
        self.lblActionSum.setObjectName(_fromUtf8("lblActionSum"))
        self.gridLayout.addWidget(self.lblActionSum, 1, 1, 1, 1)
        self.btnRadiationDosePrint = QtGui.QPushButton(RadiationDosePage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnRadiationDosePrint.sizePolicy().hasHeightForWidth())
        self.btnRadiationDosePrint.setSizePolicy(sizePolicy)
        self.btnRadiationDosePrint.setObjectName(_fromUtf8("btnRadiationDosePrint"))
        self.gridLayout.addWidget(self.btnRadiationDosePrint, 2, 0, 1, 1)
        self.scrollArea = QtGui.QScrollArea(RadiationDosePage)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 100))
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 675, 258))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tblRadiationDose = CTableView(self.scrollAreaWidgetContents)
        self.tblRadiationDose.setMinimumSize(QtCore.QSize(0, 200))
        self.tblRadiationDose.setObjectName(_fromUtf8("tblRadiationDose"))
        self.verticalLayout.addWidget(self.tblRadiationDose)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 3)

        self.retranslateUi(RadiationDosePage)
        QtCore.QMetaObject.connectSlotsByName(RadiationDosePage)

    def retranslateUi(self, RadiationDosePage):
        RadiationDosePage.setWindowTitle(_translate("RadiationDosePage", "Form", None))
        self.lblRecordCount.setText(_translate("RadiationDosePage", "Количество записей", None))
        self.lblDoseSum.setText(_translate("RadiationDosePage", "Сумма доз", None))
        self.lblActionSum.setText(_translate("RadiationDosePage", "Сумма количества действий", None))
        self.btnRadiationDosePrint.setText(_translate("RadiationDosePage", "Печать", None))

from Events.Utils import CRadiationDoseSumLabel
from library.TableView import CTableView
