# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013-2014 Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore, QtGui

from Ui_HospitalBedsLocationCardEditor import Ui_HospitalBedsLocationCardEditor
from library.Utils import forceDate, forceRef, forceInt, toVariant
from library.crbcombobox import CRBComboBox


class CHospitalBedsLocationCardTypeEditor(QtGui.QDialog, Ui_HospitalBedsLocationCardEditor):
    def __init__(self,  parent, eventIdList):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.cmbLocationCardType.setTable('rbHospitalBedsLocationCardType', True)
        self.cmbLocationCardType.setShowFields(CRBComboBox.showCodeAndName)

        db = QtGui.qApp.db
        tableEHBLC = db.table('Event_HospitalBedsLocationCard')
        recordList = db.getRecordList(tableEHBLC, where=db.joinAnd([
            tableEHBLC['event_id'].eq(eventIdList[0]),
            tableEHBLC['deleted'].eq(0)
        ]))
        if len(recordList) == 1:
            self.edtDateMoveCard.setDate(forceDate(recordList[0].value('moveDate')))
            self.edtDateReturnCard.setDate(forceDate(recordList[0].value('returnDate')))
            self.cmbLocationCardType.setValue(forceRef(recordList[0].value('locationCardType_id')))
        else:
            self.edtDateMoveCard.setDate(QtCore.QDate.currentDate())
            self.edtDateReturnCard.setDate(None)

        # Предполагаем, что в таблице Event_HospitalBedsLocationCard event_id является уникальным.
        # Это должно быть правдой, начиная с ревизии 16478.
        self.oldRecords = {}
        for record in recordList:
            self.oldRecords[forceInt(record.value('id'))] = forceInt(record.value('event_id'))
        oldEventIds = set(self.oldRecords.values())
        self.newRecords = [eventId for eventId in eventIdList if eventId not in oldEventIds]

    def save(self):
        db = QtGui.qApp.db
        db.transaction()
        try:
            tableEHBLC = db.table('Event_HospitalBedsLocationCard')
            cardTypeId = self.cmbLocationCardType.value()
            if cardTypeId is None:
                db.deleteRecord(tableEHBLC, tableEHBLC['id'].inlist(self.oldRecords.keys()))
            else:
                moveDate = toVariant(forceDate(self.edtDateMoveCard.date()))
                returnDate = toVariant(forceDate(self.edtDateReturnCard.date()))

                db.updateRecords(
                    tableEHBLC,
                    [
                        tableEHBLC['locationCardType_id'].eq(cardTypeId),
                        tableEHBLC['moveDate'].eq(moveDate),
                        tableEHBLC['returnDate'].eq(returnDate),
                    ],
                    tableEHBLC['id'].inlist(list(self.oldRecords))
                )

                for eventId in self.newRecords:
                    record = db.record('Event_HospitalBedsLocationCard')
                    record.setValue('moveDate', moveDate)
                    record.setValue('returnDate', returnDate)
                    record.setValue('locationCardType_id', toVariant(forceRef(cardTypeId)))
                    record.setValue('event_id', toVariant(eventId))
                    db.insertRecord(tableEHBLC, record)

            db.commit()
        except Exception, e:
            QtGui.qApp.logCurrentException()
            db.rollback()
            QtGui.QMessageBox.critical(self,
                                       u'',
                                       unicode(e),
                                       QtGui.QMessageBox.Close)


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Ok:
            self.save()
        elif buttonCode == QtGui.QDialogButtonBox.Cancel:
            self.close()
