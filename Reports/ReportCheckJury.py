# -*- coding: utf-8 -*-

import codecs
import re
import xml.dom.minidom
import zipfile
from PyQt4 import QtCore, QtGui
from datetime import date, timedelta

from Events.Utils import findLastDiagnosisRecord
from Registry.Utils import CClientInfo
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ReportCheckJury import Ui_ReportCheckJury
from library.PrintInfo import CInfoContext
from library.Utils import forceRef, forceString


class XLSXReader:
    rows = []

    def _nodeText(self, node):
        return "".join(t.nodeValue for t in node.childNodes if t.nodeType == t.TEXT_NODE)

    def _get_col_num(self, col):
        strpart = col.attributes['r'].value
        colnum = re.sub('[^A-Z]', '', strpart.upper().strip())

        c = 0
        for char in colnum:
            c += ord(char)

        c -= (65) # ASCII to number
        return c

    def __init__(self, filename, filter):
        shared_strings = []
        self.rows = []
        filename = unicode(filename)
        file = zipfile.ZipFile(filename)

        share = xml.dom.minidom.parseString(file.read('xl/sharedStrings.xml'))
        j = share.getElementsByTagName("t")

        for node in j:
            shared_strings.append(self._nodeText(node))

        sheet = xml.dom.minidom.parseString(file.read('xl/worksheets/sheet1.xml'))
        sheetDimension = sheet.getElementsByTagName("dimension")
        dimension = sheetDimension[0].attributes['ref'].value
        dimensionList = dimension.split(':')
        countRows = int(dimensionList[1][1:])
        sheetrows = sheet.getElementsByTagName("row")
        for row in sheetrows:
            cols = row.getElementsByTagName("c")

            largest_col_num = 0
            for col in cols:
                colnum = self._get_col_num(col)
                if colnum > largest_col_num:
                    largest_col_num = colnum

            thiscol = ['']*(largest_col_num + 1)

            for col in cols:
                value = ''
                try:
                    value = self._nodeText(col.getElementsByTagName('v')[0])
                except IndexError:
                    continue

                colnum = self._get_col_num(col) # ASCII to number
                try:
                    if col.attributes['t'].value == 's':
                        thiscol[colnum] = shared_strings[int(value)]
                    else:
                        thiscol[colnum] = value
                except KeyError:
                    thiscol[colnum] = date(1900, 1, 1) + timedelta(int(value)-2)
                try:
                    if thiscol[colnum].upper() == u'М':
                        thiscol[colnum] = 1
                    elif thiscol[colnum].upper() == u'Ж':
                        thiscol[colnum] = 2
                    if self.rows and u'Дата рождения' in self.rows[0]:
                        index = self.rows[0].index(u'Дата рождения')
                        if colnum == index:
                            strDate = thiscol[index].strip().split('.')
                            thiscol[colnum] = date(int(strDate[2]), int(strDate[1]), int(strDate[0])).isoformat()
                except AttributeError:
                    pass
                except IndexError:
                    pass
            self.rows.append(thiscol)
        file.close()


    def __getitem__(self, i):
        return self.rows[i]

def readCsv(filePath, filter):
    table = []
    try:
        with codecs.open(filePath, 'r', 'utf-8') as csvFile:
            for line in csvFile.readlines():
                listLine = line.strip().split(';')
                try:
                    listLine[listLine.index(u'М')] = 1
                except:
                    try:
                        listLine[listLine.index(u'Ж')] = 2
                    except:
                        pass
                try:
                    index = table[0].index(u'Дата рождения')
                    strDate = listLine[index].strip().split('.')
                    listLine[index] = date(int(strDate[2]), int(strDate[1]), int(strDate[0])).isoformat()
                except:
                    pass
                table.append(listLine)
    except Exception:
        return
    return table

