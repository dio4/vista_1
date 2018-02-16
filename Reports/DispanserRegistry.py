# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from library.MapCode                import createMapCodeToRowIdx
from library.Utils                  import forceDate, forceInt, forceRef, forceString
from Orgs.Utils                     import getOrgStructureDescendants, getOrgStructures
from Reports.DispObservationList    import CDispObservationListSetupDialog
from Reports.Report                 import CReport, normalizeMKB
from Reports.ReportBase             import createTable, CReportBase


MainRows = [
    (u'Всего', u'1.0',u'A00-T98'),
    (u'в том числе: некоторые инфекционные и паразитарные болезни', u'2.0',u'A00-B99'),
    (u'новообразования',u'3.0',u'C00-D48'),
    (u'болезни крови, кроветворных органов и отдельные нарушения, вовлекающие иммунный механизм', u'4.0',u'D50-D89'),
    (u'из них: анемии',u'4.1',u'D50-D64'),
    (u'нарушения свертываемости крови', u'4.2',u'D65-D68'),
    (u'в том числе диссеминированное внутрисосудистое свертывание (синдром дефибринации)', u'4.2.1',u'D65'),
    (u'гемофилия', u'4.2.2', u'D66-D67, D68.0'),
    (u'отдельные нарушения, вовлекающие иммунный механизм', u'4.3',u'D80-D89'),
    (u'болезни эндокринной системы, расстройства питания и нарушения обмена веществ', u'5.0',u'E00-E90'),
    (u'из них: тиреотоксикоз (гипертиреоз)',u'5.1',u'E05'),
    (u'сахарный диабет', u'5.2',u'E10-E14'),
    (u'в том числе: инсулинзависимый сахарный диабет', u'5.2.1',u'E10'),
    (u'инсулиннезависимый сахарный диабет', u'5.2.2',u'E11'),
    (u'ожирение',u'5.3', u'E66'),
    (u'муковисцидоз', u'5.4', u'E84.0'),
    (u'гипофизарный нанизм', u'5.5', u'E23.0'),
    (u'болезнь Гоше', u'5.6', u'E75.5'),
    (u'психические расстройства и расстройства поведения', u'6.0',u'F00-F99'),
    (u'болезни нервной системы', u'7.0',u'G00-G99'),
    (u'из них: эпилепсия, эпилептический статус', u'7.1',u'G40-G41'),
    (u'болезни периферической нервной системы', u'7.2',u'G50-G72'),
    ( u'детский церебральный паралич', u'7.3', u'G80'),
    ( u'рассеянный склероз', u'7.4', u'G35.0'),
    (u'болезни глаза и его придаточного аппарата', u'8.0',u'H00-H59'),
    (u'из них: катаракта', u'8.1',u'H25-H26'),
    (u'глаукома', u'8.2',u'H40'),
    (u'миопия', u'8.3',u'H52.1'),
    (u'болезни уха и сосцевидного отростка', u'9.0',u'H60-H95'),
    (u'из них хронический отит', u'9.1',u'H65.2-9, H66.1-9'),
    (u'болезни системы кровообращения', u'10.0',u'I00-I99'),
    (u'из них: острая ревматическая лихорадка', u'10.1',u'I00-I02'),
    (u'хронические ревматические болезни сердца', u'10.2',u'I05-I09'),
    ( u'в том числе ревматические пороки клапанов', u'10.2.1', u'I05-I08'),
    (u'болезни, характеризующиеся повышенным кровяным давлением', u'10.3',u'I10-I13'),
    (u'ишемическая болезнь сердца', u'10.4',u'I20-I25'),
    (u'из общего числа больных ишемической болезнью больных: стенокардией', u'10.5',u'I20'),
    (u'острым инфарктом миокарда',u'10.6',u'I21'),
    (u'повторным инфарктом миокарда', u'10.7',u'I22'),
    (u'некоторыми текущими осложнениями острого инфаркта миокарда', u'10.8',u'I23'),
    (u'другими формами острой ишемической болезни сердца', u'10.9',u'I24'),
    (u'цереброваскулярные болезни', u'10.10',u'I60-I69'),
    (u'инсульт', u'10.10.1',u'I60-I64'),
    (u'эндартериит, тромбангиит облитерирующий', u'10.11',u'I70.2, I73.1'),
    (u'болезни органов дыхания', u'11.0',u'J00-J99'),
    (u'из них: пневмонии', u'11.1',u'J12-J18'),
    (u'аллергический ринит (поллиноз)', u'11.2',u'J30.1'),
    (u'хронический фарингит, назофарингит, синусит, ринит', u'11.3',u'J31-J32'),
    (u'хронические болезни миндалин и аденоидов, перитонзиллярный абсцесс', u'11.4',u'J35, J36'),
    (u'бронхит хронический и неуточненный, эмфизема', u'11.5',u'J40-J43'),
    (u'другая хроническая обструктивная легочная, бронхоэктатическая болезнь', u'11.6',u'J44, J47'),
    (u'астма, астматический статус',u'11.7',u'J45-J46'),
    (u'интерстициальные, гнойные легочные болезни, другие болезни плевры', u'11.8',u'J84-J94'),
    (u'болезни органов пищеварения',u'12.0', u'K00-K93'),
    (u'из них: язва желудка и 12-перстной кишки', u'12.1',u'K25-K26'),
    (u'гастрит и дуоденит', u'12.2',u'K29'),
    (u'функциональные расстройства желудка', u'12.3', u'K30-K31'),
    (u'неинфекционный энтерит и колит', u'12.4',u'K50-K52'),
    (u'болезни печени', u'12.5',u'K70-K76'),
    (u'болезни желчного пузыря, желчевыводящих путей', u'12.6',u'K80-K83'),
    (u'болезни поджелудочной железы', u'12.7',u'K85-K86'),
    (u'болезни кожи и подкожной клетчатки', u'13.0',u'L00-L99'),
    (u'из них: атопический дерматит', u'13.1',u'L20'),
    (u'контактный дерматит', u'13.2',u'L23-L25'),
    (u'болезни костно-мышечной системы и соединительной ткани', u'14.0',u'M00-M99'),
    (u'из них: реактивные артропатии', u'14.1',u'M02'),
    (u'ревматоидный артрит (серопозитивный и серонегативный, юношеский (ювенильный))', u'14.2',u'M05, M06, M08'),
    (u'юношеский (ювенильный) артрит', u'14.3', u'M08'),
    (u'артрозы',u'14.4',u'M15-M19'),
    (u'системные поражения соединительной ткани', u'14.5',u'M30-M35'),
    (u'анкилозирующий спондилит', u'14.6',u'M45'),
    (u'остеопороз', u'14.7',u'M80-M81'),
    (u'болезни мочеполовой системы', u'15.0',u'N00-N99'),
    (u'из них: гломерулярные, тубулоинтерстициальные болезни почек, другие болезни почки и мочеточника', u'15.1',u'N00-N16, N25-N28'),
    (u'почечная недостаточность',u'15.2',u'N17-N19'),
    (u'мочекаменная болезнь', u'15.3',u'N20-N23'),
    (u'болезни предстательной железы', u'15.4',u'N40-N42'),
    (u'мужское бесплодие', u'15.5',u'N46'),
    (u'доброкачественная дисплазия, гипертрофия молочной железы', u'15.6',u'N60, N62-N63'),
    (u'сальпингит и оофорит',u'15.7', u'N70'),
    (u'эндометриоз', u'15.8',u'N80'),
    (u'эрозия и эктропион шейки матки', u'15.9',u'N86'),
    (u'расстройства менструаций', u'15.10',u'N91-N94'),
    (u'нарушение менопаузы и другие нарушения в околоменопаузном периоде', u'15.11',u'N95'),
    (u'женское бесплодие',u'15.12',u'N97'),
    (u'беременность, роды и послеродовой период', u'16.0',u'O00-O99'),
    (u'врожденные аномалии (пороки развития), деформации и хромосомные нарушения', u'18.0',u'Q00-Q99'),
    (u'из них: врожденные аномалии системы кровообращения', u'18.1',u'Q20-Q28'),
    (u'симптомы, признаки и отклонения от нормы, выявленные при клинических и лабораторных исследованиях, не классифицированные в других рубриках', u'19.0',u'R00-R99'),
    (u'травмы, отравления и некоторые другие последствия воздействия внешних причин',u'20.0',u'S00-T98')
]


