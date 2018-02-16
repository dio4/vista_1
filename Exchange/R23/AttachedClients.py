# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################
import zipfile

from Orgs.Utils import CAttachType, COrgStructureAreaInfo, getOrgStructureDescendants, getOrganisationInfo, \
    getOrganisationMainStaff
from Ui_AttachedClients import Ui_AttachedClientsDialog
from library.Utils import calcAgeInMonths, calcAgeInYears, forceDate, forceDouble, forceInt, forceRef, forceString, \
    forceStringEx, getVal, get_date, toVariant
from library.dbfpy import dbf
from s11main import CS11mainApp

__author__ = 'craz'

'''
    author: craz
    date:   01.06.2015
'''

import os

from PyQt4 import QtCore, QtGui, QtSql


lgotaCodeList = ['010', '011', '012', '020', '030', '040', '050', '060', '061', '062', '064', '064', '081', '082', '083', \
                 '084', '085', '091', '092', '093', '094', '095', '096', '097', '098', '099', '100', '101', '102', '111', \
                 '112', '113', '120', '121', '122', '123', '124', '125', '128', '129', '131', '132', '140', '141', '142', \
                 '150', '201', '203', '205', '207', '209', '210', '211', '281', '282', '284', '301', '302', '303', '304', \
                 '305', '306', '307', '308', '309', '310', '311', '312', '313', '314', '315', '316', '317', '318', '319', \
                 '320', '321', '322', '323', '324', '325', '326', '327', '328', '329', '330', '331', '332', '501', '502', \
                 '503', '504', '505', '506', '507', '701', '801', '901', '902']

