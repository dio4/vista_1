# -*- coding: utf-8 -*-
u"""
Модуль для выгрузки ИЭМКа в шину Нетрики
"""
import logging
from PyQt4 import QtCore, QtGui

import library.LoggingModule.Logger
from Events.CreateEvent import editEvent
from Registry.ClientEditDialog import CClientEditDialog
from Ui_ExportIEMK import Ui_ExportIEMKDialog
from library.DialogBase import CDialogBase
from library.EMK import EmkService
from library.EMK.Utils import LogStatus
from library.InDocTable import CInDocTableCol, CRecordListModel
from library.Utils import forceRef, forceString, toVariant


class CIEMKErrorLogModel(CRecordListModel):
    def __init__(self, parent):
        CRecordListModel.__init__(self, parent, cols=[
            CInDocTableCol(u'client_id', 'client_id', 10, valueType=QtCore.QVariant.Int, readOnly=True),
            CInDocTableCol(u'event_id', 'event_id', 10, valueType=QtCore.QVariant.Int, readOnly=True),
            CInDocTableCol(u'Текст ошибки', 'error_stmt', 20, valueType=QtCore.QVariant.String, readOnly=True)
        ])

    def addItem(self, clientId=None, eventId=None, errorStmt=u''):
        record = self.getEmptyRecord()
        record.setValue('client_id', toVariant(clientId))
        record.setValue('event_id', toVariant(eventId))
        record.setValue('error_stmt', toVariant(errorStmt))
        self.addRecord(record)


class CExportIEMK(CDialogBase, Ui_ExportIEMKDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)

        self.addModels('ErrorLog', CIEMKErrorLogModel(self))

        self.setupUi(self)

        self.setModels(self.tblErrorLog, self.modelErrorLog, self.selectionModelErrorLog)
        self.tblErrorLog.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblErrorLog.doubleClicked.connect(self.openEditor)
        self.tblErrorLog.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        self.edtCountClosed.setPlaceholderText(u'Закрытые, готовые к отправке случаи')
        self.edtCountOpened.setPlaceholderText(u'Не закрытые(isClosed) случаи')
        self.edtCountFailed.setPlaceholderText(u'Отправленные с ошибкой случаи')

        self.setConnections()
        self.cmbEventType.setTable(tableName='EventType')
        EmkService.loggingConfigure(logToFile=False,
                                    textBrowser=self.txtLog,
                                    textBrowserDetailed=self.txtDetailedLog,
                                    tblError=self.tblErrorLog,
                                    handlerClass=TextBrowserExportHandler)

        self._IEMKService = None
        u""":type : EmkService.Service | None"""

    def openEditor(self):
        row = self.tblErrorLog.currentIndex().row()
        record = self.tblErrorLog.model().getRecordByRow(row)
        eventId = forceRef(record.value('event_id')) if record is not None else None
        clientId = forceRef(record.value('client_id')) if record is not None else None

        if eventId is not None:
            editEvent(self, eventId)
        elif clientId is not None:
            dlg = CClientEditDialog(self)
            dlg.load(clientId)
            dlg.exec_()

    def setConnections(self):
        self.btnToggleFilters.toggled.connect(lambda state: self.btnToggleFilters.setText(u'v' if state else u'^'))
        self.btnStart.clicked.connect(self.start)
        self.edtBegDate.editTextChanged.connect(self.reCount)
        self.edtEndDate.editTextChanged.connect(self.reCount)
        self.cmbEventType.currentIndexChanged.connect(self.reCount)
        self.cmbOrgStrucutre.currentIndexChanged.connect(self.reCount)

    def reCount(self):
        db = QtGui.qApp.db
        tblEvent = db.table('Event')
        tblPerson = db.table('Person')
        tblIEMKLog = db.table(library.LoggingModule.Logger.loggerDbName + '.IEMKEventLog')
        orgStructureId = self.cmbOrgStrucutre.value()
        eventTypeId = self.cmbEventType.value()
        tbl = tblEvent.innerJoin(tblPerson, tblEvent['execPerson_id'].eq(tblPerson['id']))
        tbl = tbl.leftJoin(
            tblIEMKLog,
            u'''{logger}.IEMKEventLog.id = (SELECT MAX(id) FROM {logger}.IEMKEventLog WHERE {logger}.IEMKEventLog.event_id = Event.id)'''.format(
                logger=library.LoggingModule.Logger.loggerDbName)
        )
        where = [
            tblEvent['deleted'].eq(0),
            tblEvent['execDate'].between(self.edtBegDate.date(), self.edtEndDate.date())
        ]
        if orgStructureId:
            orgStructureIds = db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
            where.append(tblPerson['orgStructure_id'].inlist(orgStructureIds))
        if eventTypeId:
            where.append(tblEvent['eventType_id'].eq(eventTypeId))

        countClosed = db.getCount(table=tbl, where=where+[db.joinOr([tblIEMKLog['status'].isNull(),
                                                                     tblIEMKLog['status'].eq(LogStatus.NotSent)]),
                                                          tblEvent['isClosed'].eq(1)])
        countOpened = db.getCount(table=tbl, where=where+[tblEvent['isClosed'].eq(0)])
        countFailed = db.getCount(table=tbl, where=where+[tblIEMKLog['status'].eq(LogStatus.Failed),
                                                          tblEvent['isClosed'].eq(1)])
        self.edtCountClosed.setText(str(countClosed))
        self.edtCountOpened.setText(str(countOpened))
        self.edtCountFailed.setText(str(countFailed))

    def start(self):
        if self._IEMKService is None:
            self.init()

        self.txtLog.clear()
        self.txtDetailedLog.clear()
        self.tblErrorLog.model().clearItems()
        self.btnStart.setEnabled(False)

        try:
            self._IEMKService.sendEvents(startDate=self.edtBegDate.date(),
                                         endDate=self.edtEndDate.date(),
                                         maxCount=int(self.edtMaxCount.text()) if self.edtMaxCount.text() else 500,
                                         resend=self.chkResend.isChecked(),
                                         newEpicrisis=self.chkEpicrisis.isChecked(),
                                         orgStructureId=self.cmbOrgStrucutre.value(),
                                         eventTypeId=self.cmbEventType.value())
        except:
            QtGui.QMessageBox.warning(self, u'Ошибка', u'\n Произошла ошибка. Смотрите error.log')
            raise
        finally:
            self.btnStart.setEnabled(True)

    def init(self):
        prefs = QtGui.qApp.preferences.appPrefs
        self._IEMKService = QtGui.qApp.callWithWaitCursor(self, EmkService.Service,
                                                          EMK_WSDL_URL=forceString(prefs.get('edtCaseURL', '')),
                                                          PIX_WSDL_URL=forceString(prefs.get('edtPixURL', '')),
                                                          GUID=forceString(prefs.get('edtGUID', '')))


class TextBrowserExportHandler(logging.Handler):
    def __init__(self, textBrowser, textBrowserDetailed):
        u"""
        :param textBrowser:
        :type textBrowser: PyQt4.QtGui.QTextBrowser.QTextBrowser
        """
        logging.Handler.__init__(self)
        self.textBrowser = textBrowser
        self.textBrowserDetailed = textBrowserDetailed

    def emit(self, record):
        self.textBrowserDetailed.insertPlainText(self.format(record=record).decode('utf-8'))
        if record.funcName == 'sendEvent' or record.funcName == 'sendEvents':
            self.textBrowser.insertPlainText(self.format(record=record).decode('utf-8'))
