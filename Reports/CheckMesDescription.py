#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.Utils       import getEventLengthDays
from library.MES.Model  import parseModel
from library.Utils      import forceDate, forceDouble, forceInt, forceRef, forceString, formatNum
from Registry.Utils     import getClientInfoEx
from Reports.ReportBase import createTable, CReportBase
from Reports.ReportView import CReportViewDialog


def showCheckMesDescription(parent, mesId):
    if parent.eventEditor is not None:
        view = CReportViewDialog(parent)
        view.setWindowTitle(u'ПРОТОКОЛ')
        view.setText(getMesDescription(parent, mesId))
        view.showMaximized()
        view.exec_()


def getMesDescription(parent, mesId):
    doc = QtGui.QTextDocument()
    cursor = QtGui.QTextCursor(doc)

    insertMainSection(parent, cursor, mesId)
    cursor.insertBlock()
    cursor.insertBlock()

    if hasattr(parent.eventEditor, 'modelFinalDiagnostics'):
        insertMKBSection(parent, cursor, mesId)
        cursor.insertBlock()
        cursor.insertBlock()
    if hasattr(parent.eventEditor, 'modelVisits'):
        insertPersonServicesSection(parent, cursor, mesId)
    actionMesIdList = set()
    actionTypeMesIdList = set()
    actionMesIdList, actionTypeMesIdList = insertServiceSection(parent, cursor, mesId, u'Услуги лечащего врача', u'в', actionMesIdList, actionTypeMesIdList)
    actionMesIdList, actionTypeMesIdList = insertServiceSection(parent, cursor, mesId, u'Лабораторные диагностические услуги', u'к', actionMesIdList, actionTypeMesIdList)
    actionMesIdList, actionTypeMesIdList = insertServiceSection(parent, cursor, mesId, u'Инструментальные диагностические услуги', u'д', actionMesIdList, actionTypeMesIdList)
    actionMesIdList, actionTypeMesIdList = insertServiceSection(parent, cursor, mesId, u'Немедикаментозная терапия', u'л', actionMesIdList, actionTypeMesIdList)
    actionMesIdList, actionTypeMesIdList = insertServiceSection(parent, cursor, mesId, u'Вспомогательные услуги', u'с', actionMesIdList, actionTypeMesIdList)
    actionMesIdList, actionTypeMesIdList = insertServiceSection(parent, cursor, mesId, u'Услуги по экспертизе', u'э', actionMesIdList, actionTypeMesIdList)
    insertServiceNoSection(parent, cursor, actionMesIdList, actionTypeMesIdList)
    insertMedicamentsSection(cursor, mesId)
    return doc


