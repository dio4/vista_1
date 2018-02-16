# -*- coding: utf-8 -*-
from library.ComboBoxWithSpaceBtnHiding import CComboBoxWithSpaceBtnHiding
from library.Recipe.Utils import recipeStatusNames


class CGroupByExemptionRecipesComboBox(CComboBoxWithSpaceBtnHiding):
    def __init__(self, parent):
        CComboBoxWithSpaceBtnHiding.__init__(self, parent, [u'пациенту', u'врачу', u'дате рецепта', u'коду льготы'])


class CRecipeStatusComboBox(CComboBoxWithSpaceBtnHiding):
    def __init__(self, parent):
        CComboBoxWithSpaceBtnHiding.__init__(self, parent, recipeStatusNames)