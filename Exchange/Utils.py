#!/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
from zipfile import *

from Registry.Utils import *
from library import database
from library.PreferencesMixin import CPreferencesMixin
from library.Utils import *
from library.crbcombobox import CRBModelDataCache
from library.dbfpy.dbf import Dbf
from library.exception import CException, CRarException
from library.vm_collections import OrderedDict

MIS_REFUSE_ACCOUNT_NUMBER = u'Отказано МИС'

logger = None

def getLogger():
    global logger
    if logger is None:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.WARN)

    return logger

def getAdditionalPersonIdList(lstSNILS = []):
    stmt = u"""
    SELECT DISTINCT
        p.id AS id
    FROM
        Person p
    WHERE
        p.deleted = 0
        {lstSNILS}
    """.format(lstSNILS=(u'AND p.SNILS IN(%s)' % u','.join(map(str, lstSNILS))) if lstSNILS else u'AND p.SNILS IN("0")')
    record = QtGui.qApp.db.getRecordList(stmt=stmt)
    return [forceRef(x.value('id')) for x in record]

def getPersonIdList(idList=None):
    stmt = u"""
    SELECT DISTINCT
        p.id AS id,
        p.regionalCode,
        p.lastName,
        p.firstName,
        p.patrName,
        p.sex,
        p.birthDate
    FROM
        Person p
    WHERE
        p.deleted = 0
        AND p.speciality_id IS NOT NULL
        AND p.regionalCode IS NOT NULL
        {idList}
        AND LENGTH(p.regionalCode) >= 1
        AND (p.retireDate IS NULL)
    GROUP BY
        p.lastName,
        p.firstName,
        p.patrName,
        p.birthDate
    """.format(idList=(u'AND p.id IN(%s)' % u','.join(map(str, idList))) if idList else u'')
    record = QtGui.qApp.db.getRecordList(stmt=stmt)
    return [forceRef(x.value('id')) for x in record]


#TODO: atronah: добавить поддержку архивирования папок с поддержкой структуры
def makeZipArchive(widget, fileList, zipName = None, isRemoveSource = False):
    import zipfile
    zipExt = u'.zip'
    dirName = QtCore.QDir.homePath()
    if isinstance(zipName, (basestring, QString)):
        zipName = os.path.abspath(forceString(zipName))
        dirName = zipName if os.path.isdir(zipName) else dirName
        zipName = os.path.basename(zipName)
    else:
        zipName = 'archive.zip'
    
    
    
    zipName = forceString(QtGui.QFileDialog.getSaveFileName(parent = widget, 
                                                            caption = u'Создать архив ...',
                                                            directory = dirName,
                                                            filter = u'Zip files (*%s)' % zipExt))
    
    if not zipName:
        return
    
    if os.path.splitext(zipName)[1] != zipExt:
        os.path.join(zipName, zipExt) 
    
    missingFiles = []
    errorMessage = u''
    zipFile = None
    try:
        zipFile = ZipFile(zipName, 'w')
        for fileName in fileList:
            if os.path.isfile(fileName):
                zipFile.write(fileName, os.path.basename(fileName))
            else:
                missingFiles.append(fileName)
    except zipfile.BadZipfile, e:
        errorMessage = u'Некорректный архив (%s)' % e
    except zipfile.LargeZipFile, e:
        errorMessage = u'Слишком большой размер архива (%s)' % e
    except Exception, e:
        errorMessage = u'Неизвестная ошибка (%s)' % e
    finally:
        if zipFile:
            zipFile.close()
    
    if errorMessage:
        QMessageBox.critical(widget, u'Ошибка', errorMessage, buttons = QMessageBox.Ok)
        return None
    
    if missingFiles:
        missingFiles.insert(0, 'Не удалось найти файлы из списка ниже для помещения в архив')
        QMessageBox.information(widget, 
                                u'Не найдены файлы...',
                                u'\n'.join(missingFiles),
                                buttons = QMessageBox.Ok)
    if isRemoveSource:
        for fileName in fileList:
            os.remove(fileName)
    return zipName
                                      

def getFilesZipArchive(zipFileName):
    if not is_zipfile(zipFileName):
        return None, None
    archive = ZipFile(zipFileName, "r")
    return archive, archive.namelist()

def getDBFFileFromZipArchive(archive, nameDBF):
    outFile = QtCore.QTemporaryFile()
    if not outFile.open(QtCore.QFile.WriteOnly):
        return None
    outFile.write(archive.read(nameDBF))
    outFile.close()
    return Dbf(forceString(QtCore.QFileInfo(outFile).filePath()), encoding='cp866')

def getId(table, fields, fields2=None):
    if not fields2:
        fields2 = []
    db = QtGui.qApp.db
#    cond=[table[name].eq(toVariant(val)) for (name, val) in fields]
    cond=[]
    for (name, val) in fields:
        if val==None:
            cond.append(table[name].isNull())
        else:
            cond.append(table[name].eq(toVariant(val)))
    record=db.getRecordEx(table, '*', where=cond)
    if record:
        updateRecord = False
        for (name, val) in fields2:
            recVal=record.value(name)
            if (recVal.isNull() or forceString(recVal)=='') and isNotNull(val):
                record.setValue(name, toVariant(val))
                updateRecord = True
        if updateRecord:
            db.updateRecord(table, record)
        return forceInt(record.value('id'))
    else:
        record = table.newRecord()
        for (name, val) in fields+fields2:
            record.setValue(name, toVariant(val))
        return db.insertRecord(table, record)


def findAndUpdateOrCreateRecord(table, filterFields, updateFields=None, id=None):
    # вариант getId, обновляющий запись не только если поля пусты
    if not updateFields:
        updateFields = []
    db = QtGui.qApp.db
    cond=[ table[name].isNull() if val is None else table[name].eq(toVariant(val))
           for (name, val) in filterFields
         ]
    if id:
        cond.append(table['id'].eq(id))
    record=db.getRecordEx(table, '*', where=cond)
    if record:
        updateRecord = False
        for (name, val) in updateFields:
            recVal=record.value(name)
            newVal=toVariant(val)
            if not variantEq(recVal, newVal):
                record.setValue(name, newVal)
                updateRecord = True
        if updateRecord:
            db.updateRecord(table, record)
        return forceInt(record.value('id'))
    else:
        record = table.newRecord()
        for (name, val) in filterFields:
            record.setValue(name, toVariant(val))
        for (name, val) in updateFields:
            record.setValue(name, toVariant(val))
        return db.insertRecord(table, record)


def checkPatientData(self, lastNameField, firstNameField, patrNameField, sexField, birthDateField):
    bad=False
    lastName=nameCase(self.row[lastNameField])
    firstName=nameCase(self.row[firstNameField])
    patrName=nameCase(self.row[patrNameField])
    if not (lastName and firstName and patrName):
        bad=True
        self.err2log(u'нет полного ФИО')
    fio=lastName+firstName+patrName
    if not check_rus_lat(fio):
        bad=True
        self.err2log(u'недопустимое ФИО')
    sex=self.row[sexField]
    if not sex:
        bad=True
        self.err2log(u'не указан пол')
    else:
        if sex in [u'м', u'М']: sex = 1
        if sex in [u'ж', u'Ж']: sex = 2
    birthDate=self.row[birthDateField]
    if not birthDate:
        bad=True
        self.err2log(u'не указан день рождения')
    if bad:
        return None
    else:
        clientFields=[
            ('lastName', lastName), ('firstName', firstName), ('patrName', patrName),
            ('sex', sex), ('birthDate', birthDate)]
        return checkData(clientFields, self.tableClient)

def checkData(fields, table):
    db = QtGui.qApp.db
    cond=[]
    for (name, val) in fields:
        if val==None:
            cond.append(table[name].isNull())
        else:
            cond.append(table[name].eq(toVariant(val)))
    record=db.getRecordEx(table, '*', where=cond)
    if record:
        return True
    return False


def isNull(s):
    return s in (None, '', 'Null', 'null', 'NULL')


def isNotNull(s):
    return s not in (None, '', 'Null', 'null', 'NULL')


def dbfCheckNames(d, names):
    for name in names:
        if name not in d.header.fields:
            return False
    return True


def getOKVED(okved):
    OKVED=''
    for c in okved:
        if c==' ': pass
        elif c=='-': break
        else: OKVED=OKVED+c
    if len(OKVED) and OKVED[0:1].isdigit():
        OKVED=QtGui.qApp.db.translate('rbOKVED', 'OKVED', OKVED, 'code')
    return OKVED

# это, товарищи, говнище...
currentYear=QDate.currentDate().year()
currentYearBeg=datetime.date(currentYear, 1, 1)
currentYearEnd=datetime.date(currentYear, 12, 31)

def tbl(tn):
    t=QtGui.qApp.db.table(tn)
    assert t.fields
    return t

rus_re=re.compile(u'[А-Яа-яЁё]')
lat_re=re.compile(r'[A-Za-z]')

def check_rus_lat(s):
    rus=rus_re.search(s)!=None
    lat=lat_re.search(s)!=None
    return rus!=lat

def check_rus(s):
    return rus_re.search(s)