def insertMainSection(parent, cursor, mesId):
    db = QtGui.qApp.db
    mesRecord = db.getRecord('mes.MES', '*', mesId)
    eventSetDateTime = parent.eventEditor.eventSetDateTime
    eventDate = parent.eventEditor.eventDate
    begDateEvent = eventSetDateTime if isinstance(eventSetDateTime, QtCore.QDateTime) else (QtCore.QDateTime(eventSetDateTime) if eventDate  else QtCore.QDateTime())
    endDateEvent = eventDate if isinstance(eventDate, QtCore.QDateTime) else (QtCore.QDateTime(eventDate) if eventDate  else QtCore.QDateTime())
    currentDateTime = QtCore.QDateTime.currentDateTime()
    if endDateEvent.isNull():
        endDateEvent = currentDateTime

    bigChars = QtGui.QTextCharFormat()
    bigChars.setProperty(QtGui.QTextFormat.FontSizeIncrement, QtCore.QVariant(2))
    bigChars.setFontWeight(QtGui.QFont.Bold)
    boldChars = QtGui.QTextCharFormat()
    boldChars.setFontWeight(QtGui.QFont.Bold)

    cursor.setCharFormat(bigChars)
    titleInfo = parent.eventEditor.eventTypeName
    if eventDate:
        titleInfo += u' с %s по %s'%(forceString(begDateEvent.date()), forceString(eventDate))
    else:
        titleInfo += u' от %s'%(forceString(begDateEvent))
    cursor.insertText(u'Протокол контроля выполнения случая обслуживания %s'%(titleInfo))
    cursor.insertBlock()
    cursor.setCharFormat(QtGui.QTextCharFormat())

    columns = [
            ('30%',[], CReportBase.AlignLeft),
            ('60%',[], CReportBase.AlignLeft),
            ]

    table = createTable(cursor, columns, headerRowCount=0, border=0, cellPadding=2, cellSpacing=0)

    i = table.addRow()
    personId = parent.eventEditor.personId
    personInfo = forceString(QtGui.qApp.db.translate('vrbPersonWithSpeciality', 'id', personId, 'name')) if personId else u''
    table.setText(i, 0, u'Ответственный', charFormat=boldChars)
    table.setText(i, 1, personInfo, charFormat=boldChars)
    i = table.addRow()
    clientId = parent.eventEditor.clientId
    if clientId:
        clientInfo = getClientInfoEx(clientId, endDateEvent.date() if endDateEvent else None)
        clientText = u'%(fullName)s, %(birthDate)s (%(age)s), %(sex)s, СНИЛС: %(SNILS)s\n' \
                     u'документ %(document)s, полис %(policy)s\n' \
                     u'адр.рег. %(regAddress)s\n' \
                     u'адр.прож. %(locAddress)s\n' \
                     u'%(phones)s' % clientInfo
    else:
        clientText = u''
    table.setText(i, 0, u'Пациент', charFormat=boldChars)
    table.setText(i, 1, clientText, charFormat=boldChars)
    i = table.addRow()
    table.setText(i, 0, forceString(mesRecord.value('code')), charFormat=boldChars)
    table.setText(i, 1, forceString(mesRecord.value('name')), charFormat=boldChars)
    i = table.addRow()
    table.setText(i, 0, u'Описание')
    table.setText(i, 1, forceString(mesRecord.value('descr')))
    i = table.addRow()
    table.setText(i, 0, u'Минимальная длительность')
    minDuration = forceInt(mesRecord.value('minDuration'))
    table.setText(i, 1, minDuration)
    i = table.addRow()
    table.setText(i, 0, u'Максимальная длительность')
    maxDuration = forceInt(mesRecord.value('maxDuration'))
    table.setText(i, 1, maxDuration)
    i = table.addRow()
    table.setText(i, 0, u'Средняя длительность')
    mesAvgDuration = forceInt(mesRecord.value('avgDuration'))
    startDate = begDateEvent.date() if begDateEvent else QtCore.QDate.currentDate()
    stopDate = endDateEvent.date() if endDateEvent else QtCore.QDate.currentDate()
    avgDurationDay = getEventLengthDays(startDate, stopDate, True, parent.eventEditor.eventTypeId)
    if avgDurationDay != mesAvgDuration:
        brushColor = QtCore.Qt.red
    else:
        brushColor = QtCore.Qt.green
    avgDuration = formatNum(avgDurationDay, (u'день', u'дня', u'дней'))
    if not eventDate:
        avgDuration += u'   на текущую дату: ' + forceString(currentDateTime.date())
    table.setText(i, 1, u'норма: %d   реальная длительность: %s'%(mesAvgDuration, avgDuration), boldChars, None, brushColor, True)
    if hasattr(parent.eventEditor, 'modelVisits'):
        i = table.addRow()
        table.setText(i, 0, u'Норматив визитов')
        KSGNorm = forceInt(mesRecord.value('KSGNorm')) #FIXME: возможно нужен double
        mesVisitType = {}
        visitTypeList = {}
        visitTypeIdList = []
        mesVisitResult = {}
        personIdList = []
        groupAvailable = {}
        if hasattr(parent.eventEditor, 'modelVisits'):
            for row, record in enumerate(parent.eventEditor.modelVisits.items()):
                visitTypeId = forceRef(record.value('visitType_id'))
                personId = forceRef(record.value('person_id'))
                if visitTypeId and personId:
                    specialityId = forceRef(db.translate('Person', 'id', personId, 'speciality_id'))
                    countVisitTypeId = visitTypeList.get((visitTypeId, specialityId), 0)
                    visitTypeList[(visitTypeId, specialityId)] = countVisitTypeId + 1
                    if personId not in personIdList:
                        personIdList.append(personId)
                    if visitTypeId not in visitTypeIdList:
                        visitTypeIdList.append(visitTypeId)
        if visitTypeIdList and personIdList:
            mesVisitResult, groupAvailable, mesVisitType = getMesAmountVisitType(visitTypeIdList, visitTypeList, mesId, personIdList, groupAvailable, mesVisitResult)
        countVisitType = 0
        for key, item in mesVisitType.items():
            countVisitType += item
        countVisitTypeAll = 0
        for key, item in visitTypeList.items():
            countVisitTypeAll += item
        if (not countVisitType and countVisitTypeAll != KSGNorm) or (countVisitType and (countVisitType != KSGNorm or countVisitTypeAll != countVisitType)):
            brushColor = QtCore.Qt.red
        else:
            brushColor = QtCore.Qt.green
        visitsCount = u'норма: %d'%(KSGNorm) + u'   визитов по требованию: %d'%(countVisitType) + u'   визитов всего: %d'%(countVisitTypeAll)
        table.setText(i, 1, visitsCount, boldChars, None, brushColor, True)
    cursor.movePosition(QtGui.QTextCursor.End)


