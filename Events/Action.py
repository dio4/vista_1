# -*- coding: utf-8 -*-
u"""
Описание объекта Action и его свойств
"""
import copy
import tempfile
from PyQt4 import QtCore, QtGui, QtSql

from Blank.BlankComboBox import CBlankComboBoxActions
from Events.Utils import getEventContextData
from Exchange.alfalab.service import CAlfalabService
from Exchange.alfalab.types import ReferralQuery
from Exchange.alfalab.utils import CAlfalabException
from HospitalBeds.HospitalBedFindComboBox import CHospitalBedFindComboBox
from MultipleMKBDialog import CMultipleMKBDialog
from Orgs.OrgComboBox import COrgComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.Orgs import selectOrganisation
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from Orgs.PersonInfo import CPersonInfo
from Orgs.Utils import COrgInfo, COrgStructureInfo, getOrgStructureFullName, getOrganisationShortName, getPersonChiefs
from Quoting.ClientQuotingComboBox import CClientQuotingComboBox
from Quoting.QuotaTypeComboBox import CClientQuotingModelPatientComboBox
from Registry.Utils import CClientQuotaInfo, personIdToText
from Resources.JobTicketChooser import CJobTicketChooserComboBox
from Resources.Utils import JobTicketStatus
from TissueJournal.TissueInfo import CTissueTypeInfo
from Users.Rights import urDefaultJobTickets, urEditJobTicket, urEditOtherPeopleAction
from library.AgeSelector import checkAgeSelector, parseAgeSelector
from library.Counter import getDocumentNumber
from library.DateEdit import CDateEdit
from library.DbEntityCache import CDbEntityCache
from library.Enum import CEnum
from library.ImageProcDialog import CImageProcDialog
from library.ItemListModel import CItemAttribCol, CItemListModel
from library.ItemListView import CItemListView
from library.LoggingModule.Logger import getLoggerDbName
from library.PrintInfo import CDateInfo, CInfo, CRBInfo, CTimeInfo
from library.RLS.RLSComboBox import CRLSComboBox
from library.RLS.RLSExtendedEditor import CRLSExtendedEditor, CRLSExtendedVectorEditor
from library.RLS.RLSInfo import CRLSInfo, CRLSExtendedInfo
from library.StrComboBox import CDoubleComboBox, CIntComboBox, CStrComboBox
from library.TreeModel import CDBTreeItem, CDBTreeModel
from library.Utils import CCustomContextMenuManager, forceBool, forceDate, forceDateTime, forceDouble, forceInt, \
    forceRef, \
    forceString, forceStringEx, forceTr, formatNum1, pyDate, smartDict, toVariant
from library.angel import CAngelDialog
from library.crbcombobox import CRBComboBox, CRBModelDataCache


class ActionClass:
    u""" ActionType.class """

    Status = 0
    Diagnostic = 1
    Cure = 2
    Misc = 3
    Analyses = 4

    All = [Status, Diagnostic, Cure, Misc, Analyses]

    nameMap = {
        Status    : u'Статус',
        Diagnostic: u'Диагностика',
        Cure      : u'Лечение',
        Misc      : u'Мероприятия',
        Analyses  : u'Анализы'
    }
    nameList = [nameMap[k] for k in sorted(nameMap.keys())]


class ActionStatus:
    u""" Action.status """

    Started = 0
    Awaiting = 1
    Done = 2
    Cancelled = 3
    WithoutResult = 4
    Appointed = 5
    NotProvided = 6
    NotDoneByMedicalReasons = 7
    NotDoneByOtherReasons = 8
    PatientRefused = 9
    DoneOnTime = 10
    DoneWhilstClinicalExamination = 11

    nameMap = {
        Started                      : u'Начато',
        Awaiting                     : u'Ожидание',
        Done                         : u'Закончено',
        Cancelled                    : u'Отменено',
        WithoutResult                : u'Без результата',
        Appointed                    : u'Назначено',
        NotProvided                  : u'Не предусмотрено',
        # Используются в выгрузкках:
        NotDoneByMedicalReasons      : u'Не выполнено по мед. противопоказаниям',
        NotDoneByOtherReasons        : u'Не выполнено по прочим причинам',
        PatientRefused               : u'Пациент отказался от услуги (документированный отказ)',
        DoneOnTime                   : u'Выполнено в пределах установленных сроков (для ДД)',
        DoneWhilstClinicalExamination: u'Выполнено при проведении диспансеризации (для ДД)'
    }
    nameList = [nameMap[k] for k in sorted(nameMap.keys())]


class ActionServiceType(CEnum):
    u""" Тип услуги (ActionType.serviceType) """
    Other = 0
    PrimaryVisit = 1
    SecondaryVisit = 2
    Procedure = 3
    Operation = 4
    Examination = 5
    Cure = 6

    nameMap = {
        Other         : u'Прочие',
        PrimaryVisit  : u'Первичный осмотр',
        SecondaryVisit: u'Повторный осмотр',
        Procedure     : u'Процедура/манипуляция',
        Operation     : u'Операция',
        Examination   : u'Исследование',
        Cure          : u'Лечение'
    }


class ActionPropertyCopyModifier(CEnum):
    u""" ActionPropertyType.copyModifier """
    NoCopy = 0
    Concat = 1
    Last = 2
    Merge = 3

    nameMap = {
        NoCopy: u'Не копировать',
        Concat: u'Копировать с конкатенацией',
        Last  : u'Копировать последнее',
        Merge : u'Копировать, при возникновении конфликта выбирать вручную'
    }


class CActionPropertyValueTypeRegistry(object):
    # вспомогательное средство для создания CActionPropertyValueType по имени/обл.определения
    nameList = []
    mapNameToValueType = {}
    cache = {}

    @classmethod
    def register(cls, type_):
        cls.nameList.append(type_.name)
        cls.mapNameToValueType[type_.name.lower()] = type_

    @classmethod
    def normTypeName(cls, name):
        type_ = cls.mapNameToValueType.get(name.lower(), None)
        if type_:
            return type_.name
        else:
            return name

    @classmethod
    def get(cls, typeName, domain, my_name):
        name = typeName.lower()
        key = (name, domain, my_name)
        if key in cls.cache:
            result = cls.cache[key]
        else:
            if (typeName == 'String'):
                result = cls.mapNameToValueType[name](domain, my_name)
            else:
                result = cls.mapNameToValueType[name](domain)
            cls.cache[key] = result
        return result


class CActionPropertyValueType(object):
    tableNamePrefix = 'ActionProperty_'
    prefferedHeight = 1
    prefferedHeightUnit = 1
    isCopyable = True
    isHtml = False
    customSaveLoad = False

    def __init__(self, domain=None):
        self.domain = domain
        self.tableName = self.getTableName()

    def getTableName(self):
        return self.tableNamePrefix + self.name

    @staticmethod
    def convertPyValueToQVariant(value):
        return toVariant(value)

    @staticmethod
    def convertSpecialText(value):
        return value

    def getEditorClass(self, isVector=False):
        return self.CPropEditor

    def toText(self, v):
        return forceString(v)

    def toImage(self, v):
        return None

    def toInfo(self, context, v):
        return forceString(v) if v else ''

    def getPresetValue(self):
        return None

    def saveValues(self, propertyId, values):
        pass

    def loadValues(self, propertId):
        return []


class CDoubleActionPropertyValueType(CActionPropertyValueType):
    name = 'Double'
    variantType = QtCore.QVariant.Double

    class CPropEditor(QtGui.QLineEdit):
        def __init__(self, action, domain, parent, clientId):
            QtGui.QLineEdit.__init__(self, parent)
            self._validator = QtGui.QDoubleValidator(self)
            self.setValidator(self._validator)

        def setValue(self, value):
            v = forceDouble(value)
            self.setText(str(v))

        def value(self):
            return self.text().toDouble()[0]

    class CComboBoxPropEditor(CDoubleComboBox):
        def __init__(self, action, domain, parent, clientId):
            CDoubleComboBox.__init__(self, parent)
            self.setDomain(domain)

        def setValue(self, value):
            v = forceDouble(value)
            CDoubleComboBox.setValue(self, str(v))

        def value(self):
            return CDoubleComboBox.value(self).toDouble()[0]

    @staticmethod
    def convertQVariantToPyValue(value):
        return value.toDouble()[0]

    def toInfo(self, context, v):
        return v if v else 0.0

    def getEditorClass(self, isVector=False):
        if self.domain:
            return self.CComboBoxPropEditor
        else:
            return self.CPropEditor


class CIntegerActionPropertyValueType(CActionPropertyValueType):
    name = 'Integer'
    variantType = QtCore.QVariant.Int

    class CPropEditor(QtGui.QLineEdit):
        def __init__(self, action, domain, parent, clientId):
            QtGui.QLineEdit.__init__(self, parent)
            self._validator = QtGui.QIntValidator(self)
            self.setValidator(self._validator)

        def setValue(self, value):
            v = forceInt(value)
            self.setText(str(v))

        def value(self):
            return self.text().toInt()[0]

    class CComboBoxPropEditor(CIntComboBox):
        def __init__(self, action, domain, parent, clientId):
            CIntComboBox.__init__(self, parent)
            self.setDomain(domain)

        def setValue(self, value):
            v = forceDouble(value)
            CIntComboBox.setValue(self, str(v))

        def value(self):
            return CIntComboBox.value(self).toDouble()[0]

    def getEditorClass(self, isVector=False):
        if self.domain:
            return self.CComboBoxPropEditor
        else:
            return self.CPropEditor

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceInt(value)

    def toInfo(self, context, v):
        return v if v else 0


class CStringActionPropertyValueType(CActionPropertyValueType):
    name = 'String'
    variantType = QtCore.QVariant.String

    class CPlainPropEditor(QtGui.QLineEdit):
        def __init__(self, action, domain, parent, clientId):
            QtGui.QLineEdit.__init__(self, parent)
            self._customContextManager = CCustomContextMenuManager()
            self._customContextManager.configureWidget(self)

        def setValue(self, value):
            v = forceString(value)
            self.setText(v)

        def value(self):
            return unicode(self.text())

    class CComboBoxPropEditor(CStrComboBox):
        def __init__(self, action, domain, parent, clientId):
            CStrComboBox.__init__(self, parent)
            self.setDomain(domain)

    def __init__(self, domain, my_name):
        CActionPropertyValueType.__init__(self, domain)
        self.my_name = my_name

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    # actionType_id's: Индивидуальная карта/Лист обследования
    # actionProperty: Терапевт, ЛОР, окулист, стоматолог / Осложнения данной беременности, экстрагенитальныe заболевания
    # actionType_id 23944, id 3658 Экстрагенитальные заболевания
    # 3657 - Осложнения данной беременности
    # actionType_id 700, id 3787 Терапевт
    # 3788 - ЛОР
    # 3789 - Окулист
    # 3790 - Стоматолог

    def getEditorClass(self, isVector=False):
        names = [u'Экстрагенитальные заболевания (диагноз)', u'Осложнения данной беременности', u'Терапевт', u'ЛОР',
                 u'Окулист', u'Стоматолог']
        if self.domain:
            return self.CComboBoxPropEditor
        elif unicode(self.my_name) in names:
            return CMultipleMKBDialog
        else:
            return self.CPlainPropEditor


class CBlankSerialActionPropertyValueType(CActionPropertyValueType):
    name = 'BlankSerial'
    variantType = QtCore.QVariant.String
    isCopyable = False

    class CPropEditor(CBlankComboBoxActions):
        def __init__(self, action, domain, parent, clientId):
            blankIdList = self.getBlankIdList(action)
            CBlankComboBoxActions.__init__(self, parent, blankIdList, True)

        def getBlankIdList(self, action):
            blankIdList = []
            docTypeId = action._actionType.id
            if docTypeId:
                db = QtGui.qApp.db
                tableEvent = db.table('Event')
                tableRBBlankActions = db.table('rbBlankActions')
                tableBlankActionsParty = db.table('BlankActions_Party')
                tableBlankActionsMoving = db.table('BlankActions_Moving')
                eventId = forceRef(action._record.value('event_id'))
                personId = None
                orgStructureId = None
                if eventId:
                    record = db.getRecordEx(tableEvent, [tableEvent['execPerson_id'], tableEvent['setDate']],
                                            [tableEvent['deleted'].eq(0), tableEvent['id'].eq(eventId)])
                    if record:
                        personId = forceRef(record.value('execPerson_id')) if record else None
                        setDate = forceDate(record.value('setDate')) if record else None
                else:
                    personId = forceRef(action._record.value('person_id'))
                if not personId:
                    personId = forceRef(action._record.value('setPerson_id'))
                if not personId:
                    personId = QtGui.qApp.userId
                if personId:
                    orgStructureId = self.getOrgStructureId(personId)
                if not orgStructureId:
                    orgStructureId = QtGui.qApp.currentOrgStructureId()

                date = forceDate(action._record.value('begDate'))
                if not date and setDate:
                    date = setDate
                cond = [tableRBBlankActions['doctype_id'].eq(docTypeId),
                        tableBlankActionsParty['deleted'].eq(0),
                        tableBlankActionsMoving['deleted'].eq(0)
                        ]
                if date:
                    cond.append(tableBlankActionsMoving['date'].le(date))
                if personId and orgStructureId:
                    cond.append(db.joinOr([tableBlankActionsMoving['person_id'].eq(personId),
                                           tableBlankActionsMoving['orgStructure_id'].eq(orgStructureId)]))
                elif personId:
                    cond.append(tableBlankActionsMoving['person_id'].eq(personId))
                elif orgStructureId:
                    cond.append(tableBlankActionsMoving['orgStructure_id'].eq(orgStructureId))
                queryTable = tableRBBlankActions.innerJoin(tableBlankActionsParty,
                                                           tableBlankActionsParty['doctype_id'].eq(
                                                               tableRBBlankActions['id']))
                queryTable = queryTable.innerJoin(tableBlankActionsMoving, tableBlankActionsMoving['blankParty_id'].eq(
                    tableBlankActionsParty['id']))
                blankIdList = db.getIdList(queryTable, u'BlankActions_Moving.id', cond,
                                           u'rbBlankActions.checkingSerial, rbBlankActions.checkingNumber, rbBlankActions.checkingAmount DESC')
            return blankIdList

        def setValue(self, value):
            CBlankComboBoxActions.setValue(self, forceString(value) if forceString(value) else forceString(
                CBlankComboBoxActions.text(self)))

        def getOrgStructureId(self, personId):
            orgStructureId = None
            if personId:
                db = QtGui.qApp.db
                tablePerson = db.table('Person')
                recOrgStructure = db.getRecordEx(tablePerson, [tablePerson['orgStructure_id']],
                                                 [tablePerson['deleted'].eq(0), tablePerson['id'].eq(personId)])
                orgStructureId = forceRef(recOrgStructure.value('orgStructure_id')) if recOrgStructure else None
            return orgStructureId

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getTableName(self):
        return self.tableNamePrefix + self.name

    def toText(self, v):
        return forceString(v)


class CBlankNumberActionPropertyValueType(CActionPropertyValueType):
    name = 'BlankNumber'
    variantType = QtCore.QVariant.String

    class CPlainPropEditor(QtGui.QLineEdit):
        def __init__(self, action, domain, parent, clientId):
            QtGui.QLineEdit.__init__(self, parent)

        def setValue(self, value):
            v = forceString(value)
            self.setText(v)

        def value(self):
            return unicode(self.text())

    class CComboBoxPropEditor(CStrComboBox):
        def __init__(self, action, domain, parent, clientId):
            CStrComboBox.__init__(self, parent)
            self.setDomain(domain)

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getEditorClass(self, isVector=False):
        if self.domain:
            return self.CComboBoxPropEditor
        else:
            return self.CPlainPropEditor


class CArterialPressureActionPropertyValueType(CActionPropertyValueType):
    name = 'ArterialPressure'
    variantType = QtCore.QVariant.Int

    class CPlainPropEditor(QtGui.QLineEdit):
        def __init__(self, action, domain, parent, clientId):
            QtGui.QLineEdit.__init__(self, parent)

        def setValue(self, value):
            v = forceString(value)
            self.setText(v)

        def value(self):
            return unicode(self.text())

    class CComboBoxPropEditor(CStrComboBox):
        def __init__(self, action, domain, parent, clientId):
            CStrComboBox.__init__(self, parent)
            self.setDomain(domain)

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getEditorClass(self, isVector=False):
        if self.domain:
            return self.CComboBoxPropEditor
        else:
            return self.CPlainPropEditor


class CTemperatureActionPropertyValueType(CActionPropertyValueType):
    name = 'Temperature'
    variantType = QtCore.QVariant.Double

    class CPropEditor(QtGui.QLineEdit):
        def __init__(self, action, domain, parent, clientId):
            QtGui.QLineEdit.__init__(self, parent)
            self._validator = QtGui.QDoubleValidator(self)
            self.setValidator(self._validator)

        def setValue(self, value):
            v = forceDouble(value)
            self.setText(str(v))

        def value(self):
            return self.text().toDouble()[0]

    @staticmethod
    def convertQVariantToPyValue(value):
        return value.toDouble()[0]

    def toInfo(self, context, v):
        return v if v else 0.0


class CPulseActionPropertyValueType(CActionPropertyValueType):
    name = 'Pulse'
    variantType = QtCore.QVariant.Int

    class CPropEditor(QtGui.QLineEdit):
        def __init__(self, action, domain, parent, clientId):
            QtGui.QLineEdit.__init__(self, parent)
            self._validator = QtGui.QIntValidator(self)
            self.setValidator(self._validator)

        def setValue(self, value):
            v = forceInt(value)
            self.setText(str(v))

        def value(self):
            return self.text().toInt()[0]

    @staticmethod
    def convertQVariantToPyValue(value):
        return value.toInt()[0]

    def toInfo(self, context, v):
        return v if v else 0


