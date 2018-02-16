#! /usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
##
## 'H' запись протокола ASTM E-1394
##
#############################################################################


from PyQt4.QtCore import *


from Record import CRecord

class CHeaderRecord(CRecord):
    structure = {
                    'recordType':             ( 0,       str),
                    'delimiters':             ( 1,       str),
                    'messageControlId'      : ( 2,       unicode),
                    'password'              : ( 3,       unicode),
                    'senderName'            : ( (4,0,0), unicode),
                    'senderVersion'         : ( (4,0,1), unicode),
                    'senderStreetAddress'   : ( 5,       unicode),
                    'reserved'              : ( 6,       unicode),
                    'senderPhone'           : ( 7,       unicode),
                    'senderCharacteristics' : ( 8,       unicode),
                    'receiverId'            : ( 9,       unicode),
                    'comment'               : (10,       unicode),
                    'processingId'          : (11,       unicode),
                    'version'               : (12,       unicode),
                    'dateTime'              : (13,       QDateTime),

                }
    recordType = 'H'

    def setStdFields(self):
        self.senderName = 'Samson-Vista'
        self.senderVersion = '2.0'
        self.processingId = 'P'
        self.version ='1.0'
        self.dateTime = QDateTime.currentDateTime()


    def asString(self, delimiters, encoding='utf8'):
        self.delimiters = None
        result = CRecord.asString(self, delimiters, encoding)
        return result[:1] + delimiters + result[2:]


    def setString(self, string, encoding='utf8'):
        delimiters = string[1:5]
        CRecord.setString(self, string[:2] + string[5:], delimiters, encoding)
        self.delimiters = delimiters


if __name__ == '__main__':
    r = CHeaderRecord()
    s = r'H|\^&|||HOST^1.0.0|||||||P|E 1394-97|20091116104731'
    r.setString(s)
    print r._storage
    s1 = r.asString('|\\^&')
    print s1==s
    print s
    print s1

    r1 = CHeaderRecord()
    r1.setStdFields()
    r1.processingId = 'X'
    print r1.asString('|\\^&')
    print r1._storage

