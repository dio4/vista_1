# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils import forceStringEx


class CMaxGroupValueSpinBox(QtGui.QSpinBox):
    def __init__(self, parent=None):
        QtGui.QSpinBox.__init__(self, parent)
        self._parent = parent
        self.setValue(100)
        
    def keyPressEvent(self, event):
        QtGui.QSpinBox.keyPressEvent(self, event)
        
        
class CControlButton(QtGui.QToolButton):
    def __init__(self, parent=None):
        QtGui.QToolButton.__init__(self, parent)
        self._calculator = parent.parent()
        self._actAddButon = QtGui.QAction(u'Назначить', self)
        self._menu = QtGui.QMenu(self)
        self._menu.addAction(self._actAddButon)
        self.connect(self._actAddButon, QtCore.SIGNAL('triggered()'), self.on_actAddButon)
        
        
        
    def contextMenuEvent(self, event):
        if not self.isEnabled():
            self._menu.setEnabled(True)
            self._menu.exec_(event.globalPos())
            event.accept()
        else:
            event.ignore()
           
    # когда виджет задизаблен он не реагирует на mouseEvent-ы. А мне нужно контекстное меню.
    # у меня contextMenuPolicy = Qt.DefaultContextMenu, так что я сразу в нужный момент перекидываю event
    # в contextMenuEvent
    def event(self, event):
        if event.type() == QtCore.QEvent.ContextMenu:
            self.contextMenuEvent(event)
            return True
        else:
            return QtGui.QToolButton.event(self, event)
            
    def on_actAddButon(self):
        asker = CButtonAskerWidget(self, self._calculator.availableGroupList())
        if asker.exec_():
            group = asker.group()
            name = asker.name()
            self._calculator.addButton(self, group, name)
        
    
        
class CButtonAskerWidget(QtGui.QDialog):
    def __init__(self, parent, groupList):
        QtGui.QDialog.__init__(self, parent)
        self.vLayout = QtGui.QVBoxLayout()
        self.lblName = QtGui.QLabel(u'Наименование', self)
        self.vLayout.addWidget(self.lblName)
        self.edtName = QtGui.QLineEdit(self)
        self.vLayout.addWidget(self.edtName)
        self.lblGroup = QtGui.QLabel(u'Группа', self)
        self.vLayout.addWidget(self.lblGroup)
        self.cmbGroup = QtGui.QComboBox(self)
        self.cmbGroup.addItems(groupList)
        self.vLayout.addWidget(self.cmbGroup)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)
        self.vLayout.addWidget(self.buttonBox)
        self.setLayout(self.vLayout)
        
        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL('rejected()'), self.reject)
        
    def name(self):
        return forceStringEx(self.edtName.text())
        
    def group(self):
#        return int(unicode(self.cmbGroup.currentText()), 16)
        return unicode(self.cmbGroup.currentText())
        
        
        