def get_specs(POL):
    if POL in (1, u'м', u'М'):
        POL_spec1, POL_spec2 = [], [('U', '84', 3)]
    else:
        POL_spec1, POL_spec2 = [('A', '02', 3)], []
    return [('T', '78', 5)]+POL_spec1+[('N', '40', 3), ('H', '89', 3)]+POL_spec2+[('O', '49', 3), ('E', '91', 3)]


def getWorkHurt(clientWorkId):
    # mdldml: После i2025 эта функция теряет остатки смысла. Допустим, клиент работал на работе, для
    # которой у него указаны пять вредностей и шесть факторов вредности. Что мы должны здесь вернуть?
    # Пока будем делать join всех подходящих пар и возвращать первый набор. Мда.
    hurt   = ''
    stage  = 0
    factors = ''
    if clientWorkId:
        db = QtGui.qApp.db
        stmt = u'''
SELECT
    rbHurtType.code AS hurt,
    ClientWork_Hurt.stage AS stage,
    rbHurtFactorType.code AS factors
FROM
    ClientWork_Hurt
    LEFT JOIN rbHurtType ON rbHurtType.id = ClientWork_Hurt.hurtType_id
    LEFT JOIN ClientWork_Hurt_Factor ON ClientWork_Hurt_Factor.master_id = ClientWork_Hurt.master_id
    LEFT JOIN rbHurtFactorType ON rbHurtFactorType.id = ClientWork_Hurt_Factor.factorType_id
WHERE
    ClientWork_Hurt.master_id = %d AND
    ClientWork_Hurt.stage = (
        SELECT MAX(CWH.stage) FROM ClientWork_Hurt AS CWH WHERE CWH.master_id=%d)
            ''' % (clientWorkId, clientWorkId)
        query = db.query(stmt)
        if query.next():
            record = query.record()
            hurt    = forceString(record.value(0))
            stage   = forceInt(record.value(1))
            factors = forceString(record.value(2))
    return hurt, stage, factors

def get_Account_Item(eventId):
    if not eventId: return None
    stmt='''
select
Account_Item.date, rbPayRefuseType.code, rbPayRefuseType.name
from
Account_Item
left join rbPayRefuseType on rbPayRefuseType.id=Account_Item.refuseType_id
where
Account_Item.event_id='''+str(eventId)+''' and Account_Item.date=(
    select max(a.date) from Account_Item as a where a.master_id=Account_Item.master_id)
        '''
    query=QtGui.qApp.db.query(stmt)
    if query.next():
        return query.record()
    return None

def getClientAddressEx(clientId):
    freeInput = ''
    KLADRCode = ''
    KLADRStreetCode = ''
    house = ''
    corpus = ''
    flat = ''

    db = QtGui.qApp.db
    regAddressRecord=getClientAddress(clientId, 0)
    if regAddressRecord:
        addressId=forceRef(regAddressRecord.value('address_id'))
        freeInput=forceString(regAddressRecord.value('freeInput'))
        if addressId:
            recAddress = db.getRecord('Address', 'house_id, flat', addressId)
            if recAddress:
                flat = forceString(recAddress.value('flat'))
                houseId = forceRef(recAddress.value('house_id'))
                if houseId:
                    recHouse = db.getRecord(
                        'AddressHouse', 'KLADRCode, KLADRStreetCode, number, corpus',  houseId)
                    KLADRCode=forceString(recHouse.value('KLADRCode'))
                    KLADRStreetCode=forceString(recHouse.value('KLADRStreetCode'))
                    house = forceString(recHouse.value('number'))
                    corpus = forceString(recHouse.value('corpus'))
    return freeInput, KLADRCode, KLADRStreetCode, house, corpus, flat



def getDiags(event_id, speciality):
    stmt='''
select
    Person.lastName, Person.firstName, Person.patrName, Person.code,
    Diagnostic.sanatorium, Diagnostic.endDate, Diagnostic.diagnosisType_id,
    Diagnosis.MKB, Diagnostic.character_id, Diagnostic.stage_id, Diagnostic.healthGroup_id, Diagnostic.medicalGroup_id,
    rbDispanser.code AS dispanser_code
from
    Diagnostic
    join Person on Diagnostic.person_id=Person.id
    join Diagnosis on Diagnosis.id=Diagnostic.diagnosis_id
    join rbSpeciality on rbSpeciality.id=Person.speciality_id
    left join rbDispanser on rbDispanser.id = Diagnostic.dispanser_id
where
    Diagnostic.event_id='''+str(event_id)+''' and rbSpeciality.code=\''''+str(speciality)+'''\'
    AND Diagnostic.deleted = 0 AND Diagnosis.deleted = 0
order
    by Diagnostic.diagnosisType_id
        '''
    query=QtGui.qApp.db.query(stmt)
    Diags=[]
    while query.next():
        Diags.append(query.record())
    return Diags

def getOtherDiags(event_id, specs):
    sp=' and rbSpeciality.code not in ('+', '.join([s[1] for s in specs])+')'
    stmt='''
select
    Person.lastName, Person.firstName, Person.patrName, Person.code,
    Diagnostic.sanatorium, Diagnostic.endDate, Diagnostic.diagnosisType_id,
    Diagnosis.MKB, Diagnostic.character_id, Diagnostic.stage_id, Diagnostic.healthGroup_id, Diagnostic.medicalGroup_id,
    rbSpeciality.code as spec_code, rbSpeciality.OKSOCode, rbSpeciality.name as spec_name
from
    Diagnostic
    join Person on Diagnostic.person_id=Person.id
    join Diagnosis on Diagnosis.id=Diagnostic.diagnosis_id
    join rbSpeciality on rbSpeciality.id=Person.speciality_id
where
    Diagnostic.event_id='''+str(event_id)+sp+'''
    AND Diagnostic.deleted = 0 AND Diagnosis.deleted = 0
order
    by Diagnostic.diagnosisType_id
        '''
    query=QtGui.qApp.db.query(stmt)
    Diags=[]
    while query.next():
        Diags.append(query.record())
    return Diags

def get_dom_korp_kv(freeInput):
    DOM, KOR, KV = None, None, None
    dom_pos=freeInput.rfind(u' д.')
    if dom_pos==-1:
        dom_pos=freeInput.rfind(u',д.')
    if dom_pos==-1:
        dom_pos=freeInput.rfind(u' Д ')
    if dom_pos==-1:
        dom_pos=freeInput.rfind(u' Д.')
    if dom_pos==-1:
        dom_pos=freeInput.rfind(u',Д.')
    if dom_pos>=0:
        f=freeInput[dom_pos+3:]
        d2=f.find(',')
        if d2>=0:
            f=f[:d2]
        DOM=f.strip()
    k_pos=freeInput.find(u' к.')
    if k_pos==-1:
        k_pos=freeInput.find(u',к.')
    if k_pos==-1:
        k_pos=freeInput.find(u',КОРП.')
    if k_pos==-1:
        k_pos=freeInput.find(u',КОР.')
    if k_pos==-1:
        k_pos=freeInput.find(u',К.')
    if k_pos>=0:
        f=freeInput[k_pos+3:]
        k2=f.find(',')
        if k2>=0:
            f=f[:k2]
        KOR=f.strip()
    kv_pos=freeInput.find(u' кв.')
    if kv_pos==-1:
        kv_pos=freeInput.find(u',кв.')
    if kv_pos==-1:
        kv_pos=freeInput.find(u' КВ ')
    if kv_pos==-1:
        kv_pos=freeInput.find(u' КВ.')
    if kv_pos==-1:
        kv_pos=freeInput.find(u',КВ.')
    if kv_pos>=0:
        f=freeInput[kv_pos+4:]
        kv2=f.find(',')
        if kv2>=0:
            f=f[:kv2]
        KV=f.strip()
    return DOM, KOR, KV

def get_dop(dop0):
    dop=[]
    for (dop_name, dop_code, dop_group_id) in dop0:
        r=QtGui.qApp.db.getRecordEx(
            'ActionType', 'id', 'code=\'%s\' and group_id=%d' % (dop_code, dop_group_id))
        if r:
            dop_id=forceInt(r.value(0))
            if dop_id:
                dop.append((dop_name, dop_id))
    return dop


def setEIS_db():
    EIS_db = QtGui.qApp.EIS_db
    if not EIS_db:
        props = QtGui.qApp.preferences.appPrefs
        EIS_dbDriverName = forceStringEx(props.get('EIS_driverName', QVariant()))
        EIS_dbServerName = forceStringEx(props.get('EIS_serverName', QVariant()))
        EIS_dbServerPort = forceInt(props.get('EIS_serverPort', QVariant()))
        EIS_dbDatabaseName = forceStringEx(props.get('EIS_databaseName', QVariant()))
        EIS_dbUserName = forceStringEx(props.get('EIS_userName', QVariant()))
        EIS_dbPassword = forceStringEx(props.get('EIS_password', QVariant()))
        EIS_dbCodepage = forceStringEx(props.get('EIS_codepage', QVariant()))
        EIS_db = database.connectDataBase(EIS_dbDriverName,
                                          EIS_dbServerName,
                                          EIS_dbServerPort,
                                          EIS_dbDatabaseName,
                                          EIS_dbUserName,
                                          EIS_dbPassword,
                                          'EIS',
                                          LC_CTYPE=EIS_dbCodepage)
        QtGui.qApp.EIS_db = EIS_db

