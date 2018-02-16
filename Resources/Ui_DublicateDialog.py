# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Resources\DublicateDialog.ui'
#
# Created: Fri Jun 15 12:16:24 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DublicateDialog(object):
    def setupUi(self, DublicateDialog):
        DublicateDialog.setObjectName(_fromUtf8("DublicateDialog"))
        DublicateDialog.resize(242, 275)
        self.gridLayout = QtGui.QGridLayout(DublicateDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.chkStart = QtGui.QCheckBox(DublicateDialog)
        self.chkStart.setObjectName(_fromUtf8("chkStart"))
        self.gridLayout.addWidget(self.chkStart, 1, 0, 1, 1)
        self.edtStart = CDateEdit(DublicateDialog)
        self.edtStart.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtStart.sizePolicy().hasHeightForWidth())
        self.edtStart.setSizePolicy(sizePolicy)
        self.edtStart.setObjectName(_fromUtf8("edtStart"))
        self.gridLayout.addWidget(self.edtStart, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(134, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.groupBox = QtGui.QGroupBox(DublicateDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.rbSingle = QtGui.QRadioButton(self.groupBox)
        self.rbSingle.setObjectName(_fromUtf8("rbSingle"))
        self.verticalLayout.addWidget(self.rbSingle)
        self.rbDual = QtGui.QRadioButton(self.groupBox)
        self.rbDual.setObjectName(_fromUtf8("rbDual"))
        self.verticalLayout.addWidget(self.rbDual)
        self.rbWeek = QtGui.QRadioButton(self.groupBox)
        self.rbWeek.setChecked(True)
        self.rbWeek.setObjectName(_fromUtf8("rbWeek"))
        self.verticalLayout.addWidget(self.rbWeek)
        self.gridLayout.addWidget(self.groupBox, 2, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(DublicateDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 3)
        self.lblMessage = QtGui.QLabel(DublicateDialog)
        self.lblMessage.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblMessage.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblMessage.setTextFormat(QtCore.Qt.PlainText)
        self.lblMessage.setWordWrap(True)
        self.lblMessage.setObjectName(_fromUtf8("lblMessage"))
        self.gridLayout.addWidget(self.lblMessage, 0, 0, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 4, 0, 1, 1)
        self.chkFillRedDays = QtGui.QCheckBox(DublicateDialog)
        self.chkFillRedDays.setEnabled(False)
        self.chkFillRedDays.setObjectName(_fromUtf8("chkFillRedDays"))
        self.gridLayout.addWidget(self.chkFillRedDays, 3, 0, 1, 3)

        self.retranslateUi(DublicateDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DublicateDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DublicateDialog.reject)
        QtCore.QObject.connect(self.chkStart, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.edtStart.setEnabled)
        QtCore.QObject.connect(self.rbWeek, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkFillRedDays.setDisabled)
        QtCore.QObject.connect(self.rbSingle, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkFillRedDays.setEnabled)
        QtCore.QObject.connect(self.rbDual, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkFillRedDays.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(DublicateDialog)
        DublicateDialog.setTabOrder(self.chkStart, self.edtStart)
        DublicateDialog.setTabOrder(self.edtStart, self.rbSingle)
        DublicateDialog.setTabOrder(self.rbSingle, self.rbDual)
        DublicateDialog.setTabOrder(self.rbDual, self.rbWeek)
        DublicateDialog.setTabOrder(self.rbWeek, self.chkFillRedDays)
        DublicateDialog.setTabOrder(self.chkFillRedDays, self.buttonBox)

    def retranslateUi(self, DublicateDialog):
        DublicateDialog.setWindowTitle(QtGui.QApplication.translate("DublicateDialog", "Дублирование графика", None, QtGui.QApplication.UnicodeUTF8))
        self.chkStart.setText(QtGui.QApplication.translate("DublicateDialog", "начинать с", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("DublicateDialog", "режим копирования", None, QtGui.QApplication.UnicodeUTF8))
        self.rbSingle.setText(QtGui.QApplication.translate("DublicateDialog", "Один план", None, QtGui.QApplication.UnicodeUTF8))
        self.rbDual.setText(QtGui.QApplication.translate("DublicateDialog", "Нечет/чёт", None, QtGui.QApplication.UnicodeUTF8))
        self.rbWeek.setText(QtGui.QApplication.translate("DublicateDialog", "Неделя", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMessage.setText(QtGui.QApplication.translate("DublicateDialog", "msg", None, QtGui.QApplication.UnicodeUTF8))
        self.chkFillRedDays.setText(QtGui.QApplication.translate("DublicateDialog", "&Заполнять выходные дни", None, QtGui.QApplication.UnicodeUTF8))

from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DublicateDialog = QtGui.QDialog()
    ui = Ui_DublicateDialog()
    ui.setupUi(DublicateDialog)
    DublicateDialog.show()
    sys.exit(app.exec_())

