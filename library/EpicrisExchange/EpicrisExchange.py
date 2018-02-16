# -*- coding: utf-8 -*-
# Эпикризы, обмен с Москвой
import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtXml import QDomDocument

from library.Utils import forceString, toVariant, forceInt
from library.XML.XMLHelper import CXMLHelper
import stmts


class EpicrisTemplates():
    def __init__(self):
        self.Document = {}
        self.encoding = u'UTF-8'

    def getEpicrisTemplate(self, epicId, eventId):
        epicrisRec = QtGui.qApp.db.getRecordEx('rbEpicrisisTemplates', '*', 'id = %s' % epicId)
        sectionsRec = self.getSection(epicId)
        self.Document.setdefault(u'epicrisis', self.createXMLDoc(epicrisRec, sectionsRec, eventId))
        doc = self.Document[u'epicrisis']
        return doc

    def getSection(self, epicId):
        record = QtGui.qApp.db.getIdList(stmt=stmts.STMT_Sections % epicId)
        return record

    # Конструктор
    # Добавление шаблона эпикриза
    def addTemplate(self, name, code, orgStruct, htmlTemplate, epicType):
        tableTemplate = QtGui.qApp.db.table('rbEpicrisisTemplates')
        recordTemplate = QtGui.qApp.db.getRecordEx(tableTemplate, 'code', 'code = %s' % code)
        if not recordTemplate:
            rec = tableTemplate.newRecord()
            rec.setValue('name', name)
            rec.setValue('code', code)
            rec.setValue('id_orgStructure', orgStruct)
            rec.setValue('printTemplate', htmlTemplate)
            rec.setValue('type', epicType)
            QtGui.qApp.db.insertRecord(tableTemplate, rec)

    # Редактирование шаблона эпикриза
    def modifyTemplate(self, epicId, name, code, orgStruct, htmlTemplate, epicType):
        tableTemplate = QtGui.qApp.db.table('rbEpicrisisTemplates')
        recordTemplate = QtGui.qApp.db.getRecordEx(tableTemplate, '*', 'id = %i' % forceInt(epicId))
        recordTemplate.setValue('name', name)
        recordTemplate.setValue('code', code)
        recordTemplate.setValue('id_orgStructure', orgStruct)
        recordTemplate.setValue('printTemplate', htmlTemplate)
        recordTemplate.setValue('type', epicType)
        QtGui.qApp.db.updateRecord(tableTemplate, recordTemplate)

    # Добавление секции
    def addSection(self, name, description):
        tableSection = QtGui.qApp.db.table('rbEpicrisisSections')
        recordSection = QtGui.qApp.db.getRecordEx(tableSection, '*', 'name = %s' % name)
        if not recordSection:
            rec = tableSection.newRecord()
            rec.setValue('name', toVariant(name))
            rec.setValue('description', toVariant(description))
            QtGui.qApp.db.insertRecord(tableSection, rec)

    # Редактирование секции
    def modifySection(self, sectId, name, description):
        tableSection = QtGui.qApp.db.table('rbEpicrisisSections')
        recordSection = QtGui.qApp.db.getRecordEx(tableSection, '*', 'id = %i' % forceInt(sectId))
        recordSection.setValue('name', name)
        recordSection.setValue('description', toVariant(description))
        QtGui.qApp.db.updateRecord(tableSection, recordSection)

    # Добавление проперти
    def addProperty(self, name, type, default, domain, description):
        table = QtGui.qApp.db.table('rbEpicrisisProperty')
        rec = QtGui.qApp.db.getRecordEx(table, '*', 'name = %s' % name)
        if not rec:
            rec = table.newRecord()
            rec.setValue('name', toVariant(name))
            rec.setValue('type', toVariant(type))
            rec.setValue('default', toVariant(default))
            rec.setValue('valueDomain', toVariant(domain))
            rec.setValue('description', toVariant(description))
            QtGui.qApp.db.insertRecord(table, rec)

    # Редактирование проперти
    def modifyProperty(self, propId, name, type, default, domain, description):
        table = QtGui.qApp.db.table('rbEpicrisisProperty')
        rec = QtGui.qApp.db.getRecordEx(table, '*', 'id = %i' % forceInt(propId))
        rec.setValue('name', toVariant(name))
        rec.setValue('type', toVariant(type))
        rec.setValue('default', toVariant(default))
        rec.setValue('valueDomain', toVariant(domain))
        rec.setValue('description', toVariant(description))
        QtGui.qApp.db.updateRecord(table, rec)

    # Добавление соедиений между шаблоном эпикриза и секциями
    def addConTemplateToSection(self, templateId, sectionsList):
        table = QtGui.qApp.db.table('rbEpicrisisTemplates_rbEpicrisisSections')
        rec = QtGui.qApp.db.getRecordEx(table, 'id', 'id_rbEpicrisisTemplates = %s' % templateId)
        if rec:
            QtGui.qApp.db.deleteRecord(table, 'id_rbEpicrisisTemplates = %s' % templateId)
        idx = 0
        for v in sectionsList:
            idx += 1
            newRec = table.newRecord()
            newRec.setValue('idx', idx)
            newRec.setValue('id_rbEpicrisisTemplates', templateId)
            newRec.setValue('id_rbEpicrisisSections', v)
            QtGui.qApp.db.insertRecord(table, newRec)

    # Добавление соединений между секциями и пропертями
    def addConSectionToProperty(self, sectionId, propertyList):
        table = QtGui.qApp.db.table('rbEpicrisisSections_rbEpicrisisProperty')
        rec = QtGui.qApp.db.getRecordEx(table, 'id', 'id_rbEpicrisisSections = %s' % sectionId)
        if rec:
            QtGui.qApp.db.deleteRecord(table, 'id_rbEpicrisisSections = %s' % sectionId)
        idx = 0
        for v in propertyList:
            idx += 1
            newRec = table.newRecord()
            newRec.setValue('idx', idx)
            newRec.setValue('id_rbEpicrisisSections', sectionId)
            newRec.setValue('id_rbEpicrisisProperty', v)
            QtGui.qApp.db.insertRecord(table, newRec)

    # Форматирование секций
    def modifySectionFormat(self, templateId, sectionId, htmlTemplate, isRequired, isEditable):
        table = QtGui.qApp.db.table('rbEpicrisisTemplates_rbEpicrisisSections')
        rec = QtGui.qApp.db.getRecordEx(table, '*', [table['id_rbEpicrisisTemplates'].eq(templateId),
                                               table['id_rbEpicrisisSections'].eq(sectionId)])
        if rec:
            rec.setValue('htmlTemplate', htmlTemplate)
            rec.setValue('isRequired', isRequired)
            rec.setValue('isEditable', isEditable)
            QtGui.qApp.db.updateRecord(table, rec)

    # Форматирование пропертей
    def modifyPropertyFormat(self, sectionId, propertyId, htmlTemplate, orgStruct, isRequired, isEditable):
        table = QtGui.qApp.db.table('rbEpicrisisSections_rbEpicrisisProperty')
        rec = QtGui.qApp.db.getRecordEx(table, '*', [table['id_rbEpicrisisSections'].eq(sectionId),
                                               table['id_rbEpicrisisProperty'].eq(propertyId)])
        if rec:
            rec.setValue('htmlTemplate', htmlTemplate)
            rec.setValue('orgStruct', orgStruct)
            rec.setValue('isRequired', isRequired)
            rec.setValue('isEditable', isEditable)
            QtGui.qApp.db.updateRecord(table, rec)

    # Добавление шаблонной фразы
    def addStoredProperty(self, propertyId, value, orgStruct):
        table = QtGui.qApp.db.table('rbEpicrisisStoredProperties')
        rec = QtGui.qApp.db.getRecordEx(table, 'id', [table['rbEpicrisisProperty_id'].eq(forceString(propertyId)),
                                                table['StoredValue'].eq(forceString(value)),
                                                table['orgStructure_id'].eq(forceString(orgStruct))])
        if not rec:
            newRec = table.newRecord()
            newRec.setValue('rbEpicrisisProperty_id', toVariant(propertyId))
            newRec.setValue('StoredValue', toVariant(value))
            newRec.setValue('orgStructure_id', toVariant(orgStruct))
            QtGui.qApp.db.insertRecord(table, newRec)

    # Получение полей раздела по Ид
    def getSectionById(self, idSection):
        doc = CXMLHelper.createDomDocument(rootElementName='PROPERTY', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        recSection = QtGui.qApp.db.getRecordEx('rbEpicrisisSections', '*', 'id = %s' % forceString(idSection))
        if recSection:
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'NAME'), forceString(recSection.value('name')))
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'DESCRIPTION'),
                                forceString(recSection.value('description')))
        return doc

    # Получение полей свойства по Ид
    def getPropertyById(self, idProperty):
        doc = CXMLHelper.createDomDocument(rootElementName='PROPERTY', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        recProperty = QtGui.qApp.db.getRecordEx('rbEpicrisisProperty', '*', 'id = %s' % forceString(idProperty))
        if recProperty:
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'NAME'), forceString(recProperty.value('name')))
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'TYPE'),
                                forceString(self.getPropertyType(recProperty.value('type'))))
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'VALUE'),
                                forceString(recProperty.value('defaultValue')))
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'HTMLTEMPLATE'),
                                forceString(recProperty.value('htmlTemplate')))
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'DOMAIN'),
                                forceString(recProperty.value('valueDomain')))
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'ORGSTRUCT'),
                                forceString(recProperty.value('orgStruct')))
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'REQUIRED'),
                                forceString(recProperty.value('isRequired')))
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'DESCRIPTION'),
                                forceString(recProperty.value('description')))
        return doc

    def delElement(self, name, elemId):
        if forceString(name).upper() == 'EPICRIS':
            table = QtGui.qApp.db.table('rbEpicrisisTemplates')
        elif forceString(name).upper() == 'SECTION':
            table = QtGui.qApp.db.table('rbEpicrisisSections')
        elif forceString(name).upper() == 'PROPERTY':
            table = QtGui.qApp.db.table('rbEpicrisisProperty')
        else:
            return
        QtGui.qApp.db.deleteRecord(table, 'id = %i' % forceInt(elemId))

    # Генерация XML со списками элементов
    # Получение списка шаблонов эпикризов
    def getEpicrisList(self):
        doc = CXMLHelper.createDomDocument(rootElementName='EPICRISLIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        query = QtGui.qApp.db.query('SELECT * FROM rbEpicrisisTemplates')
        while query.next():
            record = query.record()
            epicRoot = CXMLHelper.addElement(rootElement, 'EPICRIS')
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'ID'), forceString(record.value('id')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'NAME'), forceString(record.value('name')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'CODE'), forceString(record.value('code')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'ORG_STRUCT'), forceString(record.value('id_orgStructure')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'PRINTTEMPLATE'), forceString(record.value('printTemplate')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'TYPE'), forceString(record.value('type')))
        return doc

    # Получение списка шаблонов эпикризов по ид OrgStruct
    def getEpicrisTemplatesListByOrgStruct(self, orgStruct):
        doc = CXMLHelper.createDomDocument(rootElementName='EPICRISLIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        query = QtGui.qApp.db.query('SELECT * FROM `rbEpicrisisTemplates` WHERE id_orgStructure RLIKE \' %s,\'' % orgStruct)
        while query.next():
            record = query.record()
            epicRoot = CXMLHelper.addElement(rootElement, 'EPICRIS')
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'ID'), forceString(record.value('id')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'NAME'), forceString(record.value('name')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'CODE'), forceString(record.value('code')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'ORG_STRUCT'), forceString(record.value('id_orgStructure')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'PRINTTEMPLATE'), forceString(record.value('printTemplate')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'TYPE'), forceString(record.value('type')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'DATE'), forceString(QtCore.QDate.currentDate()))
        return doc

    # Получение списка секций
    def getSectonsList(self):
        doc = CXMLHelper.createDomDocument(rootElementName='SECTIONSLIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        query = QtGui.qApp.db.query('SELECT * FROM rbEpicrisisSections')
        while query.next():
            record = query.record()
            sectRoot = CXMLHelper.addElement(rootElement, 'SECTION')
            CXMLHelper.setValue(CXMLHelper.addElement(sectRoot, 'ID'), forceString(record.value('id')))
            CXMLHelper.setValue(CXMLHelper.addElement(sectRoot, 'NAME'), forceString(record.value('name')))
            CXMLHelper.setValue(CXMLHelper.addElement(sectRoot, 'HTMLTEMPLATE'), forceString(query.value(2))) # ???
            CXMLHelper.setValue(CXMLHelper.addElement(sectRoot, 'DESCRIPTION'), forceString(record.value('description')))
        return doc

    # Получение списка секций по ид шаблона епикриза
    def getSectionsByTemplate(self, idTemplate):
        doc = CXMLHelper.createDomDocument(rootElementName='EPICRIS', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        query = QtGui.qApp.db.query(
            'SELECT * FROM rbEpicrisisTemplates_rbEpicrisisSections WHERE id_rbEpicrisisTemplates = %s' % idTemplate)
        while query.next():
            record = query.record()
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'IDSECTION'), forceString(record.value('id_rbEpicrisisSections')))
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'IDX'), forceString(record.value('idx')))
        return doc

    # Получение списка пропертей
    def getPropertyesList(self, printAsTable=None):
        doc = CXMLHelper.createDomDocument(rootElementName='PROPERTYESLIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        if printAsTable:
            query = QtGui.qApp.db.query('SELECT * FROM rbEpicrisisProperty WHERE printAsTable = %s' % printAsTable)
        else:
            query = QtGui.qApp.db.query('SELECT * FROM rbEpicrisisProperty')
        while query.next():
            record = query.record()
            propRoot = CXMLHelper.addElement(rootElement, 'PROPERTY')
            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'ID'), forceString(record.value('id')))
            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'NAME'), forceString(record.value('name')))
            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'TYPE'), forceString(record.value('type')))
            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'DEFAULT'), forceString(record.value('defaultValue')))
            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'HTMLTEMPLATE'), forceString(query.value(5))) # ???
            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'DOMAIN'), forceString(record.value('valueDomain')))
            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'ORG_STRUCT'), forceString(query.value(7))) # ???
            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'ISREQUIRED'), forceString(query.value(8))) # ???
            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'DESCRIPTION'), forceString(record.value('desctiption')))
        return doc

    # Получение списка пропертей по ид секции
    def getPropertyesListBySection(self, idSection):
        doc = CXMLHelper.createDomDocument(rootElementName='SECTION', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        query = QtGui.qApp.db.query(
            'SELECT * FROM rbEpicrisisSections_rbEpicrisisProperty WHERE id_rbEpicrisisSections = %s' % idSection)
        while query.next():
            record = query.record()
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'IDPROPERTY'), forceString(record.value('id_rbEpicrisisProperty')))
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'IDX'), forceString(record.value('idx')))
        return doc

    # Получение шаблона проперти по ид
    def getPropertyTemplateById(self, eventId, propId, someId, orgStruct_id):
        doc = CXMLHelper.createDomDocument(rootElementName='PROPERTYESLIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        query = QtGui.qApp.db.query('SELECT * FROM rbEpicrisisProperty WHERE id = %i' % forceInt(propId))
        while query.next():
            record = query.record()
            propRoot = CXMLHelper.addElement(rootElement, 'PROPERTY')
            stringDef = forceString(record.value('defaultValue')).upper()
            if stringDef.find('SELECT') >= 0 or stringDef.find('CALL') >= 0:
                recordDef = self.getQueryResult(forceString(record.value('defaultValue')), eventId)
                if recordDef:
                    for n in recordDef:
                        countColumns = n.record().count()
                        fieldsColumns = u''
                        if countColumns > 1:
                            for i in range(countColumns):
                                fieldsColumns += forceString(n.record().fieldName(i)) + '#'
                            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'DEFAULT'), fieldsColumns)
                        while n.next():
                            resultString = u''
                            for i in range(countColumns):
                                resultString += forceString(n.record().value(i)) + '#'
                            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'DEFAULT'), resultString)
                else:
                    CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'DEFAULT'), u"Null")
            else:
                CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'DEFAULT'), forceString(record.value('defaultValue')))
            storedProp = CXMLHelper.addElement(rootElement, 'STORED')
            if orgStruct_id:
                storedPropertyes = self.getStoredProperty(propId, orgStruct_id)
                if storedPropertyes:
                    for v in storedPropertyes:
                        CXMLHelper.setValue(CXMLHelper.addElement(storedProp, 'STOREDID'), v[0])
                        CXMLHelper.setValue(CXMLHelper.addElement(storedProp, 'STOREVALUE'), v[1])
        CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'SOMEID'), forceString(someId))
        return doc

    # Получение списка типов
    def getPropertyTypesList(self):
        doc = CXMLHelper.createDomDocument(rootElementName='TYPE', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        query = QtGui.qApp.db.query('SELECT * FROM rbEpicrisisPropertyType')
        # query = QtGui.qApp.db.query('SELECT * FROM rbEpicrisPropertyType') # такой таблицы вообще нет
        while query.next():
            record = query.record()
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'ID'), forceString(record.value('id')))
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'NAME'), forceString(record.value('name')))
            CXMLHelper.setValue(CXMLHelper.addElement(rootElement, 'DESCRIPTION'), forceString(record.value('description')))
        return doc

    # Получение шаблонов фраз
    def getStoredProperty(self, propertyId, orgStruct):
        query = QtGui.qApp.db.query(
            'SELECT id, StoredValue FROM rbEpicrisisStoredProperties WHERE rbEpicrisisProperty_id = %s AND orgStructure_id = %s AND deleted = 0' % (
            propertyId, orgStruct))
        valueList = []
        while query.next():
            if forceString(query.value(0)):
                valueList.append([forceString(query.value(0)), forceString(query.value(1))])
        return valueList

    # Удаление шаблонной фразы
    def deleteStoredProperty(self, propertyId):
        tblStoredProperty = QtGui.qApp.db.table('rbEpicrisisStoredProperties')
        recProperty = QtGui.qApp.db.getRecordEx(tblStoredProperty, '*', tblStoredProperty['id'].eq(propertyId))
        if recProperty:
            recProperty.setValue('deleted', toVariant(1))
            QtGui.qApp.db.updateRecord(tblStoredProperty, recProperty)

    # Генерация XML с шаблоном эпикриза
    def createXMLDoc(self, epicrisList, sectionsList, eventId):
        doc = CXMLHelper.createDomDocument(rootElementName='EPICRIS_LIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        self.addElement(rootElement, epicrisList, sectionsList, eventId)
        return doc

    def addElement(self, rootElement, epicrisList, sectionsList, eventId):
        recordEpic = epicrisList
        epicrisRoot = CXMLHelper.addElement(rootElement, 'EPICRIS')
        CXMLHelper.setValue(CXMLHelper.addElement(epicrisRoot, 'ID'), forceString(recordEpic.value('id')))
        CXMLHelper.setValue(CXMLHelper.addElement(epicrisRoot, 'NAME'), forceString(recordEpic.value('name')))
        CXMLHelper.setValue(CXMLHelper.addElement(epicrisRoot, 'CODE'), forceString(recordEpic.value('code')))
        CXMLHelper.setValue(CXMLHelper.addElement(epicrisRoot, 'ORG_STRUCT'),
                            forceString(recordEpic.value('id_orgStructure')))
        CXMLHelper.setValue(CXMLHelper.addElement(epicrisRoot, 'PRINTTEMPLATE'),
                            forceString(recordEpic.value('printTemplate'))),
        CXMLHelper.setValue(CXMLHelper.addElement(epicrisRoot, 'TYPE'),
                            forceString(recordEpic.value('type')))

        recordSectList = sectionsList
        for k in recordSectList:
            recordSect = QtGui.qApp.db.getRecordEx('rbEpicrisisSections', 'name, id, description',
                                             'id = %s' % k)
            recordSectCon = QtGui.qApp.db.getRecordEx('rbEpicrisisTemplates_rbEpicrisisSections',
                                                'htmlTemplate, isRequired, isEditable',
                                                'id_rbEpicrisisTemplates = %s AND id_rbEpicrisisSections = %s' % (
                                                    forceString(recordEpic.value('id')), k))
            epicrisSection = CXMLHelper.addElement(epicrisRoot, 'SECTIONS')
            stringDef = forceString(recordSect.value('name')).upper()
            if stringDef.find('SELECT') >= 0 or stringDef.find('CALL') >= 0:
                recordName = self.getQueryResult(forceString(recordSect.value('name')), eventId)
                if recordName:
                    for n in recordName:
                        while n.next():
                            CXMLHelper.setValue(CXMLHelper.addElement(epicrisSection, 'NAME'), forceString(n.value(0)))
            else:
                CXMLHelper.setValue(CXMLHelper.addElement(epicrisSection, 'NAME'),
                                    forceString(recordSect.value('name')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicrisSection, 'ID'), forceString(recordSect.value('id')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicrisSection, 'NAME'), forceString(recordSect.value('name')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicrisSection, 'HTMLTEMPLATE'),
                                forceString(recordSectCon.value('htmlTemplate')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicrisSection, 'ISREQUIRED'),
                                forceString(recordSectCon.value('isRequired')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicrisSection, 'ISEDITABLE'),
                                forceString(recordSectCon.value('isEditable')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicrisSection, 'DESCRIPTION'),
                                forceString(recordSect.value('description')))

            recordList = QtGui.qApp.db.getIdList('rbEpicrisisSections_rbEpicrisisProperty', 'id_rbEpicrisisProperty',
                                           'id_rbEpicrisisSections = %i ORDER BY `idx`' % forceInt(
                                               recordSect.value('id')))
            for v in recordList:
                rec = QtGui.qApp.db.getRecordEx('rbEpicrisisProperty', '*', 'id = %s' % v)
                recCon = QtGui.qApp.db.getRecordEx('rbEpicrisisSections_rbEpicrisisProperty',
                                             'htmlTemplate, orgStruct, isRequired, isEditable',
                                             'id_rbEpicrisisSections = %s AND id_rbEpicrisisProperty = %s' % (
                                                 forceInt(recordSect.value('id')), v))
                if rec and recCon:
                    epicrisProperty = CXMLHelper.addElement(epicrisSection, 'PROPERTYES')
                    CXMLHelper.setValue(CXMLHelper.addElement(epicrisProperty, 'ID'),
                                        forceString(rec.value('id')))

                    if forceString(rec.value('name')).find('SELECT') >= 0 or forceString(rec.value('name')).find('CALL') >= 0:
                        recordName = self.getQueryResult(forceString(rec.value('name')), eventId)
                        if recordName:
                            for n in recordName:
                                while n.next():
                                    CXMLHelper.setValue(CXMLHelper.addElement(epicrisProperty, 'NAME'), forceString(n.value(0)))
                    else:
                        CXMLHelper.setValue(CXMLHelper.addElement(epicrisProperty, 'NAME'),
                                            forceString(rec.value('name')))
                    CXMLHelper.setValue(CXMLHelper.addElement(epicrisProperty, 'TYPE'),
                                        forceString(self.getPropertyType(rec.value('type'))))
                    CXMLHelper.setValue(CXMLHelper.addElement(epicrisProperty, 'DEFAULT'),
                                        forceString(rec.value('id')))
                    CXMLHelper.setValue(CXMLHelper.addElement(epicrisProperty, 'HTMLTEMPLATE'),
                                        forceString(recCon.value('htmlTemplate')))
                    CXMLHelper.setValue(CXMLHelper.addElement(epicrisProperty, 'DOMAIN'),
                                        forceString(rec.value('valueDomain')))
                    CXMLHelper.setValue(CXMLHelper.addElement(epicrisProperty, 'ORG_STRUCT'),
                                        forceString(recCon.value('orgStruct')))
                    CXMLHelper.setValue(CXMLHelper.addElement(epicrisProperty, 'ISREQUIRED'),
                                        forceString(recCon.value('isRequired')))
                    CXMLHelper.setValue(CXMLHelper.addElement(epicrisProperty, 'ISEDITABLE'),
                                        forceString(recCon.value('isEditable')))
                    CXMLHelper.setValue(CXMLHelper.addElement(epicrisProperty, 'DESCRIPTION'),
                                        forceString(rec.value('description')))

        return epicrisRoot

    # Парсинг XML для создания шаблона эпикриза
    def addEpicrisTemplate(self, docum, modify=False):
        tmp = docum
        doc = QDomDocument()
        if not doc.setContent(tmp):
            return
        root = doc.documentElement()
        if not root.firstChildElement('TEMPLATE'):
            return
        epicList = root.firstChild()
        while not epicList.isNull():
            epicElement = epicList.toElement()
            if epicElement:
                if modify:
                    epicId = forceString(epicElement.firstChildElement('ID').text())
                epicName = forceString(epicElement.firstChildElement('NAME').text())
                epicCode = forceString(epicElement.firstChildElement('CODE').text())
                epicOrgStruct = forceString(epicElement.firstChildElement('ID_ORGSTRUCTURE').text())
                epicPrintTemplate = forceString(epicElement.firstChildElement('PRINTTEMPLATE').text())
                epicType = forceString(epicElement.firstChildElement('TYPE').text())
            if modify:
                self.modifyTemplate(epicId, epicName, epicCode, epicOrgStruct, epicPrintTemplate, epicType)
            else:
                self.addTemplate(epicName, epicCode, epicOrgStruct, epicPrintTemplate, epicType)
            epicList = epicList.nextSibling()

    # Парсинг XML для создания шаблона раздела эпикриза
    def addSectionsTemplate(self, docum, modify=False):
        tmp = docum
        doc = QDomDocument()
        if not doc.setContent(tmp):
            return
        root = doc.documentElement()
        if not root.firstChildElement('SECTION'):
            return
        epicList = root.firstChild()
        while not epicList.isNull():
            sectionElement = epicList.toElement()
            if sectionElement:
                if modify:
                    sectionId = forceString(sectionElement.firstChildElement('ID').text())
                sectionName = forceString(sectionElement.firstChildElement('NAME').text())
                sectionDesc = forceString(sectionElement.firstChildElement('DESCRIPTION').text())
            if modify:
                self.modifySection(sectionId, sectionName, sectionDesc)
            else:
                self.addSection(sectionName, sectionDesc)
            epicList = epicList.nextSibling()

    # Парсинг XML для создания свойства эпикриза
    def addPropertyTemplate(self, docum, modify=False):
        tmp = docum
        doc = QDomDocument()
        if not doc.setContent(tmp):
            return
        root = doc.documentElement()
        if not root.firstChildElement('PROPERTY'):
            return
        epicList = root.firstChild()
        while not epicList.isNull():
            propertyElement = epicList.toElement()
            if propertyElement:
                if modify:
                    propertyId = forceString(propertyElement.firstChildElement('ID').text())
                propertyName = forceString(propertyElement.firstChildElement('NAME').text())
                propertyType = forceString(propertyElement.firstChildElement('TYPE').text())
                propertyDefault = forceString(propertyElement.firstChildElement('DEFAULT').text())
                propertyDomain = forceString(propertyElement.firstChildElement('DOMAIN').text())
                propertyDesc = forceString(propertyElement.firstChildElement('DESCRIPTION').text())
            if modify:
                self.modifyProperty(propertyId, propertyName, propertyType, propertyDefault,
                                    propertyDomain, propertyDesc)
            else:
                self.addProperty(propertyName, propertyType, propertyDefault, propertyDomain,
                                 propertyDesc)
            epicList = epicList.nextSibling()

    # Парсинг XML для связи пропертей и секций
    def addConnectSectionToProperty(self, docum):
        tmp = docum
        doc = QDomDocument()
        if not doc.setContent(tmp):
            return
        root = doc.documentElement()
        if not root.firstChildElement('SECTION'):
            return
        sectList = root.firstChild()
        sectionElement = sectList.toElement()
        sectionId = forceString(sectionElement.firstChildElement('ID').text())
        propertyList = sectionElement.firstChildElement('PROPERTY')
        propList = []
        while not propertyList.isNull():
            propElement = propertyList.toElement()
            propertyId = forceString(propElement.firstChildElement('ID').text())
            propList.append(propertyId)
            propertyList = propertyList.nextSibling()
        self.addConSectionToProperty(sectionId, propertyList)

    # Парсинг XML для связи шаблона эпикриза и секций
    def addConnectionTemplateToSection(self, docum):
        tmp = docum
        doc = QDomDocument()
        if not doc.setContent(tmp):
            return
        root = doc.documentElement()
        if not root.firstChildElement('TEMPLATE'):
            return
        tempList = root.firstChild()
        templateElement = tempList.toElement()
        templateId = forceString(templateElement.firstChildElement('ID').text())
        sectionsList = templateElement.firstChildElement('SECTION')
        sectList = []
        while not sectionsList.isNull():
            sectElement = sectionsList.toElement()
            sectionId = forceString(sectElement.firstChildElement('ID').text())
            sectList.append(sectionId)
            sectionsList = sectionsList.nextSibling()
        self.addConTemplateToSection(templateId, sectList)

    # Парсинг XML для форматирования секции
    def formatSection(self, docum):
        tmp = docum
        doc = QDomDocument()
        if not doc.setContent(tmp):
            return
        root = doc.documentElement()
        if not root.firstChildElement('TEMPLATE'):
            return
        tempList = root.firstChild()
        templateElement = tempList.toElement()
        templateId = forceString(templateElement.firstChildElement('ID').text())
        sectionsList = templateElement.firstChildElement('SECTION')
        sectElement = sectionsList.toElement()
        sectionId = forceString(sectElement.firstChildElement('ID').text())
        sectionHtml = forceString(sectElement.firstChildElement('HTMLTEMPLATE').text())
        sectionRequired = forceString(sectElement.firstChildElement('ISREQUIRED').text())
        sectionEditable = forceString(sectElement.firstChildElement('ISEDITABLE').text())
        self.modifySectionFormat(templateId, sectionId, sectionHtml, sectionRequired, sectionEditable)

    # Парсинг XML для форматирования проперти
    def formatProperty(self, docum):
        tmp = docum
        doc = QDomDocument()
        if not doc.setContent(tmp):
            return
        root = doc.documentElement()
        if not root.firstChildElement('SECTION'):
            return
        sectList = root.firstChild()
        sectionElement = sectList.toElement()
        sectionId = forceString(sectionElement.firstChildElement('ID').text())
        propertyList = sectionElement.firstChildElement('PROPERTY')
        propElement = propertyList.toElement()
        propertyId = forceString(propElement.firstChildElement('ID').text())
        propertyHtml = forceString(propElement.firstChildElement('HTMLTEMPLATE').text())
        propertyRequired = forceString(propElement.firstChildElement('ISREQUIRED').text())
        propertyEditable = forceString(propElement.firstChildElement('ISEDITABLE').text())
        propertyOrgStruct = forceString(propElement.firstChildElement('ORGSTRUCT').text())
        self.modifyPropertyFormat(sectionId, propertyId, propertyHtml, propertyOrgStruct, propertyRequired,
                                  propertyEditable)

    # Парсинг XML для удаления элемента шаблона
    def delElementTemplate(self, docum):
        tmp = docum
        doc = QDomDocument
        if not doc.setContent(tmp):
            return
        root = doc.documentElement()
        if not root.firstChildElement('ELEMENT'):
            return
        epicList = root.firstChild()
        while not epicList.isNull():
            deleteElement = epicList.toElement()
            if deleteElement:
                delName = forceString(deleteElement.firstChildElement('ELEMENT_NAME').text())
                delId = forceString(deleteElement.firstChildElement('ID').text())
                self.delElement(delName, delId)
            epicList = epicList.nextSibling()

    # Парсинг запросов
    def getQueryResult(self, query, eventId):
        arrayQueryes = query.split('/* */')
        result = []

        for v in arrayQueryes:
            if v.find('%s'):
                v = v.replace('%s', forceString(eventId))
                result.append(QtGui.qApp.db.query(v))
            else:
                result.append(QtGui.qApp.db.query(v))
        return result

    # Получение типа по ид
    def getPropertyType(self, propertyId):
        result = QtGui.qApp.db.translate('rbEpicrisisPropertyType', 'id', propertyId, 'name')
        if result:
            return result


class Epicris():
    def __init__(self):
        self.Document = {}
        self.encoding = u'UTF-8'
        self.actionId = 0

    def getHtmlbyXML(self, xml):
        tmp = xml
        doc = QDomDocument()
        if not doc.setContent(tmp):
            return
        root = doc.documentElement()
        epicList = root.firstChild()
        html = "<style>table{border-collapse: collapse; border: 1px solid black} table tr td,table tr th {border: 1px solid black}</style>"
        while not epicList.isNull():
            epicrisElement = epicList.toElement()
            if epicrisElement:
                html += forceString(epicrisElement.firstChildElement('PRINTTEMPLATE').text())
                sectionList = epicrisElement.firstChildElement('SECTION')
                while not sectionList.isNull():
                    sectionElement = sectionList.toElement()
                    htmlSec = ""
                    propertyList = sectionElement.firstChildElement('PROPERTY')
                    while not propertyList.isNull():
                        propertyElement = propertyList.toElement()
                        propertyType = forceString(propertyElement.firstChildElement('TYPE').text())
                        if propertyType.upper() != 'TABLE':
                            name = forceString(propertyElement.firstChildElement('NAME').text())
                            value = forceString(propertyElement.firstChildElement('VALUE').text())
                            htmlSec += forceString(
                                propertyElement.firstChildElement('HTMLTEMPLATE').text().replace("{name}",
                                                                                                 name).replace(
                                    "{value}", value))
                        else:
                            valueList = propertyElement.firstChildElement('VALUE')
                            trlist = ""
                            valueCount = 0;
                            while not valueList.isNull():
                                valueElement = forceString(valueList.toElement().text())
                                columns = valueElement.split('#')
                                # columns.pop()
                                tr = "<tr>"
                                for col in columns:
                                    if valueCount == 0:
                                        tr += "<th>" + col + "</th>"
                                    else:
                                        tr += "<td>" + col + "</td>"
                                tr += "</tr>"
                                trlist += tr
                                valueCount += 1
                                valueList = valueList.nextSibling()
                            name = forceString(propertyElement.firstChildElement('NAME').text())
                            value = "<table>" + trlist + "</table>"
                            htmlSec += forceString(
                                propertyElement.firstChildElement('HTMLTEMPLATE').text().replace("{name}",
                                                                                                 name).replace(
                                    "{value}", value))
                        propertyList = propertyList.nextSibling()
                    name = forceString(sectionElement.firstChildElement('NAME').text())
                    html += forceString(
                        sectionElement.firstChildElement('HTMLTEMPLATE').text().replace("{name}", name).replace(
                            "{value}", htmlSec))
                    sectionList = sectionList.nextSibling()
            epicList = epicList.nextSibling()
        return html

    # Получение диагноза
    def getDiagnosisAndMKBByEvent(self, eventId):
        tblEvent = QtGui.qApp.db.table('Event')
        tblDiagnostic = QtGui.qApp.db.table('Diagnostic')
        tblDiagnosis = QtGui.qApp.db.table('Diagnosis')
        tblDiagnosisType = QtGui.qApp.db.table('rbDiagnosisType')
        tblMKB = QtGui.qApp.db.table('MKB')

        table = tblEvent.innerJoin(tblDiagnostic, tblDiagnostic['event_id'].eq(tblEvent['id']))
        table = table.innerJoin(tblDiagnosis, tblDiagnostic['diagnosis_id'].eq(tblDiagnosis['id']))
        table = table.innerJoin(tblDiagnosisType, tblDiagnosis['diagnosisType_id'].eq(tblDiagnosisType['id']))
        table = table.innerJoin(tblMKB, tblMKB['DiagID'].eq(tblDiagnosis['MKB']))

        diagnosisRecords = QtGui.qApp.db.getRecordList(table,
                                                       [tblMKB['DiagID'], tblMKB['DiagName'], tblDiagnosisType['code']],
                                                       tblEvent['id'].eq(eventId))
        if diagnosisRecords:
            for v in diagnosisRecords:
                if forceInt(v.value('code')) == 1:
                    return (forceString(v.value('DiagId')), forceString(v.value('DiagName')))
                elif forceInt(v.value('code') == 2):
                    return (forceString(v.value('DiagId')), forceString(v.value('DiagName')))
                else:
                    return ('', '')
        else:
            return ('', '')


    # Создание екшена
    def setAction(self, actionId, eventId, epicrisActionTypeId):
        self.actionId = actionId if actionId else 0
        tableAction = QtGui.qApp.db.table('Action')
        rec = QtGui.qApp.db.getRecordEx(tableAction, 'id', 'id = %s' % self.actionId)
        if not rec:
            actRec = tableAction.newRecord()
            actRec.setValue('actionType_id', toVariant(epicrisActionTypeId))
            actRec.setValue('event_id', toVariant(eventId))
            actRec.setValue('begDate', toVariant(QtCore.QDateTime.currentDateTime()))
            self.actionId = QtGui.qApp.db.insertRecord(tableAction, actRec)

    # Запись эпикриза
    def setEpicris(self, epicrisDict):
        tableAction = QtGui.qApp.db.table('Action')
        tableEpicris = QtGui.qApp.db.table('Epicrisis')
        actId = QtGui.qApp.db.getRecordEx(tableAction, 'id', 'id = %s' % self.actionId)
        checkRec = QtGui.qApp.db.getRecordEx(tableEpicris, '*', 'id = %s' % self.actionId)
        if actId:
            if checkRec:
                checkRec.setValue('personId', toVariant(epicrisDict['person']))
                checkRec.setValue('name', toVariant(epicrisDict['name']))
                checkRec.setValue('code', toVariant(epicrisDict['code']))
                checkRec.setValue('id_orgStructure', toVariant(epicrisDict['orgstruct']))
                checkRec.setValue('createDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
                checkRec.setValue('event_id', toVariant(epicrisDict['eventid']))
                checkRec.setValue('printTemplate', toVariant(epicrisDict['printtemplate']))
                checkRec.setValue('type', toVariant(epicrisDict['type']))
                QtGui.qApp.db.updateRecord(tableEpicris, checkRec)
            else:
                rec = tableEpicris.newRecord()
                rec.setValue('id', toVariant(actId.value('id')))
                rec.setValue('personId', toVariant(epicrisDict['person']))
                rec.setValue('name', toVariant(epicrisDict['name']))
                rec.setValue('code', toVariant(epicrisDict['code']))
                rec.setValue('id_orgStructure', toVariant(epicrisDict['orgstruct']))
                rec.setValue('createDatetime', toVariant(QtCore.QDateTime.currentDateTime()))
                rec.setValue('event_id', toVariant(epicrisDict['eventid']))
                rec.setValue('printTemplate', toVariant(epicrisDict['printtemplate']))
                rec.setValue('type', toVariant(epicrisDict['type']))
                QtGui.qApp.db.insertRecord(tableEpicris, rec)

    # Запись раздела
    def setSection(self, sectionDict):
        tableSection = QtGui.qApp.db.table('EpicrisisSections')
        checkRec = QtGui.qApp.db.getRecordEx(tableSection, '*',
                                       'id = %s AND name = \'%s\'' % (self.actionId, sectionDict['name']))
        if checkRec:
            QtGui.qApp.db.deleteRecord(tableSection, 'id = %s AND name = \'%s\'' % (
                self.actionId, forceString(checkRec.value('name'))))
        actRec = QtGui.qApp.db.getRecordEx('Action', 'id', 'id = %s' % self.actionId)
        if actRec:
            rec = tableSection.newRecord()
            rec.setValue('id', toVariant(actRec.value('id')))
            rec.setValue('name', toVariant(sectionDict['name']))
            rec.setValue('id_rbEpicrisSections', toVariant(sectionDict['htmltemplate']))
            rec.setValue('idx', toVariant(sectionDict['idx']))
            rec.setValue('isRequired', toVariant(sectionDict['required']))
            rec.setValue('isEditable', toVariant(sectionDict['editable']))
            rec.setValue('description', toVariant(sectionDict['description']))
            QtGui.qApp.db.insertRecord(tableSection, rec)

    # запись проперти
    def setProperty(self, propertyDict):
        tableProperty = QtGui.qApp.db.table('EpicrisisProperty')
        tablePropertyTable = QtGui.qApp.db.table('EpicrisisProperty_Table')
        propertyRecs = []
        for prop in propertyDict:
            checkRec = QtGui.qApp.db.getRecordEx(tableProperty, '*', [tableProperty['id'].eq(self.actionId),
                                                                tableProperty['name'].eq(prop['name']),
                                                                tableProperty['idx_section'].eq(
                                                                    prop['sectioncount']),
                                                                tableProperty['type'].eq(prop['type'])])
            if checkRec:
                QtGui.qApp.db.deleteRecord(tableProperty,
                                     [tableProperty['id'].eq(self.actionId), tableProperty['name'].eq(prop['name']),
                                      tableProperty['idx_section'].eq(prop['sectioncount']),
                                      tableProperty['type'].eq(prop['type'])])
            actRec = QtGui.qApp.db.getRecordEx('Action', 'id', 'id = %s' % self.actionId)
            if actRec:
                if prop['type'].upper() == 'TABLE':
                    rec = tableProperty.newRecord()
                    rec.setValue('id', toVariant(actRec.value('id')))
                    rec.setValue('name', toVariant(prop['name']))
                    rec.setValue('type', toVariant(prop['type']))
                    rec.setValue('defaultValue', toVariant(len(prop['value'])))
                    rec.setValue('guid_epic', toVariant(self.actionId))
                    rec.setValue('idx_section', toVariant(prop['sectioncount']))
                    rec.setValue('htmlTemplate', toVariant(prop['htmltemplate']))
                    rec.setValue('valueDomain', toVariant(prop['domain']))
                    rec.setValue('orgStruct', toVariant(prop['orgstruct']))
                    rec.setValue('isRequired', toVariant(prop['required']))
                    rec.setValue('isEditable', toVariant(prop['editable']))
                    rec.setValue('description', toVariant(prop['description']))
                    QtGui.qApp.db.insertRecord(tableProperty, rec)
                    rec = QtGui.qApp.db.getRecordEx(tableProperty, u'idTable', u'idx_section = %s AND id = %s AND name = \'%s\' AND type = \'%s\'' % (
                        prop['sectioncount'], forceString(actRec.value('id')), forceString(prop['name']), forceString(prop['type'])))
                    if rec:
                        countIdx = 0
                        propertyTableRecs = []
                        for v in prop['value']:
                            record = tablePropertyTable.newRecord()
                            record.setValue('id', toVariant(rec.value('idTable')))
                            record.setValue('idx_property', toVariant(countIdx))
                            record.setValue('value', toVariant(v))
                            propertyTableRecs.append(record)
                            countIdx += 1
                        if propertyTableRecs:
                            QtGui.qApp.db.insertMultipleRecords(tablePropertyTable, propertyTableRecs)
                else:
                    rec = tableProperty.newRecord()
                    rec.setValue('id', toVariant(actRec.value('id')))
                    rec.setValue('name', toVariant(prop['name']))
                    rec.setValue('type', toVariant(prop['type']))
                    rec.setValue('defaultValue', toVariant(prop['value']))
                    rec.setValue('guid_epic', toVariant(self.actionId))
                    rec.setValue('idx_section', toVariant(prop['sectioncount']))
                    rec.setValue('htmlTemplate', toVariant(prop['htmltemplate']))
                    rec.setValue('valueDomain', toVariant(prop['domain']))
                    rec.setValue('orgStruct', toVariant(prop['orgstruct']))
                    rec.setValue('isRequired', toVariant(prop['required']))
                    rec.setValue('isEditable', toVariant(prop['editable']))
                    rec.setValue('description', toVariant(prop['description']))
                    propertyRecs.append(rec)
        if propertyRecs:
            QtGui.qApp.db.insertMultipleRecords(tableProperty, propertyRecs)

    # Пометка на удаление
    def delEpicris(self, id):
        record = QtGui.qApp.db.getRecordEx('Action', '*', 'id = %s' % forceString(id))
        recordEpic = QtGui.qApp.db.getRecordEx('Epicrisis', '*', 'id = %s' % forceString(id))
        if record:
            record.setValue('deleted', 1)
            QtGui.qApp.db.updateRecord('Action', record)
        if recordEpic:
            recordEpic.setValue('isDelete', 1)
            QtGui.qApp.db.updateRecord('Epicrisis', recordEpic)

    # Парсинг XML для записи готового эпикриза
    def setDoc(self, docum):
        tmp = docum
        doc = QDomDocument()
        if not doc.setContent(tmp):
            return
        root = doc.documentElement()
        epicList = root.firstChild()
        while not epicList.isNull():
            epicrisElement = epicList.toElement()
            if epicrisElement:
                self.actionId = forceString(epicrisElement.firstChildElement('ACTION_ID').text())
                epicrisPerson = forceString(epicrisElement.firstChildElement('PERSON').text())
                epicrisName = forceString(epicrisElement.firstChildElement('NAME').text())
                epicrisCode = forceString(epicrisElement.firstChildElement('CODE').text())
                epicrisEventId = forceString(epicrisElement.firstChildElement('EVENT_ID').text())
                epicrisActionTypeId = forceString(epicrisElement.firstChildElement('ACTIONTYPE_ID').text())
                epicrisOrgStruct = forceString(epicrisElement.firstChildElement('ORG_STRUCT').text())
                epicrisPrintTemplate = forceString(epicrisElement.firstChildElement('PRINTTEMPLATE').text())
                epicrisType = forceString(epicrisElement.firstChildElement('TYPE').text())
                self.setAction(self.actionId, epicrisEventId, epicrisActionTypeId)
                sectionList = epicrisElement.firstChildElement('SECTIONS')
                sectionCount = 0
                while not sectionList.isNull():
                    sectionCount += 1
                    sectionElement = sectionList.toElement()
                    sectionName = forceString(sectionElement.firstChildElement('NAME').text())
                    sectionHtml = forceString(sectionElement.firstChildElement('HTMLTEMPLATE').text())
                    sectionIsEditable = forceString(sectionElement.firstChildElement('ISEDITABLE').text())
                    sectionIsRequired = forceString(sectionElement.firstChildElement('ISREQUIRED').text())
                    sectionDescription = forceString(sectionElement.firstChildElement('DESCRIPTION').text())
                    propertyList = sectionElement.firstChildElement('PROPERTYES')
                    propertyForSave = []
                    while not propertyList.isNull():
                        propertyElement = propertyList.toElement()
                        propertyName = forceString(propertyElement.firstChildElement('NAME').text())
                        propertyType = forceString(propertyElement.firstChildElement('TYPE').text())
                        if propertyType.upper() == 'TABLE':
                            listValues = propertyElement.firstChildElement('VALUE')
                            propertyDefaultValue = []
                            row = listValues.firstChildElement('ROW')
                            while not row.isNull():
                                rowElem = row.toElement()
                                propertyDefaultValue.append(forceString(rowElem.text()))
                                row = row.nextSibling()
                        else:
                            propertyDefaultValue = forceString(propertyElement.firstChildElement('VALUE').text())
                        propertyHtmlTemplate = forceString(propertyElement.firstChildElement('HTMLTEMPLATE').text())
                        propertyDomain = forceString(propertyElement.firstChildElement('DOMAIN').text())
                        propertyOrgStruct = forceString(propertyElement.firstChildElement('ORG_STRUCT').text())
                        propertyRequred = forceString(propertyElement.firstChildElement('ISREQUIRED').text())
                        propertyEditable = forceString(propertyElement.firstChildElement('ISEDITABLE').text())
                        propertyDescription = forceString(propertyElement.firstChildElement('DESCRIPTION').text())
                        propertyDict = {
                            'name': propertyName,
                            'type': propertyType,
                            'value': propertyDefaultValue,
                            'htmltemplate': propertyHtmlTemplate,
                            'domain': propertyDomain,
                            'orgstruct': propertyOrgStruct,
                            'required': propertyRequred,
                            'sectioncount': sectionCount,
                            'eventid': epicrisEventId,
                            'actiontypeid': epicrisActionTypeId,
                            'editable': propertyEditable,
                            'description': propertyDescription
                        }
                        propertyForSave.append(propertyDict)
                        propertyList = propertyList.nextSibling()
                    if propertyForSave:
                        self.setProperty(propertyForSave)
                    sectionDict = {
                        'name': sectionName,
                        'idx': sectionCount,
                        'htmltemplate': sectionHtml,
                        'editable': sectionIsEditable,
                        'required': sectionIsRequired,
                        'description': sectionDescription
                    }
                    self.setSection(sectionDict)
                    sectionList = sectionList.nextSibling()
                epicrisDict = {
                    'person': epicrisPerson,
                    'name': epicrisName,
                    'code': epicrisCode,
                    'orgstruct': epicrisOrgStruct,
                    'eventid': epicrisEventId,
                    'printtemplate': epicrisPrintTemplate,
                    'type': epicrisType,
                }
                self.setEpicris(epicrisDict)
                epicList = epicList.nextSibling()

    # Получение списка эпикризов по ид евента
    def getEpicrisListByEventId(self, eventId, personId = None, orgStructId = None):
        tblOrgStruct = QtGui.qApp.db.table('OrgStructure')
        doc = CXMLHelper.createDomDocument(rootElementName='EPICRISLIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        query = QtGui.qApp.db.query('SELECT * FROM `Epicrisis` WHERE event_id = %s AND isDelete = 0' % eventId)
        mkb, diagName = self.getDiagnosisAndMKBByEvent(eventId)
        while query.next():
            recEpic = query.record()
            isDeletable = 'False'
            if forceInt(personId) == forceInt(recEpic.value('personId')) or \
                            forceInt(QtGui.qApp.db.translate(tblOrgStruct, tblOrgStruct['id'],
                                                       forceInt(orgStructId),
                                                       tblOrgStruct['chief_id'])) == forceInt(personId):
                isDeletable = 'True'
            epicRoot = CXMLHelper.addElement(rootElement, 'EPICRIS')
            tblEpicSections = QtGui.qApp.db.table('EpicrisisSections')
            recSecionsList = QtGui.qApp.db.getRecordList(tblEpicSections, tblEpicSections['id'], tblEpicSections['id'].eq(forceString(recEpic.value('id'))))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'ID'), forceString(recEpic.value('id')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'NAME'), forceString(recEpic.value('name')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'CODE'), forceString(recEpic.value('code')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'ORG_STRUCT'),
                                forceString(recEpic.value('id_orgStructure')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'PRINTTEMPLATE'),
                                forceString(recEpic.value('printTemplate')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'CREATEDATE'),
                                forceString(recEpic.value('createDatetime')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'DELETABLE'), forceString(isDeletable))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'TYPE'), forceString(recEpic.value('type')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'MKB'), forceString(mkb))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'DIAGNAME'), forceString(diagName))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'ISNULL'), '0' if recSecionsList else '1')
        return doc

    def getEpicrisIdListByEventId(self, eventId):
        return QtGui.qApp.db.getIdList(stmt='SELECT * FROM `Epicrisis` WHERE event_id = %s AND isDelete = 0' % eventId)

    # Получение эпикриза по Action_id
    def getEpicrisListByActionId(self, actionId):
        doc = CXMLHelper.createDomDocument(rootElementName='EPICRISLIST', encoding=self.encoding)
        rootElement = CXMLHelper.getRootElement(doc)
        queryEpic = QtGui.qApp.db.query('SELECT * FROM Epicrisis WHERE id = %s AND isDelete = 0' % actionId)
        querySect = QtGui.qApp.db.query('SELECT * FROM EpicrisisSections WHERE id = %s ORDER BY idx' % actionId)
        while queryEpic.next():
            recEpic = queryEpic.record()
            epicRoot = CXMLHelper.addElement(rootElement, 'EPICRIS')
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'ID'), forceString(recEpic.value('id')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'NAME'), forceString(recEpic.value('name')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'CODE'), forceString(recEpic.value('code')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'ORG_STRUCT'), forceString(recEpic.value('id_orgStructure')))
            printTemplate = QtGui.qApp.db.getRecordEx('rbEpicrisisTemplates', 'printTemplate',
                                                'id = %s' % forceString(recEpic.value('printTemplate')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'PRINTTEMPLATE_ID'), forceString(recEpic.value('printTemplate')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'PRINTTEMPLATE'),
                                forceString(printTemplate.value('printTemplate')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'CREATEDATE'), forceString(recEpic.value('createDatetime')))
            CXMLHelper.setValue(CXMLHelper.addElement(epicRoot, 'TYPE'), forceString(recEpic.value('type')))
            while querySect.next():
                query_sect_rec = querySect.record()
                htmlTemplate = QtGui.qApp.db.getRecordEx('rbEpicrisisTemplates_rbEpicrisisSections', 'htmlTemplate',
                                                   'id_rbEpicrisisSections = %s' % forceString(query_sect_rec.value('id_rbEpicrisSections')))
                if htmlTemplate:
                    sectRoot = CXMLHelper.addElement(epicRoot, 'SECTION')
                    CXMLHelper.setValue(CXMLHelper.addElement(sectRoot, 'ID'), forceString(query_sect_rec.value('id_rbEpicrisSections')))
                    CXMLHelper.setValue(CXMLHelper.addElement(sectRoot, 'NAME'), forceString(query_sect_rec.value('name')))
                    CXMLHelper.setValue(CXMLHelper.addElement(sectRoot, 'HTMLTEMPLATE'),
                                        forceString(htmlTemplate.value('htmlTemplate')))
                    CXMLHelper.setValue(CXMLHelper.addElement(sectRoot, 'ISEDITABLE'), forceString(query_sect_rec.value('isEditable')))
                    CXMLHelper.setValue(CXMLHelper.addElement(sectRoot, 'ISREQUIRED'), forceString(query_sect_rec.value('isRequired')))
                    CXMLHelper.setValue(CXMLHelper.addElement(sectRoot, 'DESCRIPTION'), forceString(query_sect_rec.value('description')))
                    queryProp = QtGui.qApp.db.query('SELECT * FROM EpicrisisProperty WHERE id = %s AND idx_section = %s' % (
                        actionId, forceString(query_sect_rec.value('idx'))))
                    while queryProp.next():
                        query_prop_record = queryProp.record()
                        htmlTemplate = QtGui.qApp.db.getRecordEx('rbEpicrisisSections_rbEpicrisisProperty', 'htmlTemplate',
                                                           'id_rbEpicrisisProperty = %s' % forceString(
                                                               query_prop_record.value('htmltemplate')))
                        if htmlTemplate:
                            propRoot = CXMLHelper.addElement(sectRoot, 'PROPERTY')
                            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'ID'), forceString(queryProp.value(5))) # какой ид?s
                            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'NAME'),
                                                forceString(query_prop_record.value('name')))
                            CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'TYPE'),
                                                forceString(query_prop_record.value('type')))

                            if forceString(query_prop_record.value('type')).upper() == 'TABLE':
                                CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'HTMLTEMPLATE'),
                                                    forceString(htmlTemplate.value('htmlTemplate')))
                                queryValues = QtGui.qApp.db.query(
                                    'SELECT * FROM `EpicrisisProperty_Table` WHERE id = %s' % forceString(
                                        query_prop_record.value('idTable')))
                                while queryValues.next():
                                    values_record = queryValues.record()
                                    CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'VALUE'),
                                                        forceString(values_record.value('value')))

                            else:
                                CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'VALUE'),
                                                    forceString(query_prop_record.value('defaultValue')))
                                CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'HTMLTEMPLATE'),
                                                    forceString(htmlTemplate.value('htmlTemplate')))
                                CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'DOMAIN'),
                                                    forceString(query_prop_record.value('valueDomain')))
                                CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'ORG_STRUCT'),
                                                    forceString(query_prop_record.value('orgStruct')))
                                CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'ISREQUIRED'),
                                                    forceString(query_prop_record.value('isRequired')))
                                CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'ISEDITABLE'),
                                                    forceString(query_prop_record.value('isEditable')))
                                CXMLHelper.setValue(CXMLHelper.addElement(propRoot, 'DESCRIPTION'),
                                                    forceString(query_prop_record.value('description')))
        return doc


