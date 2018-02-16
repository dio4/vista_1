# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################
from Reports.ReportsGenerator.ReportsGeneratorEngine import CReportsGeneratorEngine
from Reports.ReportsGenerator.Utils import resizeTextTableInDocument, firstTextTableFromDocument,\
    setBorderForAllTablesInDocument
import os

import locale
from library.Utils import forceString, forceInt
from Reports.ReportsGenerator.TemplateParametersModel import CTemplateParametersModel

'''
Created on 26.02.2013

@author: atronah
'''

from PyQt4 import QtCore, QtGui

from Ui_ReportsGeneratorSetupDialog import Ui_ReportsGeneratorSetupDialog


class CParameterInserter(QtGui.QDialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Вставка параметра')
        self.parametersView = QtGui.QTableView(self)
        self.parametersView.horizontalHeader().setStretchLastSection(True)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.parametersView)
        self.setLayout(self.mainLayout)
        
        self.parametersView.clicked.connect(self.on_parametersView_clicked)
        
        self._name = ''
    
    
    def setParametersModel(self, model):
        if isinstance(model, CTemplateParametersModel):
            self.parametersView.setModel(model)
            self.parametersView.setColumnHidden(1, True)
    
    
    def name(self):
        return self._name
        
    
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_parametersView_clicked(self, index):
        model = self.parametersView.model()
        if isinstance(model, CTemplateParametersModel):
            self._name = model.itemName(index)
        else:
            self._name = ''
        self.accept()
            
    
    
        
    


class CReportsGeneratorSetupDialog(QtGui.QDialog, Ui_ReportsGeneratorSetupDialog):          
    tiParameters = 0 
    tiAdditionalSettings = 1 
    tiPreview = 2
    tiQueryStmt = 3
    tiInfo = 4
    
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(u'Генератор отчетов. Бета версия')
        self.edtInputFileName.setReadOnly(True)
        
        self._reportEngine = None
        
        self.tedtPreview.setReadOnly(True)
        
        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.acceptClick)
        self.connect(self.buttonBox, QtCore.SIGNAL('rejected()'), self.reject)
        
        self.connect(self.btnSaveChanged, QtCore.SIGNAL('clicked()'), self.saveSettings)
        
        self.chkTranspose.toggled.connect(self.markAsDirty)
        
        self.tedtHeaderSection.textChanged.connect(self.markAsDirty)
        self.gbHeaderSection.clicked.connect(self.markAsDirty)
        self.tedtFooterSection.textChanged.connect(self.markAsDirty)
        self.gbFooterSection.clicked.connect(self.markAsDirty)
        self.mainTableColumns.horizontalHeader().sectionResized.connect(self.markAsDirty)
        self.mainTableColumns.itemChanged.connect(self.markAsDirty)
        
        self.spbHeaderRowCount.valueChanged.connect(self.changeHeaderSectionRowCount)
        self.spbHeaderColumnCount.valueChanged.connect(self.changeHeaderSectionColumnCount)
        self.spbFooterRowCount.valueChanged.connect(self.changeFooterSectionRowCount)
        self.spbFooterColumnCount.valueChanged.connect(self.changeFooterSectionColumnCount)
        
        self.addFooterMenu = QtGui.QMenu()
        self.addFooterMenu.addAction(u'Добавить значение параметра', self.on_actAddParameterToFooter_triggered)
        #self.addFooterMenu.addAction(u'Добавить значение из таблицы', self.on_actAddQueryValueToFooter_triggered)
        self.addFooterMenu.addAction(u'Добавить вывод итога прописью', self.addAmountInWordsToFooter)
        self.btnAddToFooter.setMenu(self.addFooterMenu)
        
        
        self.textAppearanceEditor.fontChanged.connect(self.tedtHeaderSection.setCurrentFont)
        self.textAppearanceEditor.fontChanged.connect(self.tedtFooterSection.setCurrentFont)
        self.textAppearanceEditor.fontChanged.connect(self.setFontForSelectedMainTableItem)
        
        self.textAppearanceEditor.alignmentChanged.connect(self.tedtHeaderSection.setAlignment)
        self.textAppearanceEditor.alignmentChanged.connect(self.tedtFooterSection.setAlignment)
        self.textAppearanceEditor.alignmentChanged.connect(self.setAlignmentForSelectedMainTableItem)
        
        self.setDirty(False)
        self.loadTemplatesList()
        
        self.edtInputFileName.setVisible(False)
        self.btnBrowseInputFile.setVisible(False)
        
        self.tblParameters.horizontalHeader().setStretchLastSection(True)
        
        self.setTabsEnabled(False, [self.tiAdditionalSettings, self.tiPreview, self.tiQueryStmt])
        
        self.loadedFileName = ''
        
    
    
    def loadTemplatesList(self):
        self.cmbTemplateFile.addItem(u'Не задано', None)
        workDir = os.getcwd()#.decode(locale.getpreferredencoding())
        templatesDir = os.path.join(workDir, 'ReportsTemplates')
        if os.path.exists(templatesDir) and os.path.isdir(templatesDir):
            for fileName in os.listdir(templatesDir):
                fileName = fileName.decode(locale.getpreferredencoding())
                name, ext = os.path.splitext(fileName)
                if ext == '.sql':
                    try:
