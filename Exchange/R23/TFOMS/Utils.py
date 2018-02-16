# -*- coding: utf-8 -*-
from PyQt4 import QtGui

from library.Enum import CEnum
from library.Utils import forceStringEx


class MakeTestConnectResponse(CEnum):
    u""" Возваращаемые значения метода MakeTestConnect """
    nameMap = {
        0: u'Ошибка соединения',
        1: u'Подключение установлено'
    }


class SetLoginAccessResponse(CEnum):
    u""" Возваращаемые значения метода SetLoginAccess """
    nameMap = {
        1 : u'Операция завершилась успешно',
        0 : u'Неизвестная ошибка',
        -1: u'Данные неполны',
        -2: u'Пароль указан неверно',
        -3: u'Указанный логин уже зарегистрирован в БД'
    }


class ResponsePackageCode(CEnum):
    u""" Код ответа """
    Rejected = 1000
    HasErrors = 1001
    UnknownPackageError = 1003

    Accepted = 2000


class PolicyType(CEnum):
    u""" Тип документа, подтверждающего факт страхования по обязательному медицинскому страхованию """
    Old = 1
    Temporary = 2
    New = 3
    Electronic = 4
    UEK = 5

    nameMap = {
        Old       : u'Полис ОМС старого образца',
        Temporary : u'Временное свидетельство',
        New       : u'Полис ОМС единого образца',
        Electronic: u'Электронный полис ОМС единого образца',
        UEK       : u'Полис ОМС в составе УЭК'
    }


class KladrOkatoMap(object):
    u""" KLADR.CODE -> KLADR.OCATD """

    _codeMap = {}

    @classmethod
    def getOKATO(cls, kladrCode):
        if not kladrCode: return ''
        if kladrCode not in cls._codeMap:
            cls._codeMap[kladrCode] = forceStringEx(QtGui.qApp.db.translate('kladr.KLADR', 'CODE', kladrCode, 'OCATD', idFieldName='CODE'))
        return cls._codeMap[kladrCode]
