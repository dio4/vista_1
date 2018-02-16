#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012 Vista Software. All rights reserved.
##
#############################################################################

from library.easySoap import *

class CWSMCC:
    
    def __init__(self, url):
        self.wsmcc = CEasySoap(url, "www.rintech.ru/IWSMCC/GetContext")
        self.Code = None
    
    def ReadContext(self, guid):
        self.wsmcc.reset()
        self.wsmcc.header("Guid", guid)
        
        self.Code       = u'ContextNotFound'
        self.lastName   = None
        self.firstName  = None
        self.patrName   = None
        self.sex        = None
        self.bDate      = None
        self.snils      = None
        self.oms        = None
        self.omsBegDate = None
        self.omsEndDate = None
        self.omsOkato   = None
        self.omsOgrn    = None
        
        self.wsmcc.call()
        self.Code           = self.wsmcc.result['Envelope']['Header']['Code']
        if self.wsmcc.result['Envelope'].has_key('Body') and type(self.wsmcc.result['Envelope']['Body']) is dict and self.wsmcc.result['Envelope']['Body'].has_key('ClinicalContext'):
            try:
                self.lastName   = self.wsmcc.result['Envelope']['Body']['ClinicalContext']['Patient']['personName']['family']
            except:
                pass

            try:
                self.firstName  = self.wsmcc.result['Envelope']['Body']['ClinicalContext']['Patient']['personName']['given']
            except:
                pass
            
            try:
                self.patrName   = self.wsmcc.result['Envelope']['Body']['ClinicalContext']['Patient']['personName']['given_']
            except:
                pass
            
            try:
                if self.wsmcc.result['Envelope']['Body']['ClinicalContext']['Patient']['gender'] == u'1':
                    self.sex = 1
                else:
                    self.sex = 2
            except:
                pass
            
            try:                    
                bDate           = self.wsmcc.result['Envelope']['Body']['ClinicalContext']['Patient']['birthDate']
                self.bDate      = QDate(int(bDate[0:4]),  int(bDate[4:6]),  int(bDate[6:8]))
            except:
                pass
            
            try:
                self.snils      = self.wsmcc.result['Envelope']['Body']['ClinicalContext']['Patient']['personId']['id']
            except:
                pass
            
            try:
                self.oms        = self.wsmcc.result['Envelope']['Body']['ClinicalContext']['Patient']['personId_']['id']
            except:
                pass
            
            try:
                bDate           = self.wsmcc.result['Envelope']['Body']['ClinicalContext']['Patient']['insurance']['startDate']
                self.omsBegDate = QDate(int(bDate[0:4]),  int(bDate[5:7]),  int(bDate[8:10]))
            except:
                pass
            
            try:
                bDate           = self.wsmcc.result['Envelope']['Body']['ClinicalContext']['Patient']['insurance']['endDate']
                self.omsEndDate = QDate(int(bDate[0:4]),  int(bDate[5:7]),  int(bDate[8:10]))
            except:
                pass
            
            try:
                self.omsOkato   = self.wsmcc.result['Envelope']['Body']['ClinicalContext']['Patient']['insurance']['insCompanyId']['jurisdiction']['id']
            except:
                pass
            
            try:
                self.omsOgrn    = self.wsmcc.result['Envelope']['Body']['ClinicalContext']['Patient']['insurance']['insCompanyId']['id']
            except:
                pass
            