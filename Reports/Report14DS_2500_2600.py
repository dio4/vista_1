# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from Reports.Report import CReport
from Reports.ReportBase import CReportBase
from library.Utils import forceString, getVal
from Ui_Report14DS_2500_2600 import Ui_Report14DS_2500_2600_SetupDialog


def selectData_Report2500(params, org_id, bedProfile):
    stmt = u'''
    SELECT (
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

          WHERE ap_os.value = %s
                AND %s  # shtatnaja kojka
                AND o.hasHospitalBeds=1 # imeet kojki shtiklirano e
                AND o.type=8 #SDP
                AND DATE(e.execDate) >= DATE('%s')
                AND DATE(e.execDate) <= DATE('%s')
                AND r.isDeath=1
                #AND act.name LIKE 'Движение'
                #AND aps.value = 'умер'
                AND e.deleted = 0
                AND a.deleted = 0
                GROUP BY e.id
        ) AS pacients ) AS col1,
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
          INNER JOIN ActionProperty_String aps ON ap.id = aps.id
          INNER JOIN rbResult r ON e.result_id = r.id

        WHERE #apt.name = 'Отделение пребывания'
             ap_os.value = %s
            AND %s  # shtatnaja kojka
            AND o.hasHospitalBeds=1
            AND o.type=8 # SDP
            AND DATE(e.execDate) >= DATE('%s')
            AND DATE(e.execDate) <= DATE('%s')
            AND (YEAR(e.setDate) - YEAR(DATE(c.birthDate)) - (RIGHT(DATE(e.setDate), 5)
                    < RIGHT(DATE(c.birthDate), 5))) < 18
            AND r.isDeath=1
           # AND act.name LIKE 'Движение'
            #AND aps.value = 'умер'
            AND e.deleted = 0
            AND a.deleted = 0
            GROUP BY e.id
    ) AS pacients
      ) AS col2,
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
          INNER JOIN ActionProperty_String aps ON ap.id = aps.id
          INNER JOIN rbResult r ON e.result_id = r.id
        WHERE# apt.name = 'Отделение пребывания'
        #    AND
        ap_os.value = %s
            AND %s  # shtatnaja kojka
            AND o.hasHospitalBeds=1
            AND o.type=7 # DS
            AND DATE(e.execDate) >= DATE('%s')
            AND DATE(e.execDate) <= DATE('%s')
            #AND act.name LIKE 'Движение'
           # AND aps.value = 'умер'
            AND r.isDeath=1
            AND e.deleted = 0
            AND a.deleted = 0
            GROUP BY e.id
    ) AS pacients
      ) AS col3,
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
        WHERE #apt.name = 'Отделение пребывания'
           # AND
           ap_os.value = %s
            AND %s  # shtatnaja kojka
            AND o.hasHospitalBeds=1
            AND o.type=7 # DS
            AND DATE(e.execDate) >= DATE('%s')
            AND DATE(e.execDate) <= DATE('%s')
            AND (YEAR(e.setDate) - YEAR(DATE(c.birthDate)) - (RIGHT(DATE(e.setDate), 5)
                    < RIGHT(DATE(c.birthDate), 5))) < 18
            #AND act.name LIKE 'Движение'
            #AND aps.value = 'умер'
            AND r.isDeath=1
            AND e.deleted = 0
            AND a.deleted = 0
            GROUP BY e.id
    ) AS pacients
      ) AS col4;
        '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (
        org_id, bedProfile,
        begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
        org_id, bedProfile,
        begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
        org_id, bedProfile,
        begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd'),
        org_id, bedProfile,
        begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')
    ))


def selectData_Report2600(params, org_id, bedProfile):
    stmt = u'''
