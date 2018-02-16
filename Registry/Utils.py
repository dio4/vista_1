# -*- coding: utf-8 -*-
import datetime
import re
from PyQt4 import QtCore, QtGui, QtSql

from Events.Utils import CFinanceType, CPayStatus, extractLonePayStaus, getEventDiagnosis
from Exchange.R23.attach.Utils import CAttachSentToTFOMS
from KLADR.KLADRModel import getCityName, getDistrictName, getKladrTreeModel, getOKATO, getStreetName
from Orgs.PersonInfo import CPersonInfo
from Orgs.Utils import CAttachTypeInfo, CDetachmentReasonInfo, CNet, COrgInfo, COrgStructureInfo, CSexAgeConstraint, \
    getOrgStructureDescendants, getOrgStructureNetId, getOrganisationShortName
from RefBooks.Codes import attDeath
from RefBooks.EnumFields import PersonAcademicDegree
from RefBooks.QuotaType import getQuotaTypeClassNameList
from Users.Rights import urDeleteEventWithJobTicket, urDeleteEventWithTissue, urQueueCheckVPolicy
from library.DbEntityCache import CDbEntityCache
from library.PrintInfo import CDateInfo, CDateTimeInfo, CInfo, CInfoContext, CInfoList, CRBInfo
from library.PrintTemplates import compileAndExecTemplate, getFirstPrintTemplate, getTemplate
from library.Utils import LazySmartDict, calcAge, calcAgeTuple, forceBool, forceDate, forceDateTime, forceInt, forceRef, \
    forceString, forceStringEx, formatAgeTuple, formatDate, formatName, \
    formatNameInt, formatSNILS, formatSex, formatShortNameInt, smartDict, toVariant
from library.constants import dateLeftInfinity, dateRightInfinity


def setFocusToWidget(widget, row=None, column=None):
    if widget is not None:
        if widget.hasFocus():
            widget.clearFocus()
        widget.setFocus(QtCore.Qt.ShortcutFocusReason)
        widget.update()
        if isinstance(widget, QtGui.QTableView) and isinstance(row, int) and isinstance(column, int) and widget.model():
            widget.setCurrentIndex(widget.model().index(row, column))


def checkTempInvalidNumber(parent, text):
    if len(text):
        import re
        pattern = re.compile("^\d{12}$")
        if not pattern.search(text):
            QtGui.QMessageBox.critical(
                parent,
                u"Внимание!",
                u"Ошибка при вводе номера больничного листа.\n Номер должен содержать только 12 цифр.",
                QtGui.QMessageBox.Ok,
                QtGui.QMessageBox.Ok
            )
            return False
    return True


def clientIdToText(clientId):
    text = ''
    if clientId:
        db = QtGui.qApp.db
        tableClient = db.table('Client')
        tableDocument = db.table('ClientDocument')
        tableAddress = db.table('ClientAddress')
        tableRBDocumentType = db.table('rbDocumentType')
        cols = [
            tableClient['id'],
            tableClient['lastName'],
            tableClient['firstName'],
            tableClient['patrName'],
            tableClient['birthDate'],
            tableClient['sex'],
            tableDocument['serial'],
            tableDocument['number'],
            tableDocument['date'],
            tableDocument['origin'],
            tableRBDocumentType['name']
        ]
        cols.append(
            u'''IF(ClientAddress.type = 0, concat(_utf8'Адрес регистрации: ', ClientAddress.freeInput), _utf8'') AS regAddress, IF(ClientAddress.type = 1, concat(_utf8'Адрес проживания: ', ClientAddress.freeInput), _utf8'') AS logAddress''')
        queryTable = tableClient.leftJoin(tableAddress, tableClient['id'].eq(tableAddress['client_id']))
        queryTable = queryTable.leftJoin(tableDocument, 'ClientDocument.id = getClientDocumentID(Client.id)')
        queryTable = queryTable.leftJoin(
            tableRBDocumentType, tableDocument['documentType_id'].eq(tableRBDocumentType['id']))
        cond = [tableClient['id'].eq(clientId), tableClient['deleted'].eq(0)]
        cond.append(db.joinOr([tableDocument['id'].isNull(), tableDocument['deleted'].eq(0)]))
        cond.append(db.joinOr([tableAddress['id'].isNull(), tableAddress['deleted'].eq(0)]))
        record = db.getRecordEx(queryTable, cols, cond)
        if record:
            clientId = forceString(record.value('id'))
            lastName = forceString(record.value('lastName'))
            firstName = forceString(record.value('firstName'))
            patrName = forceString(record.value('patrName'))
            birthDate = forceString(record.value('birthDate'))
            sex = formatSex(forceInt(record.value('sex')))
            regAddress = forceString(record.value('regAddress'))
            logAddress = forceString(record.value('logAddress'))
            docName = forceString(record.value('name'))
            serialDoc = forceString(record.value('serial'))
            numberDoc = forceString(record.value('number'))
            originDoc = forceString(record.value('origin'))
            dateDoc = forceString(record.value('date'))
            FIO = ' '.join([lastName, firstName, patrName])
            sexStr = ': '.join([u'пол', sex])
            docSerialNumb = ' '.join([u' серия', serialDoc])
            docSerialNumb += ' '.join([u' номер', numberDoc])
            infoDoc = ': '.join([docName, docSerialNumb])
            infoDocOrg = ': '.join([u' выдан', originDoc])
            infoDocDate = ' '.join([dateDoc])
            infoDoc += ' '.join([infoDocOrg, infoDocDate])
            text = ', '.join(
                [field for field in [FIO, clientId, birthDate, sexStr, regAddress, logAddress, infoDoc] if field])
    else:
        text = ''
    return text


def readOMSBarCode(PORT=u'COM3'):
    sixBitEncoding = {
        0: u' ', 1: u'.', 2: u'-', 3: u'"', 4: u'0', 5: u'1', 6: u'2', 7: u'3',
        8: u'4', 9: u'5', 10: u'6', 11: u'7', 12: u'8', 13: u'9', 14: u'А', 15: u'Б',
        16: u'В', 17: u'Г', 18: u'Д', 19: u'Е', 20: u'Ё', 21: u'Ж', 22: u'З', 23: u'И',
        24: u'Й', 25: u'К', 26: u'Л', 27: u'М', 28: u'Н', 29: u'О', 30: u'П', 31: u'Р',
        32: u'С', 33: u'Т', 34: u'У', 35: u'Ф', 36: u'Х', 37: u'Ц', 38: u'Ч', 39: u'Ш',
        40: u'Щ', 41: u'Ь', 42: u'Ъ', 43: u'Ы', 44: u'Э', 45: u'Ю', 46: u'Я', 47: u' ',
        48: u' ', 49: u' ', 50: u' ', 51: u' ', 52: u' ', 53: u' ', 54: u' ', 55: u' ',
        56: u' ', 57: u' ', 58: u' ', 59: u' ', 60: u' ', 61: u' ', 62: u' ', 63: u'|',
    }

    result = {
        'lastName': u'',
        'firstName': u'',
        'patrName': u'',
        'sex': u'',
        'bDate': QtCore.QDate(),
        'number': u'',
        'endDate': QtCore.QDate(),
        'errorMessage': u'Неизвестная ошибка считывания полиса ОМС'
    }

    try:
        import serial

        ser = serial.Serial()
        ser.baudrate = 9600
        # for windows
        ser = serial.Serial(PORT, 19200, timeout=1)

        message = bytearray('')
        i = 0
        readOk = False
        while not readOk and i < 60:
            if ser.inWaiting() > 0:
                while ser.inWaiting() > 0:
                    message.append(ser.read())
                polisN = 0
                for i in message[1:9]:
                    polisN = (polisN << 8) | i

                name = u''
                pos = 0
                rest = 0
                for i in message[9:60]:
                    posMod = pos % 3
                    if posMod == 0:
                        name += sixBitEncoding[(i >> 2)]
                        rest = i & 0x03
                    elif posMod == 1:
                        name += sixBitEncoding[(rest << 4) | (i >> 4)]
                        rest = i & 0x0F
                    elif posMod == 2:
                        name += sixBitEncoding[(rest << 2) | (i >> 6)]
                        name += sixBitEncoding[(i & 0x3F)]
                        rest = 0
                    pos += 1

                sex = message[60]

                bDays = 0  # birthDate
                for i in message[61:63]:
                    bDays = (bDays << 8) | i

                dateBeg = datetime.date(1900, 1, 1)
                bDate = dateBeg + datetime.timedelta(days=bDays)

                pDays = 0
                for i in message[63:65]:
                    pDays = (pDays << 8) | i

                polisEndDate = dateBeg + datetime.timedelta(days=pDays)

                ecp = u''
                for i in message[65:131]:
                    ecp += u'%02X' % i

                readOk = True

            QtCore.QThread.msleep(250)
            i += 1

        if readOk:
            nameSplit = name.split('|')
            result['lastName'] = nameSplit[0].strip()
            result['firstName'] = nameSplit[1].strip()
            result['patrName'] = nameSplit[2].strip()
            result['sex'] = sex
            result['bDate'] = QtCore.QDate(bDate)  # birth date
            result['number'] = forceString(polisN)
            # duration (срок действия)
            result['endDate'] = QtCore.QDate(polisEndDate) if datetime.date(1900, 1,
                                                                            1) != polisEndDate else QtCore.QDate()
            result['errorMessage'] = u''
        else:
            result['errorMessage'] = u'Не удалось получить данные со считывателя полиса ОМС'

    finally:
        return result


def createActionBarCode(action_id, amount):
    from library.pdf417 import pdf417image
    return pdf417image(str(action_id) + '+' + str(789))


if __name__ == '__main__':
    f = createActionBarCode(94142805, 1)
    f.save('E:/test1.png')
    f = createActionBarCode(94142804, 1)
    f.save('E:/test2.png')


class CBarCodeReaderThread(QtCore.QThread):
    class CBarCodeWorker(QtCore.QObject):
        read = QtCore.pyqtSignal(dict)
        error = QtCore.pyqtSignal(str)

        def __init__(self, port=u'COM3'):
            QtCore.QObject.__init__(self)
            self.port = port
            self.close = False

        def readActionBarCode(self):
            result = {
                'action_id': None,
                'amount': None,
                'errorMessage': u'Неизвестная ошибка считывания полиса ОМС'
            }

            try:
                import serial
                import re

                if hasattr(QtGui.qApp, 'barcodeSerialPort'):
                    QtGui.qApp.barcodeSerialPort.close()

                QtGui.qApp.barcodeSerialPort = serial.Serial()
                QtGui.qApp.barcodeSerialPort.baudrate = 9600
                # for windows
                QtGui.qApp.barcodeSerialPort = serial.Serial(self.port, 19200, timeout=1)
                # TODO: skkachaev: self.close всегда False
                while not self.close:
                    message = ''
                    i = 0
                    # readOk = False
                    # while not readOk and i < 60 and not self.close:
                    while i < 60 and not self.close:
                        # if ser.inWaiting() > 0:
                        #    message = ser.read_all()
                        if QtGui.qApp.barcodeSerialPort.inWaiting() > 0:
                            while QtGui.qApp.barcodeSerialPort.inWaiting() > 0:
                                message += QtGui.qApp.barcodeSerialPort.read()
                        # readOk = True
                        QtCore.QThread.msleep(50)
                        i += 1
                    # readOk = True
                    if message:
                        try:
                            result['action_id'] = re.findall('(\d+)\s', message)[0]
                            result['amount'] = re.findall('\s(.*)', message)[0]
                            result['errorMessage'] = u''
                            self.read.emit(result)
                        except Exception as e:
                            result['errorMessage'] = u'Не удалось получить данные со считывателя штрих-кодов.'
                            self.error.emit(result['errorMessage'] + u'\n Сканер прочел: \"%s\"' % message + '\n' + e.message)

            except Exception as e:
                self.error.emit(
                    u'СКАНЕР ШТРИХ-КОДОВ\n\n' +
                    u'Ошибка при попытке подключения к сканеру\nОбратитесь к вашему системному администратору\n\n' +
                    u'Текст ошибки:\n' + e.message)
            finally:
                QtGui.qApp.barcodeSerialPort.close()

    def __init__(self, port=u'COM3'):
        QtCore.QThread.__init__(self)
        self.barCodeReader = self.CBarCodeWorker(port)
        self.barCodeReader.moveToThread(self)
        self.busyByEvent = False

    def run(self):
        self.barCodeReader.readActionBarCode()


# TODO: need cache
def personIdToText(personId, withAcademicDegree=False):
    text = ''
    if isinstance(personId, QtCore.QVariant) and personId.isNull():
        return text
    if personId:
        db = QtGui.qApp.db
        tablePerson = db.table('Person')
        tableSpeciality = db.table('rbSpeciality')
        viewPerson = db.table('vrbPerson')

        table = viewPerson.innerJoin(tablePerson, tablePerson['id'].eq(viewPerson['id']))
        table = table.leftJoin(tableSpeciality, tableSpeciality['id'].eq(viewPerson['speciality_id']))
        cols = [
            viewPerson['name'].alias('personName'),
            tableSpeciality['name'].alias('specialityName'),
            tablePerson['academicDegree'].alias('academicDegree')
        ]
        cond = [
            viewPerson['id'].eq(personId)
        ]
        rec = db.getRecordEx(table, cols, cond)
        if rec:
            parts = [
                forceStringEx(rec.value('personName')),
                forceStringEx(rec.value('specialityName'))
            ]
            if withAcademicDegree:
                parts.append(PersonAcademicDegree.getName(forceInt(rec.value('academicDegree'))))
            text = ', '.join(filter(bool, parts))
    return text


def codeToTextPriceList(id):
    text = ''
    if id:
        db = QtGui.qApp.db
        tableContract = db.table('Contract')
        tableRBFinance = db.table('rbFinance')
        cols = [tableRBFinance['code'],
                tableRBFinance['name'],
                tableContract['grouping'],
                tableContract['resolution'],
                tableContract['number'],
                tableContract['date'],
                tableContract['begDate'],
                tableContract['endDate']
                ]
        cond = [tableContract['id'].eq(id),
                tableContract['deleted'].eq(0)
                ]
        table = tableContract.leftJoin(tableRBFinance, tableRBFinance['id'].eq(tableContract['finance_id']))
        record = db.getRecordEx(table, cols, cond)
        if record:
            code = forceString(record.value('code'))
            name = forceString(record.value('name'))
            grouping = forceString(record.value('grouping'))
            resolution = forceString(record.value('resolution'))
            number = forceString(record.value('number'))
            date = forceString(record.value('date'))
            begDate = forceString(record.value('begDate'))
            endDate = forceString(record.value('endDate'))
            text = ', '.join([field for field in [code + u'-' + name, u'Группа ' + grouping, u'Основание ' + resolution,
                                                  u'Номер ' + number, date, begDate + u'-' + endDate] if field])
    else:
        text = ''
    return text


def codeToTextForBlank(code, docTypeActions=False):
    text = ''
    if code:
        db = QtGui.qApp.db
        if docTypeActions:
            tableRBBlankTempInvalids = db.table('rbBlankActions')
            tableBlankTempInvalidParty = db.table('BlankActions_Party')
            tableBlankTempInvalidMoving = db.table('BlankActions_Moving')
        else:
            tableRBBlankTempInvalids = db.table('rbBlankTempInvalids')
            tableBlankTempInvalidParty = db.table('BlankTempInvalid_Party')
            tableBlankTempInvalidMoving = db.table('BlankTempInvalid_Moving')
        cols = [tableBlankTempInvalidParty['serial']]
        cond = [tableBlankTempInvalidParty['deleted'].eq(0),
                tableBlankTempInvalidMoving['deleted'].eq(0),
                tableBlankTempInvalidMoving['id'].eq(code)
                ]
        queryTable = tableBlankTempInvalidParty.innerJoin(tableBlankTempInvalidMoving,
                                                          tableBlankTempInvalidMoving['blankParty_id'].eq(
                                                              tableBlankTempInvalidParty['id']))
        records = db.getRecordEx(queryTable, cols, cond)
        text = forceString(records.value(0)) if records else u''
    return text


# atronah: воистину бредовая функция или я не могу понять, почему вместо простого order by id надо использовать две таблицы (они могут быть еще и разными)
def selectLatestRecordStmt(tableName, clientId, filter='', deleted=False):
    if type(tableName) == tuple:
        tableName1, tableName2 = tableName
    else:
        tableName1 = tableName
        tableName2 = tableName
    pos = tableName2.find('AS Tmp')
    if pos < 0:
        tableName2 = tableName2 + ' AS Tmp'

    if filter:
        filter = ' AND (' + filter + ')'
    s = u'SELECT * FROM %s AS Main WHERE Main.client_id = \'%d\' AND Main.id = (SELECT MAX(Tmp.id) FROM %s WHERE Tmp.client_id=%d AND Tmp.deleted=0 %s)'
    if not deleted:
        s = u'SELECT * FROM %s AS Main WHERE Main.client_id = \'%d\' AND Main.id = (SELECT MAX(Tmp.id) FROM %s WHERE Tmp.client_id=%d %s)'
    return s % (tableName1, clientId, tableName2, clientId, filter)


def selectLatestRecord(tableName, clientId, filter='', deleted=False):
    if clientId:
        stmt = selectLatestRecordStmt(tableName, clientId, filter, deleted)
        query = QtSql.QSqlQuery(QtGui.qApp.db.db)
        query.exec_(stmt)
        if query.next():
            return query.record()

    return None


def getClientRemarkTypeIdByFlatCode(flatCode, addIfNotExistsWithName=u''):
    db = QtGui.qApp.db
    table = db.table('rbClientRemarkType')
    typeId = forceRef(db.translate(table, 'flatCode', flatCode, 'id'))
    if typeId is None and addIfNotExistsWithName:
        newRecord = table.newRecord()
        newRecord.setValue('flatCode', toVariant(flatCode))
        newRecord.setValue('name', toVariant(addIfNotExistsWithName))
        typeId = db.insertRecord(table, newRecord)
    return typeId


def getClientAddress(id, addrType):
    return selectLatestRecord('ClientAddress', id, 'type=\'%d\'' % addrType)


def getClientAddressEx(id):
    addr = getClientAddress(id, 1)
    if not addr:
        addr = getClientAddress(id, 0)
    return addr


def getAddress(addressId, freeInput=None):
    result = smartDict()
    result.KLADRCode = ''
    result.KLADRStreetCode = ''
    result.number = ''
    result.corpus = ''
    result.flat = ''
    result.freeInput = forceString(freeInput) if freeInput else ''
    result.SOCR = ''
    result.Infis = ''

    db = QtGui.qApp.db
    houseId = None
    if addressId:
        recAddress = db.getRecord('Address', 'house_id, flat', addressId)
        if recAddress:
            houseId = forceRef(recAddress.value('house_id'))
            result.flat = forceString(recAddress.value('flat'))
    if houseId:
        recHouse = db.getRecord('AddressHouse', 'KLADRCode, KLADRStreetCode, number, corpus', houseId)
        if recHouse:
            result.KLADRCode = forceString(recHouse.value('KLADRCode'))
            result.KLADRStreetCode = forceString(recHouse.value('KLADRStreetCode'))
            result.number = forceString(recHouse.value('number'))
            result.corpus = forceString(recHouse.value('corpus'))
            result.SOCR = getSOCRForKLADRCode(result.KLADRCode)
            result.Infis = getInfisForKLADRCode(result.KLADRCode)
    return result


def getInfisForKLADRCode(KLADRCode):
    if KLADRCode:
        return forceString(QtGui.qApp.db.translate('kladr.KLADR', 'CODE', KLADRCode, 'infis', idFieldName='CODE'))
    return ''


def getRegionForKLADRCode(KLADRCode):
    if KLADRCode:
        return forceString(
            QtGui.qApp.db.translate('kladr.KLADR', 'CODE', '%s00000000000' % KLADRCode[:2], 'NAME', idFieldName='CODE'))
    return ''


def getSOCRForKLADRCode(KLADRCode):
    if KLADRCode:
        return forceString(QtGui.qApp.db.translate('kladr.KLADR', 'CODE', KLADRCode, 'SOCR', idFieldName='CODE'))
    return ''


def isVillagerAddress(KLADRCode):
    if not KLADRCode:
        return False

    db = QtGui.qApp.db
    tableKLADR = db.table('kladr.KLADR')
    tableSOCRBASE = db.table('kladr.SOCRBASE')

    table = tableKLADR.innerJoin(tableSOCRBASE, tableSOCRBASE['SCNAME'].eq(tableKLADR['SOCR']))
    cond = [
        tableKLADR['CODE'].eq(KLADRCode),
        tableSOCRBASE['KOD_T_ST'].inlist(['103', '301', '405'])  # город
    ]
    return db.getRecordEx(table, tableSOCRBASE['KOD_T_ST'], cond) is None


def getInfisForStreetKLADRCode(KLADRStreetCode):
    if KLADRStreetCode:
        return forceString(QtGui.qApp.db.translate('kladr.STREET', 'CODE', KLADRStreetCode, 'infis'))
    return ''


def getDocumentTypeIdListByGroupList(groupList):
    db = QtGui.qApp.db
    tableDocumentType = db.table('rbDocumentType')
    tableDocumentTypeGroup = db.table('rbDocumentTypeGroup')
    queryTable = tableDocumentType.leftJoin(tableDocumentTypeGroup,
                                            tableDocumentTypeGroup['id'].eq(tableDocumentType['group_id']))
    cond = tableDocumentTypeGroup['code'].inlist(groupList) if groupList else '0'
    return db.getIdList(table=queryTable,
                        idCol=tableDocumentType['id'],
                        where=cond)


def formatAddressInt(address):
    if address.KLADRCode:
        parts = []
        parts.append(getCityName(address.KLADRCode))
        if address.KLADRStreetCode:
            parts.append(getStreetName(address.KLADRStreetCode))
        if address.number:
            parts.append(u'д. ' + address.number)
        if address.corpus:
            parts.append(u'к. ' + address.corpus)
        if address.flat:
            parts.append(u'кв. ' + address.flat)
        return ', '.join(parts)
    if address.freeInput:
        # Убрано 150812 по просьбе Иры#return '[' + address.freeInput + ']'
        return address.freeInput
    return ''


def formatAddress(addressId, freeInput=None):
    address = getAddress(addressId, freeInput)
    return formatAddressInt(address)


def findHouseId(address):
    db = QtGui.qApp.db
    tblHouse = db.table('AddressHouse')
    filter = [tblHouse['KLADRCode'].eq(address['KLADRCode']),
              tblHouse['KLADRStreetCode'].eq(address['KLADRStreetCode']),
              tblHouse['number'].eq(address['number']),
              tblHouse['corpus'].eq(address['corpus']),
              tblHouse['deleted'].eq(0)]
    houseIdList = db.getIdList(tblHouse, 'id', filter)
    return houseIdList[0] if houseIdList else None


def getHouseId(address):
    houseId = findHouseId(address)
    if not houseId:
        db = QtGui.qApp.db
        tblHouse = db.table('AddressHouse')
        recHouse = db.record('AddressHouse')
        recHouse.setValue('KLADRCode', toVariant(address['KLADRCode']))
        recHouse.setValue('KLADRStreetCode', toVariant(address['KLADRStreetCode']))
        recHouse.setValue('number', toVariant(address['number']))
        recHouse.setValue('corpus', toVariant(address['corpus']))
        houseId = db.insertRecord(tblHouse, recHouse)
    return houseId


def findAddressIdEx(address):
    db = QtGui.qApp.db
    houseId = findHouseId(address)
    if houseId:
        tblAddress = db.table('Address')
        filter = [tblAddress['house_id'].eq(houseId),
                  tblAddress['flat'].eq(address['flat']),
                  tblAddress['deleted'].eq(0)]
        addressIdList = db.getIdList(tblAddress, 'id', filter)
        addressId = addressIdList[0] if addressIdList else None
        return houseId, addressId
    else:
        return None, None


def findAddressId(address):
    return findAddressIdEx(address)[1]


def getAddressId(address):
    houseId, addressId = findAddressIdEx(address)
    if not addressId:
        db = QtGui.qApp.db
        houseId = houseId if houseId else getHouseId(address)
        recAddress = db.record('Address')
        recAddress.setValue('house_id', toVariant(houseId))
        recAddress.setValue('flat', toVariant(address['flat']))
        tblAddress = db.table('Address')
        addressId = db.insertRecord(tblAddress, recAddress)
    return addressId


def getClientDocument(clientId):
    filter = '''Tmp.documentType_id IN (SELECT rbDocumentType.id FROM rbDocumentType LEFT JOIN rbDocumentTypeGroup ON rbDocumentTypeGroup.id=rbDocumentType.group_id WHERE rbDocumentTypeGroup.code = '1') AND deleted = 0'''
    return selectLatestRecord('ClientDocument', clientId, filter)


def formatDocument(documentTypeId, serial, number):
    result = ''
    db = QtGui.qApp.db
    documentTypeTable = db.table('rbDocumentType')
    documentTypeRecord = db.getRecord(documentTypeTable, 'name', forceInt(documentTypeId))
    if documentTypeRecord:
        result = forceString(documentTypeRecord.value(0))
    result = result + ' ' + forceString(serial) + ' ' + forceString(number)
    return result.strip()


def formatDateRange(begDate, endDate):
    result = begDate + ' - ' + endDate
    return result


def getClientPolicyList(clientId, isCompulsory, date=None):
    u""" Список полисов пациента в хронологическом порядке """
    db = QtGui.qApp.db
    tablePolicy = db.table('ClientPolicy')
    tablePolicyType = db.table('rbPolicyType')
    tableOrganisation = db.table('Organisation')

    queryTable = tablePolicy.leftJoin(tablePolicyType, tablePolicyType['id'].eq(tablePolicy['policyType_id']))
    queryTable = queryTable.leftJoin(tableOrganisation, tableOrganisation['id'].eq(tablePolicy['insurer_id']))

    cond = [
        tablePolicy['client_id'].eq(clientId),
        tablePolicy['deleted'].eq(0)
    ]

    if isCompulsory:
        cond.append(db.joinOr([tablePolicyType['name'].like(u'ОМС%%'),
                               tablePolicyType['id'].isNull()]))
    else:
        cond.append(tablePolicyType['name'].notlike(u'ОМС%%'))

    if isinstance(date, QtCore.QDateTime):
        date = date.date()
    if isinstance(date, QtCore.QDate):
        cond.extend([
            db.joinOr([tablePolicy['begDate'].isNull(),
                       tablePolicy['begDate'].le(date)]),
            db.joinOr([tablePolicy['endDate'].isNull(),
                       tablePolicy['endDate'].ge(date)])
        ])

    cols = [
        tablePolicy['*'],
        tableOrganisation['compulsoryServiceStop'],
        tableOrganisation['voluntaryServiceStop']
    ]
    order = [
        db.ifnull(tablePolicy['endDate'], dateRightInfinity),
        db.ifnull(tablePolicy['begDate'], dateLeftInfinity),
        tablePolicy['id']
    ]

    return db.getRecordList(queryTable, cols=cols, where=cond, order=order)


def getClientPolicyByEventId(eventId, date=None):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tablePolicy = db.table('ClientPolicy')
    tablePolicyType = db.table('rbPolicyType')
    tableOrganisation = db.table('Organisation')

    cond = [
        tableEvent['id'].eq(eventId),
        tablePolicy['deleted'].eq(0)
    ]

    if isinstance(date, QtCore.QDateTime):
        date = date.date()

    # if isinstance(date, QtCore.QDate):
    #     cond.append(db.joinOr([tablePolicy['begDate'].isNull(), tablePolicy['begDate'].le(date)]))
    #     cond.append(db.joinOr([tablePolicy['endDate'].isNull(), tablePolicy['endDate'].ge(date)]))

    queryTable = tableEvent.leftJoin(tablePolicy, tablePolicy['id'].eq(tableEvent['clientPolicy_id']))
    queryTable = queryTable.leftJoin(tablePolicyType, tablePolicyType['id'].eq(tablePolicy['policyType_id']))
    queryTable = queryTable.leftJoin(tableOrganisation, tableOrganisation['id'].eq(tablePolicy['insurer_id']))

    cols = [
        tablePolicy['*'],
        tableOrganisation['compulsoryServiceStop'],
        tableOrganisation['voluntaryServiceStop']
    ]

    return db.getRecordEx(queryTable, cols=cols, where=cond)


def getClientPolicyById(policyId, date=None):
    db = QtGui.qApp.db
    tablePolicy = db.table('ClientPolicy')
    tablePolicyType = db.table('rbPolicyType')
    tableOrganisation = db.table('Organisation')

    cond = [tablePolicy['id'].eq(policyId),
            tablePolicy['deleted'].eq(0)]

    if isinstance(date, QtCore.QDateTime):
        date = date.date()
    if isinstance(date, QtCore.QDate):
        cond.append(db.joinOr([tablePolicy['begDate'].isNull(),
                               tablePolicy['begDate'].le(date)]))
        cond.append(db.joinOr([tablePolicy['endDate'].isNull(),
                               tablePolicy['endDate'].ge(date)]))

    queryTable = tablePolicy.leftJoin(tablePolicyType, tablePolicyType['id'].eq(tablePolicy['policyType_id']))
    queryTable = queryTable.leftJoin(tableOrganisation, tableOrganisation['id'].eq(tablePolicy['insurer_id']))

    cols = [tablePolicy['*'],
            tableOrganisation['compulsoryServiceStop'],
            tableOrganisation['voluntaryServiceStop']
            ]

    return db.getRecordEx(queryTable, cols=cols, where=cond)


def getClientCompulsoryPolicy(clientId, date=None):
    policyRecordList = getClientPolicyList(clientId, True, date)
    return policyRecordList[-1] if policyRecordList else None


def getClientVoluntaryPolicy(clientId, date=None):
    policyRecordList = getClientPolicyList(clientId, False, date)
    return policyRecordList[-1] if policyRecordList else None


def getClientVoluntaryPolicyList(clientId, date=None):
    return getClientPolicyList(clientId, False, date)


getClientPolicy = getClientCompulsoryPolicy


