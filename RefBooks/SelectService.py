# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from RefBooks.RBService import CRBServiceList, CServiceFilterDialog


def selectService(parent, cmd):
    serviceId = cmd.value()
    filterDialog = CServiceFilterDialog(parent)
    filterDialog.setProps({})
    if filterDialog.exec_():
        dialog = CRBServiceList(parent, True)
        dialog.props = filterDialog.props()
        dialog.renewListAndSetTo(serviceId)
        if dialog.model.rowCount() == 1:
            return dialog.currentItemId()
        else:
            if dialog.exec_():
                return dialog.currentItemId()
    return None