def insertMKBSection(parent, cursor, mesId):
    boldChars = QtGui.QTextCharFormat()
    boldChars.setFontWeight(QtGui.QFont.Bold)
    db = QtGui.qApp.db
    cursor.insertText(u'Заболевания, входящие в МЭС (в формулировках МКБ)')
    cursor.insertBlock()
    cursor.setCharFormat(QtGui.QTextCharFormat())

    tableColumns = [
            ('5%',[u'№' ], CReportBase.AlignRight),
            ('15%',[u'Код диагноза по МКБ' ], CReportBase.AlignLeft),
            ('80%',[u'Диагноз' ],             CReportBase.AlignLeft),
            ]

    table = createTable(cursor, tableColumns)
    tableMKB = db.table('mes.MES_mkb')
    model = parent.eventEditor.modelFinalDiagnostics
    finalDiagnostic = False
    for row, record in enumerate(model.items()):
        if  forceInt(record.value('diagnosisType_id')) == model.diagnosisTypeCol.ids[0]:
            MKB = forceString(record.value('MKB'))
            if MKB:
                finalDiagnostic = True
                recordMES = db.getRecordEx(tableMKB, 'mkb', [tableMKB['master_id'].eq(mesId), tableMKB['deleted'].eq(0), tableMKB['mkb'].like(MKB)])
                mesMKB = forceString(recordMES.value('mkb')) if recordMES else u''
                if mesMKB:
                    MKB = mesMKB
                    brushColor = QtCore.Qt.green
                else:
                    brushColor = QtCore.Qt.red
                diagName = forceString(db.translate('MKB_Tree', 'DiagID', MKB, 'DiagName'))
                i = table.addRow()
                table.setText(i, 0, i, boldChars, None, brushColor, True)
                table.setText(i, 1, MKB, boldChars, None, brushColor, True)
                table.setText(i, 2, diagName, boldChars, None, brushColor, True)
    if not finalDiagnostic:
        i = table.addRow()
        table.setText(i, 0, i, boldChars, None, QtCore.Qt.red, True)
        table.setText(i, 1, u'', boldChars, None, QtCore.Qt.red, True)
        table.setText(i, 2, u'Нет заключительного диагноза', boldChars, None, QtCore.Qt.red, True)
    cursor.movePosition(QtGui.QTextCursor.End)


def getMesAmountVisitType(visitTypeIdList, visitTypeList, mesId, personIdList, groupAvailable, mesVisitResult):
    countedVisits = {}
    if personIdList and mesId:
        db = QtGui.qApp.db
        stmt = u'''
            SELECT
            mMV.groupCode  AS prvsGroup,
            mMV.averageQnt AS averageQnt,
            mMV.id AS mesVisitId,
            rbVisitType.id AS visitTypeId,
            Person.speciality_id,
            IF(mMV.visitType_id=mVT.id, 0, 1) AS visitTypeErr
            FROM Person
            LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
            JOIN rbVisitType
            LEFT JOIN mes.mrbVisitType  AS mVT  ON rbVisitType.code = mVT.code
            LEFT JOIN mes.mrbSpeciality AS mS   ON mS.regionalCode = rbSpeciality.regionalCode
            LEFT JOIN mes.MES_visit     AS mMV  ON mMV.speciality_id = mS.id
            WHERE Person.id IN (%s) AND mMV.deleted = 0 AND mS.deleted = 0 AND mVT.deleted = 0 AND rbVisitType.id IN (%s) AND mMV.master_id = %d
            ORDER BY mMV.groupCode
        ''' % (u','.join(str(personId) for personId in personIdList if personId), u','.join(str(visitTypeId) for visitTypeId in visitTypeIdList if visitTypeId), mesId)

        query = db.query(stmt)
        while query.next():
            record = query.record()
            visitTypeId = forceRef(record.value('visitTypeId'))
            specialityId = forceRef(record.value('speciality_id'))
            visitTypeError = forceInt(record.value('visitTypeErr'))
            if not visitTypeError and visitTypeId and not (countedVisits.get((visitTypeId, specialityId), 0)):
                prvsGroup = forceInt(record.value('prvsGroup'))
                averageQnt = forceInt(record.value('averageQnt'))
                mesVisitId = forceRef(record.value('mesVisitId'))
                available = groupAvailable.get(prvsGroup, averageQnt)
                countVisitTypeId = visitTypeList.get((visitTypeId, specialityId), 0)
                visitIdCount = mesVisitResult.get(mesVisitId, 0)
                groupAvailable[prvsGroup] = available - countVisitTypeId
                countedVisits[(visitTypeId, specialityId)] = visitIdCount + countVisitTypeId
                mesVisitResult[mesVisitId] = visitIdCount + countVisitTypeId
    return mesVisitResult, groupAvailable, countedVisits


