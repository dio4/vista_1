# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

"""
Created on 20.02.2013

@author: atronah
"""

from PyQt4 import QtGui

from library.Utils      import forceStringEx
from Reports.ReportBase import CReportBase

from Reports.ReportsGenerator.ReportsGeneratorEngine        import CReportsGeneratorEngine
from Reports.ReportsGenerator.ReportsGeneratorSetupDialog   import CReportsGeneratorSetupDialog


class CReportByTemplate(CReportBase):
    def __init__(self, parent):
        CReportBase.__init__(self, parent)
        self.setTitle(u'Отчет по шаблону')
        self._reportEngine = CReportsGeneratorEngine()
        self._reportEngine.setQueryExecuter(QtGui.qApp.db.query)
    
    
    def getDefaultParams(self):
        return {}
    
    
    def getSetupDialog(self, parent):
        setupDialog = CReportsGeneratorSetupDialog(parent)
        setupDialog.setReportEngine(self._reportEngine)
        return setupDialog
        

    def build(self, params):
        self.setQueryText(forceStringEx(self._reportEngine.executeStmt()))
        return self._reportEngine.buildDocument(params, False)
        


def main():
    import sys
    from PyQt4 import QtCore
    app = QtGui.QApplication(sys.argv)
    
    tw = QtGui.QTableWidget()
    tw.setColumnCount(5)
    tw.setRowCount(1)
    for column in xrange(tw.columnCount()):
        item = QtGui.QTableWidgetItem(u'Столбец %d' % column)
        item.setCheckState(QtCore.Qt.Unchecked)
#        item.setText(QtCore.QString.number(item.flags(), 2))
        tw.setItem(0, column, item)
    tw.show()
    app.exec_()
    print tw.item(0,0).checkState()
    return 0
     
if __name__ == '__main__':
    main()