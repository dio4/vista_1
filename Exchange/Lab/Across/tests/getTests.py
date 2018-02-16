#!/usr/bin/python
# -*- coding: utf-8 -*-

#from datetime import *
#from ZSI.auth import AUTH
from IConvertservice_client import *
from classes import *
from Exchange.Lab.Across.IConvertservice_client import IConvertserviceLocator,\
    SendTableTest1Request

logFile = file('logGetTests','w+');

loc = IConvertserviceLocator()
#port = loc.getIConvertPort('http://across.utech.ru/ws_test/ServiceServ.exe/soap/IConvert',tracefile=logFile)
port = loc.getIConvertPort('http://utech.across.ru/ws_test/ServiceServ.exe/soap/IConvert',tracefile=logFile)

print '='*10+' call test '+'='*40

responceObject = port.SendTableTest(SendTableTest1Request())
print responceObject, responceObject._return