def insertPersonServicesSection(parent, cursor, mesId):
    db = QtGui.qApp.db
    cursor.insertText(u'Услуги лечащего и консультирующего врача (ВИЗИТЫ)')
    cursor.insertBlock()

    tableColumns = [
            ('5%',[u'№ группы' ],       CReportBase.AlignRight),
            ('10%',[u'Количество' ],    CReportBase.AlignRight),
            ('10%',[u'Контроль' ],      CReportBase.AlignRight),
            ('40%',[u'Тип визита' ],    CReportBase.AlignLeft),
            ('35%',[u'Специальность' ], CReportBase.AlignLeft),
            ]

    visitTypeIdList = []
    personIdList = []
    visitTypeList = {}
    mesVisitResult = {}
    groupAvailable = {}
    countedVisitType = []
    for row, record in enumerate(parent.eventEditor.modelVisits.items()):
        visitTypeId = forceRef(record.value('visitType_id'))
        personId = forceRef(record.value('person_id'))
        if visitTypeId and personId:
            specialityId = forceRef(db.translate('Person', 'id', personId, 'speciality_id'))
            countVisitTypeId = visitTypeList.get((visitTypeId, specialityId), 0)
            visitTypeList[(visitTypeId, specialityId)] = countVisitTypeId + 1
            if personId not in personIdList:
                personIdList.append(personId)
            if visitTypeId not in visitTypeIdList:
                visitTypeIdList.append(visitTypeId)
    if visitTypeIdList and personIdList:
        mesVisitResult, groupAvailable, countedVisitType = getMesAmountVisitType(visitTypeIdList, visitTypeList, mesId, personIdList, groupAvailable, mesVisitResult)

    table = createTable(cursor, tableColumns)
    tableVisit = db.table('mes.MES_visit')
    tableVisitType  = db.table('mes.mrbVisitType')
    tableSpeciality = db.table('mes.mrbSpeciality')
    tableQuery = tableVisit.leftJoin(tableVisitType,  tableVisitType['id'].eq(tableVisit['visitType_id']))
    tableQuery = tableQuery.leftJoin(tableSpeciality, tableSpeciality['id'].eq(tableVisit['speciality_id']))
    cols = [tableVisit['groupCode'], tableVisit['averageQnt'], tableVisitType['name'], tableSpeciality['name'], tableVisit['id'].alias('mesVisitId') ]
    prevGroupCode = False
    if mesId:
        mesRecordKSGNorm = db.getRecordEx('mes.MES', 'KSGNorm', 'id = %d AND deleted = 0'%(mesId))
        if not mesRecordKSGNorm:
            raise Exception(u'mes с указанный id удалён или не существует')
        KSGNorm = forceDouble(mesRecordKSGNorm.value('KSGNorm'))
    else:
        KSGNorm = 0
    for record in db.getRecordList(tableQuery, cols, [tableVisit['master_id'].eq(mesId), tableVisit['deleted'].eq(0), tableVisitType['deleted'].eq(0), tableSpeciality['deleted'].eq(0)], 'groupCode, '+tableSpeciality['name'].name()):
        i = table.addRow()
        groupCode  = forceString(record.value(0))
        averageQnt = forceInt(record.value(1))
        visitType  = forceString(record.value(2))
        speciality = forceString(record.value(3))
        mesVisitId = forceRef(record.value(4))
        if prevGroupCode != groupCode:
            table.setText(i, 0, groupCode)
            prevGroupCode = groupCode
        table.setText(i, 1, averageQnt)
        brusColor = QtCore.Qt.red
        visitIdCount = 0
        if mesVisitResult and groupAvailable:
            prvsGroup = forceInt(record.value(0))
            available = groupAvailable.get(prvsGroup, averageQnt)
            visitIdCount = mesVisitResult.get(mesVisitId, 0)
            if available == 0:
                brusColor = QtCore.Qt.green
        table.setText(i, 2, visitIdCount, None, None, brusColor)
        table.setText(i, 3, visitType)
        table.setText(i, 4, speciality)
    if len(visitTypeList) > len(countedVisitType):
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'Услуги лечащего и консультирующего врача выходящие за пределы требования (ВИЗИТЫ)')
        cursor.insertBlock()

        tableColumns = [
                ('5%',[u'№' ], CReportBase.AlignRight),
                ('15%',[u'Количество' ],    CReportBase.AlignRight),
                ('40%',[u'Тип визита' ],    CReportBase.AlignLeft),
                ('40%',[u'Специальность' ], CReportBase.AlignLeft),
                ]
        table = createTable(cursor, tableColumns)
        visitNoMESList = {}
        visitDistinctIdList = {}
        tableSpeciality = db.table('rbSpeciality')
        tableVisitType = db.table('rbVisitType')
        for visitTypeId, specialityId in visitTypeList.keys():
            if not countedVisitType.get((visitTypeId, specialityId), 0):
                recordSpeciality = db.getRecordEx(tableSpeciality, 'rbSpeciality.name AS nameSpeciality, rbSpeciality.id AS specialityId', [tableSpeciality['id'].eq(specialityId)])
                recordVisitType = db.getRecordEx(tableVisitType, 'rbVisitType.id, rbVisitType.name AS nameVisitType', [tableVisitType['id'].eq(visitTypeId)])
                if recordVisitType:
                    visitTypeId  = forceRef(recordVisitType.value('id'))
                    if recordSpeciality:
                        specialityId = forceRef(recordSpeciality.value('specialityId'))
                        nameSpeciality = forceString(recordSpeciality.value('nameSpeciality'))
                    else:
                        specialityId = None
                        nameSpeciality = u''
                    if visitTypeId and not (visitDistinctIdList.get((visitTypeId, specialityId), 0)) and not countedVisitType.get((visitTypeId, specialityId), 0):
                        visitDistinctIdList[(visitTypeId, specialityId)] = 1
                        nameVisitType  = forceString(recordVisitType.value('nameVisitType'))
                        visitNoMES = visitNoMESList.get((visitTypeId, specialityId), None)
                        countVisitTypeId = visitTypeList.get((visitTypeId, specialityId), 0)
                        if visitNoMES:
                            visitNoMESList[(visitTypeId, specialityId)] = (visitNoMES[0] + countVisitTypeId, nameVisitType, nameSpeciality)
                        else:
                            visitNoMESList[(visitTypeId, specialityId)] = (countVisitTypeId, nameVisitType, nameSpeciality)
        for key, item in visitNoMESList.items():
            i = table.addRow()
            table.setText(i, 0, i, None, None, QtCore.Qt.red if KSGNorm <= 0 else QtCore.Qt.green)
            table.setText(i, 1, item[0], None, None, QtCore.Qt.red if KSGNorm <= 0 else QtCore.Qt.green)
            table.setText(i, 2, item[1], None, None, QtCore.Qt.red if KSGNorm <= 0 else QtCore.Qt.green)
            table.setText(i, 3, item[2], None, None, QtCore.Qt.red if KSGNorm <= 0 else QtCore.Qt.green)
            KSGNorm -= item[0]


