# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore
from Ui_EQConfigWidget import Ui_EQConfigWidget
from library.TableModel import CDesignationCol, CTextCol, CTableModel, CIntCol
from library.Utils import toNativeType, forceStringEx, forceInt, toVariant,\
    forceBool, forceRef
from library.ElectronicQueue.EQPanel import showC, connect
from Users.Rights import urAdmin

'''
Created on 05.11.2013

@author: atronah
'''

#TODO: atronah: вынести в отдельный общий модуль
class CExtendedSortFilterProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self, parent = None):
        QtGui.QSortFilterProxyModel.__init__(self, parent)
        self._isFilterByValuesList = False
        self._valuesList = []
    
    
    def setFilterByValuesList(self, valuesList):
        if isinstance(valuesList, list):
            self._isFilterByValuesList = True
            self._valuesList = valuesList
        else:
            self._isFilterByValuesList = False
            self._valuesList = []
            
    
    def setFilterByValuesListEnabled(self, isEnabled):
        self._isFilterByValuesList = isEnabled
        if not isEnabled:
            self._valuesList = []
        
    
    def filterAcceptsRow(self, sourceRow, sourceParent):
        result = QtGui.QSortFilterProxyModel.filterAcceptsRow(self, sourceRow, sourceParent)
        if result and self._isFilterByValuesList:
            value = toNativeType(self.sourceModel().index(sourceRow, self.filterKeyColumn()).data(self.filterRole()))
            result &= value in self._valuesList
        return result


class CGatewayConfigModel(CTableModel):
    eqGatewayConfigTableName = u'rbEQGatewayConfig'
    
    def __init__(self, parent = None):
        #atronah: Для возможности отвязать в дальнейшем классы от QtGui.qApp.db 
        #(пока что эта связь есть в CTableModel и поэтому я ее сохраняю)
        self._db = QtGui.qApp.db
        
        cols = [CTextCol(u'Код', ['code'], 10),
                CTextCol(u'Наименование', ['name'], 64),
                CDesignationCol(u'Подразделение', ['orgStructure_id'], ('OrgStructure', 'code'), 10),
                CTextCol(u'Шлюз', ['host'], 16),
                CIntCol(u'Порт', ['port'], 8)]
        CTableModel.__init__(self, 
                             parent,
                             cols,
                             CGatewayConfigModel.eqGatewayConfigTableName
                             )
        self.setIdList(self._db.getIdList(CGatewayConfigModel.eqGatewayConfigTableName))
    
    def host(self, row):
        return forceStringEx(self.index(row, 3).data(QtCore.Qt.DisplayRole))
    
    
    def port(self, row):
        return forceInt(self.index(row, 4).data(QtCore.Qt.DisplayRole))
    
    


