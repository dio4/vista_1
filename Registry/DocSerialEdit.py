# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

romanSymb = ['M', 'D', 'C', 'L', 'X', 'V', 'I'];
rus = u'йцукенгшщзхъфывапролджэячсмитьбюё'
eng = u'qwertyuiop[]asdfghjkl;\'zxcvbnm,.`'
r2e = {}
e2r = {}
for i in range(len(rus)):
    r2e[ rus[i] ] = eng[i]
    e2r[ eng[i] ] = rus[i]

def checkIfRoman(char):
    chr_ = unicode(char).lower()
    engChr = ''
    if r2e.has_key(chr_):
        engChr = r2e[chr_].upper()
    elif e2r.has_key(chr_):
        engChr = chr_.upper()
    if e2r.has_key(engChr.lower()):
        if engChr in romanSymb:
            return engChr
    return ''

def checkIfRu(char):
    chr_ = unicode(char).lower()
    rusChr = ''
    if e2r.has_key(chr_):
        rusChr = e2r[chr_].upper()
    elif r2e.has_key(chr_):
        rusChr = chr_.upper()
    if r2e.has_key(rusChr.lower()):
        return rusChr
    return ''

class CDocSerialEdit(QtGui.QLineEdit):
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.format = 0

    def setFormat(self, format):
        self.format = format
        text = unicode(self.text())
        text = ''.join(self.filterChar(char) for char in text)
        self.setText(text)
        
    
    def filterChar(self, char):
        assert False, 'pure virtual call'
        

    def keyPressEvent(self, event):
        if self.format                                          \
           and QtCore.Qt.Key_Space <= event.key() < QtCore.Qt.Key_Escape      \
           and len(unicode(event.text())) == 1:
            chars = self.filterChar(unicode(event.text()))
            if chars:
                for char in chars:
                    myEvent = QtGui.QKeyEvent(event.type(), ord(char), event.modifiers(), char, False, 1)
                    QtGui.QLineEdit.keyPressEvent(self, myEvent)
            event.accept()
        else:
            QtGui.QLineEdit.keyPressEvent(self, event)


class CDocSerialLeftEdit(CDocSerialEdit):
    anyToRoman = { '1': 'I',  'i': 'I',  'I': 'I', u'ш': 'I', u'Ш': 'I',
                   '2': 'II',
                   '3': 'III',
                   '4': 'IV',
                   '5': 'V',  'v': 'V',  'V': 'V', u'м': 'V', u'М': 'V',
                   '6': 'VI',
                   '7': 'VII',
                   '8': 'VIII',
                   '9': 'IX',
                   '0': 'X',  'x': 'X',  'X': 'X', u'ч': 'X', u'Ч': 'X',
                              'l': 'L',  'L': 'L', u'д': 'L', u'Д': 'L',
                              'c': 'C',  'C': 'C', u'с': 'C', u'С': 'C',
                              'd': 'D',  'D': 'D', u'в': 'D', u'В': 'D',
                              'm': 'M',  'M': 'M', u'ь': 'M', u'Ь': 'M'
                 }

    def __init__(self, parent=None):
        CDocSerialEdit.__init__(self, parent)
        self.onlyRoman = False
    #
    # def keyPressEvent(self, event):
    #     if self.onlyRoman:
    #         chr = unicode(event.text()).lower()
    #         engChr = ''
    #         if r2e.has_key(chr):
    #             engChr = r2e[chr].upper()
    #             myEvent = QtGui.QKeyEvent(event.type(), ord(engChr), event.modifiers(), engChr, event.isAutoRepeat(), event.count())
    #         elif e2r.has_key(chr):
    #             engChr = chr.upper()
    #             myEvent = QtGui.QKeyEvent(event.type(), ord(engChr), event.modifiers(), engChr, event.isAutoRepeat(), event.count())
    #         if e2r.has_key(engChr.lower()):
    #             if engChr in self.romanSymb:
    #                 QtGui.QLineEdit.keyPressEvent(self, myEvent)
    #         else:
    #             QtGui.QLineEdit.keyPressEvent(self, event)
    #     else:
    #         QtGui.QLineEdit.keyPressEvent(self, event)


    def filterChar(self, char):
        if self.format == 1:
            if char.isalpha() or 0x20 <= ord(char) <= 0xFF:
                return self.anyToRoman.get(char, '')
            else:
                return char
        if self.format == 2:
            if char.isdigit():
                return char
            else:
                return ''
        if self.format == 'onlyRomans':
            return checkIfRoman(char)
        if self.format == 'onlyRu':
            return checkIfRu(char)
        return char


class CDocSerialRightEdit(CDocSerialEdit):
    def __init__(self, parent=None):
        CDocSerialEdit.__init__(self, parent)
        self.onlyRu = False

    # def keyPressEvent(self, event):
    #     if self.onlyRu:
    #         chr = unicode(event.text()).lower()
    #         rusChr = ''
    #         if e2r.has_key(chr):
    #             rusChr = e2r[chr].upper()
    #             myEvent = QtGui.QKeyEvent(event.type(), ord(rusChr), event.modifiers(), rusChr, event.isAutoRepeat(), event.count())
    #         elif r2e.has_key(chr):
    #             rusChr = chr.upper()
    #             myEvent = QtGui.QKeyEvent(event.type(), ord(rusChr), event.modifiers(), rusChr, event.isAutoRepeat(), event.count())
    #         if r2e.has_key(rusChr.lower()):
    #             QtGui.QLineEdit.keyPressEvent(self, myEvent)
    #         else:
    #             QtGui.QLineEdit.keyPressEvent(self, event)
    #     else:
    #         QtGui.QLineEdit.keyPressEvent(self, event)

    def filterChar(self, char):
        if self.format == 1:
            if char.isalpha():
                return char.upper()
            else:
                return ''
        if self.format == 2:
            if char.isdigit():
                return char
            else:
                return ''
        if self.format == 'onlyRu':
            return checkIfRu(char)
        return char