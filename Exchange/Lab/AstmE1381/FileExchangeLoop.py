#! /usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
##
## Цикл приёма/отравки сообщений согласно протокола ASTM E1381
## (через файлы)
##
#############################################################################

import os
import time

from FileInterface     import CFileInterface
from AbstractLoop      import CAbstractLoop


class CFileExchangeLoop(CAbstractLoop, CFileInterface):
    fsCheckDelay = 1 # задержка цикла проверки файлов

    def __init__(self, opts):
        CAbstractLoop.__init__(self)
        CFileInterface.__init__(self, opts)
        self.inDirStat = None


    def _mainLoop(self):
        while not self.outputQueue.empty():
            self._putMessage()
        self._GetMessages()
        time.sleep(self.fsCheckDelay)


    def _putMessage(self):
        messageTransmitted = False
        message = self.outputQueue.get_nowait()
        try:
            self.log(2, 'output message is %s' % repr(message))
            handle, dataFilePath = CFileInterface.createFile(dir=os.path.expanduser(self.outDir),
                                                             prefix=self.outPrefix,
                                                             suffix=self.outDataExt)
            try:
                dataFile = os.fdopen(handle,'wb')
                dataFile.write( self.EOL.join(message) )
                dataFile.write( self.EOL )
            finally:
                dataFile.close()
            signalFilePath = self.replaceExt(dataFilePath, self.outSignalExt)
            signalFile = file(signalFilePath, 'w')
            signalFile.close()
            messageTransmitted = True
        finally:
            if messageTransmitted:
                self.log(2, 'message is transmitted')
            else:
                self.outputQueue.put(message) # requeue it
                self.log(2, 'message is not transmitted')


    def _GetMessages(self):
        # код получился таким сложным от того, что я не уверен
        # что в код другой стороны будет сохранять регистр символов

        inDir = os.path.expanduser(self.inDir)
        inDirStat = os.stat(inDir)
        if self.inDirStat == inDirStat:
            self.log(3, 'input directory "%s" seem unchanged' % inDir)
            return

        fileNameList = os.listdir(inDir)
        fileNameListUC = [ fileName.upper() for fileName in fileNameList ]
        prefix = self.inPrefix.upper()
        dataExt = self.inDataExt.upper()
        signalExt = self.inSignalExt.upper()

        for i, fileNameUC in enumerate(fileNameListUC):
            if fileNameUC.startswith(prefix) and self.extIs(fileNameUC,signalExt):
                self.log(3, 'signal file "%s" is detected' % fileNameList[i])
                dataFileNameUC = self.replaceExt(fileNameUC,dataExt)
                try:
                    j = fileNameListUC.index(dataFileNameUC)
                except:
                    j = -1
                if j>=0:
                    signalFilePath = os.path.join(inDir, fileNameList[i])
                    dataFilePath   = os.path.join(inDir, fileNameList[j])
                    try:
                        self._processDataFile(dataFilePath)
                        os.unlink(signalFilePath)
                        os.unlink(dataFilePath)
                    except IOError, e:
                        self.log(1, '"%s" I/O error(%s): %s' % (e.filename, e.errno, e.strerror))
                    except:
                        raise
                    self.log(2, 'input message from file "%s" is done' % dataFilePath)
        self.inDirStat == inDirStat


    def _processDataFile(self, dataFilePath):
        self.log(3, 'process data file "%s"' % dataFilePath)
        file = open(dataFilePath, 'r')
        message = [ line.strip(self.EOL) for line in file ]
        self.acceptInputMessage(message)
        file.close()
