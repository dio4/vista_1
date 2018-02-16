# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore, QtSql

from Events.AppointmentDialog import ShowAppointmentDialog
from Events.EditDispatcher import getEventFormClass, getEventFormClassByType
from Events.PreCreateEventDialog import CPreCreateEventDialog
from Events.Utils import checkEventPosibility, getDeathDate, getEventFinanceCode, \
    getEventTypeForm, getOutcomeDate, isEventDeath, CFinanceType, \
    getEventCode, isVisitDoctorBySetDate
from HospitalBeds.FastCreateEventDialog import CFastCreateEventDialog
from Registry.CheckEnteredOpenEventsDialog import CCheckEnteredOpenEvents
from Registry.Utils import getClientCompulsoryPolicy, getClientVoluntaryPolicy, hasSocStatus
from Users.Rights import urAdmin, urCheckPersonInFindSameEvent, urFastCreateEvent, \
    urRegTabWriteEvents
from library.AgeSelector import checkAgeSelector, parseAgeSelector
from library.LoggingModule import Logger
from library.Utils import forceDate, forceRef, forceString, calcAgeTuple, forceInt, CAgeTuple, forceBool


def requestNewEvent(widget, clientId, flagHospitalization=False, actionTypeId=None, valueProperties=None,
                    eventTypeFilterHospitalization=None, dateTime=None, personId=None, planningEventId=None,
                    diagnos=None, financeId=None, protocolQuoteId=None, actionByNewEvent=None, externalId='',
                    isAmb=True, recommendationList=None, moveEventId=None, begDate=None, endDate=None, referralId=None):
    if not valueProperties:
        valueProperties = []
    if not actionByNewEvent:
        actionByNewEvent = []
    if QtGui.qApp.userHasAnyRight([urAdmin, urRegTabWriteEvents]) and clientId:
        while True:
            eventTypeId = eventTypeFilterHospitalization if isinstance(eventTypeFilterHospitalization, int) else None
            if eventTypeId:
                orgId = QtGui.qApp.currentOrgId()
                relegateOrgId = None
                tissueTypeId = None
                personId = None
                orgStructureId = None
                eventSetDatetime = QtCore.QDateTime.currentDateTime()
                eventDatetime = None
                includeRedDays = None
                selectPreviousActions = False
                days = 0
                externalId = '' if not moveEventId else externalId
                assistantId = None
                curatorId = None

                lpuRef = None
                armyRef = None
                nosologyMKB = None

            else:
                if QtGui.qApp.userHasRight(urFastCreateEvent):
                    eventTypeFilterHospitalization = '(EventType.isAvailInFastCreateMode != 0)'
                dlg = CPreCreateEventDialog(widget, eventTypeFilterHospitalization, dateTime=dateTime, personId=personId,
                                            orgStructureId=valueProperties[0] if len(valueProperties) == 1 else None,
                                            externalId=externalId, clientId=clientId, begDate=begDate, endDate=endDate, referralId=referralId)
                if not dlg.exec_():
                    return
                if dlg.isAppointment:
                    ShowAppointmentDialog(widget, clientId)
                    return

                orgId = dlg.orgId()
                relegateOrgId = dlg.relegateOrgId()
                eventTypeId = dlg.eventTypeId()
                tissueTypeId = dlg.tissueTypeId()
                personId = dlg.personId()
                orgStructureId = dlg.orgStructureId()
                eventSetDatetime = dlg.eventSetDate()
                eventDatetime = dlg.eventDate()
                includeRedDays = dlg.includeRedDays()
                selectPreviousActions = dlg.selectPreviousActions()
                days = dlg.days()
                externalId = dlg.externalId()
                assistantId = dlg.assistantId()
                curatorId = dlg.curatorId()

                lpuRef = dlg.lpuRef()
                armyRef = dlg.armyRef()
                nosologyMKB = dlg.nosologyMKB() if hasattr(dlg, 'nosologyMKB') else None

            referrals = {}
            if lpuRef:
                referrals[0] = lpuRef
            if armyRef:
                referrals[1] = armyRef

            eventSetDate = eventSetDatetime.date() if eventSetDatetime else None
            eventDate = eventDatetime.date() if eventDatetime else None
            form = getEventTypeForm(eventTypeId)

            # В ПНД нельзя создавать обращения на выбывших пациентов. Остальным вроде как можно пока.
            if QtGui.qApp.isPNDDiagnosisMode():
                clientEndDate = getOutcomeDate(clientId)
                if clientEndDate and clientEndDate < eventSetDatetime.date():
                    box = QtGui.QMessageBox.warning(widget, u'Внимание!',
                                                    u'Создание нового обращения для этого пациента невозможно, так как он был снят с учета %s' % forceString(
                                                        clientEndDate),
                                                    QtGui.QMessageBox.Ok | QtGui.QMessageBox.Ignore,
                                                    QtGui.QMessageBox.Ok)
                    if box == QtGui.QMessageBox.Ok:
                        continue
            else:
                clientEndDate = getDeathDate(clientId)
                if clientEndDate and clientEndDate < eventDatetime.date():
                    QtGui.QMessageBox.warning(widget, u'Внимание!',
                                              u'Создание нового обращения для этого пациента невозможно, потому что есть отметка что он уже умер %s' % forceString(
                                                  clientEndDate))
                    continue

            if eventDate and eventSetDate > eventDate:
                if not confirmTrouble(widget, u'Дата окончания %s не может быть раньше даты начала %s' % (
                forceString(eventDate), forceString(eventSetDate))):
                    continue

            if not checkDatesRegardToClientLife(widget, clientId, eventSetDate, eventDate, eventTypeId):
                continue

            specEventId = isVisitDoctorBySetDate(eventSetDate, personId, clientId)
            if specEventId:
                msgBox = QtGui.QMessageBox()
                msgBox.setWindowTitle(u'Внимание!')
                msgBox.setText(
                    u'У данного врача этот пациент %s уже был на приеме.'
                    u'Для редактирования диагностических и лечебных манипуляций можете открыть существующее обращение.'
                    % forceString(eventSetDate)
                )
                msgBox.setIcon(QtGui.QMessageBox.Question)
                buttonOpen = msgBox.addButton(u'Открыть существующее обращение', QtGui.QMessageBox.AcceptRole)
                msgBox.addButton(u'Создать новое обращение', QtGui.QMessageBox.AcceptRole)
                buttonCancel = msgBox.addButton(QtGui.QMessageBox.Cancel)
                msgBox.setDefaultButton(buttonOpen)
                msgBox.exec_()

                if msgBox.clickedButton() == buttonOpen:
                    editEvent(widget, specEventId)
                    return specEventId
                if msgBox.clickedButton() == buttonCancel:
                    break
            elif not (form == '001'):
                eventId = findSameEvent(eventTypeId, personId, clientId, eventSetDate, eventDate)
                if eventId:
                    existingEventDate = forceString(
                        forceDate(QtGui.qApp.db.translate('Event', 'id', eventId, 'setDate')))
                    msgBox = QtGui.QMessageBox()
                    msgBox.setWindowTitle(u'Внимание!')
                    ignorePerson = QtGui.qApp.userHasRight(urCheckPersonInFindSameEvent)
                    # if not ignorePerson:
                    #     msgBox.setText(
                    #         u'Данный пациент %s был у Вас на приёме.\n'
                    #         u'Для редактирования диагностических и лечебных манипуляций '
                    #         u'можете открыть существующее обращение.' % (
                    #         existingEventDate))
                    # else:
                    msgBox.setText(
                        u'Данный пациент %s уже был на приёме.\n'
                        u'Для редактирования диагностических и лечебных манипуляций '
                        u'можете открыть существующее обращение.' % (
                            existingEventDate))
                    msgBox.setIcon(QtGui.QMessageBox.Question)
                    buttonOpen = msgBox.addButton(u'Открыть существующее обращение', QtGui.QMessageBox.AcceptRole)
                    msgBox.addButton(u'Создать новое обращение', QtGui.QMessageBox.AcceptRole)
                    buttonCancel = msgBox.addButton(QtGui.QMessageBox.Cancel)
                    msgBox.setDefaultButton(buttonOpen)

                    msgBox.exec_()

                    if msgBox.clickedButton() == buttonOpen:
                        editEvent(widget, eventId)
                        return eventId
                    if msgBox.clickedButton() == buttonCancel:
                        break

            btnOpenEvent, eventId = checkClientHasOpenEvents(widget, eventTypeId, clientId, eventSetDate, eventDate,
                                                             personId, form)
            if eventId and btnOpenEvent == 2:
                editEvent(widget, eventId)
                return eventId
            elif btnOpenEvent == 0:
                break
            elif btnOpenEvent == 1:
                continue
            if form == '001' or moveEventId is not None:
                canEnterEvent = True
            else:
                canEnterEvent, prevEventId = checkEventPosibility(clientId, eventTypeId, personId, eventSetDate,
                                                                  eventDate)
            if canEnterEvent:
                if (widget.checkClientAttach(personId, clientId, eventDatetime if eventDatetime else eventSetDatetime, False)
                    and (widget.checkClientAttendace(personId, clientId) or widget.confirmClientAttendace(widget, personId, clientId))
                    and (checkClientPolicyAttendace(eventTypeId, clientId, eventSetDate) or confirmClientPolicyAttendace(widget, eventTypeId, clientId))
                    and confirmClientPolicyConstraint(widget, eventTypeId, clientId, eventSetDate, eventDate)):
                    return createEvent(widget,
                                       form,
                                       clientId,
                                       eventTypeId,
                                       orgId,
                                       personId,
                                       eventDatetime,
                                       eventSetDatetime,
                                       includeRedDays,
                                       days,
                                       externalId,
                                       assistantId,
                                       curatorId,
                                       flagHospitalization,
                                       actionTypeId,
                                       valueProperties,
                                       tissueTypeId,
                                       selectPreviousActions,
                                       relegateOrgId,
                                       planningEventId,
                                       diagnos,
                                       financeId,
                                       protocolQuoteId,
                                       actionByNewEvent,
                                       referrals=referrals,
                                       nosologyMKB=nosologyMKB,
                                       isAmb=isAmb,
                                       recommendationList=recommendationList,
                                       moveEventId=moveEventId,
                                       useDiagnosticsAndActionsPresets=not bool(moveEventId),
                                       orgStructureId=orgStructureId)
                else:
                    continue
            else:
                msg = u'Новый осмотр указанного типа не может быть добавлен.'
                if prevEventId:
                    msg += u'\nОткрыть существующий?'
                boxResult = QtGui.QMessageBox.question(widget,
                                                       u'Внимание!',
                                                       msg,
                                                       QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Retry,
                                                       QtGui.QMessageBox.Yes
                                                       )
                if boxResult == QtGui.QMessageBox.Retry:
                    continue
                elif boxResult == QtGui.QMessageBox.Yes and prevEventId:
                    editEvent(widget, prevEventId)
                    return prevEventId
                else:
                    break
    return None


