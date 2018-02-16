# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Completer          import CStaticCompleterModel, CCompleter
from library.LineEdit import CLineEdit


class CPolicySerialEdit(CLineEdit):
    seriesList = None

    @staticmethod
    def getSeriesList():
        if CPolicySerialEdit.seriesList is None:
            db = QtGui.qApp.db
            result = []
            try:
                query = db.query('SELECT DISTINCT serial FROM Organisation_PolicySerial WHERE serial != \'\' ORDER BY serial')
                while query.next():
                    result.append(query.value(0))
            except:
                pass
            CPolicySerialEdit.seriesList = result
        return CPolicySerialEdit.seriesList


    def __init__(self, parent=None):
        super(CPolicySerialEdit, self).__init__(parent)
        self.__completerModel = CStaticCompleterModel(self, self.getSeriesList())
        self.__completer = CCompleter(self, self.__completerModel)
        self.setCompleter(self.__completer)
        self.connect(self.__completer, QtCore.SIGNAL('highlighted(QString)'), self.onCompleterHighlighted)


    def focusOutEvent(self, event):
        currentCompletion = self.__completer.currentCompletion()
        if QtCore.QString.compare(self.text(), currentCompletion, QtCore.Qt.CaseInsensitive) == 0:
                self.setText(currentCompletion)
#                self.setInsurerFilter(currentCompletion)
        super(CPolicySerialEdit, self).focusOutEvent(event)

#    def setInsurerFilter(self, text):
#        pass

    def onCompleterHighlighted(self, text):
        self.emit(QtCore.SIGNAL('textEdited(QString)'), text)
