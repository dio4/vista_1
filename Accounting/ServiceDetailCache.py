# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

# средство для определения профиля мед. помощи по услуге/полу/возрасту/коду МКБ
from library.AgeSelector import *
from library.Utils       import *


class CServiceDetailCache:
    def __init__(self):
        self._mapServiceIdToDetail = {}


    def get(self, serviceId):
        result = self._mapServiceIdToDetail.get(serviceId, None)
        if result is None:
            result = CServiceDetail(serviceId)
            self._mapServiceIdToDetail[serviceId] = result
        return result


class CServiceDetail:
    def __init__(self, serviceId):
        db = QtGui.qApp.db
        self.medicalAidProfileId = None
        self.medicalAidKindId = None
        self.medicalAidTypeId = None
        self.infisCode = ''
        self.profiles = []

        self._setupRecord(db, serviceId)
        self._setupProfiles(db, serviceId)


    def _setupRecord(self, db, serviceId):
        record = db.getRecord('rbService', ['infis', 'medicalAidProfile_id', 'medicalAidKind_id', 'medicalAidType_id'], serviceId)
        if record:
            self.infisCode = forceString(record.value('infis'))
            self.medicalAidProfileId = forceRef(record.value('medicalAidProfile_id'))
            self.medicalAidKindId = forceRef(record.value('medicalAidKind_id'))
            self.medicalAidTypeId = forceRef(record.value('medicalAidType_id'))


    def _setupProfiles(self, db, serviceId):
        table = db.table('rbService_Profile')
        for record in db.getRecordList(table, '*', table['master_id'].eq(serviceId), 'idx'):
            specialityId = forceRef(record.value('speciality_id'))
            sex = forceInt(record.value('sex'))
            age = forceString(record.value('age'))
            mkbRegExp = forceString(record.value('MKBRegExp'))
            profileId = forceRef(record.value('medicalAidProfile_id'))
            kindId = forceRef(record.value('medicalAidKind_id'))
            typeId = forceRef(record.value('medicalAidType_id'))
            self.profiles.append( CServiceMedicalAidProfile(specialityId, sex, age, mkbRegExp, profileId, kindId, typeId))


    def getMedicalAidIds(self, specialityId, clientSex, clientAge, mkb):
        for profile in self.profiles:
            if (    (not profile.specialityId or profile.specialityId == specialityId)
                and (not profile.sex or profile.sex == clientSex )
                and (not profile.age or checkAgeSelector(profile.age, clientAge))
                and (not profile.mkbRegExp or profile.mkbRegExp.indexIn(mkb) >=0)
               ):
                return profile.id, profile.kindId, profile.typeId
        return self.medicalAidProfileId, self.medicalAidKindId, self.medicalAidTypeId



class CServiceMedicalAidProfile:
    def __init__(self, specialityId, sex, age, mkbRegExp, profileId, kindId, typeId):
        self.specialityId = specialityId
        self.sex = sex
        self.age = parseAgeSelector(age) if age else None
        self.mkbRegExp = QtCore.QRegExp(mkbRegExp) if mkbRegExp else None
        self.id = profileId
        self.kindId = kindId
        self.typeId = typeId