def getEpicrisXML(epicrisId, eventId):
    doc = EpicrisTemplates()
    document = doc.getEpicrisTemplate(epicrisId, eventId)
    return forceString(document.toString())


def setEpicrisXML(file):
    doc = Epicris()
    doc.setDoc(file.encode(u'UTF-8'))


def addEpicrisTemplate(file):
    doc = EpicrisTemplates()
    doc.addEpicrisTemplate(file.encode(u'UTF-8'))


def modifyEpicrisTemplate(file):
    doc = EpicrisTemplates()
    doc.addEpicrisTemplate(file.encode(u'UTF-8'), True)


def addSectionTemplate(file):
    doc = EpicrisTemplates()
    doc.addSectionsTemplate(file.encode(u'UTF-8'))


def modifySectionTemplate(file):
    doc = EpicrisTemplates()
    doc.addSectionsTemplate(file.encode(u'UTF-8'), True)


def addPropertyTemplate(file):
    doc = EpicrisTemplates()
    doc.addPropertyTemplate(file.encode(u'UTF-8'))


def modifyPropertyTemplate(file):
    doc = EpicrisTemplates()
    doc.addPropertyTemplate(file.encode(u'UTF-8'), True)


def getEpicrisTemplatiesList():
    doc = EpicrisTemplates()
    document = doc.getEpicrisList()
    return forceString(document.toString())


