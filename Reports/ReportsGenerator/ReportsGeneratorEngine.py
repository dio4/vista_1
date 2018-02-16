# -*- coding: utf-8 -*-
from library.AmountToWords import amountToWords
from library.Utils import forceInt, forceString, forceBool
from Reports.ReportsGenerator.TemplateParameter import CTemplateParameter

'''
Created on 26.02.2013

@author: atronah
'''

import re

from PyQt4 import QtGui, QtCore, QtSql

from Reports.ReportsGenerator.TemplateParametersModel import CTemplateParametersModel


def parseFields(fieldStmt):
    fieldsInfoList = []
    fieldPattern = re.compile(ur'(?s)(?i)(?P<name>.+)\s*(?:as\s+(?P<quote>\'|"|)(?P<alias>[^,]+)(?P=quote))')
    pos = 0
    bracketCount = 0
    bracesCount = 0
    qoutasFlag = False
    doubleQuotasFlag = False
    backSlashFlag = False 
    
    while pos < len(fieldStmt):
        c = fieldStmt[pos]
        if not backSlashFlag:
            if c == ',' and bracketCount == bracesCount == 0 and not qoutasFlag and not doubleQuotasFlag:
                fieldDescription = fieldStmt[:pos].strip(u'\t\n ')
                fieldMatch = fieldPattern.search(fieldDescription)
                if fieldMatch:
                    fieldsInfoList.append(fieldMatch.groupdict())
                fieldStmt = fieldStmt[pos  + 1 :]
                pos = 0
            elif c == '(':
                bracketCount += 1
            elif c == ')':
                bracketCount -= 1
            elif c == '{':
                bracesCount += 1
            elif c == '}':
                bracesCount -= 1
            elif c == '\'':
                qoutasFlag = not qoutasFlag
            elif c == '"':
                doubleQuotasFlag = not doubleQuotasFlag
            elif c == '\\':
                backSlashFlag = True
        else:
            backSlashFlag = False
        pos += 1
    if fieldStmt:
        fieldDescription = fieldStmt.strip(u'\t\n ')
        fieldMatch = fieldPattern.search(fieldDescription)
        if fieldMatch:
            fieldsInfoList.append(fieldMatch.groupdict())
    return fieldsInfoList



def parseFieldsBlock(queryStmt):
    def getBracketsCount(text, startIndex = 0):
        pos = startIndex
        bracketCount = 0
        bracesCount = 0
        qoutasFlag = False
        doubleQuotasFlag = False
        backSlashFlag = False
        
        while pos < len(text):
            c = queryStmt[pos]
            if not backSlashFlag:
                if c == '(':
                    bracketCount += 1
                elif c == ')':
                    bracketCount -= 1
                elif c == '{':
                    bracesCount += 1
                elif c == '}':
                    bracesCount -= 1
                elif c == '\'':
                    qoutasFlag = not qoutasFlag
                elif c == '"':
                    doubleQuotasFlag = not doubleQuotasFlag
                elif c == '\\':
                    backSlashFlag = True
            else:
                backSlashFlag = False
            pos += 1
        return (bracketCount, bracesCount, qoutasFlag, doubleQuotasFlag)
    #end getBracketsCount
    
    fieldsBlock = ''
    
    stmtLength = len(queryStmt)
    fromIndex = re.search(ur'(?i)(?:\s|^)+FROM(?:\s|$)+', queryStmt).start()
    while 0 < fromIndex < stmtLength:
        if getBracketsCount(queryStmt[:fromIndex]) == (0, 0, False, False):
            break
        fromIndex = queryStmt.find(' FROM ', fromIndex + 1)
    
    selectIndex = re.search(ur'(?i)(?:\s|^)+SELECT(?:\s|$)+', queryStmt).start()
    if 0 <= selectIndex < fromIndex < stmtLength:
        fieldsBlock = queryStmt[selectIndex + 7 : fromIndex]
    
    return fieldsBlock


def removeEmptyLine(text):
    emptyLinePattern = re.compile(ur'\n\s*\n')
    emptyLineSearch = emptyLinePattern.search(text)
    while emptyLineSearch:
        text = text[:emptyLineSearch.start()] + text[emptyLineSearch.end() - 1:]
        emptyLineSearch = emptyLinePattern.search(text)
    return text