def confirmTrouble(widget, message):
    boxResult = QtGui.QMessageBox.question(widget,
                                           u'Внимание!',
                                           message,
                                           QtGui.QMessageBox.Ok,
                                           QtGui.QMessageBox.Ok)
    if boxResult == QtGui.QMessageBox.Ok:
        return False


def checkDatesRegardToClientLife(widget, clientId, eventSetDate, eventDate, eventTypeId):
    result = True
    if clientId:
        db = QtGui.qApp.db
        birthDate = forceDate(db.translate('Client', 'id', clientId, 'birthDate'))
        deathDate = getDeathDate(clientId)
        possibleDeathDate = birthDate.addYears(QtGui.qApp.maxLifeDuration)
        if birthDate:
            postmortem = isEventDeath(eventTypeId)
            if eventSetDate:
                result = result and (eventSetDate >= birthDate or confirmTrouble(widget, u'Дата назначения %s не должна быть раньше даты рождения пациента %s' % (forceString(eventSetDate), forceString(birthDate))))
                if deathDate:
                    result = result and (eventSetDate <= deathDate or postmortem or confirmTrouble(widget, u'Дата назначения %s не должна быть позже имеющейся даты смерти пациента %s' % (forceString(eventSetDate), forceString(deathDate))))
                else:
                    result = result and (eventSetDate <= possibleDeathDate or postmortem or confirmTrouble(widget, u'Дата назначения %s не должна быть позже возможной даты смерти пациента %s' % (forceString(eventSetDate), forceString(possibleDeathDate))))

                ageConstraint = forceString(db.translate('EventType', 'id', eventTypeId, 'age'))
                ageConstraint = parseAgeSelector(ageConstraint, isExtend=True)
                clientAge = calcAgeTuple(birthDate, eventSetDate)
                ageResult = False
                if QtGui.qApp.region() == u'91':
                    eventTypeCode = getEventCode(eventTypeId)
                    ageResult = (QtGui.qApp.region() == u'91'
                                 and eventTypeCode.lower() in [u'дв1', u'дв2']
                                 and hasSocStatus(clientId, {'specialCase': ['10', '11', '12']}))
                if not ageResult:
                    for ageSelector in ageConstraint:
                        begUnit, begCount, endUnit, endCount, step, useCalendarYear, useExclusion = ageSelector
                        checkClientAge = clientAge
                        if useCalendarYear and isinstance(checkClientAge, CAgeTuple):
                            checkClientAge = CAgeTuple((checkClientAge[0], checkClientAge[1], checkClientAge[2],
                                                        eventSetDate.year() - birthDate.year()),
                                                       birthDate,
                                                       eventSetDate)
                        ageResult = checkAgeSelector((begUnit, begCount, endUnit, endCount), checkClientAge)
                        if ageResult:
                            if step:
                                unit = begUnit if begUnit else endUnit
                                if (checkClientAge[unit - 1] - begCount) % step != 0:
                                    ageResult = False
                            if ageResult:
                                ageResult = not useExclusion
                                break

                if clientAge and ageConstraint and not ageResult:
                    result = result and confirmTrouble(widget, u'Возраст пациента не подходит для создания обращения данного типа')

            if eventDate:
                result = result and (eventDate >= birthDate or confirmTrouble(widget, u'Дата выполнения (окончания) %s не должна быть раньше даты рождения пациента %s' % (forceString(eventDate), forceString(birthDate))))
                if deathDate:
                    result = result and (eventDate <= deathDate or postmortem or confirmTrouble(widget, u'Дата выполнения (окончания) %s не должна быть позже имеющейся даты смерти пациента %s' % (forceString(eventDate), forceString(deathDate))))
                else:
                    result = result and (eventDate <= possibleDeathDate or postmortem or confirmTrouble(widget, u'Дата выполнения (окончания) %s не должна быть позже возможной даты смерти пациента %s' % (forceString(eventDate), forceString(possibleDeathDate))))
    return result


