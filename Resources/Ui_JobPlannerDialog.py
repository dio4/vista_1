# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'JobPlannerDialog.ui'
#
# Created: Tue Sep 23 16:34:36 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_JobPlannerDialog(object):
    def setupUi(self, JobPlannerDialog):
        JobPlannerDialog.setObjectName(_fromUtf8("JobPlannerDialog"))
        JobPlannerDialog.resize(656, 581)
        self.verticalLayout = QtGui.QVBoxLayout(JobPlannerDialog)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter_2 = QtGui.QSplitter(JobPlannerDialog)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setChildrenCollapsible(False)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.splitter = QtGui.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.calendar = CCalendarWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calendar.sizePolicy().hasHeightForWidth())
        self.calendar.setSizePolicy(sizePolicy)
        self.calendar.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.calendar.setGridVisible(False)
        self.calendar.setObjectName(_fromUtf8("calendar"))
        self.treeOrgStructure = QtGui.QTreeView(self.splitter)
        self.treeOrgStructure.setObjectName(_fromUtf8("treeOrgStructure"))
        self.tblJobs = CTableView(self.splitter)
        self.tblJobs.setObjectName(_fromUtf8("tblJobs"))
        self.widget = QtGui.QWidget(self.splitter_2)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblJobPlan = CJobPlanTable(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblJobPlan.sizePolicy().hasHeightForWidth())
        self.tblJobPlan.setSizePolicy(sizePolicy)
        self.tblJobPlan.setObjectName(_fromUtf8("tblJobPlan"))
        self.gridLayout.addWidget(self.tblJobPlan, 0, 0, 1, 5)
        self.btnFill = QtGui.QPushButton(self.widget)
        self.btnFill.setObjectName(_fromUtf8("btnFill"))
        self.gridLayout.addWidget(self.btnFill, 1, 0, 1, 1)
        self.btnDuplicate = QtGui.QPushButton(self.widget)
        self.btnDuplicate.setObjectName(_fromUtf8("btnDuplicate"))
        self.gridLayout.addWidget(self.btnDuplicate, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(273, 23, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 1)
        self.btnClose = QtGui.QPushButton(self.widget)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 1, 4, 1, 1)
        self.btnDublicateWeek = QtGui.QPushButton(self.widget)
        self.btnDublicateWeek.setObjectName(_fromUtf8("btnDublicateWeek"))
        self.gridLayout.addWidget(self.btnDublicateWeek, 1, 2, 1, 1)
        self.verticalLayout.addWidget(self.splitter_2)

        self.retranslateUi(JobPlannerDialog)
        QtCore.QObject.connect(self.btnClose, QtCore.SIGNAL(_fromUtf8("clicked()")), JobPlannerDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(JobPlannerDialog)
        JobPlannerDialog.setTabOrder(self.calendar, self.treeOrgStructure)
        JobPlannerDialog.setTabOrder(self.treeOrgStructure, self.tblJobs)
        JobPlannerDialog.setTabOrder(self.tblJobs, self.tblJobPlan)
        JobPlannerDialog.setTabOrder(self.tblJobPlan, self.btnFill)
        JobPlannerDialog.setTabOrder(self.btnFill, self.btnClose)

    def retranslateUi(self, JobPlannerDialog):
        JobPlannerDialog.setWindowTitle(_translate("JobPlannerDialog", "Планирование ресурсов", None))
        self.btnFill.setText(_translate("JobPlannerDialog", "Заполнить (F9)", None))
        self.btnFill.setShortcut(_translate("JobPlannerDialog", "F9", None))
        self.btnDuplicate.setText(_translate("JobPlannerDialog", "Копировать с предыдущего месяца", None))
        self.btnClose.setText(_translate("JobPlannerDialog", "Закрыть", None))
        self.btnDublicateWeek.setText(_translate("JobPlannerDialog", "Копировать с выбранной недели", None))
        self.btnFill.setAutoDefault(False)
        self.btnDuplicate.setAutoDefault(False)
        self.btnClose.setAutoDefault(False)
        self.btnDublicateWeek.setAutoDefault(False)

from JobPlanTable import CJobPlanTable
from library.TableView import CTableView
from library.calendar import CCalendarWidget
