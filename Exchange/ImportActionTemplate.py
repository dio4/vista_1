#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore

import library.exception

if 'QXmlStreamReader' in QtCore.__dict__:
    from PyQt4.QtCore import QXmlStreamReader

from library.DialogBase import CDialogBase

from Utils import *
from Events.ActionPropertiesTable import CActionPropertiesTableModel
from Events.Action import CAction

from Ui_ImportActionTemplate_Wizard_1 import Ui_ImportActionTemplate_Wizard_1
from Ui_ImportActionTemplate_Wizard_2 import Ui_ImportActionTemplate_Wizard_2
from Ui_ImportActionTemplate_Wizard_3 import Ui_ImportActionTemplate_Wizard_3

from Ui_ImportActionProperty import Ui_ImportActionProperty

from Exchange.ExportActionTemplate import actionTemplateFields,  actionFields, \
        actionRefFields, actionPropertyTypeFields,  unitFields,   actionTypeFields,  \
        actionPropertyTemplateFields, getActionPropertyValue,  ownerFields


actionTemplateRefFields = ('group_id',  'owner_id', 'speciality_id')

def ImportActionTemplate():
    dlg = CImportActionTemplate(forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportActionTemplateFileName', '')),
        fullLog = forceBool(getVal(QtGui.qApp.preferences.appPrefs, \
            'ImportActionTemplateFullLog', 'False')),
        importAll = forceBool(getVal(QtGui.qApp.preferences.appPrefs, \
            'ImportActionTemplateImportAll', 'False')))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportActionTemplateFileName'] \
        = toVariant(dlg.fileName)
    QtGui.qApp.preferences.appPrefs['ImportActionTemplateFullLog'] \
        = toVariant(dlg.fullLog)
    QtGui.qApp.preferences.appPrefs['ImportActionTemplateImportAll'] \
        = toVariant(dlg.importAll)


class CMyXmlStreamReader(QXmlStreamReader):
    def __init__(self,  parent,  showLog = False):
        QXmlStreamReader.__init__(self)
        self.parent = parent
        self.db=QtGui.qApp.db
        self.tableAction = tbl('Action')
        self.tableActionProperty = tbl('ActionProperty')
        self.tableActionPropertyTemplate = tbl('ActionPropertyTemplate')
        self.tableActionPropertyType = tbl('ActionPropertyType')
        self.tableActionType = tbl('ActionType')
        self.tableActionTemplate = tbl('ActionTemplate')
        self.tableSpeciality = tbl('rbSpeciality')
        self.tablePerson = tbl('Person')
        self.tableUnit = tbl('rbUnit')
        self.nadded = 0
        self.ncoincident = 0
        self.nprocessed = 0
        self.nupdated = 0
        self.mapActionTemplateKeyToId = {}
        self.mapActionPropertyTemplateKeyToId = {}
        self.mapActionTypeKeyToId = {}
        self.mapSpecialityKeyToId = {}
        self.mapOwnerKeyToId = {}
        self.mapUnitKeyToId = {}
        self.showLog = showLog
        self.actionList = []
        self.recursionLevel = 0


    def raiseError(self,  str):
        QXmlStreamReader.raiseError(self, u'[%d:%d] %s' % (self.lineNumber(), self.columnNumber(), str))


    def readNext(self):
        QXmlStreamReader.readNext(self)
        self.parent.progressBar.setValue(self.device().pos())

    def getEventPropertyParams(self, eventProperty):
        if eventProperty['type'] == 'action':
            fieldList = self.eventTypeActionFieldNamesExist
            refFields = self.eventTypeActionRefFieldNamesExist
            table = self.tableEventTypeAction
        elif eventProperty['type'] == 'diagnostic':
            fieldList = self.eventTypeDiagnosticFieldNamesExist
            refFields = self.eventTypeDiagnosticRefFieldNamesExist
            table = self.tableEventTypeDiagnostic
        elif eventProperty['type'] == 'form':
            fieldList = self.eventTypeFormFieldNamesExist
            refFields = self.eventTypeFormRefFieldNamesExist
            table = self.tableEventTypeForm
        else:
            self.raiseError(u'! Неизвестный тип свойства события: "%s"'\
                      % eventProperty['type'])
            return None

        return (table,  fieldList,  refFields)


    def log(self, str,  forceLog = False):
        if self.showLog or forceLog:
            self.parent.logBrowser.append(str)
            self.parent.logBrowser.update()


    def readFile(self, device,  makeActionList = False):
