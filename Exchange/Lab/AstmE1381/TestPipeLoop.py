#! /usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
##
## Тестовый интерфейс приёма/отравки сообщений согласно протокола
## ASTM E1381. Предназначен для тестирования и отладки CAstmE1381Loop
##
#############################################################################


import time
import threading
import sys
import Queue

from AbstractInterface import CAbstractInterface


class CPipeInterface(CAbstractInterface):
    def __init__(self, writeQueue, readQueue):
        self.writeQueue = writeQueue
        self.readQueue = readQueue

    def prepareForWork(self):
        return True


    def open(self):
        pass

    def close(self):
        pass


    def read(self, timeout):
        try:
            sys.stdout.flush()
            return self.readQueue.get(True, timeout)
        except Queue.Empty:
            return ''

    def write(self, buff):
        for c in buff:
            self.writeQueue.put(c)


if __name__ == '__main__':
    from AstmE1381Loop import CAstmE1381Loop

    def testPipe():
        print '-'*60
        queue = Queue.Queue()
        pipe = CPipeInterface(queue, queue)
        pipe.write('hello')
        for i in xrange(10):
            print i, repr(pipe.read(5))


    def testDryRun():
        print '-'*60
        print 'dry run'
        abQueue = Queue.Queue()
        baQueue = Queue.Queue()
        
        abPipe = CPipeInterface(abQueue, baQueue)
        baPipe = CPipeInterface(baQueue, abQueue)

        print '0', [repr(t) for t in threading.enumerate()]

        aLoop = CAstmE1381Loop(abPipe, abPipe)
        aLoop.setName('aLoop')
        bLoop = CAstmE1381Loop(baPipe, baPipe)
        bLoop.setName('bLoop')

        print '1', [repr(t) for t in threading.enumerate()]

        aLoop.start()
        bLoop.start()

        print '2', [repr(t) for t in threading.enumerate()]

        aLoop.stop()
        bLoop.stop()

        print '3', [repr(t) for t in threading.enumerate()]


    def testPassSingleMessage(size=0):
        print '-'*60
        print 'send message from a to b'

        abQueue = Queue.Queue()
        baQueue = Queue.Queue()

        abPipe = CPipeInterface(abQueue, baQueue)
        baPipe = CPipeInterface(baQueue, abQueue)

        print '0', [repr(t) for t in threading.enumerate()]

        aLoop = CAstmE1381Loop(abPipe, abPipe)
        aLoop.setName('aLoop')
        aLoop.setLogLevel(9)
        bLoop = CAstmE1381Loop(baPipe, baPipe)
        bLoop.setName('bLoop')
        #bLoop.setLogLevel(9)

        print '1', [repr(t) for t in threading.enumerate()]

        aLoop.start()
        bLoop.start()

        print '2', [repr(t) for t in threading.enumerate()]

        if size == 0:
            message = [ '0','11','222','3333' ]
        else:
            message = [ str(i)*(i*10+1) for i in range(100) ] # 467 фреймов. достаточно?
        aLoop.send(message)
        try:
            result = None
            for i in xrange(60):
                echo = bLoop.get()
                if echo:
                    print '3.1', i, 'echo equal to message', echo == message
                    #print '3.1.1', repr(message)
                    #print '3.1.2', repr(echo)
                    result = echo == message
                    break
                else:
                    print '3.2 %d wait, ab.size=%d, ba.size=%d' % (i, abQueue.qsize(), baQueue.qsize())
                time.sleep(1)
        finally:
            print '4', [repr(t) for t in threading.enumerate()]
            aLoop.stop()
            bLoop.stop()
            print '5', [repr(t) for t in threading.enumerate()]

    # testPipe()
    # testDryRun()
    testPassSingleMessage(1)