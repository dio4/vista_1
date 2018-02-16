# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui
from PyQt4.QtCore import QString, QDate
from Orgs.PersonInfo import CPersonInfo
from Registry.Utils import CClientInfo
from library.PrintInfo import CInfo, CTemplatableInfoMixin, CInfoProxyList
from library.Utils import forceString, forceInt, forceRef


class CDestinationDayInfo(CInfo):
    def __init__(self, context, eventId, date, num):
        CInfo.__init__(self, context)
        self._eventId = eventId
        self._date = date
        self._num = num
        self._times = self.getInstance(CDestinationHourInfoList, eventId, date)

    def _load(self):
        return True

    date  = property(lambda self: self.load()._date.toString('dd.MM.yyyy'))
    num   = property(lambda self: self.load()._num + 1)
    times = property(lambda self: self.load()._times)


class CDestinationDayInfoList(CInfoProxyList):
    def __init__(self, context, eventId, dateBegin, dateEnd):
        CInfoProxyList.__init__(self, context)
        self._eventId = eventId
        self._dates = []

        db = QtGui.qApp.db
        stmt = "CALL getEventDrugDestinationsDates('%s', '%s', '%s')" % (eventId, dateBegin.toString('yyyy-MM-dd'),
                                                                                                dateEnd.toString('yyyy-MM-dd'))
        query = db.query(stmt)
        while query.next():
            dateStrings = forceString(query.record().value('takeDate'))
            dateStrings = dateStrings.split(',')
            for dateStr in dateStrings:
                date = QDate.fromString(dateStr, 'yyyy-MM-dd')
                if not self._dates.__contains__(date):
                    self._dates.append(date)
        self._items = [ None ] * len(self._dates)

    def __getitem__(self, key):
        v = self._items[key]
        if v is None:
            v = self.getInstance(CDestinationDayInfo, self._eventId, self._dates[key], key)
            self._items[key] = v
        return v

    def begDate(self):
        if self._dates:
            return self._dates[0]
        else:
            return None

    def endDate(self):
        if self._dates:
            return self._dates[-1]
        else:
            return None

    def generateBarCode(self):
        if self._dates:
            return self.begDate().toString('ddMMyyyy') + self.endDate().toString('ddMMyyyy') + QString.number(self._eventId)
        else:
            return None


class CDestinationHourInfo(CInfo):
    def __init__(self, context, eventId, date, time):
        CInfo.__init__(self, context)
        self._eventId = eventId
        self._date = date
        self._time = time
        self._drugId = None
        self._drugName = None
        self._drugDose = None
        self._drugRoute = None

    def _load(self):
        db = QtGui.qApp.db
        stmt = "CALL getEventDateDrugDestinations('%s', '%s', '%s')" % (self._eventId, self._date.toString('yyyy-MM-dd'), self._time + ':00')
        query = db.query(stmt)
        if query.first():
            record = query.record()
            self._drugId = forceInt(record.value('drugItem_id'))
            medicineId = forceInt(db.translate('DrugFormulary_Item', 'id', self._drugId, 'drug_id'))
            self._drugName = forceString(db.translate('rbMedicines', 'id', medicineId, 'name'))
            self._drugDose = forceString(record.value('takeDose')) + ' ' + forceString(db.translate('rbUnit', 'id', forceInt(record.value('drugMeasureUnit_id')), 'name'))
            self._drugRoute = forceString(db.translate('rbRoute', 'id', forceInt(record.value('drugRouteId')), 'name'))
            return True
        else:
            return False

    time      = property(lambda self: self.load()._time)
    drugName  = property(lambda self: self.load()._drugName)
    drugDose  = property(lambda self: self.load()._drugDose)
    drugRoute = property(lambda self: self.load()._drugRoute)

class CDestinationHourInfoList(CInfoProxyList):
    def __init__(self, context, eventId, date):
        CInfoProxyList.__init__(self, context)

        self._eventId = eventId
        self._date = date
        self._hours = []
        self._items = None

        db = QtGui.qApp.db
        stmt = "CALL getEventDateDrugDestinationsHours('%s', '%s')" % (eventId, date.toString('yyyy-MM-dd'))
        query = db.query(stmt)
        while query.next():
            timeStrings = forceString(query.record().value('takeTime'))
            timeStrings = timeStrings.split(',')
            for timeStr in timeStrings:
                timeStr = timeStr[:-3]
                if not self._hours.__contains__(timeStr):
                    self._hours.append(timeStr)
        self._items = [ None ] * len(self._hours)

    def __getitem__(self, key):
        v = self._items[key]
        if v is None:
            v = self.getInstance(CDestinationHourInfo, self._eventId, self._date, self._hours[key])
            self._items[key] = v
        return v

class CDestinationInfo(CInfo, CTemplatableInfoMixin):
    def __init__(self, context, eventId, dateBegin, dateEnd):
        CInfo.__init__(self, context)
        self._eventId = eventId
        self._begDate = dateBegin
        self._endDate = dateEnd

    def _load(self):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        record = db.getRecord(tableEvent, '*', self._eventId)
        if record:
            self._client = self.getInstance(CClientInfo, forceRef(record.value('client_id')))
            self._setPerson = self.getInstance(CPersonInfo, forceRef(record.value('setPerson_id')))
            self._destinationDays = self.getInstance(CDestinationDayInfoList, self._eventId, self._begDate, self._endDate)
        else:
            self._client = None
            self._setPerson = None
            self._destinationDays = None
        return True

    def __str__(self):
        self.load()
        return unicode(u'Назначения для ') + self.client.fullName()

    begDate         = property(lambda self: self.load()._destinationDays.begDate().toString('dd.MM.yyyy'))
    endDate         = property(lambda self: self.load()._destinationDays.endDate().toString('dd.MM.yyyy'))
    barCode         = property(lambda self: self.load()._destinationDays.generateBarCode())
    client          = property(lambda self: self.load()._client)
    setPerson       = property(lambda self: self.load()._setPerson)
    destinationDays = property(lambda self: self.load()._destinationDays)