#! /usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
##
## Интерфейс приёма/отравки сообщений согласно протокола
## ASTM E1381 через последовательный порт 
##
#############################################################################


import time
import serial

from AbstractInterface import CAbstractInterface


class CSerialInterface(CAbstractInterface):
    def __init__(self, opts):
        self.opts = opts
        self.port = None


    def prepareForWork(self):
        if self.port is None:
            self.open()
        return bool(self.port)


    def open(self):
        self.port = serial.Serial(port         = self.opts.get('port',     0),
                                  baudrate     = self.opts.get('baudrate', 9600),
                                  bytesize     = self.opts.get('bytesize', serial.EIGHTBITS),
                                  parity       = self.opts.get('parity',   serial.PARITY_NONE),
                                  stopbits     = self.opts.get('stopbits', serial.STOPBITS_ONE),
                                  timeout      = 1,
                                  writeTimeout = 1,
                                  rtscts       = self.opts.get('rtscts',   False),
                                  dsrdtr       = self.opts.get('dsrdtr',   False),
                                  xonxoff      = self.opts.get('xonxoff',  False)
                                 )


    def close(self):
        if self.port:
            try:
                self.port.close()
            except:
                pass
            self.port = None


    def read(self, timeout):
#        print '--read--start--', timeout
        self.port.timeout=timeout
        result = self.port.read(1)
#        print '--read--done--', repr(result)
        return result




    def write(self, buff):
#        print '--write--start--', len(buff), repr(buff)
        p = 0
        while p<len(buff):
            written = self.port.write(buff[p:])
#            print '--write--done--', written, len(buff), repr(buff)
            p += written
#        print '--write--done--'


if __name__ == '__main__':
    from AstmE1381Loop import CAstmE1381Loop


    def testSinglePortSendMessage(opts):
        print '-'*60
        print 'testSinglePortSendMessage'
        try:
            f = file('samples/order-small.ord','r')
#            f = file('samples/order-average.ord','r')
#            f = file('samples/order-big.ord','r')
            message = [ s.replace('\r','').replace('\n','') for s in f ]
            f.close()
        except:
            message = ['1','2','3','4']
        interface = CSerialInterface(opts)
        loop = CAstmE1381Loop(interface, interface)
        loop.setName('i/o loop')
#        l.setLogLevel(9)
        loop.start()
        try:
            loop.send(message)
            for i in range(60):
                print 'write',i
                if loop.outputQueue.empty():
                    break
                time.sleep(1)
        finally:
            loop.stop()



    def testSinglePortGetMessage(opts):
        print '-'*60
        print 'testSinglePortGetMessage'
        interface = CSerialInterface(opts)

        loop = CAstmE1381Loop(interface, interface)
        loop.setName('i/o loop')
        loop.setLogLevel(9)
        loop.start()
        try:
            for i in range(60):
                print 'read', i
                result = loop.get()
                if result:
                    print repr(result)
                time.sleep(1)
        finally:
            loop.stop()

    testSinglePortSendMessage({'port':'/dev/ttyUSB0'})
#    testSinglePortGetMessage({'port':'/dev/ttyUSB0'})

