# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceDate
from Events.Utils import getEventLengthDays
from library.Utils import forceString, getVal, forceRef
from Ui_Report14DS_3000 import Ui_Report14DS_3000_SetupDialog
from library.vm_collections import OrderedDict

#
#  razlichni se kverinjata za 3000 i 3500
#
def selectData(params, org_id, bedProfile, MKB_query):
    stmt = u'''
     SELECT
     ( SELECT COUNT(vypisannye.col_4) FROM (
     SELECT c.id AS col_4
        FROM Event
          INNER JOIN Action ON Event.id = Action.event_id
          INNER JOIN ActionType ON Action.actionType_id = ActionType.id
          INNER JOIN ActionPropertyType AS BED_APT ON ActionType.id = BED_APT.actionType_id AND BED_APT.name = 'койка'
          INNER JOIN ActionProperty AS BED_AP ON BED_APT.id = BED_AP.type_id AND BED_AP.action_id = Action.id
          INNER JOIN ActionProperty_HospitalBed AS BED ON BED_AP.id = BED.id
          INNER JOIN OrgStructure_HospitalBed oh ON BED.value = oh.id

          INNER JOIN ActionPropertyType AS OS_APT ON ActionType.id = OS_APT.actionType_id AND OS_APT.name = 'отделение пребывания'
          INNER JOIN ActionProperty AS OS_AP ON OS_APT.id = OS_AP.type_id AND Action.id = OS_AP.action_id
          INNER JOIN ActionProperty_OrgStructure AS OS ON OS_AP.id = OS.id
          INNER JOIN OrgStructure ON OS.value = OrgStructure.id
          INNER JOIN Client c ON Event.client_id = c.id

          INNER JOIN Diagnostic d1 ON Event.id = d1.event_id
          INNER JOIN Diagnosis d ON d1.diagnosis_id = d.id
          INNER JOIN rbDiagnosisType r ON d1.diagnosisType_id = r.id

        WHERE ActionType.name = 'Движение'
          AND OrgStructure.id = %s
          AND %s
          AND OrgStructure.type = 8
          AND OrgStructure.hasHospitalBeds=1
          AND DATE(Event.execDate) >= DATE('%s')
          AND DATE(Event.execDate) <= DATE('%s')
          AND LTRIM(oh.age) LIKE '0г%%'
          AND Event.deleted = 0
          AND d.deleted = 0
          AND Action.deleted = 0
          AND %s
          AND (r.code=01 OR r.code=02)
          GROUP BY Event.id

    ) vypisannye
        ) AS discharge_Patients_SDP,
        (
    SELECT COUNT(vypisannye.col_4) FROM (
     SELECT c.id AS col_4
        FROM Event
          INNER JOIN Action ON Event.id = Action.event_id
          INNER JOIN ActionType ON Action.actionType_id = ActionType.id
          INNER JOIN ActionPropertyType AS BED_APT ON ActionType.id = BED_APT.actionType_id AND BED_APT.name = 'койка'
          INNER JOIN ActionProperty AS BED_AP ON BED_APT.id = BED_AP.type_id AND BED_AP.action_id = Action.id
          INNER JOIN ActionProperty_HospitalBed AS BED ON BED_AP.id = BED.id
          INNER JOIN OrgStructure_HospitalBed oh ON BED.value = oh.id

          INNER JOIN ActionPropertyType AS OS_APT ON ActionType.id = OS_APT.actionType_id AND OS_APT.name = 'отделение пребывания'
          INNER JOIN ActionProperty AS OS_AP ON OS_APT.id = OS_AP.type_id AND Action.id = OS_AP.action_id
          INNER JOIN ActionProperty_OrgStructure AS OS ON OS_AP.id = OS.id
          INNER JOIN OrgStructure ON OS.value = OrgStructure.id
          INNER JOIN Client c ON Event.client_id = c.id

          INNER JOIN Diagnostic d1 ON Event.id = d1.event_id
          INNER JOIN Diagnosis d ON d1.diagnosis_id = d.id
          INNER JOIN rbDiagnosisType r ON d1.diagnosisType_id = r.id

        WHERE ActionType.name = 'Движение'
          AND OrgStructure.id = %s
          AND OrgStructure.type = 7
          AND OrgStructure.hasHospitalBeds=1
          AND %s
          AND DATE(Event.execDate) >= DATE('%s')
          AND DATE(Event.execDate) <= DATE('%s')
          AND LTRIM(oh.age) LIKE '0г%%'
          AND Event.deleted = 0
          AND d.deleted = 0
          AND Action.deleted = 0
          AND %s
          AND (r.code=01 OR r.code=02)
          GROUP BY Event.id
    ) vypisannye
        ) AS discharge_Patients_DS,


      (
       SELECT COUNT(pacients.id) FROM(
      SELECT c.id
            FROM Action a
              LEFT JOIN ActionProperty ap ON a.id = ap.action_id
              INNER JOIN ActionPropertyType apt ON ap.type_id = apt.id
              INNER JOIN ActionType act ON a.actionType_id = act.id
              INNER JOIN Event e ON a.event_id = e.id
              INNER JOIN Client c ON e.client_id = c.id
              LEFT JOIN ActionProperty_OrgStructure ap_os ON ap.id = ap_os.id
              INNER JOIN OrgStructure o ON ap_os.value = o.id
              INNER JOIN OrgStructure_HospitalBed oh ON o.id = oh.master_id
              INNER JOIN rbResult r ON e.result_id = r.id
              INNER JOIN Diagnostic d1 ON e.id = d1.event_id
              INNER JOIN Diagnosis d ON d1.diagnosis_id = d.id
              INNER JOIN rbDiagnosisType rbDiagType ON d1.diagnosisType_id = rbDiagType.id


              WHERE ap_os.value = %s
                    AND %s
                    AND o.hasHospitalBeds=1 # imeet kojki shtiklirano e
                    AND o.type=8 #SDP
                    AND DATE(e.execDate) >= DATE('%s')
                    AND DATE(e.execDate) <= DATE('%s')
                    AND LTRIM(oh.age) LIKE '0г%%'
                    AND r.isDeath=1
                    AND e.deleted = 0
                    AND a.deleted = 0
                    AND %s

                    AND (rbDiagType.code=01 OR rbDiagType.code=02)
                    GROUP BY e.id
        ) AS pacients
      ) AS dead_SDP,

      (
       SELECT COUNT(pacients.id) FROM(
      SELECT c.id
            FROM Action a
              LEFT JOIN ActionProperty ap ON a.id = ap.action_id
              INNER JOIN ActionPropertyType apt ON ap.type_id = apt.id
              INNER JOIN ActionType act ON a.actionType_id = act.id
              INNER JOIN Event e ON a.event_id = e.id
              INNER JOIN Client c ON e.client_id = c.id
              LEFT JOIN ActionProperty_OrgStructure ap_os ON ap.id = ap_os.id
              INNER JOIN OrgStructure o ON ap_os.value = o.id
              INNER JOIN OrgStructure_HospitalBed oh ON o.id = oh.master_id
              #INNER JOIN ActionProperty_String aps ON ap.id = aps.id
              INNER JOIN rbResult r ON e.result_id = r.id

              INNER JOIN Diagnostic d1 ON e.id = d1.event_id
              INNER JOIN Diagnosis d ON d1.diagnosis_id = d.id
              INNER JOIN rbDiagnosisType rbDiagType ON d1.diagnosisType_id = rbDiagType.id


              WHERE ap_os.value = %s
                    AND %s
                    AND o.hasHospitalBeds=1
                    AND o.type=7
                    AND DATE(e.execDate) >= DATE('%s')
                    AND DATE(e.execDate) <= DATE('%s')
                    AND LTRIM(oh.age) LIKE '0г%%'
                    AND r.isDeath=1
                    AND e.deleted = 0
                    AND a.deleted = 0
                    AND %s

                    AND (rbDiagType.code=01 OR rbDiagType.code=02)
                    GROUP BY e.id
        ) AS pacients
      ) AS dead_DS
        '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (
                             org_id, bedProfile,
                             begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'), MKB_query,
                             org_id, bedProfile,
                             begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'), MKB_query,
                             org_id, bedProfile,
                             begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'), MKB_query,
                             org_id, bedProfile,
                             begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'), MKB_query
                            ))


"""
vidi za tipot na podrazdelenieto da se implementira
"""
def selectDataMKB(params, org_id, bedProfile, o_type, MKB_query):
    stmt = u'''
    SELECT d.MKB AS MKB
        FROM Event
          INNER JOIN Action ON Event.id = Action.event_id
          INNER JOIN ActionType ON Action.actionType_id = ActionType.id
          INNER JOIN ActionPropertyType AS BED_APT ON ActionType.id = BED_APT.actionType_id AND BED_APT.name = 'койка'
          INNER JOIN ActionProperty AS BED_AP ON BED_APT.id = BED_AP.type_id AND BED_AP.action_id = Action.id
          INNER JOIN ActionProperty_HospitalBed AS BED ON BED_AP.id = BED.id
          INNER JOIN OrgStructure_HospitalBed oh ON BED.value = oh.id

          INNER JOIN ActionPropertyType AS OS_APT ON ActionType.id = OS_APT.actionType_id AND OS_APT.name = 'отделение пребывания'
          INNER JOIN ActionProperty AS OS_AP ON OS_APT.id = OS_AP.type_id AND Action.id = OS_AP.action_id
          INNER JOIN ActionProperty_OrgStructure AS OS ON OS_AP.id = OS.id
          INNER JOIN OrgStructure ON OS.value = OrgStructure.id
          INNER JOIN Client c ON Event.client_id = c.id

          INNER JOIN Diagnostic d1 ON Event.id = d1.event_id
          INNER JOIN Diagnosis d ON d1.diagnosis_id = d.id
          INNER JOIN rbDiagnosisType r ON d1.diagnosisType_id = r.id

        WHERE ActionType.name = 'Движение'
          AND OrgStructure.id = %s
          AND %s
          AND OrgStructure.type = %s
          AND OrgStructure.hasHospitalBeds=1
          AND DATE(Event.execDate) >= DATE('%s')
          AND DATE(Event.execDate) <= DATE('%s')
          AND LTRIM(oh.age) LIKE '0г%%' # 0г-17г
          AND Event.deleted = 0
          AND d.deleted=0
          AND Action.deleted = 0
          AND %s
          AND (r.code=01 OR r.code=02)
          GROUP BY d.MKB
    ;
        '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (
        org_id, bedProfile, o_type,
        begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'), MKB_query
    ))


