#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012 Vista Software. All rights reserved.
##
#############################################################################

from library.easySoap import *

class CMIPWinSrv:
    
    def __init__(self, url):
        self.wsmcc = CEasySoap(url, "www.rintech.ru/IContextIdentity/GetCurrent")
        self.Guid = None
    
    def ReadContext(self):
        self.Guid = None
        self.wsmcc.reset()
        self.wsmcc.call()
        self.Guid = self.wsmcc.result['Envelope']['Body']['GetCurrentResponse']['GetCurrentResult']
        
