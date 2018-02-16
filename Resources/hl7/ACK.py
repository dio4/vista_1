#!/usr/bin/env python
# -*- coding: utf-8 -*-

from segments import *


class ACK(THl7Message):
    _items = [ ('MSH', 'MSH', MSH),
               ('SFT', 'SFT', [SFT]),
               ('MSA', 'MSA', MSA), 
               ('ERR', 'ERR', [ERR]), 
             ]
    _name = 'ACK'

ACK.register()