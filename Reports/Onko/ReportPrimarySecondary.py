# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from library.DialogBase import CDialogBase
from library.Utils import quote, forceBool, forceDate, forceDateTime, forceInt, forceRef, forceString, \
    formatShortNameInt, formatSex, getPref, setPref, toVariant, smartDict, formatNum
from library.database import addDateInRange

from Orgs.Utils import getOrgStructureName, getOrgStructureDescendants

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase

from Ui_ReportPrimarySecondary import Ui_SetupDialog


SelectBySpeciality = 0
SelectBySpecialityAndCountry = 1


def selectData(begDate, endDate, eventTypeIdList, orgStructureId, ageFrom, ageTo, sex, mode=SelectBySpeciality):
    db = QtGui.qApp.db
    Address = db.table('Address')
    AddressHouse = db.table('AddressHouse')
    Client = db.table('Client')
    ClientAddress = db.table('ClientAddress').alias('RegAddress')
    # ClientDocument = db.table('ClientDocument')
    # DocumentType = db.table('rbDocumentType')
    Event = db.table('Event')
    EventType = db.table('EventType')
    OrgStructure = db.table('OrgStructure')
    Person = db.table('Person')
    CitizenshipCSS = db.table('ClientSocStatus').alias('CitizenshipCSS')
    CitizenshipSSC = db.table('rbSocStatusClass').alias('CitizenshipSSC')
    CitizenshipSST = db.table('rbSocStatusType').alias('CitizenshipSST')
    Speciality = db.table('rbSpeciality')

    table = OrgStructure
    table = table.innerJoin(Person, [Person['orgStructure_id'].eq(OrgStructure['id']), Person['deleted'].eq(0)])
    table = table.innerJoin(Speciality, [Speciality['id'].eq(Person['speciality_id'])])
    table = table.innerJoin(Event, [Event['execPerson_id'].eq(Person['id']), Event['setDate'].dateGe(begDate), Event['setDate'].dateGe(endDate), Event['deleted'].eq(0)])
    table = table.innerJoin(EventType, [EventType['id'].eq(Event['eventType_id']), EventType['code'].eq(CReportOnkoPrimarySecondary.StationaryEventTypeCode), EventType['deleted'].eq(0)])
    table = table.innerJoin(Client, [Client['id'].eq(Event['client_id']), Client['deleted'].eq(0)])

    cond = [
        OrgStructure['deleted'].eq(0),
    ]

    if ageFrom > 0 or ageTo < 150:
        cond.append(db.func.age(Client['birthDate'], Event['setDate']).between(ageFrom, ageTo))

    if eventTypeIdList:
        cond.append(EventType['id'].inlist(eventTypeIdList))
    if orgStructureId:
        cond.append(OrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if sex:
        cond.append(Client['sex'].eq(sex))

    cols = [
        Speciality['id'].alias('specialityId')
    ]
    group = [
        'specialityId'
    ]

    if mode == SelectBySpeciality:
        # Иностранцы: вместо определения по rbDocumentType.isForeigner -- определеняем по наличию соц. статуса 'Гражданство' со значением != 'Россия'
        # table = table.leftJoin(ClientDocument, ClientDocument['id'].eq(db.func.getClientDocumentId(Client['id'])))
        # table = table.leftJoin(DocumentType, DocumentType['id'].eq(ClientDocument['documentType_id']))
        table = table.leftJoin(ClientAddress, ClientAddress['id'].eq(db.func.getClientRegAddressId(Client['id'])))
        table = table.leftJoin(Address, [Address['id'].eq(ClientAddress['address_id']), Address['deleted'].eq(0)])
        table = table.leftJoin(AddressHouse, [AddressHouse['id'].eq(Address['house_id']), AddressHouse['deleted'].eq(0)])

        table = table.leftJoin(CitizenshipSSC, CitizenshipSSC['flatCode'].eq('citizenship'))
        table = table.leftJoin(CitizenshipCSS, [CitizenshipCSS['client_id'].eq(Client['id']), CitizenshipCSS['socStatusClass_id'].eq(CitizenshipSSC['id']), CitizenshipCSS['deleted'].eq(0)])
        table = table.leftJoin(CitizenshipSST, [CitizenshipSST['id'].eq(CitizenshipCSS['socStatusType_id']), CitizenshipSST['name'].ne(u'Россия')])

        cols.extend([
            Speciality['name'].alias('specialityName'),
            db.count(Client['id'], distinct=True).alias('countClient'),
            db.count(Event['id'], distinct=True).alias('countEvent'),
            db.countIf(db.left(AddressHouse['KLADRCode'], 2).inlist(['47', '78']), Client['id'], distinct=True).alias('countSpb'),
            db.countIf(db.joinAnd([AddressHouse['KLADRCode'],
                                   db.left(AddressHouse['KLADRCode'], 2).inlist(['47', '78'])]), Client['id'], distinct=True).alias('countNonSpb'),
            db.countIf(db.not_(db.joinOr([CitizenshipSST['id'], AddressHouse['KLADRCode']])), Client['id'], distinct=True).alias('notFoundInKLADR')
        ])

    elif mode == SelectBySpecialityAndCountry:
        table = table.innerJoin(CitizenshipSSC, CitizenshipSSC['flatCode'].eq('citizenship'))
        table = table.innerJoin(CitizenshipCSS, [CitizenshipCSS['client_id'].eq(Client['id']), CitizenshipCSS['socStatusClass_id'].eq(CitizenshipSSC['id']), CitizenshipCSS['deleted'].eq(0)])
        table = table.innerJoin(CitizenshipSST, [CitizenshipSST['id'].eq(CitizenshipCSS['socStatusType_id']), CitizenshipSST['name'].ne(u'Россия')])
        cols.extend([
            CitizenshipSST['name'].alias('country'),
            db.count(Client['id'], distinct=True).alias('cnt')
        ])
        group.extend([
            'country'
        ])

    order = group
    stmt = db.selectStmt(table, cols, cond, group, order)
    return db.query(stmt)


class CReportOnkoPrimarySecondary(CReport):

    StationaryEventTypeCode = '01'

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Отчёт по первичности/повторности за период')

    def getSetupDialog(self, parent):
        dlg = CReportOnkoPrimarySecondarySetupDialog(parent)
        dlg.setWindowTitle(self.title())
        return dlg

    def getDescription(self, params):
        db = QtGui.qApp.db
        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)
        eventTypeIdList = params.get('eventTypeIdList', [])
        orgStructureId = params.get('orgStructureId', None)
        ageFrom = params.get('ageFrom', None)
        ageTo = params.get('ageTo', 150)
        sex = params.get('sex', 0)

        rows = []
        if begDate and endDate:
            rows.append(u'за период с {0} по {1}'.format(forceString(begDate), forceString(endDate)))
        if eventTypeIdList:
            rows.append(u'типы обращений: {0}'.format(u', '.join([forceString(db.translate('EventType', 'id', id, 'code')) for id in eventTypeIdList])))
        if orgStructureId:
            rows.append(u'подразделение: {0}'.format(getOrgStructureName(orgStructureId)))
        if (not ageFrom is None) and (not ageTo is None):
            rows.append(u'возраст: с {0} по {1}'.format(ageFrom, formatNum(ageTo, [u'год', u'года', u'лет'])))
        if sex:
            rows.append(u'пол: {0}'.format(formatSex(sex)))

        return rows

    @staticmethod
    def createTable(cursor):
        tableColumns = [
            ('14?', [u'Вид деятельности'], CReportBase.AlignLeft),
            ('12?', [u'Первично'], CReportBase.AlignCenter),
            ('12?', [u'Повторно'], CReportBase.AlignCenter),
            ('12?', [u'Жители СПб и ЛО'], CReportBase.AlignCenter),
            ('12?', [u'Иногородние'], CReportBase.AlignCenter),
            ('12?', [u'Адрес не установлен через КЛАДР'], CReportBase.AlignCenter),
            ('12?', [u'Иностранцы'], CReportBase.AlignCenter),
            ('4?', [u'Страна', u'Кол-во'], CReportBase.AlignCenter),
            ('10?', [u'', u'Название'], CReportBase.AlignCenter)
        ]
        table = createTable(cursor, tableColumns)

        for c in xrange(7):
            table.mergeCells(0, c, 2, 1)
        table.mergeCells(0, 7, 1, 2)

        return table

    def build(self, params):
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventTypeIdList = params.get('eventTypeIdList', [])
        orgStructureId = params.get('orgStructureId', None)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        sex = params.get('sex', 0)

        countPerCountry = {}
        query = selectData(begDate, endDate, eventTypeIdList, orgStructureId, ageFrom, ageTo, sex, SelectBySpecialityAndCountry)
        self.addQueryText(forceString(query.lastQuery()))
        while query.next():
            rec = query.record()
            specialityId = forceRef(rec.value('specialityId'))
            country = forceString(rec.value('country'))
            cnt = forceInt(rec.value('cnt'))
            countPerCountry.setdefault(specialityId, {})[country] = cnt

        reportRows = []
        query = selectData(begDate, endDate, eventTypeIdList, orgStructureId, ageFrom, ageTo, sex, SelectBySpeciality)
        self.addQueryText(forceString(query.lastQuery()))
        while query.next():
            rec = query.record()
            specialityId = forceRef(rec.value('specialityId'))
            specialityName = forceString(rec.value('specialityName'))
            countPrimary = forceInt(rec.value('countClient'))
            countSecondary = forceInt(rec.value('countEvent')) - countPrimary
            countSpb = forceInt(rec.value('countSpb'))
            countNonSpb = forceInt(rec.value('countNonSpb'))
            notFoundInKLADR = forceInt(rec.value('notFoundInKLADR'))
            perCountry = countPerCountry.get(specialityId, None)

            reportRows.append((
                specialityName,
                [
                    countPrimary,
                    countSecondary,
                    countSpb,
                    countNonSpb,
                    notFoundInKLADR,
                    sum(perCountry.values()) if (not perCountry is None) else 0,
                ],
                countPerCountry.get(specialityId, None)
            ))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.movePosition(QtGui.QTextCursor.End)

        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        bodyBoldFormat = CReportBase.TableBody
        bodyBoldFormat.setFontWeight(QtGui.QFont.Bold)

        table = CReportOnkoPrimarySecondary.createTable(cursor)

        for specialityName, line, countPerCountry in reportRows:
            i = table.addRow()
            table.setText(i, 0, specialityName, charFormat=bodyBoldFormat)
            for j, cnt in enumerate(line):
                table.setText(i, j+1, cnt)

            if countPerCountry:
                numRows = len(countPerCountry)
                for _ in xrange(numRows - 1):
                    table.addRow()
                for c in xrange(7):
                    table.mergeCells(i, c, numRows, 1)

                for r, country in enumerate(sorted(countPerCountry.keys())):
                    table.setText(i + r, 7, countPerCountry[country])
                    table.setText(i + r, 8, country)

        return doc


