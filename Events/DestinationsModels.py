# -*- coding: utf-8 -*-

#############################################################################
# #
# # Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
# #
#############################################################################

u"""Модель: Назначения"""
import datetime

from PyQt4 import QtCore, QtGui, QtSql
from PyQt4.QtCore import QSize, Qt, QRect
from PyQt4.QtGui import QItemDelegate, QBrush, QStyle, QPen
from PyQt4.QtSql import QSqlField
from Events.FormularyItemSelectionDialog import CFormularyInDocTableCol

from library.crbcombobox                import CRBComboBox, CRBModelDataCache
from library.InDocTable                 import CInDocTableCol, CDateInDocTableCol, CEnumInDocTableCol, CRBInDocTableCol, CRecordListModel
from library.Utils                      import forceDate, forceDouble, forceInt, forceString, toVariant
from Orgs.Utils                         import getOrgStructures, getOrgStructureDescendants

class CPatientsModel(CRecordListModel):
    def __init__(self, parent):
        CRecordListModel.__init__(self, parent)
        self.addCol(CInDocTableCol(u'№ ИБ', 'eventExternalId', 30))
        self.addCol(CInDocTableCol(u'ФИО', 'clientName', 120))
        self.addCol(CInDocTableCol(u'Палата', 'bedName', 50))

    def idList(self):
        idList = []
        for item in self._items:
            idList.append(forceInt(item.value('id')))
        return idList

    def itemById(self, id):
        for item in self._items:
            if forceInt(item.value('id')) == id:
                return item
        return None

    def loadData(self, date):
        self._items = []
        db = QtGui.qApp.db
        currentOrgStructureId = QtGui.qApp.currentOrgStructureId()
        stmt = u'''
            CALL getOrgStructurePatients(%(orgStructureId)s, '%(date)s')
        ''' % {
                'orgStructureId' : currentOrgStructureId if currentOrgStructureId else 'NULL',
                'date' : date.toString('yyyy-MM-dd')
            }
        query = db.query(stmt)
        while query.next():
            record = query.record()
            self._items.append(record)
        self.reset()

#
# ##############################################################################
#

class CTakeDosesInDocTableCol(CInDocTableCol):
    def __init__(self, title, fieldName, width, parent=None):
        super(CTakeDosesInDocTableCol, self).__init__(title, fieldName, width)
        self._cache = {}
        self._parent = parent

    def toString(self, val, record):
        takeDoses = forceString(record.value('takeDose'))
        takeTime = forceString(record.value('takeTime'))
        takeDate = forceString(record.value('takeDate'))

        begDate = forceDate(record.value('takeDateBegin'))
        endDate = forceDate(record.value('takeDateEnd'))
        interval = forceInt(record.value('interval'))

        cache = CRBModelDataCache.getData('rbUnit', True)
        unit = cache.getStringById(forceInt(record.value('drugMeasureUnit_id')), CRBComboBox.showName)

        times = takeTime.split(',')
        doses = takeDoses.split(',')

        result = u''
        i = 0
        date = begDate
        while date <= endDate:
            for time in times:
                if result:
                    result += ';'
                dose = doses[i]
                result += '(' + date.toString('dd.MM.yyyy') + ' ' + time + ') ' + dose + ' (' + unit + ')'
                i += 1
            date = date.addDays(interval + 1)
        return QtCore.QVariant(result)

dsNew = 0
dsCreated = 1
dsSet = 2
dsQueried = 3
dsReady = 4
dsExecuted = 5
dsNotExecuted = 6
dsCancelled = 7

