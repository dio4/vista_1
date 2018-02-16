# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012 Vista Software. All rights reserved.
##
#############################################################################

"""
Package doc string here
"""

import ctypes
from ctypes import *
from Ui_AskPin import Ui_Dialog
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from library.Preferences import isPython27
import os

if os.name == 'nt' and isPython27():
    try:
        OMSLib = WinDLL("oms_lib2.dll")
    except BaseException as e:
        err = create_string_buffer(1024)
        err.value = str(e)
        OMSLib = None
else:
    OMSLib = None
    
UECMaxStringLength = 2048 + 1

##//  Активация автомата
E_ACTIVATE                             = 0x0000
##// Ожидание выбора услуги
E_SERVICE_SELECTING                    = 0x0001
##// Услуга выбрана
E_SERVICE_SELECTED                     = 0x0002
#// Ожидание установки карты в ридер
E_CARD_WAITING                         = 0x0003
#// Карта установлена
E_CARD_INSERTED                        = 0x0004
#// Ожидание извлечения карты из ридера             
E_CARD_RELEASING                       = 0x0005
#// Карта извлечена
E_CARD_RELEASED                        = 0x0006
#// Запрос на получение метаинформации по услуге
E_METAINFO_REQUESTED                   = 0x0007
#// Метаинформация по услуге получена и сохранена в контексте
E_METAINFO_ENTERED                     = 0x0008
#// Запрос на ввод ПИН
E_PIN_REQUESTED                        = 0x0009
#// Введен ПИН
E_PIN_ENTERED                          = 0x000A
#// Повторный ввод ПИН
E_PIN_RETRY_REQUESTED                  = 0x000B
#// Запрос на получение внешних данных для оказания услуги
E_EXTRA_DATA_REQUESTED                 = 0x000C
#// Внешние данные получены
E_EXTRA_DATA_ENTERED                   = 0x000D
#// Данные с карты подготовлены
E_CARD_DATA_PREPARED                   = 0x000E
#// Данные запроса на оказание услуги подготовлены
E_SERVICE_REQUEST_DATA_PREPARED        = 0x000F
#// Запрос на аутентификацию ИД-приложения сформирован
E_APP_AUTH_REQUEST_PREPARED            = 0x0010
#// Обработка результатов аутентификации ИД-приложения
E_PROCESS_APP_AUTH_RESPONSE_DATA       = 0x0011
#// Запрос на ввод нового ПИН
E_NEW_PIN_REQUESTED                    = 0x0012
#// Новый ПИН введён
E_NEW_PIN_ENTERED                      = 0x0013
#// Запрос на ввод подтверждающнго ПИН
E_CONFIRM_PIN_REQUESTED                = 0x0014
#// Подтверждающий ПИН введён
E_CONFIRM_PIN_ENTERED                  = 0x0015
#// Выбор данных для изменения
E_SELECT_EDITING_CARD_DATA             = 0x0016
#// Данных для редактирования выбраны
E_EDITING_CARD_DATA_SELECTED           = 0x0017
#// Запрос на редактирование считанных с карты данных
E_CARD_DATA_EDIT_REQUSTED              = 0x0018
#// Редактируемые карточные данные изменены
E_CARD_DATA_MODIFIED                   = 0x0019
#// Редактируемые карточные данные не изменены
E_CARD_DATA_NOT_MODIFIED               = 0x001A
#// Запрос на ввод КРП
E_PUK_REQUESTED                        = 0x001B
#// Введен КРП
E_PUK_ENTERED                          = 0x001C
#// Запрос на повторный ввод КРП
E_PUK_RETRY_REQUESTED                  = 0x001D
#// Запрос на ввод нового КРП
E_NEW_PUK_REQUESTED                    = 0x001E
#// Новый КРП введён
E_NEW_PUK_ENTERED                      = 0x001F
#// Требуется установка защищённой сессии с эмитентом
E_ISSUER_SESSION_REQUESTED             = 0x0020
#// Криптограмма аутентификации хоста для защищённой сессии с эмитентом подготовлена
E_ISSUER_AUTH_CRYPTOGRAMM_READY        = 0x0021
#// Требуется проверка установленной защищённой сессии с эмитентом
E_CHECK_ISSUER_SESSION_REQUESTED       = 0x0022
#// Установленная защищённая сессии с эмитентом проверена
E_ISSUER_SESSION_CHECKED               = 0x0023
#// Ожидание пакета APDU-комманд
E_APDU_PACKET_WAITING                  = 0x0024
#// Пакет APDU-комманд введён
E_APDU_PACKET_ENTERED                  = 0x0025
#// Пакет APDU-комманд оттствует
E_APDU_PACKET_ABSENT                   = 0x0026
#// Обработка хостом пакета APDU-комманд после их исполнения
E_PROCESS_APDU_PACKET                  = 0x0027
#// Обработка хостом пакета APDU-комманд успешно завершена
E_APDU_PACKET_PROCESSED                = 0x0028
#// Запрос на получение хэш XML-запроса услуги
E_HASH_REQUESTED                       = 0x0029
#// Хэш XML-запроса услуги введён
E_HASH_ENTERED                         = 0x002A
#// Ввод строки-запроса на чтение карточных данных для оказания услуги
E_CARD_DATA_REQUESTED                  = 0x002B
#// Строка-запрос на чтение карточных данных введёна
E_CARD_DATA_DESCR_ENTERED              = 0x002C
#// Требуется изъятие карты
E_CARD_CAPTURE_REQUESTED               = 0x002D
#// Карта изъята
E_CARD_CAPTURED                        = 0x002E
#// Требуется блокировка карты
E_CARD_LOCK_REQUESTED                  = 0x002F
#// Запрос на получение внешнего описателя добавляемого сектора
E_SECTOR_EX_DESCR_REQUESTED            = 0x0030
#// Параметры внешнего описателя добавляемого сектора введены
E_SECTOR_EX_DESCR_ENTERED              = 0x0031
#// Требуется установка буфера для описателя секторов
E_SECTORS_DESCR_BUF_REQUESTED          = 0x0032
#// Буфера для описателя секторов установлен
E_SECTORS_DESCR_BUF_SET                = 0x0033
#// Буфера для описателя секторов не используется
E_SECTORS_DESCR_BUF_NOT_USED           = 0x0034
#// Верификация гражданина прошла успешно
E_CITIZEN_VERIFIED                     = 0x0035
#// Подтверждение формирования электронной подписи держателя карты
E_DIGITAL_SIGN_CONFIRMATION            = 0x0036
#// Формирование электронной подписи держателя карты подтверждено
E_DIGITAL_SIGN_CONFIRMED               = 0x0037
#// Формирование электронной подписи держателя карты не требуется
E_DIGITAL_SIGN_NOT_CONFIRMED           = 0x0038
#// Запрос на ввод пароля держателя электронной подписи
E_DIGITAL_SIGN_PIN_REQUESTED           = 0x0039
#// Пароль держателя электронной подписи введён
E_DIGITAL_SIGN_PIN_ENTERED             = 0x003A
#// Повторный ввод пароля держателя электронной подписи
E_DIGITAL_SIGN_PIN_RETRY_REQUESTED     = 0x003B
#// Электронная подпись держателя карты сформирована
E_DIGITAL_SIGN_PREPARED                = 0x003C
#// Подтверждение установления защищённой сессии с Поставщиком Услуги 
E_PROVIDER_SESSION_CONFIRMATION        = 0x003D
#// Установка защищённой сессии с Поставщиком Услуги подтверждена 
E_PROVIDER_SESSION_CONFIRMED           = 0x003E
#// Установка защищённой сессии с Поставщиком Услуги не требуется 
E_PROVIDER_SESSION_NOT_CONFIRMED       = 0x003F
#// Защищённая сессии с Поставщиком Услуги установлена
E_PROVIDER_SESSION_ESTABLISHED         = 0x0040
#// Защищённая сессии с Поставщиком Услуги установлена на стороне хоста
E_PROVIDER_SESSION_HOST_ESTABLISHED    = 0x0041
#// Требуется передать блок данных для шифрования в рамках сессии с Поставщиком Услуги
E_PROVIDER_DATA_ENCRYPT_REQUESTED      = 0x0042
#// Блок данных для шифрования передан
E_PROVIDER_DATA_ENCRYPT_ENTERED        = 0x0043
#// Блок данных для шифрования/расшифрования отсутствует
E_PROVIDER_DATA_EMPTY                  = 0x0044
#// Блок данных зашифрован
E_PROVIDER_DATA_ENCRYPTED              = 0x0045
#// Зашифрованный/Расшифрованный блок данных использован
E_PROVIDER_DATA_PROCESSED              = 0x0046
#// Требуется передать блок данных для расшифрования в рамках сессии с Поставщиком Услуги
E_PROVIDER_DATA_DECRYPT_REQUESTED      = 0x0047
#// Блок данных для расшифрования передан
E_PROVIDER_DATA_DECRYPT_ENTERED        = 0x0048
#// Блок переданных данных расшифрован
E_PROVIDER_DATA_DECRYPTED              = 0x0049
#// Подтверждение необходимости аутентификации Поставщика Услуги
E_PROVIDER_AUTH_CONFIRMATION           = 0x004A
#// Аутентификация Поставщика Услуги подтверждена 
E_PROVIDER_AUTH_CONFIRMED              = 0x004B
#// Аутентификация Поставщика Услуги не требуется 
E_PROVIDER_AUTH_NOT_CONFIRMED          = 0x004C
#// Получен ответ на аутентификацию ИД-приложения 
E_APP_AUTH_RESPONSE_RECEIVED           = 0x004D
#// Необходимы данные ответа на аутентификацию ИД-приложения 
E_APP_AUTH_RESPONSE_DATA_REQUESTED     = 0x004E
#// Введён пакет APDU-команд, зашифрованный на ключе Провайдера Услуги
E_APDU_ENCRYPTED_PACKET_ENTERED        = 0x004F
#// Запрос на ввод пароля активации модуля безопасности 
E_SE_ACTIVATION_PIN_REQUESTED          = 0x0050
#// Пароль активации модуля безопасности введён
E_SE_ACTIVATION_PIN_ENTERED            = 0x0051
#// Повторный ввод пароля активации модуля безопасности
E_SE_ACTIVATION_PIN_RETRY_REQUESTED    = 0x0052
#// Требуется предать имя владельца МБ 
E_SE_OWNER_NAME_REQUESTED              = 0x0053
#// Имя владельца МБ введён
E_SE_OWNER_NAME_ENTERED                = 0x0054
#// Ввод фразы контрольного приветствия
E_PASS_PHRASE_REQUESTED                = 0x0055
#// Фраза контрольного приветствия введена
E_PASS_PHRASE_ENTERED                  = 0x0056
#// Требуется посылка зароса на аутентификацию ИД-приложения
E_SEND_APP_AUTH_REQUESTED              = 0x0057
#// Продолжение выполнения 
E_CONTINUE                             = 0x0058

