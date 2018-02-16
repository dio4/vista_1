#!/usr/bin/env python
# -*- coding: utf-8 -*-
from library.InDocTable import *
from library.ICDCodeEdit import CICDCodeEdit, CICDCodeEditEx

from Utils import *
from Events.Utils import getMKBName

u"""Столбики для редактирования кодов МКБ"""


class CICDInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.cache = {}

    def createEditor(self, parent):
        editor = CICDCodeEdit(parent)
        return editor

    def getEditorData(self, editor):
        text = trim(editor.text())
        if text.endswith('.'):
            text = text[0:-1]
        if not text:
            return QVariant()
        return QVariant(text)

    def toStatusTip(self, val, record):
        code = forceString(val)
        if self.cache.has_key(code):
            descr = self.cache[code]
        else:
            descr = getMKBName(code) if code else ''
            self.cache[code] = descr
        return toVariant((code + ': ' + descr) if code else '')


class CICDExInDocTableCol(CICDInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CICDInDocTableCol.__init__(self, title, fieldName, width, **params)
        self.filter = None

    def createEditor(self, parent):
        editor = CICDCodeEditEx(parent)
        if self.filter:
            editor.setMKBFilter(self.filter)
        return editor

    def setFilter(self, filter):
        self.filter = filter
