# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import QModelIndex, Qt

from Accounting.AccountInfo import CAccountInfo
from Accounting.PayStatusDialog import CPayStatusDialog
from Events.Utils import CFinanceType, CPayStatus, getEventDiagnosis, getExposed, getPayStatusMask, \
    getRealPayed
from Orgs.Utils import COrgStructureInfo, getOrgStructureDescendants
from Registry.Utils import getClientInfo
from Users.Rights import urAccessAccountInfo, urAccessAccounting, urAccessAccountingBudget, urAccessAccountingCMI, \
    urAccessAccountingCash, \
    urAccessAccountingTargeted, urAccessAccountingVMI, urAdmin
from library.AgeSelector import checkAgeSelector, parseAgeSelector
from library.CashRegister.CashRegisterDriverInfo import CCashRegisterDriverInfo
from library.CashRegister.CheckItemModel import CCheckItem
from library.Counter import getContractDocumentNumber
from library.PreferencesMixin import CPreferencesMixin
from library.PrintInfo import CInfoContext
from library.TableModel import CCol, CDateCol, CDesignationCol, CNumCol, CRefBookCol, CSumCol, CTableModel, CTextCol
from library.Utils import TWO_PLACES, calcAgeTuple, forceBool, forceDate, forceDateTime, forceDecimal, forceDouble, \
    forceInt, forceRef, \
    forceString, forceStringEx, formatName, formatSex, getPref, getVal, setPref, smartDict, toVariant
from library.database import CTableRecordCache

accountantRightList = (
    urAdmin,
    urAccessAccountInfo,
    urAccessAccounting,
    urAccessAccountingBudget,
    urAccessAccountingCMI,
    urAccessAccountingVMI,
    urAccessAccountingCash,
    urAccessAccountingTargeted
)


def setPayStatus(parent, contractInfo, accountItemIdList, payParams):
    if hasattr(QtGui.qApp, 'dontTouchPayStatus') and QtGui.qApp.dontTouchPayStatus:
        return True

    result = False
    date = toVariant(payParams.get('date', QtCore.QDate()))
    number = toVariant(payParams.get('number', ''))
    note = toVariant(payParams.get('note', ''))
    if payParams.get('accepted', True):
        refuseTypeId = toVariant(None)
        if date.isNull():
            bits = CPayStatus.exposedBits
        else:
            bits = CPayStatus.payedBits
    else:
        refuseTypeId = toVariant(payParams.get('refuseTypeId', None))
        bits = CPayStatus.refusedBits

    db = QtGui.qApp.db
    table = db.table('Account_Item')
    db.transaction()
    try:
        accountIdList = set()
        items = db.getRecordList(
            table,
            'id, master_id, event_id, visit_id, action_id, date, number, refuseType_id, reexposeItem_id, note',
            where=table['id'].inlist(accountItemIdList))
        for item in items:
            reexposed = not item.isNull('reexposeItem_id')
            emptyDateOrNumber = item.isNull('date') or item.value('number').toString().isEmpty()
            if reexposed and not emptyDateOrNumber:
                QtGui.QMessageBox.critical(
                    parent,
                    u'Внимание!',
                    u'Нельзя изменить данные о подтверждении для перевыставленных записей реестра.',
                    QtGui.QMessageBox.Ok,
                    QtGui.QMessageBox.Ok
                )
            else:
                item.setValue('date', date)
                item.setValue('number', number)
                if not reexposed:
                    item.setValue('refuseType_id', refuseTypeId)
                    updateDocsPayStatus(item, contractInfo.payStatusMask, bits)
                item.setValue('note', note)
                db.updateRecord(table, item)
                accountId = forceRef(item.value('master_id'))
                accountIdList.add(accountId)
        updateAccounts(list(accountIdList))
        db.commit()
        result = True
    except:
        db.rollback()
        QtGui.qApp.logCurrentException()
        raise
    return result


def setPayment(parent, accountId, accountItemsList, payParams):
    result = False
    isAccountant = QtGui.qApp.userHasAnyRight(accountantRightList)
    if isAccountant:
        contractId = forceRef(QtGui.qApp.db.translate(
            'Account', 'id', accountId, 'contract_id'
        ))
        financeId = forceRef(QtGui.qApp.db.translate('Contract', 'id', contractId, 'finance_id'))
        if accountItemsList:
            dialog = CPayStatusDialog(parent, financeId)
            dialog.setAccountItemsCount(len(accountItemsList))
            dialog.setParams(payParams)
            if dialog.exec_():
                payParams.update(dialog.params())
                result = setPayStatus(parent, getContractInfo(contractId), accountItemsList, payParams)
    return result


def editPayment(parent, accountId, accountItemId, payParams):
    result = False
    isAccountant = QtGui.qApp.userHasAnyRight(accountantRightList)
    if isAccountant:
        contractId = forceRef(QtGui.qApp.db.translate('Account', 'id', accountId, 'contract_id'))
        financeId = forceRef(QtGui.qApp.db.translate('Contract', 'id', contractId, 'finance_id'))
        if accountItemId:
            dialog = CPayStatusDialog(parent, financeId)
            dialog.setAccountItemsCount(1)
            dialog.setParams(payParams)
            if dialog.exec_():
                payParams.update(dialog.params())
                result = setPayStatus(parent, getContractInfo(contractId), [accountItemId], payParams)
    return result


def registerCheckInECR(accountingDialog, franchisePercent=0.0):
    from Orgs.TariffModel import CTariffModel
    if not accountingDialog.currentAccountId:
        return

    from library.CashRegister.CashRegisterWindow import getECashRegister
    accountItemIdList = accountingDialog.modelAccountItems.idList()
    context = CInfoContext()
    accountInfo = context.getInstance(CAccountInfo, accountingDialog.currentAccountId)
    checkItems = []
    clientInfo = None
    clientInfoIdSet = set()

    actionTypeIdList = set()
    serviceCodeList = set()
    itemsCashFlowArticle = u'Медицинские услуги'
    serviceName = u''

    for item in accountInfo.items:
        # Если элемента нет среди отображаемых в окне, то пропустить
        if item.id not in accountItemIdList:
            continue
        serviceName = item.service.name
        itemName = item.service.name + (' (%s)' % item.service.code) if item.service.code else ''
        if item.action:
            actionTypeIdList.add(item.action.typeId)
        serviceCodeList.add(item.service.code)
        payStatus = CPayStatus.refused if item.refuseType else CPayStatus.payed if item.date else CPayStatus.exposed
        clientInfo = item.event.client
        clientInfoIdSet.add(item.event.client.id)
        vatIndex = forceInt(QtGui.qApp.db.translate('Contract_Tariff', 'id', item.tariff_id, 'vat'))

        checkItems.append(CCheckItem(
            itemName,
            item.amount,
            item.price if not franchisePercent else item.price * franchisePercent / 100.0,
            payStatus=payStatus,
            userInfo=item.id,
            vat=CTariffModel.vat_values[vatIndex],
            clientId=clientInfo.id
        ))

    # Если все услуги имеют одинаковый код
    if len(serviceCodeList) == 1:
        itemsCashFlowArticle = serviceName
    else:
        tableActionType = QtGui.qApp.db.table('ActionType')
        commonActionTypeId = QtGui.qApp.db.getCommonParent(table=tableActionType,
                                                           idList=actionTypeIdList,
                                                           groupCol='group_id')
        if commonActionTypeId:
            itemsCashFlowArticle = forceString(QtGui.qApp.db.translate(tableActionType,
                                                                       tableActionType['id'],
                                                                       commonActionTypeId,
                                                                       'name'))

    ecrDialog = getECashRegister(accountingDialog)
    ecrDialog.setItems(checkItems)

    exportInfo = {
        'itemsCashFlowArticle': itemsCashFlowArticle,
        'substructure': COrgStructureInfo(CInfoContext(), QtGui.qApp.currentOrgStructureId()).name
    }

    if accountInfo.contract.payer.id != QtGui.qApp.currentOrgId():
        exportInfo.update({
            'personName': accountInfo.contract.payer.shortName,
            'isNaturalPerson': False,
            'personINN': '/'.join([accountInfo.contract.payer.INN,
                                   accountInfo.contract.payer.KPP]) if accountInfo.contract.payer.INN else ''

        })
    elif len(clientInfoIdSet) == 1:
        documentType = clientInfo.document.documentType
        documentTypeList = [documentType] if documentType else [u'паспорт']
        exportInfo.update({
            'personName': clientInfo.fullName,
            'isNaturalPerson': True,
            'documenTypeList': documentTypeList,
            'documentTypeIndex': 0,
            'documentSerial': clientInfo.document.serial,
            'documentNumber': clientInfo.document.number,
            'documentIssuedDate': clientInfo.document.date.date,
            'documentIssued': clientInfo.document.origin
        })
    ecrDialog.setExportInfo(exportInfo)
    ecrDialog.addInfoForPrint('account', accountInfo)
    ecrDialog.exec_()
    setPref(QtGui.qApp.preferences.appPrefs, 'ECRSettings', ecrDialog.preferences())

    contractInfo = getContractInfo(accountInfo.contract.id)

    for item in ecrDialog.items():
        itemId = forceInt(item.userInfo)
        if not item.payStatusChanged or not item.lastCheckInfo or not itemId:
            continue

        checkNumber = u'Чек №%08d' % item.lastCheckInfo['CheckNumber']
        checkAdditionalInfo = u'тип чека: %s\nзакрыт: %s\nтип оплаты: %s' % (
            CCashRegisterDriverInfo.CheckType.title(item.lastCheckInfo['CheckType']),  # наименование типа чека
            item.lastCheckInfo['CloseDatetime'].toString('hh:mm dd.MM.yyyy'),
            item.lastCheckInfo['CloseType']
        )

        date = item.lastCheckInfo.get(u'CloseDatetime', QtCore.QDateTime()).date()
        payParams = {
            'date': date if item.payStatus == CPayStatus.payed else QtCore.QDate(),
            'number': checkNumber if item.payStatus == CPayStatus.payed else u'',
            'note': '\n'.join([checkNumber, checkAdditionalInfo]),
            'accepted': True if item.payStatus != CPayStatus.refused else False,
            'refuseTypeId': None
        }

        setPayStatus(accountingDialog, contractInfo, [itemId], payParams)


# TODO: проверить, что будет, если начать формировать счета параллельно с двух разных соединений.
def getNextAccountNumber(contractNumber):
    """
    Функция генерирует новый номер для счета по одному договору с указанием тиража для первого счета в серии.
    Номер счета формируется, как contractNumber-#, где # - порядковый номер счета.

    @param contractNumber: базовый номер счета.
    @return: актуальный номер счета.
    """
    stmt = 'SELECT MAX(CAST(SUBSTR(number, %d) AS SIGNED)) AS seqNumber FROM Account WHERE number LIKE \'%s-%%\'' % (
        len(contractNumber) + 2, contractNumber
    )
    query = QtGui.qApp.db.query(stmt)
    if query.first():
        lastSeqNumber = forceInt(query.record().value('seqNumber'))
    else:
        lastSeqNumber = 0
    return u'%s-%d' % (contractNumber, lastSeqNumber + 1)


def getNextAccountNumberFromZero(contractNumber, dbName=None):
    """
    Функция генерирует новый номер для счета по одному договору без указания тиража для первого счета в серии.
    Номер первого счета серии должен быть равным contractNumber, последующие - contractNumber-#,
    где # - порядковый номер счета-1.

    @param contractNumber: базовый номер счета.
    @return: актуальный номер счета.
    """
    dbName = dbName if dbName else forceString(QtGui.qApp.db.db.databaseName())
    db = QtGui.qApp.db
    stmt = 'SELECT MAX(CAST(SUBSTR(number, %d) AS SIGNED)) AS seqNumber FROM ' + dbName + '.Account WHERE number LIKE \'%s-%%\''
    query = db.query(stmt % (len(contractNumber) + 2, contractNumber))
    if query.first() and not query.record().isNull(0):
        lastSeqNumber = forceInt(query.record().value('seqNumber'))
        return u'%s-%d' % (contractNumber, lastSeqNumber + 1)
    else:
        stmt = 'SELECT Account.id FROM ' + dbName + '.Account WHERE number LIKE \'%s\'' % contractNumber
        query = db.query(stmt)
        if query.first():
            return u'%s-1' % contractNumber
        return contractNumber


def updateAccount(accountId, dbName=None):
    dbName = dbName if dbName else forceString(QtGui.qApp.db.db.databaseName())
    QtGui.qApp.db.query('CALL ' + dbName + '.updateAccount(%d);' % accountId)


def updateAccounts(accountIdList, dbName=None):
    for accountId in accountIdList:
        updateAccount(accountId, dbName)


def updateAccountInfo(accountId, **kwargs):
    if not kwargs: return
    db = QtGui.qApp.db
    tableAccount = db.table('Account')
    expr = [tableAccount[field].eq(value) for field, value in kwargs.iteritems()]
    db.updateRecords(tableAccount, expr, tableAccount['id'].eq(accountId))


def setEventPayStatus(eventId, payStatusMask, bits):
    if hasattr(QtGui.qApp, 'dontTouchPayStatus') and QtGui.qApp.dontTouchPayStatus:
        return

    stmt = u'UPDATE Event SET payStatus = ((payStatus & ~%d) | %d) WHERE id=%d''' % \
           (payStatusMask, payStatusMask & bits, eventId)
    QtGui.qApp.db.query(stmt)


