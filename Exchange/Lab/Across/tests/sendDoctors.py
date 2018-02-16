#!/usr/bin/python
# -*- coding: utf-8 -*-

#from datetime import *
#from ZSI.auth import AUTH
from IConvertservice_client import *
from classes import *
from Exchange.Lab.Across.IConvertservice_client import IConvertserviceLocator,\
    UpdateDoctors3Request
from Exchange.Lab.Across.AcrossRecords import CUpdateDoctorsRequest

logFile = file('log','w+');

loc = IConvertserviceLocator()
port = loc.getIConvertPort('http://utech.across.ru/ws_test/ServiceServ.exe/soap/IConvert',tracefile=logFile)
#http://across.utech.ru/ws_test/ServiceServ.exe/soap/IConvert
#port.binding.SetAuth(AUTH.httpdigest, user='testuser', password='testpassword')

print '='*10+' call test '+'='*40

request = CUpdateDoctorsRequest()
doctor = request.addDoctor()
doctor.code = '1'
doctor.name = u'Пушкин А.С.'
doctor.orgStructure = '577'

doctor = request.addDoctor()
doctor.code = '2'
doctor.name = u'Лермонтов М.Ю.'
doctor.orgStructure = '233'

doctor = request.addDoctor()
doctor.code = '3'
doctor.name = u'Тургенев И.С.'
doctor.orgStructure = '412'

doctor = request.addDoctor()
doctor.code = '4'
doctor.name = u'Гоголь Н.В.'
doctor.orgStructure = '625'

doctor = request.addDoctor()
doctor.code = '5'
doctor.name = u'Толстой Л.Н.'
doctor.orgStructure = '937'

doctor = request.addDoctor()
doctor.code = '6'
doctor.name = u'Хармс Д.'
doctor.orgStructure = '1905'

requestObject = UpdateDoctors3Request()
requestObject._Value = request.toXml({'mis_id':'10'}).encode('utf8')
#requestObject._value = request.toXml({'mis_id':'1234567890'})
requestDumpFile = file('doctors.xml','w+');
print >>requestDumpFile, request.toXml({'mis_id':'10'}).encode('utf8')
requestDumpFile.close()

responceObject = port.UpdateDoctors(requestObject)
print responceObject, responceObject._return
