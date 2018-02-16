# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Users import Rights
from Users.Tables import tblUser, usrLogin, usrName
from library.Utils import forceRef, forceString


class CUserInfo(object):
    def __init__(self, userId):
        db = QtGui.qApp.db
        tablePUP = db.table('Person_UserProfile')
        recPerson = db.getRecord(tblUser, [usrLogin, usrName, 'userProfile_id', 'orgStructure_id', 'speciality_id'], userId)
        self._userId = userId
        self.userProfilesId = db.getIdList(tablePUP, tablePUP['userProfile_id'], tablePUP['person_id'].eq(userId))
        self._login = forceString(recPerson.value(usrLogin))
        self._name = forceString(recPerson.value(usrName))
        self._availableJobTypes = CUserAvailableJobTypes(self._userId)
        self._orgStructureId = forceRef(recPerson.value('orgStructure_id'))
        self.specialityId = forceRef(recPerson.value('speciality_id'))
        self._rights = []
        self._profiles = []
        self._hiddenGUIWidgets = []
        self._hiddenGUIWidgetsOfFirstProfile = []
        self.reloadRightsAndHiddenUI()

    def reloadRightsAndHiddenUI(self):
        self._rights, self._profiles = loadProfileAndRights(self._userId)
        self._hiddenGUIWidgets = self.loadHiddenGUIWidgetsNameList(self._userId)
        self._hiddenGUIWidgetsOfFirstProfile = self.loadHiddenGUIWidgetsNameList(
            self._userId,
            self.userProfilesId[0] if self.userProfilesId else []
        )

    @property
    def orgStructureId(self):
        """
            Return orgStructure ID to which user if exists, else None
        :rtype : int or None
        :return: orgStructure ID to which user
        """
        return self._orgStructureId

    ## Загружает список имен скрываемых элементов интерфейса для текущего профиля прав
    # @param profileId: идентификатор профиля прав, для которого будет загружен список
    @staticmethod
    def loadHiddenGUIWidgetsNameList(userId, userProfileId=None):
        if userId:
            db = QtGui.qApp.db
            tablePUP = db.table('Person_UserProfile')
            tableUPH = db.table('rbUserProfile_Hidden')
            cond = [
                tablePUP['person_id'].eq(userId)
            ]
            if userProfileId:
                cond.append(tablePUP['userProfile_id'].eq(userProfileId))

            return db.getColumnValues(tablePUP.innerJoin(tableUPH, tableUPH['master_id'].eq(tablePUP['userProfile_id'])),
                                      'objectName',
                                      cond)
        return []

    def availableJobTypeIdList(self):
        return self._availableJobTypes.availableJobTypeIdList()

    def isAvailableJobTypeId(self, jobTypeId):
        return self._availableJobTypes.isAvailableJobTypeId(jobTypeId)

    def isAvailableJobType(self, jobTypeCode):
        return self._availableJobTypes.isAvailableJobType(jobTypeCode)

    def login(self):
        return self._login

    def name(self):
        return self._name

    def hasRight(self, right):
        return right.lower() in self._rights

    def hasProfile(self, profileId):
        return profileId in self._profiles

    def hasAnyRight(self, rights):
        return any(self.hasRight(right) for right in rights)

    def isObjectHidden(self, objectName):
        return objectName in self._hiddenGUIWidgets

    def hiddenObjectNames(self):
        return self._hiddenGUIWidgets

    ## Возвращает список полных имен объектов, которые должны быть скрыты для текущего пользователя согласно настройкам профиля прав.
    # @baseNameParts: список строк. Если задан, то будут возвращены имена не всех необходимых для скрытия объектов, 
    #                 а только тех, чье имя начинается с указанных частей (разделенных точкой)
    # @return: список имен объектов, которые необходимо скрывать для пользователя и которые начинаются с baseNameParts.
    def hiddenObjectsNameList(self, baseNameParts=None, fromFistProfile=False):
        hiddenWidgets = self._hiddenGUIWidgetsOfFirstProfile if fromFistProfile else self._hiddenGUIWidgets
        if isinstance(baseNameParts, list):
            baseName = '.'.join(baseNameParts)
        elif isinstance(baseNameParts, QtCore.QString):
            baseName = forceString(baseNameParts)
        elif isinstance(baseNameParts, basestring):
            baseName = baseNameParts
        else:
            baseName = u''
        return [objName for objName in hiddenWidgets if not baseName or objName.startswith(baseName)]