class CReportOnkoPrimarySecondarySetupDialog(CDialogBase, Ui_SetupDialog):

    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)

        db = QtGui.qApp.db
        tableEventType = db.table('EventType')
        tableEventTypeFilter = [tableEventType['code'].eq(CReportOnkoPrimarySecondary.StationaryEventTypeCode),
                                tableEventType['deleted'].eq(0)]

        self.lstEventTypes.setTable('EventType', filter=db.joinAnd(tableEventTypeFilter))
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventTypeIdList'] = self.lstEventTypes.values()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['ageFrom'] = self.edtAgeFrom.value()
        result['ageTo'] = self.edtAgeTo.value()
        result['sex'] = self.cmbSex.currentIndex()
        return result

#
# def main():
#     import sys
#     from s11main import CS11mainApp
#     from library.database import connectDataBaseByInfo
#
#     app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
#     QtGui.qApp = app
#     QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))
#
#     QtGui.qApp.currentOrgId = lambda: 229608
#     QtGui.qApp.currentOrgStructureId = lambda: 1
#
#     QtGui.qApp.db = connectDataBaseByInfo({
#         'driverName' :      'mysql',
#         'host' :            'pes',
#         'port' :            3306,
#         'database' :        's12',
#         'user':             'dbuser',
#         'password':         'dbpassword',
#         'connectionName':   'vista-med',
#         'compressData' :    True,
#         'afterConnectFunc': None
#     })
#
#     CReportOnkoPrimarySecondary(None).exec_()
#
# if __name__ == '__main__':
#     main()