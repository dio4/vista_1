# -*- coding: utf-8 -*-


from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QVariant

from Reports.Report import CReport
from Reports.ReportBase import CReportBase, createTable
from library.DialogBase import CDialogBase
from Ui_Smp import Ui_Form
from SmpService import SmpExchange
from library.InDocTable import CInDocTableModel, CInDocTableCol, forceInt
from library.TableModel import CTextCol
from library.Utils import forceString, toVariant, forceDate, getVal, forceBool, forceTime
from Ui_ReportCallsSmp import Ui_Dialog


class CSmpWindow(CDialogBase, Ui_Form):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.db = QtGui.qApp.db
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        if not forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'smpService', False)) or not forceString(getVal(QtGui.qApp.preferences.appPrefs, 'smpAddress', '')):
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Не введен адрес сервиса')
        try:
            self.exchange = SmpExchange()
        except Exception as ex:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Не удалось установить соединение \n %s' % forceString(ex.message))
        self.addModels('Events', CEventsModel(self))
        self.addModels('CallsSmp', CCallsSmpModel(self))
        self.tblEvents.setModel(self.modelEvents)
        self.tblEvents.setSelectionModel(self.selectionModelEvents)
        self.setModels(self.tblCallsSmp, self.modelCallsSmp, self.selectionModelCallsSmp)
        self.connect(self.selectionModelEvents, QtCore.SIGNAL('currentChanged(QModelIndex, QModelIndex)'),
                     self.on_selectionModelEvents_currentChanged)
        self.exchange.getEventList()
        self.loadData()
        self.clearData()
        # Типы событий. Не вижу смысла для этого создавать отдельную таблицу.
        eventTypes = [u'', u'Принят звонок от пациента', u'Пациент отказался от вызова', u'Отказ ПНМП', u'Принят звонок из ПНМП',
                      u'Изменился адрес', u'Вызов выполнен', u'Вызов передан на 03', u'Вызов безрезультатный', u'Назначен ошибочный ПНМП']

        self.cmbResult.addItems(eventTypes)
        self.dtFilterDate.setDate(QtCore.QDate.currentDate())
        self.edtCallSmpBegDate.setDate(QtCore.QDate.currentDate())
        self.edtCallSmpEndDate.setDate(QtCore.QDate.currentDate())
        self.tblCallsSmp.setSortingEnabled(True)


    def loadData(self):
        self.tblEvents.model().loadItems(0)
        self.tblEvents.resizeColumnsToContents()

    def exec_(self):
        result = CDialogBase.exec_(self)
        return result

    def clearData(self):
        self.edtCallNumber.clear()
        self.dtCallDate.clear()
        self.tmEventTime.clear()
        self.edtReceiver.clear()
        self.edtClientFIO.clear()
        self.edtAge.clear()
        self.edtSex.clear()
        self.edtContact.clear()
        self.edtAddress.clear()
        self.edtCallType.clear()
        self.edtCallerName.clear()
        self.edtUrgency.clear()

    def getFilter(self):
        filt = []
        if self.edtFilterNumber.isEnabled():
            filt.append('callNumberId = %s' % self.edtFilterNumber.text())
        if self.dtFilterDate.isEnabled():
            filt.append('callDate = \'%s\'' % self.dtFilterDate.text())
        if self.edtFilterFIO.isEnabled():
            filt.append('fio = \'%s\'' % self.edtFilterFIO.text())
        if self.cmbFilterDoneEvents.isEnabled():
            if self.cmbFilterDoneEvents.currentIndex():
                if self.cmbFilterDoneEvents.currentIndex() == 1:
                    filt.append('isDone = 1')
                elif self.cmbFilterDoneEvents.currentIndex() == 2:
                    filt.append('isDone in (0, 1)')
        result = ' AND '.join(filt)
        return result

    @QtCore.pyqtSlot()
    def on_btnGetEvents_clicked(self):
        self.exchange.getEventList()
        self.loadData()

    @QtCore.pyqtSlot()
    def on_selectionModelEvents_currentChanged(self):
        self.clearData()
        item = self.tblEvents.model().items()[self.tblEvents.currentIndex().row()]
        if item:
            if forceInt(item.value('sex')):
                sex = u'Женский'
            else:
                sex = u'Мужской'
            self.edtCallNumber.setText(forceString(item.value('callNumberId')))
            self.dtCallDate.setDate(forceDate(item.value('callDate')))
            self.tmEventTime.setTime(forceTime(item.value('eventTime')))
            self.edtReceiver.setText(forceString(item.value('receiver')))
            self.edtClientFIO.setText(forceString(item.value('fio')))
            self.edtAge.setText(forceString(item.value('age')))
            self.edtSex.setText(sex)
            self.edtContact.setText(forceString(item.value('contact')))
            self.edtAddress.setText(forceString(item.value('address')))
            self.edtCallerName.setText(forceString(item.value('callerName')))
            self.edtUrgency.setText(forceString(item.value('urgencyCategory')))
            self.edtCallType.setText(forceString(item.value('callKind')))



    @QtCore.pyqtSlot()
    def on_btnAprovedEvent_clicked(self):
        tablePerson = self.db.table('Person')
        tableSmp = self.db.table('SmpEvents')
        item = self.tblEvents.model().items()[self.tblEvents.currentIndex().row()]
        if item:
            recEvent = self.db.getRecordEx(tableSmp, '*', tableSmp['callNumberId'].eq(forceString(item.value('callNumberId'))))
            if recEvent:
                respoce = self.exchange.updEvent(forceInt(recEvent.value('id')))
                if respoce:
                    recUser = self.db.getRecordEx(tablePerson, [tablePerson['lastName'], tablePerson['firstName'],
                                                                tablePerson['patrName'],
                                                                tablePerson['id'].eq(QtGui.qApp.userId)])
                    recEvent.setValue('eventTime', toVariant(forceString(QtCore.QDateTime.currentDateTime().time()) + ':00'))
                    recEvent.setValue('receiver', toVariant(forceString(recUser.value('lastName')) + u' ' + forceString(
                        recUser.value('firstName')) + u' ' + forceString(recUser.value('patrName'))))
                    self.db.updateRecord(tableSmp, recEvent)
                    QtGui.QMessageBox.information(self, u'Успешно', u'Вызов успешно принят')
                else:
                    QtGui.QMessageBox.warning(self, u'Ошибка', u'Не удалось принять вызов')

    @QtCore.pyqtSlot()
    def on_btnAddEvent_clicked(self):
        tableSmpEvents = self.db.table('SmpEvents')
        item = self.tblEvents.model().items()[self.tblEvents.currentIndex().row()]
        if forceInt(self.cmbResult.currentIndex()):
            responce = self.exchange.addEvent(forceString(item.value('callNumberId')), forceInt(self.cmbResult.currentIndex()), self.edtNote.text())
        else:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Не выбран результат события')
            return
        if responce:
            recEvent = self.db.getRecordEx(tableSmpEvents, '*', tableSmpEvents['callNumberId'].eq(forceString(item.value('callNumberId'))))
            if recEvent:
                recEvent.setValue('result', toVariant(self.cmbResult.currentText()))
                recEvent.setValue('isDone', toVariant(1))
                self.db.updateRecord(tableSmpEvents, recEvent)
                QtGui.QMessageBox.information(self, u'Успешно', u'Событие успешно добавлено')
                self.loadData()
        else:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'При регистрации события возникла ошибка')

    @QtCore.pyqtSlot(bool)
    def on_chkFilterNumber_clicked(self, checked):
        self.edtFilterNumber.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterDate_clicked(self, checked):
        self.dtFilterDate.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterFIO_clicked(self, checked):
        self.edtFilterFIO.setEnabled(checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFilterDoneEvents_clicked(self, checked):
        self.cmbFilterDoneEvents.setEnabled(checked)

    @QtCore.pyqtSlot()
    def on_btnFilter_clicked(self):
        self.tblEvents.model().setFilter(self.getFilter())
        self.loadData()

    ######################Вызовы смп###################################
    @QtCore.pyqtSlot()
    def on_btnCallSmpGet_clicked(self):
        # self.tblCallsSmp.reset()
        items = self.exchange.getCallListStr(forceString(self.edtCallSmpBegDate.date()),
                                             forceString(self.edtCallSmpEndDate.date()))
        self.modelCallsSmp.loadData(items)
        self.tblCallsSmp.resizeColumnsToContents()

    @QtCore.pyqtSlot()
    def on_btnCallSmpPrint_clicked(self):
        CReportCallsSmp(self, forceString(self.edtCallSmpBegDate.date()),
                              forceString(self.edtCallSmpEndDate.date())).exec_()





#############Utils##############
class CEventsModel(CInDocTableModel):
    def __init__(self, parent):
        CInDocTableModel.__init__(self, 'SmpEvents', 'id', 'isDone', parent)
        self.addCol(CInDocTableCol(u'Ид', 'eventId', 20)).setReadOnly()
        self.addCol(CInDocTableCol(u'Номер вызова', 'callNumberId', 30)).setReadOnly()
        self.addCol(CInDocTableCol(u'Дата вызова', 'callDate', 15)).setReadOnly()
        self.addCol(CInDocTableCol(u'ФИО', 'fio', 40)).setReadOnly()
        self.addCol(CInDocTableCol(u'Адрес', 'address', 60)).setReadOnly()
        self.addCol(CInDocTableCol(u'Ориентиры', 'landmarks', 60)).setReadOnly()
        self.addCol(CInDocTableCol(u'Причина вызова', 'occasion', 60)).setReadOnly()
        self.addHiddenCol('contact')
        self.addHiddenCol('age')
        self.addHiddenCol('callerName')
        self.addHiddenCol('urgencyCategory')
        self.addHiddenCol('callKind')
        self.addHiddenCol('eventTime')
        self.addHiddenCol('receiver')
        self.addHiddenCol('sex')
        self.setEditable(False)

class CBaseCallsSmpModel(QtCore.QAbstractTableModel):
    headerText = [u'Номер вызова', u'Дата и время вызова', u'ФИО', u'Пол', u'Полных лет', u'Телефон']
    # tables = smartDict()

    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.items = []
        self.headerSortingCol = {}
        self._cols = []
        self.mapColFieldNameToColIndex = {}
        self._isSorted = False
        self._sortColumn = 0
        self._sortOrder = QtCore.Qt.AscendingOrder

    def cols(self):
        return self._cols

    def getColumnByFieldName(self, fieldName):
        if fieldName not in self.mapColFieldNameToColIndex:
            for i, column in enumerate(self.cols()):
                fields = column.fields()
                for field in fields:
                    if field not in self.mapColFieldNameToColIndex:
                        self.mapColFieldNameToColIndex[field] = i
        index = self.mapColFieldNameToColIndex.get(fieldName, None)
        return self.cols()[index]

    def columnCount(self, index=QtCore.QModelIndex()):
        return len(self._cols)

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.items)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(self.headerText[section])
            elif role == QtCore.Qt.ToolTipRole:
                return QtCore.QVariant(self._cols[section].title(short=False))
        return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        column = index.column()
        row = index.row()
        if role == QtCore.Qt.DisplayRole:
            item = self.items[row]
            if column == 0:
                return toVariant(item['number'])
            elif column == 1:
                return toVariant(item['date'])
            elif column == 2:
                return toVariant(item['fio'])
            elif column == 3:
                return toVariant(item['sex'])
            elif column == 4:
                return toVariant(item['age'])
            elif column == 5:
                return toVariant(item['contact'])
        return QtCore.QVariant()

    def formColumns(self):
        self._cols = []
        self._cols.append(CTextCol(u'Номер вызова', ['number'], 15, 'l'))
        self._cols.append(CTextCol(u'Дата и время вызова', ['date'], 15, 'l'))
        self._cols.append(CTextCol(u'ФИО', ['fio'], 15, 'l'))
        self._cols.append(CTextCol(u'Пол', ['sex'], 15, 'l'))
        self._cols.append(CTextCol(u'Полных лет', ['age'], 15, 'l'))
        self._cols.append(CTextCol(u'Телефон', ['contact'], 15, 'l'))

    def getQueryCols(self):
        cols = []
        return cols

    def getCondAndQueryTable(self):
        pass

    def getItemFromRecord(self, item):
        return {
            'number': forceString(item.number),
            'date': forceString(item.callDate) + u' ' + forceString(item.endReceivingCall)[:8],
            'fio': forceString(item.lastName) + u' ' + forceString(item.name) + u' ' + forceString(item.patronymic),
            'sex': u'женский' if forceInt(item.sex) else u'мужской',
            'age': forceString(item.ageYears) if item.ageYears and forceInt(item.ageYears) > 0 else u'',
            'contact': forceString(item.telephone)
        }

    def sort(self, column, order=QtCore.Qt.AscendingOrder):
        if column != self._sortColumn:
            self._sortColumn = column
            self._isSorted = False
        if order != self._sortOrder:
            self._sortOrder = order
            self._isSorted = False
        if self.items and not self._isSorted:
            self.items.sort(key=lambda x: x[self.cols()[column]._fields[0]], reverse=order == QtCore.Qt.DescendingOrder)
            self._isSorted = True
            self.reset()

