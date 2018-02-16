#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtSql import *

from Ui_ImportPersons import Ui_Dialog
from Utils import *


def ImportPersons(widget):
    dlg = CImportPersons()
    dlg.exec_()

class CImportPersons(QtGui.QDialog, Ui_Dialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.edtLog.setText("")
        self.edtFilePath.setReadOnly(True)
        self.edtFilePath.setText(self.getDbfPath())
        self.pbProcess.setVisible(False)
        self.selectFrom_rbpost = "SELECT id FROM rbPost WHERE name = '%s'"
        self.selectFrom_orgstructure = "SELECT id FROM OrgStructure WHERE name = '%s'"
        self.selectFrom_organisation = "SELECT id FROM Organisation WHERE id = 229081"
        self.selectFrom_personAddress = "SELECT id FROM Person_Address WHERE master_id = %s"
        self.selectFrom_personOrder = "SELECT id FROM Person_Order WHERE master_id = %s"
        self.insertTo_personAddress = """INSERT INTO Person_Address
            (createDatetime, modifyDatetime, deleted, master_id, type, freeInput)
            VALUES (NOW(), NOW(), 0, :master_id, 0, :freeInput)"""
        self.update_personAddress = "UPDATE Person_Address SET modifyDatetime = NOW(), freeInput = :freeInput WHERE master_id = :master_id"
        self.insertTo_personOrder = """INSERT INTO Person_Order
            (createDatetime, modifyDatetime, deleted, master_id, date, type, documentDate, documentNumber, salary)
            VALUES (now(), now(), '0', :master_id, :date, '0', now(), '', '')"""
        self.update_personOrder = "UPDATE Person_Order SET date = :date WHERE master_id = :master_id"
        self.insertTo_person = """
        INSERT INTO Person (
            createDatetime, modifyDatetime, deleted, code, federalCode, regionalCode, lastName, firstName, patrName, post_id, 
            org_id, orgStructure_id, office, office2, finance_id, retireDate, ambPlan, ambPlan2, ambNorm, homPlan, 
            homPlan2, homNorm, expPlan, expNorm, login, password, userProfile_id, retired, birthDate, birthPlace, 
            sex, snils, inn, availableForExternal, timelineAccessibleDays, academicDegree, typeTimeLinePerson, addComment
        )
        VALUES (
            NOW(), NOW(), 0, :code, :federalCode, :regionalCode, :lastName, :firstName, :patrName, :post_id, 
            229081, :orgStructure_id, '', '', 1, :retireDate, 0, 0, 0, 0, 
            0, 0, 0, 0, :login, '', NULL, 0, '0000-00-00', '', 0, :snils, '', 0, 0, 0, 0, 0
        )
        """
        self.update_person = """
            UPDATE Person SET
                modifyDatetime = NOW(),
                code = :code,
                federalCode = :federalCode,
                regionalCode = :regionalCode,
                post_id = :post_id,
                orgStructure_id = :orgStructure_id,
                retireDate = :retireDate
            WHERE id = :id
        """
        self.notFoundPosts = []
        self.notFoundOrgStructures = []
        self.updatedRecords = 0
        self.insertedRecords = 0
        self.skippedRecords = 0
        self.stop = False
        self.db = None

    def bindSelectQuery(self, table, fields, values):
        whereStr = ''
        for field, value in zip(fields, values):
            if QVariant(value).isNull():
                continue
            if whereStr:
                whereStr += ' AND '
            whereStr += '({0} = :{1})'.format(field, field)
        select = 'SELECT id FROM {0} WHERE {1}'.format(table, whereStr)
        query = QSqlQuery(self.db)
        query.prepare(select)
        for field, value in zip(fields, values):
            if not QVariant(value).isNull():
                query.bindValue(":" + field, value)
        return query

    def startProcess(self):
        dbfFileName = unicode(forceStringEx(self.edtFilePath.text()))
        dbf = Dbf(dbfFileName, encoding='cp866')
        db = QtGui.qApp.db.db
        self.db = db

        querySelect = QSqlQuery(db)
        if not querySelect.exec_(self.selectFrom_organisation):
            self.writeToLog(u"Ошибка при получении данных: %s" % querySelect.lastError().text())
            self.writeToLog(u"Запрос:")
            self.writeToLog(self.selectFrom_organisation)
            return
        if not querySelect.first():
            self.writeToLog(u"Не найдена организация с кодом 229081")
            return
        rowCurr = 0
        rowCount = len(dbf)
        self.writeToLog(u"Процесс обработки начат.")
        for row in dbf:
            QtGui.qApp.processEvents()
            rowCurr += 1
#            if rowCurr == 1000+1:
#                break
            code = row['tabnum']
            lastName = row['famis']
            firstName = row['ims']
            patrName = row['otchs']
            post = row['dolgh']
            orgStructure = row['div']
            snils = row['snils']
            retireDate = row['datev']
            personAddress = unicode(row['kladr'])
            personOrder = row['datep']

            if snils:
                snils = snils.replace('-', '')
                snils = snils.replace(' ', '')
            retireDate = forceDate(retireDate)
            personOrder = forceDate(personOrder)
#            if personAddress:
#                personAddress = personAddress.replace(',,', ',')
#                if personAddress[0] == ',': personAddress = personAddress[1:]
#                personAddress = personAddress.replace(',', ', ')

            postNotFound = False
            stmt = self.selectFrom_rbpost % (post)
            querySelect = QSqlQuery(db)
            querySelect.exec_(stmt)
            if querySelect.first():
                id_rbPost = querySelect.value(0).toInt()[0]
            else:
                if not post in self.notFoundPosts:
                    self.notFoundPosts.append(post)
                id_rbPost = QVariant(QVariant.String)
                postNotFound = True

            orgStructureNotFound = False
            stmt = self.selectFrom_orgstructure % (orgStructure)
            querySelect = QSqlQuery(db)
            querySelect.exec_(stmt)
            if querySelect.first():
                id_orgStructure = querySelect.value(0).toInt()[0]
            else:
                if not orgStructure in self.notFoundOrgStructures:
                    self.notFoundOrgStructures.append(orgStructure)
                id_orgStructure = QVariant(QVariant.String)
                orgStructureNotFound = True

            if postNotFound and orgStructureNotFound:
                self.writeToLog(u"Предупреждение:\n{0} {1} {2}".format(lastName, firstName, patrName))
                self.writeToLog(u"Не найдены должность и структурное подразделение:\n{0}\n{1}\n".format(post, orgStructure))
                self.skippedRecords += 1
                continue

            fields = ['lastName', 'firstName', 'patrName', 'post_id', 'orgStructure_id']
            values = [lastName, firstName, patrName, id_rbPost, id_orgStructure]
            querySelect = self.bindSelectQuery('Person', fields, values)
            querySelect.exec_()
            if querySelect.first():
                idForUpdate, isUpdate = querySelect.value(0).toInt()
            else:
                idForUpdate, isUpdate = (0, False)

            if isUpdate:
                fields = ['id', 'code', 'federalCode', 'regionalCode', 'snils', 'retireDate']
                values = [idForUpdate, code, code, code, snils, retireDate]
                querySelect = self.bindSelectQuery('Person', fields, values)
                if not querySelect.exec_():
                    self.writeToLog(u"Ошибка при получении данных: %s" % querySelect.lastError().text())
                    self.writeToLog(u"Запрос:")
                    self.writeToLog(self.getLastExecutedQuery(querySelect))
                    break
                print self.getLastExecutedQuery(querySelect)
                if not querySelect.first():
                    query = QSqlQuery(db)
                    query.prepare(self.update_person)
                    query.bindValue(":id", idForUpdate)
                    query.bindValue(":code", code)
                    query.bindValue(":federalCode", code)
                    query.bindValue(":regionalCode", code)
                    query.bindValue(":post_id", id_rbPost)
                    query.bindValue(":orgStructure_id", id_orgStructure)
                    query.bindValue(":retireDate", retireDate)
                    if not query.exec_():
                        self.writeToLog(u"Ошибка при обновлении записи: %s" % query.lastError().text())
                        self.writeToLog(u"Запрос:")
                        self.writeToLog(self.getLastExecutedQuery(query))
                        break
                    self.updatedRecords += 1

                stmt = self.selectFrom_personAddress % (idForUpdate)
                querySelect = QSqlQuery(db)
                querySelect.exec_(stmt)
                if querySelect.first():
                    query = QSqlQuery(db)
                    query.prepare(self.update_personAddress)
                    query.bindValue(":master_id", idForUpdate)
                    query.bindValue(":freeInput", personAddress)
                    if not query.exec_():
                        self.writeToLog(u"Ошибка при обновлении записи: %s" % query.lastError().text())
                        self.writeToLog(u"Запрос:")
                        self.writeToLog(self.getLastExecutedQuery(query))
                        break

                stmt = self.selectFrom_personOrder % (idForUpdate)
                querySelect = QSqlQuery(db)
                querySelect.exec_(stmt)
                if querySelect.first():
                    query = QSqlQuery(db)
                    query.prepare(self.update_personOrder)
                    query.bindValue(":master_id", idForUpdate)
                    query.bindValue(":date", personOrder)
                    if not query.exec_():
                        self.writeToLog(u"Ошибка при обновлении записи: %s" % query.lastError().text())
                        self.writeToLog(u"Запрос:")
                        self.writeToLog(self.getLastExecutedQuery(query))
                        break
            else:
                query = QSqlQuery(db)
                query.prepare(self.insertTo_person)
                query.bindValue(":code", code)
                query.bindValue(":federalCode", code)
                query.bindValue(":regionalCode", code)
                query.bindValue(":lastName", lastName)
                query.bindValue(":firstName", firstName)
                query.bindValue(":patrName", patrName)
                query.bindValue(":retireDate", retireDate)
                query.bindValue(":post_id", id_rbPost)
                query.bindValue(":orgStructure_id", id_orgStructure)
                query.bindValue(":login", "")
                query.bindValue(":snils", snils)
                if not query.exec_():
                    self.writeToLog(u"Ошибка при добавлении записи: %s" % query.lastError().text())
                    self.writeToLog(u"Запрос:")
                    self.writeToLog(self.getLastExecutedQuery(query))
                    break
                self.insertedRecords += 1

                idForInsert = query.lastInsertId().toInt()[0]

                query = QSqlQuery(db)
                if not query.prepare(self.insertTo_personAddress):
                    self.writeToLog(u"Запрос не был подготовлен:")
                    self.writeToLog(query.lastError().text())
                    break
                query.bindValue(":master_id", idForInsert)
                query.bindValue(":freeInput", personAddress)
                if not query.exec_():
                    self.writeToLog(u"Ошибка при добавлении записи: %s" % query.lastError().text())
                    self.writeToLog(u"Запрос:")
                    self.writeToLog(self.getLastExecutedQuery(query))
                    break

                query = QSqlQuery(db)
                if not query.prepare(self.update_personOrder):
                    self.writeToLog(u"Запрос не был подготовлен:")
                    self.writeToLog(query.lastError().text())
                    break
                query.bindValue(":master_id", idForInsert)
                query.bindValue(":date", personOrder)
                if not query.exec_():
                    self.writeToLog(u"Ошибка при добавлении записи: %s" % query.lastError().text())
                    self.writeToLog(u"Запрос:")
                    self.writeToLog(self.getLastExecutedQuery(query))
                    break

#            if not rowCurr % 10:
#                self.writeToLog(u"Обработано %d/%d записей..." % (rowCurr, rowCount))
            percent = int(float(rowCurr) / rowCount * 100)
            self.pbProcess.setValue(percent)

            if self.stop:
                break

        dbf.close()
        self.pbProcess.setValue(100)
        self.writeToLog("")
        self.writeToLog(u"Процесс обработки завершен.")
        self.writeToLog("")
        self.writeToLog(u"Обновлено: %d записей." % self.updatedRecords)
        self.writeToLog(u"Добавлено: %d записей." % self.insertedRecords)
        self.writeToLog(u"Пропущено: %d записей." % self.skippedRecords)

    def writeToLog(self, message):
        self.edtLog.append(message)

    def getLastExecutedQuery(self, query):
        sql = QString(query.executedQuery())
        nbBindValues = len(query.boundValues())
        i = 0
        j = 0
        while (j < nbBindValues):
            i = sql.indexOf(QString("?"), i)
            if i <= 0:
                break
            var = query.boundValue(j)
            field = QSqlField(QString(""), var.type())
            if var.isNull():
                field.clear()
            else:
                field.setValue(var)
            formatV = QString(query.driver().formatValue(field))
            sql.replace(i, 1, formatV)
            i += formatV.length()
            j += 1
        return unicode(sql)

    def getDbfPath(self):
        return forceString(QtGui.qApp.preferences.appPrefs.get('ImportPersons_DbfPath', QVariant()))

    def setDbfPath(self, path):
        QtGui.qApp.preferences.appPrefs['ImportPersons_DbfPath'] = QVariant(path)

    @QtCore.pyqtSlot()
    def on_btnOpenFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, u"Укажите файл с данными", self.edtFilePath.text(), u"DBF-файлы (*.dbf)")
        if fileName != '':
            self.edtFilePath.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.setDbfPath(self.edtFilePath.text())

    @QtCore.pyqtSlot()
    def on_btnStart_clicked(self):
        if not forceStringEx(self.edtFilePath.text()):
            QtGui.QMessageBox.critical(self, u'Внимание!', u'Укажите файл с данными', QtGui.QMessageBox.Close)
            return
        self.pbProcess.setVisible(True)
        self.startProcess()

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.stop = True
        self.close()