def getMesAmountActionType(actionTypeIdList, mesId, groupId, actionTypeMesIdList, mesActionResult, mesActionAmount):
    result = 0
    db = QtGui.qApp.db
    stmt = u'''
        SELECT
        mMV.id AS mesActionId,
        ActionType.id AS actionTypeId,
        ActionType.amount
        FROM ActionType
        INNER JOIN rbService  ON rbService.id = ActionType.nomenclativeService_id
        INNER JOIN mes.mrbService  AS mSV ON rbService.code = mSV.code
        INNER JOIN mes.MES_service AS mMV ON mMV.service_id = mSV.id
        WHERE ActionType.deleted = 0 AND mMV.deleted = 0 AND mSV.deleted = 0 AND ActionType.id IN (%s) AND mMV.master_id = %d AND mSV.group_id = %d
        ORDER BY mSV.code, mSV.name, mSV.id
    ''' % (u','.join(str(actionTypeId) for actionTypeId in actionTypeIdList.keys() if actionTypeId), mesId, groupId)

    query = db.query(stmt)
    while query.next():
        record = query.record()
        actionTypeId = forceRef(record.value('actionTypeId'))
        if actionTypeId and (actionTypeId not in actionTypeMesIdList):
            mesActionId = forceRef(record.value('mesActionId'))
            amount = forceInt(record.value('amount'))
            if mesActionId:
                amountCount, amountCountExecuted = mesActionAmount.get(mesActionId, (0, 0))
                actionIdCount = mesActionResult.get(mesActionId, 0)
                countActionTypeId, actionTypeIdExecuted = actionTypeIdList.get(actionTypeId, (0, 0))
                actionTypeMesIdList.add(actionTypeId)
                mesActionAmount[mesActionId] = (amountCount + (amount * countActionTypeId), amountCountExecuted + (amount * actionTypeIdExecuted))
                mesActionResult[mesActionId] = actionIdCount + countActionTypeId
    return mesActionResult, mesActionAmount, actionTypeMesIdList


