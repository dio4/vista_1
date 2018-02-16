# -*- coding: utf-8 -*-

from collections import defaultdict

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, QModelIndex
from Events.Action import ActionClass
from Events.Utils import getMainActionTypesAnalyses
from Events.ActionTypeComboBox import CActionTypeTableCol
from Users.Rights import urAdmin
from library.InDocTable import CInDocTableModel, CRBInDocTableCol, CDateInDocTableCol, CRecordListModel, CInDocTableView, \
    CInDocTableCol, CFloatInDocTableCol
from library.Utils import forceRef, forceString, toVariant, forceInt, forceDouble
from library.Utils import forceDate


class CSumCol(CFloatInDocTableCol):
    def __init__(self, title, fieldName, width, **params):
        CFloatInDocTableCol.__init__(self, title, fieldName, width, **params)

    def toString(self, val, record):
        return self._toString(toVariant(forceDouble(val) * forceDouble(record.value('amount'))))


class CAnalysesRecommendationMixin(object):
    def __init__(self):
        self._analysesRecommendations = set()
        self._analysesRecommendationMap = defaultdict(list)
        self._mainActionTypesAnalyses = set(getMainActionTypesAnalyses())
        boldFont = QtGui.QFont()
        boldFont.setWeight(QtGui.QFont.Bold)
        self._mainAnalysesActionTypeFont = toVariant(boldFont)

    def isAnalysesRecommendation(self, recommendationId):
        return recommendationId in self._analysesRecommendations

    def isMainActionTypeAnalyses(self, actionTypeId):
        return actionTypeId in self._mainActionTypesAnalyses

    def resetAnalyses(self, idList, resetCache=True):
        if not resetCache or not idList:
            return idList

        self._analysesRecommendations.clear()
        self._analysesRecommendationMap.clear()

        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        tableRecommendation = db.table('Recommendation')

        table = tableRecommendation.innerJoin(tableActionType, [tableActionType['id'].eq(tableRecommendation['actionType_id']),
                                                                tableActionType['class'].eq(ActionClass.Analyses)])
        cols = [
            tableRecommendation['id'],
            tableActionType['id'].alias('actionTypeId'),
            tableActionType['group_id']
        ]
        recList = db.getRecordList(table, cols, tableRecommendation['id'].inlist(idList))

        actionTypeRecommendationMap = dict((forceRef(rec.value('actionTypeId')),
                                            forceRef(rec.value('id'))) for rec in recList)
        for rec in recList:
            recommendationId = forceRef(rec.value('id'))
            mainActionTypeId = forceRef(rec.value('group_id'))
            self._analysesRecommendations.add(recommendationId)
            if mainActionTypeId:
                mainRecommendationId = actionTypeRecommendationMap.get(mainActionTypeId)
                if mainRecommendationId:
                    self._analysesRecommendationMap[mainRecommendationId].append(recommendationId)

        return [recId for recId in idList if recId not in self._analysesRecommendations] + \
               [recId for recId in idList if recId in self._analysesRecommendations]


