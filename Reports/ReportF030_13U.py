# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore

from library.MapCode                import createMapCodeToRowIdx
from library.Utils                  import forceDate, forceInt, forceRef, forceString
from Orgs.Utils                     import getOrgStructureDescendants, getOrgStructures
from Reports.DispObservationList    import CDispObservationListSetupDialog
from Reports.Report                 import CReport, normalizeMKB
from Reports.ReportBase             import createTable, CReportBase
from library.vm_collections import OrderedDict

QUERY = u'''
select
  c.id as cid,
  disp.code as dispanser,
  concat_ws(' ', c.lastName, c.firstName, c.patrName) as clientName,
  c.birthDate,
  getClientPolicyOnDate(c.id, true, e.execDate) as clientPolicy,
  c.SNILS,
  sst.code as socStatus,
  mkb.DiagName,
  mkb.DiagID,
  e.setDate,
  e.execDate,
  count(distinct v.id) as visits,
  if(locate('05', group_concat(r.code)) or locate('08', group_concat(r.code)) or locate('07', group_concat(et.code)), et.name, r.name) as f20
from Event e
  inner join Visit v on e.id = v.event_id
  
  inner join Client c on e.client_id = c.id
  inner join ClientSocStatus css on c.id = css.client_id
  inner join rbSocStatusClass ssc on css.socStatusClass_id = ssc.id
  inner join rbSocStatusType sst on css.socStatusType_id = sst.id
  left join ClientWork cw on c.id = cw.client_id

  inner join Person p on e.execPerson_id = p.id
  inner join Diagnosis d on d.id = getEventDiagnosis(e.id)
  inner join MKB_Tree mkb on d.MKB = mkb.DiagID
  inner join rbDispanser disp on d.dispanser_id = disp.id
  
  inner join EventType et on e.eventType_id = et.id
  inner join rbResult r on e.result_id = r.id
  inner join rbSpeciality spec on p.speciality_id = spec.id
where ssc.flatCode = 'benefits' and
      e.deleted = 0 and
      c.deleted = 0 and
      v.deleted = 0 and
      css.deleted = 0 and
      spec.code in (27, 22, 224) and (
        {cond}
      )
group by e.id
order by c.lastName, c.firstName, c.patrName, mkb.DiagID
'''

INITIAL_ROW_DICT = {
    'clientName': '-',
    'birthDate': None,
    'clientPolicy': '-',
    'SNILS': '-',
    'socStatus': '-',
    'diagName': '-',
    'diagId': '-',
    'setDate': None,
    'execDate': None,
    'visits': 0,
    'f20': ''
}


def selectData(begDate, endDate, workOrgId, sex, ageFrom, ageTo, areaIdEnabled, areaId, MKBFilter, MKBFrom, MKBTo,
               MKBExFilter, MKBExFrom, MKBExTo, socStatusType, socStatusClass, personId):
    db = QtGui.qApp.db
    cond = []
    if begDate:
        cond.append("e.execDate >= {}".format(db.formatArg(begDate)))
    if endDate:
        cond.append("e.execDate <= {}".format(db.formatArg(endDate)))
    if workOrgId:
        cond.append("cw.org_id = {}".format(db.formatArg(workOrgId)))
    if sex:
        cond.append("c.sex = {}".format(db.formatArg(sex)))
    if ageFrom <= ageTo:
        cond.append('e.execDate >= adddate(c.birthDate, interval {} year)'.format(db.formatArg(ageFrom)))
        cond.append('e.execDate < subdate(adddate(c.birthDate, interval {} year), 1)'.format(db.formatArg(ageTo + 1)))
    if MKBFilter == 1:
        cond.append('d.MKB >= {}'.format(db.formatArg(MKBFrom)))
        cond.append('d.MKB <= {}'.format(db.formatArg(MKBTo)))
    if MKBExFilter == 1:
        cond.append('d.MKBEx >= {}'.format(db.formatArg(MKBExFrom)))
        cond.append('d.MKBEx <= {}'.format(db.formatArg(MKBExTo)))
    if socStatusType:
        cond.append('css.socStatusType_id = {}'.format(db.formatArg(socStatusType)))
    if personId:
        cond.append('p.id = {}'.format(db.formatArg(personId)))
    # if areaIdEnabled:
    #     queryTable = queryTable.innerJoin(tableClientAddress, db.joinAnd([tableClientAddress['client_id'].eq(tableDiagnosis['client_id']), 'ClientAddress.id = (SELECT MAX(id) FROM ClientAddress AS CA0 WHERE CA0.Type=0 and CA0.client_id = Diagnosis.client_id)']))
    #     queryTable = queryTable.innerJoin(tableAddress, tableAddress['id'].eq(tableClientAddress['address_id']))
    #     if areaId:
    #         orgStructureIdList = getOrgStructureDescendants(areaId)
    #     else:
    #         orgStructureIdList = getOrgStructures(QtGui.qApp.currentOrgId())
    #     tableOrgStructureAddress = db.table('OrgStructure_Address')
    #     tableAddress = db.table('Address')
    #     subCond = [ tableOrgStructureAddress['master_id'].inlist(orgStructureIdList),
    #                 tableOrgStructureAddress['house_id'].eq(tableAddress['house_id']),
    #               ]
    #     cond.append(db.existsStmt(tableOrgStructureAddress, subCond))

    if not cond:
        cond = ['1=1']
    return QUERY.format(cond=db.joinAnd(cond))