def getAreaPolicy(insureId):
    defaultArea = QtGui.qApp.defaultKLADR()
    db = QtGui.qApp.db
    table = db.table('Organisation')
    cols = [table['area']]
    cond = [table['id'].eq(insureId),
            table['deleted'].eq(0)]
    stmt = db.selectStmt(table, cols, where=cond)
    query = db.query(stmt)
    if query.first():
        record = query.record()
        area = forceString(record.value('area'))
        if area and area != defaultArea:
            stmt = u'SELECT NAME, SOCR FROM kladr.KLADR WHERE CODE = %s ' % (area)
            if query.exec_(stmt) and query.first():
                record = query.record()
                name = forceString(record.value(0))
                socr = forceString(record.value(1))
                return name + ' ' + socr
    return None


def formatPolicy(insurerId, serial, number, begDate=None, endDate=None, name=None, note=None, policyKindId=None,
                 dischargeDate=None):
    policyKindId = forceRef(policyKindId)
    result = (('[' + CPolicyKindCache.getCode(policyKindId) + ']') if policyKindId  else '') + u': '
    result += forceString(serial) + ' ' + forceString(number)
    area = getAreaPolicy(insurerId)
    insurerId = forceRef(insurerId)
    nameParts = []
    if insurerId:
        nameParts.append(getOrganisationShortName(insurerId))
    name = forceStringEx(name)
    if name:
        nameParts.append(name)
    insurerName = ' '.join(nameParts)
    if area:
        result = result + u' (' + area + u') '
    if insurerName:
        result = result + u' выдан ' + insurerName
    dateRange = ''
    if begDate and not begDate.isNull():
        dateRange = u'с ' + forceString(begDate)
    if endDate and not endDate.isNull():
        dateRange += u' по ' + forceString(endDate)
    if dateRange:
        result += u' действителен ' + dateRange.strip()
    return result


def getClientWork(clientId):
    return selectLatestRecord('ClientWork', clientId)


def getAllClientAttaches(clientId):
    attaches = []
    table = QtGui.qApp.db.table('ClientAttach')
    clientAttachList = QtGui.qApp.db.getRecordList(table, '*', [table['client_id'].eq(clientId), table['deleted'].eq(0)])

    for clientAttach in clientAttachList:
        attachTypeId = forceRef(clientAttach.value('attachType_id'))
        attachType = QtGui.qApp.db.getRecord('rbAttachType', '*', attachTypeId)
        result = {
            'attachTypeId': attachTypeId,
            'LPU_id': forceRef(clientAttach.value('LPU_id')),
            'orgStructure_id': forceRef(clientAttach.value('orgStructure_id')),
            'begDate': forceDate(clientAttach.value('begDate')),
            'endDate': forceDate(clientAttach.value('endDate')),
            'code': forceString(attachType.value('code')),
            'name': forceString(attachType.value('name')),
            'temporary': forceBool(attachType.value('temporary')),
            'outcome': forceBool(attachType.value('outcome')),
            'finance_id': forceRef(attachType.value('finance_id')),
            'document_id': forceRef(attachType.value('document_id')),
            'sentToTFOMS': forceInt(clientAttach.value('sentToTFOMS')),
            'errorCode': forceString(clientAttach.value('errorCode'))
        }
        if result['outcome']:
            result['date'] = result['endDate']
        else:
            result['date'] = result['begDate']
        attaches.append(result)

    return attaches


def getAttachRecord(clientId, temporary):
    clientAttach = selectLatestRecord(('ClientAttach',
                                       'ClientAttach AS Tmp JOIN rbAttachType ON Tmp.attachType_id=rbAttachType.id'),
                                      clientId,
                                      'Tmp.deleted= 0 AND rbAttachType.temporary %s \'0\'' % (
                                      '!=' if temporary else '='))
    if clientAttach:
        attachTypeId = forceRef(clientAttach.value('attachType_id'))
        attachType = QtGui.qApp.db.getRecord('rbAttachType', '*', attachTypeId)
        result = {
            'attachTypeId': attachTypeId,
            'LPU_id': forceRef(clientAttach.value('LPU_id')),
            'orgStructure_id': forceRef(clientAttach.value('orgStructure_id')),
            'begDate': forceDate(clientAttach.value('begDate')),
            'endDate': forceDate(clientAttach.value('endDate')),
            'code': forceString(attachType.value('code')),
            'name': forceString(attachType.value('name')),
            'temporary': forceBool(attachType.value('temporary')),
            'outcome': forceBool(attachType.value('outcome')),
            'finance_id': forceRef(attachType.value('finance_id')),
            'document_id': forceRef(attachType.value('document_id')),
            'sentToTFOMS': forceInt(clientAttach.value('sentToTFOMS')),
            'errorCode': forceString(clientAttach.value('errorCode'))
        }
        if result['outcome']:
            result['date'] = result['endDate']
        else:
            result['date'] = result['begDate']
        return result
    else:
        return None


def getClientAttachOrgStructure(clientId):
    u"""
    Поиск подходящего подразделения (участка) по прикреплению/адресу пациента
    :param clientId: Client.id
    :return: OrgStructure.id
    """
    attach = getAttachRecord(clientId, False)
    if attach:
        return attach['orgStructure_id']

    for addType in (0, 1):
        addrInfo = getAddressInfo(getClientAddress(clientId, addType))
        if addrInfo and addrInfo.KLADRCode:
            db = QtGui.qApp.db
            tableAddressHouse = db.table('AddressHouse')
            tableOrgStructureAddress = db.table('OrgStructure_Address')

            table = tableOrgStructureAddress.innerJoin(tableAddressHouse, [tableAddressHouse['id'].eq(tableOrgStructureAddress['house_id']),
                                                                           tableAddressHouse['deleted'].eq(0)])
            cond = [
                tableAddressHouse['KLADRCode'].eq(addrInfo.KLADRCode)
            ]
            if addrInfo.KLADRStreetCode:
                cond.append(tableAddressHouse['KLADRStreetCode'].eq(addrInfo.KLADRStreetCode))
            if addrInfo.number:
                cond.append(db.joinOr([tableAddressHouse['number'].eq(addrInfo.number),
                                       tableAddressHouse['number'].isNull()]))
                if addrInfo.corpus:
                    cond.append(db.joinOr([tableAddressHouse['corpus'].eq(addrInfo.corpus),
                                           tableAddressHouse['corpus'].isNull()]))
            if addrInfo.flat:
                cond.extend([
                    db.joinOr([tableOrgStructureAddress['firstFlat'].eq(0),
                               tableOrgStructureAddress['firstFlat'].le(addrInfo.flat)]),
                    db.joinOr([tableOrgStructureAddress['lastFlat'].eq(0),
                               tableOrgStructureAddress['lastFlat'].ge(addrInfo.flat)])
                ])
            cols = [
                tableOrgStructureAddress['master_id'].alias('orgStructureId')
            ]
            order = [
                tableOrgStructureAddress['id'].desc()
            ]
            rec = db.getRecordEx(table, cols, cond, order)
            if rec:
                return forceRef(rec.value('orgStructureId'))
    return None


def getClientMonitoringRecords(clientId):
    db = QtGui.qApp.db
    tableMonitoring = db.table('ClientMonitoring')
    tableMonitoringKind = db.table('rbClientMonitoringKind')
    tableMonitoringFrequence = db.table('rbClientMonitoringFrequence')
    queryTable = tableMonitoring.innerJoin(tableMonitoringKind,
                                           tableMonitoringKind['id'].eq(tableMonitoring['kind_id']))
    queryTable = queryTable.leftJoin(tableMonitoringFrequence,
                                     tableMonitoringFrequence['id'].eq(tableMonitoring['frequence_id']))
    cols = [tableMonitoring['setDate'],
            tableMonitoring['endDate'],
            tableMonitoring['reason'],
            tableMonitoringKind['name'].alias('kind'),
            tableMonitoringFrequence['name'].alias('frequence')]
    return db.getRecordList(table=queryTable,
                            cols=cols,
                            where=[tableMonitoring['client_id'].eq(clientId), tableMonitoring['deleted'].eq(0)],
                            order=tableMonitoring['setDate'])


def getClientMonitorings(clientId):
    result = []
    for record in getClientMonitoringRecords(clientId):
        monitoringInfo = smartDict()
        for idx in xrange(record.count()):
            value = record.value(idx)
            monitoringInfo[forceString(record.fieldName(idx))] = forceString(
                value) if value.type() == QtCore.QVariant.String else value.toPyObject()
        result.append(monitoringInfo)

    return result


def getClientAttaches(clientId):
    temporary = getAttachRecord(clientId, True)
    permanent = getAttachRecord(clientId, False)
    result = []
    if temporary:
        result.append(temporary)
    if permanent:
        result.append(permanent)
    result.sort(key=lambda record: record['date'])
    return result


def getClientSocStatuses(clientId):
    db = QtGui.qApp.db
    table = db.table('ClientSocStatus')
    cond = [table['client_id'].eq(clientId),
            table['deleted'].eq(0),
            db.joinOr([table['endDate'].isNull(),
                       table['endDate'].gt(QtCore.QDate.currentDate())])]
    return db.getIdList(table, idCol='socStatusType_id', where=cond, order='begDate')


def getClientSocStatusIds(clientId, includeExpired=False):
    db = QtGui.qApp.db
    table = db.table('ClientSocStatus')
    cond = [table['client_id'].eq(clientId),
            table['deleted'].eq(0)]
    if not includeExpired:
        cond.append(db.joinOr([table['endDate'].isNull(),
                               table['endDate'].ge(QtCore.QDate.currentDate())]))
    return db.getIdList(table, idCol='id', where=cond, order='begDate')


def getClientPhonesMaskDict():
    db = QtGui.qApp.db
    dict = {}
    stmt = u"Select `id`, `mask`, `maskEnabled` From rbContactType"
    query = db.query(stmt)
    while query.next():
        record = query.record()
        if forceString(record.value('mask')):
            dict[forceInt(record.value('id'))] = {'mask': forceString(record.value('mask')),
                                                  'enabled': forceBool(record.value('maskEnabled'))}
    return dict


def getEmailContactType():
    db = QtGui.qApp.db
    tableContactType = db.table('rbContactType')
    cond = db.joinOr([
        tableContactType['name'].like(u'%электронный адрес%'),
        tableContactType['name'].like(u'%электронная почта%'),
    ])
    idList = db.getIdList(tableContactType, where=cond)
    if idList:
        return idList[0]
    return db.insertFromDict(tableContactType, {'createDateTime' : QtCore.QDateTime.currentDateTime(),
                                                'createPerson_id': QtGui.qApp.userId,
                                                'code'           : 'email',
                                                'name'           : u'электронная почта'})


def getClientEmail(clientId, isPrimary=False):
    if not clientId: return []

    maskDict = getClientPhonesMaskDict()
    emailContactTypeId = getEmailContactType()

    def formatContact(contact, typeId):
        if maskDict.has_key(typeId) and maskDict[typeId]['enabled']:
            check = QtGui.QLineEdit()
            check.setInputMask(maskDict[typeId]['mask'])
            check.setText(contact)
            return unicode(check.text())
        else:
            return contact

    db = QtGui.qApp.db
    tableClientContact = db.table('ClientContact')
    tableContactType = db.table('rbContactType')
    queryTable = tableClientContact.leftJoin(tableContactType, tableContactType['id'].eq(tableClientContact['contactType_id']))
    cols = [
        tableContactType['code'].alias('typeCode'),
        tableContactType['name'],
        tableClientContact['contact'],
        tableClientContact['notes'],
        tableClientContact['contactType_id']
    ]
    cond = [
        tableClientContact['client_id'].eq(clientId),
        tableClientContact['deleted'].eq(0),
        tableClientContact['contactType_id'].eq(emailContactTypeId)
    ]
    order = [
        tableContactType['code'],
        tableClientContact['id']
    ]

    if isPrimary:
        cond.append(tableClientContact['isPrimary'].eq(1))

    result = []
    for record in db.iterRecordList(queryTable, cols, cond, order):
        typeCode = forceString(record.value('typeCode'))
        typeName = forceString(record.value('name'))
        contact = formatContact(forceString(record.value('contact')), forceInt(record.value('contactType_id')))
        notes = forceString(record.value('notes'))
        result.append((typeCode, typeName, contact, notes))
    return result


def getClientPhones(clientId, isPrimary=False):
    maskDict = getClientPhonesMaskDict()

    def formatContact(contact, typeId):
        if maskDict.has_key(typeId) and maskDict[typeId]['enabled']:
            check = QtGui.QLineEdit()
            check.setInputMask(maskDict[typeId]['mask'])
            check.setText(contact)
            return unicode(check.text())
        else:
            return contact

    db = QtGui.qApp.db
    table = db.table('ClientContact')
    tableContactTypes = db.table('rbContactType')
    queryTable = table.leftJoin(tableContactTypes, tableContactTypes['id'].eq(table['contactType_id']))
    cond = [
        table['client_id'].eq(clientId),
        table['deleted'].eq(0)
    ]

    cols = [
        tableContactTypes['code'].alias('typeCode'),
        tableContactTypes['name'].alias('typeName'),
        table['contact'].alias('contact'),
        table['notes'].alias('notes'),
        table['contactType_id'].alias('typeId')
    ]

    if isPrimary:
        cond.append(table['isPrimary'].eq(1))
        cols.append(table['isPrimary'])

    records = db.getRecordList(queryTable, cols, cond, [tableContactTypes['code'].name(), table['id'].name()])
    result = []
    for record in records:
        typeId = forceInt(record.value('typeId'))
        typeCode = forceString(record.value('typeCode'))
        typeName = forceString(record.value('typeName'))
        contact = formatContact(forceString(record.value('contact')), typeId)
        notes = forceString(record.value('notes'))
        # isPrimary = forceInt(record.value('isPrimary'))
        result.append((typeCode, typeName, contact, notes))  # , isPrimary))
    return result


def formatClientPhones(phones, withNotes=True):
    return u', '.join(
        # [u'%s: %s%s' % (name, contact, u'(%s)' % notes if notes and withNotes else u'') for code, name, contact, notes, isPrimary
        [u'%s: %s%s' % (name, contact, u'(%s)' % notes if notes and withNotes else u'') for code, name, contact, notes,
         in phones])


def getClientPhonesEx(id, withNotes=True, isPrimary=False):
    return formatClientPhones(getClientPhones(id, isPrimary), withNotes)

def getClientEmailsEx(id, withNotes=True, isPrimary=False):
    return formatClientPhones(getClientEmail(id, isPrimary), withNotes)

def getClientDDStatus(clientId):
    """
    возвращает (ddStatus, ddDate) - статус прохождения дополнительной диспансеризации
    (0, Event.execDate), если закончил в этом году;
    (1, Event.setDate), если начал в этом году, но ещё не закончил;
    (2, None), если подлежит ДД;
    None иначе.

    <!-- использование -->
    Проведение диспансеризации по приказу № 36ан от 03.02.2015 г. в текущем году:
    {if: client.statusDD}
        {: ddStatus, ddDate = client.statusDD}
        {if:   ddStatus == 0}<font color="#00aa00">проведена {ddDate}</font>
        {elif: ddStatus == 1}<font color="#aa4000">начата    {ddDate}</font>
        {elif: ddStatus == 2}<font color="#cc0000">подлежит</font>
        {end:}
    {else:}
        не подлежит
    {end:}
    """
    if not QtGui.qApp.checkContingentDDGlobalPreference():
        return None

    curDate = QtCore.QDate.currentDate()
    ageSelectors = QtGui.qApp.getContingentDDAgeSelectors()
    eventTypeCodes = QtGui.qApp.getContingentDDEventTypeCodes()

    db = QtGui.qApp.db
    tableClient = db.table('Client')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')

    queryTable = tableEvent.leftJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    cols = [
        tableEvent['setDate'],
        tableEvent['execDate']
    ]
    cond = [
        tableEvent['deleted'].eq(0),
        tableEvent['client_id'].eq(clientId),
        tableEventType['code'].inlist(eventTypeCodes)
    ]
    order = [
        tableEvent['setDate'].desc()
    ]
    record = db.getRecordEx(queryTable, cols, cond, order)
    if record:
        setDate = forceDate(record.value('setDate'))
        execDate = forceDate(record.value('execDate'))
        started = not execDate or execDate >= curDate
        return (0, 1)[started], \
               CDateInfo(setDate if started else execDate)

    cols = [
        tableClient['birthDate'],
        db.func.age(tableClient['birthDate'], curDate).alias('clientAge')
    ]
    clientRec = db.getRecord(tableClient, cols, clientId)
    clientBirthYear = forceDate(clientRec.value('birthDate')).year()
    clientAge = forceInt(clientRec.value('clientAge'))
    for begAge, endAge, step, useCalendarYear, useExclusion in ageSelectors:
        ages = range(begAge, endAge + 1, step if step else 1)
        years = [curDate.year() - age for age in ages]
        if not useExclusion:
            if (useCalendarYear and clientBirthYear in years) or (not useCalendarYear and clientAge in ages):
                return 2, None  # подлежит ДД

    return None


def getActualClientQuoting(id):
    date = QtCore.QDate.currentDate()
    return getClientQuoting(id, date=date)


def getClientQuoting(id, date=None):
    db = QtGui.qApp.db
    table = db.table('Client_Quoting')
    tableQuotaType = db.table('QuotaType')
    queryTable = table.innerJoin(tableQuotaType, tableQuotaType['id'].eq(table['quotaType_id']))
    cond = [table['master_id'].eq(id),
            table['deleted'].eq(0)]
    if date and date.isValid():
        cond.extend([table['dateRegistration'].dateLe(date),
                     db.joinOr([
                         table['dateEnd'].dateGe(date),
                         'DATE(' + table['dateEnd'].name() + ')=' + 'DATE(0000-00-00)'
                     ])
                     ])
    fields = [tableQuotaType['class'].name(),
              tableQuotaType['code'].name(),
              table['quotaTicket'].name(),
              table['status'].name()]
    recordList = db.getRecordList(queryTable, fields, cond)
    result = []
    for record in recordList:
        class_ = getQuotaTypeClassNameList()[forceInt(record.value('class'))]
        code = forceString(record.value('code'))
        quotaTicket = forceString(record.value('quotaTicket'))
        status = [u'Отменено',
                  u'Ожидание',
                  u'Активный талон',
                  u'Талон для заполнения',
                  u'Заблокированный талон',
                  u'Отказано',
                  u'Необходимо согласовать дату обслуживания',
                  u'Дата обслуживания на согласовании',
                  u'Дата обслуживания согласована',
                  u'Пролечен',
                  u'Обслуживание отложено',
                  u'Отказ пациента',
                  u'Импортировано из ВТМП'][forceInt(record.value('status'))]
        result.append((class_, code, quotaTicket, status))
    return result


def formatClientQuoting(clientQuotingList):
    result = []
    for clientQuoting in clientQuotingList:
        values = {'class': clientQuoting[0],
                  'code': clientQuoting[1],
                  'quotaTicket': clientQuoting[2],
                  'status': clientQuoting[3]}
        result.append(u'класс-%(class)s, код-%(code)s, талон-%(quotaTicket)s, состояние-%(status)s' % values)
    return u' | '.join(result)


def getActualClientPaymentScheme(id):
    date = QtCore.QDate.currentDate()
    return getClientPaymentScheme(id, date=date)


def getClientPaymentScheme(id, date=None):
    db = QtGui.qApp.db
    table = db.table('Client_PaymentScheme')
    tablePaymentScheme = db.table('PaymentScheme')
    tableOrganisation = db.table('Organisation')
    queryTable = table.innerJoin(tablePaymentScheme, tablePaymentScheme['id'].eq(table['paymentScheme_id']))
    queryTable = queryTable.innerJoin(tableOrganisation, tableOrganisation['id'].eq(tablePaymentScheme['org_id']))
    cond = [table['client_id'].eq(id)]
    if date and date.isValid():
        cond.extend([table['begDate'].dateLe(date),
                     db.joinOr([table['endDate'].dateGe(date),
                                table['endDate'].isNull()])])
    cond.append(table['deleted'].eq(0))
    recordList = db.getRecordList(queryTable,
                                  [tablePaymentScheme['id'], tablePaymentScheme['type'], tablePaymentScheme['number'],
                                   tableOrganisation['shortName'], table['begDate'], table['endDate']],
                                  cond)
    result = []
    for record in recordList:
        result.append((forceRef(record.value('id')),
                       [u'Клинические исследование', u'Безналичный расчет'][forceInt(record.value('type'))],
                       forceString(record.value('number')),
                       forceString(record.value('shortName')),
                       forceDate(record.value('begDate')),
                       forceDate(record.value('begDate'))))
    return result


def formatWork(workRecord):
    orgId = forceRef(workRecord.value('org_id'))
    if orgId:
        orgShortName = getOrganisationShortName(orgId)
    else:
        orgShortName = forceString(workRecord.value('freeInput'))
    post = forceString(workRecord.value('post'))
    OKVED = forceString(workRecord.value('OKVED'))
    result = []
    if orgShortName:
        result.append(orgShortName)
    if post:
        result.append(post)
    if OKVED:
        result.append(u'ОКВЭД: ' + OKVED)
    return forceStringEx(', '.join(result))


def formatWorkPlace(workRecord):
    orgId = forceRef(workRecord.value('org_id'))
    if orgId:
        return getOrganisationShortName(orgId)
    else:
        return forceString(workRecord.value('freeInput'))


def getSocStatusTypeClasses(id):
    db = QtGui.qApp.db
    table = db.table('rbSocStatusClassTypeAssoc')
    cond = table['type_id'].eq(id)
    return db.getIdList(table, idCol='class_id', where=cond, order='class_id')


def formatClientIdentificationWithCounter(clientIdentification):
    return ', '.join(
        ['<font color=green>%s: <B>%s</B></font>' % (key, val[0]) for key, val in clientIdentification.items()])


def formatClientIdentification(clientIdentification):
    dpd = clientIdentification.pop(u'Согласие', None)
    if not dpd is None:
        if unicode(dpd[0]).lower() == u'да' and dpd[1].daysTo(QtCore.QDate.currentDate()) + 1 < 366:
            dpd = u'Согласие: <B><font color=green>%s</font></B>' % (dpd[0] + '(' + forceString(dpd[1]) + ')')
        else:
            dpd = u'Согласие: <B><font color=red>%s</font></B>' % (dpd[0] + '(' + forceString(dpd[1]) + ')')
        return ', '.join([dpd] + ['%s: <B>%s</B>' % (key, val[0]) for key, val in clientIdentification.items()])
    return ', '.join(['%s: <B>%s</B>' % (key, val[0]) for key, val in clientIdentification.items()])


def getLocationCard(id):
    if id:
        db = QtGui.qApp.db
        table = db.table('Client_LocationCard')
        rbTable = db.table('rbLocationCardType')
        record = db.getRecordEx(table.innerJoin(rbTable, table['locationCardType_id'].eq(rbTable['id'])),
                                [rbTable['code'], rbTable['name'], rbTable['color']],
                                [table['deleted'].eq(0), table['master_id'].eq(id)], 'Client_LocationCard.id DESC')
        if record:
            #            code = forceString(record.value('code')) + '-' + forceString(record.value('name'))
            code = forceString(record.value('name'))
            color = forceString(record.value('color'))
            return [code, color]
    return None


def getIncapacityCheck(id):
    db = QtGui.qApp.db
    tableCR = db.table('ClientRemark')
    tableCRT = db.table('rbClientRemarkType')
    cond = []
    cond.append(tableCR['client_id'].eq(id))
    cond.append(tableCRT['flatCode'].eq(u'''incapacity'''))
    stmt = u'''SELECT flatCode
               FROM ClientRemark INNER JOIN rbClientRemarkType ON remarkType_id=rbClientRemarkType.id
               WHERE %s LIMIT 1''' % (db.joinAnd(cond))
    query = db.query(stmt)
    if query.first():
        return u'Недееспособен'
    else:
        return u''


def getSurveyResult(id):
    db = QtGui.qApp.db
    tableCSS = db.table('ClientSocStatus')
    tableSST = db.table('rbSocStatusType')
    cond = []
    cond.append(tableCSS['client_id'].eq(id))
    cond.append(
        tableSST['code'].inlist([u'''ОбВИЧ_3''', u'''ОбГВ_3''', u'''ОбГС_3''', u'''ОбТуб_3''', u'''ОбВИЧ_31''']))
    stmt = u'''SELECT code
               FROM ClientSocStatus INNER JOIN rbSocStatusType ON socStatusType_id = rbSocStatusType.id
               WHERE %s ''' % (db.joinAnd(cond))
    query = db.query(stmt)
    result = []
    while query.next():
        record = query.record()
        socCode = forceString(record.value('code'))
        if socCode == u'''ОбВИЧ_31''' or socCode == u'''ОбВИЧ_3''':
            result.append(u'Обследование на ВИЧ - результат положительный<BR>')
        elif socCode == u'''ОбГВ_3''':
            result.append(u'Обследование на гепатит В - результат положительный<BR>')
        elif socCode == u'''ОбГС_3''':
            result.append(u'Обследование на гепатит С - результат положительный<BR>')
        elif socCode == u'''ОбТуб_3''':
            result.append(u'Обследование на туберкулез - результат положительный<BR>')
    stringresult = u''
    if len(result):
        for record in result:
            stringresult += record
    return stringresult


def getStatusObservationClient(id):
    if id:
        db = QtGui.qApp.db
        table = db.table('Client_StatusObservation')
        rbTable = db.table('rbStatusObservationClientType')
        record = db.getRecordEx(table.innerJoin(rbTable, table['statusObservationType_id'].eq(rbTable['id'])),
                                [rbTable['code'], rbTable['name'], rbTable['color']],
                                [table['deleted'].eq(0), table['master_id'].eq(id)], 'Client_StatusObservation.id DESC')
        if record:
            #            code = forceString(record.value('code')) + '-' + forceString(record.value('name'))
            code = forceString(record.value('name'))
            color = forceString(record.value('color'))
            return [code, color]
    return None


def getUnregisteredRelatives(id, allRelations):
    db = QtGui.qApp.db
    result = []
    tableCR = db.table('ClientRelation')
    tableRT = db.table('rbRelationType')
    tmpCond1 = db.joinAnd([tableCR['client_id'].eq(id),
                           db.joinOr([tableCR['relative_id'].eq(-1),
                                      tableCR['relative_id'].isNull()])
                           ])
    tmpCond2 = db.joinAnd([db.joinOr([tableCR['client_id'].eq(-1),
                                      tableCR['client_id'].isNull()]),
                           tableCR['relative_id'].eq(id)])
    tmpCond3 = db.joinOr([tmpCond1, tmpCond2])
    cond = db.joinAnd([tableCR['deleted'].eq(0),
                       tableCR['relativeType_id'].isNotNull(),
                       tmpCond3
                       ])
    table = tableCR.innerJoin(tableRT, tableCR['relativeType_id'].eq(tableRT['id']))
    fields = [tableCR['client_id'].name(),
              tableCR['relative_id'].name(),
              tableRT['leftName'].name(),
              tableRT['rightName'].name(),
              tableCR['freeInput'].name()]
    if not allRelations:
        stmt = db.selectStmt(table, fields, cond, limit=1)
    else:
        stmt = db.selectStmt(table, fields, cond)
    query = db.query(stmt)
    while query.next():
        record = query.record()
        clientId = forceInt(record.value('client_id'))
        if not clientId or clientId == -1:
            res = forceString(record.value('leftName'))
        else:
            res = forceString(record.value('rightName'))
        res += u' - '
        res += forceString(record.value('freeInput'))
        result.append(res)
    if len(result):
        return result
    else:
        return u''


def getRelative(id):
    if QtGui.qApp.addUnregisteredRelationsEnabled():
        relatives = getUnregisteredRelatives(id, QtGui.qApp.outputAllRelations())
        relative = u''
        for record in relatives:
            relative += u'%s<BR>' % record
        return relative
    else:
        return u''


def getDocument(id, documentRecord):
    if documentRecord:
        return formatDocument(documentRecord.value('documentType_id'),
                              documentRecord.value('serial'),
                              documentRecord.value('number'))
    else:
        return u'не указано'


def getDispanserizationDateRange(record):
    return formatDateRange(record['date_begin'], record['date_end'])


def getPolicyAndColor(policyRecord, defaultColor, serviceStopField):
    policy = u''
    color = defaultColor
    if policyRecord:
        policy = formatPolicy(policyRecord.value('insurer_id'),
                              policyRecord.value('serial'),
                              policyRecord.value('number'),
                              policyRecord.value('begDate'),
                              policyRecord.value('endDate'),
                              policyRecord.value('name'),
                              policyRecord.value('note'),
                              policyRecord.value('policyKind_id'),
                              policyRecord.value('dischargeDate')
                              )
        policyServiceDMC = forceBool(policyRecord.value(serviceStopField))
        dateInvalid = False
        # if QtGui.qApp.showPolicyDischargeDate():
        #     if (
        #                     policyRecord.value('dischargeDate')
        #                     and not policyRecord.value('dischargeDate').isNull()
        #                     and forceDate(policyRecord.value('dischargeDate')) < datetime.date.today()
        #     ):
        #         dateInvalid = True
        if (
                        policyRecord.value('endDate')
                    and not policyRecord.value('endDate').isNull()
                and forceDate(policyRecord.value('endDate')) < datetime.date.today()
        ):
            dateInvalid = True

        if policyServiceDMC or dateInvalid:
            color = u'red'
    return policy, color


def getAddressInfo(record):
    if record:
        return getAddress(record.value('address_id'),
                          record.value('freeInput'))
    return None


def getWork(id):
    workRecord = getClientWork(id)
    return formatWork(workRecord) if workRecord else None


