# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\ActionPropertyTemplateEditor.ui'
#
# Created: Fri Jun 15 12:15:35 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ActionPropertyTemplateEditorDialog(object):
    def setupUi(self, ActionPropertyTemplateEditorDialog):
        ActionPropertyTemplateEditorDialog.setObjectName(_fromUtf8("ActionPropertyTemplateEditorDialog"))
        ActionPropertyTemplateEditorDialog.resize(349, 273)
        ActionPropertyTemplateEditorDialog.setSizeGripEnabled(True)
        self.gridlayout = QtGui.QGridLayout(ActionPropertyTemplateEditorDialog)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.lblCode = QtGui.QLabel(ActionPropertyTemplateEditorDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridlayout.addWidget(self.lblCode, 0, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ActionPropertyTemplateEditorDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridlayout.addWidget(self.edtCode, 0, 1, 1, 6)
        spacerItem = QtGui.QSpacerItem(321, 22, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem, 0, 7, 1, 1)
        self.lblFederalCode = QtGui.QLabel(ActionPropertyTemplateEditorDialog)
        self.lblFederalCode.setObjectName(_fromUtf8("lblFederalCode"))
        self.gridlayout.addWidget(self.lblFederalCode, 1, 0, 1, 1)
        self.edtFederalCode = QtGui.QLineEdit(ActionPropertyTemplateEditorDialog)
        self.edtFederalCode.setObjectName(_fromUtf8("edtFederalCode"))
        self.gridlayout.addWidget(self.edtFederalCode, 1, 1, 1, 6)
        spacerItem1 = QtGui.QSpacerItem(171, 22, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem1, 1, 7, 1, 1)
        self.lblRegionalCode = QtGui.QLabel(ActionPropertyTemplateEditorDialog)
        self.lblRegionalCode.setObjectName(_fromUtf8("lblRegionalCode"))
        self.gridlayout.addWidget(self.lblRegionalCode, 2, 0, 1, 1)
        self.edtRegionalCode = QtGui.QLineEdit(ActionPropertyTemplateEditorDialog)
        self.edtRegionalCode.setObjectName(_fromUtf8("edtRegionalCode"))
        self.gridlayout.addWidget(self.edtRegionalCode, 2, 1, 1, 6)
        spacerItem2 = QtGui.QSpacerItem(171, 22, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem2, 2, 7, 1, 1)
        self.lblGroup = QtGui.QLabel(ActionPropertyTemplateEditorDialog)
        self.lblGroup.setObjectName(_fromUtf8("lblGroup"))
        self.gridlayout.addWidget(self.lblGroup, 3, 0, 1, 1)
        self.cmbGroup = CActionPropertyTemplateComboBox(ActionPropertyTemplateEditorDialog)
        self.cmbGroup.setObjectName(_fromUtf8("cmbGroup"))
        self.gridlayout.addWidget(self.cmbGroup, 3, 1, 1, 7)
        self.lblName = QtGui.QLabel(ActionPropertyTemplateEditorDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridlayout.addWidget(self.lblName, 4, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ActionPropertyTemplateEditorDialog)
        self.edtName.setMinimumSize(QtCore.QSize(200, 0))
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridlayout.addWidget(self.edtName, 4, 1, 1, 7)
        self.lblAbbrev = QtGui.QLabel(ActionPropertyTemplateEditorDialog)
        self.lblAbbrev.setObjectName(_fromUtf8("lblAbbrev"))
        self.gridlayout.addWidget(self.lblAbbrev, 5, 0, 1, 1)
        self.edtAbbrev = QtGui.QLineEdit(ActionPropertyTemplateEditorDialog)
        self.edtAbbrev.setMinimumSize(QtCore.QSize(200, 0))
        self.edtAbbrev.setObjectName(_fromUtf8("edtAbbrev"))
        self.gridlayout.addWidget(self.edtAbbrev, 5, 1, 1, 7)
        self.lblSex = QtGui.QLabel(ActionPropertyTemplateEditorDialog)
        self.lblSex.setObjectName(_fromUtf8("lblSex"))
        self.gridlayout.addWidget(self.lblSex, 6, 0, 1, 1)
        self.cmbSex = QtGui.QComboBox(ActionPropertyTemplateEditorDialog)
        self.cmbSex.setObjectName(_fromUtf8("cmbSex"))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.setItemText(0, _fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.cmbSex.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbSex, 6, 1, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(231, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem3, 6, 2, 1, 6)
        self.lblAge = QtGui.QLabel(ActionPropertyTemplateEditorDialog)
        self.lblAge.setObjectName(_fromUtf8("lblAge"))
        self.gridlayout.addWidget(self.lblAge, 7, 0, 1, 1)
        self.cmbBegAgeUnit = QtGui.QComboBox(ActionPropertyTemplateEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbBegAgeUnit.sizePolicy().hasHeightForWidth())
        self.cmbBegAgeUnit.setSizePolicy(sizePolicy)
        self.cmbBegAgeUnit.setObjectName(_fromUtf8("cmbBegAgeUnit"))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.setItemText(0, _fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.cmbBegAgeUnit.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbBegAgeUnit, 7, 1, 1, 1)
        self.edtBegAgeCount = QtGui.QLineEdit(ActionPropertyTemplateEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtBegAgeCount.sizePolicy().hasHeightForWidth())
        self.edtBegAgeCount.setSizePolicy(sizePolicy)
        self.edtBegAgeCount.setMaxLength(3)
        self.edtBegAgeCount.setObjectName(_fromUtf8("edtBegAgeCount"))
        self.gridlayout.addWidget(self.edtBegAgeCount, 7, 2, 1, 1)
        self.lblAgeSep = QtGui.QLabel(ActionPropertyTemplateEditorDialog)
        self.lblAgeSep.setObjectName(_fromUtf8("lblAgeSep"))
        self.gridlayout.addWidget(self.lblAgeSep, 7, 3, 1, 1)
        self.cmbEndAgeUnit = QtGui.QComboBox(ActionPropertyTemplateEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbEndAgeUnit.sizePolicy().hasHeightForWidth())
        self.cmbEndAgeUnit.setSizePolicy(sizePolicy)
        self.cmbEndAgeUnit.setObjectName(_fromUtf8("cmbEndAgeUnit"))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.setItemText(0, _fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.cmbEndAgeUnit.addItem(_fromUtf8(""))
        self.gridlayout.addWidget(self.cmbEndAgeUnit, 7, 4, 1, 2)
        self.edtEndAgeCount = QtGui.QLineEdit(ActionPropertyTemplateEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtEndAgeCount.sizePolicy().hasHeightForWidth())
        self.edtEndAgeCount.setSizePolicy(sizePolicy)
        self.edtEndAgeCount.setMaxLength(3)
        self.edtEndAgeCount.setObjectName(_fromUtf8("edtEndAgeCount"))
        self.gridlayout.addWidget(self.edtEndAgeCount, 7, 6, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(71, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridlayout.addItem(spacerItem4, 7, 7, 1, 1)
        self.lblService = QtGui.QLabel(ActionPropertyTemplateEditorDialog)
        self.lblService.setObjectName(_fromUtf8("lblService"))
        self.gridlayout.addWidget(self.lblService, 8, 0, 1, 1)
        self.cmbService = CRBComboBox(ActionPropertyTemplateEditorDialog)
        self.cmbService.setObjectName(_fromUtf8("cmbService"))
        self.gridlayout.addWidget(self.cmbService, 8, 1, 1, 7)
        spacerItem5 = QtGui.QSpacerItem(73, 231, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem5, 9, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ActionPropertyTemplateEditorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridlayout.addWidget(self.buttonBox, 10, 0, 1, 8)
        self.lblCode.setBuddy(self.edtCode)
        self.lblFederalCode.setBuddy(self.edtFederalCode)
        self.lblRegionalCode.setBuddy(self.edtRegionalCode)
        self.lblGroup.setBuddy(self.cmbGroup)
        self.lblName.setBuddy(self.edtName)
        self.lblAbbrev.setBuddy(self.edtAbbrev)
        self.lblSex.setBuddy(self.cmbSex)
        self.lblAge.setBuddy(self.cmbBegAgeUnit)
        self.lblAgeSep.setBuddy(self.cmbEndAgeUnit)
        self.lblService.setBuddy(self.cmbService)

        self.retranslateUi(ActionPropertyTemplateEditorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ActionPropertyTemplateEditorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ActionPropertyTemplateEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ActionPropertyTemplateEditorDialog)
        ActionPropertyTemplateEditorDialog.setTabOrder(self.edtCode, self.edtFederalCode)
        ActionPropertyTemplateEditorDialog.setTabOrder(self.edtFederalCode, self.edtRegionalCode)
        ActionPropertyTemplateEditorDialog.setTabOrder(self.edtRegionalCode, self.cmbGroup)
        ActionPropertyTemplateEditorDialog.setTabOrder(self.cmbGroup, self.edtName)
        ActionPropertyTemplateEditorDialog.setTabOrder(self.edtName, self.edtAbbrev)
        ActionPropertyTemplateEditorDialog.setTabOrder(self.edtAbbrev, self.cmbSex)
        ActionPropertyTemplateEditorDialog.setTabOrder(self.cmbSex, self.cmbBegAgeUnit)
        ActionPropertyTemplateEditorDialog.setTabOrder(self.cmbBegAgeUnit, self.edtBegAgeCount)
        ActionPropertyTemplateEditorDialog.setTabOrder(self.edtBegAgeCount, self.cmbEndAgeUnit)
        ActionPropertyTemplateEditorDialog.setTabOrder(self.cmbEndAgeUnit, self.edtEndAgeCount)
        ActionPropertyTemplateEditorDialog.setTabOrder(self.edtEndAgeCount, self.cmbService)
        ActionPropertyTemplateEditorDialog.setTabOrder(self.cmbService, self.buttonBox)

    def retranslateUi(self, ActionPropertyTemplateEditorDialog):
        ActionPropertyTemplateEditorDialog.setWindowTitle(QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "ChangeMe!", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "&Код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFederalCode.setText(QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "&Федеральный код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRegionalCode.setText(QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "&Региональный код", None, QtGui.QApplication.UnicodeUTF8))
        self.lblGroup.setText(QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "&Группа", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "На&именование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAbbrev.setText(QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "&Сокращение", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSex.setText(QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "&Пол", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSex.setItemText(1, QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "М", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbSex.setItemText(2, QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "Ж", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAge.setText(QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "&Возраст", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbBegAgeUnit.setItemText(1, QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "Д", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbBegAgeUnit.setItemText(2, QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "Н", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbBegAgeUnit.setItemText(3, QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "М", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbBegAgeUnit.setItemText(4, QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "Г", None, QtGui.QApplication.UnicodeUTF8))
        self.edtBegAgeCount.setInputMask(QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "000; ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblAgeSep.setText(QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbEndAgeUnit.setItemText(1, QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "Д", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbEndAgeUnit.setItemText(2, QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "Н", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbEndAgeUnit.setItemText(3, QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "М", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbEndAgeUnit.setItemText(4, QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "Г", None, QtGui.QApplication.UnicodeUTF8))
        self.edtEndAgeCount.setInputMask(QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "000; ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblService.setText(QtGui.QApplication.translate("ActionPropertyTemplateEditorDialog", "&Услуга", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from Events.ActionPropertyTemplateComboBox import CActionPropertyTemplateComboBox

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ActionPropertyTemplateEditorDialog = QtGui.QDialog()
    ui = Ui_ActionPropertyTemplateEditorDialog()
    ui.setupUi(ActionPropertyTemplateEditorDialog)
    ActionPropertyTemplateEditorDialog.show()
    sys.exit(app.exec_())

