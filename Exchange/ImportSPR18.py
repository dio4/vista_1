#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime

from PyQt4 import QtCore, QtGui

from Exchange.Cimport import CDBFimport
from Exchange.Utils import dbfCheckNames
from Exchange.Ui_ImportSPR18 import Ui_Dialog
from library.constants import dateLeftInfinity, dateRightInfinity

from library.dbfpy.dbf import Dbf
from library.exception import CException
from library.Utils import forceDate, forceString, forceStringEx, toVariant, getVal

from RefBooks import synchronizeActionTypes_sql
from RefBooks import synchronizeActionTypes_create_sql


# Импорт справочника услуг, КСГ и HTG для Краснодарского Края

def ImportSPR18(widget):
    dlg = CImportSPR18(widget)
    dlg.exec_()


def rowConv(row, columnName):
    return row.asDict()[columnName]  # .decode(encoding)


class CImportSPR18(CDBFimport, QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        super(CImportSPR18, self).__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.newServices = []
        self.edtFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportSPR18FileName', '')))

    def openDBF(self):
        dbf = None

        fileName = forceStringEx(self.edtFileName.text())
        result = os.path.isfile(fileName)
        if result:
            dbf = Dbf(fileName, readOnly=True, encoding='cp866')
            fieldsList = ['CODE', 'NAME', 'NAME_LONG', 'KOLICH', 'ED', 'UET',
                          'CODE_BASE', 'DATN', 'DATO', 'NOT_OMS', 'VISIT', 'VAR40']
            if not dbfCheckNames(dbf, fieldsList):
                raise CException(u'файл %s\nне содержит одного из полей:\n%s' % (fileName, ', '.join(fieldsList)))
            self.labelNum.setText(u'всего записей в источнике: ' + str(dbf.recordCount))
        return dbf

    @staticmethod
    def fillMESRecord(db, table, record, code=None, name=None, descr=None, begDate=None, endDate=None):
        if code is not None:    record.setValue('code', toVariant(code))
        if name is not None:    record.setValue('name', toVariant(name))
        if descr is not None:   record.setValue('descr', toVariant(descr))
        if begDate is not None: record.setValue('begDate', toVariant(begDate))
        if endDate is not None: record.setValue('endDate', toVariant(endDate))
        db.insertOrUpdate(table, record)

    @staticmethod
    def fillHTGRecord(db, table, record, code=None, name=None, begDate=None, endDate=None):
        if code is not None:    record.setValue('code', toVariant(code))
        if name is not None:    record.setValue('name', toVariant(name))
        if begDate is not None: record.setValue('begDate', toVariant(begDate))
        if endDate is not None: record.setValue('endDate', toVariant(endDate))
        db.insertOrUpdate(table, record)

    @staticmethod
    def fillMrbServiceRecord(db, table, record, code=None, name=None, begDate=None, endDate=None):
        if code is not None:    record.setValue('code', toVariant(code))
        if name is not None:    record.setValue('name', toVariant(name))
        if begDate is not None: record.setValue('begDate', toVariant(begDate))
        if endDate is not None: record.setValue('endDate', toVariant(endDate))
        db.insertOrUpdate(table, record)

    @staticmethod
    def fillRbServiceRecord(db, table, record, code=None, name=None, begDate=None, endDate=None, uet=None, visitType=None):
        if name is not None:
            record.setValue('name', toVariant(name))
        if code is not None:
            record.setValue('infis', toVariant(code))
            record.setValue('code', toVariant(code))
        if begDate is not None:
            record.setValue('begDate', toVariant(begDate))
        if endDate is not None:
            record.setValue('endDate', toVariant(endDate))
        if uet:
            record.setValue('adultUetDoctor', toVariant(uet))
            record.setValue('childUetDoctor', toVariant(uet))
        if visitType is not None:
            record.setValue('visitType_id', toVariant(db.translate('rbVisitType', 'code', visitType, 'id')))
        record.setValue('eisLegacy', QtCore.QVariant(0))
        record.setValue('nomenclatureLegacy', QtCore.QVariant(0))
        record.setValue('license', QtCore.QVariant(0))
        db.insertOrUpdate(table, record)

    @staticmethod
    def fillActionTypeRecord(db, table, record, code=None, name=None, nom_id=None, classProp=None, insert=None):
        if code is not None:
            record.setValue('code', toVariant(code))
        if name is not None:
            record.setValue('name', toVariant(name))
        if classProp is not None:
            record.setValue('class', QtCore.QVariant(classProp))
        record.setValue('nomenclativeService_id', toVariant(nom_id))
        record.setValue('propertyNormVisible', QtCore.QVariant(name))
        record.setValue('title', QtCore.QVariant(name))
        if insert:
            record.setValue('sex', QtCore.QVariant(0))
            record.setValue('amountEvaluation', QtCore.QVariant(0))
            record.setValue('isPreferable', QtCore.QVariant(1))
            record.setValue('isPrinted', QtCore.QVariant(0))
            record.setValue('showInForm', QtCore.QVariant(1))
            record.setValue('propertyAssignedVisible', QtCore.QVariant(0))
            record.setValue('propertyUnitVisible', QtCore.QVariant(0))
            record.setValue('propertyEvaluationVisible', QtCore.QVariant(0))
            record.setValue('amount', QtCore.QVariant(1))

        db.insertOrUpdate(table, record)


    @staticmethod
    def fillActionType_ServiceRecord(db, table, record, actionType_id=None, service_id=None):
        if actionType_id is not None:
            record.setValue('master_id', toVariant(actionType_id))
        if service_id is not None:
            record.setValue('service_id', toVariant(service_id))
        record.setValue('idx', QtCore.QVariant(0))
        db.insertOrUpdate(table, record)

    def processMESRow(self, row):
        db = QtGui.qApp.db
        tblMES = db.table('mes.MES')

        begDate = forceDate(row['DATN'])
        if not begDate: begDate = dateLeftInfinity  # Сейчас мы считаем, что так быть не может.
        endDate = forceDate(row['DATO'])
        code = row['CODE']
        descr = row['NAME_LONG']
        name = row['NAME']

        if endDate:  # Запись с проставленной датой окончания действия. Сейчас мы считаем, что такая измениться не может.
            MESList = db.getRecordList(tblMES,
                                       cols=['id', 'code'],
                                       where=db.joinAnd([tblMES['code'].eq(code),
                                                         tblMES['deleted'].eq(0),
                                                         tblMES['begDate'].eq(begDate),
                                                         tblMES['endDate'].eq(endDate)]))

            if len(
                    MESList) > 1:  # Несколько идентичных записей. Вставлять ничего не надо, но надо предупредить пользователя, что у него база в плохом состоянии
                self.addDuplicateAlertToLog(u'КСГ (mes.MES)', code, [forceString(mes.value('id')) for mes in MESList])
            elif len(MESList) == 1:
                return  # Запись уже есть. Вставлять не надо.
            else:  # Записи нет. Возможно, есть запись с неограниченным сроком действия (endDate == dateRightInfinity)
                MESList = db.getRecordList(tblMES,
                                           cols=['id', 'code', 'descr', 'begDate', 'endDate'],
                                           where=db.joinAnd([tblMES['code'].eq(code),
                                                             tblMES['deleted'].eq(0),
                                                             tblMES['begDate'].eq(begDate),
                                                             tblMES['endDate'].eq(dateRightInfinity)]))

                if len(
                        MESList) > 1:  # Несколько идентичных записей. Обновляем все, но надо предупредить пользователя, что у него база в плохом состоянии
                    self.addDuplicateAlertToLog(u'КСГ (mes.MES)', code,
                                                [forceString(mes.value('id')) for mes in MESList])
                    for record in MESList: self.fillMESRecord(db, tblMES, record,
                                                              endDate=endDate)  # Обновить требуется только дату окончания
                elif len(MESList) == 1:
                    self.fillMESRecord(db, tblMES, MESList[0], endDate=endDate)  # Обновляем единственную запись. Всё ок
                else:
                    self.fillMESRecord(db, tblMES, tblMES.newRecord(), code, name, descr, begDate,
                                       endDate)  # Ничего не нашли. Надо вставить запись

        else:  # Запись с непроставленной датой окончания. Если такая у нас уже есть — не делаем ничего. Иначе вставляем новую.
            endDate = dateRightInfinity

            MESList = db.getRecordList(tblMES,
                                       cols=['id', 'code'],
                                       where=db.joinAnd([tblMES['code'].eq(code),
                                                         tblMES['deleted'].eq(0),
                                                         tblMES['begDate'].eq(begDate),
                                                         tblMES['endDate'].eq(endDate)]))
            if len(
                    MESList) > 1:  # Несколько идентичных записей. Вставлять ничего не надо, но надо предупредить пользователя, что у него база в плохом состоянии
                self.addDuplicateAlertToLog(u'КСГ (mes.MES)', code, [forceString(mes.value('id')) for mes in MESList])
            elif len(MESList) == 1:
                return  # Запись уже есть. Вставлять не надо.
            else:
                self.fillMESRecord(db, tblMES, tblMES.newRecord(), code, name, descr, begDate,
                                   endDate)  # Ничего не нашли. Надо вставить запись

    def processHTGRow(self, row):
        db = QtGui.qApp.db
        tblHTG = db.table('mes.mrbHighTechMedicalGroups')

        begDate = forceDate(row['DATN'])
        if not begDate: begDate = dateLeftInfinity  # Сейчас мы считаем, что так быть не может.
        endDate = forceDate(row['DATO'])
        code = row['CODE']
        name = row['NAME']

        if endDate:  # Запись с проставленной датой окончания действия. Сейчас мы считаем, что такая измениться не может.
            HTGList = db.getRecordList(tblHTG,
                                       cols=['id', 'code'],
                                       where=db.joinAnd([tblHTG['code'].eq(code),
                                                         tblHTG['deleted'].eq(0),
                                                         tblHTG['begDate'].eq(begDate),
                                                         tblHTG['endDate'].eq(endDate)]))
            if len(
                    HTGList) > 1:  # Несколько идентичных записей. Вставлять ничего не надо, но надо предупредить пользователя, что у него база в плохом состоянии
                self.addDuplicateAlertToLog(u'HTG (mes.mrbHighTechMedicalGroups)', code,
                                            [forceString(htg.value('id')) for htg in HTGList])
            elif len(HTGList) == 1:
                return  # Запись уже есть. Вставлять не надо.
            else:  # Записи нет. Возможно, есть запись с неограниченным сроком действия (endDate == dateRightInfinity)
                HTGList = db.getRecordList(tblHTG,
                                           cols=['id', 'code'],
                                           where=db.joinAnd([tblHTG['code'].eq(code),
                                                             tblHTG['deleted'].eq(0),
                                                             tblHTG['begDate'].eq(begDate),
                                                             tblHTG['endDate'].eq(dateRightInfinity)]))
                if len(
                        HTGList) > 1:  # Несколько идентичных записей. Обновляем все, но надо предупредить пользователя, что у него база в плохом состоянии
                    self.addDuplicateAlertToLog(u'HTG (mes.mrbHighTechMedicalGroups)', code,
                                                [forceString(htg.value('id')) for htg in HTGList])
                    for record in HTGList: self.fillHTGRecord(db, tblHTG, record,
                                                              endDate=endDate)  # Обновить требуется только дату окончания
                elif len(HTGList) == 1:
                    self.fillHTGRecord(db, tblHTG, HTGList[0], endDate=endDate)  # Обновляем единственную запись. Всё ок
                else:
                    self.fillHTGRecord(db, tblHTG, tblHTG.newRecord(), code, name, begDate,
                                       endDate)  # Ничего не нашли. Надо вставить запись

        else:  # Запись с непроставленной датой окончания. Если такая у нас уже есть — не делаем ничего. Иначе вставляем новую.
            endDate = dateRightInfinity
            HTGList = db.getRecordList(tblHTG,
                                       cols=['id', 'code'],
                                       where=db.joinAnd([tblHTG['code'].eq(code),
                                                         tblHTG['deleted'].eq(0),
                                                         tblHTG['begDate'].eq(begDate),
                                                         tblHTG['endDate'].eq(endDate)]))
            if len(
                    HTGList) > 1:  # Несколько идентичных записей. Вставлять ничего не надо, но надо предупредить пользователя, что у него база в плохом состоянии
                self.addDuplicateAlertToLog(u'HTG (mes.mrbHighTechMedicalGroups)', code,
                                            [forceString(htg.value('id')) for htg in HTGList])
            elif len(HTGList) == 1:
                return  # Запись уже есть. Вставлять не надо.
            else:
                self.fillHTGRecord(db, tblHTG, tblHTG.newRecord(), code, name, begDate,
                                   endDate)  # Ничего не нашли. Надо вставить запись

    def processMrbServiceRow(self, row):
        db = QtGui.qApp.db
        tblMRBService = db.table('mes.mrbService')

        begDate = forceDate(row['DATN'])
        if not begDate: begDate = dateLeftInfinity  # Сейчас мы считаем, что так быть не может.
        endDate = forceDate(row['DATO'])
        code = row['CODE']
        name = row['NAME']

        if endDate:  # Запись с проставленной датой окончания действия. Сейчас мы считаем, что такая измениться не может.
            mrbServicesList = db.getRecordList(tblMRBService,
                                               cols=['id', 'code'],
                                               where=db.joinAnd([tblMRBService['code'].eq(code),
                                                                 tblMRBService['deleted'].eq(0),
                                                                 tblMRBService['begDate'].eq(begDate),
                                                                 tblMRBService['endDate'].eq(endDate)
                                                                 ]))
            # pirozhok: вставлять в mrbService не нужно, а также не следует вставлять в rbService во всех неблагоприятных случаях
            if len(
                    mrbServicesList) > 1:  # Несколько идентичных записей. Вставлять ничего не надо, но надо предупредить пользователя, что у него база в плохом состоянии
                self.addDuplicateAlertToLog(u'Услуга (mes.mrbService)', code,
                                            [forceString(service.value('id')) for service in mrbServicesList])
                return
            elif len(mrbServicesList) == 1:
                return  # Запись уже есть. Вставлять не надо.
            else:  # Записи нет. Возможно, есть запись с неограниченным сроком действия (endDate == dateRightInfinity)
                mrbServicesList = db.getRecordList(tblMRBService,
                                                   cols=['id', 'code'],
                                                   where=db.joinAnd([tblMRBService['code'].eq(code),
                                                                     tblMRBService['deleted'].eq(0),
                                                                     tblMRBService['begDate'].eq(begDate),
                                                                     tblMRBService['endDate'].eq(dateRightInfinity)]))
                if len(
                        mrbServicesList) > 1:  # Несколько идентичных записей. Обновляем все, но надо предупредить пользователя, что у него база в плохом состоянии
                    self.addDuplicateAlertToLog(u'Услуга (mes.mrbService)', code,
                                                [forceString(service.value('id')) for service in mrbServicesList])
                    for record in mrbServicesList: self.fillMrbServiceRecord(db, tblMRBService, record,
                                                                             endDate=endDate)  # Обновить требуется только дату окончания
                elif len(mrbServicesList) == 1:
                    self.fillMrbServiceRecord(db, tblMRBService, mrbServicesList[0],
                                              endDate=endDate)  # Обновляем единственную запись. Всё ок
                else:
                    self.fillMrbServiceRecord(db, tblMRBService, tblMRBService.newRecord(), code, name, begDate,
                                              endDate)  # Ничего не нашли. Надо вставить запись

        else:  # Запись с непроставленной датой окончания. Если такая у нас уже есть — не делаем ничего. Иначе вставляем новую.
            endDate = dateRightInfinity
            mrbServicesList = db.getRecordList(tblMRBService,
                                               cols=['id', 'code'],
                                               where=db.joinAnd([tblMRBService['code'].eq(code),
                                                                 tblMRBService['deleted'].eq(0),
                                                                 tblMRBService['begDate'].eq(begDate),
                                                                 tblMRBService['endDate'].eq(endDate)
                                                                 ]))

            if len(
                    mrbServicesList) > 1:  # Несколько идентичных записей. Вставлять ничего не надо, но надо предупредить пользователя, что у него база в плохом состоянии
                self.addDuplicateAlertToLog(u'Услуга (mes.mrbService)', code,
                                            [forceString(service.value('id')) for service in mrbServicesList])
            elif len(mrbServicesList) == 1:
                return  # Запись уже есть. Вставлять не надо.
            else:
                self.fillMrbServiceRecord(db, tblMRBService, tblMRBService.newRecord(), code, name, begDate, endDate)

    def processRbServiceRow(self, row):
        db = QtGui.qApp.db
        tblRbService = db.table('rbService')

        begDate = forceDate(row['DATN'])
        if not begDate: begDate = dateLeftInfinity  # Сейчас мы считаем, что такого быть не может
        endDate = forceDate(row['DATO'])
        code = row['CODE']
        name = row['NAME']
        uet = row['UET']
        visitType = row['VISIT']
        date_end=""
        date_today=""
        if not endDate.isNull():
            date_end = datetime.datetime.strptime(str(endDate.toString('yyyyMMdd')), "%Y%m%d").date()
            date_today = datetime.datetime.strptime(str(datetime.datetime.now().strftime("%Y%m%d")), "%Y%m%d").date()

        if endDate.isNull() or date_end > date_today:
            rbServicesList = db.getRecordList(tblRbService,
                                              cols='*',
                                              where=db.joinAnd([
                                                  tblRbService['code'].eq(code)
                                              ]))
            endDate = dateRightInfinity
            if len(rbServicesList) > 1:  # if more than one entry, just give a warning
               self.addDuplicateAlertToLog(u'Услуга (rbService)', code,
                                            [forceString(service.value('id')) for service in rbServicesList])
            elif len(rbServicesList) == 1:  # if one entry, update it
                self.fillRbServiceRecord(db, tblRbService, rbServicesList[0], code, name, begDate, endDate, uet, visitType) # обновляем только visitType
            else:  # insert it
                self.fillRbServiceRecord(db, tblRbService, tblRbService.newRecord(), code, name, begDate, endDate, uet, visitType)


    def processActionTypeRow(self, row):
        db = QtGui.qApp.db
        tblActiontType = db.table('ActionType')
        tblActionType_Service = db.table('ActionType_Service')
        code = row['CODE']
        name = row['NAME']

        ActionTypeList = db.getRecordList(tblActiontType, cols='*',
                                          where=db.joinAnd([
                                              tblActiontType['code'].eq(code),
                                              tblActiontType['deleted'].eq(0)
                                          ]))

        tblRbService = db.table('rbService')
        nomen_id = db.getRecordEx(tblRbService,
                                  cols='id',
                                  where=tblRbService['code'].eq(code))

        nom_id = forceStringEx(nomen_id.value('id').toString())

        if len(ActionTypeList) > 1:  # if more than one entry, just give a warning
            self.addDuplicateAlertToLog(u'Тип действие (ActionType)', code,
                                        [forceString(act_type.value('id')) for act_type in ActionTypeList])
        elif len(ActionTypeList) == 1:  # if one entry, update it
            self.fillActionTypeRecord(db, tblActiontType, ActionTypeList[0], code, name, nom_id, insert=False)
        else:  # insert it
            self.fillActionTypeRecord(db, tblActiontType, tblActiontType.newRecord(), code, name, nom_id, 3, insert=True)
            acttype_id = db.getRecordEx(tblActiontType,
                                      cols='id',
                                      where = db.joinAnd([tblActiontType['code'].eq(code),
                                                          tblActiontType['deleted'].eq(0)])
                                      )
            actionType_id = forceStringEx(acttype_id.value('id').toString())
            tblActionType_ServiceList = db.getRecordList(tblActionType_Service, cols='*', where=tblActionType_Service['service_id'].eq(nom_id))
            if len(tblActionType_ServiceList) > 0:
                for i in range(0, len(tblActionType_ServiceList)):
                    db.deleteRecord(tblActionType_Service, tblActionType_Service['service_id'].eq(nom_id))

            self.fillActionType_ServiceRecord(db, tblActionType_Service, tblActionType_Service.newRecord(), actionType_id, nom_id)



    def processNewActionTypes(self):
        return  # TODO:skkachaev: Адок старинный какой-то. Осмыслить и переписать. Утверждается, что сейчас (23.03.2016) не работает
        db = QtGui.qApp.db
        error = self.runScript(synchronizeActionTypes_create_sql.COMMAND.split('\n'))
        if not error:
            db.query("""
                              INSERT IGNORE INTO tmpService2ActionType(code, name, parentCode, `level`, `class`)
                              SELECT  rbService.code AS code,
                                      rbService.name AS name,
                                      NULL AS `parentCode`,
                                      0 AS `level`,
                                      rbServiceType.`class` AS `class`
                              FROM rbService
                              LEFT JOIN rbServiceType ON rbServiceType.section = LEFT(rbService.code, 1) AND rbServiceType.code = SUBSTR(rbService.code FROM 2 FOR 2)
                              WHERE rbService.nomenclatureLegacy = 1
                              AND rbService.id IN (%s)
                            """ % ', '.join([str(id) for id in self.newServices]))
            db.query("""
                              INSERT IGNORE INTO tmpService2ActionType(code, name, parentCode, `level`, `class`)
                              SELECT  rbService.code AS code,
                                      rbService.name AS name,
                                      '-' AS `parentCode`,
                                      2 AS `level`,
                                      3 AS `class`
                              FROM rbService
                              WHERE rbService.nomenclatureLegacy = 0
                              AND rbService.id IN (%s)
                            """ % ', '.join([str(id) for id in self.newServices]))
            error = self.runScript(synchronizeActionTypes_sql.COMMAND.split('\n'), {'person_id': QtGui.qApp.userId,
                                                                                    'updateNames': 1,
                                                                                    'compareDeleted': 0})
        if error != None:
            QtGui.QMessageBox.warning(self, u'Импорт услуг',
                                      u'Ошибка при импорте услуг:\n%s.' % error.text())
            self.log.append(unicode(error.text()))

    def startImport(self):
        dbf = self.openDBF()
        nprocessed = 0
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(dbf.recordCount)

        for row in dbf:
            self.progressBar.step()
            QtGui.qApp.processEvents()

            if self.abort:
                self.log.append(u'Прервано пользователем')
                return

            code = row['CODE']
            try:
                if code.startswith('G'):
                    self.processMESRow(row)
                elif code.startswith('V'):
                    self.processHTGRow(row)
                if code and code[0].upper() not in ('K', 'S'):
                    self.processMrbServiceRow(row)
                    self.processRbServiceRow(row)
                if code[0].upper() in ('A', 'B'):
                    self.processActionTypeRow(row)
            except IndexError:
                print "IndexError"


            nprocessed += 1

        self.log.append(u'Обработано %d записей' % nprocessed)
        self.log.append(u'готово')

        QtGui.qApp.preferences.appPrefs['ImportSPR18FileName'] = toVariant(self.edtFileName.text())

    def err2log(self, e):
        if self.log: self.log.append(u'запись ' + str(self.n) + ': ' + e)

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)')
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFileName_textChanged(self, fileName):
        self.btnImport.setEnabled(fileName != '')
