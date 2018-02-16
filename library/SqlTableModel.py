# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

__author__ = 'atronah'

'''
    author: atronah
    date:   26.11.2014
'''


from PyQt4 import QtSql
from PyQt4 import QtCore

class CSqlTableModel(QtSql.QSqlTableModel):
    def __init__(self, parent = None, db = QtSql.QSqlDatabase()):
        super(CSqlTableModel, self).__init__(parent, db)
        self._sortRuleList = []


    def setSort(self, columnList, defaultOrder = QtCore.Qt.AscendingOrder):
        """
        Задает правила сортировки (секция ORDER BY) для формируемого запроса на выборку.

        :param columnList: список правил сортировки вида (поле, направление_сортировки).
                Может быть номером столбца (для совместимости с QSqlTableModel.setSort)
        :param defaultOrder: направление сортировки по умолчанию.

        """
        if isinstance(columnList, int):
            columnList = [(columnList, defaultOrder)]

        if isinstance(columnList, list):
            self._sortRuleList = []
            for sortRule in columnList:
                column, order = sortRule if isinstance(sortRule, tuple) else (sortRule, defaultOrder)
                field = self.record().field(column)
                if field.isValid():
                    fieldDescription = u'%s.%s %s' % (self.tableName(),
                                                      self.database().driver().escapeIdentifier(field.name(),
                                                                                                QtSql.QSqlDriver.FieldName),
                                                      u'DESC' if order == QtCore.Qt.DescendingOrder else u'ASC')
                    self._sortRuleList.append(fieldDescription)




    def orderByClause(self):
        return QtCore.QString(u'ORDER BY %s' % u', '.join(self._sortRuleList)) if self._sortRuleList else QtCore.QString()



def main():
    import sys

    sys.exit(0)


if __name__ == '__main__':
    main()