# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\RefBooks\ServiceFilterDialog.ui'
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

class Ui_ServiceFilterDialog(object):
    def setupUi(self, ServiceFilterDialog):
        ServiceFilterDialog.setObjectName(_fromUtf8("ServiceFilterDialog"))
        ServiceFilterDialog.resize(267, 283)
        ServiceFilterDialog.setSizeGripEnabled(True)
        self.gridLayout = QtGui.QGridLayout(ServiceFilterDialog)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblSection = QtGui.QLabel(ServiceFilterDialog)
        self.lblSection.setObjectName(_fromUtf8("lblSection"))
        self.gridLayout.addWidget(self.lblSection, 1, 0, 1, 1)
        self.cmbSection = CRBComboBox(ServiceFilterDialog)
        self.cmbSection.setObjectName(_fromUtf8("cmbSection"))
        self.gridLayout.addWidget(self.cmbSection, 1, 1, 1, 1)
        self.lblType = QtGui.QLabel(ServiceFilterDialog)
        self.lblType.setObjectName(_fromUtf8("lblType"))
        self.gridLayout.addWidget(self.lblType, 2, 0, 1, 1)
        self.cmbType = CRBComboBox(ServiceFilterDialog)
        self.cmbType.setObjectName(_fromUtf8("cmbType"))
        self.gridLayout.addWidget(self.cmbType, 2, 1, 1, 1)
        self.lblClass = QtGui.QLabel(ServiceFilterDialog)
        self.lblClass.setObjectName(_fromUtf8("lblClass"))
        self.gridLayout.addWidget(self.lblClass, 3, 0, 1, 1)
        self.cmbClass = CRBComboBox(ServiceFilterDialog)
        self.cmbClass.setObjectName(_fromUtf8("cmbClass"))
        self.gridLayout.addWidget(self.cmbClass, 3, 1, 1, 1)
        self.lblCode = QtGui.QLabel(ServiceFilterDialog)
        self.lblCode.setObjectName(_fromUtf8("lblCode"))
        self.gridLayout.addWidget(self.lblCode, 4, 0, 1, 1)
        self.edtCode = QtGui.QLineEdit(ServiceFilterDialog)
        self.edtCode.setObjectName(_fromUtf8("edtCode"))
        self.gridLayout.addWidget(self.edtCode, 4, 1, 1, 1)
        self.lblName = QtGui.QLabel(ServiceFilterDialog)
        self.lblName.setObjectName(_fromUtf8("lblName"))
        self.gridLayout.addWidget(self.lblName, 5, 0, 1, 1)
        self.edtName = QtGui.QLineEdit(ServiceFilterDialog)
        self.edtName.setObjectName(_fromUtf8("edtName"))
        self.gridLayout.addWidget(self.edtName, 5, 1, 1, 1)
        self.chkEIS = QtGui.QCheckBox(ServiceFilterDialog)
        self.chkEIS.setTristate(True)
        self.chkEIS.setObjectName(_fromUtf8("chkEIS"))
        self.gridLayout.addWidget(self.chkEIS, 6, 0, 1, 2)
        self.chkNomenclature = QtGui.QCheckBox(ServiceFilterDialog)
        self.chkNomenclature.setTristate(True)
        self.chkNomenclature.setObjectName(_fromUtf8("chkNomenclature"))
        self.gridLayout.addWidget(self.chkNomenclature, 7, 0, 1, 2)
        self.lblPeriod = QtGui.QLabel(ServiceFilterDialog)
        self.lblPeriod.setObjectName(_fromUtf8("lblPeriod"))
        self.gridLayout.addWidget(self.lblPeriod, 8, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblFrom = QtGui.QLabel(ServiceFilterDialog)
        self.lblFrom.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblFrom.setObjectName(_fromUtf8("lblFrom"))
        self.horizontalLayout.addWidget(self.lblFrom)
        self.edtBegDate = CDateEdit(ServiceFilterDialog)
        self.edtBegDate.setObjectName(_fromUtf8("edtBegDate"))
        self.horizontalLayout.addWidget(self.edtBegDate)
        self.lblTo = QtGui.QLabel(ServiceFilterDialog)
        self.lblTo.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lblTo.setObjectName(_fromUtf8("lblTo"))
        self.horizontalLayout.addWidget(self.lblTo)
        self.edtEndDate = CDateEdit(ServiceFilterDialog)
        self.edtEndDate.setObjectName(_fromUtf8("edtEndDate"))
        self.horizontalLayout.addWidget(self.edtEndDate)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout, 9, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 10, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ServiceFilterDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 11, 0, 1, 2)
        self.cmbServiceGroup = CRBComboBox(ServiceFilterDialog)
        self.cmbServiceGroup.setObjectName(_fromUtf8("cmbServiceGroup"))
        self.gridLayout.addWidget(self.cmbServiceGroup, 0, 1, 1, 1)
        self.lblServiceGroup = QtGui.QLabel(ServiceFilterDialog)
        self.lblServiceGroup.setObjectName(_fromUtf8("lblServiceGroup"))
        self.gridLayout.addWidget(self.lblServiceGroup, 0, 0, 1, 1)
        self.lblSection.setBuddy(self.cmbSection)
        self.lblType.setBuddy(self.cmbType)
        self.lblClass.setBuddy(self.cmbClass)
        self.lblCode.setBuddy(self.edtCode)
        self.lblName.setBuddy(self.edtName)
        self.lblFrom.setBuddy(self.edtBegDate)
        self.lblTo.setBuddy(self.edtEndDate)
        self.lblServiceGroup.setBuddy(self.cmbServiceGroup)

        self.retranslateUi(ServiceFilterDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ServiceFilterDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ServiceFilterDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ServiceFilterDialog)
        ServiceFilterDialog.setTabOrder(self.cmbServiceGroup, self.cmbSection)
        ServiceFilterDialog.setTabOrder(self.cmbSection, self.cmbType)
        ServiceFilterDialog.setTabOrder(self.cmbType, self.cmbClass)
        ServiceFilterDialog.setTabOrder(self.cmbClass, self.edtCode)
        ServiceFilterDialog.setTabOrder(self.edtCode, self.edtName)
        ServiceFilterDialog.setTabOrder(self.edtName, self.chkEIS)
        ServiceFilterDialog.setTabOrder(self.chkEIS, self.chkNomenclature)
        ServiceFilterDialog.setTabOrder(self.chkNomenclature, self.edtBegDate)
        ServiceFilterDialog.setTabOrder(self.edtBegDate, self.edtEndDate)
        ServiceFilterDialog.setTabOrder(self.edtEndDate, self.buttonBox)

    def retranslateUi(self, ServiceFilterDialog):
        ServiceFilterDialog.setWindowTitle(QtGui.QApplication.translate("ServiceFilterDialog", "Фильтр услуг", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSection.setText(QtGui.QApplication.translate("ServiceFilterDialog", "&Раздел", None, QtGui.QApplication.UnicodeUTF8))
        self.lblType.setText(QtGui.QApplication.translate("ServiceFilterDialog", "&Тип", None, QtGui.QApplication.UnicodeUTF8))
        self.lblClass.setText(QtGui.QApplication.translate("ServiceFilterDialog", "&Класс", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCode.setText(QtGui.QApplication.translate("ServiceFilterDialog", "Код начинается &с", None, QtGui.QApplication.UnicodeUTF8))
        self.lblName.setText(QtGui.QApplication.translate("ServiceFilterDialog", "&Название содержит", None, QtGui.QApplication.UnicodeUTF8))
        self.chkEIS.setText(QtGui.QApplication.translate("ServiceFilterDialog", "Унаследовано из ЕИС", None, QtGui.QApplication.UnicodeUTF8))
        self.chkNomenclature.setText(QtGui.QApplication.translate("ServiceFilterDialog", "Унаследовано из номенклатуры", None, QtGui.QApplication.UnicodeUTF8))
        self.lblPeriod.setText(QtGui.QApplication.translate("ServiceFilterDialog", "Период:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFrom.setText(QtGui.QApplication.translate("ServiceFilterDialog", "c", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTo.setText(QtGui.QApplication.translate("ServiceFilterDialog", "по", None, QtGui.QApplication.UnicodeUTF8))
        self.lblServiceGroup.setText(QtGui.QApplication.translate("ServiceFilterDialog", "&Группа", None, QtGui.QApplication.UnicodeUTF8))

from library.crbcombobox import CRBComboBox
from library.DateEdit import CDateEdit

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ServiceFilterDialog = QtGui.QDialog()
    ui = Ui_ServiceFilterDialog()
    ui.setupUi(ServiceFilterDialog)
    ServiceFilterDialog.show()
    sys.exit(app.exec_())

