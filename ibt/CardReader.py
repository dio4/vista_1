#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
## Copyright (C) 2012 SAMSON Group. All rights reserved.
##
#############################################################################
##
## Это программа является свободным программным обеспечением.
## Вы можете использовать, распространять и/или модифицировать её согласно
## условиям GNU GPL версии 3 или любой более поздней версии.
##
#############################################################################

import sys
from ctypes import RTLD_GLOBAL
from cffi import FFI

from CDefs import IBT_C_DECLARATION


class CCardReader(object):

    class CheckLibVersionError(Exception):
        """Не совпадает версия библиотеки ИБТ УЭК."""
        pass

    class LoadLibrariesError(Exception):
        """Не удалось загрузить библиотеку ИБТ УЭК."""
        pass

    class InitPKCS11Error(Exception):
        """Не удалось инициализировать PKCS11."""
        pass

    class ReaderNotFoundError(Exception):
        """Считыватель карт УЭК не найден."""
        pass

    class CardNotFoundError(Exception):
        """Карта УЭК не найдена."""
        pass

    class InitOperationError(Exception):
        """Не удалось инициализировать операцию."""

    class VerifyPinError(Exception):
        """Не удалось проверить PIN-код."""

    class ReadDataError(Exception):
        """Не удалось прочитать данные."""

    _IBT_VERSION = u'2.1 Модификация 1'

    _IBT_LIBRARIES_WIN32 = (
        ('halCommon', 'HAL_Common.dll'),
        ('halParameters', 'HAL_Parameters.dll'),
        ('halRTC', 'HAL_RTC.dll'),
        ('halProtocol', 'HAL_Protocol.dll'),
        ('halSCReader', 'HAL_SCReader.dll'),
        ('ruCrypto', 'ru.cryptodsb.dll'),
        ('comCrypto', 'com.cryptodsb.dll'),
        ('cryptoLib', 'CryptoLib.dll'),
        ('cardLib', 'CardLib.dll'),
        ('opLib', 'OpLib.dll'))

    _IBT_LIBRARIES_LINUX = (
        ('halCommon', 'libhal_common.so'),
        ('halParameters', 'libhal_parameters.so'),
        ('halRTC', 'libhal_rtc.so'),
        ('halProtocol', 'libhal_protocol.so'),
        ('halSCReader', 'libhal_screader.so'),
        ('openSSL', 'libcrypto.so'),
        ('fipGost', 'libfip_gost.so'),
        ('fipRsaDes', 'libfip_rsades.so'),
        ('cryptoLib', 'libcryptolib.so'),
        ('cardLib', 'libcardlib.so'),
        ('opLib', 'liboplib.so'))

    _IBT_COMMON_DATA_REQUEST = (
        '1-2-DF27',  # СНИЛС
        '1-2-DF2B',  # Номер полиса ОМС
        '1-2-DF2D',  # Фамилия
        '1-2-DF2E',  # Имя
        '1-2-DF2F',  # Отчество
        '1-2-5F2B',  # Дата рождения
        '1-2-DF24',  # Место рождения
        '1-2-5F35',  # Пол
        '3-1-0',     # ОГРН СМО
        '3-1-7',     # ОКАТО территории страхования
        '3-1-10')    # Дата начала полиса

    _IBT_DOCUMENT_DATA_REQUEST = (
        '1-5-9F7F',  # Тип
        '1-5-DF4A',  # Серия
        '1-5-DF4B',  # Номер
        '1-5-5F25',  # Дата выдачи
        '1-5-DF4C')  # Кем выдан

    def __init__(self, callbackPinRequest):
        IBT_LIBRARIES = self._IBT_LIBRARIES_WIN32 if sys.platform == 'win32' else self._IBT_LIBRARIES_LINUX
        self._ffi = FFI()
        try:
            self._libs = {}
            for libName, fileName in IBT_LIBRARIES:
                self._libs[libName] = self._ffi.dlopen(fileName, RTLD_GLOBAL)
        except:
            raise self.LoadLibrariesError()
        self._ffi.cdef(IBT_C_DECLARATION)
        # Проверяем версию библиотеки IBT
        self._checkLibVersion()
        # Инициализируем основные структуры
        cardHandle = self._ffi.new('IL_CARD_HANDLE *')
        readerHandle = self._ffi.new('HANDLE_READER *')
        cardHandle.hRdr = readerHandle
        cryptoHandle = self._ffi.new('HANDLE_CRYPTO *')
        cardHandle.hCrypto = cryptoHandle
        opContext = self._ffi.new('s_opContext *')
        # Инициализируем устройство PKCS11
        isPKCS11 = self._initPKCS11(cryptoHandle)
        try:
            # Подключаемся к карте УЭК
            self._openCard(cardHandle)
            # Инициализируем операцию УЭК
            self._initOperation(opContext, cardHandle, callbackPinRequest)
            # Чтение данных карты УЭК
            self._readCardData(opContext)
        finally:
            self._libs['opLib'].opApiDeinitOperation(opContext)
            if isPKCS11:
                self._libs['cryptoLib'].cryptoDeinit(cryptoHandle)

    @property
    def cardNumber(self):
        return self._cardNumber

    @property
    def cardBegDate(self):
        return '%s.%s.20%s' % (self._begDate[-2:], self._begDate[2:4], self._begDate[:2])

    @property
    def cardEndDate(self):
        return '%s.%s.20%s' % (self._endDate[-2:], self._endDate[2:4], self._endDate[:2])

    @property
    def SNILS(self):
        return self._commonBlocks.get('1-2-DF27', u'')

    @property
    def policyNumber(self):
        return self._commonBlocks.get('1-2-DF2B', u'')

    @property
    def lastName(self):
        return self._commonBlocks.get('1-2-DF2D', u'')

    @property
    def firstName(self):
        return self._commonBlocks.get('1-2-DF2E', u'')

    @property
    def patrName(self):
        return self._commonBlocks.get('1-2-DF2F', u'')

    @property
    def birthDate(self):
        birthDate = self._commonBlocks.get('1-2-5F2B', u'')
        return u'' if not birthDate else u'%s.%s.%s' % (birthDate[-2:], birthDate[4:6], birthDate[:4])

    @property
    def birthPlace(self):
        return self._commonBlocks.get('1-2-DF24', u'')

    @property
    def sex(self):
        return self._commonBlocks.get('1-2-5F35', u'')

    @property
    def insurerOGRN(self):
        return self._commonBlocks.get('3-1-0', u'')[1:]

    @property
    def insurerOKATO(self):
        return self._commonBlocks.get('3-1-7', u'')[1:]

    @property
    def policyBegDate(self):
        policyBegDate = self._commonBlocks.get('3-1-10', u'')
        return u'' if not policyBegDate else u'%s.%s.%s' % (policyBegDate[-2:], policyBegDate[4:6], policyBegDate[:4])

    @property
    def documentType(self):
        # Соответствия кодов типа документа карты и поля federalCode таблицы rbDocumentType
        return {u'01': u'14'}.get(self._documentBlocks.get('1-5-9F7F', u''), u'')

    @property
    def documentSerial(self):
        return self._documentBlocks.get('1-5-DF4A', u'')

    @property
    def documentNumber(self):
        return self._documentBlocks.get('1-5-DF4B', u'')

    @property
    def documentDate(self):
        return self._documentBlocks.get('1-5-5F25', u'')

    @property
    def documentOrigin(self):
        return self._documentBlocks.get('1-5-DF4C', u'')

    def _checkLibVersion(self):
        libVersion = self._ffi.new('IL_CHAR[20]')
        appVersion = self._ffi.new('IL_CHAR[20]')
        self._libs['opLib'].opApiGetVersion(libVersion, appVersion)
        if self._IBT_VERSION != self._winEncodingToUnicode(self._ffi.string(libVersion)):
            raise self.CheckLibVersionError()

    def _initPKCS11(self, cryptoHandle):
        # Константы
        IL_PARAM_IF_PKCS11 = self._ffi.cast('IL_WORD', 998)

        isPKCS11 = self._ffi.new('IL_BYTE[1]', '1')
        self._libs['halParameters'].prmGetParameter(IL_PARAM_IF_PKCS11, isPKCS11, self._ffi.new('IL_DWORD *'))
        isPKCS11 = self._ffi.string(isPKCS11)
        if isPKCS11 and self._libs['cryptoLib'].cryptoInit(self._ffi.cast('IL_HANDLE_CRYPTO *', cryptoHandle)):
            raise self.InitPKCS11Error()
        return isPKCS11

    def _openCard(self, cardHandle):
        # Константы
        IL_PARAM_READERNAME = self._ffi.cast('IL_WORD', 14)
        ILRET_SCR_REMOVED_CARD = self._ffi.cast('IL_RETCODE', 302)

        self._readerName = self._ffi.new('IL_BYTE[128]')
        self._libs['halParameters'].prmGetParameter(IL_PARAM_READERNAME, self._readerName, self._ffi.new('IL_DWORD *'))
        initResult = self._libs['cardLib'].flInitReader(cardHandle, self._readerName)
        if initResult and initResult != int(ILRET_SCR_REMOVED_CARD):
            raise self.ReaderNotFoundError()
        if self._libs['cardLib'].clCardOpen(cardHandle):
            self._libs['cardLib'].flDeinitReader(cardHandle)
            raise self.CardNotFoundError()

    def _initOperation(self, opContext, cardHandle, callbackPinRequest):
        # Константы
        UEC_OP_PROVIDE_SERVICE = self._ffi.cast('IL_BYTE', 1)
        ILRET_OPLIB_ILLEGAL_PIN_TRIES_LEFT_1 = self._ffi.cast('IL_WORD', 4012)
        ILRET_OPLIB_ILLEGAL_PIN_TRIES_LEFT_16 = self._ffi.cast('IL_WORD', 4027)

        cardNumber = self._ffi.new('IL_CHAR[23]')
        cardVersion = self._ffi.new('IL_CHAR[4]')
        begDate = self._ffi.new('IL_CHAR[7]')
        endDate = self._ffi.new('IL_CHAR[7]')
        passPhase = self._ffi.new('IL_CHAR[51]')
        if self._libs['opLib'].opApiInitOperation(opContext, cardHandle, UEC_OP_PROVIDE_SERVICE, self._ffi.NULL,
                                                  self._ffi.cast('IL_WORD', 0), cardNumber, cardVersion, begDate,
                                                  endDate, passPhase, self._ffi.NULL):
            raise self.InitOperationError()
        self._cardNumber = self._ffi.string(cardNumber)
        self._begDate = self._ffi.string(begDate)
        self._endDate = self._ffi.string(endDate)
        passPhase = self._winEncodingToUnicode(self._ffi.string(passPhase)).strip()
        pin = callbackPinRequest(self.cardNumber, self.cardBegDate, self.cardEndDate, passPhase)
        pin = self._ffi.new('IL_CHAR[9]', self._unicodeToWinEncoding(pin[:8]))
        attempts = int(ILRET_OPLIB_ILLEGAL_PIN_TRIES_LEFT_16) - int(ILRET_OPLIB_ILLEGAL_PIN_TRIES_LEFT_1) + 1
        while attempts:
            if not self._ffi.string(pin):
                raise self.VerifyPinError()
            verifyResult = self._libs['opLib'].opApiVerifyCitizen(opContext, self._ffi.cast('IL_BYTE', 1), pin)
            if not verifyResult:
                break
            elif verifyResult < int(ILRET_OPLIB_ILLEGAL_PIN_TRIES_LEFT_1) or \
                    verifyResult > int(ILRET_OPLIB_ILLEGAL_PIN_TRIES_LEFT_16):
                raise self.VerifyPinError()
            attempts = verifyResult - int(ILRET_OPLIB_ILLEGAL_PIN_TRIES_LEFT_1) + 1
            pin = self._ffi.new('IL_CHAR[9]',
                                self._unicodeToWinEncoding(callbackPinRequest(attempts=attempts)[:8]))

    def _readCardData(self, opContext):

        def read(request):
            dataRequest = self._ffi.new('IL_CHAR[]', ';'.join(request))
            data = self._ffi.new('IL_CHAR[8192]')
            readResult = self._libs['opLib'].opApiReadCardData(opContext, dataRequest, data,
                                                               self._ffi.new('IL_WORD *', self._ffi.sizeof(data)))
            return readResult, self._winEncodingToUnicode(self._ffi.string(data))

        def parseBlocks(data):
            return dict(line.split('=') for line in data.split('\n') if line)

        readResult, data = read(self._IBT_COMMON_DATA_REQUEST)
        if readResult:
            raise self.ReadDataError()
        self._commonBlocks = parseBlocks(data)
        readResult, data = read(self._IBT_DOCUMENT_DATA_REQUEST)
        if readResult:
            self._documentBlocks = {}
        else:
            self._documentBlocks = parseBlocks(data)

    def _winEncodingToUnicode(self, string):
        if isinstance(string, str):
            return string.decode('cp1251')
        return string

    def _unicodeToWinEncoding(self, string):
        if isinstance(string, unicode):
            return string.encode('cp1251')
        return string


