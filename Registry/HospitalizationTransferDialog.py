# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Events.Action import CAction
from Events.EventInfo import CEventHospTransferInfo, CEventInfo
from Registry.Ui_HospitalizationTransfer import Ui_HospitalizationTransferDialog
from library.LoggingModule.Logger import getLoggerDbName
from library.PrintInfo import CInfoContext
from library.PrintTemplates import applyTemplate, getFirstPrintTemplate
from library.Utils import forceDate, forceString
from library.interchange import getDateEditValue

LOG_TRANSFER_TABLE = u"%s.EventHospTransfer" % getLoggerDbName()

LOG_TRANSFER_STMT = u"""
INSERT INTO {table} (
    `dateFrom`, 
    `dateTo`,       
    `person_id`,        
    `event_id`,     
    `comment`,
    `diagnosis`,
    `treatmentMethod`,
    `recommendedTreatment`,
    `treatmentOrgStructure`
) 
VALUES (
    \'{dateFrom}\',    
    \'{dateTo}\',     
    {personId},    
    {eventId},     
    \'{comment}\',
    \'{diagnosis}\',
    \'{treatmentMethod}\',
    \'{recommendedTreatment}\',
    \'{treatmentOrgStructure}\'
)
"""


def setLineEditValue(lineEdit, value):
    lineEdit.setText(forceString(value))
    lineEdit.setCursorPosition(0)


def setTextEditValue(textEdit, value):
    textEdit.setPlainText(forceString(value))


def getPlanningAction(eventId):
    db = QtGui.qApp.db

    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')

    table = tableAction
    table = table.innerJoin(tableActionType, [
        tableActionType['id'].eq(tableAction['actionType_id']),
        tableActionType['deleted'].eq(0),
        tableActionType['flatCode'].eq('planning')
    ])

    return db.getRecordEx(table, cols=['Action.*'], where=[tableAction['event_id'].eq(eventId)])


def getValue(record):
    if record:
        return forceString(record.value('value'))
    return u''


def printHospitalTransferTemplate(widget, eventId):
    context = CInfoContext()

    eventInfo = context.getInstance(CEventInfo, eventId)
    clientInfo = eventInfo.client
    actionsInfo = eventInfo.actions
    hospitalTransferInfo = context.getInstance(CEventHospTransferInfo, eventId)
    data = {
        'event': eventInfo,
        'client': clientInfo,
        'actions': actionsInfo,
        'hospitalTransfer': hospitalTransferInfo
    }
    applyTemplate(widget, getFirstPrintTemplate('hospitalTransfer')[1], data)


class CHospitalizationTransferDialog(QtGui.QDialog, Ui_HospitalizationTransferDialog):
    def __init__(self, parent, eventId):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        assert eventId is not None

        self.dateFrom = None
        self.personId = QtGui.qApp.userId
        self.eventId = eventId

        self.planningAction = getPlanningAction(eventId)
        self.consultationAction = CAction.getAction(eventId, '1-3')

        self.edtTransferDate.setDate(QtCore.QDate.currentDate())
        self.dateFrom = forceDate(self.planningAction.value('directionDate'))

        setLineEditValue(self.edtDiagnosis, self.consultationAction.getProperty(u'Диагноз').getValue())
        setTextEditValue(self.edtTreatmentMethod, self.consultationAction.getProperty(u'Метод лечения').getValue())
        setTextEditValue(self.edtRecommentedTreatment, self.consultationAction.getProperty(u'Рекомендуемое лечение').getValue())
        setLineEditValue(self.edtTreatmentOrgStructure, self.consultationAction.getProperty(u'Лечебное отделение').getValue())

        self.buttonBox.buttons()[0].setText(u'Сохранить и печатать')

    def log(self, dateTo, comment):
        db = QtGui.qApp.db
        stmt = LOG_TRANSFER_STMT.format(
            table=LOG_TRANSFER_TABLE,
            dateFrom=self.dateFrom.toString('yyyy-MM-dd'),
            dateTo=dateTo.toString('yyyy-MM-dd'),
            personId=self.personId,
            eventId=self.eventId,
            comment=comment,
            diagnosis=self.consultationAction.getProperty(u'Диагноз').getValue() or u'',
            treatmentMethod=self.consultationAction.getProperty(u'Метод лечения').getValue() or u'',
            recommendedTreatment=self.consultationAction.getProperty(u'Рекомендуемое лечение').getValue() or u'',
            treatmentOrgStructure=self.consultationAction.getProperty(u'Лечебное отделение').getValue() or u'',
        )
        db.query(stmt)

    def save(self):
        comment = self.edtComment.toPlainText()
        dateTo = self.edtTransferDate.date()

        getDateEditValue(self.edtTransferDate, self.planningAction, 'directionDate')

        self.consultationAction.getProperty(u'Диагноз').setValue(forceString(self.edtDiagnosis.text()))
        self.consultationAction.getProperty(u'Метод лечения').setValue(forceString(self.edtTreatmentMethod.toPlainText()))
        self.consultationAction.getProperty(u'Рекомендуемое лечение').setValue(forceString(self.edtRecommentedTreatment.toPlainText()))
        self.consultationAction.getProperty(u'Лечебное отделение').setValue(forceString(self.edtTreatmentOrgStructure.text()))
        self.consultationAction.save(self.eventId)

        QtGui.qApp.db.insertOrUpdate('Action', self.planningAction)

        self.log(dateTo, comment)

    def canClose(self):
        if not self.edtComment.toPlainText():
            QtGui.QMessageBox.warning(
                self, u'Внимание!', u'Укажите причину переноса!', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok
            )
            return False

        if self.edtTransferDate.date().isNull():
            QtGui.QMessageBox.warning(
                self, u'Внимание!', u'Укажите дату переноса!', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok
            )
            return False

        return True

    def done(self, result):
        if result == QtGui.QDialog.Accepted:
            if self.canClose():
                self.save()
                printHospitalTransferTemplate(self, self.eventId)
                QtGui.QDialog.done(self, result)
        else:
            QtGui.QDialog.done(self, result)


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pes',
        'port': 3306,
        'database': 's12',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    QtGui.qApp.userId = 1

    w = CHospitalizationTransferDialog(None, 203123)
    w.exec_()


if __name__ == '__main__':
    main()
