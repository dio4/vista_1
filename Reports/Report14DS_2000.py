# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import createTable, CReportBase
from library.Utils import forceDate
from Events.Utils import getEventLengthDays
from library.Utils import forceString, getVal, forceStringEx
from Ui_Report14DS_2000 import Ui_Report14DS_2000_SetupDialog
from library.vm_collections import OrderedDict


def selectData(params, org_id, bedProfile, bed_id):
    stmt=u'''
SELECT (
        SELECT SUM(s.beds) FROM (
                SELECT IF(oh.relief=2, 2, 1) AS beds FROM OrgStructure o
                INNER JOIN OrgStructure_HospitalBed oh ON o.id = oh.master_id
                INNER JOIN rbHospitalBedProfile r ON oh.profile_id = r.id
                WHERE o.id = %s # Infekcionaya bolnica dlja vzroslyh
                AND o.hasHospitalBeds=1 # imeet kojki shtiklirano e
                AND %s # shtatnaja kojka
                AND r.row_code = %s
                AND o.type=8 # SDP
                AND (LTRIM(oh.age) = '' OR LTRIM(oh.age) LIKE '18%%' )
                ) s ) AS koek_vzroslye,
                        (
             SELECT SUM(ss.beds) FROM(
                SELECT IF(oh.relief=2, 2, 1) AS beds FROM OrgStructure o
                INNER JOIN OrgStructure_HospitalBed oh ON o.id = oh.master_id
                INNER JOIN rbHospitalBedProfile r ON oh.profile_id = r.id
                WHERE o.id = %s # Infekcionaya bolnica dlja vzroslyh
                AND o.hasHospitalBeds=1 # imeet kojki shtiklirano e
                AND %s # shtatnaja kojka
                AND r.row_code = %s
                AND o.type=8 # SDP
                AND LTRIM(oh.age) LIKE '0г-%%' # 0г-17г
                ) ss
            ) AS koek_detey,
          pac.vzroslye AS col_7,
          pac.starshe AS col_8,
          pac.detey AS col_9
FROM(
   SELECT SUM(vypisanny.detey) AS detey, SUM(vypisanny.vzroslye) AS vzroslye, SUM(vypisanny.starshe) AS starshe FROM ( # kolicestvo na pacienti
                SELECT
   IF (c.sex=1,
                  ((YEAR(Event.setDate) - YEAR(DATE(c.birthDate)) - (RIGHT(DATE(Event.setDate), 5)
                  < RIGHT(DATE(c.birthDate), 5))) >= 60),
                      ((YEAR(Event.setDate) - YEAR(DATE(c.birthDate)) - (RIGHT(DATE(Event.setDate), 5)
                 < RIGHT(DATE(c.birthDate), 5))) >= 55)
                  ) AS starshe,

                  (((YEAR(Event.setDate) - YEAR(DATE(c.birthDate)) - (RIGHT(DATE(Event.setDate), 5)
                  < RIGHT(DATE(c.birthDate), 5))) < 18) and
                  (YEAR(Event.setDate) - YEAR(DATE(c.birthDate)) - (RIGHT(DATE(Event.setDate), 5)
                  < RIGHT(DATE(c.birthDate), 5))) >= 0) AS detey,
                 ((YEAR(Event.setDate) - YEAR(DATE(c.birthDate)) - (RIGHT(DATE(Event.setDate), 5)
                  < RIGHT(DATE(c.birthDate), 5))) >= 18) AS vzroslye
    FROM Event
      INNER JOIN Action ON Event.id = Action.event_id
      INNER JOIN ActionType ON Action.actionType_id = ActionType.id
      INNER JOIN ActionPropertyType AS BED_APT ON ActionType.id = BED_APT.actionType_id AND BED_APT.name = 'койка'
      INNER JOIN ActionProperty AS BED_AP ON BED_APT.id = BED_AP.type_id AND BED_AP.action_id = Action.id
      INNER JOIN ActionProperty_HospitalBed AS BED ON BED_AP.id = BED.id
      INNER JOIN OrgStructure_HospitalBed oh ON BED.value = oh.id
      INNER JOIN rbHospitalBedProfile ON oh.profile_id = rbHospitalBedProfile.id

      INNER JOIN ActionPropertyType AS OS_APT ON ActionType.id = OS_APT.actionType_id AND OS_APT.name = 'отделение пребывания'
      INNER JOIN ActionProperty AS OS_AP ON OS_APT.id = OS_AP.type_id AND Action.id = OS_AP.action_id
      INNER JOIN ActionProperty_OrgStructure AS OS ON OS_AP.id = OS.id
      INNER JOIN OrgStructure ON OS.value = OrgStructure.id

      INNER JOIN Client c ON Event.client_id = c.id

    WHERE ActionType.name = 'Движение'
      AND OrgStructure.id = %s
      AND %s
      AND rbHospitalBedProfile.row_code = %s
      AND OrgStructure.type = 8
      AND OrgStructure.hasHospitalBeds=1
      AND DATE(Event.execDate) >= DATE('%s')
      AND DATE(Event.execDate) <= DATE('%s')
      AND (LTRIM(oh.age) = '' OR LTRIM(oh.age) LIKE '18%%' OR LTRIM(oh.age) LIKE '0%%')
      AND Event.deleted = 0
      AND Action.deleted = 0
      GROUP BY Event.id

     ) AS vypisanny
      ) AS pac ;
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    print org_id, bedProfile, bed_id
    return db.query(stmt % (
                             org_id, bedProfile, bed_id,
                             org_id, bedProfile, bed_id,
                             org_id, bedProfile, bed_id,
                             begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            ))


def selectData_PacientDays(params, provedeno_dney, bedProfile, org_id, bed_id):
    stmt = u'''
      SELECT Event.setDate AS e_set, Event.execDate AS e_exec, et.id AS et_id, c.id AS c_id
          FROM Event
          INNER JOIN EventType et ON Event.eventType_id = et.id
          INNER JOIN Action ON Event.id = Action.event_id

          INNER JOIN ActionType ON Action.actionType_id = ActionType.id
          INNER JOIN ActionPropertyType AS BED_APT ON ActionType.id = BED_APT.actionType_id AND BED_APT.name = 'койка'
          INNER JOIN ActionProperty AS BED_AP ON BED_APT.id = BED_AP.type_id AND BED_AP.action_id = Action.id
          INNER JOIN ActionProperty_HospitalBed AS BED ON BED_AP.id = BED.id
          INNER JOIN OrgStructure_HospitalBed oh ON BED.value = oh.id
          INNER JOIN rbHospitalBedProfile ON oh.profile_id = rbhospitalbedprofile.id

          INNER JOIN ActionPropertyType AS OS_APT ON ActionType.id = OS_APT.actionType_id AND OS_APT.name = 'отделение пребывания'
          INNER JOIN ActionProperty AS OS_AP ON OS_APT.id = OS_AP.type_id AND Action.id = OS_AP.action_id
          INNER JOIN ActionProperty_OrgStructure AS OS ON OS_AP.id = OS.id
          INNER JOIN OrgStructure ON OS.value = OrgStructure.id
          INNER JOIN Client c ON Event.client_id = c.id
       WHERE ActionType.name = 'Движение'
          AND OrgStructure.id = %s
          AND %s
          AND rbHospitalBedProfile.row_code = %s
          AND OrgStructure.type = 8
          AND OrgStructure.hasHospitalBeds=1
          AND DATE(Event.execDate) >= DATE('%s')
          AND DATE(Event.execDate) <= DATE('%s')
          AND (%s)
          AND (LTRIM(oh.age) = '' OR LTRIM(oh.age) LIKE '18%%' OR LTRIM(oh.age) LIKE '0%%')
          AND Event.deleted = 0
          AND Action.deleted = 0
          GROUP BY Event.id
  ;

    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())
    return db.query(stmt % (org_id, bedProfile, bed_id,
                            begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
                            provedeno_dney
                            ))


