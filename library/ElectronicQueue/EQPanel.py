#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore
import socket
import serial
import struct
import time
import sys, os
import select
from collections import deque
from library.Utils import forceString, forceStringEx, forceInt

'''
Created on 09.10.2012

@author: atronah
'''

def SerialScan():
    """
    Gets a list of available ports
    """
    available = []
    if sys.platform == 'win32':
        try:
            from serial.tools.list_ports import comports

            comPortsList = comports()
            for comPort in comPortsList:
                available.append(comPort[0])
        except:
            available = []
    return available


class CDataExchangeInterface(object):
    def __init__(self):
        self._lastError = None
        self._isConnect = False
    
    # Отправить данные по интерфейсу
    def sendData(self, data):
        return True
    
    
    # Принять данные по интерфейсу
    def receiveData(self, size = 1, timeout = 0.5):
        return bytes()
    
    
    # Состояние соединения
    def isConnect(self):
        return self._isConnect
    
    # Установить соединение
    def connect(self):
        if self.isConnect():
            self.disconnect()
        self._isConnect = True
        return self.isConnect()
    
    
    # Закрыть соединение
    def disconnect(self):
        self._isConnect = False
        return not self.isConnect()
    
    
    def reconnect(self):
        self.disconnect()
        self.connect()
 
 
class CSocketDEInterface(CDataExchangeInterface):
    timeout = 0.05
    def __init__(self, address, protocol = 'tcp'):
        CDataExchangeInterface.__init__(self)
        self.proto = socket.SOCK_DGRAM if protocol == 'udp' else socket.SOCK_STREAM
#        self.socket.setblocking(0)
        self._connectionAddress = address
        self.readedQueue = deque()
    
    
    def connectionAddress(self):
        return self._connectionAddress
    
    
#    def setConnectionAddress(self, address):
#        self._connectionAddress = address
#        if self.isConnect():
#            self.reconnect()


    def connect(self):
        if self.isConnect():
            return True
        self.socket = socket.socket(socket.AF_INET, self.proto)
        self.socket.settimeout(self.timeout)
        if self.proto == socket.SOCK_STREAM:
            try:
                self.socket.connect(self.connectionAddress())
            except socket.error, e:
                # errno = 10056 - Socket is already connected.
                if e.errno != 10056:
                    raise
        return CDataExchangeInterface.connect(self)
        
    
    def disconnect(self):
        if self.proto == socket.SOCK_STREAM:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        return CDataExchangeInterface.disconnect(self)
    
    
    def isConnect(self):
        if self._isConnect:
            self.readedQueue.append(self._receiveDataFromSocket(1, self.timeout))
            return True
        return False
        
    
    def sendData(self, data):
        if not data:
            return 0
        sentBytes = -1
        if self.isConnect():
            sentBytes = self.socket.send(data) if self.proto == socket.SOCK_STREAM else self.socket.sendto(data, self.connectionAddress())
        return sentBytes
            
    
    def _receiveDataFromSocket(self, size, timeout):
        if timeout is None:
            timeout = self.timeout
        data = bytes()        
        while True:
            readable = select.select([self.socket], [], [], timeout)[0]
            if readable:
                data, address = readable[0].recvfrom(size)
                if not data:
                    raise IOError(u'Break socket connection on other end for', self.connectionAddress())
                else:
                    if self.proto == socket.SOCK_STREAM or address == self.connectionAddress():
                        break                      
                    else:
                        data = bytes()
            else:
                break
        
        return data
    
    
    def receiveData(self, size = 1, timeout = None):
        data = bytes()
        if size > 0 and self.isConnect():
            while len(self.readedQueue) and len(data) < size:
                data += self.readedQueue.popleft()
            if len(data) < size:
                data += self._receiveDataFromSocket(size - len(data), timeout)
        return data
    
    
    
class CSerialDEInterface(CDataExchangeInterface):
    timeout = 0.05
    def __init__(self, comPort):
        CDataExchangeInterface.__init__(self)
        self.serial = serial.Serial()
        self.serial.port = comPort
        self.serial.baudrate = CEQPanel.panelBaudrate
        self.serial.bytesize = CEQPanel.panelBytesize
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = CEQPanel.panelStopbits
        self.serial.timeout = CEQPanel.timeout
        self.readedQueue = deque()
    
    
#    def connectionAddress(self):
#        return self._connectionAddress
    
    
#    def setConnectionAddress(self, address):
#        self._connectionAddress = address
#        if self.isConnect():
#            self.reconnect()
    
    def isConnect(self):
        return self.serial.isOpen()


    def connect(self):
        if self.isConnect():
            return True
        self.serial.open()
        return self.isConnect()
        
    
    def disconnect(self):
        self.serial.close()
        return CDataExchangeInterface.disconnect(self)
    
    
    
        
    
    def sendData(self, data):
        if not data:
            return 0
        sentBytes = -1
        if self.isConnect():
            sentBytes = self.serial.write(data)
        return sentBytes
            
    
    def _receiveDataFromSerial(self, size, timeout):
        if timeout is None:
            timeout = self.timeout
        data = self.serial.read(size)
        return data
    
    
    def receiveData(self, size = 1, timeout = None):
        data = bytes()
        if size > 0 and self.isConnect():
            data += self._receiveDataFromSerial(size, timeout)
        return data
    


