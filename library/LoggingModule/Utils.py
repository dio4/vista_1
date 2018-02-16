# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
import platform
import Logger

def prepareKwargsWindowAccess(kwargs):
    if not ('date' in kwargs): kwargs['date'] = unicode(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
    if not ('login_id' in kwargs): kwargs['login_id'] = Logger.loginId
    if not ('organisation_id' in kwargs): kwargs['organisation_id'] = QtGui.qApp.currentOrgId()

def prepareKwargsLogin(kwargs):
    if not ('start_date' in kwargs): kwargs['start_date'] = unicode(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
    if not ('person_id' in kwargs): kwargs['person_id'] = unicode(QtGui.qApp.userId)
    if not ('pc_name' in kwargs): kwargs['pc_name'] = platform.node().decode('cp1251')

def prepareKwargsClientChoice(kwargs):
    if not ('date' in kwargs): kwargs['date'] = unicode(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))

def prepareKwargsEventChoice(kwargs):
    if not ('date' in kwargs): kwargs['date'] = unicode(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))

def prepareKwargsReports(kwargs):
    if not ('date' in kwargs): kwargs['date'] = unicode(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
    if not ('lpu' in kwargs): kwargs['lpu'] = QtGui.qApp.currentOrgId()

def prepareKwargsPackages(kwargs):
    if not ('createDateTime' in kwargs): kwargs['createDateTime'] = unicode(QtCore.QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
    if not ('createPerson' in kwargs): kwargs['createPerson'] = QtGui.qApp.userId