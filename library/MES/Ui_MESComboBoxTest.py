# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\library\MES\MESComboBoxTest.ui'
#
# Created: Fri Jun 15 12:16:22 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TestDialog(object):
    def setupUi(self, TestDialog):
        TestDialog.setObjectName(_fromUtf8("TestDialog"))
        TestDialog.resize(400, 364)
        self.gridLayout = QtGui.QGridLayout(TestDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblAge = QtGui.QLabel(TestDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridLayout.addWidget(self.lblAge, 1, 0, 1, 1)
        self.edtAge = QtGui.QSpinBox(TestDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtAge.sizePolicy().hasHeightForWidth())
        self.edtAge.setSizePolicy(sizePolicy)
        self.edtAge.setMaximum(150)
        self.edtAge.setObjectName(_fromUtf8("edtAge"))
        self.gridLayout.addWidget(self.edtAge, 1, 1, 1, 1)
        self.lblSpeciality = QtGui.QLabel(TestDialog)
        self.lblSpeciality.setObjectName(_fromUtf8("lblSpeciality"))
        self.gridLayout.addWidget(self.lblSpeciality, 6, 0, 1, 1)
        self.cmbSpeciality = CRBComboBox(TestDialog)
        self.cmbSpeciality.setObjectName(_fromUtf8("cmbSpeciality"))
        self.gridLayout.addWidget(self.cmbSpeciality, 6, 1, 1, 2)
        self.lblMKB = QtGui.QLabel(TestDialog)
        self.lblMKB.setObjectName(_fromUtf8("lblMKB"))
        self.gridLayout.addWidget(self.lblMKB, 7, 0, 1, 1)
        self.edtMKB = CICDCodeEditEx(TestDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtMKB.sizePolicy().hasHeightForWidth())
        self.edtMKB.setSizePolicy(sizePolicy)
        self.edtMKB.setObjectName(_fromUtf8("edtMKB"))
        self.gridLayout.addWidget(self.edtMKB, 7, 1, 1, 1)
        self.lblMES = QtGui.QLabel(TestDialog)
        self.lblMES.setObjectName(_fromUtf8("lblMES"))
        self.gridLayout.addWidget(self.lblMES, 8, 0, 1, 1)
        self.cmbMES = CMESComboBox(TestDialog)
        self.cmbMES.setObjectName(_fromUtf8("cmbMES"))
        self.gridLayout.addWidget(self.cmbMES, 8, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 131, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(TestDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 7, 2, 1, 1)
        self.cmbEventProfile = CRBComboBox(TestDialog)
        self.cmbEventProfile.setObjectName(_fromUtf8("cmbEventProfile"))
        self.gridLayout.addWidget(self.cmbEventProfile, 3, 1, 1, 2)
        self.lblEventProfile = QtGui.QLabel(TestDialog)
        self.lblEventProfile.setObjectName(_fromUtf8("lblEventProfile"))
        self.gridLayout.addWidget(self.lblEventProfile, 3, 0, 1, 1)
        self.lblSex = QtGui.QLabel(TestDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridLayout.addWidget(self.lblSex, 0, 0, 1, 1)
        self.cmbSex = QtGui.QComboBox(TestDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbSex.sizePolicy().hasHeightForWidth())
        self.cmbSex.setSizePolicy(sizePolicy)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbSex, 0, 1, 1, 1)
        self.lblMESCodeTemplate = QtGui.QLabel(TestDialog)
        self.lblMESCodeTemplate.setObjectName(_fromUtf8("lblMESCodeTemplate"))
        self.gridLayout.addWidget(self.lblMESCodeTemplate, 4, 0, 1, 1)
        self.lblMESNameTemplate = QtGui.QLabel(TestDialog)
        self.lblMESNameTemplate.setObjectName(_fromUtf8("lblMESNameTemplate"))
        self.gridLayout.addWidget(self.lblMESNameTemplate, 5, 0, 1, 1)
        self.edtMESCodeTemplate = QtGui.QLineEdit(TestDialog)
        self.edtMESCodeTemplate.setObjectName(_fromUtf8("edtMESCodeTemplate"))
        self.gridLayout.addWidget(self.edtMESCodeTemplate, 4, 1, 1, 1)
        self.edtMESNameTemplate = QtGui.QLineEdit(TestDialog)
        self.edtMESNameTemplate.setObjectName(_fromUtf8("edtMESNameTemplate"))
        self.gridLayout.addWidget(self.edtMESNameTemplate, 5, 1, 1, 1)
        self.lblAge.setBuddy(self.edtAge)
        self.lblSpeciality.setBuddy(self.cmbSpeciality)
        self.lblMKB.setBuddy(self.edtMKB)
        self.lblMES.setBuddy(self.cmbMES)
        self.lblEventProfile.setBuddy(self.cmbEventProfile)
        self.lblSex.setBuddy(self.cmbSex)

        self.retranslateUi(TestDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TestDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TestDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TestDialog)
        TestDialog.setTabOrder(self.cmbSex, self.edtAge)
        TestDialog.setTabOrder(self.edtAge, self.cmbEventProfile)
        TestDialog.setTabOrder(self.cmbEventProfile, self.edtMESCodeTemplate)
        TestDialog.setTabOrder(self.edtMESCodeTemplate, self.edtMESNameTemplate)
        TestDialog.setTabOrder(self.edtMESNameTemplate, self.cmbSpeciality)
        TestDialog.setTabOrder(self.cmbSpeciality, self.edtMKB)
        TestDialog.setTabOrder(self.edtMKB, self.cmbMES)
        TestDialog.setTabOrder(self.cmbMES, self.buttonBox)

    def retranslateUi(self, TestDialog):
        TestDialog.setWindowTitle(QtGui.QApplication.translate("TestDialog", "Испытание МЭС", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAge.setText(QtGui.QApplication.translate("TestDialog", "&Возраст пациента", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSpeciality.setText(QtGui.QApplication.translate("TestDialog", "&Специальность", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSpeciality.setWhatsThis(QtGui.QApplication.translate("TestDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMKB.setText(QtGui.QApplication.translate("TestDialog", "Код &диагноза", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMES.setText(QtGui.QApplication.translate("TestDialog", "С&тандарт", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbEventProfile.setWhatsThis(QtGui.QApplication.translate("TestDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEventProfile.setText(QtGui.QApplication.translate("TestDialog", "Профиль события", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSex.setText(QtGui.QApplication.translate("TestDialog", "&Пол пациента", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSex.setItemText(1, QtGui.QApplication.translate("TestDialog", "М", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSex.setItemText(2, QtGui.QApplication.translate("TestDialog", "Ж", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMESCodeTemplate.setText(QtGui.QApplication.translate("TestDialog", "Шаблон кода  МЭС", None, QtGui.QApplication.UnicodeUTF8))
        self.lblMESNameTemplate.setText(QtGui.QApplication.translate("TestDialog", "Шаблон наименования МЭС", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from library.ICDCodeEdit import CICDCodeEditEx
from library.MES.MESComboBox import CMESComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TestDialog = QtGui.QDialog()
    ui = Ui_TestDialog()
    ui.setupUi(TestDialog)
    TestDialog.show()
    sys.exit(app.exec_())