def getMesAmountActionTypeAlternative(actionTypeIdList, mesId, groupId, actionTypeMesIdList, mesActionResult, mesActionAmount):
    result = 0
    db = QtGui.qApp.db
    stmt = u'''
        SELECT
        mMV.id AS mesActionId,
        mMV.groupCode AS groupAlternative,
        ActionType.id AS actionTypeId,
        ActionType.amount
        FROM ActionType
        INNER JOIN rbService  ON rbService.id = ActionType.nomenclativeService_id
        INNER JOIN mes.mrbService  AS mSV ON rbService.code = mSV.code
        INNER JOIN mes.MES_service AS mMV ON mMV.service_id = mSV.id
        WHERE ActionType.deleted = 0 AND mMV.deleted = 0 AND mSV.deleted = 0 AND ActionType.id IN (%s) AND mMV.master_id = %d AND mSV.group_id = %d
        GROUP BY mSV.code
        ORDER BY groupAlternative, mSV.code, mSV.name, mSV.id
    ''' % (u','.join(str(actionTypeId) for actionTypeId in actionTypeIdList.keys() if actionTypeId), mesId, groupId)

    query = db.query(stmt)
    groupAlternativeList = {}
    while query.next():
        record = query.record()
        actionTypeId = forceRef(record.value('actionTypeId'))
        if actionTypeId and (actionTypeId not in actionTypeMesIdList):
            mesActionId = forceRef(record.value('mesActionId'))
            amount = forceInt(record.value('amount'))
            groupAlternativeNew = forceRef(record.value('groupAlternative'))
            if mesActionId:
                amountCount, amountCountExecuted, groupAlternative = mesActionAmount.get(mesActionId, (0, 0, None))
                actionIdCount = mesActionResult.get(mesActionId, 0)
                countActionTypeId, actionTypeIdExecuted = actionTypeIdList.get(actionTypeId, (0, 0))
                actionTypeMesIdList.add(actionTypeId)
                groupAlternativeCode = groupAlternative if (not groupAlternativeNew and groupAlternative) else groupAlternativeNew
                mesActionAmount[mesActionId] = (amountCount + (amount * countActionTypeId), amountCountExecuted + (amount * actionTypeIdExecuted), groupAlternativeCode)
                mesActionResult[mesActionId] = actionIdCount + countActionTypeId
                groupAlternativeCount = groupAlternativeList.get(groupAlternativeCode, 0)
                groupAlternativeList[groupAlternativeCode] = groupAlternativeCount + (1 if (amount * countActionTypeId) > 0 else 0)
    return mesActionResult, mesActionAmount, actionTypeMesIdList, groupAlternativeList


def insertServiceSection(parent, cursor, mesId, title, code, actionMesIdList, actionTypeMesIdList):
    cursor.movePosition(QtGui.QTextCursor.End)
    cursor.insertBlock()
    cursor.insertBlock()
    groupId = forceRef(QtGui.qApp.db.translate('mes.mrbServiceGroup', 'code', code, 'id'))
    if groupId:
        columns = [
                ('10%',[u'№', u''],    CReportBase.AlignRight),
                ('70%',[title, u''],   CReportBase.AlignLeft),
                ('5%',[u'CK', u''],    CReportBase.AlignRight),
                ('5%',[u'Чп', u''],    CReportBase.AlignRight),
                ('5%',[u'Контроль', u'Всего'], CReportBase.AlignRight),
                ('5%',[u'', u'Выполнено'], CReportBase.AlignRight),
                ]
        table = createTable(cursor, columns)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 1, 2)
        table.mergeCells(0, 7, 2, 1)
        table.mergeCells(0, 8, 2, 1)
        table.mergeCells(0, 9, 2, 1)
        actionTypeIdList = {}
        actionTypeAmountList = {}
        for row, record in enumerate(parent.eventEditor.modelActionsSummary.items()):
            amount = forceInt(record.value('amount'))                                   #added by Eugene // 01.11.2012
            actionTypeId = forceRef(record.value('actionType_id'))
            endDate = forceDate(record.value('endDate'))
            if actionTypeId:
                countActionTypeId, actionTypeIdExecuted = actionTypeIdList.get(actionTypeId, (0, 0))
                #actionTypeIdList[actionTypeId] = (countActionTypeId + 1, actionTypeIdExecuted + (1 if endDate else 0))
                actionTypeIdList[actionTypeId] = (countActionTypeId + amount, actionTypeIdExecuted + (amount if endDate else 0))  #modified by Eugene // 01.11.2012
        mesActionResult = {}
        mesActionAmount = {}
        groupAlternativeCodeList = {}
        groupAlternativeList = []
        if actionTypeIdList:
            mesActionResult, mesActionAmount, actionTypeMesIdList, groupAlternativeCodeList = getMesAmountActionTypeAlternative(actionTypeIdList, mesId, groupId, actionTypeMesIdList, mesActionResult, mesActionAmount)
        stmt = '''
            SELECT mrbService.code, mrbService.name, MES_service.averageQnt, MES_service.necessity, mrbService.doctorWTU, mrbService.paramedicalWTU, MES_service.id AS mesServiceId, MES_service.groupCode AS groupAlternative
            FROM mes.mrbService
            LEFT JOIN mes.MES_service ON MES_service.service_id = mrbService.id
            WHERE MES_service.master_id=%d AND MES_service.deleted = 0 AND mrbService.deleted = 0 AND mrbService.group_id = %d
            GROUP BY mrbService.code
            ORDER BY groupAlternative, mrbService.code, mrbService.name, mrbService.id
            ''' % (mesId, groupId)
        query = QtGui.qApp.db.query(stmt)
        prevGroupCode = False
        start = 0
        while query.next():
            record = query.record()
            code  = forceString(record.value('code'))
            name  = forceString(record.value('name'))
            averageQnt = forceInt(record.value('averageQnt'))
            necessity = forceDouble(record.value('necessity'))
            doctorWTU = forceDouble(record.value('doctorWTU'))
            paramedicalWTU = forceDouble(record.value('paramedicalWTU'))
            groupAlternativeNew = forceInt(record.value('groupAlternative'))
            groupAlternative = groupAlternativeNew
            if necessity >= 1:
                brusColor = QtCore.Qt.red
                brusColorNecessity = QtCore.Qt.red
            else:
                brusColor = QtCore.Qt.lightGray
                brusColorNecessity = QtCore.Qt.lightGray
            amountCount = 0
            amountCountExecuted = 0
            groupAlternativeCodeCount = groupAlternativeCodeList.get(groupAlternative, 0) if groupAlternative else 0
            if mesActionResult and mesActionAmount:
                mesServiceId = forceInt(record.value('mesServiceId'))
                if mesServiceId in mesActionAmount.keys():
                    serviceAmoutCount, executedAmoutCount, groupAlternative = mesActionAmount.get(mesServiceId, (0, 0, None))
                else:
                    serviceAmoutCount = 0
                    executedAmoutCount = 0
                serviceIdCount = mesActionResult.get(mesServiceId, 0)
                if serviceIdCount == 0 and (not groupAlternative or not groupAlternativeCodeCount):
                    if necessity >= 1:
                        brusColorNecessity = QtCore.Qt.red
                        brusColor = QtCore.Qt.red
                    else:
                        brusColorNecessity = QtCore.Qt.lightGray
                        brusColor = QtCore.Qt.lightGray
                elif serviceIdCount > 0 and serviceAmoutCount == averageQnt and (not groupAlternative or (groupAlternative not in groupAlternativeList)):
                    brusColor = QtCore.Qt.green
                    brusColorNecessity = None
                    amountCount = serviceAmoutCount
                    amountCountExecuted = executedAmoutCount
                elif (serviceIdCount > 0 and serviceAmoutCount != averageQnt) or (serviceIdCount > 0 and serviceAmoutCount == averageQnt and (groupAlternative and groupAlternative in groupAlternativeList)):
                    if necessity >= 1:
                        brusColorNecessity = None
                        brusColor = QtCore.Qt.red
                    else:
                        brusColorNecessity = None
                        brusColor = QtCore.Qt.lightGray
                    amountCount = serviceAmoutCount
                    amountCountExecuted = executedAmoutCount
                else:
                    brusColor = QtCore.Qt.white
                    brusColorNecessity = QtCore.Qt.white
                if serviceIdCount > 0 and groupAlternative and (groupAlternative not in groupAlternativeList):
                    groupAlternativeList.append(groupAlternative)