class CReportsGeneratorEngine(QtCore.QObject):
    """
    Позволяет генерировать отчет на основе файла-шаблона, содержащего параметризируемый SQL-запрос
    и дополнительные опции отображения. Итоговый отчет состоит из заголовочной секции; секции основной таблицы,
    дублирующей результат запроса, и конечной секции. Заголовочная и конечная секции могут быть заполнены произвольными данными.
    """
#    __pyqtSignals__ = ()
    
    def __init__(self):
        self._fieldInfoList = []
        #Текст шаблона пригодный выполнения в качестве запроса (с исключенными вспомогательными данным, такими, как настройки отчета)
        self._stmtForExecute = u''
        self._mainTableInfo = {}
        self._settingsInfo = {}
        self._queryExecuter = None
        self._parametersModel = CTemplateParametersModel()
#        self._headerSectionModel = CReportAdditionalSectionModel()
#        self._footerSectionModel = CReportAdditionalSectionModel()
    
    #typeIndex - тип сексии
    # 0 - Верхняя/Заголовочная/Header секция
    # 1 - Нижняя/Заключительная/Footer секция
    def additionalSection(self, typeIndex):
        if type == 0:
            return self._headerSectionModel
        else:
            return self._footerSectionModel
            
    
    def executeStmt(self):
        stmt = CTemplateParameter.transcriptParameters(self._stmtForExecute, self._parametersModel.itemsAsDict())
        return stmt
    
    
    def clear(self):
        self._parametersNameList = []
        self._fieldInfoList = []
        self._stmtForExecute = u''
        self._mainTableInfo.clear()
        self._settingsInfo.clear()
        self._parametersModel.clear()
#        self._headerSectionModel.clear()
#        self._footerSectionModel.clear()
    
    
    def loadTemplateFromFile(self, fileName):
        import os
        if not( os.path.exists(fileName) and os.path.isfile(fileName)):