if __name__ == '__main__':

    def callbackPinRequest(cardNumber=None, begDate=None, endDate=None, passPhase=None, attempts=None):
        if attempts:
            print u'Неверный PIN-код, осталось попыток: %s' % attempts
        else:
            print u'Номер карты: %s' % cardNumber
            print u'Дата начала: %s' % begDate
            print u'Дата окончания: %s' % endDate
            if passPhase:
                print u'Контрольное приветствие: %s' % passPhase
        return raw_input(u'PIN: ')

    try:
        cardReader = CCardReader(callbackPinRequest)
        print u'\r\nДанные с карты успешно прочитаны'
        print u'СНИЛС: %s' % cardReader.SNILS
        print u'Полис ОМС: %s' % cardReader.policyNumber
        print u'Фамилия: %s' % cardReader.lastName
        print u'Имя: %s' % cardReader.firstName
        print u'Отчество: %s' % cardReader.patrName
        print u'Дата рождения: %s' % cardReader.birthDate
        print u'Место рождения: %s' % cardReader.birthPlace
        print u'Пол: %s' % cardReader.sex
        print u'ОГРН СМО: %s' % cardReader.insurerOGRN
        print u'ОКАТО СМО: %s' % cardReader.insurerOKATO
        print u'Дата начала действия полиса: %s' % cardReader.policyBegDate
        print u'\r\nДокумент, удостоверяющий личность'
        print u'Тип: %s' % cardReader.documentType
        print u'Серия: %s' % cardReader.documentSerial
        print u'Номер: %s' % cardReader.documentNumber
        print u'Дата выдачи: %s' % cardReader.documentDate
        print u'Кем выдан: %s' % cardReader.documentOrigin
    except CCardReader.CheckLibVersionError:
        print u'Не совпадает версия библиотеки ИБТ УЭК'
    except CCardReader.LoadLibrariesError:
        print u'Не удалось загрузить библиотеку ИБТ УЭК'
    except CCardReader.InitPKCS11Error:
        print u'Не удалось инициализировать PKCS11'
    except CCardReader.ReaderNotFoundError:
        print u'Считыватель карт УЭК не найден'
    except CCardReader.CardNotFoundError:
        print u'Карта УЭК не найдена'
    except CCardReader.InitOperationError:
        print u'Не удалось инициализировать операцию'
    except CCardReader.VerifyPinError:
        print u'Не удалось проверить PIN-код'
    except CCardReader.ReadDataError:
        print u'Не удалось прочитать данные'