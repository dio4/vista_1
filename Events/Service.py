# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.PrintInfo import CDateInfo, CRBInfo
from library.Utils     import forceBool, forceInt, forceRef, forceString


class CServiceGroupInfo(CRBInfo):
    tableName = 'rbServiceGroup'

    def _initByRecord(self, record):
        self._regionalCode = forceString(record.value('regionalCode'))


    def _initByNull(self):
        self._regionalCode = None

    regionalCode  = property(lambda self: self.load()._regionalCode)


class CMedicalAidProfileInfo(CRBInfo):
    tableName = 'rbMedicalAidProfile'

    def _initByRecord(self, record):
        self._federalCode = forceString(record.value('federalCode'))
        self._regionalCode = forceString(record.value('regionalCode'))

    def _initByNull(self):
        self._federalCode = ''
        self._regionalCode = ''

    federalCode = property(lambda self: self.load()._federalCode)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CMedicalAidKindInfo(CRBInfo):
    tableName = 'rbMedicalAidKind'

    def _initByRecord(self, record):
        self._federalCode = forceString(record.value('federalCode'))
        self._regionalCode = forceString(record.value('regionalCode'))

    def _initByNull(self):
        self._federalCode = ''
        self._regionalCode = ''

    federalCode = property(lambda self: self.load()._federalCode)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CMedicalAidTypeInfo(CRBInfo):
    tableName = 'rbMedicalAidType'

    def _initByRecord(self, record):
        self._federalCode = forceString(record.value('federalCode'))
        self._regionalCode = forceString(record.value('regionalCode'))

    def _initByNull(self):
        self._federalCode = ''
        self._regionalCode = ''

    federalCode = property(lambda self: self.load()._federalCode)
    regionalCode = property(lambda self: self.load()._regionalCode)


class CServiceInfo(CRBInfo):
    tableName = 'rbService'

    def _initByRecord(self, record):
        self._groupId = forceRef(record.value('group_id'))
        self._eisLegacy = forceBool(record.value('eisLegacy'))
        self._license = forceBool(record.value('license'))
        self._infis = forceString(record.value('infis'))
        self._begDate = CDateInfo(record.value('begDate'))
        self._endDate = CDateInfo(record.value('endDate'))
        self._qualityLevel = forceInt(record.value('qualityLevel'))
        self._medicalAidProfile = self.getInstance(CMedicalAidProfileInfo,
                                                   forceRef(record.value('medicalAidProfile_id')))
        self._medicalAidKind = self.getInstance(CMedicalAidKindInfo,
                                                forceRef(record.value('medicalAidKind_id')))
        self._medicalAidType = self.getInstance(CMedicalAidTypeInfo,
                                                forceRef(record.value('medicalAidType_id')))

    def _initByNull(self):
        self._groupId = None
        self._eisLegacy = False
        self._eisLegacy = False
        self._license = False
        self._infis = ''
        self._begDate = CDateInfo()
        self._endDate = CDateInfo()
        self._qualityLevel = 0
        self._medicalAidProfileId = None
        self._medicalAidKindId = None
        self._medicalAidTypeId = None

    group               = property(lambda self: self.getInstance(CServiceGroupInfo, self.load()._groupId))
    eisLegacy           = property(lambda self: self.load()._eisLegacy)
    license             = property(lambda self: self.load()._license)
    infis               = property(lambda self: self.load()._infis)
    begDate             = property(lambda self: self.load()._begDate)
    endDate             = property(lambda self: self.load()._endDate)
    qualityLevel        = property(lambda self: self.load()._qualityLevel)
    medicalAidProfile   = property(lambda self: self.load()._medicalAidProfile)
    medicalAidKind      = property(lambda self: self.load()._medicalAidKind)
    medicalAidType      = property(lambda self: self.load()._medicalAidType)