#            print 'exist: %s    isfile: %s    name: %s' % (os.path.exists(fileName), os.path.isfile(fileName), fileName)
            return False
        
        with open(fileName, "r") as loadFile:
            try:
                templateSourceText = forceString(loadFile.read().decode('utf-8'))
                self.loadTemplate(templateSourceText)
            except UnicodeDecodeError:
                QtGui.QMessageBox.critical(
                    None,
                    u'Ошибка',
                    u'В имени файла не должны присутствовать символы кирилицы: %s' % fileName,
                    buttons=QtGui.QMessageBox.Close
                )
                return False

        return True
        
    
    def loadTemplate(self, sourceText):
        self.clear()
        
        for paramDescription in CTemplateParameter.parseParametersFromText(sourceText):
            self._parametersModel.addItemByDescription(paramDescription)
        
        
        selectPattern = re.compile(ur'(?s)(?i)SELECT.+FROM.*')
        selectStmtMatch = selectPattern.search(sourceText)
        
        
        selectStmt = selectStmtMatch.group() if selectStmtMatch else ''
        
        self._stmtForExecute = self.loadSettingsFromText(sourceText) if selectStmt else ''
        
        
        fieldsInStmt = parseFieldsBlock(selectStmt)
        
        self._fieldInfoList = parseFields(fieldsInStmt)
        
        
        #----loading main table info
        
        headColumnCount = len(self._fieldInfoList)
        headRowCount = 0
        
        mergeInfo = {} #словарь, хранящий информацию о слиянии ячеек в формате mergeInfo[(row, column)] = [rowCount, columnCount]
        prevFieldNames = [] #список имен предыдущего столбца
        mergeColumnsCountList = [] # список счетчиков количества сливаемых столбцов для каждой строки
        notFillHeadCells = [] # список ячеек (строка, столбец), в которые не надо писать текст, так как они будут слиты с другими ячейками
        for column, fieldInfo in enumerate(self._fieldInfoList):
            #каждый столбец таблицы представлен списком имен его строк (одно имя для "одноэтажной шапки")
            fieldNames = [fieldInfo['name']]
            if fieldInfo['alias'] is not None:
                #Список имен получается разбиением псевдонима на фрагменты, разделенные точкой
                fieldNames = fieldInfo['alias'].split('.')
            #Вычисление максимальной "этажности" шапки
            headRowCount = max(headRowCount, len(fieldNames))
            
            fieldNames.extend([''] * (headRowCount - len(fieldNames)))
            if prevFieldNames:
                prevFieldNames.extend([''] * (len(fieldNames) - len(prevFieldNames)))
            
            while headRowCount > len(mergeColumnsCountList):
                mergeColumnsCountList.append(1)
            
            #Количество слияемых строк (0, а не 1 на случай, если первое имя окажется пустым)
            mergeRowsCount = 0
            #для каждого строки шапки (row) c именем столбца (fieldName) 
            for row, fieldName in enumerate(fieldNames):
                if fieldName == '':         #Пустое имя означает, что текущая строка шапки сливается с предыдущей 
                    mergeRowsCount += 1
                else: #Если найдено очередное не пустое имя
                    if mergeRowsCount > 1: #то, если количество слияемых строк больше 1
                        #Произвести слияение предыдущих строк
                        mergeInfo.setdefault((row - mergeRowsCount + 1, column), [1, 1])[0] = mergeRowsCount
                    mergeRowsCount = 1 #вернуть значение счетчика слияемых строк к начальному значению
                #Если текущее имя (в текущей строке) столбца равно тому же имени (в той же строке) предыдущего столбца 
                if prevFieldNames and fieldName == prevFieldNames[row]:
                    mergeColumnsCountList[row] += 1
                    notFillHeadCells.append((row, column))
                else:
                    if mergeColumnsCountList[row] > 1:
                        mergeInfo.setdefault((row, max(0, column - mergeColumnsCountList[row])), [1, 1])[1] = mergeColumnsCountList[row]
                    mergeColumnsCountList[row] = 1
            #end cycle on rows (fieldNames)
            
            #учесть конечные слияемые строки, которые не могли быть учитаны в цикле
            if mergeRowsCount > 1:
                mergeInfo.setdefault((row - mergeRowsCount + 1, column), [1, 1])[0] = mergeRowsCount
            
            prevFieldNames = fieldNames
        #end of cycle on columns (fieldInfoList)
        
        #учесть конечные слияемые столбцы, которые не могли быть учитаны в цикле
        for row, mergeColumnsCount in enumerate(mergeColumnsCountList):
            if mergeColumnsCount > 1:
                mergeInfo.setdefault((row, max(0, headColumnCount - mergeColumnsCount)), [1, 1])[1] = mergeColumnsCount
        
        #------store main table info
        self._mainTableInfo = {'headColumnCount' : headColumnCount,
                               'headRowCount': headRowCount,
                               'mergeInfo' : mergeInfo,
                               'notFillHeadCells' : notFillHeadCells,
                               }

    
    def storeTemplateToText(self):
        result = '\n'.join([self.storeSettingsToText(), self._stmtForExecute])
        return result
    
    
    def storeTemplateToFile(self, fileName):
        if not fileName:
            return False

        with open(fileName, 'w') as outFile:
            text = self.storeTemplateToText()
            outFile.write(text.encode('utf-8'))
        
        return True
    
    
    def parametersNameList(self):
        return self._parametersNameList
    
    
    #Загружает настройки отчета и возвращает шаблон, из которого вырезаны все найденные настройки
    def loadSettingsFromText(self, sourceText, namePartDelimiter = '_' ):
        self._settingsInfo = {}
        settingsPattern = re.compile(ur'(?s)(?i)(?:/\*\*([\w\d]+?)=(.*?)\*/)+')
        settingsSearch = settingsPattern.search(sourceText)
        while settingsSearch:
            settingName = settingsSearch.group(1)
            settingValue = settingsSearch.group(2)
            self.setSetting(settingName, settingValue, namePartDelimiter)
            sourceText = sourceText[:settingsSearch.start()] + sourceText[settingsSearch.end():]
            settingsSearch = settingsPattern.search(sourceText)
        
        return removeEmptyLine(sourceText)
        
        
    def storeSettingsToText(self, namePartDelimiter = '_'):
        needProcessingDict = {'' : self._settingsInfo}
        settingsList = []
        
        while needProcessingDict:
            currentNodeName, currentNodeValue = needProcessingDict.popitem()
            if isinstance(currentNodeValue, dict):
                for item in currentNodeValue.items():
                    itemName = currentNodeName + namePartDelimiter + item[0] if currentNodeName else item[0]
                    needProcessingDict[itemName] = item[1]
            else:
                settingsList.append('/**%s=%s*/' % (currentNodeName, currentNodeValue))
        
        return '\n'.join(settingsList)
    
    
    def setSetting(self, settingName, settingValue, namePartDelimiter = '_' ):
        currentDict = self._settingsInfo
        settingNamePartsList = settingName.split(namePartDelimiter)
        lastSettingNamePart = None
        for depth, settingNamePart in enumerate(settingNamePartsList):
            if depth < (len(settingNamePartsList) - 1):
                currentDict = currentDict.setdefault(settingNamePart, {})
            else:
                lastSettingNamePart = settingNamePart
        
        currentDict[lastSettingNamePart] = forceString(settingValue)
    
    
    def getSetting(self, settingName, defaultValue = None, namePartDelimiter = '_' ):
        value  = defaultValue
        currentDict = self._settingsInfo
        settingNamePartsList = settingName.split(namePartDelimiter)
        for depth, settingNamePart in enumerate(settingNamePartsList):
            if not currentDict.has_key(settingNamePart):
                return value
            if depth < (len(settingNamePartsList) - 1):
                currentDict = currentDict.get(settingNamePart, {})
            else:
                value = currentDict.get(settingNamePart, defaultValue)
        
        return value
    
    
    def mainTableColumnsNames(self):
        result = []
        #каждый столбец таблицы представлен списком имен его строк (одно имя для "одноэтажной шапки")
        for fieldInfo in self._fieldInfoList:
            #Список имен получается разбиением псевдонима на фрагменты, разделенные точкой
            result.append(fieldInfo['alias'].split('.') if fieldInfo['alias'] else [ fieldInfo['name'] ])
        return result
            
    
    def setQueryExecuter(self, executer):
        if callable(executer):
            self._queryExecuter = executer
    
    
    def query(self, stmt):
        if not self._queryExecuter:
            return QtSql.QSqlQuery()
        return self._queryExecuter(stmt)
            
    
    def buildDocument(self, params, onlyStructure = True):
        
        def appendRows(mainTable, count, transpose):
            if transpose:
                row = mainTable.columns()
                mainTable.insertColumns(row, count) #вставляем столбцы, но переменная остается называться row, так как по сути мы добавляем строку, но повернутую на 90 градусов
            else:
                row = mainTable.rows()
                mainTable.insertRows(row, count)
            return row + count - 1
        #end appendRows
        
        def getCellCursor(mainTable, row, column, transpose):
            return mainTable.cellAt(row if not transpose else column,
                                    column if not transpose else row).firstCursorPosition()
        #end getCellCursor
        
        
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        
    #---- Header section start
        if self.getSetting('headerSectionEnabled', 'False') == 'True':
            cursor.insertBlock()
            htmlText = CTemplateParameter.transcriptParameters(self.getSetting('headerSectionHtml', ''), 
                                                               self._parametersModel.itemsAsDict())
            cursor.insertFragment(QtGui.QTextDocumentFragment.fromHtml(htmlText))
