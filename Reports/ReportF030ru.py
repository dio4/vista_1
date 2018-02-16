# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from Orgs.Utils import getOrgStructureFullName, getOrganisationInfo

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.DialogBase import CDialogBase
from library.Recipe.Utils import recipeStatusNames
from library.Utils import forceString
from Reports.Ui_ReportF030ruSetup import Ui_ReportF030ruSetup

def selectData(params):
    stmt = u'''
SELECT
    DATE(DrugRecipe.dateTime) AS recipeDate,
    CONCAT(vrbPerson.name, ' (', vrbPerson.code, ')') AS person,
    CONCAT_WS(' ', Client.lastName, Client.firstName, Client.patrName) AS clientName,
    Client.SNILS,
    ClientPolicy.serial AS policySerial,
    ClientPolicy.number AS policyNumber,
    DrugRecipe.number AS recipeNumber
FROM
    DrugRecipe
    INNER JOIN Event ON Event.id = DrugRecipe.event_id
    INNER JOIN Client ON Event.client_id = Client.id
    INNER JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND ClientPolicy.id = getClientPolicyOnDateId(Client.id, 1, DATE(DrugRecipe.dateTime))
    INNER JOIN Person ON Event.execPerson_id = Person.id
    INNER JOIN vrbPerson ON Person.id = vrbPerson.id
WHERE
    %s
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    orgStructureId = params.get('orgStructureId', None)
    financeId = params.get('typeFinanceId', None)
    recipeStatus = params.get('recipeStatus', 0)

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
        tableDrugRecipe['status'].eq(recipeStatus)
    ]
    if orgStructureId is not None:
        cond.append(db.joinOr([
            tablePerson['orgStructure_id'].eq(orgStructureId),
            tablePerson['orgStructure_id'].inInnerStmt(
                "(SELECT id FROM OrgStructure_Ancestors WHERE fullPath LIKE '%" + str(orgStructureId) + "%')"
            )
        ]))
    if financeId is not None:
        cond.append(tableDrugRecipe['finance_id'].eq(financeId))

    return db.query(stmt % db.joinAnd(cond))


class CReportF030ruSetup(CDialogBase, Ui_ReportF030ruSetup):

    def __init__(self, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        #self.addModels('RecipeStatus', CRecipeStatusModel())
        #self.cmbRecipeStatus.setModel(self.modelRecipeStatus)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))

        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))

        self.cmbFinance.setTable('rbFinance', addNone=True)
        self.cmbFinance.setFilter('code in (70, 71, 72)')
        self.cmbFinance.setValue(params.get('typeFinanceId', None))
        self.cmbRecipeStatus.setCurrentIndex(params.get('recipeStatus', 0))

    def accept(self):
        if not self.edtBegDate.date().isValid() or not self.edtEndDate.date().isValid() or self.edtBegDate.date() > self.edtEndDate.date():
            QtGui.QMessageBox.critical(
                QtGui.qApp.mainWindow,
                u'Внимание!',
                u'Неверно задан период. ',
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
            'recipeStatus': self.cmbRecipeStatus.currentIndex()
        }


class CReportF030ru(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"Форма 030-Р/у (Сведения о ЛС)")

    def getSetupDialog(self, parent):
        result = CReportF030ruSetup(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        db = QtGui.qApp.db
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(QtGui.QTextCharFormat())
        columns = [('50%',  [], CReportBase.AlignLeft), ('50%',  [], CReportBase.AlignRight)]
        table = createTable(cursor, columns, border=0, cellPadding=2, cellSpacing=0)
        i = table.addRow()
        currentOrgInfo = getOrganisationInfo(QtGui.qApp.currentOrgId())
        headerLeft = u'''
Министерство здравоохранения и
социального развития
Российской Федерации
%s
%s
Код ОГРН: %s
        ''' % (
            currentOrgInfo['fullName'],
            forceString(db.translate('Organisation', 'id', currentOrgInfo['id'], 'Address')),
            currentOrgInfo['OGRN']
        )
        headerRight = u'''