SELECT COUNT(a.id) AS sum_all, a.o_type AS o_type FROM (
SELECT c.id AS id, o.type AS o_type
  FROM (
       SELECT ap_os.value AS ap_os_value, e.id AS e_id#, et.id AS et_id
            FROM Action a
            INNER JOIN ActionProperty ap ON a.id = ap.action_id
            INNER JOIN ActionPropertyType apt ON ap.type_id = apt.id
            INNER JOIN ActionType act ON a.actionType_id = act.id
            LEFT JOIN ActionProperty_OrgStructure ap_os ON ap.id = ap_os.id
            INNER JOIN Event e ON a.event_id = e.id
            WHERE apt.name = 'Отделение пребывания'
              AND ap_os.value = %s
              AND act.name='Движение'
              AND e.deleted = 0
              AND a.deleted = 0
    ) actions

        INNER JOIN Event e ON actions.e_id = e.id
      INNER JOIN EventType et ON e.eventType_id = et.id
      INNER JOIN Client c ON e.client_id = c.id
      INNER JOIN OrgStructure o ON actions.ap_os_value = o.id
      INNER JOIN OrgStructure_HospitalBed oh ON o.id = oh.master_id
      INNER JOIN rbHospitalBedProfile r ON oh.profile_id = r.id


  INNER JOIN ClientAddress AS ClientRegAddress ON ClientRegAddress.id = getClientRegAddressId(c.id)
                LEFT JOIN Address AS RegAddress ON RegAddress.`id` = ClientRegAddress.`address_id`
                LEFT JOIN AddressHouse AS RegAddressHouse ON RegAddressHouse.`id` = RegAddress.`house_id`
                INNER JOIN ClientAddress AS ClientLocAddress ON ClientLocAddress.id = getClientLocAddressId(c.id)
                LEFT JOIN Address AS LocAddress ON LocAddress.`id` = ClientLocAddress.`address_id`
                LEFT JOIN AddressHouse AS LocAddressHouse ON LocAddressHouse.`id` = LocAddress.`house_id`
                LEFT JOIN kladr.KLADR AS LocKLADR ON LocKLADR.`CODE` = LocAddressHouse.`KLADRCode`
                LEFT JOIN kladr.KLADR AS RegKLADR ON RegKLADR.`CODE` = RegAddressHouse.`KLADRCode`
                LEFT JOIN kladr.SOCRBASE AS RegSOCR ON RegSOCR.`KOD_T_ST` = (SELECT KOD_T_ST FROM kladr.SOCRBASE
                WHERE kladr.SOCRBASE.`SCNAME` = RegKLADR.`SOCR`    LIMIT 0, 1)
                LEFT JOIN kladr.SOCRBASE AS LocSOCR ON LocSOCR.`KOD_T_ST` = (SELECT KOD_T_ST FROM kladr.SOCRBASE
                WHERE kladr.SOCRBASE.`SCNAME` = LocKLADR.`SOCR`    LIMIT 0, 1)

                WHERE %s # Infekcionaya bolnica dlja vzroslyh
                AND o.hasHospitalBeds=1 # imeet kojki shtiklirano e


                AND (o.type=8 OR o.type=7) # SDP
                AND DATE(e.execDate) >= DATE('%s')
                AND DATE(e.execDate) <= DATE('%s')



  AND ((ClientRegAddress.`isVillager` = 1) OR (RegSOCR.`KOD_T_ST` IN ('302','303','304','305','310','314',
                '316','317','401','402','403','404','406','407','416','417','419','421','423','424','425','429',
                '430','431','433','434','435','443','448','449')) OR (ClientLocAddress.`isVillager` = 1)
                OR (LocSOCR.`KOD_T_ST` IN ('302','303','304','305','310','314','316','317','401','402','403',
                '404','406','407','416','417','419','421','423','424','425','429','430','431','433','434','435','443','448','449')))

                GROUP BY c.id, o.type
                ORDER BY c.id
) a
  GROUP BY a.o_type;
    '''

    db = QtGui.qApp.db
    begDate = params.get('begDate', QtCore.QDate())
    endDate = params.get('endDate', QtCore.QDate())

    return db.query(stmt % (
        org_id, bedProfile,
        begDate.toString('yyyy-MM-dd'), endDate.toString('yyyy-MM-dd')
    ))


class CReportF14DSSetupDialog(QtGui.QDialog, Ui_Report14DS_2500_2600_SetupDialog):
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
            'begDate': self.edtBegDate.date(),
            'endDate': self.edtEndDate.date(),
            'orgStructureId': self.cmbOrgStructure.value(),
            'RegularBedId': self.cmbRegularBed.currentIndex()
        }

    @QtCore.pyqtSlot()
    def on_buttonBox_accepted(self):
        QtGui.qApp.callWithWaitCursor(self, self.setParams)
        self.accept()


class CReportF14DS(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u"(2500) / (2600)")

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
        cursor.insertText(" (2500 / 2600)")
        cursor.insertBlock()

        db = QtGui.qApp.db
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

        RegularBedId = getVal(params, 'RegularBedId', None)

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

        sumAll_sdp = 0
        sumChild_sdp = 0
        sumAll_ds = 0
        sumChild_ds = 0

        num_SDPvilligers = 0
        num_DSvillagers = 0

        for org_id in range(0, len(lst_id)):
            query = selectData_Report2500(params, lst_id[org_id], bedProfile)
            self.setQueryText(forceString(query.lastQuery()))

            while query.next():
                record = query.record()
                sumAll_sdp += int(forceString(record.value('col1')))
                sumChild_sdp += int(forceString(record.value('col2')))
                sumAll_ds += int(forceString(record.value('col3')))
                sumChild_ds += int(forceString(record.value('col4')))

            query_2600 = selectData_Report2600(params, lst_id[org_id], bedProfile)
            self.setQueryText(forceString(query_2600.lastQuery()))
            query_2600.next()
            record = query_2600.record()

            if forceString(record.value('o_type')) == str(8):
                num_SDPvilligers = num_SDPvilligers + int(forceString(record.value('sum_all')))
                #
                # if o.type is first since it is Ordered by o.type
                # and if query.next() than o.type = 8 exists
                #
                if query_2600.next() and forceString(record.value('o_type')) == str(7):
                    num_DSvillagers = num_DSvillagers + int(forceString(record.value('sum_all')))
            elif forceString(record.value('o_type')) == str(7):
                num_DSvillagers = num_DSvillagers + int(forceString(record.value('sum_all')))

        cursor.insertBlock()
        txt = u'(2500)\n Умерло в дневном стационаре при  подразделениях медицинских организаций, оказывающих медицинскую помощь: в стационарных условиях  1 __'
        txt += forceString(sumAll_sdp)
        txt += u'__, из них: детей  2 __'
        txt += forceString(sumChild_sdp)
        txt += u'__, в амбулаторных условиях  3 __'
        txt += forceString(sumAll_ds)
        txt += u'__, из них: детей  4 __'
        txt += forceString(sumChild_ds)
        txt += u'__ на дому 5 __/__ , из них: детей  6 __/__. '
        cursor.insertText(txt)

        cursor.insertBlock()
        cursor.insertBlock()
        cursor.insertBlock()
        txt_2600 = u'(2600)\n  Число выписанных сельских жителей из дневных стационаров медицинских организаций, оказывающих медицинскую  помощь:  в стационарных условиях  1 __'
        txt_2600 += forceString(num_SDPvilligers)
        txt_2600 += u'__, в амбулаторных условиях  2 __'
        txt_2600 += forceString(num_DSvillagers)
        txt_2600 += u'__, на дому  3 __/__.'
        cursor.insertText(txt_2600)

        return doc


def main():
    import sys
    from library.database import connectDataBaseByInfo
    from s11main import CS11mainApp
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda:  230226 #229525  # 229005

    connectionInfo = {'driverName' : 'mysql',
                      'host' : 'pacs',
                      'port' : 3306,
                      'database' : 's11vm',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}


    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)
    CReportF14DS(None).exec_()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

