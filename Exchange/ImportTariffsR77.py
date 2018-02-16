# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

u"""
Импорт тарифа из ЕИС-ОМС
"""
from Ui_ImportTariffsR77 import Ui_Dialog
from Cimport import *


def ImportTariffsR77(widget, contractId):
    dlg=CImportTariffs(widget, contractId)
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportTariffR77FileName',  '')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportTariffR77FileName'] = toVariant(dlg.edtFileName.text())


class CImportTariffs(QtGui.QDialog, Ui_Dialog, CDBFimport):
    def __init__(self, parent, contractId):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.parent = parent
        self.contractId = contractId
        self.tblContract_Tariff = tbl('Contract_Tariff')

        self.aborted = False
        self.dupAskUser = False
        self.dupUpdate = False
        self.dupSkip = False

        self.nSkipped = 0
        self.nAdded = 0
        self.nUpdated = 0
        self.nProcessed = 0

        self.unitId = None
        self.amount = 0
        self.tariffType = 2


    def startImport(self):
        db = QtGui.qApp.db
        contractId = self.contractId
        if not contractId:
            return

        dbfFileName = forceStringEx(self.edtFileName.text())
        dbfTariff = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
        self.progressBar.setMaximum(len(dbfTariff)-1)

        self.nSkipped = 0
        self.nAdded = 0
        self.nUpdated = 0
        self.nProcessed = 0

        self.amount =  0
        self.unitId = forceRef(QtGui.qApp.db.translate('rbMedicalAidUnit', 'code',
            '6', 'id'))

        if not self.unitId:
            self.log.append(u'<b><font color=red>ОШИБКА:</b>'
             u' Не найдена единица учета медицинской помощи'
             u' (rbMedicalAidUnit) с кодом "6"(Медицинская услуга)')
            return

        self.dupAskUser = self.chkAskUser.isChecked()
        self.dupUpdate = self.chkUpdate.isChecked()
        self.dupSkip = self.chkSkip.isChecked()

        self.process(dbfTariff, self.processTariff)

        dbfTariff.close()
        self.log.append(u'добавлено: %d; изменено: %d' % (self.nAdded, self.nUpdated))
        self.log.append(u'пропущено: %d; обработано: %d' % (self.nSkipped, self.nProcessed))
        self.log.append(u'готово')


    def process(self, dbf, step):
        try:
            for row in dbf:
                QtGui.qApp.processEvents()
                if self.aborted:
                    self.reject()
                    return
                self.progressBar.setValue(self.progressBar.value()+1)
                QtGui.qApp.db.transaction()
                try:
                    step(row)
                    QtGui.qApp.db.commit()
                except:
                    QtGui.qApp.db.rollback()
                    QtGui.qApp.logCurrentException()
                    raise

        except ValueError:
            self.log.append(u'<b><font color=red>ОШИБКА:</b>'
                    u' неверное значение строки "%d" в dbf.' % \
                    (self.progressBar.value()+1))
            self.nSkipped += 1
            self.aborted = True


    def processTariff(self,  row):
        serviceCode = row['SCODE'].strip()
        tariff = row['PRICE'] # float
        serviceId = self.findServiceByInfisCode(serviceCode)

        if not serviceId:
            self.log.append(u'<b><font color=orange>ОШИБКА:</b>'
                u' Услуга, код ИНФИС: "%s", не найдена' % serviceCode)
            self.nSkipped += 1
            return

        self.log.append(u'Услуга: "%s". Тариф: <b>'
                u'<font color=green>"%.2f"</b>' % (serviceCode, tariff))
        self.addOrUpdateTariff(serviceCode, serviceId,  tariff)
        self.nProcessed += 1


    def addOrUpdateTariff(self,  serviceCode,  serviceId, price,  age = None):
        (tariffId, oldPrice) = self.findTariff(serviceId,  age)

        if tariffId:
            self.log.append(u'Найден совпадающий тариф.')
            if self.dupSkip:
                self.log.append(u'Пропускаем.')
                self.nSkipped += 1
                return
            elif oldPrice == price:
                self.log.append(u'Цены совпадают (%.2f), пропускаем.' % price)
                self.nSkipped += 1
                return
            elif self.dupUpdate:
                self.log.append(u'Обновляем. (%.2f на %.2f)' % (oldPrice, price))
                self.updateTariff(tariffId,  price)
                self.nUpdated += 1
            else:
                self.log.append(u'Запрос действий у пользователя.')
                answer = QtGui.QMessageBox.question(self, u'Совпадающий тариф',
                                        u'Услуга "%s", возраст "%s"\n'
                                        u'Тариф: "%.2f", новый "%.2f"\n'
                                        u'Обновить?' %(serviceCode,  age if age else '-',  oldPrice,  price),
                                        QtGui.QMessageBox.No|QtGui.QMessageBox.Yes,
                                        QtGui.QMessageBox.No)
                self.log.append(u'Выбор пользователя %s' % \
                    (u'обновить' if answer == QtGui.QMessageBox.Yes else u'пропустить'))
                if answer == QtGui.QMessageBox.Yes:
                    self.updateTariff(tariffId,  price)
                    self.nUpdated += 1
                else:
                    self.nSkipped += 1
        else:
            self.log.append(u'Добавляем тариф.')
            self.nAdded += 1
            self.addTariff(serviceId,  price,  age)


    def addTariff(self, serviceId,  price,  age = None):
        record = self.tblContract_Tariff.newRecord()
        record.setValue('price', toVariant(price))
        if age:
            record.setValue('age', toVariant(age))
        record.setValue('service_id', toVariant(serviceId))
        record.setValue('master_id',  toVariant(self.contractId))
        record.setValue('tariffType',  toVariant(self.tariffType))
        record.setValue('unit_id',  toVariant(self.unitId))
        record.setValue('amount',  toVariant(self.amount))
        return QtGui.qApp.db.insertRecord(self.tblContract_Tariff, record)


    def updateTariff(self, tariffId,  price):
        record = QtGui.qApp.db.getRecord(self.tblContract_Tariff, '*', tariffId)
        record.setValue('price', toVariant(price))
        return QtGui.qApp.db.updateRecord(self.tblContract_Tariff, record)


    def findTariff(self,  serviceId,  age):
        table = QtGui.qApp.db.table('Contract_Tariff')
        cond = []
        cond.append(table['master_id'].eq(self.contractId))
        if age:
            cond.append(table['age'].eq(age))
        cond.append(table['service_id'].eq(serviceId))
        cond.append(table['tariffType'].eq(self.tariffType))
        record = QtGui.qApp.db.getRecordEx(table, 'id, price',  cond, 'id')
        if record:
            return (forceRef(record.value(0)), forceDouble(record.value(1)))
        else:
            return (None,  0.0)


    def findServiceByInfisCode(self, code):
        table = QtGui.qApp.db.table('rbService')
        record = QtGui.qApp.db.getRecordEx(table, 'id',  table['infis'].eq(code), 'id')
        if record:
            return forceRef(record.value(0))
        else:
            return None


    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '' :
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)
            dbfFileName = forceStringEx(self.edtFileName.text())
            dbfTariff = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
            self.labelNum.setText(u'всего записей в источнике: '+str(len(dbfTariff)))