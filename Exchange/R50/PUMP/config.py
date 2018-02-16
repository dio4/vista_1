# -*- coding: utf-8 -*-
from PyQt4 import QtGui

LPU_ID = 666 #TODO:skkachaev: Здесь настроить ID ЛПУшки
SYSTEM = u'VISTA-MED' #TODO:skkachaev: Если я правильно понял, о чём речь
USER = u'Admin' #TODO:skkachaev: Автоматом почти всегда посылаем
PUMP_URL = '' #TODO:skkachaev: Пока что можем только мечтать

#Наша база данных
db = None
traceFileName = 'PUMPTraceFile.log'

connectionInfo = {
    'driverName': 'mysql',
    'host': '192.168.0.207',
    'port': 3306,
    'database': 'most03-06-2016',
    'user': 'dbuser',
    'password': 'dbpassword',
    'connectionName': 'vista-med',
    'compressData': True,
    'afterConnectFunc': None
}