class CEQConfigWidget(QtGui.QWidget, Ui_EQConfigWidget):  
    eqOfficeTableName = u'EQOffice'
    eqPersonPreferenceTableName = u'EQPersonPreference'
      
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        
        self.personOrgStructureIdList = []
        self.personId = None 
        
        
        self.stackedWidget.setCurrentIndex(1) #atronah: 0 страница (задание адреса табло) пока не поддерживается
        
        self.gatewayConfigModel = CGatewayConfigModel()
        self.gatewayConfigProxyModel = CExtendedSortFilterProxyModel(self)
        self.gatewayConfigProxyModel.setSourceModel(self.gatewayConfigModel)
        self.gatewayConfigProxyModel.setFilterKeyColumn(2)
        self.gatewayConfigProxyModel.setFilterRole(QtCore.Qt.UserRole)
        
        self.cmbOffice.setTable(CEQConfigWidget.eqOfficeTableName, 'office', True)
        self.cmbGatewayPlace.setModel(self.gatewayConfigProxyModel)
        self.cmbGatewayPlace.setModelColumn(1)
        self.cmbGatewayPlace.setCurrentIndex(0)
        
        self._isDirty = False
        
        
        self.cmbOffice.currentIndexChanged.connect(self.markAsDirty)
        self.chkDateControl.toggled.connect(self.markAsDirty)
        self.chkPersonControl.toggled.connect(self.markAsDirty)
        
    
    @staticmethod
    def getEQConfig(personId):
        db = QtGui.qApp.db
        
        tableEQPersonPreferences = db.table(CEQConfigWidget.eqPersonPreferenceTableName)
        tableEQOffice = db.table(CEQConfigWidget.eqOfficeTableName)
        tableEQGatewayConfig = db.table(CGatewayConfigModel.eqGatewayConfigTableName)
        
        queryTable = tableEQPersonPreferences.leftJoin(tableEQOffice, tableEQOffice['id'].eq(tableEQPersonPreferences['eqOffice_id']))
        queryTable = queryTable.leftJoin(tableEQGatewayConfig, tableEQGatewayConfig['id'].eq(tableEQOffice['gateway_id']))
        
        cols = [tableEQOffice['address'],
                tableEQOffice['office'],
                tableEQGatewayConfig['host'],
                tableEQGatewayConfig['port'],
                tableEQPersonPreferences['dateControl'],
                tableEQPersonPreferences['personControl'],
                tableEQPersonPreferences['isControlEnabled'] 
                ]
        
        cond = [tableEQPersonPreferences['person_id'].eq(personId)]
        
        record = db.getRecordEx(queryTable, cols, where = cond)
        
        isControl = forceBool(record.value('isControlEnabled')) if record and not record.isNull('isControlEnabled') else False
        host = forceStringEx(record.value('host')) if record and not record.isNull('host') else None
        port = forceInt(record.value('port')) if record and not record.isNull('port') else None
        panelAddress = forceInt(record.value('address')) if record and not record.isNull('address') else None
        office = forceStringEx(record.value('office')) if record and not record.isNull('office') else None
        dateControl = forceBool(record.value('dateControl')) if record and not record.isNull('dateControl') else True
        personControl = forceBool(record.value('personControl')) if record and not record.isNull('personControl') else True
        
        return {'isConfigured': bool(record),
                'isControl': isControl,
                'host' : host,
                'port' : port,
                'office' : office,
                'panelAddress' : panelAddress,
                'dateControl' : dateControl,
                'personControl' : personControl}
    
    
    def configure(self, isControl):
        if not self.personId:
            return False
        
        db = QtGui.qApp.db
        tableEQPersonPreferences = db.table(CEQConfigWidget.eqPersonPreferenceTableName)
        
        record = db.getRecordEx(tableEQPersonPreferences, '*', tableEQPersonPreferences['person_id'].eq(self.personId))
        if not record or record.isEmpty():
            record = tableEQPersonPreferences.newRecord()
            record.setValue('person_id', toVariant(self.personId))
            
        record.setValue('eqOffice_id', toVariant(self.cmbOffice.value()))
        record.setValue('isControlEnabled', toVariant(isControl))
        
        db.insertOrUpdate(tableEQPersonPreferences, record)
        self.setDirty(False)
        return True
        
    
    def setOfficeId(self, officeId):
        self.cmbOffice.setValue(officeId)
    
    
    def setDirty(self, isDirty):
        self._isDirty = isDirty
        self.btnCommit.setEnabled(isDirty)
    
    
    def isDirty(self):
        return self._isDirty
    
    
    @QtCore.pyqtSlot()
    def markAsDirty(self):
        self.setDirty(True)
        
    
    def setPersonInfo(self, personId, orgStructureIdList):
        self.personId =  personId
        self.personOrgStructureIdList = orgStructureIdList

        self.btnShowAllAddresses.setVisible(QtGui.qApp.userHasRight(urAdmin))

        db = QtGui.qApp.db
        tableEQOffice = db.table(CEQConfigWidget.eqOfficeTableName)
        tableEQPersonPreferences = db.table(CEQConfigWidget.eqPersonPreferenceTableName)
        
        record = db.getRecord(tableEQPersonPreferences, '*', self.personId)
        if record:
            self.chkDateControl.setChecked(forceBool(record.value('dateControl')))
            self.chkPersonControl.setChecked(forceBool(record.value('personControl')))
            self.gatewayConfigProxyModel.setFilterByValuesListEnabled(False)
            
            officeId = forceRef(record.value('eqOffice_id'))
            officeRecord = db.getRecord(tableEQOffice, '*', officeId) if officeId else None
            if officeRecord:
                gatewayId = forceRef(officeRecord.value('gateway_id'))
                gatewayProxyRow = 0
                for gatewaySourceRow in xrange(self.gatewayConfigModel.rowCount()):
                    if self.gatewayConfigModel.idList[gatewaySourceRow] == gatewayId:
                        sourceIndex = self.gatewayConfigModel.index(gatewaySourceRow, 0)
                        gatewayProxyRow = self.gatewayConfigProxyModel.mapFromSource(sourceIndex).row()
                        break
                if not gatewayProxyRow:
                    self.on_btnReset_clicked()
                    return
                
                self.cmbGatewayPlace.setCurrentIndex(gatewayProxyRow)
                if officeId in self.cmbOffice.values():
                    self.cmbOffice.setValue(officeId)
                else:
                    self.cmbOffice.setValue(0)
                    self.setDirty(True)            
        else:
            self.on_btnReset_clicked()
        
        return {'host' : forceStringEx(self.edtHost.text()),
                'port' : forceInt(self.spbPort.value())}
        
    
    
    def setPersonOrgStructureIdList(self, orgStructureIdList):
        self.personOrgStructureIdList = orgStructureIdList if isinstance(orgStructureIdList, list) else [orgStructureIdList]
    
    
    @QtCore.pyqtSlot(bool)
    def on_chkFindByOrgStructure_toggled(self, isChecked):
        if isChecked:
            self.gatewayConfigProxyModel.setFilterByValuesList(self.personOrgStructureIdList)
        else:
            self.gatewayConfigProxyModel.setFilterByValuesListEnabled(False)
        self.gatewayConfigProxyModel.invalidate()
        self.cmbGatewayPlace.setCurrentIndex(0)
    
    
    #atronah: не уверен, что сия функция сработает, если мы для пустого комбобокса сделаем setCurrentIndex(0)
    @QtCore.pyqtSlot(int)
    def on_cmbGatewayPlace_currentIndexChanged(self, currentRow):
        if currentRow not in xrange(self.gatewayConfigProxyModel.rowCount()):
            self.setDirty(False)
            return
        
        proxyIndex = self.gatewayConfigProxyModel.index(currentRow, 0)
        sourceIndex = self.gatewayConfigProxyModel.mapToSource(proxyIndex)
        
        self.edtHost.setText(self.gatewayConfigModel.host(sourceIndex.row()))
        self.spbPort.setValue(self.gatewayConfigModel.port(sourceIndex.row()))
        
        officeFilter = 'gateway_id = %d' % self.gatewayConfigModel.idList()[sourceIndex.row()]
        #TODO: atronah: Можно было бы сделать так же, как и с cmbGatewayPlace
        # т.е. не грузить каждый раз из базы, а один раз загрузить и дальше фильтровать через прокси модель
        # но, у CTableModel нет режима с None строкой, а так же у CDbComboBox есть кеширование с учетом фильтра.
        # Поэтому возможен вариант, что реализация cmbGatewayPlace через прокси модель окажется медленнее, чем если бы через CDbComboBox
        self.cmbOffice.setFilter(officeFilter) 
        self.cmbOffice.setCurrentIndex(0)
    
    
    @QtCore.pyqtSlot()
    def on_btnCommit_clicked(self):
        self.configure(True)
    
    
    @QtCore.pyqtSlot()   
    def on_btnReset_clicked(self):
        self.chkDateControl.setChecked(True)
        self.chkPersonControl.setChecked(True)
        self.chkFindByOrgStructure.setChecked(True)
        self.cmbGatewayPlace.setCurrentIndex(0)
        self.cmbOffice.setCurrentIndex(0)
        self.markAsDirty()
        
    
    def getOfficeSelectDialog(self, parent):
        return COfficeSelectDialog(self.cmbOffice.model(), parent)
    
    
    @QtCore.pyqtSlot()
    def on_btnShowAllAddresses_clicked(self):
        timeout = 1
        fromIdx = 1
        toIdx = 254
        userChoise = QtGui.QMessageBox.information(self, 
                                                   u'Подтвердтите операцию', 
                                                   u'Данная операция произведет вывод на все табло их адресов.\n'
                                                   u'Вывод будет производится последовательно\n'
                                                   u'(перебором адресов от %d до %d)\n' % (fromIdx, toIdx)
                                                   + u'с задержкой в %f секунд(-у)\n' % timeout
                                                   + u'Информация будет отображаться на табло в течении минуты.\n'
                                                   u'\n'
                                                   u'Хотите продолжить?', 
                                                   buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel, 
                                                   defaultButton = QtGui.QMessageBox.NoButton)
        if userChoise == QtGui.QMessageBox.Yes:
            QtGui.qApp.callWithWaitCursor(self, self.showAllAddresses, fromIdx, toIdx, timeout)
            
            
    
    def showAllAddresses(self, fromIdx, toIdx, timeout):
        if not self.personId:
            return
        
        import time, sip
        eqConfig = CEQConfigWidget.getEQConfig(self.personId)
