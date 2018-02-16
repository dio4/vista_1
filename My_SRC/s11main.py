#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################
##
## Copyright (C) 2006-2017 Vista Software. All rights reserved.
##
###############################################################

import codecs
import gc
import glob
import hashlib
import locale
import os
import os.path
import re
import shutil
import socket
import sys
import tempfile
import traceback
from PyQt4 import QtCore, QtGui
from getpass import getuser
from optparse import OptionParser
from socket import error as SocketError

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from GUIHider.VisibleStateManager import CVisibleStateManager  # имена файлов .py соответств. каталога (подкаталога) -> см. каталоги
from HospitalBeds.HospitalBedsDialog import CHospitalBedsDialog
from KLADR.Utils import getProvinceKLADRCode
from Orgs.PersonComboBox import CPersonComboBox
from Orgs.Utils import getOrganisationInfo
from Registry.DiagnosisDock import CDiagnosisDockWidget
from Registry.FreeQueueDock import CFreeQueueDockWidget
from Registry.OpenedEventsDock import COpenedEventsDockWidget
from Registry.RegistryWindow import CRegistryWindow
from Registry.ResourcesDock import CResourcesDockWidget
from Ui_s11main import Ui_MainWindow
from Users.Informer import showInformer
from Users.Login import CLoginDialog, createLogin, getADUser, verifyUser, verifyUserPassword
from Users.RightList import CUserRightListDialog, CUserRightProfileListDialog
from Users.Rights import *
from Users.Tables import demoUserName, tblUser, usrLogin, usrRetired
from Users.UserInfo import CDemoUserInfo, CUserInfo
from library import database
from library.AgeSelector import convertAgeSelectorToAgeRange, parseAgeSelector
from library.ElectronicQueue.EQController import CEQController
from library.ErrorBox import CErrorBox
from library.LoggingModule import Logger
from library.Preferences import CPreferences
from library.Thread import CThreadSingleApplication
from library.Utils import forceBool, forceDateTime, forceInt, forceRef, forceString, forceStringEx, getPref, getVal, \
    log, logException, setPref, splitShellCommand, toVariant
from library.calendar import CCalendarExceptionList
from library.exception import CDatabaseException, CSoapException
from preferences.appPreferencesDialog import DefaultAverageDuration
from preferences.connection import CConnectionDialog

title = u'ВИСТА-МЕД'
titleLat = 'VISTA-MED'
about = u'''Комплекс Программных Средств 
"Система автоматизации медико-страхового обслуживания населения"
КПС «%s»
Версия 2.0 (ревизия %s от %s)
Ревизия МИС КПС "Виста-Мед" %s от %s
Copyright (C) 2007-2011 ООО "Чук и Гек" и ООО "Виста"
Copyright (C) 2012-2017 ООО "Виста"
распространяется под лицензией GNU GPL v.3 или выше
телефоны тех.поддержки:
    8-800-200-87-60
    (812) 416-60-50
    (812) 416-60-51
    (812) 324-46-14
    (812) 324-32-07
    (812) 324-46-15

Рабочая директория: "%s"'''