class CCallsSmpModel(CBaseCallsSmpModel):
    def __init__(self, parent):
        self.parentWidget = parent
        CBaseCallsSmpModel.__init__(self, parent)
        self.items = []
        self.idList = []
        self.formColumns()
        self.isColor = False
        self._isSorted = False
        self._sortColumn = 0
        self._sortOrder = QtCore.Qt.AscendingOrder

    def data(self, index, role=QtCore.Qt.DisplayRole):
        return CBaseCallsSmpModel.data(self, index, role)

    def loadData(self, callList):
        self.items = []
        for call in callList:
            item = self.getItemFromRecord(call)
            self.items.append(item)
        self.reset()

class CReportCallsSmp(CReport):
    def __init__(self, parent, begDate, endDate):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчет: вызовы СМП')
        self.begDate = begDate
        self.endDate = endDate
        if not forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'smpService', False)) or not forceString(getVal(QtGui.qApp.preferences.appPrefs, 'smpAddress', '')):
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Не введен адрес сервиса')
        try:
            self.exchange = SmpExchange()
        except Exception as ex:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'Не удалось установить соединение \n %s' % forceString(ex.message))

    def getSetupDialog(self, parent):
        result = CProtocol(self.begDate, self.endDate, parent=parent)
        result.setTitle(self.title())
        return result

    def setParams(self):
        pass

    def getAddrStrCall(self, callInfo):
        settlement = u'нас. пункт: ' + forceString(callInfo.settlement1) if forceString(callInfo.settlement1) else u''
        street = u', улица: ' + forceString(callInfo.street1) if forceString(callInfo.street1) else u''
        house = u', дом: ' + forceString(callInfo.house1) if callInfo.house1 and forceInt(callInfo.house1) > 0 else u''
        houseFract = u', дробь: ' + forceString(callInfo.houseFract1) if callInfo.houseFract1 else u''
        corp = u', корпус: ' + forceString(callInfo.building1) if callInfo.building1 else u''
        flat = u', квартира: ' + forceString(callInfo.flat1) if callInfo.flat1 else u''
        porch = u', подъезд: ' + forceString(callInfo.porch1) if callInfo.porch1 and forceInt(callInfo.porch1) > 0 else u''
        floor = u', этаж: ' + forceString(callInfo.floor1) if callInfo.floor1 and forceInt(callInfo.floor1) > 0 else u''
        return settlement + street + house + houseFract + corp + flat + porch + floor

    def getAddrStrLive(self, callInfo):
        settlement = u'нас. пункт: ' + forceString(callInfo.settlement2) if forceString(callInfo.settlement2) else u''
        street = u', улица: ' + forceString(callInfo.street2) if forceString(callInfo.street2) else u''
        house = u', дом: ' + forceString(callInfo.house2) if callInfo.house2 and forceInt(callInfo.house2) > 0 else u''
        houseFract = u', дробь: ' + forceString(callInfo.houseFract2) if callInfo.houseFract2 else u''
        corp = u', корпус: ' + forceString(callInfo.building2) if callInfo.building2 else u''
        flat = u', квартира: ' + forceString(callInfo.flat2) if callInfo.flat2 else u''
        porch = u', подъезд: ' + forceString(callInfo.porch2) if callInfo.porch2 and forceInt(callInfo.porch2) > 0 else u''
        floor = u', этаж: ' + forceString(callInfo.floor2) if callInfo.floor2 and forceInt(callInfo.floor2) > 0 else u''
        return settlement + street + house + houseFract + corp + flat + porch + floor

    def getAddrStrProp(self, callInfo):
        settlement = u'нас. пункт: ' + forceString(callInfo.settlement3) if forceString(callInfo.settlement3) else u''
        street = u', улица: ' + forceString(callInfo.street3) if forceString(callInfo.street3) else u''
        house = u', дом: ' + forceString(callInfo.house3) if callInfo.house3 and forceInt(callInfo.house3) > 0 else u''
        houseFract = u', дробь: ' + forceString(callInfo.houseFract3) if callInfo.houseFract3 else u''
        corp = u', корпус: ' + forceString(callInfo.building3) if callInfo.building3 else u''
        flat = u', квартира: ' + forceString(callInfo.flat3) if callInfo.flat3 else u''
        porch = u', подъезд: ' + forceString(callInfo.porch3) if callInfo.porch3 and forceInt(callInfo.porch3) > 0 else u''
        floor = u', этаж: ' + forceString(callInfo.floor3) if callInfo.floor3 and forceInt(callInfo.floor3) > 0 else u''
        return settlement + street + house + houseFract + corp + flat + porch + floor

    def build(self, params):
        begDate = params.get('begDate')
        endDate = params.get('endDate')
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        items = self.exchange.getCallListStr(forceString(begDate), forceString(endDate))
        tableColumns = [('5%', [u'Номер вызова'], CReportBase.AlignLeft),
                        ('5%', [u'Дата вызова'], CReportBase.AlignLeft),
                        ('10%', [u'ФИО'], CReportBase.AlignLeft),
                        ('5%', [u'Пол'], CReportBase.AlignLeft),
                        ('5%', [u'Полных лет'], CReportBase.AlignLeft),
                        ('10%', [u'Телефон'], CReportBase.AlignLeft),
                        ('20%', [u'Диагноз'], CReportBase.AlignLeft),
                        ('15%', [u'Уточненный адрес'], CReportBase.AlignLeft),
                        ('15%', [u'Адрес проживания'], CReportBase.AlignLeft),
                        ('15%', [u'Адрес прописки'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)
        for record in items:
            i = table.addRow()
            table.setText(i, 0, forceString(record.number))
            table.setText(i, 1, forceString(record.callDate) + u' ' + forceString(record.endReceivingCall)[:8])
            table.setText(i, 2, forceString(record.lastName) + u' ' + forceString(record.name) + u' ' + forceString(record.patronymic))
            table.setText(i, 3, u'женский' if forceInt(record.sex) else u'мужской')
            table.setText(i, 4, forceString(record.ageYears) if record.ageYears and forceInt(record.ageYears) > 0 else u'')
            table.setText(i, 5, forceString(record.telephone))
            table.setText(i, 6, forceString(record.diseaseBasicCode) + u': ' + forceString(record.diseaseBasic))
            table.setText(i, 7, forceString(self.getAddrStrCall(record)))
            table.setText(i, 8, forceString(self.getAddrStrLive(record)))
            table.setText(i, 9, forceString(self.getAddrStrProp(record)))
        return doc

class CProtocol(QtGui.QDialog, Ui_Dialog):
    def __init__(self, begDate, endDate, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.begDate = begDate
        self.endDate = endDate

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(QtCore.QDate().fromString(self.begDate, 'dd.MM.yyyy'))
        self.edtEndDate.setDate(QtCore.QDate().fromString(self.endDate, 'dd.MM.yyyy'))


    def params(self):
        params = {}
        params['begDate']     = self.edtBegDate.date()
        params['endDate']     = self.edtEndDate.date()
        return params