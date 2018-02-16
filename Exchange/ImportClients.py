# -*- coding: utf-8 -*-
import re
import xml.dom.minidom
import zipfile
from PyQt4 import QtCore, QtGui

from Orgs.Orgs import selectOrganisation
from Registry.Utils import getClientWork
from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from Ui_ImportClients import Ui_ImportClients
from library.Utils import databaseFormatSex, forceBool, forceRef, forceDate, formatSex, forceString, forceStringEx, \
    toVariant
from library.excel.ExcelReader import CWorkbook


# Класс ниже не удален, т.к. пока что используется в другом модуле
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

        c -= (65)  # ASCII to number
        return c

    def __init__(self, filename, progressBar):
        progressBar.reset()
        progressBar.setFormat('%p%')
        progressBar.setValue(0)
        shared_strings = []
        self.rows = []
        filename = unicode(filename)
        file = zipfile.ZipFile(filename)

        share = xml.dom.minidom.parseString(file.read('xl/sharedStrings.xml'))
        j = share.getElementsByTagName("t")

        for node in j:
            shared_strings.append(self._nodeText(node))

        sheet = xml.dom.minidom.parseString(file.read('xl/worksheets/sheet1.xml'))
        sheetrows = sheet.getElementsByTagName("row")
        progressBar.setMaximum(len(sheetrows) - 1)
        for index, row in enumerate(sheetrows):
            progressBar.setValue(index)
            cols = row.getElementsByTagName("c")
            largest_col_num = 0
            for col in cols:
                colnum = self._get_col_num(col)
                if colnum > largest_col_num:
                    largest_col_num = colnum

            thiscol = [''] * (largest_col_num + 1)

            for col in cols:
                value = ''
                try:
                    value = self._nodeText(col.getElementsByTagName('v')[0])
                except IndexError:
                    continue

                colnum = self._get_col_num(col)  # ASCII to number
                try:
                    if col.attributes['t'].value == 's':
                        thiscol[colnum] = shared_strings[int(value)].replace('\n', ' ').strip()
                    else:
                        thiscol[colnum] = value.replace('\n', ' ').strip()
                except KeyError:
                    thiscol[colnum] = value.replace('\n', ' ').strip()
                except AttributeError:
                    pass
                except IndexError:
                    pass
            self.rows.append(thiscol)
        file.close()

    def __getitem__(self, i):
        return self.rows[i]


columns = [u'№ списка',
           u'Подразделение',
           u'Фамилия',
           u'Имя',
           u'Отчество',
           u'Пол',
           u'Дата рождения',
           u'Профессия',
           u'Вредные  и  опасные производственные факторы',
           u'Приложение 1',
           u'Приложение 2',
           u'Дата послед. Мед. осмотра']

optionalColumns = [u'Подразделение',
                   u'Вредные  и  опасные производственные факторы',
                   u'Дата послед. Мед. осмотра']  # информация из этих колонок записывается в примечание и не несет логически неверной информации


# Выбор данных из базы
def selectData(workOrgId, clients):
    db = QtGui.qApp.db
    table = [db.table('Client'), db.table('ClientWork'), db.table('ClientWork_Hurt'),
             db.table('ClientWork_Hurt_Factor')]
    cond = []
    condValues = {0: [], 1: []}
    for client in clients:
        for key in condValues.keys():
            condValues[key].append(client[key])
    for key in condValues.keys():
        if condValues[key]:
            cond.append(table[key]['id'].inlist(condValues[key]))

    stmt = u'''SELECT Client.id as clientId
                     , Client.lastName
                     , Client.firstName
                     , Client.patrName
                     , Client.sex
                     , Client.birthDate
                     , Client.notes
                     , ClientWork.id as workId
                     , ClientWork.org_id
                     , ClientWork.post
                     , ClientWork_Hurt.id as workHurtId
                     , group_concat(DISTINCT rbHurtType.code) as hurtType
                     , group_concat(DISTINCT rbHurtFactorType.code) as hurtFactorType
                FROM
                    Client
                    LEFT JOIN ClientWork ON Client.id = ClientWork.client_id AND ClientWork.org_id = %s
                    LEFT JOIN ClientWork_Hurt ON ClientWork_Hurt.master_id = ClientWork.id
                    LEFT JOIN ClientWork_Hurt_Factor ON ClientWork_Hurt_Factor.master_id = ClientWork.id
                    LEFT JOIN rbHurtType ON rbHurtType.id = ClientWork_Hurt.hurtType_id
                    LEFT JOIN rbHurtFactorType ON rbHurtFactorType.id = ClientWork_Hurt_Factor.factorType_id
                WHERE
                    %s
                GROUP BY
                    Client.id''' % (workOrgId, db.joinAnd(cond))
    return db.query(stmt)