class CReportF030_13U(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Ф030-13/у')

    def getSetupDialog(self, parent):
        result = CDispObservationListSetupDialog(parent)
        result.setTitle(self.title())
        result.setVisibleSocStatus(True)

        result.lblOrgStrucutreAttachType.setVisible(False)
        result.cmbOrgStructureAttachType.setVisible(False)
        result.cmbSocStatusType.setFilter('id in ({})'.format(', '.join(str(x) for x in QtGui.qApp.db.getIdList(
            stmt='''select rSST.id
                    from rbSocStatusType rSST
                      inner join rbSocStatusClassTypeAssoc rSSCTA on rSST.id = rSSCTA.type_id
                      inner join rbSocStatusClass rSSC on rSSCTA.class_id = rSSC.id
                    where rSSC.flatCode = 'benefits'
                    '''))))
        result.cmbPerson.setAcceptableSpecialities(QtGui.qApp.db.getIdList(
            stmt='''select id
                    from rbSpeciality
                    where code in (27, 22, 224)
                    '''))
        result.lblArea.setVisible(False)
        result.cmbArea.setVisible(False)
        result.lblSocStatusClass.setVisible(False)
        result.cmbSocStatusClass.setVisible(False)
        result.label.setVisible(False)
        result.cmbRowGrouping.setVisible(False)
        result.lblSpeciality.setVisible(False)
        result.cmbSpeciality.setVisible(False)
        return result

    def build(self, params):
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
        personId = params.get('personId', None)

        query = QtGui.qApp.db.query(selectData(begDate, endDate, workOrgId, sex, ageFrom, ageTo, areaIdEnabled, areaId,
                                               MKBFilter, MKBFrom, MKBTo, MKBExFilter, MKBExFrom, MKBExTo,
                                               socStatusType, socStatusClass, personId))
        self.setQueryText(forceString(query.lastQuery()))

        rows = OrderedDict()

        while query.next():
            rec = query.record()
            cid = forceRef(rec.value('cid'))
            dispanser = forceInt(rec.value('dispanser'))
            clientName = forceString(rec.value('clientName'))
            birthDate = forceDate(rec.value('birthDate'))
            clientPolicy = forceString(rec.value('clientPolicy'))
            SNILS = forceString(rec.value('SNILS'))
            socStatus = forceString(rec.value('socStatus'))
            diagName = forceString(rec.value('DiagName'))
            diagId = forceString(rec.value('DiagId'))
            setDate = forceDate(rec.value('setDate'))
            execDate = forceDate(rec.value('execDate'))
            visits = forceInt(rec.value('visits'))
            f20 = forceString(rec.value('f20'))

            d = rows.setdefault((cid, diagId), INITIAL_ROW_DICT.copy())
            if clientName:
                d['clientName'] = clientName
            if birthDate:
                d['birthDate'] = birthDate
            if clientPolicy:
                d['clientPolicy'] = clientPolicy
            if SNILS:
                d['SNILS'] = SNILS
            if socStatus:
                d['socStatus'] = socStatus
            if diagName:
                d['diagName'] = diagName
            if diagId:
                d['diagId'] = diagId
            if setDate and (not d['setDate'] or d['setDate'] > setDate) and dispanser in (1, 2):
                d['setDate'] = setDate
            if execDate and (not d['execDate'] or d['execDate'] < execDate) and dispanser in (3, 4, 5):
                d['execDate'] = execDate
            if visits:
                d['visits'] += visits
            if f20:
                d['f20'] = f20

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
            ('5%', [u'№ п/п', u'', u'', u'', u'1'], CReportBase.AlignLeft),
            ('5%', [u'Сведения врача-терапевта участкового, врача-педиатра участкового, врача общей практики '
                    u'(семейного врача)', u'Ф.И.О. пациента', u'', u'', u'2'], CReportBase.AlignLeft),
            ('5%', [u'', u'Дата рождения', u'', u'', u'3'], CReportBase.AlignLeft),
            ('5%', [u'', u'Номер полиса ОМС', u'', u'', u'4'], CReportBase.AlignLeft),
            ('5%', [u'', u'СНИЛС', u'', u'', u'5'], CReportBase.AlignLeft),
            ('5%', [u'', u'Код категории льготы', u'', u'', u'6'], CReportBase.AlignLeft),
            ('5%', [u'', u'Наименование заболевания', u'', u'', u'7'], CReportBase.AlignLeft),
            ('5%', [u'', u'Код по МКБ-10', u'', u'', u'8'], CReportBase.AlignLeft),
            ('5%', [u'', u'Дата начала диспансерного наблюдения', u'', u'', u'9'], CReportBase.AlignLeft),
            ('5%', [u'', u'Дата прекращения диспансерного наблюдения', u'', u'', u'10'], CReportBase.AlignLeft),
            ('5%', [u'', u'Число посещений', u'', u'', u'11'], CReportBase.AlignLeft),
            ('5%', [u'Сведения организационно-методического кабинета', u'Лекарственное обеспечение', u'выписано',
                    u'наименование лекарственного препарата, дозировка', u'12'], CReportBase.AlignLeft),
            ('5%', [u'', u'', u'', u'№ и серия рецепта', u'13'], CReportBase.AlignLeft),
            ('5%', [u'', u'', u'фактически получено (наименование лекарственного препарата, дозировка)', u'',
                    u'14'], CReportBase.AlignLeft),
            ('5%', [u'', u'Стоимость лекарственного обеспечения', u'', u'', u'15'], CReportBase.AlignLeft),
            ('5%', [u'', u'Санитарно-курортное лечение', u'Выдано:',
                    u'справок для получения путевки на санаторно-курортное лечение', u'16'], CReportBase.AlignLeft),
            ('5%', [u'', u'', u'', u'из них на амбулаторное курортное лечение', u'17'], CReportBase.AlignLeft),
            ('5%', [u'', u'', u'', u'санаторно-курортных карт', u'18'], CReportBase.AlignLeft),
            ('5%', [u'', u'', u'Возвращено обратных талонов санаторно-курортных карт', u'',
                    u'19'], CReportBase.AlignLeft),
            ('5%', [u'', u'Направлено на госпитализацию, медицинскую реабилитацию, обследование, консультацию',
                    u'', u'', u'20'], CReportBase.AlignLeft),
            ]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 4, 1)
        table.mergeCells(0, 1, 1, 10)
        table.mergeCells(1, 1, 3, 1)
        table.mergeCells(1, 2, 3, 1)
        table.mergeCells(1, 3, 3, 1)
        table.mergeCells(1, 4, 3, 1)
        table.mergeCells(1, 5, 3, 1)
        table.mergeCells(1, 6, 3, 1)
        table.mergeCells(1, 7, 3, 1)
        table.mergeCells(1, 8, 3, 1)
        table.mergeCells(1, 9, 3, 1)
        table.mergeCells(1, 10, 3, 1)
        table.mergeCells(0, 11, 1, 9)
        table.mergeCells(1, 11, 1, 3)
        table.mergeCells(2, 11, 1, 2)
        table.mergeCells(2, 13, 2, 1)
        table.mergeCells(1, 14, 3, 1)
        table.mergeCells(1, 15, 1, 4)
        table.mergeCells(2, 15, 1, 3)
        table.mergeCells(2, 18, 2, 1)
        table.mergeCells(1, 19, 3, 1)

        for i, row in enumerate(rows.values()):
            birthDate = row['birthDate'].toString('dd.MM.yyyy') if row['birthDate'] else '-'
            setDate = row['setDate'].toString('dd.MM.yyyy') if row['setDate'] else '-'
            execDate = row['execDate'].toString('dd.MM.yyyy') if row['execDate'] else '-'
            table.addRowWithContent(str(i+1), row['clientName'], birthDate, row['clientPolicy'], row['SNILS'],
                                    row['socStatus'], row['diagName'], row['diagId'], setDate, execDate,
                                    str(row['visits']), '', '', '', '', '', '', '', '', row['f20'])

        cursor.movePosition(QtGui.QTextCursor.End)
        return doc