def selectData(params):
    lastName  = params.get('lastName', True)
    firstName = params.get('firstName', True)
    partName  = params.get('partName', True)
    sex       = params.get('chkSex', True)
    birthDate = params.get('birthDate', True)
    list      = params.get('list', [])
    columns   = params.get('columns', [])
    enterClientIdentification = params.get('enterClientIdentification', True)
    db = QtGui.qApp.db

    tableClient                 = db.table('Client')
    tableClientIdentification   = db.table('ClientIdentification')
    tableAccountingSystem       = db.table('rbAccountingSystem')
    tableClientAddress = db.table('ClientAddress')

    queryTable = tableClient.leftJoin(tableClientAddress, tableClientAddress['client_id'].eq(tableClient['id']))
    queryTable = queryTable.leftJoin(tableClientIdentification, db.joinAnd([tableClient['id'].eq(tableClientIdentification['client_id']), tableClientIdentification['accountingSystem_id'].eq(db.translate(tableAccountingSystem, 'code', '8', 'id'))]))

    cols = [tableClient['id']]
    if enterClientIdentification:
        cols.append(tableClientIdentification['identifier'])
    cond = [tableClientAddress['deleted'].eq(0)]
    condField = []
    valueField = []
    condValue = []

    if lastName:
        condField.append('Client.lastName')
        valueField.append(columns.index(u'Фамилия'))
    if firstName:
        condField.append('Client.firstName')
        valueField.append(columns.index(u'Имя'))
    if partName:
        condField.append('Client.patrName')
        valueField.append(columns.index(u'Отчество'))
    if sex:
        cols.append(tableClient['sex'])
        condField.append('Client.sex')
        valueField.append(columns.index(u'Пол'))
    if birthDate:
        cols.append(tableClient['birthDate'])
        condField.append('Client.birthDate')
        valueField.append(columns.index(u'Дата рождения'))
    for value in list:
        values = []
        for index in valueField:
            values.append(''' '%s' ''' % value[index])
        condValue.append('concat_ws(%s)' % ','.join(values))
    cond.append('concat_ws(%s) IN (%s)' % (','.join(condField), ','.join(condValue)))
    group = [tableClient['lastName'].name(), tableClient['firstName'].name(), tableClient['patrName'].name()]
    stmt = QtGui.qApp.db.selectStmt(queryTable, cols, cond, group=group)
    query = QtGui.qApp.db.query(stmt)
    return query