def EIS_close():
    if QtGui.qApp.EIS_db:
        QtGui.qApp.EIS_db.close()
        QtGui.qApp.EIS_db=None
    QtGui.QMessageBox.information(
        None, u'нет связи', u'не удалось установить соединение с базой ЕИС',
        QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)


def binaryToInt(str):
    str = str.encode('cp866')
    return int('0' + binascii.hexlify(str), 16)


def insertRecordFromDbf(db, tablename, record, fields = None):
    u"""
    Конвертирует запись DBF в запись в любой БД
    db - БД
    tablename - имя таблицы БД, куда вставлять запись
    record - запись DBF
    fields - номера полей, которые надо конвертировать (None - все поля). Если номер равен -1, нужно вставить значение по умолчанию.
    """
    db_record = db.record(tablename)
    values = record.asList()
    strvalues = []
    if fields is None:
        fields = xrange(len(values))
    for i in xrange(len(fields)):
        field = db_record.field(i)
        if fields[i] == -1:
            field.setValue(field.defaultValue())
        else:
            if values[fields[i]]:
                field.setValue(QtCore.QVariant(values[fields[i]]))
            else:
                field.clear()
        # fields.append(unicode('`'+record.fieldName(i)+'`'))
        strvalues = strvalues + [unicode(db.db.driver().formatValue(field, False)), ]
    stmt = ('INSERT INTO ' +  tablename +
#          '(' + (', '.join(fields)) + ') '+
           ' VALUES (' + (', '.join(strvalues)) + ')')
    #print stmt
    querier =  QtSql.QSqlQuery(db.db)
    if not querier.exec_(stmt):
        return querier.lastError()

def insertTableDataFromDbf(db, tablename, filename, encoding, binaries=None, fields=None):
    u"""
    Выкачивает данные из DBF и добавляет в таблицу БД
    tablename - имя таблицы БД
    filename - имя файла DBF
    encoding - кодировка, в которой хранится DBF
    binaries - список номеров полей, которые нужно перекодировать из бинарных в целые
    fields - номера полей, которые надо конвертировать (None - все поля). Если номер равен -1, нужно вставить значение по умолчанию.
    """
    if not binaries:
        binaries = []
    dbf = Dbf(filename, readOnly=True, encoding=encoding, enableFieldNameDups=True)
#    for i in binaries:
#        dbf.fieldDefs[i].encoding = 'latin-1'
    for record in dbf:
        for i in binaries:
            record[i] = binaryToInt(record[i])
        insertRecordFromDbf(db, tablename, record, fields)
        QtGui.qApp.processEvents()
    dbf.close()


def logQueryResult(log, query):
    u"""Записывает результат выполнения запроса query в лог по строкам"""
    while query.next():
        rec = query.record()
        str = query.value(0).toString()
        for i in xrange(1,  rec.count()):
            str = str + '\t' + query.value(i).toString()
        log.append(str)

def setSqlVariable(db, name, value):
    u"""Устанавливает значение переменной в запросе на SQL"""
    if value:
        if str(type(value)) == "<type 'string'>" or str(type(value)) == "<type 'unicode'>":
            strvalue = '\'' + value + '\''
        else:
            strvalue = str(value)
    else:
        strvalue = 'NULL'
    querier =  QtSql.QSqlQuery(db.db)
    if not querier.exec_('SELECT @' + name + ' := ' + strvalue):
        return querier.lastError()
    return None


def execQuery(db, s, log):
    if QtCore.QRegExp('[ \n\r\t]*').exactMatch(s): # пустой запрос
        return None
    #print "QUERY: " + s
    querier =  QtSql.QSqlQuery(db.db)
    if not querier.exec_(s):
        return querier.lastError()
    if log:
        logQueryResult(log, querier) # записываем результат выполнения
    return None

def runScript(db, log, instream, dict=None):
    u"""Выполняет последовательность запросов к базе данных db, считанную из входного потока instream.
    instream - это произвольный контейнер со строками
    Записывает результаты в окно log
    dict - набор пар (имя, значение) для установки переменных в SQL
    """
    if not dict:
        dict = {}
    # устанавливаем значения переменных:
    for (key,  value) in dict.items():
        setSqlVariable(db, key,  value)

    # анализируем запросы:
    fullstr = '' # текущий запрос
    delimiter = ';' # разделитель запросов
    for idx, str in enumerate(instream):
        delimexp = QtCore.QRegExp('delimiter', QtCore.Qt.CaseInsensitive)
        if delimexp.indexIn(str.strip()) == 0: # в этой строке меняется разделитель
            delimiter = str.strip()[delimexp.matchedLength():].strip()
        else:
            pos = QtCore.QRegExp('--|\'|\"|%s'%QtCore.QRegExp.escape(delimiter)).indexIn(str, 0) # позиция, с которой начинается комментарий или открывается строка
            while pos != -1:
                if str[pos] == '\'':
                    pos = str.find('\'', pos+1)
                    pos += (1 if pos != -1 else 0)
                elif str[pos] == '\"':
                    pos = str.find('\"', pos+1)
                    pos += (1 if pos != -1 else 0)
                elif str[pos:pos+len(delimiter)] == delimiter: # здесь запрос закончился
                    fullstr = fullstr + ' ' + str[:pos]
                    result = execQuery(db, fullstr, log) # выполняем его
                    if result:
                        getLogger().error(u'(line: %s) %s\nStatement: "%s"\n%s' % (idx, result.text(), fullstr.strip(), u'=' * 80))
                        return result
                    fullstr = '' # и ждем нового
                    str = str[pos+len(delimiter):]
                    pos = 0
                else: # найден комментарий
                    str = str[:pos]
                    break
                pos = QtCore.QRegExp('--|\'|\"|%s'%QtCore.QRegExp.escape(delimiter)).indexIn(str, pos)
            fullstr = fullstr + ' ' + str
    result = execQuery(db, fullstr, log) # выполняем всё, что осталось в конце
    if result:
        getLogger().error(u'(line: %s) %s\nStatement: "%s"\n%s' % (idx, result.text(), fullstr.strip(), u'=' * 80))
    return result

def checkEmail(email):
    reg = '^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$'
    if len(email) > 7:
        if re.match(reg, email):
            return True
    return False

def rarArchiver():
    try:
        me = forceString(QtGui.qApp.preferences.appPrefs['extArchiver'])
        if 'rar' not in me.lower():
            me= u'rar'
        return me
    except KeyError:
        raise CRarException(u"Архиватор по умолчанию не выбран")


# Этот метод кидает CRarException. Его нужно при вызове обрабатывать.
# Примерно так:
# try:
#   compressFileInRar(fileName, fileName+'.rar')
#   self.progressBar.setText(u'Сжато в "%s"' % (fileName+'.rar'))
# except CRarException as e:
#   self.progressBar.setText(unicode(e))
#   QtGui.QMessageBox.critical(self, e.getWindowTitle(), unicode(e), QtGui.QMessageBox.Close)
def compressFileInRar(filePath='', rarFilePath=''):
        if not filePath:
            raise CRarException(u'При сжатии полуен пустой адрес сохранения файла')
        if not rarFilePath:
            rarFilePath = filePath+'.rar'

        filePath = unicode(filePath)
        rarFilePath = unicode(rarFilePath)

        arch = rarArchiver()
        prg = QtGui.qApp.execProgram(u'"%s" mf -ep -m5 -o+ -y -- "%s" "%s"'% (arch,  rarFilePath, filePath))
        if not prg[0]:
            raise CRarException(u'не удалось запустить rar')
        if prg[2]:
            raise CRarException(u'ошибка при выполнении rar')

        return True


def compressFileInArj(filePath, arjFilePath=''):
    if filePath:
        if not arjFilePath:
            arjFilePath = filePath+'.arj'

        filePath = unicode(filePath)
        arjFilePath = unicode(arjFilePath)

        prg=QtGui.qApp.execProgram(u'arj m -m4 -y -e "%s" "%s"'% (arjFilePath, filePath))
        if not prg[0]:
            raise CException(u'не удалось запустить arj')
        if prg[2]:
            raise CException(u'ошибка при выполнении arj')
        return True

    return False


def compressFileInZip(filePath, zipFilePath=''):
    if not zipFilePath:
        zipFilePath = filePath+'.zip'

    filePath = unicode(filePath)
    zipFilePath = unicode(zipFilePath)

    try:
        zf = ZipFile(zipFilePath, 'w', allowZip64=True)
        zf.write(filePath, os.path.basename(filePath), ZIP_DEFLATED)
        zf.close()
    except:
        return False

    return True


