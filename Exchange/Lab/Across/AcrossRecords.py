# -*- coding: utf-8 -*-

from PyQt4.QtCore import *

from xml.sax import parseString, handler


def escape(s):
    return unicode(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace('\'', '&#39;')


class CRequest:
    def __init__(self):
        self.samples = []
        pass


    def addSample(self):
        sample = CSampleRequest()
        sample.id_ = len(self.samples)+1
        self.samples.append(sample)
        return sample


    def toXml(self, extraFields):
#            <?xml version="1.0" encoding="utf-8"?>
#            <dbdata>
#            <rows table="doctors_kb">
#                <row>
#                <value field="code">1</value>
#                </row>
#            </rows>
#            </dbdata>
        tables = {}
        for sample in self.samples:
            sample.collectXml(tables, extraFields)
        parts = []
        for tableName, content in tables.iteritems():
            parts.append(('<rows table="%s">\n' % tableName)+'\n '.join(content)+'\n</rows>')
        return '<?xml version="1.0" encoding="utf-8"?>\n<dbdata>\n '+' \n'.join(parts)+'\n</dbdata>'


class CUpdateDoctorsRequest:
    def __init__(self):
        self.doctors = []
        pass


    def addDoctor(self):
        doctor = CDoctor()
        self.doctors.append(doctor)
        return doctor


    def toXml(self, extraFields):
        tables = {}
        for doctor in self.doctors:
            doctor.collectXml(tables, extraFields)
        parts = []
        for tableName, content in tables.iteritems():
            parts.append(('<rows table="%s">\n' % tableName)+'\n '.join(content)+'\n</rows>')
        return '<?xml version="1.0" encoding="utf-8"?>\n<dbdata>\n '+' \n'.join(parts)+'\n</dbdata>'



class CXmlableRecord(object):
    def __init__(self):
        assert(self.tableName)
        assert(self.fields)

    def fielsListAsXML(self, extraFields):
        parts = []
        for attrName, xmlName, mustHave, type_ in self.fields:
            val = getattr(self, attrName, None)
            if val is None:
                if mustHave:
                    raise AttributeError(u'%s instance has no attribute or emply attribute "%s"'% (type(self).__name__, attrName))
                else:
#                    continue
                    val = ''
            if isinstance(val, QDate):
#               val = val.toString('yyyy-MM-dd')
                val = val.toString('dd.MM.yyyy')
            val = escape(unicode(val))
            if val:
                parts.append('<value field="%s">%s</value>' % (xmlName, val))
            else:
                parts.append('<value field="%s"/>' % (xmlName,))
        for xmlName, val in extraFields.iteritems():
            parts.append('<value field="%s">%s</value>' % (xmlName, unicode(val)))
        return u'\n    '.join(parts)


    def collectXml(self, tables, extraFields):
        records = tables.setdefault(self.tableName,[])
        records.append(' <row>\n    ' + self.fielsListAsXML(extraFields) + '\n  </row>')


    def initByDict(self, xmlDict):
        for attrName, xmlName, mustHave, type_ in self.fields:
            val = xmlDict.get(xmlName, None)
            if val is None:
                if mustHave:
                    raise AttributeError(u'%s instance has no attribute or emply attribute "%s" (%s)'% (type(self).__name__, attrName, xmlName))
            else:
                if type_ == QDate:
                    if val:
#                        val = QDate.fromString(val, Qt.ISODate)
                        val = QDate.fromString(val, 'dd.MM.yyyy')
                        if not val.isValid():
                            raise AttributeError(u'date format is invalid')
                    else:
                        val = QDate()
                setattr(self, attrName, val)
#                del xmlDict[xmlName]


#Поля таблицы «acl_in_sample»
class CSampleRequest(CXmlableRecord):
    tableName = 'acl_in_sample'
    #               attr            | name in xml | must have | type
    fields    = ( ('id_',           'record_id',    True,       unicode),
                  ('date',          'send_date',    True,       QDate),
                  ('sampleType',    'sample_type',  True,       unicode),
                  ('lab',           'lab',          True,       unicode),
                  ('label',         'sid',          True,       unicode),
                  ('clientId',      'patient_id',   True,       unicode),
                  ('eventId',       'doc_id',       True,       unicode),
                  ('fullName',      'family_name',  True,       unicode),
                  ('birthDate',     'birth_date',   True,       QDate),
                  ('sex',           'sex',          True,       unicode),
                  ('pregnancy',     'Pregnancy',    False,      unicode),
                  ('datecw',        'datecw',       False,      unicode),
                  ('climax',        'climax',       False,      unicode),
                  ('counterpart',   'counterpart',  False,      unicode),
                  ('financeType',   'subcounterpart', False,    unicode),
                  ('orgStructure',  'dep_no',       False,      unicode),
                  ('person',        'dr_no',        False,      unicode),
                  ('policy',        'social_no',    False,      unicode),
                  ('insurer',       'social_name',  False,      unicode),
                  ('mkb',           'diag_code',    False,      unicode),
                  ('diag',          'diag',         False,      unicode),
                  ('note',          'note',         False,      unicode),
                  ('priority',      'priority',     False,      unicode),
                  ('host_id',       'host_id',      False,      unicode),
                  ('reserved1',     'reserved1',    False,      unicode),
                  ('reserved2',     'reserved2',    False,      unicode),
                  ('reserved3',     'reserved3',    False,      unicode),
                  ('reserved4',     'reserved4',    False,      unicode),
                  ('reserved5',     'reserved5',    False,      unicode),
                )

    def __init__(self):
        self.id_            = None  # Уникальный идентификатор записи в таблице/V
        self.date           = QDate.currentDate()  # Дата записи/V
        self.sampleType     = 0    # Для морфологии = 1, для всех других исследований = 0/V
        self.lab            = ''   # Номер лаборатории/V
        self.label          = None # Номер пробы/V
        self.clientId       = None # Уникальный идентификатор пациента/V
        self.eventId        = None # ИсторияБолезни/№ Истории Болезни/V
        self.fullName       = None # ИндОбследуемого/ФИО/V
        self.birthDate      = None # ДатаРождения/ДатаРождения/V
        self.sex            = None # Пол/V
        self.pregnancy      = None # Беременость
        self.datecw         = None # ДеньЦикла
        self.climax         = None # Пменоп
        self.counterpart    = None # Контрагент/Код отделения ЛПУ, или код внешнего ЛПУ/V
        self.orgStructure   = None # ОтделенияКонтрагента/Код отделения внешнего ЛПУ
        self.financeType    = None # Код ИсточникаЗаказа (ОМС,ДМС )/V
        self.person         = None # Назначающий_врач	Код Назначающего врача
        self.policy         = None # Серия Номер страхового полиса (ННН 000000000008)
        self.insurer        = None # Код страховой компании
        self.mkb            = None # ДиагнозМКБ
        self.diag           = None # ДиагнозСтрока
        self.note           = None # Примечание
        self.priority       = 1    # Приоритет (срочный/рутинный- 0/1)
        self.host_id        = None # идентификатор внешней системы, используется при связи с несколькими внешними системами
        self.reserved1      = None
        self.reserved2      = None
        self.reserved3      = None
        self.reserved4      = None
        self.reserved5      = None
#        self.mis_id         = ''   # идентификатор МИС
        self.tests         = []


    def addTest(self):
        test = CTestRequest()
        test.masterId = self.id_
        test.id_ = len(self.tests)+1
        self.tests.append(test)
        return test


    def collectXml(self, tables, extraFields):
        CXmlableRecord.collectXml(self, tables, extraFields)
        for test in self.tests:
            test.collectXml(tables, extraFields)



class CTestRequest(CXmlableRecord):
    tableName = 'acl_in_test'

    #               attr            | name in xml | must have | type
    fields    = ( ('masterId',      'sample_in_record_id',    True,       unicode),
                  ('id_',           'test_code',    True,       unicode),
                  ('mcn',           'mcn_code',     False,      unicode),
                  ('note',          'note_text',    False,      unicode),
                  ('specimen',      'specimen',     False,      unicode),
                  ('reserved1',     'reserved1',    False,      unicode),
                  ('reserved2',     'reserved2',    False,      unicode),
                  ('reserved3',     'reserved3',    False,      unicode),
                  ('reserved4',     'reserved4',    False,      unicode),
                  ('reserved5',     'reserved5',    False,      unicode),
                )


    def __init__(self):
        self.masterId     = None
        self.id_          = None # ТестКод/Уникальный код теста/V
        self.mcn          = None # ГосКод
        self.note         = None # ТестКомментарий
        self.specimen     = None # Материал
        self.reserved1    = None
        self.reserved2    = None
        self.reserved3    = None
        self.reserved4    = None
        self.reserved5    = None
#       self.mis_id       = '' # идентификатор МИС



class CResultHandler(handler.ContentHandler):
    def __init__(self, classes):
        handler.ContentHandler.__init__(self)
        self.mapTableNameToClass = dict((class_.tableName, class_) for class_ in classes)
        self.instancesByClasses = {}
        self.elementStack = []
        self.tableName = None
        self.values = {}
        self.fieldName = None
        self.fieldValue = ''


    def startElement(self, name, attrs):
        if name == 'dbdata':
            if self.elementStack:
                raise Exception('element "%s" is out of order' % name)
        elif name == 'rows':
            if len(self.elementStack) != 1 or self.elementStack[-1] != 'dbdata':
                raise Exception('element "%s" is out of order' % name)
            tableName = attrs.get('table', None)
            if not tableName:
                raise Exception('attribute "table" is empty in "rows"')
            self.tableName = tableName
        elif name == 'row':
            if len(self.elementStack) != 2 or self.elementStack[-1] != 'rows':
                raise Exception('element "%s" is out of order' % name)
            self.values = {}
        elif name == 'value':
            if len(self.elementStack) != 3 or self.elementStack[-1] != 'row':
                raise Exception('element "%s" is out of order' % name)
            fieldName = attrs.get('field', None)
            if not fieldName:
                raise Exception('attribute "field" is empty in "value"')
            self.fieldName = fieldName
            self.fieldValue = ''
        else:
            raise Exception('unknown element "%s"' % name)
        self.elementStack.append(name)


    def endElement(self, name):
        if self.elementStack[-1] != name:
            raise Exception('element "%s" closed by element "%s"' % (self.elementStack[-1], name))
        if name == 'rows':
            self.tableName = None
        elif name == 'row':
            self.createRecord()
        elif name == 'value':
            self.values[self.fieldName] = self.fieldValue
        self.elementStack.pop()


    def characters(self, content):
        if self.elementStack[-1] == 'value':
            self.fieldValue += content


    def endDocument(self):
        for class_, records in self.instancesByClasses.iteritems():
            if hasattr(class_, 'restoreStruct'):
                for record in records:
                    record.restoreStruct(self.instancesByClasses)


    def createRecord(self):
        class_ = self.mapTableNameToClass.get(self.tableName,None)
        if class_ is None:
            raise Exception('undefined table "%s"/' % self.tableName)
        record = class_()
        record.initByDict(self.values)
        self.instancesByClasses.setdefault(class_, []).append(record)



class CResult:
    def __init__(self):
        self.samples = []

    def fromXml(self, xml):
        handler = CResultHandler( (CSampleResult, CTestType0Result, CTestType1Result ))
        parseString(xml, handler)
        return handler.instancesByClasses.get(CSampleResult,[])



class CSampleResult(CXmlableRecord):
    tableName = 'acl_out_sample'
    #               attr            | name in xml | must have | type
    fields    = ( ('id_',           'record_id',    True,       unicode),
                  ('date',          'sample_date',  True,       QDate),
                  ('sampleType',    'sample_type',  True,       unicode),
                  ('lab',           'lab',          True,       unicode),
                  ('label',         'sid',          True,       unicode),
                  ('clientId',      'patient_id',   True,       unicode),
                  ('eventId',       'doc_id',       True,       unicode),
                  ('fullName',      'family_name',  True,       unicode),
                  ('birthDate',     'birth_date',   True,       QDate),
                  ('sex',           'sex',          True,       unicode),
                  ('pregnancy',     'Pregnancy',    False,      unicode),
                  ('datecw',        'datecw',       False,      unicode),
                  ('climax',        'climax',       False,      unicode),
                  ('counterpart',   'counterpart',  False,      unicode),
                  ('orgStructure',  'subcounterpart', False,   unicode),
                  ('person',        'dr_no',        False,      unicode),
                  ('policy',        'social_no',    False,      unicode),
                  ('insurer',       'social_name',  False,      unicode),
                  ('mkb',           'diag_code',    False,      unicode),
                  ('diag',          'diag',         False,      unicode),
                  ('note',          'note',         False,      unicode),
                  ('priority',      'priority',     False,      unicode),
                  ('host_id',       'host_id',      False,      unicode),
                  ('reserved1',     'reserved1',    False,      unicode),
                  ('reserved2',     'reserved2',    False,      unicode),
                  ('reserved3',     'reserved3',    False,      unicode),
                  ('reserved4',     'reserved4',    False,      unicode),
                  ('reserved5',     'reserved5',    False,      unicode),
                  ('misId',         'mis_id',       False,      unicode),
                )

    def __init__(self):
        self.id_            = None # V
        self.date           = None # ДатаЗаказа  ДатаЗаказа  V
        self.sampleType     = None # sample_type 1   V
        self.lab            = None # Лаборатория lab1    V
        self.label          = None # НомПробы (Штрихкод) V
        self.clientId       = None # PID -
        self.eventId        = None # ИсторияБолезни/№ Истории Болезни   V
        self.fullName       = None # ИндОбследуемого ФИО
        self.birthDate      = None # ДатаРождения
        self.sex            = None # Пол
        self.pregnancy      = None # Беременость
        self.datecw         = None # ДеньЦикла
        self.climax         = None # Пменоп
        self.counterpart    = None # Контрагент/Код отделения ЛПУ, или код внешнего ЛПУ
        self.orgStructure   = None # ОтделенияКонтрагента/Код отделения внешнего ЛПУ
        self.person         = None # Назначающий_врач   Код Назначающего врача
        self.policy         = None # Серия Номер страхового полиса (ННН 000000000008)
        self.insurer        = None # Код страховой компании
        self.mkb            = None # ДиагнозМКБ
        self.diag           = None # ДиагнозСтрока
        self.note           = None # Примечание
        self.priority       = None # Порядковы номер выгрузки в ББД
        self.host_id        = None # идентификатор внешней системы, используется при связи с несколькими внешними системами
        self.reserved1      = None
        self.reserved2      = None
        self.reserved3      = None
        self.reserved4      = None
        self.reserved5      = None
        self.misId          = None # идентификатор МИС
        self.tests          = []




class CTestType0Result(CXmlableRecord):
    tableName = 'acl_out_results_sample_type0'
    #               attr            | name in xml | must have | type
    fields    = ( ('masterId',      'sample_out_record_id',    True,       unicode),
                  ('id_',           'test_code',    True,       unicode),
                  ('mcn',           'mcn_code',     False,      unicode),
                  ('note',          'note',         False,      unicode),
                  ('result',        'result',       False,      unicode),
                  ('unit',          'units',        False,      unicode),
                  ('refmin',        'refmin',       False,      unicode),
                  ('refmax',        'refmax',       False,      unicode),
                  ('specimen',      'specimen',     False,      unicode),
                  ('device',        'device',       False,      unicode),
                  ('reserved1',     'reserved1',    False,      unicode),
                  ('reserved2',     'reserved2',    False,      unicode),
                  ('reserved3',     'reserved3',    False,      unicode),
                  ('reserved4',     'reserved4',    False,      unicode),
                  ('reserved5',     'reserved5',    False,      unicode),
                  ('misId',         'mis_id',       False,      unicode),

                )

    def __init__(self):
#        sample_out_record_id
        self.masterId       = None
        self.id_            = None # ТестКод
        self.mcn            = None # ГосКод
        self.note           = None # ТекстРезультат  -   V или и
        self.result         = None # Результат
        self.unit           = None # Единица
        self.refmin         = None # НормаLO
        self.refmax         = None # НормаHI НормаHI
        self.specimen       = None # Материал    -
        self.device         = None # Анализатор  -
        self.reserved1      = None # ДатаВремяРезультата
        self.reserved2      = None # reserved2   Тест.Наименование
        self.reserved3      = None # reserved3
        self.reserved4      = None # reserved4
        self.reserved5      = None # reserved5
        self.misId          = None # идентификатор МИС


    def restoreStruct(self, instancesByClasses):
        masters = instancesByClasses.get(CSampleResult)
        for master in masters:
            if master.id_ == self.masterId and master.sampleType == '0':
                master.tests.append(self)
                return
        raise Exception('cannot find sample with id="%s" and type="0"' % self.masterId)


class CTestType1Result(CXmlableRecord):
    tableName = 'acl_out_results_sample_type1'
    fields    = ( ('masterId',      'sample_out_record_id',    True,       unicode),
                  ('id_',           'test_code',    True,       unicode),
                  ('mcn',           'mcn_code',     False,      unicode),
                  ('note',          'note_text',    True,       unicode),
                  ('result',        'result',       False,      unicode),
                  ('refmin',        'refmin',       False,      unicode),
                  ('refmax',        'refmax',       False,      unicode),
                  ('specimen',      'specimen',     False,      unicode),
                  ('device',        'device',       False,      unicode),
                  ('reserved1',     'reserved1',    False,      unicode),
                  ('reserved2',     'reserved2',    False,      unicode),
                  ('reserved3',     'reserved3',    False,      unicode),
                  ('reserved4',     'reserved4',    False,      unicode),
                  ('reserved5',     'reserved5',    False,      unicode),
                  ('misId',         'mis_id',       False,      unicode),
                )

    def __init__(self):
        self.masterId       = None
        self.id_            = None # ТестКод
        self.note           = None # ТекстРезультат  -   V или и
        self.specimen       = None # Материал    -
        self.reserved1      = None # ДатаВремяРезультата
        self.reserved2      = None # reserved2   Тест.Наименование
        self.reserved3      = None # reserved3
        self.reserved4      = None # reserved4
        self.reserved5      = None # reserved5
        self.misId          = None # идентификатор МИС

    def restoreStruct(self, instancesByClasses):
        masters = instancesByClasses.get(CSampleResult)
        for master in masters:
            if master.id_ == self.masterId and master.sampleType == '1':
                master.tests.append(self)
                return
        raise Exception('cannot find sample with id="%s" and type="1"' % self.masterId)


class CTest(CXmlableRecord):
    tableName = 'acl_Test'
    #               attr            | name in xml | must have | type
    fields    = ( ('code',          'code',         True,       unicode),
                  ('name',          'name',         True,       unicode),
                  ('descr',         'fname',        False,      unicode),
                  ('type_',         'type',         False,      unicode),
                  ('unit',          'units',        False,      unicode),
                  ('specimen',      'specimen',     False,      unicode),
                  ('lab',           'lab',          False,      unicode),
                  ('socialCode',    'social_code',  False,      unicode),
                  ('group',         'group_pro',    False,      unicode),
                  ('reserved1',     'reserved1',    False,      unicode),
                  ('reserved2',     'reserved2',    False,      unicode),
                  ('reserved3',     'reserved3',    False,      unicode),
                  ('reserved4',     'reserved4',    False,      unicode),
                  ('reserved5',     'reserved5',    False,      unicode),
                  ('reserved6',     'reserved6',    False,      unicode),
                )

    def __init__(self):
        self.code           = None # ТестКод ACL/V
        self.name           = None # Имя теста/V
        self.descr          = None # Полное имя теста
        self.type_          = None # Тип теста
        self.unit           = None # Ед. измерения
        self.specimen       = None # Материал
        self.lab            = None # Лаборатория
        self.socialCode     = None # Гос код (ОМС)
        self.group          = None # Группа обработки
        self.reserved1      = None
        self.reserved2      = None
        self.reserved3      = None
        self.reserved4      = None
        self.reserved5      = None
        self.reserved6      = None


class CSpecimen(CXmlableRecord):
    tableName = 'acl_Test'
    #               attr            | name in xml | must have | type
    fields    = ( ('code',          'code',         True,       unicode),
                  ('name',          'name',         True,       unicode),
                  ('type_',         'type',         False,      unicode),
                  ('reserved1',     'reserved1',    False,      unicode),
                  ('reserved2',     'reserved2',    False,      unicode),
                  ('reserved3',     'reserved3',    False,      unicode),
                  ('reserved4',     'reserved4',    False,      unicode),
                  ('reserved5',     'reserved5',    False,      unicode),
                  ('reserved6',     'reserved6',    False,      unicode),
                )

    def __init__(self):
        self.code           = None # Код Материала ACL
        self.name           = None # Имя материала/V
        self.type_          = None # Тип материала
        self.reserved1      = None
        self.reserved2      = None
        self.reserved3      = None
        self.reserved4      = None
        self.reserved5      = None
        self.reserved6      = None


class CDoctor(CXmlableRecord):
    tableName = 'Doctors_KB'
    #               attr            | name in xml | must have | type
    fields    = ( ('code',          'code',         True,       unicode),
                  ('name',          'familyname',   True,       unicode),
                  ('orgStructure',  'department_code', False,      unicode),
                  ('reserved1',     'reserved1',    False,      unicode),
                  ('reserved2',     'reserved2',    False,      unicode),
                  ('reserved3',     'reserved3',    False,      unicode),
                  ('reserved4',     'reserved4',    False,      unicode),
                  ('reserved5',     'reserved5',    False,      unicode),
#                  ('reserved6',     'reserved6',    False,      unicode),
                )

    def __init__(self):
        self.code           = None # Код врача Хост  (табельный номер)
        self.name           = None # ФИО врача
        self.orgStructure   = None # Код отделения КБ (По таблице соответствия кодов)
        self.reserved1      = None
        self.reserved2      = None
        self.reserved3      = None
        self.reserved4      = None
        self.reserved5      = None
        self.reserved6      = None



if __name__ == '__main__':
    request = CRequest()
    sample = request.addSample()
    sample.date           = QDate.currentDate()  # Дата
    sample.sampleType     = '0'          # Тип
    sample.lab            = 'some lab'   # Номер лаборатории/V
    sample.label          = '3780115'    # Номер пробы/V
    sample.clientId       = 123456       # Уникальный идентификатор пациента/V
    sample.eventId        = 654321       # ИсторияБолезни/№ Истории Болезни/V
    sample.fullName       = u'Иванов Иван Иванович' # ИндОбследуемого/ФИО/V
    sample.birthDate      = QDate(2000,12,31) # ДатаРождения/ДатаРождения/V
    sample.sex            = u'м' # Пол/V
    #sample.pregnancy      = None # Беременость
    #sample.datecw         = None # ДеньЦикла
    #sample.climax         = None # Пменоп
    sample.counterpart    = u'п51'# Контрагент/Код отделения ЛПУ, или код внешнего ЛПУ/V
    sample.orgStructure   = u'терап1'   # ОтделенияКонтрагента/Код отделения внешнего ЛПУ
    sample.financeType    = u'ОМС' # Код ИсточникаЗаказа (ОМС,ДМС )/V
    sample.person         = u'007' # Назначающий_врач   Код Назначающего врача
    sample.policy         = u'АК 47' # Серия Номер страхового полиса (ННН 000000000008)
    sample.insurer        = u'кАСКО' # Код страховой компании
    sample.mkb            = u'S19.2' # ДиагнозМКБ
    sample.diag           = u'Никто не знает' # ДиагнозСтрока
    sample.note           = u'Примечаешь?' # Примечание
    sample.priority       = 1    # Приоритет (срочный/рутинный- 0/1)
    #sample.host_id        = None # идентификатор внешней системы, используется при связи с несколькими внешними системами
    test = sample.addTest()
    test.mcn          = u'001' # ГосКод
    #test.note         = None # ТестКомментарий
    test.specimen     = u'кровища' # Материал
    test = sample.addTest()
    test.mcn          = u'002' # ГосКод
    #test.note         = None # ТестКомментарий
    test.specimen     = u'ещё кровища' # Материал


    sample = request.addSample()
    sample.date           = QDate.currentDate()  # Дата
    sample.sampleType     = '1'          # Тип
    sample.lab            = 'some lab'   # Номер лаборатории/V
    sample.label          = '3784004'    # Номер пробы/V
    sample.clientId       = 234567       # Уникальный идентификатор пациента/V
    sample.eventId        = 765432       # ИсторияБолезни/№ Истории Болезни/V
    sample.fullName       = u'Петров Пётр Петрович' # ИндОбследуемого/ФИО/V
    sample.birthDate      = QDate(1900,11,30) # ДатаРождения/ДатаРождения/V
    sample.sex            = u'м' # Пол/V
    #sample.pregnancy      = None # Беременость
    #sample.datecw         = None # ДеньЦикла
    #sample.climax         = None # Пменоп
    sample.counterpart    = u'п51'# Контрагент/Код отделения ЛПУ, или код внешнего ЛПУ/V
    sample.orgStructure   = u'терап2'   # ОтделенияКонтрагента/Код отделения внешнего ЛПУ
    sample.financeType    = u'Бюджет' # Код ИсточникаЗаказа (ОМС,ДМС )/V
    sample.person         = u'007' # Назначающий_врач   Код Назначающего врача
    sample.policy         = u'АК 47:)" &) <3' # Серия Номер страхового полиса (ННН 000000000008)
    sample.insurer        = u'кАСКО' # Код страховой компании
    sample.mkb            = u'Z00.1' # ДиагнозМКБ
    sample.diag           = u'Никто не знает - 2' # ДиагнозСтрока
    sample.note           = u'Всё ещё примечаешь?' # Примечание
    sample.priority       = 0    # Приоритет (срочный/рутинный- 0/1)
    #sample.host_id        = None # идентификатор внешней системы, используется при связи с несколькими внешними системами
    test = sample.addTest()
    test.mcn          = u'011' # ГосКод
    #test.note         = None # ТестКомментарий
    test.specimen     = u'кровища второго' # Материал
    test = sample.addTest()
    test.mcn          = u'012' # ГосКод
    #test.note         = None # ТестКомментарий
    test.specimen     = u'ещё кровища второго' # Материал

    print request.toXml({'mis_id':'1234567890'}).encode('utf8')


    inxml = u'''<?xml version="1.0" encoding="utf-8"?>
    <dbdata>
    <rows table="acl_out_sample">
    <row>
        <value field="record_id">1</value>
        <value field="sample_date">2011-09-16</value>
        <value field="sample_type">0</value>
        <value field="lab">some lab</value>
        <value field="sid">11001011101</value>
        <value field="patient_id">123456</value>
        <value field="doc_id">654321</value>
        <value field="family_name">Иванов Иван Иванович</value>
        <value field="birth_date">2000-12-31</value>
        <value field="sex">м</value>
        <value field="counterpart">п51</value>
        <value field="dep_no">Трижды краснознамённое отделение амбулаторной хирургии</value>
        <value field="dr_no">007</value>
        <value field="social_no">АК 47</value>
        <value field="social_name">кАСКО</value>
        <value field="diag_code">S19.2</value>
        <value field="diag">Никто не знает</value>
        <value field="note">Примечаешь?</value>
        <value field="priority">1</value>
        <value field="host_id">1</value>
        <value field="reserved1">1111111111</value>
        <value field="reserved2">2222222222</value>
        <value field="reserved3">3333333333</value>
        <value field="reserved4">4444444444</value>
        <value field="reserved5">5555555555</value>
        <value field="mis_id">1234567890</value>
    </row>
    <row>
        <value field="record_id">2</value>
        <value field="sample_date">2011-09-16</value>
        <value field="sample_type">1</value>
        <value field="lab">some lab</value>
        <value field="sid">Это я, ваш штрих-код</value>
        <value field="patient_id">234567</value>
        <value field="doc_id">765432</value>
        <value field="family_name">Петров Пётр Петрович</value>
        <value field="birth_date">1900-11-30</value>
        <value field="sex">м</value>
        <value field="counterpart">п51</value>
        <value field="dep_no">Терапия</value>
        <value field="dr_no">007</value>
        <value field="social_no">АК 47:)&quot; &amp;) &lt;3</value>
        <value field="social_name">кАСКО</value>
        <value field="diag_code">Z00.1</value>
        <value field="diag">Никто не знает - 2</value>
        <value field="note">Всё ещё примечаешь?</value>
        <value field="priority">0</value>
        <value field="mis_id">1234567890</value>
    </row>
    </rows>
    <rows table="acl_out_results_sample_type0">
    <row>
        <value field="sample_out_record_id">1</value>
        <value field="test_code">1</value>
        <value field="mcn_code">001</value>
        <value field="note">ура!</value>
        <value field="result">37</value>
        <value field="units">попугай</value>
        <value field="refmin">30</value>
        <value field="refmax">40</value>
        <value field="specimen">кровища</value>
        <value field="device">миска</value>
        <value field="reserved1">11111111111</value>
        <value field="reserved2">22222222222</value>
        <value field="reserved3">33333333333</value>
        <value field="reserved4">44444444444</value>
        <value field="reserved5">55555555555</value>
        <value field="mis_id">1234567890</value>
    </row>
    <row>
        <value field="sample_out_record_id">1</value>
        <value field="test_code">2</value>
        <value field="mcn_code">002</value>
        <value field="note">ура! два раза</value>
        <value field="result">37.25</value>
        <value field="units">мм/сек</value>
        <value field="refmin">10</value>
        <value field="refmax">20</value>
        <value field="specimen">ещё кровища</value>
        <value field="device">чашка</value>
        <value field="reserved1">11111111111</value>
        <value field="reserved2">22222222222</value>
        <value field="reserved3">33333333333</value>
        <value field="reserved4">44444444444</value>
        <value field="reserved5">55555555555</value>
        <value field="mis_id">1234567890</value>
    </row>
    </rows>
    <rows table="acl_out_results_sample_type1">
    <row>
        <value field="sample_out_record_id">2</value>
        <value field="test_code">1</value>
        <value field="mcn_code">011</value>
        <value field="note_text">ура! два раза</value>
        <value field="specimen">кровища второго</value>
        <value field="reserved1">11111111111</value>
        <value field="reserved2">22222222222</value>
        <value field="reserved3">33333333333</value>
        <value field="reserved4">44444444444</value>
        <value field="reserved5">55555555555</value>
        <value field="mis_id">1234567890</value>
    </row>
    <row>
        <value field="sample_out_record_id">2</value>
        <value field="test_code">2</value>
        <value field="mcn_code">012</value>
        <value field="specimen">ещё кровища второго</value>
        <value field="note_text">xa-xa. два раза</value>
        <value field="reserved1">11111111111</value>
        <value field="reserved2">22222222222</value>
        <value field="reserved3">33333333333</value>
        <value field="reserved4">44444444444</value>
        <value field="reserved5">55555555555</value>
        <value field="mis_id">1234567890</value>
    </row>
    </rows>
    </dbdata>
    '''

    result = CResult().fromXml(inxml.encode('utf8'))