class CRecommendationsModel(CInDocTableModel, CAnalysesRecommendationMixin):
    def __init__(self, parent):
        CAnalysesRecommendationMixin.__init__(self)
        CInDocTableModel.__init__(self, 'Recommendation', 'id', 'setEvent_id', parent)
        self.__parent = parent
        self.clientId = None
        self.personId = None
        self.contractId = None
        self.addCol(CRBInDocTableCol(u'Врач', 'person_id', 10, 'vrbPersonWithSpeciality', parent=parent).setReadOnly())
        self.addCol(CDateInDocTableCol(u'Дата рекомендации', 'setDate', 15).setReadOnly())
        self.addCol(CActionTypeTableCol(u'Рекомендация', 'actionType_id', 15, None, classesVisible=True).setReadOnly())
        self.addCol(CFloatInDocTableCol(u'Цена', 'price', 7, precision=2).setReadOnly())
        self.addCol(CInDocTableCol(u'Количество', 'amount', 7, precision=2))
        self.addCol(CSumCol(u'Сумма', 'price', 7, precision=2).setReadOnly())
        self.addCol(CDateInDocTableCol(u'Актуально до', 'expireDate', 15).setReadOnly())

        self.ActionTypeColIndex = self.getColIndex('actionType_id')

    def setClientId(self, clientId):
        self.clientId = clientId

    def flags(self, index = QtCore.QModelIndex()):
        flags = super(CRecommendationsModel, self).flags(index)
        items = self._items
        if index.isValid():
            if (flags & QtCore.Qt.ItemIsEditable) and index.row() >= len(self._items):
                flags ^= QtCore.Qt.ItemIsEditable
            if index.row() < len(self._items):
                record = items[index.row()]
                if (flags & QtCore.Qt.ItemIsEditable) and forceRef(record.value('id')) is not None:
                    flags ^= QtCore.Qt.ItemIsEditable
        return flags

    def formatActionTypeAnalyses(self, record):
        actionTypeId = forceRef(record.value('actionType_id'))
        col = self.cols()[self.ActionTypeColIndex]
        prefix = '' if self.isMainActionTypeAnalyses(actionTypeId) else ' ' * 10
        actionName = forceString(col.toString(record.value(col.fieldName()), record))
        return QtCore.QVariant(prefix + actionName)

    def loadItems(self, masterId):
        super(CRecommendationsModel, self).loadItems(masterId)
        idList = [forceRef(rec.value('id')) for rec in self.items()]
        self.resetAnalyses(idList)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()

        row, column = index.row(), index.column()
        if 0 <= row < len(self._items):
            if role == Qt.DisplayRole and column == self.ActionTypeColIndex:
                record = self._items[row]
                if self.isAnalysesRecommendation(forceRef(record.value('id'))):
                    return self.formatActionTypeAnalyses(record)

            elif role == Qt.FontRole and column == self.ActionTypeColIndex:
                record = self._items[row]
                if self.isMainActionTypeAnalyses(forceRef(record.value('actionType_id'))):
                    return self._mainAnalysesActionTypeFont

        return super(CRecommendationsModel, self).data(index, role)

    def setData(self, index, value, role=Qt.EditRole):
        column = index.column()
        row = index.row()
        if role == Qt.EditRole:
            if row == len(self._items):
                if value.isNull():
                    return False

            if column == self.getColIndex('actionType_id'):
                db = QtGui.qApp.db
                actionTypeId = forceRef(value)

                for r in range(self.rowCount() - 1):
                    record = self._items[r]
                    otherActionTypeId = forceRef(record.value('actionType_id'))
                    otherActionExpireDate = forceDate(record.value('expireDate'))
                    otherActionAmountLeft = forceDouble(record.value('amount_left'))
                    otherPerson2Id = forceRef(record.value('person2_id'))
                    currentDate = QtCore.QDate.currentDate()
                    if actionTypeId == otherActionTypeId and currentDate <= otherActionExpireDate and otherActionAmountLeft > 0.0 and not otherPerson2Id:
                        person = forceString(db.translate('vrbPerson', 'id', record.value('person_id'), 'name'))
                        date = forceString(record.value('setDate'))
                        currentActionTypeId = self._items[row].value('actionType_id')
                        actionCode = forceString(db.translate('ActionType', 'id', actionTypeId, 'code'))
                        actionName = forceString(db.translate('ActionType', 'id', actionTypeId, 'name'))
                        if currentActionTypeId != actionTypeId:
                            QtGui.QMessageBox.warning(
                                None,  #TODO: mdldml: неплохо бы получить виджет-предок, amirite?
                                u'Внимание!',
                                u'Услуга ' + actionCode + u'|' + actionName + u' была рекомендована врачом ' + person + u' и ' + date,
                                QtGui.QMessageBox.Close
                            )
                        return False

                stmt = u'''
                    SELECT
                        Recommendation.setDate AS date,
                        vrbPerson.name AS person
                    FROM
                        Recommendation
                        INNER JOIN vrbPerson ON Recommendation.person_id = vrbPerson.id
                        INNER JOIN Event ON Recommendation.setEvent_id = Event.id
                        INNER JOIN ActionType ON Recommendation.actionType_id = ActionType.id
                    WHERE
                        Event.client_id = %s
                        AND Recommendation.deleted = 0
                        AND Recommendation.actionType_id = %s
                        AND Recommendation.amount_left > 0.0
                        AND Recommendation.person2_id IS NULL
                        AND DATE(NOW()) <= Recommendation.expireDate
                    LIMIT 1
                '''
                query = db.query(stmt % (self.clientId, forceString(value)))
                if query.next():
                    record = query.record()
                    person = forceString(record.value('person'))
                    date = forceString(record.value('date'))
                    currentActionTypeId = self._items[row].value('actionType_id') if row < len(self._items) else None
                    if currentActionTypeId != actionTypeId:
                        actionCode = forceString(db.translate('ActionType', 'id', actionTypeId, 'code'))
                        actionName = forceString(db.translate('ActionType', 'id', actionTypeId, 'name'))
                        QtGui.QMessageBox.warning(
                            None,
                            u'Внимание!',
                            u'Услуга ' + actionCode + u'|' + actionName + u' была рекомендована врачом ' + person + u' и ' + date,
                            QtGui.QMessageBox.Close
                        )
                    return False

                if row == len(self._items):
                    self._items.append(self.getEmptyRecord(actionTypeId))
                    count = len(self._items)
                    rootIndex = QModelIndex()
                    self.beginInsertRows(rootIndex, count, count)
                    self.insertRows(count, 1, rootIndex)
                    self.endInsertRows()
                record = self._items[row]  #todo: заменить на getEmptyRecord или проставить все изменившиеся поля, потому что amount и expirePeriod зависят от actionType_id
                col = self._cols[column]
                record.setValue(col.fieldName(), value)
                self.emitCellChanged(row, column)
                return True

            elif column == self.getColIndex('amount'):
                result = CRecordListModel.setData(self, index, value, role)
                if result:
                    record = self._items[row]
                    record.setValue('amount_left', record.value('amount'))
                return result

        return CRecordListModel.setData(self, index, value, role)

    def updatePersonId(self, personId):
        self.personId = personId
        for row in range(self.rowCount() - 1):
            eventId = forceRef(self._items[row].value('setEvent_id'))
            if eventId is None:
                index = self.index(row, self.getColIndex('person_id'))
                self.setData(index, toVariant(personId))

    def updateContractId(self, contractId):
        self.contractId = contractId

    def getEmptyRecord(self, actionTypeId=None):
        result = CInDocTableModel.getEmptyRecord(self)
        result.setValue('person_id', toVariant(self.personId))
        currentDate = QtCore.QDate.currentDate()
        result.setValue('setDate', toVariant(currentDate))
        if actionTypeId:
            actionTypeRecord = QtGui.qApp.db.getRecord('ActionType', '*', actionTypeId)
            expirePeriod = forceInt(actionTypeRecord.value('recommendationExpirePeriod'))
            result.setValue('expireDate', toVariant(currentDate.addDays(expirePeriod)))
            result.setValue('amount', actionTypeRecord.value('amount'))
            result.setValue('amount_left', actionTypeRecord.value('amount'))
        return result


