# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
##############################################################################

__author__ = 'craz'

'''
    author: craz
    date:   17.12.2014
'''
from PyQt4 import QtCore, QtGui

from Accounting.Utils import getClientDiscountInfo, getContractInfo, isTariffApplicable, CTariff, getMesAmount
from Events.EventInfo import CMesInfo
from Events.MapActionTypeToServiceIdList import CMapActionTypeIdToServiceIdList
from Events.Utils   import getActionLengthDays, getEventLengthDays, getEventPurposeCode, getEventServiceId
from library.PrintInfo import CInfoContext
from library.Utils import forceDate, forceDateTime, forceDecimal, forceRef, forceString, formatName, addPeriod
from Reports.ReportBase import CReportBase, createTable
from Reports.ReportView import CReportViewDialog


class CReportEventCost(object):
    def __init__(self, eventId, clientId, parent):
        self.infoContext = CInfoContext()
        self.mapEventIdToMKB = {}
        report = self.build(eventId, clientId)
        self.view = self.getView(report, parent)

    def build(self, eventId, clientId):
        db = QtGui.qApp.db
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.setBlockFormat(CReportBase.AlignCenter)
        cursor.insertText(u'Справка\n')
        cursor.setCharFormat(CReportBase.ReportSubTitle)
        cursor.insertText(u'о стоимости медицинской помощи, оказанной застрахованному лицу в рамках программ обязательного медицинского страхования\n')
        cursor.insertHtml(u'<hl/><hr/>')
        f = CReportBase.ReportBody
        f.setFontItalic(True)
        cursor.insertBlock()
        cursor.insertText(forceString(db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'shortName')))
        cursor.insertBlock()
        cursor.setCharFormat(f)
        cursor.insertText(u'\n(штамп с наименованием и адресом учреждения выдавшего справку)\n')

        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignRight)
        fb = CReportBase.ReportBody
        fb.setFontWeight(QtGui.QFont.Bold)
        cursor.setCharFormat(fb)
        cursor.insertText(u'от %s\n' % QtCore.QDate.currentDate().toString('dd.MM.yyyy'))

        cursor.insertBlock()
        cursor.setBlockFormat(CReportBase.AlignLeft)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertText(u'(Ф.И.О.) ')
        # fu = CReportBase.ReportBody
        # fu.setFontUnderline(True)
        # cursor.setCharFormat(fu)
        clientRecord = db.getRecord('Client', ['lastName', 'firstName', 'patrName'], clientId)
        cursor.insertText(u'%s\n' % formatName(clientRecord.value('lastName'),
                                             clientRecord.value('firstName'),
                                             clientRecord.value('patrName')))
        eventRecord = db.getRecord('Event', ['setDate', 'execDate'], eventId)
        cursor.insertText(u'в период с %sг. по %sг.\n' % (forceDate(eventRecord.value('setDate')).toString('dd.MM.yyyy'),
                                                          forceDate(eventRecord.value('execDate')).toString('dd.MM.yyyy')))

        cursor.insertText(u'оказаны медицинские услуги:\n')

        columns = [('80%', [u'наименование медицинской услуги'], CReportBase.AlignLeft),
                   ('20%', [u'стоимость (руб.)'], CReportBase.AlignRight)]


        table = createTable(cursor, columns)
        self.fillTable(table, eventId)
        cursor.movePosition(QtGui.QTextCursor.End)

        cursor.insertText(u'\n\nВнимание! Настоящая справка носит уведомительный характер, оплате за счет личных средств не '
                          u'подлежит. При несоответствии фактически оказанных услуг приведенным в настоящей справке '
                          u'необходимо обратиться в свою страховую медицинскую организацию или в территориальный фонд '
                          u'обязательного медицинского страхования.')

        return doc

    def fillTable(self, table, eventId):
        db = QtGui.qApp.db
        results = []
        event = db.getRecord(table = 'Event '
                                     ' LEFT JOIN Person ON Person.id = Event.execPerson_id'
                                     ' LEFT JOIN mes.MES ON MES.id = Event.MES_id'
                                     ' LEFT JOIN rbService ON rbService.code = MES.code',
                             cols = ['Event.client_id',
                                     'Event.setDate',
                                     'Event.execDate',
                                     'Event.eventType_id',
                                     'Event.MES_id',
                                     'rbService.id as serviceId',
                                     'Person.tariffCategory_id',
                                     'Event.contract_id'
                                     ],
                             itemId = eventId)

        eventContractId = forceRef(event.value('contract_id'))
        contractInfo = getContractInfo(eventContractId)

        eventEndDate = forceDate(event.value('execDate'))
        eventTypeId = forceRef(event.value('eventType_id'))
        tariffCategoryId = forceRef(event.value('tariffCategory_id'))
        eventBegDate = forceDateTime(event.value('setDate'))
        mesId = forceRef(event.value('MES_id'))
        clientId = forceRef(event.value('client_id'))
        # Случай лечения
        tariffList = contractInfo.tariffByEventType.get(eventTypeId, [])
        for tariff in tariffList:
            if isTariffApplicable(tariff, eventId, tariffCategoryId, eventEndDate, mapEventIdToMKB = self.mapEventIdToMKB):
                serviceId = getEventServiceId(eventTypeId)
                price  = tariff.price
                federalPrice = 0
                if contractInfo.isConsiderFederalPrice:
                    federalPrice = tariff.federalPrice
                discount = getClientDiscountInfo(clientId)[0]
                price *= 1.0 - discount
                sum    = round((price + federalPrice), 2)
                results.append((forceString(db.translate('rbService', 'id', serviceId, 'name')), sum))
                break

        # Визит по МЭС
        serviceId = forceRef(event.value('serviceId'))
        tariffList = contractInfo.tariffVisitsByMES.get((eventTypeId, serviceId), [])
        for tariff in tariffList:
            if isTariffApplicable(tariff, eventId, tariffCategoryId, eventEndDate, mapEventIdToMKB = self.mapEventIdToMKB):
                amount = float(getMesAmount(eventId, mesId))
                federalPrice = 0
                if contractInfo.isConsiderFederalPrice:
                    federalPrice = tariff.federalPrice
                amount, price, sum = tariff.evalAmountPriceSum(amount, clientId)
                sum = round((price + federalPrice) * amount, 2)
                results.append((forceString(db.translate('rbService', 'id', serviceId, 'name')), sum))
                break

        # Обращение по МЭС
        tariffDate = eventEndDate # Дата для выбора подходящего тарифа
        tariffList = contractInfo.tariffEventByMES.get((eventTypeId, serviceId), [])
        eventLengthDays = getEventLengthDays(eventBegDate, eventEndDate, True, eventTypeId)

        # Если включена опция "Учитывать максимальную длительность по стандарту"
        if contractInfo.exposeByMESMaxDuration:
            # Получаем максимальную длительность текущего МЭС
            mesMaxDuration = CMesInfo(self.infoContext, mesId).maxDuration
        else:
            # В качестве максимальной используем реальную длительность события
            mesMaxDuration = eventLengthDays
        # Если максимальная длительность события по МЭС меньше реальной
        if mesMaxDuration < eventLengthDays:
            purposeCode = getEventPurposeCode(eventTypeId)
            # Для обращений с типом назначения "заболевание", "профилактика" или "патронаж"
            if purposeCode in ['1', '2', '3']:
                # Дата, по которой ищется нужный тариф, получается путем добавления к дате начала обращения максимальной длительности с учетом выходных
                tariffDate = addPeriod(eventBegDate, mesMaxDuration, True)
            # Для обращений с типом назначения "Реабилитация" или "Стационар"
            elif purposeCode in ['7', '10']:
                # Дата, по которой ищется нужный тариф, получается путем добавления к дате начала обращения максимальной длительности без учета выходных
                tariffDate = addPeriod(eventBegDate, mesMaxDuration, False)

        for tariff in tariffList:
            if isTariffApplicable(tariff, eventId, tariffCategoryId, tariffDate, mapEventIdToMKB = self.mapEventIdToMKB):
                if tariff.tariffType == CTariff.ttEventByMESLen:
                    amount = eventLengthDays
                else:
                    amount = 1
                federalPrice = 0
                if contractInfo.isConsiderFederalPrice:
                    federalPrice = tariff.federalPrice
                amount, price, sum = tariff.evalAmountPriceSum(amount, clientId)
                sum = round((price + federalPrice) * amount, 2)
                results.append((forceString(db.translate('rbService', 'id', serviceId, 'name')), sum))
                break

        # Визиты
        visitStmt = db.selectStmt(table = 'Visit'
                                     ' LEFT JOIN Person ON Person.id = Visit.person_id',
                             fields = [
                                     'Visit.id',
                                     'Visit.event_id',
                                     'Visit.date',
                                     'Visit.service_id',
                                     'Person.tariffCategory_id',
                                     'Person.speciality_id',
                                     ],
                             where = 'Visit.event_id = %s AND Visit.deleted = 0' % eventId)
        visitQuery = db.query(visitStmt)
        while visitQuery.next():
            visit = visitQuery.record()

            serviceId = forceRef(visit.value('service_id'))
            tariffList = contractInfo.tariffByVisitService.get(serviceId, None)
            if tariffList:
                visitDate = forceDate(visit.value('date'))
                specialityId = forceRef(visit.value('speciality_id'))
                tariffCategoryId = forceRef(visit.value('tariffCategory_id'))
                for tariff in tariffList:
                    if isTariffApplicable(tariff, eventId, tariffCategoryId, visitDate, mapEventIdToMKB = self.mapEventIdToMKB):
                        if not tariff.specialityId or specialityId == tariff.specialityId:
                            price  = tariff.price
                            federalPrice = 0
                            if contractInfo.isConsiderFederalPrice:
                                federalPrice = tariff.federalPrice
                            discount = getClientDiscountInfo(clientId)[0]
                            price *= 1.0 - discount
                            amount = 1.0
                            sum    = round((price + federalPrice) * amount, 2)
                            results.append((forceString(db.translate('rbService', 'id', serviceId, 'name')), sum))

        actionStmt = db.selectStmt(table = 'Action'
                                      ' LEFT JOIN Person ON Person.id = Action.person_id'
                                      ' LEFT JOIN mes.MES ON MES.id = Action.MES_id'
                                      ' LEFT JOIN rbService ON rbService.code = MES.code',
                              fields = [
                                      'Action.id',
                                      'Action.actionType_id',
                                      'Action.event_id, Action.begDate',
                                      'Action.endDate',
                                      'Action.amount',
                                      'Action.MKB',
                                      'Person.tariffCategory_id',
                                      'Action.MES_id',
                                      'Action.contract_id',
                                      'rbService.id as serviceId'
                                      ],
                              where = 'Action.event_id = %s AND Action.deleted = 0' % eventId)
        actionQuery = db.query(actionStmt)
        while actionQuery.next():
            success = False
            action = actionQuery.record()
            actionContractId = forceRef(action.value('contract_id'))
            if actionContractId and actionContractId != eventContractId:
                actionContractInfo = getContractInfo(actionContractId)
            else:
                actionContractInfo = contractInfo
            serviceId = forceRef(action.value('serviceId'))
            tariffList = actionContractInfo.tariffActionsByMES.get((eventTypeId, serviceId), None)
            amount = getActionLengthDays(forceDate(action.value('begDate')), forceDate(action.value('endDate')), True, eventTypeId)

            if tariffList:
                endDate = forceDate(action.value('endDate'))
                MKB = forceString(action.value('MKB'))
                tariffCategoryId = forceRef(action.value('tariffCategory_id'))
                for tariff in tariffList:
                    if isTariffApplicable(tariff, eventId, tariffCategoryId, endDate, MKB, mapEventIdToMKB = self.mapEventIdToMKB):
                        amount, price, sum = tariff.evalAmountPriceSum(amount, clientId)
                        results.append((forceString(db.translate('rbService', 'id', serviceId, 'name')), sum))
                        success = True
                        break

            if success:
                continue

            serviceIdList = CMapActionTypeIdToServiceIdList.getActionTypeServiceIdList(forceRef(action.value('actionType_id')), actionContractInfo.finance_id)
            origAmount = forceDecimal(action.value('amount'))
            for serviceId in serviceIdList:
                tariffList = actionContractInfo.tariffByActionService.get(serviceId, None)
                if tariffList:
                    endDate = forceDate(action.value('endDate'))
                    MKB = forceString(action.value('MKB'))
                    tariffCategoryId = forceRef(action.value('tariffCategory_id'))
                    for tariff in tariffList:
                        if isTariffApplicable(tariff, eventId, tariffCategoryId, endDate, MKB, mapEventIdToMKB = self.mapEventIdToMKB):
                            federalPrice = 0
                            if actionContractInfo.isConsiderFederalPrice:
                                federalPrice = tariff.federalPrice
                            amount, price, sum = tariff.evalAmountPriceSum(origAmount, clientId)
                            sum += federalPrice * amount
                            results.append((forceString(db.translate('rbService', 'id', serviceId, 'name')), sum))
                            break

        for result in results:
            i = table.addRow()
            table.setText(i, 0, result[0])
            table.setText(i, 1, result[1])

    def getView(self, report, parent):
        view = CReportViewDialog(parent)
        view.setWindowTitle(u'Справка о стоимости лечения')
        view.setText(report)
        return view

    def exec_(self):
        self.view.exec_()