class CDateActionPropertyValueType(CActionPropertyValueType):
    name = 'Date'
    variantType = QtCore.QVariant.Date

    class CPropEditor(CDateEdit):
        def __init__(self, action, domain, parent, clientId):
            CDateEdit.__init__(self, parent)

        def setValue(self, value):
            v = value.toDate()
            self.setDate(v)

        def value(self):
            return self.date()

    @staticmethod
    def convertQVariantToPyValue(value):
        return value.toDate()

    def toText(self, v):
        return forceString(v)

    def toInfo(self, context, v):
        return CDateInfo(v)


class CTimeActionPropertyValueType(CActionPropertyValueType):
    name = 'Time'
    variantType = QtCore.QVariant.Time

    class CPropEditor(QtGui.QTimeEdit):
        def __init__(self, action, domain, parent, clientId):
            QtGui.QLineEdit.__init__(self, parent)

        def setValue(self, value):
            v = value.toTime()
            self.setTime(v)

        def value(self):
            return self.time()

    @staticmethod
    def convertQVariantToPyValue(value):
        return value.toTime()

    def toText(self, v):
        return forceString(v)

    def toInfo(self, context, v):
        return CTimeInfo(v)


class CReferenceActionPropertyValueType(CActionPropertyValueType):
    name = 'Reference'
    variantType = QtCore.QVariant.Int

    class CRBInfoEx(CRBInfo):
        def __init__(self, context, tableName, itemId):
            CInfo.__init__(self, context)
            self.id = itemId
            self.tableName = tableName

    class CPropEditor(CRBComboBox):
        def __init__(self, action, domain, parent, clientId):
            CRBComboBox.__init__(self, parent)
            db = QtGui.qApp.db

            table = db.table(domain)
            cond = []

            try:
                org_struct_id = action[u'Отделение пребывания']
                filter = 'master_id = %s' % forceString(org_struct_id)
                if QtGui.qApp.isDisregardHospitalBedOrgStructure() and domain == u'rbHospitalBedProfile':
                    condHB = None
                    self.model().coloredRows = db.getDistinctIdList('OrgStructure_HospitalBed', idCol='profile_id', where=filter)
                else:
                    condHB = filter

                profile_list = db.getDistinctIdList('OrgStructure_HospitalBed', idCol='profile_id', where=condHB)
                cond.append(table['id'].inlist(profile_list))
            except KeyError:
                cond = []

            if 'deleted' in table.fieldsDict:
                cond.append(table['deleted'].eq(0))

            self.setTable(domain, filter=db.joinAnd(cond))

        def setValue(self, value):
            CRBComboBox.setValue(self, forceRef(value))

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def toText(self, v):
        result = v
        if v:
            result = forceString(QtGui.qApp.db.translate(self.domain, 'id', v, 'name'))
        return forceString(result)

    def toInfo(self, context, v):
        return CReferenceActionPropertyValueType.CRBInfoEx(context, self.domain, v)

    def getTableName(self):
        tableName = self.tableNamePrefix + self.domain
        if tableName.lower() not in (forceString(tableName).lower() for tableName in
                                     QtSql.QSqlDatabase.database(QtGui.qApp.connectionName).tables()):
            tableName = self.tableNamePrefix + self.name
        return tableName


class CPrescriptionDrugActionPropertyValueType(CReferenceActionPropertyValueType):
    name = 'PrescriptionDrug'

    class CPropEditor(CRBComboBox):
        def __init__(self, action, domain, parent, clientId):
            CRBComboBox.__init__(self, parent)
            self.setTable(domain)
            if QtGui.qApp.userInfo:
                self.setFilter('master_id = %s' % QtGui.qApp.userInfo.orgStructureId)

        def setValue(self, value):
            CRBComboBox.setValue(self, forceRef(value))


class CTextActionPropertyValueType(CActionPropertyValueType):
    name = 'Text'
    variantType = QtCore.QVariant.String
    prefferedHeight = 10
    prefferedHeightUnit = 1

    class CPropEditor(QtGui.QTextEdit):
        def __init__(self, action, domain, parent, clientId):
            QtGui.QTextEdit.__init__(self, parent)
            self._customContextManager = CCustomContextMenuManager()
            self._customContextManager.configureWidget(self)

        def setValue(self, value):
            v = forceString(value)
            self.setPlainText(v)

        def value(self):
            return unicode(self.toPlainText())

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    @staticmethod
    def convertSpecialText(value):
        return value.replace('<br>', '\n')

    def toInfo(self, context, v):
        return forceString(v) if v else ''

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name


class CHtmlActionPropertyValueType(CActionPropertyValueType):
    name = 'Html'
    variantType = QtCore.QVariant.String
    prefferedHeight = 20
    prefferedHeightUnit = 1
    isHtml = True

    class CPropEditor(QtGui.QTextEdit):
        def __init__(self, action, domain, parent, clientId):
            QtGui.QTextEdit.__init__(self, parent)
            self.domain = domain
            self.eventEditor = None
            p = parent
            while p:
                if hasattr(p, 'eventEditor'):
                    self.eventEditor = p.eventEditor
                    break
                p = p.parent()

        def setValue(self, value):
            v = forceString(value)
            self.setHtml(v)

        def value(self):
            return unicode(self.toHtml())

        def contextMenuEvent(self, event):
            from library.PrintTemplates import getPrintAction
            menu = self.createStandardContextMenu(event.pos())
            actions = menu.actions()
            topAction = actions[0] if actions else 0
            if self.domain and self.eventEditor is not None:
                action = getPrintAction(self, self.domain, name=u'Заполнить')
                QtCore.QObject.connect(action, QtCore.SIGNAL('printByTemplate(int)'), self.fillByTemplate)
                menu.insertAction(topAction, action)
                menu.insertSeparator(topAction)
            action = QtGui.QAction(u'Редактировать во внешнем редакторе', self)
            QtCore.QObject.connect(action, QtCore.SIGNAL('triggered()'), self.editInExternalEditor)
            action.setEnabled(bool(QtGui.qApp.documentEditor()))
            menu.insertAction(topAction, action)
            menu.insertSeparator(topAction)
            menu.exec_(event.globalPos())

        def fillByTemplate(self, templateId):
            def work():
                import library
                data = getEventContextData(self.eventEditor)
                template, templateType = library.PrintTemplates.getTemplate(templateId)[1:]
                if templateType != library.PrintTemplates.htmlTemplate:
                    template = u'<HTML><BODY>Поддержка шаблонов печати в формате' \
                               u' отличном от html не реализована</BODY></HTML>'
                html = library.PrintTemplates.compileAndExecTemplate(template, data)[0]
                self.setHtml(html)

            QtGui.qApp.call(self, work)

        def editInExternalEditor(self):
            QtGui.qApp.editDocument(self.document())

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def toInfo(self, context, v):
        return forceString(v) if v else ''

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name


def cursorInPlaceholder(cursor):
    position = cursor.position()
    cursor.select(QtGui.QTextCursor.WordUnderCursor)
    selectedText = unicode(cursor.selectedText())
    bot = selectedText[:1]
    eot = selectedText[-1:]
    result = bot == '_' and eot == '_' or bot == '[' and eot == ']'
    if result:
        position = cursor.selectionStart()
        cursor.removeSelectedText()
    cursor.setPosition(position)
    return result


def moveCursorToEndOfWord(cursor):
    position = cursor.position()
    cursor.movePosition(QtGui.QTextCursor.NextCharacter, QtGui.QTextCursor.KeepAnchor)
    selectedText = unicode(cursor.selectedText()).rstrip()
    cursor.setPosition(position)
    if selectedText and not selectedText.isspace():
        cursor.movePosition(QtGui.QTextCursor.EndOfWord)


def separatorBeforeCursor(cursor):
    position = cursor.position()
    cursor.movePosition(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.KeepAnchor)
    selectedText = unicode(cursor.selectedText()).rstrip()
    cursor.setPosition(position)
    lastChar = selectedText[-1:]
    return lastChar in ':,;.?!([{</|'


def removeUsedPrefix(cursor, text):
    if ':' in text:
        position = cursor.position()
        cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.KeepAnchor)
        selectedText = unicode(cursor.selectedText())
        cursor.setPosition(position)
        parts = text.split(':')
        for x in range(len(parts) - 1, 0, -1):
            prefix = ':'.join(parts[:x])
            if prefix in selectedText:
                return ':'.join(parts[x:])
    return text


class CConstructorActionPropertyValueType(CActionPropertyValueType):
    name = 'Constructor'
    prefferedHeight = 10
    prefferedHeightUnit = 1
    variantType = QtCore.QVariant.String

    class CPropEditor(QtGui.QWidget):
        __pyqtSignals__ = ('editingFinished()',
                           'commit()',
                           )

        def __init__(self, action, domain, parent, clientId, typeEditable=True):
            QtGui.QWidget.__init__(self, parent)
            self.gridlayout = QtGui.QGridLayout(self)
            self.gridlayout.setMargin(0)
            self.gridlayout.setSpacing(0)
            self.gridlayout.setObjectName('gridlayout')

            self.splitter = QtGui.QSplitter(self)
            self.splitter.setObjectName('splitter')
            self.splitter.setOrientation(QtCore.Qt.Horizontal)
            self.splitter.setChildrenCollapsible(False)
            self.splitter.setAutoFillBackground(True)

            #            self.treeView = QtGui.QTreeView(self.splitter)
            self.treeView = CComplaintsActionPropertyValueType.CTreeView(self.splitter)
            self.treeView.setObjectName('treeView')

            db = QtGui.qApp.db
            table = db.table('rbThesaurus')
            rootItemIdCandidates = db.getIdList(table, 'id', [table['group_id'].isNull(), table['code'].eq(domain)],
                                                'id')
            # если в корне не нашлось, ищем в прочих.
            if not rootItemIdCandidates:
                rootItemIdCandidates = db.getIdList(table, 'id', table['code'].eq(domain), 'id')
            rootItemId = rootItemIdCandidates[0] if rootItemIdCandidates else None
            self.treeModel = CDBTreeModel(self, 'rbThesaurus', 'id', 'group_id', 'name', order='code')
            self.treeModel.setRootItem(CDBTreeItem(None, domain, rootItemId, self.treeModel))
            self.treeModel.setRootItemVisible(False)
            self.treeModel.setLeavesVisible(True)
            self.treeView.setModel(self.treeModel)
            self.treeView.header().setVisible(False)
            self.textEdit = QtGui.QTextEdit(self.splitter)
            self.textEdit.setObjectName('textEdit')
            self.textEdit.setFocusPolicy(QtCore.Qt.StrongFocus)
            self.textEdit.setTabChangesFocus(True)
            self.textEdit.setReadOnly(not typeEditable)
            self.gridlayout.addWidget(self.splitter, 0, 0, 1, 1)
            self.setFocusProxy(self.treeView)
            if QtGui.qApp.addBySingleClick():
                self.connect(self.treeView, QtCore.SIGNAL('clicked(QModelIndex)'), self.on_doubleClicked)
            else:
                self.connect(self.treeView, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.on_doubleClicked)
            self.textEdit.installEventFilter(self)
            self.treeView.installEventFilter(self)
            self.previousBranchMainId = None

        def eventFilter(self, widget, event):
            et = event.type()
            if et == QtCore.QEvent.FocusOut:
                fw = QtGui.qApp.focusWidget()
                if not (fw and self.isAncestorOf(fw)):
                    self.emit(QtCore.SIGNAL('editingFinished()'))
            elif et == QtCore.QEvent.Hide and widget == self.textEdit:
                self.emit(QtCore.SIGNAL('commit()'))
            return QtGui.QWidget.eventFilter(self, widget, event)

        def focusNextPrevChild(self, nextChild):
            if self.treeView.hasFocus() and nextChild:
                self.textEdit.setFocus(QtCore.Qt.TabFocusReason)
                return True
            elif self.textEdit.hasFocus() and not nextChild:
                self.treeView.setFocus(QtCore.Qt.BacktabFocusReason)
                return True
            self.setFocusProxy(self.textEdit if nextChild else self.treeView)  # иначе что-то "проскакивает" мимо.
            QtGui.QWidget.focusNextPrevChild(self, nextChild)
            return True

        def setValue(self, value):
            v = forceString(value)
            self.textEdit.setPlainText(v)
            self.textEdit.moveCursor(QtGui.QTextCursor.End)

        def value(self):
            value = unicode(self.textEdit.toPlainText())
            if value and value[-1] != '.':
                value += u'.'
            return value

        def getCurrentBranchMainId(self, item):
            if item:
                tmpItem = None
                while item.parent() and item.parent().id():
                    tmpItem = item
                    item = item.parent()
                return item.id() if item.parent() else tmpItem.id() if tmpItem else None
            return None

        def on_doubleClicked(self, index):
            db = QtGui.qApp.db
            table = db.table('rbThesaurus')
            item = index.internalPointer()
            text = '%s'
            while item and item.id():
                template = forceString(db.translate(table, 'id', item.id(), 'template'))
                try:
                    text = text % template
                except:
                    break
                item = item.parent()
            try:
                text = text % ''
            except:
                pass
            cursor = self.textEdit.textCursor()
            if cursor.hasSelection():
                pos = cursor.selectionStart()
                cursor.removeSelectedText()
                cursor.setPosition(pos)
            elif cursorInPlaceholder(cursor):
                pass
            elif not cursor.atBlockStart():
                moveCursorToEndOfWord(cursor)
                if separatorBeforeCursor(cursor):
                    cursor.insertText(' ')
                elif index.internalPointer().parent() is self.treeModel.getRootItem():
                    cursor.insertText('; ')
                else:
                    cursor.insertText(', ')

            currentBranchMainId = self.getCurrentBranchMainId(index.internalPointer())
            setFromNewBranch = (self.previousBranchMainId and self.previousBranchMainId != currentBranchMainId)
            newSetIntoNotFull = (not self.previousBranchMainId and forceStringEx(self.textEdit.toPlainText()))
            self.previousBranchMainId = currentBranchMainId
            if setFromNewBranch or newSetIntoNotFull:
                cursor.insertText('\n')
            cursor.insertText(removeUsedPrefix(cursor, text))

            self.textEdit.setTextCursor(cursor)

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name


class CComplaintsActionPropertyValueType(CActionPropertyValueType):
    name = u'Жалобы'
    prefferedHeight = 10
    prefferedHeightUnit = 1
    variantType = QtCore.QVariant.String

    class CTreeView(QtGui.QTreeView):
        def keyPressEvent(self, event):
            if event.key() == QtCore.Qt.Key_Space:
                self.emit(QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.currentIndex())
            else:
                QtGui.QTreeView.keyPressEvent(self, event)

    class CPropEditor(QtGui.QWidget):
        __pyqtSignals__ = ('editingFinished()',
                           'commit()',
                           )

        def __init__(self, action, domain, parent, clientId):
            QtGui.QWidget.__init__(self, parent)
            self.gridlayout = QtGui.QGridLayout(self)
            self.gridlayout.setMargin(0)
            self.gridlayout.setSpacing(0)
            self.gridlayout.setObjectName('gridlayout')

            self.splitter = QtGui.QSplitter(self)
            self.splitter.setObjectName('splitter')
            self.splitter.setOrientation(QtCore.Qt.Horizontal)
            self.splitter.setChildrenCollapsible(False)
            self.splitter.setAutoFillBackground(True)

            self.treeView = CComplaintsActionPropertyValueType.CTreeView(self.splitter)
            self.treeView.setObjectName('treeView')
            self.treeView.setFocusPolicy(QtCore.Qt.StrongFocus)

            self.treeModel = CDBTreeModel(self, 'rbComplain', 'id', 'group_id', 'name')
            self.treeModel.setRootItemVisible(False)
            self.treeModel.setLeavesVisible(True)
            self.treeView.setModel(self.treeModel)
            self.treeView.header().setVisible(False)

            self.textEdit = QtGui.QTextEdit(self.splitter)
            self.textEdit.setObjectName('textEdit')
            self.textEdit.setFocusPolicy(QtCore.Qt.StrongFocus)
            self.textEdit.setTabChangesFocus(True)
            self.gridlayout.addWidget(self.splitter, 0, 0, 1, 1)
            self.setFocusProxy(self.treeView)
            #            self.setFocusProxy(self.textEdit)
            self.connect(self.treeView, QtCore.SIGNAL('doubleClicked(QModelIndex)'), self.on_doubleClicked)
            self.textEdit.installEventFilter(self)
            self.treeView.installEventFilter(self)

        def eventFilter(self, widget, event):
            et = event.type()
            if et == QtCore.QEvent.FocusOut:
                fw = QtGui.qApp.focusWidget()
                if not (fw and self.isAncestorOf(fw)):
                    self.emit(QtCore.SIGNAL('editingFinished()'))
            elif et == QtCore.QEvent.Hide and widget == self.textEdit:
                self.emit(QtCore.SIGNAL('commit()'))
            return QtGui.QWidget.eventFilter(self, widget, event)

        def focusNextPrevChild(self, nextChild):
            if self.treeView.hasFocus() and nextChild:
                self.textEdit.setFocus(QtCore.Qt.TabFocusReason)
                return True
            elif self.textEdit.hasFocus() and not nextChild:
                self.treeView.setFocus(QtCore.Qt.BacktabFocusReason)
                return True
            #            self.emit(SIGNAL('editingFinished()'))
            #            self.emit(SIGNAL('commit()'))
            self.setFocusProxy(self.textEdit if nextChild else self.treeView)  # иначе что-то "проскакивает" мимо.
            QtGui.QWidget.focusNextPrevChild(self, nextChild)
            return True

        def setValue(self, value):
            v = forceString(value)
            self.textEdit.setPlainText(v)
            self.textEdit.moveCursor(QtGui.QTextCursor.End)

        def value(self):
            return unicode(self.textEdit.toPlainText())

        #        def hasFocus(self):
        #            return self.treeView.hasFocus() or self.textEdit.hasFocus()

        def on_doubleClicked(self, index):
            parts = []
            item = index.internalPointer()
            while item and item.id():
                parts.append(unicode(item.name()))
                item = item.parent()
            parts.reverse()
            text = ': '.join(parts)
            cursor = self.textEdit.textCursor()
            if cursor.hasSelection():
                pos = cursor.selectionStart()
                cursor.removeSelectedText()
                cursor.setPosition(pos)
            elif cursorInPlaceholder(cursor):
                pass
            elif not cursor.atBlockStart():
                moveCursorToEndOfWord(cursor)
                if separatorBeforeCursor(cursor):
                    cursor.insertText(' ')
                else:
                    cursor.insertText(', ')

            cursor.insertText(removeUsedPrefix(cursor, text))
            self.textEdit.setTextCursor(cursor)

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name


