#! /usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
##
## Цикл приёма/отравки сообщений согласно протокола ASTM E1381
## (через последовательный порт или сокет)
##
#############################################################################

import time
#import Queue

from AbstractLoop      import CAbstractLoop
from AbstractInterface import CAbstractInterface


ENQ = '\x05'
NAK = '\x15'
ACK = '\x06'
EOT = '\x04'
ETX = '\x03'
ETB = '\x17'
STX = '\x02'
CR  = '\r' # 0x0D
LF  = '\n' # 0x0A
CRLF = '\r\n'


def charName(c):
    return { ENQ: '[ENQ]',
             NAK: '[NAK]',
             ACK: '[ACK]',
             EOT: '[EOT]',
             ETX: '[ETX]',
             ETB: '[ETB]',
             STX: '[STX]',
             CR:  '[CR]',
             LF:  '[LF]'
           }.get(c,None) or repr(c)


class CAstmE1381Loop(CAbstractLoop):
    establishTransmissionTimeout = 15 # таймаут начала передачи
    retryTransmissionTimeout     = 10 # задержка повтора передачи
    ackTransmissionTimeout       = 15 # таймаут подтверждения получения пакета
    maxFrameRetransmissionCount  =  6 # максимальное количество попыток отправки фрейма

    startReceivingTimeout        = 0.5 # ожидание начала передачи с другой стороны
    receivingFrameTimeout        = 30 # таймаут получения очередного фрейма

    def __init__(self, outputInterface=None, inputInterface=None):
        CAbstractLoop.__init__(self)
        assert(outputInterface is None or isinstance(outputInterface, CAbstractInterface))
        assert(inputInterface is None or isinstance(inputInterface, CAbstractInterface))
        self.inputInterface = inputInterface
        self.outputInterface = outputInterface


    def _mainLoop(self):
        # пытаюсь начать свою передачу
        if not self.outputQueue.empty():
            self._tryPutMessage(self.outputInterface)
        # пытаюсь получить сообщение, из-за таймаута получается задержка главного цикла
        self._tryGetMessage(self.inputInterface)


    def _tryPutMessage(self, interface):
        self.log(1, 'trying to output message')
        if interface and interface.prepareForWork():
            self.log(1, 'output interface ready to work')
            interface.write(ENQ)
            c = interface.read(self.establishTransmissionTimeout)
            self.log(1, 'other side responded to our [ENQ] %s' % charName(c))
            if c == NAK:
                time.sleep(self.retryTransmissionTimeout)
                return
            if c == ENQ:
                self._getMessage(interface)
                return
            if c == ACK:
                self._putMessage(interface)
                self._terminateTransmission(interface)
                return
            self._terminateTransmission(interface)
        else:
            self.log(1, 'output interface is not assigned or is not ready to work')


    def _putMessage(self, interface):
        def messageAsFrames(message):
            maxLen = 240
            frameNumber = 1
            for buff in message:
                buff += '\r'
                buffLen = len(buff)
                lastPartPos = buffLen - (buffLen % maxLen)
                for partPos in xrange(0, buffLen, maxLen):
                    part = buff[partPos:partPos+maxLen]
                    frameTerminator = ETX if partPos == lastPartPos else ETB
                    cs = ( ord('0') + frameNumber + sum(ord(c) for c in part) + ord(frameTerminator)) % 256
                    frame = '%d%s%c%02X' % (frameNumber, part, frameTerminator, cs)
                    yield frame
                    frameNumber = (frameNumber+1)%8

        messageTransmitted = False
        message = self.outputQueue.get_nowait()
        try:
            self.log(2, 'output message is %s' % repr(message))
            for i, frame in enumerate(messageAsFrames(message)):
                self.log(3, 'output frame #%d, text is %s' % (i, repr(frame)))
                tryCountDown = self.maxFrameRetransmissionCount
                while True:
                    if not self._continue.isSet():
                        self.log(1, 'output of message is canceled by request')
                        return
                    code = self._putFrame(interface, frame)
                    if code == 0:# frame accepted
                        self.log(3,'output frame #%d/%d is accepted' % (i,tryCountDown))
                        break
                    if code == 1:# frame rejected
                        self.log(3,'output frame #%d/%d is rejected' % (i,tryCountDown))
                        tryCountDown -= 1
                        if tryCountDown == 0:
                            return
                    else:       # message transmission discarded
                        self.log(3,'output of frame #%d/%d over refusal to send the message' % (i,tryCountDown))
                        return

            messageTransmitted = True
        finally:
            if messageTransmitted:
                self.log(2, 'message is transmitted')
            else:
                self.outputQueue.put(message) # requeue it
                self.log(2, 'message is not transmitted')


    def _putFrame(self, interface, frame):
        interface.write(STX)
        interface.write(frame)
        interface.write(CR)
        interface.write(LF)
        c = interface.read(self.ackTransmissionTimeout)
        self.log(4, 'after output of the frame we received %s' % charName(c))
        if c == ACK:
            return 0
        if c == EOT: # A reply of <EOT> signifies that the last frame was received successfully and the receiver is
                     # prepared to receive another frame, but <EOT> is a request to the sender to stop transmitting.
            return 2
        return 1


    def _terminateTransmission(self, interface):
        self.log(2, 'terminate transmission: send [EOT]')
        interface.write(EOT)


    def _tryGetMessage(self, interface):
        self.log(4, 'try to input message')
        if interface and interface.prepareForWork():
            self.log(4, 'input interface is ready to work')
            c = interface.read(self.startReceivingTimeout)
            self.log(4, 'from the input interface %s is read' % charName(c))
            if c == ENQ:
                self._getMessage(interface)
            else:
                return
        else:
            self.log(4, 'input interface is not assinged or is not ready to work')
            time.sleep(self.startReceivingTimeout)


    def _getMessage(self, interface):
        self.log(2, 'waiting for a input message')
        interface.write(ACK)
        frameNumber = 0
        frameStrings = []
        while True:
            if not self._continue.isSet():
                self.log(1, 'input of message is canceled by request')
                return
            code, frameIsLast, frame = self._getFrame(interface, frameNumber)
            if code == 0: # frame accepted
                frameStrings.append(frame)
                if frameIsLast and not frame.endswith(CR):
                    frameStrings.append(CR) # судя по документации, возможный вариант
                interface.write(ACK)
                frameNumber +=1
            elif code == 1: # frame not accepted,retry required
                interface.write(NAK)
            elif code == 2: # timeout
                self.log(2, 'timeout of input message')
                return
            elif code == 3: # work done
                if frameStrings:
                    self.log(2, 'input message arrived')
                    self.acceptInputMessage(''.join(frameStrings).rstrip(CR).split(CR))
                else:
                    self.log(2, 'empty input message is dropped')
                return


    def _getFrame(self, interface, frameNumber):
        self.log(3, 'waiting for a input frame')
        startTime = time.time()
        buff = None
        while True:
            c = interface.read(1)
            if c == EOT:
                self.log(4, 'EOT accepted, end of input message')
                return 3, None, None
            if c:
                if c == STX:
                    buff = ''
                elif buff is not None:
                    buff += c
                    if buff.endswith(CRLF):
                        badFrameFormat = (     len(buff)<6 # [FN][ETB/ETX][SC1][CS2][CR][LF]
                                            or buff[0] != str((frameNumber+1)%8)
                                            or buff[-5] not in (ETX, ETB)
                                            or buff[-4:-2].upper() != '%02X' % (sum(ord(c) for c in buff[:-4]) % 256)
                                         )
                        if badFrameFormat:
                            self.log(3, 'input frame #%d %s is not accepted' % (frameNumber, repr(buff)))
                            return 1, None, None
                        else:
                            self.log(3, 'input frame #%d %s is accepted' % (frameNumber, repr(buff)))
                            return 0, False, buff[1:-5]
            currTime = time.time()
            if currTime-startTime>self.receivingFrameTimeout:
                self.log(3, 'input frame #%d is not accepted due to a timeout' % (frameNumber))
                return 2, None, None
            if currTime<startTime: # время переставили...
                currTime = startTime

