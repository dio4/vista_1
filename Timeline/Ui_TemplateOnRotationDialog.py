# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TemplateOnRotationDialog.ui'
#
# Created: Mon Nov  2 16:54:18 2015
#      by: PyQt4 UI code generator 4.11.3
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

class Ui_TemplateOnRotationDialog(object):
    def setupUi(self, TemplateOnRotationDialog):
        TemplateOnRotationDialog.setObjectName(_fromUtf8("TemplateOnRotationDialog"))
        TemplateOnRotationDialog.resize(669, 419)
        self.gridLayout = QtGui.QGridLayout(TemplateOnRotationDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.grbOnePlan = QtGui.QGroupBox(TemplateOnRotationDialog)
        self.grbOnePlan.setTitle(_fromUtf8(""))
        self.grbOnePlan.setObjectName(_fromUtf8("grbOnePlan"))
        self.gridLayout_6 = QtGui.QGridLayout(self.grbOnePlan)
        self.gridLayout_6.setMargin(4)
        self.gridLayout_6.setSpacing(4)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.edtAmbPlan12 = QtGui.QSpinBox(self.grbOnePlan)
        self.edtAmbPlan12.setEnabled(False)
        self.edtAmbPlan12.setMaximum(9999)
        self.edtAmbPlan12.setObjectName(_fromUtf8("edtAmbPlan12"))
        self.gridLayout_6.addWidget(self.edtAmbPlan12, 3, 3, 1, 1)
        self.edtHomeTimeRange1 = CTimeRangeEdit(self.grbOnePlan)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtHomeTimeRange1.sizePolicy().hasHeightForWidth())
        self.edtHomeTimeRange1.setSizePolicy(sizePolicy)
        self.edtHomeTimeRange1.setMaximumSize(QtCore.QSize(90, 16777215))
        self.edtHomeTimeRange1.setMaxLength(13)
        self.edtHomeTimeRange1.setObjectName(_fromUtf8("edtHomeTimeRange1"))
        self.gridLayout_6.addWidget(self.edtHomeTimeRange1, 2, 10, 1, 1)
        self.edtAmbPlan1 = QtGui.QSpinBox(self.grbOnePlan)
        self.edtAmbPlan1.setMaximum(9999)
        self.edtAmbPlan1.setObjectName(_fromUtf8("edtAmbPlan1"))
        self.gridLayout_6.addWidget(self.edtAmbPlan1, 2, 3, 1, 1)
        self.edtAmbOffice12 = QtGui.QLineEdit(self.grbOnePlan)
        self.edtAmbOffice12.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAmbOffice12.sizePolicy().hasHeightForWidth())
        self.edtAmbOffice12.setSizePolicy(sizePolicy)
        self.edtAmbOffice12.setMaximumSize(QtCore.QSize(70, 16777215))
        self.edtAmbOffice12.setMaxLength(8)
        self.edtAmbOffice12.setObjectName(_fromUtf8("edtAmbOffice12"))
        self.gridLayout_6.addWidget(self.edtAmbOffice12, 3, 2, 1, 1)
        self.lblAmbPlan = QtGui.QLabel(self.grbOnePlan)
        self.lblAmbPlan.setAlignment(QtCore.Qt.AlignCenter)
        self.lblAmbPlan.setObjectName(_fromUtf8("lblAmbPlan"))
        self.gridLayout_6.addWidget(self.lblAmbPlan, 1, 3, 1, 1)
        self.label_1 = QtGui.QLabel(self.grbOnePlan)
        self.label_1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_1.setObjectName(_fromUtf8("label_1"))
        self.gridLayout_6.addWidget(self.label_1, 2, 0, 1, 1)
        self.edtHomeTimeRange12 = CTimeRangeEdit(self.grbOnePlan)
        self.edtHomeTimeRange12.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtHomeTimeRange12.sizePolicy().hasHeightForWidth())
        self.edtHomeTimeRange12.setSizePolicy(sizePolicy)
        self.edtHomeTimeRange12.setMaximumSize(QtCore.QSize(90, 16777215))
        self.edtHomeTimeRange12.setMaxLength(13)
        self.edtHomeTimeRange12.setObjectName(_fromUtf8("edtHomeTimeRange12"))
        self.gridLayout_6.addWidget(self.edtHomeTimeRange12, 3, 10, 1, 1)
        spacerItem = QtGui.QSpacerItem(147, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem, 3, 13, 1, 1)
        self.edtAmbOffice1 = QtGui.QLineEdit(self.grbOnePlan)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAmbOffice1.sizePolicy().hasHeightForWidth())
        self.edtAmbOffice1.setSizePolicy(sizePolicy)
        self.edtAmbOffice1.setMaximumSize(QtCore.QSize(70, 16777215))
        self.edtAmbOffice1.setMaxLength(8)
        self.edtAmbOffice1.setObjectName(_fromUtf8("edtAmbOffice1"))
        self.gridLayout_6.addWidget(self.edtAmbOffice1, 2, 2, 1, 1)
        self.cmbReasonOfAbsence1 = CRBComboBox(self.grbOnePlan)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbReasonOfAbsence1.sizePolicy().hasHeightForWidth())
        self.cmbReasonOfAbsence1.setSizePolicy(sizePolicy)
        self.cmbReasonOfAbsence1.setObjectName(_fromUtf8("cmbReasonOfAbsence1"))
        self.gridLayout_6.addWidget(self.cmbReasonOfAbsence1, 2, 13, 1, 1)
        self.edtAmbTimeRange1 = CTimeRangeEdit(self.grbOnePlan)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAmbTimeRange1.sizePolicy().hasHeightForWidth())
        self.edtAmbTimeRange1.setSizePolicy(sizePolicy)
        self.edtAmbTimeRange1.setMaximumSize(QtCore.QSize(90, 16777215))
        self.edtAmbTimeRange1.setMaxLength(13)
        self.edtAmbTimeRange1.setObjectName(_fromUtf8("edtAmbTimeRange1"))
        self.gridLayout_6.addWidget(self.edtAmbTimeRange1, 2, 1, 1, 1)
        self.edtHomePlan12 = QtGui.QSpinBox(self.grbOnePlan)
        self.edtHomePlan12.setEnabled(False)
        self.edtHomePlan12.setMaximum(9999)
        self.edtHomePlan12.setObjectName(_fromUtf8("edtHomePlan12"))
        self.gridLayout_6.addWidget(self.edtHomePlan12, 3, 11, 1, 1)
        self.edtAmbTimeRange12 = CTimeRangeEdit(self.grbOnePlan)
        self.edtAmbTimeRange12.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAmbTimeRange12.sizePolicy().hasHeightForWidth())
        self.edtAmbTimeRange12.setSizePolicy(sizePolicy)
        self.edtAmbTimeRange12.setMaximumSize(QtCore.QSize(90, 16777215))
        self.edtAmbTimeRange12.setMaxLength(13)
        self.edtAmbTimeRange12.setObjectName(_fromUtf8("edtAmbTimeRange12"))
        self.gridLayout_6.addWidget(self.edtAmbTimeRange12, 3, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.grbOnePlan)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_6.addWidget(self.label_2, 3, 0, 1, 1)
        self.lblAmb = QtGui.QLabel(self.grbOnePlan)
        self.lblAmb.setAlignment(QtCore.Qt.AlignCenter)
        self.lblAmb.setObjectName(_fromUtf8("lblAmb"))
        self.gridLayout_6.addWidget(self.lblAmb, 0, 0, 1, 4)
        self.lblReasonOfAbsence1 = QtGui.QLabel(self.grbOnePlan)
        self.lblReasonOfAbsence1.setAlignment(QtCore.Qt.AlignCenter)
        self.lblReasonOfAbsence1.setObjectName(_fromUtf8("lblReasonOfAbsence1"))
        self.gridLayout_6.addWidget(self.lblReasonOfAbsence1, 0, 13, 1, 1)
        self.lblAmbHours = QtGui.QLabel(self.grbOnePlan)
        self.lblAmbHours.setAlignment(QtCore.Qt.AlignCenter)
        self.lblAmbHours.setObjectName(_fromUtf8("lblAmbHours"))
        self.gridLayout_6.addWidget(self.lblAmbHours, 1, 0, 1, 2)
        self.lblAmbCab = QtGui.QLabel(self.grbOnePlan)
        self.lblAmbCab.setAlignment(QtCore.Qt.AlignCenter)
        self.lblAmbCab.setObjectName(_fromUtf8("lblAmbCab"))
        self.gridLayout_6.addWidget(self.lblAmbCab, 1, 2, 1, 1)
        self.lblHome = QtGui.QLabel(self.grbOnePlan)
        self.lblHome.setAlignment(QtCore.Qt.AlignCenter)
        self.lblHome.setObjectName(_fromUtf8("lblHome"))
        self.gridLayout_6.addWidget(self.lblHome, 0, 10, 1, 2)
        self.lblHomePlan = QtGui.QLabel(self.grbOnePlan)
        self.lblHomePlan.setAlignment(QtCore.Qt.AlignCenter)
        self.lblHomePlan.setObjectName(_fromUtf8("lblHomePlan"))
        self.gridLayout_6.addWidget(self.lblHomePlan, 1, 11, 1, 1)
        self.lblHomeHours = QtGui.QLabel(self.grbOnePlan)
        self.lblHomeHours.setAlignment(QtCore.Qt.AlignCenter)
        self.lblHomeHours.setObjectName(_fromUtf8("lblHomeHours"))
        self.gridLayout_6.addWidget(self.lblHomeHours, 1, 10, 1, 1)
        self.lblReasonOfAbsence2 = QtGui.QLabel(self.grbOnePlan)
        self.lblReasonOfAbsence2.setAlignment(QtCore.Qt.AlignCenter)
        self.lblReasonOfAbsence2.setObjectName(_fromUtf8("lblReasonOfAbsence2"))
        self.gridLayout_6.addWidget(self.lblReasonOfAbsence2, 1, 13, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.edtAmbInterval12 = QtGui.QSpinBox(self.grbOnePlan)
        self.edtAmbInterval12.setEnabled(False)
        self.edtAmbInterval12.setObjectName(_fromUtf8("edtAmbInterval12"))
        self.horizontalLayout.addWidget(self.edtAmbInterval12)
        self.lblAmbInterval12 = QtGui.QLabel(self.grbOnePlan)
        self.lblAmbInterval12.setEnabled(False)
        self.lblAmbInterval12.setObjectName(_fromUtf8("lblAmbInterval12"))
        self.horizontalLayout.addWidget(self.lblAmbInterval12)
        self.gridLayout_6.addLayout(self.horizontalLayout, 3, 4, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.edtAmbInterInterval1 = QtGui.QSpinBox(self.grbOnePlan)
        self.edtAmbInterInterval1.setEnabled(False)
        self.edtAmbInterInterval1.setObjectName(_fromUtf8("edtAmbInterInterval1"))
        self.horizontalLayout_2.addWidget(self.edtAmbInterInterval1)
        self.lblAmbInterInterval1 = QtGui.QLabel(self.grbOnePlan)
        self.lblAmbInterInterval1.setEnabled(False)
        self.lblAmbInterInterval1.setObjectName(_fromUtf8("lblAmbInterInterval1"))
        self.horizontalLayout_2.addWidget(self.lblAmbInterInterval1)
        self.gridLayout_6.addLayout(self.horizontalLayout_2, 4, 4, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.edtAmbInterval1 = QtGui.QSpinBox(self.grbOnePlan)
        self.edtAmbInterval1.setObjectName(_fromUtf8("edtAmbInterval1"))
        self.horizontalLayout_3.addWidget(self.edtAmbInterval1)
        self.lblAmbInterval1 = QtGui.QLabel(self.grbOnePlan)
        self.lblAmbInterval1.setObjectName(_fromUtf8("lblAmbInterval1"))
        self.horizontalLayout_3.addWidget(self.lblAmbInterval1)
        self.gridLayout_6.addLayout(self.horizontalLayout_3, 2, 4, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.edtHomeInterval12 = QtGui.QSpinBox(self.grbOnePlan)
        self.edtHomeInterval12.setEnabled(False)
        self.edtHomeInterval12.setObjectName(_fromUtf8("edtHomeInterval12"))
        self.horizontalLayout_4.addWidget(self.edtHomeInterval12)
        self.lblHomeInterval12 = QtGui.QLabel(self.grbOnePlan)
        self.lblHomeInterval12.setEnabled(False)
        self.lblHomeInterval12.setObjectName(_fromUtf8("lblHomeInterval12"))
        self.horizontalLayout_4.addWidget(self.lblHomeInterval12)
        self.gridLayout_6.addLayout(self.horizontalLayout_4, 3, 12, 1, 1)
        self.edtHomePlan1 = QtGui.QSpinBox(self.grbOnePlan)
        self.edtHomePlan1.setMaximum(9999)
        self.edtHomePlan1.setObjectName(_fromUtf8("edtHomePlan1"))
        self.gridLayout_6.addWidget(self.edtHomePlan1, 2, 11, 1, 1)
        self.edtAmbOfficeInter = QtGui.QLineEdit(self.grbOnePlan)
        self.edtAmbOfficeInter.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAmbOfficeInter.sizePolicy().hasHeightForWidth())
        self.edtAmbOfficeInter.setSizePolicy(sizePolicy)
        self.edtAmbOfficeInter.setMaximumSize(QtCore.QSize(70, 16777215))
        self.edtAmbOfficeInter.setMaxLength(8)
        self.edtAmbOfficeInter.setObjectName(_fromUtf8("edtAmbOfficeInter"))
        self.gridLayout_6.addWidget(self.edtAmbOfficeInter, 4, 2, 1, 1)
        self.edtAmbInterPlan1 = QtGui.QSpinBox(self.grbOnePlan)
        self.edtAmbInterPlan1.setEnabled(False)
        self.edtAmbInterPlan1.setMaximum(9999)
        self.edtAmbInterPlan1.setObjectName(_fromUtf8("edtAmbInterPlan1"))
        self.gridLayout_6.addWidget(self.edtAmbInterPlan1, 4, 3, 1, 1)
        self.label_3 = QtGui.QLabel(self.grbOnePlan)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_6.addWidget(self.label_3, 4, 1, 1, 1)
        self.btnAmbColor1 = CColorPicker(self.grbOnePlan)
        self.btnAmbColor1.setText(_fromUtf8(""))
        self.btnAmbColor1.setObjectName(_fromUtf8("btnAmbColor1"))
        self.gridLayout_6.addWidget(self.btnAmbColor1, 2, 7, 1, 1)
        self.btnAmbColor12 = CColorPicker(self.grbOnePlan)
        self.btnAmbColor12.setEnabled(False)
        self.btnAmbColor12.setText(_fromUtf8(""))
        self.btnAmbColor12.setObjectName(_fromUtf8("btnAmbColor12"))
        self.gridLayout_6.addWidget(self.btnAmbColor12, 3, 7, 1, 1)
        self.btnAmbInterColor1 = CColorPicker(self.grbOnePlan)
        self.btnAmbInterColor1.setEnabled(False)
        self.btnAmbInterColor1.setText(_fromUtf8(""))
        self.btnAmbInterColor1.setObjectName(_fromUtf8("btnAmbInterColor1"))
        self.gridLayout_6.addWidget(self.btnAmbInterColor1, 4, 7, 1, 1)
        self.label_4 = QtGui.QLabel(self.grbOnePlan)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_6.addWidget(self.label_4, 1, 4, 1, 1)
        self.label_5 = QtGui.QLabel(self.grbOnePlan)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_6.addWidget(self.label_5, 1, 12, 1, 1)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.edtHomeInterval1 = QtGui.QSpinBox(self.grbOnePlan)
        self.edtHomeInterval1.setObjectName(_fromUtf8("edtHomeInterval1"))
        self.horizontalLayout_5.addWidget(self.edtHomeInterval1)
        self.lblHomeInterval1 = QtGui.QLabel(self.grbOnePlan)
        self.lblHomeInterval1.setObjectName(_fromUtf8("lblHomeInterval1"))
        self.horizontalLayout_5.addWidget(self.lblHomeInterval1)
        self.gridLayout_6.addLayout(self.horizontalLayout_5, 2, 12, 1, 1)
        self.line = QtGui.QFrame(self.grbOnePlan)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout_6.addWidget(self.line, 0, 9, 5, 1)
        self.chkNotExternalSystem1 = QtGui.QCheckBox(self.grbOnePlan)
        self.chkNotExternalSystem1.setText(_fromUtf8(""))
        self.chkNotExternalSystem1.setObjectName(_fromUtf8("chkNotExternalSystem1"))
        self.gridLayout_6.addWidget(self.chkNotExternalSystem1, 2, 8, 1, 1)
        self.chkNotExternalSystem12 = QtGui.QCheckBox(self.grbOnePlan)
        self.chkNotExternalSystem12.setEnabled(False)
        self.chkNotExternalSystem12.setText(_fromUtf8(""))
        self.chkNotExternalSystem12.setObjectName(_fromUtf8("chkNotExternalSystem12"))
        self.gridLayout_6.addWidget(self.chkNotExternalSystem12, 3, 8, 1, 1)
        self.lblNotExternalSystem = QtGui.QLabel(self.grbOnePlan)
        self.lblNotExternalSystem.setObjectName(_fromUtf8("lblNotExternalSystem"))
        self.gridLayout_6.addWidget(self.lblNotExternalSystem, 1, 8, 1, 1)
        self.chkInterNotExternalSystem1 = QtGui.QCheckBox(self.grbOnePlan)
        self.chkInterNotExternalSystem1.setEnabled(False)
        self.chkInterNotExternalSystem1.setText(_fromUtf8(""))
        self.chkInterNotExternalSystem1.setObjectName(_fromUtf8("chkInterNotExternalSystem1"))
        self.gridLayout_6.addWidget(self.chkInterNotExternalSystem1, 4, 8, 1, 1)
        self.gridLayout.addWidget(self.grbOnePlan, 0, 0, 1, 3)
        self.lblCountSelectedDays = QtGui.QLabel(TemplateOnRotationDialog)
        self.lblCountSelectedDays.setMaximumSize(QtCore.QSize(16777215, 20))
        self.lblCountSelectedDays.setAlignment(QtCore.Qt.AlignCenter)
        self.lblCountSelectedDays.setObjectName(_fromUtf8("lblCountSelectedDays"))
        self.gridLayout.addWidget(self.lblCountSelectedDays, 3, 2, 1, 1)
        self.calendarTemplateOnRotation = CCalendarWidget(TemplateOnRotationDialog)
        self.calendarTemplateOnRotation.setObjectName(_fromUtf8("calendarTemplateOnRotation"))
        self.gridLayout.addWidget(self.calendarTemplateOnRotation, 1, 0, 4, 1)
        self.lblSelectedDays = QtGui.QLabel(TemplateOnRotationDialog)
        self.lblSelectedDays.setText(_fromUtf8(""))
        self.lblSelectedDays.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblSelectedDays.setWordWrap(True)
        self.lblSelectedDays.setObjectName(_fromUtf8("lblSelectedDays"))
        self.gridLayout.addWidget(self.lblSelectedDays, 2, 1, 1, 2)
        self.label = QtGui.QLabel(TemplateOnRotationDialog)
        self.label.setMaximumSize(QtCore.QSize(16777215, 25))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 1, 1, 2)
        self.btnClear = QtGui.QPushButton(TemplateOnRotationDialog)
        self.btnClear.setObjectName(_fromUtf8("btnClear"))
        self.gridLayout.addWidget(self.btnClear, 4, 2, 1, 1)
        self.chkFillRedDays = QtGui.QCheckBox(TemplateOnRotationDialog)
        self.chkFillRedDays.setChecked(True)
        self.chkFillRedDays.setObjectName(_fromUtf8("chkFillRedDays"))
        self.gridLayout.addWidget(self.chkFillRedDays, 5, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(TemplateOnRotationDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 9, 0, 1, 1)
        self.chkAmbSecondPeriod = QtGui.QCheckBox(TemplateOnRotationDialog)
        self.chkAmbSecondPeriod.setObjectName(_fromUtf8("chkAmbSecondPeriod"))
        self.gridLayout.addWidget(self.chkAmbSecondPeriod, 6, 0, 1, 1)
        self.chkHomeSecondPeriod = QtGui.QCheckBox(TemplateOnRotationDialog)
        self.chkHomeSecondPeriod.setObjectName(_fromUtf8("chkHomeSecondPeriod"))
        self.gridLayout.addWidget(self.chkHomeSecondPeriod, 8, 0, 1, 1)
        self.chkAmbInterPeriod = QtGui.QCheckBox(TemplateOnRotationDialog)
        self.chkAmbInterPeriod.setEnabled(False)
        self.chkAmbInterPeriod.setObjectName(_fromUtf8("chkAmbInterPeriod"))
        self.gridLayout.addWidget(self.chkAmbInterPeriod, 7, 0, 1, 1)

        self.retranslateUi(TemplateOnRotationDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TemplateOnRotationDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TemplateOnRotationDialog.reject)
        QtCore.QObject.connect(self.chkAmbSecondPeriod, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkAmbInterPeriod.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(TemplateOnRotationDialog)
        TemplateOnRotationDialog.setTabOrder(self.edtAmbTimeRange1, self.edtAmbOffice1)
        TemplateOnRotationDialog.setTabOrder(self.edtAmbOffice1, self.edtAmbPlan1)
        TemplateOnRotationDialog.setTabOrder(self.edtAmbPlan1, self.edtAmbInterval1)
        TemplateOnRotationDialog.setTabOrder(self.edtAmbInterval1, self.btnAmbColor1)
        TemplateOnRotationDialog.setTabOrder(self.btnAmbColor1, self.chkNotExternalSystem1)
        TemplateOnRotationDialog.setTabOrder(self.chkNotExternalSystem1, self.edtHomeTimeRange1)
        TemplateOnRotationDialog.setTabOrder(self.edtHomeTimeRange1, self.edtHomePlan1)
        TemplateOnRotationDialog.setTabOrder(self.edtHomePlan1, self.edtHomeInterval1)
        TemplateOnRotationDialog.setTabOrder(self.edtHomeInterval1, self.cmbReasonOfAbsence1)
        TemplateOnRotationDialog.setTabOrder(self.cmbReasonOfAbsence1, self.edtAmbTimeRange12)
        TemplateOnRotationDialog.setTabOrder(self.edtAmbTimeRange12, self.edtAmbOffice12)
        TemplateOnRotationDialog.setTabOrder(self.edtAmbOffice12, self.edtAmbPlan12)
        TemplateOnRotationDialog.setTabOrder(self.edtAmbPlan12, self.edtAmbInterval12)
        TemplateOnRotationDialog.setTabOrder(self.edtAmbInterval12, self.btnAmbColor12)
        TemplateOnRotationDialog.setTabOrder(self.btnAmbColor12, self.chkNotExternalSystem12)
        TemplateOnRotationDialog.setTabOrder(self.chkNotExternalSystem12, self.edtHomeTimeRange12)
        TemplateOnRotationDialog.setTabOrder(self.edtHomeTimeRange12, self.edtHomePlan12)
        TemplateOnRotationDialog.setTabOrder(self.edtHomePlan12, self.edtHomeInterval12)
        TemplateOnRotationDialog.setTabOrder(self.edtHomeInterval12, self.edtAmbOfficeInter)
        TemplateOnRotationDialog.setTabOrder(self.edtAmbOfficeInter, self.edtAmbInterPlan1)
        TemplateOnRotationDialog.setTabOrder(self.edtAmbInterPlan1, self.edtAmbInterInterval1)
        TemplateOnRotationDialog.setTabOrder(self.edtAmbInterInterval1, self.btnAmbInterColor1)
        TemplateOnRotationDialog.setTabOrder(self.btnAmbInterColor1, self.chkInterNotExternalSystem1)
        TemplateOnRotationDialog.setTabOrder(self.chkInterNotExternalSystem1, self.calendarTemplateOnRotation)
        TemplateOnRotationDialog.setTabOrder(self.calendarTemplateOnRotation, self.btnClear)
        TemplateOnRotationDialog.setTabOrder(self.btnClear, self.chkFillRedDays)
        TemplateOnRotationDialog.setTabOrder(self.chkFillRedDays, self.chkAmbSecondPeriod)
        TemplateOnRotationDialog.setTabOrder(self.chkAmbSecondPeriod, self.chkAmbInterPeriod)
        TemplateOnRotationDialog.setTabOrder(self.chkAmbInterPeriod, self.chkHomeSecondPeriod)
        TemplateOnRotationDialog.setTabOrder(self.chkHomeSecondPeriod, self.buttonBox)

    def retranslateUi(self, TemplateOnRotationDialog):
        TemplateOnRotationDialog.setWindowTitle(_translate("TemplateOnRotationDialog", "Шаблон планировщика", None))
        self.lblAmbPlan.setText(_translate("TemplateOnRotationDialog", "План", None))
        self.label_1.setText(_translate("TemplateOnRotationDialog", "1", None))
        self.label_2.setText(_translate("TemplateOnRotationDialog", "2", None))
        self.lblAmb.setText(_translate("TemplateOnRotationDialog", "Амбулаторный приём", None))
        self.lblReasonOfAbsence1.setText(_translate("TemplateOnRotationDialog", "Причина", None))
        self.lblAmbHours.setText(_translate("TemplateOnRotationDialog", "Часы", None))
        self.lblAmbCab.setText(_translate("TemplateOnRotationDialog", "Кабинет", None))
        self.lblHome.setText(_translate("TemplateOnRotationDialog", "Вызовы на дом", None))
        self.lblHomePlan.setText(_translate("TemplateOnRotationDialog", "План", None))
        self.lblHomeHours.setText(_translate("TemplateOnRotationDialog", "Часы", None))
        self.lblReasonOfAbsence2.setText(_translate("TemplateOnRotationDialog", "отсутствия", None))
        self.lblAmbInterval12.setText(_translate("TemplateOnRotationDialog", "мин.", None))
        self.lblAmbInterInterval1.setText(_translate("TemplateOnRotationDialog", "мин.", None))
        self.lblAmbInterval1.setText(_translate("TemplateOnRotationDialog", "мин.", None))
        self.lblHomeInterval12.setText(_translate("TemplateOnRotationDialog", "мин.", None))
        self.label_3.setText(_translate("TemplateOnRotationDialog", "Вне очереди", None))
        self.label_4.setText(_translate("TemplateOnRotationDialog", "Интервал", None))
        self.label_5.setText(_translate("TemplateOnRotationDialog", "Интервал", None))
        self.lblHomeInterval1.setText(_translate("TemplateOnRotationDialog", "мин.", None))
        self.chkNotExternalSystem1.setToolTip(_translate("TemplateOnRotationDialog", "<html><head/><body><p>Данный период недоступен для использования через внешние системы</p></body></html>", None))
        self.chkNotExternalSystem12.setToolTip(_translate("TemplateOnRotationDialog", "<html><head/><body><p>Данный период недоступен для использования через внешние системы</p></body></html>", None))
        self.lblNotExternalSystem.setToolTip(_translate("TemplateOnRotationDialog", "<html><head/><body><p>Данный период недоступен для использования через внешние системы</p></body></html>", None))
        self.lblNotExternalSystem.setText(_translate("TemplateOnRotationDialog", "ВС", None))
        self.lblCountSelectedDays.setText(_translate("TemplateOnRotationDialog", "Всего выбрано дней: 0", None))
        self.label.setText(_translate("TemplateOnRotationDialog", "Выбранные дни:", None))
        self.btnClear.setText(_translate("TemplateOnRotationDialog", "Очистить", None))
        self.chkFillRedDays.setText(_translate("TemplateOnRotationDialog", "&Заполнять выходные дни", None))
        self.chkAmbSecondPeriod.setText(_translate("TemplateOnRotationDialog", "&Ввод второго периода приема", None))
        self.chkHomeSecondPeriod.setText(_translate("TemplateOnRotationDialog", "&Ввод второго периода вызовов", None))
        self.chkAmbInterPeriod.setText(_translate("TemplateOnRotationDialog", "&Добавить план между приемами", None))

from library.calendar import CCalendarWidget
from library.TimeEdit import CTimeRangeEdit
from library.crbcombobox import CRBComboBox
from library.CColorPicker import CColorPicker
