# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013-2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui
import DestinationsModels
from Events.DestinationInfo import CDestinationInfo
from library.DialogBase                     import CConstructHelperMixin
from library.PrintInfo import CInfoContext
from library.PrintTemplates import customizePrintButton, applyTemplate
from library.Utils                          import forceInt, forceString, toVariant, forceDate, smartDict
from DestinationsModels                     import dsNew, dsCreated, dsSet, dsCancelled
from AddDestinationDialog                   import CAddDestinationSetupDialog
from AddDosesDialog                         import CAddDosesSetupDialog
from AddCommentDialog                       import CAddCommentSetupDialog
from Ui_DestinationsPage                    import Ui_DestinationsPageWidget


class CFastDestinationsPage(QtGui.QWidget, CConstructHelperMixin, Ui_DestinationsPageWidget):
    def __init__(self, eventId=0, clientId=0, personId=0, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.curComplexNumber = -1
        self.eventId = eventId
        self.clientId = clientId
        self.personId = personId
        self.localIndex = -1
        self.destFilter = smartDict()

    def setEventId(self, eventId, clientId, personId):
        self.eventId = eventId
        self.clientId = clientId
        self.personId = personId
        self.applyDestinationsFilter()

    def setupUiMini(self, Dialog):
        pass


    def preSetupUiMini(self):
        pass


    def preSetupUi(self):
        pass


    def postSetupUiMini(self):
        self.addModels('Destinations', DestinationsModels.CDestinationsModel(self))
        self.tblDestinations.setModel(self.modelDestinations)


    def postSetupUi(self):
        self.tblDestinations.setAlternatingRowColors(False)
        self.grpDestFilter.setVisible(False)
        self.btnDestCancel.setVisible(False)
        self.btnDestDelete.setVisible(False)
        self.btnDestSet.setVisible(False)
        self.btnDestAddToComplex.setVisible(False)
        self.btnDestSave.setVisible(False)
        self.btnDestFind.setVisible(True)
        self.btnDestPrint.setVisible(True)
        self.btnDestAll.setVisible(True)
        self.resetDestinationsFilter()
        customizePrintButton(self.btnDestPrint, 'destination_list')

        self.tblDestinations.setSelectionModel(self.selectionModelDestinations)
        self.tblDestinations.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblDestinations.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tblDestinations.setWordWrap(True)
        self.tblDestinations.setItemDelegate(DestinationsModels.CDestinationsItemDelegate())

    def setData(self, eventId, personId):
        self.eventId = eventId
        self.personId = personId
        self.applyDestinationsFilter()

    @QtCore.pyqtSlot()
    def on_btnDestAdd_clicked(self):
        setupDialog = CAddDestinationSetupDialog()
        if setupDialog.exec_():
            drugFormularyItemIdList, rlsTradeNameCodesList = setupDialog.getDrugFormularyItemIdList()
            self.tblDestinations.model().addItems(drugFormularyItemIdList, rlsTradeNameCodesList)
            self.buttonLayoutInvisible()
            self.applyDestinationsFilter()


    @QtCore.pyqtSlot()
    def on_btnDestAddToComplex_clicked(self):
        selectedItems = self.getSelectedItems()
        if len(self.tblDestinations.model()._items) > 0:
            index = self.tblDestinations.currentIndex()
            curRow = index.row()
            unitId = forceInt(self.tblDestinations.model()._items[curRow].value('drugMeasureUnit_id'))
            filter = 'AND rbMedicines.unit_id = %d' % unitId
            setupDialog = CAddDestinationSetupDialog(filter= filter)
            if setupDialog.exec_():
                drugFormularyItemIdList, rlsCodeList = setupDialog.getDrugFormularyItemIdList()
                self.tblDestinations.model()._items[curRow].setValue('actionParentId', toVariant(self.curComplexNumber))
                self.tblDestinations.model().addItems(drugFormularyItemIdList, rlsCodeList, self.curComplexNumber)

                self.buttonLayoutInvisible()
                self.applyDestinationsFilter()
                self.setSelectedItems(selectedItems)
                self.curComplexNumber -= 1

    @QtCore.pyqtSlot()
    def on_btnDestSave_clicked(self):
        selectedItems = self.getSelectedItems()
        saveItems = self.buildItems(u'сохранить')
        if len(saveItems) > 0:
            items = self.tblDestinations.model().getItems()
            setItems = []
            for item in saveItems:
                setItems.append(items[item])
            if self.saveDestinationsList(saveItems, setItems):
                self.buttonLayoutInvisible()
                self.applyDestinationsFilter()
                self.setSelectedItems(selectedItems)

    @QtCore.pyqtSlot()
    def on_btnDestSet_clicked(self):
        selectedItems = self.getSelectedItems()
        setItems = self.buildItems(u'назначить')
        if len(setItems) > 0:
            items = self.tblDestinations.model().getItems()
            for item in setItems:
                takeId = items[item].value('actionId')
                self.tblDestinations.model().setStatus(takeId, dsSet)
                self.buttonLayoutInvisible()
            self.applyDestinationsFilter()
            self.setSelectedItems(selectedItems)

    @QtCore.pyqtSlot()
    def on_btnDestDelete_clicked(self):
        delItems = self.buildItems(u'удалить')
        if len(delItems) > 0:
            self.tblDestinations.model().deleteItems(delItems)
            self.buttonLayoutInvisible()
            self.applyDestinationsFilter()

    @QtCore.pyqtSlot()
    def on_btnDestCancel_clicked(self):
        selectedItems = self.getSelectedItems()
        cancelItems = self.buildItems(u'отменить назначение')
        if len(cancelItems) > 0:
            items = self.tblDestinations.model().getItems()
            for item in cancelItems:
                takeId = forceInt(items[item].value('actionId'))
                self.tblDestinations.model().setStatus(takeId, dsCancelled)
                self.buttonLayoutInvisible()
            self.applyDestinationsFilter()
            self.setSelectedItems(selectedItems)

    @QtCore.pyqtSlot()
    def on_btnDestFind_clicked(self):
        self.grpDestFilter.setVisible(not self.grpDestFilter.isVisible())


    def getDestinationInfo(self, context, infoClass = CDestinationInfo):
        result = context.getInstance(infoClass, self.eventId, self.destFilter.dateBegin, self.destFilter.dateEnd)
        return result


    @QtCore.pyqtSlot(int)
    def on_btnDestPrint_printByTemplate(self, templateId):
        context = CInfoContext()
        destinationInfo = self.getDestinationInfo(context)

        orgStructureId = forceInt(QtGui.qApp.db.translate('Person', 'id', self.personId, 'orgStructure_id'))

        data = {
            'departmentNumber' : forceString(QtGui.qApp.db.translate('OrgStructure', 'id', orgStructureId, 'code')),
            'destinationInfo' : destinationInfo
        }

        QtGui.qApp.call(self, applyTemplate, (self, templateId, data))

    @QtCore.pyqtSlot()
    def on_btnDestAll_clicked(self):
        eventBegDateRecord = QtGui.qApp.db.getRecordEx('Event',
                                                       'createDatetime',
                                                       'Event.deleted = 0 AND Event.id = %s' % self.eventId)
        if eventBegDateRecord:
            eventBegDate = forceDate(eventBegDateRecord.value('createDatetime'))
            self.edtDestFilterBegDate.setDate(eventBegDate)
            self.edtDestFilterEndDate.setDate(QtCore.QDate().currentDate())
            self.edtDestFilterDrug.setText('')
            self.cmbDestFilterStatus.setCurrentIndex(0)
            self.applyDestinationsFilter()

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_bbxDestFilter_clicked(self, button):
        buttonCode = self.bbxDestFilter.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Apply:
            self.applyDestinationsFilter()
        elif buttonCode == QtGui.QDialogButtonBox.Reset:
            self.resetDestinationsFilter()
            self.applyDestinationsFilter()

    @QtCore.pyqtSlot(QtGui.QItemSelection, QtGui.QItemSelection)
    def on_selectionModelDestinations_selectionChanged(self, selected, deselected):
        if selected.indexes():
            status = self.tblDestinations.model().getStatus(selected.indexes()[0].row())
            if status in (None, dsNew):
                self.btnDestSave.setVisible(True)
                self.btnDestAddToComplex.setVisible(True)
                self.btnDestSet.setVisible(False)
                self.btnDestCancel.setVisible(False)
                self.btnDestDelete.setVisible(True)
            elif status == dsCreated:
                self.btnDestSave.setVisible(False)
                self.btnDestAddToComplex.setVisible(True)
                self.btnDestSet.setVisible(True)
                self.btnDestCancel.setVisible(False)
                self.btnDestDelete.setVisible(True)
            elif status == dsSet:
                self.btnDestSave.setVisible(False)
                self.btnDestAddToComplex.setVisible(False)
                self.btnDestSet.setVisible(False)
                self.btnDestCancel.setVisible(True)
            else:
                self.btnDestSave.setVisible(False)
                self.btnDestAddToComplex.setVisible(False)
                self.btnDestDelete.setVisible(False)
                self.btnDestSet.setVisible(False)
                self.btnDestCancel.setVisible(False)
        else:
            self.buttonLayoutInvisible()



    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblDestinations_clicked(self, index):
        curRow = index.row()
        if index.column() in (3, 4, 5, 6, 7) and forceInt(self.tblDestinations.model()._items[curRow].value('drugStatus')) < dsSet:
            setupDialog = CAddDosesSetupDialog()
            unit, timeList, doseItems, route, interval, beginDate, endDate, comments = self.tblDestinations.model().getDataToDosesSetupDialog(curRow)
            setupDialog.setData(unit, timeList, doseItems, route, interval, beginDate, endDate, comments)
            if setupDialog.exec_():
                doseItems, injectionPath, interval, begDate, endDate = setupDialog.getData()
                doses = doseItems.doses()
                hours = doseItems.times()
                comments = doseItems.comments()
                self.tblDestinations.model().setDataToDosesSetupDialog(doses, hours, injectionPath, interval, begDate, endDate, curRow, comments)
                if forceInt(self.tblDestinations.model()._items[curRow].value('drugStatus')) == dsCreated:
                    self.tblDestinations.model().setItem(self.tblDestinations.model()._items[curRow],
                                                         self.personId,
                                                         forceInt(self.tblDestinations.model()._items[curRow].value('actionParentId')))
                self.applyDestinationsFilter()
        elif index.column() == 8:
            setupDialog = CAddCommentSetupDialog(forceString(self.tblDestinations.model()._items[curRow].value('drugComment')),
                                                 forceInt(self.tblDestinations.model()._items[curRow].value('rlsCode')))
            if setupDialog.exec_():
                comment, rlsCode = setupDialog.getData()
                self.tblDestinations.model()._items[curRow].setValue('drugComment', toVariant(comment))
                self.tblDestinations.model()._items[curRow].setValue('rlsCode', toVariant(rlsCode))
                self.applyDestinationsFilter()
        self.tblDestinations.viewport().update()        # Вряд ли оно должно быть именно здесь. Суть в том, что для переопределенного поведения при выделении строк, само выделение отрисовывалось криво и не сразу. Поэтому так.

    def drawSpan(self, spanList):
        self.tblDestinations.clearSpans()
        if len(spanList) > 0:
            for item in spanList:
                self.tblDestinations.setSpan(item[0], item[1], item[2], item[3])

    def resetDestinationsFilter(self):
        today = QtCore.QDate().currentDate()
        beginDate = QtCore.QDate(today.year(), today.month(), 1)
        self.edtDestFilterBegDate.setDate(beginDate)
        self.edtDestFilterEndDate.setDate(beginDate.addMonths(1 if today.day() < 15 else 2))
        self.edtDestFilterDrug.setText('')
        self.cmbDestFilterStatus.setCurrentIndex(0)

    def applyDestinationsFilter(self):
        filter = self.destFilter
        filter.dateBegin = self.edtDestFilterBegDate.date()
        filter.dateEnd = self.edtDestFilterEndDate.date()
        filter.patient = None
        filter.drug = self.edtDestFilterDrug.text()
        filter.status = self.cmbDestFilterStatus.currentIndex()

        self.updateDestinationsList(filter.dateBegin,  filter.dateEnd)

    def updateDestinationsList(self, begDate, endDate):
        self.tblDestinations.model().updateDestinationsList(self.eventId, True, begDate, endDate)
        spanList = self.tblDestinations.model().getComplexSpan()
        self.drawSpan(spanList)
        self.tblDestinations.resizeRowsToContents()

    def getSelectedItems(self):
        indexesList = self.tblDestinations.selectedIndexes()
        itemsList = []
        curRow = -1
        for index in indexesList:
            if curRow != index.row():
                curRow = index.row()
                itemsList.append(self.tblDestinations.model()._items[curRow])
        return itemsList

    def setSelectedItems(self, itemsList):
        for item in itemsList:
            i = 0
            while i < len(self.tblDestinations.model()._items):
                if item.value('drugItem_id') == self.tblDestinations.model()._items[i].value('drugItem_id')\
                        and item.value('drugDose') == self.tblDestinations.model()._items[i].value('drugDose')\
                        and item.value('drugMeasureUnit_id') == self.tblDestinations.model()._items[i].value('drugMeasureUnit_id')\
                        and item.value('drugRouteId') == self.tblDestinations.model()._items[i].value('drugRouteId')\
                        and item.value('interval') == self.tblDestinations.model()._items[i].value('interval')\
                        and item.value('takeDateBegin') == self.tblDestinations.model()._items[i].value('takeDateBegin')\
                        and item.value('takeDateEnd') == self.tblDestinations.model()._items[i].value('takeDateEnd'):
                    index = self.tblDestinations.model().index(i, 0)
                    self.tblDestinations.selectionModel().setCurrentIndex(index, QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows)
                    break
                i += 1

    def saveDestinationsList(self, saveItems, setItems):
        isSave = True
        i = saveItems[0]
        for item in setItems:
            if not forceInt(item.value('drugRouteId')) or not forceString(item.value('takeTime')) or not forceDate(item.value('takeDateBegin')) or not forceDate(item.value('takeDateEnd')):
                title = ''
                if not forceInt(item.value('drugRouteId')):
                    title = u'Не указан путь введения'
                elif not forceString(item.value('takeTime')):
                    title =  u'Не указано время приёма'
                elif not forceDate(item.value('takeDateBegin')):
                    title = u'Не указана дата начала'
                elif not forceDate(item.value('takeDateEnd')):
                    title = u'Не указана дата окончания'
                QtGui.QMessageBox.warning(self,
                                          u'Внимание!',
                                          title,
                                          QtGui.QMessageBox.Close)
                isSave = False
                break
            i += 1

        if isSave:
            inComplexItems = [[]]
            for span in self.tblDestinations.model().getComplexSpan():
                buffer = []
                deleteBuffer = []
                for row in range(len(saveItems)):
                    if saveItems[row] >= span[0] and saveItems[row] <= span[0] + span[2] - 1:
                        buffer.append(setItems[row])
                        deleteBuffer.append(saveItems[row])
                for j in deleteBuffer:
                    saveItems.remove(j)
                if len(buffer) > 1:
                    inComplexItems.append(buffer)
                    for item in buffer:
                        setItems.remove(item)
            return self.tblDestinations.model().saveData(self.eventId, self.personId, setItems, inComplexItems)
        else:
            index = self.tblDestinations.model().index(i, 3)
            self.on_tblDestinations_clicked(index)
            return False

    def buttonLayoutInvisible(self):
        self.btnDestCancel.setVisible(False)
        self.btnDestDelete.setVisible(False)
        self.btnDestSet.setVisible(False)
        self.btnDestAddToComplex.setVisible(False)
        self.btnDestSave.setVisible(False)

    def buildItems(self, title):
        isComplex = False
        complex = []
        notComplex = []
        items = []
        indexesList = self.tblDestinations.selectedIndexes()
        for index in indexesList:
            curRow = index.row()
            if curRow not in notComplex:
                notComplex.append(curRow)
            if curRow not in complex:
                for span in self.tblDestinations.model().getComplexSpan():
                    if curRow >= span[0] and curRow <= span[0] + span[2] - 1:
                        isComplex = True
                        complex.extend(range(span[0], span[0] + span[2]))
                        break
        if isComplex and QtGui.QMessageBox.question(self,
                                                    u'Внимание!',
                                                    u'Вы действительно хотите %s весь комлпекс?' % title,
                                                    QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            items = complex
        elif not isComplex:
            if QtGui.QMessageBox.question(self,
                                        u'Внимание!',
                                        u'Вы действительно хотите %s назначение?' % title,
                                        QtGui.QMessageBox.Yes|QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                items = notComplex
        return items


    def canClose(self):
        if self.tblDestinations.model().isUnsavedItems():
            QtGui.QMessageBox.information(self, u'Внимание!', u'Имеются несохранённые назначения!', QtGui.QMessageBox.Ok)
            return False
        return True

    def checkDataEntered(self):
        return self.canClose()


class CDestinationsPage(CFastDestinationsPage):
    def __init__(self, eventId=0, personId=0, parent=None):
        CFastDestinationsPage.__init__(self, eventId, personId, parent)
        self.preSetupUiMini()
        self.preSetupUi()
        self.setupUiMini(self)
        self.setupUi(self)
        self.postSetupUiMini()
        self.postSetupUi()