class CS11mainApp(QtGui.QApplication):
    __pyqtSignals__ = ('dbConnectionChanged(bool)',
                       'currentOrgIdChanged()',
                       'currentOrgStructureIdChanged()',
                       'currentClientIdChanged()',
                       'currentClientInfoChanged()',
                       'currentUserIdChanged()',
                       'createdOrder()')

    inputCalculatorMimeDataType = 'vista-med/inputLaboratoryCalculator'
    outputCalculatorMimeDataType = 'vista-med/outputLaboratoryCalculator'
    connectionName = 'vistamed'

    def __init__(self, args, demoModeRequest, customIniFileName, disableLock, disableWindowPrefs=False):
        QtGui.QApplication.__init__(self, args)

        self.logDir = os.path.join(unicode(QDir.toNativeSeparators(QDir.homePath())), '.vista-med')
        oldLogDir = os.path.join(unicode(QDir.toNativeSeparators(QDir.homePath())), '.samson-vista')
        if os.path.exists(oldLogDir) and not os.path.exists(self.logDir):
            os.rename(oldLogDir, self.logDir)
        self.oldMsgHandler = qInstallMsgHandler(self.msgHandler)
        self.oldExceptHook = sys.excepthook
        sys.excepthook = self.logException
        self.preferences = CPreferences(customIniFileName if customIniFileName else 'S11App.ini')
        self.loadPreferences(disableWindowPrefs)
        self.traceActive = True
        self.homeDir= None
        self.saveDir= None
        self.userId = None
        self.hostName = socket.gethostname()
        self.userSpecialityId = None
        self.userPostId = None
        self.userOrgStructureId = None
        self.demoMode = False
        self.demoModeRequested = demoModeRequest or ('-demo' in args)
        self.loggedWithoutPassword = False
        self.disableLockRequested = disableLock
        self.disableLock = disableLock
        self.db = None  # type: database.CMySqlDatabase
        self.EIS_db = None
        self.mainWindow = None
        self.registerDocumentTables()
        self.clearPreferencesCache()
        self._currentClientId = None
        self.userInfo = None
        self.calendarInfo = CCalendarExceptionList()
        self.maxLifeDuration = 130
        self.currentJTR = None # JobTicketReserve
        self.eventLogFile = None
        self.eventLogTime = 0
        self._globalPreferences = {}
        self._visibleControledObjectNameList = None
        self._oldClipboardSlot = None
        self.accountingSystem = None
        self._isNurseUser = False
        self._nurseOwnerId = None
        self._nurseOwnerSpecialityId = None
        self._isNeedAddComment = False
        self._personCommentText = u''
        self.openedEvents = []
        self.datetimeDiff = 0
        self.isAuth = False
        # self.hasRightToRunMoreThanOneProgramm = False

        try:
            self.threadSingleApplication = CThreadSingleApplication(getuser() + 'checkForRights')
            self.connect(self.threadSingleApplication, QtCore.SIGNAL('hasRight(bool)'), self.onHasRightToRunMoreThanOneProgramm)
            self.threadSingleApplication.checkConnection()
            self.isServer = self.threadSingleApplication.isServer
            if self.isServer or self.hasRightToRunMoreThanOneProgramm:
                self.threadSingleApplication.run()
        except:
            self.isServer = True

        try:
            import faulthandler
            import buildInfo

            if hasattr(buildInfo, 'DB_DEBUG') and buildInfo.DB_DEBUG:
                faulthandler.enable()
            else:
                self.crashLog = open(os.path.join(self.logDir, 'crash.log'), 'a', 0)
                faulthandler.enable(self.crashLog)
        except (ImportError, IOError):
            pass

    @QtCore.pyqtSlot(bool)
    def onHasRightToRunMoreThanOneProgramm(self, value):
        try:
            self.threadSingleApplication.setHasRight(value)
        except:
            pass
        self.hasRightToRunMoreThanOneProgramm = value

    def connectClipboard(self, slotFunction):
        self.disconnectClipboard()
        self._oldClipboardSlot = slotFunction
        self.connect(self.clipboard(), SIGNAL('dataChanged()'), slotFunction)

    def disconnectClipboard(self):
        if self._oldClipboardSlot:
            self.disconnect(self.clipboard(), SIGNAL('dataChanged()'), self._oldClipboardSlot)
            self._oldClipboardSlot = None

    def doneTrace(self):
        self.traceActive = False
        qInstallMsgHandler(self.oldMsgHandler)
        sys.excepthook = self.oldExceptHook

    def loadPreferences(self, disableWindowPrefs):
        if disableWindowPrefs:
            onlyTheseGroups = self.preferences.supportedGroupNames()
            onlyTheseGroups.remove(u'windowPrefs')
            self.preferences.load(onlyTheseGroups)
            self.preferencesDir = self.preferences.getDir()
        else:
            self.preferences.load()
            self.preferencesDir = self.preferences.getDir()

    def loadWindowsPreferences(self):
        self.preferences.load()
        self.preferencesDir = self.preferences.getDir()

    def applyDecorPreferences(self):
        self.setStyle(self.preferences.decorStyle)
        font = QtGui.qApp.font()
        font.setPointSize(self.preferences.decorFontSize)
        font.setFamily(self.preferences.decorFontFamily)
        font.setWeight(QtGui.QFont.Normal)
        QtGui.qApp.setFont(font)
        if self.preferences.decorStandardPalette:
            self.setPalette(self.style().standardPalette())
        p = self.palette()
        p.setBrush(QPalette.ToolTipBase, QColor(255, 255, 175))
        p.setBrush(QPalette.ToolTipText, QColor(0, 0, 0))
        p.setBrush(QPalette.Disabled, QPalette.WindowText, QColor(80, 80, 80))
        p.setBrush(QPalette.Disabled, QPalette.ButtonText, QColor(80, 80, 80))
        p.setBrush(QPalette.Disabled, QPalette.Text, QColor(80, 80, 80))
        self.setPalette(p)
        if self.mainWindow:
            state = Qt.WindowNoState
            if self.preferences.decorMaximizeMainWindow:
                state |= Qt.WindowMaximized
            if self.preferences.decorFullScreenMainWindow:
                state |= Qt.WindowFullScreen
            self.mainWindow.setWindowState(state)

    def defaultPrintFont(self):
        font = QtGui.QFont(forceString(self.preferences.appPrefs.get('printFontFamily', 'Times New Roman')))
        font.setPointSize(forceInt(self.preferences.appPrefs.get('printFontFamilySize', 11)))
        return font

    def registerDocumentTables(self):
        database.registerDocumentTable('Account')
        database.registerDocumentTable('Action')
        database.registerDocumentTable('ActionProperty')
        database.registerDocumentTable('ActionPropertyTemplate')
        database.registerDocumentTable('ActionTemplate')
        database.registerDocumentTable('ActionType')
        database.registerDocumentTable('Action_ExecutionPlan')
        database.registerDocumentTable('Address')
        database.registerDocumentTable('AddressAreaItem')
        database.registerDocumentTable('AddressHouse')
        database.registerDocumentTable('Bank')
        database.registerDocumentTable('BlankTempInvalid_Party')
        database.registerDocumentTable('BlankActions_Party')
        database.registerDocumentTable('BlankTempInvalid_Moving')
        database.registerDocumentTable('BlankActions_Moving')
        database.registerDocumentTable('CalendarExceptions')
        database.registerDocumentTable('Client')
        database.registerDocumentTable('Client_LocationCard')
        database.registerDocumentTable('ClientAddress')
        database.registerDocumentTable('ClientAllergy')
        database.registerDocumentTable('ClientAttach')
        database.registerDocumentTable('ClientCompulsoryTreatment')
        database.registerDocumentTable('ClientContact')
        database.registerDocumentTable('ClientIdentification')
        database.registerDocumentTable('ClientIntoleranceMedicament')
        database.registerDocumentTable('ClientDocument')
        database.registerDocumentTable('ClientMonitoring')
        database.registerDocumentTable('ClientPolicy')
        database.registerDocumentTable('ClientSocStatus')
        database.registerDocumentTable('ClientWork')
        database.registerDocumentTable('ClientFile')
        database.registerDocumentTable('Contract')
        database.registerDocumentTable('Diagnosis')
        database.registerDocumentTable('Diagnostic')
        database.registerDocumentTable('EmergencyCall')
        database.registerDocumentTable('ClientRelation')
        database.registerDocumentTable('Event')
        database.registerDocumentTable('Event_LocalContract')
        database.registerDocumentTable('Event_OutgoingReferral')
        database.registerDocumentTable('Event_Payment')
        database.registerDocumentTable('EventType')
        database.registerDocumentTable('Event_Feed')
        database.registerDocumentTable('Event_Feed_Meal')
        database.registerDocumentTable('Event_OutgoingReferral')
        database.registerDocumentTable('Event_PhysicalActivity')
        database.registerDocumentTable('ForeignHospitalization')
        database.registerDocumentTable('InformerMessage')
        database.registerDocumentTable('Licence')
        database.registerDocumentTable('Organisation')
        database.registerDocumentTable('OrgStructure')
        database.registerDocumentTable('Person')
        database.registerDocumentTable('Person_Activity')
        database.registerDocumentTable('Person_TimeTemplate')
        database.registerDocumentTable('SocStatus')
        database.registerDocumentTable('TempInvalid')
        database.registerDocumentTable('Visit')
        database.registerDocumentTable('QuotaType')
        database.registerDocumentTable('Quoting')
        database.registerDocumentTable('Quoting_Region')
        database.registerDocumentTable('Client_Quoting')
        database.registerDocumentTable('Job')
        database.registerDocumentTable('TakenTissueJournal')
        database.registerDocumentTable('Probe')
        database.registerDocumentTable('rbPrintTemplate')
        database.registerDocumentTable('Referral')
        database.registerDocumentTable('rbAccountExportFormat')
        database.registerDocumentTable('rbAccountingSystem')
        database.registerDocumentTable('rbActionShedule')
        database.registerDocumentTable('rbActionShedule_Item')
        database.registerDocumentTable('rbActionTypeIncompatibility')
        # database.registerDocumentTable('rbActionTypeSimilarity')
        database.registerDocumentTable('rbActivity')
        database.registerDocumentTable('rbAgreementType')
        database.registerDocumentTable('rbAssignedContracts')
        database.registerDocumentTable('rbAttachType')
        database.registerDocumentTable('rbBlankActions')
        database.registerDocumentTable('rbBlankTempInvalids')
        database.registerDocumentTable('rbBloodType')
        database.registerDocumentTable('rbCashOperation')
        database.registerDocumentTable('rbCitizenship')
        database.registerDocumentTable('rbComplain')
        database.registerDocumentTable('rbContactType')
        database.registerDocumentTable('rbContainerType')
        database.registerDocumentTable('rbCureType')
        database.registerDocumentTable('rbDeferredQueueStatus')
        database.registerDocumentTable('rbDetachmentReason')
        database.registerDocumentTable('rbDiagnosisType')
        database.registerDocumentTable('rbDiagnosticResult')
        database.registerDocumentTable('rbDiet')
        database.registerDocumentTable('rbDiseaseCharacter')
        database.registerDocumentTable('rbDiseasePhases')
        database.registerDocumentTable('rbDiseaseStage')
        database.registerDocumentTable('rbDispanser')
        database.registerDocumentTable('rbDocumentType')
        database.registerDocumentTable('rbDocumentTypeGroup')
        database.registerDocumentTable('rbECROperationType')
        database.registerDocumentTable('rbEmergencyAccident')
        database.registerDocumentTable('rbEmergencyCauseCall')
        database.registerDocumentTable('rbEmergencyDeath')
        database.registerDocumentTable('rbEmergencyDiseased')
        database.registerDocumentTable('rbEmergencyEbriety')
        database.registerDocumentTable('rbEmergencyMethodTransportation')
        database.registerDocumentTable('rbEmergencyPlaceCall')
        database.registerDocumentTable('rbEmergencyPlaceReceptionCall')
        database.registerDocumentTable('rbEmergencyReasondDelays')
        database.registerDocumentTable('rbEmergencyReceivedCall')
        database.registerDocumentTable('rbEmergencyResult')
        database.registerDocumentTable('rbEmergencyTransferredTransportation')
        database.registerDocumentTable('rbEmergencyTypeAsset')
        database.registerDocumentTable('rbEQGatewayConfig')
        database.registerDocumentTable('rbEquipment')
        database.registerDocumentTable('rbEquipmentType')
        database.registerDocumentTable('rbEventGoal')
        database.registerDocumentTable('rbEventProfile')
        database.registerDocumentTable('rbEventTypePurpose')
        database.registerDocumentTable('rbExpenseServiceItem')
        database.registerDocumentTable('rbFinance')
        database.registerDocumentTable('rbHealthGroup')
        database.registerDocumentTable('rbHighTechCureKind')
        database.registerDocumentTable('rbHighTechCureMethod')
        database.registerDocumentTable('rbHospitalBedProfile')
        database.registerDocumentTable('rbHospitalBedShedule')
        database.registerDocumentTable('rbHospitalBedType')
        database.registerDocumentTable('rbHurtFactorType')
        database.registerDocumentTable('rbHurtType')
        database.registerDocumentTable('rbImageMap')
        database.registerDocumentTable('rbJobType')
        database.registerDocumentTable('rbJobType_ActionType')
        database.registerDocumentTable('rbLaboratory')
        database.registerDocumentTable('rbLocationCardType')
        database.registerDocumentTable('rbMealTime')
        database.registerDocumentTable('rbMedicalAidKind')
        database.registerDocumentTable('rbMedicalAidProfile')
        database.registerDocumentTable('rbMedicalAidType')
        database.registerDocumentTable('rbMedicalAidUnit')
        database.registerDocumentTable('rbMenu')
        database.registerDocumentTable('rbMenu_Content')
        database.registerDocumentTable('rbMesSpecification')
        database.registerDocumentTable('rbMKBSubclass')
        database.registerDocumentTable('rbMKBSubclass_Item')
        database.registerDocumentTable('rbNet')
        database.registerDocumentTable('rbNomenclature')
        database.registerDocumentTable('rbNomenclature_Analog')
        database.registerDocumentTable('rbNomenclatureClass')
        database.registerDocumentTable('rbNomenclatureKind')
        database.registerDocumentTable('rbNomenclatureType')
        database.registerDocumentTable('rbOKFS')
        database.registerDocumentTable('rbOKPF')
        database.registerDocumentTable('rbOKVED')
        database.registerDocumentTable('rbPatientModel')
        database.registerDocumentTable('rbPatientModel_Item')
        database.registerDocumentTable('rbPayRefuseType')
        database.registerDocumentTable('rbPersonCategory')
        database.registerDocumentTable('rbPhysicalActivityMode')
        database.registerDocumentTable('rbPolicyKind')
        database.registerDocumentTable('rbPolicyType')
        database.registerDocumentTable('rbPost')
        database.registerDocumentTable('rbPrerecordQuotaType')
        database.registerDocumentTable('rbReasonOfAbsence')
        database.registerDocumentTable('rbRelationType')
        database.registerDocumentTable('rbScene')
        database.registerDocumentTable('rbService')
        database.registerDocumentTable('rbService_Contents')
        database.registerDocumentTable('rbService_Profile')
        database.registerDocumentTable('rbServiceClass')
        database.registerDocumentTable('rbServiceGroup')
        database.registerDocumentTable('rbServiceSection')
        database.registerDocumentTable('rbServiceType')
        database.registerDocumentTable('rbSocStatusClass')
        database.registerDocumentTable('rbSocStatusType')
        database.registerDocumentTable('rbSpeciality')
        database.registerDocumentTable('rbStatusObservationClientType')
        database.registerDocumentTable('rbStockRecipe')
        database.registerDocumentTable('rbStockRecipe_Item')
        database.registerDocumentTable('rbTariffCategory')
        database.registerDocumentTable('rbTempInvalidBreak')
        database.registerDocumentTable('rbTempInvalidDocument')
        database.registerDocumentTable('rbTempInvalidDuplicateReason')
        database.registerDocumentTable('rbTempInvalidExtraReason')
        database.registerDocumentTable('rbTempInvalidReason')
        database.registerDocumentTable('rbTempInvalidRegime')
        database.registerDocumentTable('rbTempInvalidResult')
        database.registerDocumentTable('rbTest')
        database.registerDocumentTable('rbTest_AnalogTest')
        database.registerDocumentTable('rbTestGroup')
        database.registerDocumentTable('rbThesaurus')
        database.registerDocumentTable('rbTissueType')
        database.registerDocumentTable('rbTraumaType')
        database.registerDocumentTable('rbUserProfile')
        database.registerDocumentTable('rbUserProfile_Hidden')
        database.registerDocumentTable('rbUserProfile_Right')
        database.registerDocumentTable('rbUserRight')
        database.registerDocumentTable('rbVisitType')
        database.registerDocumentTable('Recommendation')
        database.registerDocumentTable('Recommendation_Action')
        database.registerDocumentTable('Action_Assistant')
        database.registerDocumentTable('DrugFormulary')
        database.registerDocumentTable('DrugRecipe')
        database.registerDocumentTable('DloDrugFormulary')
        database.registerDocumentTable('DloDrugRecipe')

    def getHomeDir(self):
        if not self.homeDir:
            homeDir = os.path.expanduser('~')
            if homeDir == '~':
                homeDir = unicode(QDir.homePath())
            if isinstance(homeDir, str):
                homeDir = unicode(homeDir, locale.getpreferredencoding())
            self.homeDir = homeDir
        return self.homeDir

    def getSaveDir(self):
        self.saveDir = forceString(self.preferences.appPrefs.get('saveDir', QVariant()))
        if not self.saveDir:
            self.saveDir = self.getHomeDir()
        return self.saveDir

    def setSaveDir(self, path):
        saveDir = os.path.dirname(unicode(path))
        if saveDir and self.saveDir != saveDir:
            self.preferences.appPrefs['saveDir'] = QVariant(saveDir)

    def getTemplateDir(self):
        result = forceString(self.preferences.appPrefs.get('templateDir', None))
        if not result:
            result = os.path.join(self.logDir, 'templates')
        return result

    def getTmpDir(self, suffix=''):
        return unicode(tempfile.mkdtemp('','vista-med_%s_'%suffix), locale.getpreferredencoding())

    def removeTmpDir(self, directory):
        shutil.rmtree(directory, True)

    def log(self, title, message, stack=None):
        log(self.logDir, title, message, stack)

    def logException(self, exceptionType, exceptionValue, exceptionTraceback):
        u"""Перехватываем все необработанные исключения в системе.
            1) Пишем в файл с логом
            2) Показываем пользователю окошко с ошибкой
            3) Вызываем системный excepthook (он, в том числе, в stderr пишет)
        """
        title = repr(exceptionType)
        try:
            message = unicode(exceptionValue)
        except UnicodeDecodeError:
            message = str(exceptionValue).decode('utf-8', 'replace')
        stack = traceback.extract_tb(exceptionTraceback)
        self.log(title, message, stack)
        if forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'showErrorMessages', QVariant())):
            try:
                from buildInfo import lastChangedRev, lastChangedDate
            except:
                lastChangedRev = 'unknown'
                lastChangedDate = 'unknown'
            timeString = unicode(QDateTime().currentDateTime().toString(Qt.SystemLocaleDate))
            logString = u'Revision: %s\n(python: %s)\n(Qt: %s)\n%s: %s\n(%s)\n' % (lastChangedRev,
                                                                                   sys.version,
                                                                                   QtCore.qVersion(),
                                                                                   timeString,
                                                                                   title,
                                                                                   message)
            if stack:
                try:
                    logString += ''.join(traceback.format_list(stack)).decode('utf-8') + '\n'
                except:
                    logString += 'stack lost\n'
            widget = self.activeModalWidget() or self.mainWindow
            result = CErrorBox(widget, logString).exec_()
            # Если у нас исключение вызывается по notify модальным окном, то было бы неплохо это модальное окно закрыть
            if result == QtGui.QMessageBox.Abort:
                self.activeModalWidget().reject()

        sys.__excepthook__(exceptionType, exceptionValue.message.decode('utf8'), exceptionTraceback)

    def logCurrentException(self):
        self.logException(*sys.exc_info())

    def msgHandler(self, type, msg):
        if type == 0:    # QtMsgType.QtDebugMsg:
            typeName = 'QtDebugMsg'
        elif type == 1:  # QtMsgType.QtWarningMsg:
            typeName = 'QtWarningMsg'
        elif type == 2:  # QtMsgType.QtCriticalMsg:
            typeName = 'QtCriticalMsg'
        elif type == 3:  # QtFatalMsg
            typeName = 'QtFatalMsg'
        else:
            typeName = 'QtUnknownMsg'

        self.log( typeName, msg, traceback.extract_stack()[:-1])

    def setCurrentUserPassword(self, password):
        db = QtGui.qApp.db
        resultMessageLines = []

        login = self.userInfo.login() if self.userInfo else ''
        resultMessageLines.append(u'Пароль для пользователя: %s' % login)
        if db and db.db.isValid() and self.userId:
            encodedPassword = unicode(password).encode('utf8')
            hashedPassword = hashlib.md5(encodedPassword).hexdigest()
            if self.preferences.dbNewAuthorizationScheme:
                db.query(u'SET PASSWORD = PASSWORD(\'%s\')' % hashedPassword)
            query = db.query('UPDATE Person SET password = \'%s\' WHERE id = %d' % (hashedPassword, self.userId))
            rowsAffected = query.result().numRowsAffected()
            if rowsAffected > 0:
                resultMessageLines.append(u'Был успешно изменен')
            else:
                resultMessageLines.append(u'Не был изменен по неизвестным причинам')
                resultMessageLines.append(u'(количество измененных записей: %d)' % rowsAffected)
        else:
            resultMessageLines.append(u'Не был изменен из-за проблем связи с базой')
        return '\n'.join(resultMessageLines)

    def openDatabase(self, connectionAddInfo = None):
        self.db = None
        connectionInfo = {'driverName' : self.preferences.dbDriverName,
                          'host' : self.preferences.dbServerName,
                          'port' : self.preferences.dbServerPort,
                          'database' : self.preferences.dbDatabaseName,
                          'user' : self.preferences.dbUserName,
                          'password' : self.preferences.dbPassword,
                          'connectionName' : self.connectionName,
                          'compressData' : self.preferences.dbCompressData,
                          'afterConnectFunc' : self.afterConnectToDatabase}

        if isinstance(connectionAddInfo, dict):
            connectionInfo.update(connectionAddInfo)

        self.db = database.connectDataBaseByInfo(connectionInfo)
        self.afterConnectToDatabase()
        self.connect(self.db, SIGNAL('connected()'), self.afterConnectToDatabase)
        self.connect(self.db, SIGNAL('disconnected()'), self.onDatabaseDisconnected)
        self.loadGlobalPreferences()
        self.loadServerDatetimeDiff()
        self.emit(QtCore.SIGNAL('dbConnectionChanged(bool)'), True)
        self.setCurrentClientId(None)
        #FIXME надо ли загружать календарную информацию сразу в момент открытия БД????
        self.calendarInfo.load(self.db)
        self.disableLock = self.disableLockRequested or self.db.db.record('AppLock').count() == 0

    @QtCore.pyqtSlot()
    def afterConnectToDatabase(self):
        if not self.disableLock:
            try:
                self.db.query('CALL getAppLock_prepare()')
            except:
                self.disableLock = True

    def loadGlobalPreferences(self):
        if self.db:
            try:
                recordList = self.db.getRecordList('GlobalPreferences')
            except:
                recordList = []
            self._visibleControledObjectNameList = None
            for record in recordList:
                code  = forceString(record.value('code'))
                value = forceString(record.value('value'))
                self._globalPreferences[code] = value

    def updateGlobalPreference(self, code):
        if self.db:
            value = forceString(self.db.translate('GlobalPreferences', 'code', code, 'value'))
            self._globalPreferences[code] = value

    def checkGlobalPreference(self, code, chkValue):
        value = self._globalPreferences.get(code, None)
        if value:
            return unicode(value).lower() == unicode(chkValue).lower()
        return False

    def getGlobalPreference(self, code):
        value = self._globalPreferences.get(code, None)
        return unicode(value).lower() if value else None

    def loadServerDatetimeDiff(self):
        self.datetimeDiff = 0
        if self.db:
            query = self.db.query('SELECT CURRENT_TIMESTAMP')
            if query.first():
                serverDatetime = forceDateTime(query.record().value(0))
                systemDatetime = QtCore.QDateTime.currentDateTime()
                self.datetimeDiff = systemDatetime.secsTo(serverDatetime)

    def getDatetimeDiff(self):
        return self.datetimeDiff

    def closeDatabase(self):
        if self.db:
            # Подчистка блокировок при выходе из приложения
            if not self.disableLock and self.db.db.isOpen():
                try:
                    self.db.query('CALL CleanupLocks()', True)
                except:
                    pass
            self.db.close()
            self.db = None

    @pyqtSlot()
    def onDatabaseDisconnected(self):
        self.setCurrentClientId(None)
        self.setUserId(None, False)

        self._globalPreferences.clear()
        self.accountingSystem = None

        self.emit(QtCore.SIGNAL('dbConnectionChanged(bool)'), False)

    def call(self, widget, func, params = ()):
        try:
            return True, func(*params)
        except IOError, e:
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical(widget,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
        return False, None

    def callWithWaitCursor(self, widget, func, *params, **kwparams):
        self.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
        try:
            return func(*params, **kwparams)
        finally:
            self.restoreOverrideCursor()

    def execProgram(self, cmd, args=None, env=None):
        if not args:
            args = []
        if not env:
            env = {}
        cmd = cmd.strip()
        self.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
        try:
            process = QProcess()
            if env:
                outEnv = QProcess.systemEnvironment()
                for key, value in env.iteritems():
                    outEnv.append("%s=%s"%(key, value))
                process.setEnvironment(outEnv)

            homePath = unicode(QDir.toNativeSeparators(QDir.homePath()))
            programFileName = os.path.basename(splitShellCommand(cmd)[0])
            pidFileName = os.path.join(homePath, programFileName + '.pid')
            checkByPIDFile = not os.path.exists(pidFileName)

            if args:
                outArgs = [arg if isinstance(arg, basestring) else unicode(arg) for arg in args]
                process.start(cmd, outArgs)
            else:
                process.start(cmd)
            stepTimeOut = 200

            for i in xrange(100):
                checkByPIDFile = checkByPIDFile and os.path.exists(pidFileName)
                started = process.waitForStarted(stepTimeOut) if not checkByPIDFile else True
                self.processEvents()
                if started:
                    break
            if started:
                while process.state() == QProcess.Running and not process.waitForFinished(stepTimeOut):
                    self.processEvents()
                    if checkByPIDFile and not os.path.exists(pidFileName):
                        break
            return (started, QProcess.UnknownError, 0) if checkByPIDFile \
                                                       else started, process.error(), process.exitCode()
        finally:
            self.restoreOverrideCursor()

    def editDocument(self,  textDocument):
        tmpDir = QtGui.qApp.getTmpDir('edit')
        try:
            fileName = os.path.join(tmpDir, 'document.html')
            txt = textDocument.toHtml(QByteArray('utf-8'))
            file = codecs.open(unicode(fileName), encoding='utf-8', mode='w+')
            file.write(unicode(txt))
            file.close()
            cmdLine = u'"%s" "%s"' % (self.documentEditor(), fileName)
            started = self.execProgram(cmdLine)[0]
            if started:
                for enc in ['utf-8', 'cp1251']:
                    try:
                        file = codecs.open(fileName, encoding=enc, mode='r')
                        txt = file.read()
                        file.close()
                        textDocument.setHtml(txt)
                        return True
                    except:
                        pass
                QtGui.QMessageBox.critical(None,
                                       u'Внимание!',
                                       u'Не удалось загрузить "%s" после' % fileName,
                                       QtGui.QMessageBox.Close)
            else:
                QtGui.QMessageBox.critical(None,
                                       u'Внимание!',
                                       u'Не удалось запустить "%s"' % self.documentEditor(),
                                       QtGui.QMessageBox.Close)
        finally:
            QtGui.qApp.removeTmpDir(tmpDir)
        return False

    def startProgressBar(self, steps, format='%v/%m'):
        progressBar = self.mainWindow.getProgressBar()
        progressBar.setFormat(format)
        progressBar.setMinimum(0)
        progressBar.setMaximum(steps)
        progressBar.setValue(0)

    def stepProgressBar(self, step=1):
        progressBar = self.mainWindow.getProgressBar()
        progressBar.setValue(progressBar.value()+step)

    def stopProgressBar(self):
        self.mainWindow.hideProgressBar()

    def demoModePosible(self):
        try:
            tableUser = self.db.table(tblUser)
            record = self.db.getRecordEx(tableUser, ['password = \'\' AS passwordIsEmpty', usrRetired], tableUser[usrLogin].eq(demoUserName))
            return not record or (not forceBool(record.value('passwordIsEmpty')) and not forceBool(record.value(usrRetired)))
        except:
            pass
        return False

    def isNurse(self):
        """Возвращает True, если текущий пользователь - медсестра(-брат)"""
        return self._isNurseUser

    def nurseOwnerId(self):
        """Возвращает ID врача, привязанного к текущему пользователю-медсестре"""
        return self._nurseOwnerId

    def getDrId(self):
        """Если работает медстестра, возвращает id врача, привязанного к медсестре, иначе либо - id текущего пользователя"""
        # если текущий пользователь - медсестра и указан врач, с которым она работает
        if self.isNurse() and self.nurseOwnerId():
            # то вернуть ID врача, а не медсестры
            return self.nurseOwnerId()
        else:
            # иначе, вернуть id текущего пользователя
            return self.userId

    def personAddingCommentState(self, personId):
        isNeedAddComment = False
        commentText = u''
        try:
            record = self.db.getRecord(self.db.table('Person'),  ('addComment',  'commentText'),  personId)
            isNeedAddComment = forceBool(record.value('addComment'))
            if isNeedAddComment:
                commentText = forceString(record.value('commentText'))
        finally:
            return isNeedAddComment, commentText

    def isNeedAddComent(self):
        return self._isNeedAddComment

    def personCommentText(self):
        return self._personCommentText

    def drOrUserSpecialityId(self):
        """ID специальности текущего пользователя или врача, с которым работает текущий пользователь-медсестра"""
        if self.isNurse():
            return self._nurseOwnerSpecialityId
        return self.userSpecialityId

    def checkNurseAndBindToDr(self, postId):
        u""" Выявление медсестры и привязка ее к врачу
        Проверяет, содержит ли наименование указанной должности слова сестра или брат
        и, если содержит, выдает окно с выбором врача для привязки к текущему ползователю-медсестре
        @param postId: ID должности текущего пользователя
        """
        if not postId:
            return
        if not self.isBindNurseWithDoctor():
            return
        record = self.db.getRecord('rbPost', 'name', postId)
        if record:
            name = forceString(record.value('name'))
            if name.find(u'сестра') != -1 or name.find(u'брат') != -1:
                self._isNurseUser = True
                # создание диалогового окна со списком врачей для выбора
                # можно вынести в отдельную функцию/ui-файл
                dlg = QDialog(self.mainWindow)
                dlg.setWindowTitle(u'Выберите врача')
                vlayout = QVBoxLayout()
                btnBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                dlg.connect(btnBox, SIGNAL('accepted()'), dlg.accept)
                dlg.connect(btnBox, SIGNAL('rejected()'), dlg.reject)
                personComboBox = CPersonComboBox(dlg)
                personComboBox.setCurrentIndex(0)
                vlayout.addWidget(personComboBox)
                vlayout.addWidget(btnBox)
                dlg.setLayout(vlayout)
                # конец создания диалога
                if dlg.exec_():
                    ownId = personComboBox.getValue()
                    if ownId:
                        self._nurseOwnerId = ownId
                        self._nurseOwnerSpecialityId = forceRef(self.db.translate('Person', 'id', ownId, 'speciality_id'))

    def setUserId(self, userId, demoMode = False):
        self.userId = userId
        record = self.db.getRecord('Person', ['speciality_id', 'orgStructure_id', 'post_id'], userId) if userId else None
        if record:
            self.userSpecialityId = forceRef(record.value('speciality_id'))
            self.userOrgStructureId = forceRef(record.value('orgStructure_id'))
            self.userPostId = forceRef(record.value('post_id'))
        else:
            self.userSpecialityId = None
            self.userOrgStructureId = None
            self.userPostId = None
        self.demoMode = demoMode
        if demoMode:
            self.userInfo = CDemoUserInfo(userId)
        else:
            if userId:
                self.userInfo = CUserInfo(userId)
            else :
                self.userInfo = None
        self.checkNurseAndBindToDr(self.userPostId)
        self.emit(QtCore.SIGNAL('currentUserIdChanged()'))

    def isUserAvailableJobTypeId(self, jobTypeId):
        return self.userInfo.isAvailableJobTypeId(jobTypeId)

    def isUserAvailableJobType(self, jobTypeCode):
        return self.userInfo.isAvailableJobType(jobTypeCode)

    def userAvailableJobTypeIdList(self):
        return self.userInfo.availableJobTypeIdList()

    def userName(self):
        if self.userInfo:
            orgId = self.currentOrgId()
            orgInfo = getOrganisationInfo(orgId)
            if not orgInfo:
                QtGui.qApp.preferences.appPrefs['orgId'] = QVariant()
            shortName = getVal(orgInfo, 'shortName', u'ЛПУ в настройках не указано!')
            return u'%s (%s) %s' % (self.userInfo.name(), self.userInfo.login(), shortName)
        else:
            return ''

    def userHasRight(self, userRight):
        return self.userInfo is not None and self.userInfo.hasRight(userRight)

    def userHasProfile(self, profileId):
        return self.userInfo is not None and self.userInfo.hasProfile(profileId)

    def isObjectHidden(self, objectName):
        return self.userInfo.isObjectHidden(objectName) if self.userInfo else False

    def userHasAnyRight(self, rights):
        return self.userInfo is not None and self.userInfo.hasAnyRight(rights)

    def currentOrgId(self):
        return forceRef(getVal(QtGui.qApp.preferences.appPrefs, 'orgId', QVariant()))

    def currentLpuList(self):
        recOrg = self.db.getRecordEx('Organisation', '*', 'id=%s' % QtGui.qApp.currentOrgId())
        if forceInt(recOrg.value('head_id')):
            idList = self.db.getIdList('Organisation', 'id', 'head_id=%s' % forceInt(recOrg.value('head_id')))
            if idList:
                idList.append(QtGui.qApp.currentOrgId())
            else:
                idList = [QtGui.qApp.currentOrgId()]
            return idList
        else:
            idList =  self.db.getIdList('Organisation', 'id', 'head_id=%s' % QtGui.qApp.currentOrgId())
            if idList:
                idList.append(QtGui.qApp.currentOrgId())
            else:
                idList = [QtGui.qApp.currentOrgId()]
            return idList


    def currentOrgInfis(self):
        return forceString(QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode'))

    def currentOrgStructureInfis(self):
        return forceString(self.db.translateEx('OrgStructure', 'id', self.currentOrgId(), 'infisCode'))

    def currentOrgStructureId(self):
        return forceRef(getVal(QtGui.qApp.preferences.appPrefs, 'orgStructureId', QVariant()))

    def filterPaymentByOrgStructure(self):
        return forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'filterPaymentByOrgStructure', QVariant()))

    def setCurrentClientId(self, id):
        if self._currentClientId != id:
            self._currentClientId = id
            self.emit(QtCore.SIGNAL('currentClientIdChanged()'))

    def emitCurrentClientInfoChanged(self):
        self.emit(QtCore.SIGNAL('currentClientInfoChanged()'))

    def currentClientId(self):
        return self._currentClientId

    def canFindClient(self):
        return bool(self.mainWindow.registry)

    def findClient(self, clientId):
        if self.mainWindow.registry:
            self.mainWindow.registry.findClient(clientId)

    def identServiceEnabled(self):
        if self._identService is None:
            return forceBool(self.preferences.appPrefs.get('TFCheckPolicy', False))
        else:
            return True

    def identService(self, clientId, firstName, lastName, patrName, sex, birthDate, SNILS = '', policyKind = '', policySerial='', policyNumber='', docTypeId = '', docSerial='', docNumber=''):
        from Exchange.TF78Ident.Service import CTF78IdentService
        from Exchange.TF23Ident.Service import CTF23IdentService
        if self._identService is None:
            url      = forceString(self.preferences.appPrefs.get('TFCPUrl', ''))
            login    = forceString(self.preferences.appPrefs.get('TFCPLogin', ''))
            password = forceString(self.preferences.appPrefs.get('TFCPPassword', ''))
            if self.defaultKLADR().startswith('23'):
                self._identService = CTF23IdentService(url, login, password)
            else:
                self._identService = CTF78IdentService(url, login, password)
        try:
            if self.defaultKLADR().startswith('23'):
                db = QtGui.qApp.db
                codeMO = forceStringEx(db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode'))
                policyType = forceStringEx(db.translate('rbPolicyKind', 'id', policyKind, 'regionalCode'))
                docType = forceStringEx(db.translate('rbDocumentType', 'id', docTypeId, 'regionalCode'))
                return self.callWithWaitCursor(self, self._identService.getPolicy, codeMO, clientId, firstName, lastName, patrName, sex, birthDate, SNILS, policyType, policySerial, policyNumber, docType, docSerial, docNumber)
            else:
                return self.callWithWaitCursor(self, self._identService.getPolicy, firstName, lastName, patrName, sex, birthDate, policySerial, policyNumber, docSerial, docNumber)
        except SocketError:
            self.logCurrentException()
            raise CSoapException(u"Ошибка! Нет связи с сервером ТФОМС")
        except:
            self.logCurrentException()
            raise CSoapException(u"Неизвестная ошибка при подключении к серверу ТФОМС")

    def requestNewEvent(self, clientId, isAmb=True):
        if self.mainWindow.registry:
            self.mainWindow.registry.findClient(clientId)
            self.mainWindow.registry.requestNewEvent(isAmb=isAmb)

    def canFindEvent(self):
        return bool(self.mainWindow.registry)

    def findEvent(self, id):
        if self.mainWindow.registry:
            self.mainWindow.registry.findEvent(id)

    def setEventList(self, idList):
        if self.mainWindow.registry:
            self.mainWindow.registry.setEventList(idList)

    def addMruEvent(self, eventId, descr):
        self.mainWindow.addMruEvent(eventId, descr)

    def clearPreferencesCache(self):
        self._defaultKLADR = None
        self._provinceKLADR = None
        self._averageDuration = None
        self._globalAverageDuration = None
        self._highlightRedDate = None
        self._highlightInvalidDate = None
        self._identService = None
        self.accountingSystem = None
        self.loadGlobalPreferences()

    def defaultKLADR(self):
        u"""код КЛАДР по умолчанию"""
        if self._defaultKLADR is None:
            self._defaultKLADR = forceString(self.preferences.appPrefs.get('defaultKLADR', ''))
            if not self._defaultKLADR:
                self._defaultKLADR = '7800000000000'
        return self._defaultKLADR

    def provinceKLADR(self):
        """областной код КЛАДР по умолчанию"""
        if self._provinceKLADR is None:
            self._provinceKLADR = forceString(self.preferences.appPrefs.get('provinceKLADR', ''))
            if not self._provinceKLADR:
                self._provinceKLADR = getProvinceKLADRCode(self.defaultKLADR())
        return self._provinceKLADR

    def isKrasnodarRegion(self):
        return self.defaultKLADR().startswith('23')

    def isSPbRegion(self):
        return self.defaultKLADR().startswith('78')

    def getGlobalPreferenceAverangeDuration(self):
        if self._globalAverageDuration is None:
            self._averageDuration = self._globalPreferences.get('71', DefaultAverageDuration)
        return self._globalAverageDuration

    def averageDuration(self):
        """средняя длительность заболевания"""
        if self._averageDuration is None:
            self._averageDuration = forceInt(self.preferences.appPrefs.get('averageDuration', QVariant(DefaultAverageDuration)))
        return self._averageDuration

    def isAddressOnlyByKLADR(self):
        return forceBool(self.preferences.appPrefs.get('addressOnlyByKLADR', 0))

    def checkDiagChange(self):
        """Возвращает возможность изменения диагноза в случае наличия счёта
        0: изменение запрещено
        1: изменение возможно, требуется подтверждение
        2: изменение разрешено
        """
        return forceInt(self.preferences.appPrefs.get('checkDiagChange', 0))

    def checkActionChange(self):
        """Возвращает возможность изменения действия в случае наличия счёта
        0: изменение запрещено
        1: изменение возможно, требуется подтверждение
        2: изменение разрешено
        """
        return forceInt(self.preferences.appPrefs.get('checkActionChange', 0))

    def tempInvalidDoctype(self):
        """Возвращает код документа временной нетрудоспособности"""
        return forceString(self.preferences.appPrefs.get('tempInvalidDoctype', ''))

    def tempInvalidReason(self):
        """возвращает код причины временной нетрудоспособности"""
        return forceString(self.preferences.appPrefs.get('tempInvalidReason', ''))

    def labelPrinter(self):
        printerName = forceString(self.preferences.appPrefs.get('labelPrinter', ''))
        if 'QPrinterInfo' in QtGui.__dict__: # work-around for current version of pyqt in ubuntu 8.04
            printerInfoList = [ pi for pi in  QtGui.QPrinterInfo.availablePrinters() if pi.printerName() == printerName ]
        else:
            printerInfoList = []
        if printerInfoList:
            return QtGui.QPrinter(printerInfoList[0], QtGui.QPrinter.HighResolution)
        else:
            return None

    def doubleClickQueuePerson(self):
        """изменение двойного щелчка в листе предварительной записи врача
        0: изменить жалобы/примечания
        1: перейти в картотеку
        2: новое обращение
        """
        return forceInt(self.preferences.appPrefs.get('doubleClickQueuePerson', 0))

    def doubleClickQueuing(self):
        """изменение двойного щелчка в листе предварительной записи врача
        0: ничего не выводить
        1: выводить номерок
        2: выводить жалобу
        3: выводить номерок и жалобу
        """
        return forceInt(self.preferences.appPrefs.get('doubleClickQueuing', 1))

    def doubleClickQueueClient(self):
        """изменение двойного щелчка в листе предварительной записи пациента
        0: Нет действия
        1: новое обращение
        2: изменить жалобы/примечания
        3: напечатать приглашение
        4: перейти в график
        """
        return forceInt(self.preferences.appPrefs.get('doubleClickQueueClient', 0))

    def doubleClickQueueFreeOrder(self):
        """изменение двойного щелчка в списке свободных номерков
        0: Нет действия
        1: Поставить в очередь
        2: Выполнить бронирование
        """
        return forceInt(self.preferences.appPrefs.get('doubleClickQueueFreeOrder', 0))

    def ambulanceUserCheckable(self):
        return forceBool(QtGui.qApp.preferences.appPrefs.get('ambulanceUserCheckable', False))

    def f025DefaultPrimacy(self):
        return forceInt(QtGui.qApp.preferences.appPrefs.get('f025DefaultPrimacy', 0))

    def isAutoPrimacy(self):
        return not forceBool(QtGui.qApp.preferences.appPrefs.get('autoPrimacy', False))

    def openEventsIfDuplicating(self):
        return forceBool(QtGui.qApp.preferences.appPrefs.get('openEventsIfDuplicating', True))

    def highlightRedDate(self):
        if self._highlightRedDate is None:
            self._highlightRedDate = forceBool(QtGui.qApp.preferences.appPrefs.get('highlightRedDate', False))
        return self._highlightRedDate

    def highlightInvalidDate(self):
        if self._highlightInvalidDate is None:
            self._highlightInvalidDate = forceBool(QtGui.qApp.preferences.appPrefs.get('highlightInvalidDate', False))
        return self._highlightInvalidDate

    def documentEditor(self):
        return forceString(QtGui.qApp.preferences.appPrefs.get('documentEditor', ''))

    def cashBox(self):
        """номер кассы"""
        return forceString(self.preferences.appPrefs.get('cashBox', ''))

    def defaultAccountingSystem(self):
        if self.accountingSystem is None:
            id = None
            name = None
            code = self.getGlobalPreference('3')
            if code is not None:
                table = self.db.table('rbAccountingSystem')
                record = self.db.getRecordEx(table, ['id', 'name'], table['code'].eq(code))
                if record:
                    id = forceRef(record.value('id'))
                    name = forceString(record.value('name'))
            self.accountingSystem = id, name
        return self.accountingSystem

    def defaultAccountingSystemId(self):
        return self.defaultAccountingSystem()[0]

    def defaultAccountingSystemName(self):
        return self.defaultAccountingSystem()[1]

    def defaultIsManualSwitchDiagnosis(self):
        return self.checkGlobalPreference('1', u'в ручную')

    def defaultMorphologyMKBIsVisible(self):
        return self.checkGlobalPreference('2', u'да')

    def defaultHospitalBedProfileByMoving(self):
        # Учитывать профиль койки по движению:
        # нет: по койке
        # да:  по движению
        return self.checkGlobalPreference('5', u'да')

    def defaultNeedPreCreateEventPerson(self):
        # необходимость контроля ответственного врача в диалоге 'новое обращение'
        return self.checkGlobalPreference('6', u'да')

    def defaultRegProbsWhithoutTissueJournal(self):
        return self.checkGlobalPreference('42', u'да')

    def isTNMSVisible(self):
        return self.checkGlobalPreference('7', u'да')

    def isStrictAttachCheckOnEventCreation(self):
        return self.checkGlobalPreference('8', u'да')

    def defaultHospitalBedFinanceByMoving(self):
        # Глобальная настройка для определения правила учета источника финансирования в стац. мониторе:
        # по событию
        # по движению
        # по движению или событию
        return self.checkGlobalPreferenceHospitalBedFinance('9')

    def checkGlobalPreferenceHospitalBedFinance(self, code):
        checkGlobalPreferenceList = {u'по событию':0, u'по движению':1, u'по движению или событию':2}
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
        checkGlobalPreferenceList = {u'Внешняя ИС':0, u'Вся ИС':1}
        value = self._globalPreferences.get(code, None)
        if value:
            return checkGlobalPreferenceList.get(unicode(value), None)
        return None

    def isBindNurseWithDoctor(self):
        """
            Atronah for issue 353:
            Проверка на необходимость делать привязку медсестры к врачу.
        """
        return self.checkGlobalPreference('13', u'да')

    def isSeparateStaffFromPatient(self):
        return self.checkGlobalPreference('14', u'да')

    def isCheckOnlyClientNameAndBirthdateAndSex(self):
        return self.checkGlobalPreference('15', u'да')

    def getDiscountParams(self):
        doscountPreferencesCode = '16'
        result = (0, 0, 0, 0, 0, 0, 0, [])
        discountParams = self.getGlobalPreference(doscountPreferencesCode)

        if discountParams is None:
            return result

        if isinstance(discountParams, basestring):
            rePattern = r'<(\d):(\d{1,3})%;(\d)-(\d):(\d{1,3})%;>(\d):(\d{1,3})%;'
            rexp = re.compile(rePattern)
            #поиск выражения вида "<A:B%;C-D:E%;>F:J%"
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
            result = (lowThan, lowDiscount, leftBound, rightBound, middleDiscount, highThan, highDiscount, relativeTypeCodeList)
            self._globalPreferences[doscountPreferencesCode] = result

        elif isinstance(discountParams, tuple):
            return discountParams

        return result

    def isCheckPolisEndDateAndNumberEnabled(self):
        return self.checkGlobalPreference('17',  u'да')

    def isButtonBoxAtTopWindow(self):
        return self.checkGlobalPreference('18',  u'да')

    def hideLeaversBeforeCurrentYearPatients(self):
        return self.checkGlobalPreference('20', u'до начала текущего года') or self.checkGlobalPreference('20', u'да')

    def hideAllLeavers(self):
        return self.checkGlobalPreference('20', u'всех')

    # Ввод направления при создании обращения из любого места, кроме "Графика"
    def isReferralRequired(self):
        return self.checkGlobalPreference('21', u'да') or self.checkGlobalPreference('21', u'1') or self.checkGlobalPreference('21', u'2')

    # Ввод направления при создании обращения из "Графика"
    def isReferralRequiredInPreRecord(self):
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
        # TODO: Сейчас при создании нового обращения фокус ставится на комбобокс с ЛПУ. Неловкое движение - и он изменяется, причем незаметно.
        # Пока решили перемещать курсор на Тип обращения, но Песочке это неудобно. К тому же, есть вероятность, что ЛПУ может изменяться само по себе
        # независимо от манипуляций с комбобоксом. В дальнейшем надо убедиться, что подобное поведение исключено и изменить назначение данной настройки -
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
        return QTime.fromString(stringTime,
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

        eventTypeCodes = filterDD[delimInd+1:]
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

    def isHideClinicalResearh(self):
        return self.checkGlobalPreference('68', u'да')

    def isDisregardHospitalBedOrgStructure(self):
        return self.checkGlobalPreference('69', u'да')

    def isRequiredLoginAndPass(self):
        return self.checkGlobalPreference('70', u'нет')

    def isOncologyForm90Enabled(self):
        return self.checkGlobalPreference('71', u'да') and QtGui.qApp.db.getCount('ActionType', where="flatCode = 'f90' AND deleted = 0")

    def isFilterJobTicketByOrgStructEnabled(self):
        return self.checkGlobalPreference('72', u'да')

    def isSortAnalizesByDirectionDateAndShowImportDate(self):
        return self.checkGlobalPreference('73', u'да')

    def isAllowedIntersectionOfTime(self):
        return self.checkGlobalPreference('74', u'да')

    def getContingentDDAgeSelectors(self):
        return self._contingentDDAgeSelectors

    def getContingentDDEventTypeCodes(self):
        return self._contingentDDEventTypeCodes

    def region(self):
        region = self.globalRegion()
        if not region:
            region = self.defaultKLADR()[:2]
        return region

    def isDisplayStaff(self, parentForMessageBox = None):
        result = True
        if self.isSeparateStaffFromPatient():
            if not self.userHasRight(urSeeStaff):
                result = False
                if parentForMessageBox:
                    QMessageBox.warning(parentForMessageBox,
                                        u'Недостаточно прав',
                                        u'У вас нет прав для работы с сотрудниками',
                                        QtGui.QMessageBox.Ok,
                                        QtGui.QMessageBox.Ok)
        return result

    def setJTR(self, jtr):
        self.currentJTR = jtr # JobTicketReserve

    def isReservedJobTicket(self, id):
        if self.currentJTR:
            return self.currentJTR.isReservedJobTicket(id)
        else:
            return False

    def addJobTicketReservation(self, id, personId, quotaId=None):
        if self.currentJTR:
            return self.currentJTR.addJobTicketReservation(id, personId, quotaId)
        else:
            return False

    def delJobTicketReservation(self, id, checkReservation=True):
        if self.currentJTR:
            return self.currentJTR.delJobTicketReservation(id, checkReservation)
        else:
            return False

    def getReservedJobTickets(self):
        if self.currentJTR:
            return self.currentJTR.getReservedJobTickets()
        else:
            return []


# noinspection PyUnresolvedReferences
class CS11MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    __pyqtSignals__ = ('goToNextPatient()',
                       'nonePatient()',
                       'startPatient()')
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.initDockResources()
        self.initDockFreeQueue()
        self.initDockChessboardQueue()
        self.initDockDiagnosis()
        self.initDockOpenedEvents()
        self.setupUi(self)
        self.loadModules()
        self.setCorner(Qt.TopLeftCorner,    Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)
        for dock in [self.dockResources, self.dockChessboardQueue, self.dockFreeQueue, self.dockDiagnosis, self.dockOpenedEvents]:
            self.menuPreferences.addAction(dock.toggleViewAction())
            dock.loadDialogPreferences()
        self.setCentralWidget(None)
        self.centralWidget = None
        self.centralWidget = QtGui.QWorkspace()
        self.centralWidget.setObjectName("centralWidget")
        self.setCentralWidget(self.centralWidget)
        self.prepareStatusBar()
        self.registry = None
        self.deferredQueue = None
        self.updateActionsState()
        self.setUserName('')
        self.addExportToDbfAction()
        self.mruEventList = []
        self.mruEventListChanged = False
        self.loadPreferences()

    def addExportToDbfAction(self):
        self.actExportToDbf = QtGui.QAction(self)
        self.actExportToDbf .setText(u'Экспорт операций')
        self.mnuExport.addAction(self.actExportToDbf)
        self.connect(self.actExportToDbf, QtCore.SIGNAL('triggered()'), self.on_actExportToDbf_triggered)

    def initDockResources(self):
        self.dockResources = CResourcesDockWidget(self)
        self.dockResources.setObjectName('dockResources')
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockResources)

    def initDockFreeQueue(self):
        self.dockFreeQueue = CFreeQueueDockWidget(self)
        self.dockFreeQueue.setObjectName('dockFreeQueue')
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockFreeQueue)

    def initDockChessboardQueue(self):
        from Registry.ChessboardQueueDock import CChessboardQueueDockWidget
        self.dockChessboardQueue = CChessboardQueueDockWidget(self)
        self.dockChessboardQueue.setObjectName('dockChessboardQueue')
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockChessboardQueue)

    def initDockDiagnosis(self):
        self.dockDiagnosis = CDiagnosisDockWidget(self)
        self.dockDiagnosis.setObjectName('dockDiagnosis')
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockDiagnosis)

    def initDockOpenedEvents(self):
        self.dockOpenedEvents = COpenedEventsDockWidget(self)
        self.dockOpenedEvents.setObjectName('dockOpenedEvents')
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockOpenedEvents)

    # Загрузка доступных модулей.
    # atronah: пока работа с модулями не реализована и функция нужна только для работы мдоуля сокрытия интерфейса.
    def loadModules(self):
        def registerAction(action, manager, nameParts=None):
            if not nameParts:
                nameParts = []
            if action.isSeparator():
                return

            actionMenu = action.menu()
            objectName = forceString(actionMenu.objectName() if actionMenu else action.objectName())
            objectText = forceString(actionMenu.title() if actionMenu else action.text()).replace('&', '')
            if actionMenu:
                for subAction in actionMenu.actions():
                    registerAction(subAction, manager, nameParts + [objectName])

            manager.registerObject(fullName=u'.'.join(nameParts + [objectName]),
                                   title=objectText)
        # end of sub-function

        manager = CVisibleStateManager()
        manager.registerObject(fullName = self.menuBar.objectName(),
                               title = u'Главное меню')
        for menuBlock in self.menuBar.children():
            if not isinstance(menuBlock, QMenu):
                continue

            if forceString(menuBlock.objectName()) in ['menuFile', 'menuHelp']:
                continue

            registerAction(menuBlock.menuAction(), manager, [forceString(self.menuBar.objectName())])

        # инициализация данных по настройки скрываемости
        from Registry.ClientEditDialog import CClientEditDialog
        from Events.EventEditDialog import CEventEditDialog
        from Events.PreCreateEventDialog import CPreCreateEventDialog
        from RefBooks.Person import CRBPersonEditor
        manager.registerModuleClass(CClientEditDialog)
        manager.registerModuleClass(CHospitalBedsDialog)
        manager.registerModuleClass(CEventEditDialog)
        manager.registerModuleClass(CPreCreateEventDialog)
        manager.registerModuleClass(CRegistryWindow)
        manager.registerModuleClass(CRBPersonEditor)

        #atronah: используется для генерации контента статьи вики по скрываемым виджетам

    def prepareStatusBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setMaximumWidth(200)
        self.progressBar.setMaximumHeight(self.statusBar.height()/2)
        self.progressBarVisible = False

    def closeEvent(self, event):
        self.dockResources.saveDialogPreferences()
        if self.dockFreeQueue:
            self.dockFreeQueue.saveDialogPreferences()
        self.dockDiagnosis.saveDialogPreferences()
        self.dockOpenedEvents.saveDialogPreferences()
        self.savePreferences()
        self.centralWidget.closeAllWindows()
        Logger.logoutInClient()
        QtGui.QMainWindow.closeEvent(self, event)

    def loadPreferences(self):
        preferences = getPref(QtGui.qApp.preferences.windowPrefs, self.objectName(), {})
        geometry = getPref(preferences, 'geometry', None)
        if type(geometry) == QVariant and geometry.type() == QVariant.ByteArray and not geometry.isNull():
            self.restoreGeometry(geometry.toByteArray())
        state = getPref(preferences, 'state', None)
        if type(state) == QVariant and state.type() == QVariant.ByteArray and not geometry.isNull():
            self.restoreState(state.toByteArray())

    def savePreferences(self):
        preferences = {}
        setPref(preferences,'geometry',QVariant(self.saveGeometry()))
        setPref(preferences,'state', QVariant(self.saveState()))
        setPref(QtGui.qApp.preferences.windowPrefs, self.objectName(), preferences)

    def updateActionsState(self):
        notImplemented = False
        app = QtGui.qApp
        loggedIn = bool(app.db) and (app.demoMode or app.userId != None)
        orgIdSet = loggedIn and bool(app.currentOrgId())
        isAdmin      = loggedIn and app.userHasRight(urAdmin)
        isAccountant = orgIdSet and (app.userHasRight(urAccessAccountInfo) or isAdmin)
        isTimekeeper = orgIdSet and (app.userHasRight(urAccessTimeLine) or isAdmin)
        isBlankskeeper = orgIdSet and (app.userHasRight(urAccessBlanks) or isAdmin)
        isRefAdmin   = loggedIn and (app.userHasRight(urAccessRefBooks) or isAdmin)
        isEmergencyRefAdmin = loggedIn and (isRefAdmin or app.userHasRight(urAccessRefEmergency))
        isFeedRefAdmin = loggedIn and (isRefAdmin or app.userHasRight(urAccessRefFeed))
        isMedicalRefAdmin = loggedIn and (isRefAdmin or app.userHasRight(urAccessRefMedical))
        isClassificatorRefAdmin = loggedIn and (isRefAdmin or app.userHasRight(urAccessRefClassificators))
        exchangeEnabled = orgIdSet and (app.userHasRight(urAccessExchange) or isAdmin)
        personalAnalysisEnabled = orgIdSet and (app.userHasRight(urAccessAnalysisPersonal)
                                                            or app.userHasRight(urAccessAnalysis) or isAdmin)
        subStructAnalysisEnabled = orgIdSet and (app.userHasRight(urAccessAnalysisSubStruct)
                                                            or app.userHasRight(urAccessAnalysis) or isAdmin)

        if app.userId:
            menuBarName = forceString(self.menuBar.objectName())
            forProcessingList = [(self.menuBar.actions(), [menuBarName])]
            hiddenObjectNames = [name.split('.')[-1] for name in CVisibleStateManager().model().itemNameList(parentObjectName = menuBarName)]
            while forProcessingList:
                actions, nameParts = forProcessingList.pop(0)
                for action in actions:
                    actionMenu = action.menu()
                    objectName = forceString(actionMenu.objectName() if actionMenu else action.objectName())

                    if objectName in ['menuFile', 'menuHelp']:
                        continue

                    if objectName not in hiddenObjectNames:
                        continue

                    if app.isObjectHidden('.'.join(nameParts + [objectName])):
                        action.setVisible(False)
                    else:
                        action.setVisible(True)
                        if actionMenu:
                            forProcessingList.append((actionMenu.actions(), nameParts + [objectName]))





        # Меню Сессия
        self.actLogin.setEnabled(not loggedIn)
        self.actLogout.setEnabled(loggedIn)
        self.actQuit.setEnabled(True)

        # Меню Работа
        self.actRegistry.setEnabled(orgIdSet and (app.userHasRight(urAccessRegistry) or isAdmin))
        self.actDeferredQueue.setEnabled(orgIdSet and app.userHasAnyRight([urAddDeferredQueueItems, urEditDeferredQueueItems]))
        self.actTimeline.setEnabled(isTimekeeper)
        self.actFormRegistration.setEnabled(isBlankskeeper)
        self.actHospitalBeds.setEnabled(orgIdSet and (app.userHasRight(urAccessHospitalBeds) or isAdmin))
        self.actJobsPlanning.setEnabled(orgIdSet and (app.userHasRight(urAccessJobsPlanning) or isAdmin))
        self.actJobsOperating.setEnabled(orgIdSet and (app.userHasRight(urAccessJobsOperating) or isAdmin))
        self.actQuoting.setEnabled(app.userHasRight(urAccessQuoting) or
                                   app.userHasRight(urAccessQuotingWatch) or
                                   isAdmin)
        self.actTissueJournal.setEnabled(app.userHasRight(urAccessTissueJournal))
        self.actStockControl.setEnabled(orgIdSet and (app.userHasRight(urAccessStockControl) or isAdmin))
        self.actDiabetRegistry.setEnabled(False)


        # Меню Расчет
        self.mnuAccounting.setEnabled(orgIdSet and (   isAccountant
                                                    or app.userHasAnyRight((urAccessAccounting,
                                                                            urAccessAccountingBudget,
                                                                            urAccessAccountingCMI,
                                                                            urAccessAccountingVMI,
                                                                            urAccessAccountingCash,
                                                                            urAccessAccountingTargeted,
                                                                            urAccessContract,
                                                                            urAccessCashBook
                                                                           )
                                                                          )
                                                   )
                                     )
        self.actAccounting.setEnabled(orgIdSet and (   isAccountant
                                                    or app.userHasAnyRight((urAccessAccounting,
                                                                            urAccessAccountingBudget,
                                                                            urAccessAccountingCMI,
                                                                            urAccessAccountingVMI,
                                                                            urAccessAccountingCash,
                                                                            urAccessAccountingTargeted
                                                                           )
                                                                          )
                                                   )
                                     )
        self.actContract.setEnabled(orgIdSet and (isAccountant or app.userHasRight(urAccessContract)))
        self.actCashBook.setEnabled(orgIdSet and (isAccountant or app.userHasRight(urAccessCashBook)))

        # Меню Обмен
        self.mnuExchange.setEnabled(exchangeEnabled)
        self.actImportSPRSMO.setVisible(QtGui.qApp.preferences.appUserName == u'админ')

        # Меню Анализ
        self.mnuStatReports.setEnabled(subStructAnalysisEnabled)
        self.menu_131.setEnabled(subStructAnalysisEnabled)
        self.actGenRep.setEnabled(subStructAnalysisEnabled)
        self.menu_21.setEnabled(personalAnalysisEnabled)
        self.mnuAccountingAnalysis.setEnabled(personalAnalysisEnabled)
        self.mnuDispObservation.setEnabled(personalAnalysisEnabled)
        self.mnuTempInvalid.setEnabled(personalAnalysisEnabled)
        self.mnuDeath.setEnabled(personalAnalysisEnabled)
        self.mnuContingent.setEnabled(personalAnalysisEnabled)
        self.mnuStationary.setEnabled(personalAnalysisEnabled)
        self.mnuPreRecord.setEnabled(personalAnalysisEnabled)
        self.actReportF39PND.setVisible(QtGui.qApp.isPNDDiagnosisMode())
        self.actReportConstructor.setVisible(app.userHasRight(urAccessReportConstructor))
        # временно скроем этот пункт, до появления какой-то определенности с отчетами по новому питанию
        self.actReportFeedDistribution.setVisible(False)

        # self.actReportVerifiedAction.setVisible(
        #    forceStringEx(
        #        QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode')
        #    ) == u'б15'
        # )

        # Отчёты для Москвы (МСК Б36) видны только в Москве
        reportsForMoscow = [
            self.actReportLeavedMovedDead, self.actReportMovingB36, self.actReportMovingB36Monthly,
            self.actReportMovingRVC, self.actReportStationaryF007, self.actReportBedspaceUsage,
            self.actReportOperationProtocolB36
        ]
        for actReport in reportsForMoscow:
            actReport.setVisible(QtGui.qApp.region() == '77')

        # Меню Справочники
        # Подменю Адреса
        self.menu.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAddress,
                                 urAccessRefAddressKLADR,
                                 urAccessRefAddressAreas
                                ]))
        self.actMilitaryUnits.setEnabled(isRefAdmin or app.userHasAnyRight([urAccessRefAddressKLADR]))
        self.actKLADR.setEnabled(notImplemented)
        self.actAreas.setEnabled(notImplemented)

        # Подменю Персонал
        self.menu_2.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefPerson,
                                 urAccessRefPersonOrgStructure,
                                 urAccessRefPersonRBSpeciality,
                                 urAccessRefPersonRBPost,
                                 urAccessRefPersonRBActivity,
                                 urAccessRefPersonPersonal
                                ]))
        self.actOrgStructure.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefPerson, urAccessRefPersonOrgStructure]))
        self.actRBSpeciality.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefPerson, urAccessRefPersonRBSpeciality]))
        self.actRBPost.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefPerson, urAccessRefPersonRBPost]))
        self.actRBActivity.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefPerson, urAccessRefPersonRBActivity]))
        self.actPersonal.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefPerson, urAccessRefPersonPersonal]))

        # Подменю Скорая помощь
        self.menu_9.setEnabled(isEmergencyRefAdmin or
            app.userHasAnyRight([urAccessRefEmergency]))

        # Подменю Питание
        self.menu_16.setEnabled(isFeedRefAdmin or
            app.userHasAnyRight([urAccessRefFeed]))

        # Подменю Медицинские
        self.menu_3.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical,
                                 urAccessRefMedMKB,
                                 urAccessRefMedMKBSubClass,
                                 urAccessRefMedDiseaseCharacter,
                                 urAccessRefMedDiseaseStage,
                                 urAccessRefMedDiseasePhases,
                                 urAccessRefMedDiagnosisType,
                                 urAccessRefMedTraumaType,
                                 urAccessRefMedHealthGroup,
                                 urAccessRefMedDispanser,
                                 urAccessRefMedResult,
                                 urAccessRefMedTempInvalidReason,
                                 urAccessRefMedTempInvalidDocument,
                                 urAccessRefMedTempInvalidBreak,
                                 urAccessRefMedTempInvalidRegime,
                                 urAccessRefMedTempInvalidResult,
                                 urAccessRefMedComplain,
                                 urAccessRefMedThesaurus,
                                 urAccessRefMedBloodType
                                ]))
        self.actMKB.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedMKB]))
        self.actMKBSubclass.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedMKBSubClass]))
        self.actMKBMorphology.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical]))
        self.actRBDiseaseCharacter.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedDiseaseCharacter]))
        self.actRBDiseaseStage.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedDiseaseStage]))
        self.actRBDiseasePhases.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedDiseasePhases]))
        self.actRBDiagnosisType.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedDiagnosisType]))
        self.actRBTraumaType.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedTraumaType]))
        self.actRBHealthGroup.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedHealthGroup]))
        self.actRBDispanser.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedDispanser]))
        self.actRBResult.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedResult]))
        self.actRBTempInvalidReason.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedTempInvalidReason]))
        self.actRBTempInvalidDocument.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedTempInvalidDocument]))
        self.actRBTempInvalidBreak.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedTempInvalidBreak]))
        self.actRBTempInvalidRegime.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedTempInvalidRegime]))
        self.actRBTempInvalidResult.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedTempInvalidResult]))
        self.actRBTempInvalidDuplicateReason.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedTempInvalidResult]))

        self.actRBComplain.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedComplain]))
        self.actRBThesaurus.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedThesaurus]))
        self.actRBBloodType.setEnabled(isMedicalRefAdmin or
            app.userHasAnyRight([urAccessRefMedical, urAccessRefMedBloodType]))
        self.actRBImageMap.setEnabled(isMedicalRefAdmin or app.userHasAnyRight([urAccessRefMedical,]))

        # Подменю Классификаторы
        self.menu_4.setEnabled(isClassificatorRefAdmin
            or app.userHasAnyRight([urAccessRefClOKPF,
                                    urAccessRefClOKFS,
                                    urAccessRefClHurtType,
                                    urAccessRefClHurtFactorType,
                                    urAccessRefClUnit,
                                   ]))
        self.actRBOKPF.setEnabled(isClassificatorRefAdmin or app.userHasRight(urAccessRefClOKPF))
        self.actRBOKFS.setEnabled(isClassificatorRefAdmin or app.userHasRight(urAccessRefClOKFS))
        self.actRBHurtType.setEnabled(isClassificatorRefAdmin or app.userHasRight(urAccessRefClHurtType))
        self.actRBHurtFactorType.setEnabled(isClassificatorRefAdmin or app.userHasRight(urAccessRefClHurtFactorType))
        self.actRBUnit.setEnabled(isClassificatorRefAdmin or app.userHasRight(urAccessRefClUnit))

        # Подменю Учет
        self.menu_6.setEnabled(isRefAdmin or
           app.userHasAnyRight([urAccessRefAccount,
                                urAccessRefAccountRBVisitType,
                                urAccessRefAccountEventType,
                                urAccessRefAccountRBEventTypePurpose,
                                urAccessRefAccountRBScene,
                                urAccessRefAccountRBAttachType,
                                urAccessRefAccountRBMedicalAidUnit,
                                urAccessRefAccountActionPropertyTemplate,
                                urAccessRefAccountActionType,
                                urAccessRefAccountActionTemplate,
                                urAccessRefAccountRBReasonOfAbsence,
                                urAccessRefAccountRBHospitalBedProfile,
                               ]))
        self.actRBVisitType.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAccount, urAccessRefAccountRBVisitType]))
        self.actRBTest.setEnabled(isRefAdmin or app.userHasAnyRight([urAccessRefAccount]))
        self.actRBTestGroup.setEnabled(isRefAdmin or app.userHasAnyRight([urAccessRefAccount]))
        self.actRBLaboratory.setEnabled(isRefAdmin or app.userHasAnyRight([urAccessRefAccount]))
        self.actRBSuiteReagent.setEnabled(isRefAdmin or app.userHasAnyRight([urAccessRefAccount]))
        self.actEventType.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAccount, urAccessRefAccountEventType]))
        self.actRBEventTypePurpose.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAccount, urAccessRefAccountRBEventTypePurpose]))
        self.actRBEventProfile.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAccount, urAccessRefAccountRBEventProfile]))
        self.actRBScene.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAccount, urAccessRefAccountRBScene]))
        self.actRBAttachType.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAccount, urAccessRefAccountRBAttachType]))
        self.actRBMedicalAidUnit.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAccount, urAccessRefAccountRBMedicalAidUnit]))
        self.actRBMedicalAidKind.setEnabled(isRefAdmin or app.userHasRight(urAccessRefAccount))
        self.actRBMedicalAidType.setEnabled(isRefAdmin or app.userHasRight(urAccessRefAccount))
        self.actRBMedicalAidProfile.setEnabled(isRefAdmin or app.userHasRight(urAccessRefAccount))
        self.actRBMesSpecification.setEnabled(isRefAdmin or app.userHasRight(urAccessRefAccount))

        self.actActionPropertyTemplate.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAccount, urAccessRefAccountActionPropertyTemplate]))
        self.actRBActionShedule.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAccount, urAccessRefAccountRBActionShedule]))
        self.actActionType.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAccount, urAccessRefAccountActionType]))
        self.actActionTemplate.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAccount, urAccessRefAccountActionTemplate]))
        self.actRBReasonOfAbsence.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAccount, urAccessRefAccountRBReasonOfAbsence]))
        self.actRBHospitalBedProfile.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefAccount, urAccessRefAccountRBHospitalBedProfile]))
        self.actRBJobType.setEnabled(isRefAdmin or app.userHasAnyRight([urAccessRefAccount]))

        # Подменю Организации
        self.menu_11.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefOrganization, urAccessRefOrgRBNet, urAccessRefOrgBank, urAccessRefOrgOrganisation]))
        self.actRBNet.setEnabled(isRefAdmin or \
            app.userHasAnyRight([urAccessRefOrganization, urAccessRefOrgRBNet]))
        self.actBank.setEnabled(isRefAdmin or \
            app.userHasAnyRight([urAccessRefOrganization, urAccessRefOrgBank]))
        self.actOrganisation.setEnabled(isRefAdmin or \
            app.userHasAnyRight([urAccessRefOrganization, urAccessRefOrgOrganisation]))

        # Подменю Финансовые
        self.menu_5.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefFinancial, urAccessRefFinRBFinance,
                                 urAccessRefFinRBService, urAccessRefFinRBTariffCategory,
                                 urAccessRefFinRBPayRefuseType, urAccessRefFinRBCashOperation]))
        self.actRBFinance.setEnabled(isRefAdmin or \
            app.userHasAnyRight([urAccessRefFinancial, urAccessRefFinRBFinance]))
        self.actRBServiceGroup.setEnabled(isRefAdmin or \
            app.userHasAnyRight([urAccessRefFinancial, urAccessRefFinRBService]))
        self.actRBService.setEnabled(isRefAdmin or \
            app.userHasAnyRight([urAccessRefFinancial, urAccessRefFinRBService]))
        self.actRBTariffCategory.setEnabled(isRefAdmin or \
            app.userHasAnyRight([urAccessRefFinancial, urAccessRefFinRBTariffCategory]))
        self.actRBPayRefuseType.setEnabled(isRefAdmin or \
            app.userHasAnyRight([urAccessRefFinancial, urAccessRefFinRBPayRefuseType]))
        self.actRBCashOperation.setEnabled(isRefAdmin or \
            app.userHasAnyRight([urAccessRefFinancial, urAccessRefFinRBCashOperation]))

        # Подменю Социальный Статус
        self.menu_12.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefSocialStatus, urAccessRefSocialStatusType, urAccessRefSocialStatusClass]))
        self.actRBSocStatusType.setEnabled(isRefAdmin or \
            app.userHasAnyRight([urAccessRefSocialStatus, urAccessRefSocialStatusType]))
        self.actRBSocStatusClass.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefSocialStatus, urAccessRefSocialStatusClass]))

        # Подменю Персонификация
        self.menu_13.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefPersonfication,
                                 urAccessRefPersnftnPolicyKind,
                                 urAccessRefPersnftnPolicyType,
                                 urAccessRefPersnftnDocumentTypeGroup,
                                 urAccessRefPersnftnDocumentType,
                                 urAccessRefPersnftnContactType
                                ]))
        self.actRBPolicyType.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefPersonfication, urAccessRefPersnftnPolicyType]))
        self.actRBPolicyKind.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefPersonfication, urAccessRefPersnftnPolicyKind]))
        self.actRBDocumentTypeGroup.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefPersonfication, urAccessRefPersnftnDocumentTypeGroup]))
        self.actRBDocumentType.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefPersonfication, urAccessRefPersnftnDocumentType]))
        self.actRBContactType.setEnabled(isRefAdmin or
            app.userHasAnyRight([urAccessRefPersonfication, urAccessRefPersnftnContactType]))

        # Подменю Номенклатура
        self.mnuNomenclature.setEnabled(isRefAdmin
                                        or app.userHasRight(urAccessNomenclature)
                                        or app.userHasRight(urAccessStockRecipe)
                                       )
        self.actRBNomenclatureClass.setEnabled(isRefAdmin or app.userHasRight(urAccessNomenclature))
        self.actRBNomenclatureKind.setEnabled(isRefAdmin or app.userHasRight(urAccessNomenclature))
        self.actRBNomenclatureType.setEnabled(isRefAdmin or app.userHasRight(urAccessNomenclature))
        self.actRBNomenclature.setEnabled(isRefAdmin or app.userHasRight(urAccessNomenclature))
        self.actRBStockRecipe.setEnabled(isRefAdmin or app.userHasRight(urAccessStockRecipe))

        # Подменю Лаборатория
        self.mnuLaboratory.setEnabled(isRefAdmin or app.userHasRight(urAccessLaboratory))

        # Подменю Оборудование
        self.mnuEquipment.setEnabled(isRefAdmin or app.userHasRight(urAccessEquipment))

        # Меню Сервис
        self.actCreateAttachClientsForArea.setEnabled(isAdmin or app.userHasRight(urAccessAttachClientsForArea))
        self.actTestSendMail.setEnabled(loggedIn)
        self.actTestMKB.setEnabled(loggedIn)
        self.actTestRLS.setEnabled(loggedIn)
        self.actTestMES.setEnabled(loggedIn)
        self.actTestTNMS.setEnabled(loggedIn)
        self.actSchemaClean.setEnabled(isAdmin or app.userHasRight(urAccessSchemaClean))
        self.actSchemaSync.setEnabled(isAdmin or app.userHasRight(urAccessSchemaSync))
        self.actCheckJury.setVisible(QtGui.qApp.isPNDDiagnosisMode())
        self.actCheckAccounts.setVisible(QtGui.qApp.defaultKLADR()[:2] == '23')

        # Подменю Логический контроль
        self.mnuCheck.setEnabled(isAdmin or app.userHasRight(urAccessLogicalControl))
        self.actControlDiagnosis.setEnabled(isAdmin or app.userHasRight(urAccessLogicalControlDiagnosis))
        self.actControlDoubles.setEnabled(isAdmin or app.userHasRight(urAccessLogicalControlDoubles))
        self.actControlMes.setEnabled(isAdmin or app.userHasRight(urAccessLogicalControlMES))

        # Меню Настройки
        self.actConnection.setEnabled(True)
        self.actAppPreferences.setEnabled(loggedIn)
