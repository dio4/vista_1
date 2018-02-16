# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################

__author__ = 'nat'

import locale
import logging
import os
import tempfile
import zipfile

from PyQt4 import QtCore, QtGui

from library.DateEdit import CDateEdit
from library.dbfpy import dbf
from library.ProgressBar import CProgressBar
from library.ProgressInformer import CProgressInformer
from library.Utils import CLogHandler, getClassName, forceDouble, get_date, forceInt, \
                            forceStringEx, forceTr
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.Utils import getOrgStructureDescendants


lgotaCodeList = ['010', '011', '012', '020', '030', '040', '050', '060', '061', '062', '064', '064', '081', '082', '083', \
                 '084', '085', '091', '092', '093', '094', '095', '096', '097', '098', '099', '100', '101', '102', '111', \
                 '112', '113', '120', '121', '122', '123', '124', '125', '128', '129', '131', '132', '140', '141', '142', \
                 '150', '201', '203', '205', '207', '209', '210', '211', '281', '282', '284', '301', '302', '303', '304', \
                 '305', '306', '307', '308', '309', '310', '311', '312', '313', '314', '315', '316', '317', '318', '319', \
                 '320', '321', '322', '323', '324', '325', '326', '327', '328', '329', '330', '331', '332', '501', '502', \
                 '503', '504', '505', '506', '507', '701', '801', '901', '902']