class CReportF14DSSetupDialog(QtGui.QDialog, Ui_Report14DS_2000_SetupDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

        #
        # Filtering which bed profiles will appear in the listBox
        #
        db = QtGui.qApp.db
        tablerbHospitalBedProfile = db.table('rbHospitalBedProfile')
        bedProfileFilter = db.joinAnd([
            tablerbHospitalBedProfile['row_code'].isNotNull()
        ])
        self.lstFilterProfile.setTable('rbHospitalBedProfile', filter=bedProfileFilter)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        currentDate = QtCore.QDate.currentDate()
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate(currentDate.year(), currentDate.month(), 1)))
        self.edtEndDate.setDate(
            params.get('endDate', QtCore.QDate(currentDate.year(), currentDate.month(), currentDate.daysInMonth())))
        self.cmbOrgStructure.setValue((getVal(params, 'orgStructureId', None)))
        self.lstFilterProfile.setValues(params.get('profileBedId', []))


    def params(self):
        return {
                'begDate'           : self.edtBegDate.date(),
                'endDate'           : self.edtEndDate.date(),
                'orgStructureId'    : self.cmbOrgStructure.value(),
                'profileBedId'      : self.lstFilterProfile.values(),
                'ageId'             : self.cmbAge.currentIndex(),
                'RegularBedId'      : self.cmbRegularBed.currentIndex()
            }

    @QtCore.pyqtSlot()
    def on_buttonBox_accepted(self):
        self.accept()


