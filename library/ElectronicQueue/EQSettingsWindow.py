# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################
from library.ElectronicQueue.EQControl import CEQRemoteControl
from library.ElectronicQueue.EQControlEditor import CEQControlEditor
from library.ElectronicQueue.EQViewer import CEQViewer
from library.Utils import generalConnectionName


__author__ = 'atronah'

'''
    author: atronah
    date:   19.10.2014
'''


from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtSql

from library.ElectronicQueue.Ui_EQSettingsWindow import Ui_EQSettingsWindow



class CEQSettingsWindow(QtGui.QDialog, Ui_EQSettingsWindow):
    addedControl = QtCore.pyqtSignal(int, int, QtCore.QString, QtCore.QString, int) # (orgStructureId, queueTypeId, name, host, port)
    allControlsEnabled = QtCore.pyqtSignal()
    allControlsDisabled = QtCore.pyqtSignal()

    viewQueueTypeAdded = QtCore.pyqtSignal(int)

    loadControlsClicked = QtCore.pyqtSignal()
    saveControlsClicked = QtCore.pyqtSignal()

    def __init__(self, parent = None, flags = QtCore.Qt.Window):
        flags |= QtCore.Qt.Dialog
        super(CEQSettingsWindow, self).__init__(parent, flags)
        self.setupUi(self)
        self.tblControls.horizontalHeader().setStretchLastSection(True)
        self.tblControls.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        self.btnStart.clicked.connect(self.allControlsEnabled)
        self.btnStop.clicked.connect(self.allControlsDisabled)

        self._viewer = CEQViewer.getInstance()
        self.sbNotifyPort.setValue(self._viewer.notifyPort())
        self.sbNotifyPort.valueChanged.connect(self._viewer.setNotifyPort)

        self.dsbViewerUpdateTimeout.setValue(self._viewer.updateTimeout())
        self.dsbViewerUpdateTimeout.valueChanged.connect(self._viewer.setUpdateTimeout)

        self.sbViewerRows.setValue(self._viewer.rowCount())
        self.sbViewerRows.valueChanged.connect(self._viewer.setRowCount)

        self.sbViewerColumns.setValue(self._viewer.columnCount())
        self.sbViewerColumns.valueChanged.connect(self._viewer.setColumnCount)

        self.sbViewerMaxTickets.setValue(self._viewer.maxTicketCount())
        self.sbViewerMaxTickets.valueChanged.connect(self._viewer.setMaxTicketCount)

        self.btnShowViewer.clicked.connect(self._viewer.showViewerWindow)

        self.tblViewedEQTypes.setModel(self._viewer.viewedEQTypeModel())

        self.btnLoadControls.clicked.connect(self.loadControlsClicked)
        self.btnSaveControls.clicked.connect(self.saveControlsClicked)


        self._queueTypeModel = QtSql.QSqlTableModel(self, QtSql.QSqlDatabase.database(generalConnectionName(),
                                                                                      open=True))
        self._queueTypeModel.setTable(u'rbEQueueType')
        # self._queueTypeModel.setFilter('`date` = CURRENT_DATE()')
        self._queueTypeModel.select()
        self.cmbAddedQueueType.setModel(self._queueTypeModel)
        self.cmbAddedQueueType.setModelColumn(self._queueTypeModel.fieldIndex('name'))



    def setControlModel(self, model):
        self.tblControls.setModel(model)


    def changeWorkState(self, isWork):
        self.btnStart.setEnabled(not isWork)
        self.btnStop.setEnabled(isWork)
        self.btnAddControl.setEnabled(not isWork)
        self.btnRemoveControl.setEnabled(not isWork)


    def isAutoStart(self):
        return self.chkAutoStart.isEnabled()



    def setAutoStart(self, checked):
        self.chkAutoStart.setChecked(checked)


    # def setDefaults(self, orgStructureId = None, queueTypeId = None, name = None, host = None, port = None):
    #     if orgStructureId:
    #         self.cmbO
    #


    @QtCore.pyqtSlot()
    def on_btnAddControl_clicked(self):
        dlg = CEQControlEditor(self)
        # dlg.setHost('192.168.0.209') #debug: atronah:
        dlg.setPort(4001)
        if dlg.exec_():
            self.addedControl.emit(dlg.orgStructureId(), dlg.queueTypeId(), dlg.name(), dlg.host(), dlg.port())



    @QtCore.pyqtSlot()
    def on_btnRemoveControl_clicked(self):
        index = self.tblControls.currentIndex()
        model = self.tblControls.model()
        controlId = model.controlIdByIndex(index)
        if model.canBeRemoved(controlId):
            model.removeControl(controlId)
        else:
            QtGui.QMessageBox.warning(self, u'Отказано', u'Нельзя удалить выбранный пульт управления очередью')


    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_tblControls_doubleClicked(self, index):
        model = self.tblControls.model()

        dlg = CEQControlEditor(self)

        controlId = model.controlIdByIndex(index)
        control = model.control(controlId)
        isRemoteControl = isinstance(control, CEQRemoteControl)

        dlg.setName(model.name(controlId))
        if isRemoteControl:
            dlg.setHost(control.host())
            dlg.setPort(control.port())
        else:
            dlg.disableRemoteSettings()

        dlg.setOrgStructureId(currentId=model.orgStructureId(controlId))
        dlg.setQueueTypeId(model.queueTypeId(controlId))

        if dlg.exec_():
            name = [dlg.name(), dlg.host(), dlg.port()] if isRemoteControl else dlg.name()
            model.setData(model.index(index.row(), model.iName),
                          QtCore.QVariant(name))
            model.setData(model.index(index.row(), model.iQueueType),
                          QtCore.QVariant(dlg.queueTypeId()))
            model.setData(model.index(index.row(), model.iOrgStructure),
                          QtCore.QVariant(dlg.orgStructureId()))


    # @QtCore.pyqtSlot(int)
    # def on_cmbAddedQueueType_currentChanged(self, idx):
    #     self.btnAddControl.setEnabled(idx in xrange(self._queueTypeModel.rowCount()))


    @QtCore.pyqtSlot()
    def on_btnAddQueue_clicked(self):
        row = self.cmbAddedQueueType.currentIndex()
        queueTypeId = self._queueTypeModel.record(row).value('id').toInt()[0]
        self.tblViewedEQTypes.model().addQueueTypeId(queueTypeId)


    @QtCore.pyqtSlot()
    def on_btnRemoveQueue_clicked(self):
        index = self.tblViewedEQTypes.currentIndex()
        if index.isValid():
            row = index.row()
            self.tblViewedEQTypes.model().removeRow(row)






def main():
    import sys
    app = QtGui.QApplication(sys.argv)


    sys.exit(app.exec_())


if __name__ == '__main__':
    main()