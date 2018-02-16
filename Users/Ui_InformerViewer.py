# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Users\InformerViewer.ui'
#
# Created: Fri Jun 15 12:15:59 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_InformerPage(object):
    def setupUi(self, InformerPage):
        InformerPage.setObjectName(_fromUtf8("InformerPage"))
        InformerPage.resize(523, 323)
        InformerPage.setSizeGripEnabled(False)
        self.gridLayout = QtGui.QGridLayout(InformerPage)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCreatePerson = QtGui.QLabel(InformerPage)
        self.lblCreatePerson.setObjectName(_fromUtf8("lblCreatePerson"))
        self.gridLayout.addWidget(self.lblCreatePerson, 0, 0, 1, 1)
        self.lblSubject = QtGui.QLabel(InformerPage)
        self.lblSubject.setObjectName(_fromUtf8("lblSubject"))
        self.gridLayout.addWidget(self.lblSubject, 2, 0, 1, 1)
        self.lblCreatePersonValue = QtGui.QLabel(InformerPage)
        self.lblCreatePersonValue.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblCreatePersonValue.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblCreatePersonValue.setText(_fromUtf8(""))
        self.lblCreatePersonValue.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lblCreatePersonValue.setObjectName(_fromUtf8("lblCreatePersonValue"))
        self.gridLayout.addWidget(self.lblCreatePersonValue, 0, 1, 1, 1)
        self.lblCreateDatetimeValue = QtGui.QLabel(InformerPage)
        self.lblCreateDatetimeValue.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblCreateDatetimeValue.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblCreateDatetimeValue.setText(_fromUtf8(""))
        self.lblCreateDatetimeValue.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lblCreateDatetimeValue.setObjectName(_fromUtf8("lblCreateDatetimeValue"))
        self.gridLayout.addWidget(self.lblCreateDatetimeValue, 1, 1, 1, 1)
        self.lblSubjectValue = QtGui.QLabel(InformerPage)
        self.lblSubjectValue.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblSubjectValue.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblSubjectValue.setText(_fromUtf8(""))
        self.lblSubjectValue.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lblSubjectValue.setObjectName(_fromUtf8("lblSubjectValue"))
        self.gridLayout.addWidget(self.lblSubjectValue, 2, 1, 1, 1)
        self.lblText = QtGui.QLabel(InformerPage)
        self.lblText.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblText.setObjectName(_fromUtf8("lblText"))
        self.gridLayout.addWidget(self.lblText, 3, 0, 1, 1)
        self.edtText = QtGui.QTextBrowser(InformerPage)
        self.edtText.setOpenExternalLinks(True)
        self.edtText.setObjectName(_fromUtf8("edtText"))
        self.gridLayout.addWidget(self.edtText, 3, 1, 1, 1)
        self.chkMarkViewed = QtGui.QCheckBox(InformerPage)
        self.chkMarkViewed.setChecked(True)
        self.chkMarkViewed.setObjectName(_fromUtf8("chkMarkViewed"))
        self.gridLayout.addWidget(self.chkMarkViewed, 4, 1, 1, 1)
        self.lblCreateDatetime = QtGui.QLabel(InformerPage)
        self.lblCreateDatetime.setObjectName(_fromUtf8("lblCreateDatetime"))
        self.gridLayout.addWidget(self.lblCreateDatetime, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(InformerPage)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 2)

        self.retranslateUi(InformerPage)
        QtCore.QMetaObject.connectSlotsByName(InformerPage)

    def retranslateUi(self, InformerPage):
        InformerPage.setWindowTitle(QtGui.QApplication.translate("InformerPage", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCreatePerson.setText(QtGui.QApplication.translate("InformerPage", "Автор", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSubject.setText(QtGui.QApplication.translate("InformerPage", "Тема", None, QtGui.QApplication.UnicodeUTF8))
        self.lblText.setText(QtGui.QApplication.translate("InformerPage", "Текст", None, QtGui.QApplication.UnicodeUTF8))
        self.chkMarkViewed.setText(QtGui.QApplication.translate("InformerPage", "Больше не &показывать", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCreateDatetime.setText(QtGui.QApplication.translate("InformerPage", "Дата", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    InformerPage = QtGui.QDialog()
    ui = Ui_InformerPage()
    ui.setupUi(InformerPage)
    InformerPage.show()
    sys.exit(app.exec_())

