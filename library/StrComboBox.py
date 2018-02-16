# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.Utils import *


class CStrComboBox(QtGui.QComboBox):
    def __init__(self, parent):
        QtGui.QComboBox.__init__(self, parent)
        self.setDuplicatesEnabled(True)
        self._variants = []
        self._regexps  = []


    def setDomain(self, domain):
        self.clear()
        self._variants, self._regexps, err = self._parse(domain)
        for variant in self._variants:
            self.addItem(variant)
        self.setEditable(bool(self._regexps))
        self.setCurrentIndex(0)


    def _parse(self, domain):
        return CStrComboBox.parse(domain)

    def setValue(self, value):
        text = forceString(value)
        if self.isEditable():
            index = self.findText(text, Qt.MatchStartsWith)
            self.setCurrentIndex(index)
            self.setEditText(text)
        else:
            index = self.findText(text, Qt.MatchFixedString)
            self.setCurrentIndex(index)


    def text(self):
        return unicode(self.currentText())

    value = text


    def canMatch(self, text):
        for regexp in self._regexps:
            if re.match(regexp, text, re.I):
                return True
        return False


    def setEditText(self, text):
        t = forceString(text)
        if t in self._variants or self.canMatch(t):
            QtGui.QComboBox.setEditText(self, t)


    @staticmethod
    def parse(definition):
        def appendUnique(target, str):
            if str not in target:
                target.append(str)

        variants = []
        regexps  = []
        err = False
        state = 0

        for c in definition:
            if state == 0: # base state
                if c == '"' or c == "'":
                    q = c
                    state = 2
                    a = ''
                    target = variants # variant string
                elif c == '*':
                    appendUnique(regexps, '.*')
                    state = 3
                elif c == 'r':
                    state = 1
                elif c == ' ':
                    pass
                else:
                    err = True
                    break
            elif state == 1: # awaiting quote in regexp
                if c == '"' or c == "'":
                    q = c
                    state = 2
                    a = ''
                    target = regexps # regexp mode
                else:
                    err = True
                    break
            elif state == 2: # string input mode
                if c == '\\':
                    state = 3
                elif c == q:
                    appendUnique(target, a)
                    state = 4
                else:
                    a += c
            elif state == 3: # back slashed char
                a += c
                state = 2
            elif state == 4: # string finished, awaiting comma or EOS
                if c == ',':
                    state = 0
                elif c == ' ':
                    pass
                else:
                    err = True
                    break
            else:
                err = True
                break

        if state != 0 and state != 4:
            err = True
        return variants, regexps, err



class CDoubleComboBox(CStrComboBox):
    def __init__(self, parent):
        CStrComboBox.__init__(self, parent)

    def _parse(self, domain):
        return CDoubleComboBox.parse(domain)

    def value(self):
        return self.currentText()

    def setDomain(self, domain):
        CStrComboBox.setDomain(self, domain)
        if self.isEditable():
            validator = QtGui.QDoubleValidator(self)
            self.lineEdit().setValidator(validator)


    @staticmethod
    def parse(definition):
        variants = []
        regexps  = []
        err = False
        state = None
        dote = False

        for c in definition:
            if state is None and c == '{':
               continue 
            if state is None:
                state = 1 # working state
                a = ''
            elif state:
                if c == '{':
                    state = 0 # not working state
                    err = True
                elif c == '}':
                    state = 2 # end state
                    
                
            if state == 1:
                if c == ' ':
                    pass
                elif c == ';':
                    if a:
                        variants.append(a)
                    a = ''
                    dote = False
                elif c.isdigit() or c in ['.', '-']:
                    if c == '.':
                        if dote:
                            state = 0
                            err = True
                        dote = True
                    a += c
                elif c == '*':
                    regexps.append('.*')
                else:
                    state = 0
                    err = True
                    
            elif state == 2:
                if a and a.replace('-', '').isdigit():
                    variants.append(a)
                    state = 0
                
        if not err and state == 1:
            if a and a.replace('-', '').isdigit():
                variants.append(a)
                
        return variants, regexps, err


class CIntComboBox(CStrComboBox):
    def __init__(self, parent):
        CStrComboBox.__init__(self, parent)

    def _parse(self, domain):
        return CIntComboBox.parse(domain)

    def value(self):
        return self.currentText()
        
    def setDomain(self, domain):
        CStrComboBox.setDomain(self, domain)
        if self.isEditable():
            validator = QtGui.QIntValidator(self)
            self.lineEdit().setValidator(validator)

    @staticmethod
    def parse(definition):
        variants = []
        regexps  = []
        err = False
        state = None
        dote = False

        for c in definition:
            if state is None and c == '{':
               continue 
            if state is None:
                state = 1 # working state
                a = ''
            elif state:
                if c == '{':
                    state = 0 # not working state
                    err = True
                elif c == '}':
                    state = 2 # end state
                    
            if state == 3:
                if c == ';':
                    state = 1
                
            if state == 1:
                if c == ' ':
                    pass
                    
                elif c == ';':
                    if a:
                        variants.append(a)
                    a = ''
                    dote = False
                    
                elif c.isdigit() or c == '-':
                    a += c
                    
                elif c == '*':
                    regexps.append('.*')
                    
                elif c == '.':
                    if dote:
                        state = 0
                        err = True
                    else:
                        state = 3 # wait `;` char 
                        variants.append(a)
                        a = ''
                        dote = True
                    
                else:
                    state = 0
                    err = True
                    
            elif state == 2:
                if a and a.replace('-', '').isdigit():
                    variants.append(a)
                    state = 0
        if not err and state == 1:
            if a and a.replace('-', '').isdigit():
                variants.append(a)
                
        return variants, regexps, err