def compressFileIn7Zip(filePath, zipFilePath=''):
    if filePath:
        if not zipFilePath:
            zipFilePath = filePath+'.7z'

        filePath = unicode(filePath)
        zipFilePath = unicode(zipFilePath)

        prg=QtGui.qApp.execProgram(u'7za a -y "%s" "%s"'% (zipFilePath, filePath))
        if not prg[0]:
            raise CException(u'не удалось запустить 7za')
        if prg[2]:
            raise CException(u'ошибка при выполнении 7za')
        return True

    return False


def getClientRepresentativeInfoFromRecord(record):
    def getDocument(_str):
        tailIndex = _str.find(' (')
        if tailIndex > 0:
            _str = _str[:tailIndex] # В скобочках шла занятость в старом формате. Сразу убираем ее.
        _strList = _str.split(':')
        result = {}
        if len(_strList) == 2:
            docType, serAndNumber = _strList
            docTypeCache = CRBModelDataCache.getData('rbDocumentType', False, 'group_id=1')
            cacheIndex = docTypeCache.getIndexByName(docType)
            result['docTypeRegCode'] = forceInt(docTypeCache.getRegionalCode(cacheIndex)) if cacheIndex > 0 else 0
            result['docTypeCode'] = docTypeCache.getCode(cacheIndex) if cacheIndex > 0 else ''
        else:
            serAndNumber = _str
        numberParts = serAndNumber.split()
        if len(numberParts) > 2:
            result['serial'] = numberParts[0] + ' ' +  numberParts[1]
            result['number'] = ''.join(numberParts[2:])
        elif len(numberParts) == 2:
            result['serial'], result['number'] = numberParts
        elif len(numberParts) == 1:
            result['number'] = numberParts[0]

        return result

    def getBirthDate(_str):
        return QDate.fromString(_str, 'dd.MM.yyyy')

    def getSex(s):
        _str = s.lower()
        if _str.startswith(u'пол: '):
            sexStr = _str[-1]
            return 1 if sexStr == u'м' else 2 if sexStr == u'ж' else 0
        return None

    result = {}
    result['relationTypeCode'] = forceString(record.value('relationTypeCode'))

    if not forceInt(record.value('relativeId')):
        freeInputList = forceStringEx(record.value('relativeFreeInput')).split(', ')
        if freeInputList:
            fioList = freeInputList.pop(0).split()
            if len(fioList) > 2:
                result['lastName'] = fioList[0]
                result['firstName'] = ' '.join(fioList[1:-1])
                result['patrName'] = fioList[-1]
            elif len(fioList) == 2:
                result['lastName'] = fioList[0]
                result['firstName'] = fioList[1]
            elif len(fioList) == 1:
                result['lastName'] = fioList[0]
            if freeInputList:
                rest = freeInputList.pop(0)
                sex = getSex(rest)
                if not sex is None:
                    result['sex'] = sex
                    if not freeInputList: return result
                    rest = freeInputList.pop(0)
                birthDate = getBirthDate(rest)
                if birthDate:
                    result['birthDate'] = birthDate
                    if not freeInputList: return result
                    rest = freeInputList.pop(0)
                documentData = getDocument(rest)
                if documentData:
                    result['documentTypeCode'] = documentData.get('docTypeCode', '')
                    result['documentTypeRegionalCode'] = documentData.get('docTypeRegCode', 0)
                    result['serial'] = documentData.get('serial', '')
                    result['number'] = documentData.get('number', '')
    else:
        result['firstName'] = forceString(record.value('relativeFirstName'))
        result['lastName']  = forceString(record.value('relativeLastName'))
        result['patrName']  = forceString(record.value('relativePatrName'))
        result['serial'] = forceString(record.value('relativeDocumentSerial'))
        result['number'] = forceString(record.value('relativeDocumentNumber'))
        result['sex'] = forceInt(record.value('relativeSex'))
        result['birthDate'] = forceDate(record.value('relativeBirthDate'))
        result['documentTypeCode'] = forceString(record.value('relativeDocTypeCode'))
        result['documentTypeRegionalCode'] = forceInt(record.value('relativeDocTypeRegCode'))

    result['policyNumber'] = forceString(record.value('relativePolicyNumber'))
    result['policySerial'] = forceString(record.value('relativePolicySerial'))
    result['SNILS'] = forceString(record.value('relativeSNILS'))
    return result

def getClientRepresentativeInfo(clientId):
    db = QtGui.qApp.db
    stmt = """
SELECT
    Client.id as relativeId,
    Client.firstName as relativeFirstName,
    Client.lastName as relativeLastName,
    Client.patrName as relativePatrName,
    Client.sex as relativeSex,
    Client.birthDate as relativeBirthDate,
    ClientDocument.number as relativeDocumentNumber,
    ClientDocument.serial as relativeDocumentSerial,
    rbDocumentType.code AS relativeDocTypeCode,
    rbDocumentType.regionalCode AS relativeDocTypeRegCode,
    rbRelationType.regionalCode AS relationTypeCode,
    T.freeInput AS relativeFreeInput,
    ClientPolicy.number as relativePolicyNumber,
    ClientPolicy.serial as relativePolicySerial,
    Client.SNILS AS relativeSNILS
FROM
    (SELECT rbRelationType.code, ClientRelation.relative_id, ClientRelation.relativeType_id, ClientRelation.freeInput AS freeInput
    FROM ClientRelation
    LEFT JOIN rbRelationType ON ClientRelation.relativeType_id = rbRelationType.id
    WHERE ClientRelation.deleted=0
      AND ClientRelation.client_id = %d
      AND rbRelationType.isBackwardRepresentative
    UNION
    SELECT rbRelationType.code, ClientRelation.client_id AS relative_id, ClientRelation.relativeType_id, ClientRelation.freeInput AS freeInput
    FROM ClientRelation
    LEFT JOIN rbRelationType ON ClientRelation.relativeType_id=rbRelationType.id
    WHERE ClientRelation.deleted=0
      AND ClientRelation.relative_id = %d
      AND rbRelationType.isDirectRepresentative
    ) AS T
    LEFT JOIN Client ON T.relative_id = Client.id
    LEFT JOIN ClientDocument ON ClientDocument.client_id = Client.id AND
        ClientDocument.id = (SELECT MAX(CD.id)
                        FROM   ClientDocument AS CD
                        LEFT JOIN rbDocumentType AS rbDT ON rbDT.id = CD.documentType_id
                        LEFT JOIN rbDocumentTypeGroup AS rbDTG ON rbDTG.id = rbDT.group_id
                        WHERE  rbDTG.code = '1' AND CD.client_id = Client.id AND CD.deleted=0)
    LEFT JOIN rbDocumentType ON rbDocumentType.id = ClientDocument.documentType_id
    LEFT JOIN rbRelationType ON T.relativeType_id=rbRelationType.id
    LEFT JOIN ClientPolicy ON Client.id = ClientPolicy.client_id AND ClientPolicy.deleted = 0
WHERE
    Client.deleted = 0 OR Client.id IS NULL
ORDER BY T.code
LIMIT 1
    """ % (clientId, clientId)
    query = db.query(stmt)

    if query.first():
        return getClientRepresentativeInfoFromRecord(query.record())
    return {}