def selectData(begDate, endDate, workOrgId,
               sex, ageFrom, ageTo,
               areaIdEnabled, areaId, MKBFilter,
               MKBFrom, MKBTo, MKBExFilter,
               MKBExFrom, MKBExTo, socStatusType,
               socStatusClass, forTeenager,
               orgStructureAttachTypeId,
               personId):

    db = QtGui.qApp.db
    tableDiagnosis = db.table('Diagnosis')
    tableClient = db.table('Client')
    tableClientWork = db.table('ClientWork')
    tableClientAddress = db.table('ClientAddress')
    tableAddress = db.table('Address')
    tableDiagnostic = db.table('Diagnostic')
    tableEvent = db.table('Event')
    tableClientSocStatus = db.table('ClientSocStatus')
    tablePerson = db.table('Person')

    queryTable = tableDiagnosis
    queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableDiagnosis['client_id']))
    queryTable = queryTable.innerJoin(tableDiagnostic, tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']))
    queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableDiagnostic['event_id']))

    cond = [tableDiagnosis['deleted'].eq(0)]

    if personId:
        queryTable = queryTable.innerJoin(tablePerson, tableEvent['execPerson_id'].eq(tablePerson['id']))
        cond.append(tablePerson['id'].eq(personId))

    if MKBFilter == 1:
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    if MKBExFilter == 1:
        cond.append(tableDiagnosis['MKBEx'].ge(MKBExFrom))
        cond.append(tableDiagnosis['MKBEx'].le(MKBExTo))
    if workOrgId:
        queryTable = queryTable.innerJoin(tableClientWork, tableClientWork['client_id'].eq(tableClient['id']))
        cond.append(tableClientWork['org_id'].eq(workOrgId))
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if ageFrom <= ageTo:
        cond.append('Diagnosis.endDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
        cond.append('Diagnosis.endDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if areaIdEnabled:
        queryTable = queryTable.innerJoin(tableClientAddress, db.joinAnd([tableClientAddress['client_id'].eq(tableDiagnosis['client_id']), 'ClientAddress.id = (SELECT MAX(id) FROM ClientAddress AS CA0 WHERE CA0.Type=0 and CA0.client_id = Diagnosis.client_id)']))
        queryTable = queryTable.innerJoin(tableAddress, tableAddress['id'].eq(tableClientAddress['address_id']))
        if areaId:
            orgStructureIdList = getOrgStructureDescendants(areaId)
        else:
            orgStructureIdList = getOrgStructures(QtGui.qApp.currentOrgId())
        tableOrgStructureAddress = db.table('OrgStructure_Address')
        tableAddress = db.table('Address')
        subCond = [ tableOrgStructureAddress['master_id'].inlist(orgStructureIdList),
                    tableOrgStructureAddress['house_id'].eq(tableAddress['house_id']),
                  ]
        cond.append(db.existsStmt(tableOrgStructureAddress, subCond))
    if socStatusType or socStatusClass:
        queryTable = queryTable.innerJoin(tableClientSocStatus, tableClient['id'].eq(tableClientSocStatus['client_id']))
        if socStatusType: cond.append(tableClientSocStatus['socStatusType_id'].eq(socStatusType))
        if socStatusClass: cond.append(tableClientSocStatus['socStatusClass_id'].eq(socStatusClass))
    if forTeenager:
        cond.append('age(Client.birthDate, Event.setDate) <= 17')
        if orgStructureAttachTypeId:
            tableClientAttach = db.table('ClientAttach')
            tableOrgStructure = db.table('OrgStructure')
            attachTypeId = forceRef(db.translate('rbAttachType', 'code', u'1', 'id'))
            queryTable = queryTable.leftJoin(tableClientAttach, '''ClientAttach.id = (SELECT max(clAttach.id)
                                                                                                                    FROM ClientAttach clAttach
                                                                                                                    WHERE clAttach.attachType_id = %s
                                                                                                                    AND clAttach.client_id = Client.id)''' % (attachTypeId))
            queryTable = queryTable.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableClientAttach['orgStructure_id']))
            orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureAttachTypeId)
            cond.append(tableClientAttach['orgStructure_id'].inlist(orgStructureIdList))
    if not forTeenager:
        endDate1 = forceString(endDate)
        endDate1 = endDate1.split('.')
        endDateYear = endDate
        begDateYear = endDate
        begDateYear.setDate(forceInt(endDate1[2]),1,1)
    else:
        begDateYear = begDate
        endDateYear = endDate

    return db.selectStmt(queryTable, ['''COUNT( IF (DATE(Event.`setDate`) >= DATE('%s'),Diagnosis.`id`,NULL)) AS countSetInYear''' % begDateYear.toString('yyyy-MM-dd'),
                                      '''COUNT( IF (DATE(Event.`setDate`) >= DATE('%s') AND ((Diagnostic.`character_id`= 1) OR (Diagnostic.`character_id`= 2)),Diagnosis.`id`,NULL)) AS countSetFirstInYear''' % begDateYear.toString('yyyy-MM-dd'),
                                      '''COUNT( IF (DATE(Event.`execDate`) >= DATE('%s'),Diagnosis.`id`,NULL)) AS countExecInYear''' % begDateYear.toString('yyyy-MM-dd'),
                                      '''COUNT( IF (DATE(Event.`setDate`) <= DATE('%s') AND (Diagnostic.`dispanser_id` = 2),Diagnosis.`id`,NULL)) AS countInLastYear''' % begDateYear.toString('yyyy-MM-dd'),
                                      '''COUNT( IF (DATE(Event.`setDate`) >= DATE('%s') AND (Diagnostic.`dispanser_id` = 1),Diagnosis.`id`,NULL)) AS countInThisYear''' % begDateYear.toString('yyyy-MM-dd'),
                                      tableDiagnosis['MKB'],
                                      tableDiagnosis['dispanser_id']],
                         where=cond,group='Diagnosis.MKB')