#/*  Исключения
# * Диапазон исключений резервируется от 0x1000 до 0x1200.
# * Актуально до 0x1100, оставльное пространство для перехвата исключений.
# */

#// Базовый идентификатор исключений 
E_EXCEPTION_EVENTS                  = 0x1000 
#//  Недопустимая глубина вложенного автомата 
E_EXCEPTION_DEPTH                   = E_EXCEPTION_EVENTS + 0x01
#//  Недопустимое использование подсистемы 
E_EXCEPTION_USE                     = E_EXCEPTION_EVENTS + 0x02
#//  Ошибка выполнения 
E_EXCEPTION_RUNTIME_ERROR           = E_EXCEPTION_EVENTS + 0x03
#//  Отказ пользователя 
E_EXCEPTION_USER_BREAK              = E_EXCEPTION_EVENTS + 0x04
#// Экстренное прерывание 
E_EXCEPTION_INTERRUPT               = E_EXCEPTION_EVENTS + 0x05
#//  Зацикливание автомата
E_EXCEPTION_CYCLING_DETECTED        = E_EXCEPTION_EVENTS + 0xFF
#// Смещение к базе Исключительного события при его обработке 
E_CATCHING_OFFSET_EVENTS            = 0x100                   


eUECRetCode_NoErrors                = 0#,    // Ошибок нет
eUECRetCode_InitReader_Failed        = 1#,    // Ошибка при инициализации ридера
eUECRetCode_DeinitReader_Failed        = 2#,    // Ошибка при закрытии ридера
eUECRetCode_OpenCard_Failed            = 3#,    // Ошибка открытия карты (возможна при отутствии карты в ридере)
eUECRetCode_CardClose_Failed        = 4#,    // Ошибка при закрытии карты
eUECRetCode_Authorise_Failed        = 5#,    // Ошибка при авторизации
eUECRetCode_PIN_Incorrect            = 6#,    // Неверный ПИН
eUECRetCode_PIN_Blocked                = 7#,    // ПИН заблокирован    (необходима разблокировка с помощью КРП)    
eUECRetCode_ReadCardInfo_Failed        = 8#,    // Ошибка при чтении информации по карте
eUECRetCode_ReadOMSData_Failed        = 9#,    // Ошибка чтения данных ОМС
eUECRetCode_WriteOMSData_Failed        = 10#,    // Ошибка записи данных ОМС
eUECRetCode_WrongDataToWrite        = 11#,    // Неверный формат данных для записи на карту
eUECRetCode_WriteOMSHistory_Failed    = 12#,    // Ошибка при записи данных в историю изменения ОМС
eUECRetCode_ReadOMSHistory_Failed    = 13#    // Ошибка чтения данных истории изменения ОМС


