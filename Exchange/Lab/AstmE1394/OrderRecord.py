#! /usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
##
## 'O' запись протокола ASTM E-1394
##
#############################################################################


from PyQt4.QtCore import *


from Record import CRecord

class COrderRecord(CRecord):
    structure = {
                    'recordType'            : ( 0,       str),
                    'seqNo'                 : ( 1,       int),
                    'specimenId'            : ( 2,       unicode), # sample id
                    'instrumentSpecimenId'  : ( 3,       unicode),
                    'testId'                : ( 4,       unicode), # as vector
                    'assayCode'             : ( (4,0,3), unicode),
                    'assayName'             : ( (4,0,4), unicode),
                    'priority'              : ( 5,       unicode), # S=Stat, R=Routine
                    'requestDateTime'       : ( 6,       QDateTime),
                    'specimenCollectionDateTime' : ( 7,       QDateTime),
                    'actionCode'            : (11,       str),  # (C)ancel – Used to cancel a previously downloaded test order.
                                                                # (A)dd – Used to add a test to a known specimen.
                                                                # (N)ew – Used to identify New Test Order for an unknown specimen. If the specimen is known, this message is ignored.
                                                                # (R)erun – Used to request a Rerun for a test.
                    'specimenDescr'         : (15,       unicode), # S (Serum), U (Urine) etc, etc
                    'userField1'            : (18,       unicode),
                    'userField2'            : (19,       unicode),
                    'laboratoryField1'      : (20,       unicode),
                    'laboratoryField2'      : (21,       unicode),

                    'reportTypes'           : (25,       unicode), # (O)rder – Normal request from Host.
                                                                   # (F)inal - Final Result
                    'specimenInstitution'   : (30,       unicode), # Production Lab: when using multi-laboratory configuration
                                                                   # this field can indicate laboratory expected to process the sample
                }
    recordType = 'O'


if __name__ == '__main__':
    r = COrderRecord()
    s = r'O|1|12120001||^^^NA^Sodium\^^^Cl^Clorum|R|20011023105715|20011023105715||||N||||S|||CHIM|AXM|Lab1|12120||||O|||||LAB2'
    r.setString(s, '|\\^&')
    print r._storage
    for n in ('specimenId', 'instrumentSpecimenId', 'testId', 'assayCode', 'assayName',
              'requestDateTime', 'specimenCollectionDateTime', 'actionCode', 'specimenDescr',
              'userField1', 'userField2', 'laboratoryField1', 'laboratoryField2','reportTypes', 'specimenInstitution'):
        print n,'\t= ', getattr(r, n)
    s1 = r.asString('|\\^&')
    print s1==s
    print s
    print s1

