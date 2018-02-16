# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

##### Передача данных из Виста-Мед флюорографу. #####

import os.path
import shutil

from library.database  import *
from library.Utils     import *
from Exchange.Utils import CExportHelperMixin, prepareRefBooksCacheById

from Ui_ExportR67XML_VMPage1 import Ui_ExportPage1
from Ui_ExportR67XML_VMPage2 import Ui_ExportPage2

# FIXME: GUI-вариант не доделан, а скорее всего и не нужен. Либо допилить, либо выкинуть.

def exportR78_p48_FLG(widget):
    wizard = CExportWizard(widget)
    wizard.exec_()

def createJobTicketsQuery(db, date):
    if not db:
        db = QtGui.qApp.db
    tableAP = db.table('ActionProperty').alias('ap')
    stmt = u"""
    SELECT
      jt.idx AS jtIdx, jt.datetime AS jtTime, c.id AS clientId
    FROM Job_Ticket jt
      INNER JOIN Job j
        ON j.id = jt.master_id AND jt.status = 0
      INNER JOIN rbJobType jt1 ON jt1.code = '4-4' AND jt1.id= j.jobType_id
      INNER JOIN ActionProperty_Job_Ticket apjt
        ON apjt.value = jt.id
      INNER JOIN ActionProperty ap ON ap.id = apjt.id
      INNER JOIN Action a ON a.id = ap.action_id AND a.deleted = 0
      INNER JOIN Event ON Event.id = a.event_id AND Event.deleted = 0
      INNER JOIN Client c ON c.id = Event.client_id AND c.deleted = 0
    WHERE %s
    """
    cond = tableAP['modifyDatetime'].gt(forceDateTime(date)) if date else '1'
    return db.query(stmt % cond)

def createRegDataQuery(db, idList):
    if not db:
        db = QtGui.qApp.db

    tableClient = db.table('Client')

    stmt = u'''
        SELECT
            Client.id                   AS clientId,
            Client.lastName             AS clientLastName,
            Client.firstName            AS clientFirstName,
            Client.patrName             AS clientPatrName,
            Client.birthDate            AS clientBirthDate,
            Client.sex                  AS clientSex,
            Client.notes                AS clientNote,
            ClientIdentification.identifier,

            ClientRegAddress.freeInput  AS freeInput,
            ClientRegAddress.address_id AS addressId,
            RegAddress.flat             AS flat,
            RegAddressHouse.corpus      AS corpus,
            RegAddressHouse.number      AS house,
            kladr.KLADR.name            AS city,
            kladr.STREET.name           AS street,
            kladr.SOCRBASE.SOCRNAME     AS streetSokr

        FROM Client
        LEFT JOIN ClientIdentification ON ClientIdentification.client_id = Client.id AND
                  ClientIdentification.id = (SELECT MAX(CI.id)
                                     FROM ClientIdentification AS CI
                                     INNER JOIN rbAccountingSystem ON rbAccountingSystem.id = CI.accountingSystem_id
                                                                    AND rbAccountingSystem.code = 'FLG'
                                     WHERE CI.client_id = Client.id AND CI.deleted = 0)
        LEFT JOIN ClientAddress ClientRegAddress ON ClientRegAddress.client_id = Client.id AND
                  ClientRegAddress.id = (SELECT MAX(CRA.id)
                                     FROM   ClientAddress AS CRA
                                     WHERE  CRA.type = 0 AND CRA.client_id = Client.id AND CRA.deleted=0)
        LEFT JOIN Address   RegAddress ON RegAddress.id = ClientRegAddress.address_id
        LEFT JOIN AddressHouse RegAddressHouse ON RegAddressHouse.id = RegAddress.house_id
        LEFT JOIN kladr.KLADR ON kladr.KLADR.CODE = RegAddressHouse.KLADRCode
        LEFT JOIN kladr.STREET ON kladr.STREET.CODE = RegAddressHouse.KLADRStreetCode
        LEFT JOIN kladr.SOCRBASE ON kladr.SOCRBASE.SCNAME = kladr.STREET.SOCR AND kladr.SOCRBASE.LEVEL = 5
        WHERE %s
    '''

    cond = tableClient['id'].inlist(idList if idList else [])
    return db.query(stmt % cond)