def isTariffApplicable(tariff, eventId, tariffCategoryId, date, actualMKB='', mapEventIdToMKB=None):
    if tariff.tariffCategoryId and tariffCategoryId != tariff.tariffCategoryId:
        return False
    if not tariff.dateInRange(date):
        return False
    sex = tariff.sex
    ageSelector = tariff.ageSelector
    eventTypeId = tariff.eventTypeId
    attachTypeId = tariff.attachTypeId
    attachLpuId = tariff.attachLpuId
    if sex or ageSelector or eventTypeId or attachTypeId:
        eventRecord = QtGui.qApp.db.getRecord('Event', ['eventType_id', 'client_id', 'execDate'], eventId)
        if eventRecord:
            if eventTypeId and eventTypeId != forceRef(eventRecord.value('eventType_id')):
                return False
            if not date:
                date = forceDate(eventRecord.value('execDate'))
            if sex or ageSelector or attachTypeId:
                clientId = forceRef(eventRecord.value('client_id'))
                clientRecord = QtGui.qApp.db.getRecord('Client', ['sex', 'birthDate'], clientId) if clientId else None
                if clientRecord:
                    clientSex = forceInt(clientRecord.value('sex'))
                    if sex and sex != clientSex:
                        return False
                    if ageSelector:
                        clientBirthDate = forceDate(clientRecord.value('birthDate'))
                        clientAge = calcAgeTuple(clientBirthDate, date)
                        if not clientAge:
                            clientAge = (0, 0, 0, 0)
                        if not checkAgeSelector(ageSelector, clientAge):
                            return False
                else:
                    return False
                if attachTypeId:  # issue 447 (Задача №2).
                    attachRecord = QtGui.qApp.db.getRecordEx(
                        'ClientAttach', '*',
                        'attachType_id = %d AND client_id = %d' % (attachTypeId, clientId),
                        'id DESC'
                    )
                    if attachRecord:
                        # Если для услуги указан Тип и ЛПУ прикрепления,
                        # то не учитывать ее для клиентов с таким прикреплением
                        if attachLpuId and attachLpuId == forceRef(attachRecord.value('LPU_id')):
                            return False
                        # Если для услуги указан только Тип,
                        # то не учитывать ее для клиентов с таким типом прикрепления
                        if not attachLpuId:
                            return False
        else:
            return False
    if tariff.MKB:
        if actualMKB:
            MKB = actualMKB
        else:
            if mapEventIdToMKB:
                eventMKB = mapEventIdToMKB.get(eventId, None)
                if eventMKB is None:
                    eventMKB = getEventDiagnosis(eventId)
                    mapEventIdToMKB[eventId] = eventMKB
                MKB = eventMKB
            else:
                MKB = getEventDiagnosis(eventId)
        if not tariff.matchMKB(MKB):
            return False
    return True


## Проверяет на наличии неудаленного(-ых) счета (-ов) по обращению с id равным evnetId
# @param eventId: id обращения
# @return: True, если есть хотя бы один счет по указанному обращению. Иначе False
def isEventPresenceInAccounts(eventId, db=None):
    if not db:
        db = QtGui.qApp.db
    tableAccountItem = db.table('Account_Item')
    if db.getIdList(tableAccountItem, 'id', [tableAccountItem['deleted'].eq(0),
                                             tableAccountItem['event_id'].eq(eventId)]):
        return True
    return False


def getEventPayStatusByRecord(eventRecord, contractId=None):
    u"""
    Получение значения статуса оплаты для обращения с учетом метода формирования счета по нему
    Для событий, тарифицируемых целиком, статус оплаты берется из поля payStatus таблицы Event.
    Для событий, тарифицируемых в виде отдельных счетов по каждому внутреннему действию и/или посещению
    payStatus вычисляется на основе Action.payStatus и Visit.payStatus.

    :param eventRecord: запись базы данных таблицы Event (QSqlRecord)
    :param contractId: id договора, к которому прикрепленно обращение (если None, то берется из eventRecord.contract_id)
    :return: битовую последовательсть, обозначающую статус оплаты по каждому типу финансирования, в виде целого числа
    """
    payStatus = 0
    if contractId is None:
        contractId = forceRef(eventRecord.value('contract_id'))
    if contractId:
        contractInfo = getContractInfo(contractId)
        eventTypeId = forceRef(eventRecord.value('eventType_id'))
        eventId = forceRef(eventRecord.value('id'))
        isRatedEvent = False  # Тарифицируется ли событие (проставляется ли payStatus у события при формировании счетов)
        tariffList = []

        if contractInfo.tariffByEventType:
            tariffList.extend(contractInfo.tariffByEventType.get(eventTypeId, []))
        elif contractInfo.tariffByCoupleVisitEventType:
            tariffList.extend(contractInfo.tariffByHospitalBedDay.get(eventTypeId, []))
        elif contractInfo.tariffByHospitalBedDay:
            tariffList.extend(contractInfo.tariffByHospitalBedDay.get(eventTypeId, []))
        elif contractInfo.tariffVisitsByMES or contractInfo.tariffEventByMES:
            mesId = forceRef(eventRecord.value('MES_id'))
            if mesId:
                mesCode = QtGui.qApp.db.translate('mes.MES', 'id', mesId, 'code')
                serviceId = forceRef(QtGui.qApp.db.translate('rbService', 'code', mesCode, 'id'))
                tariffList.extend(contractInfo.tariffVisitsByMES.get((eventTypeId, serviceId), []))
                tariffList.extend(contractInfo.tariffEventByMES.get((eventTypeId, serviceId), []))

        if tariffList:
            for tariff in tariffList:
                tariffCategoryId = forceRef(eventRecord.value('tariffCategory_id'))
                eventEndDate = forceDateTime(eventRecord.value('execDate'))
                if isTariffApplicable(tariff, eventId, tariffCategoryId, eventEndDate):
                    isRatedEvent = True
                    break
        # Если событие тарифицируется, то взять paySTatus из базы
        if isRatedEvent:
            payStatus = forceRef(eventRecord.value('contract_id'))
        # Иначе расчитать payStatus
        else:
            eventPayStatus = CPayStatus.payedBits  # Изначально считать событие оплаченным (все пары == 0b11)
            # Есть необходимость менять статус оплаты события
            # (чтобы не установить статус в "оплачено" в случае, когда ни один визит и ни одно действие не обработано)
            isNeedChangeEventPayStatus = False
            actionRecordList = QtGui.qApp.db.getRecordList(
                'Action',
                ['id', 'payStatus', 'contract_id', 'finance_id', 'actionType_id'],
                where='event_id = %d AND deleted = 0' % eventId
            )

            eventFinanceId = contractInfo.finance_id
            # Получение списка всех тарифицируемых услуг для договора обращения
            eventContractTariffServiceIdList = QtGui.qApp.db.getIdList(
                'Contract_Tariff', 'service_id',
                where='deleted = 0 AND master_id = %d' % contractId
            )
            # результатом переборов по действиям и посещениям в нужной позиции eventPayStatus будет пара бит
            # 0b00 (нет статуса): если есть и выставленные (0b01) и отказанные (0b10) и оплаченные (0b11)
            # или хотя бы одно без статуса (0b00)
            # 0b01 (выставлено): если есть хотя бы одно выставленные(0b01) и остальные оплаченные (0b11)
            # 0b10 (отказано): если есть хотя бы одно отказанные(0b10) и остальные оплаченные (0b11)
            # 0b11 если все оплачены(0b11)
            for actionRecord in actionRecordList:
                actionId = forceInt(actionRecord.value('id'))
                actionFinanceId = forceRef(
                    QtGui.qApp.db.translate('Action', 'id', actionId, 'finance_id')) or eventFinanceId
                actionTypeId = forceRef(QtGui.qApp.db.translate('Action', 'id', actionId, 'actionType_id'))
                # Получение списка услуг, привязанных к типу действия
                serviceIdList = QtGui.qApp.db.getIdList(
                    'ActionType_Service', 'service_id',
                    where='master_id = %d AND (finance_id = %d OR finance_id IS NULL)' % (
                        actionTypeId, actionFinanceId
                    ),
                    order='service_id DESC',
                    limit=1
                )
                if serviceIdList:
                    actionContractId = forceRef(QtGui.qApp.db.translate('Action', 'id', actionId, 'contract_id'))
                    contractTariffServiceIdList = []
                    if actionContractId and actionContractId != contractId:  # Если у услуги отдельный договор
                        # Получение списка услуг, тарифицируемых договором типа действия
                        contractTariffServiceIdList = QtGui.qApp.db.getIdList(
                            'Contract_Tariff', 'service_id',
                            where='deleted = 0 AND master_id = %d' % actionContractId
                        )
                    else:
                        contractTariffServiceIdList = eventContractTariffServiceIdList
                    # Если первая из привязанных к типу действия услуг содержится в списке тарифицируемых услуг,
                    # то расчитать статус оплаты
                    if serviceIdList[0] in contractTariffServiceIdList:
                        isNeedChangeEventPayStatus = True
                        eventPayStatus &= forceInt(actionRecord.value('payStatus'))

            visitRecordList = QtGui.qApp.db.getRecordList(
                'Visit',
                ['id', 'payStatus', 'service_id'],
                where='event_id = %d AND deleted = 0' % eventId
            )
            for visitRecord in visitRecordList:
                visitServiceId = forceRef(visitRecord.value('service_id'))
                if visitServiceId in eventContractTariffServiceIdList:
                    isNeedChangeEventPayStatus = True
                    eventPayStatus &= forceInt(visitRecord.value('payStatus'))

            eventPayStatus &= contractInfo.payStatusMask
            if isNeedChangeEventPayStatus:
                payStatus = eventPayStatus
    return payStatus


def getEventPayStatusById(eventId):
    record = QtGui.qApp.getRecord('Event', '*', eventId)
    return getEventPayStatusByRecord(record)


def setEventVisitsPayStatus(eventId, payStatusMask, bits):
    if hasattr(QtGui.qApp, 'dontTouchPayStatus') and QtGui.qApp.dontTouchPayStatus:
        return

    stmt = u'UPDATE Visit SET payStatus = ((payStatus & ~%d) | %d) WHERE event_id=%d''' % \
           (payStatusMask, payStatusMask & bits, eventId)
    QtGui.qApp.db.query(stmt)


def setVisitPayStatus(id, payStatusMask, bits):
    if hasattr(QtGui.qApp, 'dontTouchPayStatus') and QtGui.qApp.dontTouchPayStatus:
        return

    stmt = u'UPDATE Visit SET payStatus = ((payStatus & ~%d) | %d) WHERE id=%d''' % \
           (payStatusMask, payStatusMask & bits, id)
    QtGui.qApp.db.query(stmt)


def setActionPayStatus(id, payStatusMask, bits):
    if hasattr(QtGui.qApp, 'dontTouchPayStatus') and QtGui.qApp.dontTouchPayStatus:
        return

    stmt = u'UPDATE Action SET payStatus = ((payStatus & ~%d) | %d) WHERE id=%d''' % \
           (payStatusMask, payStatusMask & bits, id)
    QtGui.qApp.db.query(stmt)


def updateDocsPayStatus(accountItem, payStatusMask, bits):
    actionId = forceRef(accountItem.value('action_id'))
    if actionId:
        setActionPayStatus(actionId, payStatusMask, bits)
        return

    visitId = forceRef(accountItem.value('visit_id'))
    if visitId:
        setVisitPayStatus(visitId, payStatusMask, bits)
        return

    eventId = forceRef(accountItem.value('event_id'))
    if eventId:
        setEventPayStatus(eventId, payStatusMask, bits)


def removeAccountItems(items):
    CLEAR_PAYSTATUS = u"""
            UPDATE 
                {table} INNER JOIN Account_Item ai ON ai.{field} = {table}.id
            SET 
                {table}.payStatus = 0
            WHERE 
                ai.id IN ({items})
            """
    IS_EVENT_PAYSTATUS_CLEAR = u"""
    SELECT 
        Event.id
    FROM 
        Event 
        INNER JOIN Account_Item ai ON ai.event_id = Event.id
    WHERE 
        ai.id IN ({items})
        AND 0 = ALL (
            SELECT Action.payStatus FROM Action WHERE Action.event_id = Event.id
        ) AND 0 = ALL (
            SELECT Visit.payStatus FROM Visit WHERE Visit.event_id = Event.id
        );
    """

    db = QtGui.qApp.db
    tableAccountItem = db.table('Account_Item')
    db.markRecordsDeleted(tableAccountItem, tableAccountItem['id'].inlist(items))

    cond = ', '.join(map(str, items))
    # clear paystatus
    db.query(CLEAR_PAYSTATUS.format(table='Action', field='action_id', items=cond))
    db.query(CLEAR_PAYSTATUS.format(table='Visit', field='visit_id', items=cond))
    if db.getRecordEx(stmt=IS_EVENT_PAYSTATUS_CLEAR.format(items=cond)):
        db.query(CLEAR_PAYSTATUS.format(table='Event', field='event_id', items=cond))


