# -*- coding: utf-8 -*-

from library.LoggingModule.Log import Logger
import urllib2

from library.Utils import AnyRequest, forceString
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class CPrepareSoap():
    def __init__(self):
        self.message = u'<?xml version="1.0" encoding="UTF-8"?>'
        self.result = u''

    def addHeader(self, headerText):
        self.message += headerText + u'<soapenv:Header/><soapenv:Body>'

    def addSection(self, name):
        self.message += u'<%s>' % forceString(name)

    def closeSection(self, name):
        self.message += u'</%s>' % forceString(name)

    def addField(self, fieldText):
        self.message += forceString(fieldText)

    def getMessage(self):
        return forceString(self.message)

    def getResult(self):
        return forceString(self.result)

    def sendMessage(self, url):
        try:
            req_headers = {
                'Content-Type': 'text/plain; charset=utf-8',
            }

            req = AnyRequest(url, data=self.message.encode('utf-8'), method='POST', headers=req_headers)
            self.result = '\n'.join(urllib2.urlopen(req).readlines())
            logger = Logger('15part.log')
            logger.insertFileLog(message=self.message, result=self.result)

        except urllib2.HTTPError as e:
            print 'Error:' + ' ' + url
        except urllib2.URLError, e:
            print 'Error:' + e.reason + ' ' + url
        except Exception as e:
            print e