#        u''' Разбирает и загружает xml из указанного устройства device
#            если makeActionList == True - составляет список найденных
#            действий для загрузки'''

        self.setDevice(device)
        xmlVersion = '1.01'

        try:
            while (not self.atEnd()):
                self.readNext()

                if self.isStartElement():
                    if self.name() == 'ActionTemplateExport':
                        if self.attributes().value('version') == xmlVersion:
                            self.readData(makeActionList)
                        else:
                            self.raiseError(u'Версия формата "%s" не поддерживается. Должна быть "%s"' \
                                % (self.attributes().value('version').toString(), xmlVersion))
                    else:
                        self.raiseError(u'Неверный формат экспорта данных.')

                if self.hasError() or self.parent.aborted:
                    return False

        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
            self.log(u'! Ошибка ввода-вывода: %s' % msg,  True)
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            self.log(u'! Ошибка: %s' % unicode(e),  True)
            return False


        return not self.hasError()


    def readData(self,  makeActionList):
        assert self.isStartElement() and self.name() == 'ActionTemplateExport'

        # очищаем список событий перед заполнением
        if makeActionList:
            self.actionList = []

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == 'ActionTemplate'):
                    self.readActionTemplate(makeActionList)
                else:
                    self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break


    def readActionTemplate(self,  makeActionList):
        assert self.isStartElement() and self.name() == 'ActionTemplate'

        actionTemplateProperties = []
        actionTemplate = {}
        service = None
        finance = None
        purpose = None
        groupId = None

        if self.parent.aborted:
            return None

        if makeActionList:
            self.actionList.append((forceString(self.attributes().value('code').toString()), \
                                            forceString(self.attributes().value('name').toString())))
            self.log(u' Найден шаблон действия: (%s) "%s"' % self.actionList[-1])
        else:
            for x in actionTemplateFields:
                actionTemplate[x] = forceString(self.attributes().value(x).toString())

            name = actionTemplate['name']
            code = actionTemplate['code']
            self.log(u'Шаблон действия: "%s" ("%s")[строка "%d": колонка "%d"]' %\
                    (name, code,  self.lineNumber(), self.columnNumber()))

        while not self.atEnd():
            QtGui.qApp.processEvents()
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if not makeActionList:
                    if (self.name() == 'Action'):
                        actionTemplate['action'] = self.readAction()
                    elif (self.name() == 'Group'):
                        actionTemplate['group_id'] = self.readGroup(makeActionList)
                    elif (self.name() == 'Owner'):
                        actionTemplate['owner'] = self.readOwner()
                        actionTemplate['owner_id'] = actionTemplate['owner']['id']
                    elif (self.name() == 'Speciality'):
                        actionTemplate['speciality'] = self.readSpeciality()
                        actionTemplate['speciality_id'] = actionTemplate['speciality']['id']
                    else:
                        self.readUnknownElement()
                else:
                    # молча пропускаем все элементы, т.к мы только
                    # создаем список событий
                    self.readUnknownElement(False)

        if makeActionList:
            return None

        groupId = actionTemplate.get('group_id')
        id = self.lookupActionTemplate(name,  code,  groupId)

        if self.hasError() or self.parent.aborted:
            return None

        try:
            if id:
                self.log(u'%% Найдена похожая запись (id=%d)' % id)
                # такое действие уже есть. надо проверить все его свойства
                if not self.parent.parent.page(0).rbSkip.isChecked():
                    if not self.isCoincidentActionTemplate(actionTemplate,  id):
                        # есть разхождения в полях. спрашиваем у пользователя что делать
                        self.log(u' поля различаются')
                        if self.parent.parent.page(0).rbAskUser.isChecked():
                            self.log(u' Запрос действия пользователя: ')
                            if QtGui.QMessageBox.question(self.parent, u'Записи различаются',
                                                        self.prepareMessageBoxText(actionTemplate, id) ,
                                                        QtGui.QMessageBox.No|QtGui.QMessageBox.Yes,
                                                        QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                                self.log(u' - обновляем')
                                self.updateActionTemplate(actionTemplate, id)
                            else:
                                self.log(u' - пропускаем')
                        elif self.parent.parent.page(0).rbUpdate.isChecked():
                            self.log(u' - обновляем')
                            self.updateActionTemplate(actionTemplate,  id)

                    # проверим свойства у действия.
                    ourAction = actionTemplate.get('action',  0)
                    record = self.db.getRecord(self.tableActionTemplate, 'action_id', id)
                    extActionId = forceRef(record.value('action_id')) if record else None

                    if ourAction and extActionId:
                        cond = []
                        cond.append(self.tableActionProperty['action_id'].eq(toVariant(extActionId)))
                        idList = self.db.getIdList(self.tableActionProperty, where=cond)

                        if not (idList == [] and ourAction['properties'] == []):

                            for x in ourAction['properties']:
                                QtGui.qApp.processEvents()
                                flag = False

                                for propId in idList:
                                    if self.isCoincidentActionProperty(x, propId):
                                        flag = True
                                        break

                                if not flag:
                                    self.log(u' Обнаружено новое свойство шаблона действия')

                                    if self.parent.parent.page(0).rbAskUser.isChecked():
                                        self.log(u' Запрос действия пользователя: ')
                                        dlg = CActionPropertyReplaceDialog(actionTemplate, x, extActionId,  self.parent)
                                        dlg.exec_()

                                        if dlg.updateData: # пользователь нажал кнопку обновить
                                            self.log(u'   - выбор пользователя: обновить')
                                            self.updateActionProperty(x,  extActionId,  dlg.getSelectedItemsList())
                                        else:
                                            self.log(u'   - выбор пользователя: пропускаем')
                                    elif self.parent.parent.page(0).rbUpdate.isChecked():
                                        self.log(u'  + обновляем')
                                        self.addActionProperty(x,  extActionId)
                                    else:
                                        self.log(u'  + пропускаем')

                else: # rbSkip == True
                    self.log(u' - пропускаем')


                self.ncoincident += 1
            else:
                self.log(u'% Сходные записи не обнаружены. Добавляем')
                if self.addActionTemplate(actionTemplate):
                    self.nadded += 1
                else:
                    self.log(u'<b><font color=orange>Шаблон ("%s") "%s" не добавлен.<\font><\b>' %\
                                (code, name),  True)

        except library.exception.CDatabaseException,  e:
            self.log(u'!<b><font color=red>ОШИБКА<\font><\b>'
                        u' работы с БД: "%s"'  % unicode(e),  True)
            QtGui.QMessageBox.critical(
                self.parent,
                u'Ошибка базы данных',
                unicode(e),
                QtGui.QMessageBox.Close)
            return None

        self.nprocessed += 1
        self.parent.statusLabel.setText(
                u'импорт шаблонов действий: %d добавлено; %d обновлено; %d совпадений; %d обработано' % \
                (self.nadded, self.nupdated,  self.ncoincident,  self.nprocessed))

        return id


    def readOwner(self):
        assert self.isStartElement() and self.name() == 'Owner'
        owner = {}

        for fieldName in ownerFields:
            owner[fieldName] = forceString(self.attributes().value(fieldName).toString())

        owner['id'] = self.lookupOwner(owner)

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
               break

        return owner


    def readSpeciality(self):
        assert self.isStartElement() and self.name() == 'Speciality'
        speciality = {}

        for fieldName in ('code', 'name'):
            speciality[fieldName] = forceString(self.attributes().value(fieldName).toString())

        speciality['id'] = self.lookupSpeciality(speciality['name'], speciality['code'])

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
               break

        return speciality


    def readAction(self):
        assert self.isStartElement() and self.name() == 'Action'
        action = {}
        action['properties'] = []

        for fieldName in actionFields:
            action[fieldName] = forceString(self.attributes().value(fieldName).toString())

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == 'ActionProperty'):
                    action['properties'].append(self.readActionProperty())
                elif (self.name() == 'ActionType'):
                    action['actionType'] = self.readActionType()
                    action['actionType_id'] = self.lookupActionType(action['actionType'])
                else:
                    self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
               break

        return action


    def readActionType(self):
        assert self.isStartElement() and self.name() == 'ActionType'
        actionType = {}

        for fieldName in actionTypeFields:
            actionType[fieldName] = forceString(self.attributes().value(fieldName).toString())

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == 'ActionType'):
                    actionType['group'] = self.readActionType()
                else:
                    self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
               break

        return actionType


    def readActionProperty(self):
        assert self.isStartElement() and self.name() == 'ActionProperty'
        actionProperty = {}

        for x in ('norm',  'value'):
            actionProperty[x] = forceString(self.attributes().value(x).toString())

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == 'ActionPropertyType'):
                    actionProperty['type'] = self.readActionPropertyType()
                    actionProperty['type_id'] = actionProperty['type']['id']
                elif (self.name() == 'Unit'):
                    actionProperty['unit'] = self.readUnit()
                    actionProperty['unit_id'] = actionProperty['unit']['id']
                else:
                    self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
               break

        return actionProperty


    def readGroup(self,  makeActionList):
        assert self.isStartElement() and self.name() == 'Group'

        group_id = None
        self.log(u'Группа:' )

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == 'ActionTemplate'):
                    if self.recursionLevel < 10:
                        self.recursionLevel += 1
                        group_id = self.readActionTemplate(makeActionList)
                        self.recursionLevel -= 1
                    else:
                        self.raiseError(u'Уровень вложенности групп больше 10')
                else:
                    self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break

        return group_id


    def readActionPropertyType(self):
        assert self.isStartElement() and self.name() == 'ActionPropertyType'

        actionPropertyType = {}
        actionType = None

        for x in actionPropertyTypeFields:
            actionPropertyType[x] = forceString(self.attributes().value(x).toString())

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break


            if self.isStartElement():
                if (self.name() == 'PropertyTemplate'):
                    actionPropertyType['template'] = self.readActionPropertyTemplate()
                    actionPropertyType['template_id'] = actionPropertyType['template']['id']
                elif (self.name() == 'ActionType'):
                    actionType = self.readActionType()
                else:
                    self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break

        if actionType:
            typeId = self.lookupActionType(actionType)
            if typeId:
                actionPropertyType['id'] = self.lookupActionPropertyType(actionPropertyType,  typeId)
            else:
                self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                 u'Для свойства действия "%s", тип: "%s"'
                 u'тип не импортирован, свойство не загружено.' % \
                 (actionPropertyType['name'], actionPropertyType['typeName']),  True)

        return actionPropertyType


    def readActionPropertyTemplate(self):
        assert self.isStartElement() and self.name() == 'PropertyTemplate'

        actionPropertyTemplate = {}

        for x in actionPropertyTemplateFields:
            actionPropertyTemplate[x] = forceString(self.attributes().value(x).toString())

        actionPropertyTemplate['id'] = self.lookupActionPropertyTemplate(actionPropertyTemplate)

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break

        return actionPropertyTemplate


    def readUnit(self):
        assert self.isStartElement() and self.name() == 'Unit'

        unit = {}

        for x in unitFields:
            unit[x] = forceString(self.attributes().value(x).toString())

        self.log(u'Ед.изм.: %s, код %s' %(unit['name'], unit['code']))
        unit['id'] = self.lookupUnit(unit['name'], unit['code'])

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break

        return unit


    def readUnknownElement(self, report = True):
        """ Читает неизвестный элемент, и сообщает об этом,
            если report ==True """

        assert self.isStartElement()

        if report:
            self.log(u'Неизвестный элемент: '+self.name().toString())

        while (not self.atEnd()):
            self.readNext()

            if (self.isEndElement()):
                break

            if (self.isStartElement()):
                self.readUnknownElement(report)

            if self.hasError() or self.parent.aborted:
                break


    def lookupActionType(self, actionType):
        group = actionType.get('group',  None)
        actionType['group_id'] = self.lookupActionType(group) if group else None
        key = (actionType['code'], actionType['name'], \
                    actionType['class'], actionType['group_id'])
        id = self.mapActionTypeKeyToId.get(key,  None)

        if id:
            return id

        cond = []

        for x in ('code', 'name', 'class',  'group_id'):
            if actionType[x]:
                cond.append(self.tableActionType[x].eq(toVariant(actionType[x])))

        record = self.db.getRecordEx(self.tableActionType, ['id'], where=cond)

        if record:
            id = forceRef(record.value('id'))
            self.mapActionTypeKeyToId[key] = id
            return id

        self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
                 u'Тип действия "%s", код: "%s", класс "%s"'
                 u'не найден в базе-приемнике.' % \
                 (actionType['name'], actionType['code'], actionType['class']),  True)
        return None


    def lookupActionTemplate(self, name,  code,  groupId):
        """ Поиск похожего шаблона действия по имени и коду"""

        key = (code, name,  groupId)
        id = self.mapActionTemplateKeyToId.get(key,  None)

        if id:
            return id

        cond = []
        cond.append(self.tableActionTemplate['code'].eq(toVariant(code)))
        cond.append(self.tableActionTemplate['name'].eq(toVariant(name)))

        if groupId:
            cond.append(self.tableActionTemplate['group_id'].eq(toVariant(groupId)))

        record = self.db.getRecordEx(self.tableActionTemplate, ['id'], where=cond)

        if record:
            id = forceRef(record.value('id'))
            self.mapActionTemplateKeyToId[key] = id
            return id

        return None


    def lookupActionPropertyTemplate(self, actionPropertyTemplate):
        """ Поиск похожего шаблона действия по имени и коду"""

        code = actionPropertyTemplate['code']
        name = actionPropertyTemplate['name']

        key = (code, name)
        id = self.mapActionPropertyTemplateKeyToId.get(key,  None)

        if id:
            return id

        cond = []
        cond.append(self.tableActionPropertyTemplate['code'].eq(toVariant(code)))
        cond.append(self.tableActionPropertyTemplate['name'].eq(toVariant(name)))

        record = self.db.getRecordEx(self.tableActionPropertyTemplate, ['id'], where=cond)

        if record:
            id = forceRef(record.value('id'))
            self.mapActionPropertyTemplateKeyToId[key] = id
            return id

        return None


    def lookupActionPropertyType(self, actionPropertyType, id):
        cond = []

        # ищем похожие свойства по название-ед.измерения
        cond.append(self.tableActionPropertyType['actionType_id'].eq(toVariant(id)))
        for x in actionPropertyTypeFields:
            p = actionPropertyType[x]
            if p:
                cond.append(self.tableActionPropertyType[x].eq(toVariant(p)))

        for x in ('unit_id', 'template_id'):
            id = forceRef(actionPropertyType.get(x, None))
            if id:
                cond.append(self.tableActionPropertyType[x].eq(toVariant(id)))

        record = self.db.getRecordEx(self.tableActionPropertyType,  'id',  where = cond)

        if record:
            return forceRef(record.value('id'))

        return None


    def lookupSpeciality(self, name, code):
        """ Для идентификации специальности
            используем имя и код"""

        key = (name, code)
        id = self.mapSpecialityKeyToId.get(key,  None)

        if id:
            return id

        cond = []
        cond.append(self.tableSpeciality['name'].eq(toVariant(name)))
        cond.append(self.tableSpeciality['code'].eq(toVariant(code)))
        record = self.db.getRecordEx(self.tableSpeciality, ['id'], where=cond)

        if record:
            id = forceRef(record.value('id'))
            self.mapSpecialityKeyToId[key] = id
            return id

        return None


    def lookupOwner(self, ownerInfo):
        """ Для идентификации специальности
            используем имя и код"""

        key = (ownerInfo['lastName'], ownerInfo['firstName'], \
                    ownerInfo['patrName'])
        id = self.mapOwnerKeyToId.get(key,  None)

        if id:
            return id

        cond = []

        for x in ('lastName',  'firstName',  'patrName'):
            cond.append(self.tablePerson[x].eq(toVariant(ownerInfo[x])))

        record = self.db.getRecordEx(self.tablePerson, ['id'], where=cond)

        if record:
            id = forceRef(record.value('id'))
            self.mapOwnerKeyToId[key] = id
            return id

        return None


    def lookupUnit(self, name, code):
        """Для идентификации единиц измерения используем имя и код"""

        key = (name, code)
        id = self.mapUnitKeyToId.get(key,  None)

        if id:
            return id

        cond = []
        cond.append(self.tableUnit['name'].eq(toVariant(name)))
        cond.append(self.tableUnit['code'].eq(toVariant(code)))
        record = self.db.getRecordEx(self.tableUnit, ['id'], where=cond)

        if record:
            id = forceRef(record.value('id'))
            self.mapUnitKeyToId[key] = id
            return id

        return None


    def isCoincidentActionTemplate(self,  actionTemplate,  id):
        record = self.db.getRecord(self.tableActionTemplate, \
                                actionTemplateFields+actionTemplateRefFields+
                                ('action_id', ), id)

        if record:
            for x in actionTemplateFields:
                if forceString(record.value(x)) != forceString(actionTemplate[x]):
                    return False

            for x in actionTemplateRefFields:
                a = forceRef(actionTemplate.get(x))
                b = forceRef(record.value(x))

                if ((a or (not b)) and (a != b)):
                    return False

            # проверим свойства у действия.
            ourAction = forceRef(actionTemplate.get('action',  0))
            extActionId = forceRef(record.value('action_id'))

            if ourAction and extActionId:
                return True
            elif not ourAction and not extActionId:
                return True
            else:
                return False

            # Свойста действия проверим отдельно.

        return False


    def prepareMessageBoxText(self, actionTemplate, id):
        record = self.db.getRecord(self.tableActionTemplate, \
                                actionTemplateFields+actionTemplateRefFields+('action_id', ), id)
        str = u'''<h3>Обнаружены следующие различия в записях:</h3>\n\n\n
                        <table>
                        <tr>
                            <td><b>Название поля</b></td>
                            <td align=center><b>Новое</b></td>
                            <td align=center><b>Исходное</b></td>
                        </tr>'''

        if record:
            for x in actionTemplateFields:
                str += '<tr><td><b> '+x+': </b></td>'

                if forceString(record.value(x)) != forceString(actionTemplate[x]):
                    str += '<td align=center bgcolor=''red''> '
                else:
                    str += '<td align=center>'

                str += forceString(actionTemplate[x])+' </td><td align=center>' \
                        + forceString(record.value(x)) + '</td></tr>\n'

            for x in actionTemplateRefFields+('action_id', ):
                a = forceRef(actionTemplate.get(x))
                b = forceRef(record.value(x))

                str += u'<tr><td><b> '+x

                if a != b:
                    str += u': </b></td><td align=center bgcolor=red>'
                else:
                    str += u': </b></td><td align=center>'

                str += forceString(actionTemplate.get(x,  '-'))
                str += u' </td><td align=center>' + forceString(record.value(x)) \
                            + u'</td></tr>\n'

            str += u'</table>\n\n<p align=center>Обновить?</p>'
        return str


    def isCoincidentActionProperty(self, property,  id):
        record = self.db.getRecord(self.tableActionProperty, '*', id)

        if not record:
            return False

        if forceString(record.value('norm')) != property.get('norm',  ''):
            return False

        for x in ('unit_id',  'type_id'):
            if forceRef(record.value(x)) != forceRef(property.get(x,  None)):
                return False

        value = property.get('value',  None)
        id = forceRef(record.value('id'))

        if id:
            extValue = getActionPropertyValue(id,  property['type']['typeName'])
            return value == extValue

        return value == id


    def addActionTemplate(self, actionTemplate):

        if actionTemplate.has_key('action'):
            actionTemplate['action_id'] = self.addAction(actionTemplate['action'])

        record = self.tableActionTemplate.newRecord()

        for x in actionTemplateFields+('action_id', 'group_id', 'owner_id',  'speciality_id'):
            value = actionTemplate.get(x,  None)
            if value:
                record.setValue(x,  toVariant(value))

        actionTemplateId = self.db.insertRecord(self.tableActionTemplate, record)
        return actionTemplateId


    def addAction(self,  action):
        actionTypeId = action.get('actionType_id',  None)

        if not actionTypeId:
            self.log(u'<b><font color=red>ОШИБКА<\font><\b>:'
            u'Для действия "(%s) %s"'
            u'не импортирован тип действия. Шаблон не загружен.'
            % (action.get('code', '-'),  action.get('name', '-')))
            return None

        record = self.tableAction.newRecord()

        for x in actionFields + actionRefFields:
            value = action.get(x,  None)
            if value:
                record.setValue(x,  toVariant(value))

        actionId = self.db.insertRecord(self.tableAction, record)

        for property in action['properties']:
            self.addActionProperty(property,  actionId)

        return actionId


    def addActionProperty(self,  property,  actionId):
        typeId = forceRef(property.get('type_id',  None))
        type = property.get('type',  None)

        if typeId and type:

            record = self.tableActionProperty.newRecord()
            record.setValue('action_id',  toVariant(actionId))

            for x in ('type_id',  'unit_id'):
                value = property.get(x,  None)
                if value:
                    record.setValue(x,  toVariant(value))

            id = self.db.insertRecord(self.tableActionProperty, record)
            typeName = forceString(type.get('typeName',  ''))

            if typeName != '':
                # определяем тип значения и пишем его.

                if typeName in ('Text',  'Constructor', u'Жалобы'):
                    typeName = 'String'

                if typeName == 'RLS':
                    typeName = 'Integer'

                t = tbl('ActionProperty_%s' % typeName)
                valueRecord = t.newRecord()

                if property['value']:
                    valueRecord.setValue('value',  toVariant(property['value']))

                valueRecord.setValue('id',  toVariant(id))
                self.db.insertRecord(t, valueRecord)
            else:
                self.log(u'! Имя типа действия (id=%d) не определено' % id)
                self.log(u'!  значение свойства ("%s")  не добавлено. ' % property['value'])

        else:
            typeName = type.get('typeName', '') if type else ''
            self.log(u'! В БД отсутствует тип действий "%s"' % typeName)
            self.log(u'! Свойство не добавлено.')

    def updateActionTemplate(self,  actionTemplate, id):
        record = self.db.getRecord(self.tableActionTemplate,  '*', id)

        for x in actionTemplateFields + \
            ('action_id', 'group_id', 'owner_id',  'speciality_id'):
            val = actionTemplate.get(x, None)
            if val:
                record.setValue(x, toVariant(val))

        self.db.updateRecord(self.tableActionTemplate, record)
        self.nupdated += 1

    def updateActionProperty(self, property,  actionId,  propertyList):

        if propertyList == []:
            self.addActionProperty(property,  actionId)
        else:
            for x in propertyList:
                x.setValue(property['value'])
                x.save(actionId)


