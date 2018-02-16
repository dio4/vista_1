# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'JobTicketChooserDialog.ui'
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

class Ui_JobTicketChooserDialog(object):
    def setupUi(self, JobTicketChooserDialog):
        JobTicketChooserDialog.setObjectName(_fromUtf8("JobTicketChooserDialog"))
        JobTicketChooserDialog.resize(702, 457)
        JobTicketChooserDialog.setSizeGripEnabled(True)
        JobTicketChooserDialog.setModal(True)
        self.verticalLayout_3 = QtGui.QVBoxLayout(JobTicketChooserDialog)
        self.verticalLayout_3.setMargin(4)
        self.verticalLayout_3.setSpacing(4)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.splitter = QtGui.QSplitter(JobTicketChooserDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.treeJobTypes = QtGui.QTreeView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeJobTypes.sizePolicy().hasHeightForWidth())
        self.treeJobTypes.setSizePolicy(sizePolicy)
        self.treeJobTypes.setSizeIncrement(QtCore.QSize(1, 0))
        self.treeJobTypes.setObjectName(_fromUtf8("treeJobTypes"))
        self.tabWidget = QtGui.QTabWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabOld = QtGui.QWidget()
        self.tabOld.setObjectName(_fromUtf8("tabOld"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.tabOld)
        self.horizontalLayout.setMargin(4)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tblOldTickets = CTableView(self.tabOld)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblOldTickets.sizePolicy().hasHeightForWidth())
        self.tblOldTickets.setSizePolicy(sizePolicy)
        self.tblOldTickets.setSizeIncrement(QtCore.QSize(2, 0))
        self.tblOldTickets.setObjectName(_fromUtf8("tblOldTickets"))
        self.horizontalLayout.addWidget(self.tblOldTickets)
        self.tabWidget.addTab(self.tabOld, _fromUtf8(""))
        self.tabNew = QtGui.QWidget()
        self.tabNew.setObjectName(_fromUtf8("tabNew"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.tabNew)
        self.horizontalLayout_2.setMargin(4)
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.widget = QtGui.QWidget(self.tabNew)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.clnCalendar = CCalendarWidget(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clnCalendar.sizePolicy().hasHeightForWidth())
        self.clnCalendar.setSizePolicy(sizePolicy)
        self.clnCalendar.setFirstDayOfWeek(QtCore.Qt.Monday)
        self.clnCalendar.setGridVisible(False)
        self.clnCalendar.setVerticalHeaderFormat(QtGui.QCalendarWidget.ISOWeekNumbers)
        self.clnCalendar.setObjectName(_fromUtf8("clnCalendar"))
        self.verticalLayout.addWidget(self.clnCalendar)
        self.gpSuperviseUnit = QtGui.QGroupBox(self.widget)
        self.gpSuperviseUnit.setObjectName(_fromUtf8("gpSuperviseUnit"))
        self.gridLayout = QtGui.QGridLayout(self.gpSuperviseUnit)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblJobDescription = QtGui.QLabel(self.gpSuperviseUnit)
        self.lblJobDescription.setText(_fromUtf8(""))
        self.lblJobDescription.setAlignment(QtCore.Qt.AlignCenter)
        self.lblJobDescription.setWordWrap(True)
        self.lblJobDescription.setObjectName(_fromUtf8("lblJobDescription"))
        self.gridLayout.addWidget(self.lblJobDescription, 0, 0, 1, 4)
        self.lblCurrentSuperviseUnitValue = QtGui.QLabel(self.gpSuperviseUnit)
        self.lblCurrentSuperviseUnitValue.setObjectName(_fromUtf8("lblCurrentSuperviseUnitValue"))
        self.gridLayout.addWidget(self.lblCurrentSuperviseUnitValue, 1, 1, 1, 3)
        self.lblCurrentSuperviseUnit = QtGui.QLabel(self.gpSuperviseUnit)
        self.lblCurrentSuperviseUnit.setObjectName(_fromUtf8("lblCurrentSuperviseUnit"))
        self.gridLayout.addWidget(self.lblCurrentSuperviseUnit, 1, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.gpSuperviseUnit)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblLimitSuperviseUnitValue = QtGui.QLabel(self.groupBox)
        self.lblLimitSuperviseUnitValue.setObjectName(_fromUtf8("lblLimitSuperviseUnitValue"))
        self.gridLayout_2.addWidget(self.lblLimitSuperviseUnitValue, 0, 3, 1, 1)
        self.lblFromSuperviseUnit = QtGui.QLabel(self.groupBox)
        self.lblFromSuperviseUnit.setObjectName(_fromUtf8("lblFromSuperviseUnit"))
        self.gridLayout_2.addWidget(self.lblFromSuperviseUnit, 0, 2, 1, 1)
        self.lblFreePersonQuota = QtGui.QLabel(self.groupBox)
        self.lblFreePersonQuota.setObjectName(_fromUtf8("lblFreePersonQuota"))
        self.gridLayout_2.addWidget(self.lblFreePersonQuota, 1, 1, 1, 1)
        self.lblFromPersonQuota = QtGui.QLabel(self.groupBox)
        self.lblFromPersonQuota.setObjectName(_fromUtf8("lblFromPersonQuota"))
        self.gridLayout_2.addWidget(self.lblFromPersonQuota, 1, 2, 1, 1)
        self.lblPersonQuota = QtGui.QLabel(self.groupBox)
        self.lblPersonQuota.setObjectName(_fromUtf8("lblPersonQuota"))
        self.gridLayout_2.addWidget(self.lblPersonQuota, 1, 0, 1, 1)
        self.lblLimitPersonQuota = QtGui.QLabel(self.groupBox)
        self.lblLimitPersonQuota.setObjectName(_fromUtf8("lblLimitPersonQuota"))
        self.gridLayout_2.addWidget(self.lblLimitPersonQuota, 1, 3, 1, 1)
        self.lblFreeSuperviseUnit = QtGui.QLabel(self.groupBox)
        self.lblFreeSuperviseUnit.setObjectName(_fromUtf8("lblFreeSuperviseUnit"))
        self.gridLayout_2.addWidget(self.lblFreeSuperviseUnit, 0, 0, 1, 1)
        self.lblOnDayLimitTitle = QtGui.QLabel(self.groupBox)
        self.lblOnDayLimitTitle.setObjectName(_fromUtf8("lblOnDayLimitTitle"))
        self.gridLayout_2.addWidget(self.lblOnDayLimitTitle, 2, 0, 1, 1)
        self.lblFreeSuperviseUnitValue = QtGui.QLabel(self.groupBox)
        self.lblFreeSuperviseUnitValue.setObjectName(_fromUtf8("lblFreeSuperviseUnitValue"))
        self.gridLayout_2.addWidget(self.lblFreeSuperviseUnitValue, 0, 1, 1, 1)
        self.lblOnDayActionTypes = QtGui.QLabel(self.groupBox)
        self.lblOnDayActionTypes.setText(_fromUtf8(""))
        self.lblOnDayActionTypes.setWordWrap(True)
        self.lblOnDayActionTypes.setObjectName(_fromUtf8("lblOnDayActionTypes"))
        self.gridLayout_2.addWidget(self.lblOnDayActionTypes, 3, 0, 1, 1)
        self.lblOnDayLimits = QtGui.QLabel(self.groupBox)
        self.lblOnDayLimits.setText(_fromUtf8(""))
        self.lblOnDayLimits.setAlignment(QtCore.Qt.AlignCenter)
        self.lblOnDayLimits.setObjectName(_fromUtf8("lblOnDayLimits"))
        self.gridLayout_2.addWidget(self.lblOnDayLimits, 3, 1, 1, 3)
        self.gridLayout.addWidget(self.groupBox, 2, 0, 1, 4)
        self.verticalLayout.addWidget(self.gpSuperviseUnit)
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.cmbSubdivFilter = QtGui.QComboBox(self.widget)
        self.cmbSubdivFilter.setObjectName(_fromUtf8("cmbSubdivFilter"))
        self.verticalLayout.addWidget(self.cmbSubdivFilter)
        self.btnApplyFilter = QtGui.QPushButton(self.widget)
        self.btnApplyFilter.setObjectName(_fromUtf8("btnApplyFilter"))
        self.verticalLayout.addWidget(self.btnApplyFilter)
        spacerItem = QtGui.QSpacerItem(20, 152, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2.addWidget(self.widget)
        self.tblTickets = CTableView(self.tabNew)
        self.tblTickets.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblTickets.sizePolicy().hasHeightForWidth())
        self.tblTickets.setSizePolicy(sizePolicy)
        self.tblTickets.setSizeIncrement(QtCore.QSize(2, 0))
        self.tblTickets.setObjectName(_fromUtf8("tblTickets"))
        self.horizontalLayout_2.addWidget(self.tblTickets)
        self.tabWidget.addTab(self.tabNew, _fromUtf8(""))
        self.verticalLayout_3.addWidget(self.splitter)
        self.buttonBox = QtGui.QDialogButtonBox(JobTicketChooserDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)
        self.buttonBox.raise_()
        self.splitter.raise_()

        self.retranslateUi(JobTicketChooserDialog)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), JobTicketChooserDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), JobTicketChooserDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(JobTicketChooserDialog)
        JobTicketChooserDialog.setTabOrder(self.treeJobTypes, self.tabWidget)
        JobTicketChooserDialog.setTabOrder(self.tabWidget, self.tblOldTickets)
        JobTicketChooserDialog.setTabOrder(self.tblOldTickets, self.clnCalendar)
        JobTicketChooserDialog.setTabOrder(self.clnCalendar, self.tblTickets)
        JobTicketChooserDialog.setTabOrder(self.tblTickets, self.buttonBox)

    def retranslateUi(self, JobTicketChooserDialog):
        JobTicketChooserDialog.setWindowTitle(_translate("JobTicketChooserDialog", "Выберите работу-дату-место", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabOld), _translate("JobTicketChooserDialog", "Ранее назначенные", None))
        self.gpSuperviseUnit.setTitle(_translate("JobTicketChooserDialog", "Информация по квотам и УЕТ", None))
        self.lblCurrentSuperviseUnitValue.setText(_translate("JobTicketChooserDialog", "0", None))
        self.lblCurrentSuperviseUnit.setText(_translate("JobTicketChooserDialog", "УЕТ текущей услуги:", None))
        self.groupBox.setTitle(_translate("JobTicketChooserDialog", "Остатки", None))
        self.lblLimitSuperviseUnitValue.setText(_translate("JobTicketChooserDialog", "0", None))
        self.lblFromSuperviseUnit.setText(_translate("JobTicketChooserDialog", "из", None))
        self.lblFreePersonQuota.setText(_translate("JobTicketChooserDialog", "0", None))
        self.lblFromPersonQuota.setText(_translate("JobTicketChooserDialog", "из", None))
        self.lblPersonQuota.setText(_translate("JobTicketChooserDialog", "Врачебная квота:", None))
        self.lblLimitPersonQuota.setText(_translate("JobTicketChooserDialog", "0", None))
        self.lblFreeSuperviseUnit.setText(_translate("JobTicketChooserDialog", "УЕТ:", None))
        self.lblOnDayLimitTitle.setText(_translate("JobTicketChooserDialog", "Суточная квота:", None))
        self.lblFreeSuperviseUnitValue.setText(_translate("JobTicketChooserDialog", "0", None))
        self.label.setText(_translate("JobTicketChooserDialog", "Фильтр подразделений", None))
        self.btnApplyFilter.setText(_translate("JobTicketChooserDialog", "Применить", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabNew), _translate("JobTicketChooserDialog", "Новые", None))

from library.TableView import CTableView
from library.calendar import CCalendarWidget