# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PaginationBar.ui'
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

class Ui_PagnationBar(object):
    def setupUi(self, PagnationBar):
        PagnationBar.setObjectName(_fromUtf8("PagnationBar"))
        PagnationBar.resize(986, 28)
        self.horizontalLayout = QtGui.QHBoxLayout(PagnationBar)
        self.horizontalLayout.setMargin(2)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(PagnationBar)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.edtPageSize = QtGui.QSpinBox(PagnationBar)
        self.edtPageSize.setFrame(True)
        self.edtPageSize.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.edtPageSize.setMinimum(5)
        self.edtPageSize.setMaximum(1000)
        self.edtPageSize.setSingleStep(5)
        self.edtPageSize.setProperty("value", 100)
        self.edtPageSize.setObjectName(_fromUtf8("edtPageSize"))
        self.horizontalLayout.addWidget(self.edtPageSize)
        self.lablel_2 = QtGui.QLabel(PagnationBar)
        self.lablel_2.setObjectName(_fromUtf8("lablel_2"))
        self.horizontalLayout.addWidget(self.lablel_2)
        self.line = QtGui.QFrame(PagnationBar)
        self.line.setMinimumSize(QtCore.QSize(20, 0))
        self.line.setLineWidth(1)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.btnFirst = QtGui.QToolButton(PagnationBar)
        self.btnFirst.setMinimumSize(QtCore.QSize(0, 24))
        self.btnFirst.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.btnFirst.setObjectName(_fromUtf8("btnFirst"))
        self.horizontalLayout.addWidget(self.btnFirst)
        self.btnPrev = QtGui.QToolButton(PagnationBar)
        self.btnPrev.setMinimumSize(QtCore.QSize(40, 24))
        self.btnPrev.setObjectName(_fromUtf8("btnPrev"))
        self.horizontalLayout.addWidget(self.btnPrev)
        self.lblPage = QtGui.QLabel(PagnationBar)
        self.lblPage.setObjectName(_fromUtf8("lblPage"))
        self.horizontalLayout.addWidget(self.lblPage)
        self.edtCurrent = QtGui.QLineEdit(PagnationBar)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtCurrent.sizePolicy().hasHeightForWidth())
        self.edtCurrent.setSizePolicy(sizePolicy)
        self.edtCurrent.setMaximumSize(QtCore.QSize(100, 16777215))
        self.edtCurrent.setMaxLength(5)
        self.edtCurrent.setFrame(True)
        self.edtCurrent.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.edtCurrent.setReadOnly(True)
        self.edtCurrent.setObjectName(_fromUtf8("edtCurrent"))
        self.horizontalLayout.addWidget(self.edtCurrent)
        self.lblSpliiter = QtGui.QLabel(PagnationBar)
        self.lblSpliiter.setAlignment(QtCore.Qt.AlignCenter)
        self.lblSpliiter.setObjectName(_fromUtf8("lblSpliiter"))
        self.horizontalLayout.addWidget(self.lblSpliiter)
        self.edtCount = QtGui.QLineEdit(PagnationBar)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edtCount.sizePolicy().hasHeightForWidth())
        self.edtCount.setSizePolicy(sizePolicy)
        self.edtCount.setMaximumSize(QtCore.QSize(100, 16777215))
        self.edtCount.setSizeIncrement(QtCore.QSize(0, 0))
        self.edtCount.setMaxLength(5)
        self.edtCount.setFrame(True)
        self.edtCount.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.edtCount.setReadOnly(True)
        self.edtCount.setObjectName(_fromUtf8("edtCount"))
        self.horizontalLayout.addWidget(self.edtCount)
        self.btnNext = QtGui.QToolButton(PagnationBar)
        self.btnNext.setMinimumSize(QtCore.QSize(40, 24))
        self.btnNext.setObjectName(_fromUtf8("btnNext"))
        self.horizontalLayout.addWidget(self.btnNext)
        self.btnLast = QtGui.QToolButton(PagnationBar)
        self.btnLast.setMinimumSize(QtCore.QSize(0, 24))
        self.btnLast.setObjectName(_fromUtf8("btnLast"))
        self.horizontalLayout.addWidget(self.btnLast)
        self.line_2 = QtGui.QFrame(PagnationBar)
        self.line_2.setMinimumSize(QtCore.QSize(20, 0))
        self.line_2.setLineWidth(1)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.horizontalLayout.addWidget(self.line_2)
        self.lblItemsCount = QtGui.QLabel(PagnationBar)
        self.lblItemsCount.setObjectName(_fromUtf8("lblItemsCount"))
        self.horizontalLayout.addWidget(self.lblItemsCount)
        spacerItem = QtGui.QSpacerItem(100, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.retranslateUi(PagnationBar)
        QtCore.QMetaObject.connectSlotsByName(PagnationBar)
        PagnationBar.setTabOrder(self.edtPageSize, self.btnFirst)
        PagnationBar.setTabOrder(self.btnFirst, self.btnPrev)
        PagnationBar.setTabOrder(self.btnPrev, self.edtCurrent)
        PagnationBar.setTabOrder(self.edtCurrent, self.edtCount)
        PagnationBar.setTabOrder(self.edtCount, self.btnNext)
        PagnationBar.setTabOrder(self.btnNext, self.btnLast)

    def retranslateUi(self, PagnationBar):
        PagnationBar.setWindowTitle(_translate("PagnationBar", "Form", None))
        self.label.setText(_translate("PagnationBar", "Отображать по", None))
        self.lablel_2.setText(_translate("PagnationBar", "на странице", None))
        self.btnFirst.setToolTip(_translate("PagnationBar", "Первая страница", None))
        self.btnFirst.setText(_translate("PagnationBar", "<<<", None))
        self.btnPrev.setToolTip(_translate("PagnationBar", "Предыдущая страница", None))
        self.btnPrev.setText(_translate("PagnationBar", "<", None))
        self.lblPage.setText(_translate("PagnationBar", "страница", None))
        self.edtCurrent.setText(_translate("PagnationBar", "1", None))
        self.lblSpliiter.setText(_translate("PagnationBar", "/", None))
        self.edtCount.setText(_translate("PagnationBar", "1", None))
        self.btnNext.setToolTip(_translate("PagnationBar", "Следующая страница", None))
        self.btnNext.setText(_translate("PagnationBar", ">", None))
        self.btnLast.setToolTip(_translate("PagnationBar", "Последняя страница", None))
        self.btnLast.setText(_translate("PagnationBar", ">>>", None))
        self.lblItemsCount.setText(_translate("PagnationBar", "записей в таблице: 0", None))
