# -*- coding: utf-8 -*-
# Учетные данные для авторизации в ТФОМС
userName = '780103'
password = '32007rgSbK9'

# УРЛ подключения к ТФОМС
# http://pkd-dev.ru:17488 - тестовый
# http://10.20.31.222:8080 - боевой
url = 'http://pkd-dev.ru:17488'

# Интревал для отправки данных в ТФОМС (минут)
interval = 20

# Настройки подключения к БД
connectionInfo = {
    'driverName': 'mysql',
    'host': 'pes',
    'port': 3306,
    'database': 's11',
    'user': 'dbuser',
    'password': 'dbpassword',
    'connectionName': 'vista-med',
    'compressData': True,
    'afterConnectFunc': None
}