Медицинская документация
Форма № 030-Р/у
утв. приказом
Министерства здравоохранения
и социального развития РФ
№ 255 от 22.11.2004 г.
        '''
        table.setText(i, 0, headerLeft)
        table.setText(i, 1, headerRight)
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'Сведения о лекарственных средствах, выписанных и отпущенных гражданам,\n')
        cursor.insertText(u'имеющим право на получение набора социальных услуг')
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
        cursor.insertText(u'Источник финансирования: ' + (forceString(db.translate('rbFinance', 'id', financeId, 'name')) if financeId else u'не задано'))
        cursor.insertBlock()
        cursor.insertText(u'Подразделение: ' + (getOrgStructureFullName(orgStructureId) if orgStructureId else u'ЛПУ'))
        cursor.insertBlock()
        cursor.insertText(u'Статус рецепта: ' + recipeStatusNames[recipeStatus])
        cursor.insertBlock()
        cursor.insertBlock()

        tableColumns = [
            ('3%',  [u'Заполняется специалистом ОМК', u'№ п/п'], CReportBase.AlignLeft),
            ('5%',  [u'', u'Дата выписки рецепта'], CReportBase.AlignLeft),
            ('20%', [u'', u'Ф.И.О. врача (таб №)'], CReportBase.AlignLeft),
            ('10%', [u'', u'Ф.И.О. пациента'], CReportBase.AlignLeft),
            ('7%', [u'', u'Серия и номер страхового медицинского полиса'], CReportBase.AlignLeft),
            ('10%', [u'', u'СНИЛС'], CReportBase.AlignLeft),
            ('10%', [u'', u'Серия и номер выписанного рецепта'], CReportBase.AlignLeft),
            ('5%', [u'Заполняется на основании сведений аптечных учреждений', u'Дата отпуска лекарственного средства'], CReportBase.AlignLeft),
            ('5%', [u'', u'Наименование отпущенного лекарственного средства'], CReportBase.AlignLeft),
            ('5%', [u'', u'Стоимость упаковки лекарственного средства'], CReportBase.AlignLeft),
            ('5%', [u'', u'Отпущено упаковок'], CReportBase.AlignLeft),
            ('5%', [u'', u'Общая стоимость отпущенного лекарственного средства'], CReportBase.AlignLeft),
        ]
        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 1, 7)
        table.mergeCells(0, 7, 1, 5)
        rowSize = len(tableColumns)

        i = table.addRow()
        for j in range(rowSize):
            table.setText(i, j, (j + 1))

        query = selectData(params)
        self.setQueryText(forceString(query.lastQuery()))
        while query.next():
            record = query.record()
            i = table.addRow()
            table.setText(i, 0, i - 2)
            table.setText(i, 1, forceString(record.value('recipeDate')))
            table.setText(i, 2, forceString(record.value('person')))
            table.setText(i, 3, forceString(record.value('clientName')))
            policySerial = forceString(record.value('policySerial'))
            policyNumber = forceString(record.value('policyNumber'))
            table.setText(i, 4, policyNumber if policySerial == u'' else policySerial + u' ' + policyNumber)
            table.setText(i, 5, forceString(record.value('SNILS')))
            table.setText(i, 6, forceString(record.value('recipeNumber')).replace(u'#', u' '))

        cursor.movePosition(QtGui.QTextCursor.End)

        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertText(u'Итого общая стоимость ' + u'_' * 96)
        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()

        footerColumns = [(percent, [], CReportBase.AlignLeft) for percent in ['25%', '35%', '25%', '15%']]
        table = createTable(cursor, footerColumns, border=0, cellPadding=2, cellSpacing=0)
        i = table.addRow()
        table.setText(i, 0, u'Зав. ОМК')
        table.setText(i, 1, u'_' * 60, blockFormat=CReportBase.AlignCenter)
        table.setText(i, 3, u'_' * 30, blockFormat=CReportBase.AlignCenter)
        i = table.addRow()
        table.setText(i, 1, u'(Ф.И.О.)', blockFormat=CReportBase.AlignCenter)
        table.setText(i, 3, u'(подпись)', blockFormat=CReportBase.AlignCenter)
        i = table.addRow()
        table.setText(i, 0, u'Работник аптечного учреждения')
        table.setText(i, 1, u'_' * 60, blockFormat=CReportBase.AlignCenter)
        table.setText(i, 3, u'_' * 30, blockFormat=CReportBase.AlignCenter)
        i = table.addRow()
        table.setText(i, 1, u'(Ф.И.О.)', blockFormat=CReportBase.AlignCenter)
        table.setText(i, 3, u'(подпись)', blockFormat=CReportBase.AlignCenter)
        return doc

