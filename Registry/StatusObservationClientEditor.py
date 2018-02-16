# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.crbcombobox    import CRBComboBox
from library.Utils          import forceRef, toVariant

from Ui_StatusObservationClientEditor import Ui_StatusObservationClientEditor


class CStatusObservationClientEditor(QtGui.QDialog, Ui_StatusObservationClientEditor):
    def __init__(self,  parent, clientId):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.clientId = clientId
        self.record = None
        self.cmbStatusObservationType.setTable('rbStatusObservationClientType', True)
        self.cmbStatusObservationType.setShowFields(CRBComboBox.showCodeAndName)
        self.setRecord()


    def setRecord(self):
        if self.clientId:
            db = QtGui.qApp.db
            table = db.table('Client_StatusObservation')
            rbTable = db.table('rbStatusObservationClientType')
            self.record = db.getRecordEx(table.innerJoin(rbTable, table['statusObservationType_id'].eq(rbTable['id'])), 'Client_StatusObservation.*', [table['deleted'].eq(0), table['master_id'].eq(self.clientId)], 'Client_StatusObservation.id DESC')
            if self.record:
                self.cmbStatusObservationType.setValue(forceRef(self.record.value('statusObservationType_id')))


    def getRecord(self):
        if self.clientId:
            db = QtGui.qApp.db
            if not self.record:
                self.record = db.record('Client_StatusObservation')
                self.record.setValue('master_id', toVariant(self.clientId))
            self.record.setValue('statusObservationType_id', toVariant(forceRef(self.cmbStatusObservationType.value())))
        return self.record


    def save(self):
        try:
            db = QtGui.qApp.db
            db.transaction()
            try:
                record = self.getRecord()
                id = db.insertOrUpdate(db.table('Client_StatusObservation'), record)
                db.commit()
            except:
                db.rollback()
                raise
            return id
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical( self,
                                        u'',
                                        unicode(e),
                                        QtGui.QMessageBox.Close)
            return None


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Ok:
            self.save()
        elif buttonCode == QtGui.QDialogButtonBox.Cancel:
            self.close()