def clearPayStatus(accountId, accountItemIdList=None):
    if not accountItemIdList:
        accountItemIdList = []
    db = QtGui.qApp.db
    contractId = forceRef(db.translate('Account', 'id', accountId, 'contract_id'))
    financeId = forceRef(db.translate('Contract', 'id', contractId, 'finance_id'))
    payStatusMask = getPayStatusMask(financeId)
    table = db.table('Account_Item')
    cond = []
    cond.append(table['master_id'].eq(accountId))
    if accountItemIdList:
        cond.append(table['id'].inlist(accountItemIdList))
    cond = db.joinAnd(cond)

    stmt = u'''UPDATE Event, Account_Item
               SET Event.payStatus = (Event.payStatus & ~%s) |
                   IF(EXISTS (SELECT id FROM Account_Item AS AI WHERE AI.master_id != %d AND AI.deleted = 0 AND AI.event_id = Event.id AND AI.visit_id IS NULL AND AI.action_id IS NULL), %d, 0)
               WHERE %s AND Account_Item.event_id = Event.id AND Account_Item.deleted = 0 AND Account_Item.visit_id IS NULL AND Account_Item.action_id IS NULL''' \
           % (payStatusMask, accountId, getExposed(payStatusMask), cond)
    db.query(stmt)
    stmt = u'''UPDATE Visit, Account_Item
               SET Visit.payStatus = (Visit.payStatus & ~%s) |
                   IF(EXISTS (SELECT id FROM Account_Item AS AI WHERE AI.master_id != %d AND AI.deleted = 0 AND AI.visit_id = Visit.id), %d, 0)
               WHERE %s AND Account_Item.visit_id = Visit.id AND Account_Item.deleted = 0''' \
           % (payStatusMask, accountId, getExposed(payStatusMask), cond)
    db.query(stmt)
    stmt = u'''UPDATE Action, Account_Item
               SET Action.payStatus = (Action.payStatus & ~%s) |
                   IF(EXISTS (SELECT id FROM Account_Item AS AI WHERE AI.master_id != %d AND AI.deleted = 0 AND AI.action_id = Action.id), %d, 0)
               WHERE %s AND Account_Item.action_id = Action.id AND Account_Item.deleted = 0''' \
           % (payStatusMask, accountId, getExposed(payStatusMask), cond)
    db.query(stmt)


def canRemoveAccount(accountId):
    db = QtGui.qApp.db
    tableAI = db.table('Account_Item')
    cond = [
        tableAI['master_id'].eq(accountId),
        tableAI['date'].isNotNull(),
        tableAI['number'].ne('')
    ]
    record = db.getRecordEx(tableAI, db.count(tableAI['id']), cond)
    return record and forceInt(record.value(0)) == 0


def getContractExportFormat(contractId):
    prog = u''
    db = QtGui.qApp.db
    formatId = forceRef(db.translate('Contract', 'id', contractId, 'format_id'))
    if formatId:
        prog = forceString(db.translate('rbAccountExportFormat', 'id', formatId, 'prog'))
    return prog


def getAccountExportFormat(accountId):
    prog = u''
    db = QtGui.qApp.db
    formatId = forceRef(db.translate('Account', 'id', accountId, 'format_id'))
    if not formatId:
        contractId = forceRef(db.translate('Account', 'id', accountId, 'contract_id'))
        formatId = forceRef(db.translate('Contract', 'id', contractId, 'format_id'))
    if formatId:
        prog = forceString(db.translate('rbAccountExportFormat', 'id', formatId, 'prog'))
    return prog


def isShowJobTickets(jobId, actionId, debug=False):
    u"""
    Проверяет, нужно ли выводить номерок в список
    (если EventType.isOnJobPayedFilter = 1 и rbjobtype.showOnlyPayed = 1 то выводит только оплаченные)

    atronah for issue 317
    """
    result = True
    try:
        db = QtGui.qApp.db
        tblEvent = db.table('Event')
        tblEventType = db.table('EventType')
        tblAction = db.table('Action')
        # Узнаем тип указанного события
        # Узнаем тип указанной работы
        queryTable = tblAction.innerJoin(tblEvent, tblEvent['id'].eq(tblAction['event_id']))
        queryTable = queryTable.innerJoin(tblEventType, tblEventType['id'].eq(tblEvent['eventType_id']))
        actionRecord = db.getRecordEx(
            queryTable,
            'EventType.isOnJobPayedFilter, Action.payStatus, Action.contract_id',
            [tblAction['id'].eq(actionId)]
        )

        # Узнаем, стоит ли для данного типа события учитывать настройки работ по оплате при формировании списка
        isOnJobFilter = forceBool(actionRecord.value('isOnJobPayedFilter'))
        if isOnJobFilter:  # Если стоит учитывать настройки, то вытаскиваем эти настройки
            tblJob = db.table('Job')
            tblJobType = db.table('rbJobType')
            queryTable = tblJob.innerJoin(tblJobType, tblJobType['id'].eq(tblJob['jobType_id']))
            record = db.getRecordEx(queryTable, tblJobType['showOnlyPayed'], [tblJob['id'].eq(jobId)])
            showOnlyPayed = forceBool(record.value('showOnlyPayed'))
            if showOnlyPayed:  # Если в настройках работы указано показывать только оплаченные
                # вернуть истину, если событие оплачено или включено игнорирование оплаты у контракта
                if getRealPayed(forceInt(actionRecord.value('payStatus'))):
                    result = True
                elif forceBool(db.translate(
                        'Contract', 'id', forceRef(actionRecord.value('contract_id')), 'ignorePayStatusForJobs'
                )):
                    result = True
                else:
                    result = False
    finally:
        return result


def getClientDiscountInfo(clientId):
    u"""
    Определение скидки для пациента на основании родства с сотрудником ЛПУ

    :param clientId: ID пациента, на которого проверяется скидка
    :return: (DiscountSize, StaffId, DiscountNote) Кортеж из размера скидки, ID сотрудника и причины скидки
    """
    discountNote = u'-'
    # получение параметров скидок из глобальных настроек
    lowThan, lowDiscount, leftBound, rightBound, middleDiscount, highThan, highDiscount, relativeTypeCodeList = QtGui.qApp.getDiscountParams()

    if lowDiscount == middleDiscount == highDiscount:
        return (lowDiscount, None, u'Одинаковая скидка для всех')

    db = QtGui.qApp.db
    tableClientRelation = db.table('ClientRelation')
    tableClientWork = db.table('ClientWork')
    tableRelationType = db.table('rbRelationType')
    relativeTypeIdList = db.getIdList(
        tableRelationType, 'id',
        where=tableRelationType['code'].inlist(relativeTypeCodeList)
    ) if relativeTypeCodeList else []
    inClientRelationIdList = db.getIdList(
        tableClientRelation, 'relative_id',
        where=[
            tableClientRelation['relativeType_id'].inlist(relativeTypeIdList) if relativeTypeIdList else '1',
            tableClientRelation['client_id'].eq(clientId)
        ]
    )
    hasClientInRealtionIdList = db.getIdList(
        tableClientRelation, 'client_id',
        where=[
            tableClientRelation['relativeType_id'].inlist(relativeTypeIdList) if relativeTypeIdList else '1',
            tableClientRelation['relative_id'].eq(clientId)
        ]
    )
    staffIdList = db.getIdList(
        tableClientWork, 'client_id',
        where=[tableClientWork['org_id'].eq(QtGui.qApp.currentOrgId())]
    )
    relativeStaff = list(set([clientId] + inClientRelationIdList + hasClientInRealtionIdList) & set(staffIdList))
    relativeMaxStageList = db.getRecordList(
        table=tableClientWork,
        cols=[tableClientWork['stage'], tableClientWork['client_id']],
        where=[tableClientWork['client_id'].inlist(relativeStaff)],
        order=['%s DESC' % tableClientWork['stage'].name()]
    )
    relativeMaxStage = forceInt(relativeMaxStageList[0].value('stage')) if relativeMaxStageList else 0
    relativeMaxStageStaffId = forceRef(relativeMaxStageList[0].value('client_id')) if relativeMaxStageList else None

    if clientId == relativeMaxStageStaffId:
        discountNote = u'Сотрудник (стаж: %d)' % relativeMaxStage
    elif relativeMaxStageStaffId is not None:
        staffInfo = getClientInfo(relativeMaxStageStaffId)
        staffName = formatName(staffInfo.lastName, staffInfo.firstName, staffInfo.patrName)
        discountNote = u'%s (стаж: %d)' % (staffName, relativeMaxStage)

    if relativeMaxStage < lowThan:
        return (lowDiscount, relativeMaxStageStaffId, discountNote)
    elif leftBound <= relativeMaxStage <= rightBound:
        return (middleDiscount, relativeMaxStageStaffId, discountNote)
    elif relativeMaxStage >= highThan:
        return (highDiscount, relativeMaxStageStaffId, discountNote)

    return (0.0, None, discountNote)


class CContractTreeView(QtGui.QTreeView, CPreferencesMixin):
    def processPrefs(self, model, preferences, load, parent=QtCore.QModelIndex(), prefix=''):
        for i in xrange(model.columnCount(parent)):
            for j in xrange(model.rowCount(parent)):
                index = model.index(j, i, parent)
                if index.isValid():
                    prefix += index.internalPointer().name + '_'
                    if load:
                        self.setExpanded(
                            index,
                            forceBool(getPref(preferences, prefix + 'col_' + str(i) + '_row_' + str(j), True))
                        )
                    else:
                        setPref(
                            preferences,
                            prefix + 'col_' + str(i) + '_row_' + str(j),
                            QtCore.QVariant(self.isExpanded(index))
                        )
                if index.isValid():
                    self.processPrefs(model, preferences, load, index, prefix)

    def loadPreferences(self, preferences):
        model = self.model()

        if model and isinstance(model, CContractTreeModel):
            self.processPrefs(model, preferences, True)

    def savePreferences(self):
        preferences = {}
        model = self.model()

        if model and isinstance(model, CContractTreeModel):
            self.processPrefs(model, preferences, False)

        return preferences


class CContractTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None, financeTypeCodeList=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.contracts = {}
        self.financeTypeCodeList = financeTypeCodeList
        self._rootItem = CContractRootTreeItem()
        self.loadData()

    def setContractDates(self, begDate, endDate):
        self._rootItem = CContractRootTreeItem()
        self._rootItem.setDates(begDate, endDate)
        self.contracts = {}
        self._rootItem.loadData(self.contracts, self.financeTypeCodeList)
        self.reset()

    def setFinaceTypeCodes(self, financeTypeCodeList):
        self.financeTypeCodeList = financeTypeCodeList
        self._rootItem = CContractRootTreeItem()
        self.contracts = {}
        self._rootItem.loadData(self.contracts, self.financeTypeCodeList)
        self.reset()

    def emitDataChanged(self):
        leftTop = self.index(0, 0)
        rightBottom = self.index(self.rowCount(self._rootItem.index(0, 0)), self.columnCount())
        self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), leftTop, rightBottom)

    def getPathById(self, contractId):
        return self.getRootItem().getPathById(contractId)

    def getIdByPath(self, path):
        return self.getRootItem().getIdByPath(path)

    def getRootItem(self):
        return self._rootItem

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        item = index.internalPointer()
        return QtCore.QVariant(item.data(index.column()))

    def flags(self, index):
        if not index.isValid():
            return 0
        item = index.internalPointer()
        return item.flags()

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if parent and parent.isValid():
            parentItem = parent.internalPointer()
            childItem = parentItem.child(row)
            return self.createIndex(row, column, childItem)
        else:
            return self.createIndex(0, 0, self.getRootItem())

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()
        childItem = index.internalPointer()
        parentItem = childItem.parent
        if not parentItem:
            return QtCore.QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent and parent.isValid():
            parentItem = parent.internalPointer()
            return parentItem.childCount()
        else:
            return 1

    def loadData(self):
        if QtGui.qApp.db is not None and QtGui.qApp.db.isValid():
            self._rootItem.loadData(self.contracts, self.financeTypeCodeList)


class CContractTreeItem(object):
    def __init__(self, name, parent):
        self.name = name
        self.items = []
        self.idList = []
        self.mapNameToItem = {}
        self.parent = parent

    def addItem(self, path, depth, contractId):
        self.idList.append(contractId)
        if depth < len(path):
            name = path[depth]
            if self.mapNameToItem.has_key(name):
                child = self.mapNameToItem[name]
            else:
                child = CContractTreeItem(name, self)
                self.items.append(child)
                self.mapNameToItem[name] = child
            child.addItem(path, depth + 1, contractId)

    def child(self, row):
        return self.items[row]

    def childCount(self):
        return len(self.items)

    def columnCount(self):
        return 1

    def data(self, column):
        return QtCore.QVariant(self.name)

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def row(self):
        if self.parent:
            return self.parent.items.index(self)
        return 0


class CContractRootTreeItem(CContractTreeItem):
    def __init__(self):
        CContractTreeItem.__init__(self, u'Все договоры', None)
        self._contractIdToPath = {}
        self._pathToContractId = {}
        today = QtCore.QDate.currentDate()
        self.begDate = QtCore.QDate(today.year(), 1, 1)
        self.endDate = QtCore.QDate(today.year(), 12, 31)

    def setDates(self, begDate, endDate):
        self.begDate = begDate
        self.endDate = endDate

    def loadData(self, contracts, financeTypeCodeList=None):
        db = QtGui.qApp.db
        table = db.table('Contract')
        cond = []
        # cond =.append(table['recipient_id'].eq(QtGui.qApp.currentOrgId()))  #Временно убранно по просьбе симы 200912
        if financeTypeCodeList:
            cond.append(table['finance_id'].inlist([CFinanceType.getId(code) for code in financeTypeCodeList]))
        if self.begDate and self.endDate:
            cond.append(u'''(Contract.begDate >= %(begDate)s AND Contract.begDate < %(endDate)s )
OR (Contract.begDate <= %(begDate)s AND Contract.endDate > %(begDate)s )''' % {'begDate': db.formatDate(self.begDate),
                                                                               'endDate': db.formatDate(self.endDate)})
        elif self.begDate:
            cond.append(table['begDate'].isNotNull())
            cond.append(db.joinOr([table['begDate'].dateGe(self.begDate), db.joinAnd(
                [table['begDate'].dateLe(self.begDate), table['endDate'].dateGe(self.begDate)])]))
        elif self.endDate:
            cond.append(table['begDate'].isNotNull())
            cond.append(table['begDate'].dateLe(self.endDate))
        cond.append(db.joinOr([table['typeId'].isNull(),
                               'Contract.typeId not IN (select id from rbContractType where code in (\'clearing\', \'clinicalTest\'))']))
        records = db.getRecordList(table,
                                   'id, finance_id, grouping, resolution, date, number',
                                   where=db.joinAnd(cond),
                                   order='finance_id, grouping, resolution, date, number, id')
        for record in records:
            contractId = forceRef(record.value('id'))
            contractName = forceString(record.value('number')) + u' от ' + forceString(record.value('date'))
            path = [
                self.getFinanceName(record.value('finance_id')),
                forceString(record.value('grouping')),
                forceString(record.value('resolution')),
                contractName
            ]
            self.addItem(path, 0, contractId)
            contracts[contractId] = contractName
            self._contractIdToPath[contractId] = path
            self._pathToContractId['\\'.join(path)] = contractId

    def getPathById(self, contractId):
        return self._contractIdToPath.get(contractId, '')

    def getIdByPath(self, path):
        return self._pathToContractId.get(path, None)

    def getFinanceName(self, val):
        financeId = forceRef(val)
        financeRecord = QtGui.qApp.db.getRecord('rbFinance', 'name', financeId)
        if financeRecord:
            return forceString(financeRecord.value(0))
        else:
            return '{%s}' % financeId


