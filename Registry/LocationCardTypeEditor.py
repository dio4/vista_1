# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.crbcombobox import CRBComboBox
from library.Utils import forceRef
from Ui_LocationCardEditor import Ui_LocationCardEditor


class CLocationCardTypeEditor(QtGui.QDialog, Ui_LocationCardEditor):
    def __init__(self, parent, clientId):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.clientId = clientId
        self.record = None
        self.cmbLocationCardType.setTable('rbLocationCardType', True)
        self.cmbLocationCardType.setShowFields(CRBComboBox.showCodeAndName)
        self.setRecord()

    def setRecord(self):
        if self.clientId:
            db = QtGui.qApp.db
            table = db.table('Client_LocationCard')
            rbTable = db.table('rbLocationCardType')
            self.record = db.getRecordEx(table.innerJoin(rbTable, table['locationCardType_id'].eq(rbTable['id'])),
                                         'Client_LocationCard.*',
                                         [table['deleted'].eq(0), table['master_id'].eq(self.clientId)],
                                         'Client_LocationCard.id DESC')
            if self.record:
                self.cmbLocationCardType.setValue(forceRef(self.record.value('locationCardType_id')))

    def save(self):
        try:
            db = QtGui.qApp.db
            db.transaction()
            try:
                if self.clientId:
                    locationCardType = forceRef(self.cmbLocationCardType.value())
                    db = QtGui.qApp.db
                    table = db.table('Client_LocationCard')
                    if self.record:
                        self.record.setValue('deleted', 1)
                        db.insertOrUpdate(table, self.record)
                    if locationCardType:
                        record = table.newRecord()
                        record.setValue('master_id', QtCore.QVariant(self.clientId))
                        record.setValue('locationCardType_id', QtCore.QVariant(locationCardType))
                        db.insertOrUpdate(table, record)
                db.commit()
            except:
                db.rollback()
                raise
            return id
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical(self,
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
