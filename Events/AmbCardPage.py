# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Registry.AmbCardMixin import CAmbCardMixin
from Registry.Utils import getClientBanner
from Ui_AmbCardPage import Ui_AmbCardPage
from library.DialogBase import CDialogBase
from library.TextBrowser import CTextBrowser


class CFastAmbCardPage(QtGui.QWidget, CAmbCardMixin, Ui_AmbCardPage):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._clientId = None

    def setupUiMini(self, Dialog):
        pass

    def setClientId(self, clientId):
        self._clientId = clientId
        if hasattr(self, 'tabRadiationDose'):
            if QtGui.qApp.isPNDDiagnosisMode():
                self.tabAmbCardContent.removeTab(self.tabAmbCardContent.indexOf(self.tabRadiationDose))
            else:
                self.tabRadiationDose.setClientId(clientId)

    def currentClientId(self):
        return self._clientId

    def resetWidgets(self):
        self.on_cmdAmbCardDiagnosticsButtonBox_reset()
        self.on_cmdAmbCardStatusButtonBox_reset()
        self.on_cmdAmbCardDiagnosticButtonBox_reset()
        self.on_cmdAmbCardCureButtonBox_reset()
        self.on_cmdAmbCardMiscButtonBox_reset()
        self.on_cmdAmbCardAnalysesButtonBox_reset()

        self.on_cmdAmbCardDiagnosticsButtonBox_apply()
        self.on_cmdAmbCardStatusButtonBox_apply()
        self.on_cmdAmbCardDiagnosticButtonBox_apply()
        self.on_cmdAmbCardCureButtonBox_apply()
        self.on_cmdAmbCardMiscButtonBox_apply()
        self.on_cmdAmbCardAnalysesButtonBox_apply()


class CAmbCardPage(CFastAmbCardPage):
    def __init__(self, parent=None):
        CFastAmbCardPage.__init__(self, parent)
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()


class CAmbCardDialog(CDialogBase):
    def __init__(self, parent=None, clientId=None):
        CDialogBase.__init__(self, parent)
        self.setObjectName('AmbCardDialog')

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        self.vLayout = QtGui.QVBoxLayout(self)

        self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical, self)
        self.splitter.setChildrenCollapsible(False)

        self.ambCardPageWidget = CAmbCardPage(self)
        self.clientInfoBanner = CTextBrowser(self)

        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, self)

        self.splitter.addWidget(self.clientInfoBanner)
        self.splitter.addWidget(self.ambCardPageWidget)

        self.vLayout.addWidget(self.splitter)
        self.vLayout.addWidget(self.buttonBox)

        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.accept)

        self.setClientId(clientId)
        self.ambCardPageWidget.resetWidgets()

    def setClientId(self, clientId):
        self._clientId = clientId
        if clientId:
            self.clientInfoBanner.setHtml(getClientBanner(clientId))
        else:
            self.clientInfoBanner.setText('')

        self.ambCardPageWidget.setClientId(clientId)
