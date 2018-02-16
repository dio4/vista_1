#! /usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
##
## 'R' запись протокола ASTM E-1394
##
#############################################################################


from PyQt4.QtCore import *

from Record import CRecord


class CResultRecord(CRecord):
    structure = {
                    'recordType'            : ( 0,       str),
                    'seqNo'                 : ( 1,       int),
                    'testId'                : ( 2,       unicode), # as vector
                    'assayCode'             : ( (2,0,3), unicode),
                    'assayName'             : ( (2,0,4), unicode),
                    'dilution'              : ( (2,0,5), unicode),
                    'assayStatus'           : ( (2,0,6), unicode),
                    'reagentLot'            : ( (2,0,7), unicode),
                    'reagentSerialNumber'   : ( (2,0,8), unicode),
                    'controlLotNumber'      : ( (2,0,9), unicode),
                    'resultType'            : ( (2,0,10), unicode),
                    'value'                 : ( 3,       unicode),
                    'unit'                  : ( 4,       unicode),
                    'referenceRange'        : ( 5,       unicode),
#                    'abnormalFlags'         : ( 6,       int),  # 0: Normal result
                                                                # 1: Result out ofnormal values
                                                                # 2: Result out ofattention values
                                                                # 3: Result out of panic values 
                                                                # +10 Delta-check
                                                                # +1000 Device alarm

                    'abnormalFlags'         : ( 6,       unicode),  # 0: Normal result
                                                                # 1: Result out ofnormal values
                                                                # 2: Result out ofattention values
                                                                # 3: Result out of panic values 
                                                                # +10 Delta-check
                                                                # +1000 Device alarm

                    'abnormalityTestingNature'
                                            : ( 7,       unicode),
                    'status'                : ( 8,       str), # 'F': indicating a finalresult, 'R': indicating arerun.
                    'operator1'             : ( (10,0,1), unicode),
                    'operator2'             : ( (10,0,2), unicode),
                    
                    'startDateTime'         : (11,       QDateTime),
                    'stopDateTime1'         : ((12,0,1), QDateTime),
                    'stopDateTime2'         : ((12,0,1), QDateTime),
                    'instrumentIdent'       : (13,       unicode)
                }
    recordType = 'R'


if __name__ == '__main__':
    r = CResultRecord()
    s = r'R|1|^^^NA^Sodium|7.273|mmol/l|10-120|0|N|F||Val.Autom.^Smith|201009261006|201009261034^201009261033|Architect'
    r.setString(s, '|\\^&')
    print r._storage
    s1 = r.asString('|\\^&')
    print s1==s
    print s
    print s1