def checkEventTypeAssociations(clientId, eventTypeId, eventDate):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableEventTypeAssociations = db.table('EventTypeAssociations')
    queryTable = tableEventTypeAssociations.leftJoin(tableEvent, [
        tableEventTypeAssociations['eventType_id'].eq(tableEvent['eventType_id']), tableEvent['client_id'].eq(clientId),
        tableEvent['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableEventType,
                                      tableEventType['id'].eq(tableEventTypeAssociations['eventType_id']))
    cond = [tableEventTypeAssociations['master_id'].eq(eventTypeId),
            tableEventTypeAssociations['type'].inlist([1, 2])]
    cols = [tableEventType['name'],
            tableEventTypeAssociations['type'],
            'if(EventTypeAssociations.type = 1, Event.id, if(YEAR(Event.execDate) = YEAR(DATE(\'%s\')), Event.id, NULL)) AS id' % eventDate.toString(QtCore.Qt.ISODate)]
    recordList = db.getRecordList(queryTable, cols, cond)
    msg = None
    for record in recordList:
        type = forceInt(record.value('type'))
        eventId = forceRef(record.value('id'))
        eventTypeAssociation = forceString(record.value('name'))
        if eventId is None and type == 1:
            msg = u'Невозможно создать обращение данного типа без обращения с типом \'%s\'.' % eventTypeAssociation
        elif eventId is None and type == 2:
            msg = u'Невозможно создать обращение данного типа без обращения с типом \'%s\' в текущем году.' % eventTypeAssociation
        if msg is not None:
            res = QtGui.QMessageBox.critical(None, u'Внимание!', msg, QtGui.QMessageBox.Ok | QtGui.QMessageBox.Ignore)
            if res == QtGui.QMessageBox.Ok:
                return False
    return True


def findSameEvent(eventTypeId, personId, clientId, eventSetDate, eventDate):
    if QtGui.qApp.userHasRight(urCheckPersonInFindSameEvent):
        return None

    if clientId and eventTypeId and personId and (eventSetDate or eventDate):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tablePerson = db.table('Person')

        queryTable = tableEvent.innerJoin(tablePerson, tablePerson['id'].eq(tableEvent['execPerson_id']))
        cols = [tableEvent['id']]
        cond = [
            tableEvent['client_id'].eq(clientId),
            tableEvent['eventType_id'].eq(eventTypeId),
            tableEvent['deleted'].eq(0)
        ]
        cond.append(
            u"""
            Person.speciality_id IN (
                SELECT rbs.id
                FROM
                    Person p
                    INNER JOIN rbSpeciality rbs ON rbs.id = p.speciality_id
                WHERE
                    p.id = %s
                )
             """ % personId
        )
        if eventSetDate:
            eventSetDateTime = tableEvent['setDate'].formatValue(eventSetDate)
        else:
            eventSetDateTime = None

        if eventDate:
            eventDateTime = tableEvent['execDate'].formatValue(eventDate)
        else:
            eventDateTime = None

        if eventSetDateTime and eventDateTime:
            cond.append(
                u' (Event.execDate IS NOT NULL AND ((DATE(Event.setDate) <= DATE(%s) AND DATE(Event.execDate) >= DATE(%s)) OR (DATE(Event.setDate) >= DATE(%s) AND DATE(Event.execDate) <= DATE(%s)) OR (DATE(Event.setDate) >= DATE(%s) AND (DATE(Event.setDate) <= DATE(%s)) OR (DATE(Event.setDate) <= DATE(%s) AND (DATE(Event.execDate) <= DATE(%s) AND DATE(Event.execDate) >= DATE(%s))))) OR (Event.execDate IS NULL AND (DATE(Event.setDate) = DATE(%s) OR DATE(Event.setDate) = DATE(%s) OR (DATE(%s) <= DATE(Event.setDate) AND DATE(Event.setDate) <= DATE(%s)))))' % (
                eventSetDateTime, eventDateTime, eventSetDateTime, eventDateTime, eventSetDateTime, eventDateTime,
                eventSetDateTime, eventDateTime, eventSetDateTime, eventSetDateTime, eventDateTime, eventSetDateTime,
                eventDateTime))
        elif eventSetDateTime:
            cond.append(
                u' ((Event.execDate IS NULL AND DATE(Event.setDate) <= DATE(%s)) OR (Event.execDate IS NOT NULL AND (DATE(Event.setDate) <= DATE(%s) AND DATE(Event.execDate) >= DATE(%s))))' % (
                eventSetDateTime, eventSetDateTime, eventSetDateTime))
        elif eventDateTime:
            cond.append(
                u' ((Event.execDate IS NULL AND DATE(Event.setDate) = DATE(%s)) OR (Event.execDate IS NOT NULL AND (DATE(Event.setDate) <= DATE(%s) AND DATE(Event.execDate) >= DATE(%s))))' % (
                eventDateTime, eventDateTime, eventDateTime))
        recordList = db.getRecordList(queryTable, cols, cond, 'Event.setDate')
        if recordList:
            record = recordList[-1]
            eventId = forceRef(record.value('id'))
            return eventId
    return None


def checkClientHasOpenEvents(widget, eventTypeId, clientId, eventSetDate, eventDate, personId, form):
    result = (3, None)
    if QtGui.qApp.userHasRight(urFastCreateEvent):
        return result
    if not checkEventTypeAssociations(clientId, eventTypeId, eventSetDate):
        return (1, None)
    if clientId and eventTypeId and (eventSetDate or eventDate):
        db = QtGui.qApp.db
        recordList = []
        tableEvent = db.table('Event')
        tableEventType = db.table('EventType')
        tableEventTypeAssociations = db.table('EventTypeAssociations')
        tableAction = db.table('Action')
        table = tableEvent.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
        table = table.leftJoin(tableEventTypeAssociations,
                               [tableEventTypeAssociations['eventType_id'].eq(tableEventType['id']),
                                tableEventTypeAssociations['master_id'].eq(eventTypeId),
                                tableEventTypeAssociations['type'].inlist([0, 3]), ])
        table = table.leftJoin(tableAction,
                               [tableAction['event_id'].eq(tableEvent['id']),
                                '''Action.actionType_id IN (SELECT id FROM ActionType WHERE ActionType.flatCode = 'leaved' AND ActionType.deleted = 0)''',
                                tableAction['deleted'].eq(0)])
        cols = [tableEvent['id'],
                tableEventTypeAssociations['type'],
                tableEventTypeAssociations['id'].alias('eventTypeAssociationId'),
                tableAction['id'].alias('leavedActionId')]
        cond = [tableEvent['client_id'].eq(clientId),
                tableEvent['deleted'].eq(0),
                tableEventType['purpose_id'].gt(1)]
        if form == '001':
            cond.append(tableEventType['form'].eq(form))
            cond001 = [tableEvent['execDate'].isNull()]
            if eventDate and eventDate.isValid():
                cond001.append(db.joinAnd([tableEvent['execDate'].eq(eventDate),
                                           tableEvent['execPerson_id'].eq(personId)]))
            cond.append(db.joinOr(cond001))
        else:
            cond.append(tableEvent['execDate'].isNull())
        query = db.query(db.selectStmt(table, cols, cond, 'Event.setDate'))
        while query.next():
            record = query.record()
            type = forceInt(record.value('type'))
            eventTypeAssociationId = forceRef(record.value('eventTypeAssociationId'))
            if (eventTypeAssociationId and type == 0) or (
                    eventTypeAssociationId and not forceRef(record.value('leavedActionId')) and type == 3):
                QtGui.QMessageBox.critical(None, u'Внимание!',
                                           u'Невозможно создать обращение данного типа в период действия ранее открытого обращения.',
                                           QtGui.QMessageBox.Ok)
                return (1, None)
            recordList.append(forceRef(record.value('id')))
        if recordList:
            dialog = CCheckEnteredOpenEvents(widget, recordList, clientId)
            dialog.exec_()
            result = (dialog.btnResult, dialog.resultEventId)
    return result


def checkClientPolicyAttendace(eventTypeId, clientId, date=None):
    financeCode = getEventFinanceCode(eventTypeId)
    if financeCode == CFinanceType.CMI:
        return bool(getClientCompulsoryPolicy(clientId, date))
    elif financeCode == CFinanceType.VMI:
        return bool(getClientVoluntaryPolicy(clientId, date))
    else:
        return True


def confirmClientPolicyAttendace(widget, eventTypeId, clientId):
    checkPolicyPref = QtGui.qApp.getGlobalPreference('4')

    if checkPolicyPref == u'2' or checkPolicyPref == u'Да':  # строгий контроль
        message = u'Пациент не имеет полиса, требуемого для данного типа обращения.\nРегистрация обращения запрещена.'
        QtGui.QMessageBox.critical(widget, u'Внимание!', message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        return False
    elif checkPolicyPref == u'1' or checkPolicyPref == u'Нет':
        message = u'Пациент не имеет полиса, требуемого для данного типа обращения.\nЭто может привести к затруднениям оплаты обращения.\nВсё равно продолжить?'
        return QtGui.QMessageBox.critical(widget,
                                          u'Внимание!',
                                          message,
                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                          QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes
    else:
        return True


def confirmClientPolicyConstraint(widget, eventTypeId, clientId, eventSetDate, eventDate):
    if not eventTypeId:
        QtGui.QMessageBox.warning(widget,
                                  u'Внимание!',
                                  u'Не указан указан тип (цель) события.',
                                  QtGui.QMessageBox.Ok)
        return False
    db = QtGui.qApp.db
    stmt = u'''SELECT rbFinance.code
FROM rbFinance INNER JOIN EventType ON EventType.finance_id = rbFinance.id
WHERE EventType.id = %d AND EventType.deleted = 0''' % eventTypeId
    query = QtSql.QSqlQuery(db.db)
    query.exec_(stmt)

    eventSetDate = eventSetDate if eventSetDate and eventSetDate.isValid() else QtCore.QDate.currentDate()

    eventDate = eventDate if eventDate and eventDate.isValid() else eventSetDate

    if query.next():
        record = query.record()
        financeCode = forceString(record.value('code'))
        policyRecordGetter = None

        if u'2' in financeCode.lower():
            policyRecordGetter = getClientCompulsoryPolicy
        elif u'3' in financeCode.lower():
            policyRecordGetter = getClientVoluntaryPolicy

        if policyRecordGetter:
            policyRecord = policyRecordGetter(clientId, eventDate)
            if not policyRecord:
                policyRecord = policyRecordGetter(clientId)
            if policyRecord:
                policyBegDate = forceDate(policyRecord.value('begDate'))
                policyEndDate = forceDate(policyRecord.value('endDate'))
                validPolicy = not policyBegDate.isValid() or policyBegDate <= eventDate
                validPolicy = validPolicy and (not policyEndDate.isValid() or policyEndDate >= eventDate)
                if not validPolicy:
                    if not confirmPolicyAvailable(widget, u'Полис пациента не действителен по дате!'):
                        return False

    # i4226: Жесткий контроль ввода событий для пациента,
    # чей полис принадлежит страховой компании с приостановленным обслуживанием
    compPolicyRecord = getClientCompulsoryPolicy(clientId, eventDate)
    volunPolicyRecord = getClientVoluntaryPolicy(clientId, eventDate)

    if compPolicyRecord:
        compulsoryServiceStop = forceBool(compPolicyRecord.value('compulsoryServiceStop'))
        compulsoryServiceStopIgnore = forceBool(
            db.translate('EventType', 'id', eventTypeId, 'compulsoryServiceStopIgnore')
        )
    else:
        compulsoryServiceStop = False
        compulsoryServiceStopIgnore = False

    if volunPolicyRecord:
        voluntaryServiceStop = forceBool(volunPolicyRecord.value('voluntaryServiceStop'))
        voluntaryServiceStopIgnore = forceBool(
            db.translate('EventType', 'id', eventTypeId, 'voluntaryServiceStopIgnore')
        )
    else:
        voluntaryServiceStop = False
        voluntaryServiceStopIgnore = False

    if (compulsoryServiceStop and not compulsoryServiceStopIgnore) \
            or (voluntaryServiceStop and not voluntaryServiceStopIgnore):
        if compulsoryServiceStop:
            policyType = u'ОМС '
        elif voluntaryServiceStop:
            policyType = u'ДМС '
        else:
            policyType = u''
        message = u"По данной СМО приостановлено обслуживание {policyType}полисов.\n" \
                  u"Это может привести к затруднениям оплаты обращения.".format(policyType=policyType)
        # return confirmPolicyAvailable(widget, message)
        QtGui.QMessageBox.critical(widget, u'Внимание!', message, QtGui.QMessageBox.Ok)
        return False
    return True


def confirmPolicyAvailable(widget, message):
    checkPolicyPref = QtGui.qApp.getGlobalPreference('4')
    if checkPolicyPref == u'2' or checkPolicyPref == u'да':  # строгий контроль
        default = buttons = QtGui.QMessageBox.Ok
        messageBox = QtGui.QMessageBox.critical
    elif checkPolicyPref == u'1' or checkPolicyPref == u'нет':  # предупреждение
        buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
        default = QtGui.QMessageBox.Yes
        message = '\n'.join([message, u'Все равно продолжить?'])
        messageBox = QtGui.QMessageBox.question
    else:  # Не проверять
        return True
    result = messageBox(widget,
                        u'Внимание!',
                        message,
                        buttons,
                        default) == QtGui.QMessageBox.Yes
    return result


def createEvent(widget, form, clientId, eventTypeId, orgId, personId, eventDate, eventSetDate, includeRedDays, numDays,
                externalId, assistantId, curatorId, flagHospitalization=False, actionTypeId=None, valueProperties=None,
                tissueTypeId=None, selectPreviousActions=False, relegateOrgId=None, planningEventId=None, diagnos=None,
                financeId=None, protocolQuoteId=None, actionByNewEvent=None, referrals=None, nosologyMKB=None, isAmb=True,
                recommendationList=None, moveEventId=None, useDiagnosticsAndActionsPresets=True, orgStructureId=None):
    if not actionByNewEvent:
        actionByNewEvent = []
    if not referrals:
        referrals = {}
    if QtGui.qApp.userHasRight(urFastCreateEvent):
        formClass = CFastCreateEventDialog
    else:
        formClass = getEventFormClassByType(eventTypeId)
    dialog = formClass(widget)
    if dialog.prepare(clientId,
                      eventTypeId,
                      orgId,
                      personId,
                      eventSetDate,
                      eventDate,
                      includeRedDays,
                      numDays,
                      externalId,
                      assistantId,
                      curatorId,
                      flagHospitalization,
                      actionTypeId,
                      valueProperties,
                      tissueTypeId,
                      selectPreviousActions,
                      relegateOrgId,
                      diagnos,
                      financeId,
                      protocolQuoteId,
                      actionByNewEvent,
                      referrals,
                      isAmb,
                      recommendationList,
                      useDiagnosticsAndActionsPresets=useDiagnosticsAndActionsPresets,
                      orgStructureId=orgStructureId):
        if isinstance(nosologyMKB, basestring):
            dialog.addNosologyInfo(nosologyMKB)
        if hasattr(dialog, 'getEventDataPlanning'):
            dialog.getEventDataPlanning(planningEventId)
        dialog.appendActionTypesByMes()

        if moveEventId is not None:
            dialog.moveInformationFromAnotherEvent(moveEventId)
        if dialog.exec_():
            updateEventListAfterEdit(dialog.itemId())
            return dialog.itemId()
    return None


def editEvent(widget, eventId):
    formClass = getEventFormClass(eventId)
    dialog = formClass(widget)
    Logger.updateEvent(eventId)
    try:
        dialog.load(eventId)
        if dialog.exec_():
            updateEventListAfterEdit(eventId)
            return dialog.itemId()
        if 'on_buttonBoxEvent_apply' in dir(widget):
            widget.on_buttonBoxEvent_apply()
        return None
    finally:
        pass
        # dialog.destroy()
        # sip.delete(dialog)
        # del dialog


def updateEventListAfterEdit(eventId):
    if QtGui.qApp.mainWindow.registry:
        QtGui.qApp.mainWindow.registry.updateEventListAfterEdit(eventId)
    if QtGui.qApp.mainWindow.dockOpenedEvents:
        QtGui.qApp.mainWindow.dockOpenedEvents.content.updateList()
