# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils      import forceDouble, forceInt, forceString
from Reports.Report     import CReport
from Reports.ReportBase import createTable, CReportBase

from ReportMedicinesSMP import CReportBaseSetup

__author__ = 'nat'

tableColumnsList = [
            ('20?', [u'Наименование показателя'],        CReportBase.AlignLeft),
            ('2?',  [u'№ строки'], CReportBase.AlignCenter),
            ('10?', [u'Единица измерения'], CReportBase.AlignCenter),
            ('10?', [u'Коечный фонд, объем оказанной медицинской помощи', u'Всего'], CReportBase.AlignCenter),
            ('10?', [u'', u'в том числе при страховых случаях, видах и условиях оказания медицинской помощи, установленных базовой программой ОМС', u'всего'], CReportBase.AlignCenter),
            ('10?', [u'', u'', u'из них при оказании высокотехно-логичной медицинской помощи'], CReportBase.AlignCenter),
            ('10?', [u'Стоимость оказанной медицинской помощи', u'Всего'], CReportBase.AlignCenter),
            ('10?', [u'', u'в том числе при страховых случаях, видах и условиях оказания медицинской помощи, установленных базовой программой ОМС', u'всего'], CReportBase.AlignCenter),
            ('10?', [u'', u'', u'из них при оказании высокотехно-логичной медицинской помощи'], CReportBase.AlignCenter)]

tableColumnsDs = [
            ('20?', [u'Наименование показателя'],        CReportBase.AlignLeft),
            ('2?',  [u'№ строки'], CReportBase.AlignCenter),
            ('10?', [u'Единица измерения'], CReportBase.AlignCenter),
            ('10?', [u'Величина показателя', u'Всего'], CReportBase.AlignCenter),
            ('10?', [u'', u'в том числе при страховых случаях, видах и условиях оказания медицинской помощи, установленных базовой программой ОМС'], CReportBase.AlignCenter),
            ('10?', [u'', u'из них при оказании:', u'первичной специализиро-ванной медико-санитарной помощи'], CReportBase.AlignCenter),
            ('10?', [u'', u'', u'специализиро-ванной медицинской помощи, всего'], CReportBase.AlignCenter),
            ('10?', [u'', u'', u'в том числе высокотехноло-гичной меди-цинской помощи'], CReportBase.AlignCenter)]

def mergeCellTable(table):
    table.mergeCells(0, 0, 3, 1)
    table.mergeCells(0, 1, 3, 1)
    table.mergeCells(0, 2, 3, 1)
    table.mergeCells(0, 3, 1, 3)
    table.mergeCells(1, 3, 2, 1)
    table.mergeCells(1, 4, 1, 2)
    table.mergeCells(0, 6, 1, 3)
    table.mergeCells(1, 6, 2, 1)
    table.mergeCells(1, 7, 1, 2)

def mergeCellTableDs(table):
    table.mergeCells(0, 0, 3, 1)
    table.mergeCells(0, 1, 3, 1)
    table.mergeCells(0, 2, 3, 1)
    table.mergeCells(0, 3, 1, 5)
    table.mergeCells(1, 3, 2, 1)
    table.mergeCells(1, 4, 2, 1)
    table.mergeCells(1, 5, 1, 3)