class CReportCheckJury(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Сверка списка присяжных со списком пациентов')

    def getSetupDialog(self, parent):
        result = CCheckJury(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        columns = params.get('columns', [])
        enterClientId = params.get('enterClientId', True)
        enterClientIdentification = params.get('enterClientIdentification', False)
        defColumns = [u'Фамилия', u'Имя', u'Отчество', u'Пол', u'Дата рождения']
        query = selectData(params)
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        cursor.insertText(u'проверка производилась по: ' + ', '.join(index for index in set(columns) & set(defColumns)), QtGui.QTextCharFormat())
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        tableColumns = [
                        ('%20',  [u'ФИО'], CReportBase.AlignLeft),
                        ('%15',  [u'Дата рождения'], CReportBase.AlignLeft),
                        ('%15',  [u'Адрес регистрации'], CReportBase.AlignLeft),
                        ('%15',  [u'Адрес проживания'], CReportBase.AlignLeft),
                        ('%15',  [u'Диагноз'], CReportBase.AlignLeft)]
        if enterClientId:
            tableColumns.insert(0, ('%2',  [ u'Код'], CReportBase.AlignRight))
        if enterClientIdentification:
            tableColumns.insert(1 if enterClientId else 0, ('%2',  [u'№ истории \n болезни'], CReportBase.AlignRight))

        table = createTable(cursor, tableColumns)
        boldChars = QtGui.QTextCharFormat()
        boldChars.setFontWeight(QtGui.QFont.Bold)

        boldItalicChars = QtGui.QTextCharFormat()
        boldItalicChars.setFontWeight(QtGui.QFont.Bold)
        boldItalicChars.setFontItalic(True)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            identifier = forceString(record.value('identifier'))
            id         = forceRef(record.value('id'))
            clientInfo = CClientInfo(CInfoContext(), id)
            name       = clientInfo.fullName
            birthDate  = clientInfo.birthDate
            addressReg = clientInfo.regAddress
            address    = clientInfo.locAddress
            diagnosis  = findLastDiagnosisRecord(id)
            diag = forceString(diagnosis.value('MKB')) if diagnosis else u''
            if id:
                i = table.addRow()
                table.setText(i, 0, identifier if not enterClientId and enterClientIdentification else id)
                if enterClientIdentification:
                    table.setText(i, 1, identifier)
                table.setText(i, 2 if enterClientIdentification and enterClientId else 1, name)
                table.setText(i, 3 if enterClientIdentification and enterClientId  else 2, birthDate)
                table.setText(i, 4 if enterClientIdentification and enterClientId else 3, addressReg)
                table.setText(i, 5 if enterClientIdentification and enterClientId else 4, address)
                table.setText(i, 6 if enterClientIdentification and enterClientId else 5, diag)
        return doc

class CCheckJury(QtGui.QDialog, Ui_ReportCheckJury):
    def __init__(self, parent=None, filePath = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.edtFilePath.setReadOnly(True)
        self.list = []
        self.columns = []
        self.filter = {u'Фамилия': self.chkLastName, u'Имя': self.chkFirstName, u'Отчество': self.chkPartName, u'Пол': self.chkSex, u'Дата рождения': self.chkBirthDate}

    def checkCheckBox(self, chk1, chk2, chk3, chk4):
        if chk1 or chk2 or chk3 or chk4:
            return True
        return False

    def accept(self):
        if self.edtFilePath.text() == '':
            QtGui.QMessageBox.warning(None, u'Ошибка', u'Файл не выбран.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            return
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            listFileName = list(self.edtFilePath.text().split('.'))
            if listFileName[len(listFileName)-1] == u'csv':
                tmpList = readCsv(unicode(self.edtFilePath.text()), self.filter)
            else:
                tmpList = list(XLSXReader(unicode(self.edtFilePath.text()), self.filter))
            self.columns = list(tmpList[0])
            tmpList.remove(tmpList[0])
            self.list = tmpList
            if len(self.list) and self.checkStructureFile(self.filter, self.columns):
                QtGui.QDialog.accept(self)
        finally:
            QtGui.QApplication.restoreOverrideCursor()

    def checkStructureFile(self, filter, columns):
        difference = list(set(filter.keys()).difference(columns))
        if len(difference) >= 5:
            QtGui.QMessageBox.warning(None, u'Ошибка', u'В файле нет нужных колонок.', QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
            return False
        for item in difference:
            if filter[item].isChecked():
                res = QtGui.QMessageBox.warning(None, u'Ошибка', u'Колонка "' + item + u'" отсутствует.', QtGui.QMessageBox.Ok | QtGui.QMessageBox.Ignore, QtGui.QMessageBox.Ok)
                if res == QtGui.QMessageBox.Ignore:
                    filter[item].setChecked(False)
                else:
                    return False
        return True

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.chkLastName.setChecked(params.get('lastName', True))
        self.chkFirstName.setChecked(params.get('firstName', True))
        self.chkPartName.setChecked(params.get('partName', True))
        self.chkSex.setChecked(params.get('chkSex', True))
        self.chkBirthDate.setChecked(params.get('birthDate', True))
        self.edtFilePath.setText(params.get('filePath', u''))
        self.chkClientId.setChecked(params.get('enterClientId', False))
        self.chkClientIdentification.setChecked(params.get('enterClientIdentification', True))

    def params(self):
        params = {}
        params['lastName']     = self.chkLastName.isChecked()
        params['firstName']    = self.chkFirstName.isChecked()
        params['partName']     = self.chkPartName.isChecked()
        params['chkSex']       = self.chkSex.isChecked()
        params['birthDate']    = self.chkBirthDate.isChecked()
        params['filePath']     = self.edtFilePath.text()
        params['list']         = self.list
        params['columns']      = self.columns
        params['enterClientId'] = self.chkClientId.isChecked()
        params['enterClientIdentification'] = self.chkClientIdentification.isChecked()
        return params

    @QtCore.pyqtSlot()
    def on_btnOpenFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileNames(self, u'Укажите файл с данными', self.edtFilePath.text(), u'Файлы CSV (*.csv *.xlsx *.xls)')
        if fileName[0] != '':
            self.chkLastName.setChecked(True)
            self.edtFilePath.setText(QtCore.QDir.toNativeSeparators(fileName[0]))

    @QtCore.pyqtSlot(bool)
    def on_chkLastName_clicked(self):
        if not self.checkCheckBox(self.chkFirstName.isChecked(), self.chkPartName.isChecked(), self.chkSex.isChecked(), self.chkBirthDate.isChecked()):
            self.chkLastName.setChecked(True)

    @QtCore.pyqtSlot(bool)
    def on_chkFirstName_clicked(self):
        if not self.checkCheckBox(self.chkLastName.isChecked(), self.chkPartName.isChecked(), self.chkSex.isChecked(), self.chkBirthDate.isChecked()):
            self.chkFirstName.setChecked(True)

    @QtCore.pyqtSlot(bool)
    def on_chkPatrName_clicked(self):
        if not self.checkCheckBox(self.chkFirstName.isChecked(), self.chkLastName.isChecked(), self.chkSex.isChecked(), self.chkBirthDate.isChecked()):
            self.chkPartName.setChecked(True)

    @QtCore.pyqtSlot(bool)
    def on_chkSex_clicked(self):
        if not self.checkCheckBox(self.chkFirstName.isChecked(), self.chkPartName.isChecked(), self.chkLastName.isChecked(), self.chkBirthDate.isChecked()):
            self.chkSex.setChecked(True)

    @QtCore.pyqtSlot(bool)
    def on_chkBirthDate_clicked(self):
        if not self.checkCheckBox(self.chkFirstName.isChecked(), self.chkPartName.isChecked(), self.chkSex.isChecked(), self.chkLastName.isChecked()):
            self.chkBirthDate.setChecked(True)