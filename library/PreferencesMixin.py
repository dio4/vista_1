# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006,2008 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.Utils import *

dont_load_pref = [
    #'PreCreateEventDialog',     # Новое обращение
]

class CPreferencesMixin:
    def loadPreferences(self, preferences):
        pass

    def savePreferences(self):
        return {}


class CContainerPreferencesMixin(CPreferencesMixin):
    def loadPreferences(self, preferences):
        recursiveLoadPreferences(self, preferences)

    def savePreferences(self):
        return savePreferences(self)


class CDialogPreferencesMixin(CContainerPreferencesMixin):
    def loadPreferences(self, preferences):
        geometry = getPref(preferences, 'geometry', None)
        if type(geometry) == QVariant and geometry.type() == QVariant.ByteArray and not geometry.isNull():
            self.restoreGeometry(geometry.toByteArray())
            CContainerPreferencesMixin.loadPreferences(self, preferences)


    def savePreferences(self):
        result = CContainerPreferencesMixin.savePreferences(self)
        setPref(result,'geometry',QVariant(self.saveGeometry()))
        return result


    def loadDialogPreferences(self):
        #if self.objectName() in dont_load_pref:
        #    return
        preferences = getPref(QtGui.qApp.preferences.windowPrefs, self.objectName(), {})
        self.loadPreferences(preferences)


    def saveDialogPreferences(self):
        #if self.objectName() in dont_load_pref:
        #    return
        preferences = self.savePreferences()
        setPref(QtGui.qApp.preferences.windowPrefs, self.objectName(), preferences)


def recursiveLoadPreferences(obj, preferences):
    deleteLater = []
    for childName, childPreferences in preferences.iteritems():
        children = filter(lambda x: QtCore.QObject.parent(x) is obj, obj.findChildren(QtGui.QWidget, QtCore.QRegExp(childName, QtCore.Qt.CaseInsensitive)))
        if len(children) > 0:
            if isinstance(childPreferences, dict):
                child = children[0]
                if isinstance(child, CPreferencesMixin):
                    child.loadPreferences(childPreferences)
                if isinstance(child, QtGui.QSplitter):
                    geometry = childPreferences.get('geometry', None)
                    if isinstance(geometry, QtCore.QVariant) and geometry.type() == QtCore.QVariant.ByteArray:
                        if not geometry.isNull():
                            child.restoreState(geometry.toByteArray())
                recursiveLoadPreferences(child, childPreferences)
        # else:
        #     deleteLater.append(childName)
    for name in deleteLater:
        del preferences[name]


def savePreferences(obj):
    preferences = {}
    for child in filter(lambda x: isinstance(x, (QtGui.QSplitter, CPreferencesMixin)), obj.findChildren(QtGui.QWidget)):
        childPreferences = {}
        if isinstance(child, CPreferencesMixin):
            childPreferences = child.savePreferences()
        if isinstance(child, QtGui.QSplitter):
            childPreferences['geometry'] = QVariant(child.saveState())

        if childPreferences:
            name = [unicode(child.objectName())]
            parent = QtCore.QObject.parent(child)
            while parent and parent is not obj:
                name.append(unicode(parent.objectName()))
                parent = QtCore.QObject.parent(parent)
            if name:
                name = list(reversed(name))
                tmpPrefs = preferences
                while len(name) > 1:
                    tmpPrefs = tmpPrefs.setdefault(name.pop(0), {})
                tmpPrefs[name[0]] = childPreferences
    return preferences

