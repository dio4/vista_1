# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.Utils       import forceRef, forceString, toVariant
from library.TableModel  import CCol
from library.crbcombobox import CRBComboBox, CRBModelDataCache


class CActionTypeCol(CCol):
#    """
#      ActionType column for list of Actions
#    """
    def __init__(self, title, defaultWidth, showFields=CRBComboBox.showName, alignment='l'):
        CCol.__init__(self, title, ('actionType_id', 'specifiedName'), defaultWidth, alignment)
        self.data = CRBModelDataCache.getData('ActionType', True, '')
        self.showFields = showFields


    def format(self, values):
        id = forceRef(values[0])
        specifiedName = forceString(values[1])
        if id:
            return toVariant(self.data.getStringById(id, self.showFields)+(' '+specifiedName if specifiedName else ''))
        else:
            return CCol.invalid
