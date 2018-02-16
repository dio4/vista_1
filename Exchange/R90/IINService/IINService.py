# -*- coding: utf-8 -*-
import json
import urllib
import urllib2

from library.Utils import AnyRequest


class CR90IINService:
    def __init__(self, login, password, url):
        self.auth = {
            'login' : login,
            'password' : password
        }
        self.header = {
            'PHPSESSID' : None,
            'BITRIX_USER_ID' : None,
        }
        self.url = url
        self.error = u''
        self.patientResult = {
            'orgHealthCareId' : None,
            'iin' : None,
            'name' : None,
            'surname' : None,
            'middlename' : None,
            'birthdate' : None, # "DD.MM.YYYY"
            'phone' : None,
            'orgHealthCareName' : None,
            'territoryNumber' : None,
            'address' : None
        }

    def postAuthorization(self):
        url = self.url + '/auth/'
        req = urllib2.Request(url=url, data=urllib.urlencode(self.auth))
        resp = json.load(urllib2.urlopen(req))
        if resp['success']:
            self.header['PHPSESSID'] = str(resp['sessionId'])
            self.header['BITRIX_USER_ID'] = str(resp['bitrixSessionId'])
            return True
        else: return False


    def getPatient(self, IIN=None, name=None):
        u"""
        Передать только один из параметров. Если переданы оба — будет использоваться второй
        IIN — /d{12}: Двенадцать цифр
        name — {/w }3: Три слова через пробел (Ф И О)
        :return True/False — Успешно или не успешно прошло получение данных.
            Если успешно — данные в patientResult.
            Если не успешно — данные об ошибке в error
        """

        url = self.url + '/rpn/'
        if self.header['PHPSESSID'] is None or self.header['BITRIX_USER_ID'] is None:
            res = self.postAuthorization()
            if not res:
                self.error = u'Ошибка авторизации'
                return False
        if IIN is None and name is None:
            self.error = u'Пустой запрос'
            return False
        if IIN:  search = IIN
        elif name: search = name.replace(' ', '%20')
        req = AnyRequest(url=str(url) + '?search=' + search.encode('utf-8'), headers={'Cookie' : ';'.join('%s=%s' % (k,v) for k,v in self.header.items())}, method='GET')
        resp = urllib2.urlopen(req)
        try:
            resp = json.load(resp)
        except AttributeError as e:
            #TODO:skkachaev: Считаем, что если пришла на xml'ка, то, наверное, нас считают не авторизованными
            self.error = u'Наверное, нас, почему-то, считают не авторизованными\n'
            self.error += resp.decode('utf-8')
            self.error += u'\nЗапрос:\n'
            self.error += '\n'.join([str(k) + u' : ' + str(s) for k,s in self.header.items()])
            return False
        if 'errorMessage' in resp:
            self.error = resp['errorMessage']
            return False
        else:
            self.patientResult['orgHealthCareId'] = resp['orgHealthCareId']
            self.patientResult['iin'] = resp['iin']
            self.patientResult['name'] = resp['name']
            self.patientResult['surname'] = resp['surname']
            self.patientResult['middlename'] = resp['middlename']
            self.patientResult['birthdate'] = resp['birthdate']
            self.patientResult['phone'] = resp['phone']
            self.patientResult['orgHealthCareName'] = resp['orgHealthCareName']
            self.patientResult['territoryNumber'] = resp['territoryNumber']
            self.patientResult['address'] = resp['address']
            return True


if __name__ == '__main__':
    serv = CR90IINService('mis_demeu', 'mis_demeu', 'http://www.densaulyk.com/service')
    serv.postAuthorization()