class CAccountsModel(CTableModel):
    def __init__(self, parent):
        cols = [
            CDesignationCol(u'Плательщик', ['payer_id'], ('Organisation', 'shortName'), 12),
            CDateCol(u'Расчётная дата', ['settleDate'], 20),
            CDateCol(u'Дата создания', ['createDatetime'], 20),
            CTextCol(u'Номер', ['number'], 20),
            CDateCol(u'Дата', ['date'], 20),
            CNumCol(u'Количество', ['amount'], 20, 'r'),
            CNumCol(u'УЕТ', ['uet'], 20, 'r'),
            CSumCol(u'Сумма', ['sum'], 20, 'r'),
            CSumCol(u'Оплачено', ['payedSum'], 20, 'r'),
            CSumCol(u'Отказано', ['refusedSum'], 20, 'r'),
            CDateCol(u'Дата выставления', ['exposeDate'], 20),
            CDesignationCol(u'Подразделение', ['orgStructure_id'], ('OrgStructure', 'name'), 8),
        ]
        if QtGui.qApp.defaultKLADR()[:2] == '23':
            cols.insert(4, CTextCol(u'Имя экспортного файла', ['exportFileName'], 20))
        CTableModel.__init__(self, parent, cols, 'Account')
        self.parentWidget = parent

    def canRemoveItem(self, accountId):
        return canRemoveAccount(accountId)

    def confirmRemoveItem(self, view, accountId, multiple=False):
        if not canRemoveAccount(accountId):
            buttons = QtGui.QMessageBox.Ok
            if multiple:
                buttons |= QtGui.QMessageBox.Cancel
            mbResult = QtGui.QMessageBox.critical(
                view,
                u'Внимание!',
                u'Счёт имеет подтверждённые записи реестра и не подлежит удалению',
                buttons
            )
            return False if mbResult == QtGui.QMessageBox.Ok else None
        else:
            buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
            if multiple:
                buttons |= QtGui.QMessageBox.Cancel
            mbResult = QtGui.QMessageBox.question(
                view,
                u'Внимание!',
                u'Вы действительно хотите удалить счёт?',
                buttons,
                QtGui.QMessageBox.No
            )
            return {QtGui.QMessageBox.Yes: True,
                    QtGui.QMessageBox.No: False}.get(mbResult, None)

    def beforeRemoveItem(self, accountId):
        clearPayStatus(accountId)

    def deleteRecord(self, table, itemId):
        # CLEAR_PAYSTATUS = u"""
        # UPDATE
        #     {table} INNER JOIN Account_Item ai ON ai.{field} = {table}.id
        # SET
        #     {table}.payStatus = 0
        # WHERE
        #     ai.deleted = 0 AND ai.master_id = {master_id}
        # """

        db = QtGui.qApp.db
        tableAccount = db.table('Account')
        tableAccountItem = db.table('Account_Item')

        # clear paystatus
        # db.query(CLEAR_PAYSTATUS.format(table='Event', field='event_id', master_id=itemId))
        # db.query(CLEAR_PAYSTATUS.format(table='Action', field='action_id', master_id=itemId))
        # db.query(CLEAR_PAYSTATUS.format(table='Visit', field='visit_id', master_id=itemId))

        db.markRecordsDeleted(tableAccount, tableAccount['id'].eq(itemId))
        db.markRecordsDeleted(tableAccountItem, tableAccountItem['master_id'].eq(itemId))


    def removeRow(self, row, parent=QModelIndex()):
        if self._idList and 0 <= row < len(self._idList):
            itemId = self._idList[row]
            if self.canRemoveItem(itemId):
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
                try:
                    db = QtGui.qApp.db
                    table = self._table
                    db.transaction()
                    try:
                        self.beforeRemoveItem(itemId)
                        self.deleteRecord(table, itemId)
                        self.afterRemoveItem(itemId)
                        db.commit()
                    except:
                        db.rollback()
                        raise
                    self.beginRemoveRows(parent, row, row)
                    del self._idList[row]
                    self.endRemoveRows()
                    self.emitItemsCountChanged()
                    for x in self._cols:
                        if (hasattr(x, 'clearCache')):
                            x.clearCache()
                    return True
                finally:
                    QtGui.QApplication.restoreOverrideCursor()
        return False


class CAccountItemsModel(CTableModel):
    def __init__(self, parent):
        fieldList = ['event_id', 'visit_id', 'action_id', 'service_id']
        eventCol = CLocEventColumn(u'Услуга', fieldList, 20)
        eventCodeCol = CLocEventCodeColumn(u'Код', fieldList, 20, eventCol)
        eventDateCol = CLocEventDateColumn(u'Выполнено', fieldList, 10, eventCol)
        clientCol = CLocClientColumn(u'Ф.И.О.', fieldList, 20, eventCol.eventCache)
        clientBirthDateCol = CLocClientBirthDateColumn(
            u'Дата рожд.', fieldList, 10, eventCol.eventCache, clientCol.clientCache
        )
        clientSexCol = CLocClientSexColumn(u'Пол', fieldList, 3, eventCol.eventCache, clientCol.clientCache)
        clientPolicyCol = CLocClientPolicyColumn(u'Полис', fieldList, 30, eventCol)

        CTableModel.__init__(self, parent, [
            clientCol,
            clientBirthDateCol,
            clientSexCol,
            clientPolicyCol,
            eventCodeCol,
            eventCol,
            eventDateCol,
            CSumCol(u'Тариф', ['price'], 10, 'r'),
            CLocFederalPriceColumn(u'Фед.тариф', ['tariff_id'], 10),
            CRefBookCol(u'Ед.Уч.', ['unit_id'], 'rbMedicalAidUnit', 10),
            CNumCol(u'Кол-во', ['amount'], 10, 'r'),
            CNumCol(u'УЕТ', ['uet'], 10, 'r'),
            CSumCol(u'Сумма', ['sum'], 10, 'r'),
            CTextCol(u'Подтверждение', ['number'], 10),
            CDateCol(u'Дата', ['date'], 10),
            CRefBookCol(u'Причина отказа', ['refuseType_id', 'reexposeItem_id'], 'rbPayRefuseType', 20),
            CTextCol(u'Примечание', ['note'], 20),
            CLocFinalDiagnosisColumn(u'Диагноз', fieldList, 20),
        ], 'Account_Item')
        self.eventCache = eventCol.eventCache
        self.visitCache = eventCol.visitCache
        self.actionCache = eventCol.actionCache
        self.serviceCache = eventCol.serviceCache
        self.clientCache = clientCol.clientCache
        self.clientPolicyCache = clientPolicyCol.clientPolicyCache


class CLocClientPolicyColumn(CCol):
    def __init__(self, title, fields, defaultWidth, master):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        db = QtGui.qApp.db
        self.eventCache = master.eventCache
        self.visitCache = master.visitCache
        self.actionCache = master.actionCache
        self.clientPolicyCache = CTableRecordCache(db, db.table('ClientPolicy'), 'serial, number')

    def getPolicyFromEvent(self, eventId):
        eventRecord = self.eventCache.get(eventId)
        if eventRecord:
            policyId = forceRef(eventRecord.value('clientPolicy_id'))
            policyRecord = self.clientPolicyCache.get(policyId)
            if policyRecord:
                policy = u'{serial} {number}'.format(serial=forceString(policyRecord.value('serial')),
                                                     number=forceString(policyRecord.value('number')))
                return toVariant(policy)
        return None

    def format(self, values):
        eventId = forceRef(values[0])
        policy = self.getPolicyFromEvent(eventId)
        if not policy is None:
            return policy

        visitId = forceRef(values[1])
        visitRecord = self.visitCache.get(visitId)
        if visitRecord:
            eventId = forceRef(visitRecord.value('event_id'))
            policy = self.getPolicyFromEvent(eventId)
            if not policy is None:
                return policy

        actionId = forceRef(values[2])
        actionRecord = self.actionCache.get(actionId)
        if actionRecord:
            eventId = forceRef(actionRecord.value('event_id'))
            policy = self.getPolicyFromEvent(eventId)
            if not policy is None:
                return policy

        return CCol.invalid

    def invalidateRecordsCache(self):
        self.clientPolicyCache.invalidate()


class CLocFederalPriceColumn(CCol):
    def __init__(self, title, fields, defaultWidth):
        CCol.__init__(self, title, fields, defaultWidth, 'c')
        db = QtGui.qApp.db
        self.tariffCache = CTableRecordCache(db, db.table('Contract_Tariff'), 'federalPrice')

    def format(self, values):
        tariffId = values[0]
        if tariffId:
            tariffRecord = self.tariffCache.get(tariffId)
            price = forceDouble(tariffRecord.value('federalPrice'))
            return toVariant(QtCore.QLocale().toString(price, 'f', 2))
        return CCol.invalid

    def formatNative(self, values):
        tariffId = values[0]
        if tariffId:
            tariffRecord = self.tariffCache.get(tariffId)
            return forceDouble(tariffRecord.value('federalPrice'))
        return 0.0


class CLocFinalDiagnosisColumn(CCol):
    def __init__(self, title, fields, defaultWidth):
        CCol.__init__(self, title, fields, defaultWidth, 'c')
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableDiagnostic = db.table('Diagnostic')
        tableDiagnosis = db.table('Diagnosis')
        tableDiagnosisType = db.table('rbDiagnosisType')
        generalTable = tableEvent.join(tableDiagnostic, tableDiagnostic['event_id'].eq(tableEvent['id']))
        generalTable = generalTable.join(tableDiagnosis, [
            tableDiagnosis['id'].eq(tableDiagnostic['diagnosis_id']), tableDiagnosis['deleted'].eq(0)
        ])
        # При поиске диагноза предполагается, что в базе не может быть и основного (code = 2) и заключительного (code = 1) диагноза
        # одновременно на один event. Это предположение сделанно из того, что на формах, где можно выбрать тип дипгноза, нельзя указать и осн и закл.
        # Если это не так, необходимо добавить проверку.
        generalTable = generalTable.join(tableDiagnosisType, ('%s AND %s') % (
            tableDiagnosisType['id'].eq(tableDiagnostic['diagnosisType_id']),
            tableDiagnosisType['code'].inlist(['1', '2'])
        ))
        self.recordCache = CTableRecordCache(db, generalTable, 'MKB')

    def format(self, values):
        eventId = forceRef(values[0])
        record = self.recordCache.get(eventId)
        if record:
            return record.value('MKB')
        return CCol.invalid


class CLocEventColumn(CCol):
    def __init__(self, title, fields, defaultWidth):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        db = QtGui.qApp.db
        self.eventCache = CTableRecordCache(db, db.table('Event'), 'eventType_id, client_id, execDate, clientPolicy_id')
        self.eventTypeCache = CTableRecordCache(db, db.table('EventType'), 'name, service_id')
        self.visitCache = CTableRecordCache(db, db.table('Visit'), 'date, service_id, event_id')
        self.serviceCache = CTableRecordCache(db, db.table('rbService'), 'name, code')
        self.actionCache = CTableRecordCache(db, db.table('Action'), 'endDate, actionType_id, event_id')
        self.actionTypeCache = CTableRecordCache(db, db.table('ActionType'), 'name')

    def format(self, values):
        serviceId = forceRef(values[3])
        name = CCol.resolveValueByCaches(serviceId, [(self.serviceCache, 'name')])
        if name != CCol.invalid:
            return name

        actionId = forceRef(values[2])
        name = CCol.resolveValueByCaches(actionId, [(self.actionCache, 'actionType_id'),
                                                    (self.actionTypeCache, 'name')])
        if name != CCol.invalid:
            return name

        visitId = forceRef(values[1])
        name = CCol.resolveValueByCaches(visitId, [(self.visitCache, 'service_id'),
                                                   (self.serviceCache, 'name')])
        if name != CCol.invalid:
            return name

        eventId = forceRef(values[0])
        name = CCol.resolveValueByCaches(eventId, [(self.eventCache, 'eventType_id'),
                                                   (self.eventTypeCache, 'name')])

        return name

    def invalidateRecordsCache(self):
        self.eventCache.invalidate()
        self.eventTypeCache.invalidate()
        self.visitCache.invalidate()
        self.serviceCache.invalidate()
        self.actionCache.invalidate()
        self.actionTypeCache.invalidate()