class CActionPropertyReplaceDialog(CDialogBase, Ui_ImportActionProperty):
    def __init__(self, actionTemplate, actionProperty,  actionId,  parent=None):
        CDialogBase.__init__(self, parent)
        self.tableName = 'ActionProperty'
        self.parent = parent
        self.actionTemplate = actionTemplate
        self.actionProperty = actionProperty
        self.actionId = actionId
        self.selectedIds = []
        self.updateData = False
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()


    def preSetupUi(self):
        self.addModels('Table', CActionPropertiesTableModel(self))


    def postSetupUi(self):
        self.setModels(self.tblNew,   self.modelTable, self.selectionModelTable)
        self.tblNew.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.setActionId()
        self.selectionModelTable.clearSelection()
        self.tblNew.setFocus(Qt.OtherFocusReason)
        self.txtActionInfo.setHtml(self.getActionBanner())
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint)


    def setActionId(self):
        if self.actionId:
            db = QtGui.qApp.db
            record = db.getRecord('Action', '*', self.actionId)
        else:
            record = None

        if record:
            self.setAction(CAction(record=record))
        else:
            self.setAction(None)


    def setAction(self, action):
        self.action = action
        if action:
            actionTypeId = action.getType().id
        else:
            actionTypeId = None
        if self.action:
            self.tblNew.model().setAction(self.action, None, 0, None)
            self.tblNew.resizeRowsToContents()


    def getSelectedItemsList(self):
        list = []

        for x in self.selectionModelTable.selectedRows():
            propertyType = self.modelTable.propertyTypeList[x.row()]
            list.append(self.modelTable.action.getProperty(propertyType.name))

        return list

    def updateBtnReplaceText(self):
        if self.selectionModelTable.selectedRows() == []:
            self.btnReplace.setText(u'Добавить')
        else:
            self.btnReplace.setText(u'Заменить')

        self.btnReplace.update()


    @QtCore.pyqtSlot()
    def on_btnSelectAll_clicked(self):
        self.tblNew.selectAll()


    @QtCore.pyqtSlot()
    def on_btnClearSelection_clicked(self):
        self.selectionModelTable.clearSelection()
        self.updateBtnReplaceText()


    @QtCore.pyqtSlot()
    def on_btnReplace_clicked(self):
        self.updateData = True
        if self.selectionModelTable.selectedRows() == []:
            self.updateData = QtGui.QMessageBox.question(self.parent, u'Импорт свойств действия',
                                            u'Вы не выбрали ни одной записи для замены.\nДобавить новое свойство типа действия?',
                                            QtGui.QMessageBox.No|QtGui.QMessageBox.Yes,
                                            QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes
        self.close()

    @QtCore.pyqtSlot()
    def on_btnSkip_clicked(self):
        self.updateData = False
        self.close()


    @QtCore.pyqtSlot(QModelIndex)
    def on_tblNew_clicked(self, index):
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.updateBtnReplaceText()


    def getActionBanner(self):
        t = self.actionTemplate
        p = self.actionProperty

        str = u'''Шаблон действия:<br>
        Название: <b>%s</b>, код: <b>%s</b>, пол: <b>%s</b>,<br>
        возраст: <b>%s</b>, id группы "<b>%d</b>".<br><br>
        ''' % (t['name'], t['code'], formatSex(t['sex']), t['age'], t['group_id'])

        str += u''' Свойство:<br>
        Значение: <b>%s</b>.<br>
        Тип: <b>%s</b> (<b>%s</b>), код шаблона <b>%s</b><br>
        нормировка: <b>%s</b>.
        ''' % (p['value'],  p['type']['name'],  p['type']['typeName'],
                  p['norm'], p['type']['template_id'])

        if p.has_key('unit'):
            str += u''',единица измерения: <b>%s(%s)</b>.<br>''' % (p['unit']['name'],
                                                                                                p['unit']['code'],)

        return u'<html><body>%s</body><html>' % str


class CImportActionTemplateWizardPage1(QtGui.QWizardPage, Ui_ImportActionTemplate_Wizard_1):
    def __init__(self,  parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setTitle(u'Параметры загрузки')
        self.setSubTitle(u'Выбор источника импорта')
        self.isPreImportDone = False
        self.aborted = False
        self.setupUi(self)
        self.progressBar.reset()
        self.progressBar.setValue(0)
        self.edtFileName.setText(parent.fileName)
        self.chkFullLog.setChecked(parent.fullLog)
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)


    def isComplete(self):
        return self.edtFileName.text()!= ''


    def validatePage(self):
        self.import_()
        return self.isPreImportDone


    def abort(self):
        self.aborted = True


    def import_(self):
        self.isPreImportDone = False
        self.aborted = False
        success,  result = QtGui.qApp.call(self, self.doPreImport)

        if self.aborted or not success:
            self.progressBar.setText(u'Прервано')
        else:
            self.isPreImportDone = result


    def doPreImport(self):
        inFile = QtCore.QFile(self.parent.fileName)
        if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт типов событий',
                                      QString(u'Не могу открыть файл для чтения %1:\n%2.')
                                      .arg(self.parent.fileName)
                                      .arg(inFile.errorString()))
            return False
        else:
            self.progressBar.reset()
            self.progressBar.setValue(0)
            self.progressBar.setFormat(u'%v байт')
            self.statusLabel.setText(u'Составления списка событий для загрузки')
            self.progressBar.setMaximum(max(inFile.size(), 1))
            myXmlStreamReader = CMyXmlStreamReader(self)
            if (myXmlStreamReader.readFile(inFile,  True)):
                self.progressBar.setText(u'Готово')
                # сохраняем список найденных типов событий в предке
                self.parent.actionList = myXmlStreamReader.actionList
                self.statusLabel.setText(u'Найдено %d событий для импорта' % len(self.parent.actionList))
            else:
                self.progressBar.setText(u'Прервано')
                if self.aborted:
                    self.logBrowser.append(u'! Прервано пользователем.')
                else:
                    self.logBrowser.append(u'! Ошибка: файл %s, %s' % (self.parent.fileName, myXmlStreamReader.errorString()))
                return False

        return True

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        self.parent.fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (*.xml)')
        if self.parent.fileName != '' :
            self.edtFileName.setText(self.parent.fileName)
            self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot(QString)
    def on_edtFileName_textChanged(self,  text):
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.parent.fileName = forceString(text)


    @QtCore.pyqtSlot(bool)
    def on_chkFullLog_toggled(self,  checked):
        self.parent.fullLog = checked