def selectData_PacientDays(params, org_id, bedProfile, o_type, MKB_query):
    stmt = u'''
    SELECT SUM(Event.id), Event.setDate AS e_set, c.id AS c_idd, Event.execDate AS e_exec, et.id AS et_id
        FROM Event
          INNER JOIN EventType et ON Event.eventType_id = et.id
          INNER JOIN Action ON Event.id = Action.event_id
          INNER JOIN ActionType ON Action.actionType_id = ActionType.id
          INNER JOIN ActionPropertyType AS BED_APT ON ActionType.id = BED_APT.actionType_id AND BED_APT.name = 'койка'
          INNER JOIN ActionProperty AS BED_AP ON BED_APT.id = BED_AP.type_id AND BED_AP.action_id = Action.id
          INNER JOIN ActionProperty_HospitalBed AS BED ON BED_AP.id = BED.id
          INNER JOIN OrgStructure_HospitalBed oh ON BED.value = oh.id

          INNER JOIN ActionPropertyType AS OS_APT ON ActionType.id = OS_APT.actionType_id AND OS_APT.name = 'отделение пребывания'
          INNER JOIN ActionProperty AS OS_AP ON OS_APT.id = OS_AP.type_id AND Action.id = OS_AP.action_id
          INNER JOIN ActionProperty_OrgStructure AS OS ON OS_AP.id = OS.id
          INNER JOIN OrgStructure ON OS.value = OrgStructure.id
          INNER JOIN Client c ON Event.client_id = c.id

          INNER JOIN Diagnostic d1 ON Event.id = d1.event_id
          INNER JOIN Diagnosis d ON d1.diagnosis_id = d.id
          INNER JOIN rbDiagnosisType r ON d1.diagnosisType_id = r.id

        WHERE ActionType.name = 'Движение'
          AND OrgStructure.id = %s
          AND %s
          AND OrgStructure.type = %s
          AND OrgStructure.hasHospitalBeds=1
          AND DATE(Event.execDate) >= DATE('%s')
          AND DATE(Event.execDate) <= DATE('%s')
          AND LTRIM(oh.age) LIKE '0г%%' # 0г-17г
          AND Event.deleted = 0
          AND d.deleted=0
          AND Action.deleted = 0
          AND %s
          AND (r.code=01 OR r.code=02)
          GROUP BY Event.id;
        '''

    # AND o.type=%s
    # AND LTRIM(oh.age) LIKE '0%%' # 18г-150г

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (org_id, bedProfile, o_type,
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            MKB_query
                            ))


