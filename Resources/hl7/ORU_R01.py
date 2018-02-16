#!/usr/bin/env python
# -*- coding: utf-8 -*-

from segments import *


class ORU_R01_VISIT(THl7Compound):
    _items = [ ('PV1', 'PV1', PV1),
               ('PV2', 'PV2', PV2),
             ]


class ORU_R01_PATIENT(THl7Compound):
    _items = [ ('PID', 'PID', PID),
               ('PD1', 'PD1', PD1),
               ('NTE', 'NTE', [NTE]),
               ('NK1', 'NK1', [NK1]),
               ('ORU_R01_VISIT','ORU_R01.VISIT', ORU_R01_VISIT),
             ]


class ORU_R01_TIMING_QTY(THl7Compound):
    _items = [ ('TQ1', 'TQ1', TQ1),
               ('TQ2', 'TQ2', [TQ2]),
             ]

             
class ORU_R01_OBSERVATION(THl7Compound):
    _items = [ ('OBX', 'OBX', OBX),
               ('NTE', 'NTE', [NTE]),
             ]


class ORU_R01_SPECIMEN(THl7Compound):
    _items = [ ('SPM', 'SPM', SPM),
               ('OBX', 'OBX', [OBX]),
             ]
             

class ORU_R01_ORDER_OBSERVATION(THl7Compound):
    _items = [ ('ORC', 'ORC', ORC),
               ('OBR', 'OBR', OBR), 
               ('NTE', 'NTE', [NTE]), 
               ('ORU_R01_TIMING_QTY', 'ORU_R01.TIMING_QTY', [ORU_R01_TIMING_QTY]), 
               ('CTD', 'CTD', CTD),
               ('ORU_R01_OBSERVATION', 'ORU_R01.OBSERVATION', [ORU_R01_OBSERVATION]),
               
               ('FT1', 'FT1', [FT1]),
               ('CTI', 'CTI', [CTI]),
               ('ORU_R01_SPECIMEN', 'ORU_R01.SPECIMEN', [ORU_R01_SPECIMEN]),
             ]
             
             
class ORU_R01_PATIENT_RESULT(THl7Compound):
    _items = [ ('ORU_R01_PATIENT', 'ORU_R01.PATIENT', ORU_R01_PATIENT),
               ('ORU_R01_ORDER_OBSERVATION',   'ORU_R01.ORDER_OBSERVATION',   [ORU_R01_ORDER_OBSERVATION]),
             ]

             
class ORU_R01(THl7Message):
    _items = [ ('MSH', 'MSH', MSH),
               ('SFT', 'SFT', [SFT]),
               ('ORU_R01_PATIENT_RESULT', 'ORU_R01.PATIENT_RESULT', ORU_R01_PATIENT_RESULT),
               ('DSC', 'DSC', DSC),
             ]
    _name = 'ORU_R01'

    
ORU_R01.register()

