# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ResourcesDockContent.ui'
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(452, 790)
        self.hboxlayout = QtGui.QHBoxLayout(Form)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(0)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.splitterMain = QtGui.QSplitter(Form)
        self.splitterMain.setOrientation(QtCore.Qt.Vertical)
        self.splitterMain.setChildrenCollapsible(False)
        self.splitterMain.setObjectName(_fromUtf8("splitterMain"))
        self.splitterOrgs = QtGui.QSplitter(self.splitterMain)
        self.splitterOrgs.setOrientation(QtCore.Qt.Horizontal)
        self.splitterOrgs.setHandleWidth(2)
        self.splitterOrgs.setChildrenCollapsible(False)
        self.splitterOrgs.setObjectName(_fromUtf8("splitterOrgs"))
        self.treeOrgStructure = CTreeView(self.splitterOrgs)
        self.treeOrgStructure.setObjectName(_fromUtf8("treeOrgStructure"))
        self.treeOrgPersonnel = CTreeView(self.splitterOrgs)
        self.treeOrgPersonnel.setObjectName(_fromUtf8("treeOrgPersonnel"))
        self.calendarWidget = CCalendarWidget(self.splitterMain)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calendarWidget.sizePolicy().hasHeightForWidth())
        self.calendarWidget.setSizePolicy(sizePolicy)
        self.calendarWidget.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.calendarWidget.setObjectName(_fromUtf8("calendarWidget"))
        self.tabPlace = QtGui.QTabWidget(self.splitterMain)
        self.tabPlace.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabPlace.setObjectName(_fromUtf8("tabPlace"))
        self.tabAmbulatory = QtGui.QWidget()
        self.tabAmbulatory.setObjectName(_fromUtf8("tabAmbulatory"))
        self.gridlayout = QtGui.QGridLayout(self.tabAmbulatory)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.splitterAmb = QtGui.QSplitter(self.tabAmbulatory)
        self.splitterAmb.setOrientation(QtCore.Qt.Vertical)
        self.splitterAmb.setObjectName(_fromUtf8("splitterAmb"))
        self.frmAmbTimeTable = QtGui.QFrame(self.splitterAmb)
        self.frmAmbTimeTable.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmAmbTimeTable.setFrameShadow(QtGui.QFrame.Plain)
        self.frmAmbTimeTable.setObjectName(_fromUtf8("frmAmbTimeTable"))
        self.gridLayout_2 = QtGui.QGridLayout(self.frmAmbTimeTable)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.eqPanelWidget = CEQPanelWidget(self.frmAmbTimeTable)
        self.eqPanelWidget.setObjectName(_fromUtf8("eqPanelWidget"))
        self.gridLayout = QtGui.QGridLayout(self.eqPanelWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gridLayout_2.addWidget(self.eqPanelWidget, 1, 0, 1, 1)
        self.btnRefreshAmb = QtGui.QToolButton(self.frmAmbTimeTable)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        font.setStrikeOut(True)
        self.btnRefreshAmb.setFont(font)
        self.btnRefreshAmb.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/new/prefix1/icons/refresh.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnRefreshAmb.setIcon(icon)
        self.btnRefreshAmb.setObjectName(_fromUtf8("btnRefreshAmb"))
        self.gridLayout_2.addWidget(self.btnRefreshAmb, 1, 1, 1, 1)
        self.tblAmbTimeTable = CTableView(self.frmAmbTimeTable)
        self.tblAmbTimeTable.setObjectName(_fromUtf8("tblAmbTimeTable"))
        self.gridLayout_2.addWidget(self.tblAmbTimeTable, 0, 0, 1, 2)
        self.frmAmbQueue = QtGui.QFrame(self.splitterAmb)
        self.frmAmbQueue.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmAmbQueue.setFrameShadow(QtGui.QFrame.Raised)
        self.frmAmbQueue.setObjectName(_fromUtf8("frmAmbQueue"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frmAmbQueue)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tblAmbQueue = CTableView(self.frmAmbQueue)
        self.tblAmbQueue.setObjectName(_fromUtf8("tblAmbQueue"))
        self.verticalLayout_2.addWidget(self.tblAmbQueue)
        self.gridlayout.addWidget(self.splitterAmb, 1, 0, 1, 1)
        self.tabPlace.addTab(self.tabAmbulatory, _fromUtf8(""))
        self.tabHome = QtGui.QWidget()
        self.tabHome.setObjectName(_fromUtf8("tabHome"))
        self.gridlayout1 = QtGui.QGridLayout(self.tabHome)
        self.gridlayout1.setMargin(4)
        self.gridlayout1.setSpacing(0)
        self.gridlayout1.setObjectName(_fromUtf8("gridlayout1"))
        self.splitterHome = QtGui.QSplitter(self.tabHome)
        self.splitterHome.setOrientation(QtCore.Qt.Vertical)
        self.splitterHome.setObjectName(_fromUtf8("splitterHome"))
        self.frmHomeTimeTable = QtGui.QFrame(self.splitterHome)
        self.frmHomeTimeTable.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmHomeTimeTable.setFrameShadow(QtGui.QFrame.Plain)
        self.frmHomeTimeTable.setObjectName(_fromUtf8("frmHomeTimeTable"))
        self.gridLayout_3 = QtGui.QGridLayout(self.frmHomeTimeTable)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.btnRefreshHome = QtGui.QToolButton(self.frmHomeTimeTable)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        font.setStrikeOut(True)
        self.btnRefreshHome.setFont(font)
        self.btnRefreshHome.setText(_fromUtf8(""))
        self.btnRefreshHome.setIcon(icon)
        self.btnRefreshHome.setObjectName(_fromUtf8("btnRefreshHome"))
        self.gridLayout_3.addWidget(self.btnRefreshHome, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 1, 0, 1, 1)
        self.tblHomeTimeTable = CTableView(self.frmHomeTimeTable)
        self.tblHomeTimeTable.setObjectName(_fromUtf8("tblHomeTimeTable"))
        self.gridLayout_3.addWidget(self.tblHomeTimeTable, 0, 0, 1, 2)
        self.frmHomeQueue = QtGui.QFrame(self.splitterHome)
        self.frmHomeQueue.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmHomeQueue.setFrameShadow(QtGui.QFrame.Raised)
        self.frmHomeQueue.setObjectName(_fromUtf8("frmHomeQueue"))
        self.vboxlayout = QtGui.QVBoxLayout(self.frmHomeQueue)
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(0)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.tblHomeQueue = CTableView(self.frmHomeQueue)
        self.tblHomeQueue.setObjectName(_fromUtf8("tblHomeQueue"))
        self.vboxlayout.addWidget(self.tblHomeQueue)
        self.gridlayout1.addWidget(self.splitterHome, 0, 0, 1, 1)
        self.tabPlace.addTab(self.tabHome, _fromUtf8(""))
        self.tabExpert = QtGui.QWidget()
        self.tabExpert.setObjectName(_fromUtf8("tabExpert"))
        self.tabPlace.addTab(self.tabExpert, _fromUtf8(""))
        self.hboxlayout.addWidget(self.splitterMain)

        self.retranslateUi(Form)
        self.tabPlace.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.treeOrgStructure, self.treeOrgPersonnel)
        Form.setTabOrder(self.treeOrgPersonnel, self.calendarWidget)
        Form.setTabOrder(self.calendarWidget, self.tabPlace)
        Form.setTabOrder(self.tabPlace, self.tblAmbTimeTable)
        Form.setTabOrder(self.tblAmbTimeTable, self.tblAmbQueue)
        Form.setTabOrder(self.tblAmbQueue, self.tblHomeTimeTable)
        Form.setTabOrder(self.tblHomeTimeTable, self.tblHomeQueue)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.btnRefreshAmb.setToolTip(_translate("Form", "Обновить список номерков", None))
        self.tabPlace.setTabText(self.tabPlace.indexOf(self.tabAmbulatory), _translate("Form", "Амбулаторно", None))
        self.btnRefreshHome.setToolTip(_translate("Form", "Обновить список номерков", None))
        self.tabPlace.setTabText(self.tabPlace.indexOf(self.tabHome), _translate("Form", "На дому", None))
        self.tabPlace.setTabText(self.tabPlace.indexOf(self.tabExpert), _translate("Form", "КЭР", None))

from library.ElectronicQueue.EQPanelWidget import CEQPanelWidget
from library.TableView import CTableView
from library.TreeView import CTreeView
from library.calendar import CCalendarWidget
