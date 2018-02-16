#! /usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
##
## Базовый класс цикла приёма/отравки сообщений согласно протокола
## ASTM E1381 (через последовательный порт сокет) либо файлового обмена
##
#############################################################################

import sys
import traceback
import threading
import Queue



class CAbstractLoop(threading.Thread):
    #
    def __init__(self):
        threading.Thread.__init__(self)
        self.inputQueue  = Queue.Queue()
        self.outputQueue = Queue.Queue()
        self._continue   = threading.Event()
        self._stopped    = threading.Event()
        self._logLevel   = 0
        self.onAcceptMessage = None # наверное, методически правильнее
        self.onLog = None           # накручивать сигналы/слоты. но я пока не хочу.


    def setLogLevel(self, logLevel):
        self._logLevel = logLevel


    def send(self, message):
        self.outputQueue.put(message)


    def acceptInputMessage(self, message):
        if self.onAcceptMessage:
            self.onAcceptMessage(message)
        else:
            self.inputQueue.put(message)


    def get(self):
        try:
            return self.inputQueue.get_nowait()
        except Queue.Empty:
            return None
        except:
            raise


    def stop(self, timeout=None):
        self._continue.clear()
        self._stopped.wait(timeout)


    def run(self):
        self._continue.set()
        self._stopped.clear()
        while self._continue.isSet():
            try:
                self._mainLoop()
            except:
                exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                print repr(exceptionType), unicode(exceptionValue), traceback.extract_tb(exceptionTraceback)
        self._stopped.set()


    def log(self, level, message):
        # 1: work start/stop
        # 2: message exchange
        # 3: frame exchange
        # 4: byte exchange
        if level<=self._logLevel:
            if self.onLog:
                self.onLog('%s:%d: %s' % (self.getName(), level, message))
            else:
                print '%s:%d: %s' % (self.getName(), level, message)
                sys.stdout.flush()


    def _mainLoop(self):
        raise NotImplementedError