class CRLSActionPropertyValueType(CActionPropertyValueType):
    name = 'RLS'
    variantType = QtCore.QVariant.Int

    class CPropEditor(CRLSComboBox):
        def __init__(self, action, domain, parent, clientId):
            CRLSComboBox.__init__(self, parent)

        def setValue(self, value):
            v = forceInt(value)
            CRLSComboBox.setValue(self, v)

    @staticmethod
    def convertQVariantToPyValue(value):
        return value.toInt()[0]

    def getTableName(self):
        return self.tableNamePrefix + CIntegerActionPropertyValueType.name

    def toText(self, v):
        return CRLSComboBox.codeToText(forceInt(v))

    def toInfo(self, context, v):
        return context.getInstance(CRLSInfo, forceInt(v))


class CRLSExtendedActionPropertyValueType(CActionPropertyValueType):
    name = 'RLSExtended'
    variantType = QtCore.QVariant.Int
    customSaveLoad = True

    class ScalarEditor(CRLSExtendedEditor):
        def __init__(self, action, domain, parent, clientId, isVector=False):
            CRLSExtendedEditor.__init__(self, parent)

    class VectorEditor(CRLSExtendedVectorEditor):
        def __init__(self, action, domain, parent, clientId, isVector=False):
            CRLSExtendedVectorEditor.__init__(self, parent)

    def getEditorClass(self, isVector=False):
        return self.VectorEditor if isVector else self.ScalarEditor

    @staticmethod
    def convertQVariantToPyValue(value):
        return value[:4] if isinstance(value, tuple) else (None, None, 0, u'')

    def saveValues(self, propertyId, values):
        if values and not isinstance(values, list):
            values = [values]
        elif not values:
            values = []

        db = QtGui.qApp.db
        valueTable = db.table(self.getTableName())
        dbValues = [
            {'id'     : propertyId,
             'index'  : idx,
             'value'  : itemId,
             'form_id': formId,
             'amount' : amount,
             'note'   : note}
            for idx, (itemId, formId, amount, note) in enumerate(values)
        ]
        db.insertFromDictList(valueTable, dbValues, updateFields=['value', 'form_id', 'amount', 'note'])

        deleteCond = [valueTable['id'].eq(propertyId)]
        if values:
            deleteCond.append(valueTable['index'].notInlist(range(len(values))))
        db.deleteRecord(valueTable, deleteCond)

    def loadValues(self, propertyId):
        db = QtGui.qApp.db
        valueTable = db.table(self.getTableName())
        return [
            (forceRef(rec.value('value')),
             forceRef(rec.value('form_id')),
             forceDouble(rec.value('amount')),
             forceString(rec.value('note')))
            for rec in db.iterRecordList(valueTable,
                                         cols=['value', 'form_id', 'amount', 'note'],
                                         where=valueTable['id'].eq(propertyId),
                                         order=valueTable['index'])
        ]

    def getTableName(self):
        return self.tableNamePrefix + 'RLS'

    def toText(self, value):
        if isinstance(value, tuple):
            code, formId, amount, note = value[:4]
            return CRLSExtendedEditor.valueToText(code, formId, amount, note)
        return u'-'

    def toInfo(self, context, value):
        code, formId, amount, note = value[:4]
        return context.getInstance(CRLSExtendedInfo, code, formId, amount, note)


class COrganisationActionPropertyValueType(CActionPropertyValueType):
    name = 'Organisation'
    variantType = QtCore.QVariant.Int
    badDomain = u'Неверное описание области определения значения свойства действия типа Organisation:\n%(domain)s'
    badKey = u'Недопустимый ключ "%(key)s" в описание области определения значения свойства действия типа Organisation:\n%(domain)s'
    badValue = u'Недопустимое значение "%(val)s" ключа "%(key)s" в описание области определения значения свойства действия типа Organisation:\n%(domain)s'

    class CPropEditor(QtGui.QWidget):
        __pyqtSignals__ = ('editingFinished()',
                           'commit()',
                           )

        def __init__(self, action, domain, parent, clientId):
            QtGui.QWidget.__init__(self, parent)
            self.boxlayout = QtGui.QHBoxLayout(self)
            self.boxlayout.setMargin(0)
            self.boxlayout.setSpacing(0)
            self.boxlayout.setObjectName('boxlayout')
            self.cmbOrganisation = COrgComboBox(self)
            self.cmbOrganisation.setEditable(True)
            self.cmbOrganisation.setObjectName('cmbOrganisation')
            self.cmbOrganisation.setFilter(domain)
            self.boxlayout.addWidget(self.cmbOrganisation)
            self.btnSelect = QtGui.QPushButton(self)
            self.btnSelect.setObjectName('btnSelect')
            #            self.btnSelect.setText(u'…')
            self.btnSelect.setText(u'...')
            self.btnSelect.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Ignored)
            self.btnSelect.setFixedWidth(20)
            self.boxlayout.addWidget(self.btnSelect)
            self.setFocusProxy(self.cmbOrganisation)
            self.connect(self.btnSelect, QtCore.SIGNAL('clicked()'), self.on_btnSelect_clicked)
            self.cmbOrganisation.installEventFilter(self)
            self.btnSelect.installEventFilter(self)

        def eventFilter(self, widget, event):
            et = event.type()
            if et == QtCore.QEvent.FocusOut:
                fw = QtGui.qApp.focusWidget()
                while fw and fw != self:
                    fw = fw.parentWidget()
                if not fw:
                    self.emit(QtCore.SIGNAL('editingFinished()'))
            elif et == QtCore.QEvent.Hide and widget == self.cmbOrganisation:
                self.emit(QtCore.SIGNAL('commit()'))
            return QtGui.QWidget.eventFilter(self, widget, event)

        def on_btnSelect_clicked(self):
            orgId = selectOrganisation(self, self.cmbOrganisation.value(), False, self.cmbOrganisation.filter())
            self.cmbOrganisation.update()
            if orgId:
                self.cmbOrganisation.setValue(orgId)

        def setValue(self, value):
            self.cmbOrganisation.setValue(forceRef(value))

        def value(self):
            return self.cmbOrganisation.value()

    def __init__(self, domain=None):
        CActionPropertyValueType.__init__(self, domain)
        self.rawDomain = domain
        self.domain = self.parseDomain(domain)

    def parseDomain(self, domain):
        isInsurer = None
        isHospital = None
        isMed = None
        netCodes = []
        for word in domain.split(','):
            if word:
                parts = word.split(':')
                if len(parts) == 1:
                    key, val = u'тип', parts[0].strip()
                elif len(parts) == 2:
                    key, val = parts[0].strip(), parts[1].strip()
                else:
                    raise ValueError, self.badDomain % locals()
                keylower = key.lower()
                vallower = val.lower()
                if keylower in [u'тип']:
                    if vallower in [u'смо']:
                        isInsurer = True
                    elif vallower in [u'стац', u'стационар']:
                        isHospital = True
                    elif vallower in [u'лпу']:
                        isMed = True
                    else:
                        raise ValueError, self.badValue % locals()
                elif keylower in [u'сеть']:
                    netCodes.append(val)
                else:
                    raise ValueError, self.badKey % locals()
        db = QtGui.qApp.db
        table = db.table('Organisation')
        cond = []
        if isInsurer:
            cond.append('isInsurer')
        if isHospital:
            cond.append('isMedical = 2')
        if isMed:
            cond.append(table['net_id'].isNotNull())
        if netCodes:
            tableNet = db.table('rbNet')
            contNet = [tableNet['code'].inlist(netCodes), tableNet['name'].inlist(netCodes)]
            netIdList = db.getIdList(tableNet, 'id', db.joinOr(contNet))
            cond.append(table['net_id'].inlist(netIdList))
        return db.joinAnd(cond)

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def toText(self, v):
        return getOrganisationShortName(forceRef(v))

    def toInfo(self, context, v):
        return context.getInstance(COrgInfo, forceRef(v))


class COrgStructureActionPropertyValueType(CActionPropertyValueType):
    name = 'OrgStructure'
    variantType = QtCore.QVariant.Int
    emptyRootName = None
    badDomain = u'Неверное описание области определения значения свойства действия типа OrgStructure:\n%(domain)s'
    badKey = u'Недопустимый ключ "%(key)s" в описание области определения значения свойства действия типа OrgStructure:\n%(domain)s'
    badValue = u'Недопустимое значение "%(val)s" ключа "%(key)s" в описание области определения значения свойства действия типа OrgStructure:\n%(domain)s'

    class CPropEditor(COrgStructureComboBox):
        def __init__(self, action, domain, parent, clientId):
            COrgStructureComboBox.__init__(self, parent, None, None, domain)
            self.setOrgId(QtGui.qApp.currentOrgId(), COrgStructureActionPropertyValueType.emptyRootName)

        def setValue(self, value):
            COrgStructureComboBox.setValue(self, forceRef(value))

    def __init__(self, domain=None):
        CActionPropertyValueType.__init__(self, domain)
        COrgStructureActionPropertyValueType.emptyRootName = None
        self.domain = self.parseDomain(domain)

    def parseDomain(self, domain):
        db = QtGui.qApp.db
        orgStructureType = None
        orgStructureTypeList = [u'амбулатория', u'стационар', u'скорая помощь', u'мобильная станция',
                                u'приемное отделение стационара', u'реанимация']
        netCodes = []
        orgStructureCode = ''
        orgStructureIdList = []
        orgStructureId = None
        isBeds = 0
        isStock = 0
        isFilter = False
        for word in domain.split(','):
            if word:
                parts = word.split(':')
                if len(parts) == 1:
                    key = parts[0].strip()
                    val = None
                elif len(parts) == 2:
                    key, val = parts[0].strip(), parts[1].strip()
                else:
                    raise ValueError, self.badDomain % locals()
                keylower = key.lower()
                vallower = val.lower() if val else ''
                if keylower in [u'код']:
                    orgStructureCode = vallower
                elif keylower in [u'тип']:
                    if vallower in orgStructureTypeList:
                        orgStructureType = orgStructureTypeList.index(vallower)
                    else:
                        raise ValueError, self.badValue % locals()
                elif keylower in [u'сеть']:
                    netCodes.append(val)
                elif keylower in [u'имеет койки']:
                    isBeds = 1
                elif keylower in [u'имеет склад']:
                    isStock = 1
                else:
                    raise ValueError, self.badKey % locals()
        db = QtGui.qApp.db
        table = db.table('OrgStructure')
        cond = []
        if isBeds:
            cond.append(table['hasHospitalBeds'].eq(isBeds))
            isFilter = True
        if isStock:
            cond.append(table['hasStocks'].eq(isStock))
            isFilter = True
        if orgStructureType != None:
            cond.append(table['type'].eq(orgStructureType))
            isFilter = True
        if orgStructureCode:
            isFilter = True
            record = db.getRecordEx(table, [table['id'], table['code']],
                                    [table['deleted'].eq(0), table['code'].like(orgStructureCode)])
            if record:
                orgStructureId = forceRef(record.value('id'))
                COrgStructureActionPropertyValueType.emptyRootName = orgStructureId
                if orgStructureId:
                    orgStructureIdList = db.getDescendants('OrgStructure', 'parent_id', orgStructureId)
                    if orgStructureIdList:
                        cond.append(table['id'].inlist(orgStructureIdList))
        if netCodes:
            isFilter = True
            tableNet = db.table('rbNet')
            contNet = [tableNet['code'].inlist(netCodes), tableNet['name'].inlist(netCodes)]
            netIdList = db.getIdList(tableNet, 'id', db.joinOr(contNet))
            cond.append(table['net_id'].inlist(netIdList))
        cond.append(table['deleted'].eq(0))
        return cond
        # cond.append(table['organisation_id'].eq(QtGui.qApp.currentOrgId()))
        # idList = db.getIdList(table, 'OrgStructure.id', cond)
        # theseAndParentIdList = []
        # if idList:
        #     theseAndParentIdList = db.getTheseAndParents('OrgStructure', 'parent_id', idList)
        # cond = []
        # if theseAndParentIdList or isFilter:
        #     cond.append(table['id'].inlist(theseAndParentIdList if theseAndParentIdList else []))
        #     cond.append(table['deleted'].eq(0))
        #     #cond.append(table['organisation_id'].eq(QtGui.qApp.currentOrgId()))
        #     return cond
        # return None

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def toText(self, v):
        return getOrgStructureFullName(forceRef(v))

    def toInfo(self, context, v):
        return context.getInstance(COrgStructureInfo, forceRef(v))


class CHospitalBedActionPropertyValueType(CActionPropertyValueType):
    name = 'HospitalBed'
    variantType = QtCore.QVariant.Int
    isCopyable = False

    class CPropEditor(CHospitalBedFindComboBox):
        def __init__(self, action, domain, parent, clientId):
            plannedEndDate = forceDate(action._record.value('plannedEndDate'))
            bedId = action[u'койка']
            if bedId:
                orgStructureId = forceRef(QtGui.qApp.db.translate('OrgStructure_HospitalBed', 'id', bedId, 'master_id'))
            else:
                orgStructureId = action[u'Отделение пребывания'] if any(
                    flatCode in action._actionType.flatCode.lower() for flatCode in
                    [u'moving', u'maternityward', u'reanimation']) else None

            # if QtGui.qApp.isDisregardHospitalBedOrgStructure():
            #     orgStructureId = None

            CHospitalBedFindComboBox.__init__(self, parent, domain, plannedEndDate, orgStructureId,
                                              forceInt(QtGui.qApp.db.translate('Client', 'id', clientId, 'sex')), bedId)

        def setValue(self, value):
            CHospitalBedFindComboBox.setValue(self, forceRef(value))

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def getTableName(self):
        return self.tableNamePrefix + self.name

    def toText(self, v):
        return forceString(QtGui.qApp.db.translate('OrgStructure_HospitalBed', 'id', v, 'CONCAT(code,\' | \',name)'))

    def toInfo(self, context, v):
        from HospitalBeds.HospitalBedInfo import CHospitalBedInfo
        return context.getInstance(CHospitalBedInfo, forceRef(v))

    def propertiesUpdated(self, propertyName, oldValue, newValue, propertiesModel):
        if propertyName == u'Отделение пребывания':
            try:
                propertiesModel.action[u'койка'] = 0
                propertiesModel.emitDataChanged()
            except KeyError:
                pass


class CHospitalBedProfileActionPropertyValueType(CActionPropertyValueType):
    name = 'rbHospitalBedProfile'
    variantType = QtCore.QVariant.String

    class CPropEditor(CRBComboBox):
        def __init__(self, action, domain, parent, clientId):
            CRBComboBox.__init__(self, parent)
            self.setTable(domain)

        def setValue(self, value):
            CRBComboBox.setValue(self, forceRef(value))

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def toText(self, v):
        result = v
        if v:
            result = forceString(QtGui.qApp.db.translate(self.domain, 'id', v, 'concat(code, \' | \', name)'))
        return forceString(result)

    def toInfo(self, context, v):
        from HospitalBeds.HospitalBedInfo import CHospitalBedProfileInfo
        return context.getInstance(CHospitalBedProfileInfo, forceRef(v))


