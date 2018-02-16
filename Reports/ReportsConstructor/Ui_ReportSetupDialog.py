# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_RCReportDialog(object):
    def setupUi(self, RCReportDialog, modelParams):
        RCReportDialog.setObjectName(_fromUtf8("RCReportDialog"))
        RCReportDialog.resize(398, 125)
        self.gridLayout = QtGui.QGridLayout(RCReportDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.currentRow = 0
        inputs = {}
        self.inputTypes = {'cmbInsurer': CInsurerComboBox,
                           'cmbOrgStructure': COrgStructureComboBox,
                           'cmbContract': CContractComboBox,
                           'cmbPerson': CPersonComboBoxEx}
        order = ['begDate', 'endDate']
        for code in order:
            param = modelParams.get(code)
            if param:
                inputs.update(self.addInput(RCReportDialog, self.gridLayout, param))
        for code, param in modelParams.items():
            if not code in order:
                inputs.update(self.addInput(RCReportDialog, self.gridLayout, param))

        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, self.currentRow, 1, 1, 1)
        self.currentRow += 1
        self.buttonBox = QtGui.QDialogButtonBox(RCReportDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, self.currentRow, 2, 1, 1)

        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), RCReportDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), RCReportDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RCReportDialog)
        return inputs

    def addControl(self, mainWidget, gridLayout, control, column = 0, rowSpan = 1, columnSpan = 1):
        type = control.get('type')
        name = control.get('name')
        text = control.get('title')
        inputCode = control.get('inputCode')
        baseCode = control.get('baseCode')
        visible = control.get('visible')
        if type == 'lbl':
            column = 0
            columnSpan = 1
            self.__setattr__(name, self.inputTypes.get(name, QtGui.QLabel)(mainWidget))
        elif type == 'cmb':
            column = 1
            columnSpan = 2
            self.__setattr__(name, self.inputTypes.get(name, CRBComboBox)(mainWidget))
        elif type == 'customCmb':
            column = 1
            columnSpan = 2
            self.__setattr__(name, self.inputTypes.get(name, QtGui.QComboBox)(mainWidget))
        elif type == 'lst':
            column = 0
            columnSpan = 3
            self.__setattr__(name, self.inputTypes.get(name, CRBListBox)(mainWidget))
        elif type == 'chk':
            column = 0
            columnSpan = 1
            self.__setattr__(name, self.inputTypes.get(name, QtGui.QCheckBox)(mainWidget))
            self.__getattribute__(name).clicked.connect(self.listBehavior)
        elif type == 'date':
            column = 1
            columnSpan = 1
            self.__setattr__(name, self.inputTypes.get(name, CDateEdit)(mainWidget))
            self.__getattribute__(name).setCalendarPopup(True)
        widget = self.__getattribute__(name)
        widget.setObjectName(_fromUtf8(name))

        if text:
            widget.setText(_translate("RCReportDialog", text, None))
        if visible != None:
            widget.setVisible(visible)
        widget.type = type
        widget.code = inputCode
        widget.baseCode = baseCode
        gridLayout.addWidget(widget, self.currentRow, column, rowSpan, columnSpan)
        if inputCode:
            return {inputCode: widget}
        return {}


    def addInput(self, mainWidget, gridLayout, param):
        inputs = {}
        if not param:
            return inputs
        type = param.get('type')
        code = param.get('code')
        text = param.get('title', '')
        name = str(''.join([code[0].upper(), code[1:]]))
        if type == 'date':
            lbl = {'name': str(''.join(['lbl', name])),
                   'title': text,
                   'type': 'lbl'}
            date = {'name': str(''.join(['edt', name])),
                    'inputCode': code,
                    'type': 'date',
                    'baseCode': code}

            inputs.update(self.addControl(mainWidget, gridLayout, lbl))
            inputs.update(self.addControl(mainWidget, gridLayout, date))
            self.currentRow += 1

        elif type == 'cmb':
            lbl = {'name': str(''.join(['lbl', name])),
                   'title': text,
                   'type': 'lbl'}
            cmb = {'name': str(''.join(['cmb', name])),
                   'inputCode': str(''.join([code, 'Id'])),
                   'type': 'cmb',
                   'baseCode': code}

            inputs.update(self.addControl(mainWidget, gridLayout, lbl))
            inputs.update(self.addControl(mainWidget, gridLayout, cmb))
            self.currentRow += 1

        elif type == 'customCmb':
            lbl = {'name': str(''.join(['lbl', name])),
                   'title': text,
                   'type': 'lbl'}
            cmb = {'name': str(''.join(['cmb', name])),
                   'inputCode': str(code),
                   'type': 'customCmb',
                   'baseCode': code}

            inputs.update(self.addControl(mainWidget, gridLayout, lbl))
            inputs.update(self.addControl(mainWidget, gridLayout, cmb))
            self.currentRow += 1

        elif type == 'treeCmb':
            lbl = {'name': str(''.join(['lbl', name])),
                   'title': text,
                   'type': 'lbl'}
            cmb = {'name': str(''.join(['cmb', name])),
                   'inputCode': str(''.join([code, 'IdList'])),
                   'type': 'cmb',
                   'baseCode': code}

            inputs.update(self.addControl(mainWidget, gridLayout, lbl))
            inputs.update(self.addControl(mainWidget, gridLayout, cmb))
            self.currentRow += 1

        elif type == 'mixCmb':
            chk = {'name': str(''.join(['chk', name])),
                   'title': text,
                   'inputCode': str(''.join(['chk', name])),
                   'type': 'chk',
                   'baseCode': code}
            cmb = {'name': str(''.join(['cmb', name])),
                   'inputCode': str(''.join([code, 'Id'])),
                   'type': 'cmb',
                   'baseCode': code}
            lst = {'name': str(''.join(['lst', name])),
                   'inputCode': str(''.join(['lst', name])),
                   'type': 'lst',
                   'visible': False,
                   'baseCode': code}

            inputs.update(self.addControl(mainWidget, gridLayout, chk))
            inputs.update(self.addControl(mainWidget, gridLayout, cmb))
            self.currentRow += 1
            inputs.update(self.addControl(mainWidget, gridLayout, lst))
            self.currentRow += 1

        return {code: inputs}

    def listBehavior(self, bool):
        pass

from library.DateEdit import CDateEdit
from library.crbcombobox import CRBComboBox
from library.RBListBox import CRBListBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.OrgComboBox import CInsurerComboBox
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from Accounting.ContractComboBox import CContractComboBox