def getSectionsTemplatiesList():
    doc = EpicrisTemplates()
    document = doc.getSectonsList()
    return forceString(document.toString())


def getEpicrisTemplateSectionsList(idTemplate):
    doc = EpicrisTemplates()
    document = doc.getSectionsByTemplate(idTemplate)
    return forceString(document.toString())


def getPropertyesTemplatiesList(printAsTable=None):
    doc = EpicrisTemplates()
    document = doc.getPropertyesList(printAsTable)
    return forceString(document.toString())

def getPropertyTypesList():
    doc = EpicrisTemplates()
    document = doc.getPropertyTypesList()
    return forceString(document.toString())


def getSectionsPropertyList(idSection):
    doc = EpicrisTemplates()
    document = doc.getPropertyesListBySection(idSection)
    return forceString(document.toString())


def getEpicrisListByEvent(eventId, personId = None, orgStructId = None):
    doc = Epicris()
    document = doc.getEpicrisListByEventId(eventId, personId, orgStructId)
    return forceString(document.toString())


def getEpicrisIdListByEventId(eventId):
    doc = Epicris()
    return doc.getEpicrisIdListByEventId(eventId)


def getEpicrisListByOrgStruct(orgStruct):
    doc = EpicrisTemplates()
    document = doc.getEpicrisTemplatesListByOrgStruct(orgStruct)
    return forceString(document.toString())


