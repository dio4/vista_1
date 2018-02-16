# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from Events.EventJobTicketsEditorTable import CEventJobTicketsModel
from Ui_EventJobTicketsEditorDialog import Ui_EventJobTicketsEditor
from library.DialogBase import CDialogBase


class CEventJobTicketsEditor(CDialogBase, Ui_EventJobTicketsEditor):
    def __init__(self, parent=None, emptyActionModelsItemList=None, fullActionModelsItemList=None, clientId=None):
        if not emptyActionModelsItemList:
            emptyActionModelsItemList = []
        if not fullActionModelsItemList:
            fullActionModelsItemList = []
        CDialogBase.__init__(self, parent)
        self.setupUi(self)

        self.addModels('SetEventJobTickets', CEventJobTicketsModel(self, emptyActionModelsItemList, clientId))
        self.addModels('ChangeEventJobTickets', CEventJobTicketsModel(self, fullActionModelsItemList, clientId))

        self.setModels(self.tblSetEventJobTickets, self.modelSetEventJobTickets, self.selectionModelSetEventJobTickets)
        self.setModels(self.tblChangeEventJobTickets, self.modelChangeEventJobTickets, self.selectionModelChangeEventJobTickets)

        self.tblSetEventJobTickets.expandAll()
        self.tblChangeEventJobTickets.expandAll()

        self.setWindowTitle(u'Назначение работ')

    def exec_(self):
        result = CDialogBase.exec_(self)
        if result:
            self.modelSetEventJobTickets.setCheckedValues()
            self.modelChangeEventJobTickets.changeCheckedValues()
            self.modelSetEventJobTickets.saveLIDs()
            self.modelChangeEventJobTickets.saveLIDs()
        return result
