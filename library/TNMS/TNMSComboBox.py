# -*- coding: utf-8 -*-

from library.CustomComboBoxLike import CCustomComboBoxLike
from library.InDocTable import CInDocTableCol
from library.TNMS.TNMSPopup import CTNMSPopup
from library.TNMS.Utils import convertTNMSDictToDigest, convertTNMSDictToString, convertTNMSStringToDict
from library.Utils import forceString, toVariant


class CTNMSComboBox(CCustomComboBoxLike):
    def __init__(self, parent=None):
        CCustomComboBoxLike.__init__(self, parent)

    def setValue(self, tnmsString):
        CCustomComboBoxLike.setValue(self, convertTNMSStringToDict(unicode(tnmsString)))

    def valueAsString(self, value):
        return convertTNMSDictToDigest(value)

    def getValue(self):
        return convertTNMSDictToString(CCustomComboBoxLike.getValue(self))

    def createPopup(self):
        return CTNMSPopup(self)

    def setValueToPopup(self):
        self._popup.setValue(CCustomComboBoxLike.getValue(self))

    def updateValueFromPopup(self):
        CCustomComboBoxLike.setValue(self, self._popup.getValue())


class CTNMSCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)

    def toString(self, val, record):
        return toVariant(convertTNMSDictToDigest(convertTNMSStringToDict(forceString(val))))

    def createEditor(self, parent):
        editor = CTNMSComboBox(parent)
        return editor

    def setEditorData(self, editor, value, record):
        editor.setValue(forceString(value))

    def getEditorData(self, editor):
        return toVariant(editor.getValue())
