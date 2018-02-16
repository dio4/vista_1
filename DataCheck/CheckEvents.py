#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from DataCheck.CCheck       import CCheck

from library.AgeSelector    import checkAgeSelector, parseAgeSelector
from library.Utils          import forceDate, forceInt, forceString, forceStringEx, toVariant, getPref, getPrefBool, \
                                   getPrefDate, setPref, calcAgeTuple, firstYearDay, MKBwithoutSubclassification

from Registry.Utils         import getClientPolicy

from Ui_Events              import Ui_EventsCheckDialog


class CEventsCheck(QtGui.QDialog, Ui_EventsCheckDialog, CCheck):
    def __init__(self, parent):
        global EventTypes
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CCheck.__init__(self)
        self.tblEventType.setTable('EventType')
        EventTypes_str=forceString(QtGui.qApp.preferences.appPrefs.get('EventTypesControl', '1, 12, 25, 27, 26'))
        EventTypes=[int(x) for x in EventTypes_str.split(', ') if EventTypes_str]
        self.tblEventType.setValues(EventTypes)
        self.diag_info={}
        self.action_info={}
        self.Action_selectionGroups_info={}
        self.Diag_selectionGroups_info={}
        self.__preferences = ''


    def check(self):
        global EventTypes
        db=QtGui.qApp.db
        my_orgId=QtGui.qApp.currentOrgId()
        checkExt=self.checkExt.isChecked()
        checkSetPerson=self.checkSetPerson.isChecked()
        checkPolis=self.checkPolis.isChecked()
        n=0
        q='''
            select
                Event.id as event_id, Event.externalId,
                Event.org_id as event_org_id, Event.contract_id,
                Event.setDate, Event.setPerson_id, Event.execDate, Event.execPerson_id,
                Event.result_id, Event.eventType_id,
                Client.id as client_id, Client.birthDate, Client.sex,
                Client.lastName, Client.firstName, Client.patrName
            from
                Event
                join Client on Client.id=Event.client_id
            where
                1
            '''
        date1=forceString(self.dateEdit_1.date().toString('yyyy-MM-dd'))
        date2=forceString(self.dateEdit_2.date().toString('yyyy-MM-dd'))
        q+=' and (Event.execDate between "'+date1+'" and "'+date2+'")'
        EventTypes=self.tblEventType.values()
        if EventTypes:
            q+=' and Event.eventType_id in ('+', '.join([str(et) for et in EventTypes])+')'
        if self.checkPayed.isChecked():
            q+=' and isEventPayed(Event.id)'
        query=db.query(q)
        query.setForwardOnly(True)
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
            eventId=forceInt(val('event_id'))
            self.eventId=eventId
            self.itemId=eventId
            clientId=forceInt(val('client_id'))
            lastName=forceString(val('lastName'))
            firstName=forceString(val('firstName'))
            patrName=forceString(val('patrName'))
            fio=lastName+' '+firstName+' '+patrName
            birthDate=forceDate(val('birthDate'))
            sex=forceInt(val('sex'))
            setDate=forceDate(val('setDate'))
            execDate=forceDate(val('execDate'))
            self.err_str='client '+forceString(clientId)+' ('+fio+', '+forceString(birthDate.toString('dd.MM.yyyy'))+') event '+forceString(execDate.toString('dd.MM.yyyy'))+' '
            if checkPolis:
                self.checkPolicy(clientId, setDate, execDate)
            externalId=forceString(val('externalId'))
            event_orgId=forceInt(val('event_org_id'))
            if checkExt and not externalId and event_orgId!=str(my_orgId):
                self.err2log(u'без внешнего идентификатора')
            contractId=forceInt(val('contract_id'))
            if not contractId and event_orgId==my_orgId:
                self.err2log(u'без договора')
            if checkSetPerson:
                setPersonId=forceInt(val('setPerson_id'))
                if not setPersonId:
                    self.err2log(u'без ответственного врача')
            execPersonId=forceInt(val('execPerson_id'))
            if not execPersonId:
                self.err2log(u'без выполнившего врача')
            resultId=forceInt(val('result_id'))
            if not resultId:
                self.err2log(u'отсутствует код результата')
            elif not db.getRecord('rbResult', 'id', resultId):
                self.err2log(u'неправильный код результата')
            eventTypeId=forceInt(val('eventType_id'))
            clientAge = calcAgeTuple(birthDate, execDate)
            self.checkDiags(eventId, sex, setDate, execDate, eventTypeId, clientAge)
            self.checkActions(eventId, sex, setDate, execDate, eventTypeId, clientAge)
            if self.item_bad:
                n_bad+=1
            self.labelInfo.setText(u'%d карточек всего; %d с ошибками' % (s, n_bad))
            EventTypes=self.tblEventType.values()

    def checkPolicy(self, clientId, setDate, execDate):
        policy=getClientPolicy(clientId)
        if policy:
            begDate=forceDate(policy.value('begDate'))
            endDate=forceDate(policy.value('endDate'))
            if begDate and begDate>setDate:
                self.err2log(u'полис выдан после начала ДД')
            if endDate and endDate<execDate:
                self.err2log(u'полис аннулирован')

    def checkDiags(self, eventId, sex, setDate, execDate, eventTypeId, clientAge):
        db=QtGui.qApp.db
        selectionGroups=self.get_Diag_selectionGroups(eventTypeId)
        if not selectionGroups:
            self.err2log(u'проверка диагнозов пропущена, так как не реализована')
            return # skip check
        mnogo=False
        malo=False
        zak_diags=0
        zak_gz=0
        gz_max=0
        no_person=False
        person_0=False
        person_null=False
        for selectionGroup in selectionGroups:
            stmt=u'''
select
Diagnostic.endDate, Diagnostic.diagnosisType_id, Diagnostic.stage_id, Diagnostic.person_id,
Diagnosis.MKB, Diagnostic.healthGroup_id,
rbSpeciality.code as speciality, rbSpeciality.name as sname,
EventType_Diagnostic.sex as EventType_Diagnostic_sex,
EventType_Diagnostic.age, EventType_Diagnostic.actuality,
Person.code as person_code, Person.federalCode

from
Diagnostic
left join Person on Diagnostic.person_id=Person.id
left join Diagnosis on Diagnosis.id=Diagnostic.diagnosis_id
left join rbSpeciality on rbSpeciality.id=Diagnostic.speciality_id
left join Event on Event.id=Diagnostic.event_id
left join EventType_Diagnostic on
    (EventType_Diagnostic.eventType_id=Event.eventType_id and
    EventType_Diagnostic.speciality_id=Diagnostic.speciality_id)
where
Diagnostic.event_id=%d and
Diagnostic.deleted = 0 and
EventType_Diagnostic.eventType_id=%d and
EventType_Diagnostic.selectionGroup=%d
order by
Diagnostic.diagnosisType_id
                ''' % (eventId, eventTypeId, selectionGroup)
            query=QtGui.qApp.db.query(stmt)
            diag_num=0
            diag_osn={} # количество осн./закл. диагнозов
            while query.next():
                diag_num+=1
                record=query.record()
                speciality=forceString(record.value('speciality'))
                osn_num=diag_osn.get(speciality, 0)
                sname=forceString(record.value('sname'))
                MKB=forceStringEx(record.value('MKB'))
                if not MKB:
                    self.err2log(u'отсутствует МКБ')
                    continue
                if MKB != MKB.upper():
                    self.err2log(u'неправильный МКБ')
                    continue
                if not db.getRecordEx('MKB', '*', 'DiagID="%s"' % MKBwithoutSubclassification(MKB)):
                    self.err2log(u'неправильный МКБ')
                    continue
                person_code=forceString(record.value('person_code'))
                federalCode=forceString(record.value('federalCode'))
                if person_code=='' and federalCode=='':
                    no_person=True
                elif person_code in ['', '0'] and federalCode in ['', '0']:
                    person_0=True
                endDate=forceDate(record.value('endDate'))
                diagnosisTypeId=forceInt(record.value('diagnosisType_id'))
                healthGroupId=forceInt(record.value('healthGroup_id'))
                personId=forceInt(record.value('person_id'))
                if not personId:
                    person_null=True
                if MKB[:1] in ['Z', 'z']:
#                    if diagnosisTypeId not in [1, 2]:
#                        #z0-z13.9
#                        mkb_num=MKB[1:].split('.')
#                        if len(mkb_num):
#                            num1=int(mkb_num[0])
#                            if num1<13 or (num1==13 and (len(mkb_num)>1 and int(mkb_num[1])<=9)):
#                                self.err2log(u'диагноз Z назначен сопутствующим')
                    if healthGroupId>1 and diagnosisTypeId>1:
                        #z0-z13.9
                        mkb_num=MKB[1:].split('.')
                        if len(mkb_num):
                            num1=int(mkb_num[0])
                            if num1<14:
                                self.err2log(u'группа>1 диагноз Z')
                else:
                    if healthGroupId==1:
                        self.err2log(u'группа=1 диагноз не Z')
                if diagnosisTypeId==1:
                    zak_diags+=1
                    zak_gz=healthGroupId
                    if healthGroupId<1 or healthGroupId>6:
                        self.err2log(u'неправильная группа заключительного диагноза')
                if diagnosisTypeId in [1, 2]:
                    gz_max=max(gz_max, healthGroupId)
                    diag_osn[speciality]=osn_num+1
                else:
                    diag_osn[speciality]=osn_num
                EventType_Diagnostic_sex=forceInt(record.value('EventType_Diagnostic_sex'))
                age=forceString(record.value('age'))
                actuality=forceInt(record.value('actuality'))
                if age and clientAge:
                    ageSelector = parseAgeSelector(age)
                    if not checkAgeSelector(ageSelector, clientAge):
                        self.err2log(u'осмотр спец. '+sname+u' не подходит по возрасту')
                beg=setDate.addMonths(-actuality)
                if not endDate:
                    self.err2log(u'осмотр спец. '+sname+u' без даты')
                if endDate and endDate<beg:
                    self.err2log(u'осмотр спец. '+sname+u' раньше начала ДД')
                if endDate and endDate>execDate:
                    self.err2log(u'осмотр спец. '+sname+u' позже окончания ДД')
                if EventType_Diagnostic_sex and EventType_Diagnostic_sex!=sex:
                    self.err2log(u'осмотр спец. '+sname+u' не подходит по полу')

            cond='eventType_id=%d and selectionGroup=%d' % (eventTypeId, selectionGroup)
            EventType_Diagnostic=QtGui.qApp.db.getRecordEx(
                'EventType_Diagnostic', cols='sex, age', where=cond)
            if EventType_Diagnostic:
                EventType_Diagnostic_sex=forceString(EventType_Diagnostic.value('sex'))
                if EventType_Diagnostic_sex and EventType_Diagnostic_sex!=sex:
                    continue
                age=forceString(EventType_Diagnostic.value('age'))
                if age and clientAge:
                    ageSelector = parseAgeSelector(age)
                    if not checkAgeSelector(ageSelector, clientAge):
                        continue

            for (spec, num) in diag_osn.iteritems():
                sname=forceString(db.translate('rbSpeciality', 'code', spec, 'name'))
                if num==0:
                    self.err2log(u'нет основного диагноза у спец. '+sname)
                if num>1:
                    self.err2log(u'несколько основных диагнозов у спец. '+sname)
            if selectionGroup>1:
                if diag_num>1:
                    mnogo=True
                elif not diag_num:
                    malo=True
            elif selectionGroup==1:
                if not diag_num:
                    malo=True
            elif selectionGroup==0:
                if diag_num:
                    mnogo=True
            else:
                if diag_num>1:
                    mnogo=True
        if mnogo:
            self.err2log(u'лишние диагнозы')
        if malo:
            self.err2log(u'не хватает диагнозов')
        if zak_diags==0:
            self.err2log(u'нет заключительного диагноза')
        elif zak_diags>1:
            self.err2log(u'несколько заключительных диагнозов')
        if zak_gz<gz_max:
            self.err2log(u'у заключительного диагноза не самая высокая группа здоровья')
        if person_null:
            self.err2log(u'нет врача')
        elif no_person:
            self.err2log(u'нет кода врача')
        elif person_0:
            self.err2log(u'код врача 0')


    def checkActions(self, eventId, sex, setDate, execDate, eventTypeId, clientAge):
        selectionGroups=self.get_Action_selectionGroups(eventTypeId)
        mnogo=False
        malo=False
        for selectionGroup in selectionGroups:
            stmt='''
                select
                    ActionType.name, Action.actionType_id,
                    Action.begDate, Action.endDate,
                    EventType_Action.sex as EventType_Action_sex,
                    EventType_Action.age, EventType_Action.actuality
                from
                    Action
                    join ActionType on ActionType.id=Action.actionType_id
                    join EventType_Action on EventType_Action.actionType_id=Action.actionType_id
                where
                    Action.event_id=%d and
                    EventType_Action.eventType_id=%d and
                    EventType_Action.selectionGroup=%d
                ''' % (eventId, eventTypeId, selectionGroup)
            query=QtGui.qApp.db.query(stmt)
            act_num=0
            while query.next():
                act_num+=1
                record=query.record()
                begDate=forceDate(record.value('begDate'))
                endDate=forceDate(record.value('endDate'))
                name=forceString(record.value('name'))
                EventType_Action_sex=forceInt(record.value('EventType_Action_sex'))
                age=forceString(record.value('age'))
                actuality=forceInt(record.value('actuality'))
                if age and clientAge:
                    ageSelector = parseAgeSelector(age)
                    if not checkAgeSelector(ageSelector, clientAge):
                        self.err2log(u'исслед. '+name+u' не подходит по возрасту')
                beg=setDate.addMonths(-actuality)
                if not endDate:
                    self.err2log(u'исслед. '+name+u' без даты')