class CReportF14DS(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"2. Использование коек дневного стационара медицинской организации по профилям")

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
        self.dumpParams(cursor, params)
        cursor.insertBlock()
        cursor.insertText("(2000)")
        cursor.insertBlock()

        tableColumns = [
            ('24%', [u'Профиль коек', u'', u'', u''], CReportBase.AlignLeft),
            ('3%', [u'№ строки', u'', u'', u''], CReportBase.AlignLeft),
            ('7%', [u'Дневные стационары медицинских организаций, оказывающих медицинскую помощь '
                    u'в стационарных условиях', u'Число коек', u'для взрослых', u'на конец года'], CReportBase.AlignLeft),
            ('6%', [u'', u'', u'', u'среднегодовых'], CReportBase.AlignLeft),
            ('6%', [u'', u'', u'для детей', u'на конец года'], CReportBase.AlignLeft),
            ('6%', [u'', u'', u'', u'среднегодовых'], CReportBase.AlignLeft),
            ('9%', [u'', u'Выписано пациентов', u'', u'взрослых'], CReportBase.AlignLeft),
            ('8%', [u'', u'', u'из них:', u'лиц старше трудоспособного возраста'], CReportBase.AlignLeft),
            ('8%', [u'', u'', u'', u'детей 0-17 лет включительно'], CReportBase.AlignLeft),
            ('9%', [u'', u'Проведено пациенто-дней', u'', u'взрослыми:'], CReportBase.AlignLeft),
            ('8%', [u'', u'', u'из них:', u'лицами старше трудоспособного возраста'], CReportBase.AlignLeft),
            ('6%', [u'', u'', u'', u'детьми 0-17 лет включительно'], CReportBase.AlignLeft)
        ]

        table = createTable(cursor, tableColumns)

        db = QtGui.qApp.db
        tblrbHospitalBedProfile = db.table('rbHospitalBedProfile')
        rbHospitalBedProfile = db.getRecordList(tblrbHospitalBedProfile, cols='*')
        profileBedId = getVal(params, 'profileBedId', None)

        #
        #  bedProfile_dict collects the bed types we have. If none bed_type is chosen, then we have to take all the
        #  bed_types in the db, else only the chosen beds
        #
        # else: we have the whole table 'rbhospitalbedprofile', and from the table we have to find the item with that
        # particular id and to put it in the list bedProfile_dict
        #
        #
        from decimal import Decimal
        bedProfile_dict = {}
        if profileBedId is None or not profileBedId:
            for i in range(0, len(rbHospitalBedProfile)):
                name = forceStringEx((rbHospitalBedProfile[i]).value('name'))
                row_code = forceStringEx((rbHospitalBedProfile[i]).value('row_code'))
                if row_code:
                    bedProfile_dict.update({name : Decimal(row_code)})
        else:
            for i in range(0, len(profileBedId)):
                rbProfileBed = db.getRecordEx(tblrbHospitalBedProfile, cols='name, row_code',
                                              where=tblrbHospitalBedProfile['id'].eq(profileBedId[i]))
                name = forceStringEx(rbProfileBed.value('name').toString())
                row_code = forceStringEx(rbProfileBed.value('row_code').toString())
                # print type(name), type(row_code)
                # Vidi dali da go pravish so Decimal(row_code), bidejki kako i da e unicode
                # ne mi teknuva dali nekade ke mi treba kako cifra, ili ke projde so Unicode,
                # ako sto brisi
                bedProfile_dict.update({name : Decimal(row_code)})

        #
        # creates as much rows as there are bed_profiles
        #
        from library.vm_collections import OrderedDict
        from operator import itemgetter
        bedProfile_dict = OrderedDict(sorted(bedProfile_dict.items(), key=itemgetter(1)))
        self.createRowsCols(table, bedProfile_dict)

        orgStructureId = getVal(params, 'orgStructureId', None)
        tblOrgstructure = db.table('OrgStructure')
        Orgstructure = db.getRecordList(tblOrgstructure, cols='id, name, parent_id')
        lst_id = []

        if orgStructureId is None:
            #
            # load everything from orgstructure, if no organisation is chosen
            #
            for rec in Orgstructure:
                lst_id.append(int(forceString(rec.value("id"))))
        else:
            #
            # list from the organisation_tree that should be included
            #
            lst_id.append(int(orgStructureId))
            for id in lst_id:
                for rec in Orgstructure:
                    if int(id) == int(forceString(rec.value("parent_id"))) and int(
                            forceString(rec.value("id"))) not in lst_id:
                        lst_id.append(int(forceString(rec.value("id"))))

        ageId = getVal(params, 'ageId', None)
        RegularBedId = getVal(params, 'RegularBedId', None)


        ii = 0

        lst_age = [
            "((YEAR(event.setDate) - YEAR(DATE(c.birthDate)) - (RIGHT(DATE(event.setDate), 5) < RIGHT(DATE(c.birthDate), 5))) >= 18)",
            "(((YEAR(event.setDate) - YEAR(DATE(c.birthDate)) - (RIGHT(DATE(event.setDate), 5) < RIGHT(DATE(c.birthDate), 5))) >= 60) AND c.sex = 1) "
            "OR (((YEAR(event.setDate) - YEAR(DATE(c.birthDate)) - (RIGHT(DATE(event.setDate), 5) < RIGHT(DATE(c.birthDate), 5))) >= 55) AND c.sex = 2)",
            "((YEAR(event.setDate) - YEAR(DATE(c.birthDate)) - (RIGHT(DATE(event.setDate), 5) < RIGHT(DATE(c.birthDate), 5))) < 18)"
            "AND ((YEAR(event.setDate) - YEAR(DATE(c.birthDate)) - (RIGHT(DATE(event.setDate), 5) < RIGHT(DATE(c.birthDate), 5))) >=0)"]

        lst_bedProfile = [
            "(oh.isPermanent = 1 OR oh.isPermanent = 0)", "oh.isPermanent = 1", "oh.isPermanent = 0"
        ]

        bedProfile = lst_bedProfile[0]
        if RegularBedId == 0:
            bedProfile = lst_bedProfile[0]
        elif RegularBedId == 1:
            bedProfile = lst_bedProfile[1]
        else:
            bedProfile = lst_bedProfile[2]

        sumBeds_col3 = 0
        sumBeds_col5 = 0
        sumPac_col7 = 0
        sumPac_col8 = 0
        sumPac_col9 = 0
        sumDays_col10 = 0
        sumDays_col11 = 0
        sumDays_col12 = 0

        #
        # We are looping through beds with row_code given, checking in each orgstructure if they have that bed
        # summing the values for each bed
        #
        for bed_id in range(0, len(bedProfile_dict)):
            sum_koek_vzrolsye = 0
            sum_koek_detey = 0
            sum_col7 = 0
            sum_col8 = 0
            sum_col9 = 0
            sum_col10 = 0
            sum_col11 = 0
            sum_col12 = 0

            for org_id in range(0, len(lst_id)):
                #
                # summing the columns for each organisation
                #
                query = selectData(params, lst_id[org_id], bedProfile, (bedProfile_dict.values()[bed_id]))
                self.setQueryText(forceString(query.lastQuery()))  # this does nothing?
                #
                # list of age range that is appending each time to the query
                # This is done in order to make the query smaller and simpler (changing the age range by looping in for cycle)
                #
                for j in range (0, len(lst_age)):
                    queryPacDays = selectData_PacientDays(params, lst_age[j], bedProfile, lst_id[org_id],
                                                          (bedProfile_dict.values()[bed_id]))
                    self.setQueryText(forceString(queryPacDays.lastQuery()))  # this does nothing?
                    #
                    # input: query that outputs the events (setDate, execDate and eventId). We calculate the days spend
                    # in SDP for a pacient belonging in particular age range (lst_age)
                    #
                    while queryPacDays.next():
                        recordPacDays = queryPacDays.record()
                        days = getEventLengthDays(
                            forceDate(recordPacDays.value('e_set')),
                            forceDate(recordPacDays.value('e_exec')),
                            countRedDays=False,
                            eventTypeId=forceString(recordPacDays.value('et_id')),
                            isDayStationary= True)

                        #
                        # Depending on the index in lst_age we sum the days for a pacient in a particular age range
                        #
                        if j == 0:
                            sum_col10 = sum_col10 + int(days)
                            sumDays_col10 = sumDays_col10 + int(days)
                        elif j == 1:
                            sum_col11 = sum_col11 + int(days)
                            sumDays_col11 = sumDays_col11 + int(days)
                        else:
                            sum_col12 = sum_col12 + int(days)
                            sumDays_col12 = sumDays_col12 + int(days)

                while query.next():
                    record = query.record()
                    try:
                        sum_koek_vzrolsye = sum_koek_vzrolsye + int(forceString(record.value('koek_vzroslye')))
                    except ValueError:
                        pass
                    try:
                        sum_koek_detey = sum_koek_detey + int(forceString(record.value('koek_detey')))
                    except ValueError:
                        pass
                    try:
                        sum_col7 = sum_col7 + int(forceString(record.value('col_7')))
                    except ValueError:
                        pass
                    try:
                        sum_col8 = sum_col8 + int(forceString(record.value('col_8')))
                    except ValueError:
                        pass
                    try:
                        sum_col9 = sum_col9 + int(forceString(record.value('col_9')))
                    except ValueError:
                        pass


            #
            # Depending on the choice in the combobox we have to choose the which columns are going to be filled
            #
            if ageId == 0:
                table.setText(ii + 6, 2, sum_koek_vzrolsye)
                table.setText(ii + 6, 4, sum_koek_detey)
                sumBeds_col3 = sumBeds_col3 + sum_koek_vzrolsye
                sumBeds_col5 = sumBeds_col5 + sum_koek_detey

                table.setText(ii + 6, 6, sum_col7)
                table.setText(ii + 6, 7, sum_col8)
                table.setText(ii + 6, 8, sum_col9)
                sumPac_col7 = sumPac_col7 + sum_col7
                sumPac_col8 = sumPac_col8 + sum_col8
                sumPac_col9 = sumPac_col9 + sum_col9

                table.setText(ii + 6, 9, sum_col10)
                table.setText(ii + 6, 10, sum_col11)
                table.setText(ii + 6, 11, sum_col12)
            elif ageId == 1:  # detey
                table.setText(ii + 6, 4, sum_koek_detey)
                sumBeds_col5 = sumBeds_col5 + sum_koek_detey

                table.setText(ii + 6, 8, sum_col9)
                sumPac_col9 = sumPac_col9 + sum_col9

                table.setText(ii + 6, 11, sum_col12)
            elif ageId == 2:  # vzroslye
                table.setText(ii + 6, 2, sum_koek_vzrolsye)
                sumBeds_col3 = sumBeds_col3 + sum_koek_vzrolsye

                table.setText(ii + 6, 6, sum_col7)
                table.setText(ii + 6, 7, sum_col8)
                sumPac_col7 = sumPac_col7 + sum_col7
                sumPac_col8 = sumPac_col8 + sum_col8

                table.setText(ii + 6, 9, sum_col10)
                table.setText(ii + 6, 10, sum_col11)

            ii = ii + 1
        if ageId == 0:
            table.setText(5, 2, sumBeds_col3)
            table.setText(5, 4, sumBeds_col5)
            table.setText(5, 6, sumPac_col7)
            table.setText(5, 7, sumPac_col8)
            table.setText(5, 8, sumPac_col9)
            table.setText(5, 9, sumDays_col10)
            table.setText(5, 10, sumDays_col11)
            table.setText(5, 11, sumDays_col12)
        elif ageId == 1:
            table.setText(5, 4, sumBeds_col5)
            table.setText(5, 8, sumPac_col9)
            table.setText(5, 11, sumDays_col12)
        else:
            table.setText(5, 2, sumBeds_col3)
            table.setText(5, 6, sumPac_col7)
            table.setText(5, 7, sumPac_col8)
            table.setText(5, 9, sumDays_col10)
            table.setText(5, 10, sumDays_col11)

        self.merge_cells(table)
        return doc


    def createRowsCols(self, table, bedProfile_dict):
        #
        # fifth row
        #
        lst_ffth_row = [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'10', u'11', u'12']
        lst_count = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

        i = table.addRow()
        for j in range(0, 12):
            table.setText(i, lst_count[j], lst_ffth_row[j])

        i = table.addRow()
        table.setText(i, 0, "Всего")
        table.setText(i, 1, "1")
        for j in range(0, len(bedProfile_dict.keys())):
            i = table.addRow()
            table.setText(i, 0, bedProfile_dict.keys()[j])
            table.setText(i, 1, bedProfile_dict.values()[j])

    def merge_cells(self, table):
        table.mergeCells(0, 0, 4, 1)  # first column, 0,1,2,3 rows
        table.mergeCells(1, 0, 4, 1)
        table.mergeCells(2, 0, 4, 1)
        table.mergeCells(3, 0, 4, 1)

        table.mergeCells(0, 1, 4, 1)  # second column, 0,1,2,3 rows
        table.mergeCells(1, 1, 4, 1)
        table.mergeCells(2, 1, 4, 1)
        table.mergeCells(3, 1, 4, 1)

        table.mergeCells(0, 2, 1, 10)  # first row, 3-12 columns
        table.mergeCells(0, 3, 1, 10)
        table.mergeCells(0, 4, 1, 10)
        table.mergeCells(0, 5, 1, 10)
        table.mergeCells(0, 6, 1, 10)
        table.mergeCells(0, 7, 1, 10)
        table.mergeCells(0, 8, 1, 10)
        table.mergeCells(0, 9, 1, 10)
        table.mergeCells(0, 10, 1, 10)
        table.mergeCells(0, 11, 1, 10)

        table.mergeCells(1, 2, 1, 4)  # second row, 3-6 cols
        table.mergeCells(1, 3, 1, 4)
        table.mergeCells(1, 4, 1, 4)
        table.mergeCells(1, 5, 1, 4)

        table.mergeCells(1, 6, 1, 3)  # second row, 7-9 cols
        table.mergeCells(1, 7, 1, 3)
        table.mergeCells(1, 8, 1, 3)

        table.mergeCells(1, 9, 1, 3)  # second row, 10-12 cols
        table.mergeCells(1, 10, 1, 3)
        table.mergeCells(1, 11, 1, 3)

        table.mergeCells(2, 2, 1, 2)  # third row, 3,4 columns
        table.mergeCells(2, 3, 1, 2)

        table.mergeCells(2, 4, 1, 2)  # third row, 5,6 columns
        table.mergeCells(2, 5, 1, 2)

        table.mergeCells(1, 4, 1, 2)  # third row, 10-12 cols
        table.mergeCells(1, 5, 1, 2)

        table.mergeCells(1, 2, 1, 2)  # third row, 10-12 cols
        table.mergeCells(1, 3, 1, 2)

        table.mergeCells(1, 4, 1, 2)  # third row, 10-12 cols
        table.mergeCells(1, 5, 1, 2)

        table.mergeCells(2, 6, 2, 1)  # 7th column, 0,1,2 rows
        table.mergeCells(3, 6, 2, 1)
        table.mergeCells(2, 8, 2, 1)  # 9th column, 0,1,2 rows
        table.mergeCells(3, 8, 2, 1)
        table.mergeCells(2, 9, 2, 1)  # 10th column, 0,1,2 rows
        table.mergeCells(3, 9, 2, 1)
        table.mergeCells(2, 11, 2, 1)  # 12th column, 0,1,2 rows
        table.mergeCells(3, 11, 2, 1)


def main():
    import sys
    from library.database import connectDataBaseByInfo
    from s11main import CS11mainApp
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 229525#  230493 # 229525 # 230226 #229525 #229005

    connectionInfo = {'driverName' : 'mysql',
                      'host' : 'pacs',
                      'port' : 3306,
                      'database' : 'novros',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    """

    connectionInfo = {'driverName': 'mysql',
                      'host': 'pes',
                      'port': 3306,
                      'database': 's12',
                      'user': 'dbuser',
                      'password': 'dbpassword',
                      'connectionName': 'vista-med',
                      'compressData': True,
                      'afterConnectFunc': None}

    """
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)
    CReportF14DS(None).exec_()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

