# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\DataCheck\CorrectsControlDublesDialog.ui'
#
# Created: Fri Jun 15 12:16:09 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_CorrectsControlDublesDialog(object):
    def setupUi(self, CorrectsControlDublesDialog):
        CorrectsControlDublesDialog.setObjectName(_fromUtf8("CorrectsControlDublesDialog"))
        CorrectsControlDublesDialog.resize(512, 630)
        self.gridLayout = QtGui.QGridLayout(CorrectsControlDublesDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.scrollArea = QtGui.QScrollArea(CorrectsControlDublesDialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 500, 570))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_2 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblNameTitle = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.lblNameTitle.setFont(font)
        self.lblNameTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.lblNameTitle.setWordWrap(True)
        self.lblNameTitle.setObjectName(_fromUtf8("lblNameTitle"))
        self.gridLayout_2.addWidget(self.lblNameTitle, 0, 0, 1, 1)
        self.lblBaseLineTitle = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblBaseLineTitle.setFont(font)
        self.lblBaseLineTitle.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.lblBaseLineTitle.setWordWrap(True)
        self.lblBaseLineTitle.setObjectName(_fromUtf8("lblBaseLineTitle"))
        self.gridLayout_2.addWidget(self.lblBaseLineTitle, 1, 0, 1, 1)
        self.splitter = QtGui.QSplitter(self.scrollAreaWidgetContents)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tblCorrectBaseLine = QtGui.QListWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.tblCorrectBaseLine.sizePolicy().hasHeightForWidth())
        self.tblCorrectBaseLine.setSizePolicy(sizePolicy)
        self.tblCorrectBaseLine.setObjectName(_fromUtf8("tblCorrectBaseLine"))
        self.lblDoubleTitle = QtGui.QLabel(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblDoubleTitle.sizePolicy().hasHeightForWidth())
        self.lblDoubleTitle.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblDoubleTitle.setFont(font)
        self.lblDoubleTitle.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.lblDoubleTitle.setWordWrap(True)
        self.lblDoubleTitle.setObjectName(_fromUtf8("lblDoubleTitle"))
        self.tblCorrectDoubleLine = QtGui.QListWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.tblCorrectDoubleLine.sizePolicy().hasHeightForWidth())
        self.tblCorrectDoubleLine.setSizePolicy(sizePolicy)
        self.tblCorrectDoubleLine.setObjectName(_fromUtf8("tblCorrectDoubleLine"))
        self.gridLayout_2.addWidget(self.splitter, 2, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 3)
        self.lblCancelTitle = QtGui.QLabel(CorrectsControlDublesDialog)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lblCancelTitle.setFont(font)
        self.lblCancelTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.lblCancelTitle.setWordWrap(True)
        self.lblCancelTitle.setObjectName(_fromUtf8("lblCancelTitle"))
        self.gridLayout.addWidget(self.lblCancelTitle, 1, 0, 1, 3)
        self.btnOkCancel = QtGui.QDialogButtonBox(CorrectsControlDublesDialog)
        self.btnOkCancel.setOrientation(QtCore.Qt.Horizontal)
        self.btnOkCancel.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.btnOkCancel.setCenterButtons(False)
        self.btnOkCancel.setObjectName(_fromUtf8("btnOkCancel"))
        self.gridLayout.addWidget(self.btnOkCancel, 2, 0, 1, 3)

        self.retranslateUi(CorrectsControlDublesDialog)
        QtCore.QObject.connect(self.btnOkCancel, QtCore.SIGNAL(_fromUtf8("accepted()")), CorrectsControlDublesDialog.accept)
        QtCore.QObject.connect(self.btnOkCancel, QtCore.SIGNAL(_fromUtf8("rejected()")), CorrectsControlDublesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CorrectsControlDublesDialog)

    def retranslateUi(self, CorrectsControlDublesDialog):
        CorrectsControlDublesDialog.setWindowTitle(QtGui.QApplication.translate("CorrectsControlDublesDialog", "Внимание!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblNameTitle.setText(QtGui.QApplication.translate("CorrectsControlDublesDialog", "Будет произведено удаление дублей.", None, QtGui.QApplication.UnicodeUTF8))
        self.lblBaseLineTitle.setText(QtGui.QApplication.translate("CorrectsControlDublesDialog", "За основную взята строка:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDoubleTitle.setText(QtGui.QApplication.translate("CorrectsControlDublesDialog", "Следующие дубли будут удалены. Вы можете отредактировать информацию на пациента(двойной щелчок по строке открывает соответствующий документ).", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCancelTitle.setText(QtGui.QApplication.translate("CorrectsControlDublesDialog", "Подтвердите эти действия.", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    CorrectsControlDublesDialog = QtGui.QDialog()
    ui = Ui_CorrectsControlDublesDialog()
    ui.setupUi(CorrectsControlDublesDialog)
    CorrectsControlDublesDialog.show()
    sys.exit(app.exec_())