def getEpicrisByAction(id):
    doc = Epicris()
    document = doc.getEpicrisListByActionId(id)
    return forceString(document.toString())


def getPropertyTemplateValueById(eventId, propId, someId, orgStruct_id=None):
    doc = EpicrisTemplates()
    document = doc.getPropertyTemplateById(eventId, propId, someId, orgStruct_id)
    return forceString(document.toString())


def getSectionById(id):
    doc = EpicrisTemplates()
    document = doc.getSectionById(id)
    return forceString(document.toString())


def getPropertyById(id):
    doc = EpicrisTemplates()
    document = doc.getPropertyById(id)
    return forceString(document.toString())

def addStoredProperty(propId, propValue, propOrgStruct):
    doc = EpicrisTemplates()
    doc.addStoredProperty(propId, propValue, propOrgStruct)

def formatProperty(file):
    doc = EpicrisTemplates()
    doc.formatProperty(file.encode(u'UTF-8'))

def formatSection(file):
    doc = EpicrisTemplates()
    doc.formatSection(file.encode(u'UTF-8'))

def delElement(file):
    doc = EpicrisTemplates()
    doc.delElement(file.encode(u'UTF-8'))

def delEpicris(id):
    doc = Epicris()
    doc.delEpicris(id)

def delStoredProperty(id):
    doc = EpicrisTemplates()
    doc.deleteStoredProperty(id)