class CLocEventCodeColumn(CCol):
    def __init__(self, title, fields, defaultWidth, master):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.eventCache = master.eventCache
        self.eventTypeCache = master.eventTypeCache
        self.visitCache = master.visitCache
        self.actionCache = master.actionCache
        self.actionTypeCache = master.actionTypeCache
        self.serviceCache = master.serviceCache

    def getServiceCode(self, serviceId):
        if serviceId:
            serviceRecord = self.serviceCache.get(serviceId)
            if serviceRecord:
                return serviceRecord.value('code')
        else:
            return CCol.invalid

    # TODO: atronah: мб стоит переписать с использованием CCol.resolveValueByCaches
    def format(self, values):
        serviceId = forceRef(values[3])
        if serviceId:
            return self.getServiceCode(serviceId)

        visitId = forceRef(values[1])
        if visitId:
            visitRecord = self.visitCache.get(visitId)
            if visitRecord:
                serviceId = forceRef(visitRecord.value('service_id'))
                return self.getServiceCode(serviceId)
            return CCol.invalid

        eventId = forceRef(values[0])
        if eventId:
            eventRecord = self.eventCache.get(eventId)
            if eventRecord:
                eventTypeId = forceRef(eventRecord.value('eventType_id'))
                eventTypeRecord = self.eventTypeCache.get(eventTypeId)
                if eventTypeRecord:
                    serviceId = forceRef(eventTypeRecord.value('service_id'))
                    return self.getServiceCode(serviceId)
            return CCol.invalid

        return CCol.invalid


class CLocEventDateColumn(CCol):
    def __init__(self, title, fields, defaultWidth, master):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.eventCache = master.eventCache
        self.visitCache = master.visitCache
        self.actionCache = master.actionCache

    def getFieldValue(self, values):
        fieldValue = None
        eventId = forceRef(values[0])
        visitId = forceRef(values[1])
        actionId = forceRef(values[2])
        if actionId:
            actionRecord = self.actionCache.get(actionId)
            if actionRecord:
                fieldValue = actionRecord.value('endDate')
        elif visitId:
            visitRecord = self.visitCache.get(visitId)
            if visitRecord:
                fieldValue = visitRecord.value('date')
        elif eventId:
            eventRecord = self.eventCache.get(eventId)
            if eventRecord:
                fieldValue = eventRecord.value('execDate')
        return fieldValue

    def format(self, values):
        fieldValue = self.getFieldValue(values)
        if fieldValue != None:
            return toVariant(forceString(fieldValue.toDate()))
        return CCol.invalid

    def formatNative(self, values):
        fieldValue = self.getFieldValue(values)
        if fieldValue != None:
            return fieldValue.toDate().toPyDate()
        return None


class CLocClientColumn(CCol):
    def __init__(self, title, fields, defaultWidth, eventCache):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        db = QtGui.qApp.db
        self.eventCache = eventCache
        self.clientCache = CTableRecordCache(
            db, db.table('Client'), 'lastName, firstName, patrName, birthDate, sex, SNILS')

    def format(self, values):
        val = values[0]
        eventId = forceRef(val)
        eventRecord = self.eventCache.get(eventId)
        if eventRecord:
            clientId = forceRef(eventRecord.value('client_id'))
            clientRecord = self.clientCache.get(clientId)
            if clientRecord:
                name = formatName(
                    clientRecord.value('lastName'),
                    clientRecord.value('firstName'),
                    clientRecord.value('patrName')
                )
                return toVariant(name)
        return CCol.invalid

    def invalidateRecordsCache(self):
        self.clientCache.invalidate()


class CLocClientBirthDateColumn(CCol):
    def __init__(self, title, fields, defaultWidth, eventCache, clientCache):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.eventCache = eventCache
        self.clientCache = clientCache

    def format(self, values):
        val = values[0]
        eventId = forceRef(val)
        eventRecord = self.eventCache.get(eventId)
        if eventRecord:
            clientId = forceRef(eventRecord.value('client_id'))
            clientRecord = self.clientCache.get(clientId)
            if clientRecord:
                return toVariant(forceString(clientRecord.value('birthDate')))
        return CCol.invalid

    def formatNative(self, values):
        val = values[0]
        eventId = forceRef(val)
        eventRecord = self.eventCache.get(eventId)
        if eventRecord:
            clientId = forceRef(eventRecord.value('client_id'))
            clientRecord = self.clientCache.get(clientId)
            if clientRecord:
                birthDate = forceDateTime(clientRecord.value('birthDate'))
                if birthDate.isValid():
                    return birthDate.toPyDateTime()
        return None


class CLocClientSexColumn(CCol):
    def __init__(self, title, fields, defaultWidth, eventCache, clientCache):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self.eventCache = eventCache
        self.clientCache = clientCache

    def format(self, values):
        val = values[0]
        eventId = forceRef(val)
        eventRecord = self.eventCache.get(eventId)
        if eventRecord:
            clientId = forceRef(eventRecord.value('client_id'))
            clientRecord = self.clientCache.get(clientId)
            if clientRecord:
                return toVariant(formatSex(clientRecord.value('sex')))
        return CCol.invalid


class CTariff(object):
    ttVisit = 0  # visit (при выгрузке в ЕИСОМС каждому посещению должен быть сопоставлен отдельный основной диагноз)
    ttEvent = 1  # event
    ttActionAmount = 2  # action, по количеству
    ttCoupleVisits = 3  # "визит-день", тарифицируется множество визитов
    ttHospitalBedDay = 4  # "койко-день"
    ttActionUET = 5  # action, по УЕТ
    ttHospitalBedService = 6  # "койка-профиль"
    ttVisitByAction = 7  # визит по мероприятию
    ttVisitsByMES = 8  # Визиты по МЭС
    ttEventByMES = 9  # Событие по МЭС
    ttEventByMESLen = 10  # Событие по МЭС, с учётом длительности события
    ttActionsByMES = 11  # Мероприятие по МЭС
    ttVisitWithCommonDiag = 12  # Посещения с одним диагнозом (выставляется в счета так же, как и ttVisit. Добавлено для выгрузки в ЕИСОМС: не пытаемся подставить для каждого посещения свой диагноз, берем один основной/заключительный из обращения)
    ttEventByCSG = 13  # Стандарт по КСГ
    ttVisitByActionUET = 14  # Посещение по УЕТ услуги
    ttEventByHTG = 15  # Событие по ВМП
    ttClinicalExam = 16  # Услуга по диспансеризации (КОСТЫЛЬ. добавлено потому что минздрав - молодцы, и у них теперь замечательнейшая логика оплаты случаев диспансеризации. Будет применяться как в выгрузке мероприятий, так и в выгрузке посещений, т.к. на данный момент в разных регионах ДД настроена по-разному).

    def __init__(self, record):
        if record:
            self.id = forceInt(record.value('id'))
            self.eventTypeId = forceRef(record.value('eventType_id'))
            self.tariffType = forceInt(record.value('tariffType'))
            self.serviceId = forceRef(record.value('service_id'))
            self.tariffCategoryId = forceRef(record.value('tariffCategory_id'))
            self.MKB = forceStringEx(record.value('MKB'))
            self.parsedMKB = self.parseMKB(self.MKB)
            self.amount = forceDecimal(record.value('amount'))
            self.uet = forceDecimal(record.value('uet'))
            self.price = forceDecimal(record.value('price'))
            self.federalPrice = forceDecimal(record.value('federalPrice'))
            self.federalLimitation = forceDecimal(record.value('federalLimitation'))
            self.specialityId = forceRef(record.value('speciality_id'))
            frags = [(forceDecimal(0.0), forceDecimal(0.0), self.price)]
            if forceDouble(record.value('frag1Start')):
                frags.append((
                    forceDecimal(record.value('frag1Start')),
                    forceDecimal(record.value('frag1Sum')),
                    forceDecimal(record.value('frag1Price')),
                ))
            if forceDouble(record.value('frag2Start')):
                frags.append((
                    forceDecimal(record.value('frag2Start')),
                    forceDecimal(record.value('frag2Sum')),
                    forceDecimal(record.value('frag2Price')),
                ))
            frags.reverse()
            self.frags = frags
            self.sex = forceInt(record.value('sex'))
            self.age = forceStringEx(record.value('age'))
            self.attachTypeId = forceRef(record.value('attachType_id'))
            self.attachLpuId = forceRef(record.value('attachLPU_id'))
            self.begDate = forceDate(record.value('begDate'))
            self.endDate = forceDate(record.value('endDate'))
            self.endDate1 = self.endDate.addDays(1) if self.endDate else None
            if self.age:
                self.ageSelector = parseAgeSelector(self.age)
            else:
                self.ageSelector = None
            self.unitId = forceRef(record.value('unit_id'))
        else:
            self.id = None
            self.eventTypeId = None
            self.tariffType = 0
            self.serviceId = None
            self.tariffCategoryId = None
            self.MKB = ''
            self.parsedMKB = ''
            self.amount = forceDecimal(0.0)
            self.uet = forceDecimal(0.0)
            self.price = forceDecimal(0.0)
            self.federalPrice = forceDecimal(0.0)
            self.federalLimitation = forceDecimal(0.0)
            self.specialityId = None
            self.frags = []
            self.sex = 0
            self.age = 0
            self.attachTypeId = None
            self.attachLpuId = None
            self.begDate = QtCore.QDate()
            self.endDate = QtCore.QDate()
            self.endDate1 = QtCore.QDate()
            self.ageSelector = None
            self.unitId = None

    @staticmethod
    def parseMKB(MKB):
        result = []
        MKB = MKB.replace(' ', '').replace('\t', '').upper()
        for range in MKB.split(','):
            if range:
                parts = range.split('-')
                result.append((parts[0], parts[-1] + '\x7F'))
        return result

    def dateInRange(self, date):
        # atronah: опытным путем выяснилось, что сравнение QDateTime и QDate не поддерживается)
        date = forceDate(date)
        return (not self.begDate or self.begDate <= date) and (not self.endDate1 or date < self.endDate1)

    def matchMKB(self, MKB):
        if self.parsedMKB:
            if not MKB:
                return False
            for low, high in self.parsedMKB:
                if low <= MKB.upper() < high:
                    return True
            return False
        else:
            return True

    def evalAmountPriceSum(self, amount, clientId=None, lightweightLogic=False, coeff=forceDecimal(1.0)):
        """
        Вычисляет цену оказанной услуги. В простом варианте сумма(sum) = количество(amount) * цена_за_еденицу(price),
        но у нас очень много сторонней логики, из-за этого вычисление становиться нетривиальным

        :param amount: Количество оказаний услуги
        :param clientId: Человек, которому оказывали услугу
        :param lightweightLogic: Флаг, по которому включается простая логика (sum = amount * price)
        :param coeff: Коэффициент, который применяется к :param price. Пока используется только при :param lightweightLogic
        :return: (количество, цена за единицу с учетом сложной логики, сумма)
        """
        if self.amount:
            amount = forceDecimal(min(amount, self.amount))
        else:
            amount = forceDecimal(amount)

        sum = forceDecimal(0.0)

        if lightweightLogic:
            price = (forceDecimal(self.frags[0][2]) * coeff).quantize(TWO_PLACES)
            sum = forceDecimal(price) * forceDecimal(amount)
            return amount, price, sum

        for fragStart, fragSum, fragPrice in self.frags:
            if amount >= fragStart:
                sum = forceDecimal(fragSum) + (forceDecimal(amount) - forceDecimal(fragStart)) * forceDecimal(fragPrice)
                break
        if clientId:
            sum = sum * (forceDecimal(1.0) - forceDecimal(getClientDiscountInfo(clientId)[0]))
        price = forceDecimal(sum / forceDecimal(amount) if amount else self.price)

        return forceDecimal(amount), price, sum

    def limitationIsExceeded(self, amount):
        for fragStart, fragSum, fragPrice in self.frags:
            if fragStart > 0 and amount >= fragStart:
                return True
        return False


