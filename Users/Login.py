# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import sys
import hashlib

from PyQt4 import QtGui, QtCore

from library        import database
from library.Utils  import forceString

from Users.Tables   import tblUser, usrId, usrLogin, usrRetired

from Ui_Login       import Ui_LoginDialog

def getADUser():
    if sys.platform != 'win32':
        return None
    try:
        import win32com.client
        _sysInfo= win32com.client.Dispatch('ADSystemInfo')
        _adsi_provider = win32com.client.Dispatch('ADsNameSpaces')
        _curUser = _adsi_provider.GetObject('', "LDAP://"+_sysInfo.UserName)
        _userName = _curUser.MISUsername
        if _userName!="":
            return _userName
        else:
            return None
    except Exception:
            return None
    return None

def verifyUser(login):
    if hasattr(QtGui.qApp, 'db') and QtGui.qApp.db:
        db = QtGui.qApp.db
        tableUser = QtGui.qApp.db.table(tblUser)
        cond = [tableUser[usrLogin].eq(login),
                tableUser[usrRetired].eq(False)]
        userIdList = db.getIdList(tableUser, usrId, cond, [usrId])
        if len(userIdList) == 1:
            return True, userIdList[0]
    return False, None

def verifyUserPassword(login, verifiablePassword):
    isTruePassword = True
    userId = None
    db = None
    
    if login is None:
        login = QtGui.qApp.userInfo.login() if hasattr(QtGui.qApp, 'userInfo') and QtGui.qApp.userInfo else ''
    
    encodedLogin = unicode(login).encode('utf-8')
    encodedPassword = unicode(verifiablePassword).encode('utf8')
    hashedPassword = hashlib.md5(encodedPassword).hexdigest()
    
    if hasattr(QtGui.qApp, 'preferences') and QtGui.qApp.preferences.dbNewAuthorizationScheme:
        connectionInfo = {'driverName' : QtGui.qApp.preferences.dbDriverName,
                          'host' : QtGui.qApp.preferences.dbServerName,
                          'port' : QtGui.qApp.preferences.dbServerPort,
                          'database' : QtGui.qApp.preferences.dbDatabaseName,
                          'user' : createLogin(encodedLogin),
                          'password' : hashedPassword,
                          'connectionName' : 'testPassword',
                          'compressData' : QtGui.qApp.preferences.dbCompressData}
        
        try:
            db = database.connectDataBaseByInfo(connectionInfo)
        except:
            isTruePassword = False
        finally:
            if isinstance(db, database.CDatabase):
                db.close()
    
    if hasattr(QtGui.qApp, 'db') and QtGui.qApp.db:
        db = QtGui.qApp.db
        tableUser = QtGui.qApp.db.table(tblUser)
    
        ustsQuery = db.query('SELECT CONCAT(NOW(), RAND())')
        ustsQuery.first()
        usts = forceString(ustsQuery.record().value(0))
    
        cond = [ tableUser[usrLogin].eq(login),
                 'MD5(CONCAT(\'%s\', password))=\'%s\'' % (usts ,hashlib.md5(usts+hashedPassword).hexdigest()),
                 tableUser[usrRetired].eq(False)
               ]
        cond.append("(Person.retireDate IS NULL) OR (DATE(Person.retireDate) > DATE(CURDATE()))")
        userIdList = db.getIdList(tableUser, usrId, cond, [usrId])
        if len(userIdList) == 1:
            userId = userIdList[0]
        else:
            isTruePassword = False
    else:
        isTruePassword = False
    return (isTruePassword, userId)


def doTranslit(word):
    charset_dict = {
        'а':'a', 'б':'b', 'в':'v', 'г':'g', 'д':'d', 'е':'e', 'ё':'yo', 'ж':'zh',
        'з':'z', 'и':'i', 'й':'j', 'к':'k', 'л':'l', 'м':'m', 'н':'n',  'о':'o',
        'п':'p', 'р':'r', 'с':'s', 'т':'t', 'у':'u', 'ф':'f', 'х':'kh', 'ц':'cz',
        'ч':'ch','ш':'sh','щ':'scz','ъ':'', 'ы':'y', 'ь':'',  'э':'e',  'ю':'yu',
        'я':'ya',

        'А':'A', 'Б':'B', 'В':'V', 'Г':'G', 'Д':'D', 'Е':'E', 'Ё':'YO', 'Ж':'ZH',
        'З':'Z', 'И':'I', 'Й':'J', 'К':'K', 'Л':'L', 'М':'M', 'Н':'N',  'О':'O',
        'П':'P', 'Р':'R', 'С':'S', 'Т':'T', 'У':'U', 'Ф':'F', 'Х':'KH', 'Ц':'CZ',
        'Ч':'CH','Ш':'SH','Щ':'SCZ','Ъ':'', 'Ы':'Y', 'Ь':'',  'Э':'E',  'Ю':'YU',
        'Я':'YA'
    }
    for key in charset_dict.keys():
        word = word.replace( key, charset_dict[key] )
    return word


