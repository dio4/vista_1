# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from Orgs.Utils import getOrgStructureFullName, getPersonInfo

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.DialogBase import CDialogBase
from library.Recipe.Utils import recipeStatusNames
from library.Utils import forceString, forceInt
from Reports.Ui_ReportExemptionRecipesSetup import Ui_ReportExemptionRecipesSetup


def selectData(params):
    stmt = u'''
SELECT
    Client.id AS clientId,
    CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName,
    Client.birthDate,
    Client.SNILS,
    DrugRecipe.socCode,
    IF (DrugRecipe.pregCard is not null, DrugRecipe.pregCard, '') AS pregCard,
    REPLACE(DrugRecipe.number, '#', ' ') AS recipeNumber,
    DATE(DrugRecipe.dateTime) AS recipeDate,
    DrugRecipe.mkb,
    dlo_rbMNN.name AS drugMNN,

    CONCAT_WS(' ',
        dlo_rbTradeName.name,
        dlo_rbIssueForm.name,
        DrugRecipe.dosage,
        '№',
        CAST(DloDrugFormulary_Item.qnt AS CHAR)) AS drugTrade,

    CONCAT(vrbPersonWithSpeciality.name, ', ', vrbPersonWithSpeciality.code) AS person,
    IF (DrugRecipe.isVk = '1', 'да', '') AS isVk,
    DrugRecipe.qnt AS drugCount
FROM
    DrugRecipe
    INNER JOIN Event ON Event.id = DrugRecipe.event_id
    INNER JOIN Client ON Event.client_id = Client.id
    INNER JOIN Person ON Event.execPerson_id = Person.id
    INNER JOIN vrbPersonWithSpeciality ON Person.id = vrbPersonWithSpeciality.id
    LEFT JOIN DloDrugFormulary_Item ON DloDrugFormulary_Item.id = DrugRecipe.formularyItem_id
    LEFT JOIN dlo_rbMNN ON dlo_rbMNN.id = DloDrugFormulary_Item.mnn_id
    LEFT JOIN dlo_rbIssueForm ON dlo_rbIssueForm.id = DloDrugFormulary_Item.issueForm_id
    LEFT JOIN dlo_rbTradeName ON dlo_rbTradeName.id = DloDrugFormulary_Item.tradeName_id
    LEFT JOIN dlo_rbDosage ON dlo_rbDosage.id = DloDrugFormulary_Item.dosage_id
WHERE
    %s
ORDER BY
    %s
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    orgStructureId = params.get('orgStructureId', None)
    financeId = params.get('typeFinanceId', None)
    recipeStatus = params.get('recipeStatus', 0)
    socStatusType = params.get('socStatusType', None)
    mkbFrom = params.get('mkbFrom')
    mkbTo = params.get('mkbTo')
    personId = params.get('personId')
    onlyVK = params.get('onlyVK', False)
    orderBy = params.get('sortBy', 0)

    clientId = params.get('clientId', None)
    drugCount = params.get('drugCount', None)

    tableEvent = db.table('Event')
    tableClient = db.table('Client')
    tablePerson = db.table('Person')
    tableDrugRecipe = db.table('DrugRecipe')

    cond = [
        tableDrugRecipe['deleted'].eq(0),
        tableEvent['deleted'].eq(0),
        tableClient['deleted'].eq(0),
        tablePerson['deleted'].eq(0),

        tableDrugRecipe['dateTime'].dateGe(begDate),
        tableDrugRecipe['dateTime'].dateLe(endDate),
        tableDrugRecipe['status'].eq(recipeStatus),
        tableDrugRecipe['socCode'].ne('')
    ]
    if clientId and forceInt(clientId) > -1:
        cond.append(tableClient['id'].eq(clientId))
    if drugCount and drugCount > -1:
        cond.append(tableDrugRecipe['qnt'].eq(drugCount))

    if socStatusType is not None:
        cond.append(tableDrugRecipe['socCode'].eq(db.translate('rbSocStatusType', 'id', socStatusType, 'code')))
    if orgStructureId is not None:
        cond.append(db.joinOr([
            tablePerson['orgStructure_id'].eq(orgStructureId),
            tablePerson['orgStructure_id'].inInnerStmt(
                "(SELECT id FROM OrgStructure_Ancestors WHERE fullPath LIKE '%" + str(orgStructureId) + "%')"
            )
        ]))
    if mkbFrom != '':
        cond.append(db.joinAnd([
            tableDrugRecipe['mkb'].ge(mkbFrom),
            tableDrugRecipe['mkb'].le(mkbTo)
        ]))
    if personId is not None:
        cond.append(tablePerson['id'].eq(personId))
    if onlyVK:
        cond.append(tableDrugRecipe['isVk'].eq(1))
    if financeId is not None:
        cond.append(tableDrugRecipe['finance_id'].eq(financeId))

    orderByCol = ['clientName', 'person', 'recipeDate', 'socCode'][orderBy]
    return db.query(stmt % (db.joinAnd(cond), orderByCol))


class CReportExemptionRecipesSetup(CDialogBase, Ui_ReportExemptionRecipesSetup):

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))

        self.cmbFinance.setTable('rbFinance', addNone=True)
        self.cmbFinance.setFilter('code in (70, 71, 72)')
        self.cmbFinance.setValue(params.get('typeFinanceId', None))

        self.cmbSocStatusType.setTable('rbSocStatusType', addNone=True)
        self.cmbSocStatusType.setFilter('id in (select type_id from rbSocStatusClassTypeAssoc where class_id in (select id from rbSocStatusClass where flatCode = "benefits"))')
        self.cmbSocStatusType.setValue(params.get('socStatusType', None))

        self.edtMKBFrom.setText(params.get('mkbFrom', ''))
        self.edtMKBTo.setText(params.get('mkbTo', ''))

        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbRecipeStatus.setCurrentIndex(params.get('recipeStatus', 0))
        self.cmbPerson.setValue(params.get('personId', None))
        self.chkOnlyVK.setChecked(params.get('onlyVK', False))
        self.cmbSortBy.setCurrentIndex(params.get('sortBy', 0))
        self.edtDrugCount.setVisible(False)
        self.chkDrugCount.setVisible(False)

    def accept(self):
        if not self.edtBegDate.date().isValid() or not self.edtEndDate.date().isValid() or self.edtBegDate.date() > self.edtEndDate.date():
            QtGui.QMessageBox.critical(
                QtGui.qApp.mainWindow,
                u'Внимание!',
                u'Неверно задан период. ',
                QtGui.QMessageBox.Ok
            )
            return
        if bool(self.edtMKBFrom.text()) ^ bool(self.edtMKBTo.text()):  # если заполнено ровно одно поле
            QtGui.QMessageBox.critical(
                QtGui.qApp.mainWindow,
                u'Внимание!',
                u'Диапазон значений МКБ задан некорректно. ',
                QtGui.QMessageBox.Ok
            )
            return
        if self.cmbPerson.value() is not None and self.cmbOrgStructure.value() is not None:
            db = QtGui.qApp.db
            personOrgStructureId = forceInt(db.getRecord('Person', '*', self.cmbPerson.value()).value('orgStructure_id'))
            orgStructureId = self.cmbOrgStructure.value()
            orgStructureAncestors = db.getIdList('OrgStructure_Ancestors', where="fullPath LIKE '%" + str(orgStructureId) + "%'")
            if personOrgStructureId != orgStructureId and personOrgStructureId not in orgStructureAncestors:
                QtGui.QMessageBox.critical(
                    QtGui.qApp.mainWindow,
                    u'Внимание!',
                    u'Обнаружено несоответствие выбранного подразделения и врача. Выберите другое подразделение или другого врача.',
                    QtGui.QMessageBox.Ok
                )
                return
        QtGui.QDialog.accept(self)

    def params(self):
        return {
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date(),
            'orgStructureId': self.cmbOrgStructure.value(),
            'typeFinanceId': self.cmbFinance.value(),
            'recipeStatus': self.cmbRecipeStatus.currentIndex(),
            'socStatusType': self.cmbSocStatusType.value(),
            'mkbFrom': self.edtMKBFrom.text(),
            'mkbTo': self.edtMKBTo.text(),
            'personId': self.cmbPerson.value(),
            'onlyVK': self.chkOnlyVK.isChecked(),
            'sortBy': self.cmbSortBy.currentIndex(),
            'clientId': self.edtClientId.text() if self.chkClientId.isChecked() else -1,
            'drugCount': self.edtDrugCount.value() if self.chkDrugCount.isChecked() else -1
        }


class CReportExemptionRecipes(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Список льготных рецептов")

    def getSetupDialog(self, parent):
        result = CReportExemptionRecipesSetup(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        db = QtGui.qApp.db
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Список выписанных рецептов для льготных категорий граждан')
        cursor.insertBlock()
        cursor.insertBlock()

        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        orgStructureId = params.get('orgStructureId', None)
        financeId = params.get('typeFinanceId', None)
        recipeStatus = params.get('recipeStatus', 0)
        cursor.setCharFormat(QtGui.QTextCharFormat())
        cursor.insertText(u'За период с ' + forceString(begDate.toString('dd.MM.yyyy')) + u' по ' + forceString(endDate.toString('dd.MM.yyyy')))
        cursor.insertBlock()
        cursor.insertText(u'Источник финансирования: ' + (forceString(db.translate('rbFinance', 'id', financeId, 'name')) if financeId else u'все'))
        cursor.insertBlock()
        cursor.insertText(u'Код льготной категории граждан: ')
        socStatusId = params.get('socStatusType', None)
        if socStatusId:
            socStatusCode = forceString(db.translate('rbSocStatusType', 'id', socStatusId, 'code'))
            socStatusName = forceString(db.translate('rbSocStatusType', 'id', socStatusId, 'name'))
            cursor.insertText(socStatusCode + u' ' + socStatusName)
        else:
            cursor.insertText(u'все')
        cursor.insertBlock()
        cursor.insertText(u'Подразделение: ' + (getOrgStructureFullName(orgStructureId) if orgStructureId else u'ЛПУ'))
        cursor.insertBlock()
        cursor.insertText(u'Врач: ')
        personId = params.get('personId', None)
        if personId:
            personInfo = getPersonInfo(personId)
            cursor.insertText(personInfo['fullName'] + u', ' + personInfo['specialityName'] + u', ' + personInfo['code'])
        else:
            cursor.insertText(u'все')
        cursor.insertBlock()
        cursor.insertText(u'Статус рецепта: ' + recipeStatusNames[recipeStatus])
        cursor.insertBlock()
        cursor.insertBlock()

        tableColumns = [
            ('5%',  [u'Код пациента', u''], CReportBase.AlignLeft),
            ('13%', [u'Ф.И.О. пациента', u''], CReportBase.AlignLeft),
            ('7%', [u'Дата рождения', u''], CReportBase.AlignLeft),
            ('11%', [u'СНИЛС', u''], CReportBase.AlignLeft),
            ('5%', [u'Код льготной категории', u''], CReportBase.AlignLeft),
            ('7%', [u'№ карты беременной', u''], CReportBase.AlignLeft),
            ('11%', [u'Серия и номер рецепта', u''], CReportBase.AlignLeft),
            ('7%', [u'Дата выписки', u''], CReportBase.AlignLeft),
            ('5%', [u'Код МКБ', u''], CReportBase.AlignLeft),
            ('7%', [u'Лекарственное средство', u'МНН'], CReportBase.AlignLeft),
            ('8%', [u'', u'Торговое наименование'], CReportBase.AlignLeft),
            ('7%', [u'', u'Количество единиц'], CReportBase.AlignLeft),
            ('13%', [u'Ф.И.О., спец-ть врача, таб. №'], CReportBase.AlignLeft),
            ('3%', [u'ВК'], CReportBase.AlignLeft),
        ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 9, 1, 2)
        table.mergeCells(0, 0, 2, 1)
        table.mergeCells(0, 1, 2, 1)
        table.mergeCells(0, 2, 2, 1)
        table.mergeCells(0, 3, 2, 1)
        table.mergeCells(0, 4, 2, 1)
        table.mergeCells(0, 5, 2, 1)
        table.mergeCells(0, 6, 2, 1)
        table.mergeCells(0, 7, 2, 1)
        table.mergeCells(0, 8, 2, 1)
        table.mergeCells(0, 9, 1, 3)
        # table.mergeCells(0, 11, 1, 2)
        table.mergeCells(0, 12, 2, 1)
        table.mergeCells(0, 13, 2, 1)
        rowSize = len(tableColumns)

        clientIdSet = set()
        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            clientId = forceInt(record.value('clientId'))
            clientIdSet.add(clientId)
            i = table.addRow()
            table.setText(i, 0, clientId)
            table.setText(i, 1, forceString(record.value('clientName')))
            table.setText(i, 2, forceString(record.value('birthDate')))
            table.setText(i, 3, forceString(record.value('SNILS')))
            table.setText(i, 4, forceString(record.value('socCode')))
            table.setText(i, 5, forceString(record.value('pregCard')))
            table.setText(i, 6, forceString(record.value('recipeNumber')))
            table.setText(i, 7, forceString(record.value('recipeDate')))
            table.setText(i, 8, forceString(record.value('mkb')))
            table.setText(i, 9, forceString(record.value('drugMNN')))
            table.setText(i, 10, forceString(record.value('drugTrade')))
            table.setText(i, 11, forceString(record.value('drugCount')))
            table.setText(i, 12, forceString(record.value('person')))
            table.setText(i, 13, forceString(record.value('isVk')))

        i = table.addRow()
        table.mergeCells(i, 0, 1, rowSize)
        table.setText(i, 0, u'Количество пациентов: ' + str(len(clientIdSet)), charFormat=CReportBase.TableTotal)
        i = table.addRow()
        table.mergeCells(i, 0, 1, rowSize)
        table.setText(i, 0, u'Количество рецептов: ' + str((i - 3)), charFormat=CReportBase.TableTotal)
        return doc


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pz12',
        'port': 3306,
        'database': 's11',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CReportExemptionRecipes(None)
    w.exec_()


if __name__ == '__main__':
    main()
