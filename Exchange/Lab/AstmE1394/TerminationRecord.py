#! /usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
##
## 'L' запись протокола ASTM E-1394
##
#############################################################################



from Record import CRecord

class CTerminationRecord(CRecord):
    structure = {
                    'recordType'            : ( 0,       str),
                    'seqNo'                 : ( 1,       int),
                    'code'                  : ( 2,       str), # "N" - Normal termination
                }
    recordType = 'L'


if __name__ == '__main__':
    r = CTerminationRecord()
    s = r'L|1|N'
    r.setString(s, '|\\^&')
    print r._storage
    s1 = r.asString('|\\^&')
    print s1==s
    print s
    print s1

