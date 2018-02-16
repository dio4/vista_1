# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui


class CBigIntSpinBox(QtGui.QAbstractSpinBox):
    u""" Счетчик для длинных чисел [- 2 ** 63 .. 2 ** 63 - 1] """

    def __init__(self, parent=None):
        super(CBigIntSpinBox, self).__init__(parent)
        self._minimum = -2L ** 63
        self._maximum = 2L ** 63 - 1
        self._singleStep = 1

        regExp = QtCore.QRegExp(r"[1-9]\d{0,20}")
        validator = QtGui.QRegExpValidator(regExp, self)

        self.lineEdit = QtGui.QLineEdit(self)
        self.lineEdit.setValidator(validator)
        self.setLineEdit(self.lineEdit)

    def value(self):
        return int(self.lineEdit.text())

    def setValue(self, value):
        if self._minimum <= value <= self._maximum:
            self.lineEdit.setText(str(value))

    def stepBy(self, steps):
        self.setValue(self.value() + steps*self.singleStep())

    def stepEnabled(self):
        return self.StepUpEnabled | self.StepDownEnabled

    def setSingleStep(self, singleStep):
        assert isinstance(singleStep, int)
        self._singleStep = abs(singleStep)

    def singleStep(self):
        return self._singleStep

    def minimum(self):
        return self._minimum

    def setMinimum(self, minimum):
        assert isinstance(minimum, int) or isinstance(minimum, long)
        self._minimum = minimum

    def maximum(self):
        return self._maximum

    def setMaximum(self, maximum):
        assert isinstance(maximum, int) or isinstance(maximum, long)
        self._maximum = maximum