def getDiagnosis(id):
    db = QtGui.qApp.db
    empty = QtSql.QSqlRecord()
    if QtGui.qApp.isPNDDiagnosisMode():
        # tableDiagnosis = db.table('Diagnosis')
        # cond  = [tableDiagnosis['client_id'].eq(id)]
        # select = db.selectStmt(tableDiagnosis, ['MAX(Diagnosis.`setDate`)', tableDiagnosis['MKB'].alias('diagnosisMKB')],where=cond)
        select = db.selectStmt(
            '''SELECT  MAX(Diagnosis.id), Diagnosis.`MKB` AS `diagnosisMKB`, MKB_Tree.`DiagName`
               FROM Diagnosis LEFT JOIN MKB_Tree ON Diagnosis.`MKB` = MKB_Tree.`DiagID`
               WHERE Diagnosis.`client_id` = %s AND Diagnosis.`deleted` = 0
               GROUP BY Diagnosis.`MKB`
               ORDER BY MAX(Diagnosis.`setDate`) DESC''' % (id))
        query = db.query(select)
        if query.first():
            return query.record()
    return empty


def getCheckDate(id):
    checkDate = None
    try:
        tableClientIdentification = QtGui.qApp.db.table('ClientIdentification')
        identDate = QtGui.qApp.db.getRecordEx(
            tableClientIdentification,
            u'max(checkDate)',
            u'client_id=%d and accountingSystem_id in (1, 2)' % id)
        if identDate:
            checkDate = forceString(identDate.value(0))
    except:
        QtGui.qApp.logCurrentException()
    return checkDate


def getDeattachReason(id):
    db = QtGui.qApp.db
    ClientAttach = db.table('ClientAttach')
    rbDetachmentReason = db.table('rbDetachmentReason')
    Organisation = db.table('Organisation')
    OrgStructure = db.table('OrgStructure')

    table = ClientAttach.leftJoin(rbDetachmentReason, rbDetachmentReason['id'].eq(ClientAttach['detachment_id']))
    table = table.leftJoin(Organisation, Organisation['id'].eq(ClientAttach['LPU_id']))
    table = table.leftJoin(OrgStructure, OrgStructure['id'].eq(ClientAttach['orgStructure_id']))

    cols = [
        Organisation['shortName'].alias('orgName'),
        OrgStructure['name'].alias('orgStructureName'),
        rbDetachmentReason['name'].alias('reason')
    ]

    result = db.getRecordList(table, cols, [ClientAttach['client_id'].eq(id),
                                            ClientAttach['deleted'].eq(0)])
    reasons = []
    for x in result:
        reason = forceString(x.value('reason'))
        orgName = forceString(x.value('orgName'))
        orgStructureName = forceString(x.value('orgStructureName'))
        reasons.append(((orgStructureName or orgName) + u' - ' + reason) if reason else u'не указано')

    return u', '.join(reasons)


# TODO: move all formatted fields to formatter functions
def getClientInfo(id):
    db = QtGui.qApp.db
    table = db.table('Client')
    result = LazySmartDict()
    result.record = lambda: db.getRecord(table, '*', id) or QtSql.QSqlRecord()
    result.id = lambda: forceRef(id)
    result.createDate = lambda: forceDate(result.record.value('createDatetime'))
    result.lastName = lambda: forceString(result.record.value('lastName'))
    result.firstName = lambda: forceString(result.record.value('firstName'))
    result.patrName = lambda: forceString(result.record.value('patrName'))
    result.sexCode = lambda: forceInt(result.record.value('sex'))
    result.birthDate = lambda: forceDate(result.record.value('birthDate'))
    result.birthPlace = lambda: forceString(result.record.value('birthPlace'))
    result.SNILS = lambda: forceString(result.record.value('SNILS'))
    result.notes = lambda: forceString(result.record.value('notes'))
    result.attaches = lambda: getClientAttaches(id)
    result.socStatuses = lambda: getClientSocStatuses(id)
    result.quoting = lambda: getActualClientQuoting(id)
    result.identification = lambda: formatClientIdentification(getClientIdentification(id))
    result.identificationWithCounter = lambda: formatClientIdentificationWithCounter(
        getClientIdentificationWithCounter(id))
    result.identificationWithoutCounter = lambda: formatClientIdentification(
        getClientIdentificationWithCounter(id, False))
    result.locationCard = lambda: getLocationCard(id)
    result.statusObservationClient = lambda: getStatusObservationClient(id)
    result.diagNames = lambda: forceString(result.record.value('diagNames'))
    result.monitorings = lambda: getClientMonitorings(id)
    result.incapacity = lambda: getIncapacityCheck(id)
    result.surveyResult = lambda: getSurveyResult(id)
    result.relative = lambda: getRelative(id)
    result.checkDate = lambda: getCheckDate(id)

    result.documentRecord = lambda: getClientDocument(id)
    result.document = lambda: getDocument(id, result.documentRecord)
    result.deattachReason = lambda: getDeattachReason(id)
    result.compulsoryPolicyRecord = lambda: getClientCompulsoryPolicy(id)
    result._compPolicyAndColor = lambda: getPolicyAndColor(result.compulsoryPolicyRecord,
                                                           u'green', 'compulsoryServiceStop')
    result.compulsoryPolicy = lambda: result._compPolicyAndColor[0]
    colorOMC = lambda: result._compPolicyAndColor[1]
    result.policy = lambda: result.compulsoryPolicy

    result.voluntaryPolicyRecord = lambda: getClientVoluntaryPolicy(id)
    result._voluntPolicyAndColor = lambda: getPolicyAndColor(result.voluntaryPolicyRecord,
                                                             u'blue', 'voluntaryServiceStop')
    result.voluntaryPolicy = lambda: result._voluntPolicyAndColor[0]
    colorDMC = lambda: result._voluntPolicyAndColor[1]

    result.compulsoryvoluntaryPolicy = lambda: \
        u'''<B><font color=%s>%s</font></B>%s<B><font color=%s>%s</font></B>''' \
        % (colorOMC(), result.compulsoryPolicy,
           (u', полис ДМС' if result.voluntaryPolicy else ''),
           colorDMC(), result.voluntaryPolicy)

    # TODO: abstract it out? That's not so easy to do while staying lazy.
    result.regAddressRecord = lambda: getClientAddress(id, 0)
    result.regAddressInfo = lambda: getAddressInfo(result.regAddressRecord)
    result.regAddress = lambda: formatAddressInt(result.regAddressInfo) if result.regAddressInfo else None

    result.locAddressRecord = lambda: getClientAddress(id, 1)
    result.locAddressInfo = lambda: getAddressInfo(result.locAddressRecord)
    result.locAddress = lambda: formatAddressInt(result.locAddressInfo) if result.locAddressInfo else None

    result.attendingPerson = lambda: forceString(
        db.translate('vrbPersonWithSpeciality', 'id', forceInt(result.record.value('attendingPerson_id')), 'name')
    )

    result.disabilityGroup = lambda: forceString(db.translate(
        'ClientDisability',
        'client_id',
        forceInt(result.record.value('id')),
        'groupNumber',
        order='setDate DESC, recertificationDate DESC'
    ))

    result.work = lambda: getWork(id)
    result.paymentScheme = lambda: getActualClientPaymentScheme(id)

    result.diagnosis = lambda: getDiagnosis(id)
    result.diagnosisName = lambda: (forceString(result.diagnosis.value('DiagName'))
                                    if result.diagnosis else None)
    result.diagnosisMKB = lambda: (forceString(result.diagnosis.value('diagnosisMKB'))
                                   if result.diagnosis else None)
    return result


def getClientInfoEx(clientId, date=None):
    clientInfo = getClientInfo(clientId)
    clientInfo.fullName = lambda: formatNameInt(clientInfo.lastName, clientInfo.firstName, clientInfo.patrName)
    clientInfo.shortName = lambda: formatShortNameInt(clientInfo.lastName, clientInfo.firstName, clientInfo.patrName)

    clientInfo.birthDate = lambda: formatDate(clientInfo.record.value('birthDate'))
    clientInfo.age = lambda: calcAge(clientInfo.record.value('birthDate'), date)
    clientInfo.sex = lambda: formatSex(clientInfo.sexCode)
    clientInfo.SNILS = lambda: formatSNILS(forceString(clientInfo.record.value('SNILS')))

    clientInfo.setdefault('document', u'нет')
    clientInfo.setdefault('compulsoryPolicy', u'нет')
    clientInfo.setdefault('voluntaryPolicy', u'нет')
    clientInfo.policy = lambda: clientInfo.compulsoryPolicy
    clientInfo.socStatus = lambda: formatSocStatuses(clientInfo.get('socStatuses', []))
    clientInfo.setdefault('regAddress', u'не указан')
    clientInfo.setdefault('locAddress', u'не указан')
    clientInfo.setdefault('work', u'не указано')
    clientInfo.phones = lambda: getClientPhonesEx(clientId)
    return clientInfo


def formatAttachAsHTML(attach, atDate):
    td = forceDate(atDate) if atDate else QtCore.QDate.currentDate()
    bold = False
    txt = attach['name']
    attachPlace = ''
    if forceString(QtGui.qApp.db.translate('rbAttachType', 'code', attach['code'], 'temporary')) == '0' and (
                forceString(QtGui.qApp.db.translate('rbAttachType', 'code', attach['code'], 'outcome')) == '0'):
        if attach['LPU_id']:
            attachPlace = u'(' + forceString(
                QtGui.qApp.db.translate('Organisation', 'id', attach['LPU_id'], 'shortName')) + u')'
        if attach['orgStructure_id']:
            attachPlace += u'(' + forceString(
                QtGui.qApp.db.translate('OrgStructure', 'id', attach['orgStructure_id'], 'code')) + u')'
    if attach['outcome']:
        color = 'red'
        txt = txt + ' ' + forceString(attach['begDate'])
    elif attach['temporary']:
        color = 'blue'
        bold = True
        txt = txt + ' ' + attachPlace
        if attach['begDate'].isValid():
            txt = txt + u' с ' + forceString(attach['begDate'])
            color = 'blue' if attach['begDate'] <= td else 'red'
        if attach['endDate'].isValid():
            txt = txt + u' по ' + forceString(attach['endDate'])
            color = 'blue' if attach['endDate'] >= td else 'red'
    else:
        txt = txt + ' ' + attachPlace
        if attach['endDate']:
            color = 'red'
            txt += u' до ' + forceString(attach['endDate'])
        else:
            color = 'green'

    sentToTFOMS = attach['sentToTFOMS']
    sentToTFOMSMsg = CAttachSentToTFOMS.getBannerMessage(sentToTFOMS)
    if sentToTFOMSMsg:
        txt += u' (%s)' % sentToTFOMSMsg
        if sentToTFOMS == CAttachSentToTFOMS.NotSynced:
            errorCode = attach['errorCode']
            if errorCode:
                txt += u'(ошибка: "%s")' % errorCode

    return u'<font color="%s">%s%s%s</font>' % (color, '<B>' if bold else '', txt, '</B>' if bold else '')


def formatAttachesAsHTML(attaches, atDate):
    return ', '.join([formatAttachAsHTML(x, atDate) for x in attaches])


def formatAttachAsText(attach):
    txt = attach['name']
    attachPlace = ''
    if forceString(QtGui.qApp.db.translate('rbAttachType', 'code', attach['code'], 'temporary')) == '0' and (
                forceString(QtGui.qApp.db.translate('rbAttachType', 'code', attach['code'], 'outcome')) == '0'):
        if attach['LPU_id']:
            attachPlace = u'(' + forceString(
                QtGui.qApp.db.translate('Organisation', 'id', attach['LPU_id'], 'shortName')) + u')'
        if attach['orgStructure_id']:
            attachPlace += u'(' + forceString(
                QtGui.qApp.db.translate('OrgStructure', 'id', attach['orgStructure_id'], 'code')) + u')'
    if attach['outcome']:
        txt = txt + ' ' + forceString(attach['begDate'])
    elif attach['temporary']:
        txt = txt + ' ' + attachPlace
        if attach['begDate'].isValid():
            txt = txt + u' с ' + forceString(attach['begDate'])
        if attach['endDate'].isValid():
            txt = txt + u' по ' + forceString(attach['endDate'])
    else:
        txt = txt + ' ' + attachPlace
        if attach['endDate']:
            txt += u' до ' + forceString(attach['endDate'])

    sentToTFOMS = attach['sentToTFOMS']
    sentToTFOMSMsg = CAttachSentToTFOMS.getBannerMessage(sentToTFOMS)
    if sentToTFOMSMsg:
        txt += u' (%s)' % sentToTFOMSMsg
        if sentToTFOMS == CAttachSentToTFOMS.NotSynced:
            errorCode = attach['errorCode']
            if errorCode:
                txt += u'(ошибка: "%s")' % errorCode
    return txt


def formatAttachesAsText(attaches):
    return ';\n'.join([formatAttachAsText(x) for x in attaches])


def getSocStatusClassList():
    socStatusClassList = {}
    records = QtGui.qApp.db.getRecordList('rbSocStatusClass', 'id', 'group_id IS NULL')
    for record in records:
        classId = forceRef(record.value('id'))
        if classId and (classId not in socStatusClassList.keys()):
            socStatusClassList[classId] = []
    return socStatusClassList


def formatSocStatus(socStatusTypeId, socStatusClassList):
    db = QtGui.qApp.db
    tableClassTypeAssoc = db.table('rbSocStatusClassTypeAssoc')
    tableSocStatusClass = db.table('rbSocStatusClass')
    table = tableClassTypeAssoc.innerJoin(tableSocStatusClass,
                                          tableClassTypeAssoc['class_id'].eq(tableSocStatusClass['id']))
    cond = [tableClassTypeAssoc['type_id'].eq(socStatusTypeId),
            tableSocStatusClass['isShowInClientInfo'].eq(1)]
    socStatusClasses = db.getDistinctIdList(table,
                                            'IF(rbSocStatusClass.group_id IS NOT NULL, rbSocStatusClass.group_id, rbSocStatusClass.id) AS class_id',
                                            where=cond, order='class_id')
    for id in socStatusClasses:
        record = db.getRecordEx('rbSocStatusClass',
                                'IF(code = 1 OR group_id IN (SELECT SSC.id FROM rbSocStatusClass AS SSC WHERE SSC.code = 1), 1, 0) AS privilegeClass, group_id',
                                'id = %d' % (id))
        if record:
            groupId = forceRef(record.value('group_id'))
            privilegeClass = forceBool(record.value('privilegeClass'))
            if groupId and groupId in socStatusClassList.keys():
                socStatusClass = socStatusClassList[groupId]
                socStatusClass.append(u': '.join([CSocStatusTypeCache.getCode(socStatusTypeId),
                                                  CSocStatusTypeCache.getName(
                                                      socStatusTypeId)]) if privilegeClass else CSocStatusTypeCache.getName(
                    socStatusTypeId))
            elif id in socStatusClassList.keys():
                socStatusClass = socStatusClassList[id]
                socStatusClass.append(u': '.join([CSocStatusTypeCache.getCode(socStatusTypeId),
                                                  CSocStatusTypeCache.getName(
                                                      socStatusTypeId)]) if privilegeClass else CSocStatusTypeCache.getName(
                    socStatusTypeId))
    return socStatusClassList


def formatSocStatuses(socStatuses):
    if socStatuses:
        db = QtGui.qApp.db
        result = u''
        socStatusTypeClassList = {}
        socStatusClassList = getSocStatusClassList()
        for socStatusTypeId in socStatuses:
            socStatusTypeClassList = formatSocStatus(socStatusTypeId, socStatusClassList)
        keys = socStatusTypeClassList.keys()
        keys.sort()
        for key in keys:
            value = socStatusTypeClassList[key]
            if value:
                nameStatusClass = forceString(db.translate('rbSocStatusClass', 'id', key, 'name'))
                result += nameStatusClass + u': ' + u' ,'.join(nameStatusType for nameStatusType in value) + u'; '
        return result
    else:
        return u'нет'


def getClientMiniInfo(id, atDate=None):
    db = QtGui.qApp.db
    record = db.getRecord('Client', ['lastName', 'firstName', 'patrName', 'birthDate', 'sex'], id)
    if record:
        name = formatName(record.value('lastName'), record.value('firstName'), record.value('patrName'))
        birthDate = forceDate(record.value('birthDate'))
        birthDateStr = formatDate(birthDate)
        age = calcAge(birthDate, atDate)
        sex = formatSex(forceInt(record.value('sex')))
        return u'%s, %s (%s) %s' % (name, birthDateStr, age, sex)
    else:
        return u''


def getClientBanner(id, atDate=None, keys=None):
    printTemplate = getFirstPrintTemplate('clientBanner')  # (name, id, dpdAgreement, banUnkeptDate)
    if printTemplate is not None:
        template = getTemplate(printTemplate[1])  # (name, content, type)
        clientInfo = getClientInfo2(id, atDate)
        data = {'client': clientInfo}
        content, canvases = compileAndExecTemplate(template[1], data)
        return content
    info = getClientInfo(id)
    return formatClientBanner(info, atDate, keys)


def getFullClientInfoAsHtml(clientId, atDate=None):
    info = getClientInfo(clientId)
    return formatFullClientInfoAsHtml(info, atDate)


def getClientString(id, atDate=None):
    info = getClientInfo(id)
    return formatClientString(info, atDate)


def getDispansInfo(client_id):
    try:
        db = QtGui.qApp.db
        table = db.table('ClientDispanserization')
        record = db.getRecordEx(table, 'code, date_begin, date_end, codeMO',
                                'client_id = %s ORDER BY id DESC' % client_id)
        dict = {}
        dict['code'] = forceString(record.value('code')) + " " + forceString(
            db.translate('rbMedicalAidType', 'regionalCode', forceString(record.value('code')),
                         'name')) if record else '-'
        dict['date_begin'] = forceString(formatDate(record.value('date_begin'))) if record else '-'
        dict['date_end'] = forceString(formatDate(record.value('date_end'))) if record else '-'
        dict['codeMO'] = forceString(record.value('codeMO')) + " " + forceString(
            db.translate('Organisation', 'infisCode', forceString(record.value('codeMO')),
                         'shortName')) if record else '-'
        return dict
    except:
        # pirozhok: для старых баз, которые не умеют ClientDispanserization воткнул сие
        return {
            'code': '-',
            'date_begin': '-',
            'date_end': '-',
            'codeMO': '-'
        }


def getClientHospitalOrgStructureAndBedRecords(clientId=None):
    result = [None, None]
    if clientId:
        db = QtGui.qApp.db
        tableAPHB = db.table('ActionProperty_HospitalBed')
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableOS = db.table('OrgStructure')
        tableHBP = db.table('rbHospitalBedProfile')
        tableAPOS = db.table('ActionProperty_OrgStructure')
        currentDate = QtCore.QDateTime.currentDateTime()
        cols = [tableAction['id'],
                tableEvent['id'].alias('eventId'),
                tableEvent['client_id'],
                tableActionType['flatCode'],
                tableAction['begDate'],
                tableAction['endDate']
                ]
        condBeds = [tableAP['deleted'].eq(0),
                    tableActionType['deleted'].eq(0),
                    tableAPT['deleted'].eq(0),
                    tableAPT['typeName'].like('HospitalBed')
                    ]
        condBeds.append('A.deleted = 0')
        condBeds.append('A.id = Action.id')
        condBeds.append('ActionProperty.action_id=A.id')
        condOS = [tableAP['deleted'].eq(0),
                  tableActionType['deleted'].eq(0),
                  tableAPT['deleted'].eq(0)
                  ]
        condOS.append('A.id = Action.id')
        condOS.append('A.deleted = 0')
        condOS.append('ActionProperty.action_id=A.id')
        condOS.append('ActionProperty.type_id=ActionPropertyType.id')
        condOS.append(
            '''(ActionProperty.id IN (SELECT DISTINCT APHB.id FROM ActionProperty_HospitalBed AS APHB) AND NOT(SELECT DISTINCT APHB.value FROM ActionProperty_HospitalBed AS APHB WHERE APHB.id = ActionProperty.id LIMIT 1)) OR (ActionProperty.id NOT IN (SELECT DISTINCT APHB.id FROM ActionProperty_HospitalBed AS APHB))''')
        condOS.append(
            db.joinOr([tableAPT['name'].like(u'Отделение пребывания'), tableAPT['typeName'].like('HospitalBed')]))
        cols.append('''(SELECT ActionProperty_HospitalBed.value
        FROM ActionType
        INNER JOIN Action AS A ON ActionType.id=A.actionType_id
        INNER JOIN ActionPropertyType ON ActionPropertyType.actionType_id=ActionType.id
        INNER JOIN ActionProperty ON ActionProperty.type_id=ActionPropertyType.id
        INNER JOIN ActionProperty_HospitalBed ON ActionProperty_HospitalBed.id=ActionProperty.id
        WHERE %s
        LIMIT 0,1) AS bedId''' % (db.joinAnd(condBeds)))
        cols.append('''(SELECT ActionProperty_OrgStructure.value
        FROM ActionType
        INNER JOIN Action AS A ON ActionType.id=A.actionType_id
        INNER JOIN ActionPropertyType ON ActionPropertyType.actionType_id=ActionType.id
        INNER JOIN ActionProperty ON ActionProperty.type_id=ActionPropertyType.id
        INNER JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id=ActionProperty.id
        WHERE %s
        LIMIT 0,1) AS orgStructureId ''' % (db.joinAnd(condOS)))
        cols.append('''(SELECT name
        FROM OrgStructure
        WHERE OrgStructure.id = orgStructureId
        LIMIT 0,1) AS orgStructureName ''')

        queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
        queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
        cond = [tableEvent['deleted'].eq(0),
                tableAction['deleted'].eq(0),
                tableAP['deleted'].eq(0),
                tableActionType['deleted'].eq(0),
                tableAPT['deleted'].eq(0),
                tableEvent['client_id'].eq(clientId),
                tableEvent['setDate'].le(currentDate),
                tableAction['begDate'].le(currentDate),
                tableAP['action_id'].eq(tableAction['id'])
                ]
        cond.append(db.joinOr([tableEvent['execDate'].isNull(), tableEvent['execDate'].ge(currentDate)]))
        cond.append(db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].ge(currentDate)]))
        cond.append(
            db.joinOr([tableActionType['flatCode'].like('moving'), tableActionType['flatCode'].like('planning')]))
        recordsMoving = db.getRecordListGroupBy(queryTable, cols, cond, u'Action.id')
        for record in recordsMoving:
            result = [record, None]
            bedId = forceRef(record.value('bedId'))
            queryTableBed = tableOSHB.innerJoin(tableHBP, tableHBP['id'].eq(tableOSHB['profile_id']))
            queryTableBed = queryTableBed.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
            colsBed = [tableOS['name'].alias('nameOS'),
                       tableOS['code'].alias('codeOS'),
                       tableOSHB['code'].alias('codeBed'),
                       tableOSHB['name'].alias('nameBed'),
                       tableHBP['code'].alias('codeBedProfile'),
                       tableHBP['name'].alias('nameBedProfile')
                       ]
            recordsBed = db.getRecordListGroupBy(queryTableBed, colsBed, [tableOSHB['id'].eq(bedId)],
                                                 u'OrgStructure_HospitalBed.id')
            for recordBed in recordsBed:
                result = [record, recordBed]
    return result


def getClientHospitalOrgStructureAndBeds(clientId=None):
    result = [u'', 0]
    resultStr = ''
    flatCode = ''
    resultFlatCode = -1
    [recordMoving, recordBed] = getClientHospitalOrgStructureAndBedRecords(clientId)
    if recordMoving:
        bedId = forceRef(recordMoving.value('bedId'))
        orgStructureName = forceString(recordMoving.value('orgStructureName'))
        flatCode = forceString(recordMoving.value('flatCode'))
        resultStr = (u' отделение : ' + orgStructureName + u';') if orgStructureName else u''
    if recordBed:
        nameOS = forceString(recordBed.value('nameOS'))
        codeOS = forceString(recordBed.value('codeOS'))
        codeBed = forceString(recordBed.value('codeBed'))
        nameBed = forceString(recordBed.value('nameBed'))
        codeBedProfile = forceString(recordBed.value('codeBedProfile'))
        nameBedProfile = forceString(recordBed.value('nameBedProfile'))
        resultStr += u' койка: ' + codeOS + u', ' + codeBed + u'(' + codeBedProfile + u'-' + nameBedProfile + u')'
    if u'moving' in flatCode.lower():
        resultFlatCode = 1
    elif u'planning' in flatCode.lower():
        resultFlatCode = 0
    result = [resultStr, resultFlatCode]
    return result


def formatClientHospitalisation(list):
    return '; '.join([record[0] + '\t' + record[1] for record in list])


def getClientHospitalisation(clientId=None):
    db = QtGui.qApp.db
    tableEvent = db.table('Event')
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableActionPropertyType = db.table('ActionPropertyType')
    tableActionProperty = db.table('ActionProperty')
    tableActionProperty_OrgStructure = db.table('ActionProperty_OrgStructure')
    tableOrgStructure = db.table('OrgStructure')
    queryTable = tableEvent.innerJoin(tableAction, db.joinAnd([tableAction['event_id'].eq(tableEvent['id']), '''Action.id = (SELECT max(act.id)
                                                                                                                             FROM Action act
                                                                                                                             INNER JOIN ActionType actType ON actType.id = act.actionType_id
                                                                                                                             WHERE actType.flatCode = 'moving' AND act.event_id = Event.id)''']))
    # queryTable = queryTable.innerJoin(tableActionType, db.joinAnd([tableActionType['id'].eq(tableAction['actionType_id']), '''ActionType.id = (SELECT max(Action.id]))
    queryTable = queryTable.innerJoin(tableActionPropertyType,
                                      tableActionPropertyType['name'].eq(u'Отделение пребывания'))
    queryTable = queryTable.innerJoin(tableActionProperty, db.joinAnd(
        [tableAction['id'].eq(tableActionProperty['action_id']),
         tableActionProperty['type_id'].eq(tableActionPropertyType['id'])]))
    queryTable = queryTable.innerJoin(tableActionProperty_OrgStructure,
                                      tableActionProperty_OrgStructure['id'].eq(tableActionProperty['id']))
    queryTable = queryTable.innerJoin(tableOrgStructure,
                                      tableActionProperty_OrgStructure['value'].eq(tableOrgStructure['id']))
    cols = [tableOrgStructure['name'],
            'date(Event.execDate)']
    cond = [tableEvent['deleted'].eq(0),
            tableAction['deleted'].eq(0),
            tableActionProperty['deleted'].eq(0),
            # tableActionType['flatCode'].eq('leaved'),
            tableEvent['client_id'].eq(clientId),
            tableEvent['execDate'].le(QtCore.QDateTime.currentDateTime())]
    records = db.getRecordList(queryTable, cols, cond, tableEvent['id'])
    result = []
    for record in records:
        orgStructure = forceString(record.value(0))
        execDate = forceString(record.value(1))
        result.append((orgStructure, execDate))
    return formatClientHospitalisation(result)


