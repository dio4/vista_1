# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\svn-s11\s11\TissueJournal\SamplePreparationDialog.ui'
#
# Created: Fri Jun 15 12:17:38 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SamplePreparationDialog(object):
    def setupUi(self, SamplePreparationDialog):
        SamplePreparationDialog.setObjectName(_fromUtf8("SamplePreparationDialog"))
        SamplePreparationDialog.resize(850, 716)
        SamplePreparationDialog.setSizeGripEnabled(True)
        self.gridLayout_2 = QtGui.QGridLayout(SamplePreparationDialog)
        self.gridLayout_2.setMargin(4)
        self.gridLayout_2.setSpacing(4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.splitter = QtGui.QSplitter(SamplePreparationDialog)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.pnlInfo = QtGui.QWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pnlInfo.sizePolicy().hasHeightForWidth())
        self.pnlInfo.setSizePolicy(sizePolicy)
        self.pnlInfo.setObjectName(_fromUtf8("pnlInfo"))
        self.verticalLayout = QtGui.QVBoxLayout(self.pnlInfo)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setMargin(4)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.textBrowser = CTextBrowser(self.pnlInfo)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.verticalLayout.addWidget(self.textBrowser)
        self.lblTissueRecordInfo = QtGui.QLabel(self.pnlInfo)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblTissueRecordInfo.sizePolicy().hasHeightForWidth())
        self.lblTissueRecordInfo.setSizePolicy(sizePolicy)
        self.lblTissueRecordInfo.setObjectName(_fromUtf8("lblTissueRecordInfo"))
        self.verticalLayout.addWidget(self.lblTissueRecordInfo)
        self.pnlItems = QtGui.QWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pnlItems.sizePolicy().hasHeightForWidth())
        self.pnlItems.setSizePolicy(sizePolicy)
        self.pnlItems.setObjectName(_fromUtf8("pnlItems"))
        self.gridLayout = QtGui.QGridLayout(self.pnlItems)
        self.gridLayout.setMargin(4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEquipment = QtGui.QLabel(self.pnlItems)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblEquipment.sizePolicy().hasHeightForWidth())
        self.lblEquipment.setSizePolicy(sizePolicy)
        self.lblEquipment.setObjectName(_fromUtf8("lblEquipment"))
        self.gridLayout.addWidget(self.lblEquipment, 0, 0, 1, 1)
        self.cmbEquipment = CRBComboBox(self.pnlItems)
        self.cmbEquipment.setObjectName(_fromUtf8("cmbEquipment"))
        self.gridLayout.addWidget(self.cmbEquipment, 0, 1, 1, 1)
        self.lblTestGroup = QtGui.QLabel(self.pnlItems)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblTestGroup.sizePolicy().hasHeightForWidth())
        self.lblTestGroup.setSizePolicy(sizePolicy)
        self.lblTestGroup.setObjectName(_fromUtf8("lblTestGroup"))
        self.gridLayout.addWidget(self.lblTestGroup, 0, 2, 1, 1)
        self.cmbTestGroup = CRBComboBox(self.pnlItems)
        self.cmbTestGroup.setObjectName(_fromUtf8("cmbTestGroup"))
        self.gridLayout.addWidget(self.cmbTestGroup, 0, 3, 1, 1)
        self.tblSamplePreparation = CSamplePreparationInDocTableView(self.pnlItems)
        self.tblSamplePreparation.setObjectName(_fromUtf8("tblSamplePreparation"))
        self.gridLayout.addWidget(self.tblSamplePreparation, 1, 0, 1, 5)
        self.btnSelectItems = QtGui.QPushButton(self.pnlItems)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnSelectItems.sizePolicy().hasHeightForWidth())
        self.btnSelectItems.setSizePolicy(sizePolicy)
        self.btnSelectItems.setObjectName(_fromUtf8("btnSelectItems"))
        self.gridLayout.addWidget(self.btnSelectItems, 0, 4, 1, 1)
        self.gridLayout_2.addWidget(self.splitter, 0, 0, 1, 5)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 1, 0, 1, 1)
        self.btnApply = QtGui.QPushButton(SamplePreparationDialog)
        self.btnApply.setObjectName(_fromUtf8("btnApply"))
        self.gridLayout_2.addWidget(self.btnApply, 1, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(SamplePreparationDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 4, 1, 1)
        self.btnSetEquipment = QtGui.QPushButton(SamplePreparationDialog)
        self.btnSetEquipment.setObjectName(_fromUtf8("btnSetEquipment"))
        self.gridLayout_2.addWidget(self.btnSetEquipment, 1, 3, 1, 1)

        self.retranslateUi(SamplePreparationDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SamplePreparationDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SamplePreparationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SamplePreparationDialog)

    def retranslateUi(self, SamplePreparationDialog):
        SamplePreparationDialog.setWindowTitle(QtGui.QApplication.translate("SamplePreparationDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTissueRecordInfo.setText(QtGui.QApplication.translate("SamplePreparationDialog", "Информация о биоматериале", None, QtGui.QApplication.UnicodeUTF8))
        self.lblEquipment.setText(QtGui.QApplication.translate("SamplePreparationDialog", "Оборудование", None, QtGui.QApplication.UnicodeUTF8))
        self.lblTestGroup.setText(QtGui.QApplication.translate("SamplePreparationDialog", "Группа тестов", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectItems.setText(QtGui.QApplication.translate("SamplePreparationDialog", "Выбрать", None, QtGui.QApplication.UnicodeUTF8))
        self.btnApply.setText(QtGui.QApplication.translate("SamplePreparationDialog", "Регистрация проб", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSetEquipment.setText(QtGui.QApplication.translate("SamplePreparationDialog", "Назначить оборудование", None, QtGui.QApplication.UnicodeUTF8))

from TissueJournal.TissueJournalModels import CSamplePreparationInDocTableView
from library.crbcombobox import CRBComboBox
from library.TextBrowser import CTextBrowser

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SamplePreparationDialog = QtGui.QDialog()
    ui = Ui_SamplePreparationDialog()
    ui.setupUi(SamplePreparationDialog)
    SamplePreparationDialog.show()
    sys.exit(app.exec_())

