# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################

"""
    author: Mahoney
    date:   26.02.2015
"""

from PyQt4 import QtCore, QtGui
from library.InDocTable import CInDocTableView

class CDestinationsTableView(CInDocTableView):
    """Special selection treatment: always select entire complex"""

    def getSpanForRow(self, row, spansList):
        for span in spansList:
            if row >= span[0] and row < span[0] + span[2]:
                return span
        return None

    def selectionCommand(self, index, event):
        if event:
            if event.type() in [QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonRelease]:
                if event.buttons() & QtCore.Qt.LeftButton:
                    if not index.isValid():
                        return QtGui.QItemSelectionModel.Clear

                    self.clearSelection()

                    spansList = self.model().getComplexSpan()
                    span = self.getSpanForRow(index.row(), spansList)
                    if span is not None:
                        for r in range(span[0], span[0] + span[2]):
                            if r != index.row():
                                self.selectRow(r)
                        return QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows
                    else:
                        return QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows
            elif event.type() in [QtCore.QEvent.MouseMove, QtCore.QEvent.KeyPress]:
                return QtGui.QItemSelectionModel.Current

        return super(CDestinationsTableView, self).selectionCommand(index, event)
