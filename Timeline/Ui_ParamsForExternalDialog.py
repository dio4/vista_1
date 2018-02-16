# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Timeline\ParamsForExternalDialog.ui'
#
# Created: Fri Jun 15 12:16:59 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ParamsForExternalDialog(object):
    def setupUi(self, ParamsForExternalDialog):
        ParamsForExternalDialog.setObjectName(_fromUtf8("ParamsForExternalDialog"))
        ParamsForExternalDialog.resize(265, 109)
        self.gridLayout = QtGui.QGridLayout(ParamsForExternalDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ParamsForExternalDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 4)
        self.lblLastAccessibleTimelineDate = QtGui.QLabel(ParamsForExternalDialog)
        self.lblLastAccessibleTimelineDate.setWordWrap(False)
        self.lblLastAccessibleTimelineDate.setObjectName(_fromUtf8("lblLastAccessibleTimelineDate"))
        self.gridLayout.addWidget(self.lblLastAccessibleTimelineDate, 0, 0, 1, 1)
        self.edtLastAccessibleTimelineDate = CDateEdit(ParamsForExternalDialog)
        self.edtLastAccessibleTimelineDate.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtLastAccessibleTimelineDate.sizePolicy().hasHeightForWidth())
        self.edtLastAccessibleTimelineDate.setSizePolicy(sizePolicy)
        self.edtLastAccessibleTimelineDate.setCalendarPopup(True)
        self.edtLastAccessibleTimelineDate.setObjectName(_fromUtf8("edtLastAccessibleTimelineDate"))
        self.gridLayout.addWidget(self.edtLastAccessibleTimelineDate, 0, 1, 1, 2)
        self.lblTimelineAccessibilityDays = QtGui.QLabel(ParamsForExternalDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblTimelineAccessibilityDays.sizePolicy().hasHeightForWidth())
        self.lblTimelineAccessibilityDays.setSizePolicy(sizePolicy)
        self.lblTimelineAccessibilityDays.setWordWrap(False)
        self.lblTimelineAccessibilityDays.setObjectName(_fromUtf8("lblTimelineAccessibilityDays"))
        self.gridLayout.addWidget(self.lblTimelineAccessibilityDays, 1, 0, 1, 1)
        self.edtTimelineAccessibilityDays = QtGui.QSpinBox(ParamsForExternalDialog)
        self.edtTimelineAccessibilityDays.setEnabled(False)
        self.edtTimelineAccessibilityDays.setMaximumSize(QtCore.QSize(50, 16777215))
        self.edtTimelineAccessibilityDays.setMaximum(999)
        self.edtTimelineAccessibilityDays.setObjectName(_fromUtf8("edtTimelineAccessibilityDays"))
        self.gridLayout.addWidget(self.edtTimelineAccessibilityDays, 1, 1, 1, 1)
        self.lblTimelineAccessibilityDaysSuffix = QtGui.QLabel(ParamsForExternalDialog)
        self.lblTimelineAccessibilityDaysSuffix.setObjectName(_fromUtf8("lblTimelineAccessibilityDaysSuffix"))
        self.gridLayout.addWidget(self.lblTimelineAccessibilityDaysSuffix, 1, 2, 1, 1)
        self.chkTimelineAccessibilityDays = QtGui.QCheckBox(ParamsForExternalDialog)
        self.chkTimelineAccessibilityDays.setText(_fromUtf8(""))
        self.chkTimelineAccessibilityDays.setObjectName(_fromUtf8("chkTimelineAccessibilityDays"))
        self.gridLayout.addWidget(self.chkTimelineAccessibilityDays, 1, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 4, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 4, 1, 1)
        self.chkLastAccessibleTimelineDate = QtGui.QCheckBox(ParamsForExternalDialog)
        self.chkLastAccessibleTimelineDate.setText(_fromUtf8(""))
        self.chkLastAccessibleTimelineDate.setChecked(False)
        self.chkLastAccessibleTimelineDate.setObjectName(_fromUtf8("chkLastAccessibleTimelineDate"))
        self.gridLayout.addWidget(self.chkLastAccessibleTimelineDate, 0, 3, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 3, 4, 1, 1)

        self.retranslateUi(ParamsForExternalDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ParamsForExternalDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ParamsForExternalDialog.reject)
        QtCore.QObject.connect(self.chkLastAccessibleTimelineDate, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.edtLastAccessibleTimelineDate.setEnabled)
        QtCore.QObject.connect(self.chkTimelineAccessibilityDays, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.edtTimelineAccessibilityDays.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(ParamsForExternalDialog)
        ParamsForExternalDialog.setTabOrder(self.edtLastAccessibleTimelineDate, self.edtTimelineAccessibilityDays)
        ParamsForExternalDialog.setTabOrder(self.edtTimelineAccessibilityDays, self.buttonBox)

    def retranslateUi(self, ParamsForExternalDialog):
        ParamsForExternalDialog.setWindowTitle(QtGui.QApplication.translate("ParamsForExternalDialog", "Изменить параметры доступа к расписанию", None, QtGui.QApplication.UnicodeUTF8))
        self.lblLastAccessibleTimelineDate.setText(QtGui.QApplication.translate("ParamsForExternalDialog", "Расписание видимо до", None, QtGui.QApplication.UnicodeUTF8))
        self.edtLastAccessibleTimelineDate.setToolTip(QtGui.QApplication.translate("ParamsForExternalDialog", "Если это поле заполнено,\n"
"то указанная дата используется как предельная дата до которой видно расписание.", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTimelineAccessibilityDays.setText(QtGui.QApplication.translate("ParamsForExternalDialog", "Расписание видимо на", None, QtGui.QApplication.UnicodeUTF8))
        self.edtTimelineAccessibilityDays.setToolTip(QtGui.QApplication.translate("ParamsForExternalDialog", "Если это поле заполнено (не 0),\n"
"то указанная значение используется как количество дней начиная с текущего на которые видно расписание.", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTimelineAccessibilityDaysSuffix.setText(QtGui.QApplication.translate("ParamsForExternalDialog", "дней", None, QtGui.QApplication.UnicodeUTF8))

from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ParamsForExternalDialog = QtGui.QDialog()
    ui = Ui_ParamsForExternalDialog()
    ui.setupUi(ParamsForExternalDialog)
    ParamsForExternalDialog.show()
    sys.exit(app.exec_())

