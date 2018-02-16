#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Ui_ImportEISOMS_LPU import Ui_Dialog
from Cimport import *
import updateLPU_sql

u"""Диалог импорта организаций ЛПУ из ЕИС.ОМС"""

def ImportEISOMS_LPU(widget):
    u"""Настройка соединения с ЕИС и запуск диалога"""
    try:
        EIS_db=QtGui.qApp.EIS_db
        if not EIS_db:
            pref=QtGui.qApp.preferences
            props=pref.appPrefs
            EIS_dbDriverName=forceStringEx(getVal(props, 'EIS_driverName', QVariant()))
            EIS_dbServerName=forceStringEx(getVal(props, 'EIS_serverName', QVariant()))
            EIS_dbServerPort=forceInt(getVal(props, 'EIS_serverPort', QVariant()))
            EIS_dbDatabaseName=forceStringEx(getVal(props, 'EIS_databaseName', QVariant()))
            EIS_dbUserName=forceStringEx(getVal(props, 'EIS_userName', QVariant()))
            EIS_dbPassword=forceStringEx(getVal(props, 'EIS_password', QVariant()))
            EIS_db = database.connectDataBase(
                EIS_dbDriverName, EIS_dbServerName, EIS_dbServerPort,
                EIS_dbDatabaseName, EIS_dbUserName, EIS_dbPassword, 'EIS')
            QtGui.qApp.EIS_db=EIS_db
        dlg=CImportEISOMS_LPU(widget, EIS_db)
        dlg.edtFileName.setText(EIS_dbDatabaseName)
        dlg.edtIP.setText(EIS_dbServerName)
        dlg.checkName()
        dlg.exec_()
        QtGui.qApp.EIS_db.close()
        QtGui.qApp.EIS_db=None
    except:
        if QtGui.qApp.EIS_db:
            QtGui.qApp.EIS_db.close()
            QtGui.qApp.EIS_db=None
        QtGui.QMessageBox.information(
            None, u'нет связи', u'не удалось установить соединение с базой ЕИС',
            QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

class CImportEISOMS_LPU(QtGui.QDialog, Ui_Dialog, CImport):
    u"""Диалог импорта организаций ЛПУ из ЕИС.ОМС"""
    def __init__(self, parent, EIS_db):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.EIS_db=EIS_db

    def checkName(self):
        self.btnImport.setEnabled(self.edtFileName.text()!='' and self.edtIP.text()!='')

    def oldInfisList(self, record):
        u"""Список старых инфисов организации"""
        Id = record.value("id").toInt()[0]
        code = unicode(record.value("CODE").toString())
        result = []
        qresult = self.EIS_db.query("""select ID_LPU, ID_HISTORY, CODE
                        from LPU
                        where ID_LPU <> %d
                        and ID_HISTORY = %d
                        """%(Id, Id))
        while qresult.next():
            record = qresult.record()
            oldcode = unicode(record.value("CODE").toString())
            if len(oldcode) and oldcode != code:
                result = result + [oldcode, ]
            Id = record.value("ID_LPU").toInt()[0]
            qresult = self.EIS_db.query("""select ID_LPU, ID_HISTORY, CODE
                        from LPU
                        where ID_LPU <> %d
                        and ID_HISTORY = %d
                        """%(Id, Id))
        result = list(set(result)) # убираем повторы
        return result

    def orgStructureInfisList(self, record):
        u"""Список инфисов всех подчиненных организаций"""
        Id = record.value("id").toInt()[0]
        code = unicode(record.value("CODE").toString())
        result = []
        qresult = self.EIS_db.query("""select ID_LPU as id, ID_PARENT, CODE
                        from LPU
                        where ID_LPU <> %d
                        and ID_PARENT = %d
                        """%(Id, Id))
        while qresult.next():
            record = qresult.record()
            subcode = unicode(record.value("CODE").toString())
            if len(subcode) and subcode != code:
                result += [subcode,]
            result += self.orgStructureInfisList(record)
        result = list(set(result)) # убираем повторы
        return result

    def getNumRecords(self):
        u"""Общее количество записей в источнике"""
        num_query = self.EIS_db.query("""SELECT count(*) as num from LPU""")
        num_query.next()
        return num_query.record().value("num").toInt()[0]

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

        from_stmt="""
        SELECT a.ID_LPU as id,
            a.ID_HISTORY,
            a.ID_PARENT,
            a.ID_PAYER,
            a.IS_ATTACH,
            a.IS_JUR,
            a.ID_HELP_TYPE,
            a.LPU_SHORT_NAME,
            a.LPU_LONG_NAME,
            a.LPU_END_DATE,
            a.BANK,
            a.FILIAL,
            a.INN,
            a.PC,
            a.PC2,
            a.BIK,
            a.OKPO,
            a.ADDRESS,
            a.JUR_ADDRESS,
            a.PHONE,
            a.FAX,
            a.EMAIL,
            a.REMARK,
            a.ID_TAREA,
            a.ID_LPU_TYPE,
            a.CHANGE_DATE,
            a.FIO,
            '' as OLD_CODES,
            a.CODE,
            a.ID_ATTACH,
            a.LPU_PRINT_NAME
        FROM LPU a
        where a.IS_ACTIVE = 1
        """
        from_query = EIS_db.query(from_stmt)
        from_query.setForwardOnly(True)
        db.query("""DROP TABLE if exists tmpLPU""")
        to_stmt = """
        CREATE TEMPORARY TABLE if not exists tmpLPU(
  id Integer NOT NULL,
  ID_HISTORY Integer NOT NULL,
  ID_PARENT Integer NOT NULL,
  ID_PAYER Integer NOT NULL,
  IS_ATTACH Char(1) NOT NULL,
  IS_JUR Char(1) NOT NULL,
  ID_HELP_TYPE Smallint NOT NULL,
  LPU_SHORT_NAME Varchar(10) NOT NULL,
  LPU_LONG_NAME Varchar(250) NOT NULL,
  LPU_END_DATE Timestamp,
  BANK Varchar(80) NOT NULL,
  FILIAL Varchar(80) NOT NULL,
  INN Varchar(10) NOT NULL,
  PC Varchar(20) NOT NULL,
  PC2 Varchar(20) NOT NULL,
  BIK Varchar(10) NOT NULL,
  OKPO Varchar(10) NOT NULL,
  ADDRESS Varchar(80) NOT NULL,
  JUR_ADDRESS Varchar(80) NOT NULL,
  PHONE Varchar(30) NOT NULL,
  FAX Varchar(30) NOT NULL,
  EMAIL Varchar(30) NOT NULL,
  REMARK Varchar(80) NOT NULL,
  ID_TAREA Integer NOT NULL,
  ID_LPU_TYPE Integer NOT NULL,
  CHANGE_DATE Timestamp NOT NULL,
  FIO Varchar(80) NOT NULL,
  CODE Varchar(5) NOT NULL,
  OLD_CODES Varchar(30) NOT NULL,
  ID_ATTACH Integer NOT NULL,
  LPU_PRINT_NAME Varchar(30) NOT NULL,
  CONSTRAINT PK_LPU PRIMARY KEY (id)
);
        """
        to_query = db.query(to_stmt)

        while from_query.next():
            QtGui.qApp.processEvents()
            if self.abort:
                break
            self.n += 1
            record = from_query.record()
            old_infises = ','.join(self.oldInfisList(record) + self.orgStructureInfisList(record)) # старые инфисы и инфисы подчинённых организаций
            record.setValue('OLD_CODES', toVariant(old_infises))
            self.record = record
            org_found+=1
            org_add+=1          #????????????????????????????????????????????????????
            db.insertRecord('tmpLPU',  self.record)
            self.progressBar.step()
            statusText = u'Найдено %d организаций' %org_found
            self.statusLabel.setText(statusText)

        self.log.append(u'Найдено %d организаций' %org_found)
        self.runScript(updateLPU_sql.COMMAND.split('\n'))
        self.log.append(u'готово')
        self.progressBar.setValue(self.n-1)
        #db.query('DROP TABLE tmpLPU')


    def err2log(self, e):
        if self.log:
            self.log.append(u'запись '+str(self.n)+': '+e)

