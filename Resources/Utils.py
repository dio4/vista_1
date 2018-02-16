# -*- coding: utf-8 -*-

from PyQt4 import QtGui

from library.Enum import CEnum
from library.Utils import forceBool, forceLong, forceRef


class JobTicketStatus(CEnum):
    u""" Статус выполнения номерка на работу (Job_Ticket.status) """
    Awaiting = 0
    InProgress = 1
    Done = 2

    nameMap = {
        Awaiting  : u'Ожидание',
        InProgress: u'Выполняется',
        Done      : u'Закончено'
    }


class TakenTissueJournalStatus(CEnum):
    u""" Статус забора биоматериала (TakenTissueJournal.status) """
    Awaiting = 0
    Started = 1
    InProgress = 2
    Done = 3
    Cancelled = 4
    NoResult = 5

    nameMap = {
        Awaiting  : u'В работе',
        Started   : u'Начато',
        InProgress: u'Ожидание',
        Done      : u'Закончено',
        Cancelled : u'Отменено',
        NoResult  : u'Без результата'
    }


def getJobTicketActionIdList(jobTicketId):
    u""" Список действий (с типами), содержащих данный номерок
    :rtype: (list, list)
    """
    db = QtGui.qApp.db
    tableAction = db.table('Action')
    tableAP = db.table('ActionProperty')
    tableAPJT = db.table('ActionProperty_Job_Ticket')
    table = tableAPJT.innerJoin(tableAP, [tableAP['id'].eq(tableAPJT['id']), tableAP['deleted'].eq(0)])
    table = table.innerJoin(tableAction, [tableAction['id'].eq(tableAP['action_id']), tableAction['deleted'].eq(0)])
    cond = [
        tableAPJT['value'].eq(jobTicketId)
    ]
    cols = [
        tableAction['id'],
        tableAction['actionType_id']
    ]
    actionIdList, actionTypeIdList = [], []
    for rec in db.iterRecordList(table, cols, cond):
        actionIdList.append(forceRef(rec.value('id')))
        actionTypeIdList.append(forceRef(rec.value('actionType_id')))
    return actionIdList, actionTypeIdList


def getTissueTypeCounterValue(tissueTypeId):
    u"""
    Получение значение счетчика для биоматериала (для подставления в TTJ.externalId)
    :param tissueTypeId: rbTissueType.id
    :type tissueTypeId: int
    :return: tuple (rbCounter.id, rbCounter.value) or None
    :rtype: (long, long)
    """
    db = QtGui.qApp.db
    if not tissueTypeId or forceBool(db.translate('rbTissueType', 'id', tissueTypeId, 'counterManualInput')):
        return None

    tableCounter = db.table('rbCounter')
    record = db.getRecordEx(tableCounter,
                            ['id', 'value'],
                            tableCounter['code'].eq('tis{0}'.format(tissueTypeId)))
    if record:
        counterId = forceRef(record.value('id'))
        value = forceLong(record.value('value'))
        return counterId, value

    return None
