# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportPersons.ui'
#
# Created: Mon Dec 10 12:28:42 2012
#      by: PyQt4 UI code generator 4.9.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.setEnabled(True)
        Dialog.resize(700, 500)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(700, 500))
        Dialog.setMaximumSize(QtCore.QSize(700, 500))
        Dialog.setLayoutDirection(QtCore.Qt.LeftToRight)
        Dialog.setSizeGripEnabled(False)
        self.verticalLayoutWidget = QtGui.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 681, 481))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lblPath = QtGui.QLabel(self.verticalLayoutWidget)
        self.lblPath.setObjectName(_fromUtf8("lblPath"))
        self.verticalLayout.addWidget(self.lblPath)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.edtFilePath = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.edtFilePath.setObjectName(_fromUtf8("edtFilePath"))
        self.horizontalLayout.addWidget(self.edtFilePath)
        self.btnOpenFile = QtGui.QToolButton(self.verticalLayoutWidget)
        self.btnOpenFile.setObjectName(_fromUtf8("btnOpenFile"))
        self.horizontalLayout.addWidget(self.btnOpenFile)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.pbProcess = QtGui.QProgressBar(self.verticalLayoutWidget)
        self.pbProcess.setProperty("value", 0)
        self.pbProcess.setTextVisible(True)
        self.pbProcess.setOrientation(QtCore.Qt.Horizontal)
        self.pbProcess.setObjectName(_fromUtf8("pbProcess"))
        self.verticalLayout.addWidget(self.pbProcess)
        self.edtLog = QtGui.QTextBrowser(self.verticalLayoutWidget)
        self.edtLog.setObjectName(_fromUtf8("edtLog"))
        self.verticalLayout.addWidget(self.edtLog)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.btnStart = QtGui.QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btnStart.setFont(font)
        self.btnStart.setObjectName(_fromUtf8("btnStart"))
        self.horizontalLayout_3.addWidget(self.btnStart)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.btnClose = QtGui.QPushButton(self.verticalLayoutWidget)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.horizontalLayout_3.addWidget(self.btnClose)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Импорт врачей", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPath.setText(QtGui.QApplication.translate("Dialog", "Путь к файлу:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOpenFile.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnStart.setText(QtGui.QApplication.translate("Dialog", "Начать", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("Dialog", "Закрыть", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

