# -*- coding: utf-8 -*-

from PyQt4 import QtCore

from Events.EditDispatcher      import getEventFormClass
from library.DialogBase         import CDialogBase
from library.TableModel         import CTableModel, CDateCol, CRefBookCol
from Ui_EventsListDialog import  Ui_eventsListDialog


class CEventsListDialog(CDialogBase, Ui_eventsListDialog):
    def __init__(self, parent, eventIdList):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        cols = [
                CDateCol(u'Назначен', ['setDate'],  10),
                CDateCol(u'Выполнен', ['execDate'], 10),
                CRefBookCol(u'Тип', ['eventType_id'], 'EventType', 40),
                CRefBookCol(u'Врач', ['execPerson_id'], 'vrbPersonWithSpeciality', 15),
                CRefBookCol(u'Результат', ['result_id'], 'rbResult', 40),
               ]

        self.setup(cols, 'Event', ['id'], eventIdList, parent.recSelectClient, parent.recSelectCorrect)
        self.setWindowTitleEx(u'Логический контроль - события')


    def setup(self, cols, tableName, order, eventIdList, recSelectClient = u'', recSelectCorrect = u''):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.booleanRowEnabled = False
        self.booleanCloseCorrect = False
        self.props = {}
        self.order = order
        self.model = CTableModel(self, cols, tableName)
        self.model.setIdList(eventIdList)
        self.tblListWidget.setModel(self.model)
        if eventIdList:
            self.tblListWidget.selectRow(0)

        self.tblListWidget.setFocus(QtCore.Qt.OtherFocusReason)
        self.lblClientInfo.setText(recSelectClient)
        self.lblSelectInfo.setText(recSelectCorrect)

        QtCore.QObject.connect(self.tblListWidget.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'), self.setSort)


    def setCurrentItemId(self, itemId):
        self.tblListWidget.setCurrentItemId(itemId)


    def currentItemId(self):
        return self.tblListWidget.currentItemId()


    def renewListAndSetTo(self, itemId=None):
        idList = self.select(self.props)
        self.tblListWidget.setIdList(idList, itemId)
        self.lblClientInfo.setText(u'всего: %d' % len(idList))
        self.lblSelectInfo.setText(u'всего: %d' % len(idList))


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblListWidget_doubleClicked(self, index):
        self.booleanRowEnabled = False
        event_id = self.currentItemId()
        if event_id:
            self.booleanRowEnabled = self.editEvent(event_id)


    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.close()


    @QtCore.pyqtSlot()
    def on_btnCloseCorrect_clicked(self):
        self.booleanCloseCorrect = True
        self.close()


#    def getReportHeader(self):
#        return self.objectName()
#
#
#    def contentToHTML(self):
#        reportHeader = self.getReportHeader()
#        self.tblListWidget.setReportHeader(reportHeader)
#        reportDescription = u''
#        self.tblListWidget.setReportDescription(reportDescription)
#        return self.tblListWidget.contentToHTML()


    def setSort(self, col):
        name = self.model.cols()[col].fields()[0]
        self.order = name
        header=self.tblListWidget.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.setSortIndicator(col, QtCore.Qt.AscendingOrder)
        self.renewListAndSetTo(self.currentItemId())


    def editEvent(self, eventId):
        formClass = getEventFormClass(eventId)
        dialog = formClass(self)
        dialog.load(eventId)
        return dialog.exec_()
