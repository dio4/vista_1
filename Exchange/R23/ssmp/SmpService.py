# -*- coding: utf-8 -*-


from PyQt4 import QtGui, QtCore
from suds.client import Client

# Работа с методами ССМП
from library.Utils import forceString, toVariant, forceInt, getVal


class SmpExchange():
    def __init__(self):
        self.db = QtGui.qApp.db
        tableOrganisation = self.db.table('Organisation')
        self.api = Client(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'smpAddress', '')) + u'/emergency/soap11/description')
        recOrg = self.db.getRecordEx(tableOrganisation, [tableOrganisation['infisCode'], tableOrganisation['head_id']], tableOrganisation['id'].eq(QtGui.qApp.currentOrgId()))
        if forceInt(recOrg.value('head_id')):
            self.lpuCode = forceString(self.db.translate(tableOrganisation, tableOrganisation['id'], forceInt(recOrg.value('head_id')), tableOrganisation['infisCode']))
        else:
            self.lpuCode = forceString(recOrg.value('infisCode'))

    # Методы для событий
    def getEventList(self):
        tableSmp = self.db.table('SmpEvents')
        lpuCode = forceString(self.lpuCode)
        eventList = self.api.service.getEventList(lpuCode)
        if eventList:
            for v in eventList.item:
                callInfo = self.getCallInfoStr(v.idCallNumber)
                if callInfo:
                    recEvent = self.db.getRecordEx(tableSmp, '*', tableSmp['callNumberId'].eq(forceString(callInfo.idCallNumber)))
                    if not recEvent:
                        lastName = forceString(callInfo.lastName) if forceString(callInfo.lastName) else u''
                        name = forceString(callInfo.name) if forceString(callInfo.name) else u''
                        patrName = forceString(callInfo.patronymic) if forceString(callInfo.patronymic) else u''
                        fio = lastName + u' ' + name + u' ' + patrName

                        settlement = u'нас. пункт: ' + forceString(callInfo.settlement) if forceString(callInfo.settlement) else u''
                        street = u', улица: ' + forceString(callInfo.street) if forceString(callInfo.street) else u''
                        house = u', дом: ' + forceString(callInfo.house) if callInfo.house and forceInt(callInfo.house) > 0 else u''
                        houseFract = u', дробь: ' + forceString(callInfo.houseFract) if callInfo.houseFract else u''
                        corp = u', корпус: ' + forceString(callInfo.building) if callInfo.building else u''
                        flat = u', квартира: ' + forceString(callInfo.flat) if callInfo.flat else u''
                        porch = u', подъезд: ' + forceString(callInfo.porch) if callInfo.porch and forceInt(callInfo.porch) > 0 else u''
                        floor = u', этаж: ' + forceString(callInfo.floor) if callInfo.floor and forceInt(callInfo.floor) > 0 else u''
                        address = settlement + street + house + houseFract + corp + flat + porch + floor

                        newRec = tableSmp.newRecord()
                        newRec.setValue('eventId', toVariant(v.id))
                        newRec.setValue('eventTime', toVariant(forceString(v.eventTime)))
                        newRec.setValue('callNumberId', toVariant(forceString(callInfo.idCallNumber)))
                        newRec.setValue('callDate', toVariant(QtCore.QDate.fromString(forceString(callInfo.callDate), 'yyyy-MM-dd')))
                        newRec.setValue('fio',  toVariant(fio))
                        newRec.setValue('sex', toVariant(forceInt(callInfo.sex)))
                        newRec.setValue('age', toVariant(forceInt(callInfo.ageYears)))
                        newRec.setValue('contact', toVariant(forceString(callInfo.telephone)))
                        newRec.setValue('address', toVariant(address))
                        newRec.setValue('landmarks', toVariant(forceString(callInfo.landmarks)))
                        newRec.setValue('occasion', toVariant(forceString(callInfo.callOccasion)))
                        newRec.setValue('callerName', toVariant(forceString(callInfo.callerName)))
                        newRec.setValue('urgencyCategory', toVariant(forceString(callInfo.urgencyCategory)))
                        newRec.setValue('callKind', toVariant(forceString(callInfo.callKind)))
                        newRec.setValue('receiver', toVariant(forceString(callInfo.userReceiver)))
                        self.db.insertRecord(tableSmp, newRec)



    #Получение вызовов СМП
    def getCallListStr(self, begDate, endDate):
        lpuCode = forceString(self.lpuCode)
        responce = self.api.service.getCallListStrNew(begDate, endDate, lpuCode)
        if responce:
            return responce[0]

    def getCallInfoStr(self, idCallNumber):
        lpuCode = forceString(self.lpuCode)
        callInfo = self.api.service.getCallInfoStr(lpuCode, idCallNumber)
        if callInfo:
            return callInfo

    def updEvent(self, idEvent):
        tablePerson = self.db.table('Person')
        lpuCode = forceString(self.lpuCode)
        eventTime = forceString(QtCore.QDateTime.currentDateTime().time()) + ':00'
        recUser = self.db.getRecordEx(tablePerson, [tablePerson['lastName'], tablePerson['firstName'], tablePerson['patrName'], tablePerson['id'].eq(QtGui.qApp.userId)])
        receivedUser = forceString(recUser.value('lastName')) + u' ' + forceString(recUser.value('firstName')) + u' ' + forceString(recUser.value('patrName'))
        responce = self.api.service.updEvent(lpuCode=lpuCode, id=idEvent, eventTime=eventTime, receivedUser=receivedUser)
        if responce:
            return responce

    def addEvent(self, idCallNumberSmp, idCallEventType, note, ):
        tablePerson = self.db.table('Person')
        lpuCode = forceString(self.lpuCode)
        eventTime = forceString(QtCore.QDateTime.currentDateTime().time()) + ':00'
        recUser = self.db.getRecordEx(tablePerson, [tablePerson['lastName'], tablePerson['firstName'], tablePerson['patrName'], tablePerson['id'].eq(QtGui.qApp.userId)])
        transferUser = forceString(recUser.value('lastName')) + u' ' + forceString(recUser.value('firstName')) + u' ' + forceString(recUser.value('patrName'))
        responce = self.api.service.addEvent(lpuCode=lpuCode, idCallNumber=idCallNumberSmp, idCallEventType=idCallEventType, note=note, eventTime=eventTime, transferUser=transferUser)
        if responce:
            return responce


    # Методы для работы со справочниками
    # where - фильтр
    # например where id = {id}, where is_deleted = 0

    # Справочник улиц
    def getSprStreet(self, where):
        pass

    # Справочник населенных пунктов
    def getSprSettlement(self, where):
        pass

    # Справочник мест вызова
    def getSprCallPlace(self, where):
        pass

    # Справочник видов вызова
    def getSprCallKind(self, where):
        pass

    # Справочник типов событий
    def getSprCallEventType(self, where):
        pass

    # Справочник категорий срочности
    def getSprUrgencyCategory(self):
        pass


def main():
    sender = SmpExchange()
    sender.getEventList()
if __name__ == '__main__':
    main()