# Функция, в которой формирует список данных, согласно заданным столбцам
# Параметры: data   - словарь данных по столбцам, полученный при считывании из файла
# Возвращает список, формат которого соответствует для последующей обработки
def getFormattedListClients(sheet):
    clientInfo = {}
    rows = sheet.getRows()
    cols = sheet.getColumns()
    countDeleteRow = 0

    def deleteRow(key, indexRow, countDeleteRow):
        del rows[key]
        for col in cols.values():
            if len(col) > 1:
                try:
                    col.pop(indexRow - countDeleteRow)
                except IndexError:
                    continue
            else:
                break

    for indexRow, key in enumerate(rows.keys()):
        values = rows[key]
        setValues = set(values)
        # Пустая строка, идем дальше
        if len(setValues) == 1:
            deleteRow(key, indexRow, countDeleteRow)
            countDeleteRow += 1
            continue
        # Не подходящее количество столбцов в строке с уникальными значениями (возможно это заголовок)
        if len(setValues) <= (len(columns) - len(optionalColumns)):
            deleteRow(key, indexRow, countDeleteRow)
            countDeleteRow += 1
            continue
    upperColumn = [header.upper() for header in columns]
    for values in cols.values():
        if values[0] and values[0].upper() in upperColumn:
            clientInfo[columns[upperColumn.index(values[0].upper())]] = values[1:]
    return clientInfo, len(rows) - 1


