# -*- coding: utf-8 -*-


from PyQt4 import QtGui, QtCore

from Exchange.R23.netrica.services import NetricaServices
from Ui_QueueList import Ui_QueueForm
from Ui_CreateQueueDialog import Ui_CreateQueueDialog
from library.DialogBase import CDialogBase
from library.TableModel import CTableModel, CTextCol, CRefBookCol
from library.Utils import forceString, forceInt, toVariant, forceDate


class QueueList(CDialogBase, Ui_QueueForm):
    def __init__(self, parent,):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.db = QtGui.qApp.db
        self.tblQueueControl = self.db.table('QueueControlEvents')
        self.tblOrgStruct = self.db.table('OrgStructure')
        self.tblMedProfile = self.db.table('rbMedicalAidProfile')
        self.address = forceString(self.db.translate(self.tblOrgStruct, self.tblOrgStruct['id'], QtGui.qApp.currentOrgStructureId(), self.tblOrgStruct['address']))
        self.setIsDirty(False)
        self.tblQueue.setModel(QueueTableModel(self))
        self.updateQueueTable()

    def updateQueueTable(self):
        idList = self.db.getIdList(self.tblQueueControl, self.tblQueueControl['id'])
        self.tblQueue.model().setIdList(idList)
        self.tblQueue.resizeColumnsToContents()

    @QtCore.pyqtSlot()
    def on_btnCreateQueue_clicked(self):
        editor = CreateQueue(self)
        editor.show()

    @QtCore.pyqtSlot()
    def on_btnRefresh_clicked(self):
        self.updateQueueTable()

    @QtCore.pyqtSlot()
    def on_btnCloseQueue_clicked(self):
        row = self.tblQueue.currentIndex().row()
        record = self.tblQueue.model().getRecordByRow(row)
        if record:
            exchange = NetricaServices()
            queueDict = {}
            queueDict['profile'] = forceString(self.db.translate(self.tblMedProfile, self.tblMedProfile['id'], forceInt(record.value('medicalProfile_id')), self.tblMedProfile['netrica_Code']))
            queueDict['begDate'] = forceDate(record.value('begDate'))
            queueDict['endDate'] = forceDate(QtCore.QDate.currentDate())
            queueDict['address'] = self.address
            queueDict['contacts'] = forceString(record.value('contacts'))
            queueDict['comment'] = forceString(record.value('notes'))
            exchange.updateMedServiceProfile(queueDict)
            record.setValue('closedDate', toVariant(QtCore.QDate.currentDate()))
            self.db.updateRecord('QueueControlEvents', record)
            self.updateQueueTable()
            QtGui.QMessageBox.information(self, u'Успешно', u'Очередь успешно остановлена')


class CreateQueue(CDialogBase, Ui_CreateQueueDialog):
    def __init__(self, parent,):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.db = QtGui.qApp.db
        self.tblQueue = self.db.table('QueueControlEvents')
        self.tblOrgStruct = self.db.table('OrgStructure')
        self.tblMedProfile = self.db.table('rbMedicalAidProfile')
        self.cmbMedicalProfile.setTable('rbMedicalAidProfile',  False, filter='netrica_Code IS NOT NULL')
        self.address = forceString(self.db.translate(self.tblOrgStruct, self.tblOrgStruct['id'], QtGui.qApp.currentOrgStructureId(), self.tblOrgStruct['address']))
        self.edtBeginDate.setDate(QtCore.QDate.currentDate())
        self.edtEndDate.setDate(QtCore.QDate.currentDate())
        self.edtBeginDate.setMinimumDate(QtCore.QDate.currentDate())
        self.setIsDirty(False)

    @QtCore.pyqtSlot()
    def on_btnCreate_clicked(self):
        recQueue = self.db.getRecordEx(self.tblQueue, '*',
                                       [self.tblQueue['medicalProfile_id'].eq(self.cmbMedicalProfile.value()),
                                        self.tblQueue['endDate'].gt(QtCore.QDate.currentDate()),
                                        self.tblQueue['closedDate'].isNull()])
        if recQueue:
            if QtGui.QMessageBox.warning(self, u'Обновление', u'Данная очередь уже существует. Обновить?', QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                      QtGui.QMessageBox.Yes) == QtGui.QMessageBox.No:
                return
        if self.checkData():
            exchange = NetricaServices()
            queueDict = {}
            queueDict['profile'] = forceString(self.db.translate(self.tblMedProfile, self.tblMedProfile['id'], forceInt(self.cmbMedicalProfile.value()), self.tblMedProfile['netrica_Code']))
            queueDict['begDate'] = self.edtBeginDate.date()
            queueDict['endDate'] = self.edtEndDate.date()
            queueDict['address'] = self.address
            queueDict['contacts'] = forceString(self.edtContacts.text())
            queueDict['comment'] = forceString(self.edtComment.text())
            exchange.updateMedServiceProfile(queueDict)
            recQueue = self.db.getRecordEx(self.tblQueue, '*', [self.tblQueue['medicalProfile_id'].eq(self.cmbMedicalProfile.value()), self.tblQueue['endDate'].gt(QtCore.QDate.currentDate()), self.tblQueue['closedDate'].isNull()])
            if not recQueue:
                recQueue = self.tblQueue.newRecord()
            recQueue.setValue('createPerson_id', toVariant(QtGui.qApp.userId))
            recQueue.setValue('medicalProfile_id', toVariant(self.cmbMedicalProfile.value()))
            recQueue.setValue('begDate', toVariant(self.edtBeginDate.date()))
            recQueue.setValue('endDate', toVariant(self.edtEndDate.date()))
            recQueue.setValue('contacts', toVariant(self.edtContacts.text()))
            recQueue.setValue('notes', toVariant(self.edtComment.text()))
            self.db.insertOrUpdate(self.tblQueue, recQueue)
            QtGui.QMessageBox.information(self, u'Успешно', u'Очередь успешно зарегистрирована')

    @QtCore.pyqtSlot()
    def on_btnCancel_clicked(self):
        self.close()


    def checkData(self):
        if not self.cmbMedicalProfile.value():
            self.checkInputMessage(u'профиль мед помощи', False, self.cmbMedicalProfile)
            return False
        if self.edtBeginDate.date().isNull() or self.edtBeginDate.date() < QtCore.QDate.currentDate() or self.edtBeginDate.date() > self.edtEndDate.date():
            self.checkInputMessage(u'дату начала', False, self.edtBeginDate)
            return False
        if not self.address:
            self.checkInputMessage(u'адрес подразделения', False, None)
            return False
        return True



class QueueTableModel(CTableModel):

    def __init__(self, parent):
        CTableModel.__init__(self, parent, [
            CRefBookCol(u'Профиль', ['medicalProfile_id'], 'rbMedicalAidProfile', 20),
            CTextCol(u'Дата начала', ['begDate'], 30),
            CTextCol(u'Дата окончания', ['endDate'],  20),
            CTextCol(u'Контакты', ['contacts'], 20),
            CTextCol(u'Комментарий', ['notes'], 20),
            CTextCol(u'Дата закрытия очереди', ['closedDate'], 20)
        ], 'QueueControlEvents')

        self.parentWidget = parent