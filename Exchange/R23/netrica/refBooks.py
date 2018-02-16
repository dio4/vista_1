# -*- coding: utf-8 -*-


from PyQt4 import QtGui, QtCore
import json, requests, config
from tempfile import TemporaryFile
from library.Utils import forceString

# Работа со справочниками нетрики



class CNetricaRefBooks():
    def __init__(self):
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    # Получение информации о справочнике
    def rbInfo(self, rbName, version):
        file = TemporaryFile()
        data = forceString({"resourceType": "Parameters", "parameter": [{"name": "system", "valueString": rbName},
                                                                        {"name": "version", "valueString": version}]})
        file.write(data)
        file.seek(0)
        resp = requests.post(url=(config.termUrl + 'ValueSet/$expand'), data=file.read(), headers=self.headers)
        file.close()
        if resp.status_code == 200:
            data = json.loads(resp.text)
            for par in data['parameter']:
                return par['resource']['expansion']['contains']

    # Поиск значения в справочнике
    def rbGetValue(self, rbName, code):
        file = TemporaryFile()
        data = forceString({"resourceType": "Parameters", "parameter": [{"name": "system", "valueString": rbName},
                                                                        {"name": 'code', "valueString": code}]})
        file.write(data)
        file.seek(0)
        resp = requests.post(url=(config.termUrl + 'ValueSet/$lookup'), data=file.read(), headers=self.headers)
        file.close()
        if resp.status_code == 200:
            data = json.loads(resp.text)
            return data

    # Версия справочника
    def getVersion(self, rbName):
        resp = requests.post(url=(config.termUrl + 'ValueSet?_format=json&url=' + rbName), data=file.read(), headers=self.headers)
        file.close()
        if resp.status_code == 200:
            data = json.loads(resp.text)
            return data