def prepareRefBooksCacheByCode(db = None):
    """
        Кэшируем все небольшие справочники, чтобы не плодить массу одинаковых запросов.
        Исходим из допущения, что коды уникальны.
    """
    def extractBasicFields(record):
        return forceRef(record.value('id')), forceString(record.value('code')), forceString(record.value('name'))
    if not db:
        db = QtGui.qApp.db
    cache = smartDict()

    diseaseCharacters = db.getRecordList('rbDiseaseCharacter')
    cache.diseaseCharacter = {}
    for dc in diseaseCharacters:
        id, code, name = extractBasicFields(dc)
        replace = forceString(dc.value('replaceInDiagnosis'))
        cache.diseaseCharacter[code] = {'id': id, 'name': name, 'replaceInDiagnosis': replace}

    diseasePhases = db.getRecordList('rbDiseasePhases')
    cache.diseasePhases = {}
    for dh in diseasePhases:
        id, code, name = extractBasicFields(dh)
        characterRelation = forceString(dh.value('characterRelation'))
        cache.diseasePhases[code] = {'id': id, 'name': name, 'characterRelation': characterRelation}

    diseaseStages = db.getRecordList('rbDiseaseStage')
    cache.diseaseStage = {}
    for ds in diseaseStages:
        id, code, name = extractBasicFields(ds)
        characterRelation = forceString(ds.value('characterRelation'))
        cache.diseaseStage[code] = {'id': id, 'name': name, 'characterRelation': characterRelation}

    diagnosisType = db.getRecordList('rbDiagnosisType')
    cache.diagnosisType = {}
    for dt in diagnosisType:
        id, code, name = extractBasicFields(dt)
        replace = forceString(dt.value('replaceInDiagnosis'))
        cache.diagnosisType[code] = {'id': id, 'name': name, 'replace': replace}

    diagnosticResult = db.getRecordList('rbDiagnosticResult')
    cache.diagnosticResult = {}
    for dr in diagnosticResult:
        id, code, name = extractBasicFields(dr)
        eventPurpose = forceRef(dr.value('eventPurpose_id'))
        continued = forceInt(dr.value('continued'))
        regionalCode = forceString(dr.value('regionalCode'))
        federalCode = forceString(dr.value('federalCode'))
        resultId = forceRef(dr.value('result_id'))
        cache.diagnosticResult[code] = {'id': id, 'name': name, 'eventPurpose_id': eventPurpose,
                                      'regionalCode': regionalCode, 'federalCode': federalCode, 'result_id': resultId}

    eventTypePurpose = db.getRecordList('rbEventTypePurpose')
    cache.eventTypePurpose = {}
    for etp in eventTypePurpose:
        id, code, name = extractBasicFields(etp)
        regionalCode = forceString(etp.value('regionalCode'))
        federalCode = forceString(etp.value('federalCode'))
        cache.eventTypePurpose[code] = {'id': id, 'name': name, 'regionalCode': regionalCode, 'federalCode': federalCode}

    # eventGoal = db.getRecordList('rbEventGoal')
    # cache.eventGoal = {}
    # for eg in eventGoal:
    #     id, code, name = extractBasicFields(eg)
    #     regionalCode = forceString(eg.value('regionalCode'))
    #     federalCode = forceString(eg.value('federalCode'))
    #     eventTypePurpose = forceRef(eg.value('eventTypePurpose_id'))
    #     cache.eventGoal[code] = {'id': id, 'name': name, 'regionalCode': regionalCode,
    #                            'federalCode': federalCode, 'eventTypePurpose_id': eventTypePurpose}

    medicalAidKind = db.getRecordList('rbMedicalAidKind')
    cache.medicalAidKind = {}
    for mak in medicalAidKind:
        id, code, name = extractBasicFields(mak)
        regionalCode = forceString(mak.value('regionalCode'))
        federalCode = forceString(mak.value('federalCode'))
        cache.medicalAidKind[code] = {'id': id, 'name': name, 'regionalCode': regionalCode, 'federalCode': federalCode}

    result = db.getRecordList('rbResult')
    cache.result = {}
    for r in result:
        id, code, name = extractBasicFields(r)
        regionalCode = forceString(r.value('regionalCode'))
        federalCode = forceString(r.value('federalCode'))
        continued = forceString(r.value('continued'))
        notAccount = forceString(r.value('notAccount'))
        eventPurpose = forceRef(r.value('eventPurpose_id'))
        cache.result[(code, eventPurpose)] = {'id': id, 'name': name, 'regionalCode': regionalCode, 'federalCode': federalCode,
                            'continued': continued, 'notAccount': notAccount}

    scene = db.getRecordList('rbScene')
    cache.scene = {}
    for s in scene:
        id, code, name = extractBasicFields(s)
        serviceModifier = forceString(s.value('serviceModifier'))
        cache.scene[code] = {'id': id, 'name': name, 'serviceModifier': serviceModifier}

    visitType = db.getRecordList('rbVisitType')
    cache.visitType = {}
    for vt in visitType:
        id, code, name = extractBasicFields(vt)
        serviceModifier = forceString(vt.value('serviceModifier'))
        cache.visitType[code] = {'id': id, 'name': name, 'serviceModifier': serviceModifier}

    finance = db.getRecordList('rbFinance')
    cache.finance = {}
    for f in finance:
        id, code, name = extractBasicFields(f)
        cache.finance[code] = {'id': id, 'name': name}

    unit = db.getRecordList('rbUnit')
    cache.unit = {}
    for u in unit:
        id, code, name = extractBasicFields(u)
        cache.unit[code] = {'id': id, 'name': name}

    documentType = db.getRecordList('rbDocumentType')
    cache.documentType = {}
    # TODO: если нам все-таки нужно экспортировать этот справочник, то взять остальные поля.
    for dt in documentType:
        id, code, name = extractBasicFields(dt)
        regionalCode = forceString(dt.value('regionalCode'))
        federalCode = forceString(dt.value('federalCode'))
        cache.documentType[code] = {'id': id, 'name': name, 'regionalCode': regionalCode, 'federalCode': federalCode}

    policyKind = db.getRecordList('rbPolicyKind')
    cache.policyKind = {}
    for pk in policyKind:
        id, code, name = extractBasicFields(pk)
        regionalCode = forceString(pk.value('regionalCode'))
        federalCode = forceString(pk.value('federalCode'))
        cache.policyKind[code] = {'id': id, 'name': name, 'regionalCode': regionalCode, 'federalCode': federalCode}

    policyType = db.getRecordList('rbPolicyType')
    cache.policyType = {}
    for pt in policyType:
        id, code, name = extractBasicFields(pt)
        cache.policyType[code] = {'id': id, 'name': name}

    return cache

def prepareRefBooksCacheById(db = None):
    """
        Кэшируем все небольшие справочники, чтобы не плодить массу одинаковых запросов.
        Исходим из допущения, что коды уникальны.
    """
    def extractBasicFields(record):
        return forceRef(record.value('id')), forceString(record.value('code')), forceString(record.value('name'))
    if not db:
        db = QtGui.qApp.db
    cache = smartDict()

    diseaseCharacters = db.getRecordList('rbDiseaseCharacter')
    cache.diseaseCharacter = {}
    for dc in diseaseCharacters:
        id, code, name = extractBasicFields(dc)
        replace = forceString(dc.value('replaceInDiagnosis'))
        cache.diseaseCharacter[id] = {'code': code, 'name': name, 'replaceInDiagnosis': replace}

    diseasePhases = db.getRecordList('rbDiseasePhases')
    cache.diseasePhases = {}
    for dh in diseasePhases:
        id, code, name = extractBasicFields(dh)
        characterRelation = forceString(dh.value('characterRelation'))
        cache.diseasePhases[id] = {'code': code, 'name': name, 'characterRelation': characterRelation}

    diseaseStages = db.getRecordList('rbDiseaseStage')
    cache.diseaseStage = {}
    for ds in diseaseStages:
        id, code, name = extractBasicFields(ds)
        characterRelation = forceString(ds.value('characterRelation'))
        cache.diseaseStage[id] = {'code': code, 'name': name, 'characterRelation': characterRelation}

    diagnosisType = db.getRecordList('rbDiagnosisType')
    cache.diagnosisType = {}
    for dt in diagnosisType:
        id, code, name = extractBasicFields(dt)
        replace = forceString(dt.value('replaceInDiagnosis'))
        cache.diagnosisType[id] = {'code': code, 'name': name, 'replace': replace}

    diagnosticResult = db.getRecordList('rbDiagnosticResult')
    cache.diagnosticResult = {}
    for dr in diagnosticResult:
        id, code, name = extractBasicFields(dr)
        eventPurpose = forceRef(dr.value('eventPurpose_id'))
        continued = forceInt(dr.value('continued'))
        regionalCode = forceString(dr.value('regionalCode'))
        federalCode = forceString(dr.value('federalCode'))
        resultId = forceRef(dr.value('result_id'))
        cache.diagnosticResult[id] = {'code': code, 'name': name, 'eventPurpose_id': eventPurpose,
                                      'regionalCode': regionalCode, 'federalCode': federalCode, 'result_id': resultId}

    eventTypePurpose = db.getRecordList('rbEventTypePurpose')
    cache.eventTypePurpose = {}
    for etp in eventTypePurpose:
        id, code, name = extractBasicFields(etp)
        regionalCode = forceString(etp.value('regionalCode'))
        federalCode = forceString(etp.value('federalCode'))
        cache.eventTypePurpose[id] = {'code': code, 'name': name, 'regionalCode': regionalCode, 'federalCode': federalCode}

    eventGoal = db.getRecordList('rbEventGoal')
    cache.eventGoal = {}
    for eg in eventGoal:
        id, code, name = extractBasicFields(eg)
        regionalCode = forceString(eg.value('regionalCode'))
        federalCode = forceString(eg.value('federalCode'))
        eventTypePurpose = forceRef(eg.value('eventTypePurpose_id'))
        cache.eventGoal[id] = {'code': code, 'name': name, 'regionalCode': regionalCode,
                               'federalCode': federalCode, 'eventTypePurpose_id': eventTypePurpose}

    medicalAidKind = db.getRecordList('rbMedicalAidKind')
    cache.medicalAidKind = {}
    for mak in medicalAidKind:
        id, code, name = extractBasicFields(mak)
        regionalCode = forceString(mak.value('regionalCode'))
        federalCode = forceString(mak.value('federalCode'))
        cache.medicalAidKind[id] = {'code': code, 'name': name, 'regionalCode': regionalCode, 'federalCode': federalCode}

    result = db.getRecordList('rbResult')
    cache.result = {}
    for r in result:
        id, code, name = extractBasicFields(r)
        regionalCode = forceString(r.value('regionalCode'))
        federalCode = forceString(r.value('federalCode'))
        continued = forceString(r.value('continued'))
        notAccount = forceString(r.value('notAccount'))
        eventPurpose = forceRef(r.value('eventPurpose_id'))
        cache.result[id] = {'code': code, 'name': name, 'regionalCode': regionalCode, 'federalCode': federalCode,
                            'continued': continued, 'notAccount': notAccount, 'eventPurpose_id': eventPurpose}

    scene = db.getRecordList('rbScene')
    cache.scene = {}
    for s in scene:
        id, code, name = extractBasicFields(s)
        serviceModifier = forceString(s.value('serviceModifier'))
        cache.scene[id] = {'code': code, 'name': name, 'serviceModifier': serviceModifier}

    visitType = db.getRecordList('rbVisitType')
    cache.visitType = {}
    for vt in visitType:
        id, code, name = extractBasicFields(vt)
        serviceModifier = forceString(vt.value('serviceModifier'))
        cache.visitType[id] = {'code': code, 'name': name, 'serviceModifier': serviceModifier}

    finance = db.getRecordList('rbFinance')
    cache.finance = {}
    for f in finance:
        id, code, name = extractBasicFields(f)
        cache.finance[id] = {'code': code, 'name': name}

    unit = db.getRecordList('rbUnit')
    cache.unit = {}
    for u in unit:
        id, code, name = extractBasicFields(u)
        cache.unit[id] = {'code': code, 'name': name}

    documentType = db.getRecordList('rbDocumentType')
    cache.documentType = {}
    # TODO: если нам все-таки нужно экспортировать этот справочник, то взять остальные поля.
    for dt in documentType:
        id, code, name = extractBasicFields(dt)
        regionalCode = forceString(dt.value('regionalCode'))
        federalCode = forceString(dt.value('federalCode'))
        cache.documentType[id] = {'code': code, 'name': name, 'regionalCode': regionalCode, 'federalCode': federalCode}

    policyKind = db.getRecordList('rbPolicyKind')
    cache.policyKind = {}
    for pk in policyKind:
        id, code, name = extractBasicFields(pk)
        regionalCode = forceString(pk.value('regionalCode'))
        federalCode = forceString(pk.value('federalCode'))
        cache.policyKind[id] = {'code': code, 'name': name, 'regionalCode': regionalCode, 'federalCode': federalCode}

    policyType = db.getRecordList('rbPolicyType')
    cache.policyType = {}
    for pt in policyType:
        id, code, name = extractBasicFields(pt)
        cache.policyType[id] = {'code': code, 'name': name}

    return cache

