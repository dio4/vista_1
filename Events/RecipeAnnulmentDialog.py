# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################

from Events.Ui_RecipeAnnulmentDialog import Ui_RecipeAnnulmentDialog
from library.DialogBase import CDialogBase
from library.Recipe.Utils import CRecipeStatusModel


class CRecipeAnnulmentDialog(CDialogBase, Ui_RecipeAnnulmentDialog):

    def __init__(self, parent, showDefaultStatus=True):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.addModels('RecipeStatus', CRecipeStatusModel(showDefaultStatus))
        self.cmbRecipeStatus.setModel(self.modelRecipeStatus)

    def getRecipeStatusCode(self):
        return self.modelRecipeStatus.getCode(self.cmbRecipeStatus.currentIndex())
