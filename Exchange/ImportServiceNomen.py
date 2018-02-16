#!/usr/bin/env python
# -*- coding: utf-8 -*-
import exceptions

from Ui_ImportServiceNomen import Ui_Dialog
from Cimport import *
import importServices_sql
import importServices_create_sql
import importServices_deltemp_sql

import codecs

u"""Диалог импорта услуг из номенклатуры"""

FILE1_A_BEGIN = [u'РАЗДЕЛ А. ПРОСТЫЕ МЕДИЦИНСКИЕ УСЛУГИ',
u"",
u'Раздел',
u'Код ПМУ',
u'Наименование ПМУ',
u"",
u""
]

FILE1_B_BEGIN = [u'РАЗДЕЛ В. СЛОЖНЫЕ И КОМПЛЕКСНЫЕ МЕДИЦИНСКИЕ УСЛУГИ',
u"",
u'Раздел',
u'Код СКМУ',
u'Наименование СКМУ',
u"",
u""
]

FILE2_C_BEGIN = [u'Раздел',
u'Код услуги',
u'Наименование услуги'
]

FILE2_REQUIRED = u'Перечень медицинских услуг обязательного ассортимента'
FILE2_ADDITIONAL = u'Перечень медицинских услуг дополнительного ассортимента'

FILE3_D_BEGIN = [u'РАЗДЕЛ D. МАНИПУЛЯЦИИ, ИССЛЕДОВАНИЯ, ПРОЦЕДУРЫ И РАБОТЫ В ЗДРАВООХРАНЕНИИ',
u"",
u'Раздел',
u'Код работы',
u'Наименование работы'
]

FILE3_F_BEGIN = [u'РАЗДЕЛ F. КЛАССИФИКАТОР "УСЛУГИ МЕДИЦИНСКОГО СЕРВИСА"',
u'',
u'Раздел',
u'Код услуги',
u'Наименование услуги'
]

FILE3_APPENDIX_BEGIN = [u'Приложение N 1',
u'к Номенклатуре работ',
u'и услуг в здравоохранении',
u"",
u'РЕЕСТР',
u'МЕДИЦИНСКИХ УСЛУГ С УКАЗАНИЕМ УСЛОВНЫХ ЕДИНИЦ ТРУДОЗАТРАТ',
u"",
u'Код',
u'Наименование',
u'УЕТ врача',
u'УЕТ м/с'
]



class CImportServiceNomen(QtGui.QDialog, Ui_Dialog, CImport):
    u"""Диалог импорта услуг из номенклатуры"""
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        self.checkName()
        self.progressBar.setFormat('%v') # заранее неизвестно, сколько записей

    def checkName(self):
        self.btnImport.setEnabled(self.edtFileName.text()!='')

    def openFile(self, name):
        filename = unicode(self.edtFileName.text()) + name
        try:
            f = codecs.open(filename, encoding='utf-8', mode='rt')
            return [str.strip() for str in f]
        except exceptions.UnicodeDecodeError, e:
            f = codecs.open(filename, encoding='cp1251', mode='rt')
            return [str.strip() for str in f]
        except Exception, e:
            print type(e)
            self.err2log(u'Ошибка при открытии файла %s: %s'%(filename, unicode(e)))
            return []

    def runProgramScript(self, lines, name):
        ##self.log.append(u'Начинаем импорт!!!!!!')
        error = self.runScript(lines) # дату в словарь!!!!!!!!!!!!!!!!!!
        if error != None:
            QtGui.QMessageBox.warning(self, u'Ошибка при выполнении запроса к БД',
                        u'Ошибка при выполнении операции "%s".\n%s.'%(name, error.text()))
            self.log.append(unicode(error.text()))
            # как устанавливать ошибку???????????????????????

    def insert(self, db, table, values):
        driver = db.db.driver()
        record = db.record(table)
        db_values = []
        for i in xrange(len(values)):
            if values[i] or (values[i]==0): # values[i] != None
                field = record.field(i)
                field.setValue(QtCore.QVariant(values[i]))
                db_values = db_values + [unicode(driver.formatValue(field, False)), ]
            else:
                db_values = db_values + ["NULL", ]
        query = "INSERT IGNORE INTO %s VALUES("%table
        query = query + db_values[0]
        for value in db_values[1:]:
            query = query + ", " + value
        query = query + ")"
        db.query(query)

    def startImport(self):
        db = QtGui.qApp.db
        self.n = 0
        service_found = 0
        self.runProgramScript(importServices_create_sql.COMMAND.split('\n'), u'Создание временных таблиц')
        file1 = self.openFile(u'/НОМЕНКЛАТУРА1.txt')
        file2 = self.openFile(u'/НОМЕНКЛАТУРА2.txt')
        file3 = self.openFile(u'/НОМЕНКЛАТУРА3.txt')
        ##self.log.append(str(dir(file1)))
        num = (len(file1) + len(file2) + len(file3))/3
        self.progressBar.setMaximum(num)
        tA_len = len(FILE1_A_BEGIN)
        tB_len = len(FILE1_B_BEGIN)
        tC_len = len(FILE2_C_BEGIN)
        tD_len = len(FILE3_D_BEGIN)
        tF_len = len(FILE3_F_BEGIN)
        tApp_len = len(FILE3_APPENDIX_BEGIN)
        ##for str in file1[i:i+tA_len]:
        ##    self.log.append(str)
        # читаем файл 1:
        i = 0
        while i < len(file1) and file1[i:i+tA_len] != FILE1_A_BEGIN:
            i += 1
        i += tA_len
        while i < len(file1) and file1[i:i+tB_len] != FILE1_B_BEGIN:
            QtGui.qApp.processEvents()
            if self.abort:
                break
            if not len(file1[i]):
                i+=1
                continue
            [letter, code, name] = [file1[i], file1[i+1], file1[i+2]]
            i += 3
            ##self.log.append(str(i))
            self.insert(db, "tmpA", [code, name, None, 0, None, 0, None, 0])
            self.n += 1
            service_found += 1
            self.progressBar.step()
            statusText = u'Найдено %d услуг' %service_found
            self.statusLabel.setText(statusText)
        i += tB_len
        while i < len(file1):
            QtGui.qApp.processEvents()
            if self.abort:
                break
            if not len(file1[i]):
                i+=1
                continue
            [letter, code, name] = [file1[i], file1[i+1], file1[i+2]]
            i += 3
            ##self.log.append(str(i))
            self.insert(db, "tmpB", [code, name, None, 0, None, 0, None, 0])
            self.n += 1
            service_found += 1
            self.progressBar.step()
            statusText = u'Найдено %d услуг' %service_found
            self.statusLabel.setText(statusText)
        # читаем файл 2:
        ##self.log.append("Read file2...")
        # могут стоять русские префиксы "А" и "В" --- меняем их на латинские:
