# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui

from Events.Utils import getEventTypeForm, isEventDeath, isEventPeriodic, isEventUrgent
from Forms.F000.F000Dialog import CF000Dialog
from Forms.F001.F001Dialog import CF001Dialog, CF001ExtendedDialog
from Forms.F003.F003Dialog import CF003ExtendedDialog
from Forms.F025.F025DentDialog import CF025DentalDialog
from Forms.F025.F025Dialog import CF025Dialog, CF025ExtendedDialog
from Forms.F025.F025TrDialog import CF025TrDialog
from Forms.F02512.F02512Dialog import CF02512Dialog
from Forms.F02512.F02512ExtendedDialog import CF02512ExtendedDialog
from Forms.F027.F027Dialog import CF027Dialog
from Forms.F027FF.F027FFDialog import CF027FFDialog
from Forms.F030.F030Dialog import CF030Dialog
from Forms.F030S.F030SDialog import CF030SDialog
from Forms.F043.F043Dialog import CF043Dialog
from Forms.F043v2.F043v2Dialog import CF043v2Dialog
from Forms.F106.F106Dialog import CF106Dialog
from Forms.F110.F110Dialog import CF110Dialog
from Forms.F131.F131Dialog import CF131Dialog

_eventForms = [
   ('000',   u'ф. 000/у (платное обслуживание)',      CF000Dialog),
   ('001',   u'ф. 001/у (ввод услуг)',                CF001Dialog),
   ('101',   u'Ф. 001/р (ввод услуг + ЕИС)',          CF001ExtendedDialog),
   ('003',   u'ф. 003/у (стационарное лечение)',      CF003ExtendedDialog),
   ('025',   u'ф. 025/у (стат.талон)',                CF025Dialog),
   ('325',   u'ф. 025/р (стат.талон)',                CF025ExtendedDialog),
   ('425',   u'ф. 025/з (стат.талон)',                CF025DentalDialog),
   ('125',   u'ф. 025-12/у (стат.талон)',             CF02512Dialog),
   ('225',   u'ф. 025-12/р (стат.талон)',             CF02512ExtendedDialog),
   ('030',   u'ф. 030/у (диспансерное наблюдение)',   CF030Dialog),
   ('043',   u'ф. 043/у (стоматология)',              CF043Dialog),
   ('106',   u'ф. 106/у (констатация смерти)',        CF106Dialog),
   ('131',   u'ф. 131/у (доп.диспансеризация)',       CF131Dialog),
   ('110',   u'ф. 110/у (скорая медицинская помощь)', CF110Dialog),
   ('027',   u'ф. 027/у (протокол)',                  CF027Dialog),
   ('027ff', u'ф. 027фф/у (протокол)',                CF027FFDialog),
   ('030S',  u'ф. 030С/у (стандарты)',                CF030SDialog),
   ('043v2', u'ф. 043/у-2 (стоматология)',            CF043v2Dialog),
 ]

_mapEventFormCodeToFormClass = dict([(descr[0], descr[2]) for descr in _eventForms if descr[2]])

def getEventFormClassByType(eventTypeId):
    form = getEventTypeForm(eventTypeId)
    result = _mapEventFormCodeToFormClass.get(form, None)
    if result:
        return result
    if isEventDeath(eventTypeId):
        return CF106Dialog
    if isEventPeriodic(eventTypeId):
        return CF131Dialog
    if isEventUrgent(eventTypeId):
        return CF025TrDialog
    return CF025Dialog


def getEventFormClass(eventId):
    eventTypeId = QtGui.qApp.db.translate('Event', 'id', eventId, 'eventType_id')
    return getEventFormClassByType(eventTypeId)


def getEventFormList():
    return [descr[:2] for descr in _eventForms if descr[2]]