def selectDataHurt(begDate, endDate, workOrgId, sex, ageFrom, ageTo, areaIdEnabled, areaId, MKBFilter, MKBFrom, MKBTo, MKBExFilter, MKBExFrom, MKBExTo, socStatusType, socStatusClass, forTeenager, orgStructureAttachTypeId):

    db = QtGui.qApp.db
    tableDiagnosis = db.table('Diagnosis')
    tableClient = db.table('Client')
    tableClientWork = db.table('ClientWork')
    tableClientWorkHurt = db.table('ClientWork_Hurt')
    tableClientAddress = db.table('ClientAddress')
    tableAddress = db.table('Address')
    tableDiagnostic = db.table('Diagnostic')
    tableEvent = db.table('Event')
    tableClientSocStatus = db.table('ClientSocStatus')
    queryTable = tableDiagnosis
    queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableDiagnosis['client_id']))
    queryTable = queryTable.innerJoin(tableClientWork, tableClientWork['client_id'].eq(tableClient['id']))
    queryTable = queryTable.innerJoin(tableClientWorkHurt, tableClientWorkHurt['master_id'].eq(tableClientWork['id']))
    queryTable = queryTable.innerJoin(tableDiagnostic, tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']))
    queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableDiagnostic['event_id']))
    cond  = [tableDiagnosis['deleted'].eq(0)]
    if MKBFilter == 1:
        cond.append(tableDiagnosis['MKB'].ge(MKBFrom))
        cond.append(tableDiagnosis['MKB'].le(MKBTo))
    if MKBExFilter == 1:
        cond.append(tableDiagnosis['MKBEx'].ge(MKBExFrom))
        cond.append(tableDiagnosis['MKBEx'].le(MKBExTo))
    if workOrgId:
        cond.append(tableClientWork['org_id'].eq(workOrgId))
    if sex:
        cond.append(tableClient['sex'].eq(sex))
    if not forTeenager:
        if ageFrom <= ageTo:
            cond.append('Diagnosis.endDate >= ADDDATE(Client.birthDate, INTERVAL %d YEAR)'%ageFrom)
            cond.append('Diagnosis.endDate < SUBDATE(ADDDATE(Client.birthDate, INTERVAL %d YEAR),1)'%(ageTo+1))
    if areaIdEnabled:
        queryTable = queryTable.innerJoin(tableClientAddress, db.joinAnd([tableClientAddress['client_id'].eq(tableDiagnosis['client_id']), 'ClientAddress.id = (SELECT MAX(id) FROM ClientAddress AS CA0 WHERE CA0.Type=0 and CA0.client_id = Diagnosis.client_id)']))
        queryTable = queryTable.innerJoin(tableAddress, tableAddress['id'].eq(tableClientAddress['address_id']))
        if areaId:
            orgStructureIdList = getOrgStructureDescendants(areaId)
        else:
            orgStructureIdList = getOrgStructures(QtGui.qApp.currentOrgId())
        tableOrgStructureAddress = db.table('OrgStructure_Address')
        tableAddress = db.table('Address')
        subCond = [ tableOrgStructureAddress['master_id'].inlist(orgStructureIdList),
                    tableOrgStructureAddress['house_id'].eq(tableAddress['house_id']),
                  ]
        cond.append(db.existsStmt(tableOrgStructureAddress, subCond))
    if socStatusType or socStatusClass:
        queryTable = queryTable.innerJoin(tableClientSocStatus, tableClient['id'].eq(tableClientSocStatus['client_id']))
        if socStatusType: cond.append(tableClientSocStatus['socStatusType_id'].eq(socStatusType))
        if socStatusClass: cond.append(tableClientSocStatus['socStatusClass_id'].eq(socStatusClass))
    if forTeenager:
        cond.append('age(Client.birthDate, Diagnosis.endDate) <= 17')
        if orgStructureAttachTypeId:
            tableClientAttach = db.table('ClientAttach')
            tableOrgStructure = db.table('OrgStructure')
            attachTypeId = forceRef(db.translate('rbAttachType', 'code', u'1', 'id'))
            queryTable = queryTable.leftJoin(tableClientAttach, '''ClientAttach.id =(SELECT max(clAttach.id)
                                                                                                                    FROM ClientAttach clAttach
                                                                                                                    WHERE clAttach.attachType_id = %s
                                                                                                                    AND clAttach.client_id = Client.id)''' % (attachTypeId))
            queryTable = queryTable.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableClientAttach['orgStructure_id']))
            orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureAttachTypeId)
            cond.append(tableClientAttach['orgStructure_id'].inlist(orgStructureIdList))
    if not forTeenager:
        endDate1 = forceString(endDate)
        endDate1 = endDate1.split('.')
        endDateYear = endDate
        begDateYear = endDate
        begDateYear.setDate(forceInt(endDate1[2]),1,1)
    else:
        begDateYear = begDate
        endDateYear = endDate

    if forTeenager:
        select = ['''COUNT( IF (DATE(Event.`setDate`) >= DATE('%s') AND age(Client.birthDate, Event.setDate) IN (15, 16, 17),Diagnosis.`id`,NULL)) AS countHurtSetInYear''' % begDateYear.toString('yyyy-MM-dd'),
                   '''COUNT( IF (DATE(Event.`setDate`) >= DATE('%s') AND ((Diagnostic.`character_id`= 1) OR (Diagnostic.`character_id`= 2)) AND age(Client.birthDate, Event.setDate) IN (15, 16, 17),Diagnosis.`id`,NULL)) AS countHurtSetFirstInYear''' % begDateYear.toString('yyyy-MM-dd'),
                   '''COUNT( IF (DATE(Event.`execDate`) >= DATE('%s') AND age(Client.birthDate, Event.setDate) IN (15, 16, 17),Diagnosis.`id`,NULL)) AS countHurtExecInYear''' % begDateYear.toString('yyyy-MM-dd'),
                   '''COUNT( IF (DATE(Event.`setDate`) <= DATE('%s') AND (Diagnostic.`dispanser_id` = 2) AND age(Client.birthDate, Event.setDate) IN (15, 16, 17),Diagnosis.`id`,NULL)) AS countHurtInLastYear''' % begDateYear.toString('yyyy-MM-dd'),
                   '''COUNT( IF (DATE(Event.`setDate`) >= DATE('%s') AND (Diagnostic.`dispanser_id` = 1) AND age(Client.birthDate, Event.setDate) IN (15, 16, 17),Diagnosis.`id`,NULL)) AS countHurtInThisYear''' % begDateYear.toString('yyyy-MM-dd'),
                  ]
    else:
         select = ['''COUNT( IF (DATE(Event.`setDate`) >= DATE('%s') AND ClientWork_Hurt.`master_id` IS NOT NULL,Diagnosis.`id`,NULL)) AS countHurtSetInYear''' % begDateYear.toString('yyyy-MM-dd'),
                   '''COUNT( IF (DATE(Event.`setDate`) >= DATE('%s') AND ((Diagnostic.`character_id`= 1) OR (Diagnostic.`character_id`= 2)) AND ClientWork_Hurt.`master_id` IS NOT NULL,Diagnosis.`id`,NULL)) AS countHurtSetFirstInYear''' % begDateYear.toString('yyyy-MM-dd'),
                   '''COUNT( IF (DATE(Event.`execDate`) >= DATE('%s') AND ClientWork_Hurt.`master_id` IS NOT NULL,Diagnosis.`id`,NULL)) AS countHurtExecInYear''' % begDateYear.toString('yyyy-MM-dd'),
                   '''COUNT( IF (DATE(Event.`setDate`) <= DATE('%s') AND (Diagnostic.`dispanser_id` = 2) AND ClientWork_Hurt.`master_id` IS NOT NULL,Diagnosis.`id`,NULL)) AS countHurtInLastYear''' % begDateYear.toString('yyyy-MM-dd'),
                   '''COUNT( IF (DATE(Event.`setDate`) >= DATE('%s') AND (Diagnostic.`dispanser_id` = 1) AND ClientWork_Hurt.`master_id` IS NOT NULL,Diagnosis.`id`,NULL)) AS countHurtInThisYear''' % begDateYear.toString('yyyy-MM-dd'),
                  ]
    select.append(tableDiagnosis['MKB'])
    select.append(tableDiagnosis['dispanser_id'])

    return db.selectStmt(queryTable, select,
                         where=cond,group='Diagnosis.MKB')


