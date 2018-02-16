# -*- coding: utf-8 -*-
import xml.dom.minidom
import zipfile
from PyQt4 import QtCore


# atronah: в сборках отсутствует модуль xml.etree
# Преобрзование числа Excel  в дату
def conversionDate(xldate):
    if xldate == 0.00:
        return QtCore.QDateTime(0, 0, 0, 0, 0, 0)
    xldays = int(xldate)
    frac = xldate - xldays
    seconds = int(round(frac * 86400.0))
    if seconds == 86400:
        hour = minute = second = 0
        xldays += 1
    else:
        # second = seconds % 60; minutes = seconds // 60
        minutes, second = divmod(seconds, 60)
        # minute = minutes % 60; hour    = minutes // 60
        hour, minute = divmod(minutes, 60)

    if xldays == 0:
        return QtCore.QDateTime(0, 0, 0, hour, minute, second)

    date = QtCore.QDateTime(1900, 3, 1, 0, 0, 0).addDays(xldays - 61)
    return QtCore.QDateTime(date.date().year(), date.date().month(), date.date().day(), hour, minute, second)


# Класс парсинга xlm-файлов, которые содержатся в zip-архиве файла .xlsx, в dom-объекты.
class CDomZipfile():
    # Открытие xlsx файла.
    # Аргументы: filename - имя открываемого файла
    def __init__(self, filename):
        self.zipFile = None
        if zipfile.is_zipfile(filename):
            file = zipfile.ZipFile(filename)
            workbookFile = 'xl/workbook.xml'
            if workbookFile in file.namelist():
                self.zipFile = file

    # Получение xml-документа из zip-архива.
    # Аргументы: item - путь до xlm-документа
    def __getitem__(self, item):
        return xml.dom.minidom.parseString(self.zipFile.read(item))

    # Закрытие zip-файла при окончании работы с ним
    def __del__(self):
        if self.zipFile:
            self.zipFile.close()


# Класс контейнера листов xlsx-документа, доступ к которым можно получить, либо по id, либо по наименованию
class CWorkbook():
    # Получение информации о xlsx-документе
    def __init__(self, filename):
        self.filename = filename
        self.sheetsById = {}
        self.sheetsByName = {}
        self.domZipfiles = CDomZipfile(self.filename)
        self.getSheets()
        try:
            self.sharedStrings = CSharedStrings(self.domZipfiles["xl/sharedStrings.xml"])
        except KeyError:
            self.sharedStrings = None
        self.styleSheet = self.domZipfiles["xl/styles.xml"]
        self.styleCells = (self.styleSheet.getElementsByTagName('cellXfs')[0].getElementsByTagName('xf'))

    # Закрытие zip-документа
    def close(self):
        self.domZipfiles.__del__()

    # Получение данных листа
    # Аргументы: item -  id или наименнование листа, данные которого получаем
    def __getitem__(self, item):

        if isinstance(item, int):
            return self.sheetsById[item]
        else:
            return self.sheetsByName[item]

    # Количество листов
    def __len__(self):
        return len(self.sheetsById)

    # Получение имен всех листов
    def keys(self):
        return self.sheetsByName.keys()

    # Получение информации о каждом из листов
    def getSheets(self):
        workbook = self.domZipfiles["xl/workbook.xml"]
        sheets = workbook.getElementsByTagName('sheets').pop()
        for sheetId, sheetNode in enumerate(sheets.childNodes):
            sheetId += 1
            name = sheetNode.attributes['name'].value
            sheet = CSheet(self, sheetId, name)
            self.sheetsById[sheetId] = sheet
            self.sheetsByName[name] = sheet


# Класс списка общих строк, содержащихся в xlsx-документе
class CSharedStrings(list):
    # Формирование списка общих строк
    def __init__(self, sharedStrings):
        cells = sharedStrings.getElementsByTagName('si')
        self.extend([self.cellText(cell) for cell in cells])

    # Предобразование 'SharedStringItem' в текст
    def cellText(self, cell):
        nodes = cell.getElementsByTagName('t')
        list = []
        for node in nodes:
            for child in node.childNodes:
                if child.nodeType == child.TEXT_NODE:
                    list.append(child.nodeValue)
        return ''.join(list)


# Класс листа
class CSheet():
    # Инициализация пустого несчитанного листа
    def __init__(self, workbook, id, name):
        self.workbook = workbook
        self.id = id
        self.name = name
        self.loaded = False
        self.columns = None
        self.rows = None

    # Получение строк листа
    def getRows(self):
        if not self.loaded:
            self.load()
        return self.rows

    # Получение колонок листа
    def getColumns(self):
        if not self.loaded:
            self.load()
        return self.columns

    # Считывание данных листа
    def load(self):
        rows = {}
        columns = {}
        data = self.loadRows()
        for indexRow, dataRow in data.items():
            rows[indexRow] = dataRow
            for indexColumn, value in enumerate(dataRow):
                indexColumn += 1
                if not indexColumn in columns:
                    columns[indexColumn] = []
                columns[indexColumn].append(value)
        self.rows = rows
        self.columns = columns
        self.loaded = True

    # Получить порядковый номер колонки
    # Аргуметры: columnChar - название колонки (например, А1)
    def getColumnNumber(self, columnChar):
        columnNum = 0
        for char in columnChar:
            columnNum += ord(char)
        columnNum -= (65)
        return columnNum

    # Считывание строк с листа
    def loadRows(self):
        sheet = self.workbook.domZipfiles["xl/worksheets/sheet%d.xml" % self.id]
        sheetData = sheet.getElementsByTagName('sheetData').pop()
        data = {}
        for rowNode in sheetData.childNodes:
            indexRow = int(rowNode.attributes['r'].value)
            rowCells = []
            for columnNode in rowNode.getElementsByTagName('c'):
                columnType = columnNode.attributes['t'].value if columnNode.hasAttribute('t') else None
                cellId = columnNode.attributes['r'].value if columnNode.hasAttribute('r') else None
                cellS = columnNode.attributes['s'].value if columnNode.hasAttribute('s') else None
                columnNum = self.getColumnNumber(cellId[:len(cellId) - len(str(indexRow))])
                value = None
                rowCells.append(value)
                try:
                    valueNode = columnNode.getElementsByTagName('v').pop().childNodes.pop()
                    if valueNode:
                        if int(cellS) == 16:
                            pass
                        if columnType == "s":
                            value = self.workbook.sharedStrings[int(valueNode.nodeValue)]
                        elif cellS and len(self.workbook.styleCells) >= int(cellS) \
                                and self.workbook.styleCells[int(cellS)].hasAttribute('numFmtId'):
                                #
                                # The following line is commented because although in the documentation for numFmtId the
                                # value  in the range of 14 to 22 is meant for dates, there are probably some changes
                                # since the dates we need don't appear when we execute ImportClients.py
                                #

                                # and int(self.workbook.styleCells[int(cellS)].attributes['numFmtId'].value) in range(14, 22+1):
                            value = conversionDate(float(valueNode.nodeValue))
                        else:
                            value = valueNode.nodeValue
                except Exception:
                    pass
                while True:
                    try:
                        rowCells[columnNum] = value
                        break
                    except IndexError:
                        rowCells.append(None)
            data[indexRow] = rowCells
        return data