#                    print '%s %s %s' % (name, ext, os.path.join(templatesDir, fileName))  
                        self.cmbTemplateFile.addItem(name, os.path.join(templatesDir, fileName))
                    except UnicodeDecodeError as e:
                        QtGui.QMessageBox.critical(
                            self,
                            u'Ошибка',
                            u'В имени файла не должны присутствовать символы кирилицы: %s' % fileName,
                            buttons=QtGui.QMessageBox.Close
                        )
                        raise e
            
    
    def isDirty(self):
        return self._isDirty
    
    
    def setDirty(self, state):
        self._isDirty = state
        self.btnSaveChanged.setEnabled(state)
    
    
    @QtCore.pyqtSlot()
    def markAsDirty(self):
        self.setDirty(True)
    
    
    def setReportEngine(self, reportEngine):
        if isinstance(reportEngine, CReportsGeneratorEngine):
            self.tblParameters.setModel(reportEngine._parametersModel)
            self.tblParameters.setItemDelegateForColumn(1, reportEngine._parametersModel.itemDelegate())
            
#            self._headerSectionModel = reportEngine.additionalSection(0)
#            self.tableHeaderSection.setModel(self._headerSectionModel)
#            self.connect(self.tableHeaderSection, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.sectionCellTextEdit)
#            self.connect(self.spbHeadRowCount, QtCore.SIGNAL('valueChanged(int)'), self._headerSectionModel.setRowCount)
#            self.connect(self.spbHeadRowCount, QtCore.SIGNAL('valueChanged(int)'), self.markAsDirty)
#            self.connect(self.spbHeadColumnCount, QtCore.SIGNAL('valueChanged(int)'), self._headerSectionModel.setColumnCount)
#            self.connect(self.spbHeadColumnCount, QtCore.SIGNAL('valueChanged(int)'),  self.markAsDirty)
#            
#            self._footerSectionModel = CReportAdditionalSectionModel()
#            self.tableFooterSection.setModel(self._footerSectionModel)
#            self.connect(self.tableFooterSection, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.sectionCellTextEdit)
#            self.connect(self.spbFooterRowCount, QtCore.SIGNAL('valueChanged(int)'), self._footerSectionModel.setRowCount)
#            self.connect(self.spbFooterRowCount, QtCore.SIGNAL('valueChanged(int)'), self.markAsDirty)
#            self.connect(self.spbFooterColumnCount, QtCore.SIGNAL('valueChanged(int)'), self._footerSectionModel.setColumnCount)
#            self.connect(self.spbFooterColumnCount, QtCore.SIGNAL('valueChanged(int)'), self.markAsDirty)
            
            self._reportEngine = reportEngine
            self.setTabsEnabled(True, [self.tiParameters])


    def setParams(self, params):
        templateFileName = params.pop('templateFileName', '')
        index = 0
        if templateFileName:
            index = self.cmbTemplateFile.findData(QtCore.QVariant(templateFileName))
            if index == -1:
                index = 0
        self.cmbTemplateFile.setCurrentIndex(index)
        self.on_cmbTemplateFile_currentIndexChanged(index) #TODO: atronah: избавится
        if self._reportEngine:
            self._reportEngine._parametersModel.setItemValues(params)
        

    
    def loadTemplateFile(self, fileName):
        if self._reportEngine:
            if self._reportEngine.loadTemplateFromFile(fileName):
                self.loadedFileName = fileName
                self.setTabsEnabled(True, [self.tiAdditionalSettings, self.tiPreview, self.tiQueryStmt])
                self.initSections()
                self.initMainTableSetting()
            else:
                self.setTabsEnabled(False, [self.tiAdditionalSettings, self.tiPreview, self.tiQueryStmt])
                self._reportEngine.clear()
            self.setDirty(False)
    
    
    def setTabsEnabled(self, state, tabIndexesList = None):
        if not tabIndexesList:
            tabIndexesList = range(self.tabWidget.count())
        for tabIndex in tabIndexesList:
            self.tabWidget.widget(tabIndex).setEnabled(state)
    
    
    def params(self):
        result = {}
        result['templateFileName'] = self.loadedFileName
        result['pageOrientation'] = QtGui.QPrinter.Landscape if self.chkIsLandscapeOrientation.isChecked() \
                                                             else QtGui.QPrinter.Portrait
        if self._reportEngine:
            result.update(self._reportEngine._parametersModel.itemsAsDict())
        return result

    
    def addParameterToSection(self, sectionName = 'header'):
        editWidget = self.tedtHeaderSection
        if sectionName == 'footer':
            editWidget = self.tedtFooterSection
        
        dlg = CParameterInserter(self)
        dlg.setParametersModel(self.tblParameters.model())
        if dlg.exec_():
            cursor = editWidget.textCursor()
            cursor.insertText(dlg.name())
            editWidget.setTextCursor(cursor)
    
    
    @QtCore.pyqtSlot()
    def acceptClick(self):
        if self._isDirty:
            userAnswer = QtGui.QMessageBox.information(self, 
                                                       u'Есть несохраненные данные', 
                                                       u'Хотите сохранить настройки отчета в файл шаблона перед продолжением?', 
                                                       buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel, 
                                                       defaultButton=QtGui.QMessageBox.Cancel)
            if userAnswer == QtGui.QMessageBox.Cancel:
                return
            if userAnswer == QtGui.QMessageBox.Yes:
                self.saveSettings()
            self.updateAdditionalSectionInEngine('header')
            self.updateAdditionalSectionInEngine('footer')
            self.updateMainTableInEngine()
            self.accept()
    
    
    #Надо оптимизировать
    @QtCore.pyqtSlot()
    def saveSettings(self):
        if not self.isDirty():
            return True
        
        fileName = self.loadedFileName
        if not fileName:
            return False
        self.updateAdditionalSectionInEngine('header')
        self.updateAdditionalSectionInEngine('footer')
        self.updateMainTableInEngine()
        self._reportEngine.storeTemplateToFile(fileName)
        self.setDirty(False)
        return True
    
    
    @QtCore.pyqtSlot()
    def updateAdditionalSectionInEngine(self, sectionName = 'header'):
        editWidget = self.tedtHeaderSection
        groupWidget = self.gbHeaderSection
        if sectionName == 'footer':
            editWidget = self.tedtFooterSection
            groupWidget = self.gbFooterSection
        elif sectionName != 'header':
            sectionName = 'header'
        
        document = editWidget.document().clone(self)
        setBorderForAllTablesInDocument(document, 0)
        
        self._reportEngine.setSetting(sectionName + 'SectionEnabled', groupWidget.isChecked())
        self._reportEngine.setSetting(sectionName + 'SectionHtml', document.toHtml())
    
    
    @QtCore.pyqtSlot()
    def updateMainTableInEngine(self):
        self._reportEngine.setSetting('mainTable_isTranspose', self.chkTranspose.isChecked())
        for column in xrange(self.mainTableColumns.columnCount()):
            itemData = self.mainTableColumns.item(0, column)
            itemTotal = self.mainTableColumns.item(1, column)
            self._reportEngine.setSetting('mainTable_columnsWidth_%d' % column, self.mainTableColumns.columnWidth(column))
            if itemData:
                self._reportEngine.setSetting('mainTable_columnsFontFamily_%d' % column, itemData.font().family())
                self._reportEngine.setSetting('mainTable_columnsFontSize_%d' % column, itemData.font().pointSize())
                self._reportEngine.setSetting('mainTable_columnsFontBold_%d' % column, itemData.font().bold())
                self._reportEngine.setSetting('mainTable_columnsFontItalic_%d' % column, itemData.font().italic())
                self._reportEngine.setSetting('mainTable_columnsFontUnderline_%d' % column, itemData.font().underline())
                self._reportEngine.setSetting('mainTable_columnsAlignment_%d' % column, itemData.textAlignment())
            if itemTotal:
                self._reportEngine.setSetting('mainTable_columnsTotalText_%d' % column, itemTotal.text())
                self._reportEngine.setSetting('mainTable_columnsTotalIsCalc_%d' % column, itemTotal.checkState() == QtCore.Qt.Checked)
    
    
    
    @QtCore.pyqtSlot()
    def updateQueryStmt(self):
        self.tedtQueryStmt.setPlainText(self._reportEngine.executeStmt())
    
    
    @QtCore.pyqtSlot()
    def updatePreview(self):
        if self.isDirty():
            self.updateAdditionalSectionInEngine('header')
            self.updateAdditionalSectionInEngine('footer')
            self.updateMainTableInEngine()
        params = self._reportEngine.parametersNameList()
        self.tedtPreview.setDocument(self._reportEngine.buildDocument(params, True).clone(self.tedtPreview))
    
    
    def initSections(self):
        def processTableInDocument(document):
            table = firstTextTableFromDocument(document)
            
            if not table:
                defaultTableFormat = QtGui.QTextTableFormat()
                defaultTableFormat.setBorder(1)
                defaultTableFormat.setWidth(QtGui.QTextLength(QtGui.QTextLength.PercentageLength, 100))
                defaultTableFormat.setAlignment(QtCore.Qt.AlignCenter)
                cursor = QtGui.QTextCursor(document)
                table = cursor.insertTable(1, 1, defaultTableFormat)
            return table
        #end processTableInDocument
        
        self.gbHeaderSection.setChecked(self._reportEngine.getSetting('headerSectionEnabled', 'False') == 'True')
        self.tedtHeaderSection.setHtml(self._reportEngine.getSetting('headerSectionHtml', ''))
        table = processTableInDocument(self.tedtHeaderSection.document())
        self.spbHeaderRowCount.setValue(table.rows())
        self.spbHeaderColumnCount.setValue(table.columns())
        setBorderForAllTablesInDocument(self.tedtHeaderSection.document(), 1)
        
        self.gbFooterSection.setChecked(self._reportEngine.getSetting('footerSectionEnabled', 'False') == 'True')
        self.tedtFooterSection.setHtml(self._reportEngine.getSetting('footerSectionHtml', ''))
        table = processTableInDocument(self.tedtFooterSection.document())
        self.spbFooterRowCount.setValue(table.rows())
        self.spbFooterColumnCount.setValue(table.columns())
        setBorderForAllTablesInDocument(self.tedtFooterSection.document(), 1)
    
    
    def initMainTableSetting(self):
        #Получаем список из набора имен каждого столбца
        columnsNames = self._reportEngine.mainTableColumnsNames()
        self.mainTableColumns.setColumnCount(len(columnsNames))
        self.mainTableColumns.setRowCount(2)
        columnNameList = []
        
        for column, fieldNames in enumerate(columnsNames):
            columnName = ''
            #Находим последнее непустое имя для столбца
            for row in xrange(len(fieldNames) - 1, -1, -1):
                columnName = fieldNames[row]
                if columnName:
                    break
            columnNameList.append(columnName)
            columnWidth = forceInt(self._reportEngine.getSetting('mainTable_columnsWidth_%d' % column, '0'))
            if columnWidth > 0:
                self.mainTableColumns.setColumnWidth(column, columnWidth)
            
            itemData = QtGui.QTableWidgetItem(u'данные %d столбца' % column)
            itemFont = itemData.font()
            itemFontFamily = self._reportEngine.getSetting('mainTable_columnsFontFamily_%d' % column, '')
            if itemFontFamily:
                itemFont.setFamily(itemFontFamily)
            itemFontSizeString  = self._reportEngine.getSetting('mainTable_columnsFontSize_%d' % column, '')
            if itemFontSizeString: 
                itemFont.setPointSize(forceInt(itemFontSizeString))
            itemFont.setBold(self._reportEngine.getSetting('mainTable_columnsFontBold_%d' % column, 'False') == 'True')
            itemFont.setItalic(self._reportEngine.getSetting('mainTable_columnsFontItalic_%d' % column, 'False') == 'True')
            itemFont.setUnderline(self._reportEngine.getSetting('mainTable_columnsFontUnderline_%d' % column, 'False') == 'True')
            itemData.setFont(itemFont)
            itemAlignment = forceInt(self._reportEngine.getSetting('mainTable_columnsAlignment_%d' % column, QtCore.Qt.AlignCenter))
            itemData.setTextAlignment(itemAlignment)
            itemData.setFlags(itemData.flags() & ~QtCore.Qt.ItemIsEditable)
            self.mainTableColumns.setItem(0, column, itemData)
            
            totalText = self._reportEngine.getSetting('mainTable_columnsTotalText_%d' % column, None)
            if totalText is None:
                totalText = u'Итого:' if column == 0  else ''
            itemTotal = QtGui.QTableWidgetItem(totalText)
            totalIsCalc = self._reportEngine.getSetting('mainTable_columnsTotalIsCalc_%d' % column, 'False') == 'True'
            itemTotal.setCheckState(QtCore.Qt.Checked if totalIsCalc else QtCore.Qt.Unchecked)
            itemFont.setBold(True)
            itemTotal.setFont(itemFont)
            itemTotal.setTextAlignment(itemAlignment)
            self.mainTableColumns.setItem(1, column, itemTotal)
            
        self.mainTableColumns.setHorizontalHeaderLabels(columnNameList)
        
            
    
    @QtCore.pyqtSlot(QtGui.QFont)
    def setFontForSelectedMainTableItem(self, font):
        for item in self.mainTableColumns.selectedItems():
            headerItem = self.mainTableColumns.horizontalHeaderItem(item.column())
            itemData = self.mainTableColumns.item(0, item.column())
            totalItem = self.mainTableColumns.item(1, item.column())
            assert item
            if itemData:
                itemData.setFont(font)
            if headerItem:
                headerItem.setFont(font)
            if totalItem:
                totalItem.setFont(font)
    
    
    @QtCore.pyqtSlot(int)
    def setAlignmentForSelectedMainTableItem(self, alignment):
        for item in self.mainTableColumns.selectedItems():
            headerItem = self.mainTableColumns.horizontalHeaderItem(item.column())
            totalItem = self.mainTableColumns.item(item.row(), item.column())
            assert item
            if item:
                item.setTextAlignment(alignment)
            if headerItem:
                headerItem.setTextAlignment(alignment)
            if totalItem:
                totalItem.setFont(alignment)

    
    @QtCore.pyqtSlot(int)
    def changeHeaderSectionRowCount(self, rowCount):
        resizeTextTableInDocument(self.tedtHeaderSection.document(), rowCount, None)
        self.markAsDirty()


    @QtCore.pyqtSlot(int)
    def changeHeaderSectionColumnCount(self, columnCount):
        resizeTextTableInDocument(self.tedtHeaderSection.document(), None, columnCount)
        self.markAsDirty()
    
    @QtCore.pyqtSlot(int)
    def changeFooterSectionRowCount(self, rowCount):
        resizeTextTableInDocument(self.tedtFooterSection.document(), rowCount, None)
        self.markAsDirty()


    @QtCore.pyqtSlot(int)
    def changeFooterSectionColumnCount(self, columnCount):
        resizeTextTableInDocument(self.tedtFooterSection.document(), None, columnCount)
        self.markAsDirty()    
    
        
    @QtCore.pyqtSlot()
    def on_tedtHeaderSection_cursorPositionChanged(self):
        cursor = self.tedtHeaderSection.textCursor()
        self.textAppearanceEditor.setFont(cursor.charFormat().font())
        self.textAppearanceEditor.setAlignment(cursor.blockFormat().alignment())
        
        
    @QtCore.pyqtSlot()
    def on_tedtFooterSection_cursorPositionChanged(self):
        cursor = self.tedtFooterSection.textCursor()
        self.textAppearanceEditor.setFont(cursor.charFormat().font())
        self.textAppearanceEditor.setAlignment(cursor.blockFormat().alignment())


    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, index):
        if index == self.tiPreview: #preview
            self.updatePreview()
        elif index == self.tiQueryStmt:
            self.updateQueryStmt()
    
    
    @QtCore.pyqtSlot(int)    
    def on_cmbTemplateFile_currentIndexChanged(self, index):
        fileName = forceString(self.cmbTemplateFile.itemData(index).toString())
        self.loadTemplateFile(fileName)
        
        
    
    @QtCore.pyqtSlot()
    def on_btnBrowseInputFile_clicked(self):
        fileName = forceString(QtGui.QFileDialog.getOpenFileName(self, u'', filter = 'SQL Files (*.sql);; All files (*.*)'))
        if not fileName.isNull(): 
            self.loadTemplateFile(fileName)
        
    
    @QtCore.pyqtSlot(QtGui.QTableWidgetItem, QtGui.QTableWidgetItem)
    def on_mainTableColumns_currentCellChanged(self, currentItem, previousItem):
        if currentItem:
            self.textAppearanceEditor.setFont(currentItem.font())
            if currentItem.row() == 0:
                self.textAppearanceEditor.setAlignment(currentItem.textAlignment())
        
    
    
    @QtCore.pyqtSlot()
    def on_btnAddToHeader_clicked(self):
        self.addParameterToSection('header')
    
    
    
    @QtCore.pyqtSlot()
    def on_actAddParameterToFooter_triggered(self):
        self.addParameterToSection('footer')
        
        
    @QtCore.pyqtSlot()
    def on_actAddQueryValueToFooter_triggered(self):
        pass


    @QtCore.pyqtSlot()
    def addAmountInWordsToFooter(self):
        dlg = QtGui.QDialog(self)
        dlg.setWindowTitle(u'Параметры')
        mainLayout = QtGui.QVBoxLayout()

        # Блок указания столбца
        subLayout = QtGui.QHBoxLayout()
        columnCountPromptLabel = QtGui.QLabel(u'Укажите &номер столбца,\n'
                                              u'итоговые данные которого\n'
                                              u'вы планируете вывести прописью')
        columnCountValue = QtGui.QSpinBox()
        columnCount = self.mainTableColumns.columnCount()
        columnCountValue.setRange(min(1, columnCount),
                                    columnCount)
        columnCountValue.setValue(columnCount)
        columnCountPromptLabel.setBuddy(columnCountValue)
        subLayout.addWidget(columnCountPromptLabel)
        subLayout.addWidget(columnCountValue)
        mainLayout.addLayout(subLayout)

        #Блок указания параметров ед. измерения
        subLayout = QtGui.QGridLayout()
        sexList = [(u'Мужской', u'm'),
                   (u'Женский', u'f'),
                   (u'Средний', u'n')]
        unitGroupBox = QtGui.QGroupBox(u'Параметры ед. измерения')
        onePieceLabel = QtGui.QLabel(u'Одна ед.')
        twoPieceLabel = QtGui.QLabel(u'Две ед.')
        muchPieceLabel = QtGui.QLabel(u'Много ед.')
        sexLabel = QtGui.QLabel(u'Род')
        integralPartLabel = QtGui.QLabel(u'Целая часть')
        fractionalPartLabel = QtGui.QLabel(u'Дробная часть')

        oneIntegralPiece = QtGui.QLineEdit(u'рубль')
        twoIntegralPiece = QtGui.QLineEdit(u'рубля')
        muchIntegralPiece = QtGui.QLineEdit(u'рублей')
        sexIntegralValue = QtGui.QComboBox()
        sexIntegralValue.addItems([i[0] for i in sexList])
        sexIntegralValue.setCurrentIndex(0)

        oneFractionalPiece = QtGui.QLineEdit(u'копейка')
        twoFractionalPiece = QtGui.QLineEdit(u'копейки')
        muchFractionalPiece = QtGui.QLineEdit(u'копеек')
        sexFractionalValue = QtGui.QComboBox()
        sexFractionalValue.addItems([i[0] for i in sexList])
        sexFractionalValue.setCurrentIndex(1)

        subLayout.addWidget(onePieceLabel, 0, 1)
        subLayout.addWidget(twoPieceLabel, 0, 2)
        subLayout.addWidget(muchPieceLabel, 0, 3)
        subLayout.addWidget(sexLabel, 0, 4)

        subLayout.addWidget(integralPartLabel, 1, 0)
        subLayout.addWidget(oneIntegralPiece, 1, 1)
        subLayout.addWidget(twoIntegralPiece, 1, 2)
        subLayout.addWidget(muchIntegralPiece, 1, 3)
        subLayout.addWidget(sexIntegralValue, 1, 4)

        subLayout.addWidget(fractionalPartLabel, 2, 0)
        subLayout.addWidget(oneFractionalPiece, 2, 1)
        subLayout.addWidget(twoFractionalPiece, 2, 2)
        subLayout.addWidget(muchFractionalPiece, 2, 3)
        subLayout.addWidget(sexFractionalValue, 2, 4)

        unitGroupBox.setLayout(subLayout)

        mainLayout.addWidget(unitGroupBox)

        #Блок кнопок управления
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dlg.accept)
        buttonBox.rejected.connect(dlg.reject)
        mainLayout.addWidget(buttonBox)

        dlg.setLayout(mainLayout)

        if dlg.exec_():
            text = u'{:%(column)s' \
                  u':(%(oneIntegralPiece)s, %(twoIntegralPiece)s, %(muchIntegralPiece)s, %(sexIntegral)s)' \
                  u':(%(oneFractionalPiece)s, %(twoFractionalPiece)s, %(muchFractionalPiece)s, %(sexFractional)s)}'
            text = text % {u'column' : columnCountValue.value(),
                           u'oneIntegralPiece' : oneIntegralPiece.text(),
                           u'twoIntegralPiece' : twoIntegralPiece.text(),
                           u'muchIntegralPiece' : muchIntegralPiece.text(),
                           u'sexIntegral' : sexList[sexIntegralValue.currentIndex()][1],
                           u'oneFractionalPiece' : oneFractionalPiece.text(),
                           u'twoFractionalPiece' : twoFractionalPiece.text(),
                           u'muchFractionalPiece' : muchFractionalPiece.text(),
                           u'sexFractional' : sexList[sexFractionalValue.currentIndex()][1]}
            cursor = self.tedtFooterSection.textCursor()
            cursor.insertText(text)
            self.tedtFooterSection.setTextCursor(cursor)






