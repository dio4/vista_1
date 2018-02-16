# -*- coding: utf-8 -*-
from Exchange.Utils import makeZipArchive

#############################################################################
##
## Copyright (C) 2012 Vista Software. All rights reserved.
##
#############################################################################

'''
Created on Jun 20, 2012

@author: atronah
'''
#TODO: atronah: объединить с генератором отчетов

from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QDateTimeEdit, QDateEdit
from PyQt4.QtGui import QSpinBox
from PyQt4.QtGui import QDoubleSpinBox
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QLayout
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QSizePolicy

from library.DialogBase import CDialogBase
from Ui_ExportToDbfDialog import Ui_ExportToDbfDialog
from library.Utils import *
from library.exception import CDatabaseException

import os

from library.dbfpy.dbf import *

## Диалоговое окно для управления выгрузкой в DBF файл с использованием внешних файлов настройки
#    Производит выгрузку (экспорт) данных, полученных из запроса на основе выбранного шаблона (*.sql), в
#    .dbf файл, использую структуру, указанную в .ini файле выбранного шаблона
class CExportToDbfDialog(CDialogBase, Ui_ExportToDbfDialog):
    iniExt = '.ini'
    sqlExt = '.sql'
    dbfExt = '.dbf'
    groupExt = '.group'
    
    ## Инициализация класса
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self._emptyFieldText = u'<Не задано>'
        self._templateParamsWidgets = {}
        self._templateVarStmt = u''
        self._pattern = re.compile(ur'\%\(([a-zA-Z_а-яА-ЯеЕёЁ]+)\)([bfdtsiq])') #Обязательно должен состоять из двух групп (имяПараметра и тип)
        
        self.setupUi(self)
        self.setWindowTitle(u'Экспорт в DBF')
        self.setDefaultOutPath()
        self.pbRecords.setVisible(False)
        self.pbFiles.setVisible(False)
        
        self.loadMyPreferences()
        self.loadTemplateNames()
        
        self._templateNameWithPathList = [] # Список имен файлов с шаблонами
    
    
    def setDefaultOutPath(self):
        outPath = os.getcwd()
        self.edtOutPath.setText(outPath)
        return outPath
        
        
    def saveMyPreferences(self):
        preferences = {}
        setPref(preferences,'codecName', QVariant(self.cmbCodec.currentText()))
        setPref(QtGui.qApp.preferences.reportPrefs, self.objectName(), preferences)
    
    
    def loadMyPreferences(self):
        preferences = getPref(QtGui.qApp.preferences.reportPrefs, self.objectName(), {})
        codecName = getPref(preferences, 'codecName', None)
        if codecName:
            codecName = codecName.toString()
            self.cmbCodec.setCurrentIndex(self.cmbCodec.findText(codecName))
    
    
    @staticmethod
    def getTemplatesDirectory():
        workDir = os.getcwd()
        return os.path.join(workDir, 'dbfExportTemplates')
    
    
    @staticmethod
    def isCorrectTemplateName(templateName, templateDir = None):
        if not templateName:
            return False
        templateDir = templateDir or CExportToDbfDialog.getTemplatesDirectory()
        templateName = os.path.basename(templateName)
        return os.path.isfile(os.path.join(templateDir, templateName + CExportToDbfDialog.sqlExt)) \
                and os.path.isfile(os.path.join(templateDir, templateName + CExportToDbfDialog.iniExt))
    
        
    ## Загружает доступные шаблоны выгрузки
    #
    #    Проверяет папку ./dbfExportTemplates на предмет наличия 
    # пар файлов {name}.sql и {name}.ini. Если подбная пара найдена, 
    # то в список шаблонов добавляется {name}
    def loadTemplateNames(self):
        self.cmbExportTemplates.clear()
        self.cmbExportTemplates.addItem(self._emptyFieldText)
        
        templatesDir = CExportToDbfDialog.getTemplatesDirectory()
        if not templatesDir:
            return
        
        if not os.path.isdir(templatesDir):
            return
        
        
        isTemplatesGroup = self.rbTemplateGroups.isChecked() 
        for fileName in os.listdir(templatesDir):
            templateName, ext = os.path.splitext(fileName)
            templateNameWithPath = os.path.join(templatesDir, templateName)
            if isTemplatesGroup:
                if not (ext == self.groupExt):
                    continue
            elif not (ext == self.sqlExt and CExportToDbfDialog.isCorrectTemplateName(templateName)):
                continue
            
            self.cmbExportTemplates.addItem(templateName, templateNameWithPath)
        
                
    
    ## Помечает шаблон как некорректный
    #    @param templateIndex: индекс шаблона в списке 
    #
    def markTemplateAsIncorrect(self, templateIndex):
        self.cmbExportTemplates.setItemData(templateIndex, u'!incorrect_file_content')
        oldTemplateName = self.cmbExportTemplates.itemText(templateIndex)
        self.cmbExportTemplates.setItemText(templateIndex, u'(incorrect)' + oldTemplateName)
        
    
    ## Обновляет список параметров шаблона
    #
    #    Очищает текущий список параметров, читает файл *.sql выбранного шаблона.
    # Для каждой подстроки вида %(name)x, где name - имя параметра, а x - тип 
    # (возможны значения: b - булево, f - число с плавающей запятой, i - целое число, s - строка, d - дата, t - дата и время, q - зарезервированное за именем значение),
    # создает виджет  ввода параметра и помещает его в scrollArea.
    #    @param templateIndex: индекс шаблона в списке шаблонов
    def updateParamsAndTemplates(self, templateIndex):
        #Удаление всех виджетов для ввода параметров шаблона (QLabel и QWidget)
        for widget in self.scrollAreaWidgetContents.children():
            if not isinstance(widget, QLayout):
                self.paramNamesLayout.removeWidget(widget)
                self.paramValuesLayout.removeWidget(widget)

        self._templateParamsWidgets.clear()
        
        self._templateNameWithPathList = []
        self._templateStmts = {}
        codecName = forceString(self.cmbCodec.currentText())
        
        templateDirectory = CExportToDbfDialog.getTemplatesDirectory()
        
        templateNameWithPath = forceString(self.cmbExportTemplates.itemData(templateIndex))
        # Если выбран режим работы с группой шаблонов
        if self.rbTemplateGroups.isChecked():
            #Подгружается файл группы шаблонов (текстовый документ, где построчно указываются пути к файлам с шаблонами группы)
            templateGroupNameWithPath = templateNameWithPath + self.groupExt
            if not os.path.exists(templateGroupNameWithPath):
                return
            with codecs.open(templateGroupNameWithPath, 'r', encoding = codecName) as groupFile:
                lineList = groupFile.readlines()
            
            for fileLine in lineList:
                fileLine = fileLine.strip()
                
                if fileLine.startswith('..'):
                    templateNameWithPath = fileLine.replace('..', os.path.dirname(templateDirectory), 1)
                elif fileLine.startswith('.'):
                    templateNameWithPath = fileLine.replace('.', templateDirectory, 1)
                elif os.path.basename(fileLine) == fileLine:
                    templateNameWithPath = os.path.join(templateDirectory, fileLine)
                else:
                    templateNameWithPath = os.path.abspath(fileLine)
                
                if not CExportToDbfDialog.isCorrectTemplateName(templateNameWithPath):
                    templateNameWithPath = os.path.splitext(templateNameWithPath)[0]
                
                if not CExportToDbfDialog.isCorrectTemplateName(templateNameWithPath):
                    continue
                
                self._templateNameWithPathList.append(os.path.abspath(templateNameWithPath))
        
        else:
            
            if CExportToDbfDialog.isCorrectTemplateName(templateNameWithPath):
                self._templateNameWithPathList.append(os.path.abspath(templateNameWithPath))
        
        
        for templateNameWithPath in self._templateNameWithPathList:
            with codecs.open(templateNameWithPath + self.sqlExt, 'r', encoding = codecName) as templateFile:
                matches = []
                try:
                    self._templateStmts[templateNameWithPath] = templateFile.read()
                    matches = self._pattern.findall(self._templateStmts[templateNameWithPath])
                except:
                    QtGui.qApp.logCurrentException()
                    self.markTemplateAsIncorrect(templateIndex)
    
                for match in matches:
                    paramName = match[0]
                    paramType = match[1]
                    if not self._templateParamsWidgets.has_key((paramName, paramType)):
                        if paramType == 'b':
                            self._templateParamsWidgets[(paramName, paramType)] = QCheckBox()
                        elif paramType == 'f':
                            self._templateParamsWidgets[(paramName, paramType)] = QDoubleSpinBox()
                            self._templateParamsWidgets[(paramName, paramType)].setRange(-999.999, 999.999)
                        elif paramType == 'd':
                            self._templateParamsWidgets[(paramName, paramType)] = QDateEdit()
                            self._templateParamsWidgets[(paramName, paramType)].setCalendarPopup(True)
                            self._templateParamsWidgets[(paramName, paramType)].setDate(QDate.currentDate())
                        elif paramType == 't':
                            self._templateParamsWidgets[(paramName, paramType)] = QDateTimeEdit()
                            self._templateParamsWidgets[(paramName, paramType)].setCalendarPopup(True)
                            self._templateParamsWidgets[(paramName, paramType)].setDate(QDate.currentDate())
                        elif paramType == 's':
                            self._templateParamsWidgets[(paramName, paramType)] = QLineEdit()
                        elif paramType == 'i':
                            self._templateParamsWidgets[(paramName, paramType)] = QSpinBox()
                            self._templateParamsWidgets[(paramName, paramType)].setRange(-999999, 999999)
                #end for match in matches
            #end with codecs.open(templateNameWithPath
        #end for templateNameWithPath
        
        for item in self._templateParamsWidgets.items():
            self.paramNamesLayout.addWidget(QLabel('%s:' % item[0][0].replace('_', ' ')), alignment = Qt.AlignRight)
            self.paramValuesLayout.addWidget(item[1])
            item[1].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
    
    @pyqtSlot(int)        
    def on_cmbExportTemplates_currentIndexChanged(self, index):
        self.updateParamsAndTemplates(index)
    
    
    ## Возвращает значение параметра с именем paramName
    #    @param paramName: 
    def getParamValue(self, paramName, paramType):
        
        value = u"''" # пустая строка в одинарных кавычках по умолчанию
        try:
            #Предопределенные имена параметров
            if paramType == 'q':
                if paramName == '__defaultKLADR':
                        value = "'%s'" % forceString(QtGui.qApp.defaultKLADR())
            #Задаваемые пользователем параметры
            else:
                widget = self._templateParamsWidgets[(paramName, paramType)]
                if paramType == 'b':
                    value = '1' if widget.isChecked() else '0'
                elif paramType == 'f' \
                   or paramType == 'i':
                    value = forceString(widget.value())
                elif paramType == 'd':
                    value = "'%s'" % forceString(widget.dateTime().toString(u'yyyy-MM-dd'))
                elif paramType == 't':
                    value = "'%s'" % forceString(widget.dateTime().toString(u'yyyy-MM-dd hh:mm:ss'))
                elif paramType == 's':
                    value = "'%s'" % forceString(widget.text())                    
        except:
            QtGui.qApp.logCurrentException()
        
        return value
    
    
    ## Подставляет параметры с формы в шаблон запроса
    def sqlStr(self, templateNameWithPath):
        completeSql = self._templateStmts.get(templateNameWithPath, '')
        for match in self._pattern.finditer(completeSql):
            subStr = match.group()
            paramName, paramType = match.groups()
            value = self.getParamValue(paramName, paramType)
            completeSql = completeSql.replace(subStr, value)
        return completeSql  
        

    def exportProcess(self):
        def trueDbfTypeValue(record, dbfField):
            fieldType = dbfField.fieldInfo()[1]
            
            fieldName = dbfField.name
            value = record.value(fieldName)
            if fieldType == 'D':
                return pyDate(forceDate(value))
            elif fieldType == 'N':
                fieldDec = dbfField.fieldInfo()[3]
                if fieldDec > 0 :
                    return forceDouble(value)
                return forceInt(value)
            elif fieldType == 'I':
                return forceInt(value)
            elif fieldType == 'L':
                return forceBool(value)
            
            return forceString(value)
        #end trueDbfTypeValue
        
        
        errorMessage = ''
        
        
        if self.cmbExportTemplates.currentText() == self._emptyFieldText:
            QMessageBox.warning(self, u'Ошибка', u'Не указан шаблон экспорта', buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)
            return
        
        self.textLogs.append('-----%s-----' % QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss'))
        self.textLogs.append(u'%s> Запуск экспорта...' % QDateTime.currentDateTime().toString('hh:mm:ss'))
        
        outPath = os.path.normpath(forceString(self.edtOutPath.text()))
        
        if outPath is None or outPath.strip() == u'':
            outPath = self.setDefaultOutPath()
        
        if not os.path.isdir(outPath):
            errorMessage += u'Пути, указанного для сохранения файла выгрузки не существует\n'
        
        if not self._templateNameWithPathList:
            errorMessage.append(u'Отсутствуют файлы для обработки')
            
        if errorMessage:
            QMessageBox.warning(self, u'Ошибка', errorMessage, buttons=QMessageBox.Ok, defaultButton=QMessageBox.Ok)
            return
        
        dbfFileList = []
        
        self.pbFiles.setVisible(True)
        self.pbFiles.setRange(0, len(self._templateNameWithPathList))
        self.pbFiles.setValue(0)
        
        self.pbRecords.setVisible(True)
        for templateNameWithPath in self._templateNameWithPathList:
            self.textLogs.append(u'%s> Обработка шаблона %s' % (QDateTime.currentDateTime().toString('hh:mm:ss'),
                                                                templateNameWithPath))
            configFileName = templateNameWithPath + self.iniExt
            
            if not os.path.exists(configFileName):
                self.textLogs.append(u'%s> <Ошибка> %s' % (QDateTime.currentDateTime().toString('hh:mm:ss'), u'Не найден конфигурационный файл\n'))
                break
            
            resultProgressMessage = u'Записей не найдено'
            try:
                self.pbRecords.reset()
                self.pbRecords.setText(u'Обработка запроса')
                self.pbRecords.setMaximum(1)
                self.pbRecords.setValue(0)
                QtGui.qApp.processEvents(QEventLoop.ExcludeUserInputEvents)
                self.textLogs.append(u'%s> Выполнение запроса...' % QDateTime.currentDateTime().toString('hh:mm:ss'))
                query = QtGui.qApp.db.query(self.sqlStr(templateNameWithPath))
                recordsCount = query.size()
                self.textLogs.append(u'%s> Найденно %s записей' % (QDateTime.currentDateTime().toString('hh:mm:ss'),
                                                                   recordsCount))
                if recordsCount > 0:
                    self.textLogs.append(u'%s> Обработка запроса...' % QDateTime.currentDateTime().toString('hh:mm:ss'))
                    self.pbRecords.setMaximum(recordsCount)
                    self.pbRecords.setFormat(u'Обработано записей %v/%m')
                    resultProgressMessage = u'Завершено записей %v/%m'
                    query.setForwardOnly(False)
                    query.next()
                    outFileName = forceString(query.record().value('outFileName'))
                    query.previous()
                    if not outFileName:
                        outFileName = forceString(QDateTime.currentDateTime()).replace(':', '-')
                    
                    if os.path.splitext(outFileName)[1].lower() != self.dbfExt:
                        outFileName += self.dbfExt
                    
                    self.textLogs.append(u'%s> Создание файла выгрузки...' % QDateTime.currentDateTime().toString('hh:mm:ss'))
                    
                    # Исключение дубликатов
                    dbfFileName = os.path.join(outPath, outFileName)
                    dbfFileNameParts = os.path.splitext(dbfFileName)
                    nameSuffix = 1
                    
                    while os.path.exists(dbfFileName):
                        dbfFileName = dbfFileNameParts[0] + ('_copy%s' % nameSuffix) + dbfFileNameParts[1]
                        nameSuffix += 1
                        
                        
                    dbf = Dbf(dbfFileName, new=True, encoding='cp866')
                    self.textLogs.append(u'%s> Открытие конфигурационного файла шаблона...' % QDateTime.currentDateTime().toString('hh:mm:ss'))
                    iniFile = open(configFileName, 'r')
                    self.textLogs.append(u'%s> Чтение конфигурационного файла шаблона и создание структуры файла выгрузки...' 
                                         % QDateTime.currentDateTime().toString('hh:mm:ss'))
                    for line in iniFile.readlines():
                        fname, ftype, flen, fdec = line.split(';')[:4]
                        fname = fname[:10].strip()
                        ftype = ftype[:1]
                        flen = int(flen) if flen.strip().isdigit() else None
                        fdec = int(fdec) if fdec.strip().isdigit() else None
                        dbf.addField(
                                     (fname, ftype, flen, fdec),
                                     )
                    iniFile.close()
                    
                    self.textLogs.append(u'%s> Обработка полученных записей...' % QDateTime.currentDateTime().toString('hh:mm:ss'))
                    while query.next():
                        self.pbRecords.step()
                        QtGui.qApp.processEvents(QEventLoop.ExcludeUserInputEvents)
                        record = query.record()
                        dbfRecord = dbf.newRecord()
                    
                        for field in dbf.header.fields:
                            dbfRecord[field.name] = trueDbfTypeValue(record, field)
                        dbfRecord.store()
                    dbf.close()
                    dbfFileList.append(dbfFileName)
                #end if
                                
            except CDatabaseException, e:
                msg = unicode(e)
                driverName = QtGui.qApp.db.db.driverName()
                index = msg.rfind('%s: Unable to execute query' % driverName)
                if index != -1:
                    msg = msg[index : ]
                self.textLogs.append(u'%s> <Ошибка выполнения запроса> %s' % (QDateTime.currentDateTime().toString('hh:mm:ss'), msg))
                
            except Exception, e:
                self.textLogs.append(u'%s> <Ошибка> %s' % (QDateTime.currentDateTime().toString('hh:mm:ss'), unicode(e)))
                resultProgressMessage = u'Ошибка экспорта для шаблона %s' % os.path.basename(templateNameWithPath)
            
            self.pbRecords.setText(resultProgressMessage)
            self.pbFiles.step()
            
        #end for
        self.textLogs.append(u'%s> Экспорт завершен...\n\n\n' % QDateTime.currentDateTime().toString('hh:mm:ss'))
          
        if self.chkMakeArchive.isChecked() and dbfFileList:
            makeZipArchive(self, dbfFileList, outPath, True)
        
    
    
        
    @pyqtSlot()
    def on_btnExport_clicked(self):
        try:
            self.btnExport.setEnabled(False)
            self.exportProcess()
        finally:
            self.btnExport.setEnabled(True)
    
    
    def closeEvent(self, event):
        if not self.btnExport.isEnabled():
            QtGui.QMessageBox.warning(self, u'Внимание', u'Нелльзя закрыть окно, пока выполняется экспорт', buttons = QtGui.QMessageBox.Ok)
            event.ignore()
        else:
            self.saveMyPreferences()
            CDialogBase.closeEvent(self, event)
    
    @pyqtSlot()    
    def on_btnBrowse_clicked(self):
        savePath = forceString(QFileDialog.getExistingDirectory(parent = self, 
                                                                caption = u'Выберите место для сохранения файла выгрузки',
                                                                directory = os.getcwd()))
        self.edtOutPath.setText(savePath)
    
    
    @pyqtSlot(int)        
    def on_cmbCodec_currentIndexChanged(self, index):
        self.loadTemplateNames()
        
    
    def on_rbTemplateGroups_toggled(self):
        self.loadTemplateNames()