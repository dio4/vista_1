#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Ui_ImportServiceMes import Ui_Dialog
from Cimport import *

import importServicesMes_sql

u"""Диалог импорта услуг из МЭС"""

class CImportServiceMes(QtGui.QDialog, Ui_Dialog, CImport):
    u"""Диалог импорта услуг из МЭС"""
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        self.checkName()

    def checkName(self):
        #self.btnImport.setEnabled(self.edtMesName.text()!='')
        self.btnImport.setEnabled(True)


    def startImport(self):
        db = QtGui.qApp.db
        mes_name = 'mes'#self.edtMesName.text()
        add_services = self.checkAdd.isChecked()
        update_services = self.checkUpdate.isChecked()
        error = self.runScript(importServicesMes_sql.COMMAND.split('\n'), {'mes':mes_name, 'add_services':add_services, 'update_services':update_services}) 
        if error != None:
            QtGui.QMessageBox.warning(self, u'Ошибка при выполнении запроса к БД',
                        u'Ошибка при выполнении операции "Импортирование услуг".\n%s.'%(error.text()))
            self.log.append(unicode(error.text()))
        self.log.append(u'готово')

    def err2log(self, e):
        if self.log:
            self.log.append(u'запись '+str(self.n)+': '+e)