class CRecommendationsView(CInDocTableView):
    def on_popupMenu_aboutToShow(self):
        CInDocTableView.on_popupMenu_aboutToShow(self)
        row = self.currentIndex().row()
        if row < len(self.model().items()):
            record = self.model().items()[row]

            if forceRef(record.value('id')) is None:
                self._CInDocTableView__actDeleteRows.setEnabled(True)
            elif not record.value('execDate').isNull() or QtCore.QDate.currentDate() > forceDate(record.value('expireDate')):
                self._CInDocTableView__actDeleteRows.setEnabled(False)
            elif QtGui.qApp.userId == self.model().personId or QtGui.qApp.userHasRight(urAdmin):
                self._CInDocTableView__actDeleteRows.setEnabled(True)
            else:
                self._CInDocTableView__actDeleteRows.setEnabled(False)

    def addAddToActions(self):
        self.__actAddToActions = QtGui.QAction(u'Добавить в Мероприятия', self)
        self.__actAddToActions.setObjectName('actDeleteRows')
        self._popupMenu.addAction(self.__actAddToActions)
        self.connect(self.__actAddToActions, QtCore.SIGNAL('triggered()'), self.on_actAddToActions)

    def on_actAddToActions(self):
        if hasattr(self.eventEditor, 'tblActions'):
            row = self.currentIndex().row()
            if row < len(self.model().items()):
                record = self.model().items()[row]
                actionsModel = self.eventEditor.tblActions.model()
                index = actionsModel.index(actionsModel.rowCount() - 1, 0)
                actionsModel.setData(index, toVariant(record.value('actionType_id')))
                actionsModel.emitDataChanged()

