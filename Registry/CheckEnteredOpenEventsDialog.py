# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.TableModel import CTableModel, CCol, CDateTimeFixedCol, CEnumCol, CRefBookCol, CTextCol
from library.Utils import forceRef

from Registry.Utils import getClientBanner

from Ui_CheckEnteredOpenEventsDialog import Ui_CheckEnteredOpenEventsDialog


class CICDCol(CCol):
    def __init__(self, title, fields, defaultWidth, alignment):
        CCol.__init__(self, title, fields, defaultWidth, alignment)
        self.valuesCache = {}

    def format(self, values):
        id = forceRef(values[0])
        val = self.valuesCache.get(id)
        if val:
            return val
        else:
            stmt = 'SELECT Diagnosis.`MKB` from Diagnostic INNER JOIN Diagnosis ON Diagnosis.`id`=Diagnostic.`diagnosis_id` WHERE Diagnosis.`id` = (SELECT MAX(diagnosis_id) FROM Diagnostic WHERE event_id=%d AND deleted=0) AND Diagnosis.`deleted`=0' % id
            query = QtGui.qApp.db.query(stmt)
            if query.first():
                val = query.value(0)
            else:
                val = QtCore.QVariant()
            self.valuesCache[id] = val
            return val


class CCheckEnteredOpenEvents(CDialogBase, Ui_CheckEnteredOpenEventsDialog):
    def __init__(self, parent, eventIdList=None, clientId=None):
        if not eventIdList:
            eventIdList = []
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.btnResult = 0
        self.resultEventId = None
        self.eventIdList = eventIdList
        self.clientId = clientId
        self.setup([
            CDateTimeFixedCol(u'Дата начала', ['setDate'], 10),
            CRefBookCol(u'Тип', ['eventType_id'], 'EventType', 40),
            CICDCol(u'МКБ', ['id'], 5, 'l'),
            CRefBookCol(u'Врач назначивший', ['setPerson_id'], 'vrbPersonWithSpeciality', 15),
            CRefBookCol(u'Врач выполнивший', ['execPerson_id'], 'vrbPersonWithSpeciality', 15),
            CEnumCol(u'Порядок', ['order'], [u'', u'плановый', u'экстренный', u'самотёком', u'принудительный'], 5),
            CTextCol(u'Примечания', ['note'], 6)
        ], 'Event', ['id'])
        self.setWindowTitleEx(u'Открытые события')

    def setup(self, cols, tableName, order):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.props = {}
        self.order = order
        self.model = CTableModel(self, cols, tableName)
        self.model.setIdList(self.eventIdList)
        self.tblOpenEvents.setModel(self.model)
        if self.eventIdList:
            self.tblOpenEvents.selectRow(0)
        if self.clientId:
            self.txtClientInfoEventsBrowser.setHtml(getClientBanner(self.clientId))
        else:
            self.txtClientInfoEventsBrowser.setText('')
        QtCore.QObject.connect(self.tblOpenEvents.horizontalHeader(), QtCore.SIGNAL('sectionClicked(int)'),
                               self.setSort)

    def currentItemId(self):
        return self.tblOpenEvents.currentItemId()

    def select(self):
        table = self.model.table()
        return QtGui.qApp.db.getIdList(table.name(), 'id', table['id'].inlist(self.eventIdList), self.order)

    def renewListAndSetTo(self, itemId=None):
        idList = self.select(self.props)
        self.tblOpenEvents.setIdList(idList, itemId)

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.resultEventId = None
        self.btnResult = 0
        self.close()

    @QtCore.pyqtSlot()
    def on_btnOpen_clicked(self):
        event_id = self.currentItemId()
        self.resultEventId = event_id if event_id else None
        self.btnResult = 2
        self.close()

    @QtCore.pyqtSlot()
    def on_btnReverse_clicked(self):
        self.resultEventId = None
        self.btnResult = 1
        self.close()

    @QtCore.pyqtSlot()
    def on_btnCreate_clicked(self):
        self.resultEventId = None
        self.btnResult = 3
        self.close()

    def setSort(self, col):
        name = self.model.cols()[col].fields()[0]
        self.order = name
        header = self.tblOpenEvents.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.setSortIndicator(col, QtCore.Qt.AscendingOrder)
        self.renewListAndSetTo(self.currentItemId())