def formatFullClientInfoAsHtml(info, atDate=None):
    def getPNDHospitalInfo(eventId):
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableActionProperty = db.table('ActionProperty')
        tableActionPropertyType = db.table('ActionPropertyType')
        tableActionPropertyString = db.table('ActionProperty_String')
        queryTable = tableAction.innerJoin(tableActionType, [tableActionType['id'].eq(tableAction['actionType_id']),
                                                             tableActionType['deleted'].eq(0),
                                                             tableActionType['code'].like(u'госп')])
        queryTable = queryTable.innerJoin(tableActionPropertyType,
                                          [tableActionPropertyType['actionType_id'].eq(tableActionType['id']),
                                           tableActionPropertyType['name'].like(u'Цель'),
                                           tableActionPropertyType['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableActionProperty,
                                          [tableActionProperty['type_id'].eq(tableActionPropertyType['id']),
                                           tableActionProperty['action_id'].eq(tableAction['id']),
                                           tableActionProperty['deleted'].eq(0)])
        queryTable = queryTable.innerJoin(tableActionPropertyString,
                                          tableActionPropertyString['id'].eq(tableActionProperty['id']))
        recordList = db.getRecordList(table=queryTable,
                                      cols=[tableAction['begDate'],
                                            tableAction['endDate'],
                                            tableActionPropertyString['value']],
                                      where=[tableAction['event_id'].eq(eventId),
                                             tableAction['deleted'].eq(0)],
                                      limit=1)

        if recordList:
            record = recordList[0]
            goal = forceString(record.value(u'value'))
            return (goal,
                    formatDate(forceDate(record.value('begDate'))),
                    formatDate(forceDate(record.value('endDate'))),
                    getEventDiagnosis(eventId))
        return (u'', u'', u'', u'')

    # end getPNDHospitalInfo

    def makeHtmlTable(headerInfo, data, inTwoColumn=False):
        if not data:
            data = [(u'',) * len(headerInfo)]

        if inTwoColumn:
            newLength = int(round(len(data) / 2.))
            if len(data) < newLength * 2:
                data.append((u'',) * len(headerInfo))

            headerInfo = headerInfo + [u''] + headerInfo

            data = [data[i] + (u'',) + data[i + 1] for i in xrange(newLength)]

        rowList = []
        for rowData in data:
            rowList.append(u'<tr>%s</tr>' % u'\n'.join([u'<td>%s</td>' % cellData for cellData in rowData]))
        htmlTable = u'''
                    <table border="1" cellpadding="4" style="padding:4;">
                            <tr>%(tableHeader)s</tr>
                            %(tableBody)s
                    </table>
                    ''' % {u'tableHeader': u'\n'.join([u'<th>%s</th>' % columnName for columnName in headerInfo]),
                           u'tableBody': u'\n'.join(rowList)}
        return htmlTable

    # end makeHtmlTable


    clientId = info.id
    name = formatName(info.lastName, info.firstName, info.patrName)
    birthDate = formatDate(info.birthDate)
    birthPlace = info.birthPlace
    age = calcAge(info.birthDate, atDate)
    sex = formatSex(info.sexCode)
    #    SNILS     = formatSNILS(info.SNILS)
    #    attaches  = info.get('attaches', [])
    createDate = formatDate(info.createDate)

    #    document                  = info.get('document', u'нет')
    #    compulsoryPolicy          = info.get('compulsoryPolicy', u'нет')
    #    voluntaryPolicy           = info.get('voluntaryPolicy', u'')
    #    compulsoryvoluntaryPolicy = info.get('compulsoryvoluntaryPolicy', u'нет')
    #    regAddress                = info.get('regAddress', u'не указан')
    locAddress = info.get('locAddress', u'не указан')
    work = info.get('work', u'не указано')
    #    notes                     = info.get('notes', u'')
    identification = info.get('identificationWithoutCounter', u'')
    identificationWithCursor = info.get('identificationWithCounter', u'')
    if identificationWithCursor:
        if identification: identification += u', '
        identification += identificationWithCursor
    #    quoting                   = formatClientQuoting(info.get('quoting', []))
    #    contacts                  = getClientPhones(id)
    phones = getClientPhonesEx(clientId)
    #    locationCard              = info.get('locationCard', u'')
    #    statusObservationClient   = info.get('statusObservationClient', u'')
    #    hospitalBed, busy         = getClientHospitalOrgStructureAndBeds(id)
    #    diagNames            = info.get('diagNames', u'')
    #    relative               = info.get('relative', u'')

    mkb = info.get('diagnosisMKB', u'')
    mainDiag = u'%s (%s)' % (mkb,
                             info.get('diagnosisName', u'')) if mkb else u''

    db = QtGui.qApp.db
    tableSocStatus = db.table('ClientSocStatus')
    tableSocStatusClass = db.table('rbSocStatusClass')
    tableSocStatusType = db.table('rbSocStatusType')
    queryTable = tableSocStatus.innerJoin(tableSocStatusClass,
                                          tableSocStatusClass['id'].eq(tableSocStatus['socStatusClass_id']))
    queryTable = queryTable.innerJoin(tableSocStatusType,
                                      tableSocStatusType['id'].eq(tableSocStatus['socStatusType_id']))
    cols = [tableSocStatus['begDate'],
            tableSocStatus['endDate'],
            tableSocStatusClass['code'].alias('classCode'),
            tableSocStatusClass['name'].alias('className'),
            # tableSocStatusType['regionalCode'].alias('typeRegionalCode'),
            tableSocStatusType['code'].alias('typeCode'),
            tableSocStatusType['name'].alias('typeName')
            ]
    socStatusRecordList = db.getRecordList(table=queryTable,
                                           cols=cols,
                                           where=[tableSocStatus['client_id'].eq(clientId),
                                                  tableSocStatus['deleted'].eq(0),
                                                  ],
                                           order=[tableSocStatus['begDate']])
    conviction = u''
    convictionTypeList = [u'Л_%02d' % idx for idx in xrange(14)]
    testHIV = u''
    disabilityList = []
    educationType = u''
    educationCount = u''
    family = u''
    accommodation = u''
    workStatus = u''
    facilities = []
    for record in socStatusRecordList:
        classCode = forceString(record.value('classCode'))
        typeCode = forceString(record.value('typeCode'))
        typeName = forceString(record.value('typeName'))

        begDate = forceDate(record.value('begDate'))
        endDate = forceDate(record.value('endDate'))
        if classCode == u'07':  # Судимость до обращения к психиатру
            conviction = typeName
        elif classCode == u'09':  # Обследование на ВИЧ
            if typeCode == u'ОбВИЧ_3':  # Результат положительный
                testHIV = [typeName, u'Дата выявления впервые: %s' % formatDate(begDate)]
            else:
                testHIV = typeName
        elif classCode == u'01':  # Льготы
            if typeCode in convictionTypeList:  # Инвалидности
                disabilityList.append((formatDate(begDate), typeName, formatDate(endDate), u'', u''))
            facilities.append(typeName)
        elif classCode == u'05':  # Образование
            educationType = typeName
        elif classCode == u'06':  # Закончено классов
            educationCount = u'Закончено классов: %s' % typeName
        elif classCode == u'04':  # Семейное положение
            family = typeName
        elif classCode == u'03':  # Условия проживания
            accommodation = typeName
        elif classCode == u'02':  # Социальный статус
            workStatus = typeName
    disability = makeHtmlTable([u'Дата установки или пересмотра',
                                u'Группа инвалидности',
                                u'Срок очередного переосви-',
                                u'Место работы',
                                u'Степень утраты работоспособ.'],
                               disabilityList)
    education = [educationType,
                 educationCount] if educationType else u''

    tableDiagnosis = db.table('Diagnosis')
    cols = ['MIN(%s) AS minSetDate' % tableDiagnosis['setDate'].name(),
            'MAX(%s) AS maxEndDate' % tableDiagnosis['endDate'].name(),
            tableDiagnosis['MKB']]
    diagnosisInfo = []
    diagnosisRecordList = db.getRecordListGroupBy(table=tableDiagnosis,
                                                  cols=cols,
                                                  where=[tableDiagnosis['client_id'].eq(clientId),
                                                         tableDiagnosis['deleted'].eq(0)],
                                                  group=[tableDiagnosis['MKB']],
                                                  order=u'minSetDate ASC')
    for record in diagnosisRecordList:
        setDate = forceDate(record.value('minSetDate'))
        mkb = forceString(record.value('MKB'))
        diagnosisInfo.append((formatDate(setDate), mkb, mkb.split('.')[0]))
    diagnosis = makeHtmlTable([u'Число, месяц, год',
                               u'Диагноз',
                               u'Код основного заболевания'], diagnosisInfo)

    tableTempInvalid = db.table('TempInvalid')
    cols = [tableTempInvalid['caseBegDate'],
            tableTempInvalid['endDate'],
            tableTempInvalid['duration']]
    tempInvalidInfo = []
    tempInvalidRecordList = db.getRecordList(table=tableTempInvalid,
                                             cols=cols,
                                             where=[tableTempInvalid['client_id'].eq(clientId)],
                                             order=tableTempInvalid['caseBegDate'])
    for record in tempInvalidRecordList:
        begDate = forceDate(record.value('caseBegDate'))
        endDate = forceDate(record.value('endDate'))
        duration = forceInt(record.value('duration'))

        tempInvalidInfo.append((len(tempInvalidInfo) + 1, formatDate(begDate), formatDate(endDate), duration))
    tempInvalid = makeHtmlTable([u'№ п/п',
                                 u'Дата открытия б/листа',
                                 u'Дата закрытия б,листа',
                                 u'Число дней ВН'],
                                tempInvalidInfo)

    # TODO: atronah: надо брать самую раннюю дату всех диагнозов или только основного?
    minDiagBegDate = formatDate(forceDate(diagnosisRecordList[0].value('minSetDate'))) if diagnosisRecordList else u''

    tableClientAttach = db.table('ClientAttach')
    tableClientAttachType = db.table('rbAttachType')
    tableOrgStructure = db.table('OrgStructure')
    tableDetachmentReason = db.table('rbDetachmentReason')
    queryTable = tableClientAttach.innerJoin(tableClientAttachType,
                                             tableClientAttachType['id'].eq(tableClientAttach['attachType_id']))
    queryTable = queryTable.leftJoin(tableOrgStructure,
                                     tableOrgStructure['id'].eq(tableClientAttach['orgStructure_id']))
    queryTable = queryTable.leftJoin(tableDetachmentReason,
                                     tableDetachmentReason['id'].eq(tableClientAttach['detachment_id']))
    cols = [tableClientAttachType['code'].alias('attachTypeCode'),
            tableClientAttachType['name'].alias('attachTypeName'),
            tableClientAttach['begDate'].alias('attachBegDate'),
            tableOrgStructure['name'].alias('orgStructureName'),
            tableOrgStructure['id'].alias('orgStructureId'),
            tableDetachmentReason['name'].alias('detachmentReason')]

    attachesRecordList = db.getRecordList(table=queryTable,
                                          cols=cols,
                                          where=[tableClientAttach['client_id'].eq(clientId),
                                                 tableClientAttach['deleted'].eq(0)],
                                          order=tableClientAttach['begDate'])
    formatDate(forceDate(attachesRecordList[0].value('attachBegDate'))) if attachesRecordList else u''
    orgStructure = u''
    orgStructureId = None
    DAttachTypeList = ['2', '10']
    D7AttachTypeList = ['30', '31']
    KAttachTypeList = ['3']
    ADNAttachTypeList = ['4']
    APLAttachTypeList = ['5']
    categoryList = []
    dynamicObservationInfo = []
    leave = u''
    minAttachBegDate = u''
    for record in attachesRecordList:
        attachTypeCode = forceString(record.value('attachTypeCode'))
        attachTypeName = forceString(record.value('attachTypeName'))
        attachBegDate = forceDate(record.value('attachBegDate'))
        if not minAttachBegDate and attachBegDate.isValid() and not attachBegDate.isNull():
            minAttachBegDate = formatDate(attachBegDate)
        if attachTypeCode == '1':
            orgStructure = forceString(record.value('orgStructureName'))
            orgStructureId = forceRef(record.value('orgStructureId'))
        elif attachTypeCode in DAttachTypeList + D7AttachTypeList:
            if u'Д' not in categoryList:
                categoryList.append(u'Д')
            dynamicObservationInfo.append((u'Д', attachTypeName, formatDate(attachBegDate)))
        elif attachTypeCode in KAttachTypeList:
            if u'К' not in categoryList:
                categoryList.append(u'К')
            dynamicObservationInfo.append((u'К', attachTypeName, formatDate(attachBegDate)))
        elif attachTypeCode in ADNAttachTypeList:
            if u'АДН' not in categoryList:
                categoryList.append(u'АДН')
            dynamicObservationInfo.append((u'АДН', attachTypeName, formatDate(attachBegDate)))
        elif attachTypeCode in APLAttachTypeList:
            if u'АПЛ' not in categoryList:
                categoryList.append(u'АПЛ')
            dynamicObservationInfo.append((u'АДН', attachTypeName, formatDate(attachBegDate)))

    for record in attachesRecordList[::-1]:  # Просмотр в обратном порядке, так как сортировка по возрастанию begDate
        if attachTypeCode == '7':
            detachmentReason = forceString(record.value('detachmentReason'))
            leave = detachmentReason
            break
        elif attachTypeCode == '8':
            detachmentReason = forceString(record.value('detachmentReason'))
            doctor = u''
            if orgStructureId:
                doctor = forceString(db.translate('vrbPersonWithSpeciality', 'orgStructure_id', orgStructureId, 'code'))
            leave = [detachmentReason,
                     u'Дата смерти: %s' % formatDate(attachBegDate),
                     u'Код врача: %s' % doctor]
            break

    dynamicObservation = makeHtmlTable([u'Вид амбул. помощи',
                                        u'Группа дисп. наблюдения',
                                        u'Помощь оказывается с'],
                                       dynamicObservationInfo)

    compulsoryTreatmentInfo = []
    hospitalInfo = []
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')
    queryTable = tableEvent.innerJoin(tableEventType, tableEventType['id'].eq(tableEvent['eventType_id']))
    cols = [tableEventType['code'].alias('eventTypeCode'),
            tableEvent['id'].alias('eventId')]
    eventRecordList = db.getRecordList(table=queryTable,
                                       cols=cols,
                                       where=[tableEvent['client_id'].eq(clientId),
                                              tableEvent['deleted'].eq(0),
                                              tableEventType['code'].notlike('0')],
                                       # Кроме событий "График" (Расписание врачей)
                                       order=tableEvent['setDate'])
    for record in eventRecordList:
        eventTypeCode = forceString(record.value('eventTypeCode'))
        eventId = forceRef(record.value('eventId'))
        if eventTypeCode == 'epicr':
            pass  # TODO: atronah: implement
            compulsoryTreatmentInfo.append()
        elif eventTypeCode in [u'08', u'09', u'10']:  # Д7, Д7Д, Д7Р
            hospitalInfo.append((len(hospitalInfo) + 1,) + getPNDHospitalInfo(eventId))

    hospital = makeHtmlTable([u'№ п/п',
                              u'Цель госпитализации',
                              u'Дата поступления',
                              u'Дата выбытия',
                              u'Диагноз'],
                             hospitalInfo)

    tableVisit = db.table('Visit')
    tableScene = db.table('rbScene')
    tablePersonWS = db.table('vrbPersonWithSpeciality')
    queryTable = tableVisit.innerJoin(tableScene, tableScene['id'].eq(tableVisit['scene_id']))
    queryTable = queryTable.innerJoin(tableEvent, tableEvent['id'].eq(tableVisit['event_id']))
    queryTable = queryTable.innerJoin(tablePersonWS, tablePersonWS['id'].eq(tableVisit['person_id']))
    cols = [tableVisit['date'],
            tableScene['code'].alias('sceneCode'),
            tablePersonWS['code'].alias('personCode')]
    visitRecordList = db.getRecordList(table=queryTable,
                                       cols=cols,
                                       where=[tableEvent['client_id'].eq(clientId),
                                              tableEvent['deleted'].eq(0),
                                              tableVisit['deleted'].eq(0)],
                                       order='%s DESC' % tableVisit['date'].name())

    visitInfo = []
    for record in visitRecordList:
        date = forceDate(record.value('date'))
        sceneCode = forceString(record.value('sceneCode'))
        personCode = forceString(record.value('personCode'))
        visitInfo.append((formatDate(date),
                          u'X' if sceneCode == u'2' else u'',
                          u'X' if sceneCode in [u'1', u'4'] else u'',
                          personCode,
                          u''))
    visits = makeHtmlTable([u'Дата',
                            u'На дому',
                            u'В ПНД',
                            u'Код врача',
                            u'Изменившееся пункты'],
                           visitInfo,
                           True)

    oodEventsInfo = []
    suicidalIndo = []
    tableClientIdentification = db.table('ClientIdentification')
    tableAccountingSystem = db.table('rbAccountingSystem')
    queryTable = tableClientIdentification.innerJoin(tableAccountingSystem, tableAccountingSystem['id'].eq(
        tableClientIdentification['accountingSystem_id']))
    cols = [tableAccountingSystem['code'].alias('accountingSystemCode'),
            tableClientIdentification['checkDate'],
            tableClientIdentification['identifier']]
    identificationRecordList = db.getRecordList(table=queryTable,
                                                cols=cols,
                                                where=[tableClientIdentification['client_id'].eq(clientId),
                                                       tableClientIdentification['deleted'].eq(0),
                                                       ],
                                                order=tableClientIdentification['checkDate'])
    for record in identificationRecordList:
        accountingSystemCode = forceStringEx(record.value('accountingSystemCode'))
        checkDate = forceDate(record.value('checkDate'))
        identifier = forceString(record.value('identifier'))
        if accountingSystemCode in [u'ОДД', u'ООД']:  # первый вариант - опечатка, сделанная при заливке в базу
            oodEventsInfo.append((len(oodEventsInfo) + 1, formatDate(checkDate), identifier))
        elif not accountingSystemCode:
            suicidalIndo.append((len(suicidalIndo) + 1, formatDate(checkDate)))

    oodEvents = makeHtmlTable([u'№ п/п',
                               u'Дата совершения ООД',
                               u'Статья УК РФ'],
                              oodEventsInfo)
    suicidal = makeHtmlTable([u'№ п/п',
                              u'Дата совершения'],
                             suicidalIndo)

    # Получение данных по лекарствам
    tableAction = db.table('Action')
    tableActionType = db.table('ActionType')
    tableAPDose = db.table('ActionProperty').alias(u'AP_Dose')
    tableAPTypeDose = db.table('ActionPropertyType').alias(u'APT_Dose')
    tableAPStringDose = db.table('ActionProperty_String').alias(u'APV_Dose')
    tableAPTypeQuantity = db.table('ActionPropertyType').alias(u'APT_Quantity')
    tableAPStringQuantity = db.table('ActionProperty_String').alias(u'APV_Quantity')
    tableAPQuantity = db.table('ActionProperty').alias(u'AP_Quantity')
    queryTable = tableAction.innerJoin(tableEvent, [tableEvent['id'].eq(tableAction['event_id']),
                                                    tableEvent['client_id'].eq(clientId)])
    queryTable = queryTable.innerJoin(tableActionType, [tableActionType['id'].eq(tableAction['actionType_id']),
                                                        tableActionType['deleted'].eq(0),
                                                        tableActionType['class'].eq(2)])
    queryTable = queryTable.innerJoin(tableAPTypeDose, [tableAPTypeDose['actionType_id'].eq(tableActionType['id']),
                                                        tableAPTypeDose['name'].like(u'Суточная доза'),
                                                        tableAPTypeDose['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableAPDose, [tableAPDose['type_id'].eq(tableAPTypeDose['id']),
                                                    tableAPDose['action_id'].eq(tableAction['id']),
                                                    tableAPDose['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableAPStringDose, tableAPStringDose['id'].eq(tableAPDose['id']))

    queryTable = queryTable.innerJoin(tableAPTypeQuantity,
                                      [tableAPTypeQuantity['actionType_id'].eq(tableActionType['id']),
                                       tableAPTypeQuantity['name'].like(u'Количество'),
                                       tableAPTypeQuantity['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableAPQuantity, [tableAPQuantity['type_id'].eq(tableAPTypeQuantity['id']),
                                                        tableAPQuantity['action_id'].eq(tableAction['id']),
                                                        tableAPQuantity['deleted'].eq(0)])
    queryTable = queryTable.innerJoin(tableAPStringQuantity, tableAPStringQuantity['id'].eq(tableAPQuantity['id']))
    cols = [tableActionType['name'],
            tableAction['begDate'],
            tableAction['endDate'],
            tableAPStringDose['value'].alias('dose'),
            tableAPStringDose['value'].alias('quantity')
            ]

    drugsInfo = []
    drugActionRecordList = db.getRecordList(table=queryTable,
                                            cols=cols,
                                            where=[tableAction['deleted'].eq(0)],
                                            order=u'%s DESC' % tableAction['begDate'].name())
    for record in drugActionRecordList:
        begDate = forceDate(record.value('begDate'))
        endDate = forceDate(record.value('endDate'))
        caption = forceString(record.value('name'))
        dose = forceString(record.value('dose'))
        quantity = forceString(record.value('quantity'))
        drugsInfo.append((begDate,
                          endDate,
                          u'',
                          caption,
                          dose,
                          quantity
                          ))
    drugs = makeHtmlTable([u'Дата назначения',
                           u'Дата отмены',
                           u'Б/платно',
                           u'Название препарата',
                           u'Суточная доза',
                           u'Количество упаковок'
                           ],
                          drugsInfo)

    infoBlocks = [(u'Ф.И.О.:', name, u''),
                  (u'Дата рождения: ', u'%s (%s)' % (birthDate, age), u''),
                  (u'Место рождения:', birthPlace, u''),
                  (u'Пол:', sex, u''),
                  (u'Проживает:', locAddress, u''),
                  (u'Район:', u'', u''),
                  (u'Телефон:', phones, u''),
                  (u'Дата открытия карты:', createDate, u'b'),
                  (u'Дата начала заболевания:', minDiagBegDate, u''),
                  (u'Взят под наблюдение:', minAttachBegDate, u''),
                  (u'Участок:', orgStructure, u''),
                  (u'', ', '.join(categoryList), u''),
                  (u'Основной диагноз:', mainDiag, u'b'),
                  (u'Дополнительный диагноз:', u'', u''),
                  (u'Работает:', workStatus, u''),
                  (u'Место работы или учебы, должность:', work, u''),
                  (u'Законный представитель:', u'', u''),
                  (u'Категория льготы:', facilities, u''),
                  (u'Установлена опека:', u'', u''),
                  (u'Недееспособен', u'', u'b'),
                  (u'Судимость до обращения к психиатру:', conviction, u'bi'),
                  (u'Обследование на ВИЧ:', testHIV, u'bi'),

                  (u'Принудительное лечение:', u'', u'bi'),
                  (u'Динамика состояния:', u'', u'bi'),
                  (u'Инвалидность:', disability, u'bi'),
                  (u'ООД:', oodEvents, u'bi'),
                  (u'Суицидальные попытки:', suicidal, u'bi'),
                  (u'Cведения о госпитализациях:', hospital, u'bi'),
                  (u'Динамика наблюдения:', dynamicObservation, u'bi'),
                  (u'Причины снятия с учета:', leave, u''),

                  (u'Образование', education, u'bi'),
                  (u'Семейное положение>', family, u'bi'),
                  (u'Условия проживания', accommodation, u'bi'),
                  (u'Диагноз с датой установки и пересмотра', diagnosis, u'bi'),
                  (u'Отмена о случаях временной нетрудоспособности', tempInvalid, u'bi'),
                  (u'Освидетельствование', u'', u'bi'),
                  (u'Контроль посещений', visits, u'bi'),
                  (u'Назначенные лекарства', drugs, u'bi')
                  ]

    htmlBlocks = []
    for idx, (title, data, mods) in enumerate(infoBlocks):
        if isinstance(data, list):
            data = u'<br />'.join(data)
        elif not data:
            continue
        htmlBlocks.append(u'''<div>
                                    <span style = "%(fontWeight)s %(fontStyle)s">%(idx)s. %(title)s&nbsp;&nbsp;&nbsp;</span>%(data)s
                              </div>''' % {'fontWeight': 'font-weight: bold;' if u'b' in mods else u'',
                                           'fontStyle': 'font-style: italic;' if u'i' in mods else u'',
                                           u'idx': idx + 1,
                                           u'title': title,
                                           u'data': data}
                          )
    result = """
            <html>
                <head>
                    <style>
                        .inlineBlock {
                            display: inline-block;
                        }
                    </style>
                </head>
                <body>
                    %s
                </body>
            </html>
    """ % ''.join(htmlBlocks)
    return result


# separator is the string that will be inserted _BEFORE_ prefix and text
def viewDict(text='', prefix=u'', sep='<BR>'):
    return {'text': text, 'prefix': prefix, 'sep': sep}


def getViewForItem(vdict):
    sep = vdict['sep'] or u''
    prefix = vdict['prefix'] or u''
    text = vdict['text'] or u''
    return sep + prefix + text


def getView(view, keys):
    if not keys: return u''
    first = view[keys[0]]['prefix'] + view[keys[0]]['text']
    rest = ''.join(map(getViewForItem, [view[k] for k in keys[1:]]))
    return first + rest


def color(color, s): return u'<font color=%s>%s</font>' % (color, s)


def bold(s): return u'<B>%s</B>' % s


def formatBannerLocationCard(locationCard):
    bannerLocationCard = ''
    if locationCard and len(locationCard) == 2:
        bannerLocationCard = u''' [А/карта: <B><font color=%s>%s</font></B>]''' % (locationCard[1], locationCard[0])
    return bannerLocationCard


def formatBannerStatusObservation(statusObservationClient):
    bannerStatusObservation = ''
    if statusObservationClient and len(statusObservationClient) == 2:
        bannerStatusObservation = u''' [Статус: <B><font color=%s>%s</font></B>] ''' % (
        statusObservationClient[1], statusObservationClient[0])
    return bannerStatusObservation


def formatAttachesAndMonitoring(attaches, monitorings, atDate):
    attachesAndMonitoring = formatAttachesAsHTML(attaches, atDate)
    isExistsOutcome = False
    for attach in attaches:
        if attach['outcome']:
            isExistsOutcome = True
            break
    if not isExistsOutcome:
        monitoringInfo = monitorings[-1] if monitorings else None
        if monitoringInfo:
            attachesAndMonitoring += u'%s<font color=%s>%s(%s) с %s</font>' % (
            u'' if not attachesAndMonitoring else u', ',
            'red' if monitoringInfo['kind'] in [u'АПЛ', u'АДН'] else 'blue',
            monitoringInfo['kind'],
            monitoringInfo['frequence'],
            formatDate(monitoringInfo['setDate']))
    return attachesAndMonitoring


def formatIdentification(identification, identificationWithCounter):
    result = identification
    if identificationWithCounter:
        if identification: result += u', '
        result += identificationWithCounter
    if result: result += '<BR>'
    return result


def formatBed(id):
    hospitalBed, busy = getClientHospitalOrgStructureAndBeds(id)
    if hospitalBed:
        bed = u' госпитализация: <B><font color=%s>%s</font></B>' % ('green' if busy else 'blue', hospitalBed)
    else:
        bed = ''
    return bed


def formatDiagnos(diagnosisMKB, diagnosisName):
    if QtGui.qApp.isPNDDiagnosisMode():
        return u'<font color=blue>Диагноз: %s %s</font><BR>' % (diagnosisMKB, diagnosisName)
    return u''


allClientBannerViewKeysForKaz = [
    'name', 'birthDate', 'age', 'sex', 'id',
    'bannerLocationCard', 'bannerStatusObservation', 'bed',
    'status', 'identification', 'quoting',
    'attachesAndMonitoring', 'strDiagnos', 'incapacity',
    'surveyresult', 'document',
    'regAddress', 'locAddress', 'work', 'relative', 'phones',
    'birthPlace', 'notes', 'checkDate', 'createDate', 'hospitalisation']

allClientBannerViewKeys = [
    'name', 'birthDate', 'age', 'sex', 'id',
    'bannerLocationCard', 'bannerStatusObservation', 'bed',
    'status', 'identification', 'quoting', 'SNILS',
    'attachesAndMonitoring', 'strDiagnos', 'incapacity',
    'surveyresult', 'document', 'compulsoryvoluntaryPolicy',
    'regAddress', 'locAddress', 'work', 'relative', 'phones',
    'birthPlace', 'notes', 'checkDate', 'createDate', 'hospitalisation',
    'codeDisp', 'begDisp', 'moDisp', 'deattachReason']


def formatClientBanner(info, atDate=None, keys=None):
    view = LazySmartDict()
    regionKaz = QtGui.qApp.defaultKLADR().startswith('90')
    # XXX: for style customization, make the list of style modifiers as another
    # separate viewDict value. The flag indicating that we do not need the
    # header for an empty text value can be provided as well.
    view.name = lambda: viewDict(bold(formatName(info.lastName, info.firstName, info.patrName)), '', ', ')
    view.birthDate = lambda: viewDict(bold(formatDate(info.birthDate)), u'дата рождения: ', ', ')
    view.age = lambda: viewDict('', '', ' ') if formatDate(info.birthDate) == u'' else viewDict(
        '(' + calcAge(info.birthDate, atDate) + ')', '', ' ')
    view.sex = lambda: viewDict(bold(formatSex(info.sexCode)), u'пол: ', ' ')
    view.id = lambda: viewDict(bold(color('blue', info.id)), u'код: ', ' ')
    view.bannerLocationCard = lambda: viewDict(formatBannerLocationCard(info.get('locationCard') or u''), '', '')
    view.bannerStatusObservation = lambda: viewDict(
        formatBannerStatusObservation(info.get('statusObservationClient') or u''), '', '')
    view.bed = lambda: viewDict(formatBed(info.id), '', '')
    view.status = lambda: viewDict(bold(formatSocStatuses(info.get('socStatuses') or [])), u'статус: ', ' ')
    view.identification = lambda: viewDict(formatIdentification(info.get('identificationWithCounter') or u'',
                                                                info.get('identificationWithoutCounter') or u''), '',
                                           '')
    view.quoting = lambda: viewDict(formatClientQuoting(info.get('quoting') or []) or '', u'<I>Квоты:</I> ',
                                    '<BR>' if info.get('quoting') else '')
    if (not regionKaz):
        view.SNILS = lambda: viewDict(bold(formatSNILS(info.SNILS)), u'СНИЛС: ', '')
    view.attachesAndMonitoring = lambda: viewDict(
        bold(formatAttachesAndMonitoring(info.get('attaches') or [], info.get('monitorings') or [], atDate) or u''),
        u'Прикрепление: ', '<BR>')
    view.strDiagnos = lambda: viewDict(formatDiagnos(info.get('diagnosisMKB') or u'', info.get('diagnosisName') or u''),
                                       '', '')
    view.incapacity = lambda: viewDict(bold(color('red', info.get('incapacity') or u'')), '',
                                       '<BR>' if info.get('incapacity') else '')
    view.surveyresult = lambda: viewDict(bold(color('red', info.get('surveyresult') or u'')), '',
                                         '<BR>' if info.get('surveyresult') else '')
    view.document = lambda: viewDict(bold(info.get('document') or u'нет'), u'Документ: ')
    if (not regionKaz):
        view.compulsoryvoluntaryPolicy = lambda: viewDict(info.get('compulsoryvoluntaryPolicy') or u'нет',
                                                          u'Полис ОМС ', ', ')
    view.regAddress = lambda: viewDict(bold(info.get('regAddress') or u'не указан'), u'Адрес регистрации: ')
    view.locAddress = lambda: viewDict(bold(info.get('locAddress') or u'не указан'), u'Адрес проживания: ')

    if info.get('attendingPerson'):
        view.attendingPerson = lambda: viewDict(bold(info.get('attendingPerson') or u'не указан'), u'Лечащий врач: ')
        if 'attendingPerson' not in allClientBannerViewKeys:
            allClientBannerViewKeys.insert(allClientBannerViewKeys.index('locAddress'), 'attendingPerson')
    elif 'attendingPerson' in allClientBannerViewKeys:
        allClientBannerViewKeys.remove('attendingPerson')

    if info.get('disabilityGroup'):
        view.disabilityGroup = lambda: viewDict(bold(info.get('disabilityGroup') or u'не указана'), u'Инвалидность: группа ')
        if 'disabilityGroup' not in allClientBannerViewKeys:
            allClientBannerViewKeys.insert(allClientBannerViewKeys.index('locAddress'), 'disabilityGroup')
    elif 'disabilityGroup' in allClientBannerViewKeys:
        allClientBannerViewKeys.remove('disabilityGroup')

    view.work = lambda: viewDict(bold(info.get('work') or u'не указано'), u'Занятость: ')
    view.relative = lambda: viewDict(info.get('relative') or u'', '', '<BR>' if info.get('relative') else '')
    view.phones = lambda: viewDict(bold(getClientPhonesEx(info.id)), u'Телефоны: ')
    view.birthPlace = lambda: viewDict(bold(info.birthPlace), u'Место рождения: ')
    view.deattachReason = lambda: viewDict(bold(info.deattachReason), u'Причины открепления: ')
    view.notes = lambda: viewDict(bold(info.get('notes') or u''), u'Примечания: ')
    view.checkDate = lambda: viewDict(bold(info.get('checkDate')), u'Дата подтверждения ЕИС: ')
    view.createDate = lambda: viewDict(bold(formatDate(info.createDate)), u'Дата регистрации пациента в МИС: ')
    view.hospitalisation = lambda: viewDict(bold(color('blue', getClientHospitalisation(info.id))),
                                            u'Выписки пациента: ')
    dispRecord = getDispansInfo(info.id)
    view.codeDisp = lambda: viewDict(bold(dispRecord['code'] or u'нет'), u'Код диспансеризации:')
    view.begDisp = lambda: viewDict(bold(getDispanserizationDateRange(dispRecord) or u'нет'), u'Дата:')
    view.moDisp = lambda: viewDict(bold(dispRecord['codeMO'] or u'нет'),
                                   u'Код МО, проводивший диспансеризацию/профосмотр:')

    # XXX: The order is of importance!
    if regionKaz:
        if keys is None: keys = allClientBannerViewKeysForKaz

    else:
        if keys is None: keys = allClientBannerViewKeys

    bannerHTML = getView(view, keys)
    clientBanner = u'<HTML><BODY>%s</BODY></HTML>' % bannerHTML
    return clientBanner


def formatClientString(info, atDate=None):
    id = info.id
    name = formatName(info.lastName, info.firstName, info.patrName)
    birthDate = formatDate(info.birthDate)
    birthPlace = info.birthPlace
    deattachReason = info.deattachReason
    age = calcAge(info.birthDate, atDate)
    sex = formatSex(info.sexCode)
    SNILS = formatSNILS(info.SNILS)
    attaches = info.get('attaches', [])
    socStatuses = info.get('socStatuses', [])

    document = info.get('document', u'нет')
    compulsoryPolicy = info.get('compulsoryPolicy', u'нет')
    voluntaryPolicy = info.get('voluntaryPolicy', u'')
    regAddress = info.get('regAddress', u'не указан')
    locAddress = info.get('locAddress', u'не указан')
    work = info.get('work', u'не указано')
    notes = info.get('notes', u'')
    identification = info.get('identification', u'')
    phones = getClientPhonesEx(id)
    hospitalBed, busy = getClientHospitalOrgStructureAndBeds(id)
    dispRec = getDispansInfo(id)
    codeDisp = dispRec['code'] if dispRec else '-'
    begDisp = dispRec['date_begin'] if dispRec else '-'
    endDisp = dispRec['date_end'] if dispRec else '-'
    moDisp = dispRec['codeMO'] if dispRec else '-'
    if hospitalBed:
        bed = u' госпитализация: %s %s' % (busy, hospitalBed)
    else:
        bed = ''

    if QtGui.qApp.defaultKLADR().startswith('90'):
        bannerHTML = u'''%s, дата рождения: %s (%s) пол: %s код: %s %s статус: %s %s, прикрепление: %s Документ: %s, Адрес регистрации: %s Адрес проживания: %s Занятость: %s''' % (
            name, birthDate, age, sex, id, bed, formatSocStatuses(socStatuses),
            ((u' %s' % identification) if identification else ''),
            formatAttachesAsHTML(attaches, atDate),
            document,
            regAddress,
            locAddress,
            work)
    else:
        bannerHTML = u'''%s, дата рождения: %s (%s) пол: %s код: %s %s статус: %s %s СНИЛС: %s, прикрепление: %s, Документ: %s, полис ОМС: %s %s %s Адрес регистрации: %s Адрес проживания: %s Занятость: %s, Код диспансеризации: %s, Дата с: %s по: %s, СМО проводившая диспансеризацию: %s''' % (
            name, birthDate, age, sex, id, bed, formatSocStatuses(socStatuses),
            ((u' %s' % identification) if identification else ''),
            SNILS, formatAttachesAsHTML(attaches, atDate),
            document, compulsoryPolicy, (u', полис ДМС: ' if voluntaryPolicy else ''), voluntaryPolicy,
            regAddress,
            locAddress,
            work,
            codeDisp,
            begDisp,
            endDisp,
            moDisp)

    if phones:
        bannerHTML += u'Телефоны: %s' % phones
    if birthPlace:
        bannerHTML += u'Место рождения: <B>%s</B><BR>' % birthPlace
    if deattachReason:
        bannerHTML += u'Причины открепления: <B>%s</B><BR>' % deattachReason
    if notes:
        bannerHTML += u'Примечания: %s' % notes

    try:
        tableClientIdentification = QtGui.qApp.db.table('ClientIdentification')
        identDate = QtGui.qApp.db.getRecordEx(
            tableClientIdentification,
            'max(checkDate)',
            'client_id= %d and accountingSystem_id in (1, 2)' % id)
        if identDate:
            checkDate = identDate.value(0)
            if checkDate:
                bannerHTML += u'Дата подтверждения ЕИС: %s' % forceString(checkDate)
    except:
        QtGui.qApp.logCurrentException()

    clientBanner = u'%s' % bannerHTML
    return clientBanner


def getClientContextData(clientId):
    from Events.TempInvalidInfo import CTempInvalidInfoList
    clientInfo = getClientInfo2(clientId)
    getTempInvalidList = lambda begDate=None, endDate=None, types=None: CTempInvalidInfoList._get(clientInfo.context,
                                                                                                  clientId, begDate,
                                                                                                  endDate, types)
    data = {'client': clientInfo,
            'getTempInvalidList': getTempInvalidList,
            'tempInvalids': getTempInvalidList()}
    return data


def getStaffCondition(clientIdFieldName='Client.id'):
    return """EXISTS(SELECT ClientWork.id
                    FROM ClientWork
                    WHERE ClientWork.id = getClientWorkId(%s)
                        AND ClientWork.org_id = %s
                    )
           """ % (clientIdFieldName, QtGui.qApp.currentOrgId())


######################################################
# mixin для проверки применимости врача/подразделения
# к данному пациенту
######################################################

class CCheckNetMixin:
    def __init__(self):
        self.reset()
        self.connect(QtGui.qApp, QtCore.SIGNAL('dbConnectionChanged(bool)'), self.onConnectionChanged)

    def reset(self):
        self.mapSpecialityIdToSpecialityConstraint = {}
        self.mapPersonIdToSpecialityId = {}
        self.mapPersonIdToOrgId = {}
        self.mapPersonIdToOrgStructureId = {}
        self.mapOrgStructureIdToNetId = {}
        self.mapNetIdToNet = {}

    def onConnectionChanged(self, state):
        if not state:
            self.reset()

    def _getPersonIds(self, personId):
        db = QtGui.qApp.db
        record = db.getRecord('Person', 'speciality_id, org_id, orgStructure_id', personId)
        if record:
            specialityId = forceRef(record.value(0))
            orgId = forceRef(record.value(1))
            orgStructureId = forceRef(record.value(2))
        else:
            specialityId = None
            orgId = None
            orgStructureId = None
        self.mapPersonIdToSpecialityId[personId] = specialityId
        self.mapPersonIdToOrgId[personId] = orgId
        self.mapPersonIdToOrgStructureId[personId] = orgStructureId

    def getPersonSpecialityId(self, personId):
        db = QtGui.qApp.db
        if personId not in self.mapPersonIdToOrgStructureId:
            self._getPersonIds(personId)
        return self.mapPersonIdToSpecialityId[personId]

    def getSpecialityConstraint(self, specialityId):
        if specialityId in self.mapSpecialityIdToSpecialityConstraint:
            return self.mapSpecialityIdToSpecialityConstraint[specialityId]
        else:
            specialityConstraint = CSpecialityConstraint(specialityId)
            self.mapSpecialityIdToSpecialityConstraint[specialityId] = specialityConstraint
            return specialityConstraint

    def getPersonOrgId(self, personId):
        db = QtGui.qApp.db
        if personId not in self.mapPersonIdToOrgId:
            self._getPersonIds(personId)
        return self.mapPersonIdToOrgId[personId]

    def getPersonOrgStructureId(self, personId):
        db = QtGui.qApp.db
        if personId not in self.mapPersonIdToOrgStructureId:
            self._getPersonIds(personId)
        return self.mapPersonIdToOrgStructureId[personId]

    def getOrgStructureNetId(self, orgStructureId):
        if orgStructureId in self.mapOrgStructureIdToNetId:
            return self.mapOrgStructureIdToNetId[orgStructureId]
        else:
            netId = getOrgStructureNetId(orgStructureId)
            self.mapOrgStructureIdToNetId[orgStructureId] = netId
            return netId

    def getNet(self, netId):
        if netId in self.mapNetIdToNet:
            return self.mapNetIdToNet[netId]
        else:
            net = CNet(netId)
            self.mapNetIdToNet[netId] = net
            return net

    def getOrgStructureNet(self, orgStructureId):
        return self.getNet(self.getOrgStructureNetId(orgStructureId))

    def getPersonSpecialityConstraint(self, personId):
        return self.getSpecialityConstraint(self.getPersonSpecialityId(personId))

    def getPersonNet(self, personId):
        return self.getNet(self.getOrgStructureNetId(self.getPersonOrgStructureId(personId)))

    def getClientSexAndAge(self, clientId):
        db = QtGui.qApp.db
        table = db.table('Client')
        record = db.getRecord(table, 'sex, birthDate', clientId)
        if record:
            clientSex = forceInt(record.value('sex'))
            clientBirthDate = forceDate(record.value('birthDate'))
            clientAge = calcAgeTuple(clientBirthDate, QtCore.QDate.currentDate())
            return clientSex, clientAge
        else:
            return None, None


        #    def checkNetAppicable(self, net, clientId):
        #        if net.sex or net.age:
        #            clientSex, clientAge = self.getClientSexAndAge(clientId)
        #            return not clientSex or net.applicable(clientSex, clientAge)
        #        return True


        #    def checkOrgStructureNetAppicable(self, orgStructureId, clientId):
        #        return self.checkNetAppicable(self.getOrgStructureNet(orgStructureId), clientId)

    def checkClientAttendace(self, personId, clientId):
        net = self.getPersonNet(personId)
        specialityConstraint = self.getPersonSpecialityConstraint(personId)
        if net.constrain() or specialityConstraint.constrain():
            clientSex, clientAge = self.getClientSexAndAge(clientId)
            return specialityConstraint.applicable(clientSex, clientAge) and net.applicable(clientSex, clientAge)
        return True

    def checkClientAttendaceEx(self, personId, clientSex, clientAge):
        net = self.getPersonNet(personId)
        specialityConstraint = self.getPersonSpecialityConstraint(personId)
        if net.constrain() or specialityConstraint.constrain():
            return specialityConstraint.applicable(clientSex, clientAge) and net.applicable(clientSex, clientAge)
        return True

    def confirmClientAttendace(self, widget, personId, clientId):
        message = u'Пациент не относится к лицам, обслуживаемым указанным врачом.\nВсё равно продолжить?'
        return QtGui.QMessageBox.critical(widget,
                                          u'Внимание!',
                                          message,
                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                          QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes

    def checkClientAttach(self, personId, clientId, date, boolCreateOrder=False):
        def _isAttachActive(attach):
            if not attach:
                return False
            return not (attach['outcome']
                        or attach['endDate'] and (forceDate(date) if date else QtCore.QDate.currentDate()) >= attach[
                            'endDate']
                        or attach['orgStructure_id'] and self.getPersonOrgStructureId(
                personId) not in getOrgStructureDescendants(attach['orgStructure_id'])
                        or attach['LPU_id'] and self.getPersonOrgId(personId) != attach['LPU_id']
                        )

        isStrict = QtGui.qApp.isStrictAttachCheckOnEventCreation()
        temporary = getAttachRecord(clientId, True)
        if isStrict and not (_isAttachActive(temporary) or _isAttachActive(getAttachRecord(clientId, False))):
            QtGui.QMessageBox.critical(self,
                                       u'Внимание!',
                                       u'У этого пациента нет подходящего прикрепления',
                                       QtGui.QMessageBox.Ok,
                                       QtGui.QMessageBox.Ok)
            return False

        if temporary:
            attachTypeId = temporary.get('attachTypeId', None)
            code = temporary.get('code', u'')
            name = temporary.get('name', u'')
            if attachTypeId:
                db = QtGui.qApp.db
                tablePerson = db.table('Person')
                tableOrgStructure = db.table('OrgStructure')
                tableOSDA = db.table('OrgStructure_DisabledAttendance')
                table = tablePerson.innerJoin(tableOSDA, tableOSDA['master_id'].eq(tablePerson['orgStructure_id']))
                record = db.getRecordEx(table, [tableOSDA['disabledType']],
                                        [tablePerson['deleted'].eq(0), tablePerson['id'].eq(personId),
                                         tableOSDA['attachType_id'].eq(attachTypeId)])
                if record:
                    disabledType = forceInt(record.value('disabledType'))
                    if not isStrict and (disabledType == 0 or (disabledType == 1 and not boolCreateOrder)):
                        buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
                        message = u'Запрещено обслуживание врачом по прикреплению: %s.\nВсё равно продолжить?' % (
                        code + u'-' + name)
                        buttonsFocus = QtGui.QMessageBox.No
                        buttonsResult = QtGui.QMessageBox.Yes
                    else:
                        buttons = QtGui.QMessageBox.Ok
                        message = u'Запрещено обслуживание врачом по прикреплению: %s.\n' % (code + u'-' + name)
                        buttonsFocus = QtGui.QMessageBox.Ok
                        buttonsResult = None
                    return QtGui.QMessageBox.critical(self,
                                                      u'Внимание!',
                                                      message,
                                                      buttons,
                                                      buttonsFocus) == buttonsResult
        return True

    @staticmethod
    def confirmClientPolicyConstraint(widget, clientId, date=None):
        compulsoryServiceStop = 0
        voluntaryServiceStop = 0
        recordCompulsoryPolicy = getClientCompulsoryPolicy(clientId, date)
        if recordCompulsoryPolicy:
            compulsoryServiceStop = forceBool(recordCompulsoryPolicy.value('compulsoryServiceStop'))
        recordVoluntaryPolicy = getClientVoluntaryPolicy(clientId, date)
        if recordVoluntaryPolicy:
            voluntaryServiceStop = forceBool(recordVoluntaryPolicy.value('voluntaryServiceStop'))
        elif QtGui.qApp.userHasRight(urQueueCheckVPolicy):
            message = u'У пациента нет полиса ДМС на текущую дату (%s)\nПродолжить?..' % formatDate(date)
            return QtGui.QMessageBox.information(widget,
                                                 u'Внимание!',
                                                 message,
                                                 QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                 QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes

        if compulsoryServiceStop or voluntaryServiceStop:
            if compulsoryServiceStop:
                messageFinance = u'ОМС'
            elif voluntaryServiceStop:
                messageFinance = u'ДМС'
            message = u'По данной СМО приостановлено обслуживание %s полисов.\nЭто может привести к затруднениям оплаты обращения.\nВсё равно продолжить?' % (
            messageFinance)
            return QtGui.QMessageBox.critical(widget,
                                              u'Внимание!',
                                              message,
                                              QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                              QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes
        return True


class CSpecialityConstraint(CSexAgeConstraint):
    def __init__(self, id):
        CSexAgeConstraint.__init__(self)
        db = QtGui.qApp.db
        table = db.table('rbSpeciality')
        record = db.getRecord(table, 'sex, age', id)
        if record:
            self.initByRecord(record)
        else:
            self.code = None
            self.name = None


class CClientInfo(CInfo):
    """
        Основная информация о пациенте.
    """

    def __init__(self, context, id, date=None):
        CInfo.__init__(self, context)
        self._id = id
        self._date = date
        self._lastName = ''
        self._firstName = ''
        self._patrName = ''

        self._sexCode = -1
        self._sex = ''
        self._birthDate = CDateInfo(None)
        self._birthPlace = ''
        self._ageTuple = None
        self._age = ''
        self._SNILS = ''
        self._notes = '' # notes _permanent atach
        self._permanentAttach = self.getInstance(CClientAttachInfo, None)
        self._temporaryAttach = self.getInstance(CClientAttachInfo, None)
        self._allAttaches = self.getInstance(CClientAttachInfoList, None)
        self._socStatuses = self.getInstance(CClientSocStatusInfoList,
                                             clientId=self._id)
        self._citizenship = None
        self._clientRemarks = self.getInstance(CClientRemarkInfoList,
                                               clientId=self._id)
        self._allSocStatuses = self.getInstance(CClientSocStatusInfoList,
                                                clientId=self._id,
                                                includeExpired=True)
        self._document = self.getInstance(CClientDocumentInfo, clientId=None)
        self._compulsoryPolicy = None
        self._voluntaryPolicy = None
        self._regAddress = None
        self._locAddress = None
        self._work = None
        self._phones = ''
        self._primaryPhones = ''
        self._contacts = ''
        self._primaryContacts = ''
        self._email = ''
        self._primaryEmail = ''
        self._bloodTypeMatch = None
        self._bloodDate = CDateInfo(None)
        self._bloodNotes = ''
        self._birthHeight = ''
        self._birthWeight = ''
        self._intolerances = self.getInstance(CClientIntoleranceMedicamentInfoList, None)
        self._allergies = self.getInstance(CClientAllergyInfoList, None)
        self._identification = self.getInstance(CClientIdentificationInfo, None)
        self._relations = self.getInstance(CClientRelationInfoList, None, date)
        self._quotas = self.getInstance(CClientQuotaInfoList, None)
        self._paymentScheme = self.getInstance(CClientPaymentSchemeInfoList, None)
        self._diagNames = ''
        self._modifyDatetime = CDateTimeInfo()
        self._createDatetime = CDateTimeInfo()
        self._cardLocation = u''
        self._chartBeginDate = CDateInfo()
        from Events.EventInfo import CDiagnosisInfoList
        self._diagnosises = self.getInstance(CDiagnosisInfoList, None)
        self._events = None
        self._disabilities = self.getInstance(CClientDisabilityInfoList, None)
        self._incapacity = None
        self._attendingPerson = self.getInstance(CPersonInfo, None)
        self._statusDD = None
        self._foreignHospitalizations = self.getInstance(CClientForeignHospitalizationInfoList, None)
        self._compulsoryTreatment = self.getInstance(CClientCompulsoryTreatmentInfoList, None)
        self._monitorings = self.getInstance(CClientMonitoringInfoList, None)
        self._hasImplants = None
        self._hasProsthesis = None

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Client')
        tableEvent = db.table('Event')
        if self._id:
            record = db.getRecord(table, '*', self._id)
        else:
            record = None
        if record:
            self._lastName = forceString(record.value('lastName')).title()
            self._firstName = forceString(record.value('firstName')).title()
            self._patrName = forceString(record.value('patrName')).title()

            self._sexCode = forceInt(record.value('sex'))
            self._sex = formatSex(self._sexCode)
            self._birthDate = CDateInfo(record.value('birthDate'))
            self._birthPlace = forceString(record.value('birthPlace'))
            self._ageTuple = calcAgeTuple(self._birthDate.date, self._date)
            self._age = formatAgeTuple(self._ageTuple, self._birthDate.date, self._date)
            self._SNILS = formatSNILS(forceString(record.value('SNILS')))
            self._notes = forceString(record.value('notes'))
            self._permanentAttach = self.getInstance(CClientAttachInfo, self._getLastAttachId(temporary=False))
            self._temporaryAttach = self.getInstance(CClientAttachInfo, self._getLastAttachId(temporary=True))
            self._allAttaches = self.getInstance(CClientAttachInfoList, self._id)
            self._socStatuses = self.getInstance(CClientSocStatusInfoList, self._id)
            self._citizenship = self._getCitizenship(self._socStatuses)
            self._clientRemarks = self.getInstance(CClientRemarkInfoList, self._id)
            self._allSocStatuses = self.getInstance(CClientSocStatusInfoList,
                                                    self._id,
                                                    includeExpired=True)
            self._document = self.getInstance(CClientDocumentInfo, clientId=self._id)
            self._compulsoryPolicy = self.getInstance(CClientPolicyInfo, self._id, True)
            self._voluntaryPolicy = self.getInstance(CClientPolicyInfo, self._id, False)
            self._policyList = self.getInstance(CClientPolicyList, self._id)
            self._regAddress = self.getInstance(CClientAddressInfo, self._id, 0)
            self._locAddress = self.getInstance(CClientAddressInfo, self._id, 1)
            self._work = self.getInstance(CClientWorkInfo, self._id)

            self._contacts = getClientPhones(self._id)
            self._primaryContacts = getClientPhones(self._id, isPrimary=True)

            self._phones = getClientPhonesEx(self._id, withNotes=False)
            self._primaryPhones = getClientPhonesEx(self._id, withNotes=False, isPrimary=True)

            self._email = getClientEmailsEx(self._id)
            self._primaryEmail = getClientEmailsEx(self._id, isPrimary=True)

            bloodTypeString = forceString(
                db.translate('rbBloodType', 'id', forceRef(record.value('bloodType_id')), 'name'))
            bloodTypeMatch = re.match(ur'(?P<name>0|A|B|AB)\((?P<number>I+V*)\)(?P<rhesus>Rh[+-])', bloodTypeString)
            self._bloodTypeInfo = bloodTypeMatch.groupdict() if bloodTypeMatch else {}

            self._bloodDate = CDateInfo(record.value('bloodDate'))
            self._bloodNotes = forceString(record.value('bloodNotes'))
            self._birthHeight = forceString(record.value('growth'))
            self._birthWeight = forceString(record.value('weight'))
            self._intolerances = self.getInstance(CClientIntoleranceMedicamentInfoList, self._id)
            self._allergies = self.getInstance(CClientAllergyInfoList, self._id)
            self._identification = self.getInstance(CClientIdentificationInfo, self._id)
            self._relations = self.getInstance(CClientRelationInfoList, self._id, self._date)
            self._quotas = self.getInstance(CClientQuotaInfoList, self._id)
            self._paymentScheme = self.getInstance(CClientPaymentSchemeInfoList, self._id)
            self._diagNames = forceString(record.value('diagNames'))
            self._modifyDatetime = CDateTimeInfo(forceDateTime(record.value('modifyDatetime')))
            self._createDatetime = CDateTimeInfo(forceDateTime(record.value('createDatetime')))
            cardLocationInfo = getLocationCard(self._id)
            self._cardLocation = cardLocationInfo[0] if cardLocationInfo else u''
            self._chartBeginDate = CDateInfo(forceDate(record.value('chartBeginDate')))
            from Events.EventInfo import CDiagnosisInfoList, CLocEventInfoList
            self._diagnosises = self.getInstance(CDiagnosisInfoList, self._id)
            eventIdList = db.getIdList('Event', tableEvent['id'],
                                       [tableEvent['client_id'].eq(self._id), tableEvent['deleted'].eq(0)])
            self._events = CLocEventInfoList(self.context, eventIdList)
            self._disabilities = self.getInstance(CClientDisabilityInfoList, self._id)
            self._incapacity = bool(getIncapacityCheck(self._id))
            self._attendingPerson = self.getInstance(CPersonInfo, forceRef(record.value('attendingPerson_id')))
            self._statusDD = getClientDDStatus(self._id)
            self._foreignHospitalizations = self.getInstance(CClientForeignHospitalizationInfoList, self._id)
            self._compulsoryTreatment = self.getInstance(CClientCompulsoryTreatmentInfoList, self._id)
            self._monitorings = self.getInstance(CClientMonitoringInfoList, self._id)
            self._statusObservation = self.getInstance(CClientStatusObservationInfo, self._id)
            self._bodyStats = self.getInstance(CClientBodyStatsInfo, self._id)

            self._hasImplants = forceBool(record.value('hasImplants'))
            self._hasProsthesis = forceBool(record.value('hasProsthesis'))
            return True
        else:
            return False

    def setSocStatuses(self, socStatuses):
        self._socStatuses = socStatuses

    @staticmethod
    def _getCitizenship(socStatuses):
        for socStatus in socStatuses:
            for statusClass in socStatus.classes:
                if statusClass.flatCode == 'citizenship' and socStatus.name:
                    return socStatus.name
        return u'РФ'

    def _getLastAttachId(self, temporary):
        attr = '_lastTemporaryAttachId' if temporary else '_lastPermanentAttachId'
        attrValue = getattr(self, attr, None)
        if attrValue:
            return attrValue
        db = QtGui.qApp.db
        tableAttach = db.table('ClientAttach')
        tableAttachType = db.table('rbAttachType')
        tableClientAttach = tableAttach.innerJoin(tableAttachType,
                                                  [tableAttach['attachType_id'].eq(tableAttachType['id'])])
        cond = [tableAttach['client_id'].eq(self._id), tableAttach['deleted'].eq(0),
                tableAttachType['temporary'].ne(0) if temporary else tableAttachType['temporary'].eq(0)]
        record = db.getRecordEx(tableClientAttach, tableAttach['id'], cond, 'id DESC')
        if record:
            id = forceRef(record.value('id'))
            setattr(self, attr, id)
            return id

    def __str__(self):
        self.load()
        return formatShortNameInt(self.lastName, self.firstName, self.patrName)

    id = property(lambda self: self.load()._id,
                  doc=u"""
                                      Код пациента.
                                      :rtype : int
                                  """)
    lastName = property(lambda self: self.load()._lastName,
                        doc=u"""
                                      Фамилия.
                                      :rtype : unicode
                                  """)
    firstName = property(lambda self: self.load()._firstName,
                         doc=u"""
                                      Имя.
                                      :rtype : unicode
                                  """)
    patrName = property(lambda self: self.load()._patrName,
                        doc=u"""
                                      Отчество.
                                      :rtype : unicode
                                  """)
    fullName = property(lambda self: formatNameInt(self.lastName, self.firstName, self.patrName),
                        doc=u"""
                                      Фамилия, имя и отчество через пробел.
                                      :rtype : unicode
                                  """)
    shortName = property(lambda self: formatShortNameInt(self.lastName, self.firstName, self.patrName),
                         doc=u"""
                                      Фамилия и инициалы.
                                      :rtype : unicode
                                  """)
    sexCode = property(lambda self: self.load()._sexCode,
                       doc=u"""
                                      Код пола пациента (1 - М, 2 - Ж).
                                      :rtype : int
                                  """)
    sex = property(lambda self: self.load()._sex,
                   doc=u"""
                                      Пол пациента (М или Ж).
                                      :rtype : unicode
                                  """)
    birthDate = property(lambda self: self.load()._birthDate,
                         doc=u"""
                                      Дата рождения.
                                      :rtype : CDateInfo
                                  """)
    birthPlace = property(lambda self: self.load()._birthPlace,
                          doc=u"""
                                      Место рождения.
                                      :rtype : unicode
                                  """)
    ageTuple = property(lambda self: self.load()._ageTuple,
                        doc=u"""
                                      Возраст пациента в виде кортежа (<в_днях>, <в_неделях>, <в_месяцах>, <в_годах>).
                                      :rtype : tuple(int, int, int, int)
                                  """)
    age = property(lambda self: self.load()._age,
                   doc=u"""
                                      Возраст.
                                      :rtype : unicode
                                  """)
    SNILS = property(lambda self: self.load()._SNILS,
                     doc=u"""
                                      Cтраховой номер индивидуального лицевого счета (СНИЛС).
                                      :rtype : tuple(int, int, int, int)
                                  """)
    notes = property(lambda self: self.load()._notes,
                     doc=u"""
                                      Примечания пациента.
                                      :rtype : unicode
                                  """)
    permanentAttach = property(lambda self: self.load()._permanentAttach,
                               doc=u"""
                                      Постоянное прикрепление.
                                      :rtype : CClientAttachInfo
                                  """)
    temporaryAttach = property(lambda self: self.load()._temporaryAttach,
                               doc=u"""
                                      Временное прикрепление.
                                      :rtype : CClientAttachInfo
                                  """)
    allAttaches = property(lambda self: self.load()._allAttaches,
                           doc=u"""
                                      Все прикрепления.
                                      :rtype : CClientAttachInfoList
                                  """)
    socStatuses = property(lambda self: self.load()._socStatuses,
                           doc=u"""
                                      Социальные статусы.
                                      :rtype : CClientSocStatusInfoList
                                  """)
    citizenship = property(lambda self: self.load()._citizenship,
                           doc=u"""
                                Гражданство.
                                :rtype : unicode
                           """)
    clientRemarks = property(lambda self: self.load()._clientRemarks,
                             doc=u"""
                                      Пометки пациента.
                                      :rtype : CClientRemarkInfoList
                                  """)
    allSocStatuses = property(lambda self: self.load()._allSocStatuses,
                              doc=u"""
                                      Социальные статусы, в том числе с истёкшим временем.
                                      :rtype : CClientSocStatusInfoList
                                  """)
    document = property(lambda self: self.load()._document,
                        doc=u"""
                                      Документ, удостоверяющий личность.
                                      :rtype : CClientDocumentInfo
                                  """)
    compulsoryPolicy = property(lambda self: self.load()._compulsoryPolicy,
                                doc=u"""
                                      ОМС полис.
                                      :rtype : CClientPolicyInfo
                                  """)
    voluntaryPolicy = property(lambda self: self.load()._voluntaryPolicy,
                               doc=u"""
                                      ДМС полис.
                                      :rtype : CClientPolicyInfo
                                  """)
    policy = compulsoryPolicy
    policyDMS = voluntaryPolicy
    policyList = property(lambda self: self.load()._policyList,
                          doc=u"""
                                      Список всех полюсов.
                                      :rtype : CClientPolicyList
                                  """)
    regAddress = property(lambda self: self.load()._regAddress,
                          doc=u"""
                                      Адрес регистрации.
                                      :rtype : CClientAddressInfo
                                  """)
    locAddress = property(lambda self: self.load()._locAddress,
                          doc=u"""
                                      Адрес проживания.
                                      :rtype : CClientAddressInfo
                                  """)
    work = property(lambda self: self.load()._work,
                    doc=u"""
                                      Занятость.
                                      :rtype : CClientWorkInfo
                                  """)
    phones = property(lambda self: self.load()._phones,
                      doc=u"""
                                      Контактная информация в виде отформатированной строки.
                                      :rtype : unicode
                                  """)
    primaryPhones = property(lambda self: self.load()._primaryPhones,
                      doc=u"""
                                          Основная контактная информация в виде отформатированной строки.
                                          :rtype : unicode
                                      """)
    email = property(lambda self: self.load()._email,
                     doc=u"""
                                   Адрес электронная почта.
                                   :rtype : unicode
                               """)
    primaryEmail = property(lambda self: self.load()._email,
                     doc=u"""
                                   Основной адрес электронная почта.
                                   :rtype : unicode
                               """)
    contacts = property(lambda self: self.load()._contacts,
                        doc=u"""
                                      Контактная информация в виде списка кортежей (<код_контакта>, <тип_контакта>, <контакт>, <примечания>).
                                      :rtype : list of tuple(unicode, unicode, unicode, unicode)
                                  """)
    primaryContacts = property(lambda self: self.load()._primaryContacts,
                        doc=u"""
                                      Основная контактная информация в виде списка кортежей (<код_контакта>, <тип_контакта>, <контакт>, <примечания>).
                                      :rtype : list of tuple(unicode, unicode, unicode, unicode)
                                  """)
    bloodType = property(
        lambda self: '%(name)s(%(number)s)%(rhesus)s' % self._bloodTypeInfo if self.load()._bloodTypeInfo else '',
        doc=u"""
                                      Группа крови и резус-фактор (например "AB(IV)Rh-").
                                      :rtype : unicode
                                  """)
    bloodTypeName = property(lambda self: self.load()._bloodTypeInfo.get('name', ''),
                             doc=u"""
                                      Название группы крови (0, A, B или AB).
                                      :rtype : unicode
                                  """)
    bloodTypeNumber = property(lambda self: self.load()._bloodTypeInfo.get('number', ''),
                               doc=u"""
                                      Номер группы крови римскими цифрами (I, II, III, IV).
                                      :rtype : unicode
                                  """)
    bloodTypeRhesus = property(lambda self: self.load()._bloodTypeInfo.get('rhesus', ''),
                               doc=u"""
                                      Резус-фактор (Rh+ или Rh-).
                                      :rtype : unicode
                                  """)
    bloodDate = property(lambda self: self.load()._bloodDate,
                         doc=u"""
                                      Дата установления группы крови.
                                      :rtype : CDateInfo
                                  """)
    bloodNotes = property(lambda self: self.load()._bloodNotes,
                          doc=u"""
                                      Примечание к группе крови.
                                      :rtype : unicode
                                  """)
    birthHeight = property(lambda self: self.load()._birthHeight,
                           doc=u"""
                                      Рост при рождении.
                                      :rtype : unicode
                                  """)
    birthWeight = property(lambda self: self.load()._birthWeight,
                           doc=u"""
                                      Вес при рождении.
                                      :rtype : unicode
                                  """)
    intolerances = property(lambda self: self.load()._intolerances,
                            doc=u"""
                                      Медикаментозная непереносимость.
                                      :rtype : CClientIntoleranceMedicamentInfoList
                                  """)
    allergies = property(lambda self: self.load()._allergies,
                         doc=u"""
                                      Аллергическая непереносимость.
                                      :rtype : CClientAllergyInfoList
                                  """)
    identification = property(lambda self: self.load()._identification,
                              doc=u"""
                                      Учётные номера в различный системах.
                                      :rtype : CClientIdentificationInfo
                                  """)
    relations = property(lambda self: self.load()._relations,
                         doc=u"""
                                      Связи пациента.
                                      :rtype : CClientRelationInfoList
                                  """)
    quotas = property(lambda self: self.load()._quotas,
                      doc=u"""
                                      Квоты.
                                      :rtype : CClientQuotaInfoList
                                  """)
    diagNames = property(lambda self: self.load()._diagNames,
                         doc=u"""
                                      Коды диагнозов.
                                      :rtype : unicode
                                  """)
    modifyDatetime = property(lambda self: self.load()._modifyDatetime,
                              doc=u"""
                                      Дата и время последнего изменения записи пациента.
                                      :rtype : CDateTimeInfo
                                  """)
    createDatetime = property(lambda self: self.load()._createDatetime,
                              doc=u"""
                                      Дата и время создания записи пациента.
                                      :rtype : CDateTimeInfo
                                  """)
    cardLocation = property(lambda self: self.load()._cardLocation,
                            doc=u"""
                                      Место нахождения амбулаторной карты.
                                      :rtype : unicode
                                  """)
    chartBeginDate = property(lambda self: self.load()._chartBeginDate,
                              doc=u"""
                                      Дата начала ведения карты.
                                      :rtype : CDateInfo
                                  """)
    diagnosises = property(lambda self: self.load()._diagnosises,
                           doc=u"""
                                      Диагнозы.
                                      :rtype : CDiagnosisInfoList
                                  """)
    events = property(lambda self: self.load()._events,
                      doc=u"""
                                      Обращения.
                                      :rtype : CLocEventInfoList
                                  """)
    disabilities = property(lambda self: self.load()._disabilities,
                            doc=u"""
                                      Инвалидность.
                                      :rtype : CTempInvalidInfoList
                                  """)
    incapacity = property(lambda self: self.load()._incapacity,
                          doc=u"""
                                      Отметка недееспособности.
                                      :rtype : Bool
                                  """)
    attendingPerson = property(lambda self: self.load()._attendingPerson,
                               doc=u"""
                                      Лечащий врач.
                                      :rtype : CPersonInfo
                                  """)
    statusDD = property(lambda self: self.load()._statusDD,
                        doc=u"""
                                      Статус прохождения доподнительной диспансеризации.
                                      :rtype : tuple(int, CDateInfo)
                                  """)
    foreignHospitalizations = property(lambda self: self.load()._foreignHospitalizations,
                                       doc=u"""
                                      Госпитализации в других ЛПУ.
                                      :rtype : CClientForeignHospitalizationInfoList
                                  """)
    compulsoryTreatment = property(lambda self: self.load()._compulsoryTreatment,
                                   doc=u"""
                                      Принудительное лечение.
                                      :rtype : CClientCompulsoryTreatmentInfoList
                                  """)
    monitorings = property(lambda self: self.load()._monitorings,
                           doc=u"""
                                      Принудительное лечение.
                                      :rtype : CClientMonitoringInfoList
                                  """)
    statusObservation = property(lambda self: self.load()._statusObservation,
                                 doc=u"""
                                           Статус наблюдения.
                                           :rtype : CClientObservationInfo
                                       """)
    bodyStats = property(lambda self: self.load()._bodyStats,
                         doc=u"""
                                    ClientBodyStats
                                    :rtype : CClientBodyStatsInfo
                               """)
    hasImplants = property(lambda self: self.load()._hasImplants,
                         doc=u"""
                                    Отметка о наличии имплантантов.
                                    :rtype : Bool
                               """)
    hasProsthesis = property(lambda self: self.load()._hasProsthesis,
                         doc=u"""
                                    Отметка о наличии протезов.
                                    :rtype : Bool
                               """)


class CClientDocumentInfo(CInfo):
    u"""
        Информация о документе, удостоверяющем личность.
    """

    def __init__(self, context, clientId=None, documentId=None):
        CInfo.__init__(self, context)
        self._clientId = clientId
        self._documentId = documentId
        self._documentType = u'-'
        self._documentTypeCode = u'-'
        self._serial = ''
        self._number = ''
        self._date = CDateInfo()
        self._origin = ''
        self._modifyDatetime = CDateTimeInfo()

    def _load(self):
        if self._documentId:
            record = QtGui.qApp.db.getRecord('ClientDocument', '*', self._documentId)
        elif self._clientId:
            record = getClientDocument(self._clientId)
        else:
            record = None
        if record:
            documentTypeId = forceRef(record.value('documentType_id'))
            self._documentType = forceString(QtGui.qApp.db.translate('rbDocumentType', 'id', documentTypeId, 'name'))
            self._documentTypeCode = forceString(
                QtGui.qApp.db.translate('rbDocumentType', 'id', documentTypeId, 'code'))
            self._serial = forceString(record.value('serial'))
            self._number = forceString(record.value('number'))
            self._date = CDateInfo(forceDate(record.value('date')))
            self._origin = forceString(record.value('origin'))
            self._modifyDatetime = CDateTimeInfo(forceDateTime(record.value('modifyDatetime')))
            return True
        else:
            return False

    def __str__(self):
        self.load()
        return (' '.join([self._documentType, self._serial, self._number])).strip()

    documentType = property(lambda self: self.load()._documentType,
                            doc=u'''
                                    Тип документа.
                                    :rtype : unicode
                                ''')
    documentTypeName = property(lambda self: self.load()._documentType,
                                doc=u'''
                                    Тип документа.
                                    :rtype : unicode
                                ''')
    documentTypeCode = property(lambda self: self.load()._documentTypeCode,
                                doc=u'''
                                    Код типа документа.
                                    :rtype : unicode
                                ''')
    type = property(lambda self: self.load()._documentType,
                    doc=u'''
                                    Тип документа.
                                    :rtype : unicode
                                ''')
    serial = property(lambda self: self.load()._serial,
                      doc=u'''
                                    Серия документа.
                                    :rtype : unicode
                                ''')
    number = property(lambda self: self.load()._number,
                      doc=u'''
                                    Номер документа.
                                    :rtype : unicode
                                ''')
    date = property(lambda self: self.load()._date,
                    doc=u'''
                                    Дата выдачи документа.
                                    :rtype : CDateInfo
                                ''')
    origin = property(lambda self: self.load()._origin,
                      doc=u'''
                                    Место выдачи документа.
                                    :rtype : unicode
                                ''')
    modifyDatetime = property(lambda self: self.load()._modifyDatetime,
                              doc=u'''
                                    Дата и время изменения записи о документе в базе данных.
                                    :rtype : CDateTimeInfo
                                ''')


class CClientDisabilityInfo(CInfo):
    """
        Информация об инвалидности
    """

    def __init__(self, context, disabilityRecordId):
        CInfo.__init__(self, context)
        self.id = disabilityRecordId

    def _load(self):
        record = QtGui.qApp.db.getRecord('ClientDisability', '*', self.id)
        if record:
            self._groupNumber = forceInt(record.value('groupNumber'))
            self._work = self.getInstance(CClientWorkInfo, forceRef(record.value('work_id')))
            self._degree = forceInt(record.value('degree'))
            self._note = forceString(record.value('note'))
            self._isPrimary = forceBool(record.value('isPrimary'))
            self._isSomatic = forceBool(record.value('isSomatic'))
            self._isStationary = forceBool(record.value('isStationary'))
            self._isTermless = forceBool(record.value('isTermless'))
            self._recertificationDate = CDateInfo(forceDate(record.value('recertificationDate')))
            self._setDate = CDateInfo(forceDate(record.value('setDate')))
            return True
        else:
            self._groupNumber = None
            self._work = self.getInstance(CClientWorkInfo, None)
            self._degree = None
            self._note = None
            self._isPrimary = None
            self._isSomatic = None
            self._isStationary = None
            self._isTermless = None
            self._recertificationDate = CDateInfo()
            self._setDate = CDateInfo()
            return False

    setDate = property(lambda self: self.load()._setDate,
                       doc=u'''
                                Дата установки инвалидности.
                                :rtype : CDateInfo
                            ''')
    groupNumber = property(lambda self: self.load()._groupNumber,
                           doc=u'''
                                        Группа инвалидности.
                                        :rtype : int
                                    ''')
    recertificationDate = property(lambda self: self.load()._recertificationDate,
                                   doc=u'''
                                        Дата очередного переосвидетельствования..
                                        :rtype : CDateInfo
                                    ''')
    work = property(lambda self: self.load()._work,
                    doc=u'''
                                        Место работы.
                                        :rtype : CClientWorkInfo
                                    ''')

    degree = property(lambda self: self.load()._degree,
                      doc=u'''
                                        Степень утраты трудоспособности.
                                        :rtype : int
                                    ''')
    note = property(lambda self: self.load()._note,
                    doc=u'''
                                        Примечание.
                                        :rtype : unicode
                                    ''')
    isPrimary = property(lambda self: self.load()._isPrimary,
                         doc=u'''
                                        Признак первичности.
                                        :rtype : Bool
                                    ''')
    isSomatic = property(lambda self: self.load()._isSomatic,
                         doc=u'''
                                        Cоматическая инвалидность.
                                        :rtype : Bool
                                    ''')
    isStationary = property(lambda self: self.load()._isStationary,
                            doc=u'''
                                        Стационар.
                                        :rtype : Bool
                                    ''')
    isTermless = property(lambda self: self.load()._isTermless,
                          doc=u'''
                                        Бессрочно.
                                        :rtype : Bool
                                    ''')


class CClientDisabilityInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientDisability')
        idList = db.getIdList(table, 'id', table['client_id'].eq(self.clientId), 'id')
        self._items = [self.getInstance(CClientDisabilityInfo, id) for id in idList]
        return True


class CRBPolicyTypeInfo(CRBInfo):
    u"""
        Информация о типе полиса.
    """
    tableName = 'rbPolicyType'


class CRBPolicyKindInfo(CRBInfo):
    u"""
        Информация о виде полиса.
    """
    tableName = 'rbPolicyKind'

    def _initByRecord(self, record):
        self._regionalCode = forceString(record.value('regionalCode'))
        self._federalCode = forceString(record.value('federalCode'))

    def _initByNull(self):
        self._regionalCode = ''
        self._federalCode = ''

    regionalCode = property(lambda self: self.load()._regionalCode)
    federalCode = property(lambda self: self.load()._federalCode)


class CContractList(CInfoList):
    def __init__(self, context, policyId):
        CInfoList.__init__(self, context)
        self.policyId = policyId

    def _load(self):
        db = QtGui.qApp.db

        tableCP = db.table('ClientPolicy')
        table = tableCP
        tableCC = db.table('Contract_Contingent')
        tableC = db.table('Contract')
        table = table.leftJoin(tableCC, tableCC['insurer_id'].eq(tableCP['insurer_id']))
        table = table.leftJoin(tableC, tableC['payer_id'].eq(tableCC['insurer_id']))
        # table = table.leftJoin(tableC, tableCP['insurer_id'].eq(tableC['payer_id']))
        idList = db.getDistinctIdList(
            table,
            tableC['id'],
            [
                tableCP['id'].eq(self.policyId),
                tableC['deleted'].eq(0),
                tableCP['deleted'].eq(0)
            ]
        )
        from Events.EventInfo import CContractInfo
        self._items = [self.getInstance(CContractInfo, id) for id in idList]
        return True


class CKLADRInfo(CInfo):
    u"""
        Информация из КЛАДРа
    """

    def __init__(self, context, code, tableName='KLADR'):
        CInfo.__init__(self, context)
        self._code = code
        self._socr = ''
        self._name = ''
        self._infis = ''
        self._tableName = tableName

    def _load(self):
        if self._code:
            db = QtGui.qApp.db
            table = db.table('kladr.%s' % self._tableName, idFieldName='CODE')
            cols = [
                table['NAME'],
                table['SOCR']
            ]
            if self._tableName.lower() == 'kladr':
                cols.extend([
                    table['infis']
                ])
            rec = db.getRecordEx(table, cols, table['CODE'].eq(self._code))
            if rec is not None:
                self._socr = forceString(rec.value('SOCR'))
                self._name = forceString(rec.value('NAME'))
                self._infis = forceString(rec.value('infis'))
                return True

        self._socr = ''
        self._name = ''
        self._infis = ''
        return False

    def __str__(self):
        self.load()
        return u' '.join([self._name, self._socr]).strip()

    socr = property(lambda self: self.load()._socr)
    name = property(lambda self: self.load()._name)
    nameSocr = property(lambda self: u' '.join([self.load()._name, self.load()._socr]).strip())
    infis = property(lambda self: self.load()._infis)


class CClientPolicyInfo(CInfo):
    u"""
        Информация о полисе пациента.
    """

    def __init__(self, context, clientId, isCompulsory=True, policyId=None):
        CInfo.__init__(self, context)
        if policyId:
            self.policyId = policyId
            self.clientId = clientId
            self.isCompulsory = isCompulsory
            self._insuranceAreaInfis = ''
        else:
            self.policyId = None
            self.clientId = clientId
            self.isCompulsory = isCompulsory
            self._insuranceAreaInfis = ''

    def _load(self):
        if self.policyId:
            record = getClientPolicyById(self.policyId)
        else:
            recordList = getClientPolicyList(self.clientId, self.isCompulsory)
            record = recordList[-1] if recordList else None
        if record:
            self._policyType = self.getInstance(CRBPolicyTypeInfo, forceRef(record.value('policyType_id')))
            self._policyKind = self.getInstance(CRBPolicyKindInfo, forceRef(record.value('policyKind_id')))
            self._insurer = self.getInstance(COrgInfo, forceRef(record.value('insurer_id')))
            self._contractList = self.getInstance(CContractList, forceRef(record.value('insurer_id')))
            self._serial = forceString(record.value('serial'))
            self._number = forceString(record.value('number'))
            self._name = forceString(record.value('name'))
            self._note = forceString(record.value('note'))
            self._begDate = CDateInfo(record.value('begDate'))
            self._endDate = CDateInfo(record.value('endDate'))
            self._franchisePercent = forceInt(record.value('franchisePercent'))
            insuranceArea = forceString(record.value('insuranceArea'))
            self._insuranceArea = self.getInstance(CKLADRInfo, insuranceArea)
            self._insuranceAreaInfis = forceString(
                QtGui.qApp.db.translate('kladr.KLADR', 'CODE', insuranceArea, 'infis', idFieldName='CODE'))
            return True
        else:
            self._policyType = self.getInstance(CRBPolicyTypeInfo, None)
            self._policyKind = self.getInstance(CRBPolicyKindInfo, None)
            self._insurer = self.getInstance(COrgInfo, None)
            self._contractList = list()
            self._serial = ''
            self._number = ''
            self._name = ''
            self._note = ''
            self._begDate = CDateInfo()
            self._endDate = CDateInfo()
            self._franchisePercent = 0
            self._insuranceArea = self.getInstance(CKLADRInfo, None)
            self._insuranceAreaInfis = ''
            return False

    def __str__(self):
        self.load()
        return (' '.join([self._policyType.name, unicode(self._insurer), self._serial, self._number])).strip()

    policyType = property(lambda self: self.load()._policyType,
                          doc=u'''
                                    Тип полиса.
                                    :rtype : CRBPolicyTypeInfo
                                ''')
    policyKind = property(lambda self: self.load()._policyKind,
                          doc=u'''
                                    Вид полиса.
                                    :rtype : CRBPolicyKindInfo
                                ''')
    contractList = property(lambda self: self.load()._contractList,
                            doc=u'''
                                    Список контрактов.
                                    :rtype : CContractList
                                ''')
    type = property(lambda self: self.load()._policyType,
                    doc=u'''
                                    Тип полиса.
                                    :rtype : CRBPolicyTypeInfo
                                ''')
    insurer = property(lambda self: self.load()._insurer,
                       doc=u'''
                                    Страховая организация.
                                    :rtype : COrgInfo
                                ''')
    serial = property(lambda self: self.load()._serial,
                      doc=u'''
                                    Серия полиса.
                                    :rtype : unicode
                                ''')
    number = property(lambda self: self.load()._number,
                      doc=u'''
                                    Номер полиса.
                                    :rtype : unicode
                                ''')
    name = property(lambda self: self.load()._name,
                    doc=u'''
                                    Название полиса.
                                    :rtype : unicode
                                ''')
    note = property(lambda self: self.load()._note,
                    doc=u'''
                                    Примечание к полису.
                                    :rtype : unicode
                                ''')
    #    notes       = note
    begDate = property(lambda self: self.load()._begDate,
                       doc=u'''
                                    Дата начала действия полиса.
                                    :rtype : CDateInfo
                                ''')
    endDate = property(lambda self: self.load()._endDate,
                       doc=u'''
                                    Дата окончания действия полиса.
                                    :rtype : CDateInfo
                                ''')

    franchisePercent = property(lambda self: self.load()._franchisePercent,
                                doc=u'''
                                        Процент франшизы полиса.
                                        :rtype : int
                                ''')

    insuranceArea = property(lambda self: self.load()._insuranceArea,
                             doc=u'''
                                Информация из КЛАДРа о территории страхования
                                :rtype : CKLADRInfo
                             ''')

    insuranceAreaInfis = property(lambda self: self.load()._insuranceAreaInfis,
                                  doc=u'''
                                    Код ИНФИС территории страхования.
                                    :rtype : unicode
                                ''')


class CClientPolicyList(CInfoList):
    u"""
        Информация о всех полюсах пациента.
    """

    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientPolicy')
        idList = db.getIdList(
            table,
            'id',
            [
                table['client_id'].eq(self.clientId),
                table['deleted'].eq(0)
            ],
            'id'
        )
        self._items = [self.getInstance(CClientPolicyInfo, None, id) for id in idList]
        return True


class CAddressInfo(CInfo):
    u"""
        Информация об адресе.
    """

    def __init__(self, context, addressId):
        CInfo.__init__(self, context)
        self._addressId = addressId
        self._KLADRCode = ''
        self._KLADRStreetCode = ''
        self._region = self.getInstance(CKLADRInfo, '')
        self._district = None
        self._city = self.getInstance(CKLADRInfo, '')
        self._street = self.getInstance(CKLADRInfo, '', tableName='STREET')
        self._number = ''
        self._corpus = ''
        self._flat = ''
        self._text = ''
        self._OKATO = None
        self._SOCR = ''
        self._Infis = ''

    def _load(self):
        address = getAddress(self._addressId)
        self._KLADRCode = address.KLADRCode
        self._KLADRStreetCode = address.KLADRStreetCode
        self._region = self.getInstance(CKLADRInfo, self._KLADRCode[:2].ljust(13, '0'))  # RR00000000000
        # Район: 1. Непосредственно по KLADR.CODE, 2. через kladr.getDistrict() (требуется STREET.CODE) :
        self._district = self.getInstance(CKLADRInfo, self._KLADRCode[:5].ljust(13, '0')).nameSocr or \
                         getDistrictName(address.KLADRCode, address.KLADRStreetCode, address.number)
        self._city = self.getInstance(CKLADRInfo, self._KLADRCode)  # RR0DD0CC*****
        self._street = self.getInstance(CKLADRInfo, self._KLADRStreetCode, tableName='STREET')
        self._number = address.number
        self._corpus = address.corpus
        self._flat = address.flat
        self._Infis = address.Infis

        parts = [
            self._region.nameSocr
        ]
        districtName = self.getDistrict()
        if districtName and districtName != self._region.nameSocr:
            parts.append(districtName)
        if (self._city.name and self._city.name != self._region.name) and (
            not districtName or self._city.name != districtName):
            parts.append(unicode(self._city))
        if self._street.name:
            parts.append(unicode(self._street))
        if self._number:
            parts.append(u'д.%s' % self._number)
        if self._corpus:
            parts.append(u'к.%s' % self._corpus)
        if self._flat:
            parts.append(u'кв.%s' % self._flat)

        self._text = (u', '.join(parts)).strip()
        return bool(self._text)

    def getOKATO(self):
        if self._OKATO is None:
            self.load()
            self._OKATO = getOKATO(self._KLADRCode, self._KLADRStreetCode, self._number)
        return self._OKATO

    def getDistrict(self):
        if self._district is None:
            self.load()
        return self._district

    KLADRCode = property(lambda self: self.load()._KLADRCode,
                         doc=u'''
                         Код населенного пункта по КЛАДР.
                         :rtype : unicode
                         ''')
    KLADRStreetCode = property(lambda self: self.load()._KLADRStreetCode,
                               doc=u'''
                               Код улицы по КЛАДР.
                               :rtype : unicode
                               ''')
    region = property(lambda self: self.load()._region,
                      doc=u'''
                      Регион.
                      :rtype : CKLADRInfo
                      ''')
    district = property(getDistrict,
                        doc=u'''
                    Район.
                    :rtype : CKLADRInfo
                    ''')
    city = property(lambda self: self.load()._city,
                    doc=u'''
                    Населённый пункт.
                    :rtype : CKLADRInfo
                    ''')
    town = city
    street = property(lambda self: self.load()._street,
                      doc=u'''
                      Название улицы.
                      :rtype : unicode
                      ''')
    number = property(lambda self: self.load()._number,
                      doc=u'''
                      Номер дома.
                      :rtype : unicode
                      ''')
    corpus = property(lambda self: self.load()._corpus,
                      doc=u'''
                      Номер корпуса.
                      :rtype : unicode
                      ''')
    flat = property(lambda self: self.load()._flat,
                    doc=u'''
                    Номер квартиры.
                    :rtype : unicode
                    ''')
    SOCR = property(lambda self: self.load()._city.socr,
                    doc=u'''
                    Сокращенное наименование типа населенного пункта.
                    :rtype : unicode
                    ''')
    Infis = property(lambda self: self.load()._Infis,
                     doc=u'''
                     Код населенного пункта по справочнику ИНФИС (доступно не всегда).
                     :rtype : unicode
                     ''')
    OKATO = property(getOKATO,
                     doc=u'''
                     Код адреса по справочнику ОКАТО.
                     :rtype : unicode
                     ''')

    def __str__(self):
        self.load()
        return self._text


class CClientAddressInfo(CAddressInfo):
    u"""
        Информация об адресе пациента.
    """

    def __init__(self, context, clientId, addrType):
        CAddressInfo.__init__(self, context, None)
        self._clientId = clientId
        self._addrType = addrType
        self._freeInput = ''
        self._districtId = None
        self._districtName = None

    def _load(self):
        record = getClientAddress(self._clientId, self._addrType)
        if record:
            self._districtId = forceRef(record.value('district_id'))
            self._districtName = forceString(QtGui.qApp.db.translate('rbDistrict', 'id', self._districtId, 'name'))
            self._addressId = forceRef(record.value('address_id'))
            self._freeInput = forceString(record.value('freeInput'))
            if self._addressId:
                return CAddressInfo._load(self)
            else:
                return True
        else:
            self._addressId = None
            self._freeInput = ''
            return False

    def getDistrict(self):
        if self._districtName is None:
            self._load()
        return self._districtName or self._district

    freeInput = property(lambda self: self.load()._freeInput,
                         doc=u'''
                         При использовании адреса КЛАДР - автоматически сгенерированное представление почтового адреса в одной строке. В противном случае - строка адреса, заданная вручную.
                         :rtype : unicode''')

    district = property(getDistrict,
                        doc=u'''
                        Название района (из rbDistrict, если указано, или из КЛАДР)
                        :rtype : unicode''')

    isVillager = property(lambda self: isVillagerAddress(self.load()._KLADRCode),
                          doc=u'''
                          Признак сельского жителя
                          :rtype : bool''')

    def __str__(self):
        self.load()
        if self._addressId and len(self._text):
            return CAddressInfo.__str__(self)
        else:
            return self.freeInput


class CClientWorkInfo(COrgInfo):
    u"""
        Информация о месте работы/учёбы пациента.
    """

    def __init__(self, context, clientId):
        COrgInfo.__init__(self, context, None)
        self.clientId = clientId
        self._post = ''
        self._OKVED = ''
        self._hurts = []
        self._factors = []
        self._modifyDatetime = CDateTimeInfo()
        self._stage = 0
        self._createDatetime = CDateTimeInfo()
        self._createPerson = self.getInstance(CPersonInfo, None)
        self._modifyPerson = self.getInstance(CPersonInfo, None)
        self._client = self.getInstance(CClientInfo, None)
        self._freeInput = u''
        self._note = u''

    def _load(self):
        workRecord = getClientWork(self.clientId)
        if workRecord:
            #            self.orgId = forceRef(workRecord.value('org_id'))
            self.id = forceRef(workRecord.value('org_id'))
            if self.id:
                COrgInfo._load(self)
            else:
                self._shortName = forceString(workRecord.value('freeInput'))
            self._post = forceString(workRecord.value('post'))
            self._OKVED = forceString(workRecord.value('OKVED'))
            self._hurts = self.getInstance(CClientWorkHurtInfoList, forceRef(workRecord.value('id')))
            self._factors = self.getInstance(CClientWorkHurtFactorInfoList, forceRef(workRecord.value('id')))
            self._modifyDatetime = CDateTimeInfo(forceDateTime(workRecord.value('modifyDatetime')))
            self._stage = forceInt(workRecord.value('stage'))
            self._createDatetime = CDateTimeInfo(forceDateTime(workRecord.value('createDatetime')))
            self._createPerson = self.getInstance(CPersonInfo, forceRef(workRecord.value('createPerson_id')))
            self._modifyPerson = self.getInstance(CPersonInfo, forceRef(workRecord.value('modifyPerson_id')))
            self._client = self.getInstance(CClientInfo, forceRef(workRecord.value('client_id')))
            self._freeInput = forceString(workRecord.value('freeInput'))
            self._note = forceString(workRecord.value('note'))
            return True
        else:
            return False

    def __str__(self):
        self.load()
        parts = []
        if self._shortName:
            parts.append(self._shortName)
        if self._post:
            parts.append(self._post)
        if self._OKVED:
            parts.append(u'ОКВЭД: ' + self._OKVED)
        return ', '.join(parts)

    shortName = property(lambda self: self.load()._shortName,
                         doc=u'''
                                    Краткое наименование организации, в которой работает пациент.
                                    :rtype : unicode
                                ''')
    post = property(lambda self: self.load()._post,
                    doc=u'''
                                    Должность пациента.
                                    :rtype : unicode
                                ''')
    OKVED = property(lambda self: self.load()._OKVED,
                     doc=u'''
                                    Код вида экономической деятельности организации по ОКВЭД.
                                    :rtype : unicode
                                ''')
    hurts = property(lambda self: self.load()._hurts,
                     doc=u'''
                                    Список типов вредности.
                                    :rtype : CClientWorkHurtInfoList
                                ''')
    factors = property(lambda self: self.load()._factors,
                       doc=u'''
                                    Информация о факторах вредности рабочего места пациента.
                                    :rtype : CClientWorkHurtFactorInfoList
                                ''')
    modifyDatetime = property(lambda self: self.load()._modifyDatetime,
                              doc=u'''
                                    Дата и время изменения записи о месте работы пациента в базе данных.
                                    :rtype : CDateTimeInfo
                                ''')
    stage = property(lambda self: self.load()._stage,
                     doc=u'''
                                    Стаж на данном месте работы.
                                    :rtype : int
                                ''')
    createDatetime = property(lambda self: self.load()._createDatetime,
                              doc=u'''
                                    Дата и время создания записи о месте работы пациента в базе данных.
                                    :rtype : CDateTimeInfo
                                ''')
    createPerson = property(lambda self: self.load()._createPerson,
                            doc=u'''
                                    Автор записи о месте работы пациента в базе данных.
                                    :rtype : CPersonInfo
                                ''')
    modifyPerson = property(lambda self: self.load()._modifyPerson,
                            doc=u'''
                                    Пользователь, внесший последние изменения в запись о месте работы пациента в базе данных.
                                    :rtype : CPersonInfo
                                ''')
    client = property(lambda self: self.load()._client,
                      doc=u'''
                                    Информация о пациенте, к которому относится запись.
                                    :rtype : CClientInfo
                                ''')
    freeInput = property(lambda self: self.load()._freeInput,
                         doc=u'''
                                    Дополнительная информация о месте работы.
                                    :rtype : unicode
                                ''')
    note = property(lambda self: self.load()._note,
                    doc=u'''
                                    Примечание
                                    :rtype : unicode
                                ''')


class CClientWorkHurtInfoList(CInfoList):
    def __init__(self, context, workId):
        CInfoList.__init__(self, context)
        self.workId = workId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientWork_Hurt')
        idList = db.getIdList(table, 'id', table['master_id'].eq(self.workId), 'id')
        self._items = [self.getInstance(CClientWorkHurtInfo, id) for id in idList]
        return True


class CClientWorkHurtInfo(CInfo):
    u"""
        Информация о типе вредности на рабочем месте.
    """

    def __init__(self, context, clientWorkHurtId):
        CInfo.__init__(self, context)
        self.clientWorkHurtId = clientWorkHurtId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientWork_Hurt')
        tableHurtType = db.table('rbHurtType')

        record = db.getRecordEx(table.leftJoin(tableHurtType, tableHurtType['id'].eq(table['hurtType_id'])),
                                [table['id'], tableHurtType['code'], tableHurtType['name'], table['stage']],
                                table['id'].eq(self.clientWorkHurtId))
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._stage = forceInt(record.value('stage'))
            # self._factors = self.getInstance(CClientWorkHurtFactorInfoList, forceRef(record.value('master_id')))
            return True
        else:
            self._code = ''
            self._name = ''
            self._stage = 0
            self._factors = []
            return False

    code = property(lambda self: self.load()._code,
                    doc=u'''
                                    Код типа вредности.
                                    :rtype : unicode
                                ''')
    name = property(lambda self: self.load()._name,
                    doc=u'''
                                    Наименование типа вредности.
                                    :rtype : unicode
                                ''')
    stage = property(lambda self: self.load()._stage,
                     doc=u'''
                                    Стаж работы при данном типе вредности.
                                    :rtype : unicode
                                ''')

    def __str__(self):
        return self.load()._name


class CClientRemarkInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientRemark')
        idList = db.getIdList(table, 'id', table['client_id'].eq(self.clientId), 'id')
        self._items = [self.getInstance(CClientRemarkInfo, id) for id in idList]
        return True


class CClientRemarkInfo(CInfo):
    u"""
        Информация о пометке пациента.
    """

    def __init__(self, context, clientRemarkId):
        CInfo.__init__(self, context)
        self.clientRemarkId = clientRemarkId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientRemark')
        tableRemarkType = db.table('rbClientRemarkType')

        record = db.getRecordEx(
            table.leftJoin(
                tableRemarkType,
                tableRemarkType['id'].eq(table['remarkType_id'])
            ),
            [
                table['id'],
                tableRemarkType['code'],
                tableRemarkType['name'],
                tableRemarkType['flatCode'],
                table['date'],
                table['note']
            ],
            table['id'].eq(self.clientRemarkId)
        )
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._flatCode = forceString(record.value('flatCode'))
            self._date = CDateInfo(forceDate(record.value('date')))
            self._note = forceInt(record.value('note'))
            return True
        else:
            self._code = ''
            self._name = ''
            self._flatCode = ''
            self._date = CDateInfo()
            self._note = ''
            return False

    code = property(lambda self: self.load()._note,
                    doc=u'''
                                    Код типа пометки пациента.
                                    :rtype : unicode
                                ''')
    name = property(lambda self: self.load()._note,
                    doc=u'''
                                    Наименование типа пометки пациента.
                                    :rtype : unicode
                                ''')
    flatCode = property(lambda self: self.load()._note,
                        doc=u'''
                                    Код для однозначной идентификации типа пометки пациента.
                                    :rtype : unicode
                                ''')
    date = property(lambda self: self.load()._date,
                    doc=u'''
                                    Дата пометки пациента.
                                    :rtype : CDateInfo
                                ''')
    note = property(lambda self: self.load()._note,
                    doc=u'''
                                    Примечания к пометке пациента.
                                    :rtype : unicode
                                ''')


class CClientWorkHurtFactorInfoList(CInfoList):
    def __init__(self, context, clientWorkId):
        CInfoList.__init__(self, context)
        self.clientWorkId = clientWorkId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientWork_Hurt_Factor')
        idList = db.getIdList(table, 'id', table['master_id'].eq(self.clientWorkId), 'id')
        self._items = [self.getInstance(CClientWorkHurtFactorInfo, id) for id in idList]


class CClientWorkHurtFactorInfo(CInfo):
    u"""
        Информация о факторе вредности рабочего места пациента.
    """

    def __init__(self, context, clientWorkHurtFactorId):
        CInfo.__init__(self, context)
        self.clientWorkHurtFactorId = clientWorkHurtFactorId
        self._code = ''
        self._name = ''

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientWork_Hurt_Factor')
        tableHurtFactorType = db.table('rbHurtFactorType')
        record = db.getRecordEx(
            table.leftJoin(tableHurtFactorType, tableHurtFactorType['id'].eq(table['factorType_id'])),
            [tableHurtFactorType['name'], tableHurtFactorType['code']],
            table['id'].eq(self.clientWorkHurtFactorId))
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            return True
        return False

    #    def __unicode__(self):
    def __str__(self):
        return self.load()._name

    code = property(lambda self: self.load()._code,
                    doc=u'''
                                    Код фактора вредности.
                                    :rtype : unicode
                                ''')
    name = property(lambda self: self.load()._name,
                    doc=u'''
                                    Название фактора вредности.
                                    :rtype : unicode
                                ''')


class CClientAttachInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientAttach')
        idList = db.getIdList(table, 'id', [table['client_id'].eq(self.clientId), table['deleted'].eq(0)], 'id')
        self._items = [self.getInstance(CClientAttachInfo, id) for id in idList]


class CClientAttachInfo(CInfo):
    u"""
        Информация о прикреплении пациента.
    """

    def __init__(self, context, clientAttachId):
        CInfo.__init__(self, context)
        self.clientAttachId = clientAttachId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientAttach')
        tableAttachType = db.table('rbAttachType')
        record = db.getRecordEx(table, '*', [table['id'].eq(self.clientAttachId), table['deleted'].eq(0)])
        if record:
            self._attachType = self.getInstance(CAttachTypeInfo, forceRef(record.value('attachType_id')))
            self._name = self._attachType.name
            self._code = self._attachType.code
            self._outcome = self._attachType.outcome
            self._org = self.getInstance(COrgInfo, forceRef(record.value('LPU_id')))
            self._orgStructure = self.getInstance(COrgStructureInfo, forceRef(record.value('orgStructure_id')))
            self._begDate = CDateInfo(forceDate(record.value('begDate')))
            self._endDate = CDateInfo(forceDate(record.value('endDate')))
            self._document = self.getInstance(CClientDocumentInfo, documentId=forceRef(record.value('document_id')))
            self._temporary = self._attachType.temporary
            self._detachmentReason = self.getInstance(CDetachmentReasonInfo, forceRef(record.value('detachment_id')))
            return True
        else:
            self._attachType = self.getInstance(CAttachTypeInfo, None)
            self._code = ''
            self._name = ''
            self._outcome = ''
            self._org = self.getInstance(COrgInfo, None)
            self._orgStructure = self.getInstance(COrgStructureInfo, None)
            self._begDate = CDateInfo()
            self._endDate = CDateInfo()
            self._document = None
            self._temporary = None
            self._detachmentReason = None
        return False

    def __str__(self):
        self.load()
        if self._ok:
            result = self._name
            if self._outcome:
                result += ' ' + unicode(self._endDate)
            elif self.temporary:
                result += ' ' + self._org.shortName
                if self._begDate:
                    result += u' c ' + unicode(self._begDate)
                if self.endDate:
                    result += u' по ' + unicode(self._endDate)
            else:
                result += ' ' + self._org.shortName
        else:
            result = ''
        return result

    code = property(lambda self: self.load()._code,
                    doc=u'''
                                Код типа прикрепления.
                                :rtype : unicode
                            ''')
    name = property(lambda self: self.load()._name,
                    doc=u'''
                                    Название.
                                    :rtype : unicode
                                ''')
    outcome = property(lambda self: self.load()._outcome,
                       doc=u'''
                                    Признак выбытия.
                                    :rtype : Bool
                                ''')
    begDate = property(lambda self: self.load()._begDate,
                       doc=u'''
                                    Дата начала.
                                    :rtype : CDateInfo
                                ''')
    endDate = property(lambda self: self.load()._endDate,
                       doc=u'''
                                    Дата завершения.
                                    :rtype : CDateInfo
                                ''')
    org = property(lambda self: self.load()._org,
                   doc=u'''
                                    Ссылка на организацию.
                                    :rtype : COrgInfo
                                ''')
    orgStructure = property(lambda self: self.load()._orgStructure,
                            doc=u'''
                                    Ссылка на организационную структуру.
                                    :rtype : COrgStructureInfo
                                ''')
    document = property(lambda self: self.load()._document,
                        doc=u'''
                                    Ссылка на документ.
                                    :rtype : CClientDocumentInfo
                                ''')
    temporary = property(lambda self: self.load()._temporary,
                         doc=u'''
                                    Временное прикрепление.
                                    :rtype : Bool
                                ''')
    attachType = property(lambda self: self.load()._attachType,
                          doc=u'''
                                    Тип прикрепления
                                    :rtype : CAttachTypeInfo
                                ''')
    detachment = property(lambda self: self.load()._detachmentReason,
                          doc=u'''
                                    Причина открепления
                                    :rtype : CDetachmentReasonInfo
                                ''')


class CClientSocStatusInfoList(CInfoList):
    def __init__(self, context, clientId, includeExpired=False):
        CInfoList.__init__(self, context)
        self.clientId = clientId
        self.includeExpired = includeExpired

    def _load(self):
        idList = getClientSocStatusIds(self.clientId, self.includeExpired)
        self._items = [self.getInstance(CClientSocStatusInfo, id) for id in idList]


class CClientSocStatusInfo(CInfo):
    u"""
        Информация о социальном статусе пациента.
    """

    def __init__(self, context, socStatusId):
        CInfo.__init__(self, context)
        self.socStatusId = socStatusId
        self._code = ''
        self._name = ''
        self._document = None
        self._classes = []
        self._begDate = CDateInfo()
        self._endDate = CDateInfo()
        self._note = ''

    def _load(self):
        db = QtGui.qApp.db
        tableClientSocStatus = db.table('ClientSocStatus')
        tableSocStatusType = db.table('rbSocStatusType')
        record = QtGui.qApp.db.getRecord(
            tableClientSocStatus.leftJoin(tableSocStatusType,
                                          tableSocStatusType['id'].eq(tableClientSocStatus['socStatusType_id'])),
            'code, name, document_id, socStatusType_id, begDate, endDate',
            self.socStatusId)
        if record:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._document = self.getInstance(CClientDocumentInfo, documentId=forceRef(record.value('document_id')))
            self._classes = self.getInstance(CSocStatusClassInfoList, forceRef(record.value('socStatusType_id')))
            self._begDate = CDateInfo(forceDate(record.value('begDate')))
            self._endDate = CDateInfo(forceDate(record.value('endDate')))
            self._note = forceString(record.value('notes'))
            return True
        return False

    code = property(lambda self: self.load()._code,
                    doc=u'''
                                    Код типа социального статуса.
                                    :rtype : unicode
                                ''')
    name = property(lambda self: self.load()._name,
                    doc=u'''
                                    Название типа социального статуса.
                                    :rtype : unicode
                                ''')
    document = property(lambda self: self.load()._document,
                        doc=u'''
                                    Документ, подтверждающий наличие социального статуса.
                                    :rtype : CClientDocumentInfo
                                ''')
    classes = property(lambda self: self.load()._classes,
                       doc=u'''
                                    Список классов, к которым относится тип социального статуса.
                                    :rtype : CSocStatusClassInfoList
                                ''')
    begDate = property(lambda self: self.load()._begDate,
                       doc=u'''
                                    Дата начала действия социального статуса.
                                    :rtype : CDateInfo
                                ''')
    endDate = property(lambda self: self.load()._endDate,
                       doc=u'''
                                    Дата окончания действия социального статуса.
                                    :rtype : CDateInfo
                                ''')
    note = property(lambda self: self.load()._note,
                    doc=u'''
                                    Примечание.
                                    :rtype : unicode
                                ''')

    def __str__(self):
        return self.load()._name


class CSocStatusClassInfoList(CInfoList):
    def __init__(self, context, socStatusTypeId):
        CInfoList.__init__(self, context)
        self.socStatusTypeId = socStatusTypeId

    def _load(self):
        idList = getSocStatusTypeClasses(self.socStatusTypeId)
        self._items = [self.getInstance(CSocStatusClassInfo, id) for id in idList]


class CSocStatusClassInfo(CInfo):
    u"""
        Информация о классе социального статуса пациента.
    """

    # некоторые возможные значения поля flatCode
    specialCase = 'specialCase'  # особый случай, для Крыма

    def __init__(self, context, socStatusClassId):
        CInfo.__init__(self, context)
        self.socStatusClassId = socStatusClassId
        self._code = ''
        self._flatCode = ''
        self._name = ''
        self._group = None

    def _load(self):
        record = QtGui.qApp.db.getRecord('rbSocStatusClass', '*', self.socStatusClassId)
        if record:
            self._code = forceString(record.value('code'))
            self._flatCode = forceString(record.value('flatCode'))
            self._name = forceString(record.value('name'))
            groupId = forceRef(record.value('group_id'))
            self._group = self.getInstance(CSocStatusClassInfo, groupId) if groupId else None
            return True
        return False

    code = property(lambda self: self.load()._code,
                    doc=u'''
                                    Код класса социального статуса.
                                    :rtype : unicode
                                ''')
    flatCode = property(lambda self: self.load()._flatCode,
                        doc=u'''
                                    Плоский код класса социального статуса.
                                    :rtype : unicode
                                ''')
    name = property(lambda self: self.load()._name,
                    doc=u'''
                                    Название класса социального статуса.
                                    :rtype : unicode
                                ''')
    group = property(lambda self: self.load()._group,
                     doc=u'''
                                    Группа, к которой относится социальный статус.
                                    :rtype : CSocStatusClassInfo
                                ''')

    #    def __unicode__(self):
    def __str__(self):
        return self.load()._name

    # TODO: document me!
    def isPartOf(self, name):
        return self._isPartOf(name.lower(), set([]))

    def _isPartOf(self, name, seen):
        self.load()
        if self._name.lower() == name:
            return True
        if self.socStatusClassId in seen:
            return None
        elif self._group:
            seen.add(self.socStatusClassId)
            return self._group._isPartOf(name, seen)
        else:
            return False


class CClientIntoleranceMedicamentInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientIntoleranceMedicament')
        idList = db.getIdList(table, 'id', table['client_id'].eq(self.clientId), 'id')
        self._items = [self.getInstance(CClientIntoleranceMedicamentInfo, id) for id in idList]
        return True


class CClientIntoleranceMedicamentInfo(CInfo):
    u"""
        Информация о медикаментозной непереносимости пациента.
    """

    def __init__(self, context, itemId):
        CInfo.__init__(self, context)
        self.itemId = itemId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientIntoleranceMedicament')
        record = db.getRecord(table, ['nameMedicament', 'power', 'createDate', 'notes'], self.itemId)
        if record:
            self._name = forceString(record.value('nameMedicament'))
            self._power = forceInt(record.value('power'))
            self._date = CDateInfo(record.value('createDate'))
            self._notes = forceString(record.value('notes'))
            return True
        else:
            self._name = ''
            self._power = 0
            self._date = CDateInfo(None)
            self._notes = ''
            return False

    name = property(lambda self: self.load()._name,
                    doc=u'''
                                    Название медикамента.
                                    :rtype : unicode
                                ''')
    power = property(lambda self: self.load()._power,
                     doc=u'''
                                    Степень непереносимости.
                                    :rtype : int
                                ''')
    date = property(lambda self: self.load()._date,
                    doc=u'''
                                    Дата установления непереносимости.
                                    :rtype : CDateInfo
                                ''')
    notes = property(lambda self: self.load()._notes,
                     doc=u'''
                                    Примечания.
                                    :rtype : unicode
                                ''')

    #    def __unicode__(self):
    def __str__(self):
        return self.load()._name


class CClientAllergyInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientAllergy')
        idList = db.getIdList(table, 'id', table['client_id'].eq(self.clientId), 'id')
        self._items = [self.getInstance(CClientAllergyInfo, id) for id in idList]
        return True


class CClientAllergyInfo(CInfo):
    u"""
        Информация об аллергиях пациента.
    """

    def __init__(self, context, itemId):
        CInfo.__init__(self, context)
        self.itemId = itemId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientAllergy')
        record = db.getRecord(table, ['nameSubstance', 'power', 'createDate', 'notes'], self.itemId)
        if record:
            self._name = forceString(record.value('nameSubstance'))
            self._power = forceInt(record.value('power'))
            self._date = CDateInfo(record.value('createDate'))
            self._notes = forceString(record.value('notes'))
            return True
        else:
            self._name = ''
            self._power = 0
            self._date = CDateInfo(None)
            self._notes = ''
            return False

    name = property(lambda self: self.load()._name,
                    doc=u'''
                                    Наименование вещества.
                                    :rtype : unicode
                                ''')
    power = property(lambda self: self.load()._power,
                     doc=u'''
                                    Степень непереносимости.
                                    :rtype : int
                                ''')
    date = property(lambda self: self.load()._date,
                    doc=u'''
                                    Дата выявления аллергии.
                                    :rtype : CDateInfo
                                ''')
    notes = property(lambda self: self.load()._notes,
                     doc=u'''
                                    Примечания.
                                    :rtype : unicode
                                ''')

    #    def __unicode__(self):
    def __str__(self):
        return self.load()._name


# TODO: требуется документация
class CClientIdentificationInfo(CInfo):
    def __init__(self, context, clientId):
        CInfo.__init__(self, context)
        self._clientId = clientId
        self._byCode = {}
        #        self._byName = {}
        self._nameDict = {}
        self._checkDate = {}

    def _load(self):
        db = QtGui.qApp.db
        tableCI = db.table('ClientIdentification')
        tableAS = db.table('rbAccountingSystem')
        stmt = db.selectStmt(tableCI.leftJoin(tableAS, tableAS['id'].eq(tableCI['accountingSystem_id'])),
                             ['code', 'name', 'identifier', 'checkDate'],
                             db.joinAnd([tableCI['client_id'].eq(self._clientId),
                                         tableCI['deleted'].eq(0),
                                         ])
                             )
        query = db.query(stmt)
        while query.next():
            record = query.record()
            code = forceString(record.value('code'))
            name = forceString(record.value('name'))
            identifier = forceString(record.value('identifier'))
            checkDate = forceDate(record.value('checkDate'))
            self._byCode[code] = identifier
            #            self._byName[name] = identifier
            self._nameDict[code] = name
            self._checkDate[code] = CDateInfo(checkDate)
        return True

    def has_key(self, key):
        self.load()
        return key in self._byCode

    def get(self, key, default=None):
        self.load()
        return self._byCode.get(key, default)

    def iter(self):
        self.load()
        return self._byCode.iter()

    def iteritems(self):
        self.load()
        return self._byCode.iteritems()

    def iterkeys(self):
        self.load()
        return self._byCode.iterkeys()

    def itervalues(self):
        self.load()
        return self._byCode.itervalues()

    def items(self):
        self.load()
        return self._byCode.items()

    def keys(self):
        self.load()
        return self._byCode.keys()

    def values(self):
        self.load()
        return self._byCode.values()

    def __nonzero__(self):
        self.load()
        return bool(self._byCode)

    def __len__(self):
        self.load()
        return len(self._byCode)

    def __contains__(self, key):
        self.load()
        return key in self._byCode

    def __getitem__(self, key):
        self.load()
        return self._byCode.get(key, '')

    def __iter__(self):
        self.load()
        return self._byCode.iterkeys()

    def __str__(self):
        self.load()
        l = [u'%s (%s): %s, %s' % (self._nameDict[code], code, identifier, self._checkDate[code])
             for code, identifier in self._byCode.iteritems()
             ]
        l.sort()
        return ', '.join(l)

    byCode = property(lambda self: self.load()._byCode)
    #    byName = property(lambda self: self.load()._byName)
    nameDict = property(lambda self: self.load()._nameDict)
    checkDate = property(lambda self: self.load()._checkDate)


class CClientRelationInfoList(CInfoList):
    def __init__(self, context, clientId, date):
        CInfoList.__init__(self, context)
        self.clientId = clientId
        self.date = date

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientRelation')
        directIdList = db.getIdList(table,
                                    'id',
                                    db.joinAnd([table['deleted'].eq(0),
                                                table['relativeType_id'].isNotNull(),
                                                table['client_id'].eq(self.clientId)
                                                ]),
                                    'id')
        reversedIdList = db.getIdList(table,
                                      'id',
                                      db.joinAnd([table['deleted'].eq(0),
                                                  table['relativeType_id'].isNotNull(),
                                                  table['relative_id'].eq(self.clientId)
                                                  ]),
                                      'id')

        self._items = ([self.getInstance(CClientRelationInfo, id, self.date, True) for id in directIdList] +
                       [self.getInstance(CClientRelationInfo, id, self.date, False) for id in reversedIdList])
        return True


class CClientRelationInfo(CInfo):
    u"""
        Информация о родственных связях пациента
    """

    def __init__(self, context, itemId, date, isDirect):
        CInfo.__init__(self, context)
        self._itemId = itemId
        self._date = date
        self._isDirect = isDirect

    def _load(self):
        db = QtGui.qApp.db
        tableCR = db.table('ClientRelation')
        tableRT = db.table('rbRelationType')
        record = db.getRecord(tableCR.leftJoin(tableRT, tableRT['id'].eq(tableCR['relativeType_id'])),
                              ['client_id', 'relative_id',
                               'leftName', 'rightName',
                               'code',
                               'isDirectGenetic', 'isBackwardGenetic',
                               'isDirectRepresentative', 'isBackwardRepresentative',
                               'isDirectEpidemic', 'isBackwardEpidemic',
                               'isDirectDonation', 'isBackwardDonation',
                               'regionalCode', 'regionalReverseCode', 'freeInput'],
                              self._itemId)
        if record:
            leftName = forceString(record.value('leftName'))
            rightName = forceString(record.value('rightName'))
            code = forceString(record.value('code'))

            isDirectGenetic = forceBool(record.value('isDirectGenetic'))
            isBackwardGenetic = forceBool(record.value('isBackwardGenetic'))
            isDirectRepresentative = forceBool(record.value('isDirectRepresentative'))
            isBackwardRepresentative = forceBool(record.value('isBackwardRepresentative'))
            isDirectEpidemic = forceBool(record.value('isDirectEpidemic'))
            isBackwardEpidemic = forceBool(record.value('isBackwardEpidemic'))
            isDirectDonation = forceBool(record.value('isDirectDonation'))
            isBackwardDonation = forceBool(record.value('isBackwardDonation'))
            freeInput = forceString(record.value('freeInput'))

            if self._isDirect:
                clientId = forceRef(record.value('relative_id'))
                role, otherRole = leftName, rightName
                regionalCode = forceString(record.value('regionalCode'))
            else:
                clientId = forceRef(record.value('client_id'))
                role, otherRole = rightName, leftName
                regionalCode = forceString(record.value('regionalReverseCode'))
                isDirectGenetic, isBackwardGenetic = isBackwardGenetic, isDirectGenetic
                isDirectRepresentative, isBackwardRepresentative = isBackwardRepresentative, isDirectRepresentative
                isDirectEpidemic, isBackwardEpidemic = isBackwardEpidemic, isDirectEpidemic
                isDirectDonation, isBackwardDonation = isBackwardDonation, isDirectDonation

            self._role = role
            self._otherRole = otherRole
            if clientId and clientId != -1:
                self._other = self.getInstance(CClientInfo, clientId, self._date)
            else:
                self._other = forceString(record.value('freeInput'))

            self._name = role + ' -> ' + otherRole
            self._code = code
            self._regionalCode = regionalCode
            self._isDirectGenetic = isDirectGenetic
            self._isBackwardGenetic = isBackwardGenetic
            self._isDirectRepresentative = isDirectRepresentative
            self._isBackwardRepresentative = isBackwardRepresentative
            self._isDirectEpidemic = isDirectEpidemic
            self._isBackwardEpidemic = isBackwardEpidemic
            self._isDirectDonation = isDirectDonation
            self._isBackwardDonation = isBackwardDonation
            self._freeInput = freeInput
            return True
        else:
            self._role = ''
            self._otherRole = ''
            self._other = None
            self._name = ''
            self._code = ''
            self._regionalCode = ''
            self._isDirectGenetic = False
            self._isBackwardGenetic = False
            self._isDirectRepresentative = False
            self._isBackwardRepresentative = False
            self._isDirectEpidemic = False
            self._isBackwardEpidemic = False
            self._isDirectDonation = False
            self._isBackwardDonation = False
            self._freeInput = ''
            return False

    role = property(lambda self: self.load()._role,
                    doc=u'''
                                    Роль пациента в связи (например, мать).
                                    :rtype : unicode
                                ''')
    otherRole = property(lambda self: self.load()._otherRole,
                         doc=u'''
                                    Роль второго участника связи (например, сын).
                                    :rtype : unicode
                                ''')
    other = property(lambda self: self.load()._other,
                     doc=u'''
                                    Информация о втором участнике связи. Объект CClientInfo, второй участник занесен в базу данных. В противном случае, текстовое представление информации.
                                    :rtype : CClientInfo or unicode
                                ''')
    name = property(lambda self: self.load()._name,
                    doc=u'''
                                    Полное строковое представление типа связи. Слева указывается роль пациента, справа - роль второго участника. (например, Мать -> Сын).
                                    :rtype : unicode
                                ''')
    code = property(lambda self: self.load()._code,
                    doc=u'''
                                    Код типа связи.
                                    :rtype : unicode
                                ''')
    regionalCode = property(lambda self: self.load()._regionalCode,
                            doc=u'''
                                    Региональный код типа связи.
                                    :rtype : unicode
                                ''')
    isDirectGenetic = property(lambda self: self.load()._isDirectGenetic,
                               doc=u'''
                                    .
                                    :rtype : unicode
                                ''')
    isBackwardGenetic = property(lambda self: self.load()._isBackwardGenetic,
                                 doc=u'''
                                    Примечания.
                                    :rtype : unicode
                                ''')
    isDirectRepresentative = property(lambda self: self.load()._isDirectRepresentative,
                                      doc=u'''
                                    Примечания.
                                    :rtype : unicode
                                ''')
    isBackwardRepresentative = property(lambda self: self.load()._isBackwardRepresentative,
                                        doc=u'''
                                    Примечания.
                                    :rtype : unicode
                                ''')
    isDirectEpidemic = property(lambda self: self.load()._isDirectEpidemic,
                                doc=u'''
                                    Примечания.
                                    :rtype : unicode
                                ''')
    isBackwardEpidemic = property(lambda self: self.load()._isBackwardEpidemic,
                                  doc=u'''
                                    Примечания.
                                    :rtype : unicode
                                ''')
    isDirectDonation = property(lambda self: self.load()._isDirectDonation,
                                doc=u'''
                                    Примечания.
                                    :rtype : unicode
                                ''')
    isBackwardDonation = property(lambda self: self.load()._isBackwardDonation,
                                  doc=u'''
                                    Примечания.
                                    :rtype : unicode
                                ''')
    freeInput = property(lambda self: self.load()._freeInput,
                         doc=u'''
                                    Примечания.
                                    :rtype : unicode
                                ''')

    def __str__(self):
        return self.name + ' ' + self.other


class CClientQuotaInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Client_Quoting')
        idList = db.getIdList(table,
                              'id',
                              db.joinAnd([table['deleted'].eq(0),
                                          table['master_id'].eq(self.clientId)
                                          ]),
                              'directionDate, id')
        self._items = ([self.getInstance(CClientQuotaInfo, id) for id in idList])
        return True


class CRBHospitalizationPurposeInfo(CRBInfo):
    tableName = 'rbHospitalizationPurpose'


class CClientForeignHospitalizationInfo(CInfo):
    u"""
        Информация о госпитализациях в других ЛПУ
    """

    def __init__(self, context, itemId):
        CInfo.__init__(self, context)
        self._itemId = itemId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ForeignHospitalization')
        record = db.getRecord(table, ['*'], self._itemId)
        if record:
            self._purpose = self.getInstance(CRBHospitalizationPurposeInfo, forceRef(record.value('purpose_id')))
            self._org = self.getInstance(COrgInfo, forceRef(record.value('org_id')))
            self._MKB = forceString(record.value('MKB'))
            self._clinicDiagnosis = forceString(record.value('clinicDiagnosis'))
            self._startDate = CDateInfo(forceDate(record.value('startDate')))
            self._endDate = CDateInfo(forceDate(record.value('endDate')))
            return True
        else:
            self._purpose = self.getInstance(CRBHospitalizationPurposeInfo, None)
            self._org = self.getInstance(COrgInfo, None)
            self._MKB = ''
            self._clinicDiagnosis = ''
            self._startDate = ''
            self._endDate = ''
            return False

    purpose = property(lambda self: self.load()._purpose,
                       doc=u'''
                                Цель госпитализации.
                                :rtype : CRBHospitalizationPurposeInfo
                            ''')
    org = property(lambda self: self.load()._org,
                   doc=u'''
                                ЛПУ.
                                :rtype : COrgInfo
                            ''')
    MKB = property(lambda self: self.load()._MKB,
                   doc=u'''
                                МКБ.
                                :rtype : unicode
                            ''')
    clinicDiagnosis = property(lambda self: self.load()._clinicDiagnosis,
                               doc=u'''
                                Клинический диагноз.
                                :rtype : unicode
                            ''')
    startDate = property(lambda self: self.load()._startDate,
                         doc=u'''
                                Дата поступления.
                                :rtype : CDateInfo
                            ''')
    endDate = property(lambda self: self.load()._endDate,
                       doc=u'''
                                Дата выбытия.
                                :rtype : CDateInfo
                            ''')


class CClientForeignHospitalizationInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ForeignHospitalization')
        idList = db.getIdList(table, 'id', [table['client_id'].eq(self.clientId), table['deleted'].eq(0)], 'id')
        self._items = ([self.getInstance(CClientForeignHospitalizationInfo, itemId) for itemId in idList])
        return True


class CQuotaTypeInfo(CRBInfo):
    tableName = 'QuotaType'

    def __init__(self, context, id):
        CRBInfo.__init__(self, context, id)

    def _initByRecord(self, record):
        self._class = forceInt(record.value('class'))
        self._group = forceString(record.value('group_code'))
        self._code = forceString(record.value('code'))
        self._name = forceString(record.value('name'))

    def _initByNull(self):
        self._class = 0
        self._group = ''
        self._code = ''
        self._name = ''

    class_ = property(lambda self: self.load()._class)
    group = property(lambda self: self.load()._group)
    code = property(lambda self: self.load()._code)
    name = property(lambda self: self.load()._name)


class CClientQuotaInfo(CInfo):
    def __init__(self, context, itemId):
        CInfo.__init__(self, context)
        self._itemId = itemId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Client_Quoting')
        record = db.getRecord(table, '*', self._itemId)
        if record:
            result = True
        else:
            record = table.newRecord()
            result = False

        self._identifier = forceString(record.value('identifier'))
        self._ticket = forceString(record.value('quotaTicket'))
        self._type = self.getInstance(CQuotaTypeInfo, forceRef(record.value('quotaType_id')))
        self._stage = forceInt(record.value('stage'))
        self._directionDate = CDateInfo(forceDate(record.value('directionDate')))
        self._freeInput = forceString(record.value('freeInput'))
        self._org = self.getInstance(COrgInfo, forceRef(record.value('org_id')))
        self._amount = forceInt(record.value('amount'))
        self._MKB = forceString(record.value('MKB'))
        self._status = forceInt(record.value('status'))
        self._request = forceInt(record.value('request'))
        self._statement = forceString(record.value('statment'))
        self._registrationDate = CDateInfo(forceDate(record.value('dateRegistration')))
        self._endDate = CDateInfo(forceDate(record.value('dateEnd')))
        self._orgStructure = self.getInstance(COrgStructureInfo, forceRef(record.value('orgStructure_id')))
        self._regionCode = forceString(record.value('regionCode'))
        self._discussion = self.getInstance(CQuotaDiscussionInfoList, self._itemId)
        return result

    identifier = property(lambda self: self.load()._identifier)
    ticket = property(lambda self: self.load()._ticket)
    type = property(lambda self: self.load()._type)
    stage = property(lambda self: self.load()._stage)
    directionDate = property(lambda self: self.load()._directionDate)
    freeInput = property(lambda self: self.load()._freeInput)
    org = property(lambda self: self.load()._org)
    amount = property(lambda self: self.load()._amount)
    MKB = property(lambda self: self.load()._MKB)
    status = property(lambda self: self.load()._status)
    request = property(lambda self: self.load()._request)
    statement = property(lambda self: self.load()._statement)
    registrationDate = property(lambda self: self.load()._registrationDate)
    endDate = property(lambda self: self.load()._endDate)
    orgStructure = property(lambda self: self.load()._orgStructure)
    regionCode = property(lambda self: self.load()._regionCode)
    discussion = property(lambda self: self.load().discussion)

    def __str__(self):
        return self.identifier + ' ' + self.ticket


class CQuotaDiscussionInfoList(CInfoList):
    def __init__(self, context, quotaId):
        CInfoList.__init__(self, context)
        self.quotaId = quotaId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Client_QuotingDiscussion')
        idList = db.getIdList(table, 'id', table['master_id'].eq(self.quotaId), 'id')
        self._items = ([self.getInstance(CQuotaDiscussionInfo, id) for id in idList])
        return True


class CQuotaAgreementTypeInfo(CRBInfo):
    tableName = 'rbAgreementType'


class CQuotaDiscussionInfo(CInfo):
    def __init__(self, context, itemId):
        CInfo.__init__(self, context)
        self._itemId = itemId

    def _load(self):
        from Orgs.PersonInfo import CPersonInfo

        db = QtGui.qApp.db
        table = db.table('Client_QuotingDiscussion')
        record = db.getRecord(table, '*', self._itemId)
        if record:
            result = True
        else:
            record = table.newRecord()
            result = False

        self._date = CDateInfo(forceDate(record.value('dateMessage')))
        self._agreementType = self.getInstance(CQuotaAgreementTypeInfo, forceRef(record.value('agreementType_id')))
        self._person = self.getInstance(CPersonInfo, forceRef(record.value('responsiblePerson_id')))
        self._cosignatory = forceString(record.value('cosignatory'))
        self._cosignatoryPost = forceString(record.value('cosignatoryPost'))
        self._cosignatoryName = forceString(record.value('cosignatoryName'))
        self._remark = forceString(record.value('remark'))

    date = property(lambda self: self.load()._date)
    agreementType = property(lambda self: self.load()._agreementType)
    person = property(lambda self: self.load()._person)
    cosignatory = property(lambda self: self.load()._cosignatory)
    cosignatoryPost = property(lambda self: self.load()._cosignatoryPost)
    cosignatoryName = property(lambda self: self.load()._cosignatoryName)
    remark = property(lambda self: self.load()._remark)

    def __str__(self):
        return self.date + ' ' + self.remark + ' ' + self.person


class CClientPaymentSchemeInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Client_PaymentScheme')
        idList = db.getIdList(table,
                              'id',
                              db.joinAnd([table['deleted'].eq(0),
                                          table['client_id'].eq(self.clientId)]),
                              'begDate, id')
        self._items = ([self.getInstance(CClientPaymentSchemeInfo, id) for id in idList])
        return True


class CClientPaymentSchemeInfo(CInfo):
    def __init__(self, context, itemId):
        CInfo.__init__(self, context)
        self._itemId = itemId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('Client_PaymentScheme')
        record = db.getRecord(table, '*', self._itemId)
        if record:
            result = True
        else:
            record = table.newRecord()
            result = False
        self._begDate = CDateInfo(forceDate(record.value('begDate')))
        self._endDate = CDateInfo(forceDate(record.value('endDate')))
        return result

    begDate = property(lambda self: self.load()._begDate)
    endDate = property(lambda self: self.load()._endDate)


class CRBCompulsoryTreatmentKindInfo(CRBInfo):
    tableName = 'rbCompulsoryTreatmentKind'


class CClientCompulsoryTreatmentInfo(CInfo):
    u"""
        Информация о госпитализациях в других ЛПУ
    """

    def __init__(self, context, itemId):
        CInfo.__init__(self, context)
        self._itemId = itemId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientCompulsoryTreatment')
        record = db.getRecord(table, '*', self._itemId)
        if record:
            self._setKind = self.getInstance(CRBCompulsoryTreatmentKindInfo, forceRef(record.value('setKind_id')))
            self._newKind = self.getInstance(CRBCompulsoryTreatmentKindInfo, forceRef(record.value('newKind_id')))
            self._begDate = CDateInfo(forceDate(record.value('begDate')))
            self._endDate = CDateInfo(forceDate(record.value('endDate')))
            self._extensionDate = CDateInfo(forceDate(record.value('extensionDate')))
            self._note = forceString(record.value('note'))
            return True
        else:
            self._setKind = self.getInstance(CRBCompulsoryTreatmentKindInfo, None)
            self._newKind = self.getInstance(CRBCompulsoryTreatmentKindInfo, None)
            self._begDate = CDateInfo()
            self._endDate = CDateInfo()
            self._extensionDate = CDateInfo()
            self._note = ''
            return False

    setKind = property(lambda self: self.load()._setKind,
                       doc=u'''
                                Назначенный вид принудительного лечения.
                                :rtype : CRBCompulsoryTreatmentKindInfo
                            ''')
    newKind = property(lambda self: self.load()._newKind,
                       doc=u'''
                                Изменённый вид принудительного лечения.
                                :rtype : CRBCompulsoryTreatmentKindInfo
                            ''')
    begDate = property(lambda self: self.load()._begDate,
                       doc=u'''
                                Дата решения суда о начале лечения.
                                :rtype : CDateInfo
                            ''')
    endDate = property(lambda self: self.load()._endDate,
                       doc=u'''
                                Дата решения суда об окончании принуд. лечения.
                                :rtype : CDateInfo
                            ''')
    extensionDate = property(lambda self: self.load()._extensionDate,
                             doc=u'''
                                Дата изменения вида (продления).
                                :rtype : CDateInfo
                            ''')
    note = property(lambda self: self.load()._note,
                    doc=u'''
                                Примечание.
                                :rtype : unicode
                            ''')


class CClientCompulsoryTreatmentInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientCompulsoryTreatment')
        idList = db.getIdList(table, 'id', [table['client_id'].eq(self.clientId), table['deleted'].eq(0)], 'id')
        self._items = ([self.getInstance(CClientCompulsoryTreatmentInfo, itemId) for itemId in idList])
        return True


class CRBClientMonitoringKindInfo(CRBInfo):
    tableName = "rbClientMonitoringKind"


class CRBClientMonitoringFrequenceInfo(CRBInfo):
    tableName = "rbClientMonitoringFrequence"


class CRBStopMonitoringReasonInfo(CRBInfo):
    tableName = "rbStopMonitoringReason"


class CClientMonitoringInfo(CInfo):
    def __init__(self, context, itemId):
        CInfo.__init__(self, context, itemId)
        self._id = itemId
        self._kind = self.getInstance(CRBClientMonitoringKindInfo, None)
        self._frequence = self.getInstance(CRBClientMonitoringFrequenceInfo, None)
        self._reason = self.getInstance(CRBStopMonitoringReasonInfo, None)
        self._setDate = CDateInfo()
        self._endDate = CDateInfo()

    def _load(self):
        if self._id:
            db = QtGui.qApp.db
            table = db.table('ClientMonitoring')
            record = db.getRecordEx(table, '*', [table['id'].eq(self._id), table['deleted'].eq(0)])
            if record:
                self._kind = self.getInstance(CRBClientMonitoringKindInfo, forceRef(record.value('kind_id')))
                self._frequence = self.getInstance(CRBClientMonitoringFrequenceInfo,
                                                   forceRef(record.value('frequence_id')))
                self._reason = self.getInstance(CRBStopMonitoringReasonInfo, forceRef(record.value('reason_id')))
                self._setDate = CDateInfo(forceDate(record.value('setDate')))
                self._endDate = CDateInfo(forceDate(record.value('endDate')))
                if not self._reason:
                    self._reason = forceString(record.value('reason'))
                return True
        return False

    setDate = property(lambda self: self.load()._setDate,
                       doc=u"""
                                      Дата начала
                                      :rtype : CDateInfo
                                  """)
    endDate = property(lambda self: self.load()._endDate,
                       doc=u"""
                                      Дата окончания
                                      :rtype : CDateInfo
                                  """)
    kind = property(lambda self: self.load()._kind,
                    doc=u"""
                                      Вид наблюдения
                                      :rtype : CRBClientMonitoringKindInfo
                                  """)
    frequence = property(lambda self: self.load()._frequence,
                         doc=u"""
                                      Частота наблюдения
                                      :rtype : CRBClientMonitoringFrequenceInfo
                                  """)
    reason = property(lambda self: self.load()._reason,
                      doc=u"""
                                      Причина прекращения наблюдения
                                      :rtype : CRBStopMonitoringReasonInfo or unicode
                                  """)


class CClientMonitoringInfoList(CInfoList):
    def __init__(self, context, clientId):
        CInfoList.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('ClientMonitoring')
        idList = db.getIdList(table, 'id', [table['client_id'].eq(self.clientId), table['deleted'].eq(0)], 'id')
        self._items = [self.getInstance(CClientMonitoringInfo, itemId) for itemId in idList]
        return True


def getClientInfo2(id, date=None):
    context = CInfoContext()
    return CClientInfo(context, id, date)


def fixClientDeath(clientId, deathDate, fixDeathDate, orgId):
    db = QtGui.qApp.db
    attDeathId = forceRef(db.translate('rbAttachType', 'code', attDeath, 'id'))
    if attDeathId:
        record = selectLatestRecord('ClientAttach', clientId, 'attachType_id=%d' % attDeathId)
        if not record:
            record = db.table('ClientAttach').newRecord()
            record.setValue('attachType_id', toVariant(attDeathId))
            record.setValue('client_id', toVariant(clientId))
        record.setValue('LPU_id', toVariant(orgId if orgId else QtGui.qApp.currentOrgId()))
        record.setValue('deleted', toVariant(0))
        record.setValue('begDate', toVariant(deathDate))
        record.setValue('endDate', toVariant(fixDeathDate))
        db.insertOrUpdate('ClientAttach', record)


def getClientIdentification(clientId):
    result = {}
    stmt = """
    SELECT r.name, ci.identifier, ci.checkDate
    FROM ClientIdentification ci
    LEFT JOIN rbAccountingSystem r ON r.id = ci.accountingSystem_id
    WHERE ci.deleted = 0 AND ci.client_id = %d
        AND r.showInClientInfo = 1
    """ % clientId
    db = QtGui.qApp.db
    query = db.query(stmt)
    while query.next():
        r = query.record()
        if r:
            result[forceString(r.value(0))] = (forceString(r.value(1)), forceDate(r.value(2)))
    return result


def getClientIdentificationWithCounter(clientId, withCounter=True):
    result = {}
    stmt = """
    SELECT r.name, ci.identifier, ci.checkDate
    FROM ClientIdentification ci
    LEFT JOIN rbAccountingSystem r ON r.id = ci.accountingSystem_id
    WHERE ci.deleted = 0 AND ci.client_id = %d
        AND r.showInClientInfo = 1
        AND r.counter_id IS %s NULL
    """ % (clientId, 'NOT' if withCounter else '')
    db = QtGui.qApp.db
    query = db.query(stmt)
    while query.next():
        r = query.record()
        if r:
            result[forceString(r.value(0))] = (forceString(r.value(1)), forceDate(r.value(2)))
    return result


def findKLADRRegionRecordsInQuoting(code, quotingRecord):
    def getValueFromRecords(records):
        res = []
        for rec in records:
            res.append(forceString(rec.value('region_code')))
        return res

    def appendCode(list, code, codesList, recordsList):
        if code in codesList:
            x = codesList.index(code)
            list.append(recordsList[x])

    db = QtGui.qApp.db
    model = getKladrTreeModel()
    item = model.getRootItem().findCode(code)
    quotingId = forceInt(quotingRecord.value('id'))
    cond = 'Quoting_Region.`master_id`=%d AND Quoting_Region.`deleted`=0' % quotingId
    quotingRegionRecords = db.getRecordList('Quoting_Region', '*', cond)
    codesList = getValueFromRecords(quotingRegionRecords)
    resumeList = []
    appendCode(resumeList, code, codesList, quotingRegionRecords)
    item = item.parent()
    while item:
        code = item._code
        appendCode(resumeList, code, codesList, quotingRegionRecords)
        item = item.parent()
    return resumeList


def uniqueIdentifierCheckingIsPassed(currentItemId, accountingSystemId, newIdentifier):
    db = QtGui.qApp.db
    table = db.table('ClientIdentification')
    cond = [table['accountingSystem_id'].eq(accountingSystemId),
            table['identifier'].eq(newIdentifier)]
    if currentItemId:
        cond.append(table['id'].ne(currentItemId))
    record = db.getRecordEx(table, 'id', cond)
    if record:
        QtGui.QMessageBox.warning(QtGui.qApp.mainWindow, u'Изменение идентификатора',
                                  u'В выбранной учётной системе требуется ввод уникального идентификатора.\n\'%s\' не уникален' % newIdentifier,
                                  QtGui.QMessageBox.Close)
        return False
    return True


class CPolicyKindCache(CDbEntityCache):
    mapIdToCode = {}
    mapCodeToId = {}

    @classmethod
    def purge(cls):
        cls.mapIdToCode.clear()

    @classmethod
    def getCode(cls, itemId):
        code = cls.mapIdToCode.get(id, False)
        if code == False:
            cls.connect()
            code = forceString(QtGui.qApp.db.translate('rbPolicyKind', 'id', itemId, 'code'))
            cls.mapIdToCode[itemId] = code
            cls.mapCodeToId[code] = itemId
        return code

    @classmethod
    def getId(cls, code):
        itemId = cls.mapCodeToId.get(code, False)
        if itemId == False:
            cls.connect()
            itemId = forceString(QtGui.qApp.db.translate('rbPolicyKind', 'id', itemId, 'code'))
            cls.mapIdToCode[itemId] = code
            cls.mapCodeToId[code] = itemId
        return itemId


class CSocStatusTypeCache(CDbEntityCache):
    mapIdToCode = {}
    mapIdToName = {}

    @classmethod
    def purge(cls):
        cls.mapIdToCode.clear()
        cls.mapIdToName.clear()

    @classmethod
    def register(cls, id):
        cls.connect()
        record = QtGui.qApp.db.getRecord('rbSocStatusType', ['code', 'name'], id)
        if record:
            code = forceString(record.value(0))
            name = forceString(record.value(1))
        else:
            code = name = u'Соц.статус {%r}' % id
        cls.mapIdToCode[id] = code
        cls.mapIdToName[id] = name
        return code, name

    @classmethod
    def getCode(cls, id):
        result = cls.mapIdToCode.get(id, False)
        if result == False:
            result, name = cls.register(id)
        return result

    @classmethod
    def getName(cls, id):
        result = cls.mapIdToName.get(id, False)
        if result == False:
            code, result = cls.register(id)
        return result


def canRemoveEventWithTissue():
    widget = QtGui.qApp.mainWindow
    hasRight = QtGui.qApp.userHasRight(urDeleteEventWithTissue)
    if hasRight:
        mbResult = QtGui.QMessageBox.question(widget,
                                              u'Внимание!',
                                              u'В событии присутствуют действия, связанные с забором биоматериалов.\nУдалить?',
                                              QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                              QtGui.QMessageBox.No)
        result = mbResult == QtGui.QMessageBox.Yes
    else:
        result = False
        QtGui.QMessageBox.warning(widget,
                                  u'Внимание!',
                                  u'В событии присутствуют действия, связанные с забором биоматериалов.\nУ вас нет прав на удаление',
                                  QtGui.QMessageBox.Ok)
    return result


def canRemoveEventWithJobTicket():
    widget = QtGui.qApp.mainWindow
    hasRight = QtGui.qApp.userHasRight(urDeleteEventWithJobTicket)
    if hasRight:
        mbResult = QtGui.QMessageBox.question(widget,
                                              u'Внимание!',
                                              u'В событии присутствуют действия, связанные с номерками.\nУдалить?',
                                              QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                              QtGui.QMessageBox.No)
        result = mbResult == QtGui.QMessageBox.Yes
    else:
        result = False
        QtGui.QMessageBox.warning(widget,
                                  u'Внимание!',
                                  u'В событии присутствуют действия, связанные с номерками.\nУ вас нет прав на удаление',
                                  QtGui.QMessageBox.Ok)
    return result


def getClientQueueNumber(clientId, date):
    if not QtGui.qApp.isUseUnifiedDailyClientQueueNumber():
        return None
    db = QtGui.qApp.db
    tableClientQueueNumber = db.table('ClientQueueNumber')
    cond = [tableClientQueueNumber['client_id'].eq(clientId),
            tableClientQueueNumber['date'].eq(date)]

    record = db.getRecordEx(tableClientQueueNumber, tableClientQueueNumber['number'], cond)
    return forceInt(record.value('number')) if record else None


def assignTodayQueueNumberToClient(clientId, date):
    if not clientId:
        return 0

    number = getClientQueueNumber(clientId, date)
    if number:
        return number

    db = QtGui.qApp.db
    tableClientQueueNumber = db.table('ClientQueueNumber')
    maxBusyNumberRecord = db.getRecordEx(tableClientQueueNumber,
                                         'MAX(number) as maxNumber',
                                         [tableClientQueueNumber['date'].eq(date)])
    newNumber = forceInt(maxBusyNumberRecord.value('maxNumber')) + 1 if maxBusyNumberRecord else 1
    record = tableClientQueueNumber.newRecord()
    record.setValue('client_id', toVariant(clientId))
    record.setValue('date', toVariant(date))
    record.setValue('number', toVariant(newNumber))
    db.insertOrUpdate(tableClientQueueNumber, record)
    return newNumber


def hasSocStatus(clientId, socStatuses):
    if clientId is None:
        return False
    db = QtGui.qApp.db
    tableCSS = db.table('ClientSocStatus')
    tableRBSST = db.table('rbSocStatusType')
    tableRBSSC = db.table('rbSocStatusClass')
    queryTable = tableCSS.innerJoin(tableRBSST, tableCSS['socStatusType_id'].eq(tableRBSST['id']))
    queryTable = queryTable.innerJoin(tableRBSSC, tableCSS['socStatusClass_id'].eq(tableRBSSC['id']))
    cond = [tableCSS['client_id'].eq(clientId),
            tableCSS['deleted'].eq(0),
            db.joinOr([
                          db.joinAnd([
                              tableRBSSC['flatCode'].eq(socStatusClass),
                              tableRBSST['code'].inlist(socStatuses[socStatusClass])
                          ]) for socStatusClass in socStatuses.keys()
                          ])]

    return db.getRecordEx(queryTable, tableCSS['id'], where=cond) is not None


class CClientStatusObservationInfo(CInfo):
    u"""
        Статус наблюдения пациента
        код: {client.statusObservation.code},
        наименование: <font color={client.statusObservation.color}>{client.statusObservation.name}</font>
        {client.statusObservation} <!-- то же, что и {client.statusObservation.name} -->
    """

    def __init__(self, context, clientId):
        CInfo.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        db = QtGui.qApp.db
        tableCSO = db.table('Client_StatusObservation')
        tableSOCT = db.table('rbStatusObservationClientType')
        record = db.getRecordEx(tableCSO.leftJoin(tableSOCT, tableSOCT['id'].eq(tableCSO['statusObservationType_id'])),
                                [tableSOCT['code'].alias('code'),
                                 tableSOCT['name'].alias('name'),
                                 tableSOCT['color'].alias('color')],
                                [tableCSO['master_id'].eq(self.clientId),
                                 tableCSO['deleted'].eq(0)])
        if not record is None:
            self._code = forceString(record.value('code'))
            self._name = forceString(record.value('name'))
            self._color = forceString(record.value('color'))
            return True
        else:
            self._code = ''
            self._name = ''
            self._color = ''
            return False

    code = property(lambda self: self.load()._code,
                    doc=u'''
                        Код статуса наблюдения.
                        :rtype : unicode
                    ''')
    name = property(lambda self: self.load()._name,
                    doc=u'''
                        Наименование статуса наблюдения.
                        :rtype : unicode
                    ''')
    color = property(lambda self: self.load()._color,
                     doc=u'''
                        Цвет статуса наблюдения.
                        :rtype : unicode
                    ''')

    def __str__(self):
        return self.load()._name


class CClientBodyStatsInfo(CInfo):
    def __init__(self, context, clientId):
        CInfo.__init__(self, context)
        self.clientId = clientId

    def _load(self):
        record = getClientBodyStats(self.clientId)
        if not record is None:
            self._weight = forceString(record.value('weight'))
            self._height = forceString(record.value('height'))
            return True
        else:
            self._weight = ''
            self._height = ''
            return False

    weight = property(lambda self: self.load()._weight)
    height = property(lambda self: self.load()._height)


def getClientBodyStats(clientId):
    return selectLatestRecord('ClientBodyStats', clientId, deleted=False)


def editClientVIPStatus(clientId, comment=None, delete=False, color='#FFD700'):
    db = QtGui.qApp.db
    userId = QtGui.qApp.userId
    tableClientVIP = db.table('ClientVIP')

    currentStatus = db.getRecordEx(
        tableClientVIP,
        '*',
        [
            tableClientVIP['deleted'].eq(0),
            tableClientVIP['client_id'].eq(clientId)
        ]
    )

    if currentStatus:
        currentStatus.setValue('deleted', toVariant(1))
        currentStatus.setValue('deletePerson_id', toVariant(userId))
        currentStatus.setValue('deleteDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
        db.insertOrUpdate(tableClientVIP, currentStatus)

    if not delete:
        record = tableClientVIP.newRecord()
        record.setValue('client_id', toVariant(clientId))
        record.setValue('createPerson_id', toVariant(userId))
        record.setValue('createDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
        record.setValue('color', toVariant(color))
        if comment:
            record.setValue('comment', toVariant(comment))
        db.insertOrUpdate(tableClientVIP, record)


def editClientVIPComment(clientId, comment):
    db = QtGui.qApp.db
    userId = QtGui.qApp.userId
    tableClientVIP = db.table('ClientVIP')

    currentStatus = db.getRecordEx(
        tableClientVIP,
        '*',
        [
            tableClientVIP['deleted'].eq(0),
            tableClientVIP['client_id'].eq(clientId)
        ]
    )

    if currentStatus:
        currentStatus.setValue('comment', toVariant(comment))
        db.insertOrUpdate(tableClientVIP, currentStatus)


def getClientOncologyForm90Record(clientId):
    return QtGui.qApp.db.getRecordEx(stmt='''
        SELECT a.*
        FROM Action a
          INNER JOIN Event e ON a.event_id = e.id
          INNER JOIN ActionType at ON a.actionType_id = at.id AND at.flatCode = 'f90'
        WHERE e.client_id = %d AND a.deleted = 0 AND e.deleted = 0 AND at.deleted = 0
        ''' % clientId)


def clientHasOncologyForm90(clientId):
    return bool(getClientOncologyForm90Record(clientId))


def clientHasOncologyEvent(clientId, excludeEventIds=None):
    if isinstance(excludeEventIds, (int, str, unicode)):
        excludeEventIds = [excludeEventIds]
    elif excludeEventIds is None:
        excludeEventIds = [-1]
    excludeEventIds = [str(x) for x in excludeEventIds]

    return bool(QtGui.qApp.db.getCount(stmt='''
        SELECT e.id
        FROM Event e
          INNER JOIN Diagnostic dc ON e.id = dc.event_id
          INNER JOIN Diagnosis ds ON dc.diagnosis_id = ds.id
          INNER JOIN Person p ON e.execPerson_id = p.id
          INNER JOIN rbSpeciality s ON p.speciality_id = s.id
        WHERE 
          ds.MKB LIKE 'C%' AND
          s.shouldFillOncologyForm90 = 1 AND 
          e.deleted = 0 AND 
          dc.deleted = 0 AND 
          ds.deleted = 0 AND 
          e.client_id = {clientId} AND
          e.id NOT IN ({excludeEventIds})
        '''.format(clientId=clientId, excludeEventIds=', '.join(excludeEventIds))))


def hasUnpaidMXActions(eventId):
    for row in QtGui.qApp.db.iterRecordList(stmt=u'''
            SELECT a.payStatus, af.code AS actionFinance, cf.code AS contractFinance
            FROM Event e
              INNER JOIN EventType et ON et.id = e.eventType_id AND et.form IN ('000', '003')
              INNER JOIN Action a ON e.id = a.event_id AND a.deleted = 0
              INNER JOIN ActionType at ON a.actionType_id = at.id AND at.name LIKE 'МХ:%' AND at.serviceType = 4
              LEFT JOIN rbFinance af ON af.id = a.finance_id
              LEFT JOIN Contract ctr ON e.contract_id = ctr.id AND ctr.ignorePayStatusForJobs = 0
              LEFT JOIN rbFinance cf ON cf.id = ctr.finance_id
              -- INNER JOIN Account_Item ai ON ai.event_id = e.id AND ai.action_id = a.id AND ai.deleted = 0
            WHERE e.id = '{eventId}'
            '''.format(eventId=eventId)):
        payStatus = forceInt(row.value('payStatus'))
        actionFinance = forceInt(row.value('actionFinance'))
        contractFinance = forceInt(row.value('contractFinance'))

        for financeCode in (actionFinance, contractFinance):
            if financeCode == CFinanceType.cash and extractLonePayStaus(payStatus, financeCode) != CPayStatus.payed:
                return True

    return False


def getDailyAvaliableQueueShare(personId=None, specialityId=None):
    u"""
    Относительное количество (в процентах) доступных номерков по дням
    :param personId: Person.id
    :param specialityId: rbSpeciality.id
    :rtype: list[int]
    :return: [ процент доступных номерков по дням, начиная с текущей даты ]
    """
    db = QtGui.qApp.db
    tablePerson = db.table('Person')
    tableSpecialityQS = db.table('rbSpecialityQueueShare')

    table = tableSpecialityQS

    if personId is not None:
        table = table.innerJoin(tablePerson, tablePerson['speciality_id'].eq(tableSpecialityQS['speciality_id']))
        cond = [
            tablePerson['id'].eq(personId)
        ]
    elif specialityId is not None:
        cond = [
            tableSpecialityQS['speciality_id'].eq(specialityId)
        ]
    else:
        return []

    return db.getColumnValues(table,
                              column=tableSpecialityQS['available'],
                              where=cond,
                              order=tableSpecialityQS['day'],
                              handler=forceInt)


def getAvailableQueueShare(date, personId=None, specialityId=None):
    queueShare = getDailyAvaliableQueueShare(personId, specialityId)
    if queueShare and date:
        days = QtCore.QDate.currentDate().daysTo(date)
        if 0 <= days < len(queueShare):
            return queueShare[days]
    return 100