def processJobTickets(query, parent=None):
    result = {}
    isGui = parent and hasattr(parent, 'aborted')

    while query.next():
        if isGui:
            QtGui.qApp.processEvents()
            if parent.aborted:
                return {}
        record = query.record()
        idx = forceString(record.value('jtIdx'))
        jtTime = forceDate(record.value('jtTime'))
        clientId = forceRef(record.value('clientId'))
        clientEntry = result.setdefault(clientId, {})
        jtList = clientEntry.setdefault('jtList', [])
        jtList.append((idx, jtTime))
    return result

class CExportWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportPage1(self)
        self.page2 = CExportPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер обмена с флюорографом')
        self.tmpDir = ''
        self.xmlLocalFileName = ''
        self.fileName = ''

    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('R67XML')
        return self.tmpDir


    def getFullXmlFileName(self):
        self.xmlLocalFileName = os.path.join(self.tmpDir, self.getTxtFileName())
        return self.xmlLocalFileName

    def getTxtFileName(self):
        if not self.fileName:
            self.fileName = u'HM_%s.xml' % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz'))
        return self.fileName

    def cleanup(self):
        if self.tmpDir:
            QtGui.qApp.removeTmpDir(self.tmpDir)
            self.tmpDir = ''


    def exec_(self):
        QtGui.QWizard.exec_(self)
        self.cleanup()


class CExportPage1(QtGui.QWizardPage, Ui_ExportPage1, CExportHelperMixin):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        CExportHelperMixin.__init__(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')

        self.setTitle(u'Экспорт для Смоленской области')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "экспорт"')

        self.setExportMode(False)
        self.aborted = False
        self.done = False
        self._cache = smartDict()
        self.parent = parent
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)

    def setExportMode(self, flag):
        self.btnCancel.setEnabled(flag)
        self.btnExport.setEnabled(not flag)
        self.btnExport.setEnabled(not flag)
        self.chkExportEvents.setEnabled(not flag)


    def log(self, str, forceLog = True):
        self.logBrowser.append(str)
        self.logBrowser.update()

    def prepareRefBooks(self):
        self._cache = prepareRefBooksCacheById()

    def prepareToExport(self):
        self.done = False
        self.aborted = False
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        output = self.createXML()
        self.progressBar.reset()
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.progressBar.setText(u'Получение информации о номерках...')
        QtGui.qApp.processEvents()
        query = self.createQuery()
        self.progressBar.setText(u'Предварительная обработка данных...')
        QtGui.qApp.processEvents()
        jobTickets = self.preProcessQuery(query)
        self.progressBar.setText(u'Получение информации о пациентах...')
        QtGui.qApp.processEvents()
        regDataQuery = self.createRegDataQuery(jobTickets.keys())

        self.progressBar.setMaximum(max(query.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        return output, jobTickets, regDataQuery


    def export(self):
        (result, rc) = QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted or not result:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))

# *****************************************************************************************

    def getTxtFileName(self):
        lpuCode = forceString(QtGui.qApp.db.translate(
            'Organisation', 'id', QtGui.qApp.currentOrgId() , 'infisCode'))
        return forceString(lpuCode + u'.TXT')

    def createTxt(self):
        txt = QFile(os.path.join(self.parent.getTmpDir(), self.getTxtFileName()))
        txt.open(QIODevice.WriteOnly | QIODevice.Text)
        txtStream =  QTextStream(txt)
        txtStream.setCodec('CP866')
        return txt,  txtStream

    def createQuery(self):
        date = self.edtStartDate.date()
        return createJobTicketsQuery(QtGui.qApp.db, date)

    def createRegDataQuery(self, idList):
        return createRegDataQuery(QtGui.qApp.db, idList)
# *****************************************************************************************

    def preProcessQuery(self, query):
        return processJobTickets(query)

    def exportInt(self):
        out, jobTickets, regDataQuery = self.prepareToExport()
        jobTicketsOut = CJobTicketsStreamWriter(self)
        jobTicketsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
        jobTicketsOut.writeFileHeader(out, self.parent.getFullXmlFileName(), QtCore.QDate.currentDate())
        if regDataQuery.size() > 0:
            while regDataQuery.next():
                QtGui.qApp.processEvents()
                if self.aborted:
                    break
                self.progressBar.step()
                record = regDataQuery.record()
                clientId = forceRef(record.value('clientId'))
                clientExternalId = forceString(record.value('identifier'))
                jobTickets[clientId]['externalId'] = clientExternalId
                jobTicketsOut.writeRecord(record)

            jobTicketsOut.closeDemography()
            jobTicketsOut.writeRequests(jobTickets)

            jobTicketsOut.writeFileFooter()
            out.close()
        else:
            self.log(u'Нечего выгружать.')
            self.progressBar.step()

