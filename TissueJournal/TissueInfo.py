# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from library.PrintInfo       import CInfo, CDateTimeInfo, CRBInfo
from library.Utils           import forceDateTime, forceInt, forceRef, forceString

from Orgs.PersonInfo         import CPersonInfo

from Registry.Utils          import CClientInfo


class CTissueTypeInfo(CRBInfo):
    tableName = 'rbTissueType'
    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)


class CTakenTissueJournalInfo(CInfo):
    def __init__(self, context, takenTissueJournalId):
        CInfo.__init__(self, context)
        self.id = takenTissueJournalId


    def _load(self):
        from Events.ActionInfo import CUnitInfo

        db = QtGui.qApp.db
        record = db.getRecord('TakenTissueJournal', '*', self.id) if self.id else None
        if record:
            self._client = self.getInstance(CClientInfo, forceRef(record.value('client_id')))
            self._tissueType = self.getInstance(CTissueTypeInfo, forceRef(record.value('tissueType_id')))
            self._externalId = forceString(record.value('externalId'))
            self._number = forceString(record.value('externalId'))
            self._amount = forceInt(record.value('amount'))
            self._unit = self.getInstance(CUnitInfo, forceRef(record.value('unit_id')))
            self._datetimeTaken = CDateTimeInfo(forceDateTime(record.value('datetimeTaken')))
            self._execPerson = self.getInstance(CPersonInfo, forceRef(record.value('execPerson_id')))
            self._note = forceString(record.value('note'))
            return True
        else:
            self._client = self.getInstance(CClientInfo, None)
            self._tissueType = self.getInstance(CTissueTypeInfo, None)
            self._externalId = ''
            self._number = ''
            self._amount = 0
            self._unit = self.getInstance(CUnitInfo, None)
            self._datetimeTaken = CDateTimeInfo()
            self._execPerson = self.getInstance(CPersonInfo, None)
            self._note = ''
            return False

    client        = property(lambda self: self.load()._client)
    tissueType    = property(lambda self: self.load()._tissueType)
    externalId    = property(lambda self: self.load()._externalId)
    number        = property(lambda self: self.load()._number)
    amount        = property(lambda self: self.load()._amount)
    unit          = property(lambda self: self.load()._unit)
    datetimeTaken = property(lambda self: self.load()._datetimeTaken)
    execPerson    = property(lambda self: self.load()._execPerson)
    note          = property(lambda self: self.load()._note)

