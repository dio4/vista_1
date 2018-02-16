# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\Timeline\TemplatePersonsCreate.ui'
#
# Created: Fri Jun 15 12:16:52 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_TemplatePersonsCreate(object):
    def setupUi(self, TemplatePersonsCreate):
        TemplatePersonsCreate.setObjectName(_fromUtf8("TemplatePersonsCreate"))
        TemplatePersonsCreate.resize(400, 385)
        self.gridLayout = QtGui.QGridLayout(TemplatePersonsCreate)
        self.gridLayout.setMargin(4)
        self.gridLayout.setHorizontalSpacing(4)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblInfo = QtGui.QLabel(TemplatePersonsCreate)
        self.lblInfo.setAlignment(QtCore.Qt.AlignCenter)
        self.lblInfo.setObjectName(_fromUtf8("lblInfo"))
        self.gridLayout.addWidget(self.lblInfo, 0, 0, 1, 2)
        self.lblPersonName = QtGui.QLabel(TemplatePersonsCreate)
        self.lblPersonName.setText(_fromUtf8(""))
        self.lblPersonName.setAlignment(QtCore.Qt.AlignCenter)
        self.lblPersonName.setObjectName(_fromUtf8("lblPersonName"))
        self.gridLayout.addWidget(self.lblPersonName, 1, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 72, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.prbTemplateCreate = QtGui.QProgressBar(TemplatePersonsCreate)
        self.prbTemplateCreate.setProperty("value", 24)
        self.prbTemplateCreate.setObjectName(_fromUtf8("prbTemplateCreate"))
        self.gridLayout.addWidget(self.prbTemplateCreate, 3, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(20, 108, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 4, 0, 1, 1)
        self.lblCountSelected = QtGui.QLabel(TemplatePersonsCreate)
        self.lblCountSelected.setObjectName(_fromUtf8("lblCountSelected"))
        self.gridLayout.addWidget(self.lblCountSelected, 5, 0, 1, 1)
        self.lblCountCreate = QtGui.QLabel(TemplatePersonsCreate)
        self.lblCountCreate.setObjectName(_fromUtf8("lblCountCreate"))
        self.gridLayout.addWidget(self.lblCountCreate, 5, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 6, 0, 1, 1)

        self.retranslateUi(TemplatePersonsCreate)
        QtCore.QMetaObject.connectSlotsByName(TemplatePersonsCreate)

    def retranslateUi(self, TemplatePersonsCreate):
        TemplatePersonsCreate.setWindowTitle(QtGui.QApplication.translate("TemplatePersonsCreate", "Массовое добавление графиков на специалистов", None, QtGui.QApplication.UnicodeUTF8))
        self.lblInfo.setText(QtGui.QApplication.translate("TemplatePersonsCreate", "СОЗДАЕТСЯ ГРАФИК НА СПЕЦИАЛИСТА ", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCountSelected.setText(QtGui.QApplication.translate("TemplatePersonsCreate", "Выбрано всего строк 0", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCountCreate.setText(QtGui.QApplication.translate("TemplatePersonsCreate", "Обработано всего строк 0", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TemplatePersonsCreate = QtGui.QWidget()
    ui = Ui_TemplatePersonsCreate()
    ui.setupUi(TemplatePersonsCreate)
    TemplatePersonsCreate.show()
    sys.exit(app.exec_())

