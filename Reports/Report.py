# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Orgs.Utils import getOrganisationShortName, getOrgStructureFullName, getPersonInfo
from RefBooks.Utils import serviceTypeNames
from Reports import OKVEDList
from Reports.ReportBase import createTable, CReportBase
from Reports.ReportSetupDialog import CReportSetupDialog
from Reports.ReportView import CReportViewOrientation
from library.Utils import forceString, getVal, agreeNumberAndWord, formatList, formatSex, \
    MKBwithoutSubclassification


class CReport(CReportBase):
    def __init__(self, parent=None):
        CReportBase.__init__(self, parent)
        self.payPeriodVisible = False
        self.workTypeVisible = False
        self.ownershipVisible = False
        self.additionalDescription = u''


    def setPayPeriodVisible(self, value):
        self.payPeriodVisible = value


    def setWorkTypeVisible(self, value):
        self.workTypeVisible = value


    def setOwnershipVisible(self, value):
        self.ownershipVisible = value


    def getSetupDialog(self, parent):
        result = CReportSetupDialog(parent)
        result.setPayPeriodVisible(self.payPeriodVisible)
        result.setWorkTypeVisible(self.workTypeVisible)
        result.setOwnershipVisible(self.ownershipVisible)
        result.setTitle(self.title())
        return result


    def dumpParams(self, cursor, params, charFormat = QtGui.QTextCharFormat(), additionalDescription=u''):
        description = self.getDescription(params)
        self.additionalDescription = additionalDescription
        columns = [ ('100%', [], CReportBase.AlignLeft) ]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row, charFormat = charFormat)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()


    def getDescription(self, params):
        db = QtGui.qApp.db
        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с '+forceString(begDate)
            if endDate:
                result += u' по '+forceString(endDate)
            return result

        def dateTimeRangeAsStr(begDate, begTime, endDate, endTime):
            result = ''
            if begDate:
                result += u' с '
                if begTime:
                    result += forceString(begTime) + u' '
                result += forceString(begDate)
            if endDate:
                result += u' по '
                if endTime:
                    result += forceString(endTime) + u' '
                result += forceString(endDate)
            return result

        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        begTime = params.get('begTime', QtCore.QTime())
        endTime = params.get('endTime', QtCore.QTime())

        byPeriod= params.get('byPeriod', None)
        begDateReestr = params.get('begDateReestr', QtCore.QDate())
        endDateReestr = params.get('endDateReestr', QtCore.QDate())

        accountNumbersList = params.get('accountNumbersList', [])

        useInputDate = bool(params.get('useInputDate', False))
        begInputDate = params.get('begInputDate', QtCore.QDate())
        endInputDate = params.get('endInputDate', QtCore.QDate())
        begDateBeforeRecord = params.get('begDateBeforeRecord', QtCore.QDate())
        endDateBeforeRecord = params.get('endDateBeforeRecord', QtCore.QDate())

        doctype = params.get('doctype', None)
        tempInvalidReason = params.get('tempInvalidReason', None)
        durationFrom = params.get('durationFrom', 0)
        durationTo = params.get('durationTo', 0)
        insuranceOfficeMark = params.get('insuranceOfficeMark', 0)
        sex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', None)
        ageTo = params.get('ageTo', None)

        birthYearParam = params.get('birthYearParam', None)
        birthYearFrom = params.get('birthYearFrom', None)
        birthYearTo = params.get('birthYearTo', None)

        socStatusClassId = params.get('socStatusClassId', None)
        socStatusTypeId = params.get('socStatusTypeId', None)
        locationCardTypeId = params.get('locationCardTypeId', None)
        areaIdEnabled = params.get('areaIdEnabled', False)
        areaId = params.get('areaId', None)
        areaAddressType = getVal(params, 'areaAddressType', None)
        locality = params.get('locality', 0)
        onlyClosed = params.get('onlyClosed', None)
        MKBFilter = params.get('MKBFilter', 0)
        MKBFrom = params.get('MKBFrom', '')
        MKBTo = params.get('MKBTo', '')
        MKBExFilter = params.get('MKBExFilter', 0)
        MKBExFrom = params.get('MKBExFrom', '')
        MKBExTo = params.get('MKBExTo', '')
        stageId = params.get('stageId', None)

        eventPurposeId = params.get('eventPurposeId', None)
        eventTypeId = params.get('eventTypeId', None)
        eventTypes = params.get('eventTypes', None)
        if params.get('cmbOrgStructure', False):
            lstOrgStructure = params.get('lstOrgStructure', None)
            orgStructureId = None
        else:
            lstOrgStructure = None
            orgStructureId = params.get('orgStructureId', None)
        sceneId = params.get('sceneId', None)
        specialityId = params.get('specialityId', None)
        personId = params.get('personId', None)
        assistantId = params.get('assistantId', None)
        userProfileId = params.get('userProfileId', None)
        beforeRecordUserId = params.get('beforeRecordUserId', None)
        onlyPermanentAttach =  params.get('onlyPermanentAttach', False)
        onlyPayedEvents = params.get('onlyPayedEvents', None)

        characterClass = params.get('characterClass', 0)
        onlyFirstTime = params.get('onlyFirstTime', None)
        registeredInPeriod = params.get('registeredInPeriod', None)
        notNullTraumaType = params.get('notNullTraumaType', None)
        accountAccomp = params.get('accountAccomp', None)

        busyness = params.get('busyness', 0)
        workOrgId = params.get('workOrgId', None)
        typeFinanceId = params.get('typeFinanceId', None)
        tariff = params.get('tariff', None)
        visitPayStatus = params.get('visitPayStatus', None)
        groupingRows = params.get('groupingRows', None)
        rowGrouping = params.get('rowGrouping', None)
        advancedRowGrouping = params.get('advancedRowGrouping', None)

        insurerId = params.get('insurerId', None)
        contractIdList = params.get('contractIdList', None)
        accountIdList = params.get('accountIdList', None)

        actionTypeClass = params.get('actionTypeClass', None)
        actionTypeId = params.get('actionTypeId', None)
        actionTypeCode = params.get('queueType', None)

        permanentAttach = params.get('PermanentAttach', None)

        deathPlace = params.get('deathPlace', '')
        deathCause = params.get('deathCause', '')
        deathFoundBy = params.get('deathFoundBy', '')
        deathFoundation = params.get('deathFoundation', '')

        reportDate = params.get('reportDate')
        confirmEISDate = params.get('confirmEISDate')

        detailServiceTypes = params.get('detailServiceTypes', None)
        serviceTypes = params.get('serviceTypes', None)
        profileBedId = params.get('profileBedId', None)

        rows = []
        if begDate or endDate:
            rows.append(u'за период' + dateTimeRangeAsStr(begDate, begTime, endDate, endTime))
        if begDateReestr or endDateReestr:
            rows.append(u'По реестрам персональных счетов с расчетной датой:' + dateRangeAsStr(begDateReestr, endDateReestr))
        if begDateBeforeRecord or endDateBeforeRecord:
            rows.append(u'период предварительной записи' + dateRangeAsStr(begDateBeforeRecord, endDateBeforeRecord))
        if useInputDate and (begInputDate or endInputDate):
            rows.append(u'дата ввода в период'+ dateRangeAsStr(begInputDate, endInputDate))
        if byPeriod is not None:
            if byPeriod:
                rows.append(u'отчёт по периоду случая')
            else:
                rows.append(u'отчёт по окончанию случая')
        if eventPurposeId:
            rows.append(u'Цель обращения: ' + forceString(db.translate('rbEventTypePurpose', 'id', eventPurposeId, 'name')))
        if eventTypeId:
            rows.append(u'тип обращения: ' + getEventTypeName(eventTypeId))
        if eventTypes:
            rows.append(u'тип обращения: ' + ', '.join([getEventTypeName(x) for x in eventTypes]))
        if sceneId:
            rows.append(u'Место: ' + forceString(db.translate('rbScene', 'id', sceneId, 'name')))
        if orgStructureId:
            if isinstance(orgStructureId, list):
                rows.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId[0]))
            else:
                rows.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId))
        elif lstOrgStructure:
            rows.append(u'подразделения: ' + ', '.join([forceString(orgStructure) for orgStructure in lstOrgStructure.itervalues()]))
        if specialityId:
            rows.append(u'специальность: ' + forceString(db.translate('rbSpeciality', 'id', specialityId, 'name')))
        if personId:
            personInfo = getPersonInfo(personId)
            rows.append(u'врач: ' + personInfo['shortName']+', '+personInfo['specialityName'])
        if assistantId:
            personInfo = getPersonInfo(assistantId)
            rows.append(u'ассистент: ' + personInfo['shortName']+', '+personInfo['specialityName'])
        if userProfileId:
            rows.append(u'профиль прав пользователя: ' + forceString(db.translate('rbUserProfile', 'id', userProfileId, 'name')))
        if beforeRecordUserId:
            personInfo = getPersonInfo(beforeRecordUserId)
            rows.append(u'пользователь: ' + personInfo['shortName']+', '+personInfo['specialityName'])
        if doctype != None:
            rows.append(u'тип документа: ' + forceString(db.translate('rbTempInvalidDocument', 'id', doctype, 'name')))
        if tempInvalidReason != None:
            rows.append(u'причина нетрудоспособности: ' + forceString(db.translate('rbTempInvalidReason', 'id', tempInvalidReason, 'name')))
        if durationTo:
            rows.append(u'длительность нетрудоспособности: c %d по %d дней' % (durationFrom, durationTo))
        if insuranceOfficeMark in (1, 2):
            rows.append([u'без отметки страхового стола', u'с отметкой страхового стола'][insuranceOfficeMark-1])
        if sex:
            rows.append(u'пол: ' + formatSex(sex))
        if not birthYearParam and ageFrom != None and ageTo != None and ageFrom <= ageTo:
            rows.append(u'возраст: c %d по %d %s' % (ageFrom, ageTo, agreeNumberAndWord(ageTo, (u'год', u'года', u'лет'))))
        if birthYearParam and birthYearFrom != None and birthYearTo != None and birthYearFrom <= birthYearTo:
            rows.append(u'год рождения: c %d по %d ' % (birthYearFrom, birthYearTo))
        if socStatusTypeId:
            rows.append(u'Тип соц.статуса:' + forceString(db.translate('vrbSocStatusType', 'id', socStatusTypeId, 'name')))
        elif socStatusClassId:
            rows.append(u'Класс соц.статуса:' + forceString(db.translate('rbSocStatusClass', 'id', socStatusClassId, 'name')))
        if locationCardTypeId:
            rows.append(u'Место нахождение амбулаторной карты: ' + forceString(db.translate('rbLocationCardType', 'id', locationCardTypeId, 'name')))
        if areaIdEnabled:
            rows.append(u'проживает на территории: ' + (getOrgStructureFullName(areaId) if areaId else u'ЛПУ'))
        if areaAddressType != None:
            rows.append(u'адрес ' + (u'проживания', u'регистрации')[areaAddressType])
        if locality:
            rows.append(u'%s жители' % ((u'городские', u'сельские')[locality-1]))
        if insurerId:
            rows.append(u'СМО: ' + forceString(db.translate('Organisation', 'id', insurerId, 'shortName')))
        if onlyClosed:
            rows.append(u'только закрытые')
        if MKBFilter == 1:
            rows.append(u'код МКБ с "%s" по "%s"' % (MKBFrom, MKBTo))
        elif MKBFilter == 2:
            rows.append(u'код МКБ пуст')
        if MKBExFilter == 1:
            rows.append(u'доп.код МКБ с "%s" по "%s"' % (MKBExFrom, MKBExTo))
        elif MKBExFilter == 2:
            rows.append(u'доп.код МКБ пуст')
        if characterClass:
            rows.append(u'характер заболевания:' + [u'Любой', u'Острый', u'Хронический', u'Острый или хронический', u'Фактор', u'исправь меня'][characterClass if 0<=characterClass<5 else -1])
        if stageId:
            rows.append(u'стадия заболевания:' + forceString(db.translate('rbDiseaseStage', 'id', stageId, 'name')))
        if onlyFirstTime:
            rows.append(u'зарегистрированные в период впервые')
        if registeredInPeriod:
            rows.append(u'зарегистрированные в период')
        if notNullTraumaType:
            rows.append(u'тип травмы указан')
        if accountAccomp:
            rows.append(u'учитывать сопутствующие')

        if onlyPermanentAttach:
            rows.append(u'имеющие постоянное прикрепление')

        if contractIdList:
            if len(contractIdList) == 1:
                rows.append(u'по договору № ' + getContractName(contractIdList[0]))
            else:
                contractPath = params.get('contractPath', None)
                if contractPath:
                    rows.append(u'По договорам: %s' % contractPath)
                else:
                    rows.append(u'по договорам №№ ' + formatList([getContractName(contractId) for contractId in contractIdList]))

        if accountIdList:
            if len(accountIdList) == 1:
                rows.append(u'по счёту № ' + getAccountName(accountIdList[0]))
            else:
                rows.append(u'по счетам №№ ' + formatList([getAccountName(accountId) for accountId in accountIdList]))

        if accountNumbersList:
            rows.append(u'Номера реестров счетов: ' + formatList(accountNumbersList))

        if onlyPayedEvents:
            rows.append(u'только оплаченные обращения')
            if self.payPeriodVisible:
                begPayDate = getVal(params, 'begPayDate', None)
                endPayDate = getVal(params, 'endPayDate', None)
                row = ''
                if begPayDate and not begPayDate.isNull():
                    row  = row + u' с ' + forceString(begPayDate)
                if endPayDate and not endPayDate.isNull():
                    row  = row + u' по ' + forceString(endPayDate)
                if row:
                    rows.append(u'в период'+row)
        if self.workTypeVisible:
            workType = getVal(params, 'workType', 0)
            if 0<workType<len(OKVEDList.rows):
                descr = OKVEDList.rows[workType]
                name = descr[0]
                code = descr[2]
            else:
                name = u'Любой'
                code = ''
            row = u'Вид деятельности: ' + name
            if code:
                row = row + u', код по ОКВЭД: ' + code
            rows.append(row)
        if self.ownershipVisible:
            ownership = getVal(params, 'ownership', 0)
            row = u'Собственность: ' + [u'Любая', u'Бюджетная', u'Частная', u'Cмешанная'][min(ownership, 3)]
            rows.append(row)
        if busyness == 1:
            rows.append(u'занятость указана')
        elif busyness == 2:
            rows.append(u'занятость не указана')
        if workOrgId:
            rows.append(u'занятость: '+getOrganisationShortName(workOrgId))
        if actionTypeClass is not None:
            actionTypeClassName={0:u'статус', 1:u'диагностика', 2:u'лечение', 3:u'прочие мероприятия'}.get(actionTypeClass, u'')
            rows.append(u'класс мероприятий: '+actionTypeClassName)
        if actionTypeId:
            actionTypeName=forceString(db.translate('ActionType', 'id', actionTypeId, 'name'))
            rows.append(u'мероприятие: '+actionTypeName)
        if actionTypeCode == 0:
            rows.append(u'мероприятие: Прием')
        elif actionTypeCode == 1:
            rows.append(u'мероприятие: Вызовы')
        if permanentAttach and permanentAttach>0:
            lpu=forceString(db.translate('Organisation', 'id', permanentAttach, 'shortName'))
            rows.append(u'прикрепление: '+lpu)
        if deathPlace:
            rows.append(u'смерть последовала: '+deathPlace)
        if deathCause:
            rows.append(u'смерть произошла: '+deathCause)
        if deathFoundBy:
            rows.append(u'причина смерти установлена: '+deathFoundBy)
        if deathFoundation:
            rows.append(u'основание установления причины смерти: '+deathFoundation)
        if typeFinanceId != None:
            rows.append(u'тип финансирования: '+ forceString(db.translate('rbFinance', 'id', typeFinanceId, 'name')))
        if tariff != None:
            rows.append(u'тарификация: '+ [u'не учитывать', u'тарифицированные', u'не тарифицированные'][tariff])
        if visitPayStatus != None:
            rows.append(u'флаг финансирования: '+ [u'не задано', u'не выставлено', u'выставлено', u'отказано', u'оплачено'][visitPayStatus])
        if groupingRows != None:
            rows.append(u'группировка: '+ [u'по специальности', u'по должности', u'по отделению'][groupingRows])
        if rowGrouping != None:
            rows.append(u'группировка: '+ [u'по датам', u'по врачам', u'по подразделениям', u'по специальности', u'по должности', u'по пациентам'][rowGrouping])
        if advancedRowGrouping != None:
            rows.append(u'группировка: '+ [u'по датам', u'по персоналу', u'по подразделениям', u'по специальности', u'по должности', u'по врачам', u'по мед.сестрам'][advancedRowGrouping])
        if confirmEISDate:
            rows.append(u'дата подтверждения ЕИС: ' + forceString(confirmEISDate))
        if self.additionalDescription:
            rows.append(self.additionalDescription)
        if reportDate:
            rows.append(u'отчёт составлен: '+forceString(reportDate))
        else:
            rows.append(u'отчёт составлен: '+forceString(QtCore.QDateTime.currentDateTime()))
        if detailServiceTypes and serviceTypes:
            rows.append(u'Типы услуг: ' + u', '.join(map(lambda x: serviceTypeNames[x+1], serviceTypes)))
        if profileBedId:
            rows.append(u'профиль койки: %s' % (
                forceString(QtGui.qApp.db.translate('rbHospitalBedProfile', 'id', profileBedId, 'name'))))
        """
        if profileDayStatId:
            #rows.append(u'профиль ДС: %s' % (
                #forceString(QtGui.qApp.db.translate('rbEventProfile', 'id', profileDayStatId, 'name'))))
            rows.append(
                u'Профиль ДС: ' + forceString(
                    [u'Дневной стационар', u'Стационар дневного пребывание'][profileDayStatId]))
        """


        return rows


    def dumpParamsAdress(self, cursor, params):
        description = []
        db = QtGui.qApp.db
        typeAdress = [u'регистрации', u'проживания']
        filterAddress = params.get('isFilterAddress', False)
        if filterAddress:
            filterAddressType = params.get('filterAddressType', 0)
            filterAddressCity = params.get('filterAddressCity', None)
            filterAddressStreet = params.get('filterAddressStreet', None)
            filterAddressHouse = params.get('filterAddressHouse', u'')
            filterAddressCorpus = params.get('filterAddressCorpus', u'')
            filterAddressFlat = params.get('filterAddressFlat', u'')

            description.append(u'Адресс ' + forceString(typeAdress[filterAddressType]) + u':')
            description.append((u'город ' + forceString(db.translate(u'kladr.KLADR', u'CODE', filterAddressCity, u'NAME')) if filterAddressCity else u'') + (u' улица ' + forceString(db.translate(u'kladr.STREET', u'CODE', filterAddressStreet, u'NAME')) if filterAddressStreet else u'') + (u' дом ' + forceString(filterAddressHouse) if filterAddressHouse else u'') + (u' корпус ' + forceString(filterAddressCorpus) if filterAddressCorpus else u'') + (u' квартира ' + forceString(filterAddressFlat) if filterAddressFlat else u''))

            columns = [ ('100%', [], CReportBase.AlignLeft) ]
            table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
            for i, row in enumerate(description):
                table.setText(i, 0, row)
            cursor.movePosition(QtGui.QTextCursor.End)