class CPersonActionPropertyValueType(CActionPropertyValueType):
    name = 'Person'
    variantType = QtCore.QVariant.Int

    class CPropEditor(CPersonComboBoxEx):
        def __init__(self, action, domain, parent, clientId):
            self.domain = domain
            self.action = action
            CPersonComboBoxEx.__init__(self, parent)

        def setValue(self, value):
            value = forceRef(value)
            if value:
                CPersonComboBoxEx.setValue(self, value)
            else:
                recordDomainList, defaultPropertyList = self.getByDefault(self.domain)
                db = QtGui.qApp.db
                tableEvent = db.table('Event')
                eventId = forceRef(self.action._record.value('event_id'))
                for key, domain in recordDomainList.items():
                    value = None
                    if key.lower() == u'ЛПУ':
                        value = forceRef(domain)
                        CPersonComboBoxEx.setOrganisationId(self, value)
                    elif key.lower() == u'подразделение':
                        tableOrgStructure = db.table('OrgStructure')
                        code = forceString(domain)
                        if code:
                            record = db.getRecordEx(tableOrgStructure, [tableOrgStructure['id']],
                                                    [tableOrgStructure['deleted'].eq(0),
                                                     tableOrgStructure['code'].eq(code)])
                            if record:
                                value = forceRef(record.value('id'))
                                CPersonComboBoxEx.setOrgStructureId(self, value)
                    elif key.lower() == u'должность':
                        value = forceString(domain)
                        CPersonComboBoxEx.setPostCode(self, value)
                    elif key.lower() == u'специальность':
                        value = forceString(domain)
                        CPersonComboBoxEx.setSpecialityCode(self, value)
                    elif key.lower() == u'деятельность':
                        value = forceString(domain)
                        CPersonComboBoxEx.setActivityCode(self, value)
                for key, domain in defaultPropertyList.items():
                    value = None
                    if key.lower() == u'подразделение':
                        if domain.contains(u'ответственного за событие', QtCore.Qt.CaseInsensitive):
                            if eventId:
                                record = db.getRecordEx(tableEvent, [tableEvent['execPerson_id']],
                                                        [tableEvent['deleted'].eq(0), tableEvent['id'].eq(eventId)])
                                if record:
                                    personId = forceRef(record.value('execPerson_id')) if record else None
                                    value = self.getOrgStructureId(personId)
                        elif domain.contains(u'назначившего действие', QtCore.Qt.CaseInsensitive):
                            personId = forceRef(self.action._record.value('setPerson_id'))
                            value = self.getOrgStructureId(personId)
                        elif domain.contains(u'выполнившего действие', QtCore.Qt.CaseInsensitive):
                            personId = forceRef(self.action._record.value('person_id'))
                            value = self.getOrgStructureId(personId)
                        elif domain.contains(u'пользователя', QtCore.Qt.CaseInsensitive):
                            userId = QtGui.qApp.userId
                            if userId:
                                value = self.getOrgStructureId(userId)
                        elif key.lower() == u'подразделение' and domain.contains(u'прибывания',
                                                                                 QtCore.Qt.CaseInsensitive):
                            value = self.action[u'Отделение пребывания'] if (
                            u'moving' in self.action._actionType.flatCode.lower()) else None
                        CPersonComboBoxEx.setOrgStructureId(self, value)
                    if key.lower() == u'специальность':
                        if domain.contains(u'ответственного за событие', QtCore.Qt.CaseInsensitive):
                            if eventId:
                                record = db.getRecordEx(tableEvent, [tableEvent['execPerson_id']],
                                                        [tableEvent['deleted'].eq(0), tableEvent['id'].eq(eventId)])
                                if record:
                                    personId = forceRef(record.value('execPerson_id')) if record else None
                                    value = self.getSpecialityId(personId)
                        elif domain.contains(u'назначившего действие', QtCore.Qt.CaseInsensitive):
                            personId = forceRef(self.action._record.value('setPerson_id'))
                            value = self.getSpecialityId(personId)
                        elif domain.contains(u'выполнившего действие', QtCore.Qt.CaseInsensitive):
                            personId = forceRef(self.action._record.value('person_id'))
                            value = self.getSpecialityId(personId)
                        elif domain.contains(u'пользователя', QtCore.Qt.CaseInsensitive):
                            userId = QtGui.qApp.userId
                            if userId:
                                value = self.getSpecialityId(userId)
                        CPersonComboBoxEx.setSpecialityId(self, value)

        def getOrgStructureId(self, personId):
            orgStructureId = None
            if personId:
                db = QtGui.qApp.db
                tablePerson = db.table('Person')
                recOrgStructure = db.getRecordEx(tablePerson, [tablePerson['orgStructure_id']],
                                                 [tablePerson['deleted'].eq(0), tablePerson['id'].eq(personId)])
                orgStructureId = forceRef(recOrgStructure.value('orgStructure_id')) if recOrgStructure else None
            return orgStructureId

        def getSpecialityId(self, personId):
            specialityId = None
            if personId:
                db = QtGui.qApp.db
                tablePerson = db.table('Person')
                record = db.getRecordEx(tablePerson, [tablePerson['speciality_id']],
                                        [tablePerson['deleted'].eq(0), tablePerson['id'].eq(personId)])
                specialityId = forceRef(record.value('speciality_id')) if record else None
            return specialityId

        def getByDefault(self, domain):
            defaultProperty = [u'ответственного за событие', u'назначившего действие', u'выполнившего действие',
                               u'пользователя', u'прибывания']
            defaultPropertyKey = {u'ЛПУ': u'', u'подразделение': u'', u'должность': u'', u'специальность': u'',
                                  u'деятельность': u''}
            recordDomainList = {}
            defaultPropertyList = {}
            if domain:
                domainR = QtCore.QString(forceString(domain))
                domainList = domainR.split(",")
                for domainI in domainList:
                    if u'\'' in domainI:
                        domainI.remove(QtCore.QChar('\''), QtCore.Qt.CaseInsensitive)
                    domainProperty = domainI.split(":")
                    if len(domainProperty) == 2:
                        for key in defaultPropertyKey.keys():
                            if domainProperty[0].contains(key, QtCore.Qt.CaseInsensitive) and forceString(
                                    domainProperty[1]).lower() not in defaultProperty:
                                recordDomainList[key] = domainProperty[1]
                                break
                            elif domainProperty[0].contains(key, QtCore.Qt.CaseInsensitive) and forceString(
                                    domainProperty[1]).lower() in defaultProperty:
                                defaultPropertyList[key] = domainProperty[1]
                                break
            return recordDomainList, defaultPropertyList

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def getTableName(self):
        return self.tableNamePrefix + self.name

    def toText(self, v):
        return personIdToText(v)

    def toInfo(self, context, v):
        return context.getInstance(CPersonInfo, forceRef(v))


class CImageActionPropertyValueType(CActionPropertyValueType):
    name = 'Image'
    variantType = QtCore.QVariant.Map
    prefferedHeight = 64
    prefferedHeightUnit = 0

    class CPropEditor(QtGui.QPushButton):
        __pyqtSignals__ = ('commit()',
                           )

        def __init__(self, action, domain, parent, clientId):
            QtGui.QPushButton.__init__(self, parent)
            self.setFocusPolicy(QtCore.Qt.StrongFocus)
            self._value = None
            self.connect(self, QtCore.SIGNAL('pressed()'), self.viewPicture)

        #           self.connect(self, QtCore.SIGNAL('clicked()'), self.onClicked, Qt.QueuedConnection)

        def setValue(self, value):
            self._value = QtGui.QImage(value) if value else None
            self.setIconByValue()

        def setIconByValue(self):
            if self._value:
                if self._value.height() > CImageActionPropertyValueType.prefferedHeight:
                    preview = self._value.scaledToHeight(CImageActionPropertyValueType.prefferedHeight,
                                                         QtCore.Qt.FastTransformation)
                else:
                    preview = self._value
            else:
                preview = QtGui.QImage(CImageActionPropertyValueType.prefferedHeight,
                                       CImageActionPropertyValueType.prefferedHeight)
            pixmap = QtGui.QPixmap.fromImage(preview)
            self.setIcon(QtGui.QIcon(pixmap))
            self.setIconSize(preview.size())

        def viewPicture(self):
            dlg = CImageProcDialog(self, self._value)
            if dlg.exec_():
                self._value = dlg.image()
                self.setIconByValue()
                self.emit(QtCore.SIGNAL('commit()'))

        def value(self):
            return self._value

    def getTableName(self):
        return self.tableNamePrefix + 'Image'

    @staticmethod
    def convertQVariantToPyValue(value):
        if value.type() == QtCore.QVariant.ByteArray:
            byteArray = value.toByteArray()
            if byteArray:
                image = QtGui.QImage()
                if image.loadFromData(byteArray):
                    return image
                else:
                    return None
        elif value.type() == QtCore.QVariant.Image:
            image = QtGui.QImage(value)
            return image
        return None

    @staticmethod
    def convertPyValueToQVariant(value):
        if value:
            byteArray = QtCore.QByteArray()
            buf = QtCore.QBuffer(byteArray)
            buf.open(QtCore.QIODevice.WriteOnly)
            value.save(buf, 'JPG')
            buf.close()
            return QtCore.QVariant(byteArray)
        return None

    def toText(self, v):
        pass
        return ''

    def toImage(self, v):
        if v:
            if v.height() > self.prefferedHeight:
                return v.scaledToHeight(self.prefferedHeight, QtCore.Qt.FastTransformation)
        return v

    def toInfo(self, context, v):
        pass
        return None


# FIXME: raipc. Я не знаю, что такое PacsImages. Нужно уточнить.
class CPacsImagesActionPropertyValueType(CImageActionPropertyValueType):
    name = "PacsImages"


class CBlankItemSelectionDialog(QtGui.QDialog):
    def __init__(self, parent, blanks):
        QtGui.QDialog.__init__(self, parent)
        self.vLayout = QtGui.QVBoxLayout(self)
        self.model = CItemListModel(self, cols=[
            CItemAttribCol(u'BlankId', 'BlankId'),
            CItemAttribCol(u'Группа', 'Groups'),
            CItemAttribCol(u'Наименование', 'Name'),
            # CItemAttribCol(u'Дата выполнения', 'DoneDate'),
            # CItemAttribCol(u'Версия', 'Version')
        ])
        self.model.setItems(blanks)
        self.table = CItemListView(self)
        self.table.setModel(self.model)
        self.table.doubleClicked.connect(self.selectBlank)
        self.vLayout.addWidget(self.table)
        self.vLayout.setMargin(4)
        self.vLayout.setSpacing(4)
        self._blank = blanks[0]
        self.setWindowTitle(u'Выберите бланк результатов для загрузки')
        self.setMinimumWidth(640)

    def selectBlank(self):
        self._blank = self.table.currentItem()
        self.accept()

    def blank(self):
        return self._blank


class CAlfalabBlankPropertyValueType(CActionPropertyValueType):
    u""" Свойство-кнопка для загрузки бланка результатов (в PDF) из ЛИС АльфаЛАБ """

    name = 'AlfalabBlank'
    variantType = QtCore.QVariant.String

    class CPropEditor(QtGui.QPushButton):
        __pyqtSignals__ = ('commit()',
                           )

        def __init__(self, action, domain, parent, clientId):
            QtGui.QPushButton.__init__(self, parent)
            self._eventId = forceRef(action.getRecord().value('event_id'))
            self._ttjId = forceRef(action.getRecord().value('takenTissueJournal_id'))
            self._actionId = forceRef(action.getRecord().value('id'))
            self._orderCodes = self.getChildrenOrderCodes()
            self._value = None
            self.setFocusPolicy(QtCore.Qt.StrongFocus)
            self.setText(u'Запросить бланк результатов')
            self.connect(self, QtCore.SIGNAL('pressed()'), self.getOrderBlanks)

        def getChildrenOrderCodes(self):
            if not (self._actionId and self._eventId):
                return set()
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            tableActionType = db.table('ActionType')
            table = tableAction.innerJoin(tableActionType, tableActionType['id'].eq(tableAction['actionType_id']))
            cols = [
                tableActionType['lis_code']
            ]
            cond = [
                tableAction['event_id'].eq(self._eventId),
                tableAction['parent_id'].eq(self._actionId),
                tableAction['deleted'].eq(0)
            ]
            return set(forceString(rec.value('lis_code')) for rec in db.iterRecordList(table, cols, cond, isDistinct=True))

        def getBlankFile(self, blank):
            try:
                QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmpFile:
                    CAlfalabService.getConnection().getBlankFile(tmpFile.name, blank.BlankId, blank.BlankGUID)
                    QtGui.QDesktopServices.openUrl(QtCore.QUrl(QtCore.QUrl.fromLocalFile(tmpFile.name)))
            except CAlfalabException as e:
                QtGui.QMessageBox.information(self, u'ЛИС АльфаЛАБ', u'Не удалось загрузить бланк результатов: {0}'.format(e), QtGui.QMessageBox.Ok)
            finally:
                QtGui.qApp.restoreOverrideCursor()

        def getOrderBlanks(self):
            if self._value or not self._eventId or not self._ttjId:
                return

            db = QtGui.qApp.db
            tableOrder = db.table('{logger}.AlfalabOrderLog'.format(logger=getLoggerDbName()))

            orderRec = db.getRecordEx(tableOrder, ['Nr', 'MisId', 'LisId'], [tableOrder['event_id'].eq(self._eventId),
                                                                             tableOrder['takenTissueJournal_id'].eq(self._ttjId)])
            if not orderRec:
                QtGui.QMessageBox.information(self, u'ЛИС АльфаЛАБ', u'Заявка не найдена', QtGui.QMessageBox.Ok)
                return

            referral = ReferralQuery(forceString(orderRec.value('Nr')), forceString(orderRec.value('MisId')), forceString(orderRec.value('LisId')))

            try:
                QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                results = CAlfalabService.getConnection().getReferralResults(referral)
                QtGui.qApp.restoreOverrideCursor()

                if results and results.Blanks:
                    resultBlanks = filter(lambda b: set(test.OrderCode for test in b.Tests).intersection(self._orderCodes), results.Blanks)
                    if resultBlanks:
                        if len(resultBlanks) > 1:
                            dlg = CBlankItemSelectionDialog(self, resultBlanks)
                            dlg.exec_()
                            blank = dlg.blank()
                        else:
                            blank = resultBlanks[0]
                        if blank:
                            self.getBlankFile(blank)
                    else:
                        QtGui.QMessageBox.information(self, u'ЛИС АльфаЛАБ', u'Нет бланка результатов для данного типа исследования', QtGui.QMessageBox.Ok)
                else:
                    QtGui.QMessageBox.warning(self, u'ЛИС АльфаЛАБ', u'Результат не получен', QtGui.QMessageBox.Ok)

            except CAlfalabException as e:
                QtGui.QMessageBox.information(self, u'ЛИС АльфаЛАБ', u'<i>"{0}"</i>'.format(e), QtGui.QMessageBox.Ok)

            except Exception as e:
                QtGui.QMessageBox.warning(self, u'Ошибка', unicode(e), QtGui.QMessageBox.Ok)
                QtGui.qApp.logCurrentException()

            finally:
                QtGui.qApp.restoreOverrideCursor()

        def value(self):
            return self._value

        def setValue(self, value):
            pass

    @staticmethod
    def convertPyValueToQVariant(value):
        return None

    @staticmethod
    def convertQVariantToPyValue(value):
        return None


class CImageMapActionPropertyValueType(CActionPropertyValueType):
    name = "ImageMap"
    variantType = QtCore.QVariant.ByteArray
    prefferedHeight = 64
    prefferedHeightUnit = 0
    domain = None
    imgValue = None

    class CPropEditor(QtGui.QPushButton):
        __pyqtSignals__ = ('commit()',
                           )
        name = 'My Editor'

        def __init__(self, action, domain, parent, clientId):
            QtGui.QPushButton.__init__(self, parent)
            self.setFocusPolicy(QtCore.Qt.StrongFocus)
            actionType = action.getType()
            self.domain = domain
            self._value = QtCore.QVariant('<code>%s</code>' % domain)
            self.markSize = 1
            self.actionTypeName = actionType.name
            self.openRedactorAbility = True
            self.connect(self, QtCore.SIGNAL('pressed()'), self.viewRedactor)

        def setValue(self, value):
            if value.toString() == u'':
                tmp = '<code>%s</code>' % self.domain
                self._value = QtCore.QVariant(tmp)
            else:
                self._value = value
            self.setIconByValue()

        def setIconByValue(self):
            image = self.getValueFromDomain()
            if image:
                if image.height() > CImageMapActionPropertyValueType.prefferedHeight:
                    preview = image.scaledToHeight(CImageMapActionPropertyValueType.prefferedHeight,
                                                   QtCore.Qt.FastTransformation)
                else:
                    preview = image
                pixmap = QtGui.QPixmap.fromImage(preview)
                self.setIcon(QtGui.QIcon(pixmap))
                self.setIconSize(preview.size())

        def getValueFromDomain(self):
            db = QtGui.qApp.db
            where = 'code=\'%s\'' % self.domain
            record = db.getRecordEx('rbImageMap', '*', where)
            try:
                ba = record.value('image').toByteArray()
                image = QtGui.QImage().fromData(ba)
                self.markSize = forceInt(record.value('markSize'))
                self.openRedactorAbility = True
                return image
            except Exception, _:
                msg = QtGui.QMessageBox()
                msg.addButton('Ok', msg.AcceptRole)
                txt = u'В полях (свойствах) действия %s указан неверный код' % self.actionTypeName
                msg.setText(txt)
                msg.exec_()
                self.openRedactorAbility = False
                return None
            #            return image

        def viewRedactor(self):
            if self.openRedactorAbility:
                dlg = CAngelDialog(self._value)
                dlg.setMarkSize(self.markSize)
                dlg.exec_()
                tmp = u'<code>%s</code>' % self.domain
                try:
                    self._value = tmp + dlg.marksData
                except:
                    self._value = tmp
                self.emit(QtCore.SIGNAL('commit()'))

        def value(self):
            return self._value

    def __init__(self, domain=None):
        self.tableName = self.getTableName()
        self.domain = domain

        value = self.getValueFromDomain()
        if value:
            self.imgValue = self.convertDBImageToPyValue(value)

    def getValueFromDomain(self):
        db = QtGui.qApp.db
        where = 'code=\'%s\'' % self.domain
        record = db.getRecordEx('rbImageMap', 'image', where)
        try:
            ba = record.value('image')
            return ba
        except Exception, _:
            msg = QtGui.QMessageBox()
            msg.addButton('Ok', msg.AcceptRole)
            msg.setText(u'В действиях типа \'ImageMap\' указаны неверные коды')
            msg.exec_()
            return None

    def getTableName(self):
        return self.tableNamePrefix + 'ImageMap'

    def convertDBImageToPyValue(self, value):
        if value.type() == QtCore.QVariant.ByteArray:
            byteArray = value.toByteArray()
            if byteArray:
                image = QtGui.QImage()
                if image.loadFromData(byteArray):
                    return image
                else:
                    return None
        return None

    @staticmethod
    def convertQVariantToPyValue(value):
        if type(value) == QtCore.QVariant:
            if value.type() == QtCore.QVariant.String:
                stringValue = value.toString()
                return stringValue
        elif isinstance(value, basestring):
            return value
        return None

    @staticmethod
    def convertPyValueToQVariant(value):
        if value:
            return QtCore.QVariant(value)
        return None

    def toText(self, v):
        pass
        return ''

    def toImage(self, v):
        v = self.imgValue
        if v:
            if v.height() > self.prefferedHeight:
                return v.scaledToHeight(self.prefferedHeight, QtCore.Qt.FastTransformation)
        return v

    def toInfo(self, context, v):
        pass
        return None


