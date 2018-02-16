# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

u"""
Импорт тарифа для Смоленской области
"""
from math import ceil
import decimal

from Ui_ImportTariffsR67 import Ui_Dialog
from Cimport import *

def ImportTariffsR67(widget, contractId, begDate, endDate, tariffList):
    dlg=CImportTariffs(widget, contractId, begDate, endDate, tariffList)
    dlg.edtFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportTariffR67FileName',  '')))
    dlg.edtCustomFileName.setText(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportTariffR67CustomFileName', '')))
    dlg.chkOnlyForCurrentOrg.setChecked(forceBool(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportTariffR67CurrentOrgOnly',  False)))
    dlg.edtUetValue.setValue(forceDouble(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportTariffR67UetValue',  0.01)))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportTariffR67FileName'] = toVariant(dlg.edtFileName.text())
    QtGui.qApp.preferences.appPrefs['ImportTariffR67CustomFileName'] = toVariant(dlg.edtCustomFileName.text())
    QtGui.qApp.preferences.appPrefs['ImportTariffR67CurrentOrgOnly'] = \
        toVariant(dlg.chkOnlyForCurrentOrg.isChecked())
    QtGui.qApp.preferences.appPrefs['ImportTariffR67UetValue'] = \
        toVariant(dlg.edtUetValue.value())
    return dlg.ok, dlg.tariffList


class CImportTariffs(QtGui.QDialog, Ui_Dialog, CDBFimport):
    def __init__(self,  parent, contractId, begDate, endDate, tariffList):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.parent = parent
        self.contractId = contractId
        self.tblContract_Tariff = tbl('Contract_Tariff')
        self.ok = False

        self.tariffList = map(None, tariffList)
        self.tariffDict = {}
        self.customData = {}

        for i, tariff in enumerate(self.tariffList):
            key = ( forceInt(tariff.value('tariffType')),
                    forceRef(tariff.value('service_id')),
                    forceInt(tariff.value('sex')),
                    forceString(tariff.value('age')),
                  )
            tariffIndexList = self.tariffDict.setdefault(key, [])
            tariffIndexList.append(i)

        self.dupAskUser = False
        self.dupUpdate = False
        self.dupSkip = False
        self.dupAppend = False
        self.currentOrgOnly = False
        self.yesToAll = False
        self.noToAll = False
        self.saveAll = False
        self.currentOrgInfisCode = None

        self.nSkipped = 0
        self.nAdded = 0
        self.nUpdated = 0
        self.nProcessed = 0
        self.nAppended = 0

        self.unitVisitId = None
        self.unitServiceId = None

        self.secondTariffUnitId = -1


    def exec_(self):
        self.updateLabel()
        QtGui.QDialog.exec_(self)


    def startImport(self):
        self.ok = False
        db = QtGui.qApp.db
        contractId = self.contractId
        if not contractId:
            return

        self.secondTariffUnitId = forceInt(QtGui.qApp.db.translate('rbMedicalAidUnit', 'code', 32, 'id'))
        if not forceStringEx(self.edtCustomFileName.text()):
            res = QtGui.QMessageBox.warning( self,
                                             u'Внимание!',
                                             u'Вы не указали файл настроек тарифов.',
                                             QtGui.QMessageBox.Ok|QtGui.QMessageBox.Ignore,
                                             QtGui.QMessageBox.Ok)
            if res == QtGui.QMessageBox.Ok:
                self.btnCustomSelectFile.setFocus(Qt.ShortcutFocusReason)
                return

        dbfFileName = forceStringEx(self.edtFileName.text())
        dbfCustomFileName = forceStringEx(self.edtCustomFileName.text())
        dbfTariff = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
        if dbfCustomFileName:
            dbfCustomize = dbf.Dbf(dbfCustomFileName, readOnly=True, encoding='cp866')
        else:
            dbfCustomize = None
        self.progressBar.setMaximum(len(dbfTariff)-1)

        self.nSkipped = 0
        self.nAdded = 0
        self.nUpdated = 0
        self.nProcessed = 0
        self.nAppended = 0

        self.unitVisitId = forceRef(QtGui.qApp.db.translate('rbMedicalAidUnit', 'code',
            '1', 'id'))
        self.unitServiceId = forceRef(QtGui.qApp.db.translate('rbMedicalAidUnit', 'code',
            '6', 'id'))

        if not self.unitVisitId:
            self.log.append(u'<b><font color=red>ОШИБКА:</b>'
             u' Не найдена единица учета медицинской помощи'
             u' (rbMedicalAidUnit) с кодом "1" (Посещение)')
            return

        if not self.unitServiceId:
            self.log.append(u'<b><font color=red>ОШИБКА:</b>'
             u' Не найдена единица учета медицинской помощи'
             u' (rbMedicalAidUnit) с кодом "6" (Медицинская услуга)')
            return

        self.dupAskUser = self.chkAskUser.isChecked()
        self.dupUpdate = self.chkUpdate.isChecked()
        self.dupSkip = self.chkSkip.isChecked()
        self.dupAppend = self.chkAppend.isChecked()
        self.currentOrgOnly = self.chkOnlyForCurrentOrg.isChecked()
        self.yesToAll = False
        self.noToAll = False
        self.saveAll = False

        if self.currentOrgOnly:
            self.currentOrgInfisCode = forceString(
                QtGui.qApp.db.translate('Organisation', 'id', QtGui.qApp.currentOrgId(), 'infisCode'))
            self.log.append(u'загрузка тарифов только с кодом `%s`' % self.currentOrgInfisCode)

        self.chkOnlyForCurrentOrg.setEnabled(False)
        self.preProcess(dbfCustomize)
        self.process(dbfTariff, self.processTariff)
        self.ok = not self.abort

        dbfTariff.close()
        self.chkOnlyForCurrentOrg.setEnabled(True)
        self.log.append(u'добавлено: %d; изменено: %d' % (self.nAdded, self.nUpdated))
        self.log.append(u'дополнено: %d' % self.nAppended)
        self.log.append(u'пропущено: %d; обработано: %d' % (self.nSkipped, self.nProcessed))
        self.log.append(u'готово')


    def process(self, dbf, step):
        for row in dbf:
            QtGui.qApp.processEvents()
            if self.abort:
                self.reject()
                return
            self.progressBar.setValue(self.progressBar.value()+1)
            try:
                step(row)
            except:
                QtGui.qApp.logCurrentException()
                raise

    def preProcess(self, dbf):
        """
        Формирует словарь вида
        {organisationCode:
            { serviceCode:
                [тип тарифа (Contract_Tariff.tariffType),
                федеральный код из rbMedicalAidUnit для заполнения unit.id,
                значение для поля Contract_Tariff.frag1Start,
                allDays,
                флаг округления вычислений из предыдущего пункта]
            }
        }
        allDays - 'если это поле заполнено, то для соответствующей записи таблицы "Contract_Tariff"
                        значение из поля "price" нужно перенести в поле "frag1Sum", а значение в поле
                        "price" вычислить по формуле: price = price / AllDays'

        Словарь используется для настройки тарифов в процессе импорта
        """
        self.customData = {}
        if dbf:
            for record in dbf:
                orgCode = record['MCOD']
                if not orgCode:
                    orgCode = 'all'
                serviceCode = record['KMU']
                tarType = record['TarType']
                unitCode = record['IDSP']
                tar2Days = record['Tar2Days']
                allDays = record['AllDays']
                okr = record['Okr']
                if not orgCode in self.customData:
                    self.customData[orgCode] = {}
                if not serviceCode in self.customData[orgCode]:
                    self.customData[orgCode][serviceCode] = [tarType, unitCode, tar2Days, allDays, okr]

    def processTariff(self,  row):
        orgCode = forceString(row['MCOD'].strip())
        serviceCode = forceString(row['KMU'].strip())

        if self.currentOrgOnly and (self.currentOrgInfisCode != orgCode):
            self.log.append(u' Услуга, код ИНФИС: "%s", не соответствует текущему ЛПУ.' \
                                    u' Пропускаем.' % serviceCode)
            self.nSkipped += 1
            return

        price = forceDouble(row['S']) # float
        federalPrice = forceDouble(row['PSZP'])

        if row.deleted:
            self.log.append(u'<b><font color=blue>ВНИМАНИЕ:</b>'
                u'Услуга, код ИНФИС: "%s", помечена на удаление. Пропускаем.' % serviceCode)
            self.nSkipped += 1
            return

        serviceId = self.findServiceByInfisCode(serviceCode)

        if not serviceId:
            self.log.append(u'<b><font color=orange>ОШИБКА:</b>'
                u' Услуга, код ИНФИС: "%s", не найдена' % serviceCode)
            self.nSkipped += 1
            return

        tariffType = 2 # тарифицируем услуги
        uet = 0

        if serviceCode[:3] in ('097', '099', '197', '199'):
            #Мероприятие по количеству и тарифу койки
            tariffType = 6
        elif serviceCode[:3] in ('009', '109'):
            #Мероприятие по количеству
            tariffType = 5
            uet = round(price/self.edtUetValue.value(), 2) #math.floor(price/self.edtUetValue.value()*100)/100
        elif serviceCode[:3] in ('001', '101'):
            #Посещение
            tariffType = 0

        amount = 1 if tariffType == 0 else 0

        self.log.append(u'Услуга: "%s". Тариф: <b>'
                u'<font color=green>"%.2f"</b>,'
                u' ует <b><font color=green>"%.2f"</b>,'
                u' федеральная часть <b><font color=green>"%.2f"</b>' % (serviceCode, price, uet,  federalPrice))
        if (orgCode in self.customData and serviceCode in self.customData[orgCode]):
            custom = self.customData[orgCode][serviceCode]
            #tariffType = custom[0]
        elif self.customData and serviceCode in self.customData['all']:
            custom = self.customData['all'][serviceCode]
            #tariffType = custom[0]
        else:
            custom = []
        self.addOrUpdateTariff(tariffType, serviceCode, serviceId,  0,  '',  amount, price,  0, uet, federalPrice, custom)
        self.nProcessed += 1


    def addOrUpdateTariff(self, tariffType, serviceCode, serviceId, sex, age, amount, price, limit, uet, federalPrice, custom=None):
        if not custom:
            custom = []
        key = (tariffType, serviceId, sex, age)
        tariffIndexList = self.tariffDict.get(key, None)

        if tariffIndexList:
            self.log.append(u'Найден совпадающий тариф.')
            if self.dupSkip:
                self.log.append(u'Пропускаем.')
                self.nSkipped += len(tariffIndexList)
                return
            for i in tariffIndexList:
                tariff = self.tariffList[i]
                oldAmount = forceDouble(tariff.value('amount'))
                oldPrice  = forceDouble(tariff.value('price'))
                oldLimit  = forceDouble(tariff.value('limit'))
                oldUet = forceDouble(tariff.value('uet'))
                oldFederalPrice = forceDouble(tariff.value('federalPrice'))

                if abs(oldPrice-price)<0.001 and abs(oldLimit-limit)<0.001 \
                        and abs(oldAmount-amount)<0.001 and abs(oldUet-uet)<0.001 \
                        and abs(oldFederalPrice-federalPrice)<0.001:
                    self.log.append(u'Количество, цены и ограничения совпадают, пропускаем.')
                    self.nSkipped += 1
                    break

                if self.dupUpdate:
                    self.log.append(u'Обновляем. (%.2f на %.2f,  фед. %.2f на %.2f)' % \
                                    (oldPrice, price, oldFederalPrice,  federalPrice))
                    self.updateTariff(tariff, amount, price, limit, uet, federalPrice, custom)
                    self.nUpdated += 1
                elif self.dupAppend:
                    self.log.append(u'Дополняем с текущей даты по новой цене.')
                    self.appendTariff(tariff, amount, price, limit, uet,  federalPrice, custom)
                    self.nAppended += 1
                    break
                else:
                    self.log.append(u'Запрос действий у пользователя.')
                    if not (self.yesToAll or self.noToAll or self.saveAll):
                        answer = QtGui.QMessageBox.question(self, u'Совпадающий тариф',
                                        u'Услуга "%s", пол "%s", возраст "%s"\n'
                                        u'Количество: %.2f, новое количество %.2f\n'
                                        u'Тариф: %.2f, новый %.2f\n'
                                        u'Фед. тариф: %.2f, новый %.2f\n'
                                        u'Предел: %d, новый предел %d\n'
                                        u'Да - Обновить, Нет - Пропустить, Сохранить - Дополнить' % \
                                            (serviceCode, sex, age if age else '-',
                                                oldAmount, amount, oldPrice, price, oldFederalPrice,  federalPrice,  oldLimit, limit),
                                        QtGui.QMessageBox.No|QtGui.QMessageBox.Yes|QtGui.QMessageBox.Save|
                                        QtGui.QMessageBox.NoToAll|QtGui.QMessageBox.YesToAll|
                                        QtGui.QMessageBox.SaveAll|QtGui.QMessageBox.Abort,
                                        QtGui.QMessageBox.No)

                        if answer == QtGui.QMessageBox.Abort:
                            self.log.append(u'Прервано пользователем.')
                            self.abort = True
                            return

                        strChoise = u'пропустить'

                        if (answer == QtGui.QMessageBox.Yes or
                            answer == QtGui.QMessageBox.YesToAll):
                            strChoise = u'обновить'
                            self.updateTariff(tariff, amount, price, limit, uet, federalPrice, custom)
                            self.nUpdated += 1
                            self.yesToAll = (answer == QtGui.QMessageBox.YesToAll)
                        elif (answer == QtGui.QMessageBox.Save or
                                answer == QtGui.QMessageBox.SaveAll or self.saveAll):
                            strChoise = u'дополнить'
                            self.appendTariff(tariff, amount, price, limit,  uet, federalPrice, custom)
                            self.nAppended += 1
                            self.saveAll = (answer == QtGui.QMessageBox.SaveAll)
                        else:
                            self.nSkipped += 1
                            self.noToAll = (answer == QtGui.QMessageBox.NoToAll)

                        self.log.append(u'Выбор пользователя %s' % strChoise)
                    else:
                        if self.yesToAll:
                            self.updateTariff(tariff, amount, price, limit, uet, custom)
                            self.nUpdated += 1
                        elif self.saveAll:
                            self.appendTariff(tariff, amount, price, limit, uet, custom)
                            self.nAppended += 1
                        else:
                            self.nSkipped += 1
        else:
            self.log.append(u'Добавляем тариф.')
            self.nAdded += 1
            self.addTariff(tariffType, serviceId, sex, age, amount, price, limit, uet, federalPrice, custom)


    def addTariff(self, tariffType, serviceId, sex, age, amount, price, limit, uet, federalPrice, custom):
        if not custom:
            record = self.tblContract_Tariff.newRecord()
            record.setValue('master_id',  toVariant(self.contractId))
            record.setValue('tariffType', toVariant(tariffType))
            record.setValue('service_id', toVariant(serviceId))
            record.setValue('sex', toVariant(sex))
            record.setValue('age', toVariant(age))
            record.setValue('unit_id',
                toVariant(self.unitVisitId if tariffType == 0 else self.unitServiceId))
            record.setValue('amount',  toVariant(amount))
            record.setValue('price', toVariant(price))
            record.setValue('limit',  toVariant(limit))
            record.setValue('uet',  toVariant(uet))
            record.setValue('federalPrice', toVariant(federalPrice))
            i = len(self.tariffList)
            self.tariffList.append(record)
            key = (tariffType, serviceId, sex, age)
            tariffIndexList = self.tariffDict.setdefault(key, [])
            tariffIndexList.append(i)
        else:
            customTariffType, unitCode, tar2Days, allDays, okr = custom
            unitId = QtGui.qApp.db.translate('rbMedicalAidUnit', 'federalCode', unitCode, 'id')
            allDays = forceDouble(allDays)
            okr = forceBool(okr)
            if allDays:
                customPrice = decimal.Decimal(price)/decimal.Decimal(allDays)
                if okr:
                    customPrice = customPrice.quantize(decimal.Decimal('0.01'))
                customPrice = forceDouble(customPrice)
            else:
                customPrice = price
            record = self.tblContract_Tariff.newRecord()
            record.setValue('master_id', toVariant(self.contractId))
            record.setValue('tariffType', toVariant(customTariffType))
            record.setValue('service_id', toVariant(serviceId))
            record.setValue('sex', toVariant(sex))
            record.setValue('age', toVariant(age))
            record.setValue('unit_id', toVariant(unitId))
            record.setValue('amount', toVariant(amount))
            record.setValue('price', toVariant(customPrice))
            if allDays:
                record.setValue('frag1Sum', toVariant(price))
                if self.secondTariffUnitId == forceInt(unitId):
                    frag2Start = forceInt(ceil(allDays * 2))
                    record.setValue('frag2Start', toVariant(frag2Start))
                    record.setValue('frag2Sum', toVariant(customPrice * frag2Start))
                    record.setValue('frag2Price', toVariant(customPrice))
            record.setValue('frag1Start', toVariant(tar2Days))
            record.setValue('limit', toVariant(limit))
            record.setValue('uet', toVariant(uet))
            record.setValue('federalPrice', toVariant(federalPrice))
            i = len(self.tariffList)
            self.tariffList.append(record)
            key = (tariffType, serviceId, sex, age)
            tariffIndexList = self.tariffDict.setdefault(key, [])
            tariffIndexList.append(i)


    def updateTariff(self, tariff, amount, price, limit, uet, federalPrice, custom):
        if not custom:
            tariff.setValue('amount',  toVariant(amount))
            tariff.setValue('price', toVariant(price))
            tariff.setValue('limit', toVariant(limit))
            tariff.setValue('uet', toVariant(uet))
            tariff.setValue('federalPrice', toVariant(federalPrice))
        else:
            customTariffType, unitCode, tar2Days, allDays, okr = custom
            unitId = QtGui.qApp.db.translate('rbMedicalAidUnit', 'federalCode', unitCode, 'id')
            allDays = forceDouble(allDays)
            okr = forceBool(okr)
            if allDays:
                customPrice = decimal.Decimal(price)/decimal.Decimal(allDays)
                if okr:
                    customPrice = customPrice.quantize(decimal.Decimal('0.01'))
                customPrice = forceDouble(customPrice)
            else:
                customPrice = price
            tariff.setValue('amount', toVariant(amount))
            tariff.setValue('price', toVariant(customPrice))
            tariff.setValue('limit', toVariant(limit))
            tariff.setValue('uet', toVariant(uet))
            tariff.setValue('federalPrice', toVariant(federalPrice))
            if allDays:
                tariff.setValue('frag1Sum', toVariant(price))
                if self.secondTariffUnitId == forceInt(unitId):
                    frag2Start = forceInt(ceil(allDays * 2))
                    tariff.setValue('frag2Start', toVariant(frag2Start))
                    tariff.setValue('frag2Sum', toVariant(customPrice * frag2Start))
                    tariff.setValue('frag2Price', toVariant(customPrice))
            tariff.setValue('frag1Start', toVariant(tar2Days))
            tariff.setValue('unit_id', toVariant(unitId))
            tariff.setValue('tariffType', toVariant(customTariffType))


    def appendTariff(self, tariff, amount, price, limit, uet, federalPrice, custom):
        endDate = forceDate(tariff.value('endDate'))
        if not custom:
            record = self.tblContract_Tariff.newRecord()
            copyFields(record, tariff)
            date = firstMonthDay(QDate.currentDate())
            record.setValue('begDate', date)

            if endDate.isValid() and endDate < date:
                record.setNull('endDate')
            else:
                tariff.setValue('endDate', date.addDays(-1))

            record.setValue('amount',  toVariant(amount))
            record.setValue('price', toVariant(price))
            record.setValue('federalPrice', toVariant(federalPrice))
            record.setValue('limit', toVariant(limit))
            record.setValue('uet',  toVariant(uet))

            i = len(self.tariffList)
            self.tariffList.append(record)
            key = (forceInt(record.value('tariffType')), forceRef(record.value('service_id')),
                        forceInt(record.value('sex')), forceString(record.value('age')))
            tariffIndexList = self.tariffDict.setdefault(key, [])
            tariffIndexList.append(i)
        else:
            customTariffType, unitCode, tar2Days, allDays, okr = custom
            unitId = QtGui.qApp.db.translate('rbMedicalAidUnit', 'federalCode', unitCode, 'id')
            allDays = forceDouble(allDays)
            okr = forceBool(okr)
            if allDays:
                customPrice = decimal.Decimal(price)/decimal.Decimal(allDays)
                if okr:
                    customPrice = customPrice.quantize(decimal.Decimal('0.01'))
                customPrice = forceDouble(customPrice)
            else:
                customPrice = price

            record = self.tblContract_Tariff.newRecord()
            copyFields(record, tariff)
            date = firstMonthDay(QDate.currentDate())
            record.setValue('begDate', date)
            if endDate.isValid() and endDate < date:
                record.setNull('endDate')
            else:
                tariff.setValue('endDate', date.addDays(-1))

            record.setValue('amount', toVariant(amount))
            record.setValue('price', toVariant(customPrice))
            record.setValue('federalPrice', toVariant(federalPrice))
            record.setValue('limit', toVariant(limit))
            record.setValue('uet', toVariant(uet))
            if allDays:
                record.setValue('frag1Sum', toVariant(price))
                if self.secondTariffUnitId == forceInt(unitId):
                    frag2Start = forceInt(ceil(allDays * 2))
                    record.setValue('frag2Start', toVariant(frag2Start))
                    record.setValue('frag2Sum', toVariant(customPrice * frag2Start))
                    record.setValue('frag2Price', toVariant(customPrice))
            record.setValue('frag1Start', toVariant(tar2Days))
            record.setValue('unit_id', toVariant(unitId))
            record.setValue('tariffType', toVariant(customTariffType))

            i = len(self.tariffList)
            self.tariffList.append(record)
            key = (forceInt(record.value('tariffType')), forceRef(record.value('service_id')),
                        forceInt(record.value('sex')), forceString(record.value('age')))
            tariffIndexList = self.tariffDict.setdefault(key, [])
            tariffIndexList.append(i)


    serviceCache = {}

    def findServiceByInfisCode(self, code):
        result = self.serviceCache.get(code)

        if not result:
            result = forceRef(QtGui.qApp.db.translate('rbService', 'infis', code, 'id'))

            if result:
                self.serviceCache[code] = result

        return result


    def updateLabel(self):
        try:
            dbfFileName = forceStringEx(self.edtFileName.text())
            dbfTariff = dbf.Dbf(dbfFileName, readOnly=True, encoding='cp866')
            self.labelNum.setText(u'всего записей в источнике: '+str(len(dbfTariff)))
        except:
            pass


    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '' :
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)
            self.updateLabel()

    @QtCore.pyqtSlot()
    def on_btnCustomSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtCustomFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '' :
            self.edtCustomFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.updateLabel()

    @QtCore.pyqtSlot()
    def on_btnCustomView_clicked(self):
        fname=unicode(forceStringEx(self.edtCustomFileName.text()))
        if fname:
            CDbfViewDialog(self, fileName=fname).exec_()