# Класс для построение отчета
class CReportImportClients(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Импорт пациентов')

    # Получение диалога
    def getSetupDialog(self, parent):
        result = CImportClients(parent)
        self.progressBar = result.progressBar
        self.lblProgressBar = result.lblProgressBar
        result.setTitle(self.title())
        return result

    # Построение отчета
    def build(self, params):
        self.data = params.get('data', [])
        self.countRows = params.get('countRows', 0)
        self.workOrgId = params.get('workOrgId', None)
        self.error = {'Clients': [], 'ClientWork_Hurt': {}, 'ClientWork_Hurt_Factor': {}}
        self.listHurtError = []
        self.listFactorError = []
        self.result = {'insert': [], 'update': []}

        if not self.data:
            self.getSetupDialog(None)
            return
        self.db = QtGui.qApp.db
        self.valueProgressBar = 0
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        self.save()
        self.progressBar.reset()
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(
            len(self.result['insert']) + len(self.result['update']) + len(self.error['ClientWork_Hurt_Factor']) + len(
                self.error['ClientWork_Hurt']) + -1)
        self.lblProgressBar.setText(u'Формирование отчета')
        cursor.insertText(u'Необработанные записи:', CReportBase.ReportSubTitle)
        tableColumns = [('%30', [u'Фамилия'], CReportBase.AlignLeft),
                        ('%30', [u'Имя'], CReportBase.AlignLeft),
                        ('%30', [u'Отчество'], CReportBase.AlignLeft),
                        ('%30', [u'Пол'], CReportBase.AlignLeft),
                        ('%30', [u'Дата рождения'], CReportBase.AlignLeft)]
        table = createTable(cursor, tableColumns)
        for client in self.error['Clients']:
            i = table.addRow()
            for index, value in enumerate(client):
                table.setText(i, index, forceString(value))
        cursor.movePosition(cursor.End, 0)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'Успешно добавленные записи записи:', CReportBase.ReportSubTitle)
        tableColumns.insert(0, ('%5', [u'ID клиента'], CReportBase.AlignLeft))
        tableColumns.extend([('%100', [u'Примечания'], CReportBase.AlignLeft),
                             ('%30', [u'Профессия'], CReportBase.AlignLeft),
                             ('%30', [u'Приложение 1'], CReportBase.AlignLeft),
                             ('%30', [u'Приложение 2'], CReportBase.AlignLeft)])
        table = createTable(cursor, tableColumns)
        cursor.insertBlock()
        cursor.insertBlock()
        query = self.formatInsertUpdateQuery('insert')
        self.fillTable(query, table)
        cursor.movePosition(cursor.End, 0)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'Успешно обнавленные записи:', CReportBase.ReportSubTitle)
        table = createTable(cursor, tableColumns)
        query = self.formatInsertUpdateQuery('update')
        self.fillTable(query, table)
        cursor.movePosition(cursor.End, 0)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        tableColumns[8] = ('%30', [u'Недобавленное/Необнавленное знаение'], CReportBase.AlignLeft)
        tableColumns[9] = ('%30', [u'Причина'], CReportBase.AlignLeft)
        cursor.insertText(u'Недобавленные записи:', CReportBase.ReportSubTitle)
        table = createTable(cursor, tableColumns)
        self.formatErrorTable(self.listHurtError, table)
        self.formatErrorTable(self.listFactorError, table)
        i = table.addRow()
        table.mergeCells(i, 1, 1, 9)
        table.setText(i, 0, u'Всего', CReport.TableTotal)
        table.setText(i, 1, i - 1, CReport.TableTotal)
        return doc

    # Формирование таблицы ошибок
    def formatErrorTable(self, error, table):
        for values in error:
            self.valueProgressBar += 1
            self.progressBar.setValue(self.valueProgressBar)
            i = table.addRow()
            for index, value in enumerate(values):
                table.setText(i, index, value)

    # Формирование данных для добавления или обновляния записей в БД
    def formatInsertUpdateQuery(self, type):
        query = None
        if len(self.result[type]):
            query = selectData(self.workOrgId, self.result[type])
            self.setQueryText(forceString(query.lastQuery()))
        return query

    # Обработка результатов запроса
    def fillTable(self, query, table):
        try:
            while query.next():
                self.valueProgressBar += 1
                self.progressBar.setValue(self.valueProgressBar)
                record = query.record()
                clientId = forceRef(record.value('clientId'))
                lastName = forceString(record.value('lastName'))
                firstName = forceString(record.value('firstName'))
                patrName = forceString(record.value('patrName'))
                sex = formatSex(forceString(record.value('sex')))
                birthDate = forceDate(record.value('birthDate')).toString('dd.MM.yyyy')
                notes = forceString(record.value('notes'))
                post = forceString(record.value('post'))
                hurtId = forceRef(record.value('workHurtId'))
                workId = forceRef(record.value('workId'))
                error = hurtId if self.error['ClientWork_Hurt_Factor'].has_key(hurtId) else workId if self.error[
                    'ClientWork_Hurt_Factor'
                ].has_key(workId) else None
                if error:
                    tuple = self.error['ClientWork_Hurt_Factor'][error]
                    self.listFactorError.append(
                        [clientId, lastName, firstName, patrName, sex, birthDate, notes, post, tuple[0], tuple[1]]
                    )
                if self.error['ClientWork_Hurt'].has_key(workId):
                    tuple = self.error['ClientWork_Hurt'][workId]
                    self.listFactorError.append(
                        [clientId, lastName, firstName, patrName, sex, birthDate, notes, post, tuple[0], tuple[1]]
                    )
                i = table.addRow()
                table.setText(i, 0, clientId)
                table.setText(i, 1, lastName)
                table.setText(i, 2, firstName)
                table.setText(i, 3, patrName)
                table.setText(i, 4, sex)
                table.setText(i, 5, birthDate)
                table.setText(i, 6, notes)
                table.setText(i, 7, post)
                table.setText(i, 8, forceString(record.value('hurtFactorType')))
                table.setText(i, 9, forceString(record.value('hurtType')))
        except AttributeError:
            pass
        i = table.addRow()
        table.mergeCells(i, 1, 1, 9)
        table.setText(i, 0, u'Всего', CReport.TableTotal)
        table.setText(i, 1, i - 1, CReport.TableTotal)

    # Формаирование записи пациента для добавления или обновления
    def getRecord(self, indexClient):
        record = self.db.record('Client')
        clientLastName = forceStringEx(self.data[u'Фамилия'][indexClient])
        clientFirstName = forceStringEx(self.data[u'Имя'][indexClient])
        clientPatrName = forceStringEx(self.data[u'Отчество'][indexClient])
        clientSex = databaseFormatSex(self.data[u'Пол'][indexClient])
        clientBirthDate = self.data[u'Дата рождения'][indexClient]
        clientOrgStructure = self.data[u'Подразделение'][indexClient] if self.data.has_key(u'Подразделение') else ''
        clientFactors = self.data[u'Вредные  и  опасные производственные факторы'][indexClient] if self.data.has_key(
            u'Вредные  и  опасные производственные факторы') else ''
        clientInspection = self.data[u'Дата послед. Мед. осмотра'][indexClient] if self.data.has_key(
            u'Дата послед. Мед. осмотра') and self.data[u'Дата послед. Мед. осмотра'][indexClient] else ''
        clientInspection = forceString(clientInspection) if type(clientInspection) else forceString(
            forceDate(clientInspection).toString('dd.MM.yyyy'))
        if not clientLastName or not clientFirstName or not clientPatrName or not clientBirthDate:
            self.error['Clients'].append(
                [clientLastName, clientFirstName, clientPatrName, self.data[u'Пол'][indexClient], clientBirthDate])
            return
        if isinstance(clientBirthDate, (str, unicode)):
            clientBirthDate = QtCore.QDate().fromString(clientBirthDate.strip(), 'dd.MM.yyyy')
        clientId = self.db.getRecordEx('Client', ['id'], [
            'concat_ws(lastName, firstName, patrName, sex, birthDate) = concat_ws(%s)' % ','.join(
                ['\'%s\'' % clientLastName, '\'%s\'' % clientFirstName, '\'%s\'' % clientPatrName,
                 '%s' % (clientSex if clientSex else 'NULL'),
                 'date(\'%s\')' % clientBirthDate.toString(QtCore.Qt.ISODate)])])
        record.setValue('id', toVariant(clientId.value('id') if clientId else None))
        record.setValue('lastName', toVariant(clientLastName))
        record.setValue('firstName', toVariant(clientFirstName))
        record.setValue('patrName', toVariant(clientPatrName))
        record.setValue('birthDate', toVariant(clientBirthDate))
        record.setValue('sex', toVariant(clientSex))
        record.setValue('notes', toVariant(forceStringEx(';'.join(
            [':'.join([u'Подразделение', clientOrgStructure]) if clientOrgStructure else "",
             ':'.join([u'Вредные  и  опасные производственные факторы', clientFactors]) if clientFactors else "",
             ':'.join([u'Дата послед. мед. осмотра', clientInspection]) if clientInspection else ""]))))
        return record

    # Формирование записи о работе пациента
    def getWorkRecord(self, clientId, post):
        organisationId = forceRef(self.workOrgId)
        post = forceStringEx(post)
        workRecord = getClientWork(clientId)
        if workRecord is not None:
            recordChanged = (
                organisationId != forceRef(workRecord.value('org_id')) or
                post != forceString(workRecord.value('post')))
        else:
            recordChanged = True
        if recordChanged:
            record = QtGui.qApp.db.record('ClientWork')
            record.setValue('client_id', toVariant(clientId))
            record.setValue('org_id', toVariant(organisationId))
            record.setValue('post', toVariant(post))
        else:
            record = workRecord
        return record, recordChanged

    # Получение записи о текущем идентификаторе пациента
    def getClientIdentificatorRecord(self, clientId, accountingSystemCode, identifier):
        accountingSystemCode = forceString(accountingSystemCode)
        db = QtGui.qApp.db
        tableClientIdentification = db.table('ClientIdentification')
        tableAccountingSystem = db.table('rbAccountingSystem')
        cond = [
            tableClientIdentification['client_id'].eq(clientId),
            tableAccountingSystem['code'].eq(accountingSystemCode),
            tableClientIdentification['deleted'].eq(0)
        ]
        record = db.getRecordEx(tableClientIdentification.leftJoin(
            tableAccountingSystem,
            tableAccountingSystem['id'].eq(tableClientIdentification['accountingSystem_id'])),
            'ClientIdentification.*',
            cond
        )
        if record is None:
            record = db.record('ClientIdentification')
            record.setValue('client_id', toVariant(clientId))
            record.setValue('accountingSystem_id',
                            toVariant(forceRef(db.translate('rbAccountingSystem', 'code', accountingSystemCode, 'id'))))
        record.setValue('identifier', toVariant(identifier))
        return record

    # Поулчение информации из справочников
    def rbTypeId(self, value, table):
        rbTable = 'rbHurtType' if table == 'ClientWork_Hurt' else 'rbHurtFactorType'
        record = self.db.getRecordEx(rbTable, 'id', where='code = \'%s\'' % value)
        if record:
            return forceRef(record.value('id'))
        else:
            return None

    # Сохраниение информации о условиях работы пациента
    def saveWorkItems(self, master_id, items, table, field):
        if items:
            masterId = toVariant(master_id)
            idList = []
            for value in items:
                if not len(value):
                    continue
                value = value.strip()
                if not value:
                    continue
                record = QtGui.qApp.db.record(table)
                valueId = self.rbTypeId(value, table)
                if not valueId:
                    self.error[table][master_id] = (value, u'такого значения нет в справочнике %s' % (
                    u'Типы вредности' if table == 'ClientWork_Hurt' else u'Факторы вредности'))
                    continue
                record.setValue('master_id', masterId)
                record.setValue(field, toVariant(valueId))
                itemId = self.db.insertOrUpdate(table, record)
                record.setValue('id', itemId)
                idList.append(itemId)
            table = self.db.table(table)
            cond = [table['master_id'].eq(masterId), 'not(' + table['id'].inlist(idList) + ')']
            self.db.deleteRecord(table, cond)
            return idList

    # Сохранение информации о работе пациента
    def saveWork(self, indexClient, master_id):
        items = self.data[u'Приложение 2'][indexClient]
        if items:
            items = items.strip().split(';')
        factors = self.data[u'Приложение 1'][indexClient]
        if factors:
            factors = factors.strip().split(';')
        return (self.saveWorkItems(master_id, items, 'ClientWork_Hurt', 'hurtType_id'),
                self.saveWorkItems(master_id, factors, 'ClientWork_Hurt_Factor', 'factorType_id'))

    @staticmethod
    def fillClientWorkRecord(db, table, record, deleted=1):
        if deleted is not None:    record.setValue('deleted', toVariant(deleted))
        db.insertOrUpdate(table, record)

    # Сохранение записей в бд
    def save(self):
        self.progressBar.reset()
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(len(self.data) - 1)
        self.lblProgressBar.setText(u'Запись в базу данных')
        try:
            db = QtGui.qApp.db
            for index in xrange(self.countRows):
                infoClient = []
                self.progressBar.setValue(index)
                db.transaction()
                try:
                    record = self.getRecord(index)
                    if record is None:
                        db.commit()
                        continue

                    import sys
                    reload(sys)
                    sys.setdefaultencoding("utf-8")

                    newRecord = not forceBool(record.value('id'))
                    clientId = db.insertOrUpdate('Client', record)
                    infoClient.append(clientId)
                    workRecord, workRecordChanged = self.getWorkRecord(clientId, self.data[u'Профессия'][index])
                    if workRecordChanged and workRecord != None:
                        table = db.forceTable('ClientWork')
                        idFieldName = table.idFieldName()
                        clientWorkList = db.getRecordList(table, cols='*', where=table['client_id'].eq(clientId))
                        if not record.isNull(idFieldName):
                            #
                            # if a new ClientWork item is inserted, the we need to delete the old `ClientWork_Hurt`
                            # and `ClientWork_Hurt_Factor` and set the old ClientWork.deleted to 1.
                            #
                            for i in range(0, len(clientWorkList)):
                                self.fillClientWorkRecord(db, table, clientWorkList[i], deleted=1)
                                row = forceStringEx((clientWorkList[i]).value('id').toString())
                                db.deleteRecord(
                                    'ClientWork_Hurt',
                                    'ClientWork_Hurt.`master_id`=%d' % int(row)
                                )
                                db.deleteRecord(
                                    'ClientWork_Hurt_Factor',
                                    'ClientWork_Hurt_Factor.`master_id`=%d' % int(row)
                                )
                        workRecordId = db.insertOrUpdate('ClientWork', workRecord)

                    elif workRecord != None:
                        workRecordId = forceRef(workRecord.value('id'))
                    else:
                        workRecordId = None

                    if workRecordId != None:
                        infoClient.append(workRecordId)
                        itemsId = self.saveWork(index, workRecordId)
                        if itemsId:
                            for itemId in itemsId:
                                if itemId:
                                    for item in itemId:
                                        infoClient.append(item)

                    db.insertOrUpdate('ClientIdentification',
                                      self.getClientIdentificatorRecord(clientId, u'№', self.data[u'№ списка'][index]))
                    db.commit()
                    if newRecord:
                        self.result['insert'].append(infoClient)
                    else:
                        self.result['update'].append(infoClient)
                except:
                    db.rollback()
                    QtGui.qApp.logCurrentException()
                    raise
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.warning(None, u'Ошибка', unicode(e), QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
        return None


# Класс диалога
class CImportClients(QtGui.QDialog, Ui_ImportClients):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.edtFilePath.setReadOnly(True)
        self.progressBar.setFormat('%p%')
        self.progressBar.setValue(0)
        self.workbook = None
        self.nameSheet = None

    # Метод для проверки коррктного заполнения всех фильтров на форме
    def checkFilters(self):
        nameFilter = []
        if not self.edtFilePath.text():
            nameFilter.append(u'Путь к файлу')
        if not self.cmbOrganisation.value():
            nameFilter.append(u'Организация')
        if nameFilter:
            QtGui.QMessageBox.warning(
                None,
                u'Ошибка',
                u'Поле %s не заполнено' % nameFilter[0] if len(
                    nameFilter
                ) == 1 else u'Поля %s не заполнены' % ','.join(nameFilter),
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok
            )
            return False
        return True

    # Метод для проверки колонок
    def checkColumns(self):
        absentColumns = (set(self.data.keys()) - set(columns)) - set(optionalColumns)
        if absentColumns:
            QtGui.QMessageBox.critical(
                None,
                u'Нехватает столбцов!',
                u'Столбец %s отсутствует!' % absentColumns[0] if len(
                    absentColumns
                ) == 1 else u'Столбцы %s отсутствуют!' % ','.join(absentColumns),
                QtGui.QMessageBox.Ok
            )
            return False
        return True

    # Метод для обработки
    def accept(self):
        if not self.checkFilters():
            return
        self.data, self.countRows = getFormattedListClients(self.workbook[self.nameSheet])
        self.workbook.close()
        if not self.checkColumns():
            return
        if not self.data:
            QtGui.QMessageBox.warning(
                None,
                u'Предупреждение',
                u'Выбранный лист не содержит информации необходимого формата.',
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok
            )
            return
        QtGui.QDialog.accept(self)

    # Установить заголовок
    def setTitle(self, title):
        self.setWindowTitle(title)

    # Установить параметры
    def setParams(self, params):
        self.edtFilePath.setText(params.get('filePath', u''))
        self.cmbOrganisation.setValue(params.get('workOrgId', None))

    # Считать параметры
    def params(self):
        params = {}
        params['filePath'] = self.edtFilePath.text()
        params['workOrgId'] = self.cmbOrganisation.value()
        params['data'] = self.data
        params['countRows'] = self.countRows
        return params

    # Обработка сигнала для кнопки выбора файла
    @QtCore.pyqtSlot()
    def on_btnOpenFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileNames(
            self,
            u'Укажите файл с данными',
            self.edtFilePath.text(),
            u'Файлы XLSX (*.xlsx)'
        )
        if fileName:
            self.edtFilePath.setText(QtCore.QDir.toNativeSeparators(fileName[0]))
            self.workbook = CWorkbook(unicode(fileName[0]))
            self.cmbNameList.clear()
            self.cmbNameList.addItems(sorted(self.workbook.keys()))
            self.cmbNameList.setCurrentIndex(0)

    # Обработка сигнала выбора организации
    @QtCore.pyqtSlot()
    def on_btnSelectOrganisation_clicked(self):
        orgId = selectOrganisation(self, self.cmbOrganisation.value(), False)
        self.cmbOrganisation.update()
        if orgId:
            self.cmbOrganisation.setValue(orgId)

    # Обработка сигнала выбора листа
    @QtCore.pyqtSlot(int)
    def on_cmbNameList_currentIndexChanged(self, index):
        self.nameSheet = unicode(self.cmbNameList.currentText())