class CReportF14DSSetupDialog(QtGui.QDialog, Ui_Report14DS_3000_SetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(
            params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))
        self.cmbOrgStructure.setValue((getVal(params, 'orgStructureId', None)))

    def params(self):
        return {
                'begDate'           : self.edtBegDate.date(),
                'endDate'           : self.edtEndDate.date(),
                'orgStructureId'    : self.cmbOrgStructure.value(),
                'RegularBedId'      : self.cmbRegularBed.currentIndex(),
                'chkDenouement'     : self.chkDenouement.isChecked()
            }

    @QtCore.pyqtSlot()
    def on_buttonBox_accepted(self):
        self.accept()


class CReportF14DS(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"3. Движение пациентов в дневных стационарах, сроки и исходы лечения")

    def getSetupDialog(self, parent):
        result = CReportF14DSSetupDialog(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        doc = QtGui.QTextDocument()

        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self._title = u"3.1. Дневные стационары для детей"
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        cursor.insertText("(3500)")
        cursor.insertBlock()

        tableColumns = [
            ('24%', [u'Наименование классов МКБ-10', u'', u''], CReportBase.AlignLeft),
            ('3%', [u'№ строки', u'', u''], CReportBase.AlignLeft),
            ('10%', [u'Код по МКБ-10', u'', u''], CReportBase.AlignLeft),
            ('7%', [u'Дневные стационары медицинских организаций, оказывающих медицинскую помощь', u'в стационарных условиях', u'Выписано пациентов'], CReportBase.AlignLeft),
            ('7%', [u'', u'', u'Проведено пациенто - дней'], CReportBase.AlignLeft),
            ('7%', [u'', u'', u'Умерло'], CReportBase.AlignLeft),
            ('7%', [u'', u'в амбулаторных условиях', u'Выписано пациентов'], CReportBase.AlignLeft),
            ('7%', [u'', u'', u'Проведено пациенто - дней'], CReportBase.AlignLeft),
            ('7%', [u'', u'', u'Умерло'], CReportBase.AlignLeft),
            ('7%', [u'', u'на дому', u'Выписано пациентов'], CReportBase.AlignLeft),
            ('7%', [u'', u'', u'Проведено пациенто - дней'], CReportBase.AlignLeft),
            ('7%', [u'', u'', u'Умерло'], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)
        RegularBedId = getVal(params, 'RegularBedId', None)
        chkDenouement = getVal(params, 'chkDenouement', False)

        db = QtGui.qApp.db
        orgStructureId = getVal(params, 'orgStructureId', None)
        tblOrgstructure = db.table('OrgStructure')
        Orgstructure = db.getRecordList(tblOrgstructure, cols='id, name, parent_id')
        lst_id = []

        if orgStructureId is None:
            '''
            load everything from orgstructure, if no organisation is chosen
            '''
            for rec in Orgstructure:
                lst_id.append(int(forceString(rec.value("id"))))
        else:
            '''
            list from the organisation_tree that should be included
            '''
            lst_id.append(int(orgStructureId))
            for id in lst_id:
                for rec in Orgstructure:
                    if int(id) == int(forceString(rec.value("parent_id"))) and int(
                            forceString(rec.value("id"))) not in lst_id:
                        lst_id.append(int(forceString(rec.value("id"))))

        ii = 0
        lst_bedProfile = [
            "(oh.isPermanent = 1 OR oh.isPermanent = 0)", "oh.isPermanent = 1", "oh.isPermanent = 0"
        ]

        lst_MKB = ["'A00%%' AND 'B99%%' OR d.MKB LIKE 'B99%%'", "'C00%%' AND 'D48%%' OR d.MKB LIKE 'D48%%'",
                   "'D50%%' AND 'D89%%' OR d.MKB LIKE 'D89%%'", "'E00%%' AND 'E90%%' OR d.MKB LIKE 'E90%%'",
                   "'F00%%' AND 'F99%%' OR d.MKB LIKE 'F99%%'", "'G00%%' AND 'G99%%' OR d.MKB LIKE 'G99%%'",
                   "'H00%%' AND 'H59%%' OR d.MKB LIKE 'H59%%'", "'H60%%' AND 'H95%%' OR d.MKB LIKE 'H95%%'",
                   "'I00%%' AND 'I99%%' OR d.MKB LIKE 'I99%%'", "'J00%%' AND 'J99%%' OR d.MKB LIKE 'J99%%'",
                   "'K00%%' AND 'K93%%' OR d.MKB LIKE 'K93%%'", "'L00%%' AND 'L98%%' OR d.MKB LIKE 'L98%%'",
                   "'M00%%' AND 'M99%%' OR d.MKB LIKE 'M99%%'", "'N00%%' AND 'N99%%' OR d.MKB LIKE 'N99%%'",
                   "'O00%%' AND 'O99%%' OR d.MKB LIKE 'O99%%'", "'P00%%' AND 'P96%%' OR d.MKB LIKE 'P96%%'",
                   "'Q00%%' AND 'Q99%%' OR d.MKB LIKE 'Q99%%'", "'R00%%' AND 'R99%%' OR d.MKB LIKE 'R99%%'",
                   "'S00%%' AND 'T98%%' OR d.MKB LIKE 'T98%%'", "'Z00%%' AND 'Z99%%' OR d.MKB LIKE 'Z99%%'"]

        bedProfile = lst_bedProfile[0]
        if RegularBedId == 0:
            bedProfile = lst_bedProfile[0]
        elif RegularBedId == 1:
            bedProfile = lst_bedProfile[1]
        else:
            bedProfile = lst_bedProfile[2]

        dict_denouement_mkb = OrderedDict()
        tblMKB = db.table('MKB')

        if chkDenouement is True:
            #dict_mkb = {}
            #MKBList = db.getRecordList(tblMKB, cols=['DiagName', 'DiagID'])
            #for i in range(0, len(MKBList)):
                #mkb = MKBList[i]
                #name = mkb.indexOf('DiagName')
                #id = mkb.indexOf('DiagID')
                #dict_mkb[str(mkb.value(name).toString())] = str(mkb.value(id).toString())

            for row in range(0, len(lst_MKB)):
                for org_id in range(0, len(lst_id)):
                    MKB_query = u"d.MKB BETWEEN %s" % lst_MKB[row]
                    query_SDP = selectDataMKB(params, lst_id[org_id], bedProfile, 8, MKB_query)
                    query_DS = selectDataMKB(params, lst_id[org_id], bedProfile, 7, MKB_query)
                    self.setQueryText(forceString(query_SDP.lastQuery()))
                    self.setQueryText(forceString(query_DS.lastQuery()))
                    while query_SDP.next():
                        record = query_SDP.record()
                        mkb = forceString(record.value('MKB'))
                        mkb_name = db.getRecordEx(table=tblMKB, cols='DiagName', where=tblMKB['DiagID'].eq(mkb))
                        field = mkb_name.field(0)
                        dict_denouement_mkb[field.value().toString()] = forceString(record.value('MKB'))
                        #if mkb in dict_mkb.items():
                            #dict_denouement_mkb[name] = mkb
                        #for name, id in dict_mkb.iteritems():
                            #if id == mkb:
                                #dict_denouement_mkb[name] = id

                    while query_DS.next():
                        record = query_DS.record()
                        mkb = forceString(record.value('MKB'))
                        mkb_name = db.getRecordEx(table=tblMKB, cols='DiagName', where=tblMKB['DiagID'].eq(mkb))
                        field = mkb_name.field(0)
                        dict_denouement_mkb[field.value().toString()] = forceString(record.value('MKB'))

        elif chkDenouement is False:
            for row in range(0, len(lst_MKB)):
                dict_denouement_mkb[lst_MKB[row]] = ""

        self.createRowsCols(table, chkDenouement, dict_denouement_mkb)

        sumPac_col4 = 0
        sumDays_col5 = 0
        sumOth_col6 = 0
        sumPac_col7 = 0
        sumDays_col8 = 0
        sumOth_col9 = 0
        '''
        We are looping through list of MKB ranges, checking in each orgstructure if they have that bed
        summing the values for each bed
        '''
        for row in range(0, len(dict_denouement_mkb)):
            sum_col5 = 0
            sum_col8 = 0
            days_col5 = 0
            days_col8 = 0
            sumcol4 = 0
            sumcol6 = 0
            sumcol7 = 0
            sumcol9 = 0

            for org_id in range(0, len(lst_id)):
                if chkDenouement is False:
                    str_mkb = str(dict_denouement_mkb.keys()[row])[-6:-1]  # F99%%
                    MKB_query = u"(d.MKB BETWEEN %s OR d.MKB LIKE '%s')" % (dict_denouement_mkb.keys()[row], str_mkb)
                    '''
                    MKB_query (d.MKB BETWEEN 'E00%' AND 'E90%' OR d.MKB='E00')
                    '''
                    #MKB_query = u"d.MKB BETWEEN %s" % (dict_denouement_mkb.keys()[row])

                elif chkDenouement is True:
                    MKB_query = u"d.MKB = '%s'" % dict_denouement_mkb.values()[row]

                query_col5 = selectData_PacientDays(params, lst_id[org_id],bedProfile, 8, MKB_query)
                query_col8 = selectData_PacientDays(params, lst_id[org_id], bedProfile, 7, MKB_query)

                query = selectData(params, lst_id[org_id], bedProfile, MKB_query)

                self.setQueryText(forceString(query.lastQuery()))
                self.setQueryText(forceString(query_col5.lastQuery()))
                self.setQueryText(forceString(query_col8.lastQuery()))
                '''
                sum of pacients for every organisation (that's why in this for)
                '''
                while query_col5.next():
                    record_col5 = query_col5.record()
                    '''
                    get the number of days having in mind the length of the working week
                    '''
                    days_col5 = getEventLengthDays(
                        forceDate(record_col5.value('e_set')),
                        forceDate(record_col5.value('e_exec')),
                        countRedDays=False,
                        eventTypeId=forceString(record_col5.value('et_id')),
                        isDayStationary=True)

                    sum_col5 += int(days_col5)
                '''
                Всего, в том числе
                '''

                while query_col8.next():
                    record_col8 = query_col8.record()
                    days_col8 = getEventLengthDays(
                        forceDate(record_col8.value('e_set')),
                        forceDate(record_col8.value('e_exec')),
                        countRedDays=False,
                        eventTypeId=forceString(record_col8.value('et_id')),
                        isDayStationary=True)
                    sum_col8 += int(days_col8)

                while query.next():
                    record = query.record()
                    sumcol4 += int(forceString(record.value('discharge_Patients_SDP')))
                    sumcol7 += int(forceString(record.value('discharge_Patients_DS')))
                    sumcol6 += int(forceString(record.value('dead_SDP')))
                    sumcol9 += int(forceString(record.value('dead_DS')))

            sumDays_col5 += sum_col5
            sumDays_col8 += sum_col8

            table.setText(ii + 5, 4, sum_col5)
            table.setText(ii + 5, 7, sum_col8)

            sumPac_col4 += sumcol4
            sumPac_col7 += sumcol7
            sumOth_col6 += sumcol6
            sumOth_col9 += sumcol9
            table.setText(ii + 5, 3, sumcol4)
            table.setText(ii + 5, 5, sumcol6)
            table.setText(ii + 5, 6, sumcol7)
            table.setText(ii + 5, 8, sumcol9)

            ii = ii + 1

        '''
        sum of all the columns minus the last one (Z)
        '''
        if chkDenouement is False:
            sumPac_col4 -= int(sumcol4)
            sumDays_col5 -= int(days_col5)
            sumOth_col6 -= int(sumcol6)
            sumPac_col7 -= int(sumcol7)
            sumDays_col8 -= int(days_col8)
            sumOth_col9 -= int(sumcol9)

        table.setText(4, 3, sumPac_col4)
        table.setText(4, 4, sumDays_col5)
        table.setText(4, 5, sumOth_col6)
        table.setText(4, 6, sumPac_col7)
        table.setText(4, 7, sumDays_col8)
        table.setText(4, 8, sumOth_col9)

        self.merge_cells(table)
        return doc

    def createRowsCols(self, table, chkDenouement, dict_denouement_mkb):
        '''

        :param table:
        :param chkDenouement: bool
        :param dict_denouement_mkb: MKBs
        :return:
        '''
        lst_frth_row = [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'10', u'11', u'12']

        lst_count = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

        dict_mkb = OrderedDict()
        dict_mkb['некоторые инфекционные и паразитарные болезни'] = 'A00 - B99'
        dict_mkb['новообразования'] = 'C00 - D48'
        dict_mkb['болезни крови, кроветворных органов и отдельные нарушения, вовлекающие иммунный механизм'] = 'D50 - D89'
        dict_mkb['болезни эндокринной системы, расстройства питания и нарушения обмена веществ'] = 'E00 - E90'
        dict_mkb['психические расстройства и расстройства поведения'] = 'F00 - F99'
        dict_mkb['болезни нервной системы'] = 'G00 - G99'
        dict_mkb['болезни глаза и его придаточного аппарата'] = 'H00 - H59'
        dict_mkb['болезни уха и сосцевидного отростка'] = 'H60 - H95'
        dict_mkb['болезни системы кровообращения'] = 'I00 - I99'
        dict_mkb['болезни органов дыхания'] = 'J00 - J99'
        dict_mkb['болезни органов пищеварения'] = 'K00 - K93'
        dict_mkb['болезни кожи и подкожной клетчатки'] = 'L00 - L98'
        dict_mkb['болезни костно-мышечной системы и соединительной ткани'] = 'M00 - M99'
        dict_mkb['болезни мочеполовой системы'] = 'N00 - N99'
        dict_mkb['беременность, роды и послеродовой период'] = 'O00 - O99'
        dict_mkb['отдельные состояния, возникающие в перинатальном периоде'] = 'P00 - P96'
        dict_mkb['врожденные аномалии, пороки развития, деформации и хромосомные нарушения'] = 'Q00 - Q99'
        dict_mkb['симптомы, признаки и отклонения от нормы, выявленные при клинических и лабораторных исследованиях, ' \
                 'не классифицированные в других  рубриках'] = 'R00 - R99'
        dict_mkb['травмы, отравления и некоторые другие последствия воздействия внешних причин'] = 'S00 - T98'
        dict_mkb['Кроме того: факторы, влияющие на состояние здоровья и обращения в учреждения здравоохранения'] = 'Z00 - Z99'
        #OrderedDict((word, True) for word in dict_mkb)
        i = table.addRow()
        for j in range(0, 12):
            table.setText(i, lst_count[j], lst_frth_row[j])

        i = table.addRow()
        table.setText(i, 0, "Всего, в том числе:")
        table.setText(i, 1, "1")

        if chkDenouement is False:
            table.setText(i, 2, "A00-T98")
            for j in range(0, len(dict_mkb)):
                i = table.addRow()
                table.setText(i, 0, dict_mkb.keys()[j])
                table.setText(i, 1, lst_count[j+2])
                table.setText(i, 2, dict_mkb.values()[j])
        elif chkDenouement is True:
            table.setText(i, 2, "")
            for j in range(0, len(dict_denouement_mkb)):
                i = table.addRow()
                table.setText(i, 0, dict_denouement_mkb.keys()[j])
                table.setText(i, 1, j+2)
                table.setText(i, 2, dict_denouement_mkb.values()[j])

    def merge_cells(self, table):
        """
        :param table:
        :return:
        """
        table.mergeCells(0, 0, 3, 1)  # first column, 0,1,2 rows
        table.mergeCells(1, 0, 3, 1)
        table.mergeCells(2, 0, 3, 1)

        table.mergeCells(0, 1, 3, 1)  # second column, 0,1,2 rows
        table.mergeCells(1, 1, 3, 1)
        table.mergeCells(2, 1, 3, 1)

        table.mergeCells(0, 2, 3, 1)  # third column, 0,1,2 rows
        table.mergeCells(1, 2, 3, 1)
        table.mergeCells(2, 2, 3, 1)

        table.mergeCells(0, 3, 1, 9)  # first row, 3-12 columns
        table.mergeCells(0, 4, 1, 9)
        table.mergeCells(0, 5, 1, 9)
        table.mergeCells(0, 6, 1, 9)
        table.mergeCells(0, 7, 1, 9)
        table.mergeCells(0, 8, 1, 9)
        table.mergeCells(0, 9, 1, 9)
        table.mergeCells(0, 10, 1, 9)
        table.mergeCells(0, 11, 1, 9)

        table.mergeCells(1, 3, 1, 3) # second row, 3-6 cols
        table.mergeCells(1, 4, 1, 3)
        table.mergeCells(1, 5, 1, 3)

        table.mergeCells(1, 6, 1, 3)  # second row, 7-9 cols
        table.mergeCells(1, 7, 1, 3)
        table.mergeCells(1, 8, 1, 3)

        table.mergeCells(1, 9, 1, 3)  # second row, 10-12 cols
        table.mergeCells(1, 10, 1, 3)
        table.mergeCells(1, 11, 1, 3)


def main():
    import sys
    from library.database import connectDataBaseByInfo
    from s11main import CS11mainApp
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 229525  # 230493 #230226  # 229005

    connectionInfo = {'driverName': 'mysql',
                      'host': 'pacs',
                      'port': 3306,
                      'database': 'novros',
                      'user': 'dbuser',
                      'password': 'dbpassword',
                      'connectionName': 'vista-med',
                      'compressData': True,
                      'afterConnectFunc': None}

    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)
    CReportF14DS(None).exec_()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


