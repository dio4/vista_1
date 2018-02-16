#!/usr/bin/python
# -*- coding: utf-8 -*-

#from datetime import *
#from ZSI.auth import AUTH
from IConvertservice_client import *
from classes import *
from Exchange.Lab.Across.IConvertservice_client import IConvertserviceLocator,\
    SendTableSpecimen2Request

logFile = file('log','w+');

loc = IConvertserviceLocator()
port = loc.getIConvertPort('http://utech.across.ru/ws_test/ServiceServ.exe/soap/IConvert',tracefile=logFile)

print '='*10+' call test '+'='*40

responceObject = port.SendTableSpecimen(SendTableSpecimen2Request())
print responceObject, responceObject._return
