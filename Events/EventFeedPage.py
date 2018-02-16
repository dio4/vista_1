# -*- coding: utf-8 -*-


from PyQt4 import QtCore, QtGui

from Events.EventFeedModel import CFeedModel, CEventFeedMealListDialog
from RefBooks.RBMenu import CGetRBMenu
from Registry.Utils import getClientString
from Reports.ReportView import CReportViewDialog
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceString, toVariant
from library.DialogBase import CConstructHelperMixin, CDialogBase
from Ui_EventFeedPage import Ui_EventFeedPage


class CFastEventFeedPage(QtGui.QWidget, CConstructHelperMixin, Ui_EventFeedPage):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.clientId = None

    def setupUiMini(self, Dialog):
        pass

    def preSetupUiMini(self):
        pass

    def preSetupUi(self):
        pass

    def postSetupUiMini(self):
        self.addModels('Feed', CFeedModel(self))
        self.tblFeed.setModel(self.modelFeed)

    def postSetupUi(self):
        self.tblFeed.addMoveRow()
        self.tblFeed.addPopupDuplicateCurrentRow()
        self.tblFeed.addPopupDuplicateSelectRows()
        self.tblFeed.addPopupSelectAllRow()
        self.tblFeed.addPopupClearSelectionRow()
        self.tblFeed.addPopupDelRow()

    def setClientId(self, clientId):
        self.clientId = clientId

    def prepare(self):
        self.load(None)

    def load(self, eventId):
        self.modelFeed.loadHeader()
        self.tblFeed.setItemDelegateForColumn(0, self.tblFeed.dateEditItemDelegate)
        self.tblFeed.setItemDelegateForColumn(1, self.tblFeed.dietItemDelegate)
        self.tblFeed.setItemDelegateForColumn(2, self.tblFeed.dietItemDelegate)
        self.modelFeed.loadData(eventId)

    def save(self, eventId):
        self.modelFeed.saveData(eventId)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblFeed_doubleClicked(self, index):
        column = index.column()
        model = index.model()
        if column >= 3 and model.cellIsEditable(index):
            dialog = CEventFeedMealListDialog(self)
            data = model.data(index, QtCore.Qt.EditRole)
            dialog.setValue(data)
            dialog.exec_()
            if dialog.result() == QtGui.QDialog.Accepted:
                model.setData(index, toVariant(dialog.value()))

    @QtCore.pyqtSlot()
    def on_btnGetMenu_clicked(self):
        dialog = CGetRBMenu(self)
        id = dialog.exec_()
        if id:
            begDate = dialog.edtBegDate.date()
            endDate = dialog.edtEndDate.date()
            if begDate and endDate and begDate <= endDate:
                self.modelFeed.insertFromMenu(id, begDate, endDate, dialog.chkUpdate.isChecked())

    @QtCore.pyqtSlot()
    def on_btnFeedPrint_clicked(self):
        model = self.modelFeed
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Питание\n')
        cursor.insertBlock()
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertHtml(u'Пациент: %s' % (getClientString(self.clientId)))
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cursor.insertText(u'Отчёт составлен: ' + forceString(QtCore.QDateTime.currentDateTime()))
        cursor.insertBlock()
        colWidths = [self.tblFeed.columnWidth(i) for i in xrange(model.columnCount() - 1)]
        colWidths.insert(0, 10)
        totalWidth = sum(colWidths)
        tableColumns = []
        iColNumber = False
        for iCol, colWidth in enumerate(colWidths):
            widthInPercents = str(max(1, colWidth * 90 / totalWidth)) + '%'
            if not iColNumber:
                tableColumns.append((widthInPercents, [u'№'], CReportBase.AlignRight))
                iColNumber = True
            headers = model.headers
            tableColumns.append((widthInPercents, [forceString(headers[iCol][1])], CReportBase.AlignLeft))
        table = createTable(cursor, tableColumns)
        for iModelRow in xrange(model.rowCount() - 1):
            iTableRow = table.addRow()
            table.setText(iTableRow, 0, iModelRow + 1)
            for iModelCol in xrange(model.columnCount()):
                index = model.createIndex(iModelRow, iModelCol)
                text = forceString(model.data(index))
                table.setText(iTableRow, iModelCol + 1, text)
        html = doc.toHtml(QtCore.QByteArray('utf-8'))
        view = CReportViewDialog(self)
        view.setText(html)
        view.exec_()


class CEventFeedPage(CFastEventFeedPage):
    def __init__(self, parent=None):
        CFastEventFeedPage.__init__(self, parent)
        self.preSetupUiMini()
        self.preSetupUi()
        self.setupUiMini(self)
        self.setupUi(self)
        self.postSetupUiMini()
        self.postSetupUi()


class CFeedPageDialog(CDialogBase):
    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)

        self.eventId = None

        self.setupUi()

        self.setupDirtyCather()

        self.setWindowTitle(u'Питание')

    def setupUi(self):
        self.vLayout = QtGui.QVBoxLayout(self)
        self.feedWidget = CEventFeedPage(self)
        self.vLayout.addWidget(self.feedWidget)
        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok,
                                                QtCore.Qt.Horizontal, self)
        self.vLayout.addWidget(self.buttonBox)

        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL('rejected()'), self.reject)

    def loadData(self, eventId):
        self.eventId = eventId
        self.feedWidget.load(eventId)

    def saveData(self):
        self.feedWidget.save(self.eventId)
        return True

    def setClientId(self, clientId):
        self.feedWidget.setClientId(clientId)