#                if begDate and begDate<beg:
#                    self.err2log(u'исслед. '+name+u' раньше начала ДД')
                if endDate and endDate>execDate:
                    self.err2log(u'исслед. '+name+u' позже окончания ДД')
                if EventType_Action_sex and EventType_Action_sex!=sex:
                    self.err2log(u'исслед. '+name+u' не подходит по полу')
            cond='eventType_id=%d and selectionGroup=%d' % (eventTypeId, selectionGroup)
            EventType_Action=QtGui.qApp.db.getRecordEx('EventType_Action', cols='sex, age', where=cond)
            if EventType_Action:
                EventType_Action_sex=forceString(EventType_Action.value('sex'))
                if EventType_Action_sex and EventType_Action_sex!=sex:
                    continue
                age=forceString(EventType_Action.value('age'))
                if age and clientAge:
                    ageSelector = parseAgeSelector(age)
                    if not checkAgeSelector(ageSelector, clientAge):
                        continue
            if selectionGroup>1:
                if act_num>1:
                    mnogo=True
                elif not act_num:
                    malo=True
            elif selectionGroup==1:
                if not act_num:
                    malo=True
            elif selectionGroup==0:
                if act_num:
                    mnogo=True
            else:
                if act_num>1:
                    mnogo=True
        if mnogo:
            self.err2log(u'лишние исслед.')
        if malo:
            self.err2log(u'не хватает исслед.')

    def exec_(self):
        global EventTypes
        params = self.getDefaultParams()
        self.setParams(params)
        QtGui.QDialog.exec_(self)
        EventTypes_str=', '.join([str(x) for x in EventTypes])
        QtGui.qApp.preferences.appPrefs['EventTypesControl'] = toVariant(EventTypes_str)
        params = self.params()
        self.saveDefaultParams(params)


    def setParams(self, params):
        self.dateEdit_1.setDate(params.get('begDateCheckEvents', QtCore.QDate.currentDate()))
        self.dateEdit_2.setDate(params.get('endDateCheckEvents', QtCore.QDate.currentDate()))
        self.checkPayed.setChecked(params.get('checkEventsPayed', False))
        self.checkExt.setChecked(params.get('checkEventsExt', False))
        self.checkSetPerson.setChecked(params.get('checkEventsSetPerson', False))
        self.checkPolis.setChecked(params.get('checkEventsPolis', False))


    def params(self):
        result = {}
        result['begDateCheckEvents'] = self.dateEdit_1.date()
        result['endDateCheckEvents'] = self.dateEdit_2.date()
        result['checkEventsPayed'] = self.checkPayed.isChecked()
        result['checkEventsExt'] = self.checkExt.isChecked()
        result['checkEventsSetPerson'] = self.checkSetPerson.isChecked()
        result['checkEventsPolis'] = self.checkPolis.isChecked()
        return result


    def getDefaultParams(self):
        result = {}
        prefs = getPref(QtGui.qApp.preferences.reportPrefs, self.__preferences, {})
        today = QtCore.QDate.currentDate()
        begYear = firstYearDay(today.addDays(-7))
        result['begDateCheckEvents']     = getPrefDate(prefs, 'begDateCheckEvents', begYear)
        result['endDateCheckEvents']     = getPrefDate(prefs, 'endDateCheckEvents', today.addDays(-1))
        result['checkEventsPayed'] = getPrefBool(prefs, 'checkEventsPayed', False)
        result['checkEventsExt'] = getPrefBool(prefs, 'checkEventsExt', False)
        result['checkEventsSetPerson'] = getPrefBool(prefs, 'checkEventsSetPerson', False)
        result['checkEventsPolis'] = getPrefBool(prefs, 'checkEventsPolis', False)
        return result


    def saveDefaultParams(self, params):
        prefs = {}
        for param, value in params.iteritems():
            setPref(prefs, param, value)
        setPref(QtGui.qApp.preferences.reportPrefs, self.__preferences, prefs)


    def openItem(self, eventId):
        eventTypeId = QtGui.qApp.db.translate('Event', 'id', eventId, 'eventType_id')
        formClass = self.getEventFormClass(eventTypeId)
        form = formClass(self)
        form.load(eventId)
        return form

    def get_EventType_Diagnostic(self, eventTypeId, specialityId):
        key=(eventTypeId, specialityId)
        info=self.diag_info.get(key, None)
        if info:
            return info
        if eventTypeId and specialityId:
            cond='eventType_id=%d AND speciality_id=%d' % (eventTypeId, specialityId)
            info = QtGui.qApp.db.getRecordEx('EventType_Diagnostic', cols='*', where=cond)
        if info:
            self.diag_info[key]=info
        return info

    def get_EventType_Action(self, eventTypeId, actionTypeId):
        key=(eventTypeId, actionTypeId)
        info=self.action_info.get(key, None)
        if info:
            return info
        if eventTypeId and actionTypeId:
            cond='eventType_id=%d AND actionType_id=%d' % (eventTypeId, actionTypeId)
            info = QtGui.qApp.db.getRecordEx('EventType_Action', cols='*', where=cond)
        if info:
            self.action_info[key]=info
        return info

    def get_Action_selectionGroups(self, eventTypeId):
        info=self.Action_selectionGroups_info.get(eventTypeId, None)
        if info:
            return info
        if eventTypeId:
            stmt='''
                select distinct selectionGroup from EventType_Action
                where eventType_id=%d
            '''% (eventTypeId)
            query=QtGui.qApp.db.query(stmt)
            groups=[]
            while query.next():
                record = query.record()
                groups.append(forceInt(record.value(0)))
            info = groups
        if info:
            self.Action_selectionGroups_info[eventTypeId]=info
        return info

    def get_Diag_selectionGroups(self, eventTypeId):
        info=self.Diag_selectionGroups_info.get(eventTypeId, None)
        if info is not None:
            return info
        info = []
        if eventTypeId:
            stmt='''
                select distinct selectionGroup from EventType_Diagnostic
                where eventType_id=%d
            '''% eventTypeId
            query=QtGui.qApp.db.query(stmt)
            while query.next():
                record = query.record()
                info.append(forceInt(record.value(0)))
        self.Diag_selectionGroups_info[eventTypeId]=info
        return info

EventTypes=[]

