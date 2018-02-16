# -*- coding: utf-8 -*-
from PyQt4 import QtGui

def cleanConfigFile():
    QtGui.qApp.preferences.windowPrefs = dict()
    QtGui.qApp.preferences.tablePrefs = dict()
    # QtGui.qApp.preferences.appPrefs = dict()
    QtGui.qApp.preferences.save()
    QtGui.QMessageBox().information(None, u'Очистка файла конфигурации',
                                    u'Очистка была успешно завершена.')
