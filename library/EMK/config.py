# -*- coding: utf-8 -*-
def getLoggingDirectory():
    import platform
    if platform.system() == 'Windows':
        return LOGGING_DIRECTORY_WINDOWS
    else:
        return LOGGING_DIRECTORY_UNIX

LOGGER_NAME = 'logger'  # Сюда вписать имя базы логгер, если оно не стандартное
LOGGING_DIRECTORY_UNIX = '/var/log/emk/'
LOGGING_DIRECTORY_WINDOWS = ''
LOGGING_DIRECTORY = getLoggingDirectory()

# REAL
KEY_TOKEN = '1BA2D440-509F-4FDA-8E24-249DE9E32E96'
PIX_WSDL_URL = 'http://10.0.1.83/EmkService/PixService.svc?wsdl'
EMK_WSDL_URL = 'http://10.0.1.83/EmkService/EMKService.svc?wsdl'

# TEST
# KEY_TOKEN = '6B980BEE-F78E-45D5-8B85-FEFD6D6A98E0'
# PIX_WSDL_URL = 'http://demo-iemk20.zdrav.netrika.ru/PixService.svc?wsdl'
# EMK_WSDL_URL = 'http://demo-iemk20.zdrav.netrika.ru/EMKService.svc?wsdl'

LPU_INFIS = u'13039'

connectionInfo = {
        'driverName': 'mysql',
        'host': '172.16.78.130', # Сюда вписать ip сервера с базой данных
        'port': 3306,
        'database': 's11vm', # Сюда вписать имя базы данных
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }