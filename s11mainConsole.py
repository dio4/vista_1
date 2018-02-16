#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import traceback
from PyQt4 import QtGui, QtCore

from Orgs.Utils import getOrganisationInfo
from Users.UserInfo import CUserInfo
from library.AgeSelector import parseAgeSelector, convertAgeSelectorToAgeRange
from library.Preferences import CPreferences
from library.Utils import forceString, forceRef, forceInt, log


class CS11MainConsoleApp(QtCore.QCoreApplication):
    def __init__(self, args, databaseConnectionInfo):
        super(CS11MainConsoleApp, self).__init__(args)
        from library.database import connectDataBaseByInfo
        QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

        self.logDir = os.path.join(unicode(QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())), '.vista-med')
        self.oldExceptHook = sys.excepthook
        sys.excepthook = self.logException

        self.preferences = CPreferences('S11App.ini')
        self.databaseConnectionInfo = databaseConnectionInfo
        self.connectionName = self.databaseConnectionInfo['connectionName']
        self.db = None
        self.userId = None
        self.userSpecialityId = None
        self.userOrgStructureId = None
        self.userInfo = None
        self._defaultKLADR = None
        self._provinceKLADR = None
        self._contingentDDEventTypeCodes = None
        self._contingentDDAgeSelectors = None
        self._globalPreferences = {}

        self.db = connectDataBaseByInfo(self.databaseConnectionInfo)
        self.loadGlobalPreferences()

    def log(self, title, message, stack=None):
        log(self.logDir, title, message, stack)

    def logException(self, exceptionType, exceptionValue, exceptionTraceback):
        u"""Перехватываем все необработанные исключения в системе.
            1) Пишем в файл с логом
            2) Показываем пользователю окошко с ошибкой
            3) Вызываем системный excepthook (он, в том числе, в stderr пишет)
        """
        title = repr(exceptionType)
        message = unicode(exceptionValue)
        stack = traceback.extract_tb(exceptionTraceback)
        self.log(title, message, stack)

        self.oldExceptHook(exceptionType, exceptionValue, exceptionTraceback)

    def logCurrentException(self):
        self.logException(*sys.exc_info())

    def loadGlobalPreferences(self):
        if self.db:
            # noinspection PyBroadException
            try:
                recordList = self.db.getRecordList('GlobalPreferences')
            except:
                recordList = []
            for record in recordList:
                code = forceString(record.value('code'))
                value = forceString(record.value('value'))
                self._globalPreferences[code] = value

    def checkGlobalPreference(self, code, chkValue):
        value = self._globalPreferences.get(code, None)
        if value:
            return unicode(value).lower() == unicode(chkValue).lower()
        return False

    def getGlobalPreference(self, code):
        value = self._globalPreferences.get(code, None)
        return unicode(value).lower() if value else None

    def getTemplateDir(self):
        result = forceString(self.preferences.appPrefs.get('templateDir', None))
        if not result:
            result = os.path.join(self.logDir, 'templates')
        return result

    def closeDatabase(self):
        u"""Подчистка блокировок при выходе из приложения"""
        if self.db:
            if self.db.db.isOpen():
                # noinspection PyBroadException
                try:
                    self.db.query('CALL CleanupLocks()', True)
                except:
                    pass
            self.db.close()
            self.db = None

    def setUserId(self, userId):
        self.userId = userId
        record = \
            self.db.getRecord('Person', ['speciality_id', 'orgStructure_id', 'post_id'], userId) if userId else None
        if record:
            self.userSpecialityId = forceRef(record.value('speciality_id'))
            self.userOrgStructureId = forceRef(record.value('orgStructure_id'))
        else:
            self.userSpecialityId = None
            self.userOrgStructureId = None
        if userId:
            self.userInfo = CUserInfo(userId)
        else:
            self.userInfo = None
        self.emit(QtCore.SIGNAL('currentUserIdChanged()'))

    def userName(self):
        if self.userInfo:
            orgId = self.currentOrgId()
            orgInfo = getOrganisationInfo(orgId)
            if not orgInfo:
                QtGui.qApp.preferences.appPrefs['orgId'] = QtCore.QVariant()
            shortName = orgInfo.get('shortName', u'ЛПУ в настройках не указано!')
            return u'%s (%s) %s' % (self.userInfo.name(), self.userInfo.login(), shortName)
        else:
            return ''

    def userHasRight(self, userRight):
        return self.userInfo is not None and self.userInfo.hasRight(userRight)

    def userHasProfile(self, profileId):
        return self.userInfo is not None and self.userInfo.hasProfile(profileId)

    def currentOrgId(self):
        return forceRef(self.preferences.appPrefs.get('orgId', QtCore.QVariant()))

    def currentOrgInfis(self):
        return forceString(self.db.translateEx('OrgStructure', 'id', self.currentOrgId(), 'infisCode'))

    def currentOrgStructureId(self):
        return forceRef(self.preferences.appPrefs.get('orgStructureId', QtCore.QVariant()))

    def defaultKLADR(self):
        u"""код КЛАДР по умолчанию"""
        if self._defaultKLADR is None:
            self._defaultKLADR = forceString(self.preferences.appPrefs.get('defaultKLADR', ''))
            if not self._defaultKLADR:
                self._defaultKLADR = '7800000000000'
        return self._defaultKLADR

    def getProvinceKLADRCode(self, KLADRCode):
        prefix = KLADRCode[:2]
        if prefix == '77':
            return '5000000000000'
        elif prefix == '78':
            return '4700000000000'
        elif prefix:
            return prefix + '00000000000'
        else:
            return ''

    def provinceKLADR(self):
        """областной код КЛАДР по умолчанию"""
        if self._provinceKLADR is None:
            self._provinceKLADR = forceString(self.preferences.appPrefs.get('provinceKLADR', ''))
            if not self._provinceKLADR:
                self._provinceKLADR = self.getProvinceKLADRCode(self.defaultKLADR())
        return self._provinceKLADR

    def region(self):
        region = self.globalRegion()
        if not region:
            region = self.defaultKLADR()[:2]
        return region

    def defaultIsManualSwitchDiagnosis(self):
        return self.checkGlobalPreference('1', u'в ручную')

    def defaultMorphologyMKBIsVisible(self):
        return self.checkGlobalPreference('2', u'да')

    def defaultHospitalBedProfileByMoving(self):
        u"""Учитывать профиль койки по движению:
        нет: по койке
        да:  по движению
        """
        return self.checkGlobalPreference('5', u'да')

    def defaultNeedPreCreateEventPerson(self):
        u"""необходимость контроля ответственного врача в диалоге 'новое обращение'"""
        return self.checkGlobalPreference('6', u'да')

    def defaultRegProbsWhithoutTissueJournal(self):
        return self.checkGlobalPreference('42', u'да')

    def isTNMSVisible(self):
        return self.checkGlobalPreference('7', u'да')

    def isStrictAttachCheckOnEventCreation(self):
        return self.checkGlobalPreference('8', u'да')

    def defaultHospitalBedFinanceByMoving(self):
        u"""Глобальная настройка для определения правила учета источника финансирования в стац. мониторе:
        по событию
        по движению
        по движению или событию
        """
        return self.checkGlobalPreferenceHospitalBedFinance('9')

    def checkGlobalPreferenceHospitalBedFinance(self, code):
        checkGlobalPreferenceList = {u'по событию': 0, u'по движению': 1, u'по движению или событию': 2}
        value = self._globalPreferences.get(code, None)
        if value:
            return checkGlobalPreferenceList.get(unicode(value).lower(), None)
        return None

    def isRestrictedEventCreationByContractPresence(self):
        return self.checkGlobalPreference('10', u'да')

    def isNextEventCreationFromAction(self):
        return self.checkGlobalPreference('11', u'да')

    def isTimelineAccessibilityDays(self):
        code = '12'
        checkGlobalPreferenceList = {u'Внешняя ИС': 0, u'Вся ИС': 1}
        value = self._globalPreferences.get(code, None)
        if value:
            return checkGlobalPreferenceList.get(unicode(value), None)
        return None

    def isBindNurseWithDoctor(self):
        u"""
            Atronah for issue 353:
            Проверка на необходимость делать привязку медсестры к врачу.
        """
        return self.checkGlobalPreference('13', u'да')

    def isSeparateStaffFromPatient(self):
        return self.checkGlobalPreference('14', u'да')

    def isCheckOnlyClientNameAndBirthdateAndSex(self):
        return self.checkGlobalPreference('15', u'да')

    def getDiscountParams(self):
        import re
        doscountPreferencesCode = '16'
        result = (0, 0, 0, 0, 0, 0, 0, [])
        discountParams = self.getGlobalPreference(doscountPreferencesCode)

        if discountParams is None:
            return result

        if isinstance(discountParams, basestring):
            rePattern = r'<(\d):(\d{1,3})%;(\d)-(\d):(\d{1,3})%;>(\d):(\d{1,3})%;'
            rexp = re.compile(rePattern)
            # поиск выражения вида "<A:B%;C-D:E%;>F:J%"
            match = rexp.match(discountParams)
            if match is None:
                return result
            discountValues = match.groups()
            relativeTypeCodeIndex = match.span()[1]
            relativeTypeCodeString = discountParams[relativeTypeCodeIndex:]
            relativeTypeCodeList = []
            for codeMatch in re.finditer(r'(\d{1,5})', relativeTypeCodeString):
                relativeTypeCodeList.append(codeMatch.group())
            lowThan = forceInt(discountValues[0])
            lowDiscount = forceInt(discountValues[1]) / 100.0
            leftBound = forceInt(discountValues[2])
            rightBound = forceInt(discountValues[3])
            middleDiscount = forceInt(discountValues[4]) / 100.0
            highThan = forceInt(discountValues[5])
            highDiscount = forceInt(discountValues[6]) / 100.0
            result = (lowThan, lowDiscount, leftBound, rightBound, middleDiscount, highThan, highDiscount,
                      relativeTypeCodeList)
            self._globalPreferences[doscountPreferencesCode] = result

        elif isinstance(discountParams, tuple):
            return discountParams

        return result

    def isCheckPolisEndDateAndNumberEnabled(self):
        return self.checkGlobalPreference('17', u'да')

    def isButtonBoxAtTopWindow(self):
        return self.checkGlobalPreference('18', u'да')

    def hideLeaversBeforeCurrentYearPatients(self):
        return self.checkGlobalPreference('20', u'до начала текущего года') or self.checkGlobalPreference('20', u'да')

    def hideAllLeavers(self):
        return self.checkGlobalPreference('20', u'всех')

    def isReferralRequired(self):
        u"""Ввод направления при создании обращения из любого места, кроме 'Графика'"""
        return self.checkGlobalPreference('21', u'да') or \
               self.checkGlobalPreference('21', u'1') or \
               self.checkGlobalPreference('21', u'2')

    def isReferralRequiredInPreRecord(self):
        u"""Ввод направления при создании обращения из 'Графика'"""
        return self.checkGlobalPreference('21', u'да') or self.checkGlobalPreference('21', u'1')

    def addUnregisteredRelationsEnabled(self):
        return self.checkGlobalPreference('22', u'да')

    def isShowPolicyInsuranceArea(self):
        return self.checkGlobalPreference('23', u'да')

    def isAllowedExtendedMKB(self):
        return self.checkGlobalPreference('24', u'да')

    def useInputMask(self):
        return self.checkGlobalPreference('25', u'да')

    def isHideActionsFromOtherTopOrgStructures(self):
        return self.checkGlobalPreference('26', u'да')

    def isShowActionsForChildOrgStructures(self):
        return self.checkGlobalPreference('27', u'да')

    def addBySingleClick(self):
        return self.checkGlobalPreference('28', u'да')

    def hideTimeInQueueTable(self):
        return self.checkGlobalPreference('29', u'да')

    def isSelectOnlyLeafOfMKBTree(self):
        return self.checkGlobalPreference('30', u'да')

    def noDefaultResult(self):
        return self.checkGlobalPreference('31', u'да')

    def changePrimaryChkBox(self):
        return self.checkGlobalPreference('31', u'да')

    def isRestrictByUserOS(self):
        return self.checkGlobalPreference('32', u'да')

    def isExcludeRedDaysInEventLength(self):
        return self.checkGlobalPreference('33', u'да')

    def isUseUnifiedDailyClientQueueNumber(self):
        return self.checkGlobalPreference('34', u'да')

    def isSupportCreateNosologyEvent(self):
        return self.checkGlobalPreference('35', u'да')

    def isPNDDiagnosisMode(self):
        return self.checkGlobalPreference('36', u'да')

    def strictOccupationControl(self):
        return self.checkGlobalPreference('37', u'да')

    def autoCreationOfNextEvent(self):
        return self.checkGlobalPreference('38', u'да')

    def changeFocusInPreCreateEvent(self):
        # TODO: Сейчас при создании нового обращения фокус ставится на комбобокс с ЛПУ.
        # Неловкое движение - и он изменяется, причем незаметно.
        # Пока решили перемещать курсор на Тип обращения, но Песочке это неудобно.
        # К тому же, есть вероятность, что ЛПУ может изменяться само по себе независимо от манипуляций с комбобоксом.
        # В дальнейшем надо убедиться, что подобное поведение исключено и изменить назначение данной настройки -
        # она должна будет скрывать комбобокс ЛПУ.
        return self.checkGlobalPreference('39', u'да')

    def outputAllRelations(self):
        return self.checkGlobalPreference('41', u'да')

    def filterByExactTime(self):
        return self.checkGlobalPreference('44', u'да')

    def isCheckMKB(self):
        return self.checkGlobalPreference('45', u'да')

    def showFavouriteActionTypesButton(self):
        return self.checkGlobalPreference('48', u'да')

    def getClientAgeOnEventSetDate(self):
        return self.checkGlobalPreference('49', u'да')

    def changingDayTime(self):
        stringTime = self._globalPreferences.get(u'40', u'00:00')
        # noinspection PyCallByClass
        return QtCore.QTime.fromString(stringTime,
                                       u'hh:mm')

    def globalRegion(self):
        return self._globalPreferences.get('50', u'')

    def justifyDrugRecipeNumber(self):
        return self.checkGlobalPreference('51', u'да')

    def checkContingentDDGlobalPreference(self):
        self._contingentDDAgeSelectors = []
        self._contingentDDEventTypeCodes = []

        filterDD = self._globalPreferences.get('52', u'').replace(' ', '')
        delimInd = filterDD.find(';')
        if delimInd == -1:
            return False

        ageSelectors = filterDD[:delimInd]
        for selectorTuple in parseAgeSelector(ageSelectors, True):
            if not selectorTuple:
                return False
            begUnit, begCount, endUnit, endCount, step, useCalendarYear, useExlusion = selectorTuple
            begAge, endAge = convertAgeSelectorToAgeRange((begUnit, begCount, endUnit, endCount))
            if begAge > endAge:
                return False
            self._contingentDDAgeSelectors.append((begAge, endAge, step, useCalendarYear, useExlusion))

        eventTypeCodes = filterDD[delimInd + 1:]
        if not eventTypeCodes:
            return False
        self._contingentDDEventTypeCodes = eventTypeCodes.split(',')

        return True

    def isExtractedDocAutocomplete(self):
        return self.checkGlobalPreference('54', u'да')

    def isDeferredQueueAutoUpdateEnabled(self):
        return self.checkGlobalPreference('56', u'да')

    def isViewDMCPercent(self):
        return self.checkGlobalPreference('60', u'да')

    def isAskAccess(self):
        return self.checkGlobalPreference('61', u'да')

    def isLimitVisibilityOrgStructTree(self):
        return self.checkGlobalPreference('62', u'да')

    def isNotLimitedTableColsSize(self):
        return self.checkGlobalPreference('63', u'да')

    def isEventLockEnabled(self):
        return self.checkGlobalPreference('64', u'да')

    def isDisableHospStatEvent(self):
        return self.checkGlobalPreference('65', u'да')

    def isWindowPrefsDisabled(self):
        return self.checkGlobalPreference('66', u'да')

    def isAutoClosed(self):
        return self.checkGlobalPreference('67', u'да')

    def getContingentDDAgeSelectors(self):
        return self._contingentDDAgeSelectors

    def getContingentDDEventTypeCodes(self):
        return self._contingentDDEventTypeCodes