class CAbstractEQPanel(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.timerFunction = None
        self.timerId = None
        self.timerFunctionArgs = ()
        QtGui.qApp.aboutToQuit.connect(self.stopTimer)
        self.dataInterface = None
    
    
    def timerEvent(self, event):
        if callable(self.timerFunction):
            self.timerFunction(*self.timerFunctionArgs)
        if event.timerId() != self.timerId:
            self.killTimer(event.timerId())
        else:
            self.stopTimer()
        
    
    
    def restartTimer(self, interval, func, args = ()):
        self.stopTimer()
        self.timerFunction = func
        self.timerFunctionArgs = args if isinstance(args, tuple) else ()
        self.timerId = self.startTimer(interval)
        
    
    @QtCore.pyqtSlot()
    def stopTimer(self):
        if self.timerId:
            self.killTimer(self.timerId)
            self.timerId = None
            
    
    def setDataExchangeInterface(self, interface):
        if self.dataInterface:
            del self.dataInterface
            self.dataInterface = None
        
        if isinstance(interface, CDataExchangeInterface):
            self.dataInterface = interface
    
    
    def dataExchangeInterface(self):
        return self.dataInterface
    
    
class CEQGuiPanel(QtGui.QLabel):
    clearTimeout = 80
    
    def __init__(self, parent = None):
        QtGui.QLabel.__init__(self, parent)
        self.timerFunction = None
        self.timerId = None
        self.timerFunctionArgs = ()
        self.connect(QtGui.qApp, QtCore.SIGNAL('aboutToQuit()'), self.stopTimer)
    
    
    def timerEvent(self, event):
        if callable(self.timerFunction):
            self.timerFunction(* self.timerFunctionArgs)
        if event.timerId() != self.timerId:
            self.killTimer(event.timerId())
        else:
            self.stopTimer()
        
    
    
    def restartTimer(self, interval, func, args = ()):
        self.stopTimer()
        self.timerFunction = func
        self.timerFunctionArgs = args if isinstance(args, tuple) else ()
        self.timerId = self.startTimer(interval)
        
    
    @QtCore.pyqtSlot()
    def stopTimer(self):
        if self.timerId:
            self.killTimer(self.timerId)
            self.timerId = None
    
    
    def showOnPanel(self, data, alwaysOn = True):
        result = False
        
        if not data:
            self.clear()
            result = True
        else:
            self.setText(u'%s' % data)
            result = True
            if not alwaysOn:
                self.restartTimer(self.clearTimeout, self.clear, ())
            
        return result
        

##Обеспечивает работу с эл.табло
class CEQPanel(CAbstractEQPanel):
    """
    atronah:
    Implementation EQ Panel work.
    """
    
    preamble = 0xFF
    startByte = 0x02
    endByte = 0x0D
    
    
    #Параметры  по умолчанию
    panelBaudrate = 9600              # скорость передачи последовательного порта (в бодах, 9600 или 115200 например).
    panelBytesize = 8                 # размер байта (в битах)
    panelStopbits = 1                 # стандартное число стоповых битов в байте
    
    timeout = 0.05                    # задержка перед чтением ответа
    
    availableCommandList = ['a', 'j', 'h', 'd', 'b', 'g', 'f', 'e']
    infoCommand = 'a'
    echoCommand = 'g'
    execWithAnswerMode = '!'
    askWithAnswerMode = '?'
    execWithoutAnswer = '#'
    
    leftAlignmentCode = '\x18'
    rightAlignmentCode = '\x17'
    
    
    answerCodes = {'successfull' : '0',
                   'notExec' : '1',
                   'notSupport' : '2',
                   'invalidPacketFormat' : '3',
                   'invalidChecksum' : '4',
                   'invalidPacketData' : '5'}
    
    #Параметры вывода табло по умолчанию
    defaultSegmentCount = 4             # количество символов для вывода
#    defaultBlinkNumber = 0              # число миганий при выводе
#    defaultBlinkTime = 0.05             # перерыв между миганиями
    defaultIsLeftAlignment = False        # выравнивание: True - налево (вывод первых n символов), False - направо (вывод последних n символов)
    
    resentTimeoutForAlwaysOn = 50   # Задержка перед отправлением сообщения для обеспечения его постоянного отображения на табло.

    ## Создание экземпляра класса для работы с конкретным эл.табло
    # @param panelAddr: адрес получателя/табло (1-244, 0 и 255 - широковещательные адреса без ответа и с ответом соответственно)
    # @param selfAddr: адрес отправителя (1-244)
    # @param expectAnswerMode: режим обработки ответов (0 - не ждать ответ, 1 - ждать первый ответ от выбранного табло, 2 - обрабатывать все ответы от выбранного табло)
    def __init__(self,
                 panelAddr = 255,
                 selfAddr = 0xFE, 
                 expectAnswerMode = 0):
        CAbstractEQPanel.__init__(self)
        self.addr = selfAddr
        self.panelAddr = panelAddr
#        self.blinkNumber = self.defaultBlinkNumber
#        self.blinkTime = self.defaultBlinkTime
        self.segmentCount = self.defaultSegmentCount
        self.isLeftAlignment = self.defaultIsLeftAlignment
        
        self._breakDisplayThread = False
        self._displayThread = None
        self._expectAnswerMode = expectAnswerMode
        self._lastAnswer = (None, None, '')
        self._successAnswerCount = 0
        self._lastError = ''
        self.errorLoger = None
        self.dataInterface = CSocketDEInterface(('127.0.0.1', 5000))
             
    
#    def setBlinkParams(self, blinkNumber, blinkTime):
#        self.blinkNumber = blinkNumber
#        self.blinkTime = blinkTime
    
    
    @staticmethod
    def packCommand(data, panelAddr = 255, selfAddr = 0x64):    
        dst= "%02X%02X%s" % (panelAddr, selfAddr,  '%s' % data)
        cnt= len(dst)
        crc= 0
        # Count checksum
        for i in xrange(cnt):
            crc += ord(dst[i])
    
        crc &= 0xFF
        cmd = struct.pack("BB" + ("%ds" % cnt) + "B2sB",
                         CEQPanel.preamble, CEQPanel.startByte, dst, 0x03, "%02X" % crc, CEQPanel.endByte)
        return cmd
    
    
    @staticmethod
    def extractAnswerFromData(data):
        beginIndex = data.find('%c%c' % (CEQPanel.preamble, CEQPanel.startByte))
        endIndex = data.find('%c' % CEQPanel.endByte, beginIndex)
        sender = None
        receiver = None
        text = u''
        otherData = data
        if beginIndex >= 0 and endIndex >= 0:
            try:
                answer = data[beginIndex:endIndex]
                otherData = data[:beginIndex] + data[endIndex:]
                
                if answer and len(answer) >= 8:
                    sender = int(answer[4:6], 16)   # адрес отправителя
                    receiver = int(answer[2:4], 16) # адрес получателя    
                    eod= answer.find(chr(0x03))
                    if eod > 5:                 # дополнительная информация из ответа (если имеется)
                        text = answer[6:eod]
            except:
                text = answer
        else:
            otherData = bytes()
        return (sender, receiver, text, otherData)
    
    
    @staticmethod
    def decriptAnswer(answer):
        answerString = u''
        if isinstance(answer, basestring):
            answer = CEQPanel.extractAnswerFromData(answer)
        elif isinstance(answer, tuple) and len(answer) >= 3:
            senderPart = u'Отправитель: %s' % answer[0]
            receiverPart = u'Получатель: %s' % answer[1]
            generalPart = u'Ответ: %s'
            if len (answer[2]) < 2:
                generalPart = generalPart % answer[2]
            else:
                commandSymbol = answer[2][0]
                commandResultCode = answer[2][1]
                commandAdditional = answer[2:]
                if commandSymbol.lower() == CEQPanel.echoCommand:
                    commandDescription = u'Команда вывада на табло (%s)' % CEQPanel.echoCommand
                elif commandSymbol.lower() == CEQPanel.infoCommand and commandResultCode == commandSymbol:
                    commandDescription = u'Команда запроса типа устройства и адресов (%s)' % commandSymbol
                elif commandSymbol.lower() == CEQPanel.infoCommand:
                    commandDescription = u'Команда настройки адресов (%s)' % commandSymbol
                else:
                    commandDescription = u'Неизвестная команда "%s"'
                
                if commandResultCode == CEQPanel.answerCodes['successfull']:
                    commandDescription += u' выполнена успешно (%s)' % commandResultCode
                elif commandResultCode == CEQPanel.answerCodes['notExec']:
                    commandDescription += u' не выполнена (%s)' % commandResultCode
                elif commandResultCode == CEQPanel.answerCodes['notSupport']:
                    commandDescription += u' не поддерживается получателем (%s)' % commandResultCode
                elif commandResultCode == CEQPanel.answerCodes['invalidPacketFormat']:
                    commandDescription += u' не выполнена (неверный формат пакета команды) (%s)' % commandResultCode
                elif commandResultCode == CEQPanel.answerCodes['invalidChecksum']:
                    commandDescription += u' не выполнена (несовпадение контрольной суммы) (%s)' % commandResultCode
                elif commandResultCode == CEQPanel.answerCodes['invalidPacketData']:
                    commandDescription += u' не выполнена (неверное поле данных в пакете) (%s)' % commandResultCode
                else:
                    commandDescription += u' выполнена с неизвестным кодом "%s"' % commandResultCode
                
                
                if commandAdditional and commandSymbol.lower() == CEQPanel.infoCommand and commandResultCode == commandSymbol:
                    preamble, sep, commandAdditional = commandAdditional.partition(u'2A')
                    serial, sep, commandAdditional = commandAdditional.partition(u'2A')
                    sensor, sep, commandAdditional = commandAdditional.partition(u'2A')
                    if sensor == '00':
                        sensorDescr = u'нет датчиков'
                    elif sensor == '01':
                        sensorDescr = u'датчик на контроллере'
                    elif sensor == '02':
                        sensorDescr = u'датчик внешний'
                    elif sensor == '03':
                        sensorDescr = u'оба датчика'
                    else:
                        sensorDescr = u'неизвестно "%s"' % sensor
                    defaultAddress = commandAdditional[0:4]
                    currentAddress = commandAdditional[4:8]
                    panelType = commandAdditional[8:]
                    
                    commandDescription += u'\n\tПреамбула: %s' % preamble
                    commandDescription += u'\n\tСерийный номер: %s' % serial
                    commandDescription += u'\n\tДатчики температуры: %s' % sensorDescr
                    commandDescription += u'\n\tАдрес по умолчанию: %s - %s' % (defaultAddress[:2], defaultAddress[2:])
                    commandDescription += u'\n\tАдрес текущий: %s - %s' % (currentAddress[:2], currentAddress[2:])
                    commandDescription += u'\n\tТип: %s' % panelType
                generalPart = commandDescription
            answerString = senderPart + ' ' + receiverPart + '\n' + generalPart
                    
        return answerString
    

    def lastError(self):
        return self._lastError
    
    
    def lastAnswer(self):
        return self._lastAnswer
    
    
    def successAnswerCount(self):
        return self._successAnswerCount
    
    
    def setPanelAddres(self, addr):
        if (0 <= addr <= 255):
            self.panelAddr = addr
            return True
        return False

    
    

    ## Возвращает true, если табло находится в рабочем состоянии
    def isWork(self):
        if not self.panelAddr:
            self._lastError = u'Не указан адрес табло'
            return False
        return self.sendCommand(self.getCommand('', self.infoCommand + self.askWithAnswerMode))
        
    
    ## Формирует управляющую команду для отправки на табло на основании переданного текста/числа.
    # @param value: сообщение для вывода на табло (не проверяется на поддерживаемость устройством) 
    def getCommand(self, value = None, controlPrefix = None):
        displayData = ''
        dataPrefix = ''
        
        if controlPrefix is None \
                or len(controlPrefix) != 2 \
                or controlPrefix[0].lower() not in self.availableCommandList \
                or controlPrefix[1] not in [self.execWithAnswerMode, self.execWithoutAnswer, self.askWithAnswerMode]:
            controlPrefix = self.echoCommand + (self.execWithAnswerMode if self._expectAnswerMode else self.execWithoutAnswer)
        
        if controlPrefix[0].lower() == self.echoCommand:
            if isinstance(value, (int, float)):
                mask = '%%0%dd' % self.defaultSegmentCount
                displayData += mask % value          #преобразует число в строку
            elif isinstance(value, basestring):
                displayData += value
            else:
                displayData = forceString(value)
            if not displayData:
                displayData = ' ' * self.segmentCount
            dataPrefix = self.leftAlignmentCode if self.isLeftAlignment else self.rightAlignmentCode

        data = '%s%s%s' % (controlPrefix, dataPrefix, displayData)
        return CEQPanel.packCommand(data, self.panelAddr, self.addr)
    
    
            
    ## Отображает value на эл.табло, используя для этого отдельный поток
    # @param data: посылаемое на табло значение
    # @param alwaysOn: включает постоянное обновление информации на табло, не давая ему погаснуть по вшитому в устройство таймауту (60сек), если равно True
    def display(self, data, alwaysOn = True):
        self.showOnPanel(data, alwaysOn)
    
    
    ## Отображает последовательность тире на табло
    def displayDash(self):
        self.display('-' * self.defaultSegmentCount, False)
    
    
    def setErrorLoger(self, logerFunc):
        if callable(logerFunc):
            self.errorLoger = logerFunc
    
    
    def logCurrentException(self):
        if callable(self.errorLoger):
            self.errorLoger()
    
    
    def sendCommand(self, command):
        if not self.dataExchangeInterface():
            self._lastError = u'Не сконфигурирован интерфейс обмена данными с табло'
            return False
        
        result = True
        tryNumber = 3
        while tryNumber > 0:
            tryNumber -= 1
            try:
                if self.dataInterface.connect():
                    break
            except IOError, e:
                message = e.strerror if hasattr(e, 'strerror') else e.message if hasattr(e, 'message') else 'unknown'
                self._lastError = u'Не удалось подключиться к табло электронной очереди (%s)' % (message.decode('cp1251') if message else '---')
                self.logCurrentException()
            
        
        if tryNumber <= 0:
            return False
        try:
            self.dataInterface.sendData(command)
            if self._expectAnswerMode:
                self._successAnswerCount = 0
                self._lastAnswer = (None, None, None)
                time.sleep(self.timeout)
                startReadingTime = time.time()
                answerData = self.dataInterface.receiveData(4096)
                while answerData:
                    answerTuple = CEQPanel.extractAnswerFromData(answerData)
                    self._lastAnswer = answerTuple[:3]
                    if answerTuple[1] == self.addr and answerTuple[2][1] == '0':
                        result = True
                        self._successAnswerCount += 1
                        if self._expectAnswerMode == 1:
                            break
                    elif self._expectAnswerMode == 1 and (time.time() - startReadingTime) > 1.0:
                        self._lastError = u'Не был получен ожидаемый ответ от табло на команду %s' % command[6:]
                        result = False
                        break
                    answerData = answerTuple[3] or self.dataInterface.receiveData(4096)      
                
        except IOError, e:
            self._lastError = u'Ошибка отправления команды на табло электронной очереди (%s)' % e
            self.logCurrentException()
            result = False
        finally:
            self.dataInterface.disconnect()
        
        if result: 
            self._lastError = u''
        return result

    
    def showOnPanel(self, data, alwaysOn):
        command = self.getCommand(data)
        result = self.sendCommand(command)
        self.stopTimer()
        if result and alwaysOn:
            self.restartTimer(self.resentTimeoutForAlwaysOn, self.showOnPanel, (data, alwaysOn))
        return result
    
    
    def getEQPanelCountList(self, isShowNumber = False, errorList = None, stepFunction = None, interval = (1, 254)):
        savedExpectAnswerMode = self._expectAnswerMode
        self._expectAnswerMode = 2
        result = [0] * (interval[1] - interval[0] + 1)
        try:
            for addr in xrange(interval[0], interval[1] + 1):
                if addr != self.addr:
                    mask = '%%0%dd' % self.defaultSegmentCount
                    displayData = mask % addr
                    command = self.packCommand('%s%s%s' % (self.echoCommand if isShowNumber else self.infoCommand,
                                                           self.execWithAnswerMode if isShowNumber else self.askWithAnswerMode,
                                                           displayData if isShowNumber else ''), 
                                               addr,
                                               self.addr)
                    if addr == self.addr:
                        continue
                    if self.sendCommand(command):
                        result[addr] = self.successAnswerCount()
                    else:
                        if errorList is not None and isinstance(errorList, list):
                            errorList.append('%d: %s (%s)' % (addr, self.lastError(), str(self.lastAnswer())))
                if callable(stepFunction):
                    stepFunction(addr, interval[1])
        finally:
            self._expectAnswerMode = savedExpectAnswerMode
        return result
        
        

#class CComEQPanel(CEQPanel):
#    
#    defaultParity = serial.PARITY_NONE       # включение контроля честности
#    
#    
#    def __init__(self, panelAddr = 255, selfAddr = 0x64, comPort = 0):
#        CEQPanel.__init__(self, panelAddr, selfAddr)
#        self.serial = serial.Serial()
#        self.serial.port = comPort
#        self.serial.baudrate = self.panelBaudrate
#        self.serial.bytesize = self.panelBytesize
#        self.serial.parity = self.defaultParity
#        self.serial.stopbits = self.panelStopbits
#        self.serial.timeout = self.timeout
#    
#    
#    
#    def getDataFromPanel(self, size = 1):
#        try:
#            data = self.serial.read(size)
#        except:
#            data = ''
#        return data
#    
#    
#    def __del__(self):
#        if self.serial: 
#            self.serial.close()
#        
#    
#    def initConnect(self):
#        if self.serial:
#            self.serial.close()
#        try:
#            self.serial.open()
#            return self.serial.isOpen()
#        except Exception as msg:
#            self._lastError = getErrorString(msg)
#            return False
#        return True
#
#    
#    def getSerialInfo(self):
#        result = """panel address = %d, sender address = %d,
#port = %s, baudrate = %d, 
#bytesize = %s, stopbits = %s, timeout = %s
#"""     % (self.panelAddr, self.addr, 
#           unicode(self.serial.port), self.serial.baudrate,
#           self.serial.bytesize, self.serial.stopbits, self.serial.timeout)        
#        return result
#    
#    
#    ## Возвращает true, если табло находится в рабочем состоянии
#    def isWork(self):
#        result = CEQPanel.isWork(self)
#        if not result:
#            serialInfo = self.getSerialInfo()
#            result = result
#            self._lastError = self.lastError() + '\n%s' % serialInfo
#        return result
#    
#    
#    ## Посылает команду на табло
#    # @param command: содержимое пакета, посылаемого на табло, предварительно сформированная последовательность байт
#    def sendCommand(self, command):
#        try:
#            if self.serial.isOpen():
#                self.serial.flushInput()
#                self.serial.flush()
#                self.serial.write(command)
#            else:
#                if self.initConnect():
#                    return self.sendCommand(command)
#        except:
#            if self.initConnect():
#                return self.sendCommand(command)
#            else:
#                return False
#        self.wait(len(command))
#        return True
#
#

#class CConfigEQPanel(QtCore.QObject):

class CEQConfig(QtCore.QObject):
    ext = '.eqcfg'
    
    def __init__(self, parent = None):
        QtCore.QObject.__init__(self, parent)
        self._placesInfo = {}
        self._loaded = False
    
    
    def isLoaded(self):
        return self._loaded
    
    
    @staticmethod
    def availableLoad(cfgDir = '.'):
        for fileName in os.listdir(cfgDir):
            if not os.path.isfile(fileName):
                continue
            if os.path.splitext(fileName)[1] != CEQConfig.ext:
                continue
            return True
        return False
    
    
    def load(self, cfgDir = '.'):
        self._loaded = False
        for fileName in os.listdir(cfgDir):
            if not os.path.isfile(fileName):
                continue
            if os.path.splitext(fileName)[1] != self.ext:
                continue
            
            s = QtCore.QSettings(fileName, QtCore.QSettings.IniFormat)
            s.setIniCodec(u'utf8')
            for place in s.childGroups():
                self._loaded = True
                s.beginGroup(place)
                placeInfo = self._placesInfo.setdefault(forceStringEx(place), {})
                placeInfo['title'] = forceStringEx(s.value(u'title', defaultValue=u'<Неизвестно>'))
                placeInfo['address'] = forceStringEx(s.value(u'address', defaultValue=u'<Неизвестно>'))
                placeInfo['port'] = forceInt(s.value(u'port', defaultValue=0))
                placeInfo['gateway'] = forceStringEx(s.value(u'gateway', defaultValue=u''))
                placeInfo['offices'] = {}
                
                s.beginGroup('offices')
                for office in s.childKeys():
                    panelAddrVariant = s.value(office, QtCore.QVariant())
                    if not panelAddrVariant.isNull():
                        placeInfo['offices'][forceStringEx(office)] = panelAddrVariant.toInt()[0]
                s.endGroup()
                s.endGroup()
        
    
    
    def getPlacesInfo(self):
        return dict(self._placesInfo)
    
    
    def getPlacesAddressList(self):
        return [value.get('address', u'') for value in self._placesInfo.values()]
            
    
    def getPlacesTitleList(self):
        return [value.get('title', u'') for value in self._placesInfo.values()]
    
    
    def getPanelAddress(self, placeCode, office):
        return self._placesInfo.get(forceStringEx(placeCode), {}).get('offices', {}).get(forceStringEx(office), 0)



class CEQConfigWindow(QtGui.QDialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self._eqConfig = CEQConfig(self)
        self.setupUi()
        self.fillPlaces()
        self.updateButtonsState()
        
    
    def closeEvent(self, event):
        userChoice = QtGui.QMessageBox.question(self, 
                                   u'Подтвердите операцию', u'Хотите отключить работу с эл. очередью и закрыть окно?', 
                                   buttons = QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                   defaultButton = QtGui.QMessageBox.Cancel)
        if userChoice == QtGui.QMessageBox.Cancel:
            event.ignore()
        else:
            self.reject()
    
    
    
    @QtCore.pyqtSlot()
    def accept(self):
        errorLines = []
        
        if self.cmbPlaceName.currentIndex() <= 0 and self.cmbPlaceName.count() > 1:
            errorLines.append(u'Не выбран объект/учреждение')
        else:
            if not self.eqPort():
                errorLines.append(u'Неверный порт моста')
            if not self.eqGateway():
                errorLines.append(u'Неверный шлюз моста')
        
        if self.cmbOffice.currentIndex() <= 0 and self.cmbOffice.count() > 1:
            errorLines.append(u'Не выбран кабинет')
        else:
            if not self.eqPanelAddress():
                errorLines.append(u'Неверный адрес табло')
        
        if errorLines:
            errorLines.append(u'\n')
            errorLines.append(u'Нажмите "Ок", чтобы поправить ошибки')
            errorLines.append(u'или "Пропустить", чтобы отключить использование табло')
            userChoice = QtGui.QMessageBox.warning(self, 
                                                   u'Обнаружены ошибки', 
                                                   u'\n'.join(errorLines), 
                                                   buttons = QtGui.QMessageBox.Ok | QtGui.QMessageBox.Ignore)
            if userChoice == QtGui.QMessageBox.Ignore:
                QtGui.QDialog.reject(self)
        else:
            QtGui.QDialog.accept(self)
    
    
    def setupUi(self):
        self.setWindowTitle(u'Настройка параметров работы табло эл. очередью')
        self.pages = QtGui.QStackedWidget() 
        
        # Страница с параметрами объекта/учреждения
        self.pagePlace = QtGui.QWidget()
        
        self.lblPlaceName = QtGui.QLabel(u'Объект/учреждение:')
        self.cmbPlaceName = QtGui.QComboBox()
        
        
        self.lblPlaceAddressCaption = QtGui.QLabel(u'Адрес:')
        self.lblPlaceAddress = QtGui.QLabel(u'')
        self.lblPlaceAddress.setWordWrap(True)
        
        self.gbEQSettings = QtGui.QGroupBox(u'Настройки моста')
        self.lblEQPort = QtGui.QLabel(u'Порт')
        self.edtEQPort = QtGui.QLineEdit()
        self.edtEQPort.setEnabled(False)
        self.lblEQGateway = QtGui.QLabel(u'Шлюз')
        self.edtEQGateway = QtGui.QLineEdit()
        self.edtEQGateway.setEnabled(False)
        layout = QtGui.QGridLayout() # Компановщик для gbEQSettings
        layout.addWidget(self.lblEQPort, 0, 0)
        layout.addWidget(self.edtEQPort, 0, 1)
        layout.addWidget(self.lblEQGateway, 1, 0)
        layout.addWidget(self.edtEQGateway, 1, 1)
        self.gbEQSettings.setLayout(layout)
        
        layout = QtGui.QGridLayout() # Компановщик для страницы с параметрами объекта/учреждения
        layout.addWidget(self.lblPlaceName, 0, 0)
        layout.addWidget(self.cmbPlaceName, 0, 1)
        layout.addWidget(self.lblPlaceAddressCaption, 1, 0)
        layout.addWidget(self.lblPlaceAddress, 1, 1)
        layout.addWidget(self.gbEQSettings, 2, 0, 1, 2)
        self.pagePlace.setLayout(layout)
        # Конец построения страницы с параметрами объекта/учреждения
        self.pages.addWidget(self.pagePlace)
        
        # Страница с выбором кабинета
        self.pageOffice = QtGui.QWidget()
        self.lblOffice = QtGui.QLabel(u'Кабинет:')
        self.cmbOffice = QtGui.QComboBox()
        self.lblEQPanelAddress = QtGui.QLabel(u'№ табло:')
        self.edtEQPanelAddress = QtGui.QLineEdit()
        self.edtEQPanelAddress.setEnabled(False)
        layout = QtGui.QGridLayout() # Компановщик для pageOffice
        layout.addWidget(self.lblOffice, 0, 0)
        layout.addWidget(self.cmbOffice, 0, 1)
        layout.addWidget(self.lblEQPanelAddress, 1, 0)
        layout.addWidget(self.edtEQPanelAddress, 1, 1)
        self.pageOffice.setLayout(layout)
        # Конец построения страницы с выбором кабинета
        self.pages.addWidget(self.pageOffice)
        
        self.btnDisablePanel = QtGui.QPushButton(u'Отключить использование табло')
        self.btnPrev = QtGui.QPushButton(u'Назад')
        self.btnNext = QtGui.QPushButton(u'Далее')
        self.btnFinish = QtGui.QPushButton(u'Завершить')
        buttonslayout = QtGui.QHBoxLayout() # Компановщик для панели с кнопками
        buttonslayout.addWidget(self.btnDisablePanel)
        buttonslayout.addStretch()
        buttonslayout.addWidget(self.btnPrev)
        buttonslayout.addWidget(self.btnNext)
        buttonslayout.addWidget(self.btnFinish)
        
        self.lblStatusBar = QtGui.QLabel()
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.pages)
        layout.addLayout(buttonslayout)
        layout.addWidget(self.lblStatusBar)
        self.setLayout(layout)
        
        self.btnDisablePanel.clicked.connect(self.on_btnDisablePanel_clicked)
        self.btnPrev.clicked.connect(self.on_btnPrev_clicked)
        self.btnNext.clicked.connect(self.on_btnNext_clicked)
        self.btnFinish.clicked.connect(self.on_btnFinish_clicked)
        self.cmbPlaceName.currentIndexChanged.connect(self.on_cmbPlaceName_currentIndexChanged)
        self.cmbOffice.currentIndexChanged.connect(self.on_cmbOffice_currentIndexChanged)
        self.pages.currentChanged.connect(self.on_pages_currentChanged)
        
    
        
    def fillPlaces(self, cfgDir = '.'):
        self._eqConfig.load(cfgDir)
        
        self.cmbPlaceName.clear()
        self.cmbPlaceName.addItem(u'Не выбрано', userData = QtCore.QVariant())
        for placeCode, placeInfo in self._eqConfig.getPlacesInfo().items():
            self.cmbPlaceName.addItem(placeInfo.get('title', u''), userData = QtCore.QVariant(placeCode))
        message = u'В конфигурационном файле отсутствуют данные по объектам' if self.cmbPlaceName.count() <= 1 else u''
        if not self._eqConfig.isLoaded():
            message = u'Не удалось загрузить конфигурационный файл (.eqcfg)'
            
        self.lblStatusBar.setText(message)
    
    
    def updateButtonsState(self):
        self.btnNext.setEnabled(self.pages.currentIndex() < (self.pages.count() - 1))
        self.btnPrev.setEnabled(self.pages.currentIndex() > 0)
        self.btnFinish.setEnabled(self.pages.currentIndex() == (self.pages.count() - 1))
        if self.btnNext.isEnabled():
            self.btnNext.setDefault(True)
        elif self.btnPrev.isEnabled():
            self.btnPrev.setDefault(True)
        else:
            self.btnDisablePanel.setDefault(True)
    
    
    def setCurrentPage(self, pageIdx):
        if pageIdx in xrange(self.pages.count()):
            self.pages.setCurrentIndex(pageIdx)
    
    
    def setPlaceCode(self, placeCode):
        idx = self.cmbPlaceName.findData(QtCore.QVariant(placeCode))
        if idx in xrange(self.cmbPlaceName.count()):
            self.cmbPlaceName.setCurrentIndex(idx)
    
    
    def setEQPort(self, port):
        port = forceInt(port)
        
        placeIdx = 0
        for idx in xrange(self.cmbPlaceName.count()):
            placeCode = forceString(self.cmbPlaceName.itemData(idx))
            if port == self._eqConfig.getPlacesInfo().get(placeCode, {}).get('port', 0):
                placeIdx = idx
                break
        
        if placeIdx:
            self.cmbPlaceName.setCurrentIndex(placeIdx)
        else:
            self.cmbPlaceName.setCurrentIndex(0)
            self.edtEQPort.setText(forceString(port))
        
    
    def eqPort(self):
        return forceInt(self.edtEQPort.text())
    
    
    def setEQGateway(self, gateway):
        gateway = forceString(gateway)
        
        placeIdx = 0
        for idx in xrange(1, self.cmbPlaceName.count()):
            placeCode = forceString(self.cmbPlaceName.itemData(idx))
            if gateway == self._eqConfig.getPlacesInfo().get(placeCode, {}).get('gateway', 0):
                placeIdx = idx
                break
        
        if placeIdx:
            self.cmbPlaceName.setCurrentIndex(placeIdx)
        else:
            self.cmbPlaceName.setCurrentIndex(0)
            self.edtEQGateway.setText(forceString(gateway))
    
    
    def eqGateway(self):
        return forceStringEx(self.edtEQGateway.text())
    
    
    def setEQPanelAddress(self, panelAddress):
        panelAddress = forceInt(panelAddress)
        
        officeIdx = 0
        for idx in xrange(1, self.cmbOffice.count()):
            if panelAddress == forceInt(self.cmbOffice.itemData(idx)):
                officeIdx = idx
                break
        
        if officeIdx:
            self.cmbOffice.setCurrentIndex(officeIdx)
        else:
            self.cmbOffice.setCurrentIndex(0)
            self.edtEQPanelAddress.setText(forceString(panelAddress))
    
    
    def eqPanelAddress(self):
        return forceInt(self.edtEQPanelAddress.text())
    
    
    @QtCore.pyqtSlot()
    def on_btnNext_clicked(self):
        newIdx = self.pages.currentIndex() + 1
        if newIdx < self.pages.count():
            self.pages.setCurrentIndex(newIdx)
    
    
    @QtCore.pyqtSlot()
    def on_btnPrev_clicked(self):
        newIdx = self.pages.currentIndex() - 1
        if newIdx >= 0:
            self.pages.setCurrentIndex(newIdx)
            
    
    @QtCore.pyqtSlot()
    def on_btnFinish_clicked(self):
        self.accept()
    
    
    @QtCore.pyqtSlot()
    def on_btnDisablePanel_clicked(self):
        self.reject()
    

    @QtCore.pyqtSlot(int)
    def on_cmbPlaceName_currentIndexChanged(self, idx):
        placeCode = forceStringEx(self.cmbPlaceName.itemData(idx))
        placeInfo = self._eqConfig.getPlacesInfo().get(placeCode, {})
        
#        self.cmbPlaceName.setStyleSheet('color:red;' if not placeCode else '')
        
        self.lblPlaceAddress.setText(placeInfo.get('address', ''))
        self.edtEQPort.setText(forceStringEx(placeInfo.get('port', '')))
        self.edtEQGateway.setText(forceStringEx(placeInfo.get('gateway', '')))
        
        self.cmbOffice.clear()
        self.cmbOffice.addItem(u'Не выбрано')
        itemsList = placeInfo.get('offices', {}).items()
        itemsList.sort(key = lambda item: forceInt(item[0]))
        for office, panelAddr in itemsList:
            self.cmbOffice.addItem(office, userData = QtCore.QVariant(panelAddr))
        self.lblStatusBar.setText(u'В конфигурационном файле отсутствует список кабинетов для выбранного объекта' if self.cmbOffice.count() <= 1 else u'')
    
    
    @QtCore.pyqtSlot(int)
    def on_cmbOffice_currentIndexChanged(self, idx):
        office = forceInt(self.cmbOffice.currentText()) if idx > 0 else 0
        placeCode = forceStringEx(self.cmbPlaceName.itemData(self.cmbPlaceName.currentIndex()))
#        self.cmbOffice.setStyleSheet('color:red;' if not office else '')
        self.edtEQPanelAddress.setText(forceStringEx(self._eqConfig.getPanelAddress(placeCode, office)))
        
        
    @QtCore.pyqtSlot(int)
    def on_pages_currentChanged(self, idx):
        self.updateButtonsState()
        


def usage(errorMessage = ''):
    moduleName = os.path.split(sys.argv[0])[1]
    if errorMessage:
        print 'Error: %s\n' % errorMessage
    print 'Usage:'
    print '%s -h' % moduleName
    print 'or'
    print '%s -c command'  % moduleName
    print 'or'
    print '%s -t text\n'  % moduleName
    print 'Where'
    print '\t-h displays this help.'
    print '\n'
    print '\t-c <command>\tsend to panel <command> in format <type><code><data>'
    print '\t\t<type> is type of command.'
    print '\t\t(If command in upper case, then is execute with writing to volatile memory.'
    print '\t\tIf in lower case - without). Can be one of following values:'
    print '\t\t\ta - request state and type of a panel(with "?" code). Setting begin and end addresses.'
    print '\t\t\th - program reset the controller (r!).'
    print '\t\t\tg - print symbols on the panel.'
    print '\t\t\tf - management blink params.'
    print '\t\t\tb - seting the brightness, further code of brightness (hex, 2 symbols).'
    print '\t\t<code> is code of command. Can be one of following values:'
    print '\t\t\t? - for command "ask" with answer.'
    print '\t\t\t! - for command "execute" with answer.'
    print '\t\t\t# - for command without answer.'
    print '\n'
    print '\t-t <text>\tsend to panel symbols of text'


def printFromatedAnswer(answer):
    sender = answer.get('sender', None)
    text = answer.get('text', '')
    if sender is None:
        print 'No answer'
    else:
        print 'Panel %s answer:' % sender
        if len(text) > 2:
            print '%s: %s' % (text[:2], text[2:])
            print 'Answer codes:'
            print '\t0 - command is executed successfully.'
            print '\t1 - command is not executed.'
            print '\t2 - command is not supported by recipient.'
            print '\t3 - incorrect format of command.'
            print '\t4 - incorrect checksum of command.'
            print '\t5 - incorrect data field in command.'
        else:
            print text

    
def connect(addr = '192.168.0.222', port = 5000, timeout = 3):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    s.connect((addr, port))
    return s


def showC(s, command, panelAddr = 255, selfAddr = 0x64):
    return s.send(CEQPanel.packCommand(command, panelAddr, selfAddr))

    
def extrAnsw(data):
    return CEQPanel.extractAnswerFromData(data)


def extr(s, timeout = 1):
    result = None
    processedKBytes = 0
    startTime = time.time()
    answer = s.recv(1024)
    while answer:
        processedKBytes += 1
        result = CEQPanel.extractAnswerFromData(answer)[:3]
        if result != (None, None, ''):
            break
        if time.time() - startTime > timeout:
            print 'reading timeout'
            break
        answer = s.recv(1024)
    return result


def createIniForOnko():
    s = QtCore.QSettings(u'..\onko.eqcfg', QtCore.QSettings.IniFormat)
    s.setIniCodec('utf8')
    
    s.beginGroup('onkoP')
    s.setValue(u'title', QtCore.QVariant(u'ФГБУ НИИ онкологии им. Н.Н. Петрова'))
    s.setValue(u'address', QtCore.QVariant(u'197758, г. Санкт–Петербург, пос. Песочный, ул. Ленинградская, дом 68'))
    s.setValue(u'port', QtCore.QVariant(5000))
    s.setValue(u'gateway', QtCore.QVariant(u'192.168.100.188'))
    s.beginGroup('offices')
    s.setValue(u'1', QtCore.QVariant(11))
    s.setValue(u'3', QtCore.QVariant(31))
    s.setValue(u'4', QtCore.QVariant(18))
    s.setValue(u'5', QtCore.QVariant(30))
    s.setValue(u'7', QtCore.QVariant(17))
    s.setValue(u'8', QtCore.QVariant(34))
    s.setValue(u'9', QtCore.QVariant(32))
    s.setValue(u'11', QtCore.QVariant(12))
    s.setValue(u'12', QtCore.QVariant(15))
    s.setValue(u'16', QtCore.QVariant(35))
    s.setValue(u'17', QtCore.QVariant(36))
    s.setValue(u'18', QtCore.QVariant(33))
    s.setValue(u'19', QtCore.QVariant(25))
    s.setValue(u'20', QtCore.QVariant(16))
    s.setValue(u'21', QtCore.QVariant(28))
    s.setValue(u'22', QtCore.QVariant(13))
    s.endGroup() #end offices description    
    s.endGroup() #end onkoP decription
    
    s.beginGroup('onkoT')
    s.setValue(u'title', QtCore.QVariant(u'Клинико-диагностический центр ФГБУ "НИИ онкологии им. Н.Н. Петрова'))
    s.setValue(u'address', QtCore.QVariant(u'191124, г. Санкт-Петербург, ул. Красного Текстильщика, д. 10-12, лит. В'))
    s.setValue(u'port', QtCore.QVariant(5000))
    s.setValue(u'gateway', QtCore.QVariant(u'192.168.100.189'))
    s.beginGroup('offices')
    s.setValue(u'21', QtCore.QVariant(26))
    s.setValue(u'26', QtCore.QVariant(20))
    s.setValue(u'29', QtCore.QVariant(29))
    s.setValue(u'32', QtCore.QVariant(24))
    s.setValue(u'34', QtCore.QVariant(21))
    s.setValue(u'35', QtCore.QVariant(23))
    s.setValue(u'36', QtCore.QVariant(27))
    s.setValue(u'37', QtCore.QVariant(22))
    s.setValue(u'38', QtCore.QVariant(19))
    s.setValue(u'39', QtCore.QVariant(37))
    s.endGroup() #end offices description
    s.endGroup() #end onkoT decription
    
    s.sync()


def main():
    createIniForOnko()
    return
    
#     eqPanel = CEQPanel(panelAddr = 32, expectAnswerMode = 2)
#     eqPanel.setDataExchangeInterface(CSocketDEInterface(('192.168.0.222', 5000), u'tcp'))
#     
#     if not eqPanel.showOnPanel('1444', False):
#         print eqPanel.lastError()
#     
#     print eqPanel.lastAnswer() 
    import time
    sock = connect('192.168.100.189', 5000, 0.1)
    for addr in xrange(1, 254):
        if addr in [11, 12, 13, 15, 16, 17, 18,25, 28, 30, 31, 32, 33, 34, 35, 36,
                    26, 29, 24, 21, 23, 27, 22, 19]:
            continue
        print addr
        showC(sock, 'g!%04d'  % addr, addr, 254)
        time.sleep(1)
    
    return 0


if __name__ == '__main__':
    main()