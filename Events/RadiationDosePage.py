# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from Events.ActionTypeCol       import CActionTypeCol

from library.DialogBase         import CConstructHelperMixin
from library.TableModel         import CTableModel, CCol, CDateCol, CRefBookCol, CSumCol
from library.Utils              import forceDouble, forceRef, forceString

from Registry.Utils             import getClientInfoEx

from Reports.ReportBase         import createTable, CReportBase
from Reports.ReportView         import CReportViewDialog

from Ui_RadiationDosePage       import Ui_RadiationDosePage


class CRadiationDosePage(QtGui.QWidget, Ui_RadiationDosePage, CConstructHelperMixin):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)

        self.addModels('RadiationDose',  CRadiationDoseModel(self))

        self.setModels(self.tblRadiationDose, self.modelRadiationDose, self.selectionModelRadiationDose)

        self.clientId = None
        self._onlyTotalDoseSumInfo = True



    def setClientId(self, clientId):
        self.clientId = clientId

        db = QtGui.qApp.db

        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableActionPropertyType = db.table('ActionPropertyType')

        queryTable = tableAction

        queryTable = queryTable.innerJoin(tableActionType,
                                          tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.innerJoin(tableActionPropertyType,
                                          tableActionPropertyType['actionType_id'].eq(tableActionType['id']))
        queryTable = queryTable.innerJoin(tableEvent,
                                          tableEvent['id'].eq(tableAction['event_id']))

        cond = [tableEvent['client_id'].eq(clientId),
                tableActionPropertyType['typeName'].eq(u'Доза облучения')]

        actionIdList = db.getDistinctIdList(queryTable, tableAction['id'].name(), cond)

        self.modelRadiationDose.setIdList(actionIdList)

        self.updateLabelsInfo()

    def updateLabelsInfo(self):
        self.updateLabelRecordCountInfo()
        self.updateLabelActionsSumInfo()
        self.updateLabelRadiationDoseInfo()

    def updateLabelRecordCountInfo(self):
        self.lblRecordCount.setText(u'Количество записей: %d'%len(self.modelRadiationDose.idList()))

    def updateLabelActionsSumInfo(self):
        self.lblActionSum.setText(u'Сумма количества действий: %.1f'%self.modelRadiationDose.actionsSum())

    def updateLabelRadiationDoseInfo(self):
        info = self.modelRadiationDose.radiationDoseSum()
        self.lblDoseSum.setRadiationDoseInfo(info)

    @QtCore.pyqtSlot()
    def on_btnRadiationDosePrint_clicked(self):
        def formatClientInfo(clientInfo):
            return u'\n'.join([u'ФИО: %s'           % clientInfo.fullName,
                               u'Дата рождения: %s' % clientInfo.birthDate,
                               u'Пол: %s'           % clientInfo.sex,
                               u'Код: %d'           % clientInfo.id])

        def formatRadiationDoseSumInfo(radiationDoseSumInfo):
            return '\n'.join(['%s: %s' % (key, item) for key, item in radiationDoseSumInfo.items() if key != 'total']+[u'Всего: %s'%radiationDoseSumInfo['total']])

        doc    = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Сигнальный лист учета дозы рентгеновского облучения')
        cursor.setCharFormat(CReportBase.TableBody)
        cursor.insertBlock()
        clientInfo = getClientInfoEx(self.clientId)
        cursor.insertText(formatClientInfo(clientInfo))
        cursor.insertBlock()

        tableColumns = [
            ('2%', [u'№' ], CReportBase.AlignLeft),
            ('20%', [u'Дата' ], CReportBase.AlignLeft),
            ('20%', [u'Вид рентгенологического исследования'], CReportBase.AlignLeft),
            ('10%', [u'Количество снимков'], CReportBase.AlignRight),
            ('25%', [u'Суммарная доза облучения'], CReportBase.AlignRight),
            ]
        table = createTable(cursor, tableColumns)

        for idRow, id in enumerate(self.modelRadiationDose.idList()):
            values = [idRow+1,
                      forceString(self.modelRadiationDose.data(self.modelRadiationDose.index(
                            idRow, self.modelRadiationDose.columnIndex(u'Дата выполнения')))),
                      forceString(self.modelRadiationDose.data(self.modelRadiationDose.index(
                            idRow, self.modelRadiationDose.columnIndex(u'Тип действия')))),
                      forceDouble(self.modelRadiationDose.data(self.modelRadiationDose.index(
                            idRow, self.modelRadiationDose.columnIndex(u'Количество')))),
                      forceDouble(self.modelRadiationDose.data(self.modelRadiationDose.index(
                            idRow, self.modelRadiationDose.columnIndex(u'Доза'))))
                     ]

            i = table.addRow()
            for column, value in enumerate(values):
                table.setText(i, column, value)

        i = table.addRow()
        table.setText(i, 0, u'Итого')
        table.setText(i, 3, self.modelRadiationDose.actionsSum())
        table.setText(i, 4, formatRadiationDoseSumInfo(self.modelRadiationDose.radiationDoseSum()))

        cursor.movePosition(QtGui.QTextCursor.End)

        result = '          '.join(['\n\n\n'+forceString(QtCore.QDate.currentDate()),
                                  u'ФИО: %s' % clientInfo.fullName])
        cursor.insertText(result)
        cursor.insertBlock()

        view = CReportViewDialog(self)
        view.setText(doc)
        view.exec_()


# #######################################################

class CRadiationDoseCol(CCol):
    def __init__(self, title, fields, defaultWidth):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self._cacheValues = {}

    def format(self, values):
        actionId = forceRef(values[0])
        value = self._cacheValues.get(actionId, None)
        if value is None:
            db = QtGui.qApp.db

            tableAction = db.table('Action')
            tableActionProperty = db.table('ActionProperty')
            tableActionPropertyType = db.table('ActionPropertyType')
            tableActionPropertyDouble = db.table('ActionProperty_Double')

            queryTable = tableAction

            queryTable = queryTable.innerJoin(tableActionProperty,
                                              tableActionProperty['action_id'].eq(tableAction['id']))
            queryTable = queryTable.innerJoin(tableActionPropertyType,
                                              tableActionPropertyType['id'].eq(tableActionProperty['type_id']))
            queryTable = queryTable.innerJoin(tableActionPropertyDouble,
                                              tableActionPropertyDouble['id'].eq(tableActionProperty['id']))

            cond = [tableAction['id'].eq(actionId),
                    tableActionPropertyType['typeName'].eq(u'Доза облучения')]

            record = db.getRecordEx(queryTable, tableActionPropertyDouble['value'].name(), cond)
            value = record.value('value') if record else CCol.invalid
            self._cacheValues[actionId] = value

        return value


class CRadiationDoseUnitCol(CCol):
    def __init__(self, title, fields, defaultWidth):
        CCol.__init__(self, title, fields, defaultWidth, 'l')
        self._cacheValues = {}
        self._isRTF = True

    def format(self, values):
        actionId = forceRef(values[0])
        value = self._cacheValues.get(actionId, None)
        if value is None:
            db = QtGui.qApp.db

            tableAction = db.table('Action')
            tableActionType = db.table('ActionType')
            tableActionPropertyType = db.table('ActionPropertyType')
            tableUnit = db.table('rbUnit')

            queryTable = tableAction

            queryTable = queryTable.innerJoin(tableActionType,
                                              tableActionType['id'].eq(tableAction['actionType_id']))
            queryTable = queryTable.innerJoin(tableActionPropertyType,
                                              tableActionPropertyType['actionType_id'].eq(tableActionType['id']))
            queryTable = queryTable.innerJoin(tableUnit,
                                              tableUnit['id'].eq(tableActionPropertyType['unit_id']))

            cond = [tableAction['id'].eq(actionId),
                    tableActionPropertyType['typeName'].eq(u'Доза облучения')]

            record = db.getRecordEx(queryTable, [tableUnit['name'].name(), tableUnit['code'].name()], cond)
            value = QtCore.QDate.QVariant(' | '.join([
                                         forceString(record.value('code')),
                                         forceString(record.value('name'))
                                        ]
                                       )
                            ) if record else CCol.invalid
            self._cacheValues[actionId] = value

        return value

class CRadiationDoseModel(CTableModel):
    def __init__(self, parent):
        CTableModel.__init__(self, parent)
        self._columnNames = []
        self.addColumn(CDateCol(u'Дата выполнения', ['endDate'], 18))
        self.addColumn(CActionTypeCol(u'Тип действия', 30, 2))
        self.addColumn(CRefBookCol(u'Исполнитель', ['person_id'], 'vrbPersonWithSpeciality', 30))
        self.addColumn(CSumCol(u'Количество', ['amount'], 14))
        self.addColumn(CRadiationDoseCol(u'Доза', ['id'], 10))
        self.addColumn(CRadiationDoseUnitCol(u'Ед.из', ['id'], 15))
        self.setTable('Action', recordCacheCapacity=None)



    def addColumn(self, col):
        self._columnNames.append(forceString(col.title()))
        CTableModel.addColumn(self, col)

    def columnIndex(self, columnTitle):
        return self._columnNames.index(columnTitle)

    def actionsSum(self):
        result = 0
        for id in self._idList:
            result += forceDouble(self.getRecordById(id).value('amount'))
        return result


    def radiationDoseSum(self):
        radiationDoseColumnIndex = self.columnIndex(u'Доза')
        radiationDoseUnitColumnIndex = self.columnIndex(u'Ед.из')
        result = {'total':0}
        for row in xrange(self.rowCount()):
            unit = forceString(self.data(self.index(row, radiationDoseUnitColumnIndex)))
            radiationDose = forceDouble(self.data(self.index(row, radiationDoseColumnIndex)))

            result['total'] += radiationDose

            if not unit in result.keys():
                result[unit] = radiationDose
            else:
                result[unit] += radiationDose

        return result






