# -*- coding: utf-8 -*-
from PyQt4.QtCore.QVariant import QVariant

from config import db
from createUpdateHospCase import createUpdateHospCase
from library.Utils import forceRef

PREPARED_EVENTS_STMT = u'''
SELECT id, exposeConfirmed FROM Event WHERE exposeConfirmed = 1;
'''

def sendHospCases():
    eventList = db.getRecordList(stmt=PREPARED_EVENTS_STMT)
    for event in eventList:
        createUpdateHospCase(forceRef(event.value('id')))
        event.setValue('exposeConfirmed', QVariant(3))

def dailyUpdate():
        sendHospCases()

if __name__ == '__main__':
    dailyUpdate()