#            groupAlternativeCodeCount = groupAlternativeCodeList.get(groupAlternative, 0) if groupAlternative else 0
            brusColorGroupAltirnetive = brusColorNecessity
            if groupAlternativeCodeCount > 1:
                brusColorGroupAltirnetive = QtCore.Qt.red
            elif groupAlternativeCodeCount == 1:
                brusColorGroupAltirnetive = QtCore.Qt.green
            i = table.addRow()
            table.setText(i, 0, i-1, None, None, brusColorNecessity)
            table.setText(i, 1, name, None, None, brusColorNecessity)
            table.setText(i, 2, averageQnt, None, None, brusColorNecessity)
            table.setText(i, 3, necessity, None, None, brusColorNecessity)
            table.setText(i, 4, amountCount, None, None, brusColor)
            table.setText(i, 5, amountCountExecuted, None, None, brusColor if amountCountExecuted == amountCount else QtCore.Qt.red)
    return actionMesIdList, actionTypeMesIdList


def insertServiceNoSection(parent, cursor, actionMesIdList, actionTypeMesIdList):
    actionNoMESIdList = []
    actionTypeNoMESIdList = {}
    actionTypeNoIdList = []
    for row, record in enumerate(parent.eventEditor.modelActionsSummary.items()):
        actionTypeId = forceRef(record.value('actionType_id'))
        if actionTypeId not in actionTypeMesIdList:
            countActionTypeId = actionTypeNoMESIdList.get(actionTypeId, 0)
            actionTypeNoMESIdList[actionTypeId] = countActionTypeId + 1
            if actionTypeId not in actionTypeNoIdList:
               actionTypeNoIdList.append(actionTypeId)

    if actionTypeNoMESIdList and actionTypeNoIdList:
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'Услуги выходящие за пределы требования')
        cursor.insertBlock()

        tableColumns = [
                ('5%',[u'№' ], CReportBase.AlignRight),
                ('15%',[u'Количество' ],    CReportBase.AlignRight),
                ('20%',[u'Тип услуги' ],    CReportBase.AlignRight),
                ('20%',[u'Код услуги' ],    CReportBase.AlignLeft),
                ('40%',[u'Название Услуги' ], CReportBase.AlignLeft),
                ]
        table = createTable(cursor, tableColumns)
        db = QtGui.qApp.db
        tableService = db.table('rbService')
        tableActionType = db.table('ActionType')
        tableQuery = tableActionType.leftJoin(tableService, tableService['id'].eq(tableActionType['nomenclativeService_id']))
        cols = [tableActionType['id'], tableService['code'].alias('codeService'), tableActionType['name'].alias('nameActionType'), tableService['name'].alias('nameService')]
        records =  db.getRecordList(tableQuery, cols, [tableActionType['id'].inlist(actionTypeNoIdList), tableActionType['deleted'].eq(0)])
        actionNoMESList = {}
        actionDistinctIdList = []
        for record in records:
            actionTypeId  = forceRef(record.value('id'))
            if actionTypeId and (actionTypeId not in actionDistinctIdList):
                actionDistinctIdList.append(actionTypeId)
                nameActionType  = forceString(record.value('nameActionType'))
                codeService = forceString(record.value('codeService'))
                nameService = forceString(record.value('nameService'))
                actionNoMES = actionNoMESList.get(actionTypeId, None)
                countActionTypeNoMES = actionTypeNoMESIdList.get(actionTypeId, 0)
                if actionNoMES:
                    actionNoMESList[actionTypeId] = (actionNoMES[0] + countActionTypeNoMES, nameActionType, codeService, nameService)
                else:
                    actionNoMESList[actionTypeId] = (countActionTypeNoMES, nameActionType, codeService, nameService)
        for key, item in actionNoMESList.items():
            i = table.addRow()
            table.setText(i, 0, i, None, None, QtCore.Qt.red)
            table.setText(i, 1, item[0], None, None, QtCore.Qt.red)
            table.setText(i, 2, item[1], None, None, QtCore.Qt.red)
            table.setText(i, 3, item[2], None, None, QtCore.Qt.red)
            table.setText(i, 4, item[3], None, None, QtCore.Qt.red)