# *****************************************************************************************

    def createXML(self):
        outFile = QtCore.QFile(self.parent.getFullXmlFileName())
        outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)
        return outFile

# *****************************************************************************************

    def isComplete(self):
        return self.done


    def abort(self):
        self.aborted = True


    @QtCore.pyqtSignature('')
    def on_btnExport_clicked(self):
        self.export()


    @QtCore.pyqtSignature('')
    def on_btnCancel_clicked(self):
        self.abort()

# *****************************************************************************************

# *****************************************************************************************


    def validatePage(self):
        return True

class CExportPage2(QtGui.QWizardPage, Ui_ExportPage2):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setTitle(u'Экспорт для Смоленской области')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "финиш"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'R67XMLExportDir', homePath))
        self.edtDir.setText(exportDir)


    def isComplete(self):
        return self.pathIsValid


    def validatePage(self):

        srcFullName = self.parent.getFullXmlFileName()
        dst = os.path.join(forceStringEx(self.edtDir.text()),
                                            self.parent.getTxtFileName())
        success, result = QtGui.qApp.call(self, shutil.move, (srcFullName, dst))

        QtGui.qApp.preferences.appPrefs['R67XMLExportDir'] = toVariant(self.edtDir.text())

        return success


    @QtCore.pyqtSignature('QString')
    def on_edtDir_textChanged(self):
        dir = forceStringEx(self.edtDir.text())
        pathIsValid = os.path.isdir(dir)
        if self.pathIsValid != pathIsValid:
            self.pathIsValid = pathIsValid
            self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSignature('')
    def on_btnSelectDir_clicked(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self,
                u'Выберите директорию для сохранения файла выгрузки в ОМС Смоленской области',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
             self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))


class CJobTicketsStreamWriter(QXmlStreamWriter):
    # persZglvFields = {'VERSION': True, 'DATA': True, 'FILENAME' : True, 'FILENAME1' : True}
    # persFields = {'ID_PAC': True, 'FAM': True, 'IM': True, 'OT': True, 'W': True, 'DR': True, 'FAM_P': False, 'IM_P': False,
    #                     'OT_P': False, 'W_P': False, 'DR_P': False, 'MR': False, 'DOCTYPE': False, 'DOCSER': False, 'DOCNUM': False, 'SNILS': False,
    #                     'OKATOG': False, 'OKATOP': False, 'COMENTP': False, 'COMENTZ': False}
    # groupMap = {'ZGLV': persZglvFields, 'PERS': persFields}

    def __init__(self, parent):
        QXmlStreamWriter.__init__(self)
        self.parent = parent
        self.setAutoFormatting(True)
        self.xmlErrorsList = []

    def writeStartElement(self, str):
        self.curGroupName = str
        return QXmlStreamWriter.writeStartElement(self, str)


    def writeEndElement(self):
        self.curGroupName = ''
        return QXmlStreamWriter.writeEndElement(self)

    def writeRecord(self, record):
        u"""
        Запись в XML-файл регистрационных данных пациента (ФИО, пол, дата рождения, адрес, идентификаторы
        """

        clientId = forceString(record.value('clientId'))
        clientExternalId = forceString(record.value('identifier'))

        birthDate = forceDate(record.value('clientBirthDate')).toString(Qt.ISODate)
        sex = forceInt(record.value('clientSex'))
        sexVal = '0' if sex == 1 else '1' if sex == 2 else '2'
        addressId = forceRef(record.value('addressId'))
        freeInput = forceString(record.value('freeInput'))
        street = forceString(record.value('street'))

        self.writeStartElement('pacient')

        self.writeTextElement('idi', clientExternalId)                                  # Внутренний ID из флг
        self.writeTextElement('ido', clientId)                                          # ID пациента в МИС
        self.writeTextElement('lastName', forceString(record.value('clientLastName')))  # Фамилия
        self.writeTextElement('firstName', forceString(record.value('clientFirstName')))# Имя
        self.writeTextElement('midlName', forceString(record.value('clientPatrName')))  # Отчество
        self.writeTextElement('dob', birthDate)                                         # Дата рождения (YYYY-MM-DD)
        self.writeTextElement('sex', sexVal)                                            # Пол (0 - м, 1 - ж)
        self.writeTextElement('pregnancyWeek', '')                                      # Неделя беременности

        self.writeStartElement('address')

        self.writeTextElement('sity', forceString(record.value('city')))                # Город
        self.writeTextElement('street', street if addressId else freeInput)            # Улица
        self.writeTextElement('streetSokr', forceString(record.value('streetSokr')))    # Тип улицы
        self.writeTextElement('house', forceString(record.value('house')))              # Номер дома
        self.writeTextElement('houseLetter', forceString(record.value('corpus')))       # Корпус
        self.writeTextElement('appartment', forceString(record.value('flat')))          # Квартира

        self.writeEndElement()  # address
        self.writeTextElement('note', forceString(record.value('clientNote')))          # Комментарий
        self.writeEndElement()  # pacient

    def writeRequests(self, jobTickets):
        u"""
        Экспорт номерков, переданных в словаре jobTickets
        """
        for clientId, clientData in jobTickets.items():
            externalId = clientData.get('externalId', '')
            for jt in clientData.get('jtList', []):
                self.writeStartElement('request')
                self.writeTextElement('idi', externalId)         # Внутренний ID из флг
                self.writeTextElement('ido', str(clientId))      # ID пациента из МИС
                self.writeTextElement('queueIndex', jt[0])       # Порядок выполнения или номер талона
                self.writeTextElement('queueDate', jt[1].toString(Qt.ISODate))
                self.writeTextElement('priority', '0')           # Приоритет задания, 0 - обычное, 1 - срочное



    def writeFileHeader(self,  device, fileName, accDate):
        self.setDevice(device)
        self.writeStartDocument()
        self.writeStartElement('doc')
        self.writeStartElement('demography')

    def closeDemography(self):
        self.writeEndElement() # demography
        self.writeStartElement('requests')

    def writeFileFooter(self):
        self.writeEndElement() # requests
        self.writeEndElement() # doc
        self.writeEndDocument()