def getHtmlbyXML(xml):
    doc = Epicris()
    document = doc.getHtmlbyXML(xml.encode(u'UTF-8'))
    return forceString(document)

def create_multiple_epicrisis(event_id):
    u"""
    Создание эпикризов по event_id
    Существующие пропускаются
    Поиск существующих ведется по event_id и printTemplate
    """
    QtGui.qApp.db.transaction()
    DEFAULT_ACTION_TYPE_ID = 11122

    template_query = QtGui.qApp.db.query('SELECT * FROM `rbEpicrisisTemplates`')

    et = EpicrisTemplates()
    while template_query.next():
        template_record = template_query.record()
        t_id = forceInt(template_record.value('id'))
        template_has_props = False
        epicris_exists = QtGui.qApp.db.getRecordEx('Epicrisis', '*', 'event_id = %d and printTemplate = %d' % (event_id, t_id))
        if epicris_exists:
            continue

        sections_to_save = []
        props_to_save = []

        section_ids = QtGui.qApp.db.getIdList(stmt=stmts.STMT_Sections % t_id)
        for s_id in section_ids:
            section_has_props = False
            section_record = QtGui.qApp.db.getRecordEx('rbEpicrisisSections', '*', 'id = %d' % s_id)
            section_record_extra = QtGui.qApp.db.getRecordEx('rbEpicrisisTemplates_rbEpicrisisSections',
                                                      'htmlTemplate, isRequired, isEditable, idx',
                                                      'id_rbEpicrisisTemplates = %s AND id_rbEpicrisisSections = %s' % (t_id, s_id))

            section_dict = {
                'name': forceString(section_record.value('name')),
                'htmltemplate': s_id,
                'idx': forceInt(section_record_extra.value('idx')),
                'required': forceInt(section_record_extra.value('isRequired')),
                'editable': forceInt(section_record_extra.value('isEditable')),
                'description': forceString(section_record.value('description')),
            }

            props_query_extra = QtGui.qApp.db.query(
                'SELECT * FROM rbEpicrisisSections_rbEpicrisisProperty WHERE id_rbEpicrisisSections = %s' % s_id)
            while props_query_extra.next():
                props_record_extra = props_query_extra.record()
                p_id = forceInt(props_record_extra.value('id_rbEpicrisisProperty'))
                props_record = QtGui.qApp.db.getRecordEx('rbEpicrisisProperty', '*', 'id = %d' % p_id)

                value_query = et.getQueryResult(forceString(props_record.value('defaultValue')),event_id)[0]

                value = None
                type = None
                if (value_query.size() == 0):
                    continue

                value_record = None
                if (value_query.size() == 1):
                    if value_query.first():
                        value_record = value_query.record()
                        column_count = value_record.count()
                        if (column_count > 1):
                            type = 'Table'
                        else:
                            type = 'String'
                else:
                    type = 'Table'

                if type == 'String':
                    value = forceString(value_query.record().value(0))
                    if not value:
                        value = None
                    else:
                        template_has_props = section_has_props = True

                if type == 'Table':
                    value_record = value_query.record()
                    column_count = value_record.count()

                    template_has_props = section_has_props = True
                    value = []

                    v = []
                    v2 = []
                    for i in range(0, column_count):
                        v.append(forceString(value_record.fieldName(i)))
                        v2.append(forceString(value_record.value(i)))
                    value.append('#'.join(v))
                    value.append('#'.join(v2))

                    # все, что после первой строки ранее
                    while value_query.next():
                        value_record = value_query.record()

                        v = []
                        for i in range(0, column_count):
                            v.append(forceString(value_record.value(i)))
                        value.append('#'.join(v))

                if value != None:
                    prop_dict= {
                        'name': forceString(props_record.value('name')),
                        'type': type,
                        'value': value,
                        'sectioncount': section_dict['idx'],
                        'htmltemplate': p_id,
                        'domain': forceString(props_record.value('valueDomain')),
                        'orgstruct': None,
                        'required': forceInt(props_record_extra.value('isRequired')),
                        'editable': forceInt(props_record_extra.value('isEditable')),
                        'description': forceString(props_record.value('description'))
                    }
                    props_to_save.append(prop_dict)

            if section_has_props:
                sections_to_save.append(section_dict)

        if template_has_props:
            epicris_dict = {
                'person': None,
                'orgstruct': None,
                'name': forceString(template_record.value('name')),
                'code': forceInt(template_record.value('code')),
                'eventid': event_id,
                'printtemplate': t_id,
                'type': forceInt(template_record.value('type'))
            }

            e = Epicris()
            e.setAction(actionId=None, eventId=event_id, epicrisActionTypeId=DEFAULT_ACTION_TYPE_ID)
            e.setEpicris(epicris_dict)

            for s in sections_to_save:
                e.setSection(s)
            for p in props_to_save:
                e.setProperty(p)

    QtGui.qApp.db.commit()


def main():
    # /home/vladimir/work/s11/s11mainConsole.py
    from s11mainConsole import CS11MainConsoleApp
    from library.database import connectDataBaseByInfo
    import sys
    config = {
        'driverName': 'mysql',
        'host': 'p51vm',
        'port': 3306,
        'database': 's11',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp = CS11MainConsoleApp(sys.argv, config)
    db = connectDataBaseByInfo(config)
    QtGui.qApp.db = db
    #
    # create_multiple_epicrisis(8223946)
    # create_multiple_epicrisis(8224153)
    pass

if __name__ == '__main__':
    main()