UECMessageEncoding = 'cp1251'

class CUekPin(QDialog, Ui_Dialog):
    
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

class CUekRead:
    
    def __init__(self):
        self.isInited = False
        
        self.lastName = u''
        self.firstName = u''
        self.patrName = u''
        self.bDate = QDate()
        self.sex = u''
        self.oms = u''
        self.snils = u''
        self.bLoc = u''
        self.omsBegDate = QDate()
        self.omsEndDate = QDate()
        self.omsOkato = u''
        self.omsOgrn = u''
        
        self.rawCardInfo = u''
        self.lastErrorCode = eUECRetCode_NoErrors
        
    
    def open(self):
        if (self.isInited):
            self.close()
        self.lastErrorCode = eUECRetCode_NoErrors 
        #welcomeMsg = create_string_buffer(UECMaxStringLength)
        #errorStr   = create_string_buffer(UECMaxStringLength)
        #self.lastErrorCode    = OMSLib.UEC_OpenCard(welcomeMsg, errorStr) if OMSLib else None
        #self.welcomeMessage   = welcomeMsg.value.decode(UECMessageEncoding)
        #self.lastErrorMessage = errorStr.value.decode(UECMessageEncoding)
        #print self.lastErrorMessage
        self.isInited = True
        
    def read(self, pin):
        if (self.isInited):
            pinStr = create_string_buffer(UECMaxStringLength)
            pinStr.value = pin
            
            # __declspec(dllexport) WORD CardStateMashine(
            #          DWORD &dwDataPtr, 
            #          void* pBuffer, 
            #          const DWORD wInBufSize, 
            #          DWORD &wOutBufSize, 
            #          const DWORD wMaxBufSize, 
            #          const BOOL bEnd);
            
            Event = c_int()
            Buffer = create_string_buffer(UECMaxStringLength)
            BufferInSize = c_int()
            BufferInSize = UECMaxStringLength

            Event = OMSLib.ReadAll(ctypes.cast(pinStr, c_void_p), BufferInSize, ctypes.cast(Buffer, c_void_p))
            
            if (Event):
                self.rawCardInfo = Buffer.value.decode(UECMessageEncoding)
                # QtGui.qApp.log(u'UEK debug log', self.rawCardInfo, None) #TODO: atronah: debug: for Suprun
                self.rawCardInfoArray = self.rawCardInfo.split("\n")
                for cardInfoLine in self.rawCardInfoArray:
                    ci = cardInfoLine.split('=')

                    if (ci[0] == '1-2-DF2D'):
                        self.lastName = ci[1]
                    elif (ci[0] == '1-2-DF2E'):
                        self.firstName = ci[1]
                    elif (ci[0] == '1-2-DF2F'):
                        self.patrName = ci[1]
                    elif (ci[0] == '1-2-5F2B'):
                        self.bDate = QDate(int(ci[1][0:4]),  int(ci[1][4:6]),  int(ci[1][6:8]))
                    elif (ci[0] == '1-2-5F35'):
                        if (ci[1] == u'М'):
                            self.sex = 1
                        else:
                            self.sex = 2
                    elif (ci[0] == '1-2-DF2B'):
                        self.oms = ci[1]
                    elif (ci[0] == '1-2-DF27'):
                        self.snils = ci[1]
                    elif (ci[0] == '1-2-DF24'):
                        self.bLoc = ci[1]
                    elif (ci[0] == '3-1-10'):
                        self.omsBegDate = QDate(int(ci[1][0:4]),  int(ci[1][4:6]),  int(ci[1][6:8]))
                    elif (ci[0] == '3-1-14'):
                        self.omsEndDate = QDate(int(ci[1][0:4]),  int(ci[1][4:6]),  int(ci[1][6:8]))
                    elif (ci[0] == '3-1-7'):
                        self.omsOkato = ci[1]
                    elif (ci[0] == '3-1-0'):
                        self.omsOgrn = ci[1]

            else:
                self.lastErrorCode = eUECRetCode_OpenCard_Failed
            
            #self.lastErrorCode    = OMSLib.UEC_Authorize(pinStr, byref(pinCnt), errorStr) if OMSLib else None
            #self.lastErrorMessage = errorStr.value.decode(UECMessageEncoding)
            #self.restPinChanges   = pinCnt.value
            #if (self.lastErrorCode == eUECRetCode_NoErrors):
            #    cardInfo = create_string_buffer(UECMaxStringLength)
            #    self.lastErrorCode    = OMSLib.UEC_GetCardInfo(cardInfo, errorStr) if OMSLib else None
            #    self.lastErrorMessage = errorStr.value.decode(UECMessageEncoding)
            #    if (self.lastErrorCode == eUECRetCode_NoErrors):
            #        self.rawCardInfo = cardInfo.value.decode(UECMessageEncoding)
            #        self.rawCardInfoArray = self.rawCardInfo.split("\n")
            #        for cardInfoLine in self.rawCardInfoArray:
            #            ci = cardInfoLine.split('|')
            #            if (ci[0] == '1-2-DF2D'):
            #                self.lastName = ci[4]
            #            elif (ci[0] == '1-2-DF2E'):
            #                self.firstName = ci[4]
            #            elif (ci[0] == '1-2-DF2F'):
            #                self.patrName = ci[4]
            #            elif (ci[0] == '1-2-5F2B'):
            #                self.bDate = QDate(int(ci[4][0:4]),  int(ci[4][4:6]),  int(ci[4][6:8]))
            #            elif (ci[0] == '1-2-5F35'):
            #                if (ci[4] == u'М'):
            #                    self.sex = 1
            #                else:
            #                    self.sex = 2
            #            elif (ci[0] == '1-2-DF2B'):
            #                self.oms = ci[4]
            #            elif (ci[0] == '1-2-DF27'):
            #                self.snils = ci[4]
            #            elif (ci[0] == '1-2-DF24'):
            #                self.bLoc = ci[4]
            #        omsRawInfo = create_string_buffer(UECMaxStringLength)
            #        self.lastErrorCode    = OMSLib.UEC_ReadOMSData(omsRawInfo, errorStr) if OMSLib else None
            #        self.lastErrorMessage = errorStr.value.decode(UECMessageEncoding)
            #        if (self.lastErrorCode == eUECRetCode_NoErrors):
            #            self.rawOmsInfo = omsRawInfo.value.decode(UECMessageEncoding)
            #            self.rawOmsInfoArray = self.rawOmsInfo.split("\n")
            #            for omsLine in self.rawOmsInfoArray:
            #                oi = omsLine.split('|')
            #                if (oi[0] == '3-1-10'):
            #                    self.omsBegDate = QDate(int(oi[4][0:4]),  int(oi[4][4:6]),  int(oi[4][6:8]))
            #                elif (oi[0] == '3-1-14'):
            #                    self.omsEndDate = QDate(int(oi[4][0:4]),  int(oi[4][4:6]),  int(oi[4][6:8]))
            #                elif (oi[0] == '3-1-7'):
            #                    self.omsOkato = oi[4]
            #                elif (oi[0] == '3-1-0'):
            #                    self.omsOgrn = oi[4]
        
    def close(self):
        if (self.isInited):
            #errorStr   = create_string_buffer(UECMaxStringLength)
            #self.lastErrorCode    = OMSLib.UEC_CloseCard(errorStr) if OMSLib else None
            #self.lastErrorMessage = errorStr.value.decode(UECMessageEncoding)
            self.isInited = False
        
        
