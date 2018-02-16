# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import codecs
import locale
import os.path
import socket
import sys
import traceback

from PyQt4 import QtCore, QtGui

from library.exception import CDatabaseException
from library.Preferences    import CPreferences
from library.Utils          import forceString, getPref, setPref

from preferences.connection import CConnectionDialog
from preferences.decor      import CDecorDialog

from TissueJournal.LaboratoryCalculator.CalculatorWidget import CCalculatorWidget

from Ui_LaboratoryCalculator import Ui_MainWindow


title = u'ВИСТА-МЕД'
titleLat = 'VISTA-MED'
about = u'Комплекс Программных Средств \n' \
        u'"Система автоматизации медико-страхового обслуживания населения"\n' \
        u'КПС «%s»\n'   \
        u'Версия 2.0 (ревизия %s от %s)\n' \
        u'Copyright (C) 2007-2014 ООО "Чук и Гек" и ООО "Виста"\n' \
        u'распространяется под лицензией GNU GPL v.3 или выше\n' \
        u'телефон тех.поддержки (812) 380-97-06'

class CLaboratoryCalculatorApp(QtGui.QApplication):
    inputMimeDataType  = 'vista-med/inputLaboratoryCalculator'
    outputMimeDataType = 'vista-med/outputLaboratoryCalculator'
    
    __pyqtSignals__ = ('dbConnectionChanged(bool)',)

    def __init__(self, args):
        QtGui.QApplication.__init__(self, args)
        self.logDir = os.path.join(unicode(QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())), '.vista-med')
        oldLogDir = os.path.join(unicode(QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())), '.samson-vista')
        if os.path.exists(oldLogDir) and not os.path.exists(self.logDir):
            os.rename(oldLogDir, self.logDir)
        self.oldMsgHandler = QtCore.qInstallMsgHandler(self.msgHandler)
        self.oldEexceptHook = sys.excepthook
        sys.excepthook = self.logException
        self.traceActive = True
        self.homeDir= None
        self.saveDir= None
        self.hostName = socket.gethostname()
        self.disableLock = False
        self.db = None
        self._isConnected = False
        self.mainWindow = None
        self.preferences = CPreferences('LaboratoryCalculatorApp.ini')
        self.preferences.load()
        self.preferencesDir = self.preferences.getDir()
        self.lastClipboardSlot = None
        
    
    def connected(self):
        return self._isConnected
    
    def connectClipboard(self, clipboardSlot):
        self.disconnectClipboard()
        self.lastClipboardSlot = clipboardSlot
        self.connect(self.clipboard(), QtCore.SIGNAL('dataChanged()'), clipboardSlot)
        
    def disconnectClipboard(self):
        if self.lastClipboardSlot:
            self.disconnect(self.clipboard(), QtCore.SIGNAL('dataChanged()'), self.lastClipboardSlot)
    
    
    def doneTrace(self):
        self.traceActive = False
        QtCore.qInstallMsgHandler(self.oldMsgHandler)
        sys.excepthook = self.oldEexceptHook


    def applyDecorPreferences(self):
        self.setStyle(self.preferences.decorStyle)
        if self.preferences.decorStandardPalette:
            self.setPalette(self.style().standardPalette())
        if self.mainWindow:
            state = QtCore.Qt.WindowNoState
            if self.preferences.decorMaximizeMainWindow:
                state |= QtCore.Qt.WindowMaximized
            if self.preferences.decorFullScreenMainWindow:
                state |= QtCore.Qt.WindowFullScreen
            self.mainWindow.setWindowState(state)

    def getHomeDir(self):
        if not self.homeDir:
            homeDir = os.path.expanduser('~')
            if homeDir == '~':
                homeDir = unicode(QtCore.QDir.homePath())
            if isinstance(homeDir, str):
                homeDir = unicode(homeDir, locale.getpreferredencoding())
            self.homeDir = homeDir
        return self.homeDir

    def msgHandler(self, type, msg):
        if type == 0: # QtMsgType.QtDebugMsg:
            typeName = 'QtDebugMsg'
        elif type == 1: # QtMsgType.QtWarningMsg:
            typeName = 'QtWarningMsg'
        elif type == 2: # QtMsgType.QtCriticalMsg:
            typeName = 'QtCriticalMsg'
        elif type == 3: # QtFatalMsg
            typeName = 'QtFatalMsg'
        else:
            typeName = 'QtUnknownMsg'

        self.log( typeName, msg, traceback.extract_stack()[:-1])

    def log(self, title, message, stack=None):
        try:
            if not os.path.exists(self.logDir):
                os.makedirs(self.logDir)
            logFile = os.path.join(self.logDir, 'error.log')
            timeString = unicode(QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.SystemLocaleDate))
            logString = u'%s\n%s: %s(%s)\n' % ('='*72, timeString, title, message)
            if stack:
                try:
                    logString += ''.join(traceback.format_list(stack)).decode('utf-8') + '\n'
                except:
                    logString += 'stack lost\n'
            file = codecs.open(logFile, mode='a', encoding=locale.getpreferredencoding())
            file.write(logString)
            file.close()
        except:
            pass


    def logException(self, exceptionType, exceptionValue, exceptionTraceback):
        title = repr(exceptionType)
        message = unicode(exceptionValue)
        self.log(title, message, traceback.extract_tb(exceptionTraceback))
        sys.__excepthook__(exceptionType, exceptionValue, exceptionTraceback)


    def logCurrentException(self):
        self.logException(*sys.exc_info())


    def openDatabase(self, clipboardSlot=None):
        QtGui.qApp.connectClipboard(clipboardSlot)
        self._isConnected = True