# *****************************************************************************************

class CExportHelperMixin():
    u"""Класс часто используемых функций экспорта"""
    sexMap = {1: u'М',  2: u'Ж'}

    def __init__(self):
        self._representativeInfoCache = {}
        self._regionCenterNameCache = {}
        self._regionNameCache = {}
        self._okatoCache = {}
        self._specialityRegionalCodeCache = {}
        self._specialityFederalCodeCache = {}
        self._personRegionalCodeCache = {}
        self._personFederalCodeCache = {}
        self._serviceCodeCache = {}
        self._serviceInfisCache = {}


    def getClientRepresentativeInfo(self, clientId):
        key = clientId
        result = self._representativeInfoCache.get(key)

        if not result:
            result = getClientRepresentativeInfo(clientId)
            self._representativeInfoCache[key] = result

        return result


    def getRegionCenterName(self, code):
        u"""Возвращает название регионального центра."""

        result = self._regionCenterNameCache.get(code)

        if not result:
            result = ''

            stmt = """
            SELECT `NAME` FROM kladr.KLADR
            WHERE `CODE` LIKE '%s%%' AND `STATUS` IN ('2','3')
            """ % code[:2]
            db = QtGui.qApp.db
            query = db.query(stmt)

            while query.next():
                record = query.record()

                if record:
                    result = forceString(record.value(0))

            self._regionCenterNameCache[code] = result

        return result


    def getRegionName(self, code):
        u""" Возвращает название района. Области отфильтровываются."""

        result = self._regionNameCache.get(code)

        if not result:
            if code != '':
                regionCode = code[:5].ljust(13, '0')
                result = forceString(QtGui.qApp.db.translate('kladr.KLADR','CODE',
                    regionCode,'NAME')) if regionCode[2:5] != '000' else \
                    self.getRegionCenterName(code)
            else:
                result = ''

            self._regionNameCache[code] = result

        return result


    def getRegionOKATO(self, subRegionOKATO):
        u"""Определяем ОКАТО региона по ОКАТО района через КЛАДР."""
        result = self._okatoCache.get(subRegionOKATO, -1)

        if result == -1:
            result = ''
            kladrCode = forceString(QtGui.qApp.db.translate(
                'kladr.KLADR', 'OCATD', subRegionOKATO, 'CODE'))

            if kladrCode:
                result = forceString(QtGui.qApp.db.translate(
                    'kladr.KLADR', 'CODE', kladrCode[:2].ljust(13,'0'),
                    'OCATD')).ljust(5, '0') if kladrCode else ''

            self._okatoCache[subRegionOKATO] = result

        return result


    def getSpecialityRegionalCode(self, personId):
        u"""Определяем региональный код специальности врача по его id"""
        result = self._specialityRegionalCodeCache.get(personId, -1)

        if result == -1:
            result = None
            specialityId = forceRef(QtGui.qApp.db.translate('Person', 'id', personId, 'speciality_id'))

            if specialityId:
                result = forceString(QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'regionalCode'))

            self._specialityRegionalCodeCache[personId] =result

        return result


    def getSpecialityFederalCode(self, personId):
        u"""Определяем федеральный код специальности врача по его id"""
        result = self._specialityFederalCodeCache.get(personId, -1)

        if result == -1:
            result = None
            specialityId = forceRef(QtGui.qApp.db.translate('Person', 'id', personId, 'speciality_id'))

            if specialityId:
                result = forceString(QtGui.qApp.db.translate('rbSpeciality', 'id', specialityId, 'federalCode'))

            self._specialityFederalCodeCache[personId] =result

        return result


    def getPersonRegionalCode(self, personId):
        u"""Определяем региональный код врача по его id"""
        result = self._personRegionalCodeCache.get(personId, -1)

        if result == -1:
            result = forceString(QtGui.qApp.db.translate('Person', 'id', personId, 'regionalCode'))
            self._personRegionalCodeCache[personId] =result

        return result


    def getPersonFederalCode(self, personId):
        u"""Определяем федеральный код врача по его id"""
        result = self._personFederalCodeCache.get(personId, -1)

        if result == -1:
            result = forceString(QtGui.qApp.db.translate('Person', 'id', personId, 'federalCode'))
            self._personFederalCodeCache[personId] =result

        return result


    def getServiceCode(self, id):
        u"""Определяем код профиля оплаты по его id"""
        result = self._serviceCodeCache.get(id, -1)

        if result == -1:
            result = forceString(QtGui.qApp.db.translate('rbService', 'id', id, 'code'))
            self._serviceCodeCache[id] = result

        return result


    def getServiceInfis(self, id):
        u"""Определяем инфис код профиля оплаты по его id"""
        result = self._serviceInfisCache.get(id, -1)

        if result == -1:
            result = forceString(QtGui.qApp.db.translate('rbService', 'id', id, 'infis'))
            self._serviceInfisCache[id] = result

        return result

# *****************************************************************************************


