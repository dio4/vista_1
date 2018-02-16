# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


from PyQt4 import QtGui

from Events.EventInfo   import CEventInfo

from library.PrintInfo  import CDateInfo, CRBInfo
from library.Utils      import forceBool, forceDate, forceInt, forceRef, forceString

from Orgs.Utils         import COrgStructureInfo


class CHospitalBedInfo(CRBInfo):
    tableName = 'OrgStructure_HospitalBed'

    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)


    def _initByRecord(self, record):
        self._orgStructure = self.getInstance(COrgStructureInfo, forceRef(record.value('master_id')))
        self._isPermanent  = forceBool(record.value('isPermanent'))
        self._type         = self.getInstance(CHospitalBedTypeInfo, forceRef(record.value('type_id')))
        self._code         = forceString(record.value('code'))
        self._name         = forceString(record.value('name'))
        self._profile      = self.getInstance(CHospitalBedProfileInfo, forceRef(record.value('profile_id')))
        self._relief       = forceInt(record.value('relief'))
        self._schedule     = self.getInstance(CHospitalBedScheduleInfo, forceRef(record.value('schedule_id')))
        self._begDate      = CDateInfo(forceDate(record.value('begDate')))
        self._endDate      = CDateInfo(forceDate(record.value('endDate')))


    def _initByNull(self):
        self._orgStructure = self.getInstance(COrgStructureInfo, None)
        self._isPermanent  = None
        self._type         = self.getInstance(CHospitalBedTypeInfo, None)
        self._code         = ''
        self._name         = ''
        self._profile      = self.getInstance(CHospitalBedProfileInfo, None)
        self._relief       = None
        self._schedule     = self.getInstance(CHospitalBedScheduleInfo, None)
        self._begDate      = CDateInfo()
        self._endDate      = CDateInfo()


    orgStructure = property(lambda self: self.load()._orgStructure)
    isPermanent  = property(lambda self: self.load()._isPermanent)
    type         = property(lambda self: self.load()._type)
    code         = property(lambda self: self.load()._code)
    name         = property(lambda self: self.load()._name)
    profile      = property(lambda self: self.load()._profile)
    relief       = property(lambda self: self.load()._relief)
    schedule     = property(lambda self: self.load()._schedule)
    begDate      = property(lambda self: self.load()._begDate)
    endDate      = property(lambda self: self.load()._endDate)


class CHospitalBedTypeInfo(CRBInfo):
    tableName = 'rbHospitalBedType'


class CHospitalBedProfileInfo(CRBInfo):
    tableName = 'rbHospitalBedProfile'


class CHospitalBedScheduleInfo(CRBInfo):
    tableName = 'rbHospitalBedSchedule'


class CHospitalEventInfo(CEventInfo):
    def __init__(self, context, id):
        CEventInfo.__init__(self, context, id)
        self._action = None
        self._finance = '' # код финансирования
        self._bedCode = ''
        self._hasFeed = False
        self._feed = '' # код диеты

    def _load(self):
        db = QtGui.qApp.db
        if CEventInfo._load(self):
            return True
        else:
            return False

    action      = property(lambda self: self.load()._action)
    finance     = property(lambda self: self.load()._finance)
    bedCode     = property(lambda self: self.load()._bedCode)
    hasFeed     = property(lambda self: self.load()._hasFeed)
    feed        = property(lambda self: self.load()._feed)
   
