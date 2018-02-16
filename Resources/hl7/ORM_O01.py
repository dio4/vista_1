#!/usr/bin/env python
# -*- coding: utf-8 -*-

from segments import *


class ORM_O01_PATIENT(THl7Compound):
    _items = [ ('PID', 'PID', PID),
             ]


class ORM_O01_OBRRQDRQ1RXOODSODT_SUPPGRP(THl7Compound):
    _items = [ ('OBR', 'OBR', OBR),
             ]


class ORM_O01_ORDER_DETAIL(THl7Compound):
    _items = [ ('ORM_O01_OBRRQDRQ1RXOODSODT_SUPPGRP', 'ORM_O01.OBRRQDRQ1RXOODSODT_SUPPGRP', ORM_O01_OBRRQDRQ1RXOODSODT_SUPPGRP),
             ]


class ORM_O01_ORDER(THl7Compound):
    _items = [ ('ORC', 'ORC', ORC),
               ('ORM_O01_ORDER_DETAIL', 'ORM_O01.ORDER_DETAIL', ORM_O01_ORDER_DETAIL),
             ]


class ORM_O01(THl7Message):
    _items = [ ('MSH', 'MSH', MSH),
               ('ORM_O01_PATIENT', 'ORM_O01.PATIENT', ORM_O01_PATIENT),
               ('ORM_O01_ORDER',   'ORM_O01.ORDER',   [ORM_O01_ORDER])
             ]
    _name = 'ORM_O01'

#    def __init__(self):
#        THl7Message.__init__(self)

ORM_O01.register()


