# -*- coding: utf-8 -*-
from collections import defaultdict
from PyQt4 import QtCore, QtGui
from Events.Utils import CFinanceType
from Exchange.Ui_ImportEISOMS_SMP import Ui_ImportSMP
from library.Utils import forceStringEx, forceInt, forceRef, forceDate, toVariant, databaseFormatSex, forceString
from library.dbfpy.dbf import Dbf


def ImportEISOMS_SMP(widget):
    dialog = CImportEISOMS_SMP(widget)
    dialog.exec_()

class CImportEISOMS_SMP(QtGui.QDialog, Ui_ImportSMP):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.btnImport.setEnabled(False)
        self.buttonBox.clicked.connect(self.on_buttonBox_clicked)
        self.cmbPerson.setValue(self.cmbPerson._model.getId(1))
        self.setWindowTitle(u'Импорт СМП')

        db = QtGui.qApp.db
        self.sceneId = forceRef(db.translateEx('rbScene', 'code', 4, 'id')) #skkachaev: 4 — Потому что так написано в F110
        self.visitTypeId = forceRef(db.translateEx('rbVisitType', 'code', u'СМП', 'id')) #skkachaev: В справочнике для типа визитов должна быть строка с кодом "СМП",
        if not self.visitTypeId:
            query = db.query('SELECT id FROM rbVisitType LIMIT 1')
            if query.next(): self.visitTypeId = forceRef(query.record().value('id'))
        query = QtGui.qApp.db.query('SELECT EventType.id FROM EventType INNER JOIN rbMedicalAidType ON EventType.medicalAidType_id = rbMedicalAidType.id WHERE rbMedicalAidType.code = \'%s\'' % '4') #skkachaev: Потому что так надо в Питере
        self.eventTypeId = forceRef(query.record().value('id')) if query.next() else None
        self.policyTypeId = forceRef(db.translateEx('rbPolicyType', 'code', '1', 'id')) #skkachaev: 1 — Потому что jene так сказал
        self.personId = None
        self.specialityId = None
        self.clientId = None
        self.diagnosisTypeId = forceRef(db.translateEx('rbDiagnosisType', 'code', '2', 'id')) # основной
        self.characterId = forceRef(db.translateEx('rbDiseaseCharacter', 'code', '2', 'id')) # хроническое известное
        self.i = 0
        self.visits = 0
        self.events = 0
        self.clients = 0

    def getPersonId(self, ID_DOC):
        db = QtGui.qApp.db

        if not ID_DOC or ID_DOC == '':
            return self.personId

        if self.cmbMod.currentIndex() == 0:
            return ID_DOC
        elif self.cmbMod.currentIndex() == 1:
            return forceRef(db.translateEx('Person', 'code', ID_DOC, 'id'))
        elif self.cmbMod.currentIndex() == 2:
            return forceRef(db.translateEx('Person', 'regionalCode', ID_DOC, 'id'))
        elif self.cmbMod.currentIndex() == 3:
            return forceRef(db.translateEx('Person', 'federalCode', ID_DOC, 'id'))

    def importSMP(self):
        self.personId = self.cmbPerson.getValue()
        self.i = 0
        self.visits = 0
        self.events = 0
        self.clients = 0
        self.specialityId = QtGui.qApp.db.translateEx('Person', 'id', self.personId, 'speciality_id')
        try:
            self.btnImport.setEnabled(False)
            fileName = forceStringEx(self.edtFileName.text())
            if not fileName:
                self.logBrowser.append(u'Необходимо выбрать файл!')
                self.logBrowser.update()
                return
            dbf = Dbf(fileName, readOnly=True
                      , encoding='cp866'
                      )
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(dbf.recordCount)
            self.progressBar.setValue(0)

            self.logBrowser.append(u'Иморт начат: %s' % (QtCore.QTime.currentTime().toString('hh:mm:ss')))
            self.logBrowser.update()
            self.progressBar.setText(u'Считывание данных из файла')
            mapSMP = defaultdict(dict)
            accItemId = 0
            for recordDBF in dbf:
                self.progressBar.step()
                # accItemId = recordDBF['ACCITEM_ID'] В предоставленном файле не было
                accItemId += 1
                mapSMP[accItemId]['lastName'] = recordDBF['SURNAME']
                mapSMP[accItemId]['firstName'] = recordDBF['NAME1']
                mapSMP[accItemId]['patrName'] = recordDBF['NAME2']
                mapSMP[accItemId]['birthDate'] = recordDBF['BIRTHDAY']
                mapSMP[accItemId]['sex'] = recordDBF['SEX']

                mapSMP[accItemId]['policySerial'] = recordDBF['POLIS_S'] if recordDBF['POLIS_S'] != '-' else ''
                mapSMP[accItemId]['policyNumber'] = recordDBF['POLIS_N'] if recordDBF['POLIS_N'] != '-' else ''
                # mapSMP[accItemId]['policyInsurer'] = recordDBF['POLIS_W'] В предоставленном файле не было
                mapSMP[accItemId]['policyInsurer'] = recordDBF['PAYER']
                mapSMP[accItemId]['documentType'] = recordDBF['TYPEDOC']
                mapSMP[accItemId]['docSeries1'] = recordDBF['SER1'] if recordDBF['SER1'] != '-' else ''
                mapSMP[accItemId]['docSeries2'] = recordDBF['SER2'] if recordDBF['SER2'] != '-' else ''
                mapSMP[accItemId]['documentNumber'] = recordDBF['NPASP'] if recordDBF['NPASP'] != '-' else ''
                # mapSMP[accItemId]['snils'] = recordDBF['SNILS'] В предоставленном файле не было
                mapSMP[accItemId]['tariffType'] = recordDBF['SERV_ID']
                mapSMP[accItemId]['emergStreet'] = recordDBF['STREET']
                mapSMP[accItemId]['emergStreetType'] = recordDBF['STREETYPE']
                mapSMP[accItemId]['emergArea'] = recordDBF['AREA']
                mapSMP[accItemId]['emergHouse'] = recordDBF['HOUSE']
                mapSMP[accItemId]['emergBuild'] = recordDBF['KORP']
                mapSMP[accItemId]['emergFlat'] = recordDBF['FLAT']
                # mapSMP[accItemId]['emergLongAddr'] = recordDBF['LONGADDR'] В предоставленном файле не было
                mapSMP[accItemId]['serviceInfisCode'] = recordDBF['PROFILE']
                mapSMP[accItemId]['begDate'] = recordDBF['DATEIN']
                mapSMP[accItemId]['endDate'] = recordDBF['DATEOUT']
                #TODO:Зависит от isHospitalization
                #TODO:Где, isHospitalization
                mapSMP[accItemId]['amount'] = recordDBF['AMOUNT']
                mapSMP[accItemId]['diagnosis'] = recordDBF['DIAGNOSIS']
                #rbSpeciality Person
                mapSMP[accItemId]['specialityCode'] = recordDBF['ID_PRVS']
                #TODO:rbDiagnosticResult.regionalCode нужен Diagnostic нужен Event
                mapSMP[accItemId]['idExitus'] = recordDBF['ID_EXITUS']
                mapSMP[accItemId]['externalId'] = recordDBF['ILLHISTORY']
                # mapSMP[accItemId]['aidProfileCode'] = recordDBF['ID_PRMP']
                # mapSMP[accItemId]['eventAidProfileCode'] = recordDBF['ID_PRMP_C']
                mapSMP[accItemId]['mkb_pc'] = recordDBF['DIAG_C']
                mapSMP[accItemId]['eventResultCode'] = recordDBF['QRESULT']
                mapSMP[accItemId]['eventSpecialityCode'] = recordDBF['ID_PRVS_C']
                # mapSMP[accItemId]['tmpAmount'] = recordDBF['ID_ED_PAY'] #Уже есть amount
                # mapSMP[accItemId]['aidKindCode'] = recordDBF['ID_VMP']
                mapSMP[accItemId]['personId'] = self.getPersonId(recordDBF['ID_DOC'])
                #OrgStructure.infisCode от person_id
                mapSMP[accItemId]['personFormat'] = recordDBF['ID_DEPT']

                mapSMP[accItemId]['eisLpuId_C'] = recordDBF['ID_DOC_C']
                mapSMP[accItemId]['personFormat_C'] = recordDBF['ID_DEPT_C']
                # mapSMP[accItemId]['accountId'] = recordDBF['ACC_ID'] В предоставленном файле не было
                # mapSMP[accItemId]['clientId'] = recordDBF['CLIENT_ID'] В предоставленном файле не было

                mapSMP[accItemId]['goal'] = recordDBF['ID_GOAL_C']
                mapSMP[accItemId]['currentOrgMiac'] = recordDBF['ID_LPU']
                mapSMP[accItemId]['nborn'] = recordDBF['N_BORN']

                mapSMP[accItemId]['series'] = mapSMP[accItemId]['docSeries1'] + ' ' + mapSMP[accItemId]['docSeries2']
        except ValueError:
            self.logBrowser.append(u'<b><font color=red>ОШИБКА:</b>'
                                   u' неверное значение строки "%d" в DBF.' % \
                                   self.progressBar.value())
            self.logBrowser.update()
            self.btnImport.setEnabled(True)
            raise
        except Exception as ex:
            self.logBrowser.append(u'<b><font color=red>ОШИБКА:</b> ' + ex.message)
            self.logBrowser.update()
            self.btnImport.setEnabled(True)
            raise

        self.progressBar.setText(u'Занесение данных в базу')
        self.logBrowser.append(u'Занесение данных в базу')
        self.logBrowser.update()

        QtGui.qApp.db.transaction()
        for rec in mapSMP.itervalues():
            QtGui.qApp.processEvents()
            self.addVisit(rec)
            self.i += 1
        # QtGui.qApp.db.rollback()
        QtGui.qApp.db.commit()

        self.progressBar.setText(u'Импорт завершен!')
        self.logBrowser.append(u'Импорт завершен!')
        self.logBrowser.append(u'Количество занесённых полей Visit: {0:d}\nКоличество занесённых полей Event: {1:d}\nКоличество занесённых полей Client: {2:d}'
                               .format(self.visits, self.events, self.clients))
        self.logBrowser.update()
        self.btnImport.setEnabled(True)

    def addVisit(self, record):
        db = QtGui.qApp.db
        try:
            visit = db.table('Visit').newRecord()
            eventId = self.addIfNotExistEvent(record)
            visit.setValue('event_id', eventId)
            self.addDiagnostic(record, eventId)
            self.addIfNotExistEmergencyCall(record, eventId)
            visit.setValue('date', toVariant(forceDate(record['begDate'])))
            visit.setValue('visitType_id', self.visitTypeId)
            visit.setValue('person_id', forceRef(record['personId']))
            visit.setValue('scene_id', self.sceneId)
            visit.setValue('finance_id', CFinanceType.getId(CFinanceType.CMI))
            visit.setValue('service_id', self.getServiceId(record))
            self.visits += 1
            return forceRef(db.insertRecord(db.table('Visit'), visit))
        except Exception as ex:
            self.logBrowser.append(u'<b><font color=red>ОШИБКА:</b> '
                                   + u'\nСтрока: {0:d} ФИО: {1:s} \n'.format(self.i, forceString(record['lastName']) + u' '
                                                                            + forceString(record['firstName']) + u' '
                                                                            + forceString(record['patrName']) + u' '
                                                                            + forceDate(record['birthDate']).toString(QtCore.Qt.ISODate))
                                   + ex.message + u'\n')
            self.btnImport.setEnabled(True)
            db.rollback()
            raise

    def addDiagnostic(self, record, eventId):
        db = QtGui.qApp.db
        diagnosis = db.table('Diagnosis').newRecord()
        diagnosis.setValue('client_id', self.clientId)
        diagnosis.setValue('diagnosisType_id', self.diagnosisTypeId)
        diagnosis.setValue('character_id', self.characterId)
        diagnosis.setValue('MKB', record['diagnosis'])
        diagnosis.setValue('person_id', forceRef(record['personId']))
        diagnosisId = forceRef(db.insertRecord(db.table('Diagnosis'), diagnosis))
        diagnostic = db.table('Diagnostic').newRecord()
        diagnostic.setValue('event_id', eventId)
        diagnostic.setValue('diagnosis_id', diagnosisId)
        diagnostic.setValue('diagnosisType_id', self.diagnosisTypeId)
        diagnostic.setValue('character_id', self.characterId)
        diagnostic.setValue('speciality_id', self.specialityId)
        diagnostic.setValue('person_id', self.personId)
        DRName = None
        if record['idExitus'] == 26:
            DRName = u'Улучшение'
        elif record['idExitus'] == 27:
            DRName = u'Без эффекта'
        elif record['idExitus'] == 28:
            DRName = u'Ухудшение'
        else:
            raise Exception(u'Неправильный код ID_EXITUS')
        query = db.query(u'''
            SELECT id
            FROM rbDiagnosticResult
            WHERE regionalCode = '{0:d}' AND name = '{1:s}'
        '''.format(record['idExitus'], DRName))
        if query.next(): diagnostic.setValue('result_id', forceRef(query.record().value('id')))
        db.insertRecord('Diagnostic', diagnostic)

    @staticmethod
    def getServiceId(record):
        return forceRef(QtGui.qApp.db.translateEx('rbService', 'infis', record['serviceInfisCode'], 'id'))


    @staticmethod
    def addIfNotExistEmergencyCall(record, eventId):
        db = QtGui.qApp.db
        emCId = forceRef(db.translateEx('EmergencyCall', 'event_id', eventId, 'id'))
        if emCId: return emCId

        emergencyCall = db.table('EmergencyCall').newRecord()
        emergencyCall.setValue('event_id', eventId)
        emergencyCall.setValue('finishServiceDate', toVariant(forceDate(record['begDate'])))
        emergencyCall.setValue('numberCardCall', record['externalId'])
        emergencyCall.setValue('birth', 0 if not record['nborn'] else 1)
        #Пока не делаем
        # emergencyCall.setValue('KLADRStreetCode', )
        # emergencyCall.setValue('house', record['emergHouse'])
        # emergencyCall.setValue('build', record['emergBuild'])
        # emergencyCall.setValue('flat', record['emergFlat'])
        return forceRef(db.insertRecord(db.table('EmergencyCall'), emergencyCall))

    #res: Event.id
    def addIfNotExistEvent(self, record):
        db = QtGui.qApp.db
        id = forceRef(db.translateEx('Event', 'externalId', record['externalId'], 'id'))
        if id:
            self.clientId = forceRef(db.translateEx('Event', 'id', id, 'client_id'))
            return id
        else:
            event = db.table('Event').newRecord()
            event.setValue('externalId', record['externalId'])
            event.setValue('eventType_id', self.eventTypeId)
            event.setValue('org_id', self.getOrganisationId(record))
            self.clientId = self.addIfNotExistClient(record)
            event.setValue('client_id', self.clientId)
            # event.setValue('contract_id', ) #Нет
            event.setValue('setDate', toVariant(forceDate(record['begDate'])))
            event.setValue('execDate', toVariant(forceDate(record['endDate'])))
            event.setValue('execPerson_id', forceRef(record['personId']))
            event.setValue('createPerson_id', forceRef(record['personId']))
            event.setValue('result_id', self.getEventResultId(record))
            event.setValue('littleStranger_id', self.addEventLittleStranger(record))
            event.setValue('goal_id', self.getGoalId(record))
            self.events += 1
            return forceRef(db.insertRecord(db.table('Event'), event))

    @staticmethod
    def getGoalId(record):
        return forceRef(QtGui.qApp.db.translateEx('rbEventGoal', 'regionalCode', record['goal'], 'id'))

    @staticmethod
    def getOrganisationId(record):
        return forceInt(QtGui.qApp.db.translateEx('Organisation', 'miacCode', record['currentOrgMiac'], 'id'))

    # Мы смотрим сначала на имя, фамилию, отчество и дату рождения
    # Если людей с такими парамитрами у нас в базе несколько, то пытаемся найти по полису
    # (Если полис есть в выгрузке)
    # Если полиса нет в выгрузке или нам вернулось пустое количество людей, но не у всех из них в принципе есть полис
    # То мы пытаемся аналогичным полису образом отфильтровать по типу и номеру документа
    # Если у нас и с документом не сложилось (и полиса и документа нет в выгрузке или у нас в базе у людей нет полиса и документа)
    # То берём с наименьшим id
    def getClientId(self, record):
        db = QtGui.qApp.db
        query = db.query(u'''
            SELECT Client.id
            , ClientPolicy.id AS policy
            , ClientDocument.id AS document
            FROM Client
            LEFT JOIN ClientPolicy ON Client.id = ClientPolicy.client_id
            LEFT JOIN ClientDocument ON Client.id = ClientDocument.client_id
            WHERE Client.firstName = '{0:s}' AND Client.lastName = '{1:s}' AND IF('{2:s}' != '', Client.patrName = '{2:s}', TRUE)
            AND Client.birthDate = '{3:s}' AND Client.deleted = 0
            GROUP BY Client.id
        '''.format(record['firstName'], record['lastName'], record['patrName'], forceDate(record['birthDate']).toString(QtCore.Qt.ISODate)))
        ids = []
        chkDoc = True
        chkPolicy = True
        while query.next():
            ids.append(forceRef(query.record().value('id')))
            chkDoc = chkDoc and (query.record().value('document') is not None)
            chkPolicy = chkPolicy and (query.record().value('policy') is not None)

        if len(ids) > 1:
            query = db.query(u'''
                SELECT Client.id
                FROM Client
                INNER JOIN ClientPolicy ON ClientPolicy.client_id = Client.id
                WHERE Client.id in {0:s} AND ClientPolicy.policyType_id = {1:d} AND ClientPolicy.number = '{2:s}' AND Client.deleted = 0
                GROUP BY Client.id
                ORDER BY Client.id
            '''.format(     ids.__str__().replace('[', '(').replace(']', ')')
                        ,   self.policyTypeId
                        ,   record['policyNumber']))

            newIds = []
            while query.next(): newIds.append(forceRef(query.record().value('id')))
            if len(newIds) == 1:
                return newIds[0]
            elif len(newIds) == 0:
                if chkPolicy: # У всех полисы были заполнены. Ни один не совпал, значит такого человека у нас нет
                    return None
                else: # Полисы были заполнены не у всех, а человек не найден. Возможно, он был среди тех, у кого полисы не заполнены
                    query = db.query(u'''
                        SELECT Client.id
                        FROM Client
                        INNER JOIN ClientDocument ON Client.id = ClientDocument.client_id
                        WHERE Client.id in {0:s} AND ClientDocument.documentType_id = {1:d} AND ClientDocument.number = '{2:s}' AND Client.deleted = 0
                        GROUP BY Client.id
                        ORDER BY Client.id
                    '''.format(     ids.__str__().replace('[', '(').replace(']', ')')
                                ,   record['documentType']
                                ,   record['documentNumber']))
                    newIds = []
                    while query.next(): newIds.append(forceRef(query.record().value('id')))

                    if len(newIds) == 1:
                        return newIds[0]
                    elif len(newIds) == 0:
                        if chkDoc: # У всех документы были заполнены. Ни один не совпал, значит, такого человека у нас нет
                            return None
                        else: # Документы заполнены не у всех, человек не найден. Возможно, он был среди тех, у кого документы не заполнены
                            self.logBrowser.append(u'<b><font color=orange>ПРЕДУПРЕЖДЕНИЕ:</b> '
                                   + u'\nСтрока: {0:d} ФИО: {1:s}\n'.format(self.i, record['lastName'] + ' '
                                                                            + record['firstName'] + ' '
                                                                            + record['patrName'] + ' '
                                                                            + forceDate(record['birthDate']).toString(QtCore.Qt.ISODate))
                                   + u'Человек дублируется в картотеке. id: {0:d}\n'.format(newIds[0]))
                            self.logBrowser.update()
                            return newIds[0] #Возвращаем с наименьшим ID
                    else: # У нескольких человек одинаковые документы.
                        self.logBrowser.append(u'<b><font color=orange>ПРЕДУПРЕЖДЕНИЕ:</b> '
                                   + u'\nСтрока: {0:d} ФИО: {1:s}\n'.format(self.i, record['lastName'] + ' '
                                                                            + record['firstName'] + ' '
                                                                            + record['patrName'] + ' '
                                                                            + forceDate(record['birthDate']).toString(QtCore.Qt.ISODate))
                                   + u'У нескольких человек одинаковые документы\n')
                        self.logBrowser.update()
                        return newIds[0]
            else: # У нескольких человек одинаковые полисы.
                self.logBrowser.append(u'<b><font color=orange>ПРЕДУПРЕЖДЕНИЕ:</b> '
                                   + u'\nСтрока: {0:d} ФИО: {1:s}\n'.format(self.i, record['lastName'] + ' '
                                                                            + record['firstName'] + ' '
                                                                            + record['patrName'] + ' '
                                                                            + forceDate(record['birthDate']).toString(QtCore.Qt.ISODate))
                                   + u'У нескольких человек одинаковые полисы\n')
                self.logBrowser.update()
                return newIds[0]

        elif len(ids) == 0: return None
        else: return ids[0]

    #res: Client.id
    def addIfNotExistClient(self, record):
        db = QtGui.qApp.db
        id = self.getClientId(record)
        if id: return id

        client = db.table('Client').newRecord()
        client.setValue('lastName', record['lastName'])
        client.setValue('firstName', record['firstName'])
        client.setValue('patrName', record['patrName'])
        client.setValue('birthDate', toVariant(forceDate(record['birthDate'])))
        client.setValue('sex', databaseFormatSex(record['sex']))
        clientId = forceRef(db.insertRecord(db.table('Client'), client))
        self.addClientPolicy(record, clientId)
        self.addClientDocument(record, clientId)
        self.clients += 1
        return clientId

    @staticmethod
    #res: ClientDocument.id
    def addClientDocument(record, clientId):
        if record['documentType'] != '' and record['series'] != 0 and record['series'] != '' and record['documentNumber'] != '':
            db = QtGui.qApp.db
            clientDocument = db.table('ClientDocument').newRecord()
            clientDocument.setValue('client_id', clientId)
            clientDocument.setValue('documentType_id', record['documentType'])
            clientDocument.setValue('serial', record['series'])
            clientDocument.setValue('number', record['documentNumber'])
            return forceRef(db.insertRecord(db.table('ClientDocument'), clientDocument))
        else: return None

    #res: ClientPolicy.id
    def addClientPolicy(self, record, clientId):
        db = QtGui.qApp.db
        if record['policySerial'] != '' and record['policyNumber'] != 0 and record['policyNumber'] != '':
            clientPolicy = db.table('ClientPolicy').newRecord()
            clientPolicy.setValue('client_id', clientId)
            clientPolicy.setValue('insurer_id', db.translateEx('Organisation', 'infisCode', record['policyInsurer'], 'id'))
            clientPolicy.setValue('policyType_id', self.policyTypeId)
            clientPolicy.setValue('serial', record['policySerial'])
            clientPolicy.setValue('number', record['policyNumber'])
            return forceRef(db.insertRecord(db.table('ClientPolicy'), clientPolicy))
        else: return None

    @staticmethod
    def getEventResultId(record):
        return forceRef(QtGui.qApp.db.translateEx('rbResult', 'regionalCode', record['eventResultCode'], 'id'))

    # noinspection PyUnusedLocal
    @staticmethod
    #Новорождённый
    #res: Event_LittleStranger.id
    def addEventLittleStranger(record):
        return None

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы DBF (*.dbf)'
        )
        if fileName != '':
            self.edtFileName.setText(fileName)
            if self.sceneId and self.visitTypeId and self.eventTypeId and self.policyTypeId:
                self.btnImport.setEnabled(True)
            else:
                self.logBrowser.append(u'База настроена неправильно!')
                self.logBrowser.update()

    @QtCore.pyqtSlot()
    def on_btnImport_clicked(self):
        self.importSMP()

    @QtCore.pyqtSlot()
    def on_buttonBox_clicked(self):
        if QtGui.qApp.db._openTransactionsCount != 0: #TODO:skkachaev:Нужен нормальный способ проверить это
            QtGui.qApp.db.rollback()
        self.close()