class CRefBooksModel(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._refBooks = OrderedDict()
        self.loadRefBooksStructure()
        self._items = []

    def loadRefBooksStructure(self):
        db = QtGui.qApp.db
        stmt = '''
        SELECT tables.TABLE_NAME AS tableName, tables.TABLE_COMMENT AS tableComment, columns.COLUMN_NAME AS columnName, columns.COLUMN_COMMENT AS columnComment
        FROM information_schema.TABLES as tables
        LEFT JOIN information_schema.COLUMNS as columns ON tables.TABLE_SCHEMA = columns.TABLE_SCHEMA AND tables.TABLE_NAME = columns.TABLE_NAME
        WHERE tables.TABLE_SCHEMA = '%(database)s' AND tables.TABLE_NAME LIKE 'rb%%'
        AND NOT EXISTS (SELECT * FROM information_schema.TABLE_CONSTRAINTS AS tc WHERE tc.TABLE_SCHEMA = '%(database)s' AND tc.TABLE_NAME = tables.TABLE_NAME AND tc.CONSTRAINT_TYPE = 'FOREIGN KEY')
        ''' % {'database':db.db.databaseName()}
        query = db.query(stmt)
        while query.next():
            record = query.record()
            tableName = forceString(record.value('tableName'))
            tableComment = forceString(record.value('tableComment')).capitalize()
            columnName = forceString(record.value('columnName'))
            columnComment = forceString(record.value('columnComment')).capitalize()

            tableDict = self._refBooks.setdefault(tableName, OrderedDict({'comment': tableComment, 'cols': OrderedDict()}))
            if not columnName in tableDict['cols'] and not columnName == 'id':
                tableDict['cols'][columnName] = columnComment


    def rowCount(self, index = QtCore.QModelIndex()):
        return len(self._items) + 1

    def columnCount(self, index = QtCore.QModelIndex()):
        return 2

    def data(self, index = None, role = Qt.DisplayRole):
        row = index.row()
        column = index.column()
        if role == Qt.DisplayRole:
            if row < len(self._items):
                tableName = self._items[row][0]
                if column == 0:
                    return QVariant(self._refBooks.get(tableName, {}).get('comment', ''))
                else:
                    colName = self._items[row][1]
                    return QVariant(self._refBooks.get(tableName, {}).get('cols', {}).get(colName, None))
        return QVariant()

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section == 0:
                    return QVariant(u'Справочник')
                elif section == 1:
                    return QVariant(u'Ключевое поле')

            # if role == Qt.ToolTipRole:
            #     return self._cols[section].toolTip()
            # if role == Qt.WhatsThisRole:
            #     return self._cols[section].whatsThis()
        return QVariant()

    def setData(self, index, value, role = Qt.EditRole):
        if role == Qt.EditRole:
            column = index.column()
            row = index.row()
            if row == len(self._items):
                if value.isNull():
                    return False
                tableName = forceString(value)
                cols = self.getTableColumns(tableName)
                self._items.append([tableName, cols.keys()[0]])
                count = len(self._items)
                rootIndex = QModelIndex()
                self.beginInsertRows(rootIndex, count, count)
                self.insertRows(count, 1, rootIndex)
                self.endInsertRows()
            else:
                self._items[row][column] = forceString(value)
            #self.emitCellChanged(row, column)
            return True
        return False

    def flags(self, index=None):
        row = index.row()
        column = index.column()
        result = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if not (row == len(self._items) and column == 1):
            result |= Qt.ItemIsEditable
        return result

    def getTableColumns(self, tableName):
        return self._refBooks.get(tableName, {}).get('cols', {})

    def getTables(self):
        result = {}
        for tableName in self._refBooks:
            tableUsed = False
            for item in self._items:
                if item[0] == tableName:
                    tableUsed = True
                    break
            if not tableUsed:
                result[tableName] = self._refBooks[tableName]
        return result

    def items(self):
        return self._items

    def getRBStructure(self):
        return self._refBooks


class CRefBooksItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.row = 0
        self.lastrow = 0
        self.column = 0
        self.editor = None

    def createEditor(self, parent, option, index):
        editor = QtGui.QComboBox(parent)
        model = index.model()
        column = index.column()
        if column == 0:
            for tableName, tableData in model.getTables().items():
                editor.addItem(tableData['comment'], tableName)
        else:
            row = index.row()
            for colName, colComment  in model.getTableColumns(model.items()[row][0]).items():
                editor.addItem(colComment, colName)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        row = index.row()
        col = index.column()
        if row == len(model.items()):
            itemIndex  = 0
        else:
            itemIndex = editor.findData(model.items()[row][col])
            if itemIndex == -1:
                itemIndex = 0
        editor.setCurrentIndex(itemIndex)

    def setModelData(self, editor, model, index):
        if editor is not None:
            model.setData(index, self.getEditorData(editor))

    def getEditorData(self, editor):
        return toVariant(editor.itemData(editor.currentIndex()))


class CRefBooksTableView(QtGui.QTableView, CPreferencesMixin):
    # TODO: remove some unnecessary functions, copied from CInDocTableView
    __pyqtSignals__ = ('editInProgress(bool)',
                                )
    def __init__(self, parent):
        QtGui.QTableView.__init__(self, parent)
        self._popupMenu = None

        h = self.fontMetrics().height()
        self.verticalHeader().setDefaultSectionSize(3*h/2)
        self.verticalHeader().hide()

        self.setShowGrid(True)
#        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.setItemDelegate(CRefBooksItemDelegate(self))


    def setSelectionModel(self, selectionModel):
        currSelectionModel = self.selectionModel()
        if currSelectionModel:
            self.disconnect(currSelectionModel, QtCore.SIGNAL('currentChanged(QModelIndex,QModelIndex))'), self.currentChanged)
        QtGui.QTableView.setSelectionModel(self, selectionModel)
        if selectionModel:
            self.connect(selectionModel, QtCore.SIGNAL('currentChanged(QModelIndex,QModelIndex))'), self.currentChanged)


    def createPopupMenu(self, actions=None):
        if not actions:
            actions = []
        self._popupMenu = QtGui.QMenu(self)
        self._popupMenu.setObjectName('popupMenu')
        self.connect(self._popupMenu, QtCore.SIGNAL('aboutToShow()'), self.on_popupMenu_aboutToShow)
        for action in actions:
            if isinstance(action, QtGui.QAction):
                self._popupMenu.addAction(action)
            elif action == '-':
                self._popupMenu.addSeparator()
        return self._popupMenu


    def addPopupSeparator(self):
        if self._popupMenu is None:
            self.createPopupMenu()
        self._popupMenu.addSeparator()


    def addMoveRow(self):
#        if self.model().idxFieldName:
        if self._popupMenu is None:
            self.createPopupMenu()
        self.__actUpRow = QtGui.QAction(u'Поднять строку', self)
        self.__actUpRow.setObjectName('actUpRow')
        self._popupMenu.addAction(self.__actUpRow)
        self.connect(self.__actUpRow, QtCore.SIGNAL('triggered()'), self.on_upRow)
        self.__actDownRow = QtGui.QAction(u'Опустить строку', self)
        self.__actDownRow.setObjectName('actDownRow')
        self._popupMenu.addAction(self.__actDownRow)
        self.connect(self.__actDownRow, QtCore.SIGNAL('triggered()'), self.on_downRow)


    def addPopupDelRow(self):
        if self._popupMenu is None:
            self.createPopupMenu()
        self.__actDeleteRows = QtGui.QAction(u'Удалить строку', self)
        self.__actDeleteRows.setObjectName('actDeleteRows')
        self._popupMenu.addAction(self.__actDeleteRows)
        self.connect(self.__actDeleteRows, QtCore.SIGNAL('triggered()'), self.on_deleteRows)


    def addPopupSelectAllRow(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actSelectAllRow = QtGui.QAction(u'Выделить все строки', self)
        self.__actSelectAllRow.setObjectName('actSelectAllRow')
        self._popupMenu.addAction(self.__actSelectAllRow)
        self.connect(self.__actSelectAllRow, QtCore.SIGNAL('triggered()'), self.on_selectAllRow)


    def addPopupSelectRowsByData(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actSelectRowsByData = QtGui.QAction(u'Выделить строки соответствующие текущему столбцу', self)
        self.__actSelectRowsByData.setObjectName('actSelectRowsByDate')
        self._popupMenu.addAction(self.__actSelectRowsByData)
        self.connect(self.__actSelectRowsByData, QtCore.SIGNAL('triggered()'), self.on_selectRowsByData)


    def addPopupClearSelectionRow(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actClearSelectionRow = QtGui.QAction(u'Снять выделение', self)
        self.__actClearSelectionRow.setObjectName('actClearSelectionRow')
        self._popupMenu.addAction(self.__actClearSelectionRow)
        self.connect(self.__actClearSelectionRow, QtCore.SIGNAL('triggered()'), self.on_clearSelectionRow)


    def addPopupRecordProperies(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actRecordProperties = QtGui.QAction(u'Свойства записи', self)
        self.__actRecordProperties.setObjectName('actRecordProperties')
        self._popupMenu.addAction(self.__actRecordProperties)
        self.connect(self.__actRecordProperties, QtCore.SIGNAL('triggered()'), self.showRecordProperties)


    def addPopupDuplicateCurrentRow(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actDuplicateCurrentRow = QtGui.QAction(u'Дублировать строку', self)
        self.__actDuplicateCurrentRow.setObjectName('actDuplicateCurrentRow')
        self._popupMenu.addAction(self.__actDuplicateCurrentRow)
        self.connect(self.__actDuplicateCurrentRow, QtCore.SIGNAL('triggered()'), self.on_duplicateCurrentRow)


    def addPopupRowFromReport(self, rbTable, rbTableName = u''):
        self.rbTable = rbTable
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actAddFromReportRow = QtGui.QAction(u'Добавить строки из справочника%s'%((u': ' + rbTableName) if rbTableName else u''), self)
        self.__actAddFromReportRow.setObjectName('actAddFromReportRow')
        self._popupMenu.addAction(self.__actAddFromReportRow)
        self.connect(self.__actAddFromReportRow, QtCore.SIGNAL('triggered()'), self.on_addFromReportRow)


    def addPopupDuplicateSelectRows(self):
        if self._popupMenu == None:
            self.createPopupMenu()
        self.__actDuplicateSelectRows = QtGui.QAction(u'Дублировать выделенные строки', self)
        self.__actDuplicateSelectRows.setObjectName('actDuplicateSelectRows')
        self._popupMenu.addAction(self.__actDuplicateSelectRows)
        self.connect(self.__actDuplicateSelectRows, QtCore.SIGNAL('triggered()'), self.on_duplicateSelectRows)


    def setPopupMenu(self, menu):
        self._popupMenu = menu


    def popupMenu(self):
        if self._popupMenu is None:
            self.createPopupMenu()
        return self._popupMenu


    def setDelRowsChecker(self, func):
        self.__delRowsChecker = func


    def keyPressEvent(self, event):
        key = event.key()
        text = unicode(event.text())
        if key == Qt.Key_Escape:
            event.ignore()
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            event.ignore()
        elif event.key() == Qt.Key_Tab :
            index = self.currentIndex()
            model = self.model()
            if index.row() == model.rowCount()-1 and index.column() == model.columnCount()-1 :
                self.parent().focusNextChild()
                event.accept()
            else:
                QtGui.QTableView.keyPressEvent(self, event)
        elif event.key() == Qt.Key_Backtab :
            index = self.currentIndex()
            if index.row() == 0 and index.column() == 0 :
                self.parent().focusPreviousChild()
                event.accept()
            else:
                QtGui.QTableView.keyPressEvent(self, event)
        else:
            QtGui.QTableView.keyPressEvent(self, event)


    def focusInEvent(self, event):
        reason = event.reason()
        model = self.model()
        if reason in [Qt.TabFocusReason, Qt.ShortcutFocusReason, Qt.OtherFocusReason]:
            if not self.hasFocus():
                self.setCurrentIndex(model.index(0, 0))
        elif reason == Qt.BacktabFocusReason:
            if not self.hasFocus():
                self.setCurrentIndex(model.index(model.rowCount()-1, model.columnCount()-1))
        QtGui.QTableView.focusInEvent(self, event)
        self.updateStatusTip(self.currentIndex())


    def focusOutEvent(self, event):
        self.updateStatusTip(None)
        QtGui.QTableView.focusOutEvent(self, event)


    def removeCurrentRow(self):
        index = self.currentIndex()
        if index.isValid():
            row = index.row()
            self.model().removeRow(row)


    def contextMenuEvent(self, event): # event: QContextMenuEvent
        if self._popupMenu and self.model().isEditable():
            self._popupMenu.exec_(event.globalPos())
            event.accept()
        else:
            event.ignore()


    def colKey(self, col):
        return unicode('width '+forceString(col))


    def getSelectedRows(self):
        rowCount = len(self.model().items())
        rowSet = set([index.row() for index in self.selectionModel().selectedIndexes() if index.row()<rowCount])
        result = list(rowSet)
        result.sort()
        return result


    def on_popupMenu_aboutToShow(self):
        row = self.currentIndex().row()
        rowCount = len(self.model().items())
        if self.__actUpRow:
            self.__actUpRow.setEnabled(0<row<rowCount)
        if self.__actDownRow:
            self.__actDownRow.setEnabled(0<=row<rowCount-1)
        if self.__actDuplicateCurrentRow:
            self.__actDuplicateCurrentRow.setEnabled(0<=row<rowCount)
        if self.__actAddFromReportRow:
            self.__actAddFromReportRow.setEnabled(rowCount <= 0)
        if self.__actDeleteRows:
            rows = self.getSelectedRows()
            canDeleteRow = bool(rows)
            if canDeleteRow and self.__delRowsChecker:
                canDeleteRow = self.__delRowsChecker(rows)
            if len(rows) == 1 and rows[0] == row:
                self.__actDeleteRows.setText(u'Удалить текущую строку')
            elif len(rows) == 1:
                self.__actDeleteRows.setText(u'Удалить выделенную строку')
            else:
                self.__actDeleteRows.setText(u'Удалить выделенные строки')
            self.__actDeleteRows.setEnabled(canDeleteRow)
            if self.__actDuplicateSelectRows:
                self.__actDuplicateSelectRows.setEnabled(canDeleteRow)
        if self.__actSelectAllRow:
            self.__actSelectAllRow.setEnabled(0<=row<rowCount)
        if self.__actSelectRowsByData:
            column = self.currentIndex().column()
            items = self.model().items()
            value = items[row].value(column) if row < len(items) else None
            self.__actSelectRowsByData.setEnabled(forceBool(0<=row<rowCount and (value and value.isValid())))
        if self.__actClearSelectionRow:
            self.__actClearSelectionRow.setEnabled(0<=row<rowCount)
        if self.__actRecordProperties:
            self.__actRecordProperties.setEnabled(0<=row<rowCount)


    def on_upRow(self):
        index = self.currentIndex()
        if index.isValid():
            row = index.row()
            if self.model().upRow(row):
                self.setCurrentIndex(self.model().index(row-1, index.column()))
                self.resetSorting()


    def on_downRow(self):
        index = self.currentIndex()
        if index.isValid():
            row = index.row()
            if self.model().downRow(row):
                self.setCurrentIndex(self.model().index(row+1, index.column()))
                self.resetSorting()


    def on_deleteRows(self):
        rows = self.getSelectedRows()
        rows.sort(reverse=True)
        for row in rows:
            self.model().removeRow(row)
#        self.removeCurrentRow()


    def on_selectAllRow(self):
        self.selectAll()


    def on_selectRowsByData(self):
        items = self.model().items()
        currentRow = self.currentIndex().row()
        if currentRow < len(items):
            currentColumn = self.currentIndex().column()
            selectIndexes = self.selectedIndexes()
            selectRowList = []
            for selectIndex in selectIndexes:
                selectRow = selectIndex.row()
                if selectRow not in selectRowList:
                    selectRowList.append(selectRow)
            currentRecord = items[currentRow]
            data = currentRecord.value(currentColumn)
            if data.isValid():
                for row, item in enumerate(items):
                    if (item.value(currentColumn) == data) and (row not in selectRowList):
                        self.selectRow(row)


    def on_duplicateCurrentRow(self):
        currentRow = self.currentIndex().row()
        items = self.model().items()
        if currentRow < len(items):
            newRecord = self.model().getEmptyRecord()
            copyFields(newRecord, items[currentRow])
            newRecord.setValue(self.model()._idFieldName, toVariant(None))
            self.model().insertRecord(currentRow+1, newRecord)


    def on_addFromReportRow(self):
        if self.rbTable:
            db = QtGui.qApp.db
            table = db.table(self.rbTable)
            rbTableIdList = db.getDistinctIdList(table, 'id')
            items = self.model().items()
            for row, rbTableId in enumerate(rbTableIdList):
                if row <= len(items):
                    newRecord = self.model().getEmptyRecord()
                    newRecord.setValue('rbTable_id', toVariant(rbTableId))
                    self.model().insertRecord(row, newRecord)


    def on_duplicateSelectRows(self):
        currentRow = self.currentIndex().row()
        items = self.model().items()
        if currentRow < len(items):
            selectIndexes = self.selectedIndexes()
            selectRowList = []
            for selectIndex in selectIndexes:
                selectRow = selectIndex.row()
                if selectRow not in selectRowList:
                    selectRowList.append(selectRow)
            selectRowList.sort()
            for row in selectRowList:
                newRecord = self.model().getEmptyRecord()
                copyFields(newRecord, items[row])
                items.append(newRecord)
            self.model().reset()


    def on_clearSelectionRow(self):
        self.clearSelection()

    def resetSorting(self):
        self.horizontalHeader().setSortIndicatorShown(False)
        self.__sortColumn = None

# мне не хочется возиться с proxy model - я принял решение сортировать в модели.
# возможны побочные эффекты, но я думаю забить на это...
    def on_sortByColumn(self, logicalIndex):
        model = self.model()
        if isinstance(model, CRefBooksModel):
            header=self.horizontalHeader()
            if model.cols()[logicalIndex].sortable():
                if self.__sortColumn == logicalIndex:
                    self.__sortAscending = not self.__sortAscending
                else:
                    self.__sortColumn = logicalIndex
                    self.__sortAscending = True
                header.setSortIndicatorShown(True)
                header.setSortIndicator(self.__sortColumn, Qt.AscendingOrder if self.__sortAscending else Qt.DescendingOrder)
                model.sortData(logicalIndex, self.__sortAscending)
            elif self.__sortColumn != None:
                header.setSortIndicator(self.__sortColumn, Qt.AscendingOrder if self.__sortAscending else Qt.DescendingOrder)
            else:
                header.setSortIndicatorShown(False)


    def loadPreferences(self, preferences):
        model = self.model()
        if isinstance(model, (CRefBooksModel)):
            for col in range(model.columnCount()):
                width = forceInt(getPref(preferences, self.colKey(col), None))
                if width:
                    self.setColumnWidth(col, width)
        self.horizontalHeader().setStretchLastSection(True)


    def savePreferences(self):
        preferences = {}
        model = self.model()
        if isinstance(model, (CRefBooksModel)):
            for col in range(model.columnCount()):
                width = self.columnWidth(col)
                setPref(preferences, self.colKey(col), QVariant(width))
        return preferences


    def updateStatusTip(self, index):
        tip = forceString(index.data(Qt.StatusTipRole)) if index else ''
        event = QtGui.QStatusTipEvent(tip)
        QtGui.qApp.sendEvent(self, event)


    def currentChanged(self, current, previous):
        QtGui.QTableView.currentChanged(self, current, previous)
        self.updateStatusTip(current)


def isExternalOrgCode(orgInfisCode):
    db = QtGui.qApp.db
    tableOrgStructure = db.table('OrgStructure')
    orgId = QtGui.qApp.currentOrgId()
    return not bool(db.getIdList(tableOrgStructure,
                                 tableOrgStructure['id'],
                                 where=[tableOrgStructure['bookkeeperCode'].eq(orgInfisCode),
                                        tableOrgStructure['organisation_id'].eq(orgId),
                                        tableOrgStructure['deleted'].eq(0)]))