def insertMedicamentsSection(cursor, mesId):
    cursor.movePosition(QtGui.QTextCursor.End)
    cursor.insertBlock()
    cursor.insertBlock()
    cursor.insertText(u'Лекарственные средства (МНН) в официнальной дозировке')
    cursor.insertBlock()
    columns = [
            ('5%',[u'№'],             CReportBase.AlignRight),
            ('85%',[u'Наименование'], CReportBase.AlignLeft),
            ('5%',[u'СЧЕ'],           CReportBase.AlignRight),
            ('5%',[u'Чн'],            CReportBase.AlignRight),
            ]
    table = createTable(cursor, columns)
    stmt = '''
        SELECT MES_medicament.medicamentCode as code, MES_medicament.dosage, MES_medicament.averageQnt, MES_medicament.necessity,
               mrbMedicamentDosageForm.name AS formName,
               mrbMedicament.name AS name, mrbMedicament.form AS medicamentForm, mrbMedicament.dosage AS medicamentDosage,
               G1.name AS groupName,
               G2.name AS subgroupName
        FROM mes.MES_medicament
        LEFT JOIN mes.mrbMedicamentDosageForm ON mrbMedicamentDosageForm.id = MES_medicament.dosageForm_id
        LEFT JOIN mes.mrbMedicament ON mrbMedicament.code = MES_medicament.medicamentCode
        LEFT JOIN mes.mrbMedicamentGroup AS G1 ON G1.code = SUBSTRING_INDEX(MES_medicament.medicamentCode, '.', 1)
        LEFT JOIN mes.mrbMedicamentGroup AS G2 ON G2.code = SUBSTRING_INDEX(MES_medicament.medicamentCode, '.', 2)
        WHERE MES_medicament.master_id=%d AND MES_medicament.deleted = 0 AND mrbMedicament.deleted = 0 AND mrbMedicamentDosageForm.deleted = 0 AND G1.deleted = 0 AND G2.deleted = 0
        ORDER BY MES_medicament.medicamentCode, mrbMedicament.name
        ''' % mesId
    query = QtGui.qApp.db.query(stmt)
    row = 0
    while query.next():
        row += 1
        record = query.record()
        groupName = forceString(record.value('groupName'))
        subgroupName = forceString(record.value('subgroupName'))
        code  = forceString(record.value('code'))
        name  = forceString(record.value('name'))
        averageQnt = forceInt(record.value('averageQnt'))
        necessity = forceDouble(record.value('necessity'))
        i = table.addRow()
        table.setText(i, 0, row)
        table.setText(i, 1, u'Группа')
        table.setText(i, 2, groupName)
        i = table.addRow()
        table.setText(i, 1, u'Подгруппа')
        table.setText(i, 2, subgroupName)
        i = table.addRow()
        table.setText(i, 1, code)
        table.setText(i, 1, name)
        table.setText(i, 2, averageQnt)
        table.setText(i, 3, necessity)
        table.mergeCells(i-2, 0, 2, 1)
        table.mergeCells(i-2, 2, 1, 3)
        table.mergeCells(i-1, 2, 1, 3)
