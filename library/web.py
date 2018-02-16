# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012-2013 ООО "Виста". All rights reserved.
##
#############################################################################

import os, sys
import webbrowser
import subprocess
import urllib2
import uuid

from PyQt4 import QtGui

from library.Utils  import forceString

def getDefaultBrowserPath():
    if sys.platform == 'win32':
        #import _winreg
        return webbrowser.get('windows-default')
    return -1

def openURLinDefaultBrowser(url):
    #browser = getDefaultBrowserPath()
    #if browser == -1:
    #    return -1
    try:
        os.startfile(url)
    except:
        QtGui.QMessageBox.warning(QtGui.qApp, u'Внимание!', u'В системе не найден браузер по умолчанию. Проверьте настройки '
                                        u'Вашего браузера или пропишите путь к нему в настройках умолчаний "ВИСТА-МЕД"',
                                        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
    return 0

def openURLinBrowser(url, browserPath):
    if browserPath:
        subprocess.Popen(browserPath + " " + url)
    else:
        openURLinDefaultBrowser(url)

def openInDicomViewer(postfix):
    url = forceString(QtGui.qApp.preferences.appPrefs.get('dicomViewerAddress', ''))
    browserPath = forceString(QtGui.qApp.preferences.appPrefs.get('browserPath', ''))
    if not url:
        QtGui.QMessageBox.warning(None, u'Внимание!', u'Для просмотра снимков необходимо указать в настройках адрес Dicom Viewer\'a.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        return

    #
    # register security token
    securityToken = forceString(uuid.uuid1()).replace('-', '')
    request = urllib2.Request(url + '?security_id=%s' % securityToken,
                              headers={"User-Agent": "Mozilla/5.0 (X11; U; Linux i686 (x86_64); en-US; rv:1.9.0.1) Gecko/2008070206 Firefox/3.0.1",
                                       "Accept-Charset": "win1251,utf-8;q=0.7,*;q=0.7",
                                       "charset": "utf-8",
                                       "Connection": "keep-alive"})
    urllib2.urlopen(request)

    if postfix.startswith('?'):
        postfix = postfix[1:]

    # open browser
    url = url + '?security_id=%s&' % securityToken + postfix
    res = openURLinBrowser(url, browserPath)
    if res == -1:
        QtGui.QMessageBox.warning(None, u'Внимание!', u'Просмотр снимков реализован только при использовании ОС Windows. Обратитесь в службу поддержки.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        return