class CImportActionTemplateWizardPage2(QtGui.QWizardPage, Ui_ImportActionTemplate_Wizard_2):
    def __init__(self,  parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setTitle(u'Параметры загрузки')
        self.setSubTitle(u'Выбор шаблонов действий')
        self.setupUi(self)
        self.chkImportAll.setChecked(parent.importAll)
        #self.postSetupUi()


    def isComplete(self):
        return self.parent.importAll or self.parent.selectedItems != []


    def initializePage(self):
        self.tblEvents.setRowCount(len(self.parent.actionList))
        self.tblEvents.setColumnCount(2) # code, name
        self.tblEvents.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.tblEvents.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tblEvents.setHorizontalHeaderLabels((u'Код',  u'Наименование'))
        self.tblEvents.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tblEvents.horizontalHeader().setStretchLastSection(True)
        self.tblEvents.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tblEvents.verticalHeader().hide()

        i = 0

        for x in self.parent.actionList:
            eventNameItem = QtGui.QTableWidgetItem(x[1])
            eventCodeItem = QtGui.QTableWidgetItem(x[0])
            eventNameItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            eventCodeItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tblEvents.setItem(i, 0,  eventCodeItem)
            self.tblEvents.setItem(i, 1,  eventNameItem)
            i += 1

    @QtCore.pyqtSlot(bool)
    def on_chkImportAll_toggled(self,  checked):
        self.parent.importAll = checked
        self.tblEvents.setEnabled(not checked)
        self.btnClearSelection.setEnabled(not checked)

        if checked:
            self.statusLabel.setText(u'Выбраны все события для импорта')
        else:
            self.statusLabel.setText(u'Выбрано %d событий для импорта' % \
                                        (len(self.parent.selectedItems)/2))

        self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_tblEvents_itemSelectionChanged(self):
        self.parent.selectedItems = self.tblEvents.selectedIndexes()
        self.statusLabel.setText(u'Выбрано %d событий для импорта' % \
                                        (len(self.parent.selectedItems)/2))
        self.emit(QtCore.SIGNAL('completeChanged()'))


class CImportActionTemplateWizardPage3(QtGui.QWizardPage, Ui_ImportActionTemplate_Wizard_3):
    def __init__(self,  parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setTitle(u'Загрузка')
        self.setSubTitle(u'Импорт типов событий')
        self.setupUi(self)
        self.isImportDone = False
        self.aborted = False
        self.connect(self, QtCore.SIGNAL('import()'), self.import_, Qt.QueuedConnection)
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.btnAbort.setEnabled(False)


    def isComplete(self):
        return self.isImportDone


    def initializePage(self):
        self.emit(QtCore.SIGNAL('import()'))


    def abort(self):
        self.aborted = True


    def import_(self):
        self.isImportDone = False
        self.aborted = False
        success,  result = QtGui.qApp.call(self, self.doImport)

        if self.aborted or not success:
            self.progressBar.setText(u'Прервано')


    def doImport(self):
        inFile = QtCore.QFile(self.parent.fileName)
        if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт типов событий',
                                      QString(u'Не могу открыть файл для чтения %1:\n%2.')
                                      .arg(self.parent.fileName)
                                      .arg(inFile.errorString()))
            return
        else:
            self.btnAbort.setEnabled(True)
            self.progressBar.reset()
            self.progressBar.setValue(0)
            self.progressBar.setFormat(u'%v байт')
            self.progressBar.setMaximum(max(inFile.size(), 1))
            myXmlStreamReader = CMyXmlStreamReader(self,  self.parent.fullLog)
            if (myXmlStreamReader.readFile(inFile)):
                self.progressBar.setText(u'Готово')
                self.isImportDone = True
                self.emit(QtCore.SIGNAL('completeChanged()'))
            else:
                self.progressBar.setText(u'Прервано')
                if self.aborted:
                    self.logBrowser.append(u'! Прервано пользователем.')
                else:
                    self.logBrowser.append(u'! Ошибка: файл %s, %s' % (self.parent.fileName, myXmlStreamReader.errorString()))
            self.btnAbort.setEnabled(False)


    @QtCore.pyqtSlot()
    def on_btnAbort_clicked(self):
        self.abort()



class CImportActionTemplate(QtGui.QWizard):
    def __init__(self, fileName = '',  importAll = False,  fullLog = False,  parent=None):
        QtGui.QWizard.__init__(self, parent, Qt.Dialog)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.setWindowTitle(u'Импорт шаблонов действий')
        self.fullLog = fullLog
        self.importAll = importAll
        self.selectedItems = []
        self.actionList =[]
        self.fileName= fileName
        self.addPage(CImportActionTemplateWizardPage1(self))
        self.addPage(CImportActionTemplateWizardPage2(self))
        self.addPage(CImportActionTemplateWizardPage3(self))
