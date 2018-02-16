# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EventMesPage.ui'
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

class Ui_EventMesPageWidget(object):
    def setupUi(self, EventMesPageWidget):
        EventMesPageWidget.setObjectName(_fromUtf8("EventMesPageWidget"))
        EventMesPageWidget.resize(822, 482)
        self.verticalLayout = QtGui.QVBoxLayout(EventMesPageWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea = QtGui.QScrollArea(EventMesPageWidget)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 810, 470))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.grpRelatedEvents = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.grpRelatedEvents.setObjectName(_fromUtf8("grpRelatedEvents"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.grpRelatedEvents)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tblRelatedEvents = CTableView(self.grpRelatedEvents)
        self.tblRelatedEvents.setMinimumSize(QtCore.QSize(0, 100))
        self.tblRelatedEvents.setObjectName(_fromUtf8("tblRelatedEvents"))
        self.horizontalLayout.addWidget(self.tblRelatedEvents)
        self.gridLayout.addWidget(self.grpRelatedEvents, 5, 0, 1, 3)
        self.lblMes = QtGui.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblMes.sizePolicy().hasHeightForWidth())
        self.lblMes.setSizePolicy(sizePolicy)
        self.lblMes.setObjectName(_fromUtf8("lblMes"))
        self.gridLayout.addWidget(self.lblMes, 0, 0, 1, 1)
        self.chkHTG = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.chkHTG.setEnabled(False)
        self.chkHTG.setObjectName(_fromUtf8("chkHTG"))
        self.gridLayout.addWidget(self.chkHTG, 1, 0, 1, 1)
        self.lblMesSpecification = QtGui.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblMesSpecification.sizePolicy().hasHeightForWidth())
        self.lblMesSpecification.setSizePolicy(sizePolicy)
        self.lblMesSpecification.setObjectName(_fromUtf8("lblMesSpecification"))
        self.gridLayout.addWidget(self.lblMesSpecification, 2, 0, 1, 1)
        self.btnCheckMes = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.btnCheckMes.setEnabled(False)
        self.btnCheckMes.setObjectName(_fromUtf8("btnCheckMes"))
        self.gridLayout.addWidget(self.btnCheckMes, 3, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 2, 1, 1)
        self.btnShowMes = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.btnShowMes.setEnabled(False)
        self.btnShowMes.setObjectName(_fromUtf8("btnShowMes"))
        self.gridLayout.addWidget(self.btnShowMes, 4, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 4, 2, 1, 1)
        self.cmbMesSpecification = CRBComboBox(self.scrollAreaWidgetContents)
        self.cmbMesSpecification.setEnabled(True)
        self.cmbMesSpecification.setObjectName(_fromUtf8("cmbMesSpecification"))
        self.gridLayout.addWidget(self.cmbMesSpecification, 2, 1, 1, 2)
        self.cmbHTG = CRBComboBox(self.scrollAreaWidgetContents)
        self.cmbHTG.setEnabled(False)
        self.cmbHTG.setObjectName(_fromUtf8("cmbHTG"))
        self.gridLayout.addWidget(self.cmbHTG, 1, 1, 1, 2)
        self.MESLayout = QtGui.QHBoxLayout()
        self.MESLayout.setObjectName(_fromUtf8("MESLayout"))
        self.cmbMes = CMESComboBox(self.scrollAreaWidgetContents)
        self.cmbMes.setObjectName(_fromUtf8("cmbMes"))
        self.MESLayout.addWidget(self.cmbMes)
        self.gridLayout.addLayout(self.MESLayout, 0, 1, 1, 2)
        spacerItem2 = QtGui.QSpacerItem(0, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 5, 3, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.lblMes.setBuddy(self.cmbMes)
        self.lblMesSpecification.setBuddy(self.cmbMesSpecification)

        self.retranslateUi(EventMesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(EventMesPageWidget)

    def retranslateUi(self, EventMesPageWidget):
        EventMesPageWidget.setWindowTitle(_translate("EventMesPageWidget", "Form", None))
        self.grpRelatedEvents.setTitle(_translate("EventMesPageWidget", "Стандарты и диагнозы других отделений", None))
        self.lblMes.setText(_translate("EventMesPageWidget", "МЭС", None))
        self.chkHTG.setText(_translate("EventMesPageWidget", "ВМП", None))
        self.lblMesSpecification.setText(_translate("EventMesPageWidget", "Особенности выполнения МЭС", None))
        self.btnCheckMes.setText(_translate("EventMesPageWidget", "Проверить выполнение стандарта", None))
        self.btnShowMes.setText(_translate("EventMesPageWidget", "Показать требования стандарта", None))

from library.MES.MESComboBox import CMESComboBox
from library.TableView import CTableView
from library.crbcombobox import CRBComboBox
