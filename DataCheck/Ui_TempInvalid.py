# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\DataCheck\TempInvalid.ui'
#
# Created: Fri Jun 15 12:15:03 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TempInvalidCheckDialog(object):
    def setupUi(self, TempInvalidCheckDialog):
        TempInvalidCheckDialog.setObjectName(_fromUtf8("TempInvalidCheckDialog"))
        TempInvalidCheckDialog.resize(589, 538)
        self.gridLayout = QtGui.QGridLayout(TempInvalidCheckDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(349, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 3)
        self.label_3 = QtGui.QLabel(TempInvalidCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.boxDocTypes = QtGui.QComboBox(TempInvalidCheckDialog)
        self.boxDocTypes.setObjectName(_fromUtf8("boxDocTypes"))
        self.boxDocTypes.addItem(_fromUtf8(""))
        self.boxDocTypes.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.boxDocTypes, 1, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(349, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 2, 1, 3)
        self.checkExpert = QtGui.QCheckBox(TempInvalidCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkExpert.sizePolicy().hasHeightForWidth())
        self.checkExpert.setSizePolicy(sizePolicy)
        self.checkExpert.setObjectName(_fromUtf8("checkExpert"))
        self.gridLayout.addWidget(self.checkExpert, 3, 0, 1, 5)
        self.checkDocum = QtGui.QCheckBox(TempInvalidCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkDocum.sizePolicy().hasHeightForWidth())
        self.checkDocum.setSizePolicy(sizePolicy)
        self.checkDocum.setObjectName(_fromUtf8("checkDocum"))
        self.gridLayout.addWidget(self.checkDocum, 4, 0, 1, 5)
        self.checkDur = QtGui.QCheckBox(TempInvalidCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkDur.sizePolicy().hasHeightForWidth())
        self.checkDur.setSizePolicy(sizePolicy)
        self.checkDur.setObjectName(_fromUtf8("checkDur"))
        self.gridLayout.addWidget(self.checkDur, 5, 0, 1, 5)
        self.progressBar = CProgressBar(TempInvalidCheckDialog)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 6, 0, 1, 5)
        self.log = QtGui.QListWidget(TempInvalidCheckDialog)
        self.log.setObjectName(_fromUtf8("log"))
        self.gridLayout.addWidget(self.log, 7, 0, 1, 5)
        self.labelInfo = QtGui.QLabel(TempInvalidCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelInfo.sizePolicy().hasHeightForWidth())
        self.labelInfo.setSizePolicy(sizePolicy)
        self.labelInfo.setText(_fromUtf8(""))
        self.labelInfo.setObjectName(_fromUtf8("labelInfo"))
        self.gridLayout.addWidget(self.labelInfo, 8, 0, 1, 3)
        self.btnStart = QtGui.QPushButton(TempInvalidCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnStart.sizePolicy().hasHeightForWidth())
        self.btnStart.setSizePolicy(sizePolicy)
        self.btnStart.setMinimumSize(QtCore.QSize(100, 0))
        self.btnStart.setObjectName(_fromUtf8("btnStart"))
        self.gridLayout.addWidget(self.btnStart, 8, 3, 1, 1)
        self.btnClose = QtGui.QPushButton(TempInvalidCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnClose.sizePolicy().hasHeightForWidth())
        self.btnClose.setSizePolicy(sizePolicy)
        self.btnClose.setMinimumSize(QtCore.QSize(100, 0))
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 8, 4, 1, 1)
        self.frmDateRange = QtGui.QWidget(TempInvalidCheckDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frmDateRange.sizePolicy().hasHeightForWidth())
        self.frmDateRange.setSizePolicy(sizePolicy)
        self.frmDateRange.setObjectName(_fromUtf8("frmDateRange"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frmDateRange)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.frmDateRange)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.dateEdit_1 = CDateEdit(self.frmDateRange)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dateEdit_1.sizePolicy().hasHeightForWidth())
        self.dateEdit_1.setSizePolicy(sizePolicy)
        self.dateEdit_1.setCalendarPopup(True)
        self.dateEdit_1.setDate(QtCore.QDate(2000, 1, 1))
        self.dateEdit_1.setObjectName(_fromUtf8("dateEdit_1"))
        self.horizontalLayout.addWidget(self.dateEdit_1)
        self.label_2 = QtGui.QLabel(self.frmDateRange)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.dateEdit_2 = CDateEdit(self.frmDateRange)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dateEdit_2.sizePolicy().hasHeightForWidth())
        self.dateEdit_2.setSizePolicy(sizePolicy)
        self.dateEdit_2.setCalendarPopup(True)
        self.dateEdit_2.setDate(QtCore.QDate(2000, 1, 1))
        self.dateEdit_2.setObjectName(_fromUtf8("dateEdit_2"))
        self.horizontalLayout.addWidget(self.dateEdit_2)
        self.gridLayout.addWidget(self.frmDateRange, 0, 0, 1, 2)

        self.retranslateUi(TempInvalidCheckDialog)
        QtCore.QMetaObject.connectSlotsByName(TempInvalidCheckDialog)
        TempInvalidCheckDialog.setTabOrder(self.dateEdit_1, self.dateEdit_2)
        TempInvalidCheckDialog.setTabOrder(self.dateEdit_2, self.boxDocTypes)
        TempInvalidCheckDialog.setTabOrder(self.boxDocTypes, self.checkExpert)
        TempInvalidCheckDialog.setTabOrder(self.checkExpert, self.checkDocum)
        TempInvalidCheckDialog.setTabOrder(self.checkDocum, self.checkDur)
        TempInvalidCheckDialog.setTabOrder(self.checkDur, self.log)
        TempInvalidCheckDialog.setTabOrder(self.log, self.btnStart)
        TempInvalidCheckDialog.setTabOrder(self.btnStart, self.btnClose)

    def retranslateUi(self, TempInvalidCheckDialog):
        TempInvalidCheckDialog.setWindowTitle(QtGui.QApplication.translate("TempInvalidCheckDialog", "логический контроль ВУТ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("TempInvalidCheckDialog", "тип документа", None, QtGui.QApplication.UnicodeUTF8))
        self.boxDocTypes.setItemText(0, QtGui.QApplication.translate("TempInvalidCheckDialog", "больничный лист", None, QtGui.QApplication.UnicodeUTF8))
        self.boxDocTypes.setItemText(1, QtGui.QApplication.translate("TempInvalidCheckDialog", "справка", None, QtGui.QApplication.UnicodeUTF8))
        self.checkExpert.setText(QtGui.QApplication.translate("TempInvalidCheckDialog", "выполнять экспертизу", None, QtGui.QApplication.UnicodeUTF8))
        self.checkDocum.setText(QtGui.QApplication.translate("TempInvalidCheckDialog", "проверять документ", None, QtGui.QApplication.UnicodeUTF8))
        self.checkDur.setText(QtGui.QApplication.translate("TempInvalidCheckDialog", "проверять длительность", None, QtGui.QApplication.UnicodeUTF8))
        self.btnStart.setText(QtGui.QApplication.translate("TempInvalidCheckDialog", "начать проверку", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("TempInvalidCheckDialog", "прервать", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("TempInvalidCheckDialog", "с", None, QtGui.QApplication.UnicodeUTF8))
        self.dateEdit_1.setDisplayFormat(QtGui.QApplication.translate("TempInvalidCheckDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("TempInvalidCheckDialog", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.dateEdit_2.setDisplayFormat(QtGui.QApplication.translate("TempInvalidCheckDialog", "dd.MM.yyyy", None, QtGui.QApplication.UnicodeUTF8))

from library.ProgressBar import CProgressBar
from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TempInvalidCheckDialog = QtGui.QDialog()
    ui = Ui_TempInvalidCheckDialog()
    ui.setupUi(TempInvalidCheckDialog)
    TempInvalidCheckDialog.show()
    sys.exit(app.exec_())
