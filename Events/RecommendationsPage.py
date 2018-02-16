# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from Events.Recommendations import CRecommendationsModel
from library.DialogBase    import CConstructHelperMixin

from Ui_RecommendationsPage import Ui_RecommendationsPage


class CFastRecommendationsPage(QtGui.QWidget, CConstructHelperMixin, Ui_RecommendationsPage):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.eventEditor = None

    def setupUiMini(self, Dialog):
        pass

    def preSetupUiMini(self):
        pass

    def preSetupUi(self):
        pass

    def postSetupUiMini(self):
        self.addModels('Recommendations', CRecommendationsModel(self))
        self.tblRecommendations.setModel(self.modelRecommendations)
        self.tblRecommendations.addPopupDelRow()
        self.tblRecommendations.addAddToActions()

    def setEventEditor(self, eventEditor):
        self.eventEditor = eventEditor
        self.tblRecommendations.eventEditor = eventEditor

    def postSetupUi(self):
        pass

    def updatePersonId(self, personId):
        self.modelRecommendations.updatePersonId(personId)

    def updateContractId(self, contractId):
        self.modelRecommendations.updateContractId(contractId)

    def setData(self, clientId, personId, contractId):
        self.modelRecommendations.setClientId(clientId)
        self.updatePersonId(personId)
        self.updateContractId(contractId)

    def load(self, eventId):
        if eventId:
            self.modelRecommendations.loadItems(eventId)

    def save(self, eventId):
        self.modelRecommendations.saveItems(eventId)

class CRecommendationsPage(CFastRecommendationsPage):
    def __init__(self, parent=None):
        CFastRecommendationsPage.__init__(self, parent)
        self.preSetupUiMini()
        self.preSetupUi()
        self.setupUiMini(self)
        self.setupUi(self)
        self.postSetupUiMini()
        self.postSetupUi()


