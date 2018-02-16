#! /usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
##
## 'P' запись протокола ASTM E-1394
##
#############################################################################


from PyQt4.QtCore import *


from Record import CRecord

class CPatientRecord(CRecord):
    structure = {
                    'recordType'            : ( 0,       str),
                    'seqNo'                 : ( 1,       int),
                    'patientId'             : ( 2,       unicode),
                    'laboratoryPatientId'   : ( 3,       unicode),
                    'reservedPatientId'     : ( 4,       unicode),
                    'lastName'              : ( (5,0,0), unicode),
                    'firstName'             : ( (5,0,1), unicode),
                    'patrName'              : ( (5,0,2), unicode),

                    'motherMaidenName'      : ( 6,       unicode),
                    'birthDate'             : ( 7,       QDate),
                    'sex'                   : ( 8,       str), # M/F
                    'race'                  : ( 9,       unicode),
                    'address'               : (10,       unicode),
                    'reserved'              : (11,       unicode),
                    'phone'                 : (12,       unicode),
                    'physician'             : (13,       unicode),
                    'age'                   : ((14,0,0), int),
                    'ageUnit'               : ((14,0,1), unicode), # days/months/years

                    'isExternal'            : (15,       int), # 1- external, 0 - internal
                    'height'                : (16,       unicode),
                    'weight'                : (17,       unicode),
                    'diagnosis'             : (18,       unicode),
                    'medication'            : (19,       unicode),
                    'diet'                  : (20,       unicode),
                    'practiceField1'        : (21,       unicode),
                    'practiceField2'        : (22,       unicode),
                    'admissionDate'         : (23,       unicode),
                    'admissionStatus'       : (24,       unicode),
                    'sender'                : (25,       unicode),# wtf CHIR ?
                }
    recordType = 'P'


if __name__ == '__main__':
    r = CPatientRecord()
    s = r'P|1|1212000|117118112||White^Nicky||19601218|M||||| Smith | 37^years|0||||||||||CHIR'
    r.setString(s, '|\\^&')
    print r._storage
    s1 = r.asString('|\\^&')
    print s1==s
    print s
    print s1

