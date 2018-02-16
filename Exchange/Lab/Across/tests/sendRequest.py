#!/usr/bin/python
# -*- coding: utf-8 -*-

#from datetime import *
#from ZSI.auth import AUTH
from IConvertservice_client import *
from AcrossRecords import *
from Exchange.Lab.Across.IConvertservice_client import IConvertserviceLocator,\
    GiveNewOrders0Request
from Exchange.Lab.Across.AcrossRecords import CRequest

import PyQt4


logFile = file('log','w+');

loc = IConvertserviceLocator()
port = loc.getIConvertPort('http://utech.across.ru/ws_test/ServiceServ.exe/soap/IConvert',tracefile=logFile)
#http://across.utech.ru/ws_test/ServiceServ.exe/soap/IConvert
#port.binding.SetAuth(AUTH.httpdigest, user='testuser', password='testpassword')

print '='*10+' call test '+'='*40

request = CRequest()
sample = request.addSample()
sample.date           = PyQt4.QtCore.QDate.currentDate()  # Дата
sample.sampleType     = '0'          # Тип
sample.lab            = '<&>\'";some lab'   # Номер лаборатории/V
sample.label          = '3780115'    # Номер пробы/V
sample.clientId       = 123456       # Уникальный идентификатор пациента/V
sample.eventId        = 654321       # ИсторияБолезни/№ Истории Болезни/V
sample.fullName       = u'Иванов Иван Иванович' # ИндОбследуемого/ФИО/V
sample.birthDate      = PyQt4.QtCore.QDate(2000,12,31) # ДатаРождения/ДатаРождения/V
sample.sex            = u'м' # Пол/V
#sample.pregnancy      = None # Беременость
#sample.datecw         = None # ДеньЦикла
#sample.climax         = None # Пменоп
sample.counterpart    = u'п51'# Контрагент/Код отделения ЛПУ, или код внешнего ЛПУ/V
sample.orgStructure   = u'терап1'   # ОтделенияКонтрагента/Код отделения внешнего ЛПУ
sample.financeType    = u'ОМС' # Код ИсточникаЗаказа (ОМС,ДМС )/V
sample.person         = u'007' # Назначающий_врач   Код Назначающего врача
sample.policy         = u'АК 47' # Серия Номер страхового полиса (ННН 000000000008)
sample.insurer        = u'кАСКО' # Код страховой компании
sample.mkb            = u'W58' # ДиагнозМКБ
sample.diag           = u'Драка с крокодилом' # ДиагнозСтрока
sample.note           = u'Примечаешь?' # Примечание
sample.priority       = 1    # Приоритет (срочный/рутинный- 0/1)
#sample.host_id        = None # идентификатор внешней системы, используется при связи с несколькими внешними системами
if 1:
    test = sample.addTest()
    test.mcn          = u'001' # ГосКод
    #test.note         = None # ТестКомментарий
    test.specimen     = u'кровища' # Материал
    test = sample.addTest()
    test.mcn          = u'002' # ГосКод
    #test.note         = None # ТестКомментарий
    test.specimen     = u'ещё кровища' # Материал

sample = request.addSample()
sample.date           = PyQt4.QtCore.QDate.currentDate()  # Дата
sample.sampleType     = '1'          # Тип
sample.lab            = '<&>\'";some lab'   # Номер лаборатории/V
sample.label          = '3784004'    # Номер пробы/V
sample.clientId       = 234567       # Уникальный идентификатор пациента/V
sample.eventId        = 765432       # ИсторияБолезни/№ Истории Болезни/V
sample.fullName       = u'Петров Пётр Петрович' # ИндОбследуемого/ФИО/V
sample.birthDate      = PyQt4.QtCore.QDate(1900,11,30) # ДатаРождения/ДатаРождения/V
sample.sex            = u'м' # Пол/V
#sample.pregnancy      = None # Беременость
#sample.datecw         = None # ДеньЦикла
#sample.climax         = None # Пменоп
sample.counterpart    = u'п51'# Контрагент/Код отделения ЛПУ, или код внешнего ЛПУ/V
sample.orgStructure   = u'терап2'   # ОтделенияКонтрагента/Код отделения внешнего ЛПУ
sample.financeType    = u'Бюджет' # Код ИсточникаЗаказа (ОМС,ДМС )/V
sample.person         = u'007' # Назначающий_врач   Код Назначающего врача
sample.policy         = u'АК 47 :)" &-) :->' # Серия Номер страхового полиса (ННН 000000000008)
sample.policy         = u'АК 47+ \'"<&>' # Серия Номер страхового полиса (ННН 000000000008)
#sample.policy         = u'АК 47+' # Серия Номер страхового полиса (ННН 000000000008)
sample.insurer        = u'кАСКО' # Код страховой компании
sample.mkb            = u'S192.2' # ДиагнозМКБ
sample.diag           = u'Секир-башка' # ДиагнозСтрока
sample.note           = u'Всё ещё примечаешь?' # Примечание
sample.priority       = 0    # Приоритет (срочный/рутинный- 0/1)
    #sample.host_id        = None # идентификатор внешней системы, используется при связи с несколькими внешними системами
if 1:
    test = sample.addTest()
    test.mcn          = u'011' # ГосКод
    #test.note         = None # ТестКомментарий
    test.specimen     = u'кусок мозга' # Материал
    test = sample.addTest()
    test.mcn          = u'012' # ГосКод
    #test.note         = None # ТестКомментарий
    test.specimen     = u'другой кусок мозга' # Материал


requestObject = GiveNewOrders0Request()
requestObject._Value = request.toXml({'mis_id':'1234567890'}).encode('utf8')
#requestObject._value = request.toXml({'mis_id':'1234567890'})
requestDumpFile = file('request.xml','w+');
print >>requestDumpFile, request.toXml({'mis_id':'1234567890'}).encode('utf8')
requestDumpFile.close()

responceObject = port.GiveNewOrders(requestObject)
print responceObject, responceObject._return