class CActionPropertyDomainJobTicketInfo(object):
    u"""
    Восстановление типа работ и возможности автоподстановки в свойство действия по ActionPropertyType.domain
    """

    def __init__(self, domain=None):
        self.jobTypeCode = None
        self.presetValue = False
        self.presetUnique = False

        if domain:
            domainParts = domain.split(';')
            self.jobTypeCode = domainParts[0]
            if len(domainParts) > 1:
                domainSuffix = forceStringEx(domainParts[1]).lower()
                self.presetUnique = domainSuffix in ['a+', u'а+']
                self.presetValue = self.presetUnique or domainSuffix in ['a', u'а']


class CJobTicketActionPropertyValueType(CActionPropertyValueType):
    name = 'JobTicket'
    variantType = QtCore.QVariant.Int
    isCopyable = False

    def __init__(self, domain=None):
        CActionPropertyValueType.__init__(self, domain)
        self._jobTicketInfo = CActionPropertyDomainJobTicketInfo(domain)
        self.domain = self._jobTicketInfo.jobTypeCode
        self.isCopyable = not QtGui.qApp.userHasRight(urDefaultJobTickets)

    class CPropEditor(CJobTicketChooserComboBox):
        def __init__(self, actionList, domain, parent, clientId, isVector=False):
            CJobTicketChooserComboBox.__init__(self, parent)
            if actionList:
                if isinstance(actionList, CAction):
                    actionList = [actionList]
                serviceIdList = []
                actionTypeIdList = []
                for action in actionList:
                    actionType = action.getType()
                    serviceId = forceRef(QtGui.qApp.db.translate('rbService', 'code', actionType.code, 'id'))
                    serviceIdList.append(serviceId)
                    actionTypeIdList.append(actionType.id)

                self.setCurrentServiceIdList(serviceIdList)
                self.setActionTypeIdList(actionTypeIdList)
            self.setClientId(clientId)
            self.isVector = isVector
            self.setDefaultJobTypeCode(CActionPropertyDomainJobTicketInfo(domain).jobTypeCode)
            date = forceDate(actionList[0]._record.value('begDate')) if actionList else None
            if date:
                self.setDefaultDate(date)

            enabled = QtGui.qApp.userHasRight(urEditJobTicket)
            if domain:
                enabled = enabled and QtGui.qApp.isUserAvailableJobType(domain)
            self.setEnabled(enabled)

        def setValue(self, values):
            # TODO: skkachaev: Сделать консистентным
            if type(values) == QtCore.QVariant:
                values = values.toPyObject()
                if values is None:
                    values = []
                if type(values) != list:
                    values = [values]
            CJobTicketChooserComboBox.setValue(self, values)



    def getPresetValue(self):
        if self._jobTicketInfo.presetValue and self._jobTicketInfo.jobTypeCode and QtGui.qApp.userHasRight(urDefaultJobTickets):
            data = CRBModelDataCache.getData('rbJobType')
            jobTypeId = data.getIdByCode(self._jobTicketInfo.jobTypeCode)
            if jobTypeId:
                jobTypeIdList = QtGui.qApp.db.getDescendants('rbJobType', 'group_id', jobTypeId)
                if len(jobTypeIdList) == 1 and jobTypeIdList[0] == jobTypeId:
                    return self.reserveUnique(jobTypeId) if self._jobTicketInfo.presetUnique else self.getClientPresetJobTicketId(jobTypeId)
        return CActionPropertyValueType.getPresetValue(self)

    @staticmethod
    def reserveUnique(jobTypeId):
        u"""
        Проставление уникальных номерков в действиях для данного типа работ
        :param jobTypeId: rbJobType.id
        :return: Job_Ticket.id
        """
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableAP = db.table('ActionProperty')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableEvent = db.table('Event')
        tableJob = db.table('Job')
        tableJobTicket = db.table('Job_Ticket')

        queryTable = tableEvent.innerJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tableAP, tableAP['action_id'].eq(tableAction['id']))
        queryTable = queryTable.innerJoin(tableAPJT, tableAPJT['id'].eq(tableAP['id']))
        queryTable = queryTable.innerJoin(tableJobTicket, tableJobTicket['id'].eq(tableAPJT['value']))
        queryTable = queryTable.innerJoin(tableJob, tableJob['id'].eq(tableJobTicket['master_id']))

        client_id = QtGui.qApp.currentClientId()
        person_id = QtGui.qApp.userId
        cond = [
            tableJob['jobType_id'].eq(jobTypeId),
            tableJobTicket['endDateTime'].isNull(),
            tableEvent['client_id'].ne(client_id),
            tableJobTicket['status'].eq(0)
        ]
        jobTicketIdListDenied = db.getDistinctIdList(queryTable, tableJobTicket['id'], cond)

        queryTable = tableJob.innerJoin(tableJobTicket, tableJobTicket['master_id'].eq(tableJob['id']))
        queryTable = queryTable.leftJoin(tableAPJT, tableAPJT['value'].eq(tableJobTicket['id']))

        cond = [
            tableAPJT['id'].isNull(),
            tableJob['jobType_id'].eq(jobTypeId),
            tableJobTicket['datetime'].datetimeGe(QtCore.QDateTime().currentDateTime()),
            # tableJobTicket['datetime'].dateEq(QtCore.QDate().currentDate()),
            db.not_(db.func.isReservedJobTicket(tableJobTicket['id'])),
            tableJobTicket['resConnectionId'].isNull(),
            tableJobTicket['status'].eq(0),
        ]

        if jobTicketIdListDenied:
            cond.append(tableJobTicket['id'].notInlist(jobTicketIdListDenied))

        while True:
            record = db.getRecordEx(queryTable, tableJobTicket['id'], cond, order=tableJobTicket['id'])
            if record:
                jobTicketId = forceRef(record.value('id'))
                result = QtGui.qApp.addJobTicketReservation(jobTicketId, person_id)
                if result:
                    return jobTicketId
                else:
                    cond.append(tableJobTicket['id'].ne(jobTicketId))
                    continue

            return None

    @staticmethod
    def getClientPresetJobTicketId(jobTypeId):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableAP = db.table('ActionProperty')
        tableAPJT = db.table('ActionProperty_Job_Ticket')
        tableEvent = db.table('Event')
        tableJob = db.table('Job')
        tableJobTicket = db.table('Job_Ticket')

        queryTable = tableEvent.innerJoin(tableAction, tableAction['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tableAP, tableAP['action_id'].eq(tableAction['id']))
        queryTable = queryTable.innerJoin(tableAPJT, tableAPJT['id'].eq(tableAP['id']))
        queryTable = queryTable.innerJoin(tableJobTicket, tableJobTicket['id'].eq(tableAPJT['value']))
        queryTable = queryTable.innerJoin(tableJob, tableJob['id'].eq(tableJobTicket['master_id']))

        cond = [
            tableJob['jobType_id'].eq(jobTypeId),
            tableJobTicket['endDateTime'].isNull()
        ]

        duration = forceInt(db.translate('rbJobType', 'id', jobTypeId, 'ticketDuration'))

        notValidDatetimeCond = 'DATE(DATE_ADD(Job_Ticket.`datetime`, INTERVAL %d DAY)) = CURRENT_DATE()' % duration

        jobTicketIdList = db.getDistinctIdList(queryTable,
                                               tableJobTicket['id'],
                                               cond + [
                                                   tableEvent['client_id'].eq(QtGui.qApp.currentClientId()),
                                                   tableJobTicket['status'].inlist([JobTicketStatus.Awaiting,
                                                                                    JobTicketStatus.InProgress]),
                                                   notValidDatetimeCond
                                               ],
                                               tableJobTicket['id'])

        for jobTicketId in jobTicketIdList:
            QtGui.qApp.addJobTicketReservation(jobTicketId, QtGui.qApp.userId)
            return jobTicketId

        jobTicketIdListDenied = db.getDistinctIdList(queryTable,
                                                     tableJobTicket['id'],
                                                     cond + [
                                                         tableEvent['client_id'].ne(QtGui.qApp.currentClientId()),
                                                         tableJobTicket['status'].inlist([JobTicketStatus.Awaiting,
                                                                                          JobTicketStatus.InProgress])
                                                     ])

        queryTable = tableJob.innerJoin(tableJobTicket, tableJobTicket['master_id'].eq(tableJob['id']))
        cond = [
            tableJob['jobType_id'].eq(jobTypeId),
            # tableJobTicket['datetime'].dateEq(QtCore.QDate.currentDate()),
            tableJobTicket['datetime'].datetimeGe(QtCore.QDateTime().currentDateTime()),
            tableJobTicket['status'].eq(JobTicketStatus.Awaiting),
            db.not_(db.func.isReservedJobTicket(tableJobTicket['id']))
        ]

        if jobTicketIdListDenied:
            cond.append(tableJobTicket['id'].notInlist(jobTicketIdListDenied))

        record = db.getRecordEx(queryTable, tableJobTicket['id'], cond, order=tableJobTicket['id'])
        if record:
            jobTicketId = forceRef(record.value('id'))
            QtGui.qApp.addJobTicketReservation(jobTicketId, QtGui.qApp.userId)
            return jobTicketId

        return None

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def getTableName(self):
        return self.tableNamePrefix + 'Job_Ticket'

    def toText(self, v):
        return CJobTicketChooserComboBox.getTicketAsText(forceRef(v))

    def toInfo(self, context, v):
        from Resources.JobTicketInfo import CJobTicketInfo
        return CJobTicketInfo(context, forceRef(v))

    def propertiesUpdated(self, propertyName, oldValue, newValue, propertiesModel):
        if propertyName == u'Номерок' and newValue.toList():
            try:
                propertiesModel.action[u'Количество номерков'] = len(newValue.toList())
                propertiesModel.emitDataChanged()
            except KeyError:
                pass


class CSamplingActionPropertyValueType(CActionPropertyValueType):
    name = u'Проба'
    variantType = QtCore.QVariant.String

    class CPropEditor(QtGui.QLineEdit):
        def __init__(self, action, domain, parent, clientId):
            QtGui.QLineEdit.__init__(self, parent)
            self.oneSpace = False

        def setValue(self, value):
            v = forceString(value)
            self.setText(v)

        def value(self):
            return unicode(self.text())

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name

    def getEditorClass(self, isVector=False):
        return self.CPropEditor


class CToothActionPropertyValueType(CActionPropertyValueType):
    name = u'Зуб'
    variantType = QtCore.QVariant.String

    class CComboBoxPropEditor(CStrComboBox):
        def __init__(self, action, domain, parent, clientId):
            CStrComboBox.__init__(self, parent)
            self.setDomain(domain)

    class CTextEditPropEditor(QtGui.QTextEdit):
        def __init__(self, action, domain, parent, clientId):
            QtGui.QTextEdit.__init__(self, parent)

        def setValue(self, value):
            v = forceString(value)
            self.setPlainText(v)

        def value(self):
            return unicode(self.toPlainText())

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name

    def getEditorClass(self, isVector=False):
        if forceStringEx(self.domain):
            return self.CComboBoxPropEditor
        else:
            return self.CTextEditPropEditor


class CCounterActionPropertyValueType(CActionPropertyValueType):
    name = u'Счетчик'
    variantType = QtCore.QVariant.String

    class CPropEditor(QtGui.QLineEdit):
        def __init__(self, action, domain, parent, clientId):
            QtGui.QLineEdit.__init__(self, parent)
            self.setReadOnly(True)

        def setValue(self, value):
            v = forceString(value)
            self.setText(v)

        def value(self):
            return unicode(self.text())

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceString(value)

    def getTableName(self):
        return self.tableNamePrefix + CStringActionPropertyValueType.name

    def getCounterValue(self):
        counterId = self.getCounterId()
        value = None
        if counterId:
            try:
                clientId = QtGui.qApp.currentClientId()
                value = getDocumentNumber(clientId, counterId)
            except:
                QtGui.QMessageBox.critical(QtGui.qApp.mainWindow,
                                           u'Внимание!',
                                           u'Произошла ошибка при получении значения счетчика!',
                                           QtGui.QMessabeBox.Ok)
                return None
        return value

    def getCounterId(self):
        domain = self.domain
        if not domain:
            return None
        return forceRef(QtGui.qApp.db.translate('rbCounter', 'code', domain, 'id'))

    def getEditorClass(self, isVector=False):
        return self.CPropEditor

    def getPresetValue(self):
        value = self.getCounterValue()
        return value


class CClientQuotingActionPropertyValueType(CActionPropertyValueType):
    mapIdToName = {}
    name = u'Квота пациента'
    variantType = QtCore.QVariant.Int
    isObsolete = False

    class CPropEditor(CClientQuotingComboBox):
        def __init__(self, action, domain, parent, clientId):
            actionRecord = action.getRecord()
            begDate = forceDate(actionRecord.value('begDate'))
            endDate = forceDate(actionRecord.value('endDate'))
            CClientQuotingComboBox.__init__(self, parent, clientId, begDate=begDate, endDate=endDate)

        def setValue(self, value):
            v = forceRef(value)

            CClientQuotingComboBox.setValue(self, v)

    def getEditorClass(self, isVector=False):
        return self.CPropEditor

    def getTableName(self):
        return self.tableNamePrefix + 'Client_Quoting'

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def toText(self, v):
        v = forceRef(v)
        name = ''
        if v:
            db = QtGui.qApp.db
            quotaTypeId = forceRef(db.translate('Client_Quoting', 'id', v, 'quotaType_id'))
            name = CClientQuotingActionPropertyValueType.mapIdToName.get(v, None)
            if not name:
                name = forceString(db.translate('QuotaType', 'id', quotaTypeId, 'CONCAT_WS(\' | \', code, name)'))
                CClientQuotingActionPropertyValueType.mapIdToName[quotaTypeId] = name
            self.isObsolete = forceBool(QtGui.qApp.db.translate('QuotaType', 'id', quotaTypeId, 'isObsolete'))
        else:
            self.isObsolete = False
        return name

    def toInfo(self, context, v):
        return context.getInstance(CClientQuotaInfo, forceRef(v))


class CQuotaTypeActionPropertyValueType(CActionPropertyValueType):
    mapIdToName = {}
    name = 'QuotaType'
    variantType = QtCore.QVariant.Int
    isObsolete = False

    class CPropEditor(CClientQuotingModelPatientComboBox):
        def __init__(self, action, domain, parent, clientId):
            CClientQuotingModelPatientComboBox.__init__(self, parent)

        def setValue(self, value):
            v = forceRef(value)
            CClientQuotingModelPatientComboBox.setValue(self, v)

    def getEditorClass(self, isVector=False):
        return self.CPropEditor

    @staticmethod
    def convertQVariantToPyValue(value):
        return forceRef(value)

    def toText(self, v):
        quotaTypeId = forceRef(v)
        name = ''
        if quotaTypeId:
            db = QtGui.qApp.db
            name = CQuotaTypeActionPropertyValueType.mapIdToName.get(quotaTypeId, None)
            if name is None:
                name = forceString(db.translate('QuotaType', 'id', quotaTypeId, 'concat_ws(\' | \', code, name)'))
                CQuotaTypeActionPropertyValueType.mapIdToName[quotaTypeId] = name
            self.isObsolete = forceBool(db.translate('QuotaType', 'id', quotaTypeId, 'isObsolete'))
        else:
            self.isObsolete = False
        return name

    def toInfo(self, context, v):
        return context.getInstance(CClientQuotaInfo, forceRef(v))


class CRadiationDoseActionPropertyValueType(CDoubleActionPropertyValueType):
    name = u'Доза облучения'
    variantType = QtCore.QVariant.Double

    def getTableName(self):
        return self.tableNamePrefix + CDoubleActionPropertyValueType.name


class CTissueTypeActionPropertyValueType(CReferenceActionPropertyValueType):
    name = 'TissueType'
    _tableName = 'rbTissueType'

    class CPropEditor(CRBComboBox):
        def __init__(self, action, domain, parent, clientId):
            CRBComboBox.__init__(self, parent)

            db = QtGui.qApp.db
            tableATTT = db.table('ActionType_TissueType')
            tableTissueType = db.table('rbTissueType')
            idList = db.getIdList(tableATTT, tableATTT['tissueType_id'], tableATTT['master_id'].eq(action._actionType.id))
            tissueTypeFilter = tableTissueType['id'].inlist(idList) if idList else '0'
            self.setTable(CTissueTypeActionPropertyValueType._tableName, filter=tissueTypeFilter, addNone=False, needCache=True)

    def toText(self, v):
        cache = CRBModelDataCache.getData(self._tableName)
        tissueType = cache.getStringById(forceRef(v), CRBComboBox.showName)
        return tissueType

    def toInfo(self, context, v):
        return context.getInstance(CTissueTypeInfo, v)

    def getTableName(self):
        return self.tableNamePrefix + CReferenceActionPropertyValueType.name


CActionPropertyValueTypeRegistry.register(CDoubleActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CIntegerActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CStringActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CDateActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CTimeActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CReferenceActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CTextActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CHtmlActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CConstructorActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CComplaintsActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CRLSActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CRLSExtendedActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(COrganisationActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(COrgStructureActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CHospitalBedActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CHospitalBedProfileActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CPersonActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CImageActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CJobTicketActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CImageMapActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CSamplingActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CBlankSerialActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CBlankNumberActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CTemperatureActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CArterialPressureActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CPulseActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CToothActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CCounterActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CClientQuotingActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CQuotaTypeActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CRadiationDoseActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CPacsImagesActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CTissueTypeActionPropertyValueType)
CActionPropertyValueTypeRegistry.register(CAlfalabBlankPropertyValueType)


class CActionPropertyType(object):
    class UserProfileBehaviour:
        DisableEdit = 0
        Hide = 1

    # Атрибуты для проверки схожих типов свойств. Для начала примем, что соответствие должно быть полным (кроме id)
    similarAPTattributes = [
        'idx', 'name', 'shortName', 'descr', 'typeName', 'valueDomain', 'valueType', 'isVector', 'unitId', 'norm',
        'sex', 'age', 'visibleInJobTicket', 'visibleInTableRedactor', 'isAssignable', 'testId',
        'defaultEvaluation', 'canChangeOnlyOwner', 'isActionNameSpecifier', 'laboratoryCalculator',
        'inActionsSelectionTable', 'redactorSizeFactor', 'isFrozen', 'typeEditable'
    ]

    def __init__(self, record):
        self.initByRecord(record)

    def initByRecord(self, record):
        self.id = forceInt(record.value('id'))
        self.idx = forceInt(record.value('idx'))
        self.name = forceString(record.value('name'))
        self.shortName = forceString(record.value('shortName'))
        self.descr = forceString(record.value('descr'))
        self.typeName = forceString(record.value('typeName'))
        self.valueDomain = forceString(record.value('valueDomain'))
        self.valueType = self.getValueType()  # type: CActionPropertyValueType
        self.defaultValue = self.valueType.convertSpecialText(forceString(record.value('defaultValue')))
        self.isVector = forceBool(record.value('isVector'))
        self.unitIdAsQVariant = record.value('unit_id')
        self.normAsQVariant = record.value('norm')
        self.unitId = forceRef(self.unitIdAsQVariant)
        self.norm = forceString(self.normAsQVariant)
        self.sex = forceInt(record.value('sex'))
        self.penalty = forceInt(record.value('penalty'))
        age = forceStringEx(record.value('age'))
        self.age = parseAgeSelector(age) if age else None
        self.qVariantType = self.valueType.variantType
        self.valueSqlFieldTemplate = QtSql.QSqlField('value', self.qVariantType)
        self.convertQVariantToPyValue = self.valueType.convertQVariantToPyValue
        self.convertPyValueToQVariant = self.valueType.convertPyValueToQVariant
        self.tableName = self.valueType.tableName
        self.visibleInJobTicket = forceBool(record.value('visibleInJobTicket'))
        self.visibleInTableRedactor = forceInt(record.value('visibleInTableRedactor'))
        self.isAssignable = forceBool(record.value('isAssignable'))
        self.testId = forceInt(record.value('test_id'))
        self.defaultEvaluation = forceInt(record.value('defaultEvaluation'))
        self.canChangeOnlyOwner = forceInt(record.value('canChangeOnlyOwner'))
        self.isActionNameSpecifier = forceBool(record.value('isActionNameSpecifier'))
        self.laboratoryCalculator = forceString(record.value('laboratoryCalculator'))
        self.inActionsSelectionTable = forceInt(record.value('inActionsSelectionTable'))
        self.redactorSizeFactor = forceDouble(record.value('redactorSizeFactor'))
        self.isFrozen = forceBool(record.value('isFrozen'))
        self.typeEditable = forceBool(record.value('typeEditable'))
        self.userProfileId = forceRef(record.value('userProfile_id'))
        self.userProfileBehaviour = forceInt(record.value('userProfileBehaviour'))

    def getValueType(self):
        return CActionPropertyValueTypeRegistry.get(self.typeName, self.valueDomain, self.name)

    def getNewRecord(self):
        db = QtGui.qApp.db
        record = db.table('ActionProperty').newRecord()
        #        record.append(QtSql.QSqlField(self.valueSqlFieldTemplate)) ???
        record.setValue('type_id', QtCore.QVariant(self.id))
        record.setValue('unit_id', self.unitIdAsQVariant)
        record.setValue('norm', self.normAsQVariant)
        return record

    def getValueTableName(self):
        return self.tableName

    def getValue(self, valueId):
        if self.valueType.customSaveLoad:
            values = self.valueType.loadValues(valueId)
            if self.isVector:
                return values
            elif values:
                return values[0]
            else:
                return None

        db = QtGui.qApp.db
        valueTable = db.table(self.tableName)
        if self.isVector:
            stmt = db.selectStmt(valueTable, 'value', valueTable['id'].eq(valueId), order='`index`')
            query = db.query(stmt)
            result = []
            while query.next():
                result.append(self.convertQVariantToPyValue(query.record().value(0)))
            return result
        else:
            stmt = db.selectStmt(valueTable, 'value', [valueTable['id'].eq(valueId), valueTable['index'].eq(0)])
            query = db.query(stmt)
            if query.next():
                return self.convertQVariantToPyValue(query.record().value(0))
            else:
                return None

    def storeRecord(self, record, value):
        db = QtGui.qApp.db
        valueTable = db.table(self.tableName)
        valueId = db.insertOrUpdate('ActionProperty', record)

        if valueId and self.valueType.customSaveLoad:
            self.valueType.saveValues(valueId, value)
            return valueId

        if self.isVector:
            vector = value
            indexes = range(len(vector))
        else:
            if value:
                vector = [value]
                indexes = [0]
            else:
                vector = []
                indexes = []

        if indexes:
            stmt = QtCore.QString()
            stream = QtCore.QTextStream(stmt, QtCore.QIODevice.WriteOnly)
            stream << (u'INSERT INTO %s (`id`, `index`, `value`) VALUES ' % self.tableName)
            for index in indexes:
                val = self.convertPyValueToQVariant(vector[index])
                if index:
                    stream << u', '
                stream << (u'(%d, %d, ' % (valueId, index))
                stream << db.formatQVariant(val.type(), val)
                stream << u')'
            stream << u' ON DUPLICATE KEY UPDATE `value` = VALUES(`value`)'
            db.query(stmt)
            db.deleteRecord(valueTable, [valueTable['id'].eq(valueId),
                                         valueTable['index'].notInlist(indexes)])
        else:
            db.deleteRecord(valueTable, [valueTable['id'].eq(valueId)])
        return valueId

    def createEditor(self, action, editorParent, clientId):
        result = None
        editorClass = self.valueType.getEditorClass(self.isVector)
        if editorClass:
            if editorClass == CConstructorActionPropertyValueType.CPropEditor:
                result = editorClass(action, self.valueType.domain, editorParent, clientId, self.typeEditable)
            elif self.isVector:
                result = editorClass(action, self.valueType.domain, editorParent, clientId, isVector=self.isVector)
            else:
                result = editorClass(action, self.valueType.domain, editorParent, clientId)
        return result

    def applicable(self, clientSex, clientAge):
        if self.sex and clientSex and clientSex != self.sex:
            return False
        if self.age and clientAge and not checkAgeSelector(self.age, clientAge):
            return False
        return True

    def getPrefferedHeight(self):
        return self.valueType.prefferedHeightUnit, self.valueType.prefferedHeight

    def isHtml(self):
        return self.valueType.isHtml

    def isSimilar(self, other):
        if not isinstance(other, CActionPropertyType):
            return False
        result = True
        for attr in self.similarAPTattributes:
            result = result and self.__getattribute__(attr) == other.__getattribute__(attr)
            if not result:
                break
        return result


class CActionType(object):
    # atronah: флаг того, что статические строковые константы класса уже были переведены
    isTranslated = False
    # режимы подсчёта количества в действии
    userInput = 0
    eventVisitCount = 1
    eventLength = 2
    eventLengthWithoutRedDays = 3
    actionLength = 4
    actionLengthWithoutRedDays = 5
    actionFilledProps = 6
    bedDaysEventLength = 7
    bedDaysEventLengthWithoutRedDays = 8

    statusNames = ActionStatus.nameList[:]

    # используется в проверка для проставления статуса
    ignoreStatus = [2, 3, 6, 7, 8, 9, 10, 11]

    # дата выполнения(default end date)
    dedUndefined = 0
    dedCurrentDate = 1
    dedEventSetDate = 2
    dedEventExecDate = 3

    # планируемая дата выполнения(default planned end date)
    dpedUndefined = 0
    dpedNextDay = 1
    dpedNextWorkDay = 2
    dpedJobTicketDate = 3
    dpedBegDatePlusAmount = 4
    dpedBegDatePlusDuration = 5

    # дата назначения(default direction date)
    dddUndefined = 0
    dddEventSetDate = 1
    dddCurrentDate = 2
    dddActionExecDate = 3

    # ответственный (default person)
    dpUndefined = 0
    dpEmpty = 1
    dpSetPerson = 2
    dpEventExecPerson = 3
    dpCurrentUser = 4

    # MKB (default MKB)
    dmkbNotUsed = 0
    dmkbByFinalDiag = 1
    dmkbBySetPersonDiag = 2
    dmkbSyncFinalDiag = 3
    dmkbSyncSetPersonDiag = 4
    dmkbEmpty = 5

    # Morphology (default Morphology)
    dmorphologyNotUsed = 0
    dmorphologyByFinalDiag = 1
    dmorphologyBySetPersonDiag = 2
    dmorphologySyncFinalDiag = 3
    dmorphologySyncSetPersonDiag = 4
    dmorphologyEmpty = 5

    dMESNotUsed = 0
    dMESFromEvent = 1
    dMESEmpty = 2

    # их названия
    amountEvaluation = [
        u'Количество вводится непосредственно',
        u'По числу визитов',
        u'По длительности события',
        u'По длительности события без выходных дней',
        u'По длительности действия',
        u'По длительности действия без выходных дней',
        u'По заполненным свойствам действия',
        u'Койко-дни заполняются по длительности',
        u'Койко-дни заполняются по длительности без выходных дней'
    ]

    # вид услуги
    serviceTypeOther = 0
    serviceTypeInitialInspection = 1
    serviceTypeReinspection = 2
    serviceTypeProcedure = 3
    serviceTypeOperation = 4
    serviceTypeResearch = 5
    serviceTypeHealing = 6
    serviceTypeSupplies = 7
    serviceTypeWardPayment = 8

    # Атрибуты, проверяемые при проверке схожих типов дествий. Помимо атрибутов ОБЯЗАТЕЛЬНО проверяются свойства типов действий.
    similarATattributes = [
        'isRequiredCoordination', 'amount', 'amountEvaluation', 'defaultStatus', 'defaultDirectionDate', 'defaultBeginDate',
        'defaultPlannedEndDate', 'defaultEndDate', 'defaultSetPersonId', 'defaultExecPersonId', 'defaultPersonInEvent',
        'defaultPersonInEditor',
        'defaultOrgId', 'defaultMKB', 'defaultMES', 'defaultMorphology', 'isMorphologyRequired', 'office', 'showTime',
        'showAPOrg',
        'maxOccursInEvent', 'isMes',  # 'nomenclativeServiceId',
        'isPrinted', 'context', 'prescribedTypeId', 'sheduleId',
        'isNomenclatureExpense', 'hasAssistant', 'propertyAssignedVisible', 'propertyUnitVisible',
        'propertyNormVisible',
        'propertyEvaluationVisible', 'serviceType', 'actualAppointmentDuration'
    ]

    def __init__(self, record):
        self._propertiesByName = {}  # type: dict[unicode, CActionPropertyType]
        self._propertiesById = {}  # type: dict[int, CActionPropertyType]
        self.initByRecord(record)
        self.retranslateClass(force=False)

    @classmethod
    def retranslateClass(cls, force=True):
        if force or not cls.isTranslated:
            cls.statusNames = map(lambda s: forceTr(s, u'ActionStatus'),
                                  cls.statusNames)
            cls.isTranslated = True
        return cls

    def initByRecord(self, record):
        self.id = forceRef(record.value('id'))
        self.groupId = forceRef(record.value('group_id'))
        self.class_ = forceInt(record.value('class'))
        self.code = forceString(record.value('code'))
        self.name = forceString(record.value('name'))
        self.title = forceString(record.value('title'))
        self.flatCode = forceString(record.value('flatCode'))
        self.isRequiredCoordination = forceBool(record.value('isRequiredCoordination'))
        #        self.serviceId = forceRef(record.value('service_id'))
        self.amount = forceDouble(record.value('amount'))
        self.amountEvaluation = forceInt(record.value('amountEvaluation'))
        self.defaultStatus = forceInt(record.value('defaultStatus'))
        self.defaultDirectionDate = forceInt(record.value('defaultDirectionDate'))
        self.defaultBeginDate = forceInt(record.value('defaultBeginDate'))
        self.defaultPlannedEndDate = forceInt(record.value('defaultPlannedEndDate'))
        self.defaultEndDate = forceInt(record.value('defaultEndDate'))
        self.defaultExecPersonId = forceRef(record.value('defaultExecPerson_id'))
        self.defaultSetPersonId = forceRef(record.value('defaultSetPerson_id'))
        self.defaultPersonInEvent = forceInt(record.value('defaultPersonInEvent'))
        self.defaultPersonInEditor = forceInt(record.value('defaultPersonInEditor'))
        self.defaultOrgId = forceRef(record.value('defaultOrg_id'))
        self.defaultMKB = forceInt(record.value('defaultMKB'))
        self.defaultMES = forceInt(record.value('defaultMES'))
        self.defaultMorphology = forceInt(record.value('defaultMorphology'))
        self.isMorphologyRequired = forceInt(record.value('isMorphologyRequired'))
        self.office = forceString(record.value('office'))
        self.showTime = forceBool(record.value('showTime'))
        self.showAPOrg = forceBool(record.value('showAPOrg')) if not record.value('showAPOrg').isNull() else True
        self.showAPNotes = forceBool(record.value('showAPNotes')) if not record.value('showAPNotes').isNull() else True
        self.maxOccursInEvent = forceInt(record.value('maxOccursInEvent'))
        self.isMes = forceBool(record.value('isMES'))
        self.nomenclativeServiceId = forceRef(record.value('nomenclativeService_id'))
        self.isPrinted = forceBool(record.value('isPrinted'))
        self.context = forceString(record.value('context'))
        self.prescribedTypeId = forceRef(record.value('prescribedType_id'))
        self.sheduleId = forceRef(record.value('shedule_id'))
        self.isNomenclatureExpense = forceBool(record.value('isNomenclatureExpense'))
        self.hasAssistant = forceInt(record.value('hasAssistant'))
        self.propertyAssignedVisible = forceBool(record.value('propertyAssignedVisible'))
        self.propertyUnitVisible = forceBool(record.value('propertyUnitVisible'))
        self.propertyNormVisible = forceBool(record.value('propertyNormVisible'))
        self.propertyEvaluationVisible = forceBool(record.value('propertyEvaluationVisible'))
        self.serviceType = forceInt(record.value('serviceType'))
        self.actualAppointmentDuration = forceInt(record.value('actualAppointmentDuration'))
        self.isCustomSum = forceBool(record.value('isCustomSum'))
        self.frequencyCount = forceInt(record.value('frequencyCount'))
        self.frequencyPeriod = forceInt(record.value('frequencyPeriod'))
        self.frequencyPeriodType = forceInt(record.value('frequencyPeriodType'))
        self.isStrictFrequency = forceBool(record.value('isStrictFrequency'))
        self.isFrequencyPeriodByCalendar = forceBool(record.value('isFrequencyPeriodByCalendar'))
        self.counterId = forceRef(record.value('counter_id'))
        self.isExecRequiredForEventExec = forceBool(record.value('isExecRequiredForEventExec'))
        self.isSubstituteEndDateToEvent = forceBool(record.value('isSubstituteEndDateToEvent'))
        self.isIgnoreEventExecDate = forceBool(record.value('isIgnoreEventExecDate'))
        self.filledLock = forceBool(record.value('filledLock'))

        self._initProperties()

    def _initProperties(self):
        db = QtGui.qApp.db
        tableAPT = db.table('ActionPropertyType')
        cond = [tableAPT['actionType_id'].eq(self.id),
                tableAPT['deleted'].eq(0)]
        for record in db.iterRecordList(tableAPT, '*', cond, order=tableAPT['name']):
            propertyType = CActionPropertyType(record)
            self._propertiesByName[propertyType.name.lower()] = propertyType
            self._propertiesById[propertyType.id] = propertyType

    def initPropertiesByRecords(self, recordList, clear=False):
        """
            Инициализируем свойства по списку записей. Используется в редакторе типов действий,
            когда актуальные для нас данные еще не записаны в БД.
            @param clear - удалить все старые свойства
        """
        if clear:
            self._propertiesByName = {}
            self._propertiesById = {}
        for record in recordList:
            propertyType = CActionPropertyType(record)
            self._propertiesByName[propertyType.name.lower()] = propertyType
            self._propertiesById[propertyType.id] = propertyType

    def containsPropertyWithName(self, name):
        return name.lower() in self._propertiesByName

    def getPropertiesById(self):
        return self._propertiesById

    def getPropertiesByName(self):
        return self._propertiesByName

    def getPropertyType(self, name):
        return self._propertiesByName.get(name.lower(), None)

    def getPropertyTypeById(self, propertyId):
        return self._propertiesById[propertyId]

    def propertyTypeIdPresent(self, propertyId):
        return propertyId in self._propertiesById

    def checkMaxOccursLimit(self, count, displayMessage=True):
        result = self.maxOccursInEvent == 0 or count < self.maxOccursInEvent
        if not result and displayMessage:
            widget = QtGui.qApp.activeModalWidget() or QtGui.qApp.mainWindow or None
            QtGui.QMessageBox.critical(widget,
                                       u'Произошла ошибка',
                                       u'Действие типа "%s" должно применяться в осмотре не более %s' % (
                                       self.name, formatNum1(self.maxOccursInEvent, (u'раза', u'раз', u'раз'))),
                                       QtGui.QMessageBox.Close)
        return result

    def checkReceivedMovingLeaved(self, message):
        widget = QtGui.qApp.activeModalWidget() or QtGui.qApp.mainWindow or None
        QtGui.QMessageBox.critical(widget,
                                   u'Произошла ошибка',
                                   message,
                                   QtGui.QMessageBox.Close)
        return False

    def isSimilar(self, otherActionType):
        other = otherActionType
        if not isinstance(otherActionType, CActionType):
            return False
        result = True
        for attr in self.similarATattributes:
            result = result and self.__getattribute__(attr) == other.__getattribute__(attr)
            if not result:
                break
        if result:
            if not len(self.getPropertiesByName()) == len(other.getPropertiesByName()):
                return False
            for propertyName in self._propertiesByName:
                thisProperty = self.getPropertyType(propertyName)
                otherProperty = other.getPropertyType(propertyName)
                result = result and thisProperty.isSimilar(otherProperty)
                if not result:
                    break
        return result


class CActionTypeCache(CDbEntityCache):
    mapIdToActionType = {}
    mapCodeToActionType = {}
    mapFlatCodeToActionType = {}

    @classmethod
    def purge(cls):
        cls.mapIdToActionType.clear()
        cls.mapCodeToActionType.clear()
        cls.mapFlatCodeToActionType.clear()

    @classmethod
    def getById(cls, actionTypeId):
        result = cls.mapIdToActionType.get(actionTypeId, None)
        if not result:
            cls.connect()
            db = QtGui.qApp.db
            actionTypeRecord = db.getRecord('ActionType', '*', actionTypeId)
            result = CActionType(actionTypeRecord)
            cls.register(result)
        return result

    @classmethod
    def getByCode(cls, actionTypeCode):
        result = cls.mapCodeToActionType.get(actionTypeCode, None)
        if not result:
            cls.connect()
            db = QtGui.qApp.db
            tableActionType = db.table('ActionType')
            actionTypeRecord = db.getRecordEx(tableActionType, '*', tableActionType['code'].eq(actionTypeCode))
            assert actionTypeRecord
            result = CActionType(actionTypeRecord)
            cls.register(result)
        return result

    @classmethod
    def getByFlatCode(cls, actionTypeFlatCode):
        result = cls.mapFlatCodeToActionType.get(actionTypeFlatCode, None)
        if not result:
            cls.connect()
            db = QtGui.qApp.db
            tableActionType = db.table('ActionType')
            actionTypeRecord = db.getRecordEx(tableActionType, '*', tableActionType['flatCode'].eq(actionTypeFlatCode))
            assert actionTypeRecord is not None, 'No ActionType with flatCode = actionTypeFlatCode'
            result = CActionType(actionTypeRecord)
            cls.register(result)
        return result

    @classmethod
    def register(cls, actionType):
        cls.mapIdToActionType[actionType.id] = actionType
        cls.mapCodeToActionType[actionType.code] = actionType
        cls.mapFlatCodeToActionType[actionType.flatCode] = actionType


class CActionProperty(object):
    def __init__(self, actionType, record=None, propertyType=None):
        self._unitId = None
        self._norm = ''
        self._record = None
        self._changed = False
        self._isAssigned = False
        self._evaluation = None
        self.setType(propertyType)
        if record:
            self.setRecord(record, actionType)
        elif self._type and self._type.isVector:
            self._value = []
        elif self._type and self._type.defaultValue:
            if self._type.typeName == 'OrgStructure':
                self._type.defaultValue = QtGui.qApp.db.translate('OrgStructure', 'code', self._type.defaultValue, 'id')
            self._value = self._type.convertQVariantToPyValue(toVariant(self._type.defaultValue))
            self._changed = True
        else:
            self._value = propertyType.valueType.getPresetValue() if propertyType else None
            self._changed = bool(self._value)

    def setType(self, propertyType):
        self._type = propertyType  # type: CActionPropertyType
        if propertyType:
            if propertyType.isVector:
                self.getValue = self.getValueVector
                self.getText = self.getTextVector
                self.getImage = self.getImageVector
                self.getInfo = self.getInfoVector
            else:
                self.getValue = self.getValueScalar
                self.getText = self.getTextScalar
                self.getImage = self.getImageScalar
                self.getInfo = self.getInfoScalar
            self._unitId = propertyType.unitId
            self._norm = propertyType.norm

    def type(self):
        return self._type

    def setRecord(self, record, actionType):
        propertyTypeId = forceRef(record.value('type_id'))
        if self._type:
            assert self._type.id == propertyTypeId
        else:
            self.setType(actionType.getPropertyTypeById(propertyTypeId))
        self._record = record
        self._value = self._type.getValue(record.value('id'))
        self._unitId = forceRef(record.value('unit_id'))
        self._norm = forceString(record.value('norm'))
        self._isAssigned = forceBool(record.value('isAssigned'))
        evaluation = record.value('evaluation')
        self._evaluation = None if evaluation.isNull() else forceInt(evaluation)

    def getRecord(self):
        return self._record

    def save(self, actionId):
        if self._changed:
            if not self._record:
                self._record = self._type.getNewRecord()
            self._record.setValue('action_id', toVariant(actionId))
            # т.к. эти данные не редактируются - можно пренебречь изменениями.
            #            self._record.setValue('unit_id', toVariant(self._unitId))
            #            self._record.setValue('norm', toVariant(self._norm))

            self._record.setValue('isAssigned', toVariant(self._isAssigned))
            self._record.setValue('evaluation', toVariant(self._evaluation))
            result = self._type.storeRecord(self._record, self._value)
            self._changed = False
        else:
            if self._record:
                result = forceRef(self._record.value('id'))
            else:
                result = None
        return result

    def getValueScalar(self):
        return self._value

    def getTextScalar(self):
        return self._type.valueType.toText(self._value)

    def getImageScalar(self):
        return self._type.valueType.toImage(self._value)

    def getInfoScalar(self, context):
        return self._type.valueType.toInfo(context, self._value)

    def getValueVector(self):
        if self._value is None:
            return []
        return self._value[:]  # shalow copy

    def getTextVector(self):
        if self._value is None:
            return []
        toText = self._type.valueType.toText
        return u', '.join([toText(x) for x in self._value])

    def getImageVector(self):
        if self._value is None:
            return []
        toImage = self._type.valueType.toImage
        return [toImage(x) for x in self._value]

    def getInfoVector(self, context):
        if self._value is None:
            return []
        toInfo = self._type.valueType.toInfo
        return [toInfo(context, x) for x in self._value]

    def setValue(self, value):
        if self._value != value:
            self._changed = True
        self._value = value

    def getUnitId(self):
        return self._unitId

    def getNorm(self):
        return self._norm

    def isAssigned(self):
        u"""Описание свойства действия @see setAssigned"""
        return self._isAssigned

    def setAssigned(self, isAssigned):
        u"""
        Оотражение поля БД ActionProperty.isAssigned
        :param isAssigned: 0 = ничего, 1 = назначен
        """
        if self._isAssigned != isAssigned:
            self._changed = True
        self._isAssigned = isAssigned

    def getEvaluation(self):
        return self._evaluation

    def setEvaluation(self, evaluation):
        if self._evaluation != evaluation:
            self._changed = True
        self._evaluation = evaluation

    def copy(self, src):
        self.setAssigned(src.isAssigned())
        self.setValue(src.getValue())
        self.setEvaluation(src.getEvaluation())

    def copyIfNotEmpty(self, src):
        val = src.getValue()
        if val and not (isinstance(val, basestring) and val.isspace()):
            self.setAssigned(src.isAssigned())
            self.setValue(src.getValue())
            self.setEvaluation(src.getEvaluation())

    def getPrefferedHeight(self):
        return self._type.getPrefferedHeight()

    def isHtml(self):
        return self._type.isHtml()

    def isActionNameSpecifier(self):
        return self._type.isActionNameSpecifier


class CAction(object):
    def __init__(self, actionType=None, record=None):
        self._actionType = actionType  # type: CActionType
        self._record = None
        self._propertiesByName = {}  # type: dict[unicode, CActionProperty]
        self._propertiesById = {}  # type: dict[int, CActionProperty]
        self._executionPlan = {}
        self._assistantsByCode = {}
        self._properties = []  # type: list[CActionProperty]
        self._locked = False
        self._nomenclatureExpense = None
        self._specifiedName = ''
        if record:
            self.setRecord(record)
        else:
            self._record = QtGui.qApp.db.table('Action').newRecord()
            self._nomenclatureExpense = CNomenclatureExpense(
                None) if self._actionType and self._actionType.isNomenclatureExpense else None

    @classmethod
    def createByTypeId(cls, actionTypeId):
        actionType = CActionTypeCache.getById(actionTypeId)
        return cls(actionType=actionType)

    @classmethod
    def createByTypeCode(cls, actionTypeCode):
        actionType = CActionTypeCache.getByCode(actionTypeCode)
        return cls(actionType=actionType)

    @classmethod
    def getAction(cls, eventId, actionTypeCode):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        actionType = CActionTypeCache.getByCode(actionTypeCode)
        cond = [tableAction['event_id'].eq(eventId), tableAction['actionType_id'].eq(actionType.id)]
        record = db.getRecordEx(tableAction, '*', cond)
        return cls(record=record, actionType=actionType)

    @classmethod
    def getActionById(cls, actionId):
        record = QtGui.qApp.db.getRecord('Action', '*', actionId)
        return cls(record=record)

    def setRecord(self, record):
        # установить тип
        actionTypeId = forceRef(record.value('actionType_id'))
        if self._actionType:
            assert actionTypeId == self._actionType.id
        else:
            self._actionType = CActionTypeCache.getById(actionTypeId)
        self._record = record
        # инициализировать properties
        actionId = record.value('id')
        if forceRef(actionId):
            db = QtGui.qApp.db

            tableAP = db.table('ActionProperty')
            cond = [
                tableAP['action_id'].eq(actionId),
                tableAP['deleted'].eq(0)
            ]
            for propertyRecord in db.iterRecordList(tableAP, '*', cond):
                propertyTypeId = forceRef(propertyRecord.value('type_id'))
                if self._actionType.propertyTypeIdPresent(propertyTypeId):
                    prop = CActionProperty(self._actionType, propertyRecord)
                    # ???                    if prop.isValid():
                    self._propertiesByName[prop._type.name.lower()] = prop
                    self._propertiesById[prop._type.id] = prop
            self._properties = self._propertiesById.values()
            self._properties.sort(key=lambda prop: prop._type.idx)

            tableActionEP = db.table('Action_ExecutionPlan')
            cond = [
                tableActionEP['master_id'].eq(actionId),
                tableActionEP['deleted'].eq(0)
            ]
            for executionPlanRecord in db.iterRecordList(tableActionEP, '*', cond):
                execDateTime = forceDateTime(executionPlanRecord.value('execDate'))
                execDate = pyDate(execDateTime.date())
                execTime = execDateTime.time()
                execTimeDict = self._executionPlan.get(execDate, {})
                execTimeDict[execTime] = executionPlanRecord
                self._executionPlan[execDate] = execTimeDict
            # Загрузка ассистентов действия.
            self._assistantsByCode = self.loadAssistants(actionId)
        else:
            if self._actionType.counterId:
                self._record.setValue('counterValue',
                                      QtCore.QVariant(getDocumentNumber(None, self._actionType.counterId)))
        # спец. отметки
        status = forceInt(record.value('status'))
        personId = forceRef(record.value('person_id'))
        if forceRef(record.value('id')) and status == ActionStatus.Done and personId:
            self._locked = not (QtGui.qApp.userId == personId
                                or QtGui.qApp.userHasRight(urEditOtherPeopleAction)
                                or QtGui.qApp.userId in getPersonChiefs(personId)
                                )
        else:
            self._locked = False
        # списание ЛСиИМН
        if self._actionType.isNomenclatureExpense:
            self._nomenclatureExpense = CNomenclatureExpense(actionId)
        self._specifiedName = forceString(record.value('specifiedName'))

    def save(self, eventId=None, idx=0, isActionTemplate=False):
        db = QtGui.qApp.db
        if self._locked:
            # для заблокированной записи сохраняем только idx (позиция в списке на экране)
            actionId = forceRef(self._record.value('id'))
            if forceInt(self._record.value('idx')) != idx:
                self._record.setValue('idx', QtCore.QVariant(idx))
                db.query('UPDATE Action SET idx=%d WHERE id=%d' % (idx, actionId))
            return actionId
        else:
            # сохранить основную запись
            tableAction = db.table('Action')
            if not self._record:
                self._record = tableAction.newRecord()
            if not forceRef(self._record.value('id')):
                self._record.setValue('actionType_id', QtCore.QVariant(self._actionType.id))
                self._record.setValue('specifiedName', QtCore.QVariant(self._specifiedName))
                if self._actionType.counterId:
                    self._record.setValue('counterValue',
                                          QtCore.QVariant(getDocumentNumber(None, self._actionType.counterId)))
            if eventId:
                self._record.setValue('event_id', QtCore.QVariant(eventId))

            signature = 1 if forceDate(self._record.value('endDate')).isValid() else 0
            self._record.setValue('signature', QtCore.QVariant(
                signature))  # atronah: Для синхронизации с изменениями в ДокторРум по просьбе olooo

            self._record.setValue('idx', QtCore.QVariant(idx))
            itemId = db.insertOrUpdate(tableAction, self._record)
            self._record.setValue('id', toVariant(itemId))
            propertiesIdList = []
            # сохранить записи свойств
            for propertyObject in self._propertiesById.itervalues():
                if type(propertyObject.type().valueType) is CCounterActionPropertyValueType and isActionTemplate:
                    continue
                propertyId = propertyObject.save(itemId)
                if propertyId:
                    propertiesIdList.append(propertyId)
            # сохранить план выполнения
            executionPlanIdList = []
            if self._executionPlan:
                tableAEP = db.table('Action_ExecutionPlan')
                for _, execTimeDict in self._executionPlan.items():
                    for _, planRecord in execTimeDict.items():
                        planRecord.setValue('master_id', QtCore.QVariant(itemId))
                        executionPlanId = db.insertOrUpdate(tableAEP, planRecord)
                        planRecord.setValue('id', toVariant(executionPlanId))
                        if executionPlanId not in executionPlanIdList:
                            executionPlanIdList.append(executionPlanId)
            # удалить записи свойств кроме сохранённых
            tableAP = db.table('ActionProperty')
            if propertiesIdList:
                db.deleteRecord(tableAP, [tableAP['action_id'].eq(itemId),
                                          tableAP['id'].notInlist(propertiesIdList)])
            else:
                db.deleteRecord(tableAP, [tableAP['action_id'].eq(itemId)])

            # удалить записи плана выполнения кроме сохранённых
            if self._executionPlan:
                tableAEP = db.table('Action_ExecutionPlan')
                if executionPlanIdList:
                    db.deleteRecord(tableAEP, [tableAEP['master_id'].eq(itemId),
                                               tableAEP['id'].notInlist(executionPlanIdList)])
                else:
                    db.deleteRecord(tableAEP, [tableAEP['master_id'].eq(itemId)])
            # списание ЛСиИМН
            if self._nomenclatureExpense:
                self._nomenclatureExpense.save(itemId)

            self.saveAssistants(itemId, self._assistantsByCode)
            return itemId

    def getType(self):
        return self._actionType

    def getRecord(self):
        return self._record

    def getId(self):
        return forceRef(self._record.value('id')) if self._record else None

    def isLocked(self):
        return self._locked

    # если любое из свойств имеет длину > 10, то блокировать (i3455)
    def isDeletable(self):
        return not self.isLocked() and not (self._actionType.filledLock and
                                            any([isinstance(x._value, (str, unicode)) and len(x._value) > 10 for x in
                                                 self._properties]))

    def getSpecifiedName(self):
        return self._specifiedName

    def getProperties(self):
        return self._properties

    def getPropertiesById(self):
        return self._propertiesById

    def getPropertiesByName(self):
        return self._propertiesByName

    def containsPropertyWithName(self, name):
        return name.lower() in self._propertiesByName

    def getFilledPropertiesCount(self):
        count = 0
        for prop in self._propertiesById.itervalues():
            if prop.getValue():
                count += 1
        return count

    def getProperty(self, name):
        result = self._propertiesByName.get(name.lower(), None)
        if not result:
            propertyType = self._actionType.getPropertyType(name)
            if propertyType:
                result = CActionProperty(self._actionType, propertyType=propertyType)
                self._propertiesByName[propertyType.name.lower()] = result
                self._propertiesById[propertyType.id] = result
                self._properties.append(result)
                self._properties.sort(key=lambda prop: prop._type.idx)
            else:
                raise KeyError(u'ActionType (%s: %s) does not have property named %s' % (self._actionType.id,
                                                                                         self._actionType.name,
                                                                                         name))
        return result

    def getPropertyById(self, propertyId):
        u"""
        Получение Свойства Действия по id Типа Свойства действия
        :param propertyId: id ТИПА свойства действия
        :return: CActionProperty
        """
        result = self._propertiesById.get(propertyId, None)
        if not result:
            propertyType = self._actionType.getPropertyTypeById(propertyId)
            result = CActionProperty(self._actionType, propertyType=propertyType)
            self._propertiesByName[propertyType.name.lower()] = result
            self._propertiesById[propertyType.id] = result
            self._properties.append(result)
            self._properties.sort(key=lambda prop: prop._type.idx)
        return result

    def getPropertyByIndex(self, index):
        return self._properties[index]

    def getExecutionPlan(self):
        return self._executionPlan

    def setExecutionPlan(self, executionPlan):
        self._executionPlan = executionPlan

    def __getitem__(self, name):
        propertyObject = self.getProperty(name)
        return propertyObject.getValue() if propertyObject else None

    def __setitem__(self, name, value):
        propertyObject = self.getProperty(name)
        if propertyObject:
            propertyObject.setValue(value)
        #        if property.isActionNameSpecifier():
        #            self.setSpecifiedName(property.getText())

    def __delitem__(self, name):
        if self._propertiesByName.has_key(name.lower()):
            propertyObject = self._propertiesByName[name.lower()]
            #            if property.isActionNameSpecifier():
            #                self.setSpecifiedName(property.getText())
            del self._propertiesByName[name.lower()]
            del self._propertiesById[propertyObject._type.id]

    def __iter__(self):
        return iter(self._properties)

    def updateByTemplate(self, templateId):
        db = QtGui.qApp.db
        templateActionId = forceRef(db.translate('ActionTemplate', 'id', templateId, 'action_id'))
        self.updateByActionId(templateActionId)

    def updateByActionId(self, actionId):
        db = QtGui.qApp.db
        templateRecord = db.getRecord('Action', '*', actionId)
        if templateRecord:
            templateAction = CAction(record=templateRecord)
            self.updateByAction(templateAction)

    def updateByAction(self, templateAction):
        for propertyName in self._propertiesByName:
            propertyObject = self._propertiesByName[propertyName]
            if propertyObject.type().valueType.isCopyable and propertyName in templateAction._propertiesByName:
                templatePropertyObject = templateAction._propertiesByName[propertyName]
                if propertyObject.type().isSimilar(templatePropertyObject.type()):
                    propertyObject.copyIfNotEmpty(templateAction._propertiesByName[propertyName])

    ## Очищает список свойств действия
    def clearProperties(self):
        self._propertiesByName.clear()
        self._propertiesById.clear()
        self._properties = []

    ## Очищает список плана выполнения действия
    def clearExecution(self):
        self._executionPlan.clear()

    ## Создает копию текущего действия
    #
    # Дополнительные (необязательная) параметры копирования данных текущего Действия в новое.
    # @param isCopyRecordData: пометка о необходимости копировать запись БД. (По умолчанию False).
    # @param isCopyActionId: пометка о необходимости копирования ID Действия при копировании записи БД. (По умолчанию False).
    # @param isCopyExecutionPlan: пометка о необходимости копирования плана выполнения. (По умолчанию False).
    # @param isCopyProperties: пометка о необходимости копирования свойств действия. (По умолчанию True).
    # @param isCheckPropertiesCopyable: пометка о необходимости проверки при копировании свойств, 
    #                                    является ли значение свойства копируемым (CActionPropertyValueType.isCopyable).
    #                                    (По умолчанию True).
    def clone(self, **kwargs):
        newAction = CAction(actionType=self.getType())
        self.copyAction(self, newAction, **kwargs)
        return newAction

    ## Копирует план выполнения из одного Действия в другое.
    # @param sourceAction: исходное Действие.
    # @param targetAction: целевое Действие.
    @staticmethod
    def copyActionExecutionPlan(sourceAction, targetAction):
        targetAction.clearExecution()
        targetAction.setExecutionPlan(copy.deepcopy(sourceAction.getExecutionPlan()))

    ## Копирует ассистентов из одного Действия в другое.
    # @param sourceAction: исходное Действие.
    # @param targetAction: целевое Действие.
    @staticmethod
    def copyActionAssistants(sourceAction, targetAction):
        for assistantTypeCode in sourceAction.existedAssistantCodeList():
            assistantId = sourceAction.getAssistantId('assistant')
            assistantFreeInput = sourceAction.getAssistantFreeInput('assistant')
            targetAction.setAssistant(assistantTypeCode, assistantId, assistantFreeInput)

    ## Копирует свойства из одного Действия в другое.
    # @param sourceAction: исходное Действие.
    # @param targetAction: целевое Действие.
    # @param isCheckCopyable: проверять свойства на возможность копирования. По умолчанию включено (True). 
    @staticmethod
    def copyActionProperties(sourceAction, targetAction, isCheckCopyable=True):
        targetAction.clearProperties()
        for sourceProperty in sourceAction.getProperties():
            if not isCheckCopyable or sourceProperty.type().valueType.isCopyable:
                sourcePropertyTypeId = sourceProperty.type().id
                targetProperty = targetAction.getPropertyById(sourcePropertyTypeId)
                targetProperty.copy(sourceProperty)

    ## Копирует основные данные о Действии из одного в другое.
    # @param sourceAction: исходное Действие.
    # @param targetAction: целевое Действие.
    # @param isCopyIdFieldData: копировать данные поля ID записи из БД. По умолчанию выключено (False).
    @staticmethod
    def copyActionRecordData(sourceAction, targetAction, isCopyIdFieldData=False):
        # получаем копиюю записи БД из исходного действия
        sourceActionRecord = QtSql.QSqlRecord(sourceAction.getRecord())
        # обнуляем id записи БД исходного действия, чтобы оно не копировалось 
        # и чтобы при setRecord не подгружались свойства действия
        sourceActionRecord.setValue(u'id', QtCore.QVariant())
        # сохраняем id целевого действия
        sourceActionId, targetActionId = sourceAction.getId(), targetAction.getId()
        # Присваиваем целевому действию новую запись БД
        targetAction.setRecord(sourceActionRecord)
        # Восстанавливаем id целевого действия
        targetAction.getRecord().setValue('id', toVariant(sourceActionId if isCopyIdFieldData else targetActionId))

    ## Копирует содержимое одного Действия в другое. По умолчанию копирует только свойства и план выполнения
    # @param sourceAction: исходное Действие.
    # @param targetAction: целевое Действие.
    #
    # Дополнительные (необязательная) параметры копирования
    # @param isCopyRecordData: пометка о необходимости копировать запись БД. (По умолчанию False).
    # @param isCopyActionId: пометка о необходимости копирования ID Действия при копировании записи БД. (По умолчанию False).
    # @param isCopyAssistants: пометка о необходимости копирования ассистентов Действия при копировании записи БД. (По умолчанию True).
    # @param isCopyExecutionPlan: пометка о необходимости копирования плана выполнения. (По умолчанию False).
    # @param isCopyProperties: пометка о необходимости копирования свойств действия. (По умолчанию True).
    # @param isCheckPropertiesCopyable: пометка о необходимости проверки при копировании свойств, 
    #                                    является ли значение свойства копируемым (CActionPropertyValueType.isCopyable)
    #                                    (По умолчанию True).
    @classmethod
    def copyAction(cls, sourceAction, targetAction, **kwargs):
        isCopyRecordData = kwargs.get('isCopyRecordData', False)
        if isCopyRecordData:
            isCopyActionId = kwargs.get('isCopyActionId', False)
            cls.copyActionRecordData(sourceAction, targetAction, isCopyActionId)

        isCopyAssistants = kwargs.get('isCopyAssistants', True)
        if isCopyAssistants:
            cls.copyActionAssistants(sourceAction, targetAction)

        isCopyExecutionPlan = kwargs.get('isCopyExecutionPlan', False)
        if isCopyExecutionPlan:
            cls.copyActionExecutionPlan(sourceAction, targetAction)

        isCopyProperties = kwargs.get('isCopyProperties', True)
        if isCopyProperties:
            isCheckPropertiesCopyable = kwargs.get('isCheckPropertiesCopyable', True)
            cls.copyActionProperties(sourceAction, targetAction, isCheckPropertiesCopyable)

    def findFireableJobTicketId(self):
        for propertyObject in self._properties:
            if type(propertyObject.type().valueType) == CJobTicketActionPropertyValueType:
                jobTicketId = propertyObject.getValue()
                if jobTicketId:
                    return jobTicketId
        return None

    def getTestProperties(self):
        return [propertyObject
                for propertyObject in self._properties
                if propertyObject.type().testId and propertyObject.isAssigned()
                ]

    def updateSpecifiedName(self):
        name = ' '.join([forceString(propertyObject.getText())
                         for propertyObject in self._properties
                         if propertyObject.isActionNameSpecifier() and propertyObject.getValue()
                         ]
                        )
        self.setSpecifiedName(name)

    def setSpecifiedName(self, name):
        if self._record:
            self._record.setValue('specifiedName', QtCore.QVariant(name))
        self._specifiedName = name

    def initPropertyPresetValues(self):
        actionType = self.getType()
        propertyTypeList = actionType.getPropertiesById().values()
        for propertyType in propertyTypeList:
            self.getPropertyById(propertyType.id)

    def existedAssistantCodeList(self):
        """
        Возвращает список кодов типов ассистентов, имеющихся в событии.
        :return: список имеющихся ассистентов (кодов их типов)
        """
        return self._assistantsByCode.keys()

    def getAssistantId(self, code):
        """
        Возвращает ID ассистента, с типом, код которого передан при вызове.
        :return: ID ассистента для указанного типа или None
        """
        if self._assistantsByCode.has_key(code):
            return self._assistantsByCode[code].id

        return None

    def getAssistantFreeInput(self, code):
        """
        Возвращает имя ассистента, с типом, код которого передан при вызове, в виде строки, введеной с клавиатуры.
        :return: строка с именем ассистента.
        """
        if self._assistantsByCode.has_key(code):
            return self._assistantsByCode[code].freeInput

    def setAssistant(self, code, assistantId=None, assistantFreeInput=u''):
        self.addAssistant(self._assistantsByCode, code, assistantId, assistantFreeInput)

    @staticmethod
    def addAssistant(assistantsByCode, code, assistantId=None, assistantFreeInput=u''):
        """
        Добавляет/изменяет информацию об ассистенте указанного типа (задает его ID или имя в свободной форме) в справочнике.
        :param assistantsByCode: словарь с информацией (smartDict()) об ассистентах по их коду, в котором будут сделаны изменения
        :param code: код типа изменяемого ассистента.
        :param assistantId: id врача, который необходимо установить для заданного типа ассистента.
        :param assistantFreeInput: имя врача, которое необходимо установить для заданного типа ассистента.
        """
        if assistantsByCode.has_key(code):
            assistantInfo = assistantsByCode[code]
        else:
            assistantInfo = smartDict()
            assistantInfo.recordId = None
            assistantsByCode[code] = assistantInfo

        assistantInfo.id = forceRef(assistantId)
        assistantInfo.freeInput = assistantFreeInput
        assistantInfo.hasBeenChanged = True

    @staticmethod
    def loadAssistants(actionId):
        """
        Загружает данные об ассистентах Действия, распределяя их по кодам типов.
        """
        assistantByCode = {}
        db = QtGui.qApp.db
        tableAssistant = db.table('Action_Assistant')
        tableAssistantType = db.table('rbActionAssistantType')

        recordList = db.iterRecordList(table=tableAssistant.innerJoin(tableAssistantType,
                                                                     tableAssistantType['id']
                                                                     .eq(tableAssistant['assistantType_id'])),
                                      cols=[tableAssistantType['code'],
                                            tableAssistantType['isEnabledFreeInput'],
                                            tableAssistant['id'].alias('recordId'),
                                            tableAssistant['person_id'],
                                            tableAssistant['freeInput']],
                                      where=[tableAssistant['action_id'].eq(actionId)])
        for record in recordList:
            code = forceString(record.value('code'))
            isEnabledFreeInput = forceBool(record.value('isEnabledFreeInput'))
            assistantInfo = smartDict()
            assistantInfo.recordId = forceRef(record.value('recordId'))
            assistantInfo.id = forceRef(record.value('person_id'))
            assistantInfo.freeInput = forceString(record.value('freeInput')) if isEnabledFreeInput else u''
            assistantInfo.hasBeenChanged = False
            assistantByCode[code] = assistantInfo

        return assistantByCode

    @staticmethod
    def saveAssistants(actionId, assistantsByCode):
        """
        Сохраняет данные об ассистентах Действия, если они были изменены
        """
        db = QtGui.qApp.db
        tableAssistant = db.table('Action_Assistant')
        tableAssistantType = db.table('rbActionAssistantType')

        savedAssistantTypeIdList = []
        db.transaction()
        try:
            for code, assistantInfo in assistantsByCode.items():
                if assistantInfo.id is None:
                    continue
                assistantTypeId = db.translate(tableAssistantType, tableAssistantType['code'], code,
                                               tableAssistantType['id'])
                if assistantInfo.hasBeenChanged:
                    newRecord = tableAssistant.newRecord()
                    newRecord.setValue('id', QtCore.QVariant(assistantInfo.recordId))
                    newRecord.setValue('action_id', QtCore.QVariant(actionId))
                    newRecord.setValue('assistantType_id', QtCore.QVariant(assistantTypeId))
                    newRecord.setValue('person_id', QtCore.QVariant(assistantInfo.id))
                    newRecord.setValue('freeInput', QtCore.QVariant(assistantInfo.freeInput))
                    db.insertOrUpdate(tableAssistant, newRecord)
                savedAssistantTypeIdList.append(assistantTypeId)
            db.deleteRecord(table=tableAssistant,
                            where=[tableAssistant['action_id'].eq(actionId),
                                   tableAssistant['assistantType_id'].notInlist(savedAssistantTypeIdList)])
            db.commit()
        except:
            db.rollback()


class CNomenclatureExpense:
    def __init__(self, actionId=None):
        self._dirty = False
        self._motionId = None
        self._items = []
        if actionId:
            self._load(actionId)

    def _load(self, actionId):
        pass

    def save(self, actionId):
        pass


def ensureActionTypePresence(actionTypeCode, propTypeList=None, isUseFlatCode=False):
    if not propTypeList:
        propTypeList = []
    db = QtGui.qApp.db
    tableActionType = db.table('ActionType')
    tablePropertyType = db.table('ActionPropertyType')
    codeFieldName = 'code' if not isUseFlatCode else 'flatCode'
    actionTypeRecord = db.getRecordEx(tableActionType, '*', tableActionType[codeFieldName].eq(actionTypeCode))
    if actionTypeRecord:
        actionTypeId = forceRef(actionTypeRecord.value('id'))
    else:
        actionTypeRecord = tableActionType.newRecord()
        actionTypeRecord.setValue(codeFieldName, toVariant(actionTypeCode))
        actionTypeId = db.insertOrUpdate(tableActionType, actionTypeRecord)
    if propTypeList:
        for propTypeDef in propTypeList:
            name = propTypeDef.get('name', None)
            descr = propTypeDef.get('descr', None)
            unit = propTypeDef.get('unit', None)
            typeName = propTypeDef.get('typeName', 'String')
            valueDomain = propTypeDef.get('valueDomain', None)
            isVector = propTypeDef.get('isVector', False)
            norm = propTypeDef.get('norm', None)
            sex = propTypeDef.get('sex', None)
            age = propTypeDef.get('age', None)

            propertyTypeRecord = db.getRecordEx(tablePropertyType, '*',
                                                [tablePropertyType['actionType_id'].eq(actionTypeId),
                                                 tablePropertyType['name'].eq(name)])
            if propertyTypeRecord:
                pass
            else:
                propertyTypeRecord = tablePropertyType.newRecord()
                propertyTypeRecord.setValue('actionType_id', toVariant(actionTypeId))
                propertyTypeRecord.setValue('name', toVariant(name))
                propertyTypeRecord.setValue('descr', toVariant(descr))
                if unit:
                    unitId = db.translate('rbUnit', 'code', unit, 'id')
                    if unitId:
                        propertyTypeRecord.setValue('descr', unitId)
                propertyTypeRecord.setValue('typeName',
                                            toVariant(CActionPropertyValueTypeRegistry.normTypeName(typeName)))
                propertyTypeRecord.setValue('valueDomain', toVariant(valueDomain))
                propertyTypeRecord.setValue('isVector', toVariant(isVector))
                propertyTypeRecord.setValue('norm', toVariant(norm))
                propertyTypeRecord.setValue('sex', toVariant(sex))
                propertyTypeRecord.setValue('age', toVariant(age))
                db.insertRecord(tablePropertyType, propertyTypeRecord)


####################################################################
# сценарий работы c Actions:
#
# 1) создание Action
#    a1 = CAction.createByTypeCode(10)
# 2) загрузка Action
#    a2 = CAction(record=query.record())
# 3) сохранение Action
#    a1.save(eventId)
#    a2.save()
# 4) доступ к свойствам Action
#    x = a2['value']
# 5) изменение свойства Action
#    a2['value'] = x
# 6) очистка/удаление свойства Action
#    del a2['value']
# 7) векторные свойства?
