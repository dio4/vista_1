#! /usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
##
## Средство приёма/отравки отного сообщения согласно протокола ASTM E1381
## (через файлы)
##
#############################################################################

import os
import time


class CFileInterface(object):
    EOL = '\r\n'
    lastUsedTs = None
    tsCounter = 0

    def __init__(self, opts):
        self.inDir        = self.expand(opts.get('inDir', opts.get('dir', '.')))
        self.inPrefix     = opts.get('inPrefix', opts.get('prefix',''))
        self.inDataExt    = self.fixExt(opts.get('inDataExt', opts.get('dataExt','')))
        self.inSignalExt  = self.fixExt(opts.get('inSignalExt',opts.get('signalExt','.ok')))

        self.outDir       = self.expand(opts.get('outDir', opts.get('dir', '.')))
        self.outPrefix    = opts.get('outPrefix', opts.get('prefix',''))
        self.outDataExt   = self.fixExt(opts.get('outDataExt', opts.get('dataExt','')))
        self.outSignalExt = self.fixExt(opts.get('outSignalExt',opts.get('signalExt','.ok')))


    @classmethod
    def createFile(cls, dir, prefix, suffix):
        while True:
            ts = time.localtime()
            if cls.lastUsedTs != ts:
                cls.lastUsedTs = ts
                cls.tsCounter = 0
            else:
                cls.tsCounter += 1
            if cls.tsCounter:
                fileName = '%s%s_%03d%s' % (prefix, time.strftime('%y%m%d_%H%M%S'), cls.tsCounter, suffix)
            else:
                fileName = '%s%s%s' % (prefix, time.strftime('%y%m%d_%H%M%S'), suffix)
            filePath = os.path.join(dir, fileName)
            try:
                flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
                if hasattr(os, 'O_BINARY'):
                    flags |= os.O_BINARY
                fileHandle = os.open(filePath, flags, 0666)
                return fileHandle, filePath
            except OSError, e:
                if e.errno == os.errno.EEXIST:
                    continue
                raise


    @staticmethod
    def expand(path):
        return os.path.expanduser(os.path.expandvars(path))


    @staticmethod
    def fixExt(ext):
        if ext == '.':
            return ''
        if ext and not ext.startswith('.'):
            return '.'+ext
        return ext


    @staticmethod
    def replaceExt(fileName, ext):
        prefix, suffix = os.path.splitext(fileName)
        return prefix + ext


    @staticmethod
    def extIs(fileName, ext):
        prefix, suffix = os.path.splitext(fileName)
        if suffix == '.':
            suffix = ''
        return suffix == ext


    def write(self, message):
        # handle - ориентированный I/O появился из-за того, что я не знаю
        # как более высокоуровневыми средствами python создать файл с условием O_EXCL
        #
        handle, dataFilePath = self.createFile(suffix=self.outDataExt, prefix=self.outPrefix, dir=os.path.expanduser(self.outDir))
        try:
            os.write(handle, self.EOL.join(message))
            os.write(handle, self.EOL)
        finally:
            os.close(handle)
        signalFilePath = self.replaceExt(dataFilePath, self.outSignalExt)
        signalFile = file(signalFilePath, 'w')
        signalFile.close()