def normalizeMKB(mkb):
    mkb = MKBwithoutSubclassification(mkb)
    if len(mkb) == 3:
        mkb = mkb + '.0'
    return mkb


def getEventTypeName(eventTypeId):
    from Events.Utils import getEventName
    if eventTypeId:
        return getEventName(eventTypeId)
    else:
        return u'-'


def getContractName(contractId):
    if contractId:
        record = QtGui.qApp.db.getRecord('Contract', 'number, date', contractId)
        return forceString(record.value('number')) + u' от ' +forceString(record.value('date'))
    else:
        return '-'


def getAccountName(accountId):
    if accountId:
        record = QtGui.qApp.db.getRecord('Account', 'number, date', accountId)
        return forceString(record.value('number')) + u' от ' +forceString(record.value('date'))
    else:
        return '-'


def convertFilterToString(filter, filterFormat):
    # filter: словарь
    # filterFormat: список троек ( ключ-или-список-ключей, заголовок, функция преобразования )
    # выводит строки заголовок: filter[ключ]
    # для непустых filter[ключ]
    parts = []
    for keys, title, formatFunc in filterFormat:
        if isinstance(keys, basestring):
            values = [filter.get(keys, None)]
        else:
            values = [filter.get(key, None) for key in keys]
        if any(values):
            if formatFunc:
                outValue = formatFunc(*values)
            else:
                outValue = ' '.join([v for v in values if v])
            if outValue:
                parts.append(title +': '+outValue)
            else:
                parts.append(title)
    return '\n'.join(parts)