class CDestinationsItemDelegate(QItemDelegate):
    def sizeHint(self, option, index):
        text = forceString(index.data())
        fontMetric = QtGui.QFontMetrics(option.font)
        rect = QRect(option.rect)
        rect = fontMetric.boundingRect(rect, Qt.Horizontal | Qt.TextWordWrap, text)
        height1 = rect.height()
        height2 = fontMetric.height() * 7
        return QSize(rect.width(), min(height1, height2))

    def paint(self, painter, option, index):
        painter.setFont(option.font)
        painter.setBrush(QBrush(Qt.black))
        if option.state & QStyle.State_Selected:
            painter.setPen(QPen(Qt.white))
        rect = QRect(option.rect)
        rect.setLeft(rect.left() + 4)
        rect.setTop(rect.top() + 4)
        rect.setWidth(rect.width() - 8)
        rect.setHeight(rect.height() - 8)
        painter.drawText(rect, Qt.Horizontal | Qt.TextWordWrap, forceString(index.data()))

class CDestinationsModel(CRecordListModel):

    ciTakeTime = 4
    ciInterval = 5
    notSaveItems = []

    def __init__(self, parent):
        CRecordListModel.__init__(self, parent)
        self.addHiddenCol('localId')
        self.addCol(CFormularyInDocTableCol(u'Препарат', 'drugItem_id', 50))                    # 0
        self.addCol(CInDocTableCol(u'Доза', 'drugDose', 15))                                    # 1
        self.addCol(CRBInDocTableCol(u'Ед. изм.', 'drugMeasureUnit_id', 14, 'rbUnit'))          # 2
        self.addCol(CRBInDocTableCol(u'Путь\nвведения', 'drugRouteId', 20, 'rbRoute'))          # 3
        self.addCol(CTakeDosesInDocTableCol(u'Время\nприёма', 'receivingTime', 100, parent))    # 4!
        self.addCol(CEnumInDocTableCol(u'Интервал', 'interval', 40, [u'ежедневно', u'через день', u'раз в два дня'])) #5!
        self.addCol(CDateInDocTableCol(u'Дата\nначала', 'takeDateBegin', 40))                   # 6
        self.addCol(CDateInDocTableCol(u'Дата\nокончания', 'takeDateEnd', 40))                  # 7
        self.addCol(CInDocTableCol(u'Коментарий', 'drugComment', 20))                           # 8
        self.addCol(CEnumInDocTableCol(u'Статус', 'drugStatus', 20, [u'новый', u'создано', u'назначено', u'сделан запрос', u'к выполнению', u'выполнено', u'не выполнено', u'отменено']).setReadOnly(True)) # 9
        self.addHiddenCol('takeDose')
        self.addHiddenCol('takeDate')
        self.addHiddenCol('takeTime')
        self.addHiddenCol('takeComment')
        self.addHiddenCol('actionParentId')
        self.addHiddenCol('rlsCode')
        self.setDirty(False)
        self.eventEditor = parent
        self._cachedRowColor = None

    def flags(self, index):
        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return flags

    def idList(self):
        idList = []
        for item in self._items:
            idList.append(forceInt(item.value('id')))
        return idList

    def itemById(self, id):
        for item in self._items:
            if forceInt(item.value('id')) == id:
                return item
        return None

    def findItemIdIndex(self, id):
        idList = self.idList()
        if id in idList:
            return idList.index(id)
        else:
            return -1


    def isUnsavedItems(self):
        for item in self._items:
            if forceInt(item.value('drugStatus')) == dsNew:
                return True
        return False


    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        column = index.column()
        if role == QtCore.Qt.DisplayRole and column == 8:
            comment = forceString(self._items[row].value('drugComment'))
            if comment:
                comment = u'Для аптеки: ' + comment
            rlsCode = forceInt(self._items[row].value('rlsCode'))
            if rlsCode > 0:
                rlsCodeRecord = QtGui.qApp.db.getRecordEx('rbRLS', 'name', 'code=%s' % rlsCode)
                if rlsCodeRecord:
                    rlsCode = forceString(rlsCodeRecord.value('name'))
                    if rlsCode:
                        if comment:
                            comment += '; '
                        comment += u'Рекомендованный препарат: ' + rlsCode
            return toVariant(comment)
        elif role == QtCore.Qt.BackgroundRole:
            return toVariant(self.getRowColor(row))
        elif role == QtCore.Qt.ToolTipRole:
                return CRecordListModel.data(self, index, Qt.DisplayRole)
        else:
            return CRecordListModel.data(self, index, role)

    def getItems(self):
        return self._items

    def setItems(self, items):
        self._items = items
        self.reset()

    def getRowColor(self, row):
        record = self._items[row]
        status = forceInt(record.value('drugStatus'))
        if status == dsCreated:
            self._cachedRowColor = QtGui.QColor(QtCore.Qt.cyan).lighter(factor=150)
        elif status == dsSet:
            self._cachedRowColor = QtGui.QColor(QtCore.Qt.gray).lighter(factor=150)
        elif status == dsQueried:
            self._cachedRowColor = QtGui.QColor(QtCore.Qt.yellow).lighter(factor=150)
        elif status == dsReady:
            self._cachedRowColor = QtGui.QColor(QtCore.Qt.green).lighter(factor=150)
        elif status == dsExecuted:
            self._cachedRowColor = QtGui.QColor(QtCore.Qt.blue).lighter(factor=150)
        elif status == dsNotExecuted:
            self._cachedRowColor = QtGui.QColor(QtCore.Qt.red).lighter(factor=150)
        elif status == dsCancelled:
            self._cachedRowColor = QtGui.QColor(QtCore.Qt.darkRed).lighter(factor=150)
        else:
            self._cachedRowColor = None
        return self._cachedRowColor

    def loadData(self, eventId, dateBegin, dateEnd, doctorMode):
        self._items = []

        if not eventId:
            self.reset()
            return

        db = QtGui.qApp.db

        stmt = u'''
            CALL getEventDrugDestinations('%(eventId)s', '%(dateBegin)s', '%(dateEnd)s', '%(doctorMode)d')
        ''' % {
            'eventId' : eventId,
            'dateBegin' : dateBegin.toString('yyyy-MM-dd'),
            'dateEnd' : dateEnd.toString('yyyy-MM-dd'),
            'doctorMode' : 1 if doctorMode else 0
        }

        query = db.query(stmt)
        while query.next():
            record = query.record()
            takeDate = forceString(record.value('takeDate'))
            takeDate = takeDate.split(',')
            takeDose = forceString(record.value('takeDose'))
            takeDose = takeDose.split(',')
            takeTime = forceString(record.value('takeTime'))
            takeTime = takeTime.split(',')

            stmtUnit = u'''
                    SELECT rbUnit.code
                    FROM rbUnit
                    WHERE rbUnit.id = %(id)s
                    ''' % {'id' : forceInt(record.value('drugMeasureUnit_id'))}
            queryUnit = QtGui.qApp.db.query(stmtUnit)
            if queryUnit.first():
                recordUnit = queryUnit.record()
                unit = '(' + forceString(recordUnit.value('code')) + ')'
            else:
                unit = ''

            destinationItems = []
            for dose in takeDose:
                item = dose + ' ' + unit if dose else ''
                destinationItems.append(item)

            i = 0
            if len(takeDate) > 1:
                date = QtCore.QDate(forceInt(takeDate[0][:4]), forceInt(takeDate[0][5:7]), forceInt(takeDate[0][8:]))
                date = date.addDays(1)
                endDate = QtCore.QDate(forceInt(takeDate[1][:4]), forceInt(takeDate[1][5:7]), forceInt(takeDate[1][8:]))
                while date != endDate:
                    date = date.addDays(1)
                    i += 1
            record.append(QtSql.QSqlField('interval'))
            record.setValue('interval', toVariant(i))

            itemDose = ''
            i = 0
            for date in takeDate:
                curDate = date[8:] + '.' + date[5:7] + '.' + date[:4]
                for time in takeTime:
                    curTime = time[:5]
                    itemDose += '(' + curDate + ' ' + curTime +') ' + destinationItems[i] + '; '
                    i += 1
            record.append(QtSql.QSqlField('receivingTime'))
            record.setValue('receivingTime', toVariant(itemDose))
            self._items.append(record)
        self.reset()

    def saveData(self, eventId, personId, notInComplexItems, inComplexItems=None):
        if not inComplexItems:
            inComplexItems = [[]]
        db = QtGui.qApp.db

        actionParentId = 0
        for item in notInComplexItems:
            self.saveItem(item, eventId, personId, actionParentId)

        if inComplexItems:
            for items in inComplexItems:
                actionParentId = 0
                if items:
                    stmt = u'''
                        CALL addOrgStructureDrugDestinationComplex('%(eventId)s', '%(personId)s')
                    ''' % {'eventId' : eventId,
                           'personId' : personId}
                    query = db.query(stmt)
                    if query.first():
                        record = query.record()
                        actionParentId = forceInt(record.value('actionComplexId'))

                for item in items:
                    self.saveItem(item, eventId, personId, actionParentId)

        return True

    def saveItem(self, item, eventId, personId, actionParentId):
        db = QtGui.qApp.db
        curDate = QtCore.QDate.currentDate()
        takeDose = forceString(item.value('takeDose'))
        takeTime = forceString(item.value('takeTime'))
        begDate = forceDate(item.value('takeDateBegin'))
        if not begDate:
            begDate = curDate
        endDate = forceDate(item.value('takeDateEnd'))
        if not endDate:
            endDate = curDate
        interval = forceInt(item.value('interval'))

        takeDose = takeDose.replace(',', ';')
        takeDose += ';'
        takeTime = takeTime.replace(',', '')
        takeTime = takeTime.replace(':00:00', '')
        rlsCode = forceInt(item.value('rlsCode'))

        stmt = u'''
            CALL addOrgStructureDrugDestination('%(eventId)s', '%(personId)s', '%(drugItemId)s', '%(type)s', '%(dose)s', '%(measureUnitId)s', '%(routeId)s', '%(rlsCode)s', '%(takeHours)s',
                                                '%(takeDose)s', '%(interval)s', '%(takeDateBegin)s', '%(takeDateEnd)s', '%(comment)s', '%(actionParentId)s',
                                                '%(takeDuration)s', '%(orgStructure)s')
        ''' % {
               'eventId' : eventId,
               'personId' : personId,
               'drugItemId' : forceInt(item.value('drugItem_id')),
               'dose' : forceInt(item.value('drugDose')),
               'type' : 1,
               'measureUnitId' : forceInt(item.value('drugMeasureUnit_id')),
               'routeId' : forceInt(item.value('drugRouteId')),
               'takeHours' : takeTime,
               'takeDose' : takeDose,
               'interval' : interval + 1,
               'takeDateBegin' : begDate.toString('yyyy-MM-dd'),
               'takeDateEnd' : endDate.toString('yyyy-MM-dd'),
               'comment' : forceString(item.value('drugComment')),
               'actionParentId' : actionParentId,
               'rlsCode' : rlsCode,
               'takeDuration' : begDate.daysTo(endDate),
               'orgStructure' : QtGui.qApp.currentOrgStructureId()
        }
        db.query(stmt)
        del self._items[self._items.index(item)]

    def setItem(self, item, personId, actionParentId):
        db = QtGui.qApp.db
        curDate = QtCore.QDate.currentDate()
        takeDose = forceString(item.value('takeDose'))
        takeTime = forceString(item.value('takeTime'))
        begDate = forceDate(item.value('takeDateBegin'))
        if not begDate:
            begDate = curDate
        endDate = forceDate(item.value('takeDateEnd'))
        if not endDate:
            endDate = curDate
        interval = forceInt(item.value('interval'))

        takeDose = takeDose.replace(',', ';')
        takeDose += ';'
        takeTime = takeTime.replace(',', '')
        takeTime = takeTime.replace(':00:00', '')
        rlsCode = forceInt(item.value('rlsCode'))

        stmt = u'''
            CALL setDrugDestination('%(actionId)s', '%(personId)s', '%(drugItemId)s', '%(dose)s', '%(measureUnitId)s', '%(routeId)s', '%(rlsCode)s', '%(takeHours)s',
                                                '%(takeDose)s', '%(interval)s', '%(takeDateBegin)s', '%(takeDateEnd)s', '%(comment)s', '%(actionParentId)s')
        ''' % {
               'actionId' : forceInt(item.value('actionId')),
               'personId' : personId,
               'drugItemId' : forceInt(item.value('drugItem_id')),
               'dose' : forceInt(item.value('drugDose')),
               'measureUnitId' : forceInt(item.value('drugMeasureUnit_id')),
               'routeId' : forceInt(item.value('drugRouteId')),
               'takeHours' : takeTime,
               'takeDose' : takeDose,
               'interval' : interval + 1,
               'takeDateBegin' : begDate.toString('yyyy-MM-dd'),
               'takeDateEnd' : endDate.toString('yyyy-MM-dd'),
               'comment' : forceString(item.value('drugComment')),
               'actionParentId' : actionParentId,
               'rlsCode' : rlsCode
        }

        db.query(stmt)

    def addItem(self, nomenclatureId, curComplexNumber = 0):
        newRecord = self.getEmptyRecord()
        for col in self._cols:
            if col.fieldName() == 'drugItem_id':
                newRecord.setValue(col.fieldName(), toVariant(nomenclatureId))
            elif col.fieldName() == 'drugMeasureUnit_id':
                stmt = '''
                    SELECT n.baseUnit_id AS unit_id
                    FROM rbStockNomenclature AS n
                    WHERE n.id = %(drugItemId)s
                    ''' % { 'drugItemId' : nomenclatureId }
                query = QtGui.qApp.db.query(stmt)
                if query.first():
                    record = query.record()
                    newRecord.setValue(col.fieldName(), toVariant(forceInt(record.value('unit_id'))))

        newRecord.setValue('actionParentId', toVariant(curComplexNumber))

        self.notSaveItems.append(newRecord)
        self.addRecord(newRecord)

    def addItems(self, drugFormularyItemIdList, rlsCodeList, curComplexNumber = 0):
        i = 0
        for drugFormularyItemId in drugFormularyItemIdList:
            newRecord = self.getEmptyRecord()
            newRecord.append(QSqlField('rlsCode'))
            if i < len(rlsCodeList) and rlsCodeList[i] > 0:
                newRecord.setValue('rlsCode', rlsCodeList[i])
            for col in self._cols:
                if col.fieldName() == 'drugItem_id':
                    newRecord.setValue(col.fieldName(), toVariant(drugFormularyItemId))
                elif col.fieldName() == 'drugMeasureUnit_id':
                    stmt = '''
                        SELECT rbMedicines.unit_id
                        FROM DrugFormulary_Item
                        INNER JOIN rbMedicines ON rbMedicines.id = DrugFormulary_Item.drug_id
                        WHERE DrugFormulary_Item.id = %(drugFormularyItemId)s
                        ''' % {'drugFormularyItemId' : drugFormularyItemId}
                    query = QtGui.qApp.db.query(stmt)
                    if query.first():
                        record = query.record()
                        newRecord.setValue(col.fieldName(), toVariant(forceInt(record.value('unit_id'))))
                elif col.fieldName() == 'drugComment':
                    strP = ''
                    if not self.isDestinationInFormulary(drugFormularyItemId):
                        strP += u'Выбранный препарат не из текущего формуляра. '
                    if rlsCodeList[i] > 0:
                        strP += u'Рекомендовано: ' + rlsCodeList[i] + ' '
                    newRecord.setValue(col.fieldName(), toVariant(strP))

            newRecord.setValue('actionParentId', toVariant(curComplexNumber))

            self.notSaveItems.append(newRecord)
            self.addRecord(newRecord)
            i += 1

    def setStatus(self, actId, status):          # Статус "Назначено"
        db = QtGui.qApp.db

        if status in (dsSet, dsCancelled):
            stmtAct = '''
            UPDATE ActionProperty_Integer
            SET ActionProperty_Integer.value = %(status)s
            WHERE ActionProperty_Integer.id = (SELECT ActionProperty.id
                                               FROM ActionProperty
                                               INNER JOIN ActionPropertyType ON ActionPropertyType.id = ActionProperty.type_id
                                                                                AND ActionPropertyType.deleted = 0
                                                                                AND ActionPropertyType.shortName = 'status'
                                                                                AND ActionPropertyType.typeName = 'Integer'
                                               WHERE ActionProperty.action_id = %(actId)s AND ActionProperty.deleted = 0)
            ''' % {'actId' : forceInt(actId),
                   'status' : status}

            queryAct = db.query(stmtAct)
            if queryAct.first():
                return True
        return False

    def getStatus(self, row):
        if row < len(self._items):
            record = self._items[row]
            return forceInt(record.value('drugStatus'))
        return None

    def delete(self, actId):
        db = QtGui.qApp.db

        stmt = u'''
            UPDATE DrugDestinationSchedule
            SET deleted = 1
            WHERE action_id = %(actId)s
        ''' % { 'actId' : actId }
        query = db.query(stmt)

        stmtAct = u'''
            UPDATE Action
            SET Action.deleted = 1
            WHERE Action.id = %(actId)s OR Action.id = (SELECT MAX(tempTab.parent_id)
                                                        FROM (SELECT act.parent_id
                                                              FROM Action AS act
                                                              WHERE act.id = %(actId)s) AS tempTab)
        ''' % { 'actId' : actId }
        queryAct = db.query(stmtAct)

        stmtActProp = u'''
            UPDATE ActionProperty
            SET deleted = 1
            WHERE action_id = %(actId)s
        ''' % { 'actId' : actId }
        queryActProp = db.query(stmtActProp)

        if query.first() and queryAct.first() and queryActProp.first():
            return True
        return False

    def deleteItems(self, delItems):
        for item in delItems:
            index = self.index(item, 0)
            if forceInt(self._items[item].value('drugStatus')) == dsNew:
                self.removeRow(item)
            elif forceInt(self._items[item].value('drugStatus')) in (dsCreated, dsSet):
                if index:
                    takeId = forceInt(self._items[item].value('actionId'))
                    self.delete(takeId)

    def updateDestinationsList(self, eventId,
                               doctorMode,
                               begDate = QtCore.QDate.currentDate(),
                               endDate = QtCore.QDate.currentDate(),
                               client = None,
                               drugItem = None,
                               status = None):
        notSaveItems = []
        for item in self._items:
            if forceInt(item.value('drugStatus')) == dsNew:
                notSaveItems.append(item)
        self.loadData(eventId, begDate, endDate, doctorMode)
        if len(self.notSaveItems) > 0:
            self._items.extend(notSaveItems)

    def getComplexSpan(self):
        i = 0
        spanList = []
        while i < len(self._items):
            parentId = forceInt(self._items[i].value('actionParentId'))
            if parentId != 0:
                spanItems = 0
                while (i + spanItems) < len(self._items) and parentId == forceInt(self._items[i + spanItems].value('actionParentId')):
                    spanItems += 1
                if spanItems > 1:
                    spanList.append([i, 1, spanItems, 1])
                    spanList.append([i, 2, spanItems, 1])
                    spanList.append([i, 3, spanItems, 1])
                    spanList.append([i, 4, spanItems, 1])
                    spanList.append([i, 5, spanItems, 1])
                    spanList.append([i, 6, spanItems, 1])
                    spanList.append([i, 7, spanItems, 1])
                    spanList.append([i, 9, spanItems, 1])
                i += spanItems
            else:
                i += 1
        return spanList

    def setDataToDosesSetupDialog(self, doses, hours, injectionPath, interval, begDate, endDate, curRow, comments):
        dose = ','.join([forceString(forceDouble(doseItem)) for doseItem in doses])
        commentList = ','.join([forceString(forceString(comment)) for comment in comments])
        sumDose = reduce(lambda x, y: x + y, doses) if doses else 0
        if forceDouble(forceInt(sumDose)) == sumDose:
            sumDose = forceInt(sumDose)
        takeHours = ','.join([hour.strftime('%H:%M:%S') for hour in hours])

        for row in range(curRow, curRow + self.getComplexLength(curRow)):
            self._items[row].setValue('drugDose', toVariant(sumDose))
            self._items[row].setValue('drugRouteId', toVariant(injectionPath))
            self._items[row].setValue('takeDose', toVariant(dose))
            self._items[row].setValue('interval', toVariant(interval))
            self._items[row].setValue('takeTime', toVariant(takeHours))
            self._items[row].setValue('takeDateBegin', toVariant(begDate))
            self._items[row].setValue('takeDateEnd', toVariant(endDate))
            self._items[row].setValue('takeComment', toVariant(commentList))

    def getDataToDosesSetupDialog(self, curRow):
        item = self._items[curRow]
        route = forceInt(item.value('drugRouteId'))
        beginDate = forceDate(item.value('takeDateBegin'))
        endDate = forceDate(item.value('takeDateEnd'))
        interval = forceInt(item.value('interval'))

        timesStr = forceString(item.value('takeTime'))
        times = timesStr.split(',') if timesStr else []

        timeList = sorted([datetime.datetime.strptime(time, '%H:%M:%S').time() if time else datetime.datetime.time() for time in times]) if times else []
        takeDose = forceString(item.value('takeDose'))
        doseItems = [forceDouble(dose) for dose in takeDose.split(',')] if takeDose else []

        stmt = u'''
               SELECT rbUnit.code
               FROM rbMedicines
               INNER JOIN DrugFormulary_Item ON rbMedicines.id = DrugFormulary_Item.drug_id
               INNER JOIN rbUnit ON rbUnit.id = rbMedicines.unit_id
               WHERE DrugFormulary_Item.id = %(id)s
               ''' % {'id' : forceInt(item.value('drugItem_id')) if curRow < len(self._items) else '0'}
        query = QtGui.qApp.db.query(stmt)
        unit = forceString(query.record().value(0)) if query.first() else ''

        commentsList = forceString(item.value('takeComment'))
        comments = commentsList.split(',') if commentsList else []
        return unit, timeList, doseItems, route, interval, beginDate, endDate, comments

    def getComplexLength(self, curRow):
        i = 0
        parentId = forceInt(self._items[curRow].value('actionParentId'))
        while (curRow + i) < len(self._items) and parentId != 0 and parentId == forceInt(self._items[curRow + i].value('actionParentId')):
            i += 1
        return i if i > 0 else 1

    def getEmptyRecord(self):
        newRecord = super(CDestinationsModel, self).getEmptyRecord()
        for col in self._cols:
            newRecord.append(QtSql.QSqlField(col.fieldName()))

        for col in self._hiddenCols:
            newRecord.append(QtSql.QSqlField(col))
        return newRecord
    
    def isDestinationInFormulary(self, drugFormularyItemId):
        if QtGui.qApp.currentOrgStructureId():
            orgStructureIdList = getOrgStructureDescendants(QtGui.qApp.currentOrgStructureId())
        else:
            orgStructureIdList = getOrgStructures(QtGui.qApp.currentOrgId())
        if len(orgStructureIdList) > 0:
            stmt = u'''
            SELECT DrugFormulary.id
            FROM DrugFormulary_Item
            INNER JOIN DrugFormulary ON DrugFormulary.id = DrugFormulary_Item.master_id
                                        AND DrugFormulary.orgStructure_id IN (%(orgStructures)s)
            WHERE DrugFormulary_Item.id = %(drugFormularyItemId)s
            ''' % {'drugFormularyItemId' : drugFormularyItemId,
                   'orgStructures': ', '.join(forceString(orgStructure) for orgStructure in orgStructureIdList)}
            query = QtGui.qApp.db.query(stmt)
            if query.first():
                return True
        return False