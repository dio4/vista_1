#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import Exchange.Cimport
import Exchange.Ui_ImportSPR18

from PyQt4 import QtCore, QtGui

from Exchange.Utils import dbfCheckNames
from library.Utils import forceString, getVal, forceStringEx, toVariant
from library.dbfpy.dbf import Dbf
from library.exception import CException


def ImportSPR15(widget):
    dlg = CImportSPR15(widget)
    dlg.exec_()

class CImportSPR15(Exchange.Cimport.CDBFimport, QtGui.QDialog, Exchange.Ui_ImportSPR18.Ui_Dialog):

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        super(CImportSPR15, self).__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.edtFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportSPR15FileName', '')))
        self.setWindowTitle(u'Импорт причин отказов из SPR15')

    def openDBF(self):
        dbf = None
        fileName = forceStringEx(self.edtFileName.text())
        result = os.path.isfile(fileName)
        if result:
            dbf = Dbf(fileName, readOnly=True, encoding='cp866')
            fieldsList = ['CODE', 'NAME', 'KOMMENT']
            if not dbfCheckNames(dbf, fieldsList): raise CException(u'файл %s\nне содержит одного из полей:\n%s' % (fileName, ', '.join(fieldsList)))
            self.labelNum.setText(u'всего записей в источнике: '+str(dbf.recordCount))
        return dbf

    @staticmethod
    def fillPayRefuseTypeRecord(db, table, record, code=None, name=None, reason=None):
        if code is not None:    record.setValue('code', toVariant(code))
        if name is not None:    record.setValue('name', toVariant(name))
        if reason is not None:   record.setValue('reason', toVariant(reason))
        db.insertOrUpdate(table, record)

    def startImport(self):
        db = QtGui.qApp.db
        dbf = self.openDBF()
        nprocessed = 0
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(dbf.recordCount)

        tblRbPayRefuseType = db.table('rbPayRefuseType')

        for row in dbf:
            self.progressBar.step()
            QtGui.qApp.processEvents()
            if self.abort:
                self.log.append(u'Прервано пользователем')
                return

            code = forceString(row['CODE'])
            name = forceString(row['NAME'])
            reason = forceString(row['KOMMENT'])

            rbPayRefuseTypeList = db.getRecordList(tblRbPayRefuseType,
                                              cols='*',
                                              where=db.joinAnd([
                                                  tblRbPayRefuseType['code'].eq(code)
                                              ]))
            if len(rbPayRefuseTypeList) > 1:  # if more than one entry, give a warning
                self.addDuplicateAlertToLog(u'Информация не обновилась - дупликаты в базе.\n Причины отказа платежа (rbPayRefuseType)', code,
                                            [forceString(service.value('id')) for service in rbPayRefuseTypeList])
            elif len(rbPayRefuseTypeList) == 1:  # if one entry, update it
                self.fillPayRefuseTypeRecord(db, tblRbPayRefuseType, rbPayRefuseTypeList[0], name=name, code=code, reason=reason)
            else:  # insert it
                self.fillPayRefuseTypeRecord(db, tblRbPayRefuseType, tblRbPayRefuseType.newRecord(), name=name, code=code, reason=reason)
                nprocessed += 1

        self.log.append(u'Добавлено %d записей' % nprocessed)
        self.log.append(u'готово')
        QtGui.qApp.preferences.appPrefs['ImportSPR69FileName'] = toVariant(self.edtFileName.text())

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