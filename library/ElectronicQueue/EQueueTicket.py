# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtSql
from library.PrintInfo import CInfo
from library.Utils import generalConnectionName

__author__ = 'atronah'

'''
    author: atronah
    date:   20.11.2014
'''


class CEQTicketInfo(CInfo):
    def __init__(self, context, itemId):
        super(CEQTicketInfo, self).__init__(context)
        self.id = itemId


    def _load(self):
        db = QtSql.QSqlDatabase.database(generalConnectionName())
        if db and db.isOpen() and self.id:
            query = QtSql.QSqlQuery(''' SELECT
                                        FROM vEQueueTicket
                                        WHERE id = %d
                                    ''' % self.id,
                                    db)
            if query.first():
                self._initByRecord(query.record())
                return True
        self._initByNull()
        return False


    def _initByRecord(self, record):
        self._idx = record.value('idx').toInt()[0]
        self._value = unicode(record.value('value').toString())
        self._status = record.value('status').toInt()[0]
        self._office = unicode(record.value('office').toString())
        # self._orgStructure = self.getInstance() # не хочу использовать COrgStructureInfo, так как оно завязано на QtGui.qApp.db

    def _initByNull(self):
        self._idx = 0
        self._value = u'---'
        self._status = 0
        self._office = u'---'


    def __str__(self):
        self.load()
        if self._ok:
            return self._value
        else:
            return ''


    idx          = property(lambda self: self.load()._idx,
                            doc = u"""
                                  Порядковый номер
                                  :rtype : int
                                  """)
    status       = property(lambda self: self.load()._status,
                            doc = u"""
                                  Статус номерка.
                                        0 - Зарезервирован
                                        1 - Выдан
                                        2 - Готов к вызову
                                        3 - Готов к вызову вне очереди
                                        4 - Выполняется
                                        5 - Завершен
                                        6 - Отменен
                                  :rtype : int
                                  """)
    value        = property(lambda self: self.load()._value,
                            doc = u"""
                                  Номер талона.
                                  :rtype : unicode
                                  """)
    office       = property(lambda self: self.load()._office,
                            doc = u"""
                                  Кабинет вызова.
                                  :rtype : unicode
                                  """)


def main():
    import sys

    sys.exit(0)


if __name__ == '__main__':
    main()