def selectStatData(params, type):
    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate().currentDate())
    endDate = params.get('endDate', QtCore.QDate.currentDate())

    selectEv = ''
    selectFinance = ''
    code = '2'
    if type == 'statDs':
        selectEv = u''', COUNT(IF(Event.isPrimary = 1, Event.id, NULL)) AS countEventPrimary
                     , COUNT(IF(Event.isPrimary = 1 AND age(Client.birthDate, Event.setDate) <= 17, Event.id, NULL)) AS countChildrenPrimary
                     , COUNT(IF(Event.isPrimary = 1 AND ((Client.sex = 1 AND age(Client.birthDate, Event.setDate) >= 60) OR (Client.sex = 2 AND age(Client.birthDate, Event.setDate) >= 55)), Event.id, NULL)) AS countOldPrimary
                     , COUNT(IF(Event.isPrimary = 1, Organisation.id, NULL)) AS countCrimeaPrimary
                     , SUM(IF(Event.isPrimary = 1, @days, 0)) AS daysPrimary
                     , SUM(IF(Event.isPrimary = 1 AND age(Client.birthDate, Event.setDate) <= 17, @days, 0)) AS daysChildrenPrimary
                     , SUM(IF(Event.isPrimary = 1 AND ((Client.sex = 1 AND age(Client.birthDate, Event.setDate) >= 60) OR (Client.sex = 2 AND age(Client.birthDate, Event.setDate) >= 55)), @days, 0)) AS daysOldPrimary
                     , SUM(IF(Event.isPrimary = 1 AND Organisation.id, @days, 0)) AS daysCrimeaPrimary'''
        selectFinance = u''', SUM(IF(Event.isPrimary = 1, Account_Item.price * Account_Item.amount, 0)) AS summaPrimary
                            , SUM(IF((Event.isPrimary = 1 AND @age := age(Client.birthDate, Event.setDate)) <= 17, Account_Item.price * Account_Item.amount, 0)) AS daysChildrenPrimary
                            , SUM(IF(Event.isPrimary = 1 AND ((Client.sex = 1 AND age(Client.birthDate, Event.setDate) >= 60) OR (Client.sex = 2 AND age(Client.birthDate, Event.setDate) >= 55)) = 1, Account_Item.price * Account_Item.amount, 0)) AS daysOldPrimary
                            , SUM(IF(Event.isPrimary = 1 AND Organisation.id, Account_Item.price * Account_Item.amount, 0)) AS daysCrimeaPrimary '''
        code = '3'

    stmt = u''' SELECT *
                FROM (SELECT
                        COUNT(Event.id) AS countEvent,
                        COUNT(IF(age(Client.birthDate, Event.setDate) <= 17, Event.id, NULL)) AS countChildren,
                        COUNT(IF((Client.sex = 1 AND age(Client.birthDate, Event.setDate) >= 60 OR (Client.sex = 2 AND age(Client.birthDate, Event.setDate) >= 55)) = 1, Event.id, NULL)) AS countOld,
                        COUNT(Organisation.id) AS countCrimea,
                        SUM(IF(date(Event.setDate) >= date('%(begDate)s'), datediff(Event.execDate, Event.setDate), datediff(Event.execDate, date('%(begDate)s')))) AS days,
                        SUM(IF(age(Client.birthDate, Event.setDate) <= 17, IF(date(Event.setDate) >= date('%(begDate)s'), datediff(Event.execDate, Event.setDate), datediff(Event.execDate, date('%(begDate)s'))), 0)) AS daysChildren,
                        SUM(IF(((Client.sex = 1 AND age(Client.birthDate, Event.setDate) >= 60) OR (Client.sex = 2 AND age(Client.birthDate, Event.setDate) >= 55)), IF(date(Event.setDate) >= date('%(begDate)s'), datediff(Event.execDate, Event.setDate), datediff(Event.execDate, date('%(begDate)s'))), 0)) AS daysOld,
                        SUM(IF(Organisation.id, IF(date(Event.setDate) >= date('%(begDate)s'), datediff(Event.execDate, Event.setDate), datediff(Event.execDate, date('%(begDate)s'))), 0)) AS daysCrimea
                        %(selectEv)s
                       FROM Event
                        INNER JOIN Client ON Client.id = Event.client_id
                        INNER JOIN EventType ON EventType.id = Event.eventType_id
                        LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND ClientPolicy.id = getClientPolicyOnDateId(Client.id, 1, Event.setDate)
                        LEFT JOIN Organisation ON Organisation.id = ClientPolicy.insurer_id AND Organisation.infisCode NOT LIKE '85%%'
                       WHERE DATE(Event.execDate) >= DATE('%(begDate)s')
                          AND DATE(Event.execDate) <= DATE('%(endDate)s')
                          AND EventType.code = '%(code)s'
                          AND Event.deleted = 0) countEv
                JOIN (SELECT
                        SUM(Account_Item.price * Account_Item.amount) AS summa,
                        SUM(IF(age(Client.birthDate, Event.setDate) <= 17, Account_Item.price * Account_Item.amount, 0)) AS daysChildren,
                        SUM(IF(((Client.sex = 1 AND age(Client.birthDate, Event.setDate) >= 60) OR (Client.sex = 2 AND age(Client.birthDate, Event.setDate) >= 55)) = 1, Account_Item.price * Account_Item.amount, 0)) AS daysOld,
                        SUM(IF(Organisation.id, Account_Item.price * Account_Item.amount, 0)) AS daysCrimea
                        %(selectFinance)s
                      FROM Account_Item
                        INNER JOIN Event ON Event.id = Account_Item.event_id
                        INNER JOIN EventType ON EventType.id = Event.eventType_id
                        INNER JOIN Client ON Client.id = Event.client_id
                        LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND ClientPolicy.id = getClientPolicyOnDateId(Client.id, 1, Event.setDate)
                        LEFT JOIN Organisation ON Organisation.id = ClientPolicy.insurer_id AND Organisation.infisCode NOT LIKE '85%%'
                      WHERE DATE(Event.execDate) >= DATE('%(begDate)s')
                        AND DATE(Event.execDate) <= DATE('%(endDate)s')
                        AND EventType.code = '%(code)s'
                        AND Event.deleted = 0) finance ''' % {'begDate': begDate.toString(QtCore.Qt.ISODate),
                                                              'endDate': endDate.toString(QtCore.Qt.ISODate),
                                                              'selectEv': selectEv,
                                                              'selectFinance': selectFinance,
                                                              'code': code}
    return db.query(stmt)