#        for i in xrange(len(file2)):
#            if file2[i] == u'А':
#                file2[i] = "A"
#            if file2[i] == u'В':
#                file2[i] = "B"
        i = 0
        while i < len(file2) and file2[i:i+tC_len] != FILE2_C_BEGIN:
            i += 1
        i += tC_len
        [master_letter, master_code, master_name] = [u'В', "", ""]
        required = False # входит в обязательный ассортимент
        while i < len(file2):
            ##self.log.append(str(i))
            QtGui.qApp.processEvents()
            if self.abort:
                break
            if (file2[i] == u'В') and (master_code == "" or (file2[i-1] == ""and file2[i+1] > master_code)):  # начало группы
                ##and (i+3 < len(file2)) and (file2[i+3]==FILE2_REQUIRED or file2[i+3] == FILE2_ADDITIONAL):
                [master_letter, master_code, master_name] = [file2[i], file2[i+1], file2[i+2]]
                ##self.log.append(master_letter + master_code + master_name)
                i+=3
            elif file2[i] == FILE2_REQUIRED: # начало перечня обязательных услуг
                required = True
                i+=1
            elif file2[i] == FILE2_ADDITIONAL: # начало перечня дополнительных услуг
                required = False
                i+=1
            elif file2[i] == u'А' or file2[i] == u'В': # элемент группы
                [letter, code, name] = [file2[i], file2[i+1], file2[i+2]]
                i += 3
                self.insert(db, "tmpC", [master_code, master_name, letter, code, name, required, None, 0])
                self.n += 1
                self.progressBar.step()
            else: # комментарии, названия разделов и прочий мусор
                i += 1
        # читаем файл 3:
        i = 0
        while i < len(file3) and file3[i:i+tD_len] != FILE3_D_BEGIN:
            i += 1
        i += tD_len
        while i < len(file3) and file3[i:i+tF_len] != FILE3_F_BEGIN:
            QtGui.qApp.processEvents()
            if self.abort:
                break
            if not len(file3[i]):
                i+=1
                continue
            [letter, code, name] = [file3[i], file3[i+1], file3[i+2]]
            i += 3
            ##self.log.append(str(i))
            self.insert(db, "tmpD", [code, name, None, 0, None, 0])
            self.n += 1
            service_found += 1
            self.progressBar.step()
            statusText = u'Найдено %d услуг' %service_found
            self.statusLabel.setText(statusText)
        i += tF_len
        while i < len(file3) and file3[i:i+tApp_len] != FILE3_APPENDIX_BEGIN:
            QtGui.qApp.processEvents()
            if self.abort:
                break
            if not len(file3[i]):
                i+=1
                continue
            [letter, code, name] = [file3[i], file3[i+1], file3[i+2]]
            i += 3
            ##self.log.append(str(i))
            self.insert(db, "tmpF", [code, name, None, 0, None, 0])
            self.n += 1
            service_found += 1
            self.progressBar.step()
            statusText = u'Найдено %d услуг' %service_found
            self.statusLabel.setText(statusText)
        self.log.append(u'Найдено %d услуг' %service_found)
        # импорт данных из временных таблиц
        self.runProgramScript(importServices_sql.COMMAND.split('\n'), u'Импортирование услуг')
        QtGui.QMessageBox.information(self, u'Импорт услуг из номенклатуры',
                        u'Импорт выполнен!')
        self.runProgramScript(importServices_deltemp_sql.COMMAND.split('\n'), u'Удаление временных таблиц')
        self.log.append(u'готово')
        self.progressBar.setValue(self.n-1)
        self.labelNum.setText(u'всего строк в источнике: '+str(num))

    @QtCore.pyqtSlot()
    def on_btnOpen_clicked(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.Directory)
        dialog.exec_()
        filename = dialog.selectedFiles()[0]
        self.edtFileName.setText(filename)
        self.checkName()

    def err2log(self, e):
        if self.log:
            self.log.append(u'запись '+str(self.n)+': '+e)