def getContractInfo(contractId, begDate=None, endDate=None, serviceIdList=None):
    u""" Удобное представление всей информации о договоре в виде словаря.

        :param contractId: идентификатор интересующего договора
        :param begDate: дата начала периода. Используется для ограничения списка выбираемых тарифов, т.к. это очень дорогая операция
        :param endDate: дата окончания периода. По одиночке begDate и endDate ведут себя одинаково. Если указаны оба, проверка будет более сложной.
        :param serviceIdList: список услуг, тарифы для которых нас интересуют.
        :return: smartDict
    """
    db = QtGui.qApp.db
    table = db.table('Contract')
    record = db.getRecord(
        table,
        [
            'number', 'date', 'payer_id', 'recipient_id', 'finance_id', 'begDate', 'endDate',
            'resolution', 'exposeUnfinishedEventVisits', 'exposeUnfinishedEventActions',
            'ignorePayStatusForJobs', 'isConsiderFederalPrice', 'visitExposition',
            'actionExposition', 'exposeDiscipline', 'deposit', 'counterValue',
            'limitationPeriod'
        ],
        contractId
    )
    result = smartDict()
    result.id = contractId
    result.number = forceString(record.value('number'))
    result.date = forceDate(record.value('date'))
    result.payer_id = forceRef(record.value('payer_id'))
    result.recipient_id = forceRef(record.value('recipient_id'))
    result.resolution = forceString(record.value('resolution'))
    financeId = forceRef(record.value('finance_id'))
    result.finance_id = financeId
    result.financeType = CFinanceType.getCode(financeId)
    result.payStatusMask = getPayStatusMask(financeId)
    result.begDate = forceDate(record.value('begDate'))
    result.endDate = forceDate(record.value('endDate'))
    result.exposeUnfinishedEventVisits = forceBool(record.value('exposeUnfinishedEventVisits'))
    result.exposeUnfinishedEventActions = forceBool(record.value('exposeUnfinishedEventActions'))
    result.isIgnorePayStatusForJobs = forceBool(record.value('ignorePayStatusForJobs'))
    result.isConsiderFederalPrice = forceBool(record.value('isConsiderFederalPrice'))
    result.exposeByMESMaxDuration = forceBool(record.value('exposeByMESMaxDuration'))
    result.visitExposition = forceInt(record.value('visitExposition'))
    result.actionExposition = forceInt(record.value('actionExposition'))
    result.exposeDiscipline = forceInt(record.value('exposeDiscipline'))
    result.deposit = forceDouble(record.value('deposit'))
    result.counterValue = forceDouble(record.value('counterValue'))
    result.limitationPeriod = forceInt(record.value('limitationPeriod'))

    tableSpecification = db.table('Contract_Specification')

    tariffByEventType = {}
    tariffByVisitService = {}
    tariffByActionService = {}
    tariffByCoupleVisitEventType = {}
    tariffByHospitalBedDay = {}
    tariffByHospitalBedService = {}
    tariffVisitByActionService = {}
    tariffVisitByActionUET = {}
    tariffVisitsByMES = {}
    tariffEventByMES = {}
    tariffActionsByMES = {}
    tariffEventByCSG = {}
    tariffEventByHTG = {}
    tariffByClinicalExamService = {}
    tableTariff = db.table('Contract_Tariff')
    tariffCond = [tableTariff['master_id'].eq(contractId), tableTariff['deleted'].eq(0)]
    # Условия введены чтобы ограничить выборку, когда тарифы меняются ежемесячно и их количество бесконечно возрастает.
    if begDate and endDate:
        # begDate <= t.endDate and endDate >= t.begDate
        tariffCond.append(tableTariff['begDate'].dateLe(endDate))
        tariffCond.append(db.joinOr([tableTariff['endDate'].dateGe(begDate), tableTariff['endDate'].isNull()]))
    elif begDate:
        tariffCond.append(tableTariff['begDate'].dateLe(begDate))
        tariffCond.append(db.joinOr([tableTariff['endDate'].dateGe(begDate), tableTariff['endDate'].isNull()]))
    elif endDate:
        tariffCond.append(tableTariff['begDate'].dateLe(endDate))
        tariffCond.append(db.joinOr([tableTariff['endDate'].dateGe(endDate), tableTariff['endDate'].isNull()]))
    if serviceIdList:
        tariffCond.append(tableTariff['service_id'].inlist(serviceIdList))
    eventTypeIdSet = set()
    for record in db.getRecordList(tableTariff, '*', where=tariffCond):
        tariff = CTariff(record)
        tariffType = tariff.tariffType
        eventTypeId = tariff.eventTypeId
        serviceId = tariff.serviceId
        if tariffType in (CTariff.ttVisit, CTariff.ttVisitWithCommonDiag):
            if serviceId:
                addTariffToDict(tariffByVisitService, serviceId, tariff)
                eventTypeIdSet.add(eventTypeId)
        elif tariffType == CTariff.ttVisitByActionUET:
            if serviceId:
                addTariffToDict(tariffVisitByActionUET, serviceId, tariff)
                eventTypeIdSet.add(eventTypeId)
        elif tariffType == CTariff.ttEvent:
            if eventTypeId:
                tariff.eventTypeId = None  # в этом случае проверка по eventTypeId избыточна.
                addTariffToDict(tariffByEventType, eventTypeId, tariff)
                eventTypeIdSet.add(eventTypeId)
        elif tariffType == CTariff.ttActionAmount or tariffType == CTariff.ttActionUET:  # action, по количеству или УЕТ
            if serviceId:
                addTariffToDict(tariffByActionService, serviceId, tariff)
                eventTypeIdSet.add(eventTypeId)
        elif tariffType == CTariff.ttCoupleVisits:  # визит-день
            if eventTypeId and serviceId:
                tariff.eventTypeId = None
                addTariffToDict(tariffByCoupleVisitEventType, eventTypeId, tariff)
                eventTypeIdSet.add(eventTypeId)
        elif tariffType == CTariff.ttHospitalBedDay:  # койко-день
            if eventTypeId and serviceId:
                tariff.eventTypeId = None
                addTariffToDict(tariffByHospitalBedDay, eventTypeId, tariff)
                eventTypeIdSet.add(eventTypeId)
        elif tariffType == CTariff.ttHospitalBedService:  # мероприятия по тарифу коек
            addTariffToDict(tariffByHospitalBedService, eventTypeId, tariff)
            eventTypeIdSet.add(eventTypeId)
        elif tariffType == CTariff.ttVisitByAction:  # визит по мероприятию
            if serviceId:
                addTariffToDict(tariffVisitByActionService, serviceId, tariff)
                eventTypeIdSet.add(eventTypeId)
        elif tariffType == CTariff.ttVisitsByMES:
            if eventTypeId:
                tariff.eventTypeId = None  # в этом случае проверка по eventTypeId избыточна.
                addTariffToDict(tariffVisitsByMES, (eventTypeId, serviceId), tariff)
                eventTypeIdSet.add(eventTypeId)
        elif tariffType == CTariff.ttEventByMES or tariffType == CTariff.ttEventByMESLen:
            if eventTypeId:
                tariff.eventTypeId = None  # в этом случае проверка по eventTypeId избыточна.
                addTariffToDict(tariffEventByMES, (eventTypeId, serviceId), tariff)
                eventTypeIdSet.add(eventTypeId)
        elif tariffType == CTariff.ttEventByHTG:
            if serviceId:
                tariff.eventTypeId = None
                addTariffToDict(tariffEventByHTG, (serviceId), tariff)
                eventTypeIdSet.add(eventTypeId)
        elif tariffType == CTariff.ttActionsByMES:
            if eventTypeId:
                tariff.eventTypeId = None
                addTariffToDict(tariffActionsByMES, (eventTypeId, serviceId), tariff)
                eventTypeIdSet.add(eventTypeId)
        elif tariffType == CTariff.ttEventByCSG:
            if serviceId:
                tariff.eventTypeId = None
                addTariffToDict(tariffEventByCSG, (serviceId), tariff)
                eventTypeIdSet.add(eventTypeId)
        elif tariffType == CTariff.ttClinicalExam:
            if serviceId:
                tariff.eventTypeId = None
                addTariffToDict(tariffByClinicalExamService, serviceId, tariff)
                eventTypeIdSet.add(eventTypeId)

    result.tariffByEventType = sortTariffsInDict(tariffByEventType)
    result.tariffByVisitService = sortTariffsInDict(tariffByVisitService)
    result.tariffByActionService = sortTariffsInDict(tariffByActionService)
    result.tariffByCoupleVisitEventType = sortTariffsInDict(tariffByCoupleVisitEventType)
    result.tariffByHospitalBedDay = sortTariffsInDict(tariffByHospitalBedDay)
    result.tariffByHospitalBedService = sortTariffsInDict(tariffByHospitalBedService)
    result.tariffVisitByActionService = sortTariffsInDict(tariffVisitByActionService)
    result.tariffVisitsByMES = sortTariffsInDict(tariffVisitsByMES)
    result.tariffEventByMES = sortTariffsInDict(tariffEventByMES)
    result.tariffActionsByMES = sortTariffsInDict(tariffActionsByMES)
    result.tariffEventByCSG = sortTariffsInDict(tariffEventByCSG)
    result.tariffVisitByActionUET = sortTariffsInDict(tariffVisitByActionUET)
    result.tariffEventByHTG = sortTariffsInDict(tariffEventByHTG)
    result.tariffByClinicalExamService = sortTariffsInDict(tariffByClinicalExamService)
    eventTypeIdList = db.getIdList(
        tableSpecification,
        'eventType_id',
        [tableSpecification['master_id'].eq(contractId), tableSpecification['deleted'].eq(0)]
    )

    if eventTypeIdList:
        if None not in eventTypeIdSet:
            eventTypeIdList = list(set(eventTypeIdList) & eventTypeIdSet)
    else:
        if None not in eventTypeIdSet:
            eventTypeIdList = list(eventTypeIdSet)
    result.specification = eventTypeIdList
    return result


