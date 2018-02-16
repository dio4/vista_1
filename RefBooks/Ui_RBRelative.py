# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\RBRelative.ui'
#
# Created: Fri Jun 15 12:16:25 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ItemEditorDialog(object):
    def setupUi(self, ItemEditorDialog):
        ItemEditorDialog.setObjectName(_fromUtf8("ItemEditorDialog"))
        ItemEditorDialog.resize(490, 250)
        ItemEditorDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ItemEditorDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCode = QtGui.QLabel(ItemEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 0, 1, 1, 3)
        self.lblRegionalCode = QtGui.QLabel(ItemEditorDialog)
        self.lblRegionalCode.setObjectName(_fromUtf8("lblRegionalCode"))
        self.gridLayout.addWidget(self.lblRegionalCode, 1, 0, 1, 1)
        self.edtRegionalCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtRegionalCode.setObjectName(_fromUtf8("edtRegionalCode"))
        self.gridLayout.addWidget(self.edtRegionalCode, 1, 1, 1, 3)
        self.lblLeftName = QtGui.QLabel(ItemEditorDialog)
        self.lblLeftName.setObjectName(_fromUtf8("lblLeftName"))
        self.gridLayout.addWidget(self.lblLeftName, 3, 0, 1, 1)
        self.edtLeftName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtLeftName.setObjectName(_fromUtf8("edtLeftName"))
        self.gridLayout.addWidget(self.edtLeftName, 3, 1, 1, 1)
        self.lblRightName = QtGui.QLabel(ItemEditorDialog)
        self.lblRightName.setObjectName(_fromUtf8("lblRightName"))
        self.gridLayout.addWidget(self.lblRightName, 3, 2, 1, 1)
        self.edtRightName = QtGui.QLineEdit(ItemEditorDialog)
        self.edtRightName.setObjectName(_fromUtf8("edtRightName"))
        self.gridLayout.addWidget(self.edtRightName, 3, 3, 1, 1)
        self.lblGenetic = QtGui.QLabel(ItemEditorDialog)
        self.lblGenetic.setObjectName(_fromUtf8("lblGenetic"))
        self.gridLayout.addWidget(self.lblGenetic, 4, 0, 1, 1)
        self.chkDirectGeneticRelation = QtGui.QCheckBox(ItemEditorDialog)
        self.chkDirectGeneticRelation.setObjectName(_fromUtf8("chkDirectGeneticRelation"))
        self.gridLayout.addWidget(self.chkDirectGeneticRelation, 4, 1, 1, 1)
        self.chkBackwardGeneticRelation = QtGui.QCheckBox(ItemEditorDialog)
        self.chkBackwardGeneticRelation.setObjectName(_fromUtf8("chkBackwardGeneticRelation"))
        self.gridLayout.addWidget(self.chkBackwardGeneticRelation, 4, 3, 1, 1)
        self.lblRepresentative = QtGui.QLabel(ItemEditorDialog)
        self.lblRepresentative.setObjectName(_fromUtf8("lblRepresentative"))
        self.gridLayout.addWidget(self.lblRepresentative, 5, 0, 1, 1)
        self.chkDirectRepresentativeRelation = QtGui.QCheckBox(ItemEditorDialog)
        self.chkDirectRepresentativeRelation.setObjectName(_fromUtf8("chkDirectRepresentativeRelation"))
        self.gridLayout.addWidget(self.chkDirectRepresentativeRelation, 5, 1, 1, 1)
        self.chkBackwardRepresentativeRelation = QtGui.QCheckBox(ItemEditorDialog)
        self.chkBackwardRepresentativeRelation.setObjectName(_fromUtf8("chkBackwardRepresentativeRelation"))
        self.gridLayout.addWidget(self.chkBackwardRepresentativeRelation, 5, 3, 1, 1)
        self.lblEpidemic = QtGui.QLabel(ItemEditorDialog)
        self.lblEpidemic.setObjectName(_fromUtf8("lblEpidemic"))
        self.gridLayout.addWidget(self.lblEpidemic, 6, 0, 1, 1)
        self.chkDirectEpidemicRelation = QtGui.QCheckBox(ItemEditorDialog)
        self.chkDirectEpidemicRelation.setObjectName(_fromUtf8("chkDirectEpidemicRelation"))
        self.gridLayout.addWidget(self.chkDirectEpidemicRelation, 6, 1, 1, 1)
        self.chkBackwardEpidemicRelation = QtGui.QCheckBox(ItemEditorDialog)
        self.chkBackwardEpidemicRelation.setObjectName(_fromUtf8("chkBackwardEpidemicRelation"))
        self.gridLayout.addWidget(self.chkBackwardEpidemicRelation, 6, 3, 1, 1)
        self.lblDonation = QtGui.QLabel(ItemEditorDialog)
        self.lblDonation.setObjectName(_fromUtf8("lblDonation"))
        self.gridLayout.addWidget(self.lblDonation, 7, 0, 1, 1)
        self.chkDirectDonationRelation = QtGui.QCheckBox(ItemEditorDialog)
        self.chkDirectDonationRelation.setObjectName(_fromUtf8("chkDirectDonationRelation"))
        self.gridLayout.addWidget(self.chkDirectDonationRelation, 7, 1, 1, 1)
        self.chkBackwardDonationRelation = QtGui.QCheckBox(ItemEditorDialog)
        self.chkBackwardDonationRelation.setObjectName(_fromUtf8("chkBackwardDonationRelation"))
        self.gridLayout.addWidget(self.chkBackwardDonationRelation, 7, 3, 1, 1)
        self.lblLeftSex = QtGui.QLabel(ItemEditorDialog)
        self.lblLeftSex.setObjectName(_fromUtf8("lblLeftSex"))
        self.gridLayout.addWidget(self.lblLeftSex, 8, 0, 1, 1)
        self.cmbLeftSex = QtGui.QComboBox(ItemEditorDialog)
        self.cmbLeftSex.setObjectName(_fromUtf8("cmbLeftSex"))
        self.cmbLeftSex.addItem(_fromUtf8(""))
        self.cmbLeftSex.setItemText(0, _fromUtf8(""))
        self.cmbLeftSex.addItem(_fromUtf8(""))
        self.cmbLeftSex.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbLeftSex, 8, 1, 1, 1)
        self.lblRightSex = QtGui.QLabel(ItemEditorDialog)
        self.lblRightSex.setObjectName(_fromUtf8("lblRightSex"))
        self.gridLayout.addWidget(self.lblRightSex, 8, 2, 1, 1)
        self.cmbRightSex = QtGui.QComboBox(ItemEditorDialog)
        self.cmbRightSex.setObjectName(_fromUtf8("cmbRightSex"))
        self.cmbRightSex.addItem(_fromUtf8(""))
        self.cmbRightSex.setItemText(0, _fromUtf8(""))
        self.cmbRightSex.addItem(_fromUtf8(""))
        self.cmbRightSex.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cmbRightSex, 8, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(103, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ItemEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 4)
        self.edtRegionalReverseCode = QtGui.QLineEdit(ItemEditorDialog)
        self.edtRegionalReverseCode.setObjectName(_fromUtf8("edtRegionalReverseCode"))
        self.gridLayout.addWidget(self.edtRegionalReverseCode, 2, 1, 1, 3)
        self.lblRegionalReverseCode = QtGui.QLabel(ItemEditorDialog)
        self.lblRegionalReverseCode.setObjectName(_fromUtf8("lblRegionalReverseCode"))
        self.gridLayout.addWidget(self.lblRegionalReverseCode, 2, 0, 1, 1)
        self.lblCode.setBuddy(self.edtCode)
        self.lblRegionalCode.setBuddy(self.edtRegionalCode)
        self.lblLeftName.setBuddy(self.edtLeftName)
        self.lblRightName.setBuddy(self.edtRightName)
        self.lblGenetic.setBuddy(self.chkDirectGeneticRelation)
        self.lblRepresentative.setBuddy(self.chkDirectRepresentativeRelation)
        self.lblEpidemic.setBuddy(self.chkDirectEpidemicRelation)
        self.lblDonation.setBuddy(self.chkDirectDonationRelation)
        self.lblLeftSex.setBuddy(self.cmbLeftSex)
        self.lblRightSex.setBuddy(self.cmbRightSex)
        self.lblRegionalReverseCode.setBuddy(self.edtRegionalReverseCode)

        self.retranslateUi(ItemEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ItemEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ItemEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ItemEditorDialog)
        ItemEditorDialog.setTabOrder(self.edtCode, self.edtRegionalCode)
        ItemEditorDialog.setTabOrder(self.edtRegionalCode, self.edtRegionalReverseCode)
        ItemEditorDialog.setTabOrder(self.edtRegionalReverseCode, self.edtLeftName)
        ItemEditorDialog.setTabOrder(self.edtLeftName, self.edtRightName)
        ItemEditorDialog.setTabOrder(self.edtRightName, self.chkDirectGeneticRelation)
        ItemEditorDialog.setTabOrder(self.chkDirectGeneticRelation, self.chkBackwardGeneticRelation)
        ItemEditorDialog.setTabOrder(self.chkBackwardGeneticRelation, self.chkDirectRepresentativeRelation)
        ItemEditorDialog.setTabOrder(self.chkDirectRepresentativeRelation, self.chkBackwardRepresentativeRelation)
        ItemEditorDialog.setTabOrder(self.chkBackwardRepresentativeRelation, self.chkDirectEpidemicRelation)
        ItemEditorDialog.setTabOrder(self.chkDirectEpidemicRelation, self.chkBackwardEpidemicRelation)
        ItemEditorDialog.setTabOrder(self.chkBackwardEpidemicRelation, self.chkDirectDonationRelation)
        ItemEditorDialog.setTabOrder(self.chkDirectDonationRelation, self.chkBackwardDonationRelation)
        ItemEditorDialog.setTabOrder(self.chkBackwardDonationRelation, self.cmbLeftSex)
        ItemEditorDialog.setTabOrder(self.cmbLeftSex, self.cmbRightSex)
        ItemEditorDialog.setTabOrder(self.cmbRightSex, self.buttonBox)

    def retranslateUi(self, ItemEditorDialog):
        ItemEditorDialog.setWindowTitle(QtGui.QApplication.translate("ItemEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRegionalCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Региональный код отношения", None, QtGui.QApplication.UnicodeUTF8))
        self.lblLeftName.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Субьект отношения", None, QtGui.QApplication.UnicodeUTF8))
        self.edtLeftName.setToolTip(QtGui.QApplication.translate("ItemEditorDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">(лат.) предметы, всякое лицо, вещь, о коих говорится.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">--</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Словарь Даля </span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRightName.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Объект отношения", None, QtGui.QApplication.UnicodeUTF8))
        self.edtRightName.setToolTip(QtGui.QApplication.translate("ItemEditorDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">(лат.) предмет противоположный субъекту.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">--</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Словарь Даля</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.lblGenetic.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Генетическая связь", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDirectGeneticRelation.setToolTip(QtGui.QApplication.translate("ItemEditorDialog", "Передача генетического материала от субъекта к объекту", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDirectGeneticRelation.setText(QtGui.QApplication.translate("ItemEditorDialog", "Прямая", None, QtGui.QApplication.UnicodeUTF8))
        self.chkBackwardGeneticRelation.setToolTip(QtGui.QApplication.translate("ItemEditorDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Передача генетического материала от объекта к субъекту</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.chkBackwardGeneticRelation.setText(QtGui.QApplication.translate("ItemEditorDialog", "Обратная", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRepresentative.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Представительская связь", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDirectRepresentativeRelation.setToolTip(QtGui.QApplication.translate("ItemEditorDialog", "Субъект является представителем объекта", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDirectRepresentativeRelation.setText(QtGui.QApplication.translate("ItemEditorDialog", "Прямая", None, QtGui.QApplication.UnicodeUTF8))
        self.chkBackwardRepresentativeRelation.setToolTip(QtGui.QApplication.translate("ItemEditorDialog", "Объект является представителем субъекта", None, QtGui.QApplication.UnicodeUTF8))
        self.chkBackwardRepresentativeRelation.setText(QtGui.QApplication.translate("ItemEditorDialog", "Обратная", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEpidemic.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Эпид.контактирование", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDirectEpidemicRelation.setToolTip(QtGui.QApplication.translate("ItemEditorDialog", "Возможна передача от субъекта к объекту", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDirectEpidemicRelation.setText(QtGui.QApplication.translate("ItemEditorDialog", "Прямое", None, QtGui.QApplication.UnicodeUTF8))
        self.chkBackwardEpidemicRelation.setToolTip(QtGui.QApplication.translate("ItemEditorDialog", "Возможна передача от объекта к субъекту", None, QtGui.QApplication.UnicodeUTF8))
        self.chkBackwardEpidemicRelation.setText(QtGui.QApplication.translate("ItemEditorDialog", "Обратное", None, QtGui.QApplication.UnicodeUTF8))
        self.lblDonation.setText(QtGui.QApplication.translate("ItemEditorDialog", "&Донорство", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDirectDonationRelation.setToolTip(QtGui.QApplication.translate("ItemEditorDialog", "Передача органов от субъекта к объекту", None, QtGui.QApplication.UnicodeUTF8))
        self.chkDirectDonationRelation.setText(QtGui.QApplication.translate("ItemEditorDialog", "Прямое", None, QtGui.QApplication.UnicodeUTF8))
        self.chkBackwardDonationRelation.setToolTip(QtGui.QApplication.translate("ItemEditorDialog", "Передача органов от объекта к субъекту", None, QtGui.QApplication.UnicodeUTF8))
        self.chkBackwardDonationRelation.setText(QtGui.QApplication.translate("ItemEditorDialog", "Обратное", None, QtGui.QApplication.UnicodeUTF8))
        self.lblLeftSex.setText(QtGui.QApplication.translate("ItemEditorDialog", "Пол субъекта", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbLeftSex.setItemText(1, QtGui.QApplication.translate("ItemEditorDialog", "мужской", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbLeftSex.setItemText(2, QtGui.QApplication.translate("ItemEditorDialog", "женский", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRightSex.setText(QtGui.QApplication.translate("ItemEditorDialog", "Пол объекта", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRightSex.setItemText(1, QtGui.QApplication.translate("ItemEditorDialog", "мужской", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbRightSex.setItemText(2, QtGui.QApplication.translate("ItemEditorDialog", "женский", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRegionalReverseCode.setText(QtGui.QApplication.translate("ItemEditorDialog", "Региональный код &обратного отношения", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ItemEditorDialog = QtGui.QDialog()
    ui = Ui_ItemEditorDialog()
    ui.setupUi(ItemEditorDialog)
    ItemEditorDialog.show()
    sys.exit(app.exec_())

