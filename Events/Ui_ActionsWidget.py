# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ActionsWidget.ui'
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

class Ui_ActionsWidget(object):
    def setupUi(self, ActionsWidget):
        ActionsWidget.setObjectName(_fromUtf8("ActionsWidget"))
        ActionsWidget.resize(924, 825)
        self.verticalLayout = QtGui.QVBoxLayout(ActionsWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.frame = QtGui.QFrame(ActionsWidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout_4 = QtGui.QGridLayout(self.frame)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)
        self.lblActionUET = QtGui.QLabel(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblActionUET.sizePolicy().hasHeightForWidth())
        self.lblActionUET.setSizePolicy(sizePolicy)
        self.lblActionUET.setMinimumSize(QtCore.QSize(50, 0))
        self.lblActionUET.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblActionUET.setFrameShadow(QtGui.QFrame.Raised)
        self.lblActionUET.setObjectName(_fromUtf8("lblActionUET"))
        self.gridLayout_4.addWidget(self.lblActionUET, 0, 1, 1, 1)
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_4.addWidget(self.label, 1, 0, 1, 1)
        self.lblEventUET = QtGui.QLabel(self.frame)
        self.lblEventUET.setMinimumSize(QtCore.QSize(50, 0))
        self.lblEventUET.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblEventUET.setFrameShadow(QtGui.QFrame.Raised)
        self.lblEventUET.setObjectName(_fromUtf8("lblEventUET"))
        self.gridLayout_4.addWidget(self.lblEventUET, 1, 1, 1, 1)
        self.horizontalLayout.addWidget(self.frame)
        self.attrsAP = QtGui.QFrame(ActionsWidget)
        self.attrsAP.setEnabled(False)
        self.attrsAP.setFrameShape(QtGui.QFrame.StyledPanel)
        self.attrsAP.setFrameShadow(QtGui.QFrame.Sunken)
        self.attrsAP.setObjectName(_fromUtf8("attrsAP"))
        self.gridLayout_3 = QtGui.QGridLayout(self.attrsAP)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.cmbAPSetPerson = CPersonComboBoxEx(self.attrsAP)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbAPSetPerson.sizePolicy().hasHeightForWidth())
        self.cmbAPSetPerson.setSizePolicy(sizePolicy)
        self.cmbAPSetPerson.setObjectName(_fromUtf8("cmbAPSetPerson"))
        self.cmbAPSetPerson.addItem(_fromUtf8(""))
        self.gridLayout_3.addWidget(self.cmbAPSetPerson, 0, 7, 1, 1)
        self.lblAPEndDate = QtGui.QLabel(self.attrsAP)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblAPEndDate.sizePolicy().hasHeightForWidth())
        self.lblAPEndDate.setSizePolicy(sizePolicy)
        self.lblAPEndDate.setObjectName(_fromUtf8("lblAPEndDate"))
        self.gridLayout_3.addWidget(self.lblAPEndDate, 3, 1, 1, 1)
        self.cmbAPPerson = CPersonComboBoxEx(self.attrsAP)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbAPPerson.sizePolicy().hasHeightForWidth())
        self.cmbAPPerson.setSizePolicy(sizePolicy)
        self.cmbAPPerson.setObjectName(_fromUtf8("cmbAPPerson"))
        self.cmbAPPerson.addItem(_fromUtf8(""))
        self.gridLayout_3.addWidget(self.cmbAPPerson, 3, 7, 1, 1)
        self.lblAPBegDate = QtGui.QLabel(self.attrsAP)
        self.lblAPBegDate.setObjectName(_fromUtf8("lblAPBegDate"))
        self.gridLayout_3.addWidget(self.lblAPBegDate, 0, 1, 1, 1)
        self.lblAPPerson = QtGui.QLabel(self.attrsAP)
        self.lblAPPerson.setObjectName(_fromUtf8("lblAPPerson"))
        self.gridLayout_3.addWidget(self.lblAPPerson, 3, 6, 1, 1)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setMargin(0)
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.edtAPEndDate = CDateEdit(self.attrsAP)
        self.edtAPEndDate.setCalendarPopup(True)
        self.edtAPEndDate.setObjectName(_fromUtf8("edtAPEndDate"))
        self.horizontalLayout_8.addWidget(self.edtAPEndDate)
        self.edtAPEndTime = QtGui.QTimeEdit(self.attrsAP)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAPEndTime.sizePolicy().hasHeightForWidth())
        self.edtAPEndTime.setSizePolicy(sizePolicy)
        self.edtAPEndTime.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.edtAPEndTime.setObjectName(_fromUtf8("edtAPEndTime"))
        self.horizontalLayout_8.addWidget(self.edtAPEndTime)
        self.gridLayout_3.addLayout(self.horizontalLayout_8, 3, 2, 1, 1)
        self.lblAPSetPerson = QtGui.QLabel(self.attrsAP)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblAPSetPerson.sizePolicy().hasHeightForWidth())
        self.lblAPSetPerson.setSizePolicy(sizePolicy)
        self.lblAPSetPerson.setObjectName(_fromUtf8("lblAPSetPerson"))
        self.gridLayout_3.addWidget(self.lblAPSetPerson, 0, 6, 1, 1)
        self.horizontalLayout_11 = QtGui.QHBoxLayout()
        self.horizontalLayout_11.setMargin(0)
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        self.edtAPBegDate = CDateEdit(self.attrsAP)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAPBegDate.sizePolicy().hasHeightForWidth())
        self.edtAPBegDate.setSizePolicy(sizePolicy)
        self.edtAPBegDate.setCalendarPopup(True)
        self.edtAPBegDate.setObjectName(_fromUtf8("edtAPBegDate"))
        self.horizontalLayout_11.addWidget(self.edtAPBegDate)
        self.edtAPBegTime = QtGui.QTimeEdit(self.attrsAP)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAPBegTime.sizePolicy().hasHeightForWidth())
        self.edtAPBegTime.setSizePolicy(sizePolicy)
        self.edtAPBegTime.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.edtAPBegTime.setObjectName(_fromUtf8("edtAPBegTime"))
        self.horizontalLayout_11.addWidget(self.edtAPBegTime)
        self.gridLayout_3.addLayout(self.horizontalLayout_11, 0, 2, 1, 1)
        self.lblAPStatus = QtGui.QLabel(self.attrsAP)
        self.lblAPStatus.setObjectName(_fromUtf8("lblAPStatus"))
        self.gridLayout_3.addWidget(self.lblAPStatus, 0, 8, 1, 1)
        self.cmbAPStatus = QtGui.QComboBox(self.attrsAP)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbAPStatus.sizePolicy().hasHeightForWidth())
        self.cmbAPStatus.setSizePolicy(sizePolicy)
        self.cmbAPStatus.setObjectName(_fromUtf8("cmbAPStatus"))
        self.gridLayout_3.addWidget(self.cmbAPStatus, 0, 9, 1, 1)
        self.lblMKB = QtGui.QLabel(self.attrsAP)
        self.lblMKB.setObjectName(_fromUtf8("lblMKB"))
        self.gridLayout_3.addWidget(self.lblMKB, 3, 8, 1, 1)
        self.cmbMKB = CICDCodeEditEx(self.attrsAP)
        self.cmbMKB.setObjectName(_fromUtf8("cmbMKB"))
        self.gridLayout_3.addWidget(self.cmbMKB, 3, 9, 1, 1)
        self.horizontalLayout.addWidget(self.attrsAP)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.scrollArea = QtGui.QScrollArea(ActionsWidget)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 912, 715))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.splitterAP = QtGui.QSplitter(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitterAP.sizePolicy().hasHeightForWidth())
        self.splitterAP.setSizePolicy(sizePolicy)
        self.splitterAP.setOrientation(QtCore.Qt.Horizontal)
        self.splitterAP.setChildrenCollapsible(False)
        self.splitterAP.setObjectName(_fromUtf8("splitterAP"))
        self.tblAPActions = CActionsTreeView(self.splitterAP)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblAPActions.sizePolicy().hasHeightForWidth())
        self.tblAPActions.setSizePolicy(sizePolicy)
        self.tblAPActions.setMinimumSize(QtCore.QSize(150, 0))
        self.tblAPActions.setAnimated(True)
        self.tblAPActions.setObjectName(_fromUtf8("tblAPActions"))
        self.frameAP = QtGui.QFrame(self.splitterAP)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameAP.sizePolicy().hasHeightForWidth())
        self.frameAP.setSizePolicy(sizePolicy)
        self.frameAP.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frameAP.setFrameShape(QtGui.QFrame.NoFrame)
        self.frameAP.setFrameShadow(QtGui.QFrame.Sunken)
        self.frameAP.setObjectName(_fromUtf8("frameAP"))
        self.gridLayout = QtGui.QGridLayout(self.frameAP)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tblAPProps = CExActionPropertiesTableView(self.frameAP)
        self.tblAPProps.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tblAPProps.sizePolicy().hasHeightForWidth())
        self.tblAPProps.setSizePolicy(sizePolicy)
        self.tblAPProps.setMinimumSize(QtCore.QSize(0, 250))
        self.tblAPProps.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tblAPProps.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.tblAPProps.setObjectName(_fromUtf8("tblAPProps"))
        self.gridLayout.addWidget(self.tblAPProps, 18, 0, 1, 2)
        self.frmAPButtonsBar = QtGui.QFrame(self.frameAP)
        self.frmAPButtonsBar.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmAPButtonsBar.setFrameShadow(QtGui.QFrame.Plain)
        self.frmAPButtonsBar.setLineWidth(0)
        self.frmAPButtonsBar.setObjectName(_fromUtf8("frmAPButtonsBar"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.frmAPButtonsBar)
        self.horizontalLayout_4.setMargin(0)
        self.horizontalLayout_4.setSpacing(4)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.btnAPPrint = CPrintButton(self.frmAPButtonsBar)
        self.btnAPPrint.setObjectName(_fromUtf8("btnAPPrint"))
        self.horizontalLayout_4.addWidget(self.btnAPPrint)
        self.btnAPLoadTemplate = CActionTemplateChooseButton(self.frmAPButtonsBar)
        self.btnAPLoadTemplate.setObjectName(_fromUtf8("btnAPLoadTemplate"))
        self.horizontalLayout_4.addWidget(self.btnAPLoadTemplate)
        self.btnAPSaveAsTemplate = QtGui.QPushButton(self.frmAPButtonsBar)
        self.btnAPSaveAsTemplate.setObjectName(_fromUtf8("btnAPSaveAsTemplate"))
        self.horizontalLayout_4.addWidget(self.btnAPSaveAsTemplate)
        self.btnAPLoadPrevAction = QtGui.QPushButton(self.frmAPButtonsBar)
        self.btnAPLoadPrevAction.setEnabled(False)
        self.btnAPLoadPrevAction.setObjectName(_fromUtf8("btnAPLoadPrevAction"))
        self.horizontalLayout_4.addWidget(self.btnAPLoadPrevAction)
        spacerItem = QtGui.QSpacerItem(145, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.gridLayout.addWidget(self.frmAPButtonsBar, 19, 0, 1, 2)
        self.verticalLayout_2.addWidget(self.splitterAP)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(ActionsWidget)
        QtCore.QMetaObject.connectSlotsByName(ActionsWidget)

    def retranslateUi(self, ActionsWidget):
        ActionsWidget.setWindowTitle(_translate("ActionsWidget", "Form", None))
        self.label_3.setText(_translate("ActionsWidget", "УЕТ действия:", None))
        self.lblActionUET.setText(_translate("ActionsWidget", "0.0", None))
        self.label.setText(_translate("ActionsWidget", "УЕТ всего:", None))
        self.lblEventUET.setText(_translate("ActionsWidget", "0.0", None))
        self.cmbAPSetPerson.setItemText(0, _translate("ActionsWidget", "Врач", None))
        self.lblAPEndDate.setText(_translate("ActionsWidget", "Выполнено", None))
        self.cmbAPPerson.setItemText(0, _translate("ActionsWidget", "Врач", None))
        self.lblAPBegDate.setText(_translate("ActionsWidget", "Начато", None))
        self.lblAPPerson.setText(_translate("ActionsWidget", "Исполнитель", None))
        self.edtAPEndTime.setDisplayFormat(_translate("ActionsWidget", "HH:mm", None))
        self.lblAPSetPerson.setText(_translate("ActionsWidget", "Назначил", None))
        self.edtAPBegDate.setWhatsThis(_translate("ActionsWidget", "дата окончания осмотра", None))
        self.edtAPBegTime.setDisplayFormat(_translate("ActionsWidget", "HH:mm", None))
        self.lblAPStatus.setText(_translate("ActionsWidget", "Состояние", None))
        self.lblMKB.setText(_translate("ActionsWidget", "МКБ", None))
        self.btnAPPrint.setText(_translate("ActionsWidget", "Печать", None))
        self.btnAPLoadTemplate.setText(_translate("ActionsWidget", "Загрузить шаблон", None))
        self.btnAPSaveAsTemplate.setText(_translate("ActionsWidget", "Сохранить шаблон", None))
        self.btnAPLoadPrevAction.setText(_translate("ActionsWidget", "Копировать из предыдущего", None))

from Events.ActionPropertiesTable import CExActionPropertiesTableView
from Events.ActionTemplateChoose import CActionTemplateChooseButton
from Events.ActionsTreeModel import CActionsTreeView
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from library.DateEdit import CDateEdit
from library.ICDCodeEdit import CICDCodeEditEx
from library.PrintTemplates import CPrintButton