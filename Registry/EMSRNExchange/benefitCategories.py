# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


from PyQt4 import QtCore, QtGui
if 'QXmlStreamReader' in QtCore.__dict__:
    from PyQt4.QtCore import QXmlStreamReader

#else:
#    from PyQt4.QtXml import QXmlStreamReader

from library.Utils          import forceString, getPref

from EMSRNExchange_client   import PersonBenefitCategoriesSoapIn, EMSRNExchangeLocator


class CResponceParser(QXmlStreamReader):
    def __init__(self, str):
        QXmlStreamReader.__init__(self, str)
        self._result = None
        self._lastName = None
        self._name = None
        self._patronymicName = None
        self._SNILS = None
        self._benefitCategories = []


    def parse(self):
        while (not self.atEnd()):
            self.readNext()

            if self.isStartElement():
                if self.name() == 'Person':
                    self.readPerson()
                else:
                    self.readUnknownElement()

            if self.hasError():
                return False
        return not self.hasError()


    def readPerson(self):
        assert self.isStartElement() and self.name() == 'Person'

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if self.name() == 'Result':
                    self._result = unicode(self.readElementText())
                elif self.name() == 'LastName':
                    self._lastName = unicode(self.readElementText())
                elif self.name() == 'Name':
                    self._name = unicode(self.readElementText())
                elif self.name() == 'PatronymicName':
                    self._patronymicName = unicode(self.readElementText())
                elif self.name() == 'SNILS':
                    self._SNILS = unicode(self.readElementText())
                elif self.name() == 'BenefitCategories':
                    self.readBenefitCategories()
                else:
                    self.readUnknownElement()

            if self.hasError():
                break


    def readBenefitCategories(self):
        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == 'BenefitCategory'):
                    default = self.attributes().value("Default").toString().toInt()[0]
                    code = unicode(self.readElementText())
                    self._benefitCategories.append((code, default))
                else:
                    self.readUnknownElement()

            if self.hasError():
                break


    def readUnknownElement(self):
        self.raiseError('Unkonwn element '+unicode(self.name().toString()))


def getBenefitCategories(lastName='', firstName='', patrName='', SNILS='00000000000', address='', name='', password=''):
    QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
    try:
        try:
            preferences = getPref(QtGui.qApp.preferences.appPrefs, 'EMSRNExchange', {})
            defaultAddress = forceString(getPref(preferences, 'address', EMSRNExchangeLocator.EMSRNExchangeSoap_address))
            defaultName = forceString(getPref(preferences, 'name', ''))
            defaultPassword = forceString(getPref(preferences, 'password', ''))

            loc = EMSRNExchangeLocator()
            port = loc.getEMSRNExchangeSoap(address or defaultAddress, timeout=30)
            req = PersonBenefitCategoriesSoapIn()
            req._User = name or defaultName
            req._Password = password or defaultPassword
            req._LastName = lastName
            req._Name = firstName
            req._PatronymicName = patrName
            req._SNILS = SNILS

            # call the remote method
            resp = port.PersonBenefitCategories(req)
            pars = CResponceParser(resp.PersonBenefitCategoriesResult)
            if pars.parse():
                return pars._result, pars._benefitCategories
        except:
            QtGui.qApp.logCurrentException()
        return None, None
    finally:
        QtGui.qApp.restoreOverrideCursor()


def checkBenefitCategoriesResult(res):
    if res == u'НАЙДЕН':
        return True, True
    elif res == u'НЕ НАЙДЕН':
        return True, False
    else:
        return False, False


#def getClientBenefitCategoriesById(clientId):
#    db = QtGui.qApp.db
#    record = db.getRecord('Client', 'lastName, firstName, patrName, SNILS', clientId)
#    if record:
#        return getBenefitCategories(
#            forceString(record.value('lastName')),
#            forceString(record.value('firstName')),
#            forceString(record.value('patrName')),
#            forceString(record.value('SNILS')))
#    else:
#        return None