class CDemoUserInfo(CUserInfo):
    def __init__(self, userId):
        self._login = 'demo'
        self._name = 'demo'
        self._rights = set([])
        self._availableJobTypeIdList = QtGui.qApp.db.getIdList('rbJobType')
        self._orgStructureId = None
        self._hiddenGUIWidgets = []

    def availableJobTypeIdList(self):
        return self._availableJobTypeIdList

    def hasRight(self, right):
        return True

    def isAvailableJobTypeId(self, jobTypeId):
        return True

    def isAvailableJobType(self, jobTypeCode):
        return True


class CUserAvailableJobTypes(object):
    def __init__(self, userId):
        self._userId = userId

        self._mapJobTypeCodeToId = {}
        self._availableJobTypeIdList = []

        self._init(userId)

    def clear(self):
        self._mapJobTypeCodeToId.clear()
        self._availableJobTypeIdList = []

    def _init(self, userId):
        assert self._userId == userId

        self.clear()

        db = QtGui.qApp.db
        tablePersonJobType = db.table('Person_JobType')
        tableJobType = db.table('rbJobType')

        jobTypeIdList = db.getIdList(tablePersonJobType,
                                     tablePersonJobType['jobType_id'],
                                     tablePersonJobType['master_id'].eq(userId))
        result = set([])
        for jobTypeId in jobTypeIdList:
            result |= set(db.getDescendants(tableJobType, 'group_id', jobTypeId))
        jobTypeIdList = list(result)

        cols = [
            tableJobType['code'].name(),
            tableJobType['id'].name()
        ]

        for record in db.iterRecordList(tableJobType, cols, tableJobType['id'].inlist(jobTypeIdList)):
            jobTypeId = forceRef(record.value('id'))
            jobTypeCode = forceString(record.value('code'))
            self._mapJobTypeCodeToId[jobTypeCode] = jobTypeId
            self._availableJobTypeIdList.append(jobTypeId)

    def jobTypeId(self, jobTypeCode):
        return self._mapJobTypeCodeToId.get(jobTypeCode, None)

    def isAvailableJobTypeId(self, jobTypeId):
        if self._availableJobTypeIdList:
            return jobTypeId in self._availableJobTypeIdList
        return True

    def isAvailableJobType(self, jobTypeCode):
        jobTypeId = self.jobTypeId(jobTypeCode)
        return self.isAvailableJobTypeId(jobTypeId)

    def availableJobTypeIdList(self):
        return self._availableJobTypeIdList


def loadProfileAndRights(userId):
    from library.crbcombobox import CRBModelDataCache
    profileList = []
    rightList = []
    db = QtGui.qApp.db
    if userId:
        tablePUP = db.table('Person_UserProfile')
        tableUPR = db.table('rbUserProfile_Right')
        tableUR = db.table('rbUserRight')

        table = tablePUP.innerJoin(tableUPR, tableUPR['master_id'].eq(tablePUP['userProfile_id']))
        table = table.innerJoin(tableUR, tableUR['id'].eq(tableUPR['userRight_id']))

        cols = [
            tablePUP['userProfile_id'].alias('profileId'),
            tableUR['code'].alias('rightCode')
        ]

        for record in db.iterRecordList(table, cols, tablePUP['person_id'].eq(userId)):
            profileId = forceRef(record.value('profileId'))
            rightCode = forceString(record.value('rightCode')).lower()
            if profileId not in profileList:
                profileList.append(profileId)
            if rightCode not in rightList:
                rightList.append(rightCode)

    # Находим все права, которые забыли добавить в БД с помощью апдейтов. Считаем, что если право не добавили в БД
    # и его нельзя выбрать в интерфейсе, то оно есть у пользователя.
    allRights = []
    for var in dir(Rights):
        if var.startswith('ur'):
            allRights.append(forceString(Rights.__getattribute__(var)))
    rightsCache = CRBModelDataCache.getData('rbUserRight', False)
    if rightsCache._notLoaded:
        rightsCache.load()
    extraRights = set(allRights).symmetric_difference(rightsCache.getAllCodes())
    # Убираем права, которые по умолчанию считаются отсутствующими (редко, но требуется)
    extraRights = extraRights - set(Rights.DefaultDisabledRights)

    extraRights = set([r.lower() for r in extraRights])

    rightList = set(rightList)
    rightList.update(extraRights)
    return rightList, profileList
