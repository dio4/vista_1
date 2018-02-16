# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore

from library.DialogBase import CDialogBase
from library.TableModel import CTableModel, CDateTimeCol

from Ui_PrevActionChooserDialog import Ui_PrevActionChooserDialog


class CPrevActionChooser(CDialogBase, Ui_PrevActionChooserDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)

        self.setupUi(self)
        self.addModels('PrevActions', CTableModel(self, [CDateTimeCol(u'Дата', ['begDate'], 50)], 'Action'))
        #self.addModels('PrevActions', CPrevActionsModel)

        self.setModels(self.tblPrevActions, self.modelPrevActions, self.selectionModelPrevActions)
        self.setWindowTitle(u'Выберите исходную услугу')
        self.connect(self.tblPrevActions, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.accept)
