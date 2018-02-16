#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from library.Utils import *

# Получаем значение счетчика для договора/счета - пациент не указывается.
def getContractDocumentNumber(counterId):
    return getDocumentNumber(None, counterId)

# Значение счетчика для внешней учетной системы
def getAccountingSystemIdentifier(counterId):
    return getDocumentNumber(None, counterId)

def getDocumentNumber(clientId, counterId):
    db = QtGui.qApp.db
    while True:
        query = db.query('SELECT getCounterValue(%d)'%counterId)
        if query.next():
            value = forceInt(query.value(0))
            if value:
                record = db.getRecord('rbCounter', '`prefix`, `postfix`, `separator`', counterId)
                prefix = forceString(record.value('prefix'))
                postfix = forceString(record.value('postfix'))
                separator = forceString(record.value('separator'))
                return formatDocumentNumber(prefix, postfix, separator, value, clientId)

#example: formatDocumentNumber('date(yy:MM:dd);id(2)', 'id();str(GD23)', '--', 111, 4442) ### `postfix` like `prefix`
# Префикс/постфикс - это разделенные через точку с запятой блоки данных (без кавычек):
#   "date(<формат_даты>)" - текущая дата (на момент формирования имени) в указанном формате
#       "D" или "d" - обозначение дня без предшествующего нуля (1-31).
#       "DD" или "dd" - обозначение дня с предшествующим нулем (01-31).
#       "DDD" или "ddd" - обозначение дня в виде сокращенного наименования недели в соотв. с локалью системы(Mon-Sun).
#       "DDDD" или "dddd" - обозначение дня в виде полного наименования недели в соотв. с локалью системы (Monday-Sunday).
#       "M" или "m" - обозначение месяца без предшествующего нуля (1-12).
#       "MM" или "mm" - обозначение месяца с предшествующим нулем (01-12).
#       "MMM" или "mmm" - обозначение месяца в виде сокращенного имени в соотв. с локалью системы(Jan-Dec).
#       "MMMM" или "mmmm" - обозначение месяца в виде полного имени в соотв. с локалью системы (January-December).
#       "YY" или "yy" - обозначение года в двухзначном формате(00-99).
#       "YYYY" или "yyyy" - обозначение года в четырехзначном формате(0000-9999).
#   "id(<код_внешней_системы>)" - Идентификатор пациента (ClientIdentification.identifier)
#       в системе с кодом <код_внешней_системы> (rbAccountingSystem.code).
#   "str(<произвольная_постоянная_строка>)" - постоянная произвольная строка
#
#   Пример: prefix = "date(dd.MM.yyyy);str(__);id(test)"

def formatDocumentNumber(prefix, postfix, separator, value, clientId = None):
    def getDatePrefix(val):
        val = val.replace('Y', 'y').replace('m', 'M').replace('D', 'd')
        if val.count('y') not in [0, 2, 4] or val.count('M')>2 or val.count('d')>2:
            return None
        s = QDate.currentDate().toString(val)
        if QDate.fromString(s,val).isValid():
            return unicode(s)
        return None

    def getIdPrefix(val):
        if val == '' or not clientId:
            return str(clientId) if clientId else ''
        stmt = 'SELECT `identifier` FROM ClientIdentification JOIN rbAccountingSystem ON rbAccountingSystem.`id`=ClientIdentification.`accountingSystem_id` WHERE ClientIdentification.`client_id`=%d AND rbAccountingSystem.`code`=\'%s\'' %(clientId, val)
        query = QtGui.qApp.db.query(stmt)
        if query.first():
            return forceString(query.value(0))
        return None

    def getStrAddition(val):
        return val

    def getPre_Post_fixValue(ppValue):
        prefixTypes = {'date':getDatePrefix, 'id':getIdPrefix, 'str':getStrAddition}
        prefixList = ppValue.split(';')
        result = []
        for p in prefixList:
            for t in prefixTypes:
                f = p.find(t)
                if f == 0:
                    tl = len(t)
                    val = p[tl:]
                    if val.startswith('(') and val.endswith(')'):
                        val = prefixTypes[t](val.replace('(', '').replace(')', ''))
                        if val:
                            result.append(val)
        return result
    prefix  = getPre_Post_fixValue(prefix)  if prefix  else []
    postfix = getPre_Post_fixValue(postfix) if postfix else []
    return separator.join(prefix+['%d'%value]+postfix)