#        print 'connecting' #atronah: debug
        sock = connect(eqConfig['host'],
                       eqConfig['port'],
                       0.1)
        
        progressWidget = QtGui.QDialog()
        layout = QtGui.QVBoxLayout()
        indicator = QtGui.QProgressBar(parent = self)
        indicator.setRange(fromIdx, toIdx)
        indicator.setAlignment(QtCore.Qt.AlignCenter)
        indicator.setFormat(u'Адрес: %v (Завершено: %p%)')
        layout.addWidget(indicator)
        btnCancel = QtGui.QPushButton(u'Отменить')
        btnCancel.clicked.connect(progressWidget.hide)
        layout.addWidget(btnCancel)
        progressWidget.setLayout(layout)
        progressWidget.setWindowTitle(u'Отображение адресов табло')
        progressWidget.setModal(True)
        progressWidget.show()
        for addr in xrange(fromIdx, toIdx + 1):
            indicator.setValue(addr)
            showC(sock, 'g!%04d'  % addr, addr, 254)
#            print addr #atronah: debug
            time.sleep(timeout)
            QtGui.qApp.processEvents()
            if progressWidget.isHidden():
                break
            
    
class COfficeSelectDialog(QtGui.QDialog):
    def __init__(self, model, parent = None):
        QtGui.QDialog.__init__(self, parent)
        
        
        self.lblPrompt = QtGui.QLabel(u'Укажите ваш кабинет,\nчтобы вызов пациента отображался\nна нужном табло') 
        
        self.cmbOffice = QtGui.QComboBox()
        self.cmbOffice.setModel(model)
        
        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok,
                                                QtCore.Qt.Horizontal)
        self.buttonBox.accepted.connect(self.accept)
        
        self.chkSaveSelect = QtGui.QCheckBox(u'Больше не спрашивать')
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.lblPrompt)
        layout.addWidget(self.cmbOffice)
        layout.addWidget(self.buttonBox)
        layout.addWidget(self.chkSaveSelect)
        
        self.setLayout(layout)
        
        self.setWindowTitle(u'Укажите свой кабинет')
    
    
    def getPanelAddressAndOffice(self):
        if self.cmbOffice.currentIndex() <= 0:
            return None, u''
        
        address = forceInt(QtGui.qApp.db.translate(CEQConfigWidget.eqOfficeTableName, 
                                              'id', self.getOfficeId(),
                                              'address'))
        
        office = self.cmbOffice.currentText()
        return address, office
    
    
    def getOfficeId(self):
        if not hasattr(self.cmbOffice.model(), 'getId'):
            return None
        return self.cmbOffice.model().getId(self.cmbOffice.currentIndex())
    
    
    def isSaveSelect(self):
        return self.chkSaveSelect.isChecked()
    
    