# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EventNotesPageProtocol.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

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

class Ui_EventNotesPageWidget(object):
    def setupUi(self, EventNotesPageWidget):
        EventNotesPageWidget.setObjectName(_fromUtf8("EventNotesPageWidget"))
        EventNotesPageWidget.resize(748, 383)
        self.gridLayoutEventNotes = QtGui.QGridLayout(EventNotesPageWidget)
        self.gridLayoutEventNotes.setMargin(4)
        self.gridLayoutEventNotes.setSpacing(4)
        self.gridLayoutEventNotes.setObjectName(_fromUtf8("gridLayoutEventNotes"))
        self.scrollArea = QtGui.QScrollArea(EventNotesPageWidget)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 740, 375))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblEventCreateDateTime = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblEventCreateDateTime.setObjectName(_fromUtf8("lblEventCreateDateTime"))
        self.gridLayout.addWidget(self.lblEventCreateDateTime, 1, 0, 1, 1)
        self.lblEventCreatePersonValue = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblEventCreatePersonValue.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblEventCreatePersonValue.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblEventCreatePersonValue.setText(_fromUtf8(""))
        self.lblEventCreatePersonValue.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lblEventCreatePersonValue.setObjectName(_fromUtf8("lblEventCreatePersonValue"))
        self.gridLayout.addWidget(self.lblEventCreatePersonValue, 2, 1, 1, 1)
        self.lblEventId = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblEventId.setObjectName(_fromUtf8("lblEventId"))
        self.gridLayout.addWidget(self.lblEventId, 0, 0, 1, 1)
        self.cmbClientPolicy = CClientPolicyComboBox(self.scrollAreaWidgetContents)
        self.cmbClientPolicy.setObjectName(_fromUtf8("cmbClientPolicy"))
        self.gridLayout.addWidget(self.cmbClientPolicy, 5, 1, 1, 1)
        self.chkLPUReferral = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.chkLPUReferral.setObjectName(_fromUtf8("chkLPUReferral"))
        self.gridLayout.addWidget(self.chkLPUReferral, 6, 0, 1, 2)
        self.lblEventCreatePerson = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblEventCreatePerson.setObjectName(_fromUtf8("lblEventCreatePerson"))
        self.gridLayout.addWidget(self.lblEventCreatePerson, 2, 0, 1, 1)
        self.lblEventIdValue = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblEventIdValue.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblEventIdValue.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblEventIdValue.setText(_fromUtf8(""))
        self.lblEventIdValue.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lblEventIdValue.setObjectName(_fromUtf8("lblEventIdValue"))
        self.gridLayout.addWidget(self.lblEventIdValue, 0, 1, 1, 1)
        self.lblEventModifyPerson = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblEventModifyPerson.setObjectName(_fromUtf8("lblEventModifyPerson"))
        self.gridLayout.addWidget(self.lblEventModifyPerson, 4, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 154, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 0, 1, 1)
        self.lblEventNote = QtGui.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblEventNote.sizePolicy().hasHeightForWidth())
        self.lblEventNote.setSizePolicy(sizePolicy)
        self.lblEventNote.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lblEventNote.setObjectName(_fromUtf8("lblEventNote"))
        self.gridLayout.addWidget(self.lblEventNote, 8, 0, 1, 1)
        self.lblEventModifyDateTime = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblEventModifyDateTime.setObjectName(_fromUtf8("lblEventModifyDateTime"))
        self.gridLayout.addWidget(self.lblEventModifyDateTime, 3, 0, 1, 1)
        self.lblEventModifyPersonValue = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblEventModifyPersonValue.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblEventModifyPersonValue.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblEventModifyPersonValue.setText(_fromUtf8(""))
        self.lblEventModifyPersonValue.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lblEventModifyPersonValue.setObjectName(_fromUtf8("lblEventModifyPersonValue"))
        self.gridLayout.addWidget(self.lblEventModifyPersonValue, 4, 1, 1, 1)
        self.edtEventNote = QtGui.QTextEdit(self.scrollAreaWidgetContents)
        self.edtEventNote.setMinimumSize(QtCore.QSize(0, 100))
        self.edtEventNote.setObjectName(_fromUtf8("edtEventNote"))
        self.gridLayout.addWidget(self.edtEventNote, 8, 1, 2, 1)
        self.lblEventCreateDateTimeValue = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblEventCreateDateTimeValue.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblEventCreateDateTimeValue.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblEventCreateDateTimeValue.setText(_fromUtf8(""))
        self.lblEventCreateDateTimeValue.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lblEventCreateDateTimeValue.setObjectName(_fromUtf8("lblEventCreateDateTimeValue"))
        self.gridLayout.addWidget(self.lblEventCreateDateTimeValue, 1, 1, 1, 1)
        self.lblClientPolicy = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblClientPolicy.setObjectName(_fromUtf8("lblClientPolicy"))
        self.gridLayout.addWidget(self.lblClientPolicy, 5, 0, 1, 1)
        self.lblEventModifyDateTimeValue = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.lblEventModifyDateTimeValue.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblEventModifyDateTimeValue.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblEventModifyDateTimeValue.setText(_fromUtf8(""))
        self.lblEventModifyDateTimeValue.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lblEventModifyDateTimeValue.setObjectName(_fromUtf8("lblEventModifyDateTimeValue"))
        self.gridLayout.addWidget(self.lblEventModifyDateTimeValue, 3, 1, 1, 1)
        self.chkArmyReferral = QtGui.QCheckBox(self.scrollAreaWidgetContents)
        self.chkArmyReferral.setObjectName(_fromUtf8("chkArmyReferral"))
        self.gridLayout.addWidget(self.chkArmyReferral, 7, 0, 1, 2)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayoutEventNotes.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.lblEventNote.setBuddy(self.edtEventNote)
        self.lblClientPolicy.setBuddy(self.cmbClientPolicy)

        self.retranslateUi(EventNotesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(EventNotesPageWidget)
        EventNotesPageWidget.setTabOrder(self.scrollArea, self.cmbClientPolicy)
        EventNotesPageWidget.setTabOrder(self.cmbClientPolicy, self.chkLPUReferral)
        EventNotesPageWidget.setTabOrder(self.chkLPUReferral, self.chkArmyReferral)
        EventNotesPageWidget.setTabOrder(self.chkArmyReferral, self.edtEventNote)

    def retranslateUi(self, EventNotesPageWidget):
        EventNotesPageWidget.setWindowTitle(_translate("EventNotesPageWidget", "Form", None))
        self.lblEventCreateDateTime.setText(_translate("EventNotesPageWidget", "Дата и время создания", None))
        self.lblEventId.setText(_translate("EventNotesPageWidget", "Идентификатор записи", None))
        self.chkLPUReferral.setText(_translate("EventNotesPageWidget", "Прикрепить направление из ЛПУ", None))
        self.lblEventCreatePerson.setText(_translate("EventNotesPageWidget", "Автор", None))
        self.lblEventModifyPerson.setText(_translate("EventNotesPageWidget", "Автор последнего изменения", None))
        self.lblEventNote.setText(_translate("EventNotesPageWidget", "Примечания", None))
        self.lblEventModifyDateTime.setText(_translate("EventNotesPageWidget", "Дата и время последнего изменения", None))
        self.lblClientPolicy.setText(_translate("EventNotesPageWidget", "Полис пациента", None))
        self.chkArmyReferral.setText(_translate("EventNotesPageWidget", "Направление из военкомата", None))

from Events.ClientPolicyComboBox import CClientPolicyComboBox