# *****************************************************************************************

def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Export assigned job tickets and reg data of corresponding clients from specified database..')
    parser.add_argument('-u', dest='user', default='dbuser')
    parser.add_argument('-P', dest='password')
    parser.add_argument('-t', dest='datetime', default=None)
    parser.add_argument('-a', dest='host', default='127.0.0.1')
    parser.add_argument('-p', dest='port', type=int, default='3306')
    parser.add_argument('-d', dest='database', default='s11')
    parser.add_argument('-D', dest='dir', default=os.getcwd())
    args = vars(parser.parse_args(sys.argv[1:]))

    if not args['user']:
        print 'Error: you should specify user name'
        sys.exit(-1)
    if not args['password']:
        print 'Error: you should specify password'
        sys.exit(-2)

    app = QtCore.QCoreApplication(sys.argv)
    connectionInfo = {
                          'driverName' : 'MYSQL',
                          'host' : args['host'],
                          'port' : args['port'],
                          'database' : args['database'],
                          'user' : args['user'],
                          'password' : args['password'],
                          'connectionName' : 'FLG',
                          'compressData' : True,
                          'afterConnectFunc' : None
                    }

    db = connectDataBaseByInfo(connectionInfo)
    QtGui.qApp.db = db
    dt = args['datetime']
    dt = QDateTime.fromString(dt, 'yyyy-MM-ddTHH:mm:ss') if dt else None # QDateTime.currentDateTime().addSecs(-60)
    if not (dt is None or dt.isValid()):
        print 'Error: incorrect base datetime.'
        sys.exit(-3)

    query = createJobTicketsQuery(db, dt)
    jobTickets = processJobTickets(query)
    regDataQuery = createRegDataQuery(db, jobTickets.keys())

    if regDataQuery.size() > 0:
        fileName = u'FLG_%s.xml' % (QtCore.QDateTime.currentDateTime().toString('yyMMddThhmmss.zzz'))
        outFile = QtCore.QFile(os.path.join(forceStringEx(args['dir']), fileName))
        outFile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text)

        jobTicketsOut = CJobTicketsStreamWriter(None)
        jobTicketsOut.setCodec(QtCore.QTextCodec.codecForName('cp1251'))
        jobTicketsOut.writeFileHeader(outFile, None, QtCore.QDate.currentDate())
        while regDataQuery.next():
            record = regDataQuery.record()
            clientId = forceRef(record.value('clientId'))
            clientExternalId = forceString(record.value('identifier'))
            jobTickets[clientId]['externalId'] = clientExternalId
            jobTicketsOut.writeRecord(record)

        jobTicketsOut.closeDemography()
        jobTicketsOut.writeRequests(jobTickets)

        jobTicketsOut.writeFileFooter()
        outFile.close()

if __name__ == '__main__':
    main()