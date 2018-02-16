# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################
from PyQt4 import QtCore, QtGui
from Events.Utils import CFinanceType
from library.Counter import formatDocumentNumber
from library.ListModel import CListModel
from library.Utils import forceDate, forceInt, forceString, MKBwithoutSubclassification


recipeStatusNames = [
    u'Действителен',
    u'Истечение срока действия рецепта',
    u'Испорчен бланк',
    u'Госпитализация в стационар',
    u'Замена источника финансирования',
    u'Изменение схемы лечения',
    u'Неявка пациента',
    u'Отказ от льготы',
    u'Отказ пациента',
    u'Ошибка в реквизитах рецепта',
    u'Ошибка в сигнатуре',
    u'Пациент исключен из регистра',
    u'Смерть пациента',
    u'Согласованная замена',
    u'Технический сбой',
    u'Прочее'
]


#TODO: mdldml: мне не нравится дублирование функции из Events\Utils.py, возможно, стоит сделать некоторые проверки отключаемыми и использовать ее.
def checkDiagnosis(MKB, issueDate):
    db = QtGui.qApp.db
    tableMKB = db.table('MKB_Tree')
    record = db.getRecordEx(tableMKB, 'DiagName, MKBSubclass_id, begDate, endDate', tableMKB['DiagID'].eq(MKBwithoutSubclassification(MKB)))
    if not record:
        return False
    begDateMKB = forceDate(record.value('begDate'))
    endDateMKB = forceDate(record.value('endDate'))
    if begDateMKB and begDateMKB > issueDate or endDateMKB and endDateMKB <= QtCore.QDate.currentDate():
        return False

    subclassMKB = MKB[5:]
    if QtGui.qApp.isSelectOnlyLeafOfMKBTree() and not subclassMKB:
        subRecord = db.getRecordEx(tableMKB, 'DiagID', 'DiagID LIKE \'%s.%%\'' % MKBwithoutSubclassification(MKB), 'DiagID')
        if subRecord:
            return False
    if subclassMKB:
        subclassId = forceInt(record.value('MKBSubclass_id'))
        tableSubclass = db.table('rbMKBSubclass_Item')
        record = db.getRecordEx(tableSubclass, 'id', [tableSubclass['master_id'].eq(subclassId), tableSubclass['code'].eq(subclassMKB)])
        if not record:
            return False
    return True


def getDocumentNumber(clientId, code, financeId):
    db = QtGui.qApp.db

    counterRecord = db.getRecordEx('rbCounter', '`id`', "`code`='%s'" % code)
    if not counterRecord:
        financeCode = CFinanceType.getCode(financeId)
        # FIXME: Мб стоит вынести 70 в CFinanceType. Хотя вообще это значения совсем из другой оперы и другого справочника по логике
        counterCodePrefix = u'f_' if financeCode == 70 else u'r_'
        counterRecord = db.getRecordEx('rbCounter', 'id', 'code = \'%s\'' % (counterCodePrefix + code))

    if not counterRecord:
        return None

    counterId = forceInt(counterRecord.value('id'))

    query = db.query('SELECT getCounterValue(%d)' % counterId)
    if query.next():
        value = forceInt(query.value(0))
        if value:
            record = db.getRecord('rbCounter', '`prefix`, `postfix`, `separator`', counterId)
            prefix = forceString(record.value('prefix'))
            postfix = u''
            separator = u'#'
            return formatDocumentNumber(prefix, postfix, separator, value, clientId)


#TODO: mdldml: вынести в Orgs/Utils.py
def getBookkeeperCode(personId):
    db = QtGui.qApp.db

    orgStructureId = forceInt(db.translate('Person', 'id', personId, 'orgStructure_id'))
    code = forceString(db.translate('OrgStructure', 'id', orgStructureId, 'bookkeeperCode'))
    while not code:
        # Получить вышестоящее подразделение
        orgStructureId = forceInt(db.translate('OrgStructure', 'id', orgStructureId, 'parent_id'))
        if not orgStructureId:
            # Выше никого нет, текущий код - искомый
            break
        # Новый код
        code = forceString(db.translate('OrgStructure', 'id', orgStructureId, 'bookkeeperCode'))
    return code


class CRecipeStatusModel(CListModel):

    def __init__(self, addDefaultStatus=True):
        CListModel.__init__(self, recipeStatusNames[(0 if addDefaultStatus else 1):], recipeStatusNames)