def selectAmbData(params, type):
    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate().currentDate())
    endDate = params.get('endDate', QtCore.QDate.currentDate())

    subFrom = ''
    selectEv = ''
    if type == 'amb':
        selectEv = u''', COUNT(IF(rbEventGoal.code = '2' and rbSpeciality.id, Visit.id, NULL)) AS countProfSpecial,
                         COUNT(IF(rbEventGoal.code = '2' and OrgStructure.id, Visit.id, NULL)) AS countProfCenter,
                         COUNT(IF(rbEventGoal.code = '2' and OrgStructure.id and (@age := age(Client.birthDate, Event.setDate)) <= 17, Visit.id, NULL)) AS countProfChildrenCenter,
                         COUNT(IF(rbEventGoal.code = '4' and rbSpeciality.id, Visit.id, NULL)) AS countUrgentSpecial,
                         COUNT(DISTINCT IF(rbEventGoal.code = '1' and rbSpeciality.id, Event.id, NULL)) AS countIllnessSpecial'''
        selectFinance = u'''SUM(IF(rbEventGoal.code = '2' and rbSpeciality.id, Account_Item.price * Account_Item.amount, 0)) AS summaProfSpecial,
                            SUM(IF(rbEventGoal.code = '2' and OrgStructure.id, Account_Item.price * Account_Item.amount, 0)) AS summaProfCenter,
                            SUM(IF(rbEventGoal.code = '2' and OrgStructure.id and (@age := age(Client.birthDate, Event.setDate)) <= 17, Account_Item.price * Account_Item.amount, 0)) AS summaProfChildrenCenter,
                            SUM(IF(rbEventGoal.code = '4' and rbSpeciality.id, Account_Item.price * Account_Item.amount, 0)) AS summaUrgentSpecial,
                            SUM(IF(rbEventGoal.code = '1' and rbSpeciality.id, Account_Item.price * Account_Item.amount, 0)) AS summaIllnessSpecial'''
        subFrom = u'''LEFT JOIN Person ON Person.id = Visit.person_id
                      LEFT JOIN rbSpeciality ON rbSpeciality.id = Person.speciality_id AND rbSpeciality.code = '16'
                      LEFT JOIN OrgStructure ON OrgStructure.id = Person.orgStructure_id AND OrgStructure.code = '851204.18' '''
    else:
        selectFinance = u'''  SUM(IF(Action.id AND rbService.id, IF(age(Client.birthDate, Action.endDate) < 18, rbService.childUetDoctor, rbService.adultUetDoctor), 0)) AS countUet
                            , SUM(IF(Action.id AND rbService.id, Account_Item.price*Account_Item.amount, 0)) AS summaUet'''

    stmt = u'''SELECT *
               FROM (SELECT
                        COUNT(IF(rbEventGoal.code = '2', Visit.id, NULL)) AS countProf,
                        COUNT(IF(rbEventGoal.code = '2' and age(Client.birthDate, Event.setDate) <= 17, Visit.id, NULL)) AS countProfChildren,
                        COUNT(IF(rbEventGoal.code = '2' and @old := ((Client.sex = 1 AND age(Client.birthDate, Event.setDate) >= 60) OR (Client.sex = 2 AND age(Client.birthDate, Event.setDate) >= 55)) = 1, Visit.id, NULL)) AS countProfOld,
                        COUNT(IF(rbEventGoal.code = '2' and Organisation.id, Visit.id, NULL)) AS countProfCrimea,
                        COUNT(IF(rbEventGoal.code = '4', Visit.id, NULL)) AS countUrgent,
                        COUNT(IF(rbEventGoal.code = '4' and age(Client.birthDate, Event.setDate)<= 17, Visit.id, NULL)) AS countUrgentChildren,
                        COUNT(IF(rbEventGoal.code = '4' and ((Client.sex = 1 AND age(Client.birthDate, Event.setDate) >= 60) OR (Client.sex = 2 AND age(Client.birthDate, Event.setDate) >= 55)), Visit.id, NULL)) AS countUrgentOld,
                        COUNT(IF(rbEventGoal.code = '4' and Organisation.id, Visit.id, NULL)) AS countUrgentCrimea,
                        COUNT(DISTINCT IF(rbEventGoal.code = '1', Event.id, NULL)) AS countIllness,
                        COUNT(DISTINCT IF(rbEventGoal.code = '1' and age(Client.birthDate, Event.setDate) <= 17, Event.id, NULL)) AS countIllnessChildren,
                        COUNT(DISTINCT IF(rbEventGoal.code = '1' and ((Client.sex = 1 AND age(Client.birthDate, Event.setDate) >= 60) OR (Client.sex = 2 AND age(Client.birthDate, Event.setDate) >= 55)), Event.id, NULL)) AS countIllnessOld,
                        COUNT(DISTINCT IF(rbEventGoal.code = '1' and Organisation.id, Event.id, NULL)) AS countIllnessCrimea
                        %(selectEv)s
                    FROM Event
                        INNER JOIN rbEventGoal ON rbEventGoal.id = Event.goal_id AND rbEventGoal.code IN ('1', '2', '4')
                        INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.code %(cond)s
                        INNER JOIN Client ON Client.id = Event.client_id
                        LEFT JOIN Visit ON Visit.event_id = Event.id AND rbEventGoal.code IN ('2', '4') AND Visit.deleted = 0
                        %(from)s
                        LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND ClientPolicy.id = getClientPolicyOnDateId(Client.id, 1, Event.setDate)
                        LEFT JOIN Organisation ON Organisation.id = ClientPolicy.insurer_id AND Organisation.infisCode NOT LIKE '85%%'
                    WHERE DATE(Event.execDate) >= DATE('%(begDate)s')
                        AND DATE(Event.execDate) <= DATE('%(endDate)s')
                        AND Event.deleted = 0) countEv
               JOIN (SELECT
                        SUM(IF(rbEventGoal.code = '2', Account_Item.price * Account_Item.amount, 0)) AS summaProf,
                        SUM(IF(rbEventGoal.code = '2' and age(Client.birthDate, Event.setDate) <= 17, Account_Item.price * Account_Item.amount, 0)) AS summaProfChildren,
                        SUM(IF(rbEventGoal.code = '2' and @old := ((Client.sex = 1 AND age(Client.birthDate, Event.setDate) >= 60) OR (Client.sex = 2 AND age(Client.birthDate, Event.setDate) >= 55)) = 1, Account_Item.price * Account_Item.amount, 0)) AS summaProfOld,
                        SUM(IF(rbEventGoal.code = '2' and Organisation.id, Account_Item.price * Account_Item.amount, 0)) AS summaProfCrimea,
                        SUM(IF(rbEventGoal.code = '4', Account_Item.price * Account_Item.amount, NULL)) AS summaUrgent,
                        SUM(IF(rbEventGoal.code = '4' and age(Client.birthDate, Event.setDate)<= 17, Account_Item.price * Account_Item.amount, 0)) AS summaUrgentChildren,
                        SUM(IF(rbEventGoal.code = '4' and ((Client.sex = 1 AND age(Client.birthDate, Event.setDate) >= 60) OR (Client.sex = 2 AND age(Client.birthDate, Event.setDate) >= 55)) = 1, Account_Item.price * Account_Item.amount, 0)) AS summaUrgentOld,
                        SUM(IF(rbEventGoal.code = '4' and Organisation.id, Account_Item.price * Account_Item.amount, 0)) AS summaUrgentCrimea,
                        SUM(IF(rbEventGoal.code = '1', Account_Item.price * Account_Item.amount, 0)) AS summaIllness,
                        SUM(IF(rbEventGoal.code = '1' and age(Client.birthDate, Event.setDate) <= 17, Account_Item.price * Account_Item.amount, 0)) AS summaIllnessChildren,
                        SUM(IF(rbEventGoal.code = '1' and ((Client.sex = 1 AND age(Client.birthDate, Event.setDate) >= 60) OR (Client.sex = 2 AND age(Client.birthDate, Event.setDate) >= 55)) = 1, Account_Item.price * Account_Item.amount, 0)) AS summaIllnessOld,
                        SUM(IF(rbEventGoal.code = '1' and Organisation.id, Account_Item.price * Account_Item.amount, 0)) AS summaIllnessCrimea,
                        %(selectFinance)s
                    FROM Account_Item
                        INNER JOIN Event ON Event.id = Account_Item.event_id
                        INNER JOIN EventType ON EventType.id = Event.eventType_id AND EventType.code %(cond)s
                        INNER JOIN rbEventGoal ON rbEventGoal.id = Event.goal_id AND rbEventGoal.code IN ('1', '2', '4')
                        INNER JOIN Client ON Client.id = Event.client_id
                        LEFT JOIN Visit ON Visit.event_id = Event.id AND rbEventGoal.code IN ('2', '4') AND Visit.deleted = 0
                        LEFT JOIN rbService ON rbService.id = Account_Item.service_id
                        LEFT JOIN Action ON Action.id = Account_Item.action_id
                        %(from)s
                        LEFT JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND ClientPolicy.id = getClientPolicyOnDateId(Client.id, 1, Event.setDate)
                        LEFT JOIN Organisation ON Organisation.id = ClientPolicy.insurer_id AND Organisation.infisCode NOT LIKE '85%%'
                    WHERE DATE(Event.execDate) >= DATE('%(begDate)s')
                        AND date(Event.execDate) <= DATE('%(endDate)s')
                        AND Event.deleted = 0) finance''' % {'begDate': begDate.toString(QtCore.Qt.ISODate),
                                        'endDate': endDate.toString(QtCore.Qt.ISODate),
                                        'selectEv': selectEv,
                                        'selectFinance': selectFinance,
                                        'cond': '= \'1\'' if type == 'amb' else '= \'5\'',
                                        'from': subFrom}
    return db.query(stmt)