class CDispanserRegistry(CReport):
    def __init__(self, parent, forTeenager = False):
        CReport.__init__(self, parent)
        self.forTeenager = forTeenager
        self.setTitle(u'Диспансерный учёт:')


    def getSetupDialog(self, parent):
        result = CDispObservationListSetupDialog(parent)
        result.setTitle(self.title())
        result.lblOrgStrucutreAttachType.setVisible(False)
        result.cmbOrgStructureAttachType.setVisible(False)
        if self.forTeenager:
            result.lblAgeTo.setVisible(False)
            result.lblAge.setVisible(False)
            result.lblAgeYears.setVisible(False)
            result.edtAgeFrom.setVisible(False)
            result.edtAgeTo.setVisible(False)
            result.lblOrgStrucutreAttachType.setVisible(True)
            result.cmbOrgStructureAttachType.setVisible(True)
        result.setVisibleSocStatus(True)
        return result


    def build(self, params):
        mapMainRows = createMapCodeToRowIdx( [row[2] for row in MainRows] )

        begDate = params.get('begDate', None)
        endDate = params.get('endDate', None)
        workOrgId = params.get('workOrgId', None)
        sex = params.get('sex', 0)
        ageFrom = params.get('ageFrom', 0)
        ageTo = params.get('ageTo', 150)
        areaIdEnabled = params.get('areaIdEnabled', False)
        areaId = params.get('areaId', None)
        MKBFilter = params.get('MKBFilter', 0)
        MKBFrom = params.get('MKBFrom', 'A00')
        MKBTo = params.get('MKBTo', 'Z99.9')
        MKBExFilter = params.get('MKBExFilter', 0)
        MKBExFrom = params.get('MKBExFrom', 'A00')
        MKBExTo = params.get('MKBExTo', 'Z99.9')
        socStatusType = params.get('socStatusType', None)
        socStatusClass = params.get('socStatusClass', None)
        orgStructureAttachTypeId = params.get('orgStructureAttachTypeId', None)
        personId = params.get('personId', None)

        endDate1 = forceString(endDate)
        endDate1 = endDate1.split('.')

        rowSize = 10
        reportMainData = [ [0]*rowSize for row in xrange(len(MainRows)) ]

        query = QtGui.qApp.db.query(selectData(begDate, endDate, workOrgId,
                                               sex, ageFrom, ageTo, areaIdEnabled,
                                               areaId, MKBFilter, MKBFrom, MKBTo,
                                               MKBExFilter, MKBExFrom, MKBExTo,
                                               socStatusType, socStatusClass,
                                               self.forTeenager, orgStructureAttachTypeId,
                                               personId))

        self.setQueryText(forceString(query.lastQuery()))
        while query.next() :
            record    = query.record()
            MKB       = normalizeMKB(forceString(record.value('MKB')))
            endDispanserDate = forceDate(record.value('endDate'))
            dispanserId = forceInt(record.value('dispanser_id'))
            countSetInYear = forceInt(record.value('countSetInYear'))
            countExecInYear = forceInt(record.value('countExecInYear'))
            countSetFirstInYear = forceInt(record.value('countSetFirstInYear'))
            countInLastYear = forceInt(record.value('countInLastYear'))
            countInThisYear = forceInt(record.value('countInThisYear'))

            for row in mapMainRows.get(MKB, []):
                reportLine = reportMainData[row]
                reportLine[0] += countInLastYear
                reportLine[2] += countSetInYear
                reportLine[4] += countSetFirstInYear
                reportLine[6] += countExecInYear
                reportLine[8] += countInThisYear

        query = QtGui.qApp.db.query(selectDataHurt(begDate, endDate, workOrgId, sex, ageFrom, ageTo, areaIdEnabled, areaId, MKBFilter, MKBFrom, MKBTo, MKBExFilter, MKBExFrom, MKBExTo, socStatusType, socStatusClass, self.forTeenager, orgStructureAttachTypeId))

        while query.next() :
            record    = query.record()
            MKB       = normalizeMKB(forceString(record.value('MKB')))
            endDispanserDate = forceDate(record.value('endDate'))
            dispanserId = forceInt(record.value('dispanser_id'))
            countHurtSetInYear = forceInt(record.value('countHurtSetInYear'))
            countHurtExecInYear = forceInt(record.value('countHurtExecInYear'))
            countHurtSetFirstInYear = forceInt(record.value('countHurtSetFirstInYear'))
            countHurtInLastYear = forceInt(record.value('countHurtInLastYear'))
            countHurtInThisYear = forceInt(record.value('countHurtInThisYear'))

            for row in mapMainRows.get(MKB, []):
                reportLine = reportMainData[row]
                reportLine[1] += countHurtInLastYear
                reportLine[3] += countHurtSetInYear
                reportLine[5] += countHurtSetFirstInYear
                reportLine[7] += countHurtExecInYear
                reportLine[9] += countHurtInThisYear


        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        if self.forTeenager:
            column = u'из нах мальчиков 15-17 лет'
        else:
            column = u'Из них с проф. вредностью'

        tableColumns = [
            ('10%', [u'Нозологическая группа', u'', u''], CReportBase.AlignLeft),
            ('10%', [u'Код МКБ', u'', u''], CReportBase.AlignLeft),
            ('10%', [u'Состояло на начало %s года' %endDate1[2], u'Всего', u''], CReportBase.AlignLeft),
            ('10%', [u'', column, u''], CReportBase.AlignLeft),
            ('5%', [u'Взято на Д учёт в %s году' %endDate1[2], u'Всего', u''], CReportBase.AlignLeft),
            ('5%', [u'', column, u''], CReportBase.AlignLeft),
            ('5%', [u'', u'Из них с впервые установленным диагнозом в отчётном году (+)', u'Всего'], CReportBase.AlignLeft),
            ('5%', [u'', u'', column], CReportBase.AlignLeft),
            ('10%', [u'Снято с Д учёта в %s году' %endDate1[2], u'Всего', u''], CReportBase.AlignLeft),
            ('10%', [u'', column, u''], CReportBase.AlignLeft),
            ('10%', [u'Состоит на Д учёте на конец %s года' %endDate1[2], u'Всего', u''], CReportBase.AlignLeft),
            ('10%', [u'', column, u''], CReportBase.AlignLeft)
            ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 3, 1) # Наименование
        table.mergeCells(0, 1, 3, 1) # Код МКБ
        table.mergeCells(0, 2, 1, 2) # Состояло
        table.mergeCells(1, 2, 2, 1)
        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(0, 4, 1, 4) # Взято на учёт
        table.mergeCells(1, 4, 2, 1)
        table.mergeCells(1, 5, 2, 1)
        table.mergeCells(1, 6, 1, 2)
        table.mergeCells(2, 6, 1, 1)
        table.mergeCells(2, 7, 1, 1)
        table.mergeCells(0, 8, 1, 2) #Снято с учёта
        table.mergeCells(1, 8, 2, 1)
        table.mergeCells(1, 9, 2, 1)
        table.mergeCells(0, 10, 1, 2) #Состоит на учёте
        table.mergeCells(1, 10, 2, 1)
        table.mergeCells(1, 11, 2, 1)


        for row, rowDescr in enumerate(MainRows):
            reportLine = reportMainData[row]
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[2])
            table.setText(i, 2, reportLine[0])
            table.setText(i, 3, reportLine[1])
            table.setText(i, 4, reportLine[2])
            table.setText(i, 5, reportLine[3])
            table.setText(i, 6, reportLine[4])
            table.setText(i, 7, reportLine[5])
            table.setText(i, 8, reportLine[6])
            table.setText(i, 9, reportLine[7])
            table.setText(i, 10, reportLine[8])
            table.setText(i, 11, reportLine[9])

        cursor.movePosition(QtGui.QTextCursor.End)
        return doc