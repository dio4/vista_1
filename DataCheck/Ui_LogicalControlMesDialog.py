# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\DataCheck\LogicalControlMesDialog.ui'
#
# Created: Fri Jun 15 12:17:02 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_LogicalControlMesDialog(object):
    def setupUi(self, LogicalControlMesDialog):
        LogicalControlMesDialog.setObjectName(_fromUtf8("LogicalControlMesDialog"))
        LogicalControlMesDialog.resize(1096, 804)
        self.gridLayout = QtGui.QGridLayout(LogicalControlMesDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblBegin = QtGui.QLabel(LogicalControlMesDialog)
        self.lblBegin.setObjectName(_fromUtf8("lblBegin"))
        self.gridLayout.addWidget(self.lblBegin, 0, 0, 1, 1)
        self.dateBeginPeriod = CDateEdit(LogicalControlMesDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dateBeginPeriod.sizePolicy().hasHeightForWidth())
        self.dateBeginPeriod.setSizePolicy(sizePolicy)
        self.dateBeginPeriod.setCalendarPopup(True)
        self.dateBeginPeriod.setObjectName(_fromUtf8("dateBeginPeriod"))
        self.gridLayout.addWidget(self.dateBeginPeriod, 0, 1, 1, 1)
        self.lblEnd = QtGui.QLabel(LogicalControlMesDialog)
        self.lblEnd.setObjectName(_fromUtf8("lblEnd"))
        self.gridLayout.addWidget(self.lblEnd, 0, 2, 1, 1)
        self.dateEndPeriod = CDateEdit(LogicalControlMesDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dateEndPeriod.sizePolicy().hasHeightForWidth())
        self.dateEndPeriod.setSizePolicy(sizePolicy)
        self.dateEndPeriod.setCalendarPopup(True)
        self.dateEndPeriod.setObjectName(_fromUtf8("dateEndPeriod"))
        self.gridLayout.addWidget(self.dateEndPeriod, 0, 3, 1, 1)
        self.lblEventFeature = QtGui.QLabel(LogicalControlMesDialog)
        self.lblEventFeature.setObjectName(_fromUtf8("lblEventFeature"))
        self.gridLayout.addWidget(self.lblEventFeature, 0, 6, 1, 1)
        self.cmbEventFeature = QtGui.QComboBox(LogicalControlMesDialog)
        self.cmbEventFeature.setObjectName(_fromUtf8("cmbEventFeature"))
        self.cmbEventFeature.addItem(_fromUtf8(""))
        self.cmbEventFeature.addItem(_fromUtf8(""))
        self.cmbEventFeature.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbEventFeature, 0, 7, 1, 1)
        spacerItem = QtGui.QSpacerItem(42, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 8, 1, 1)
        self.lblOrgStructure = QtGui.QLabel(LogicalControlMesDialog)
        self.lblOrgStructure.setObjectName(_fromUtf8("lblOrgStructure"))
        self.gridLayout.addWidget(self.lblOrgStructure, 3, 6, 1, 1)
        self.cmbOrgStructure = COrgStructureComboBox(LogicalControlMesDialog)
        self.cmbOrgStructure.setEnabled(True)
        self.cmbOrgStructure.setObjectName(_fromUtf8("cmbOrgStructure"))
        self.gridLayout.addWidget(self.cmbOrgStructure, 3, 7, 1, 2)
        self.lblSpeciality = QtGui.QLabel(LogicalControlMesDialog)
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.gridLayout.addWidget(self.lblSpeciality, 4, 6, 1, 1)
        self.cmbSpeciality = CRBComboBox(LogicalControlMesDialog)
        self.cmbSpeciality.setEnabled(True)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 4, 7, 1, 2)
        self.lblPersonal = QtGui.QLabel(LogicalControlMesDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPersonal.sizePolicy().hasHeightForWidth())
        self.lblPersonal.setSizePolicy(sizePolicy)
        self.lblPersonal.setObjectName(_fromUtf8("lblPersonal"))
        self.gridLayout.addWidget(self.lblPersonal, 5, 6, 1, 1)
        self.cmbPerson = CPersonComboBoxEx(LogicalControlMesDialog)
        self.cmbPerson.setObjectName(_fromUtf8("cmbPerson"))
        self.gridLayout.addWidget(self.cmbPerson, 5, 7, 1, 2)
        self.prbControlMes = CProgressBar(LogicalControlMesDialog)
        self.prbControlMes.setObjectName(_fromUtf8("prbControlMes"))
        self.gridLayout.addWidget(self.prbControlMes, 9, 0, 1, 9)
        self.listResultControlMes = CRemarkListWidget(LogicalControlMesDialog)
        self.listResultControlMes.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.EditKeyPressed|QtGui.QAbstractItemView.SelectedClicked)
        self.listResultControlMes.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listResultControlMes.setFlow(QtGui.QListView.TopToBottom)
        self.listResultControlMes.setObjectName(_fromUtf8("listResultControlMes"))
        self.gridLayout.addWidget(self.listResultControlMes, 10, 0, 1, 9)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.btnStartControl = QtGui.QPushButton(LogicalControlMesDialog)
        self.btnStartControl.setAutoDefault(True)
        self.btnStartControl.setObjectName(_fromUtf8("btnStartControl"))
        self.horizontalLayout_2.addWidget(self.btnStartControl)
        self.lblCountLine = QtGui.QLabel(LogicalControlMesDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblCountLine.sizePolicy().hasHeightForWidth())
        self.lblCountLine.setSizePolicy(sizePolicy)
        self.lblCountLine.setText(_fromUtf8(""))
        self.lblCountLine.setAlignment(QtCore.Qt.AlignCenter)
        self.lblCountLine.setObjectName(_fromUtf8("lblCountLine"))
        self.horizontalLayout_2.addWidget(self.lblCountLine)
        self.btnEndControl = QtGui.QPushButton(LogicalControlMesDialog)
        self.btnEndControl.setAutoDefault(True)
        self.btnEndControl.setObjectName(_fromUtf8("btnEndControl"))
        self.horizontalLayout_2.addWidget(self.btnEndControl)
        self.gridLayout.addLayout(self.horizontalLayout_2, 11, 0, 1, 9)
        self.chkMes = QtGui.QCheckBox(LogicalControlMesDialog)
        self.chkMes.setObjectName(_fromUtf8("chkMes"))
        self.gridLayout.addWidget(self.chkMes, 8, 0, 1, 2)
        self.chkDuration = QtGui.QCheckBox(LogicalControlMesDialog)
        self.chkDuration.setObjectName(_fromUtf8("chkDuration"))
        self.gridLayout.addWidget(self.chkDuration, 8, 2, 1, 2)
        self.chkMKB = QtGui.QCheckBox(LogicalControlMesDialog)
        self.chkMKB.setObjectName(_fromUtf8("chkMKB"))
        self.gridLayout.addWidget(self.chkMKB, 8, 4, 1, 1)
        self.chkExecActions = QtGui.QCheckBox(LogicalControlMesDialog)
        self.chkExecActions.setObjectName(_fromUtf8("chkExecActions"))
        self.gridLayout.addWidget(self.chkExecActions, 8, 8, 1, 1)
        self.chkCountVisits = QtGui.QCheckBox(LogicalControlMesDialog)
        self.chkCountVisits.setObjectName(_fromUtf8("chkCountVisits"))
        self.gridLayout.addWidget(self.chkCountVisits, 8, 7, 1, 1)
        self.cmbMes = CMESComboBox(LogicalControlMesDialog)
        self.cmbMes.setObjectName(_fromUtf8("cmbMes"))
        self.gridLayout.addWidget(self.cmbMes, 6, 2, 1, 7)
        self.lblMes = QtGui.QLabel(LogicalControlMesDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblMes.sizePolicy().hasHeightForWidth())
        self.lblMes.setSizePolicy(sizePolicy)
        self.lblMes.setObjectName(_fromUtf8("lblMes"))
        self.gridLayout.addWidget(self.lblMes, 6, 0, 1, 2)
        self.cmbEventPurpose = CRBComboBox(LogicalControlMesDialog)
        self.cmbEventPurpose.setObjectName(_fromUtf8("cmbEventPurpose"))
        self.gridLayout.addWidget(self.cmbEventPurpose, 3, 2, 1, 4)
        self.lblEventPurpose = QtGui.QLabel(LogicalControlMesDialog)
        self.lblEventPurpose.setObjectName(_fromUtf8("lblEventPurpose"))
        self.gridLayout.addWidget(self.lblEventPurpose, 3, 0, 1, 2)
        self.lblEventType = QtGui.QLabel(LogicalControlMesDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblEventType.sizePolicy().hasHeightForWidth())
        self.lblEventType.setSizePolicy(sizePolicy)
        self.lblEventType.setObjectName(_fromUtf8("lblEventType"))
        self.gridLayout.addWidget(self.lblEventType, 4, 0, 1, 2)
        self.cmbEventType = CRBComboBox(LogicalControlMesDialog)
        self.cmbEventType.setObjectName(_fromUtf8("cmbEventType"))
        self.gridLayout.addWidget(self.cmbEventType, 4, 2, 1, 4)
        self.cmbEventProfile = CRBComboBox(LogicalControlMesDialog)
        self.cmbEventProfile.setObjectName(_fromUtf8("cmbEventProfile"))
        self.gridLayout.addWidget(self.cmbEventProfile, 5, 2, 1, 4)
        self.lblEventProfile = QtGui.QLabel(LogicalControlMesDialog)
        self.lblEventProfile.setObjectName(_fromUtf8("lblEventProfile"))
        self.gridLayout.addWidget(self.lblEventProfile, 5, 0, 1, 2)
        self.cmbEventExec = QtGui.QComboBox(LogicalControlMesDialog)
        self.cmbEventExec.setObjectName(_fromUtf8("cmbEventExec"))
        self.cmbEventExec.addItem(_fromUtf8(""))
        self.cmbEventExec.addItem(_fromUtf8(""))
        self.cmbEventExec.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbEventExec, 0, 5, 1, 1)
        self.lblEventExec = QtGui.QLabel(LogicalControlMesDialog)
        self.lblEventExec.setObjectName(_fromUtf8("lblEventExec"))
        self.gridLayout.addWidget(self.lblEventExec, 0, 4, 1, 1)
        self.chkNotAlternative = QtGui.QCheckBox(LogicalControlMesDialog)
        self.chkNotAlternative.setObjectName(_fromUtf8("chkNotAlternative"))
        self.gridLayout.addWidget(self.chkNotAlternative, 8, 5, 1, 2)
        self.lblBegin.setBuddy(self.dateBeginPeriod)
        self.lblEnd.setBuddy(self.dateEndPeriod)
        self.lblSpeciality.setBuddy(self.cmbSpeciality)
        self.lblPersonal.setBuddy(self.cmbPerson)
        self.lblMes.setBuddy(self.cmbMes)
        self.lblEventType.setBuddy(self.cmbEventType)

        self.retranslateUi(LogicalControlMesDialog)
        QtCore.QMetaObject.connectSlotsByName(LogicalControlMesDialog)
        LogicalControlMesDialog.setTabOrder(self.dateBeginPeriod, self.dateEndPeriod)
        LogicalControlMesDialog.setTabOrder(self.dateEndPeriod, self.cmbEventFeature)
        LogicalControlMesDialog.setTabOrder(self.cmbEventFeature, self.cmbEventPurpose)
        LogicalControlMesDialog.setTabOrder(self.cmbEventPurpose, self.cmbEventType)
        LogicalControlMesDialog.setTabOrder(self.cmbEventType, self.cmbEventProfile)
        LogicalControlMesDialog.setTabOrder(self.cmbEventProfile, self.cmbMes)
        LogicalControlMesDialog.setTabOrder(self.cmbMes, self.cmbOrgStructure)
        LogicalControlMesDialog.setTabOrder(self.cmbOrgStructure, self.cmbSpeciality)
        LogicalControlMesDialog.setTabOrder(self.cmbSpeciality, self.cmbPerson)
        LogicalControlMesDialog.setTabOrder(self.cmbPerson, self.chkMes)
        LogicalControlMesDialog.setTabOrder(self.chkMes, self.chkDuration)
        LogicalControlMesDialog.setTabOrder(self.chkDuration, self.chkMKB)
        LogicalControlMesDialog.setTabOrder(self.chkMKB, self.chkCountVisits)
        LogicalControlMesDialog.setTabOrder(self.chkCountVisits, self.chkExecActions)
        LogicalControlMesDialog.setTabOrder(self.chkExecActions, self.listResultControlMes)
        LogicalControlMesDialog.setTabOrder(self.listResultControlMes, self.btnStartControl)
        LogicalControlMesDialog.setTabOrder(self.btnStartControl, self.btnEndControl)

    def retranslateUi(self, LogicalControlMesDialog):
        LogicalControlMesDialog.setWindowTitle(QtGui.QApplication.translate("LogicalControlMesDialog", "Логический контроль событий с МЭС ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBegin.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "с   ", None, QtGui.QApplication.UnicodeUTF8))
        self.dateBeginPeriod.setDisplayFormat(QtGui.QApplication.translate("LogicalControlMesDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEnd.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "  по    ", None, QtGui.QApplication.UnicodeUTF8))
        self.dateEndPeriod.setDisplayFormat(QtGui.QApplication.translate("LogicalControlMesDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventFeature.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "Особенности", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbEventFeature.setItemText(0, QtGui.QApplication.translate("LogicalControlMesDialog", "Не учитывать", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbEventFeature.setItemText(1, QtGui.QApplication.translate("LogicalControlMesDialog", "Только выполненные", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbEventFeature.setItemText(2, QtGui.QApplication.translate("LogicalControlMesDialog", "Только невыполненные", None, QtGui.QApplication.UnicodeUTF8))
        self.lblOrgStructure.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "Подразделение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSpeciality.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "&Специальность", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSpeciality.setWhatsThis(QtGui.QApplication.translate("LogicalControlMesDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPersonal.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "&Врач", None, QtGui.QApplication.UnicodeUTF8))
        self.prbControlMes.setFormat(QtGui.QApplication.translate("LogicalControlMesDialog", "%p%", None, QtGui.QApplication.UnicodeUTF8))
        self.btnStartControl.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "начать выполнение", None, QtGui.QApplication.UnicodeUTF8))
        self.btnEndControl.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "прервать", None, QtGui.QApplication.UnicodeUTF8))
        self.chkMes.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "Наличие МЭС", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDuration.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "Длительность события", None, QtGui.QApplication.UnicodeUTF8))
        self.chkMKB.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "Заключительный диагноз", None, QtGui.QApplication.UnicodeUTF8))
        self.chkExecActions.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "Наличие выполненных действий", None, QtGui.QApplication.UnicodeUTF8))
        self.chkCountVisits.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "Кол-во визитов", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMes.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "МЭС", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventPurpose.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "Назначение события", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventType.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "Тип события", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventProfile.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "Профиль МЭС", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbEventExec.setItemText(0, QtGui.QApplication.translate("LogicalControlMesDialog", "Все", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbEventExec.setItemText(1, QtGui.QApplication.translate("LogicalControlMesDialog", "Законченные", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbEventExec.setItemText(2, QtGui.QApplication.translate("LogicalControlMesDialog", "Незаконченные", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventExec.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "Учитывать события", None, QtGui.QApplication.UnicodeUTF8))
        self.chkNotAlternative.setText(QtGui.QApplication.translate("LogicalControlMesDialog", "Не выполнена альтернативность", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from library.ProgressBar import CProgressBar
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from RemarkListWidget import CRemarkListWidget
from library.DateEdit import CDateEdit
from library.MES.MESComboBox import CMESComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    LogicalControlMesDialog = QtGui.QDialog()
    ui = Ui_LogicalControlMesDialog()
    ui.setupUi(LogicalControlMesDialog)
    LogicalControlMesDialog.show()
    sys.exit(app.exec_())
