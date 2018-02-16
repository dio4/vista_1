# -*- coding: utf-8 -*-

import logging
import os
import urllib2
from PyQt4 import QtGui
from xml.dom import minidom
from xml.etree import ElementTree

from Exchange.alfalab.types import BlankFileQuery, BlankFileQueryRequest, Message, ReferralResultsRequest, ReferralResultsResponse
from Exchange.alfalab.utils import CAlfalabException
from library.Utils import forceString


class CAlfalabService(object):
    _instance = None

    headers = {
        'content-type': 'application/xml'
    }

    LogMsg = 'ALFALAB SERVICE'

    def __init__(self, url, credentials, logger, timeout=10):
        self.url = url
        self.credentials = credentials
        self.logger = logger
        self.timeout = timeout

    @staticmethod
    def toPrettyXML(xml):
        return minidom.parseString(xml).toprettyxml()

    @classmethod
    def createConnection(cls):
        formatter = logging.Formatter('[%(asctime)s] %(message)s')
        handler = logging.FileHandler(os.path.join(QtGui.qApp.logDir, 'alfalab.log'))
        handler.setFormatter(formatter)
        logger = logging.Logger('alfalab')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        prefs = QtGui.qApp.preferences.appPrefs
        return cls(
            forceString(prefs.get('alfalabHost', '')),
            {
                'Sender'  : forceString(prefs.get('alfalabSender', '')),
                'Receiver': forceString(prefs.get('alfalabReceiver', '')),
                'Password': forceString(prefs.get('alfalabPassword', ''))
            },
            logger
        )

    @classmethod
    def getConnection(cls):
        if cls._instance is None:
            cls._instance = cls.createConnection()
        return cls._instance

    def send(self, element, saveToFileName=None):
        requestData = ElementTree.tostring(element, 'utf-8')
        req = urllib2.Request(self.url, headers=self.headers, data=requestData)
        url = req.get_full_url()
        self.logger.debug('REQUEST [{0}]:\n'.format(url) + self.toPrettyXML(requestData))

        try:
            response = urllib2.urlopen(req, timeout=self.timeout)
            if saveToFileName is not None:
                responseInfo = response.info()
                if responseInfo['content-type'] in ('application/binary', 'application/pdf'):
                    with open(saveToFileName, mode="wb") as f:
                        f.write(response.read())
                    return True

            respElement = ElementTree.fromstring(response.read())
            self.logger.debug('RESPONSE:\n' + ElementTree.tostring(respElement, 'utf-8'))
            return respElement

        except urllib2.HTTPError as e:
            if e.code == 404:
                self.logger.exception(e.read())
                return None
            self.logger.exception(u"HTTP ERROR [{0}]: {1}, REQUESTED URL: {2}".format(e.code, e.message, url))
            self.logger.exception(e.read())

        except urllib2.URLError as e:
            self.logger.error(u"URL ERROR [{0}], REQUESTED URL: {1}".format(e.reason, url))
            raise CAlfalabException(u'CONNECTION ERROR: {0}'.format(e.reason))

        except Exception as e:
            self.logger.exception(e)
            raise

    @staticmethod
    def checkResponse(element):
        if element.get('MessageType') == 'error':
            msg = Message.createFromElement(element)
            raise CAlfalabException(msg.Error)

    def getReferralResults(self, referral):
        u"""
        Запрос результатов по заявке
        :param referral: Referral: основная информация о заявке
        :return: ReferralResultsResponse
        """
        self.logger.debug(u'{0}: GET REFERRAL RESULTS [Nr={1}, MisId={2}, LisId={3}]'.format(
            self.LogMsg, referral.Nr, referral.MisId, referral.LisId
        ))
        try:
            reqElement = ReferralResultsRequest(referral, **self.credentials).toElement()
            resp = self.send(reqElement)
            self.checkResponse(resp)

            result = ReferralResultsResponse.createFromElement(resp)
            if result.Error:
                raise CAlfalabException(result.Error)

            return result

        except CAlfalabException:
            raise

        except Exception as e:
            self.logger.exception(e)
            raise

    def getBlankFile(self, fileName, BlankId=None, BlankGUID=None):
        u"""
        Загрузка файла-бланка с результатами (не используется)
        :param fileName: str
        :param BlankId: BlanksItem.BlankId
        :param BlankGUID: BlanksItem.BlankGUID
        :return: ElementTree
        """
        self.logger.debug(u'{0}: GET BLANK FILE [BlankId={1}, BlankGUID={2}]: SAVE TO {3}'.format(self.LogMsg, BlankId, BlankGUID, fileName))
        try:
            reqElement = BlankFileQueryRequest(BlankFileQuery(BlankId=BlankId, BlankGUID=BlankGUID), **self.credentials).toElement()
            resp = self.send(reqElement, fileName)
            if isinstance(resp, ElementTree.Element):
                self.checkResponse(resp)

            return resp

        except CAlfalabException:
            raise

        except Exception as e:
            self.logger.exception(e)
            raise