#            cursor.movePosition(QtGui.QTextCursor.PreviousBlock)
#            table = cursor.currentTable()
#            if table:
#                tableFormat = table.format()
#                tableFormat.setBorder(0)
#                table.setFormat(tableFormat)
            cursor.movePosition(QtGui.QTextCursor.End)
    #---- Header section end
        
    #---- Main table section start
        transpose = forceBool(self.getSetting('mainTable_isTranspose', 'False') == 'True')
        
        headRowCount = self._mainTableInfo.get('headRowCount', 0)
        headColumnCount = self._mainTableInfo.get('headColumnCount', 0)
        if headRowCount > 0 and headColumnCount > 0:
            mergeInfo = self._mainTableInfo.get('mergeInfo', {})
            notFillHeadCells = self._mainTableInfo.get('notFillHeadCells', [])
            tableFormat = QtGui.QTextTableFormat()
           
                
            if transpose: #Если транспонирована
                tableFormat.setHeaderRowCount(0)
            else:
                columnsWidthConstraint = []
                for column in xrange(headColumnCount):
                    columnWidth = forceInt(self.getSetting('mainTable_columnsWidth_%d' % column, '0'))
                    if columnWidth > 0:
                        textLength = QtGui.QTextLength(QtGui.QTextLength.FixedLength, columnWidth)
                    else:
                        textLength = QtGui.QTextLength(QtGui.QTextLength.VariableLength, 0)
                    columnsWidthConstraint.append(textLength)
                tableFormat.setColumnWidthConstraints(columnsWidthConstraint)
                tableFormat.setHeaderRowCount(headRowCount)
            
            tableFormat.setAlignment(QtCore.Qt.AlignCenter)     
            mainTable = cursor.insertTable(headRowCount if not transpose else headColumnCount, 
                                           headColumnCount if not transpose else headRowCount, tableFormat)
            
            
            cellCharFormatList = []
            cellBlockFormatList = []
            totalTextList = []
            totalIsCalcList = []
            for column, fieldNames in enumerate(self.mainTableColumnsNames()):
                cellCharFormat = QtGui.QTextCharFormat()
                itemFontFamily = self.getSetting('mainTable_columnsFontFamily_%d' % column, '')
                if itemFontFamily:
                    cellCharFormat.setFontFamily(itemFontFamily)
                itemFontSizeString  = self.getSetting('mainTable_columnsFontSize_%d' % column, '')
                if itemFontSizeString: 
                    cellCharFormat.setFontPointSize(forceInt(itemFontSizeString))
                cellCharFormat.setFontWeight(QtGui.QFont.Bold if self.getSetting('mainTable_columnsFontBold_%d' % column, 'False') == 'True' else QtGui.QFont.Normal)
                cellCharFormat.setFontItalic(self.getSetting('mainTable_columnsFontItalic_%d' % column, 'False') == 'True')
                cellCharFormat.setFontUnderline(self.getSetting('mainTable_columnsFontUnderline_%d' % column, 'False') == 'True')
                cellCharFormatList.append(cellCharFormat)
                headCellCharFormat = QtGui.QTextCharFormat(cellCharFormat)
                headCellCharFormat.setFontWeight(QtGui.QFont.Bold)
                cellBlockFormat = QtGui.QTextBlockFormat()
                alignmentInt = forceInt(self.getSetting('mainTable_columnsAlignment_%d' % column, QtCore.Qt.AlignCenter))
                cellBlockFormat.setAlignment(QtCore.Qt.Alignment(alignmentInt))
                cellBlockFormatList.append(cellBlockFormat)
                
                totalTextList.append(self.getSetting('mainTable_columnsTotalText_%d' % column, ''))
                totalIsCalcList.append(self.getSetting('mainTable_columnsTotalIsCalc_%d' % column, 'False') == 'True')

                
                #Заполнение шапки таблицы
                for row, fieldName in enumerate(fieldNames):
                    if fieldName and (row, column) not in notFillHeadCells:
                        cellCursor = getCellCursor(mainTable, row, column, transpose)
                        cellCursor.setBlockFormat(cellBlockFormat)
                        cellCursor.insertText(fieldName.replace('_', ' '), headCellCharFormat)
            
            
            
            if onlyStructure or self._queryExecuter is None:
                row = appendRows(mainTable, 2, transpose)
                
                for column in xrange(mainTable.columns() if not transpose else mainTable.rows()):
                    #Вывод строки данных
                    cellCursor = getCellCursor(mainTable, row - 1, column, transpose)
                    cellCursor.setBlockFormat(cellBlockFormatList[column])
                    cellCursor.insertText(u'данные %d столбца' % column, cellCharFormatList[column])
                    
                    #Вывод строки "Итого"
                    cellCursor = getCellCursor(mainTable, row, column, transpose)
                    cellCursor.setBlockFormat(cellBlockFormatList[column])
                    totalCharFormat = QtGui.QTextCharFormat(cellCharFormatList[column])
                    totalCharFormat.setFontWeight(QtGui.QFont.Bold)
                    totalText = totalTextList[column]
                    if totalIsCalcList[column]:
                        totalText = u'<сумма> %s' % totalText
                    cellCursor.insertText(totalText, totalCharFormat)
            else:
                stmt = self.executeStmt()
                isUnresolvedParamsExists = False
                if CTemplateParameter.parseParametersFromText(stmt):
                    isUnresolvedParamsExists = True

                if isUnresolvedParamsExists:
                    row = appendRows(mainTable, 1, transpose)
                    cellCursor = getCellCursor(mainTable, row, column, transpose)
                    cellCursor.setBlockFormat(cellBlockFormatList[column])
                    cellCursor.insertText(u'обнаружены нераскрытые параметры', cellCharFormatList[column])
                else:
                    query = self.query(stmt.strip())
                    totalCounterList = [0] * mainTable.columns()
                    while query.next():
                        record = query.record()
                        row = appendRows(mainTable, 1, transpose)
                        for column in xrange(record.count()):
                            cellCursor = getCellCursor(mainTable, row, column, transpose)
                            cellCursor.setBlockFormat(cellBlockFormatList[column])
                            value = record.value(column)
                            if totalIsCalcList[column]:
                                totalCounterList[column] += value.toInt()[0] if value.type() == QtCore.QVariant.Int else value.toDouble()[0]
                            cellCursor.insertText(value.toString(), cellCharFormatList[column])
                    
                    if True in totalIsCalcList:
                        row = mainTable.rows()
                        mainTable.insertRows(row, 1)
                        for column in xrange(mainTable.columns()):
                            cellCursor = getCellCursor(mainTable, row, column, transpose)
                            cellCursor.setBlockFormat(cellBlockFormatList[column])
                            totalCharFormat = QtGui.QTextCharFormat(cellCharFormatList[column])
                            totalCharFormat.setFontWeight(QtGui.QFont.Bold)
                            totalText = totalTextList[column]
                            if totalIsCalcList[column]:
                                totalText = u'%s %s' % (totalCounterList[column], totalText)
                            cellCursor.insertText(totalText, totalCharFormat)
                            
                            
            for mergeCell in mergeInfo.keys():
                row, column = mergeCell
                rowCount, columnCount = mergeInfo[mergeCell]
                if transpose:
                    mainTable.mergeCells(column, row, columnCount, rowCount)
                else:
                    mainTable.mergeCells(row, column, rowCount, columnCount)
    #---- Main table section end
        
        cursor.movePosition(QtGui.QTextCursor.End)
    #---- Footer section start
        if self.getSetting('footerSectionEnabled', 'False') == 'True':
            htmlText = CTemplateParameter.transcriptParameters(self.getSetting('footerSectionHtml', ''), 
                                                               self._parametersModel.itemsAsDict())
            htmlText = self.addAmountInWords(htmlText, mainTable)
            cursor.insertFragment(QtGui.QTextDocumentFragment.fromHtml(htmlText))
