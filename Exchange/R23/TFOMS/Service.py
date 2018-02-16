# -*- coding: utf-8 -*-
import datetime
import functools
import logging
import socket
import uuid
from PyQt4 import QtGui
from suds import WebFault
from suds.cache import DocumentCache
from suds.client import Client
from urllib2 import HTTPError, URLError

from library.Enum import CEnum
from library.Utils import forceString, forceUnicode


class SocketError(CEnum):
    PermissionDenied = 10013
    nameMap = {
        PermissionDenied: u'Доступ к сервису заблокирован, проверьте настройки фаервола или отключите его'
    }
    RequestTimeoutMessage = u'Время ожидания запроса истекло'


class CServiceTFOMSException(Exception):
    def __init__(self, message=u'', resp=None):
        self.message = message
        self.resp = resp

    def __str__(self):
        return u'{0}{1}'.format(self.message,
                                u'\n%s' % self.resp if self.resp else u'')


def exceptionHandler(reraise=True, onexcept=None, logger=None):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            try:
                try:
                    result = method(*args, **kwargs)
                except socket.timeout:
                    raise CServiceTFOMSException(SocketError.RequestTimeoutMessage)
                except socket.error as e:
                    raise CServiceTFOMSException(SocketError.getName(e.errno) or unicode(e))
                except HTTPError as e:
                    raise CServiceTFOMSException(unicode(e), resp=e.read())
                except URLError as e:
                    raise CServiceTFOMSException(unicode(e))
                except WebFault as e:
                    raise CServiceTFOMSException(unicode(e))
                else:
                    return result
            except CServiceTFOMSException as e:
                if logger:
                    logger.exception(e)
                if reraise:
                    raise e
                else:
                    return onexcept

        return wrapper

    return decorator


logger = logging.getLogger('suds.client')
handleExceptions = exceptionHandler(reraise=True, logger=logger)
logExceptions = functools.partial(exceptionHandler, reraise=False, logger=logger)


class CServiceTFOMS(object):
    u""" Базовый класс для обмена с сервисами ТФОМС """

    _instance = None

    def __init__(self, wsdl='', username='', password='', senderCode='', logFilename=None, timeout=None):
        self._logger = logging.getLogger('suds.client')
        if logFilename:
            self._logger.addHandler(logging.FileHandler(logFilename))
        else:
            self._logger.addHandler(logging.NullHandler())
        formatter = logging.Formatter('[%(levelname)s][%(asctime)s][%(module)s:%(funcName)s:%(lineno)d] %(message)s')
        for handler in self._logger.handlers:
            handler.setFormatter(formatter)
        self._logger.setLevel(logging.DEBUG)
        self._username = username
        self._password = password
        self._senderCode = senderCode
        self._wsdl = wsdl
        self._cli = None
        self._timeout = timeout

    @property
    def cli(self):
        u"""
        :rtype: Client
        """
        if self._cli is None:
            try:
                self._cli = Client(self._wsdl, timeout=self._timeout)
                self._cli.set_options(cache=DocumentCache())
            except URLError as e:
                self._logger.exception(e)
                raise CServiceTFOMSException(u'Ошибка подключения к серверу ТФОМС: ({0})\n{1}'.format(self._wsdl,
                                                                                                      forceUnicode(e)))
        return self._cli

    @classmethod
    def createInstance(cls, wsdl='', logFilename=None, timeout=None):
        prefs = QtGui.qApp.preferences.appPrefs
        username = forceString(prefs.get('AttachLogin', ''))
        return cls(wsdl=wsdl or forceString(prefs.get('AttachUrl', '')),
                   username=username,
                   password=forceString(prefs.get('AttachPassword', '')),
                   senderCode=username,
                   logFilename=logFilename,
                   timeout=timeout)

    @classmethod
    def getInstance(cls, wsdl='', logFilename=None, timeout=None):
        if cls._instance is None:
            cls._instance = cls.createInstance(wsdl, logFilename, timeout)
        return cls._instance

    def getPackageInformation(self):
        packinf = self.cli.factory.create('cPackageInformation')
        packinf.p10_pakagedate = datetime.datetime.today()
        packinf.p11_pakagesender = self._senderCode,
        packinf.p12_pakageguid = str(uuid.uuid4())
        packinf.p13_zerrpkg = 0
        packinf.p14_errmsg = ''
        return packinf

    def testConnect(self):
        u"""
        Проверка связи с сервером ТФОМС
        :return: TestConnectStatus.*
        """
        try:
            return self.cli.service.MakeTestConnect()
        except WebFault as e:
            self._logger.exception(e)
            raise e

    def setLoginAccess(self, username, password, senderCode, oldPassword=None):
        u"""
        Регистрация МО в сервисе ТФОМС
        :return: LoginError.*
        """
        try:
            return self.cli.service.SetLoginAccess(
                sendercode=senderCode,
                username=username,
                password=password,
                oldpassword=oldPassword
            )
        except WebFault as e:
            self._logger.exception(e)
            raise
