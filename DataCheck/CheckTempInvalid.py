# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from DataCheck.CCheck   import CCheck
from library.Utils      import forceDate, forceInt, forceRef, forceString

from Ui_TempInvalid     import Ui_TempInvalidCheckDialog


class TempInvalidCheck(QtGui.QDialog, Ui_TempInvalidCheckDialog, CCheck):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CCheck.__init__(self)
        currentDate = QtCore.QDate.currentDate()
        self.dateEdit_1.setDate(QtCore.QDate(currentDate.year(), 1, 1))
        self.dateEdit_2.setDate(currentDate)

    def check(self):
        db=QtGui.qApp.db
        today=QtCore.QDate.currentDate()
        today_str=today.toString('yyyy-MM-dd')
        my_org_id=QtGui.qApp.currentOrgId()
        docType=self.boxDocTypes.currentIndex()
        checkExpert=self.checkExpert.isChecked()
        checkDocum=self.checkDocum.isChecked()
        checkDur=self.checkDur.isChecked()
        tableTempInvalid_Period = db.table('TempInvalid_Period')
        n=0
        q='''
select
TempInvalid.id as TempInvalidId, TempInvalid.client_id,
TempInvalid.doctype, TempInvalid.serial, TempInvalid.number,
TempInvalid.begDate, TempInvalid.endDate,
TempInvalid.person_id, TempInvalid.diagnosis_id,
TempInvalid.sex as TempInvalid_sex, TempInvalid.age,
TempInvalid.duration, TempInvalid.closed,
Client.birthDate, Client.sex, Client.lastName, Client.firstName, Client.patrName,
rbTempInvalidReason.code, rbTempInvalidReason.requiredDiagnosis,
rbTempInvalidReason.primary, rbTempInvalidReason.prolongate, rbTempInvalidReason.restriction
from
TempInvalid
left join Client on Client.id=TempInvalid.client_id
left join rbTempInvalidReason on rbTempInvalidReason.id=TempInvalid.tempInvalidReason_id
where
1
            '''
        date1=forceString(self.dateEdit_1.date().toString('yyyy-MM-dd'))
        date2=forceString(self.dateEdit_2.date().toString('yyyy-MM-dd'))
        q+=' and (TempInvalid.endDate between "'+date1+'" and "'+date2+'")'
        q+=' and TempInvalid.doctype=%d' % docType
        query=db.query(q)
        n=0
        n_bad=0
        s=query.size()
        if s>0:
            self.progressBar.setMaximum(s-1)
        while query.next():
            QtGui.qApp.processEvents()
            if self.abort: break
            self.progressBar.setValue(n)
            n+=1
            self.item_bad=False
            record=query.record()
            def val(name): return record.value(name)
            TempInvalidId=forceInt(val('TempInvalidId'))
            client_id=forceInt(val('client_id'))
            self.client_id=client_id
            begDate=forceDate(val('begDate'))
            endDate=forceDate(val('endDate'))
            self.begDate=begDate
            self.endDate=endDate
            self.itemId=client_id, begDate, endDate
            lastName=forceString(val('lastName'))
            firstName=forceString(val('firstName'))
            patrName=forceString(val('patrName'))
            fio=lastName+' '+firstName+' '+patrName
            birthDate=forceDate(val('birthDate')).toString('dd.MM.yyyy')
            sex=forceInt(val('sex'))
            self.err_str='client '+forceString(client_id)+' ('+fio+', '+forceString(birthDate)+') '

            code=forceString(val('code'))
            if code:
                requiredDiagnosis=forceInt(val('requiredDiagnosis'))
                if requiredDiagnosis:
                    diagnosis_id=forceInt(val('diagnosis_id'))
                    if not diagnosis_id:
                        self.err2log(u'нет диагноза')
                else:
                    TempInvalid_sex=forceInt(val('TempInvalid_sex'))
                    if not TempInvalid_sex:
                        self.err2log(u'нет пола')
                    age=forceInt(val('age'))
                    if not age:
                        self.err2log(u'нет возраста')
            else:
                self.err2log(u'нет причины нетрудоспособности')

            if checkDocum:
                serial=forceString(val('serial'))
                number=forceString(val('number'))
                if not serial or not number:
                    self.err2log(u'нет серии или номера документа')

            if db.getRecordEx(
                tableTempInvalid_Period, '*',
                'master_id=%d and result_id is null' % TempInvalidId):
                self.err2log(u'нет результата в периоде')

            if checkExpert:
                closed=forceInt(val('closed'))
                if closed==1:
                    if endDate > today:
                        self.err2log(u'максимальмая дата закрытого периода ещё не наступила')
                else:
                    if endDate < today:
                        self.err2log(u'максимальмая дата незакрытого периода уже прошла')

                if checkDur:
                    duration=forceInt(val('duration'))
                    if duration<=0:
                        self.err2log(u'неправильная длительность')
                    if begDate.daysTo(endDate) != duration-1:
                        self.err2log(u'неправильная длительность')

                primary=forceInt(val('primary'))
                prolongate=forceInt(val('prolongate'))
                restriction=forceInt(val('restriction'))
                self.checkTempInvalid_Period(
                    TempInvalidId, begDate, endDate, primary, prolongate, restriction)

            if self.item_bad:
                n_bad+=1
            self.labelInfo.setText(u'%d карточек всего; %d с ошибками' % (s, n_bad))

    def openItem(self, item):
        clientId, begDate, endDate = item
        db = QtGui.qApp.db
        tableEventType = db.table('EventType')
        eventTypeIdList = db.getIdList(
            tableEventType, 'id', tableEventType['code'].inlist(['01']))
        tableEvent = db.table('Event')
        cond = [
            tableEvent['execDate'].ge(begDate),
            tableEvent['execDate'].le(endDate.addDays(1)),
            tableEvent['deleted'].eq(0),
            tableEvent['client_id'].eq(clientId),
            tableEvent['eventType_id'].inlist(eventTypeIdList)]
        eventRecord = db.getRecordEx(tableEvent, 'id', cond, 'execDate DESC')
        if eventRecord:
            eventId = forceRef(eventRecord.value('id'))
            eventTypeId=eventTypeIdList[0]
            formClass = self.getEventFormClass(eventTypeId)
            form = formClass(self)
            form.load(eventId)
            return form
        return None

    def checkTempInvalid_Period(self,
        TempInvalidId, begDate, endDate, primary, prolongate, restriction):
        TempInvalid_PeriodList=QtGui.qApp.db.getRecordList(
            'TempInvalid_Period', cols='begDate, endDate',
            where='master_id=%d' % TempInvalidId, order='begDate')
        def dateCheck(lst, date1, date2):
            if lst:
                rec=lst[0]
                rec_date1=forceDate(rec.value('begDate'))
                rec_date2=forceDate(rec.value('endDate'))
                if rec_date1 < date1:
                    self.err2log(u'даты периодов пересекаются')
                    return
                if rec_date1 != date1:
                    self.err2log(u'разрыв в датах периодов')
                    return
                dateCheck(lst[1:], rec_date2.addDays(1), date2)
            else:
                if date1 != date2.addDays(1):
                    self.err2log(u'даты окончания периодов не совпадают')
                    return
        dateCheck(TempInvalid_PeriodList, begDate, endDate)