#        self.actEMSRNExchangePreferences.setEnabled(True)
#        self.actMIACExchangePreferences.setEnabled(True)
        self.actAdditionalFeaturesUrls.setEnabled(isAdmin)
        self.actRBPrintTemplate.setEnabled(isAdmin or app.userHasRight(urAccessSetupTemplate))
        self.actRBAccountExportFormat.setEnabled(isAdmin or app.userHasRight(urAccessSetupAccountSystems))
        self.actRBAccountingSystem.setEnabled(isAdmin or app.userHasRight(urAccessSetupExport))

        self.actUserRightListDialog.setEnabled(isAdmin or app.userHasRight(urAccessSetupUserRights))
        self.actUserRightProfileListDialog.setEnabled(isAdmin or app.userHasRight(urAccessSetupUserRights))
        self.actChangeCurrentUserPassword.setEnabled(loggedIn and not app.loggedWithoutPassword)
        self.actCalendar.setEnabled(isAdmin or app.userHasRight(urAccessCalendar))
        self.actRBCounter.setEnabled(isAdmin or app.userHasRight(urAccessSetupCounter))
        self.actEQueueSettings.setEnabled(isAdmin or app.userHasRight(urEQSettings))

        # Меню помощь
        self.actSendBugReport.setEnabled(loggedIn)
        self.actAbout.setEnabled(True)
        self.actAboutQt.setEnabled(True)
        self.actionGo1.setEnabled(True)
        self.actionGo1.setVisible(True)
        self.actECROther.setEnabled(app.userHasRight(urECRAccess))
        # self.actImportFLS.setVisible(False)

        self.actImportMIS.setEnabled(app.userHasRight(urAccessExportImportMIAC))
        self.actExportAttachedClientsR23MIAC.setEnabled(app.userHasRight(urAccessExportImportMIAC))
        self.menu_30.setEnabled(QtGui.qApp.region() == '23')

        # Отчёты для PZ12
        if QtGui.qApp.db and QtGui.qApp.db.db.isOpen():
            reportsForPZ12 = [
                self.actReportOnPaidServicesPZ12,
                self.actReportOnEconomicCalcServicesPZ12,
            ]
            for actReport in reportsForPZ12:
                actReport.setVisible(QtGui.qApp.currentOrgInfis() == u'пстом12')

    def getProgressBar(self):
        if not self.progressBarVisible:
            self.progressBarVisible = True
            self.statusBar.addWidget(self.progressBar)
            self.progressBar.show()
        return self.progressBar

    def hideProgressBar(self):
        self.statusBar.removeWidget(self.progressBar)
        self.progressBarVisible = False

    def setUserName(self, userName):
        try:
            from buildInfo import lastChangedRev
        except:
            lastChangedRev = 'unknown'
        if userName:
            self.setWindowTitle(u'%s: %s (сборка %s)' % (title, userName, lastChangedRev))
        else:
            self.setWindowTitle(title + u' (сборка %s)' % lastChangedRev)

    def closeRegistryWindow(self):
        if self.registry:
            self.registry.close()
            self.registry = None

    def closeDeferredQueueWindow(self):
        if self.deferredQueue:
            self.deferredQueue.close()
            self.deferredQueue = None

    def addMruItem(self, mruList, id, descr):
        mruList = filter(lambda item: item[0] != id, mruList)
        mruList.insert(0, (id, descr))
        return mruList[:20]

    def prepareMruMenu(self, menu, clearAction, mruList, method):
        for action in menu.actions():
            if action.isSeparator():
                break
            menu.removeAction(action)
        actions = menu.actions()
        topAction = actions[0] if actions else None
        actions = []
        for id, descr in mruList:
            action = QAction(descr, self)
            action.setData(toVariant(id))
            self.connect(action, QtCore.SIGNAL('triggered()'), method)
            actions.append(action)
        menu.insertActions(topAction, actions)
        clearAction.setEnabled(bool(actions))

    def addMruEvent(self, eventId, descr):
        newList = self.addMruItem(self.mruEventList, eventId, descr)
        self.mruEventListChanged = newList != self.mruEventList
        self.mruEventList = newList

    # i3022: pirozhok: вытаскиваем с бд подразделение, которое привязанно к аккаунту, при увсловии,
    # что в умолчания/"прочие настройки" стоит чекбокс "Определять подразделение по пользователю"
    @staticmethod
    def getDefaultSubdivision(userId):
        if forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'defaultSubdivision', False)):
            db = QtGui.qApp.db
            res = db.getRecord(db.table('Person'), 'org_id, orgStructure_id', userId)
            orgId = QtGui.qApp.preferences.appPrefs['orgId'] = forceRef(res.value('org_id'))
            QtGui.qApp.preferences.appPrefs['orgStructureId'] = forceRef(res.value('orgStructure_id'))

    @QtCore.pyqtSlot()
    def on_actExportToDbf_triggered(self):
        from Exchange.ExportToDbfDialog import CExportToDbfDialog
        CExportToDbfDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actExportR67Duplicates_triggered(self):
        from Exchange.ExportR67Duplicates     import exportR67Duplicates
        exportR67Duplicates(self)

    @QtCore.pyqtSlot()
    def on_actDBFToMySql_triggered(self):
        from Exchange.DbfToMySqlDump import CDbfToMySqlDumpDialog
        CDbfToMySqlDumpDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actLogin_triggered(self):
        try:
            demoMode = False
            ok = False

            if not QtGui.qApp.preferences.dbNewAuthorizationScheme:
                QtGui.qApp.openDatabase()

            if QtGui.qApp.demoModePosible() and QtGui.qApp.demoModeRequested:
                ok, userId, demoMode, login = True, None, True, 'demo'

            if not ok:
                login = getADUser()
                if login:
                    ok, userId = verifyUser(login)
                    QtGui.qApp.loggedWithoutPassword = ok

            if not ok:
                logo = None
                if QtGui.qApp.currentOrgId():
                    logo = 'logo'
                    defaultKLADR = QtGui.qApp.defaultKLADR()
                    if len(defaultKLADR) >= 2 and defaultKLADR[:2] != '78':
                        logo = 'logo_ivista'

                ok = False
                QtGui.qApp.isAuth = False
                while not ok:
                    if QtGui.qApp.preferences.isSaveUserPasword and QtGui.qApp.preferences.userPassword is not None:
                        login = QtGui.qApp.preferences.appUserName
                        password = QtGui.qApp.preferences.userPassword
                    else:
                        dialog = CLoginDialog(self, logo)

                        dialog.setLoginName(QtGui.qApp.preferences.appUserName)
                        if dialog.exec_():
                            login = dialog.loginName()
                            password = forceString(dialog.password())
                            QtGui.qApp.preferences.isSaveUserPasword = dialog.isSavePassword()
                            if QtGui.qApp.preferences.isSaveUserPasword:
                                QtGui.qApp.preferences.userPassword = password
                            settings = CPreferences.getSettings(CConnectionDialog.iniFileName)
                            if QtGui.qApp.preferences.dbConnectionName:
                                settings.beginGroup(QtGui.qApp.preferences.dbConnectionName)
                                settings.setValue('login', toVariant(login))
                                settings.endGroup()
                                settings.sync()
                        else:
                            return
                    ok, userId, demoMode = self.login(login, password)
                    if not ok:
                        QtGui.qApp.preferences.isSaveUserPasword = False
            self.connect(QtGui.qApp.db, SIGNAL('disconnected()'), self.onDatabaseDisconnected)

            if ok:
                QtGui.qApp.isAuth = True
                QtGui.qApp.setUserId(userId, demoMode)
                QtGui.qApp.preferences.appUserName = login
                self.emit(QtCore.SIGNAL('hasRightToRunMoreThanOneProgramm(bool)'), QtGui.qApp.userHasRight(urAccessToRunMoreThanOneProgramm))

                # =
                self.getDefaultSubdivision(userId)
                # =

                userName = QtGui.qApp.userName()
                if QtGui.qApp.isNurse() and QtGui.qApp.nurseOwnerId():
                    # Дописать имя врача, если работает медсестра с врачом
                    userName += u'(врач: %s)' % CUserInfo(QtGui.qApp.nurseOwnerId()).name()
                self.setUserName(userName)

                self.updateActionsState()

                if forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'isAutoStartEQControls', False)):
                    eqController = CEQController.getInstance()
                    eqController.updateDatabase()
                    eqController.setAutoStart(True)
                    eqController.loadControls()
                    eqController.controlModel().enableControls()
                else:
                    CEQController.setAutoStart(False)

                try:
                    showInformer(QtGui.qApp.mainWindow, True)
                except:
                    pass
                Logger.setLoggerDbName(QtGui.qApp.preferences.dbLoggerName)
                Logger.loginInClient(person_id=userId)
                Logger.loginId = Logger.getLoginId()
                if hasattr(QtGui.qApp.preferences, 'thread') and QtGui.qApp.preferences.thread.is_alive():
                    self.showLoading()
                return
        except CDatabaseException as e:
            QtGui.QMessageBox.critical(
                self,
                u'Ошибка открытия базы данных',
                unicode(e),
                QtGui.QMessageBox.Close)
        except Exception, e:
            QtGui.QMessageBox.critical(
                self,
                u'Ошибка открытия базы данных',
                u'Невозможно установить соединение с базой данных\n' + unicode(e),
                QtGui.QMessageBox.Close)
            QtGui.qApp.logCurrentException()
        QtGui.qApp.closeDatabase()

    def showLoading(self):
        from library.loadingScreen import CLoadingScreen
        CLoadingScreen(QtGui.qApp.preferences.thread, self)

    def login(self, login, password):
        try:
            encodedLogin = unicode(login).encode('utf-8')
            encodedPassword = unicode(password).encode('utf8')

            if not QtGui.qApp.db or not QtGui.qApp.db.db.isOpen():
                connectionAddInfo = None
                if QtGui.qApp.preferences.dbNewAuthorizationScheme:
                    hashedPassword = hashlib.md5(encodedPassword).hexdigest()
                    connectionAddInfo = {'user' : createLogin(encodedLogin),
                                         'password' : hashedPassword}
                QtGui.qApp.openDatabase(connectionAddInfo)

            isTruePassword, userId = verifyUserPassword(login, password)
            if isTruePassword:
                return True, userId, False #isOk, userId, isDemoMode
            if login == demoUserName and password == 'masterkey' and QtGui.qApp.demoModePosible():
                return True, None, True #isOk, userId, isDemoMod
            QtGui.QMessageBox.critical( self, u"Внимание", u"Имя пользователя или пароль неверны", QtGui.QMessageBox.Close)
        except Exception, e:
            message = unicode(e)
            if message.count(u"Access denied for user"):
                message = u"Имя пользователя или пароль неверны, либо вход с систему запрещен"
            QtGui.QMessageBox.critical(self, u"", message, QtGui.QMessageBox.Close)
        return False, None, False

    @QtCore.pyqtSlot()
    def on_actLogout_triggered(self):
        Logger.logoutInClient()
        QtGui.qApp.closeDatabase()
        self.emit(QtCore.SIGNAL('hasRightToRunMoreThanOneProgramm(bool)'), False)
        if QtGui.qApp.preferences.isSaveUserPasword:
            QtGui.qApp.preferences.isSaveUserPasword = False
            QtGui.qApp.preferences.save()

    @pyqtSlot()
    def onDatabaseDisconnected(self):
        self.emit(QtCore.SIGNAL('hasRightToRunMoreThanOneProgramm(bool)'), False)
        self.closeRegistryWindow()
        self.closeDeferredQueueWindow()

        self.setUserName('')
        self.mruEventListChanged = True
        self.mruEventList = []
        self.updateActionsState()

    @QtCore.pyqtSlot()
    def on_mnuMruEvents_aboutToShow(self):
        if self.mruEventListChanged:
            self.prepareMruMenu(self.mnuMruEvents, self.actClearMruEvents, self.mruEventList, self.onEventEdit)
            self.mruEventListChanged = False

    def onEventEdit(self):
        from Events.CreateEvent import editEvent
        eventId = forceRef(self.sender().data())
        if eventId:
            if not forceBool(QtGui.qApp.db.translate('Event', 'id', eventId, 'deleted')):
                editEvent(self, eventId)
            else:
                QtGui.QMessageBox.critical(self,
                                       u'Внимание!',
                                       u'Эту запись нельзя редактировать так как она удалена',
                                       QtGui.QMessageBox.Close)

    @QtCore.pyqtSlot()
    def on_actClearMruEvents_triggered(self):
        self.mruEventList = []
        self.mruEventListChanged = True

    @QtCore.pyqtSlot()
    def on_actQuit_triggered(self):
        Logger.logoutInClient()
        self.close()

    @QtCore.pyqtSlot()
    def on_actRegistry_triggered(self, clientId = 0):
        if self.deferredQueue:
            self.closeDeferredQueueWindow()
        if self.registry is None or not (self.registry in self.centralWidget.windowList()):
            self.registry = CRegistryWindow(None)
            self.centralWidget.addWindow(self.registry, Qt.Window)
            self.registry.setWindowState(Qt.WindowMaximized)
            self.registry.show()
            if clientId:
                self.registry.setCurrentClientId(clientId)
            if self.dockResources and self.dockResources.content:
                self.connect(self.dockResources.content, SIGNAL('createdOrder()'), self.registry.updateQueue)

    @QtCore.pyqtSlot()
    def on_actDeferredQueue_triggered(self, queueId = 0):
        from Registry.DeferredQueueWindow import CDeferredQueueWindow
        if self.registry:
            self.closeRegistryWindow()
        if self.deferredQueue is None or not (self.deferredQueue in self.centralWidget.windowList()):
            self.deferredQueue = CDeferredQueueWindow(None)
            self.centralWidget.addWindow(self.deferredQueue, Qt.Window)
            self.deferredQueue.setWindowState(Qt.WindowMaximized)
            self.deferredQueue.show()
            if queueId:
                self.deferredQueue.setCurrentQueueId(queueId)

    @QtCore.pyqtSlot()
    def on_actTimeline_triggered(self):
        from Timeline.TimelineDialog import CTimelineDialog
        CTimelineDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormRegistration_triggered(self):
        from Blank.BlanksDialog import CBlanksDialog
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
        try:
            blanksDialog = CBlanksDialog(self)
        finally:
            QtGui.qApp.restoreOverrideCursor()
        if blanksDialog:
            blanksDialog.exec_()

    @QtCore.pyqtSlot()
    def on_actQuoting_triggered(self):
        from Quoting.QuotingDialog import CQuotingDialog
        dialog = CQuotingDialog(self)
        if not (QtGui.qApp.userHasRight(urAccessQuoting) or QtGui.qApp.userHasRight(urAdmin)):
            dialog.setEditable(False)
        dialog.exec_()

    @QtCore.pyqtSlot()
    def on_actTissueJournal_triggered(self):
        from TissueJournal.TissueJournalDialog import CTissueJournalDialog
        CTissueJournalDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actJobJournal_triggered(self):
        from Resources.JobsJournalDialog import CJobsJournalDialog
        CJobsJournalDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actHospitalBeds_triggered(self):
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
        try:
            hospitalBedsDialog = CHospitalBedsDialog(self)
        finally:
            QtGui.qApp.restoreOverrideCursor()
        if hospitalBedsDialog:
            hospitalBedsDialog.exec_()

    @QtCore.pyqtSlot()
    def on_actJobsPlanning_triggered(self):
        from Resources.JobPlanner import CJobPlanner
        CJobPlanner(self).exec_()

    @QtCore.pyqtSlot()
    def on_actJobsOperating_triggered(self):
        from Resources.JobsOperatingDialog import CJobsOperatingDialog
        CJobsOperatingDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStockControl_triggered(self):
        from Stock.StockDialog import CStockDialog
        CStockDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actAccounting_triggered(self):
        from Accounting.AccountingDialog import CAccountingDialog
        CAccountingDialog(self).exec_()

    # FIXME: pirozhok: удалите как только перестанете использовать
    @QtCore.pyqtSlot()
    def on_actRecreateEvent_triggered(self):
        from library.RecreateEvent.RecreateDialog import CRecreateDialog
        CRecreateDialog().exec_()

    @QtCore.pyqtSlot()
    def on_actCashBook_triggered(self):
        from Accounting.CashBookDialog import CCashBookDialog
        CCashBookDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportLeavedMovedDead_triggered(self):
        from Reports.Moscow.ReportLeavedMovedDead import CReportLeavedMovedDead
        CReportLeavedMovedDead(self).exec_()

    @QtCore.pyqtSlot()
    def on_actClientInfoSource_triggered(self):
        from Reports.ReportClientInfoSource import CReportClientInfoSource
        CReportClientInfoSource(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportMovingB36_triggered(self):
        from Reports.Moscow.ReportMovingB36 import CReportMovingB36
        CReportMovingB36(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportMovingB36Monthly_triggered(self):
        from Reports.Moscow.ReportMovingB36Monthly import CReportMovingB36Monthly
        CReportMovingB36Monthly(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportMovingRVC_triggered(self):
        from Reports.Moscow.ReportMovingRVC import CReportMovingRVC
        CReportMovingRVC(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportMSCH3Contingent_triggered(self):
        from Reports.ReportMSCH3Contingent import CReportMSCH3Contingent
        CReportMSCH3Contingent(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportMSCH3Outpatient_triggered(self):
        from Reports.ReportMSCH3Outpatient import CReportMSCH3Outpatient
        CReportMSCH3Outpatient(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDispatchingForAdmin_triggered(self):
        from Reports.Moscow.Dispatching.ReportForAdmin import CDispatchingAdminReport
        CDispatchingAdminReport(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDispatchingByOrgStructure_triggered(self):
        from Reports.Moscow.Dispatching.ReportByOrgStructure import CDispathingByOrgStructureReport
        CDispathingByOrgStructureReport(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDispatchingByHospChannels_triggered(self):
        from Reports.Moscow.Dispatching.ReportByHospChannels import CDispatchingByHospChannelsReport
        CDispatchingByHospChannelsReport(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDispatching3_triggered(self):
        from Reports.Moscow.Dispatching.ReportDispatching3 import CDispatching3Report
        CDispatching3Report(self).exec_()

    @QtCore.pyqtSlot()
    def on_actArrivedDepartedClients_triggered(self):
        from Reports.Pes.ArrivedDepartedPatients import CArrivedDepartedPatients
        CArrivedDepartedPatients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actImportActionType_triggered(self):
        from Exchange.ImportActions           import ImportActionType
        ImportActionType()

    @QtCore.pyqtSlot()
    def on_actImportDLOMIAC_triggered(self):
        from Exchange.R23.recipes.ImportFormularyDLOMiac import ImportFormularyDLOMiac
        ImportFormularyDLOMiac(self)

    @QtCore.pyqtSlot()
    def on_actImportEventType_triggered(self):
        from Exchange.ImportEvents            import ImportEventType
        ImportEventType()

    @QtCore.pyqtSlot()
    def on_actImportRefBooks_triggered(self):
        from Exchange.ImportRefBooks import importRefBooks
        importRefBooks(self)

    @QtCore.pyqtSlot()
    def on_actImportOrganisations_triggered(self):
        from Exchange.ImportOrganisations import importOrganisations
        importOrganisations(self)

    @QtCore.pyqtSlot()
    def on_actImportPersons_VM_triggered(self):
        from Exchange.ImportPersons_VM import importPersons_VM
        importPersons_VM(self)

    @QtCore.pyqtSlot()
    def on_actImportDiagnosticResult_triggered(self):
        from Exchange.ImportRbDiagnosticResult import importDiagnosticResult
        importDiagnosticResult(self)

    @QtCore.pyqtSlot()
    def on_actImportActionTemplate_triggered(self):
        from Exchange.ImportActionTemplate import ImportActionTemplate
        ImportActionTemplate()

    @QtCore.pyqtSlot()
    def on_actImportDD_triggered(self):
        from Exchange.ImportDD                import ImportDD
        ImportDD()

    @QtCore.pyqtSlot()
    def on_actImport131DBF_triggered(self):
        from Exchange.Import131 import Import131
        Import131(self)

    @QtCore.pyqtSlot()
    def on_actImport131XML_triggered(self):
        from Exchange.Import131XML import Import131XML
        Import131XML(self)

    @QtCore.pyqtSlot()
    def on_actImport131Errors_triggered(self):
        from Exchange.Import131Errors import Import131Errors
        Import131Errors(self)

    @QtCore.pyqtSlot()
    def on_actImportLgot_triggered(self):
        from Exchange.ImportLgot import ImportLgot
        ImportLgot(self)

    @QtCore.pyqtSlot()
    def on_actImportQuotaFromVTMP_triggered(self):
        from Exchange.ImportQuotaFromVTMP import ImportQuotaFromVTMP
        ImportQuotaFromVTMP(self)

    @QtCore.pyqtSlot()
    def on_actImportProfilesEIS_triggered(self):
        from Exchange.ImportProfiles import ImportProfiles
        ImportProfiles(self)

    @QtCore.pyqtSlot()
    def on_actImportProfilesINFIS_triggered(self):
        from Exchange.ImportProfilesINFIS import ImportProfilesINFIS
        ImportProfilesINFIS(self)

    @QtCore.pyqtSlot()
    def on_actImportEIS_triggered(self):
        from Exchange.ImportEIS import  ImportEIS
        ImportEIS(self)

    @QtCore.pyqtSlot()
    def on_actImportEisOmsLpu_triggered(self):
        from Exchange.ImportEISOMS_LPU import ImportEISOMS_LPU
        ImportEISOMS_LPU(self)

    @QtCore.pyqtSlot()
    def on_actImportEisOmsSmo_triggered(self):
        from Exchange.ImportEISOMS_SMO import ImportEISOMS_SMO
        ImportEISOMS_SMO(self)

    @QtCore.pyqtSlot()
    def on_actImportEisOmsFull_triggered(self):
        from Exchange.ImportEISOMSFull import ImportEISOMSFull
        ImportEISOMSFull(self)

    @QtCore.pyqtSlot()
    def on_actImportPersons_triggered(self):
        from Exchange.ImportPersons import ImportPersons
        ImportPersons(self)

    @QtCore.pyqtSlot()
    def on_actImportServiceNomen_triggered(self):
        from Exchange.ImportServiceNomen import CImportServiceNomen
        CImportServiceNomen(self).exec_()

    @QtCore.pyqtSlot()
    def on_actImportServiceMes_triggered(self):
        from Exchange.ImportServiceMes import CImportServiceMes
        CImportServiceMes(self).exec_()

    @QtCore.pyqtSlot()
    def on_actImportR67Duplicates_triggered(self):
        from Exchange.ImportR67Duplicates import importR67Duplicates
        importR67Duplicates(self)

    @QtCore.pyqtSlot()
    def on_actImportRbResult_triggered(self):
        from Exchange.ImportRbResult import ImportRbResult
        ImportRbResult(self)

    @QtCore.pyqtSlot()
    def on_actImportRbUnit_triggered(self):
        from Exchange.ImportRbUnit import ImportRbUnit
        ImportRbUnit(self)

    @QtCore.pyqtSlot()
    def on_actImportRbThesaurus_triggered(self):
        from Exchange.ImportRbThesaurus import ImportRbThesaurus
        ImportRbThesaurus(self)

    @QtCore.pyqtSlot()
    def on_actImportRbService_triggered(self):
        from Exchange.ImportRbService import ImportRbService
        ImportRbService(self)

    @QtCore.pyqtSlot()
    def on_actImportRbComplain_triggered(self):
        from Exchange.ImportRbComplain import ImportRbComplain
        ImportRbComplain(self)

    @QtCore.pyqtSlot()
    def on_actImportPolicySerialDBF_triggered(self):
        from Exchange.ImportPolicySerialDBF import ImportPolicySerialDBF
        ImportPolicySerialDBF(self)

    @QtCore.pyqtSlot()
    def on_actImportOrgsINFIS_triggered(self):
        from Exchange.ImportOrgsINFIS import ImportOrgsINFIS
        ImportOrgsINFIS(self)

    @QtCore.pyqtSlot()
    def on_actImpotrFromSail_triggered(self):
        from Exchange.ImportFromSail import ImportFromSail
        ImportFromSail()

    @QtCore.pyqtSlot()
    def on_actImportFLS_triggered(self):
        from Exchange.R23.ImportFLC import ImportFLC
        ImportFLC(self)

    @QtCore.pyqtSlot()
    def on_actImportMKB_triggered(self):
        from Exchange.ImportMKB import importMKB
        importMKB(self)

    @QtCore.pyqtSlot()
    def on_actImportFormularyDLO_triggered(self):
        from Exchange.ImportFormularyDLO import ImportFormularyDLO
        ImportFormularyDLO(self)

    @QtCore.pyqtSlot()
    def on_actImportSPR18_triggered(self):
        from Exchange.ImportSPR18 import ImportSPR18
        ImportSPR18(self)

    @QtCore.pyqtSlot()
    def on_actImportSPR69_triggered(self):
        from Exchange.ImportSPR69 import ImportSPR69
        ImportSPR69(self)

    @QtCore.pyqtSlot()
    def on_actImportSPR70_triggered(self):
        from Exchange.R23.ImportSPR70 import ImportSPR70
        ImportSPR70(self)

    @QtCore.pyqtSlot()
    def on_actImportSPR71_triggered(self):
        from Exchange.ImportSPR71 import ImportSPR71
        ImportSPR71(self)

    @QtCore.pyqtSlot()
    def on_actImportSPR72_triggered(self):
        from Exchange.ImportSPR72 import ImportSPR72
        ImportSPR72(self)

    @QtCore.pyqtSlot()
    def on_actImportSPR73_triggered(self):
        from Exchange.ImportSPR73 import ImportSPR73
        ImportSPR73(self)

    @QtCore.pyqtSlot()
    def on_actImportSPR01_triggered(self):
        from Exchange.ImportSPR01 import ImportSPR01
        ImportSPR01(self)

    @QtCore.pyqtSlot()
    def on_actImportSPR64_triggered(self):
        from Exchange.ImportSPR64 import ImportSPR64
        ImportSPR64(self)

    @QtCore.pyqtSlot()
    def on_actImportSPR15_triggered(self):
        from Exchange.ImportSPR15 import ImportSPR15
        ImportSPR15(self)

    @QtCore.pyqtSlot()
    def on_actImportSPRSMO_triggered(self):
        from Exchange.ImportSPR_SMO import ImportSPR_SMO
        ImportSPR_SMO(self)

    @QtCore.pyqtSlot()
    def on_actImportR85ERZCentral_triggered(self):
        from Exchange.R85.ImportR85ERZCentral import importR85ERZCentral
        importR85ERZCentral(self)

    @QtCore.pyqtSlot()
    def on_actExport131_triggered(self):
        from Exchange.Export131 import Export131
        Export131(self).exec_()

    @QtCore.pyqtSlot()
    def on_actExportFedRegPer_triggered(self):
        from Exchange.ExportFedRegPer import CExportFedRegPerRMain
        CExportFedRegPerRMain(self).exec_()

    @QtCore.pyqtSlot()
    def on_actImportClients_triggered(self):
        from Exchange.ImportClients import CReportImportClients
        CReportImportClients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actImportCrimea_triggered(self):
        from Exchange.ImportCrimea import CImportCrimea
        CImportCrimea(self).exec_()

    @QtCore.pyqtSlot()
    def on_actExportAttachClient_triggered(self):
        from Exchange.ExportAttachClient import CExportClientAttachWizard
        CExportClientAttachWizard(self).exec_()

    @QtCore.pyqtSlot()
    def on_actExportAttachedClientsR23MIAC_triggered(self):
        from Exchange.R23.AttachedClients import CAttachedClientsDialog
        CAttachedClientsDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actImportMIS_triggered(self):
        from Exchange.R23.ImportMIS import CImportMIS
        CImportMIS(self).exec_()

    @QtCore.pyqtSlot()
    def on_actAttachmentPerson_triggered(self):
        from Reports.ReportAttachmentPerson import CReportAttachmentDoctors
        CReportAttachmentDoctors(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportLifetimeCytology_triggered(self):
        from Reports.ReportLifetimeCytology import CReportLifetimeCytology
        CReportLifetimeCytology(self).exec_()

    @QtCore.pyqtSlot()
    def on_actAttachment_triggered(self):
        from Reports.ReportAttachment import CReportAttachment
        CReportAttachment(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPatientAtHome_triggered(self):
        from Reports.ReportPatientsAtHome import CReportPatientsAtHome
        CReportPatientsAtHome(self).exec_()

    @QtCore.pyqtSlot()
    def on_actSelectionDiagnosis_triggered(self):
        from Reports.SelectionDiagnosis import CReportSelectionDiagnosis
        CReportSelectionDiagnosis(self).exec_()

    @QtCore.pyqtSlot()
    def on_actMilitaryAge_triggered(self):
        from Reports.ReportMilitaryAge import CReportMilitaryAge
        CReportMilitaryAge(self).exec_()

    @QtCore.pyqtSlot()
    def on_actWokingAge_triggered(self):
        from Reports.ReportWorkingAge import CReportWorkingAge
        CReportWorkingAge(self).exec_()

    @QtCore.pyqtSlot()
    def on_actTreatmentRoom_triggered(self):
        from Reports.ReportTreatmentRoom import CReportTreatmentRoom
        CReportTreatmentRoom(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPsychologicalAssistance_triggered(self):
        from Reports.ReportPsychologicalAssistance import CReportPsychologicalAssistance
        CReportPsychologicalAssistance(self).exec_()

    @QtCore.pyqtSlot()
    def on_actLogopedicAssistance_triggered(self):
        from Reports.ReportLogopedicAssistance import CReportLogopedicAssistance
        CReportLogopedicAssistance(self).exec_()

    @QtCore.pyqtSlot()
    def on_actNeurologicalAssistance_triggered(self):
        from Reports.ReportNeurologicalAssistance import CReportNeurologicalAss
        CReportNeurologicalAss(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPaidServices_triggered(self):
        from Reports.ReportPaidServices import CReportPaidServices
        CReportPaidServices(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportHospitalization_triggered(self):
        from Reports.ReportHospitalization import CReportHospitalization
        CReportHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actWorkAccount_triggered(self):
        from Reports.ReportAccountingWork import CReportAccountingWork
        CReportAccountingWork(self).exec_()

    @QtCore.pyqtSlot()
    def on_actSurgicalReport_triggered(self):
        from Reports.ReportSurgical import CReportSurgical
        CReportSurgical(self).exec_()

    @QtCore.pyqtSlot()
    def on_actCheckJury_triggered(self):
        from Reports.ReportCheckJury import CReportCheckJury
        CReportCheckJury(self).exec_()

    @QtCore.pyqtSlot()
    def on_actMovingDispClients_triggered(self):
        from Reports.ReportMovingDispClients import CReportMovingDispClients
        CReportMovingDispClients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actExportActionType_triggered(self):
        from Exchange.ExportActions import ExportActionType
        ExportActionType()

    @QtCore.pyqtSlot()
    def on_actExportEventType_triggered(self):
        from Exchange.ExportEvents import ExportEventType
        ExportEventType()

    @QtCore.pyqtSlot()
    def on_actExportActionTemplate_triggered(self):
        from Exchange.ExportActionTemplate import ExportActionTemplate
        ExportActionTemplate()

    @QtCore.pyqtSlot()
    def on_actExportPervDoc_triggered(self):
        from Exchange.Export_RD1_RD2 import exportPervDoc
        exportPervDoc(self)

    @QtCore.pyqtSlot()
    def on_actExportPrimaryDocInXml_triggered(self):
        from Exchange.ExportPrimaryDocInXml import ExportPrimaryDocInXml
        ExportPrimaryDocInXml(self)

    @QtCore.pyqtSlot()
    def on_actExportActionResult_triggered(self):
        from Exchange.ExportActionResult import ExportActionResult
        ExportActionResult(self)

    @QtCore.pyqtSlot()
    def on_actExportRefBooks_triggered(self):
        from Exchange.ExportRefBooks import exportRefBooks
        exportRefBooks(self)

    @QtCore.pyqtSlot()
    def on_actExportOrganisations_triggered(self):
        from Exchange.ExportOrganisations import exportOrganisations
        exportOrganisations(self)

    @QtCore.pyqtSlot()
    def on_actExportPersons_VM_triggered(self):
        from Exchange.ExportPersons_VM import exportPersons_VM
        exportPersons_VM(self)

    @QtCore.pyqtSlot()
    def on_actExportDiagnosticResult_triggered(self):
        from Exchange.ExportRbDiagnosticResult import exportDiagnosticResult
        exportDiagnosticResult(self)

    @QtCore.pyqtSlot()
    def on_actExportRbResult_triggered(self):
        from Exchange.ExportRbResult import ExportRbResult
        ExportRbResult(self)

    @QtCore.pyqtSlot()
    def on_actExportRbUnit_triggered(self):
        from Exchange.ExportRbUnit import ExportRbUnit
        ExportRbUnit(self)

    @QtCore.pyqtSlot()
    def on_actExportRbThesaurus_triggered(self):
        from Exchange.ExportRbThesaurus import ExportRbThesaurus
        ExportRbThesaurus(self)

    @QtCore.pyqtSlot()
    def on_actExportRbComplain_triggered(self):
        from Exchange.ExportRbComplain import ExportRbComplain
        ExportRbComplain(self)

    @QtCore.pyqtSlot()
    def on_actExportRbService_triggered(self):
        from Exchange.ExportRbService import ExportRbService
        ExportRbService(self)

    @QtCore.pyqtSlot()
    def on_actExportHL7v2_5_triggered(self):
        from Exchange.ExportHL7v2_5 import ExportHL7v2_5
        ExportHL7v2_5(self)

    @QtCore.pyqtSlot()
    def on_actExportFLCR23_triggered(self):
        from Exchange.ExportFLCR23 import exportFLCR23
        exportFLCR23(self)

    @QtCore.pyqtSlot()
    def on_actStatReportDD2013Weekly_triggered(self):
        from Reports.StatReportDD2013Weekly import CReportDD2013Weekly
        CReportDD2013Weekly(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2013Monthly_triggered(self):
        from Reports.StatReportDD2013Monthly import CReportDD2013Monthly
        CReportDD2013Monthly(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2013Results_triggered(self):
        from Reports.StatReportDD2013Results import CReportResultsDD
        CReportResultsDD(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportExposedDD_triggered(self):
        from Reports.StatReportExposedDD import CReportExposedDD
        CReportExposedDD(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDDSexAgeStructure_triggered(self):
        from Reports.StatReportDDSexAgeStructure import CReportDDSexAgeStructure
        CReportDDSexAgeStructure(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2015_1000_triggered(self):
        from Reports.StatReportDDSexAgeStructure import CReportDDSexAgeStructure2015
        CReportDDSexAgeStructure2015(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2015_2000_triggered(self):
        from Reports.StatReportDDPopulationGroups import CReportDDPopulationGroups2015
        CReportDDPopulationGroups2015(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2015_3000_triggered(self):
        from Reports.StatReportDDPopulationGroups import CReportDDPopulationGroups2015
        CReportDDPopulationGroups2015(self, stage = 2).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2015_4000_triggered(self):
        from Reports.StatReportDD2015RiskFactors import CReportDD2015RiskFactors
        CReportDD2015RiskFactors(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2015_5000_triggered(self):
        from Reports.StatReportDD2015FoundIllnesses import CReportDD2015FoundIllnesses
        CReportDD2015FoundIllnesses(self, [3, 4]).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2015_5001_triggered(self):
        from Reports.StatReportDD2015FoundIllnesses import CReportDD2015FoundIllnesses
        CReportDD2015FoundIllnesses(self, [2]).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2015_6000_triggered(self):
        from Reports.StatReportDD2015FoundIllnesses import CReportDD2015FoundIllnesses
        CReportDD2015FoundIllnesses(self, [5]).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2015_7000_triggered(self):
        from Reports.StatReportDDCommonResults import CReportDDCommonResults2015
        CReportDDCommonResults2015(self).exec_()



    @QtCore.pyqtSlot()
    def on_actStatReportDD2017_1000_triggered(self):
        from Reports.StatReportDDSexAgeStructure import CReportDDSexAgeStructure2017
        CReportDDSexAgeStructure2017(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2017_2000_triggered(self):
        from Reports.StatReportDDPopulationGroups import CReportDDPopulationGroups2017
        CReportDDPopulationGroups2017(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2017_3000_triggered(self):
        from Reports.StatReportDDPopulationGroups import CReportDDPopulationGroups2017
        CReportDDPopulationGroups2017(self, stage = 2).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2017_4000_triggered(self):
        from Reports.StatReportDD2017RiskFactors import CReportDD2017RiskFactors
        CReportDD2017RiskFactors(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2017_5000_triggered(self):
        from Reports.StatReportDD2017FoundIllnesses import CReportDD2017FoundIllnesses
        CReportDD2017FoundIllnesses(self, [3, 4]).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2017_5001_triggered(self):
        from Reports.StatReportDD2017FoundIllnesses import CReportDD2017FoundIllnesses
        CReportDD2017FoundIllnesses(self, [2]).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2017_6000_triggered(self):
        from Reports.StatReportDD2017FoundIllnesses import CReportDD2017FoundIllnesses
        CReportDD2017FoundIllnesses(self, [5]).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDD2017_7000_triggered(self):
        from Reports.StatReportDDCommonResults import CReportDDCommonResults2017
        CReportDDCommonResults2017(self).exec_()


    @QtCore.pyqtSlot()
    def on_actStatReportDDPopulationGroupsFS_triggered(self):
        from Reports.StatReportDDPopulationGroups import CReportDDPopulationGroups
        CReportDDPopulationGroups(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDDPopulationGroupsSS_triggered(self):
        from Reports.StatReportDDPopulationGroups import CReportDDPopulationGroups
        CReportDDPopulationGroups(self, stage = 2).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDDRiskFactors_triggered(self):
        from Reports.StatReportDDRiskFactors import CReportDDRiskFactors
        CReportDDRiskFactors(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDDFoundIllnesses_triggered(self):
        from Reports.StatReportDDFoundIllnesses import CReportDDFoundIllnesses
        CReportDDFoundIllnesses(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDDFoundSuspicions_triggered(self):
        from Reports.StatReportDDFoundIllnesses import CReportDDFoundIllnesses
        CReportDDFoundIllnesses(self, suspicions = True).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportDDCommonResults_triggered(self):
        from Reports.StatReportDDCommonResults import CReportDDCommonResults
        CReportDDCommonResults(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF12_D_1_07_triggered(self):
        from Reports.StatReportF12_D_1_07     import CStatReportF12_D_1_07
        CStatReportF12_D_1_07(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF12_D_2_07_triggered(self):
        from Reports.StatReportF12_D_2_07     import CStatReportF12_D_2_07
        CStatReportF12_D_2_07(self, mode='07').exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF12_D_1_08_triggered(self):
        from Reports.StatReportF12_D_1_08     import CStatReportF12_D_1_08
        CStatReportF12_D_1_08(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF12_D_2_08_triggered(self):
        from Reports.StatReportF12_D_2_07     import CStatReportF12_D_2_07
        CStatReportF12_D_2_07(self, mode='08').exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF12_D_3_M_triggered(self):
        from Reports.StatReportF12_D_3_M      import CStatReportF12_D_3_M
        CStatReportF12_D_3_M(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF12_D_2_09_triggered(self):
        from Reports.StatReportF12_D_2_07     import CStatReportF12_D_2_07
        CStatReportF12_D_2_07(self, mode='09').exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF12_D_1_10_triggered(self):
        from Reports.StatReportF12_D_1_10     import CStatReportF12_D_1_10
        CStatReportF12_D_1_10(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF12_D_2_10_triggered(self):
        from Reports.StatReportF12_D_2_10     import CStatReportF12_D_2_10
        CStatReportF12_D_2_10(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReport1NP2000_triggered(self):
        from Reports.StatReport1NP2000        import CStatReport1NP2000
        CStatReport1NP2000(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEQueueSettings_triggered(self):
        CEQController.getInstance().openSettings(self)

    @QtCore.pyqtSlot()
    def on_actStatReportF5_D_For_Teenager_triggered(self):
        from Reports.StatReportF5_D_For_Teenager import CStatReportF5_D_For_Teenager
        CStatReportF5_D_For_Teenager(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF4_D_For_Teenager_triggered(self):
        from Reports.StatReportF4_D_For_Teenager import CStatReportF4_D_For_Teenager
        CStatReportF4_D_For_Teenager(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReport1NP3000_triggered(self):
        from Reports.StatReport1NP3000 import CStatReport1NP3000
        CStatReport1NP3000(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReport1NP4000_triggered(self):
        from Reports.StatReport1NP4000 import CStatReport1NP4000
        CStatReport1NP4000(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReport1NP5000_triggered(self):
        from Reports.StatReport1NP5000 import CStatReport1NP5000
        CStatReport1NP5000(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReport1NP7000_triggered(self):
        from Reports.StatReport1NP7000 import CStatReport1NP7000
        CStatReport1NP7000(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReport1DD2000_triggered(self):
        from Reports.StatReport1DD2000 import CStatReport1DD2000
        CStatReport1DD2000(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReport1DD3000_triggered(self):
        from Reports.StatReport1DD3000 import CStatReport1DD3000
        CStatReport1DD3000(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReport1DD4000_triggered(self):
        from Reports.StatReport1DD4000 import CStatReport1DD4000
        CStatReport1DD4000(self).exec_()

    @QtCore.pyqtSlot()
    def on_actMUOMSOFTable1_triggered(self):
        from Reports.MUOMSOFTable1 import CMUOMSOFTable1
        CMUOMSOFTable1(self).exec_()

    @QtCore.pyqtSlot()
    def on_actMUOMSOFTable3_triggered(self):
        from Reports.MUOMSOFTable3 import CMUOMSOFTable3
        CMUOMSOFTable3(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportF14App3ksg_triggered(self):
        from Reports.ReportF14App3ksg import CReportF14App3ksg
        CReportF14App3ksg(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportR61Annex11_triggered(self):
        from Reports.ReportR61Annex11 import CReportR61Annex11
        CReportR61Annex11(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReport1DDAll_triggered(self):
        from Reports.StatReport1DDAll import CStatReport1DDAll
        CStatReport1DDAll(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF131ByDoctors_triggered(self):
        from Reports.StatReportF131ByDoctors import CStatReportF131ByDoctors
        CStatReportF131ByDoctors(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF131ByEmployer_triggered(self):
        from Reports.StatReportF131ByEmployer import CStatReportF131ByEmployer
        CStatReportF131ByEmployer(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF131ByRaion_triggered(self):
        from Reports.StatReportF131ByRaion import CStatReportF131ByRaion
        CStatReportF131ByRaion(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF131Raion_triggered(self):
        from Reports.StatReportF131Raion import CStatReportF131Raion
        CStatReportF131Raion(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF131ByDD_triggered(self):
        from Reports.StatReportF131ByDD import CStatReportF131ByDD
        CStatReportF131ByDD(self).exec_()

    @QtCore.pyqtSlot()
    def on_actTimelineForPerson_triggered(self):
        from Reports.TimelineForPerson import CTimelineForPersonEx
        CTimelineForPersonEx(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportFinanceSummary_triggered(self):
        from Reports.ReportFinanceSummary import CReportFinanceSummary
        CReportFinanceSummary(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportVisitByQueue_triggered(self):
        from Reports.ReportVisitByQueue import CReportVisitByQueueMoving
        CReportVisitByQueueMoving(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportVisitByQueueNext_triggered(self):
        from Reports.ReportVisitByQueue import CReportVisitByQueueNext
        CReportVisitByQueueNext(self).exec_()

    @QtCore.pyqtSlot()
    def on_actTimelineForOffices_triggered(self):
        from Reports.TimelineForOffices import CTimelineForOfficesEx
        CTimelineForOfficesEx(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPreRecordDoctors_triggered(self):
        from Reports.PreRecordDoctors import CPreRecordDoctorsEx
        CPreRecordDoctorsEx(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPreRecordUsers_triggered(self):
        from Reports.PreRecordUsers import CPreRecordUsersEx
        CPreRecordUsersEx(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPreRecordSpeciality_triggered(self):
        from Reports.PreRecordSpeciality import CPreRecordSpecialityEx
        CPreRecordSpecialityEx(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPreRecordReport_triggered(self):
        from Reports.PreRecordReport import CPreRecordReport
        CPreRecordReport(self).exec_()

    @QtCore.pyqtSlot()
    def on_actJournalBeforeRecord_triggered(self):
        from Reports.JournalBeforeRecordDialog import CJournalBeforeRecord
        CJournalBeforeRecord(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDailyJournalBeforeRecord_triggered(self):
        from Reports.DailyJournalBeforeRecord import CDailyJournalBeforeRecord
        CDailyJournalBeforeRecord(self).exec_()

    @QtCore.pyqtSlot()
    def on_actUnfinishedEventsByDoctor_triggered(self):
        from Reports.UnfinishedEventsByDoctor import CUnfinishedEventsByDoctor
        CUnfinishedEventsByDoctor(self).exec_()

    @QtCore.pyqtSlot()
    def on_actUnfinishedEventsByMes_triggered(self):
        from Reports.UnfinishedEventsByMes import CUnfinishedEventsByMes
        CUnfinishedEventsByMes(self).exec_()

    @QtCore.pyqtSlot()
    def on_actAnalyticsReportHospitalizedClients_triggered(self):
        from Reports.AnalyticsReportHospitalizedClients import CAnalyticsReportHospitalizedClients
        CAnalyticsReportHospitalizedClients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actAnalyticsReportIncomeAndLeavedClients_triggered(self):
        from Reports.AnalyticsReportIncomeAndLeavedClients import CAnalyticsReportIncomeAndLeavedClients
        CAnalyticsReportIncomeAndLeavedClients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPEDSalaryReports_triggered(self):
        from Reports.PEDSalaryReports import CPEDSalaryReports
        CPEDSalaryReports(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportClientsWithValidPolis_triggered(self):
        from Reports.ReportClientsWithValidPolis import CReportClientsWithValidPolis
        CReportClientsWithValidPolis(self).exec_()

    @QtCore.pyqtSlot()
    def on_actAnalyticsReportAnalysisOfDisease_triggered(self):
        from Reports.AnalyticsReportAnalysisOfDisease import CAnalyticsReportAnalysisOfDisease
        CAnalyticsReportAnalysisOfDisease(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportF30_triggered(self):
        if QtGui.qApp.region() == '23':
            from Reports.ReportF30 import CReportF30_KK
            CReportF30_KK(self).exec_()
        else:
            from Reports.ReportF30 import CReportF30
            CReportF30(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatuonaryF30_3100_triggered(self):
        from Reports.StationaryF30 import CStationaryF30Moving
        CStationaryF30Moving(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatuonaryF30_3101_triggered(self):
        from Reports.StationaryF30 import CStationaryF30_3101
        CStationaryF30_3101(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportF39_triggered(self):
        from Reports.ReportF39 import CReportF39
        CReportF39(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportRecordPersonVisits_triggered(self):
        from Reports.ReportRecordPersonVisitsSetup import CReportRecordPersonVisits
        CReportRecordPersonVisits(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportF39Mod_triggered(self):
        from Reports.ReportF39Mod import CReportF39Mod
        CReportF39Mod(self).exec_()

    @QtCore.pyqtSlot()
    def on_actVeterans_triggered(self):
        from Reports.ReportVeterans import CReportVeterans
        CReportVeterans(self).exec_()

    #Мурманск #3 only
    @QtCore.pyqtSlot()
    def on_actReportVisits_triggered(self):
        from Reports.ReportVisits import CReportVisits
        CReportVisits(self).exec_()

    #Мурманск #3 only
    @QtCore.pyqtSlot()
    def on_actReportDDStudentsInfo_triggered(self):
        from Reports.ReportDDStudentsInfo import CReportDDStudentsInfo
        CReportDDStudentsInfo(self).exec_()

    #Мурманск #3 only
    @QtCore.pyqtSlot()
    def on_actReportDDStudentsResults_triggered(self):
        from Reports.ReportDDStudentsResults import CReportDDStudentsResults
        CReportDDStudentsResults(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPersonVisits_triggered(self):
        from Reports.PersonVisits import CPersonVisits
        CPersonVisits(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPersonSickList_triggered(self):
        from Reports.ReportPersonSickList import CReportPersonSickList
        CReportPersonSickList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPersonSickListNew_triggered(self):
        from Reports.ReportPersonSickList import CReportPersonSickListNew
        CReportPersonSickListNew(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportAcuteInfections_triggered(self):
        from Reports.ReportAcuteInfections import CReportAcuteInfections
        CReportAcuteInfections(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportDailyAcuteInfections_triggered(self):
        from Reports.ReportDailyAcuteInfections import CReportDailyAcuteInfections
        CReportDailyAcuteInfections(self).exec_()

    @QtCore.pyqtSlot()
    def on_actAgeClassification_triggered(self):
        from Reports.ReportAgeClassification import  CReportAgeClassification
        CReportAgeClassification(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportMonthActions_triggered(self):
        from Reports.ReportMonthActions import CReportMonthActions
        CReportMonthActions(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportActionsByOrgStructure_triggered(self):
        from Reports.ReportActionsByOrgStructure import CReportActionsByOrgStructure
        CReportActionsByOrgStructure(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportActionsByServiceType_triggered(self):
        from Reports.ReportActionsByServiceType import CReportActionsByServiceType
        CReportActionsByServiceType(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPeriodontist_triggered(self):
        from Reports.ReportPeriodontist import CReportPeriodontist
        CReportPeriodontist(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportDoneActions_triggered(self):
        from Reports.ReportDoneActions import CReportDoneActions
        CReportDoneActions(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportActionsAndVisits_triggered(self):
        from Reports.ReportActionsAndVisits import CReportActionsAndVisits
        CReportActionsAndVisits(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDailyServicesReport_triggered(self):
        from Reports.DailyServicesReport import CDailyServicesReport
        CDailyServicesReport(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPayers_triggered(self):
        from Reports.ReportPayers import CReportPayers
        CReportPayers(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportClientActions_triggered(self):
        from Reports.ReportClientActions import CReportClientActions
        CReportClientActions(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportActions_triggered(self):
        from Reports.ReportActions import CReportActions
        CReportActions(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportUnderageMedicalExamination_triggered(self):
        from Reports.ReportUnderageMedicalExamination import CReportUnderageMedicalExamination
        CReportUnderageMedicalExamination(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportResultAdditionalConsultation_triggered(self):
        from Reports.ReportUnderageMedicalExamination import CReportResultAdditionalConsultation
        CReportResultAdditionalConsultation(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportResultMedicationBeforeInspection_triggered(self):
        from Reports.ReportUnderageMedicalExamination import CReportResultMedicationBeforeInspection
        CReportResultMedicationBeforeInspection(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportNumberChildrenDisabilities_triggered(self):
        from Reports.ReportUnderageMedicalExamination import CReportNumberChildrenDisabilities
        CReportNumberChildrenDisabilities(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportIndividualProgram_triggered(self):
        from Reports.ReportUnderageMedicalExamination import CReportIndividualProgram
        CReportIndividualProgram(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportImmunizations_triggered(self):
        from Reports.ReportUnderageMedicalExamination import CReportImmunizations
        CReportImmunizations(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportUnderagePhysicalDevelopment_triggered(self):
        from Reports.ReportUnderageMedicalExamination import CReportUnderagePhysicalDevelopment
        CReportUnderagePhysicalDevelopment(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportMedicalGroups_triggered(self):
        from Reports.ReportUnderageMedicalExamination import CReportMedicalGroups
        CReportMedicalGroups(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportHealthGroups_triggered(self):
        from Reports.ReportUnderageMedicalExamination import CReportHealthGroups
        CReportHealthGroups(self).exec_()

    @QtCore.pyqtSlot()
    def on_actNewFinanceSum_triggered(self):
        from Reports.ConsolidatedFinanceSum import CConsolidatedFinanceSumSetup
        CConsolidatedFinanceSumSetup(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReferralForHospitalization_triggered(self):
        from Reports.ReferralForHospitalization import CReferralForHospitalization
        CReferralForHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actExposedServicesReport_triggered(self):
        from Reports.ExposedServicesReportsSetup import CExposedServicesReports
        CExposedServicesReports(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRemoveReferralForHospitalization_triggered(self):
        from Reports.ReferralForHospitalization import CRemoveReferralForHospitalization
        CRemoveReferralForHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actUETService_triggered(self):
        from Reports.ReportActionsServiceCutaway import CReportActionsServiceCutaway
        CReportActionsServiceCutaway(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportOnPerson_triggered(self):
        from Reports.ReportOnPerson           import CReportOnPerson
        CReportOnPerson(self).exec_()

    @QtCore.pyqtSlot()
    def on_actVisitsServiceUET_triggered(self):
        from Reports.ReportVisitsServiceCutaway  import CReportVisitsServiceCutaway
        CReportVisitsServiceCutaway(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFinanceSummaryByDoctors_triggered(self):
        from Reports.FinanceSummaryByDoctors  import CFinanceSummaryByDoctorsEx
        CFinanceSummaryByDoctorsEx(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFinanceSummaryByServices_triggered(self):
        from Reports.FinanceSummaryByServices import CFinanceSummaryByServicesEx
        CFinanceSummaryByServicesEx(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFinanceSumByServicesExpenses_triggered(self):
        from Reports.FinanceSumByServicesExpenses import CFinanceSumByServicesExpensesEx
        CFinanceSumByServicesExpensesEx(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFinanceSummaryByRejections_triggered(self):
        from Reports.FinanceSummaryByRejections import CFinanceSummaryByRejectionsEx
        CFinanceSummaryByRejectionsEx(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFinanceSummaryByLoadOnDoctor_triggered(self):
        from Reports.FinanceSummaryByLoadOnDoctor import CReportFinanceSummaryByLoadOnDoctor
        CReportFinanceSummaryByLoadOnDoctor(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportClients_triggered(self):
        from Reports.ReportClients            import CReportClients
        CReportClients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportTreatments_triggered(self):
        from Reports.ReportTreatments         import CReportTreatments
        CReportTreatments(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEventResultSurvey_triggered(self):
        from Reports.EventResultSurvey import CEventResultSurvey
        CEventResultSurvey(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEventResultList_triggered(self):
        from Reports.EventResultList import CReportEventResultList
        CReportEventResultList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportSocStatus_triggered(self):
        from Reports.SocStatus                import CSocStatus
        CSocStatus(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPNDClientsRegistry_triggered(self):
        from Reports.ReportPNDClientsRegistry import CReportPNDClientsRegistry
        CReportPNDClientsRegistry(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPNDClientsRegistryByEvent_triggered(self):
        from Reports.ReportPNDClientsRegistry import CReportPNDClientsRegistry
        CReportPNDClientsRegistry(self, mode=1).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPNDClientsRegistryByDisability_triggered(self):
        from Reports.ReportPNDClientsRegistry import CReportPNDClientsRegistry
        CReportPNDClientsRegistry(self, mode=2).exec_()

    @QtCore.pyqtSlot()
    def on_actSickRateSurvey_triggered(self):
        from Reports.SickRateSurvey           import CSickRateSurvey
        CSickRateSurvey(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFactorRateSurvey_triggered(self):
        from Reports.FactorRateSurvey         import CFactorRateSurvey
        CFactorRateSurvey(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF12_triggered(self):
        from Reports.StatReportF12 import CStatReportF12
        CStatReportF12(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF57_triggered(self):
        from Reports.StatReportF57            import CStatReportF57
        CStatReportF57(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF57New_triggered(self):
        from Reports.StatReportF57New          import CStatReportF57New
        CStatReportF57New(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF57Temporary_triggered(self):
        from Reports.StatReportF57Temporary          import CStatReportF57Temporary
        CStatReportF57Temporary(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF63_triggered(self):
        from Reports.StatReportF63            import CStatReportF63
        CStatReportF63(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStatReportF71_triggered(self):
        from Reports.StatReportF71 import CStatReportF71
        CStatReportF71(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportMentalDisorderF10_triggered(self):
        from Reports.ReportF10 import CReportF10
        CReportF10(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDispObservationList_triggered(self):
        from Reports.DispObservationList import CDispObservationList
        CDispObservationList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDispObservationListChildren_triggered(self):
        from Reports.DispObservationList import CDispObservationList
        CDispObservationList(self, True).exec_()

    @QtCore.pyqtSlot()
    def on_actDispObservationSurvey_triggered(self):
        from Reports.DispObservationSurvey import CDispObservationSurvey
        CDispObservationSurvey(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDispObservationSurveyChildren_triggered(self):
        from Reports.DispObservationSurvey import CDispObservationSurvey
        CDispObservationSurvey(self, True).exec_()

    @QtCore.pyqtSlot()
    def on_actTempInvalidList_triggered(self):
        from Reports.TempInvalidList import CTempInvalidList
        CTempInvalidList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actTempInvalidSurvey_triggered(self):
        from Reports.TempInvalidSurvey import CTempInvalidSurvey
        CTempInvalidSurvey(self).exec_()

    @QtCore.pyqtSlot()
    def on_actTempInvalidF16_triggered(self):
        from Reports.TempInvalidF16 import CTempInvalidF16
        CTempInvalidF16(self).exec_()

    @QtCore.pyqtSlot()
    def on_actF13_triggered(self):
        from Reports.ReportF13 import CReportF13
        CReportF13(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReHospitalization_triggered(self):
        from Reports.ReportReHospitalization import CReportReHospitalization
        CReportReHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportBasicIndicators_triggered(self):
        from Reports.ReportBasicIndicators import CReportBasicIndicators
        CReportBasicIndicators(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRegisterSickLeave_triggered(self):
        from Reports.ReportRegisterSickLeave import CReportRegisterSickLeave
        CReportRegisterSickLeave(self).exec_()

    @QtCore.pyqtSlot()
    def on_actSendPlanOrdersClinic_triggered(self):
        from Reports.ReportReferralForHospitalization import CReportSendPlanOrdersClinic
        CReportSendPlanOrdersClinic(self).exec_()

    @QtCore.pyqtSlot()
    def on_actSendFactOrdersHospital_triggered(self):
        from Reports.ReportReferralForHospitalization import CReportSendFactOrdersHospital
        CReportSendFactOrdersHospital(self).exec_()

    @QtCore.pyqtSlot()
    def on_actSendOrdersHospitalUrgently_triggered(self):
        from Reports.ReportReferralForHospitalization import CReportSendOrdersHospitalUrgently
        CReportSendOrdersHospitalUrgently(self).exec_()

    @QtCore.pyqtSlot()
    def on_actSendOrdersLeave_triggered(self):
        from Reports.ReportReferralForHospitalization import CReportSendOrdersLeave
        CReportSendOrdersLeave(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPersonTimetable_triggered(self):
        from Reports.ReportPersonTimetable import CReportPersonTimetable
        CReportPersonTimetable(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPrintAnalysisServicesByCompany_triggered(self):
        from Reports.ReportAnalysisServices import CReportAnalysisServicesByCompany
        CReportAnalysisServicesByCompany(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPrintAnalysisServicesByDiagnosis_triggered(self):
        from Reports.ReportAnalysisServices import CReportAnalysisServicesByDiagnosis
        CReportAnalysisServicesByDiagnosis(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportSickLeaveByPerson_triggered(self):
        from Reports.ReportSickLeaveByPerson import CReportSickLeaveByPerson
        CReportSickLeaveByPerson(self).exec_()

    @QtCore.pyqtSlot()
    def on_actTempInvalidExpert_triggered(self):
        from Reports.TempInvalidExpert import CTempInvalidExpert
        CTempInvalidExpert(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDeathList_triggered(self):
        from Reports.DeathList import CDeathList
        CDeathList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDeathReport_triggered(self):
        from Reports.DeathReport import CDeathReport
        CDeathReport(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDeathSurvey_triggered(self):
        from Reports.DeathSurvey import CDeathSurvey
        CDeathSurvey(self).exec_()

    @QtCore.pyqtSlot()
    def on_actWorkload_triggered(self):
        from Reports.Workload import CWorkload
        CWorkload(self).exec_()

    @QtCore.pyqtSlot()
    def on_actAttachedContingent_triggered(self):
        from Reports.AttachedContingent import CAttachedContingent
        CAttachedContingent(self).exec_()

    @QtCore.pyqtSlot()
    def on_actAttachingMotion_triggered(self):
        from Reports.ReportAttachingMotion import CReportAttachingMotion
        CReportAttachingMotion(self).exec_()

    @QtCore.pyqtSlot()
    def on_actForma007Moving_triggered(self):
        from Reports.StationaryF007 import CStationaryF007Moving
        CStationaryF007Moving(self).exec_()

    @QtCore.pyqtSlot()
    def on_actForma007Moving2013_triggered(self):
        from Reports.StationaryF007 import CStationaryF007Moving2013
        CStationaryF007Moving2013(self).exec_()

    @QtCore.pyqtSlot()
    def on_actForma007ClientList_triggered(self):
        from Reports.StationaryF007 import CStationaryF007ClientList
        CStationaryF007ClientList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actForma007ClientList2013_triggered(self):
        from Reports.StationaryF007 import CStationaryF007ClientList2013
        CStationaryF007ClientList2013(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaF016_triggered(self):
        from Reports.StationaryF016 import CStationaryF016
        CStationaryF016(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaF007DC_triggered(self):
        from Reports.StationaryF007DC import CStationaryF007DC
        CStationaryF007DC(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaAdultF142000_triggered(self):
        from Reports.StationaryF014 import CStationaryF142000_Adults
        CStationaryF142000_Adults(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaChildrenF142000_triggered(self):
        from Reports.StationaryF014 import CStationaryF142000_Children
        CStationaryF142000_Children(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStationaryReportF14_triggered(self):
        from Reports.ReportF14 import CStationaryReportF14
        CStationaryReportF14(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaSeniorF142000_triggered(self):
        from Reports.StationaryF014 import CStationaryF142000_Seniors
        CStationaryF142000_Seniors(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStationaryF142100_triggered(self):
        from Reports.StationaryF014 import CStationaryF142100
        CStationaryF142100(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaF0143000_triggered(self):
        from Reports.StationaryF014 import CStationaryF143000
        CStationaryF143000(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaF0144000_triggered(self):
        from Reports.StationaryF014 import CStationaryF144000
        CStationaryF144000(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaF0144001_triggered(self):
        from Reports.StationaryF014 import CStationaryF144001
        CStationaryF144001(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaF0144100_triggered(self):
        from Reports.StationaryF014 import CStationaryF144100
        CStationaryF144100(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaF0144200_triggered(self):
        from Reports.StationaryF014 import CStationaryF144200
        CStationaryF144200(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaF0144201_triggered(self):
        from Reports.StationaryF014 import CStationaryF144201
        CStationaryF144201(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaF0144202_triggered(self):
        from Reports.StationaryF014 import CStationaryF144202
        CStationaryF144202(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaF0144400_triggered(self):
        from Reports.StationaryF014 import CStationaryF144400
        CStationaryF144400(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFormaF32_triggered(self):
        from Reports.ReportF32 import CReportF32
        CReportF32(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportF14DS_stat_triggered(self):
        from Reports.Report14DS_2000 import CReportF14DS
        CReportF14DS(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportF14DS_ambul_triggered(self):
        from Reports.Report14DS_2000_part2 import CReportF14DS
        CReportF14DS(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReport2500_2600_triggered(self):
        from Reports.Report14DS_2500_2600 import CReportF14DS
        CReportF14DS(self).exec_()

    @QtCore.pyqtSlot()
    def on_actOnePolyclinicF14DC_triggered(self):
        from Reports.StationaryF14DC import CStationaryOnePolyclinicF14DC
        CStationaryOnePolyclinicF14DC(self).exec_()

    @QtCore.pyqtSlot()
    def on_actOneHouseF14DC_triggered(self):
        from Reports.StationaryF14DC import CStationaryOneHouseF14DC
        CStationaryOneHouseF14DC(self).exec_()

    @QtCore.pyqtSlot()
    def on_actStationaryReportMoved_triggered(self):
        from Reports.StationaryReportMoved import CStationaryReportMoved
        CStationaryReportMoved(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEmergency2000_triggered(self):
        from Reports.ReportEmergencyF40 import CReportEmergencyF402000
        CReportEmergencyF402000(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEmergency2001_triggered(self):
        from Reports.ReportEmergencyF40 import CReportEmergencyF402001
        CReportEmergencyF402001(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEmergency2100_triggered(self):
        from Reports.ReportEmergencyF40 import CReportEmergencyF402100
        CReportEmergencyF402100(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEmergency2500_triggered(self):
        from Reports.ReportEmergencyF40 import CReportEmergencyF402500
        CReportEmergencyF402500(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEmergencyAdditionally_triggered(self):
        from Reports.ReportEmergencyF40 import CReportEmergencyAdditionally
        CReportEmergencyAdditionally(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEmergencyTalonSignal_triggered(self):
        from Reports.ReportEmergencyF40 import CReportEmergencyTalonSignal
        CReportEmergencyTalonSignal(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportF14DS_vzroslye_triggered(self):
        from Reports.Report14DS_3000 import CReportF14DS
        CReportF14DS(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportF14DS_deti_triggered(self):
        from Reports.Report14DS_3500 import CReportF14DS
        CReportF14DS(self).exec_()

    @QtCore.pyqtSlot()
    def on_actTwoAdultPoliclinicF14DC_triggered(self):
        from Reports.StationaryF14DC          import CStationaryTwoAdultPoliclinicF14DC
        CStationaryTwoAdultPoliclinicF14DC(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPopulationStructure_triggered(self):
        from Reports.PopulationStructureNew      import CPopulationStructure
        CPopulationStructure(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPopulationStructureDetailed_triggered(self):
        from Reports.PopulationStructureDetailed      import CPopulationStructureDetailed
        CPopulationStructureDetailed(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDispanserRegistry_triggered(self):
        from Reports.DispanserRegistry        import CDispanserRegistry
        CDispanserRegistry(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPeriodontist_triggered(self):
        from Reports.ReportPeriodontist import CReportPeriodontist
        CReportPeriodontist(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportMonitoringOIM_triggered(self):
        from Reports.ReportMonitoringOIM import CReportMonitoringOIM
        CReportMonitoringOIM(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPrimaryRepeatHospitalization_triggered(self):
        from Reports.ReportPrimaryRepeatHospitalization import CReportPrimaryRepeatHospitalization
        CReportPrimaryRepeatHospitalization(self, True).exec_()

    @QtCore.pyqtSlot()
    def on_actReportEventByMKB_triggered(self):
        from Reports.ReportPrimaryRepeatHospitalization import CReportPrimaryRepeatHospitalization
        CReportPrimaryRepeatHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportSickList_triggered(self):
        from Reports.ReportSickList import CReportSickList
        CReportSickList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actFinanceForma14DC_triggered(self):
        from Reports.StationaryF14DC import CStationaryTypeFinanceTypeF14DC
        CStationaryTypeFinanceTypeF14DC(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPopulation_triggered(self):
        pass
        #from Reports.Population               import CPopulation
        #CPopulation(self).exec_()

    @QtCore.pyqtSlot()
    def on_actGenRep_triggered(self):
        from Reports.ReportByTemplate import CReportByTemplate
        CReportByTemplate(self).exec_()
        return
        genRep = forceString(QtGui.qApp.preferences.appPrefs['extGenRep'])
        if genRep:
            prg=QtGui.qApp.execProgram(u'"%s"' % genRep)
            if not prg[0]:
                QtGui.QMessageBox.critical(self,
                                       u'Внимание!',
                                       u'Не удалось запустить "%s"' % genRep,
                                       QtGui.QMessageBox.Close)
            if prg[2]:
                QtGui.QMessageBox.critical(self,
                                       u'Внимание!',
                                       u'Ошибка при выполнении "%s"' % genRep,
                                       QtGui.QMessageBox.Close)
        else:
            QtGui.QMessageBox.critical(self,
                                    u'Ошибка!',
                                    u'Не указан исполнимый файл генератора отчетов\n'+
                                    u'Смотрите пункт меню "Настройки.Умолчания", закладка "Прочие настройки",\n'+
                                    u'строка "Внешний генератор отчетов".',
                                    QtGui.QMessageBox.Close)

    @QtCore.pyqtSlot()
    def on_actAreas_triggered(self):
        pass

    @QtCore.pyqtSlot()
    def on_actKLADR_triggered(self):
        pass

    @QtCore.pyqtSlot()
    def on_actMKB_triggered(self):
        from RefBooks.MKB import CMKBList
        CMKBList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actMKBSubclass_triggered(self):
        from RefBooks.MKBSubclass import CMKBSubclass
        CMKBSubclass(self).exec_()

    @QtCore.pyqtSlot()
    def on_actMKBMorphology_triggered(self):
        from RefBooks.RBMKBMorphology import CRBMKBMorphologyList
        CRBMKBMorphologyList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actBank_triggered(self):
        from Orgs.Banks import CBanksList
        CBanksList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actContract_triggered(self):
        from Orgs.Contracts import CContractsList
        CContractsList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actImportEISOMS_SMP_triggered(self):
        from Exchange.ImportEISOMS_SMP import ImportEISOMS_SMP
        ImportEISOMS_SMP(self)

    @QtCore.pyqtSlot()
    def on_actECROther_triggered(self):
        from library.CashRegister.CashRegisterWindow import getECashRegister
#        availableOperations = CCashRegisterWindow.ClippingOperation \
#                               | CCashRegisterWindow.ReportOperation | CCashRegisterWindow.OpenSessionOperation \
#                               | CCashRegisterWindow.CashOperation | CCashRegisterWindow.ECRSelectOperation
        ecrDialog = getECashRegister(self)
        ecrDialog.setExportInfo({
                                 'isNaturalPerson' : False
                                 })
        ecrDialog.exec_()
        setPref(QtGui.qApp.preferences.appPrefs, 'ECRSettings', ecrDialog.preferences())

    @QtCore.pyqtSlot()
    def on_actOrganisation_triggered(self):
        from Orgs.Orgs import COrgsList
        COrgsList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actActionPropertyTemplate_triggered(self):
        from RefBooks.ActionPropertyTemplate import CActionPropertyTemplateList
        CActionPropertyTemplateList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBActionShedule_triggered(self):
        from RefBooks.RBActionShedule import CRBActionSheduleList
        CRBActionSheduleList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actActionType_triggered(self):
        from RefBooks.ActionType import CActionTypeList
        CActionTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBActionTypeIncompatibilities_triggered(self):
        from RefBooks.RBActionTypeIncompatibilities import CRBActionTypeIncompatibilitiesList
        CRBActionTypeIncompatibilitiesList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBActionTypeSimilarity_triggered(self):
        from RefBooks.RBActionTypeSimilarity import CRBActionTypeSimilarityList
        CRBActionTypeSimilarityList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actQuotaType_triggered(self):
        from RefBooks.QuotaType import CQuotaTypeList
        CQuotaTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBAgreementType_triggered(self):
        from RefBooks.RBAgreementType import CRBAgreementTypeList
        CRBAgreementTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actBlankType_triggered(self):
        from RefBooks.RBBlanksDialog import CBlanksList
        CBlanksList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actCureMethod_triggered(self):
        from RefBooks.RBCureMethod import CRBCureMethod
        CRBCureMethod(self).exec_()

    @QtCore.pyqtSlot()
    def on_actCureType_triggered(self):
        from RefBooks.RBCureType import CRBCureType
        CRBCureType(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPatientModel_triggered(self):
        from RefBooks.RBPatientModel import CRBPatientModel
        CRBPatientModel(self).exec_()

    @QtCore.pyqtSlot()
    def on_actActionTemplate_triggered(self):
        from RefBooks.ActionTemplate import CActionTemplateList
        CActionTemplateList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEventType_triggered(self):
        from RefBooks.EventType import CEventTypeList
        CEventTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPersonal_triggered(self):
        from RefBooks.Person import CPersonList
        CPersonList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBActionAssistantType_triggered(self):
        from RefBooks.RBActionAssistantType import CRBActionAssistantTypeList
        CRBActionAssistantTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actOrgStructure_triggered(self):
        from RefBooks.OrgStructure import COrgStructureList
        COrgStructureList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBAccountExportFormat_triggered(self):
        from RefBooks.RBAccountExportFormat import CRBAccountExportFormatList
        CRBAccountExportFormatList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBAccountingSystem_triggered(self):
        from RefBooks.RBAccountingSystem import CRBAccountingSystemList
        CRBAccountingSystemList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBCounter_triggered(self):
        from RefBooks.RBCounter import CRBCounterList
        CRBCounterList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBAttachType_triggered(self):
        from RefBooks.RBAttachType import CRBAttachTypeList
        CRBAttachTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBDetachmentReason_triggered(self):
        from RefBooks.RBDetachmentReason import CRBDetachmentReasonList
        CRBDetachmentReasonList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBContactType_triggered(self):
        from RefBooks.RBContactType import CRBContactTypeList
        CRBContactTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBDiagnosisType_triggered(self):
        from RefBooks.RBDiagnosisType import CRBDiagnosisTypeList
        CRBDiagnosisTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBDiseaseCharacter_triggered(self):
        from RefBooks.RBDiseaseCharacter import CRBDiseaseCharacterList
        CRBDiseaseCharacterList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyBrigade_triggered(self):
        from RefBooks.RBEmergencyBrigade import CRBEmergencyBrigadeList
        CRBEmergencyBrigadeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyCauseCall_triggered(self):
        from RefBooks.RBEmergencyCauseCall import CRBEmergencyCauseCallList
        CRBEmergencyCauseCallList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyTransferredTransportation_triggered(self):
        from RefBooks.RBEmergencyTransferredTransportation import CRBEmergencyTransferredTransportationList
        CRBEmergencyTransferredTransportationList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyPlaceReceptionCall_triggered(self):
        from RefBooks.RBEmergencyPlaceReceptionCall import CRBEmergencyPlaceReceptionCallList
        CRBEmergencyPlaceReceptionCallList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyReceivedCall_triggered(self):
        from RefBooks.RBEmergencyReceivedCall import CRBEmergencyReceivedCallList
        CRBEmergencyReceivedCallList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyReasondDelays_triggered(self):
        from RefBooks.RBEmergencyReasondDelays import CRBEmergencyReasondDelaysList
        CRBEmergencyReasondDelaysList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyResult_triggered(self):
        from RefBooks.RBEmergencyResult import CRBEmergencyResultList
        CRBEmergencyResultList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyAccident_triggered(self):
        from RefBooks.RBEmergencyAccident import CRBEmergencyAccidentList
        CRBEmergencyAccidentList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyDeath_triggered(self):
        from RefBooks.RBEmergencyDeath import CRBEmergencyDeathList
        CRBEmergencyDeathList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyEbriety_triggered(self):
        from RefBooks.RBEmergencyEbriety import CRBEmergencyEbrietyList
        CRBEmergencyEbrietyList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyDiseased_triggered(self):
        from RefBooks.RBEmergencyDiseased import CRBEmergencyDiseasedList
        CRBEmergencyDiseasedList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyPlaceCall_triggered(self):
        from RefBooks.RBEmergencyPlaceCall import CRBEmergencyPlaceCallList
        CRBEmergencyPlaceCallList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyMethodTransportation_triggered(self):
        from RefBooks.RBEmergencyMethodTransportation import CRBEmergencyMethodTransportationList
        CRBEmergencyMethodTransportationList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEmergencyTypeAsset_triggered(self):
        from RefBooks.RBEmergencyTypeAsset import CRBEmergencyTypeAssetList
        CRBEmergencyTypeAssetList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBMealTime_triggered(self):
        from RefBooks.RBMealTime import CRBMealTime
        CRBMealTime(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBMeal_triggered(self):
        from RefBooks.RBMeal import CRBMeal
        CRBMeal(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBDiet_triggered(self):
        from RefBooks.RBDiet import CRBDiet
        CRBDiet(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBMenu_triggered(self):
        from RefBooks.RBMenu import CRBMenu
        CRBMenu(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRecativeClient_triggered(self):
        from RefBooks.RBRelativeEditor import CRBRelativeList
        CRBRelativeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBDiseaseStage_triggered(self):
        from RefBooks.RBDiseaseStage import CRBDiseaseStageList
        CRBDiseaseStageList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBDiseasePhases_triggered(self):
        from RefBooks.RBDiseasePhases import CRBDiseasePhasesList
        CRBDiseasePhasesList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBDispanser_triggered(self):
        from RefBooks.RBDispanser import CRBDispanserList
        CRBDispanserList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBDocumentType_triggered(self):
        from RefBooks.RBDocumentType import CRBDocumentTypeList
        CRBDocumentTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBDocumentTypeGroup_triggered(self):
        from RefBooks.RBDocumentTypeGroup import CRBDocumentTypeGroupList
        CRBDocumentTypeGroupList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEventTypePurpose_triggered(self):
        from RefBooks.RBEventTypePurpose import CRBEventTypePurposeList
        CRBEventTypePurposeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEventProfile_triggered(self):
        from RefBooks.RBEventProfile import CRBEventProfileList
        CRBEventProfileList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEventGoal_triggered(self):
        from RefBooks.RBEventGoal import CRBEventGoalList
        CRBEventGoalList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBFinance_triggered(self):
        from RefBooks.RBFinance import CRBFinanceList
        CRBFinanceList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBAccountType_triggered(self):
        from RefBooks.RBAccountType import CRBAccountTypeList
        CRBAccountTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBExpenseServiceItem_triggered(self):
        from RefBooks.RBExpenseServiceItem import CRBExpenseServiceItemList
        CRBExpenseServiceItemList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBHealthGroup_triggered(self):
        from RefBooks.RBHealthGroup import CRBHealthGroupList
        CRBHealthGroupList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBMedicalGroup_triggered(self):
        from RefBooks.RBMedicalGroup import CRBMedicalGroupList
        CRBMedicalGroupList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBHurtFactorType_triggered(self):
        from RefBooks.RBHurtFactorType import CRBHurtFactorTypeList
        CRBHurtFactorTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBHurtType_triggered(self):
        from RefBooks.RBHurtType import CRBHurtTypeList
        CRBHurtTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBMedicalAidKind_triggered(self):
        from RefBooks.RBMedicalAidKind import CRBMedicalAidKindList
        CRBMedicalAidKindList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEQueueType_triggered(self):
        from RefBooks.RBEQueueType import CRBEQueueType
        CRBEQueueType(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBDeferredQueueStatus_triggered(self):
        from RefBooks.RBDeferredQueueStatus import CRBDeferredQueueStatus
        CRBDeferredQueueStatus(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBMedicalAidType_triggered(self):
        from RefBooks.RBMedicalAidType import CRBMedicalAidTypeList
        CRBMedicalAidTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBMedicalAidProfile_triggered(self):
        from RefBooks.RBMedicalAidProfile import CRBMedicalAidProfileList
        CRBMedicalAidProfileList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBMesSpecification_triggered(self):
        from RefBooks.RBMesSpecification import CRBMesSpecificationList
        CRBMesSpecificationList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBMedicalAidUnit_triggered(self):
        from RefBooks.RBMedicalAidUnit import CRBMedicalAidUnitList
        CRBMedicalAidUnitList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBNet_triggered(self):
        from RefBooks.RBNet import CRBNetList
        CRBNetList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBPaidServices_triggered(self):
        from RefBooks.RBAssignedContracts import CRBPaidServicesList
        CRBPaidServicesList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBClinicalTrials_triggered(self):
        from RefBooks.RBAssignedContracts import CRBClinicalTrialsList
        CRBClinicalTrialsList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBNomenclatureClass_triggered(self):
        from RefBooks.RBNomenclatureClass import CRBNomenclatureClassList
        CRBNomenclatureClassList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportActionsWithLatePayment_triggered(self):
        from Reports.ReportActionsWithLatePayment import CReportActionsWithLatePayment
        CReportActionsWithLatePayment(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportContractsRegistry_triggered(self):
        from Reports.ReportContractsRegistry import CReportContractsRegistry
        CReportContractsRegistry(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBNomenclatureKind_triggered(self):
        from RefBooks.RBNomenclatureKind import CRBNomenclatureKindList
        CRBNomenclatureKindList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBNomenclatureType_triggered(self):
        from RefBooks.RBNomenclatureType import CRBNomenclatureTypeList
        CRBNomenclatureTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBNomenclature_triggered(self):
        from RefBooks.RBNomenclature import CRBNomenclatureList
        CRBNomenclatureList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBStockRecipe_triggered(self):
        from RefBooks.RBStockRecipe import CRBStockRecipeList
        CRBStockRecipeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBFormularies_triggered(self):
        from RefBooks.RBFormularies import CRBFormulariesList
        CRBFormulariesList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBDloFormularies_triggered(self):
        from RefBooks.RBDloFormularies import CRBDloFormulariesList
        CRBDloFormulariesList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBMedicines_triggered(self):
        from RefBooks.RBMedicines import CRBMedicinesList
        CRBMedicinesList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBMedicinesGroup_triggered(self):
        from RefBooks.RBMedicinesGroup import CRBMedicinesGroupsList
        CRBMedicinesGroupsList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBTissueType_triggered(self):
        from RefBooks.RBTissueType import CRBTissueTypeList
        CRBTissueTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBOKFS_triggered(self):
        from RefBooks.RBOKFS import CRBOKFSList
        CRBOKFSList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBOKPF_triggered(self):
        from RefBooks.RBOKPF import CRBOKPFList
        CRBOKPFList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBPayRefuseType_triggered(self):
        from RefBooks.RBPayRefuseType import CRBPayRefuseTypeList
        CRBPayRefuseTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBCashOperation_triggered(self):
        from RefBooks.RBCashOperation import CRBCashOperationList
        CRBCashOperationList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBPolicyKind_triggered(self):
        from RefBooks.RBPolicyKind import CRBPolicyKindList
        CRBPolicyKindList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBPolicyType_triggered(self):
        from RefBooks.RBPolicyType import CRBPolicyTypeList
        CRBPolicyTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBPost_triggered(self):
        from RefBooks.RBPost import CRBPostList
        CRBPostList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBActivity_triggered(self):
        from RefBooks.RBActivity import CRBActivityList
        CRBActivityList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBPrintTemplate_triggered(self):
        from RefBooks.RBPrintTemplate import CRBPrintTemplate
        CRBPrintTemplate(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBReasonOfAbsence_triggered(self):
        from RefBooks.RBReasonOfAbsence import CRBReasonOfAbsenceList
        CRBReasonOfAbsenceList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBHospitalBedProfile_triggered(self):
        from RefBooks.RBHospitalBedProfile import CRBHospitalBedProfileList
        CRBHospitalBedProfileList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBJobType_triggered(self):
        from RefBooks.RBJobType import CRBJobTypeList
        CRBJobTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBResult_triggered(self):
        from RefBooks.RBResult import CRBResultList
        CRBResultList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBDiagnosticResult_triggered(self):
        from RefBooks.RBDiagnosticResult import CRBDiagnosticResultList
        CRBDiagnosticResultList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBScene_triggered(self):
        from RefBooks.RBScene import CRBSceneList
        CRBSceneList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBService_triggered(self):
        from RefBooks.RBService import CRBServiceList
        CRBServiceList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBServiceGroup_triggered(self):
        from RefBooks.RBServiceGroup import CRBServiceGroupList
        CRBServiceGroupList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBServiceCategory_triggered(self):
        from RefBooks.RBServiceCategory import CRBServiceCategoryList
        CRBServiceCategoryList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actMilitaryUnits_triggered(self):
        from RefBooks.KLADRMilitaryUnits import CKLADRMilitaryUnitsList
        CKLADRMilitaryUnitsList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBSocStatusClass_triggered(self):
        from RefBooks.RBSocStatusClass import CRBSocStatusClassList
        CRBSocStatusClassList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBSocStatusType_triggered(self):
        from RefBooks.RBSocStatusType import CRBSocStatusTypeList
        CRBSocStatusTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBSpeciality_triggered(self):
        from RefBooks.RBSpeciality import CRBSpecialityList
        CRBSpecialityList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBTariffCategory_triggered(self):
        from RefBooks.RBTariffCategory import CRBTariffCategoryList
        CRBTariffCategoryList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBTempInvalidDocument_triggered(self):
        from RefBooks.RBTempInvalidDocument import CRBTempInvalidDocumentList
        CRBTempInvalidDocumentList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBTempInvalidBreak_triggered(self):
        from RefBooks.RBTempInvalidBreak import CRBTempInvalidBreakList
        CRBTempInvalidBreakList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBBloodType_triggered(self):
        from RefBooks.RBBloodType import CRBBloodTypeList
        CRBBloodTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBImageMap_triggered(self):
        from RefBooks.RBImageMap import CRBImageMapList
        CRBImageMapList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBTempInvalidReason_triggered(self):
        from RefBooks.RBTempInvalidReason import CRBTempInvalidReasonList
        CRBTempInvalidReasonList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBTempInvalidExtraReason_triggered(self):
        from RefBooks.RBTempInvalidExtraReason import CRBTempInvalidExtraReasonList
        CRBTempInvalidExtraReasonList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBTempInvalidRegime_triggered(self):
        from RefBooks.RBTempInvalidRegime import CRBTempInvalidRegimeList
        CRBTempInvalidRegimeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBTempInvalidResult_triggered(self):
        from RefBooks.RBTempInvalidResult import CRBTempInvalidResultList
        CRBTempInvalidResultList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBTempInvalidDuplicateReason_triggered(self):
        from RefBooks.RBTempInvalidDuplicateReason import CRBTempInvalidDuplicateReasonList
        CRBTempInvalidDuplicateReasonList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBComplain_triggered(self):
        from RefBooks.RBComplain import CRBComplainList
        CRBComplainList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBThesaurus_triggered(self):
        from RefBooks.RBThesaurus import CRBThesaurus
        CRBThesaurus(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBTraumaType_triggered(self):
        from RefBooks.RBTraumaType import CRBTraumaTypeList
        CRBTraumaTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBUnit_triggered(self):
        from RefBooks.RBUnit import CRBUnitList
        CRBUnitList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBVisitType_triggered(self):
        from RefBooks.RBVisitType import CRBVisitTypeList
        CRBVisitTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBTest_triggered(self):
        from RefBooks.RBTest import CRBTestList
        CRBTestList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBTestGroup_triggered(self):
        from RefBooks.RBTestGroup import CRBTestGroupList
        CRBTestGroupList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBLaboratory_triggered(self):
        from RefBooks.RBLaboratory import CRBLaboratoryList
        CRBLaboratoryList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBSuiteReagent_triggered(self):
        from RefBooks.RBSuiteReagent import CRBSuiteReagentList
        CRBSuiteReagentList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEquipmentType_triggered(self):
        from RefBooks.RBEquipmentType import CRBEquipmentTypeList
        CRBEquipmentTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBEquipment_triggered(self):
        from RefBooks.RBEquipment import CRBEquipmentList
        dlg = CRBEquipmentList(self)
        dlg.setEditableJournal(QtGui.qApp.userHasAnyRight([urAccessEquipmentMaintenanceJournal, urAccessRefBooks]))
        dlg.exec_()

    @QtCore.pyqtSlot()
    def on_actRBContainerType_triggered(self):
        from RefBooks.RBContainerType import CRBContainerTypeList
        CRBContainerTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBLocationCardType_triggered(self):
        from RefBooks.RBLocationCardType import CRBLocationCardTypeList
        CRBLocationCardTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBHospitalBedsLocationCardType_triggered(self):
        from RefBooks.RBHospitalBedsLocationCardType import CRBHospitalBedsLocationCardTypeList
        CRBHospitalBedsLocationCardTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBInfoSource_triggered(self):
        from RefBooks.RBInfoSource import CRBInfoSourceList
        CRBInfoSourceList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actRBStatusObservationClientType_triggered(self):
        from RefBooks.RBStatusObservationClientType import CRBStatusObservationClientTypeList
        CRBStatusObservationClientTypeList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEventsCheck_triggered(self):
        from DataCheck.CheckEvents import CEventsCheck
        CEventsCheck(self).exec_()

    @QtCore.pyqtSlot()
    def on_actControlDiagnosis_triggered(self):
        from DataCheck.LogicalControlDiagnosis import CControlDiagnosis
        CControlDiagnosis(self).exec_()

    @QtCore.pyqtSlot()
    def on_actControlDoubles_triggered(self):
        from DataCheck.LogicalControlDoubles import CControlDoubles
        dlg = CControlDoubles(self)
        dlg.setTemplateDir(forceStringEx(QtGui.qApp.preferences.appPrefs.get('controlDoubles', '')))
        dlg.exec_()
        QtGui.qApp.preferences.appPrefs['controlDoubles'] = dlg.templateDir()

    @QtCore.pyqtSlot()
    def on_actControlMes_triggered(self):
        from DataCheck.LogicalControlMes import CLogicalControlMes
        CLogicalControlMes(self).exec_()

    @QtCore.pyqtSlot()
    def on_actClientsCheck_triggered(self):
        from DataCheck.CheckClients import ClientsCheck
        ClientsCheck(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEventContractCheck_triggered(self):
        from DataCheck.EventContractCheck import CEventContractCheck
        CEventContractCheck(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEventServicesCheck_triggered(self):
        from DataCheck.EventServicesCheck import CEventServicesCheck
        CEventServicesCheck(self).exec_()

    @QtCore.pyqtSlot()
    def on_actClientExaminationPlan_triggered(self):
        from Exchange.R23.ExamPlan.ExchangeDialog import CPlannedExaminationExchangeDialog
        CPlannedExaminationExchangeDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actLDES_triggered(self):
        from Exchange.n3labdata.OrderListDialog import CLabOrderListDialog
        CLabOrderListDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actTempInvalidCheck_triggered(self):
        from DataCheck.CheckTempInvalid import TempInvalidCheck
        TempInvalidCheck(self).exec_()

    @QtCore.pyqtSlot()
    def on_actClientDocumentsCheck_triggered(self):
        from DataCheck.CheckClientDocuments import CClientDocumentsCheck
        CClientDocumentsCheck(self).exec_()

    @QtCore.pyqtSlot()
    def on_actCreateAttachClientsForArea_triggered(self):
        from Orgs.CreateAttachClientsForArea import CCreateAttachClientsForArea
        CCreateAttachClientsForArea(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDbfView_triggered(self):
        from library.DbfViewDialog import viewDbf
        viewDbf(self)

    @QtCore.pyqtSlot()
    def on_actTestSendMail_triggered(self):
        from library.SendMailDialog import sendMail
        sendMail(self, '', u'проверка связи', u'проверка связи\n1\n2\n3', [])

    @QtCore.pyqtSlot()
    def on_actTestMKB_triggered(self):
        from library.ICDTreeTest import testICDTree
        testICDTree()

    @QtCore.pyqtSlot()
    def on_actTestRLS_triggered(self):
        from library.RLS.RLSComboBoxTest import testRLSComboBox
        testRLSComboBox()

    @QtCore.pyqtSlot()
    def on_actTestMES_triggered(self):
        from library.MES.MESComboBoxTest import testMESComboBox
        testMESComboBox()

    @QtCore.pyqtSlot()
    def on_actTestTNMS_triggered(self):
        from library.TNMS.TNMSComboBoxTest import testTNMSComboBox
        testTNMSComboBox()

    @QtCore.pyqtSlot()
    def on_actSchemaSync_triggered(self):
        from DataCheck.SchemaSync import DoSchemaSync
        DoSchemaSync()

    @QtCore.pyqtSlot()
    def on_actSchemaClean_triggered(self):
        from DataCheck.SchemaClean import DoSchemaClean
        DoSchemaClean()

    @QtCore.pyqtSlot()
    def on_actKSGReselect_triggered(self):
        from Events.KSGReselection import CKSGReselection
        CKSGReselection(self).exec_()

    @QtCore.pyqtSlot()
    def on_actOldStyleServiceModifierRemake_triggered(self):
        from RefBooks.ServiceModifier import COldStyleServiceModifierRemaker
        COldStyleServiceModifierRemaker(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportFromLogger_triggered(self):
        from Reports.ReportFromLogger import CReportFromLogger
        CReportFromLogger(self).exec_()

    @QtCore.pyqtSlot()
    def on_actAdditionalFeaturesUrls_triggered(self):
        from RefBooks.AdditionalFeaturesUrls import CRBAdditionalFeaturesUrlList
        CRBAdditionalFeaturesUrlList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actAppPreferences_triggered(self):
        qApp = QtGui.qApp
        from preferences.appPreferencesDialog import CAppPreferencesDialog
        dialog = CAppPreferencesDialog(self)
        dialog.setTabGlobalEnabled(qApp.userHasAnyRight([urAdmin,
                                                         urAccessSetupGlobalPreferencesWatching,
                                                         urAccessSetupGlobalPreferencesEdit]))
        dialog.setProps(qApp.preferences.appPrefs)
        if dialog.exec_():
            prevOrgId = qApp.currentOrgId()
            prevOrgStructureId = qApp.currentOrgStructureId()
            qApp.preferences.appPrefs.update(dialog.props())
            qApp.preferences.save()
            orgId = qApp.currentOrgId()
            orgStructureId = qApp.currentOrgStructureId()
            if not orgId:
                self.closeRegistryWindow()
                self.closeDeferredQueueWindow()
            self.setUserName(qApp.userName())
            self.updateActionsState()
            if orgId != prevOrgId:
                qApp.emit(QtCore.SIGNAL('currentOrgIdChanged()'))
                settings = CPreferences.getSettings(CConnectionDialog.iniFileName)
                if qApp.preferences.dbConnectionName:
                    settings.beginGroup(qApp.preferences.dbConnectionName)
                    settings.setValue('orgId', toVariant(orgId))
                    settings.endGroup()
                    settings.sync()
            if orgStructureId != prevOrgStructureId:
                qApp.emit(QtCore.SIGNAL('currentOrgStructureIdChanged()'))
                settings = CPreferences.getSettings(CConnectionDialog.iniFileName)
                if qApp.preferences.dbConnectionName:
                    settings.beginGroup(qApp.preferences.dbConnectionName)
                    settings.setValue('orgStructureId', toVariant(orgStructureId))
                    settings.endGroup()
                    settings.sync()
            qApp.clearPreferencesCache()

    @QtCore.pyqtSlot()
    def on_actConnection_triggered(self):
        dlg = CConnectionDialog(self)
        preferences = QtGui.qApp.preferences
        dlg.setDriverName(preferences.dbDriverName)
        dlg.setServerName(preferences.dbServerName)
        dlg.setServerPort(preferences.dbServerPort)
        dlg.setDatabsaseName(preferences.dbDatabaseName)
        dlg.setConnectionName(preferences.dbConnectionName)
        dlg.setCompressData(preferences.dbCompressData)
        dlg.setUserName(preferences.dbUserName)
        dlg.setPassword(preferences.dbPassword)
        dlg.setNewAuthorizationScheme(preferences.dbNewAuthorizationScheme)
        dlg.setLoggerDbName(preferences.dbLoggerName)
        if dlg.exec_() :
            preferences.isSaveUserPasword = False
            preferences.dbDriverName = dlg.driverName()
            preferences.dbConnectionName = dlg.connectionName()
            preferences.dbServerName = dlg.serverName()
            preferences.dbServerPort = dlg.serverPort()
            preferences.dbDatabaseName = dlg.databaseName()
            preferences.dbLoggerName = dlg.loggerDbName()
            preferences.dbCompressData = dlg.compressData()
            preferences.dbUserName = dlg.userName()
            preferences.dbPassword = dlg.password()
            preferences.dbNewAuthorizationScheme = dlg.newAuthorizationScheme()
            currentOrgId = QtGui.qApp.currentOrgId()
            currentOrgStructureId = QtGui.qApp.currentOrgStructureId()
            connectionOrgId = dlg.connectionOrgId()
            connectionLogin = dlg.connectionLogin()
            connectionOrgStructureId = dlg.connectionOrgStructureId()
            if connectionOrgId and connectionOrgId != currentOrgId:
                QtGui.qApp.preferences.appPrefs['orgId'] = connectionOrgId
                prefs = getPref(QtGui.qApp.preferences.appPrefs, 'PreCreateEvent', {})  # Сбрасываем организацию по умолчанию в PreCreateEvent
                setPref(prefs, 'infisCode', None)
                setPref(QtGui.qApp.preferences.appPrefs, 'PreCreateEvent', prefs)
            elif not connectionOrgId:
                prefs = getPref(QtGui.qApp.preferences.appPrefs, 'PreCreateEvent', {})
                setPref(prefs, 'infisCode', None)
                setPref(QtGui.qApp.preferences.appPrefs, 'PreCreateEvent', prefs)
            if connectionLogin:
                QtGui.qApp.preferences.appUserName = connectionLogin
            if connectionOrgStructureId != currentOrgStructureId:
                QtGui.qApp.preferences.appPrefs['orgStructureId'] = connectionOrgStructureId
            preferences.save()

    @QtCore.pyqtSlot()
    def on_actDecor_triggered(self):
        from preferences.decor import CDecorDialog
        dlg = CDecorDialog(self)
        preferences = QtGui.qApp.preferences
        dlg.setStyle(preferences.decorStyle)
        dlg.setStandardPalette(preferences.decorStandardPalette)
        dlg.setMaximizeMainWindow(preferences.decorMaximizeMainWindow)
        dlg.setFullScreenMainWindow(preferences.decorFullScreenMainWindow)
        dlg.setFontSize(QtGui.qApp.font().pointSize())
        dlg.setFontFamily(QtGui.qApp.font().family())
        dlg.set_crb_width_unlimited(preferences.decor_crb_width_unlimited)
        if dlg.exec_():
            preferences.decorStyle = dlg.style()
            preferences.decorStandardPalette = dlg.standardPalette()
            preferences.decorMaximizeMainWindow = dlg.maximizeMainWindow()
            preferences.decorFullScreenMainWindow = dlg.fullScreenMainWindow()
            preferences.decorFontSize = dlg.fontSize()
            preferences.decorFontFamily = dlg.fontFamily()
            preferences.decor_crb_width_unlimited = dlg.crb_width_unlimited()
            preferences.save()
            QtGui.qApp.applyDecorPreferences()

    @QtCore.pyqtSlot()
    def on_actMIACExchangePreferences_triggered(self):
        from Registry.MIACExchange.MIACExchangeSetup import CMIACExchangeSetupDialog
        CMIACExchangeSetupDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEMSRNExchangePreferences_triggered(self):
        from Registry.EMSRNExchange.EMSRNExchangeSetup import CEMSRNExchangeSetupDialog
        CEMSRNExchangeSetupDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actCalendar_triggered(self):
        from preferences.calendar import CCalendarDialog
        CCalendarDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actInformerMessages_triggered(self):
        from Users.Informer import CInformerList
        CInformerList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actInformer_triggered(self):
        showInformer(self, False)

    @QtCore.pyqtSlot()
    def on_actUserRightListDialog_triggered(self):
        CUserRightListDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actUserRightProfileListDialog_triggered(self):
        CUserRightProfileListDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actSendBugReport_triggered(self):
        from bugreport.SendBugReport import CSendBugReportDialog
        CSendBugReportDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actAbout_triggered(self):
        try:
            from buildInfo import lastChangedRev, lastChangedDate as lastDate
            lastChangedDate = forceString(QDateTime.fromString(
                lastDate[:lastDate.find('+')-1],
                "yyyy-MM-dd hh:mm:ss")
            )
            if not lastChangedDate:
                lastChangedDate = lastDate
        except ImportError:
            lastChangedRev  = 'unknown'
            lastChangedDate = 'unknown'

        revisionInfoQuery =  u"""
        SELECT revision, updateDate
        FROM `DatabaseUpdateInfo`
        WHERE `completed` = 1
        ORDER BY `revision` DESC
        LIMIT 1
        """
        db = QtGui.qApp.db
        error = False
        if db and db.db.isValid():
            query = db.query(revisionInfoQuery)
            if query.first():
                lastChangedDbRev = forceString(query.record().value('revision'))
                lastChangedDbDate = forceString(query.record().value('updateDate'))
            else:
                error = True
        else:
            error = True
        if error:
            lastChangedDbRev = 'unknown'
            lastChangedDbDate = 'unknown'

        QtGui.QMessageBox.about(
            self, u'О программе', about % ( title,
                                            lastChangedRev, lastChangedDate,
                                            lastChangedDbRev, lastChangedDbDate,
                                            os.path.abspath(os.getcwd()).decode(locale.getpreferredencoding()))
            )
# добавил свой триггер на слот
    @QtCore.pyqtSlot()
    def on_actionGo1_triggered(self):
        #QtGui.QMessageBox.aboutGo1(self, u'Go1')
        QtGui.QMessageBox.aboutQt(self, u'О Qt')
        
    @QtCore.pyqtSlot()
    def on_actAboutQt_triggered(self):
        QtGui.QMessageBox.aboutQt(self, u'О Qt')
    

    @QtCore.pyqtSlot()
    def on_actChangeCurrentUserPassword_triggered(self):
        from RefBooks.Person import CChangePasswordDialog
        dlg = CChangePasswordDialog(self)
        if dlg.exec_():
            passwords = dlg.passwords()
            if verifyUserPassword(None, passwords['old'])[0]:
                resultMessage = QtGui.qApp.setCurrentUserPassword(passwords['new'])
                QtGui.QMessageBox.information(self, u'Результат изменения пароля',
                                              resultMessage,
                                              buttons = QtGui.QMessageBox.Ok,
                                              defaultButton = QtGui.QMessageBox.Ok)
            else:
                QtGui.QMessageBox.warning(self,
                                          u'Ошибка подтверждения текущего пароля',
                                          u'Не верно введен текущий пароль',
                                          buttons = QtGui.QMessageBox.Ok,
                                          defaultButton = QtGui.QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def on_actReportDeferredQueueCount_triggered(self):
        from Reports.ReportDeferredQueueCount import CReportDeferredQueueCount
        CReportDeferredQueueCount(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportDeathBSK_triggered(self):
        from Reports.ReportDeathBSK import CReportDeathBSK
        CReportDeathBSK(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPrimaryEventsOnko_triggered(self):
        from Reports.Onko.ReportPrimaryEventsOnko import CReportPrimaryEventsOnko
        CReportPrimaryEventsOnko(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPrimarySecondaryOnko_triggered(self):
        from Reports.Onko.ReportPrimarySecondary import CReportOnkoPrimarySecondary
        CReportOnkoPrimarySecondary(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportOnPaidServicesPZ12_triggered(self):
        from Reports.ReportOnPaidServicesPZ12 import CReportOnPaidServicesPZ12
        CReportOnPaidServicesPZ12(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportOnEconomicCalcServicesPZ12_triggered(self):
        from Reports.ReportOnEconomicCalcServicesPZ12 import CReportOnEconomicCalcServices
        CReportOnEconomicCalcServices(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportLeavedClients_triggered(self):
        from Reports.ReportLeavedClients import CReportLeavedClients
        CReportLeavedClients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportOnkoHospital_triggered(self):
        from Reports.ReportHopitalOnko import CReportHospitalOnko
        CReportHospitalOnko(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportEmergencySurgery_triggered(self):
        from Reports.ReportEmergencySurgery import CReportEmergencySurgery
        CReportEmergencySurgery(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportHospitalBeds_triggered(self):
        from Reports.ReportHospitalBeds import CReportHospitalBeds
        CReportHospitalBeds(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportBedspacePEOForm1_triggered(self):
        from Reports.ReportBedspacePEOForm1 import CReportBedspacePEOForm1
        CReportBedspacePEOForm1(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportBedspacePEOForm2_triggered(self):
        from Reports.ReportBedSpacePEOForm2 import CReportBedspacePEOForm2
        CReportBedspacePEOForm2(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportBedspacePEOForm3_triggered(self):
        from Reports.ReportBedspacePEOForm3 import CReportBedspacePEOForm3
        CReportBedspacePEOForm3(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportBedspacePEOForm5_triggered(self):
        from Reports.ReportBedspacePEOForm5 import CReportBedspacePEOForm5
        CReportBedspacePEOForm5(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportOperationsActivity_triggered(self):
        from Reports.ReportOperationsActivity import CReportOperationsActivity
        CReportOperationsActivity(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportOperationsActivityByActions_triggered(self):
        from Reports.ReportOperationsActivityByActions import CReportOperationsActivityByActions
        CReportOperationsActivityByActions(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportZNOEstablishedFirst_triggered(self):
        from Reports.ReportZNOEstablishedFirst import CReportZNOEstablishedFirst
        CReportZNOEstablishedFirst(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportF027Verification_triggered(self):
        from Reports.ReportF027Verification import CReportF027Verification
        CReportF027Verification(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportBedspaceUsage_triggered(self):
        from Reports.Moscow.ReportBedspaceUsage import CReportBedspaceUsage
        CReportBedspaceUsage(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportOperationProtocolB36_triggered(self):
        from Reports.Moscow.ReportOperationProtocol import CReportOperationProtocol
        CReportOperationProtocol(self).exec_()

    @QtCore.pyqtSlot()
    def on_actNonPaidEvents_triggered(self):
        from Reports.Moscow.ReportNonPaidEvents import CNonPaidEventsReport
        CNonPaidEventsReport(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportListLeavedClient_triggered(self):
        from Reports.ReportListLeavedClient import CReportListLeavedClient
        CReportListLeavedClient(self).exec_()

    @QtCore.pyqtSlot()
    def on_actDispanserRegistryTeenager_triggered(self):
        from Reports.DispanserRegistry        import CDispanserRegistry
        CDispanserRegistry(self, True).exec_()

    @QtCore.pyqtSlot()
    def on_actReportAcute_triggered(self):
        from Reports.ReportAcutePankriotit import CReportAcutePankriotit
        CReportAcutePankriotit(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportTypeVisits_triggered(self):
        from Reports.ReportTypeVisits import CReportTypeVisits
        CReportTypeVisits(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPreventiveExaminations_triggered(self):
        from Reports.ReportPreventiveExaminations import CReportPreventiveExaminations
        CReportPreventiveExaminations(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportTakenClientMonitoringD_triggered(self):
        from Reports.ReportTakenClientMonitoring import CReportTakenClientMonitoring
        CReportTakenClientMonitoring(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportTakenClientMonitoringK_triggered(self):
        from Reports.ReportTakenClientMonitoring import CReportTakenClientMonitoring
        CReportTakenClientMonitoring(self, u'К').exec_()

    @QtCore.pyqtSlot()
    def on_actReportTakenOffClientMonitoringD_triggered(self):
        from Reports.ReportTakenClientMonitoring import CReportTakenOffClientMonitoring
        CReportTakenOffClientMonitoring(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportTakenOffClientMonitoringK_triggered(self):
        from Reports.ReportTakenClientMonitoring import CReportTakenOffClientMonitoring
        CReportTakenOffClientMonitoring(self, u'К').exec_()

    @QtCore.pyqtSlot()
    def on_actReportInfoSource_triggered(self):
        from Reports.InfoSourceReport import CInfoSourceReport
        CInfoSourceReport(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportUncheckedPolicy_triggered(self):
        from Reports.ReportUncheckedPolicy import CReportUncheckedPolicy
        CReportUncheckedPolicy(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportF39PND_triggered(self):
        from Reports.ReportF39ForPND import CReportF39ForPND
        CReportF39ForPND(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportVisitsByClientType_triggered(self):
        from Reports.ReportVisitsByClientType import CReportVisitsByClientType
        CReportVisitsByClientType(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportAnalyticTable_triggered(self):
        from Reports.ReportAnalyticalTable import CReportAnalyticTable
        CReportAnalyticTable(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportBedspace_triggered(self):
        from Reports.ReportBedspace import CReportBedspace
        CReportBedspace(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportBedspaceDC_triggered(self):
        from Reports.ReportBedspace import CReportBedspace
        CReportBedspace(self, True).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPlanningAndEconomicIndicators_triggered(self):
        from Reports.ReportPlanningAndEconomicIndicators import CReportPlanningAndEconomicIndicators
        CReportPlanningAndEconomicIndicators(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportProphilaxy_triggered(self):
        from Reports.ReportProphilaxy import CReportProphilaxy
        CReportProphilaxy(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportF007_triggered(self):
        from Reports.ReportF007 import CReportF007
        CReportF007(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportStationaryF007_triggered(self):
        from Reports.Moscow.ReportStationaryF007 import CReportStationaryF007
        CReportStationaryF007(self).exec_()

    @QtCore.pyqtSlot()
    def on_actMedicinesSMP_triggered(self):
        from Reports.ReportMedicinesSMP import CReportMedicinesSMP
        CReportMedicinesSMP(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportLocationCard_triggered(self):
        from Reports.ReportLocationCard import CReportLocationCard
        CReportLocationCard(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportBedspaceInsurance_triggered(self):
        from Reports.ReportBedspaceInsurance import CReportBedspaceInsurance
        CReportBedspaceInsurance(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportAgeSexCompositionLeavedClients_triggered(self):
        from Reports.ReportAgeSexCompositionLeavedClients import CReportAgeSexCompositionLeavedClients
        CReportAgeSexCompositionLeavedClients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportReceivedClientsByOrgStructure_triggered(self):
        from Reports.ReportReceivedClients import CReportReceivedClients
        CReportReceivedClients(self, reportOrgStructure=True).exec_()

    @QtCore.pyqtSlot()
    def on_actReportReceivedClientsByProfileBeds_triggered(self):
        from Reports.ReportReceivedClients import CReportReceivedClients
        CReportReceivedClients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportReceivedOrgStructure_triggered(self):
        from Reports.ReportReceivedOrgStructure import CReportReceivedOrgStructure
        CReportReceivedOrgStructure(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportActirovania_triggered(self):
        from Reports.ReportActirovania import CReportActirovania
        CReportActirovania(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportTelefonogramm_triggered(self):
        from Reports.ReportTelefonogramm import CReportTelefonogramm
        CReportTelefonogramm(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPatientEntrance_triggered(self):
        from Reports.PatientEntranceReport import CPatientEntranceReport
        CPatientEntranceReport(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportPatientEntranceOrgStructure_triggered(self):
        from Reports.ReportPatientEntranceOrgStructure import CReportPatientEntranceOrgStructure
        CReportPatientEntranceOrgStructure(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportReceivedAndRefusalClients_triggered(self):
        from Reports.ReportReceivedAndRefusalClients import CReportReceivedAndRefusalClients
        CReportReceivedAndRefusalClients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportFinance_triggered(self):
        from Reports.ReportFinance import CReportFinance
        CReportFinance(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportSurgicalIndicators_triggered(self):
        from Reports.ReportSurgicalIndicators import CReportSurgicalIndicators
        CReportSurgicalIndicators(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportSomeSurgicalIndicators_triggered(self):
        from Reports.ReportSomeSurgicalIndicators import CReportSomeSurgicalIndicators
        CReportSomeSurgicalIndicators(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportF16_triggered(self):
        from Reports.ReportF16 import CReportF16
        CReportF16(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportDiagnosisLeaved_triggered(self):
        from Reports.ReportDiagnosisLeaved import CReportDiagnosisLeaved
        CReportDiagnosisLeaved(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportControlSurgery_triggered(self):
        from Reports.ReportSearchUncorrectServiceEventsWithKSG import CReportSearchUncorrectServiceEventsWithKSG
        CReportSearchUncorrectServiceEventsWithKSG(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportOperation_triggered(self):
        from Reports.ReportOperation import CReportOperation
        CReportOperation(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportF14Children_triggered(self):
        from Reports.ReportF14Children import CReportF14Children
        CReportF14Children(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportE15S_triggered(self):
        from Reports.ReportE15S import CReportE15S
        CReportE15S(self).exec_()

    @QtCore.pyqtSlot()
    def on_actEconomicReports_triggered(self):
        from Reports.EconomicReportsR23 import CEconomicReports
        CEconomicReports(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportTherapeutic_triggered(self):
        from Reports.ReportTherapeutic import CReportTherapeutic
        CReportTherapeutic(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportTherapeuticClients_triggered(self):
        from Reports.ReportTherapeuticClients import CReportTherapeutic
        CReportTherapeutic(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportAccount_triggered(self):
        from Reports.ReportAccount import CReportAccount
        CReportAccount(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportVIPClients_triggered(self):
        from Reports.VIPClientReports import CReportVIPClients
        CReportVIPClients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportVIPClientsDetalization_triggered(self):
        from Reports.VIPClientReports import CReportVIPClientsDetalization
        CReportVIPClientsDetalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportVerifiedAction_triggered(self):
        from Reports.VerifiedActionReport import CReportVerifiedAction
        CReportVerifiedAction(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportChildrenTherapeutic_triggered(self):
        from Reports.ReportChildrenTherapeutic import CReportChildrenTherapeutic
        CReportChildrenTherapeutic(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportChildrenSurgical_triggered(self):
        from Reports.ReportChildrenSurgical import CReportChildrenSurgical
        CReportChildrenSurgical(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportRegisterContracts_triggered(self):
        from Reports.ReportRegisterContracts import CReportRegisterContracts
        CReportRegisterContracts(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportAttachedClient_triggered(self):
        from Reports.ReportAttachedClient import CReportAttachedClient
        CReportAttachedClient(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportMoving_triggered(self):
        from Reports.ReportMoving import CReportMoving
        CReportMoving(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportControlMKB_triggered(self):
        from Reports.ReportInvalidMKBEventsList import CReportInvalidMKBEventsList
        CReportInvalidMKBEventsList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportCompositionNewborn_triggered(self):
        from Reports.ReportCompositionNewborn import CReportCompositionNewborn
        CReportCompositionNewborn(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportFeedDistribution_triggered(self):
        from Reports.ReportFeedDistribution import CReportFeedDistribution
        CReportFeedDistribution(self).exec_()

    @QtCore.pyqtSlot()
    def on_actForma007Moving2015_triggered(self):
        from Reports.StationaryF007           import CStationaryF007Moving2015
        CStationaryF007Moving2015(self).exec_()

    @QtCore.pyqtSlot()
    def on_actCheckAccounts_triggered(self):
        from Exchange.CheckAccounts.CheckAccounts import CCheckAccounts
        CCheckAccounts(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportFE5P_triggered(self):
        from Reports.ReportFE5P import CReportFE5P
        CReportFE5P(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportAccountService_triggered(self):
        from Reports.AccountRegistry import buildReport
        buildReport()

    @QtCore.pyqtSlot()
    def on_actReportAnalizeBillOnDirections_triggered(self):
        from Reports.ReportAnalizeBillOnDirections import CReportAnalizeBillOnDirections
        CReportAnalizeBillOnDirections(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportDuplicateEvents_triggered(self):
        from Reports.ReportDuplicateEvents import CReportDuplicateEvents
        CReportDuplicateEvents(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportUnclosedEvents_triggered(self):
        from Reports.ReportUnclosedEvents import CReportUnclosedEvents
        CReportUnclosedEvents(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportFE24S_triggered(self):
        from Reports.ReportFE24S import CReportFE24S
        CReportFE24S(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportStandart_triggered(self):
        from Reports.ReportStandart import CReportStandart
        CReportStandart(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportExistingClients_triggered(self):
        from Reports.ReportExistingClients import CReportExistingClients
        CReportExistingClients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actControlEventResult_triggered(self):
        from Reports.ReportControlEventResult import CReportControlEventResult
        CReportControlEventResult(self).exec_()

    @QtCore.pyqtSlot()
    def on_actF030ru_triggered(self):
        from Reports.ReportF030ru import CReportF030ru
        CReportF030ru(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportExemptionRecipes_triggered(self):
        from Reports.ReportExemptionRecipes import CReportExemptionRecipes
        CReportExemptionRecipes(self).exec_()

    @QtCore.pyqtSlot()
    def on_actControlHospBedProfile_triggered(self):
        from Reports.ReportControlHospBedProfile import CReportControlHospBedProfile
        CReportControlHospBedProfile(self).exec_()

    @QtCore.pyqtSlot()
    def on_actControlServiceSex_triggered(self):
        from Reports.ReportControlServiceSex import CReportControlServiceSex
        CReportControlServiceSex(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportControlPaymentAmount_triggered(self):
        from Reports.ReportControlPaymentAmount import CReportControlPaymentAmount
        CReportControlPaymentAmount(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportControlDischarge_triggered(self):
        from Reports.ReportControlDischarge import CReportControlDischarge
        CReportControlDischarge(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportHospitalizationTransferReason_triggered(self):
        from Reports.ReportHospitalizationTransferReason import CReportHospitalizationTransferReason
        CReportHospitalizationTransferReason(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportCancelationReason_triggered(self):
        from Reports.ReportCancellationReason import CReportCancellationReason
        CReportCancellationReason(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportStatMainIndicatorsLPU_triggered(self):
        from Reports.ReportMainIndicatorsLPU import CReportMainIndicatorsLPU
        CReportMainIndicatorsLPU(self, 'stat').exec_()

    @QtCore.pyqtSlot()
    def on_actAmbMainIndicatorsLPU_triggered(self):
        from Reports.ReportMainIndicatorsLPU import CReportMainIndicatorsLPU
        CReportMainIndicatorsLPU(self, 'amb').exec_()

    @QtCore.pyqtSlot()
    def on_actAStomMainIndicatorsLPU_triggered(self):
        from Reports.ReportMainIndicatorsLPU import CReportMainIndicatorsLPU
        CReportMainIndicatorsLPU(self, 'stom').exec_()

    @QtCore.pyqtSlot()
    def on_actReportStatDsMainIndicatorsLPU_triggered(self):
        from Reports.ReportMainIndicatorsLPU import CReportMainIndicatorsLPU
        CReportMainIndicatorsLPU(self, 'statDs').exec_()

    @QtCore.pyqtSlot()
    def on_actReportSalary_Service_triggered(self):
        from Reports.SalaryReports.ReportSalary_Service import CReportSalary_Service
        CReportSalary_Service(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportSalary_Performer_triggered(self):
        from Reports.SalaryReports.ReportSalary_Performer import CReportSalary_Performer
        CReportSalary_Performer(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportSalary_OrgStructure_triggered(self):
        from Reports.SalaryReports.ReportSalary_OrgStructure import CReportSalary_OrgStructure
        CReportSalary_OrgStructure(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportSalary_Patient_triggered(self):
        from Reports.SalaryReports.ReportSalary_Patient import CReportSalary_Patient
        CReportSalary_Patient(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportOrgByOrganisation_triggered(self):
        from Reports.StGeorge.ReportOrgByOrganisation import CReportOrgByOrganisation
        CReportOrgByOrganisation(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportOrgByService_triggered(self):
        from Reports.StGeorge.ReportOrgByService import CReportOrgByService
        CReportOrgByService(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportOrgByDoctor_triggered(self):
        from Reports.StGeorge.ReportOrgByDoctor import CReportOrgByDoctor
        CReportOrgByDoctor(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportOrgBySection_triggered(self):
        from Reports.StGeorge.ReportOrgByBed import CReportOrgByBed
        CReportOrgByBed(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportCurePatients_triggered(self):
        from Reports.StGeorge.ReportCurePatients import CReportCurePatients
        CReportCurePatients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportReceivedPatients_triggered(self):
        from Reports.StGeorge.ReportReceivedPatients import CReportReceivedPatients
        CReportReceivedPatients(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportRecommendations_triggered(self):
        from Reports.ReportRecommendations import CReportRecommendations
        CReportRecommendations(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportConstructor_triggered(self):
        from Reports.ReportsConstructor.RCReportList import CRCReportList
        CRCReportList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actSynchronizeDLOMIAC_triggered(self):
        from Exchange.R23.recipes.SynchronizeDLOMIAC import CSynchronizeDLOMIAC
        CSynchronizeDLOMIAC(self).exec_()

    @QtCore.pyqtSlot()
    def on_actSynchronizeAttach_triggered(self):
        from Exchange.R23.attach.AttachExchangeDialog import CAttachExchangeDialog
        CAttachExchangeDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actCleanIniFile_triggered(self):
        from DataCheck.IniCleaner import cleanConfigFile
        cleanConfigFile()

    @QtCore.pyqtSlot()
    def on_actUpdatesChecker_triggered(self):
        from DataCheck.UpdatesChecker import CUpdatesChecker
        CUpdatesChecker().exec_()

    @QtCore.pyqtSlot()
    def on_actRemoveServiceSpecification_triggered(self):
        from Reports.ReportServiceSpecification import CReportServiceSpecification
        dlg = CReportServiceSpecification(self)
        dlg.reportNumber = 0
        dlg.setTitle(self.actRemoveServiceSpecification.text())

        dlg.exec_()

    @QtCore.pyqtSlot()
    def on_actAddServiceSpecification_triggered(self):
        from Reports.ReportServiceSpecification import CReportServiceSpecification
        dlg = CReportServiceSpecification(self)
        dlg.reportNumber = 2
        dlg.setTitle(self.actAddServiceSpecification.text())
        dlg.exec_()

    @QtCore.pyqtSlot()
    def on_actChangeServiceSpecification_triggered(self):
        from Reports.ReportServiceSpecification import CReportServiceSpecification
        dlg = CReportServiceSpecification(self)
        dlg.reportNumber = 3
        dlg.setTitle(self.actChangeServiceSpecification.text())
        dlg.exec_()

    @QtCore.pyqtSlot()
    def on_actSsmp_triggered(self):
        from Exchange.R23.ssmp.SmpWindow import CSmpWindow
        CSmpWindow(self).exec_()

    @QtCore.pyqtSlot()
    def on_actPharmacyStore_triggered(self):
        from Pharmacy.PharmacyStore import CPharmacyStoreDialog
        CPharmacyStoreDialog(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReport2000_triggered(self):
        from Reports.ReportsPND.Report_no36_2000 import CReportReHospitalization
        CReportReHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReport2100_triggered(self):
        from Reports.ReportsPND.Report_no36_2100 import CReportReHospitalization
        CReportReHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReport2101_triggered(self):
        from Reports.ReportsPND.Report_no36_2101 import CReportReHospitalization
        CReportReHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReport2110_triggered(self):
        from Reports.ReportsPND.Report_no36_2110 import CReportReHospitalization
        CReportReHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReport2120_triggered(self):
        from Reports.ReportsPND.Report_no36_2120 import CReportReHospitalization
        CReportReHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReport2150_triggered(self):
        from Reports.ReportsPND.Report_no36_2150 import CReportReHospitalization
        CReportReHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReport2180_triggered(self):
        from Reports.ReportsPND.Report_no36_2180 import CReportReHospitalization
        CReportReHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReport2181_triggered(self):
        from Reports.ReportsPND.Report_no36_2181 import CReportReHospitalization
        CReportReHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReport2190_triggered(self):
        from Reports.ReportsPND.Report_no36_2190 import CReportReHospitalization
        CReportReHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReport2200_triggered(self):
        from Reports.ReportsPND.Report_no36_2200 import CReportReHospitalization
        CReportReHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReport2600_triggered(self):
        from Reports.ReportsPND.Report_no36_2600 import CReportReHospitalization
        CReportReHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReport2900_triggered(self):
        from Reports.ReportsPND.Report_no36_2900 import CReportReHospitalization
        CReportReHospitalization(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportNonCash_triggered(self):
        from Reports.Pes.ReportNonCashContracts import CReportNonCashContracts
        CReportNonCashContracts(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportNonCashDetails_triggered(self):
        from Reports.Pes.ReportNonCashContracts import CReportNonCashFinance
        CReportNonCashFinance(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportClinicalIssues_triggered(self):
        from Reports.Pes.ReportClinicalissues import CReportClinicalIssues
        CReportClinicalIssues(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportClinicalIssuesDetails_triggered(self):
        from Reports.Pes.ReportClinicalissues import CReportClinicalFinance
        CReportClinicalFinance(self).exec_()

    @QtCore.pyqtSlot()
    def on_actQueueControl_triggered(self):
        from library.QueueControl.QueueControl import QueueList
        QueueList(self).exec_()

    @QtCore.pyqtSlot()
    def on_actReportCurrentProtocol_triggered(self):
        from Reports.Pes.ReportProtocol import CReportProtocol
        CReportProtocol(self).exec_()

    @QtCore.pyqtSlot()
    def on_actF030_13U_triggered(self):
        from Reports.ReportF030_13U import CReportF030_13U
        CReportF030_13U(self).exec_()

    @QtCore.pyqtSlot()
    def on_actExportIEMK_triggered(self):
        from Exchange.ExportIEMK import CExportIEMK
        CExportIEMK(self).exec_()

    @QtCore.pyqtSlot()
    def on_actImportPACS_triggered(self):
        from Exchange.ImportPACS import CImportPACS
        CImportPACS(self).exec_()


def main():
    parser = OptionParser(usage = "usage: %prog [options]")
    parser.add_option('-c', '--config',
                      dest='iniFile',
                      help='custom .ini file name',
                      metavar='iniFile',
                      default='S11App.ini'
                     )
    parser.add_option('-p', '--play',
                      dest='playEventLogFile',
                      help='file name for playback events',
                      metavar='eventLogFile',
                      default=None
                     )
    parser.add_option('-d', '--demo',
                      dest='demo',
                      help='Login as demo',
                      action='store_true',
                      default=False
                     )
    parser.add_option('-l', '--nolock',
                      dest='nolock',
                      help='Disable record lock',
                      action='store_true',
                      default=False
                     )
    parser.add_option('--version',
                      dest='version',
                      help='print version and exit',
                      action='store_true',
                      default=False
                     )
    parser.add_option('--test-ecr',
                      dest='isTestECR',
                      help='Test for available connected Electronic Cash Register (KKM)',
                      action='store_true',
                      default=False
                     )
    parser.add_option('--disable-window-prefs',
                      dest='isDisableWindowPrefs',
                      help='Disables loading of window configurations from the * .ini file',
                      action='store_true',
                      default=False
                     )
    (options, args) = parser.parse_args()
    parser.destroy()

    if options.version:
        print '%s, v.2.0' % titleLat
    elif options.isTestECR:
        print 'ECR test mode are deprecated'
        return 0
    else:
        app = CS11mainApp(sys.argv, options.demo, options.iniFile, options.nolock, options.isDisableWindowPrefs)
        QTextCodec.setCodecForTr(QTextCodec.codecForName(u'utf8'))
        translators = []
        for translationFile in glob.glob(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'i18n/*.qm')):
            translators.append(QtCore.QTranslator())
            if translators[-1].load(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), translationFile)):
                app.installTranslator(translators[-1])

        QtGui.qApp = app

        try:
            app.applyDecorPreferences() # надеюсь, что это поможет немного сэкономить при создании гл.окна
        except:
            pass
        if not(app.isServer or app.hasRightToRunMoreThanOneProgramm):
            QtGui.QMessageBox().warning(None, u'Ошибка', u'Вы не имеете права запускать более одной копии программы')
            QtGui.qApp = None
            return 0
        MainWindow = CS11MainWindow()
        app.mainWindow = MainWindow
        app.connect(app.mainWindow, QtCore.SIGNAL('hasRightToRunMoreThanOneProgramm(bool)'), app.onHasRightToRunMoreThanOneProgramm)
        app.applyDecorPreferences()  # применение максимизации/полноэкранного режима к главному окну
        MainWindow.show()

        if os.path.isdir('pre-run'):
            for script_name in filter(lambda x: x.endswith('.py'), os.listdir('pre-run')):
                try:
                    execfile(os.path.join('pre-run', script_name))
                except Exception as e:
                    app.log('Pre-run script exception', 'Script name: ' + script_name)
                    app.logCurrentException()

        if app.preferences.dbAutoLogin:
            MainWindow.actLogin.activate(QtGui.QAction.Trigger)

        app.exec_()

        app.preferences.appPrefs['isAutoStartEQControls'] = CEQController.isAutoStart()
        app.preferences.save()
        CEQController.getInstance().deleteLater()
        app.closeDatabase()
        app.doneTrace()

        QtGui.qApp = None


if __name__ == '__main__':
    gc.enable()
    try:
        if "_MEIPASS2" in os.environ:
            appDir = os.environ["_MEIPASS2"]
            plugDir = "qt4_plugins"
            plugDir = os.path.join(appDir, plugDir)
            QCoreApplication.addLibraryPath(os.path.abspath(appDir))
            QCoreApplication.addLibraryPath(os.path.abspath(plugDir))

        # the X11 windowing functions are apparently not threadsafe unless explicitly set to be so, and for whatever
        # reason PyQt doesn't automatically set them to be. This can be corrected by adding the following before the
        # QApplication constructor
        if hasattr(QtCore.Qt, 'AA_X11InitThreads'):
            QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
        main()
    except:
        logException(os.path.join(unicode(QDir.toNativeSeparators(QDir.homePath())), '.vista-med'),
                     *sys.exc_info())
