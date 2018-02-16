# -*- coding: utf-8 -*-
import uuid
from library.Utils       import *
from IdentService_client import *

class CTF78IdentService:
    def __init__(self, url, login, password):
        self.port = None
        self.url = url
        self.login = login
        self.password = password
        self.smoList = None
        self.geonimNameList = None
        self.geonimTypeList = None
        self.TAreaList = None


    def getPort(self):
        if self.port is None:
            loc = IdentServiceLocator()
            self.port = loc.getIdentPort(self.url)
        return self.port


    def getSmoList(self):
        if self.smoList is None:
            req = getIdSmo()
            req._arg0 = self.login
            req._arg1 = self.password
            resp = self.getPort().getIdSmo(req)
            self.smoList = self.parseList(resp)
            if self.smoList:
                return self.smoList
            else:
                return Exception
        else:
            return self.smoList


    def getGeonimNameList(self):
        if self.geonimNameList is None:
            req = getIdGeonimName()
            req._arg0 = self.login
            req._arg1 = self.password
            resp = self.getPort().getIdGeonimName(req)
            self.geonimNameList = self.parseList(resp)
        return self.geonimNameList


    def getGeonimTypeList(self):
        if self.geonimTypeList is None:
            req = getIdGeonimType()
            req._arg0 = self.login
            req._arg1 = self.password
            resp = self.getPort().getIdGeonimType(req)
            self.geonimTypeList = self.parseList(resp)
        return self.geonimTypeList


    def getTAreaList(self):
        if self.TAreaList is None:
            req = getIdTArea()
            req._arg0 = self.login
            req._arg1 = self.password
            resp = self.getPort().getIdTArea(req)
            self.TAreaList = self.parseList(resp)
        return self.TAreaList


    def getPolicy(self, firstName, lastName, patrName, sex, birthDate, policySerial='', policyNumber='', docSerial='', docNumber=''):
        identTO = ns0.identTO_Def('identTO')
        identTO._idCase = str(uuid.uuid1())
        today = QtCore.QDate.currentDate()
        identTO._dateBegin  = today.toString('yyyy-MM-dd')
        identTO._surname    = lastName
        identTO._name       = firstName
        identTO._secondName = patrName
        identTO._birthday = birthDate.toString('yyyy-MM-dd')
        identTO._idTArea      = 0   # fake value
        identTO._idGeonimName = 0   # fake value
        identTO._idGeonimType = 0   # fake value
        identTO._house        = '' # fake value
        identTO._polisS = policySerial
        identTO._polisN = policyNumber
        identTO._docNumber = docNumber
        req = doIdentification()
        req._arg0 = self.login
        req._arg1 = self.password
        req._arg2 = identTO
        resp = self.getPort().doIdentification(req)
        if resp._return._numTest > 0:
            result = smartDict()
            result.smoId = self.getSmoId(resp._return._idSmo)
            try: #if ZSI returned str
                result.policySerial = resp._return._polisS.decode('utf8')
                result.policyNumber = resp._return._polisN.decode('utf8')
            except UnicodeEncodeError: #if ZSI returned unicode
                result.policySerial = resp._return._polisS
                result.policyNumber = resp._return._polisN
            result.policyTypeId = self.getPolicyTypeId(resp._return._agrType)
            result.begDate = QDate.fromString(resp._return._dateBegin, QtCore.Qt.ISODate) if resp._return._dateBegin else QtCore.QDate()
            result.endDate = QDate.fromString(resp._return._dateEnd, QtCore.Qt.ISODate) if resp._return._dateEnd else QtCore.QDate()
            result.attach = ''
            result.attachList = []
            if resp._return._attachList:
                for v in resp._return._attachList._attachItem:
                    wo = getIdMo()
                    wo._arg0 = self.login
                    wo._arg1 = self.password
                    respMo = self.getPort().getIdMo(wo)
                    for k in respMo._return:
                        if forceString(k._item[0]) == forceString(v._idMo):
                            strMo = k._item[1]
                            result.attachList.append(unicode(strMo, 'utf-8') if isinstance(strMo, str) else strMo)
                            attachRec = QtGui.qApp.db.getRecordEx('OrgStructure', 'id', 'attachCode = %s' % strMo[1:7])
                            if attachRec:
                                result.attach = forceString(attachRec.value('id'))
            return result
        else:
            return None


    @staticmethod
    def parseList(resp):
        result = []
        for items in resp._return:
            code = int(items._item[0])
            try:
                name = items._item[1].decode('utf8')
            except UnicodeEncodeError: #if type(name) == unicode
                name = items._item[1]
            result.append((code, name))
        return result


    @staticmethod
    def tupleToQDate(t):
        if t and len(t)>=3:
            return QtCore.QDate(t[0], t[1], t[2])


    def getSmoId(self, smoCode):
        name = dict(self.getSmoList()).get(smoCode,'')
        if name:
            db = QtGui.qApp.db
            table = db.table('Organisation')
            record = db.getRecordEx(table, 'id', [ table['deleted'].eq(0), table['isInsurer'].eq(1), table['fullName'].eq(name) ])
            if record:
                return forceRef(record.value(0))
        return None


    def getPolicyTypeId(self, agrType):
        if agrType == 1: # произвв.
            code = '2'
        elif agrType == 2: # терр.
            code = '1'
        else:
            code = None
        db = QtGui.qApp.db
        return forceRef(db.translate('rbPolicyType', 'code', code, 'id'))