class CReportOrientation(CReport):
    def __init__(self, parent, orientation=QtGui.QPrinter.Portrait):
        CReport.__init__(self, parent)
        self.parent = parent
        self.orientation = orientation

    def reportLoop(self):
        params = self.getDefaultParams()
        while True:
            setupDialog = self.getSetupDialog(self.parent)
            setupDialog.setParams(params)
            if not setupDialog.exec_() :
                break
            params = setupDialog.params()
            self.saveDefaultParams(params)
            try:
                QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                reportResult = self.build(params)
            finally:
                QtGui.qApp.restoreOverrideCursor()
            viewDialog = CReportViewOrientation(self.parent, self.orientation)
            if self.viewerGeometry:
                viewDialog.restoreGeometry(self.viewerGeometry)
            viewDialog.setWindowTitle(self.title())
            viewDialog.setRepeatButtonVisible()
            viewDialog.setText(reportResult)
            viewDialog.setQueryText(self.queryText())
            done = not viewDialog.exec_()
            self.viewerGeometry = viewDialog.saveGeometry()
            if done:
                break
        # save params?


    def oneShot(self, params):
        try:
            QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            reportResult = self.build(params)
        finally:
            QtGui.qApp.restoreOverrideCursor()
        viewDialog = CReportViewOrientation(self.parent, self.orientation)
        if self.viewerGeometry:
            viewDialog.restoreGeometry(self.viewerGeometry)
        viewDialog.setWindowTitle(self.title())
        viewDialog.setText(reportResult)
        viewDialog.exec_()
        self.viewerGeometry = viewDialog.saveGeometry()