class CAttachedClientsDialog(QtGui.QDialog, Ui_AttachedClientsDialog):
    """Обмен прикрепленным населением по формату МИАЦ Краснодарского Края"""

    def __init__(self, parent=None):
        super(CAttachedClientsDialog, self).__init__(parent)
        self.setupUi(self)
        self.postSetupUi()
        self.queryModel = QtSql.QSqlQueryModel()
        self.proxyModel = QtGui.QSortFilterProxyModel()


    # noinspection PyAttributeOutsideInit
    def postSetupUi(self):
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMaximizeButtonHint)
        self.btnRetrieve.clicked.connect(self.on_btnRetrieveClicked)
        self.btnSave.clicked.connect(self.onSaveClicked)
        self.btnClose.clicked.connect(self.onCloseClicked)
        self.cmbOrgStructure.model().setFilter('IFNULL(bookKeeperCode, \'\') != \'\'')
        self.smoDict = self.getSMOList()
        self.cmbSMO.clear()
        for item in self.smoDict.values():
            self.cmbSMO.addItem(u'%s - %s'%(item[0], item[1]), toVariant(item[1]))

    def getSMOList(self):
        db = QtGui.qApp.db
        stmt = u'''Select
                Distinct IFNULL(
                IF(Insurer.area = '2300000000000',
					IF(
						Insurer.head_id IS NULL,
						IF(
							TRIM(Insurer.infisCode),
							Insurer.infisCode,
                            ''
						),
						(
                            IF(
                                TRIM(head.infisCode),
                                head.infisCode,
                                ''
                            )
						)
					),
                    NULL
				),
					'9007'
				) AS SMO
            From ClientPolicy
                inner join Organisation Insurer
                    on Insurer.id = ClientPolicy.insurer_id
                left join Organisation head
                    on head.id = Insurer.head_id
            Where IF (head.id, head.isInsurer = 1, Insurer.isInsurer = 1)'''
        query = db.query(stmt)
        smoList = []
        table = db.table('Organisation')
        while query.next():
            item = query.record()
            SMO = forceString(item.value('SMO'))
            if SMO:
                orgName = db.getRecordEx(table, table['shortName'], [table['infisCode'].eq(SMO), table['area'].eq('2300000000000')])
                smoList.append((SMO, forceString(orgName.value('shortName')) if orgName else u'не найдено'))
        smoList.sort(key=lambda x: x[0])

        smoDict = {}
        smoDict[0] = (u'', u'все')
        smoDict[1] = (u'NULL', u'не указано')
        for index, smoItem in enumerate(smoList):
            smoDict[index + 2] = smoItem
        return smoDict

    def setQuery(self, query):
        query.setForwardOnly(False)
        self.queryModel.setQuery(query)
        self.proxyModel.setSourceModel(self.queryModel)
        self.tblResult.setModel(self.proxyModel)
        self.query = query

    def createQuery(self):
        db = QtGui.qApp.db
        orgStructureId = self.cmbOrgStructure.value()
        date = self.edtReportDate.date()
        SMO = self.rbSMO.isChecked()
        rbRegAndLoc = self.rbRegAndLoc.isChecked()
        rbRegOnly = self.rbOnlyReg.isChecked()
        rbLocOnly = self.rbOnlyLoc.isChecked()
        correct = None
        smoCode = None
        if SMO:
            smoCode = self.smoDict[self.cmbSMO.currentIndex()][0]
            correct = self.chkCorrectRecords.isChecked()
        extClients = self.chkExternalArea.isChecked()
        tableClient = db.table('Client')
        tableClientAttach = db.table('ClientAttach')
        tableClientPolicy = db.table('ClientPolicy')
        tablePolicyKind = db.table('rbPolicyKind')
        tableInsurer = db.table('Organisation').alias('Insurer')
        tableClientDocument = db.table('ClientDocument')
        tableDocumentType = db.table('rbDocumentType')
        tableClientAddress = db.table('ClientAddress')
        tableClientAddressReg = db.table('ClientAddress').alias('ClientAddressReg')
        tableClientAddressLoc = db.table('ClientAddress').alias('ClientAddressLoc')
        tableAddress = db.table('Address')
        tableAddressReg = db.table('Address').alias('AddressReg')
        tableAddressLoc = db.table('Address').alias('AddressLoc')
        tableAddressHouse = db.table('AddressHouse')
        tableAddressHouseReg = db.table('AddressHouse').alias('AddressHouseReg')
        tableAddressHouseLoc = db.table('AddressHouse').alias('AddressHouseLoc')
        tableKLADR = db.table('kladr.KLADR')
        tableKLADRReg = db.table('kladr.KLADR').alias('kladrReg')
        tableKLADRLoc = db.table('kladr.KLADR').alias('kladrLoc')
        tableSocr = db.table('kladr.SOCRBASE').alias('Socr')
        tableStreet = db.table('kladr.STREET')
        tableStreetReg = db.table('kladr.STREET').alias('streetReg')
        tableStreetLoc = db.table('kladr.STREET').alias('streetLoc')
        tableStreetSocr = db.table('kladr.SOCRBASE').alias('StreetSocr')
        tableOrgStructure = db.table('OrgStructure')
        tableOrgStructureHasBookkeeperCode = db.table('OrgStructure').alias('OrgStructureHasBookkeeperCode')
        tableAttachType = db.table('rbAttachType')
        tableClientList = db.table('ClientList')
        tableSMOList = db.table('SMOList')
        tableCodeMOList = db.table('CodeMOList')
        tableMiacControlList = db.table('client_MIACControlKrasnodar')

        queryTable = tableClientList.innerJoin(tableClientAttach, tableClientAttach['id'].eq(tableClientList['attach_id']))
        if correct:
            queryTable = queryTable.innerJoin(tableMiacControlList, tableMiacControlList['client_id'].eq(tableClientAttach['client_id']))
        queryTable = queryTable.innerJoin(tableClient, tableClient['id'].eq(tableClientAttach['client_id']))
        queryTable = queryTable.innerJoin(tableAttachType, tableAttachType['id'].eq(tableClientAttach['attachType_id']))
        queryTable = queryTable.leftJoin(tableClientPolicy, 'ClientPolicy.id = getClientPolicyId(Client.id, 1)')
        queryTable = queryTable.leftJoin(tableInsurer, tableInsurer['id'].eq(tableClientPolicy['insurer_id']))
        queryTable = queryTable.leftJoin(tableSMOList, tableSMOList['id'].eq(tableInsurer['id']))
        queryTable = queryTable.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableClientAttach['orgStructure_id']))
        queryTable = queryTable.leftJoin(tableCodeMOList, tableCodeMOList['orgStructure_id'].eq(tableOrgStructure['id']))
        #queryTable = queryTable.leftJoin(tableOrgStructureHasBookkeeperCode, u'%s = getOrgStructureIdHasBookkeeperCode(%s)' % (tableOrgStructureHasBookkeeperCode['id'], tableOrgStructure['id']))
        queryTable = queryTable.leftJoin(tableClientDocument, 'ClientDocument.id = getClientDocumentId(Client.id)')

        if not rbRegAndLoc:
            if rbRegOnly:
                queryTable = queryTable.leftJoin(tableClientAddress, """
                ClientAddress.id = (
				    Select ca.`id`
				    From ClientAddress as ca
				    where Client.`id` = ca.`client_id`
					    and ca.`type` = 0
					    and ca.deleted = 0
				    Order by If (ClientAttach.`endDate` is not Null, ca.`createDatetime` < ClientAttach.`endDate`, 1) desc, ca.`createDatetime` desc
				    Limit 1
				    )""")
            elif rbLocOnly:
                queryTable = queryTable.leftJoin(tableClientAddress, """
                ClientAddress.id = (
				    Select ca.`id`
				    From ClientAddress as ca
				    where Client.`id` = ca.`client_id`
					    and ca.`type` = 1
					    and ca.deleted = 0
				    Order by If (ClientAttach.`endDate` is not Null, ca.`createDatetime` < ClientAttach.`endDate`, 1) desc, ca.`createDatetime` desc
				    Limit 1
				    )""")
        else:
            queryTable = queryTable.leftJoin(tableClientAddress, """
                ClientAddress.id = (
				    Select ca.`id`
				    From ClientAddress as ca
				    where Client.`id` = ca.`client_id`
					    and ca.`type` = IF (%s = 1, '0', IF(%s = 2, '1', ''))
					    and ca.deleted = 0
				    Order by If (ClientAttach.`endDate` is not Null, ca.`createDatetime` < ClientAttach.`endDate`, 1) desc, ca.`createDatetime` desc
				    Limit 1
				    )""" %(tableAttachType['code'], tableAttachType['code']))
        queryTable = queryTable.leftJoin(tableAddress, tableAddress['id'].eq(tableClientAddress['address_id']))
        queryTable = queryTable.leftJoin(tableAddressHouse, tableAddressHouse['id'].eq(tableAddress['house_id']))
        queryTable = queryTable.leftJoin(tableKLADR, tableKLADR['CODE'].eq(tableAddressHouse['KLADRCode']))
        queryTable = queryTable.leftJoin(tableStreet, tableStreet['CODE'].eq(tableAddressHouse['KLADRStreetCode']))

        queryTable = queryTable.leftJoin(tableDocumentType,
                                         tableDocumentType['id'].eq(tableClientDocument['documentType_id']))
        queryTable = queryTable.leftJoin(tablePolicyKind, tablePolicyKind['id'].eq(tableClientPolicy['policyKind_id']))

        cond = [tableClientAttach['begDate'].dateLe(date),
                tableAttachType['outcome'].eq(0),
                db.joinOr([tableClientAttach['endDate'].isNull(),
                                tableClientAttach['endDate'].dateGe(date),
                                db.joinAnd([tableOrgStructure['isArea'].inlist([COrgStructureAreaInfo.Pediatric, COrgStructureAreaInfo.Therapeutic]),
                                                 tableClientAttach['endDate'].dateLt(date)])
                                ]),
                tableClientAttach['deleted'].eq(0),
                tableOrgStructure['isArea'].inlist([COrgStructureAreaInfo.Pediatric, COrgStructureAreaInfo.Therapeutic, COrgStructureAreaInfo.GeneralPractice]),
                tableAttachType['code'].inlist([CAttachType.Territorial, CAttachType.Attached])]
        if orgStructureId:
            cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
        if smoCode:
            if smoCode == u'NULL':
                cond.append(db.joinOr([tableSMOList['code'].isNull(), tableSMOList['code'].eq('')]))
            else:
                cond.append(tableSMOList['code'].eq(smoCode))
        cols = [
            tableClient['id'].alias('ID'),
            u'''(Select ciRis.identifier
                    From ClientIdentification ciRis
                    Left JOIN rbAccountingSystem as ris
                        on ris.id = ciRis.accountingSystem_id
                    Where ciRis.client_id = Client.id
                        and ris.code = 'РИС'
                        and ciRis.deleted = 0
                    Order by ciRis.createDatetime desc
                    Limit 1) AS `IDSTR`''',
            tableSMOList['code'].alias('SMO'),
            u'''
            (CASE rbPolicyKind.code
                WHEN '1' THEN 'С'
                WHEN '2' THEN 'В'
                WHEN '3' THEN 'П'
                WHEN '4' THEN 'Э'
                WHEN '5' THEN 'Э'
            END) AS DPFS''',
            tableClientPolicy['serial'].alias('DPFS_S'),
            tableClientPolicy['number'].alias('DPFS_N'),
            tableClient['lastName'].alias('FAM'),
            tableClient['firstName'].alias('IM'),
            tableClient['patrName'].alias('OT'),
            u'''
            (CASE Client.sex
                WHEN '0' THEN ''
                WHEN '1' THEN 'М'
                WHEN '2' THEN 'Ж'
            END) AS `SEX`''',
            tableClient['SNILS'].alias('SNILS'),
            tableClient['birthDate'].alias('DATR'),
            tableDocumentType['regionalCode'].alias('DOC'),
            tableClientDocument['serial'].alias('DOC_S'),
            tableClientDocument['number'].alias('DOC_N'),
            # TODO: craz: Очень странная логика для CODE_MO + функция getOrgStructureInfisCode есть только в самсоновских базах, т.к. она не наша и для всех мы ее не поставляем.
            tableCodeMOList['CODE_MO'],
            #tableOrgStructureHasBookkeeperCode['infisDepTypeCode'].alias('OID_MO'),
            "'' as `OID_MO`",
            tableAttachType['code'].alias('PRIK'),
            tableClientAttach['begDate'].alias('PRIK_D'),
            'IF(ClientAttach.endDate < \'%s\', ClientAttach.endDate, NULL) AS `OTKR_D`' % \
                                                    self.edtReportDate.date().toString(QtCore.Qt.ISODate),
            tableOrgStructure['id'].alias('orgStructureId'),
            tableOrgStructure['infisInternalCode'].alias('UCH'),
            u"""(Select ciEnp.identifier
                    From ClientIdentification ciEnp
                    Left JOIN rbAccountingSystem as enp
                        on enp.id = ciEnp.accountingSystem_id
                    Where ciEnp.client_id = Client.id
                        and enp.code = 'ЕНП'
                        and ciEnp.deleted = 0
                    Order by ciEnp.createDatetime desc
                    Limit 1) AS `F_ENP`""",
            u"""(Select kk.Name
		        From kladr.KLADR as kk
		        where kk.code = (Concat(LEFT(%s, 5), '00000000'))) AS `R_NAME`""" %(tableAddressHouse['KLADRCode']),
            u"""IF(%s = 'г', %s, '') AS C_NAME""" % (tableKLADR['SOCR'], tableKLADR['NAME']),
            u"""IF(%s = 'г', '', %s) AS NP_NAME""" % (tableKLADR['SOCR'], tableKLADR['NAME']),
            tableStreet['NAME'].alias('UL_NAME'),
            tableAddressHouse['number'].alias('DOM'),
            tableAddressHouse['corpus'].alias('KOR'),
            tableAddress['flat'].alias('KV'),
        ]
        if self.rbSMO.isChecked() and self.chkCorrectRecords.isChecked():
            cols.append(u"'001' as MIACRES")
        if correct:
            cols += [
                tableMiacControlList['F_SMO'],
                tableMiacControlList['F_DPFS'],
                tableMiacControlList['F_DPFS_S'],
                tableMiacControlList['F_DPFS_N'],
                tableMiacControlList['F_FAM'],
                tableMiacControlList['F_IM'],
                tableMiacControlList['F_OT'],
                tableMiacControlList['F_SEX'],
                tableMiacControlList['F_DATR'],
                tableMiacControlList['F_SNILS'],
                tableMiacControlList['F_DOC'],
                tableMiacControlList['F_DOC_S'],
                tableMiacControlList['F_DOC_N'],
            ]
        stmt = db.selectStmt(queryTable, cols, cond)
        if not extClients:
            stmt = u'''%s Order by FAM, IM, OT, DATR;''' %(stmt)
        else:
            stmt = u'''%s Order by FAM, IM, OT, DATR;''' %(self.getExtStmt())
        return db.query(stmt)

    def getExtStmt(self):
        db = QtGui.qApp.db

        orgStructureId = self.cmbOrgStructure.value()
        date = self.edtReportDate.date()
        SMO = self.rbSMO.isChecked()
        rbRegAndLoc = self.rbRegAndLoc.isChecked()
        rbRegOnly = self.rbOnlyReg.isChecked()
        rbLocOnly = self.rbOnlyLoc.isChecked()
        correct = None
        smoCode = None
        if SMO:
            smoCode = self.smoDict[self.cmbSMO.currentIndex()][0]
            correct = self.chkCorrectRecords.isChecked()
        tableClient = db.table('Client')
        tableClientAttach = db.table('ClientAttach')
        tableClientPolicy = db.table('ClientPolicy')
        tablePolicyKind = db.table('rbPolicyKind')
        tableInsurer = db.table('Organisation').alias('Insurer')
        tableClientDocument = db.table('ClientDocument')
        tableDocumentType = db.table('rbDocumentType')
        tableClientAddress = db.table('ClientAddress')
        tableClientAddressReg = db.table('ClientAddress').alias('ClientAddressReg')
        tableClientAddressLoc = db.table('ClientAddress').alias('ClientAddressLoc')
        tableAddress = db.table('Address')
        tableAddressReg = db.table('Address').alias('AddressReg')
        tableAddressLoc = db.table('Address').alias('AddressLoc')
        tableAddressHouse = db.table('AddressHouse')
        tableAddressHouseReg = db.table('AddressHouse').alias('AddressHouseReg')
        tableAddressHouseLoc = db.table('AddressHouse').alias('AddressHouseLoc')
        tableKLADR = db.table('kladr.KLADR')
        tableKLADRReg = db.table('kladr.KLADR').alias('kladrReg')
        tableKLADRLoc = db.table('kladr.KLADR').alias('kladrLoc')
        tableSocr = db.table('kladr.SOCRBASE').alias('Socr')
        tableStreet = db.table('kladr.STREET')
        tableStreetReg = db.table('kladr.STREET').alias('streetReg')
        tableStreetLoc = db.table('kladr.STREET').alias('streetLoc')
        tableStreetSocr = db.table('kladr.SOCRBASE').alias('StreetSocr')
        tableOrgStructure = db.table('OrgStructure')
        tableOrgStructureHasBookkeeperCode = db.table('OrgStructure').alias('OrgStructureHasBookkeeperCode')
        tableAttachType = db.table('rbAttachType')
        tableClientList = db.table('ClientList')
        tableSMOList = db.table('SMOList')
        tableCodeMOList = db.table('CodeMOList')

        queryTable = tableClientList.innerJoin(tableClient, tableClient['id'].eq(tableClientList['id']))
        queryTable = queryTable.leftJoin(tableClientAttach, tableClient['id'].eq(tableClientAttach['client_id']))
        queryTable = queryTable.leftJoin(tableAttachType, tableAttachType['id'].eq(tableClientAttach['attachType_id']))
        queryTable = queryTable.leftJoin(tableClientPolicy, 'ClientPolicy.id = getClientPolicyId(Client.id, 1)')
        queryTable = queryTable.leftJoin(tableInsurer, tableInsurer['id'].eq(tableClientPolicy['insurer_id']))
        queryTable = queryTable.leftJoin(tableSMOList, tableSMOList['id'].eq(tableInsurer['id']))
        queryTable = queryTable.leftJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableClientAttach['orgStructure_id']))
        queryTable = queryTable.leftJoin(tableCodeMOList, tableCodeMOList['orgStructure_id'].eq(tableOrgStructure['id']))
        #queryTable = queryTable.leftJoin(tableOrgStructureHasBookkeeperCode, u'%s = getOrgStructureIdHasBookkeeperCode(%s)' % (tableOrgStructureHasBookkeeperCode['id'], tableOrgStructure['id']))
        queryTable = queryTable.leftJoin(tableClientDocument, 'ClientDocument.id = getClientDocumentId(Client.id)')

        if not rbRegAndLoc:
            if rbRegOnly:
                queryTable = queryTable.leftJoin(tableClientAddress, """
                ClientAddress.id = (
				    Select ca.`id`
				    From ClientAddress as ca
				    where Client.`id` = ca.`client_id`
					    and ca.`type` = 0
					    and ca.deleted = 0
				    Order by If (ClientAttach.`endDate` is not Null, ca.`createDatetime` < ClientAttach.`endDate`, 1) desc, ca.`createDatetime` desc
				    Limit 1
				    )""")
            elif rbLocOnly:
                queryTable = queryTable.leftJoin(tableClientAddress, """
                ClientAddress.id = (
				    Select ca.`id`
				    From ClientAddress as ca
				    where Client.`id` = ca.`client_id`
					    and ca.`type` = 1
					    and ca.deleted = 0
				    Order by If (ClientAttach.`endDate` is not Null, ca.`createDatetime` < ClientAttach.`endDate`, 1) desc, ca.`createDatetime` desc
				    Limit 1
				    )""")
        else:
            queryTable = queryTable.leftJoin(tableClientAddress, """
                ClientAddress.id = (
				    Select ca.`id`
				    From ClientAddress as ca
				    where Client.`id` = ca.`client_id`
					    and ca.`type` = IF (%s = 1, '0', IF(%s = 2, '1', ''))
					    and ca.deleted = 0
				    Order by If (ClientAttach.`endDate` is not Null, ca.`createDatetime` < ClientAttach.`endDate`, 1) desc, ca.`createDatetime` desc
				    Limit 1
				    )""" %(tableAttachType['code'], tableAttachType['code']))
        queryTable = queryTable.leftJoin(tableAddress, tableAddress['id'].eq(tableClientAddress['address_id']))
        queryTable = queryTable.leftJoin(tableAddressHouse, tableAddressHouse['id'].eq(tableAddress['house_id']))
        queryTable = queryTable.leftJoin(tableKLADR, tableKLADR['CODE'].eq(tableAddressHouse['KLADRCode']))
        queryTable = queryTable.leftJoin(tableStreet, tableStreet['CODE'].eq(tableAddressHouse['KLADRStreetCode']))

        queryTable = queryTable.leftJoin(tableDocumentType,
                                         tableDocumentType['id'].eq(tableClientDocument['documentType_id']))
        queryTable = queryTable.leftJoin(tablePolicyKind, tablePolicyKind['id'].eq(tableClientPolicy['policyKind_id']))

        condAttach = [tableClientAttach['begDate'].dateLe(date),
                      tableClientAttach['deleted'].eq(0),
                      tableAttachType['outcome'].eq(0),
                      tableAttachType['code'].inlist([CAttachType.Territorial, CAttachType.Attached]),
                      tableOrgStructure['isArea'].inlist([COrgStructureAreaInfo.Pediatric, COrgStructureAreaInfo.Therapeutic, COrgStructureAreaInfo.GeneralPractice])]
        cond = []
        if orgStructureId:
            condAttach.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
        condAttach = db.joinAnd(condAttach)
        #cond.append(tableSMOList['code'].eq('9007'))
        cond.append(u'''Insurer.area NOT LIKE '2300000000000' ''')
        cols = [
            tableClient['id'].alias('ID'),
            u'''(Select ciRis.identifier
                    From ClientIdentification ciRis
                    Left JOIN rbAccountingSystem as ris
                        on ris.id = ciRis.accountingSystem_id
                    Where ciRis.client_id = Client.id
                        and ris.code = 'РИС'
                    Limit 1) AS `IDSTR`''',
            tableSMOList['code'].alias('SMO'),
            u'''
            (CASE rbPolicyKind.code
                WHEN '1' THEN 'С'
                WHEN '2' THEN 'В'
                WHEN '3' THEN 'П'
                WHEN '4' THEN 'Э'
                WHEN '5' THEN 'Э'
            END) AS DPFS''',
            tableClientPolicy['serial'].alias('DPFS_S'),
            tableClientPolicy['number'].alias('DPFS_N'),
            tableClient['lastName'].alias('FAM'),
            tableClient['firstName'].alias('IM'),
            tableClient['patrName'].alias('OT'),
            u'''
            (CASE Client.sex
                WHEN '0' THEN ''
                WHEN '1' THEN 'М'
                WHEN '2' THEN 'Ж'
            END) AS `SEX`''',
            tableClient['SNILS'].alias('SNILS'),
            tableClient['birthDate'].alias('DATR'),
            tableDocumentType['regionalCode'].alias('DOC'),
            tableClientDocument['serial'].alias('DOC_S'),
            tableClientDocument['number'].alias('DOC_N'),
            # TODO: craz: Очень странная логика для CODE_MO + функция getOrgStructureInfisCode есть только в самсоновских базах, т.к. она не наша и для всех мы ее не поставляем.
            tableCodeMOList['CODE_MO'],
            #tableOrgStructureHasBookkeeperCode['infisDepTypeCode'].alias('OID_MO'),
            "'' as `OID_MO`",
            u'''if (%s, %s, '') AS PRIK''' %(condAttach, tableAttachType['code']),
            u'''if (%s, %s, '') AS PRIK_D''' %(condAttach, tableClientAttach['begDate']),
            u'''IF(%s, %s, '') AS `OTKR_D` ''' %(condAttach, tableClientAttach['endDate']),
            tableOrgStructure['id'].alias('orgStructureId'),
            tableOrgStructure['infisInternalCode'].alias('UCH'),
            u"""(Select ciEnp.identifier
                    From ClientIdentification ciEnp
                    Left JOIN rbAccountingSystem as enp
                        on enp.id = ciEnp.accountingSystem_id
                    Where ciEnp.client_id = Client.id
                        and enp.code = 'ЕНП') AS `F_ENP`""",
            u"""(Select kk.Name
		        From kladr.KLADR as kk
		        where kk.code = (Concat(LEFT(%s, 5), '00000000'))) AS `R_NAME`""" %(tableAddressHouse['KLADRCode']),
            u"""IF(%s = 'г', %s, '') AS C_NAME""" % (tableKLADR['SOCR'], tableKLADR['NAME']),
            u"""IF(%s = 'г', '', %s) AS NP_NAME""" % (tableKLADR['SOCR'], tableKLADR['NAME']),
            tableStreet['NAME'].alias('UL_NAME'),
            tableAddressHouse['number'].alias('DOM'),
            tableAddressHouse['corpus'].alias('KOR'),
            tableAddress['flat'].alias('KV'),
        ]
        #group = [tableClient['id'], u'OTKR_D', u'PRIK', u'PRIK_D']
        #if 1: group += [tableSocStatus['id']]
        #order = [tableClient['lastName'], tableClient['firstName'], tableClient['patrName'], tableClient['birthDate'], tableClient['id'], 'ClientPolicy.id DESC']
        #return db.selectStmt(queryTable, cols, cond, group=group, order=order)
        return db.selectStmt(queryTable, cols, cond)

    def createQueryLgota(self):
        db = QtGui.qApp.db
        areaList = self.makeCondFromList([COrgStructureAreaInfo.Pediatric, COrgStructureAreaInfo.Therapeutic, COrgStructureAreaInfo.GeneralPractice])
        areaList2 = self.makeCondFromList([COrgStructureAreaInfo.Pediatric, COrgStructureAreaInfo.Therapeutic])
        attachTypeList = self.makeCondFromList([CAttachType.Territorial, CAttachType.Attached])
        date = self.edtReportDate.date()
        orgStructureId = self.cmbOrgStructure.value()
        stmt = u"""SELECT Client.`id` AS `ID`,
                rbSocStatusType.`code` AS `LGOTA`,
                DiscountDocType.`name` AS `DOCU`,
                (       SELECT
                            CodeMOList.`CODE_MO`
                        FROM ClientAttach
                            INNER JOIN rbAttachType
                                ON rbAttachType.`id` = ClientAttach.`attachType_id`
                            INNER JOIN OrgStructure
                                ON OrgStructure.`id` = ClientAttach.`orgStructure_id`
                            INNER JOIN CodeMOList
                                on CodeMOList.orgStructure_id = OrgStructure.id
                        WHERE Client.id = ClientAttach.client_id
                            AND (DATE(ClientAttach.`begDate`) <= DATE('%(date)s'))
                            AND (rbAttachType.`outcome` = 0)
                            AND (ClientAttach.`deleted` = 0)
                            AND (rbAttachType.`code` in %(attachType)s)
                            AND (OrgStructure.`isArea` in %(area)s)
                            AND %(orgStructure)s
                        ORDER BY
                            ClientAttach.`endDate`, ClientAttach.`id` desc
                        LIMIT 0, 1) AS `CODE_MO`,
                DiscountDocument.`serial` AS `DOCU_S`,
                DiscountDocument.`number` AS `DOCU_N`,
                ClientSocStatus.`begDate` AS `POLU_D`,
                ClientSocStatus.`endDate` AS `ORON_D`
            FROM Client
                INNER JOIN ClientSocStatus ON (ClientSocStatus.`client_id` = Client.`id`) AND (ClientSocStatus.`deleted` = 0) AND (ClientSocStatus.socStatusClass_id =
                        (SELECT ssc.id FROM rbSocStatusClass ssc
                         WHERE ssc.flatCode = 'benefits' LIMIT 1))
                LEFT JOIN rbSocStatusType ON (rbSocStatusType.`id` = ClientSocStatus.`socStatusType_id`) AND (rbSocStatusType.`code` IN ('010','011','012','020','030','040','050','060','061','062','064','064','081','082','083','084','085','091','092','093','094','095','096','097','098','099','100','101','102','111','112','113','120','121','122','123','124','125','128','129','131','132','140','141','142','150','201','203','205','207','209','210','211','281','282','284','301','302','303','304','305','306','307','308','309','310','311','312','313','314','315','316','317','318','319','320','321','322','323','324','325','326','327','328','329','330','331','332','501','502','503','504','505','506','507','701','801','901','902'))
                LEFT JOIN ClientDocument AS DiscountDocument ON DiscountDocument.`id` = ClientSocStatus.`document_id`
                LEFT JOIN rbDocumentType AS DiscountDocType ON DiscountDocType.`id` = DiscountDocument.`documentType_id`
                Inner join ClientListDistinct
                    on ClientListDistinct.id = Client.id""" %{u'date': forceString(date.toString('yyyy-MM-dd')),
                                             u'area': areaList,
                                             u'attachType': attachTypeList,
                                             u'orgStructure': '1' if not orgStructureId else (u'OrgStructure.id in %s' % self.makeCondFromList(getOrgStructureDescendants(orgStructureId)))}
        return db.query(stmt)

    def createQueryUch(self):
        db = QtGui.qApp.db
        orgStructureId = self.cmbOrgStructure.value()
        areaList = self.makeCondFromList([COrgStructureAreaInfo.Pediatric, COrgStructureAreaInfo.Therapeutic, COrgStructureAreaInfo.GeneralPractice])
        if not QtGui.qApp.checkGlobalPreference('53', u'да'):
            stmt = u"""
            Select
                (SELECT getOrgStructureInfisCode(os.id)) AS `CODE_MO`,
                os.infisInternalCode as `UCH`,
                LEFT(s.regionalCode, 1) as `D_SPEC`,
                p.lastName as `D_FAM`,
                p.firstName as `D_IM`,
                p.patrName as `D_OT`,
                p.SNILS as `D_SNILS`,
                pa.begDate as `D_PRIK_UCH`,
                pa.endDate as `D_OTKR_UCH`
            From OrgStructure os
                left join PersonAttach pa
                    on os.id = pa.orgStructure_id
                        and pa.deleted = 0
                left join Person p
                    on p.id = pa.master_id
                left join rbSpeciality	s
                    on s.id = p.speciality_id
            Where os.deleted = 0
                and os.`isArea` in %s
                and %s
            """ % (areaList, '1' if not orgStructureId else (u'os.id in %s' % self.makeCondFromList(getOrgStructureDescendants(orgStructureId))))
        else:
            stmt = u"""
            Select
                if (head.infisCode, head.infisCode, (SELECT getOrgStructureInfisCode(os.id))) AS `CODE_MO`,
                os.infisInternalCode as `UCH`,
                LEFT(s.regionalCode, 1) as `D_SPEC`,
                p.lastName as `D_FAM`,
                p.firstName as `D_IM`,
                p.patrName as `D_OT`,
                p.SNILS as `D_SNILS`,
                pa.begDate as `D_PRIK_UCH`,
                pa.endDate as `D_OTKR_UCH`
            From OrgStructure os
                left join OrgStructure head
                    on os.miacHead_id = head.id
                        and head.infisCode is not Null
                        and head.infisCode != ''
                left join PersonAttach pa
                    on os.id = pa.orgStructure_id
                        and pa.deleted = 0
                left join Person p
                    on p.id = pa.master_id
                left join rbSpeciality	s
                    on s.id = p.speciality_id
            Where os.deleted = 0
                and os.`isArea` in %s
                and %s
            """ % (areaList, '1' if not orgStructureId else (u'os.id in %s' % self.makeCondFromList(getOrgStructureDescendants(orgStructureId))))
        return db.query(stmt)

    def createTableClientIdList(self):
        areaList = self.makeCondFromList([COrgStructureAreaInfo.Pediatric, COrgStructureAreaInfo.Therapeutic, COrgStructureAreaInfo.GeneralPractice])
        areaList2 = self.makeCondFromList([COrgStructureAreaInfo.Pediatric, COrgStructureAreaInfo.Therapeutic])
        attachTypeList = self.makeCondFromList([CAttachType.Territorial, CAttachType.Attached])
        date = self.edtReportDate.date()
        orgStructureId = self.cmbOrgStructure.value()
        if not self.chkExternalArea.isChecked():
            stmt = u"""
                    Drop Temporary Table If Exists `ClientList`;
                    CREATE  TEMPORARY TABLE `ClientList`
                    (
                        `id` INT(11) NOT NULL,
                        `attach_id` INT(11) NOT NULL,
                        INDEX (`id`),
                        PRIMARY KEY(`attach_id`)
                    )
                        SELECT
                            ClientAttach.`client_id` as id,
                            ClientAttach.`id` as attach_id
                        FROM ClientAttach
                            INNER JOIN rbAttachType
                                ON rbAttachType.`id` = ClientAttach.`attachType_id`
                            INNER JOIN OrgStructure
                                ON OrgStructure.`id` = ClientAttach.`orgStructure_id`
                        WHERE (DATE(ClientAttach.`begDate`) <= DATE('%(date)s'))
                            AND (rbAttachType.`outcome` = 0)
                            AND (((ClientAttach.`endDate` IS NULL)
                                OR (DATE(ClientAttach.`endDate`) >= DATE('%(date)s'))
                                OR ((DATE(ClientAttach.`endDate`) < DATE('%(date)s'))
                                    AND (OrgStructure.`isArea` in %(area2)s))))
                            AND (ClientAttach.`deleted` = 0)
                            AND (rbAttachType.`code` in %(attachType)s)
                            AND (OrgStructure.`isArea` in %(area)s)
                            AND %(orgStructure)s
                        ORDER BY
                            ClientAttach.`client_id`;""" %{u'date': forceString(date.toString('yyyy-MM-dd')),
                                             u'area': areaList,
                                             u'area2': areaList2,
                                             u'attachType': attachTypeList,
                                             u'orgStructure': '1' if not orgStructureId else (u'OrgStructure.id in %s' % self.makeCondFromList(getOrgStructureDescendants(orgStructureId)))}
        else:
            stmt = u"""Drop Temporary Table If Exists `ClientList`;
                        CREATE  TEMPORARY TABLE ClientList
                        (
                            `id` INT(11) NOT NULL,
                            INDEX (`id`)
                        )
                            SELECT c.id
                            FROM Organisation o
                              INNER JOIN ClientPolicy cp
                                ON cp.insurer_id = o.id
                              LEFT JOIN ClientPolicy cp1
                                ON cp1.client_id = cp.client_id
                                AND cp1.id > cp.id AND cp1.deleted = 0
                              inner join Client c
                                on cp.Client_id = c.id
                            WHERE o.isInsurer = 1
                            AND cp1.id IS NULL
                            AND o.area != '2300000000000';"""
        query = QtGui.qApp.db.query(stmt)
        stmt = u'''Drop Temporary Table If Exists `ClientListDistinct`;
                    CREATE  TEMPORARY TABLE `ClientListDistinct`
                    (
                        `id` INT(11) NOT NULL,
                        INDEX (`id`),
                        PRIMARY KEY (`id`)
                    )
                    Select Distinct id From ClientList;'''
        query = QtGui.qApp.db.query(stmt)

    def getOrgStructureIdHasBookkeeperCode(self):
        db = QtGui.qApp.db
        stmt = u"Select OrgStructure.id, parent.infisDepTypeCode From OrgStructure Left Join OrgStructure as parent on parent.id = getOrgStructureIdHasBookkeeperCode(OrgStructure.id)"
        query = db.query(stmt)
        result = {}
        while query.next():
            record = query.record()
            result[forceInt(record.value('id'))] = forceString(record.value('infisDepTypeCode'))
        return result

    def createTableCodeMOList(self):
        db = QtGui.qApp.db
        orgStructureId = self.cmbOrgStructure.value()
        if not QtGui.qApp.checkGlobalPreference('53', u'да'):
            stmt = u"""
                    Drop Temporary Table If Exists `CodeMOList`;
                    CREATE  TEMPORARY TABLE `CodeMOList`
                    (
                        `orgStructure_id` INT(11) NOT NULL,
                        `CODE_MO` VARCHAR(30),
                        INDEX (`orgStructure_id`),
                        PRIMARY KEY (`orgStructure_id`)
                    )
                        SELECT
                            OrgStructure.id as orgStructure_id,
                            (SELECT getOrgStructureInfisCode(OrgStructure.id)) AS `CODE_MO`
                        FROM OrgStructure
                        WHERE %(orgStructure)s;
                            """ %{u'orgStructure': '1' if not orgStructureId else (u'OrgStructure.id in %s' % self.makeCondFromList(getOrgStructureDescendants(orgStructureId)))}
        else:
            stmt = u"""
                    Drop Temporary Table If Exists `CodeMOList`;
                    CREATE  TEMPORARY TABLE `CodeMOList`
                    (
                        `orgStructure_id` INT(11) NOT NULL,
                        `CODE_MO` VARCHAR(30),
                        INDEX (`orgStructure_id`),
                        PRIMARY KEY (`orgStructure_id`)
                    )
                        Select os.id as orgStructure_id,
                        if (head.infisCode, head.infisCode, (SELECT getOrgStructureInfisCode(os.id))) AS `CODE_MO`
                        FROM OrgStructure os
                            left join OrgStructure head
                                on os.miacHead_id = head.id
                                    and head.infisCode is not Null
                                    and head.infisCode != ''
                        WHERE %(orgStructure)s;
                            """ %{u'orgStructure': '1' if not orgStructureId else (u'os.id in %s' % self.makeCondFromList(getOrgStructureDescendants(orgStructureId)))}
        query = db.query(stmt)

    def createTableSMOList(self):
        db = QtGui.qApp.db
        stmt = u'''
        Drop Temporary Table If Exists SMOList;
        CREATE  TEMPORARY TABLE SMOList
        (
			`id` INT(11) NOT NULL AUTO_INCREMENT,
            `code` VARCHAR(12),
            INDEX (`id`),
			PRIMARY KEY (`id`)
        )
        Select Distinct Insurer.id as id,
	        IFNULL(
                IF(Insurer.area = '2300000000000',
					IF(
						Insurer.head_id IS NULL,
						IF(
							TRIM(Insurer.infisCode),
							Insurer.infisCode,
                            ''
						),
						(
                            IF(
                                TRIM(head.infisCode),
                                head.infisCode,
                                ''
                            )
						)
					),
                    NULL
				),
					'9007'
				) AS code
            From ClientPolicy
                inner join Organisation Insurer
                    on Insurer.id = ClientPolicy.insurer_id
                left join Organisation head
                    on head.id = Insurer.head_id
            Where IF (head.id, head.isInsurer = 1, Insurer.isInsurer = 1)
            Group by Insurer.id; '''
        query = db.query(stmt)

    def deleteTempTables(self):
        stmt = u'''DROP TABLE IF EXISTS ClientList, ClientListDistinct, SMOList, CodeMOList;'''
        QtGui.qApp.db.query(stmt)

    def makeCondFromList(self, list):
        cond = u"("
        for item in list:
            cond += u"%s, " %forceString(item)
        cond =  cond[:-2] + u")"
        return cond

    def checkOrgStructureForLoops(self):
        tables = {u'OrgStructure': u'id = parent_id',
                  u'Organisation': u'id = head_id'}
        tableErrorList = []
        for table, cond in tables.items():
            stmt = u'''Select id From %s Where %s''' %(table, cond)
            query = QtGui.qApp.db.query(stmt)
            if query.first():
                tableErrorList.append(table)
        if tableErrorList:
            QtGui.QMessageBox.warning(self,
                                      u'Ошибка в таблице',
                                      u'В таблице %s присутствует цикл. Продолжение операции невозможно. Обратитесь в службу технической поддержки' %u', '.join(tableErrorList),
                                      buttons = QtGui.QMessageBox.Ok,
                                      defaultButton = QtGui.QMessageBox.Ok)
            return False
        return True

    def on_btnRetrieveClicked(self):
        QtGui.qApp.callWithWaitCursor(self, self.onRetrieveClicked)

    def onRetrieveClicked(self):
        # time = []
        # time.append(QtCore.QDateTime.currentMSecsSinceEpoch())
        # self.orgStructureBookkeeperCodeDict = self.getOrgStructureIdHasBookkeeperCode()
        # print('get BookkeeperCode')
        # time.append(QtCore.QDateTime.currentMSecsSinceEpoch())
        # self.createTableClientIdList()
        # print('get ClientIdList')
        # time.append(QtCore.QDateTime.currentMSecsSinceEpoch())
        # self.createTableSMOList()
        # print('get SMOList')
        # time.append(QtCore.QDateTime.currentMSecsSinceEpoch())
        # print('get main')
        # time.append(QtCore.QDateTime.currentMSecsSinceEpoch())
        # self.queryUch = self.createQueryUch()
        # print('get uch')
        # time.append(QtCore.QDateTime.currentMSecsSinceEpoch())
        # self.queryLgota = self.createQueryLgota()
        # print('get lgota')
        # time.append(QtCore.QDateTime.currentMSecsSinceEpoch())
        # self.deleteTempTables()
        # diff = []
        # for i in range(len(time) - 1):
        #     diff.append(time[i+1] - time[i])
        # print(diff)
        if not self.checkOrgStructureForLoops():
            return
        self.orgStructureBookkeeperCodeDict = self.getOrgStructureIdHasBookkeeperCode()
        self.createTableClientIdList()
        self.createTableSMOList()
        self.createTableCodeMOList()
        self.queryUch = self.createQueryUch()
        self.queryLgota = self.createQueryLgota()
        query = self.createQuery()
        self.setQuery(query)

    def onSaveClicked(self):
        params = {}
        def updateCodeMODict(dict, record):
            codeMO = forceString(record.value('CODE_MO'))
            birthDate = forceDate(record.value('DATR'))
            sex = forceString(record.value('SEX'))
            age = calcAgeInYears(birthDate, self.edtReportDate.date())
            ageMonth = calcAgeInMonths(birthDate, self.edtReportDate.date())
            translate = {u'М': 'Male', u'Ж': 'Female'} #в юникоде русская
            counters = dict.get(codeMO, {})
            if not counters:
                counters = {'Male': [0] * 5,
                            'Female': [0] * 5,
                            'shortName': self.getOrganisationInfoByInfisCode(codeMO).get('shortName', u'')}
            if not translate.get(sex, '') in counters:
                return counters
            ages = counters[translate[sex]]
            if ageMonth < 12:
                ages[0] += 1
            elif age >= 1 and age <= 4:
                ages[1] += 1
            elif age >= 5 and age <= 17:
                ages[2] += 1
            elif age >= 18 and ((age <= 59 and sex == u'М') or (age <= 54 and sex == u'Ж')):
                ages[3] += 1
            elif ((age >= 60 and sex == u'М') or (age >= 55 and sex == u'Ж')):
                ages[4] += 1
            else:
                print (age, sex)

            dict[codeMO] = counters

        def fillDbfValue(dbfRow, record, fieldName, type_='str'):
            if record.contains(fieldName):
                mapTypeToFunc = {'str': forceStringEx, 'double': forceDouble, 'int': forceInt, 'date': get_date}
                dbfRow[fieldName] = forceStringEx(record.value(fieldName)) if fieldName == 'DPFS_N' else mapTypeToFunc.get(type_, forceStringEx)(record.value(fieldName))

        def fillDbfRecord(dbfRow, record, fields):
            for field in fields:
                if len(field) == 4:
                    fieldName, fieldType, _, fieldPrecision = field
                else:
                    fieldName, fieldType = field[:2]
                    fieldPrecision = 0


                if fieldType == 'D': type_ = 'date'
                elif fieldType == 'N':
                    if fieldPrecision == 0: type_ = 'int'
                    else: type_ = 'double'
                else: type_ = 'str'
                fillDbfValue(dbfRow, record, fieldName, type_)

        def initDbf(name, additionalName, getFields):
            filename = u'%s.dbf' %(name.upper() + additionName)
            tmp_filename = os.path.join(tmpdir, filename)
            dbf_file = dbf.Dbf(tmp_filename, new=True, encoding='cp866')
            fields = getFields()
            dbf_file.addField(*fields)
            return {'filename': filename,
                    'tmp_filename': tmp_filename,
                    'dbf': dbf_file,
                    'fields': fields
                    }

        def fillDbf(query, params): #обязательные поля: query, dbf_file, modifyRecord, fields, type
            if query.isForwardOnly():
                query.setForwardOnly(False)
            query.first()
            query.previous()
            counter = 0
            type = params['type']
            fields = params['fields']
            if type == 'prik':
                dictUch = {}
                dictCodeMO = {}
            emptyFieldsCounter = {}
            for field in fields:
                emptyFieldsCounter[(field[0:2])] = 0
            while query.next():
                record = query.record()
                modifyRecord(record, type)
                rec = params['dbf'].newRecord()
                if type == 'prik':
                    uch = forceString(record.value('UCH'))
                    if not  forceDate(record.value('OTKR_D')):
                        dictUch[uch] = dictUch.get(uch, 0) + 1
                    updateCodeMODict(dictCodeMO, record)
                counter += 1
                self.countEmptyFieldsInRecord(record, emptyFieldsCounter)
                fillDbfRecord(rec, record, fields)
                rec.store()
            res = {'counter': counter,
                   'emptyFieldsCounter': emptyFieldsCounter}

            params['dbf'].close()
            if type !='prik':
                return res
            big_uch_counter = 0
            for value in dictUch.values():
                if value > 3000:
                    big_uch_counter += 1
            res['big_uch_counter'] = big_uch_counter
            res['codeMOCounters'] = dictCodeMO
            return res

        def modifyRecord(record, type):
            if type == 'lgota':
                return
            elif type == 'uch':
                snils = forceString(record.value('D_SNILS'))
                snils = snils[:3] + u'-' + snils[3:6] + u'-' + snils[6:9] + u' ' + snils[9:11] if snils else u''
                record.setValue('D_SNILS', toVariant(snils))
                return
            elif type == 'prik':
                snils = forceString(record.value('SNILS')) if type == 'uch' else forceString(record.value('SNILS'))
                snils = snils[:3] + u'-' + snils[3:6] + u'-' + snils[6:9] + u' ' + snils[9:11] if snils else u''
                record.setValue('SNILS', toVariant(snils))
                record.setValue('OID_MO', toVariant(self.orgStructureBookkeeperCodeDict.get(forceInt(record.value('orgStructureId')), '')))
            return

        folder = forceStringEx(QtGui.QFileDialog.getExistingDirectory(self,
                                                        u'Директория для сохранения отчета в МИАЦ',
                                                        forceStringEx(getVal(
                                                    QtGui.qApp.preferences.appPrefs, 'ExportAttachedClientsR23Miac', ''))))
        if not folder:
            return
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        succsessful = False
        try:
            tmpdir = QtGui.qApp.getTmpDir()
            infis = forceStringEx(QtGui.qApp.db.translate('OrgStructure', 'id', self.cmbOrgStructure.value(), 'bookkeeperCode'))
            if self.rbSMO.isChecked() and self.cmbSMO.currentIndex() >= 2:
                smoCode = self.smoDict[self.cmbSMO.currentIndex()][0]
                additionName = u'%s_%s' % (smoCode, infis)
            else:
                additionName = infis
            zip_filename = u'PRIK%s.zip' % additionName

            fileList = ['prik', 'uch']
            if not self.rbSMO.isChecked():
                fileList.append('lgota')

            getFields = {'prik':  self.getPrikFields,
                         'lgota': self.getLgotaFields,
                         'uch':   self.getUchFields}
            getQuery = {'prik':  self.query,
                        'lgota': self.queryLgota,
                        'uch':   self.queryUch}

            for fileItem in fileList:
                tmpDict = {'type': fileItem}
                tmpDict.update(initDbf(fileItem, additionName, getFields[fileItem]))
                tmpDict.update(fillDbf(getQuery[fileItem], tmpDict))
                params[fileItem] = tmpDict

            zip_full_name = os.path.join(folder, zip_filename)
            zf = zipfile.ZipFile(zip_full_name, 'w', allowZip64=True)
            for fileItem in fileList:
                zf.write(params[fileItem]['tmp_filename'], params[fileItem]['filename'], zipfile.ZIP_DEFLATED)
            zf.close()

            actsInfo = {'miac': {'filename': u'act%s.html' % infis,
                                 'createFunc': self.buildActMIAC},
                        'smo':  {'filename': u'act%s.html' % additionName,
                                 'createFunc': self.buildActSMO}}

            actInfo = actsInfo.get('miac', {}) if self.rbMIAC.isChecked() else \
                            actsInfo.get('smo', {}) if self.rbSMO.isChecked() else {}
            if actInfo:
                import codecs
                attachFile_filename = actInfo['filename']
                attachFile_full_name = os.path.join(folder, attachFile_filename)
                with codecs.open(attachFile_full_name, "w", encoding="utf-8") as attachFile:
                    attachFile.write(actInfo['createFunc'](params))
                    attachFile.close()
            succsessful = True
        finally:
            QtGui.qApp.restoreOverrideCursor()
            if succsessful:
                QtGui.QMessageBox.information(self, u'Внимание!', u'Файл %s успешно сохранен.' % zip_full_name)
            else:
                QtGui.QMessageBox.information(self, u'Внимание!', u'Ошибка про сохранении файла.')
            QtGui.qApp.preferences.appPrefs['ExportAttachedClientsR23Miac'] = toVariant(folder)


    def countEmptyFieldsInRecord(self, record, dict):
        translate = {'C': forceString,
                     'N': forceInt,
                     'D': forceDate
                     }
        for key in dict.keys():
            field = key[0]
            forceFunction = translate[key[1]]
            if not forceFunction(record.value(field)):
                dict[key] += 1

    def getOrganisationInfoByInfisCode(self, infisCode):
        db = QtGui.qApp.db
        result = {}
        if not infisCode:
            return result
        record = db.getRecordEx('Organisation', '*', u"infisCode = '%s'" %infisCode)
        if record:
            result['id']         = forceRef(record.value('id'))
            result['fullName']   = forceString(record.value('fullName'))
            result['shortName']  = forceString(record.value('shortName'))
            result['infisCode']  = forceString(record.value('infisCode'))
            result['head_id']    = forceRef(record.value('head_id'))
            result['chief']      = forceString(record.value('chief'))
            result['accountant'] = forceString(record.value('accountant'))
        return result

    def getOrganisationIdByOrgStructureId(self, orgStructure_id):
        db = QtGui.qApp.db
        record = db.getRecordEx('OrgStructure', 'organisation_id', u'id=%s' %orgStructure_id)
        return forceRef(record.value('organisation_id')) if  record else 0

    def buildActMIAC(self, params):
        from ActsOfExprort import ActMIAC
        params.update({'date': self.edtReportDate.date(),
                       'currentOrgInfo': getOrganisationInfo(QtGui.qApp.currentOrgId()),
                       'currentOrgMainStuff': getOrganisationMainStaff(QtGui.qApp.currentOrgId())})
        act = ActMIAC()
        act.build(params)
        return act.toUtf()

    def buildActSMO(self, params):
        date = self.edtReportDate.date()
        smoOrgInfo = self.getOrganisationInfoByInfisCode(self.smoDict[self.cmbSMO.currentIndex()][0])
        orgId = self.getOrganisationIdByOrgStructureId(self.cmbOrgStructure.value()) if self.cmbOrgStructure.value() else QtGui.qApp.currentOrgId()
        moOrgInfo = getOrganisationInfo(orgId)
        moOrgMainStuff =  getOrganisationMainStaff(orgId)
        params.update({'date': date,
                       'moOrgInfo': moOrgInfo,
                       'moOrgMainStuff': moOrgMainStuff,
                       'smoOrgInfo': smoOrgInfo}
                      )
        from ActSMO import ActSMO
        act = ActSMO()
        return act.build(params)

    def onCloseClicked(self):
        self.deleteTempTables()
        self.accept()

    def getPrikFields(self):
        return [
            ('ID',      'N', 7, 0),     # Уникальной значение записи в пределах кода МО, используется для обратной связи
            ('IDSTR',   'N', 10, 0),    # Для идентификации записей и установления однозначного соответствия между / идентификатор РИС
                                        # сведениями в краевом регистре и сведениями в ИС МО
            ('SMO',     'C', 4),        # Код СМО плательщика (SPR02), для инокраевых - 9007
            ('DPFS',    'C', 1),        # Тип полиса. П-бумажный полис единого образца, Э-электронный полис единого
                                        # образца, В-временное свидетельство, С-полис старого образца
            ('DPFS_S',  'C', 12),       # Серия полиса (указывается для п. старого образца)
            ('DPFS_N',  'C', 20),       # Номер полиса
            ('FAM',     'C', 40),       # Фамилия
            ('IM',      'C', 40),       # Имя
            ('OT',      'C', 40),       # Отчество
            ('SEX',     'C',  1),       # Пол
            ('DATR',    'D'    ),       # Дата рождения
            ('SNILS',   'C', 14),       # Снилс
            ('DOC',     'C',  2),       # Тип ДУЛ (SPR43)
            ('DOC_S',   'C', 10),       # Серия ДУЛ
            ('DOC_N',   'C', 15),       # Номер ДУЛ
            ('CODE_MO', 'C', 5),        # Код медицинской организации (структурного подразделения, оказывающего
                                        # амб.-поликлиническую помощь), к которому прикреплен
            ('OID_MO',  'C', 30),        # Код медицинской организации из паспорта ЛПУ
            ('PRIK',    'C', 1),        # Способ прикрепления. 0-нет данных, 1-по месту регистрации, 2-по личному заявлению
            ('PRIK_D',  'D'),           # Дата прикрепления
            ('OTKR_D',  'D'),           # Дата открепления
            ('UCH',     'C', 5),        # Номер участка
            ('R_NAME',  'C', 30),       # Наименование района по месту регистрации пациента
            ('C_NAME',  'C', 30),       # Наименование города
            #('Q_NP',    'N', 2, 0),     # Код вида населенного пункта (SPR44)
            ('NP_NAME', 'C', 40),       # Наименование населенного пункта по месту регистрации
            #('Q_UL',    'N', 2, 0),     # Код типа наименования улицы (SPR45)
            ('UL_NAME', 'C', 40),       # Наименование улицы
            ('DOM',     'C', 7),        # Номер дома
            ('KOR',     'C', 5),        # Корпус/строение
            ('KV',      'C', 5),        # Квартира/комната
            ('SMORES',  'C', 40),       # Результат сверки, заполняется СМО
            ('S_COMM',  'C',200),       # Комментарий СМО
            ('MIACRES', 'C', 40),       # Результат сверки, заполняется МИАЦ
            ('M_COMM',  'C',200),       # Комментарий БГУЗ МИАЦ
            ('TFOMSRES','C', 40),       # Результат сверки
            ('F_ENP',   'C', 16),       # Номер ЕНП в системе ОМС
            ('F_SMO',   'C',  4),       # Код СМО, в системе ОМС
            ('F_DPFS',  'C',  1),       # Тип ДПФС
            ('F_DPFS_S','C', 12),       # Серия ДПФС
            ('F_DPFS_N','C', 20),       # Номер ДПФС
            ('F_FAM',   'C', 40),       # Фамилия
            ('F_IM',    'C', 40),       # Имя
            ('F_OT',    'C', 40),       # Отчество
            ('F_SEX',   'C',  1),       # Пол
            ('F_DATR',  'D'),           # Дата рождения
            ('F_DSTOP', 'D'),           # Дата окончания действия ДПФС
            ('F_DATS',  'D'),           # Дата смерти по данным органов ЗАГС
            ('F_SNILS', 'C', 14),       # СНИЛС
            ('F_DOC',   'C',  2),       # Тип документа УДЛ
            ('F_DOC_S', 'C', 10),       # Серия документа УДЛ
            ('F_DOC_N', 'C', 15),       # Номер документа УДЛ
            ('F_COMM',  'C',200),       # Комментарий ТФОМС
            ]

    def getLgotaFields(self):
        return [
            ('ID',         'N', 7, 0),     # Уникальное значение записи в пределах кода МО, используется для обратной связи
                                           #  и связи с файлом PRIK
            ('CODE_MO',    'C', 5),        # Код медицинской организации (структурного подразделения, оказывающего
                                           # амб.-поликлиническую помощь), к которому прикреплен гражданин (SPR01)
            ('LGOTA',      'C', 3),        # Код льготы из справочника
            ('DOCU',       'C', 150),      # Название документа, подтверждающего право на льготу
            ('DOCU_S',  'C', 15),       # Серия документа, подтверждающего право на льготу
            ('DOCU_N', 'C', 30),       # Номер документа, подтверждающего право на льготу
            ('POLU_D',     'D'),           # Дата получения права на льготу по категории (не обязательно)
            ('ORON_D',     'D'),           # Дата окончания права на льготу по категории (может быть пустой)
        ]

    def getUchFields(self):
        return [
            ('CODE_MO',    'C',  5),        # Код медицинской организации (структурного подразделения, оказывающего
                                            # амб.-поликлиническую помощь), к которому прикреплен гражданин (SPR01)
            ('UCH',        'C',  5),        # Номер участка
            ('D_SPEC',     'C',  2),        # Категория медицинского работника
            ('D_FAM',      'C', 40),        # Фамилия врача
            ('D_IM',       'C', 40),        # Имя врача
            ('D_OT',       'C', 40),        # Отчество врача
            ('D_SNILS',    'C', 14),        # СНИЛС
            ('D_PRIK_UCH', 'D'),            # Дата прикрепления врача к участку
            ('D_OTKR_UCH', 'D'),            # Дата открепления (или увольнения) врача с участка
            ('MIACRES',    'C', 40),        # Результат сверки
        ]

    @QtCore.pyqtSlot(bool)
    def on_rbSMO_toggled(self, value):
        self.chkExternalArea.setChecked(False)

def main():
    import sys
    from library.database import connectDataBaseByInfo
    app = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    QtGui.qApp.currentOrgId = lambda: 229917

    connectionInfo = {'driverName' : 'mysql',
                      'host' : '192.168.0.207',
                      'port' : 3306,
                      'database' : 's11vm',
                      'user' : 'dbuser',
                      'password' : 'dbpassword',
                      'connectionName' : 'vista-med',
                      'compressData' : True,
                      'afterConnectFunc' : None}
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    CAttachedClientsDialog(None).exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()