#            cursor.movePosition(QtGui.QTextCursor.PreviousBlock)
#            table = cursor.currentTable()
#            if table:
#                tableFormat = table.format()
#                tableFormat.setBorder(0)
#                table.setFormat(tableFormat)
    #---- Footer section end
        return doc


    @staticmethod
    def addAmountInWords(source, mainTable):
        def replacer(match):
            resultText = u''
            if not match:
                return u''
            column = match.group(1)
            cell = mainTable.cellAt(mainTable.rows() - 1,
                                    (column if column in xrange(mainTable.columns())\
                                            else mainTable.columns()) - 1)
            cellText = cell.firstCursorPosition().block().text()
            cellNumberList = re.findall(ur'\d+[.,]?\d*', cellText)
            if cellNumberList:
                cellNumber = float(cellNumberList[0].replace(',', '.'))
                resultText = amountToWords(cellNumber, ((match.group(2), match.group(3), match.group(4), match.group(5)),
                                                        ((match.group(6), match.group(7), match.group(8), match.group(9)))))
            return resultText

        # settingsPattern = re.compile(ur'\{:(\d+):\((\w+),\s*,(\w+),\s*,(\w+),\s*,(\w+),\s*\):\((\w+),\s*,(\w+),\s*,(\w+),\s*,(\w+),\s*\)\}')
        settingsPattern = re.compile(ur'\{:(\d+):\(([\wА-Яа-яёЁ]+),\s*([\wА-Яа-яёЁ]+),\s*([\wА-Яа-яёЁ]+),\s*([\wА-Яа-яёЁ]+)\s*\):\(([\wА-Яа-яёЁ]+),\s*([\wА-Яа-яёЁ]+),\s*([\wА-Яа-яёЁ]+),\s*([\wА-Яа-яёЁ]+)\s*\)\}')
        return settingsPattern.sub(replacer, source)

    
def main():
    settingsPattern = re.compile(ur'\{:(\d+):\(([\wА-Яа-яёЁ]+),\s*([\wА-Яа-яёЁ]+),\s*([\wА-Яа-яёЁ]+),\s*([\wА-Яа-яёЁ]+)\s*\):\(([\wА-Яа-яёЁ]+),\s*([\wА-Яа-яёЁ]+),\s*([\wА-Яа-яёЁ]+),\s*([\wА-Яа-яёЁ]+)\s*\)\}')
    print settingsPattern.findall(u'{:6:(Ё, ё, рублей, m):(копейка, копейки, копеек, f)}')
    return 0

    with open('c:\\Tmp\\q1.sql') as f:
        text = f.read().decode('utf-8')
    fieldsSearch = re.search(ur'(?s)(?i)SELECT(.*)FROM', text)
    fieldsInStmt = fieldsSearch.group(1) if fieldsSearch else ''
    print fieldsInStmt
    print '--------------'
    fieldInfoList = parseFields(fieldsInStmt)
    for i in  fieldInfoList: print '', ' # ', i['alias']
    return 0

if __name__ == '__main__':
    main()