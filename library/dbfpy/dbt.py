#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
#import glob
import struct

__all__ = ["Dbt3"]


class Dbt3(object):
    """DBT DbaseIII+ accessor.

    """

    __slots__ = "name", "stream", "_avail", "_changed"
    pageSize = 512


    def __init__(self, dbfName, readOnly, new):
        """Initialize instance.

        Arguments:
            dbfName:
                     name of .dbf file
            new:
                     True if new data table must be created. Assume
                     data table exists if this argument is False.

        """
        name, ext = os.path.splitext(dbfName)
        if ext.lower() == '.dbf':
            ext = ext[:3] + 'Tt'[ext[3].islower()]
        else:
            ext = '.dbt'
        self.name = name + ext
        if new:
            self.stream = file(self.name, "w+b")
            self._avail = 1
            self._storeHeader()
        else:
            # dbt file must exist
            self.stream = file(self.name, ("r+b", "rb")[bool(readOnly)])
            self._readHeader()
        self._changed = False


    ## protected methods


    def _storeHeader(self):
        self.stream.seek(0)
        buff = struct.pack("<L8xB", self._avail, 3) + "\0"*499
        self.stream.write(buff)

    def _readHeader(self):
        self.stream.seek(0)
        buff = self.stream.read(13)
        self._avail, ver = struct.unpack("<L8xB", buff)
        if ver != 3:
            raise TypeError(".DBT file has not DBaseIII format")

    ## iterface methods

    def close(self):
        self.flush()
        self.stream.close()

    def flush(self):
        """Flush data to the associated stream."""
        if self._changed:
            self._storeHeader()
            self.stream.flush()
            self._changed = False

    def getItem(self, idx):
        result = ''
        self.stream.seek(idx*self.pageSize)
        while True:
            buff = self.stream.read(512)
            if not buff:
                break
            pos = buff.find("\x1a") # some tools produce single 0x1a
            if pos>=0:
                result += buff[:pos]
                break
            result += buff
        return result

    def putItem(self, raw):
        result = self._avail
        offset = self._avail*self.pageSize
        self.stream.seek(offset)
        pos = self.stream.tell()
        if offset>pos:
            self.stream.write('\0'*(offset-pos))
        self.stream.write(raw)
        self.stream.write("\x1a\x1a") # specs require two 0x1a
        self._avail += (len(raw)+2+511)//512
        self._changed = True
        return result
