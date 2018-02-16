#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Ui_ImportEISOMS_SMO import Ui_Dialog
from Cimport import *
import updateSMO_sql

u"""Диалог импорта организаций СМО из ЕИС.ОМС"""

def ImportEISOMS_SMO(widget):
    u"""Настройка соединения с ЕИС и запуск диалога"""
    try:
        EIS_db = QtGui.qApp.EIS_db
        if not EIS_db:
            pref=QtGui.qApp.preferences
            props = pref.appPrefs
            EIS_dbDriverName = forceStringEx(getVal(props, 'EIS_driverName', QVariant()))
            EIS_dbServerName = forceStringEx(getVal(props, 'EIS_serverName', QVariant()))
            EIS_dbServerPort = forceInt(getVal(props, 'EIS_serverPort', QVariant()))
            EIS_dbDatabaseName = forceStringEx(getVal(props, 'EIS_databaseName', QVariant()))
            EIS_dbUserName = forceStringEx(getVal(props, 'EIS_userName', QVariant()))
            EIS_dbPassword = forceStringEx(getVal(props, 'EIS_password', QVariant()))
            EIS_db = database.connectDataBase(
                EIS_dbDriverName, EIS_dbServerName, EIS_dbServerPort,
                EIS_dbDatabaseName, EIS_dbUserName, EIS_dbPassword, 'EIS')
            QtGui.qApp.EIS_db = EIS_db
        dlg = CImportEISOMS_SMO(widget, EIS_db)
        dlg.edtFileName.setText(EIS_dbDatabaseName)
        dlg.edtIP.setText(EIS_dbServerName)
        dlg.checkName()
        dlg.exec_()
        QtGui.qApp.EIS_db.close()
        QtGui.qApp.EIS_db = None
    except:
        if QtGui.qApp.EIS_db:
            QtGui.qApp.EIS_db.close()
            QtGui.qApp.EIS_db = None
        QtGui.QMessageBox.information(
            None, u'нет связи', u'не удалось установить соединение с базой ЕИС',
            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)



class CImportEISOMS_SMO(QtGui.QDialog, Ui_Dialog, CImport):
    # Диалог импорта организаций СМО из ЕИС.ОМС
    def __init__(self, parent, EIS_db):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.EIS_db=EIS_db

    def checkName(self):
        self.btnImport.setEnabled(self.edtFileName.text()!='' and self.edtIP.text()!='')

    def oldInfisList(self, record):
        # Список старых инфисов организации
        Id = forceInt(record.value("id"))
        code = forceString(record.value("CODE"))
        result = set()
        qresult = self.EIS_db.query("""SELECT ID_SMO, ID_HISTORY, CODE
                        FROM SMO
                        WHERE ID_SMO != %d AND ID_HISTORY = %d
                        """%(Id, Id))
        while qresult.next():
            record = qresult.record()
            oldcode = forceString(record.value("CODE"))
            if oldcode and oldcode != code:
                result.add(oldcode)
            Id = forceInt(record.value("ID_SMO"))
            qresult = self.EIS_db.query("""SELECT ID_SMO, ID_HISTORY, CODE
                        FROM SMO
                        WHERE ID_SMO <> %d
                        and ID_HISTORY = %d
                        """%(Id, Id))
        result = list(result) # убираем повторы
        return result

    def getNumRecords(self):
        # Общее количество записей в источнике
        num_query = self.EIS_db.query("""SELECT COUNT(*) FROM LPU""")
        num_query.next()
        return forceInt(num_query.record().value(0))

    def startImport(self):
        db = QtGui.qApp.db
        EIS_db = self.EIS_db
        if not EIS_db:
            return
        self.n = 0
        org_found = 0
        org_add = 0
        num = self.getNumRecords()
        self.labelNum.setText(u'всего записей в источнике: '+str(num))
        self.progressBar.setMaximum(num)

        from_stmt = """
        SELECT a.ID_SMO AS id,
            a.ID_HISTORY,
            a.CHANGE_DATE,
            a.SMO_SHORT_NAME,
            a.SMO_LONG_NAME,
            a.BANK,
            a.FILIAL,
            a.INN,
            a.PC,
            a.PC2,
            a.BIK,
            a.OKPO,
            a.ADDRESS,
            a.JUR_ADDRESS,
            a.FIO,
            a.PHONE,
            a.FAX,
            a.EMAIL,
            a.REMARK,
            a.CODE,
            '' as OLD_CODES,
            a.KPP
FROM SMO a
where a.IS_ACTIVE = 1
        """
        from_query = EIS_db.query(from_stmt)
        from_query.setForwardOnly(True)
        db.query("""DROP TABLE if exists tmpSMO""")
        to_stmt = """
        CREATE TABLE if not exists tmpSMO(
  id Integer NOT NULL,
  ID_HISTORY Integer NOT NULL,
  CHANGE_DATE Timestamp NOT NULL,
  SMO_SHORT_NAME Varchar(10) NOT NULL,
  SMO_LONG_NAME Varchar(255) NOT NULL,
  BANK Varchar(80) NOT NULL,
  FILIAL Varchar(80) NOT NULL,
  INN Varchar(10) NOT NULL,
  PC Varchar(20) NOT NULL,
  PC2 Varchar(20) NOT NULL,
  BIK Varchar(10) NOT NULL,
  OKPO Varchar(10) NOT NULL,
  ADDRESS Varchar(80) NOT NULL,
  JUR_ADDRESS Varchar(80) NOT NULL,
  FIO Varchar(80) NOT NULL,
  PHONE Varchar(30) NOT NULL,
  FAX Varchar(30) NOT NULL,
  EMAIL Varchar(30) NOT NULL,
  REMARK Varchar(80) NOT NULL,
  CODE Varchar(5) NOT NULL,
  OLD_CODES Varchar(30) NOT NULL,
  KPP Varchar(9) NOT NULL,
  CONSTRAINT PK_SMO PRIMARY KEY (id)
);
        """
        to_query = db.query(to_stmt)

        while from_query.next():
            QtGui.qApp.processEvents()
            if self.abort:
                break
            self.n += 1
            record = from_query.record()
            record.setValue('OLD_CODES', toVariant(','.join(self.oldInfisList(record)))) # старые инфисы
            self.record = record
            org_found+=1
            org_add+=1  #?????????????????????????????????????????????
            db.insertRecord('tmpSMO',  self.record)
            self.progressBar.step()
            statusText = u'Найдено %d организаций' %org_found
            self.statusLabel.setText(statusText)

        self.log.append(u'Найдено %d организаций' %org_found)
        self.runScript(updateSMO_sql.COMMAND.split('\n'))
        self.log.append(u'готово')
        self.progressBar.setValue(self.n-1)
        db.query('DROP TABLE tmpSMO')


    def err2log(self, e):
        if self.log:
            self.log.append(u'запись '+str(self.n)+': '+e)