def createLogin(username):
    symb_to_delete  = [
        '!', '"', '#', '$', '%', '&', "'", '(',
        ')', '*', '+', ',', '-', '.', '/', ':',
        ';', '<', '=', '>', '?', '@', '[', '\\',
        ']', '^', '`', '{', '|', '}', '~'
    ]
    symb_to_replace = [' ']

    username = username.strip()
    if not username: return ""

    if username.isdigit():
        username = "user" + username
        return username[:16]

    username = username.lower()

    uname_tr = doTranslit(username).lower()
    uname_hash = hashlib.sha512(username).hexdigest()

    for c in symb_to_delete:  uname_tr = uname_tr.replace(c, '')
    for c in symb_to_replace: uname_tr = uname_tr.replace(c, '_')

    if not uname_tr:
        return ""
    return uname_tr[:9] + "-" + uname_hash[:3] + uname_hash[-3:]


class CLoginDialog(QtGui.QDialog, Ui_LoginDialog):
    def __init__(self, parent, logo = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self._userId = None #FIXME: stub for not failing in appendix apps after changing main login algorithm
        self._demoMode = False #FIXME: same
        if logo:
            self.label.setPixmap(QtGui.QPixmap(':/new/prefix1/images/%s.png' % logo))
        else:
            self.label.setPixmap(QtGui.QPixmap())
        
        

#    def accept(self):
#        try:
#            login    = self._savedLogin or forceString(self.edtLogin.text())
#            password = self._savedPassword or forceString(self.edtPassword.text())
#
#            encodedLogin = unicode(login).encode('utf-8')
#            encodedPassword = unicode(password).encode('utf8')
#            
#
#            if (QtGui.qApp.preferences.dbNewAuthorizationScheme):
#                hashedPassword = hashlib.md5(encodedPassword).hexdigest()
#                connectionAddInfo = {'user' : createLogin(encodedLogin),
#                                  'password' : hashedPassword}
#                QtGui.qApp.openDatabase(connectionAddInfo)
#            
#            isTruePassword, userId = verifyUserPassword(login, password)
#            if isTruePassword:
#                self._userId = userId
#                self._demoMode = False
#                QtGui.QDialog.accept(self)
#                return
#            if login == demoUserName and password == '' and QtGui.qApp.demoModePosible():
#                self._userId = None
#                self._demoMode = True
#                QtGui.QDialog.accept(self)
#                return
#            QtGui.QMessageBox.critical( self, u"Внимание", u"Имя пользователя или пароль неверны", QtGui.QMessageBox.Close)
#        except Exception, e:
#            message = unicode(e)
#            if message.count(u"Access denied for user"):
#                message = u"Имя пользователя или пароль неверны, либо вход с систему запрещен"
#            QtGui.QMessageBox.critical(self, u"", message, QtGui.QMessageBox.Close)


    def userId(self):
        return self._userId


    def demoMode(self):
        return self._demoMode


    def setLoginName(self, loginName):
        self.edtLogin.setText(loginName)
        if loginName:
            self.edtPassword.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            self.edtLogin.setFocus(QtCore.Qt.OtherFocusReason)


    def loginName(self):
        return self.edtLogin.text()
    
    def password(self):
        return self.edtPassword.text()
        
    def isSavePassword(self):
        return self.chkSavePassword.isChecked()
        
    def on_chkSavePassword_toggled(self, checked):
        self.chkSavePassword.setStyleSheet('color:red' if checked else '')
        if checked:
            QtGui.QMessageBox.information(self, u'Внимание!!!', 
                                          self.chkSavePassword.toolTip(), 
                                          buttons = QtGui.QMessageBox.Ok)