class CExportR23AttachClientEngine(object):
    attachedFields = [
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
            ('DATR',    'D'),           # Дата рождения
            ('DOC',     'C', 2),        # Тип ДУЛ (SPR43)
            ('DOC_S',   'C', 10),       # Серия ДУЛ
            ('DOC_N',   'C', 15),       # Номер ДУЛ
            ('CODE_MO', 'C', 5),        # Код медицинской организации (структурного подразделения, оказывающего
                                        # амб.-поликлиническую помощь), к которому прикреплен
            ('PRIK',    'C', 1),        # Способ прикрепления. 0-нет данных, 1-по месту регистрации, 2-по личному заявлению
            ('PRIK_D',  'D'),           # Дата прикрепления
            ('OTKR_D',  'D'),           # Дата открепления
            ('UCH',     'C', 5),        # Номер участка
            ('F_ENP',   'N', 10),       # идентификатор по ЕНП
            ('R_NAME',  'C', 30),       # Наименование района по месту регистрации пациента
            ('C_NAME',  'C', 30),       # Наименование города
            ('Q_NP',    'N', 2, 0),     # Код вида населенного пункта (SPR44)
            ('NP_NAME', 'C', 40),       # Наименование населенного пункта по месту регистрации
            ('Q_UL',    'N', 2, 0),     # Код типа наименования улицы (SPR45)
            ('UL_NAME', 'C', 40),       # Наименование улицы
            ('DOM',     'C', 7),        # Номер дома
            ('KOR',     'C', 5),        # Корпус/строение
            ('KV',      'C', 5),        # Квартира/комната
            ('SMORES',  'C', 40),       # Результат сверки, заполняется СМО
            ('MIACRES', 'C', 40),       # Результат сверки, заполняется МИАЦ
            ]

    def __init__(self, db, orgStructureId, date, progressInformer=None):
        self.db = db
        self.orgStructureId = orgStructureId
        self.date = date
        self.progressInformer = progressInformer if isinstance(progressInformer, CProgressInformer) else CProgressInformer(processEventsFlag=None)
        self.logger = logging.getLogger(name=getClassName(self))
        self.logger.setLevel(logging.INFO)
        self.documents = {}

    def getLogger(self):
        return self.logger

    def terminate(self):
        self.isTerminated = True

    def onTerminating(self):
        self.logger().info(u'Прервано')
        self.progressInformer.reset(0, u'Прервано')

    def phaseReset(self, phasesCount):
        self.currentPhase = 0
        self.totalPhases = phasesCount

    @property
    def phaseInfo(self):
        return u'[Этап %s/%s] ' % (self.currentPhase, self.totalPhases)

    def nextPhase(self, steps, description=u''):
        self.currentPhase += 1
        self.progressInformer.reset(steps, self.phaseInfo + description)
        self.getLogger().info(self.phaseInfo + description)

    def nextPhaseStep(self, description = None):
        self.progressInformer.nextStep((self.phaseInfo + description) if description else None)

    def getQueryComponents(self):
        tableClient = self.db.table('Client')
        tableClientAttach = self.db.table('ClientAttach')
        tableClientPolicy = self.db.table('ClientPolicy')
        tablePolicyKind = self.db.table('rbPolicyKind')
        tableInsurer = self.db.table('Organisation').alias('Insurer')
        tableClientDocument = self.db.table('ClientDocument')
        tableDocumentType = self.db.table('rbDocumentType')
        tableClientAddress = self.db.table('ClientAddress')
        tableAddress = self.db.table('Address')
        tableAddressHouse = self.db.table('AddressHouse')
        tableKLADR = self.db.table('kladr.KLADR')
        tableSocr = self.db.table('kladr.SOCRBASE').alias('Socr')
        tableStreet = self.db.table('kladr.STREET')
        tableStreetSocr = self.db.table('kladr.SOCRBASE').alias('StreetSocr')
        tableOrgStructure = self.db.table('OrgStructure')
        tableAttachType = self.db.table('rbAttachType')

        queryTable = tableClientAttach.innerJoin(tableClient, tableClient['id'].eq(tableClientAttach['client_id']))
        queryTable = queryTable.innerJoin(tableAttachType, tableAttachType['id'].eq(tableClientAttach['attachType_id']))
        queryTable = queryTable.leftJoin(tableClientPolicy, 'ClientPolicy.id = getClientPolicyId(Client.id, 1)')
        queryTable = queryTable.leftJoin(tableInsurer, tableInsurer['id'].eq(tableClientPolicy['insurer_id']))
        queryTable = queryTable.innerJoin(tableOrgStructure, tableOrgStructure['id'].eq(tableClientAttach['orgStructure_id']))
        queryTable = queryTable.leftJoin(tableClientDocument, 'ClientDocument.id = getClientDocumentId(Client.id)')
        queryTable = queryTable.leftJoin(tableClientAddress, 'ClientAddress.id = getClientRegAddressId(Client.id)')
        queryTable = queryTable.leftJoin(tableAddress, tableAddress['id'].eq(tableClientAddress['address_id']))
        queryTable = queryTable.leftJoin(tableAddressHouse, tableAddressHouse['id'].eq(tableAddress['house_id']))
        queryTable = queryTable.leftJoin(tableKLADR, tableKLADR['CODE'].eq(tableAddressHouse['KLADRCode']))
        queryTable = queryTable.leftJoin(tableSocr,
                                         '''Socr.KOD_T_ST = (SELECT KOD_T_ST
                                                             FROM kladr.SOCRBASE S
                                                             WHERE S.SCNAME = KLADR.SOCR
                                                             ORDER BY LEVEL
                                                             LIMIT 1)''')
        queryTable = queryTable.leftJoin(tableStreet, tableStreet['CODE'].eq(tableAddressHouse['KLADRStreetCode']))
        queryTable = queryTable.leftJoin(tableStreetSocr,
                                         '''StreetSocr.KOD_T_ST = (SELECT KOD_T_ST
                                                                   FROM kladr.SOCRBASE S
                                                                   WHERE S.SCNAME = STREET.SOCR
                                                                   ORDER BY LEVEL DESC
                                                                   LIMIT 1)
                                         ''')
        queryTable = queryTable.leftJoin(tableDocumentType,
                                         tableDocumentType['id'].eq(tableClientDocument['documentType_id']))
        queryTable = queryTable.leftJoin(tablePolicyKind, tablePolicyKind['id'].eq(tableClientPolicy['policyKind_id']))
        cond = [tableClientAttach['begDate'].dateLe(self.date),
                tableAttachType['come'].inlist([1, 2]),
                tableClientAttach['deleted'].eq(0)]
        if self.orgStructureId:
            cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(self.orgStructureId)))
        cols = [
            tableClient['id'].alias('IDSTR'),
            u'''IFNULL(IF(Insurer.head_id IS NULL,
                    IF(TRIM(Insurer.infisCode), Insurer.infisCode, NULL),
                    (SELECT IF(TRIM(Organisation.infisCode), Organisation.infisCode, NULL)
                    FROM Organisation
                    WHERE Organisation.id = Insurer.head_id)), '9007') AS SMO''',
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
            tableClient['birthDate'].alias('DATR'),
            tableDocumentType['regionalCode'].alias('DOC'),
            tableClientDocument['serial'].alias('DOC_S'),
            tableClientDocument['number'].alias('DOC_N'),
            # TODO: craz: Очень странная логика для CODE_MO + функция getOrgStructureInfisCode есть только в самсоновских базах, т.к. она не наша и для всех мы ее не поставляем.
            '(SELECT getOrgStructureInfisCode(OrgStructure.id)) AS CODE_MO',
            u'0 AS PRIK',
            tableClientAttach['begDate'].alias('PRIK_D'),
            'IF(ClientAttach.endDate < \'%s\', ClientAttach.endDate, NULL) AS OTKR_D' % \
                                                    self.date.toString(QtCore.Qt.ISODate),
            tableOrgStructure['infisInternalCode'].alias('UCH'),
            tableAddressHouse['KLADRCode'].alias('R_NAME'),
            tableKLADR['NAME'].alias('C_NAME'),
            tableSocr['infisCODE'].alias('Q_NP'),
            tableKLADR['NAME'].alias('NP_NAME'),
            tableStreetSocr['infisCODE'].alias('Q_UL'),
            tableStreet['NAME'].alias('UL_NAME'),
            tableAddressHouse['number'].alias('DOM'),
            tableAddressHouse['corpus'].alias('KOR'),
            tableAddress['flat'].alias('KV')
        ]
        group = [tableClient['id']]
        order = [tableClient['lastName'], tableClient['firstName'], tableClient['patrName'], tableClient['id'], 'ClientPolicy.id DESC']
        return queryTable, cols, cond, order, group

    def fillDbfRecord(self, dbfRow, record, attachedFields):
        def fillDbfValue(dbfRow, record, fieldName, type_='str'):
            if record.contains(fieldName):
                mapTypeToFunc = {'str': forceStringEx, 'double': forceDouble, 'int': forceInt, 'date': get_date}
                dbfRow[fieldName] = record.value(fieldName).toLongLong()[0] if fieldName == 'DPFS_N' else mapTypeToFunc.get(type_, forceStringEx)(record.value(fieldName))

        for field in attachedFields:
            if len(field) == 4:
                fieldName, fieldType, _, fieldPrecision = field
            else:
                fieldName, fieldType = field[:2]
                fieldPrecision = 0

            if fieldType == 'D':
                type = 'date'
            elif fieldType == 'N':
                type = 'int' if fieldPrecision == 0 else 'double'
            else:
                type = 'str'

            fillDbfValue(dbfRow, record, fieldName, type)

    def save(self, outDir):
        outDir = forceStringEx(outDir)
        self.nextPhase(len(self.documents), u'Сохранение файлов')
        for smo in self.documents.keys():
            dbfFile = self.documents[smo]
            filename = forceStringEx(dbfFile.name).rpartition('/')[-1]
            zipfilename = forceStringEx(filename[:-4]) + '.zip'
            zipfilepath = os.path.join(outDir, zipfilename)
            try:
                zf = zipfile.ZipFile(zipfilepath, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
                zf.write(dbfFile.name,  filename)
                self.getLogger().info(u'Создан файл: %s' % zipfilename)
                zf.close()
                self.nextPhaseStep()
                self.documents.pop(smo)
            except Exception, e:
                self.getLogger().critical(u'Не удалось сохранить файл %s' % zipfilename)


class CExportR23AttachClientMIACEngine(CExportR23AttachClientEngine):
    discountFields = [('ID',      'N', 7, 0),     # Уникальное значение записи в пределах кода МО, используется для обратной связи
                                                    #  и связи с файлом PRIK
                      ('CODE_MO', 'C', 5),        # Код медицинской организации (структурного подразделения, оказывающего
                                                    # амб.-поликлиническую помощь), к которому прикреплен гражданин (SPR01)
                      ('LGOTA',   'C', 3),        # Код льготы из справочника
                      ('DOCU',    'C', 150),      # Название документа, подтверждающего право на льготу
                      ('DOC_S',   'N', 10),       # Серия документа, подтверждающего право на льготу
                      ('DOC_N',   'N', 10),       # Номер документа, подтверждающего право на льготу
                      ('POLU_D',  'D'),           # Дата получения права на льготу по категории (не обязательно)
                      ('ORON_D',  'D'),           # Дата окончания права на льготу по категории (может быть пустой)
                    ]

    def __init__(self, db, orgStructureId, date, progressInformer=None):
        CExportR23AttachClientEngine.__init__(self, db, orgStructureId, date, progressInformer=progressInformer)
        self.documents = {}

    def process(self):
        self.isTerminated = False
        self.phaseReset(2)
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        tableDiscountDocument = db.table('ClientDocument').alias('DiscountDocument')
        tableDiscountDocType = db.table('rbDocumentType').alias('DiscountDocType')
        tableSocStatus = db.table('ClientSocStatus')
        tableSocStatusType = db.table('rbSocStatusType')

        queryTable, cols, cond, order, group = self.getQueryComponents()
        queryTable = queryTable.leftJoin(tableSocStatus,
                                        [tableSocStatus['client_id'].eq(tableClient['id']),
                                         tableSocStatus['deleted'].eq(0),
                                         '''ClientSocStatus.socStatusClass_id =
                                                    (SELECT ssc.id FROM rbSocStatusClass ssc
                                                     WHERE ssc.flatCode = 'benefits' LIMIT 1)'''])
        queryTable = queryTable.leftJoin(tableSocStatusType,
                                         tableSocStatusType['id'].eq(tableSocStatus['socStatusType_id']))
        queryTable = queryTable.leftJoin(tableDiscountDocument,
                                         tableDiscountDocument['id'].eq(tableSocStatus['document_id']))
        queryTable = queryTable.leftJoin(tableDiscountDocType,
                                         tableDiscountDocType['id'].eq(tableDiscountDocument['documentType_id']))
        cols += [tableSocStatusType['code'].alias('LGOTA'),
                 'CONCAT_WS(\' \', DiscountDocType.name, DiscountDocument.serial, DiscountDocument.number) AS DOCU',
                 tableSocStatus['begDate'].alias('POLU_D'),
                 tableSocStatus['endDate'].alias('ORON_D')
                ]
        cond += [tableSocStatusType['flatCode'].inlist(['010', '011', '012', '020', '030', '040', '050', '060', '061',
                                                        '062', '063', '064', '081', '082', '083', '084', '085', '091',
                                                        '092', '093', '094', '095', '096', '097', '098', '099', '100',
                                                        '101', '102', '111', '112', '113', '120', '121', '122', '123',
                                                        '124', '125', '128', '129', '131', '132', '140', '141', '142',
                                                        '150', '201', '207', '506', '701'])]
        group += [tableSocStatus['id']]
        self.nextPhaseStep(u'Загрузка данных')
        recordList = self.db.getRecordList(queryTable, cols, where=cond, group=group, order=order)
        self.nextPhaseStep(u'Загрузка данных завершена')

        infis = forceStringEx(QtGui.qApp.db.translate('OrgStructure', 'id', self.orgStructureId, 'bookkeeperCode'))

        self.documents.clear()
        self.documents['PRIK'] = dbf.Dbf(os.path.join(QtGui.qApp.getTmpDir(), u'PRIK%s.dbf' % infis), new=True, encoding='cp866')
        self.documents['PRIK'].addField(*self.attachedFields)
        self.documents['LGOTA'] = dbf.Dbf(os.path.join(QtGui.qApp.getTmpDir(), u'LGOTA%s.dbf' % infis), new=True, encoding='cp866')
        self.documents['LGOTA'].addField(*self.discountFields)

        clientIdList = []
        counter = 0
        self.nextPhase(len(recordList), u'Обработка данных')
        for record in recordList:
            clientId = forceInt(record.value('IDSTR'))
            if not clientId in clientIdList:
                rec = self.documents['PRIK'].newRecord()
                counter += 1
                self.fillDbfRecord(rec, record, self.attachedFields)
                rec['ID'] = counter
                rec.store()
                clientIdList.append(clientId)
            if forceStringEx(record.value('LGOTA')):
                rec_lgota = self.documents['LGOTA'].newRecord()
                self.fillDbfRecord(rec_lgota, record, self.discountFields)
                rec_lgota['ID'] = counter
            self.nextPhaseStep()
        for doc in self.documents.values():
            doc.close()
        self.getLogger().info(u'Завершено')
        if self.isTerminated:
            self.onTerminating()
            return False
        return True


class CExportR23AttachClientSMOEngine(CExportR23AttachClientEngine):
    def __init__(self, db, orgStructureId, date, progressInformer=None):
        CExportR23AttachClientEngine.__init__(self, db, orgStructureId, date, progressInformer=progressInformer)
        self.documents = {}

    def process(self):
        self.isTerminated = False
        self.phaseReset(2)
        queryTable, cols, cond, order, group = self.getQueryComponents()
        self.nextPhaseStep(u'Загрузка данных')
        recordList = self.db.getRecordList(queryTable, cols, where=cond, group=group, order=order)
        self.nextPhaseStep(u'Загрузка данных завершена')

        infis = forceStringEx(QtGui.qApp.db.translate('OrgStructure', 'id', self.orgStructureId, 'bookkeeperCode'))

        self.documents.clear()
        counter = 0
        self.nextPhase(len(recordList), u'Обработка данных')
        for record in recordList:
            smo = forceStringEx(record.value('SMO'))
            if not self.documents.has_key(smo):
                self.documents[smo] = dbf.Dbf(os.path.join(QtGui.qApp.getTmpDir(), u'PRIK%s_%s.dbf' % (smo, infis)), new=True, encoding='cp866')
                self.documents[smo].addField(*self.attachedFields)
            dbfDoc = self.documents[smo]
            dbfRow = dbfDoc.newRecord()
            self.fillDbfRecord(dbfRow, record, self.attachedFields)
            counter += 1
            dbfRow['ID'] = counter
            self.nextPhaseStep()
        for doc in self.documents.values():
            doc.close()
        self.getLogger().info(u'Завершено')
        if self.isTerminated:
            self.onTerminating()
            return False
        return True

class CExportDialog(QtGui.QDialog):
    InitState = 0
    ExportState = 1
    SaveState = 2

    def __init__(self, db, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.db = db
        self.pi = CProgressInformer(processEventsFlag=QtCore.QEventLoop.AllEvents)
        self.currentState = self.InitState

        self.setupUi()
        self.engine = CExportR23AttachClientMIACEngine(self.db, self.cmbOrgStructure.value(), self.edtDate.date(), progressInformer=self.pi)
        self.loggerHandler = CLogHandler(self.engine.getLogger(), self)
        self.btnMiac.setChecked(True)
        self.onStateChange()

    def onStateChange(self):
        self.btnNextAction.setText(self.actionNames.get(self.currentState, u'<Error>'))
        self.btnClose.setEnabled(self.currentState != self.ExportState)
        self.grInit.setEnabled(self.currentState == self.InitState)
        self.grExport.setEnabled(self.currentState == self.ExportState)
        self.grSave.setEnabled(self.currentState == self.SaveState)
        self.btnSave.setEnabled(bool(self.engine.documents))
        QtCore.QCoreApplication.processEvents()

    def setupUi(self):
        layout = QtGui.QVBoxLayout()
        self.grInit = QtGui.QGroupBox()
        grLayout = QtGui.QVBoxLayout()
        orgStructureLayout = QtGui.QHBoxLayout()
        self.lblOrgStructure = QtGui.QLabel()
        orgStructureLayout.addWidget(self.lblOrgStructure)
        self.cmbOrgStructure = COrgStructureComboBox(None)
        orgStructureLayout.addWidget(self.cmbOrgStructure)
        grLayout.addLayout(orgStructureLayout)
        dateLayout = QtGui.QHBoxLayout()
        self.lblDate = QtGui.QLabel()
        dateLayout.addWidget(self.lblDate)
        self.edtDate = CDateEdit()
        dateLayout.addWidget(self.edtDate)
        grLayout.addLayout(dateLayout)
        modeExportLayout = QtGui.QHBoxLayout()
        self.btnMiac = QtGui.QRadioButton()
        modeExportLayout.addWidget(self.btnMiac)
        self.btnSMO = QtGui.QRadioButton()
        modeExportLayout.addWidget(self.btnSMO)
        grLayout.addLayout(modeExportLayout)
        self.grInit.setLayout(grLayout)
        layout.addWidget(self.grInit)

        self.grExport = QtGui.QGroupBox()
        grLayout = QtGui.QVBoxLayout()
        self.progressBar = CProgressBar()
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setRange(0, 0)
        self.progressBar.setProgressFormat(u'(%v/%m)')
        self.pi.progressChanged.connect(self.progressBar.setProgress)
        grLayout.addWidget(self.progressBar)
        self.grExport.setLayout(grLayout)
        layout.addWidget(self.grExport)

        self.grSave = QtGui.QGroupBox()
        grLayout = QtGui.QVBoxLayout()
        lineLayout = QtGui.QHBoxLayout()
        self.edtSaveDir = QtGui.QLineEdit(QtCore.QDir.homePath())
        self.edtSaveDir.setReadOnly(True)
        lineLayout.addWidget(self.edtSaveDir)
        self.btnBrowseDir = QtGui.QToolButton()
        self.btnBrowseDir.clicked.connect(self.onBrowseDir)
        lineLayout.addWidget(self.btnBrowseDir)
        grLayout.addLayout(lineLayout)
        lineLayout = QtGui.QHBoxLayout()
        self.btnSave = QtGui.QPushButton()
        self.btnSave.clicked.connect(self.onSaveClicked)
        lineLayout.addWidget(self.btnSave)
        grLayout.addLayout(lineLayout)
        self.grSave.setLayout(grLayout)
        layout.addWidget(self.grSave)

        self.logInfo = QtGui.QTextEdit()
        layout.addWidget(self.logInfo)
        # self.loggerHandler.logged.connect(self.logInfo.append)

        subLayout = QtGui.QHBoxLayout()
        self.btnNextAction = QtGui.QPushButton()
        self.btnNextAction.clicked.connect(self.onNextActionClicked)
        subLayout.addStretch()
        subLayout.addWidget(self.btnNextAction)
        self.btnClose = QtGui.QPushButton()
        self.btnClose.clicked.connect(self.onCloseClicked)
        subLayout.addWidget(self.btnClose)
        layout.addLayout(subLayout)

        self.setLayout(layout)
        self.setMinimumWidth(512)
        self.retranselateUi()

    def retranselateUi(self):
        context = unicode(getClassName(self))
        self.setWindowTitle(forceTr(u'Экспорт прикрипленного населения. Краснодарский край', context))
        self.grInit.setTitle(forceTr(u'Параметры экспорта', context))
        self.lblOrgStructure.setText(forceTr(u'Подразделение', context))
        self.btnMiac.setText(forceTr(u'Экспорт МИАЦ', context))
        self.btnSMO.setText(forceTr(u'Экспорт СМО', context))
        self.lblDate.setText(forceTr(u'Отчетная дата', context))

        self.grExport.setTitle(forceTr(u'Экспотр', context))

        self.grSave.setTitle(forceTr(u'Сохранение результата', context))
        self.btnSave.setText(forceTr(u'Сохранить', context))

        self.actionNames = {self.InitState: forceTr(u'Экспорт', context),
                            self.ExportState: forceTr(u'Прервать', context),
                            self.SaveState: forceTr(u'Повторить', context)}
        self.btnClose.setText(forceTr(u'Закрыть', context))

    @QtCore.pyqtSlot()
    def onNextActionClicked(self):
        if self.currentState == self.InitState:
            self.currentState = self.ExportState
            try:
                result = self.engine.process()
            except:
                self.currentState = self.InitState
                raise
            self.currentState = self.SaveState if result else self.InitState
        elif self.currentState == self.ExportState:
            self.engine.terminate()
        elif self.currentState == self.SaveState:
            self.currentState = self.InitState
        self.onStateChange()

    def canClose(self):
        return not ((self.engine.documents) or QtGui.QMessageBox.warning(self,
                                                                             u'Внимание!',
                                                                             u'Остались несохраненные файлы выгрузок\n'
                                                                             u'которые будут утеряны.\n'
                                                                             u'Вы уверены, что хотите покинуть менеджер экспорта?\n',
                                                                             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                                             QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes)


    def closeEvent(self, event):
        if self.canClose():
            event.accept()
        else:
            event.ignore()

    def done(self, result):
        if self.canClose():
            super(CExportDialog, self).done(result)

    @QtCore.pyqtSlot()
    def onCloseClicked(self):
        self.accept()

    @QtCore.pyqtSlot()
    def onBrowseDir(self):
        saveDir = forceStringEx(QtGui.QFileDialog.getExistingDirectory(self,
                                                         u'Укажите директорию для сохранения файлов выгрузки',
                                                         self.edtSaveDir.text()))
        if os.path.isdir(saveDir):
            self.edtSaveDir.setText(saveDir)

    @QtCore.pyqtSlot()
    def onSaveClicked(self):
        self.btnClose.setEnabled(False)
        self.engine.save(self.edtSaveDir.text())
        self.onStateChange()

    @QtCore.pyqtSlot(bool)
    def on_btnMiac_toggled(self, checked):
        if not checked:
            self.engine = CExportR23AttachClientSMOEngine(self.db, self.cmbOrgStructure.value(), self.edtDate.date(), progressInformer=self.pi)
            self.loggerHandler = CLogHandler(self.engine.logger(), self)
        else:
            self.engine = CExportR23AttachClientMIACEngine(self.db, self.cmbOrgStructure.value(), self.edtDate.date(), progressInformer=self.pi)
            self.loggerHandler = CLogHandler(self.engine.logger(), self)


class CApplication(QtGui.QApplication):
    def __init__(self, argv):
        QtGui.QApplication.__init__(self, argv)

    def currentOrgId(self):
        return 229917

    def currentOrgStructureId(self):
        return QtCore.QVariant()

    def highlightRedDate(self):
        return True

    def getTmpDir(self, suffix=''):
        return unicode(tempfile.mkdtemp('', 'vista-med_%s_' % suffix), locale.getpreferredencoding())


def main():
    import sys
    from library.database import connectDataBaseByInfo
    app = CApplication(sys.argv)
    QtGui.qApp = app
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

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

    w = CExportDialog(QtGui.qApp.db)
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

