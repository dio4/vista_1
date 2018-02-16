# -*- coding: utf-8 -*-
from library.Utils       import *
from wsrz3_client        import *

class CTF23IdentService:
    current_rid = 1
    def __init__(self, url, login, password):
        self.port = None
        self.url = url
        self.login = login
        self.password = password


    def getPort(self):
        if self.port is None:
            loc = wsrzService3Locator()
            debugFileName = os.path.join(QtGui.qApp.logDir, 'debugSoap.log')
            traceFile = open(debugFileName, 'a') if debugFileName is not None else None
            self.port = loc.getwsrzPort3(self.url, tracefile=traceFile)
        return self.port


    def getPolicy(self, codeMO, clientId, firstName, lastName, patrName, sex, birthDate, SNILS = '', policyType = '', policySerial='', policyNumber='', docType = '', docSerial='', docNumber=''):
        identTO = getPolicyInfoRequest3()
        today = QtCore.QDate.currentDate()

        # clientId может не быть, а поле RID обязательное и "внутренне уникальное". Это идентификатор сообщения, ни на что по идее не влияет.
        if not clientId:
            clientId = CTF23IdentService.current_rid
            CTF23IdentService.current_rid += 1
        identTO.paramSource = forceStringEx(codeMO)
        identTO.paramRID = forceInt(clientId)
        identTO.paramForDate = today.toString('yyyy-MM-dd')
        identTO.personSurname = forceStringEx(lastName)
        identTO.personName = forceStringEx(firstName)
        identTO.personPatronymic = forceStringEx(patrName)
        identTO.personSex = forceStringEx(u'м' if sex == 1 else u'ж' if sex == 2 else '')
        identTO.personBirthDate = birthDate.toString('yyyy-MM-dd') #(birthDate.year(), birthDate.month(), birthDate.day(), 0, 0, 0, 0)
        if docType and docNumber:
            identTO.identityType = forceInt(docType)
            identTO.identitySeries = forceStringEx(docSerial).replace(' ', '-') if docType in ('1', '3') else forceStringEx(docSerial) # Разделители взяты из ClientEditDialog
            identTO.identityNumber = forceStringEx(docNumber)
        identTO.Snils = forceString(SNILS) if unformatSNILS(SNILS) else ''
        if policyType and policyNumber:
            identTO.policyType = forceInt(policyType)
            if policySerial: identTO.policySeries = forceString(policySerial)
            identTO.policyNumber = forceString(policyNumber)

        resp = self.getPort().getPolicyInfo3(identTO)
        if resp:
            result = smartDict()
            badResult = smartDict()
            if resp.resultType == 2:
                if resp.resultCode == 1:
                    badResult.message = u'Ошибка: недостаточно данных для идентификации пользователя, либо данные заполнены некорректно.'
                elif resp.resultCode == 2:
                    badResult.message = u'Полис не найден: результат поиска неоднозначен.'
                elif resp.resultCode == 3:
                    badResult.message = u'Полис не найден.'
                else:
                    badResult.message = u'Неизвестная ошибка (тип 2)'
                return badResult
            elif resp.resultType == 3:
                badResult.message = u'Ошибка получения данных [%s].\nНеобходимо информировать ТФОМС.' % resp.resultCode
                return badResult
            result.birthDate = QDate.fromString(resp.personBirthDate, QtCore.Qt.ISODate) if resp.personBirthDate else QtCore.QDate()
            try: #if ZSI returned str
                result.lastName = resp.personSurname.decode('utf8')
                result.firstName = resp.personName.decode('utf8')
                result.patrName = resp.personPatronymic.decode('utf8')
                result.sex = resp.personSex.decode('utf8')
            except UnicodeEncodeError: #if ZSI returned unicode
                result.lastName = resp.personSurname
                result.firstName = resp.personName
                result.patrName = resp.personPatronymic
                result.sex = resp.personSex
            db = QtGui.qApp.db
            stmt = u'''
                SELECT Organisation.id
                FROM Organisation
                WHERE Organisation.deleted = 0
                    AND %s
                LIMIT 1
            '''

            if resp.policySmo:
                cond = u'Organisation.miacCode LIKE ' + forceString(resp.policySmo)
            else:
                cond = u'0'
            query = db.query(stmt % cond)
            if query.first():
                record = query.record()
                result.smoId = forceInt(record.value('id'))
            else:
                badResult.message = u'В базе МИС не найдена СМО с кодом \'%s\', обновление полиса невозможно.' % (resp.policySmo)
                return badResult

            result.policySerial = forceString(resp.policySeries)
            result.policyNumber = forceString(resp.policyNumber)
            stmt = u'''
                SELECT rbPolicyType.id
                FROM ClientPolicy
                INNER JOIN rbPolicyType ON rbPolicyType.id = ClientPolicy.policyType_id
                WHERE ClientPolicy.deleted = 0
                    AND ClientPolicy.serial LIKE '%(serial)s'
                    AND ClientPolicy.number LIKE '%(number)s'
            ''' % {'serial' : forceString(resp.policySeries),
                   'number' : forceString(resp.policyNumber)}
            query = db.query(stmt)
            if query.first() and resp.policySeries and resp.policyNumber:
                record = query.record()
                result.policyTypeId = forceString(record.value('id'))
            else:
                policyTypeId = forceString(db.translate('rbPolicyType', 'code', '1', 'id'))
                if policyTypeId:
                    result.policyTypeId = policyTypeId
                else:
                    badResult.message = u'Не удалось определить тип полиса'
                    return badResult

            result.Snils = forceString(resp.Snils)
            result.policyKindId = forceRef(db.translate('rbPolicyKind', 'regionalCode', resp.policyType, 'id'))
            result.begDate      = QDate.fromString(resp.policyFromDate, QtCore.Qt.ISODate) if resp.policyFromDate else QtCore.QDate()
            result.endDate      = QDate.fromString(resp.policyTillDate, QtCore.Qt.ISODate) if resp.policyTillDate else QtCore.QDate()
            result.dCode = forceString(resp.ddVP)
            result.dDATN = QDate.fromString(resp.ddDATN, QtCore.Qt.ISODate) if resp.ddDATN else QtCore.QDate()
            result.dDATO = QDate.fromString(resp.ddDATO, QtCore.Qt.ISODate) if resp.ddDATO else QtCore.QDate()
            result.dCODE_MO = forceInt(resp.ddCODE_MO)
            return result
        else:
            return None