#        self.db = None
#        self.db = database.connectDataBase(self.preferences.dbDriverName,
#                                     self.preferences.dbServerName,
#                                     self.preferences.dbServerPort,
#                                     self.preferences.dbDatabaseName,
#                                     self.preferences.dbUserName,
#                                     self.preferences.dbPassword,
#                                     compressData = self.preferences.dbCompressData)
#        self.emit(QtCore.SIGNAL('dbConnectionChanged(bool)'), True)
        
        
    def closeDatabase(self):
        self._isConnected = False
        QtGui.qApp.disconnectClipboard()
        if self.db:
            self.db.close()
            self.db = None
            self.emit(QtCore.SIGNAL('dbConnectionChanged(bool)'), False)
        
        
    def callWithWaitCursor(self, widget, func, *params, **kwparams):
        self.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            return func(*params, **kwparams)
        finally:
            self.restoreOverrideCursor()
            
    def setWindowOnTop(self, window):
        window.showNormal()
        
        
class CLaboratoryCalculator(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self._centralWidget = None
        self.setWindowTitle(u'Лабораторный калькулятор ')
        self.loadPreferences()
        
    def on_clipboardDataChanged(self):
        mimeData = QtGui.qApp.clipboard().mimeData()
        baData = mimeData.data(CLaboratoryCalculatorApp.inputMimeDataType)
        self.load(forceString(QtCore.QString.fromUtf8(baData)))
        
    def load(self, data):
        if QtGui.qApp.connected() and data:
            QtGui.qApp.setWindowOnTop(self)
            self._centralWidget.load(data)
        
    def updateActionsState(self, login=True):
        self.actLogin.setEnabled(not login)
        self.actLogout.setEnabled(login)
        
        
    def loadPreferences(self):
        preferences = getPref(QtGui.qApp.preferences.windowPrefs, self.objectName(), {})
        geometry = getPref(preferences, 'geometry', None)
        if type(geometry) == QtCore.QVariant and geometry.type() == QtCore.QVariant.ByteArray and not geometry.isNull():
            self.restoreGeometry(geometry.toByteArray())
        state = getPref(preferences, 'state', None)
        if type(state) == QtCore.QVariant and state.type() == QtCore.QVariant.ByteArray and not geometry.isNull():
            self.restoreState(state.toByteArray())
        
    def savePreferences(self):
        preferences = {}
        setPref(preferences,'geometry',QtCore.QVariant(self.saveGeometry()))
        setPref(preferences,'state', QtCore.QVariant(self.saveState()))
        setPref(QtGui.qApp.preferences.windowPrefs, self.objectName(), preferences)
        
        
    def closeEvent(self, event):
        if self._centralWidget:
            QtGui.qApp.preferences.appPrefs['calculatorRounding'] = QtCore.QVariant(self._centralWidget.rounding())
        self.savePreferences()
        QtGui.QMainWindow.closeEvent(self, event)
        
        
    @QtCore.pyqtSlot()
    def on_actLogin_triggered(self):
        try:
            QtGui.qApp.openDatabase(self.on_clipboardDataChanged)
            self._centralWidget = CCalculatorWidget()
            self.setCentralWidget(self._centralWidget)
            self.updateActionsState()
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


    @QtCore.pyqtSlot()
    def on_actLogout_triggered(self):
        self._centralWidget.clear()
        self.setCentralWidget(None)
        del self._centralWidget
        QtGui.qApp.closeDatabase()
        self.updateActionsState(login=False)
        
    @QtCore.pyqtSlot()
    def on_actExit_triggered(self):
        self.close()    
    
    
    @QtCore.pyqtSlot()
    def on_actConnection_triggered(self):
        dlg   = CConnectionDialog(self)
        preferences = QtGui.qApp.preferences
        dlg.setDriverName(preferences.dbDriverName)
        dlg.setServerName(preferences.dbServerName)
        dlg.setServerPort(preferences.dbServerPort)
        dlg.setDatabaseName(preferences.dbDatabaseName)
        dlg.setCompressData(preferences.dbCompressData)
        dlg.setUserName(preferences.dbUserName)
        dlg.setPassword(preferences.dbPassword)
        if dlg.exec_() :
            preferences.dbDriverName = dlg.driverName()
            preferences.dbServerName = dlg.serverName()
            preferences.dbServerPort = dlg.serverPort()
            preferences.dbDatabaseName = dlg.databaseName()
            preferences.dbCompressData = dlg.compressData()
            preferences.dbUserName = dlg.userName()
            preferences.dbPassword = dlg.password()
            preferences.save()


    @QtCore.pyqtSlot()
    def on_actDecor_triggered(self):
        dlg = CDecorDialog(self)
        preferences = QtGui.qApp.preferences
        dlg.setStyle(preferences.decorStyle)
        dlg.setStandardPalette(preferences.decorStandardPalette)
        dlg.setMaximizeMainWindow(preferences.decorMaximizeMainWindow)
        dlg.setFullScreenMainWindow(preferences.decorFullScreenMainWindow)
        if dlg.exec_() :
            preferences.decorStyle = dlg.style()
            preferences.decorStandardPalette = dlg.standardPalette()
            preferences.decorMaximizeMainWindow = dlg.maximizeMainWindow()
            preferences.decorFullScreenMainWindow = dlg.fullScreenMainWindow()
            preferences.save()
            QtGui.qApp.applyDecorPreferences()
    
    @QtCore.pyqtSlot()
    def on_actAboutQt_triggered(self):
        QtGui.QMessageBox.aboutQt(self, u'О Qt')
        
        
    @QtCore.pyqtSlot()
    def on_actAbout_triggered(self):
        global lastChangedRev
        global lastChangedDate
        try:
            from buildInfo import lastChangedRev, lastChangedDate
        except:
            lastChangedRev  = 'unknown'
            lastChangedDate = 'unknown'

        QtGui.QMessageBox.about(
            self, u'О программе', about % ( title, lastChangedRev, lastChangedDate)
            )
            
    
if __name__ == '__main__':
    
    app = CLaboratoryCalculatorApp(sys.argv)
    
    QtGui.qApp = app
    app.applyDecorPreferences() 
    MainWindow = CLaboratoryCalculator()
    app.mainWindow = MainWindow
    app.applyDecorPreferences() # применение максимизации/полноэкранного режима к главному окну
    MainWindow.updateActionsState(login=False)
    MainWindow.actLogin.emit(QtCore.SIGNAL('triggered()'))
    MainWindow.show()
    res = app.exec_()
    app.preferences.save()
    app.closeDatabase()
    app.doneTrace()
    app.disconnectClipboard()
        
    QtGui.qApp = None