class CReportMainIndicatorsLPU(CReport):
    def __init__(self, parent, type):
        CReport.__init__(self, parent)
        self.type = type
        if type == 'stat':
            self.setTitle(u'Раздел II. Основные показатели деятельности медицинских организаций по оказанию медицинской помощи в стационарных условиях')
        elif type == 'amb':
            self.setTitle(u'Раздел III. Основные показатели деятельности медицинских организаций по оказанию медицинской помощи в амбулаторных условиях (за исключением стоматологической помощи)')
        elif type == 'stom':
            self.setTitle(u'Раздел IV. Основные показатели деятельности медицинских организаций по оказанию стоматологической помощи в амбулаторных условиях')
        elif type == 'statDs':
            self.setTitle(u'Раздел V. Основные показатели деятельности медицинских организаций по оказанию медицинской помощи в условиях дневных стационаров')

    def getSetupDialog(self, parent):
        result = CReportBaseSetup(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        if self.type in ['stat', 'statDs']:
            query = selectStatData(params, self.type)
        elif self.type in ['amb', 'stom']:
            query = selectAmbData(params, self.type)
        self.setQueryText(forceString(query.lastQuery()))

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        cursor.insertBlock()
        if self.type == 'statDs':
            tableColumns = tableColumnsDs
            table = createTable(cursor, tableColumnsDs)
            mergeCellTableDs(table)
        else:
            tableColumns = tableColumnsList
            table = createTable(cursor, tableColumns)
            mergeCellTable(table)
        if self.type == 'stat':
            rows = [
                    (u'Число коек на конец отчетного периода',      u'01', u'коек'),
                    (u' из них: для детей (0-17 лет включительно)', u'02', u'коек'),
                    (u'Число коек в среднем за отчетный период',    u'03', u'коек'),
                    (u' из них: для детей (0-17 лет включительно)', u'04', u'коек'),
                    (u'Число случаев госпитализации, всего',        u'05', u'единиц'),
                    (u' из них: для детей (0-17 лет включительно)', u'06', u'единиц'),
                    (u' лиц старше трудоспособного возраста',       u'07', u'единиц'),
                    (u' лиц, прошедших реабилитацию',               u'08', u'единиц'),
                    (u' лиц, застрахованных за пределами  субъекта   Российской Федерации', u'09', u'единиц'),
                    (u'Проведено выбывшими пациентами койко–дней, всего ',                  u'10', u'койко-дней, единиц'),
                    (u' из них: для детей (0-17 лет включительно)',                         u'11', u'койко-дней, единиц'),
                    (u' лиц старше трудоспособного возраста',                               u'12', u'койко-дней, единиц'),
                    (u' лиц, прошедших реабилитацию',                                       u'13', u'койко-дней, единиц'),
                    (u' лиц, застрахованных за пределами  субъекта   Российской Федерации', u'14', u'койко-дней, единиц')
                    ]
        elif self.type == 'statDs':
            rows = [
                    (u'Число дневных стационаров',                                                 u'46', u'единиц'),
                    (u' из них оказывающие медицинскую помощь детям (0-17 лет включительно)',      u'47', u'единиц'),
                    (u'Число мест на конец отчетного периода',                                     u'48', u'единиц'),
                    (u'Число мест, в среднем за отчетный период',                                  u'49', u'единиц'),
                    (u'Выбыло пациентов, всего',                                                   u'50', u'человек'),
                    (u' из них: детей (0-17 лет включительно)',                                    u'51', u'человек'),
                    (u' лиц старше трудоспособного возраста',                                      u'52', u'человек'),
                    (u' лиц, прошедших реабилитацию',                                              u'53', u'человек'),
                    (u' лиц, застрахованных за пределами  субъекта   Российской Федерации',        u'54', u'человек'),
                    (u'Проведено выбывшими пациентами койко–дней, всего ',                         u'55', u'единиц'),
                    (u' из них: для детей (0-17 лет включительно)',                                u'56', u'единиц'),
                    (u' лиц старше трудоспособного возраста',                                      u'57', u'единиц'),
                    (u' лиц, прошедших реабилитацию',                                              u'58', u'единиц'),
                    (u' лиц, застрахованных за пределами  субъекта   Российской Федерации',        u'59', u'единиц'),
                    (u'Стоимость оказанной медицинской помощи, всего',                             u'60', u'рублей'),
                    (u' из них: для детей (0-17 лет включительно)',                                u'61', u'рублей'),
                    (u' лиц старше трудоспособного возраста',                                      u'62', u'рублей'),
                    (u' лиц, прошедших реабилитацию',                                              u'63', u'рублей'),
                    (u' лиц, застрахованных за пределами  субъекта   Российской Федерации',        u'64', u'рублей'),
                    (u'Число случаев применения экстракорпорального оплодотворения, всего',        u'65', u'единиц'),
                    (u' из них  лицам, застрахованным за пределами субъекта Российской Федерации', u'66', u'единиц'),
                    (u'Стоимость экстракорпорального оплодотворения, всего',                       u'67', u'рублей'),
                    (u' из них лицам, застрахованным за пределами субъекта Российской Федерации',  u'68', u'рублей'),
                    ]
        elif self.type == 'amb':
            rows = [
                    (u'Посещения с профилактической целью,  всего',                          u'15', u'посещений'),
                    (u' из них: врачей общей практики (семейных врачей)',                    u'16', u'посещений'),
                    (u' центров здоровья',                                                   u'17', u'посещений'),
                    (u' из строки 15: детьми (0-17 лет включительно) ',                      u'18', u'посещений'),
                    (u'     из них  центров здоровья детьми (0-17 лет включительно) ',       u'19', u'посещений'),
                    (u' лиц старше трудоспособного возраста',                                u'20', u'посещений'),
                    (u' лиц, застрахованных за пределами  субъекта   Российской Федерации',  u'21', u'посещений'),
                    (u'Посещения при оказании медицинской помощи в неотложной форме, всего', u'22', u'посещений'),
                    (u' из них: врачей общей практики (семейных врачей)',                    u'23', u'посещений'),
                    (u' из строки 22: детьми (0-17 лет включительно) ',                      u'24', u'посещений'),
                    (u' лиц старше трудоспособного возраста',                                u'25', u'посещений'),
                    (u' лиц, застрахованных за пределами  субъекта   Российской Федерации',  u'26', u'посещений'),
                    (u'Обращения по поводу заболевания, всего',                              u'27', u'единиц'),
                    (u' из них: врачей общей практики (семейных врачей)',                    u'28', u'единиц'),
                    (u' из строки 22: детьми (0-17 лет включительно) ',                      u'29', u'единиц'),
                    (u' лиц старше трудоспособного возраста',                                u'30', u'единиц'),
                    (u' лиц, прошедших реабилитацию',                                        u'31', u'единиц'),
                    (u' лиц, застрахованных за пределами  субъекта   Российской Федерации',  u'32', u'единиц')
                    ]
        elif self.type == 'stom':
            rows = [
                    (u'Посещения с профилактической целью,  всего',                          u'33', u'посещений'),
                    (u' из строки 15: детьми (0-17 лет включительно) ',                      u'34', u'посещений'),
                    (u' лиц старше трудоспособного возраста',                                u'35', u'посещений'),
                    (u' лиц, застрахованных за пределами  субъекта   Российской Федерации',  u'36', u'посещений'),
                    (u'Посещения при оказании медицинской помощи в неотложной форме, всего', u'37', u'посещений'),
                    (u' из строки 22: детьми (0-17 лет включительно) ',                      u'38', u'посещений'),
                    (u' лиц старше трудоспособного возраста',                                u'39', u'посещений'),
                    (u' лиц, застрахованных за пределами  субъекта   Российской Федерации',  u'40', u'посещений'),
                    (u'Обращения по поводу заболевания, всего',                              u'41', u'единиц'),
                    (u' из строки 22: детьми (0-17 лет включительно) ',                      u'42', u'единиц'),
                    (u' лиц старше трудоспособного возраста',                                u'43', u'единиц'),
                    (u' лиц, застрахованных за пределами  субъекта   Российской Федерации',  u'44', u'единиц'),
                    (u'Объем фактически выполненной работы',                                 u'45', u'УЕТ*, единиц'),
                    ]

        i = table.addRow()
        for index in xrange(len(tableColumns)):
            table.setText(i, index, index + 1, blockFormat=CReportBase.AlignCenter)
        for row in rows:
            i = table.addRow()
            for index, cellText in enumerate(row):
                table.setText(i, index, cellText)

        if self.type == 'stat':
            self.fillStatTable(query, table)
        elif self.type == 'amb':
            self.fillAmbTable(query, table)
        elif self.type == 'stom':
            self.fillStomTable(query, table)
        elif self.type == 'statDs':
            self.fillStatDsTable(query, table)

        return doc

    def fillStatTable(self, query, table):
        if query.first():
           record = query.record()
           values = [
                    (forceInt(record.value('countEvent')), forceDouble(record.value('summa'))),
                    (forceInt(record.value('countChildren')), forceDouble(record.value('summaChildren'))),
                    (forceInt(record.value('countOld')), forceDouble(record.value('summaOld'))),
                    (0, 0.0),
                    (forceInt(record.value('countCrimea')), forceDouble(record.value('summaCrimea'))),
                    (forceInt(record.value('days')), ''),
                    (forceInt(record.value('daysChildren')), ''),
                    (forceInt(record.value('daysOld')), ''),
                    (0, ''),
                    (forceInt(record.value('daysCrimea')), '')]

           for index, value in enumerate(values):
               table.setText(index + 8, 3, value[0])
               table.setText(index + 8, 4, value[0])
               table.setText(index + 8, 6, value[1])
               table.setText(index + 8, 7, value[1])

    def fillAmbTable(self, query, table):
        if query.first():
           record = query.record()
           values = [
                    (forceInt(record.value('countProf')), forceDouble(record.value('summaProf'))),
                    (forceInt(record.value('countProfSpecial')), forceDouble(record.value('summaProfSpecial'))),
                    (forceInt(record.value('countProfCenter')), forceDouble(record.value('summaProfCenter'))),
                    (forceInt(record.value('countProfChildren')), forceDouble(record.value('summaProfChildren'))),
                    (forceInt(record.value('countProfChildrenCenter')), forceDouble(record.value('summaProfChildrenCenter'))),
                    (forceInt(record.value('countProfOld')), forceDouble(record.value('summaProfOld'))),
                    (forceInt(record.value('countProfCrimea')), forceDouble(record.value('summaProfCrimea'))),
                    (forceInt(record.value('countUrgent')), forceDouble(record.value('summaUrgent'))),
                    (forceInt(record.value('countUrgentSpecial')), forceDouble(record.value('summaUrgentSpecial'))),
                    (forceInt(record.value('countUrgentChildren')), forceDouble(record.value('summaUrgentChildren'))),
                    (forceInt(record.value('countUrgentOld')), forceDouble(record.value('summaUrgentOld'))),
                    (forceInt(record.value('countUrgentCrimea')), forceDouble(record.value('summaUrgentCrimea'))),
                    (forceInt(record.value('countIllness')), forceDouble(record.value('summaIllness'))),
                    (forceInt(record.value('countIllnessSpecial')), forceDouble(record.value('summaIllnessSpecial'))),
                    (forceInt(record.value('countIllnessChildren')), forceDouble(record.value('summaIllnessChildren'))),
                    (forceInt(record.value('countIllnessOld')), forceDouble(record.value('summaIllnessOld'))),
                    (0, ''),
                    (forceInt(record.value('countIllnessCrimea')), forceDouble(record.value('summaIllnessCrimea')))]

           for index, value in enumerate(values):
               table.setText(index + 4, 3, value[0])
               table.setText(index + 4, 4, value[0])
               table.setText(index + 4, 6, value[1])
               table.setText(index + 4, 7, value[1])

    def fillStomTable(self, query, table):
        if query.first():
           record = query.record()
           values = [
                    (forceInt(record.value('countProf')), forceDouble(record.value('summaProf'))),
                    (forceInt(record.value('countProfChildren')), forceDouble(record.value('summaProfChildren'))),
                    (forceInt(record.value('countProfOld')), forceDouble(record.value('summaProfOld'))),
                    (forceInt(record.value('countProfCrimea')), forceDouble(record.value('summaProfCrimea'))),
                    (forceInt(record.value('countUrgent')), forceDouble(record.value('summaUrgent'))),
                    (forceInt(record.value('countUrgentChildren')), forceDouble(record.value('summaUrgentChildren'))),
                    (forceInt(record.value('countUrgentOld')), forceDouble(record.value('summaUrgentOld'))),
                    (forceInt(record.value('countUrgentCrimea')), forceDouble(record.value('summaUrgentCrimea'))),
                    (forceInt(record.value('countIllness')), forceDouble(record.value('summaIllness'))),
                    (forceInt(record.value('countIllnessChildren')), forceDouble(record.value('summaIllnessChildren'))),
                    (forceInt(record.value('countIllnessOld')), forceDouble(record.value('summaIllnessOld'))),
                    (forceInt(record.value('countIllnessCrimea')), forceDouble(record.value('summaIllnessCrimea'))),
                    (forceInt(record.value('countUet')), forceDouble(record.value('summaUet')))]

           for index, value in enumerate(values):
               table.setText(index + 4, 3, value[0])
               table.setText(index + 4, 4, value[0])
               table.setText(index + 4, 6, value[1])
               table.setText(index + 4, 7, value[1])

    def fillStatDsTable(self, query, table):
        if query.first():
           record = query.record()
           values = [
                    (forceInt(record.value('countEvent')), forceInt(record.value('countEventPrimary'))),
                    (forceInt(record.value('countChildren')), forceInt(record.value('countChildrenPrimary'))),
                    (forceInt(record.value('countOld')), forceInt(record.value('countOldPrimary'))),
                    (0, 0),
                    (forceInt(record.value('countCrimea')), forceInt(record.value('countCrimeaPrimary'))),
                    (forceInt(record.value('days')), forceInt(record.value('daysPrimary'))),
                    (forceInt(record.value('daysChildren')), forceInt(record.value('daysChildrenPrimary'))),
                    (forceInt(record.value('daysOld')), forceInt(record.value('daysOldPrimary'))),
                    (0, 0),
                    (forceInt(record.value('daysCrimea')), forceInt(record.value('daysCrimeaPrimary'))),
                    (forceDouble(record.value('summa')), forceDouble(record.value('summaPrimary'))),
                    (forceDouble(record.value('summaChildren')), forceDouble(record.value('summaChildrenPrimary'))),
                    (forceDouble(record.value('summaOld')), forceDouble(record.value('summaOldPrimary'))),
                    (0.0, 0.0),
                    (forceDouble(record.value('summaCrimea')), forceDouble(record.value('summaCrimeaPrimary')))]

           for index, value in enumerate(values):
               table.setText(index + 8, 3, value[0])
               table.setText(index + 8, 4, value[0])
               table.setText(index + 8, 5, value[1])