def selectEvents(contractInfo, personIdList, date, orgStructureId=None):
    nonHtgTariffs = any([contractInfo.tariffByEventType,
                         contractInfo.tariffByCoupleVisitEventType,
                         contractInfo.tariffByHospitalBedDay,
                         contractInfo.tariffVisitsByMES,
                         contractInfo.tariffEventByMES,
                         contractInfo.tariffEventByCSG])
    if (not nonHtgTariffs
        and not contractInfo.tariffEventByHTG):
        return []

    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableResult = db.table('rbResult')

    table = tableEvent.leftJoin(tableResult, tableResult['id'].eq(tableEvent['result_id']))
    table = table.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))

    cond = [
        db.bitAnd(tableEvent['payStatus'], contractInfo.payStatusMask).eq(0),
        tableEvent['deleted'].eq(0),
        tableEvent['execDate'].isNotNull(),
        tableEvent['execDate'].dateBetween(max(contractInfo.begDate, date.addYears(-1)), contractInfo.endDate),
        tableEvent['execDate'].lt(date),
        db.joinOr([tableResult['notAccount'].eq(0),
                   tableResult['notAccount'].isNull()]),
        tableEvent['contract_id'].eq(contractInfo.id),
        db.joinOr([tableEventType['exposeConfirmation'].eq(0),
                   tableEvent['exposeConfirmed'].eq(1)]),
        db.func.isClientInContractContingent(
            contractInfo.id,
            tableEvent['client_id'], tableEvent['execDate'],
            QtGui.qApp.defaultKLADR(), QtGui.qApp.provinceKLADR()
        )
    ]
    if orgStructureId is not None:
        cond.append(tableEvent['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    elif personIdList:
        cond.append(tableEvent['execPerson_id'].inlist(personIdList))
    if not nonHtgTariffs:
        # Если договор только по ВМП, то проверяем его наличие
        if QtGui.qApp.defaultKLADR().startswith('91'):
            cond.append(tableEvent['hmpKind_id'].isNotNull())
        else:
            cond.append(tableEvent['HTG_id'].isNotNull())
    if contractInfo.limitationPeriod:
        cond.append(tableEvent['execDate'].ge(date.addMonths(-contractInfo.limitationPeriod)))
    if contractInfo.specification:
        cond.append(tableEvent['eventType_id'].inlist(contractInfo.specification))

    order = [
        tableEvent['execDate'],
        tableEvent['client_id'],
        tableEvent['id']
    ]
    return db.getIdList(table, tableEvent['id'], cond, order=order)


def selectVisitsByActionServices(contractInfo, personIdList, date, orgStructureId=None):
    if not contractInfo.tariffVisitByActionService:
        return {}

    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableATS = db.table('ActionType_Service')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableResult = db.table('rbResult')
    tableVisit = db.table('Visit')

    table = tableVisit.leftJoin(tableEvent, tableVisit['event_id'].eq(tableEvent['id']))
    table = table.leftJoin(tableResult, tableResult['id'].eq(tableEvent['result_id']))
    table = table.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))

    financeId = contractInfo.finance_id
    result = {}
    for serviceId, tariffList in contractInfo.tariffVisitByActionService.items():
        cond = [
            db.bitAnd(tableVisit['payStatus'], contractInfo.payStatusMask).eq(0),
            tableEvent['deleted'].eq(0),
            tableVisit['deleted'].eq(0),
            tableVisit['date'].dateBetween(max(contractInfo.begDate, date.addYears(-1)), contractInfo.endDate),
            tableVisit['date'].lt(date),
            tableVisit['finance_id'].eq(contractInfo.finance_id),
            db.joinOr([tableResult['notAccount'].eq(0), tableResult['notAccount'].isNull()]),
            db.joinOr([tableEventType['exposeConfirmation'].eq(0), tableEvent['exposeConfirmed'].eq(1)])
        ]
        if contractInfo.specification:
            cond.append(tableEvent['eventType_id'].inlist(contractInfo.specification))
        if contractInfo.limitationPeriod:
            cond.append(tableVisit['date'].ge(date.addMonths(-contractInfo.limitationPeriod)))
        eventTypeIdList = [tariff.eventTypeId for tariff in tariffList if tariff.eventTypeId]
        if eventTypeIdList:
            cond.append(tableEvent['eventType_id'].inlist(eventTypeIdList))
        if orgStructureId is not None:
            cond.append(tableEvent['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
        elif personIdList:
            if contractInfo.visitExposition == 0:
                cond.append(tableVisit['person_id'].inlist(personIdList))
            elif contractInfo.visitExposition == 1:
                cond.append(tableEvent['execPerson_id'].inlist(personIdList))
        if not contractInfo.exposeUnfinishedEventVisits:
            cond.append(tableEvent['execDate'].lt(date))
            cond.append(tableEvent['execDate'].ge(QtCore.QDate(1, 1, 1)))

        actionCond = [
            tableAction['deleted'].eq(0),
            tableAction['event_id'].eq(tableVisit['event_id']),
            tableVisit['date'].ge(tableAction['begDate']),
            tableVisit['date'].le(tableAction['endDate']),
            db.if_(
                db.existsStmt(
                    tableATS,
                    [tableATS['master_id'].eq(tableAction['actionType_id']), tableATS['finance_id'].eq(financeId)]
                ),
                db.existsStmt(
                    tableATS,
                    [
                        tableATS['master_id'].eq(tableAction['actionType_id']),
                        tableATS['finance_id'].eq(financeId),
                        tableATS['service_id'].eq(serviceId)
                    ]
                ),
                db.existsStmt(
                    tableATS,
                    [
                        tableATS['master_id'].eq(tableAction['actionType_id']),
                        tableATS['finance_id'].isNull(),
                        tableATS['service_id'].eq(serviceId)
                    ]
                )
            ),
            db.func.isClientInContractContingent(
                contractInfo.id,
                tableEvent['client_id'],
                tableVisit['date'],
                QtGui.qApp.defaultKLADR(),
                QtGui.qApp.provinceKLADR()
            )
        ]
        cond.append(db.existsStmt(tableAction, actionCond))

        order = [
            tableVisit['date'],
            tableEvent['client_id'],
            tableVisit['id']
        ]
        result[serviceId] = db.getIdList(table, tableVisit['id'], cond, order=order)
    return result


def selectVisits(contractInfo, personIdList, date, orgStructureId=None):
    if not contractInfo.tariffByVisitService \
            and not contractInfo.tariffByClinicalExamService:
        return []

    db = QtGui.qApp.db
    tableContract = db.table('Contract')
    tableDiagnostic = db.table('Diagnostic')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableResult = db.table('rbResult')
    tableVisit = db.table('Visit')

    table = tableVisit.leftJoin(tableEvent, tableVisit['event_id'].eq(tableEvent['id']))
    table = table.leftJoin(tableContract, tableContract['id'].eq(tableEvent['contract_id']))
    table = table.leftJoin(tableResult, tableResult['id'].eq(tableEvent['result_id']))
    table = table.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    table = table.leftJoin(tableDiagnostic, tableVisit['diagnostic_id'].eq(tableDiagnostic['id']))

    cond = [
        db.bitAnd(tableVisit['payStatus'], contractInfo.payStatusMask).eq(0),
        tableEvent['deleted'].eq(0),
        tableVisit['deleted'].eq(0),
        tableVisit['date'].dateBetween(max(contractInfo.begDate, date.addYears(-1)), contractInfo.endDate),
        tableVisit['date'].lt(date),
        db.if_(tableVisit['finance_id'].eq(tableContract['finance_id']),
               tableEvent['contract_id'].eq(contractInfo.id),
               tableVisit['finance_id'].eq(contractInfo.finance_id)),
        db.joinOr([tableResult['notAccount'].eq(0),
                   tableResult['notAccount'].isNull()]),
        db.joinOr([tableEventType['exposeConfirmation'].eq(0),
                   tableEvent['exposeConfirmed'].eq(1)]),
        db.func.isClientInContractContingent(
            contractInfo.id,
            tableEvent['client_id'],
            tableVisit['date'],
            QtGui.qApp.defaultKLADR(),
            QtGui.qApp.provinceKLADR()
        )
    ]
    if contractInfo.specification:
        cond.append(tableEvent['eventType_id'].inlist(contractInfo.specification))
    if contractInfo.limitationPeriod:
        cond.append(tableVisit['date'].ge(date.addMonths(-contractInfo.limitationPeriod)))
    serviceIdList = contractInfo.tariffByVisitService.keys() + contractInfo.tariffVisitByActionUET.keys() + contractInfo.tariffByClinicalExamService.keys()
    if serviceIdList:
        cond.append(tableVisit['service_id'].inlist(serviceIdList))
    if orgStructureId is not None:
        cond.append(tableEvent['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    elif personIdList:
        actionStatusList = [6, 7, 8, 9, 10, 11]  # Статусы Action
        if contractInfo.visitExposition == 0:
            cond.append(db.joinOr([tableDiagnostic['status'].inlist(actionStatusList),
                                   tableVisit['person_id'].inlist(personIdList)]))
        elif contractInfo.visitExposition == 1:
            cond.append(db.joinOr([tableDiagnostic['status'].inlist(actionStatusList),
                                   tableEvent['execPerson_id'].inlist(personIdList)]))
    if not contractInfo.exposeUnfinishedEventVisits:
        cond.append(tableEvent['execDate'].lt(date))
        cond.append(tableEvent['execDate'].ge(QtCore.QDate(1, 1, 1)))

    order = [
        tableVisit['date'],
        tableEvent['client_id'],
        tableVisit['id']
    ]
    return db.getIdList(table, tableVisit['id'], cond, order=order)


def selectActions(contractInfo, personIdList, date, orgStructureId=None):
    if not (
                    contractInfo.tariffByActionService or contractInfo.tariffActionsByMES or contractInfo.tariffByClinicalExamService):
        return []

    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableATS = db.table('ActionType_Service')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableResult = db.table('rbResult')

    table = tableAction.leftJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
    table = table.leftJoin(tableResult, tableResult['id'].eq(tableEvent['result_id']))
    table = table.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))

    cond = [
        tableEvent['deleted'].eq(0),
        db.bitAnd(tableAction['payStatus'], contractInfo.payStatusMask).eq(0),
        tableAction['deleted'].eq(0),
        tableAction['endDate'].dateBetween(max(contractInfo.begDate, date.addYears(-3)), contractInfo.endDate),
        tableAction['endDate'].lt(date),
        db.joinOr([tableEventType['exposeConfirmation'].eq(0),
                   tableEvent['exposeConfirmed'].eq(1)]),
        db.joinOr([tableResult['notAccount'].eq(0),
                   tableResult['notAccount'].isNull()])
    ]
    if contractInfo.tariffActionsByMES and not (
                contractInfo.tariffByActionService or contractInfo.tariffByClinicalExamService
    ):
        cond.append(tableAction['MES_id'].isNotNull())
    if contractInfo.specification:
        cond.append(tableEvent['eventType_id'].inlist(contractInfo.specification))
    if contractInfo.limitationPeriod:
        cond.append(tableAction['endDate'].ge(date.addMonths(-contractInfo.limitationPeriod)))

    financeId = contractInfo.finance_id
    serviceIdList = contractInfo.tariffByActionService.keys() + contractInfo.tariffByClinicalExamService.keys()
    condByService = [
        db.if_(
            db.existsStmt(
                tableATS,
                [tableATS['master_id'].eq(tableAction['actionType_id']), tableATS['finance_id'].eq(financeId)]
            ),
            db.existsStmt(
                tableATS,
                [
                    tableATS['master_id'].eq(tableAction['actionType_id']),
                    tableATS['finance_id'].eq(financeId),
                    tableATS['service_id'].inlist(serviceIdList)
                ]
            ),
            db.existsStmt(
                tableATS,
                [
                    tableATS['master_id'].eq(tableAction['actionType_id']),
                    tableATS['finance_id'].isNull(),
                    tableATS['service_id'].inlist(serviceIdList)
                ]
            )
        )
    ]
    if contractInfo.tariffActionsByMES:
        condByService.append(tableAction['MES_id'].isNotNull())
    cond.append(db.joinOr(condByService))

    if orgStructureId is not None:
        cond.append(tableEvent['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    elif personIdList is not None:
        if contractInfo.actionExposition == 0:
            cond.append(tableAction['person_id'].inlist(personIdList))
        elif contractInfo.actionExposition == 1:
            cond.append(tableEvent['execPerson_id'].inlist(personIdList))
    if not contractInfo.exposeUnfinishedEventActions:
        cond.append(tableEvent['execDate'].lt(date))
        cond.append(tableEvent['execDate'].ge(QtCore.QDate(1, 1, 1)))

    # i3582 Исключаем ненужные экшены (ДЛЯ ДККБ онли)
    if QtGui.qApp.isDisableHospStatEvent():
        cond.append(tableResult['regionalCode'].ne('305'))
        cond.append(tableEventType['code'].ne('48'))

    contractCond = [
        tableAction['contract_id'].eq(contractInfo.id),
        db.joinAnd([
            tableAction['contract_id'].isNull(),
            tableAction['finance_id'].eq(contractInfo.finance_id),
            tableEvent['contract_id'].eq(contractInfo.id),
            db.func.isClientInContractContingent(
                contractInfo.id,
                tableEvent['client_id'],
                tableAction['endDate'],
                QtGui.qApp.defaultKLADR(),
                QtGui.qApp.provinceKLADR()
            )
        ])
    ]
    cond.append(db.joinOr(contractCond))

    order = [
        tableAction['endDate'],
        tableEvent['client_id'],
        tableAction['id']
    ]
    return db.getIdList(table, tableAction['id'], cond, order=order)


def selectHospitalBedActionProperties(contractInfo, personIdList, date, orgStructureId=None):
    # недостатки:
    # 1) Неправильно обработается ситуация с многократным употреблением свойства типа HospitalBed в действии
    #    Полагаю, что это практически не должно применяться
    # 2) Неправильно обработается ситуация с векторным свойством типа HospitalBed в действии
    #    Таких пока нет
    if not contractInfo.tariffByHospitalBedService:
        return []

    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableActionProperty = db.table('ActionProperty')
    tableActionPropertyHospitalBed = db.table('ActionProperty_HospitalBed')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    tableResult = db.table('rbResult')

    table = tableActionPropertyHospitalBed.leftJoin(
        tableActionProperty,
        tableActionProperty['id'].eq(tableActionPropertyHospitalBed['id'])
    )
    table = table.leftJoin(tableAction, tableAction['id'].eq(tableActionProperty['action_id']))
    table = table.leftJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
    table = table.leftJoin(tableResult, tableResult['id'].eq(tableEvent['result_id']))
    table = table.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))

    cond = [
        tableEvent['deleted'].eq(0),
        tableAction['deleted'].eq(0),
        tableAction['endDate'].dateBetween(contractInfo.begDate, contractInfo.endDate),
        tableAction['endDate'].lt(date),
        db.bitAnd(tableAction['payStatus'], contractInfo.payStatusMask).eq(0),
        tableActionProperty['deleted'].eq(0),
        tableActionPropertyHospitalBed['value'].isNotNull(),
        db.joinOr([tableResult['notAccount'].eq(0), tableResult['notAccount'].isNull()]),
        db.joinOr([tableEventType['exposeConfirmation'].eq(0), tableEvent['exposeConfirmed'].eq(1)])
    ]
    if contractInfo.specification:
        cond.append(tableEvent['eventType_id'].inlist(contractInfo.specification))
    if contractInfo.limitationPeriod:
        cond.append(tableAction['endDate'].ge(date.addMonths(-contractInfo.limitationPeriod)))
    if orgStructureId is not None:
        cond.append(tableEvent['orgStructure_id'].inlist(getOrgStructureDescendants(orgStructureId)))
    elif personIdList:
        if contractInfo.actionExposition == 0:
            cond.append(tableAction['person_id'].inlist(personIdList))
        elif contractInfo.actionExposition == 1:
            cond.append(tableEvent['execPerson_id'].inlist(personIdList))
    if not contractInfo.exposeUnfinishedEventActions:
        cond.append(tableEvent['execDate'].lt(date))
        cond.append(tableEvent['execDate'].ge(QtCore.QDate(1, 1, 1)))

    contractCond = [
        tableAction['contract_id'].eq(contractInfo.id),
        db.joinAnd([
            tableAction['contract_id'].isNull(),
            tableAction['finance_id'].eq(contractInfo.finance_id),
            db.func.isClientInContractContingent(
                contractInfo.id, tableEvent['client_id'],
                tableAction['endDate'], QtGui.qApp.defaultKLADR(),
                QtGui.qApp.provinceKLADR()
            )
        ]),
        db.joinAnd([
            tableAction['contract_id'].isNull(),
            tableAction['finance_id'].isNull(),
            db.func.isClientInContractContingent(
                contractInfo.id, tableEvent['client_id'],
                tableAction['endDate'], QtGui.qApp.defaultKLADR(),
                QtGui.qApp.provinceKLADR()
            )
        ])
    ]
    cond.append(db.joinOr(contractCond))

    order = [
        tableAction['endDate'], tableEvent['client_id'], tableAction['id']
    ]
    return db.getIdList(table, tableActionProperty['id'], cond, order=order)


def createAccountRecord(contractInfo, orgId, orgStructureId, date, payer=None, dbName=None):
    db = QtGui.qApp.db
    dbName = dbName if dbName else forceString(QtGui.qApp.db.db.databaseName())
    dbName = '`' + dbName + '`' if not dbName[0] == '`' else dbName
    table = db.table(dbName + '.Account')
    record = table.newRecord()
    record.setValue('createPerson_id', toVariant(QtGui.qApp.userId))
    record.setValue('modifyPerson_id', toVariant(QtGui.qApp.userId))
    record.setValue('contract_id', toVariant(contractInfo.id))
    record.setValue('orgStructure_id', toVariant(orgStructureId))
    if payer is None:
        record.setValue('payer_id', toVariant(contractInfo.payer_id))
    else:
        record.setValue('payer_id', toVariant(payer))
    record.setValue('settleDate', toVariant(date))
    record.setValue('createDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
    record.setValue('modifyDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
    record.setValue('date', toVariant(QtCore.QDate.currentDate()))
    accountId = db.insertRecord(table, record)
    record.setValue('id', toVariant(accountId))
    return accountId, record


# i1560: номер счета формируется исходя из счетчика на источник финансирования
# Номер присваивается если существует искомый счетчик
def setContractNum(contractInfo):
    try:
        if contractInfo['finance_id']:
            db = QtGui.qApp.db

            tableCounter = db.table('rbCounter')
            counter = db.getRecordEx(
                tableCounter, cols='*', where=["code = 'p%s'" % contractInfo['finance_id']]
            )
            if counter:
                counter.setValue(u'value', toVariant(forceRef(counter.value('value')) + 1))
                db.updateRecord(tableCounter, counter)
                return '%s-%s' % (contractInfo.number, forceString(counter.value('value')))
            else:
                return None
    except:
        return None


def updateAccountRecord(record, contractInfo, date, numberSuffix, amount, uet, sum, dbName=None):
    dbName = dbName if dbName else forceString(QtGui.qApp.db.db.databaseName())
    dbName = '`' + dbName + '`' if not dbName[0] == '`' else dbName
    record.setValue('settleDate', toVariant(date))
    accountNumber = contractInfo.get('accountNumber', None)
    useCounter = forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'useCounterInAccounts', QtCore.QVariant()))
    if accountNumber is None:
        # Для договоров и счетов используется единый счетчик.
        if not contractInfo['counterValue'] and useCounter:
            counterId = forceRef(QtGui.qApp.db.translate('rbCounter', 'code', 'contract', 'id'))
            accountNumber = getContractDocumentNumber(counterId)
            # record.setValue('counterValue', toVariant(counterValue))
        else:
            num = setContractNum(contractInfo)
            if num:
                contractInfo.accountNumber = accountNumber = num
            else:
                contractInfo.accountNumber = accountNumber = getNextAccountNumber(contractInfo.number)
    record.setValue('number', toVariant(
        (accountNumber + numberSuffix) if (contractInfo['counterValue'] or not useCounter) else accountNumber
    ))
    record.setValue('amount', toVariant(amount))
    record.setValue('uet', toVariant(uet))
    record.setValue('sum', toVariant(sum))
    QtGui.qApp.db.updateRecord(dbName + '.Account', record)


def addTariffToDict(tariffDict, key, tariff):
    tariffList = tariffDict.get(key, None)
    if tariffList:
        tariffList.append(tariff)
    else:
        tariffDict[key] = [tariff]


def sortTariffsInDict(tariffDict):
    for tariffList in tariffDict.values():
        tariffList.sort(key=lambda tariff: (0 if tariff.MKB else 1, tariff.MKB, tariff.id))
    return tariffDict


def selectReexposableAccountItems(contractInfo, date):
    db = QtGui.qApp.db
    tableAccount = db.table('Account')
    tableAccountItem = db.table('Account_Item')
    tablePayRefuseType = db.table('rbPayRefuseType')
    table = tableAccountItem.leftJoin(tableAccount, tableAccount['id'].eq(tableAccountItem['master_id']))
    table = table.leftJoin(tablePayRefuseType, tablePayRefuseType['id'].eq(tableAccountItem['refuseType_id']))

    cond = [
        tablePayRefuseType['rerun'].ne(0),
        tableAccountItem['refuseType_id'].isNotNull(),
        tableAccountItem['reexposeItem_id'].isNull(),
        tableAccount['contract_id'].eq(contractInfo.id),
        tableAccount['settleDate'].lt(date)
    ]
    # перевыставляем с учетом срока давности договора при формировании счетов
    if contractInfo.limitationPeriod:
        cond.append(tableAccount['settleDate'].ge(date.addMonths(-contractInfo.limitationPeriod)))

    return db.getIdList(table, idCol=tableAccountItem['id'], where=cond, order='Account_Item.date, Account_Item.id')


def getRefuseTypeId(errorMessage, rerun=True, financeId=None, autoRegisterPayRefuseType=True):
    db = QtGui.qApp.db
    table = db.table('rbPayRefuseType')
    idList = db.getIdList(
        table,
        where=[table['name'].like(errorMessage + '%'), table['finance_id'].eq(financeId)]
    )
    if idList:
        return idList[0]
    elif autoRegisterPayRefuseType:
        record = table.newRecord()
        record.setValue('code', toVariant(''))
        record.setValue('name', toVariant(errorMessage))
        record.setValue('finance_id', toVariant(financeId))
        record.setValue('rerun', toVariant(rerun))
        return db.insertRecord(table, record)
    else:
        return None


def updateAccountTotals(accountId):
    stmt = '''
UPDATE Account,
       (SELECT
          SUM(amount) AS totalAmount,
          SUM(uet)    AS totalUet,
          SUM(sum)    AS totalSum
        FROM Account_Item
        WHERE  Account_Item.master_id = %d
         ) AS tmp

SET Account.amount = tmp.totalAmount,
    Account.uet = tmp.totalUet,
    Account.sum = tmp.totalSum
WHERE Account.id = %d''' % (accountId, accountId)
    db = QtGui.qApp.db
    db.query(stmt)


def unpackExposeDiscipline(exposeDiscipline):
    # Биты:
    # atiicddde
    #         ^ (0)   : exposeByEvent
    #      ^^^  (123) : exposeByDate   (0 - нет, 1- день, 2-неделя, 3-декада, 4-месяц, 5-квартал...)
    #     ^     (4)   : exposeByClient
    #   ^^      (56)  : exposeByInsurer (0 - нет, 1 - С.К. с филиалами, 2 - С.К. по филиалам )
    #  ^        (7)   : exposeByEventType
    # ^         (8)   : exposeByServiceArea
    exposeByEvent = bool(exposeDiscipline >> 0 & 1)
    exposeByDate = (exposeDiscipline >> 1 & 7) if not exposeByEvent else 0
    exposeByMonth = (exposeByDate == 4)
    exposeByClient = bool(exposeDiscipline >> 4 & 1) if not exposeByEvent else 0
    exposeByInsurer = (exposeDiscipline >> 5 & 3) if not exposeByEvent and not exposeByClient else 0
    exposeByEventType = bool(exposeDiscipline >> 7 & 1) if not exposeByEvent else 0
    exposeByServiceArea = bool(exposeDiscipline >> 8 & 1) if not exposeByEvent else 0
    return exposeByEvent, exposeByEventType, exposeByMonth, exposeByClient, exposeByInsurer, exposeByServiceArea


def packExposeDiscipline(exposeByEvent, exposeByEventType, exposeByMonth, exposeByClient, exposeByInsurer,
                         exposeByServiceArea):
    result = 0
    if exposeByEvent:
        result |= 1 << 0
    if exposeByMonth:
        result |= 4 << 1
    if exposeByClient:
        result |= 1 << 4
    if exposeByInsurer:
        result |= (exposeByInsurer & 3) << 5
    if exposeByEventType:
        result |= 1 << 7
    if exposeByServiceArea:
        result |= 1 << 8
    return result


class CAccountIdLineEdit(QtGui.QLineEdit):
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self._hearingPoint = False
        self._stopEntering = False

    def startHearingPoint(self):
        self._hearingPoint = True

    def stopHearingPoint(self):
        self._hearingPoint = False
        self._stopEntering = False

    def keyPressEvent(self, event):
        if not self._stopEntering:
            if self._hearingPoint:
                if event.text() == '.':
                    self._stopEntering = True
                else:
                    QtGui.QLineEdit.keyPressEvent(self, event)
            else:
                QtGui.QLineEdit.keyPressEvent(self, event)


def getOrganisationHead(org_id):
    if org_id is not None:
        tmpInsurerId = org_id
        db = QtGui.qApp.db
        table = db.table('Organisation')
        while True:
            headId = forceRef(db.translate(table, 'id', tmpInsurerId, 'head_id'))
            if headId:
                tmpInsurerId = headId
            else:
                break
        return tmpInsurerId
    else:
        return None


def getFranchisePercentByEvent(eventId):
    try:
        franchisePercent = forceInt(QtGui.qApp.db.getRecordEx(
            table=None,
            stmt=u"""
                SELECT
                  `ClientPolicy`.franchisePercent
                FROM `ClientPolicy`
                WHERE
                  `ClientPolicy`.`id` = (SELECT `Event`.clientPolicy_id FROM `Event` WHERE `Event`.`id` = %s)
                """ % eventId
        ).value('franchisePercent'))
    except Exception as e:
        franchisePercent = 0
    return franchisePercent


def getIgnoredCsgList():
    u"""i2776: получить список КСГ, которые не стоит учитывать при формировании счета"""
    stmt = u"""
    SELECT DISTINCT
      e1.id         'idIgnoredCsg',
      -- diag1.MKB     'diagnosis',
      e2.id         'idCsg',
      e1.setDate    'date',
      DATEDIFF(e1.execDate, e1.setDate) 'duration' -- ,
      -- IF(DATEDIFF(e1.execDate, e1.setDate) = 0, 1, DATEDIFF(e1.execDate, e1.setDate)) + IF(DATEDIFF(e2.execDate, e2.setDate) = 0, 1, DATEDIFF(e2.execDate, e2.setDate)) AS 'kd'
    FROM
      Event e1
      INNER JOIN mes.MES mes1 ON mes1.id = e1.MES_id
      INNER JOIN Event e2 ON e1.externalId = e2.externalId
      INNER JOIN mes.MES mes2 ON e2.MES_id = mes2.id

      INNER JOIN Diagnostic d1 ON d1.event_id = e1.id
      INNER JOIN Diagnosis diag1 ON d1.diagnosis_id = diag1.id
      INNER JOIN rbDiagnosisType rbdiag1 ON d1.diagnosisType_id = rbdiag1.id

      INNER JOIN Diagnostic d2 ON d2.event_id = e1.id
      INNER JOIN Diagnosis diag2 ON d2.diagnosis_id = diag2.id
      INNER JOIN rbDiagnosisType rbdiag2 ON d2.diagnosisType_id = rbdiag2.id
    WHERE
      e1.externalId != ''
      AND e1.deleted = 0
      AND e2.deleted = 0
      AND d1.deleted = 0
      AND d2.deleted = 0
      AND diag1.deleted = 0
      AND diag2.deleted = 0
      AND e1.id <> e2.id
      AND rbdiag1.code = '1'    -- заключительный диагноз
      AND rbdiag2.code = '1'    -- заключительный диагноз
      AND NOT (
        DATEDIFF(e1.execDate, e1.setDate) > 1 AND DATEDIFF(e1.execDate, e1.setDate) >= 0
        AND diag1.MKB IN ('O14.1', 'O34.2', 'O36.3', 'O36.4', 'O42.2')
        AND diag2.MKB IN ('O14.1', 'O34.2', 'O36.3', 'O36.4', 'O42.2')
      )
      AND e1.client_id = e2.client_id
      AND mes1.code IN ('G10.0217.002')
      AND mes2.code IN ('G10.0217.004', 'G10.0217.005')
      AND DATEDIFF(e1.execDate, e1.setDate) < 6 AND DATEDIFF(e1.execDate, e1.setDate) >= 0;
    """
    return [{
        'idIgnoredCsg': forceRef(x.value('idIgnoredCsg')),
        'idCsg': forceRef(x.value('idCsg')),
        'date': x.value('date'),
        # 'kd': forceInt(x.value('kd')),
        # 'diagnosis': forceString(x.value('diagnosis')),
        'duration': forceInt(x.value('duration')),
        'checked': False
    } for x in QtGui.qApp.db.getRecordList(stmt=stmt)]


def getExportInfoOFComplexEvent(eventId):
    u"""i3894c16197"""
    stmt = u"""
    SELECT
      e1.id AS prevEventId,
      e2.id AS nextEventId,
      IF(
          YEAR(e2.execDate) > YEAR(e1.execDate), YEAR(e2.execDate), YEAR(e1.execDate)
      ) AS exportYear,
      IF(
          YEAR(e2.execDate) > YEAR(e1.execDate), MONTH(e1.execDate),
          IF(YEAR(e2.execDate) < YEAR(e1.execDate), MONTH(e2.execDate),
          IF(MONTH(e2.execDate) > MONTH(e1.execDate), MONTH(e2.execDate), MONTH(e1.execDate)
      ))) AS exportMonth
    FROM
      Event e1, Event e2
    WHERE
      e1.externalId != ''
      AND e1.deleted = 0
      AND e2.deleted = 0
      AND e1.id <> e2.id
      AND e1.externalId = e2.externalId
      AND e1.client_id = e2.client_id
      AND e2.prevEvent_id = e1.id
      AND (e1.id = {eventId} or e2.id = {eventId})
    """.format(eventId=eventId)
    x = QtGui.qApp.db.getRecordEx(stmt=stmt)
    if x:
        return {
            'prevEventId': forceRef(x.value('prevEventId')),
            'nextEventId': forceRef(x.value('nextEventId')),
            'exportYear': forceInt(x.value('exportYear')),
            'exportMonth': forceInt(x.value('exportMonth'))
        }
    else:
        return None


def getMesAmount(eventId, mesId):
    result = 0
    db = QtGui.qApp.db
    stmt = u'''
        SELECT
        mMV.groupCode  AS prvsGroup,
        mMV.averageQnt AS averageQnt,
        Visit.id       AS visit_id,
        IF(mMV.visitType_id=mVT.id, 0, 1) AS visitTypeErr
        FROM Visit
        LEFT JOIN Person ON Person.id  = Visit.person_id
        LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id
        LEFT JOIN rbVisitType  ON rbVisitType.id = Visit.visitType_id
        LEFT JOIN mes.mrbVisitType  AS mVT  ON rbVisitType.code = mVT.code
        LEFT JOIN mes.mrbSpeciality AS mS   ON mS.regionalCode = rbSpeciality.regionalCode
        LEFT JOIN mes.MES_visit     AS mMV  ON mMV.speciality_id = mS.id
        WHERE Visit.deleted = 0 AND Visit.event_id = %d AND mMV.master_id = %d AND mVT.code in ('Л','К')
        ORDER BY visitTypeErr, mMV.groupCode, Visit.date
    ''' % (eventId, mesId)

    query = db.query(stmt)
    groupAvailable = {}
    countedVisits = set()

    realVisitsCount = 0
    while query.next():
        realVisitsCount += 1
        record = query.record()
        visitId = forceRef(record.value('visit_id'))
        if visitId not in countedVisits:
            prvsGroup = forceInt(record.value('prvsGroup'))
            averageQnt = forceInt(record.value('averageQnt'))
            available = groupAvailable.get(prvsGroup, averageQnt)
            if available > 0:
                groupAvailable[prvsGroup] = available - 1
                result += 1
                countedVisits.add(visitId)
    return forceDecimal(result), forceDecimal(realVisitsCount)
