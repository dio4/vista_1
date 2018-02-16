#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtCore
if 'QXmlStreamReader' in QtCore.__dict__:
    from PyQt4.QtCore import QXmlStreamReader

from library.TableModel import *
from library.DialogBase import CDialogBase
from Exchange.ExportActions import exportFormatVersion,  serviceFields,  \
    unitFields, actionTypeFields, actionPropertyTypeFields

from Utils import *

from Ui_ImportActions import Ui_ImportActions
from Ui_ImportActionProperty import Ui_ImportActionProperty


actionTypeRefFields = ('group_id', 'nomenclativeService_id')
actionPropertyTypeRefFields = ('template_id',  'actionType_id',  'unit_id')


def ImportActionType():
    fileName = forceString(getVal(
        QtGui.qApp.preferences.appPrefs, 'ImportActionTypeFileName', ''))
    fullLog = forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'ImportActionFullLog', False))
    dlg = CImportActionType(fileName)
    dlg.chkFullLog.setChecked(fullLog)
    dlg.chkUseFlatCode.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'ImportActionUseFlatCode', False)))
    dlg.exec_()
    QtGui.qApp.preferences.appPrefs['ImportActionTypeFileName'] = toVariant(dlg.fileName)
    QtGui.qApp.preferences.appPrefs['ImportActionFullLog'] = toVariant(dlg.chkFullLog.isChecked())
    QtGui.qApp.preferences.appPrefs['ImportActionUseFlatCode'] = toVariant(dlg.chkUseFlatCode.isChecked())


class CMyXmlStreamReader(QXmlStreamReader):
    def __init__(self,  parent):
        QXmlStreamReader.__init__(self)
        self.parent = parent
        self.db=QtGui.qApp.db
        self.tableActionType = tbl('ActionType')
        self.tableActionPropertyType = tbl('ActionPropertyType')
        self.tableActionPropertyTemplate = tbl('ActionPropertyTemplate')
        self.tableUnit = tbl('rbUnit')
        self.tableService = tbl('rbService')
        self.nadded = 0
        self.ncoincident = 0
        self.nprocessed = 0
        self.nupdated = 0
        self.mapUnitKeyToId = {}
        self.mapTemplateKeyToId = {}
        self.mapServiceKeyToId = {}
        self.mapActionTypeKeyToId = {}
        self.mapActionTypeFlatCodeToId = {}
        self.showLog = self.parent.chkFullLog.isChecked()
        self.recursionLevel = 0


    def raiseError(self,  str):
        QXmlStreamReader.raiseError(self, u'[%d:%d] %s' % (self.lineNumber(), self.columnNumber(), str))


    def readNext(self):
        QXmlStreamReader.readNext(self)
        self.parent.progressBar.setValue(self.device().pos())


    def log(self, str,  forceLog = False):
        if self.showLog or forceLog:
            self.parent.logBrowser.append(str)
            self.parent.logBrowser.update()


    def readFile(self, device):
        self.setDevice(device)

        try:
            while (not self.atEnd()):
                self.readNext()

                if self.isStartElement():
                    if self.name() == 'ActionTypeExport':
                        if self.attributes().value('version') == exportFormatVersion:
                            self.readData()
                        else:
                            self.raiseError(u'Версия формата "%s" не поддерживается. Должна быть "%s"' \
                                % (self.attributes().value('version').toString(), exportFormatVersion))
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


        return not (self.hasError() or self.parent.aborted)


    def readData(self):
        assert self.isStartElement() and self.name() == 'ActionTypeExport'

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == 'ActionType'):
                    self.readActionType()
                else:
                    self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break


    def readActionType(self):
        assert self.isStartElement() and self.name() == 'ActionType'

        groupId = None
        actionProperties = []
        actionType = {}
        nomenclativeService = None

        for x in actionTypeFields:
            actionType[x] = forceString(self.attributes().value(x).toString())

        while not self.atEnd():
            self.readNext()

            QtGui.qApp.processEvents()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == 'group'):
                    groupId = self.readGroup()
                    actionType['group_id'] = groupId
                elif (self.name() == 'ActionPropertyType'):
                    self.readActionPropertyType(actionProperties)
                elif (self.name() == 'service'):
                    pass
                    # service = self.readService()
                    # actionType['service_id'] = service['id']
                elif (self.name() == 'nomenclativeService'):
                    nomenclativeService = self.readService()
                    actionType['nomenclativeService_id'] = nomenclativeService['id']
                else:
                    self.readUnknownElement()

        name = actionType['name']
        code = actionType['code']
        class_ = actionType['class']
        self.log(u'Тип действия: %s (%s,%s)' %(name, code, class_))
        if self.parent.chkUseFlatCode.isChecked():
            self.log(u'* используем "плоский" код "%s"'
                    u' для поиска похожих записей' % actionType['flatCode'])
            id = self.lookupActionTypeWithFlatCode(actionType['flatCode'])
        else:
            id = self.lookupActionType(code, class_, groupId)
        # actionType['service'] = service
        actionType['nomenclativeService'] = nomenclativeService

        if self.hasError() or self.parent.aborted:
            return None

        if id:
            self.log(u'%% Найдена похожая запись (id=%d)' % id)
            # такое действие уже есть. надо проверить все его свойства
            if not self.parent.rbSkip.isChecked():
                if not self.isCoincidentActionType(actionType,  id):
                    # есть разхождения в полях. спрашиваем у пользователя что делать
                    self.log(u' поля различаются')
                    if self.parent.rbAskUser.isChecked():
                        self.log(u' Запрос действия пользователя: ')
                        answer = QtGui.QMessageBox.question(self.parent, u'Записи различаются',
                                        self.prepareMessageBoxText(actionType, id) ,
                                        QtGui.QMessageBox.No|QtGui.QMessageBox.Yes|QtGui.QMessageBox.Abort,
                                        QtGui.QMessageBox.No)
                        if answer == QtGui.QMessageBox.Yes:
                            self.log(u' - обновляем')
                            self.updateActionType(actionType, id)
                        elif answer == QtGui.QMessageBox.Abort:
                            self.parent.abort()
                            return None
                        else:
                            self.log(u' - пропускаем')
                    elif self.parent.rbUpdate.isChecked():
                        self.log(u' - обновляем')
                        self.updateActionType(actionType,  id)

                #  проверим свойства действия
                for x in actionProperties:
                    self.log(u'  Свойство: %s' %(x['name']))
                    # если нет 100% совпадения, ищем похожие свойства
                    if not self.isCoincidentActionPropertyType(x, id):
                        idList = self.lookupActionPropertyType(x,  id)
                        if idList:
                            if self.parent.rbAskUser.isChecked():
                                self.log(u'  _ запрос действия пользователя')
                                dlg = CActionTypePropertyReplaceDialog(actionType, x, idList,  self.parent)
                                dlg.exec_()
                                if dlg.updateData: # пользователь нажал кнопку обновить
                                    self.log(u'   - выбор пользователя: обновить')
                                    self.addOrUpdateActionPropertyType(x,  id,  dlg.selectedIds)
                                else:
                                    self.log(u'   - выбор пользователя: пропускаем')

                            elif self.parent.rbUpdate.isChecked():
                                self.log(u'  + обновляем')
                                self.addOrUpdateActionPropertyType(x,  id,  idList)
                            else:
                                self.log(u'  + пропускаем')
                        else: # похожих нет, добавляем
                            self.log(u'  + добавляем')
                            self.addOrUpdateActionPropertyType(x,  id)

            else:
                self.log(u' - пропускаем')


            self.ncoincident += 1
        else:
            self.log(u'% Сходные записи не обнаружены. Добавляем')
            # новая запись, добавляем само действие и все его свойства + ед.изм.
            record = self.tableActionType.newRecord()

            for x in actionTypeFields:
                if actionType[x]:
                    record.setValue(x,  toVariant(actionType[x]))

            if groupId: # если есть группа, запишем её id
                record.setValue('group_id',  toVariant(groupId))

#            if service: # если есть услуга по еис, запишем ее
#                sId = self.processService(service)
#                 record.setValue('service_id', toVariant(sId))

            if nomenclativeService: # если есть услуга по еис, запишем ее
                nsId = self.processService(nomenclativeService)
                record.setValue('nomenclativeService_id', toVariant(nsId))

            id = self.db.insertRecord(self.tableActionType, record)
            self.mapActionTypeKeyToId[(code, class_, groupId)] = id

            # поскольку тип действия - новый, то просто добавим все его свойства
            if actionProperties != []:
                for p in actionProperties:
                    record = self.tableActionPropertyType.newRecord()

                    for fieldName in actionPropertyTypeFields:
                        if p[fieldName]:
                            record.setValue(fieldName, toVariant(p[fieldName]))

                    unit = p['unit']

                    if unit: # у свойства есть ед. изм
                        uId = unit['id']

                        if not uId: # единицы измерения нет в базе. добавим
                            uId = self.addUnit(unit)

                        record.setValue('unit_id', toVariant(uId))

                    if p['template_id']:
                        record.setValue('template_id', toVariant(p['template_id']))

                    record.setValue('actionType_id',  toVariant(id))
                    self.db.insertRecord(self.tableActionPropertyType,  record)

            self.nadded += 1

        self.nprocessed += 1
        self.parent.statusLabel.setText(
                u'импорт типов действий: %d добавлено; %d обновлено; %d совпадений; %d обработано' % (self.nadded,
                                                                                                      self.nupdated,  self.ncoincident,  self.nprocessed))

        return id


    def readGroup(self):
        assert self.isStartElement() and self.name() == 'group'

        group_id = None
        self.log(u'Группа:' )

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == 'ActionType'):
                    if self.recursionLevel < 10:
                        self.recursionLevel += 1
                        group_id = self.readActionType()
                        self.recursionLevel -= 1
                    else:
                        self.raiseError(u'Уровень вложенности групп больше 10')
                else:
                    self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break

        return group_id


    def readActionPropertyType(self,  actionProperties):
        assert self.isStartElement() and self.name() == 'ActionPropertyType'

        unit = None
        self.log(u'Свойство: ' + self.attributes().value('name').toString())

        # добавляем свойство в список для обработки
        property = {}
        templateCodeList = []

        for x in actionPropertyTypeFields:
            property[x] = forceString(self.attributes().value(x).toString())

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == 'unit'):
                    unit = self.readUnit()
                elif self.name() == 'template':
                    templateCodeList.append(self.readTemplateCode())
                else:
                    self.readUnknownElement()

        # ищем код шаблона в библиотеке
        templateId = self.lookupTemplate(templateCodeList)

        property['template_id'] = templateId
        property['template_code'] = templateCodeList[-1] if templateId else None

        property['unit'] = unit
        actionProperties.append(property)


    def readTemplateCode(self):
        assert self.isStartElement() and self.name() == 'template'

        templateCode = forceString(self.attributes().value('code').toString())

        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break

        return templateCode

    def readUnit(self):
        assert self.isStartElement() and self.name() == 'unit'

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


    def readService(self):
        assert self.isStartElement() and (self.name() == 'service' or self.name() == 'nomenclativeService')
        service = {}
        name = forceString(self.attributes().value('name').toString())
        code = forceString(self.attributes().value('code').toString())
        self.log(u'Услуга ЕИС: %s, код %s' %(name, code))
        service['id'] = self.lookupService(name, code)
        for fieldName in serviceFields:
            service[fieldName] = forceString(self.attributes().value(fieldName).toString())
        while not self.atEnd():
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
               break
        return service


    def readUnknownElement(self):
        assert self.isStartElement()

        self.log(u'Неизвестный элемент: '+self.name().toString())
        while (not self.atEnd()):
            self.readNext()

            if (self.isEndElement()):
                break

            if (self.isStartElement()):
                self.readUnknownElement()

            if self.hasError() or self.parent.aborted:
                break


    def lookupActionType(self, code, class_, group_id):
        u""" Для идентификации действия (ActionType) возможно использовать составной ключ
            класс-код группы (подгрупп)-код действия"""

        key = (code, class_, group_id)
        id = self.mapActionTypeKeyToId.get(key,  None)

        if id:
            return id

        cond = []
        cond.append(self.tableActionType['code'].eq(toVariant(code)))
        cond.append(self.tableActionType['class'].eq(toVariant(class_)))
        cond.append(self.tableActionType['deleted'].eq(toVariant(0)))

        if group_id:
            cond.append(self.tableActionType['group_id'].eq(toVariant(group_id)))

        record = self.db.getRecordEx(self.tableActionType, ['id'], where=cond)

        if record:
            id = forceRef(record.value('id'))
            self.mapActionTypeKeyToId[key] = id
            return id

        return None


    def lookupActionTypeWithFlatCode(self, flatCode):
        u""" Для идентификации действия (ActionType) используется
            "плоский код" flatCode"""

        if not flatCode:
            return None

        id = self.mapActionTypeFlatCodeToId.get(flatCode,   None)

        if id:
            return id

        cond = []
        cond.append(self.tableActionType['flatCode'].eq(toVariant(flatCode)))
        record = self.db.getRecordEx(self.tableActionType, ['id'], where=cond)

        if record:
            id = forceRef(record.value('id'))
            self.mapActionTypeFlatCodeToId[flatCode] = id
            return id

        return None


    def lookupUnit(self, name, code):
        u"""Для идентификации единиц измерения используем имя и код"""

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


    def lookupService(self, name, code):
        u"""Для идентификации услуг (профиль ЕИС) используем имя и код"""

        key = (name, code)
        id = self.mapServiceKeyToId.get(key,  None)
        if not id:
            cond = []
            cond.append(self.tableService['name'].eq(toVariant(name)))
            cond.append(self.tableService['code'].eq(toVariant(code)))
            record = self.db.getRecordEx(self.tableService, ['id'], where=cond)
            if record:
                id = forceRef(record.value('id'))
                self.mapServiceKeyToId[key] = id
        return id


    def lookupTemplateId(self, code,  groupId):
        id = self.mapTemplateKeyToId.get((code, groupId),  None)
        if id:
            return id
        cond = []
        cond.append(self.tableActionPropertyTemplate['code'].eq(toVariant(code)))
        if groupId:
            cond.append(self.tableActionPropertyTemplate['group_id'].eq(toVariant(groupId)))
        else:
            cond.append(self.tableActionPropertyTemplate['group_id'].isNull())
        record = self.db.getRecordEx(self.tableActionPropertyTemplate, ['id'], where=cond)
        if record:
            id = forceRef(record.value('id'))
            self.mapTemplateKeyToId[(code,  groupId)] = id
            return id
        return None


    def lookupTemplate(self,  templateCodeList):
        groupId = None
        for x in templateCodeList:
            groupId = self.lookupTemplateId(x,  groupId)

            if not groupId:
                break
        return groupId


    def isCoincidentActionType(self,  actionType,  id):
        record = self.db.getRecord(self.tableActionType, actionTypeFields+actionTypeRefFields, id)

        if record:
            for x in actionTypeFields:
                if forceString(record.value(x)) != forceString(actionType[x]):
                    return False

            for x in actionTypeRefFields:
                a = actionType.get(x)
                b = forceRef(record.value(x))

                if (a != b) or ((not b) and (actionType.has_key(x))):
                    return False

            return True

        return False


    def prepareMessageBoxText(self, actionType, id):
        record = self.db.getRecord(self.tableActionType,  actionTypeFields+actionTypeRefFields, id)
        str = u'''<h3>Обнаружены следующие различия в записях:</h3>\n\n\n
                        <table>
                        <tr>
                            <td><b>Название поля</b></td>
                            <td align=center><b>Новое</b></td>
                            <td align=center><b>Исходное</b></td>
                        </tr>'''

        if record:
            for x in actionTypeFields:
                str += '<tr><td><b> '+x+': </b></td>'

                if forceString(record.value(x)) != forceString(actionType[x]):
                    str += '<td align=center bgcolor="red"> '
                else:
                    str += '<td align=center>'

                str += forceString(actionType[x])+' </td><td align=center>' + forceString(record.value(x)) + '</td></tr>\n'

            for x in actionTypeRefFields:
                a = actionType.get(x, None)
                b = forceRef(record.value(x))

                if (a != b) or ((not b) and (actionType.has_key(x))):
                        str += '<tr><td><b> '+x+': </b></td><td align=center bgcolor="red">' +\
                            forceString(actionType.get(x, '-'))
                        str += ' </td><td align=center>' + forceString(record.value(x)) + '</td></tr>\n'

            str += u'</table>\n\n<p align=center>Обновить?</p>'
        return str

    def processService(self,  service):
        sId = service['id']

        if not sId: # нет в базе. добавим
            sRecord = self.tableService.newRecord()
            for x in serviceFields:
                if service[x]:
                    sRecord.setValue(x, toVariant(service[x]))
            sId = self.db.insertRecord(self.tableService, sRecord)
            # добавим в кэш
            self.mapServiceKeyToId[(service['code'], service['name'])] = sId

        return sId


    def updateActionType(self,  actionType, id):
        record = self.db.getRecord(self.tableActionType,  '*', id)

        for x in actionTypeFields+actionTypeRefFields:
            val = actionType.get(x, None)
            if val:
                record.setValue(x, toVariant(val))

        self.db.updateRecord(self.tableActionType, record)
        self.nupdated += 1


    def isCoincidentActionPropertyType(self,  actionPropertyType,  actionTypeId):
        u""" Сравнивает все поля, выдает True в случае совпадения"""

        fieldList = actionPropertyTypeFields+actionPropertyTypeRefFields # все кроме id
        cond = []

        actionPropertyType['actionType_id'] = actionTypeId
        actionPropertyType['unit_id'] = actionPropertyType['unit']['id'] if actionPropertyType['unit'] else None

        for x in fieldList:
            if actionPropertyType[x]:
                cond.append(self.tableActionPropertyType[x].eq(toVariant(actionPropertyType[x])))

        record = self.db.getRecordEx(self.tableActionPropertyType, fieldList, cond)

        if record:
            # если свойство не относится к текущему действию
            if forceInt(actionTypeId) != forceInt(record.value('actionType_id')):
                return False

            if forceInt(record.value('template_id')) != forceInt(actionPropertyType['template_id']):
                return False

            for x in actionPropertyTypeFields: # сверяется все, кроме id, unit_id
                if forceString(record.value(x)) != forceString(actionPropertyType[x]):
                    return False

            uId = forceInt(record.value('unit_id'))
            return actionPropertyType['unit_id'] == uId if actionPropertyType['unit_id'] else uId == 0

        return False


    def lookupActionPropertyType(self, actionPropertyType, id):
        cond = []

        # ищем похожие свойства по название-ед.измерения
        cond.append(self.tableActionPropertyType['actionType_id'].eq(toVariant(id)))
        cond.append(self.tableActionPropertyType['name'].eq(toVariant(actionPropertyType['name'])))
        cond.append(self.tableActionPropertyType['deleted'].eq(toVariant(0)))

        if actionPropertyType['unit']:
            uId = actionPropertyType['unit']['id']
            if uId:
                cond.append(self.tableActionPropertyType['unit_id'].eq(toVariant(uId)))

        return self.db.getIdList(self.tableActionPropertyType,  where = cond)


    def addOrUpdateActionPropertyType(self,  actionPropertyType,  actionTypeId,  idList = None):
        u""" Добавляет свойства типа действия, если idList пустой. Если же idList не пуст,
            отмечаем все элементы в нем, как удаленные, и добавляем новый элемент"""

        record = self.tableActionPropertyType.newRecord()

        # заполняем все поля кроме id и unit_id, template_id
        for x in actionPropertyTypeFields:
            if actionPropertyType[x]:
                record.setValue(x, toVariant(actionPropertyType[x]))

        if actionPropertyType['unit']:
            uId = actionPropertyType['unit']['id']

            if not uId:
                uId = self.addUnit(actionPropertyType['unit'])

            record.setValue('unit_id', toVariant(uId))

        record.setValue('actionType_id', toVariant(actionTypeId))
        record.setValue('template_id', toVariant(actionPropertyType['template_id']))
        sId = self.db.insertRecord(self.tableActionPropertyType, record)

        if idList:
            for id in idList:
                record = self.db.getRecord(self.tableActionPropertyType, ['id','deleted'], id)
                record.setValue('deleted', toVariant(True))
                self.db.updateRecord(self.tableActionPropertyType,record)


    def addUnit(self,  unit):
        u""" добавляет в бд новую единицу измерения и возвращает ее id"""
        uRecord = self.tableUnit.newRecord()

        for x in unitFields:
            if unit[x]:
                uRecord.setValue(x, toVariant(unit[x]))

        uId = self.db.insertRecord(self.tableUnit, uRecord)
        self.mapUnitKeyToId[(unit['name'], unit['code'])] = uId
        return uId


class CActionTypePropertyReplaceDialog(CDialogBase, Ui_ImportActionProperty):
    def __init__(self, action, actionProperty,  idList,  parent=None):
        CDialogBase.__init__(self, parent)
        self.cols = [
            CRefBookCol(u'Шаблон',  ['template_id'], 'ActionPropertyTemplate', 60,  CRBComboBox.showCodeAndName),
            CTextCol(  u'Наименование',  ['name'],    12),
            CTextCol( u'Описание',       ['descr'],   12),
            CRefBookCol(u'Ед.изм.',        ['unit_id'], 'rbUnit', 6),
#            CEnumCol( u'Тип',         ['typeName'],  ['Double', 'Integer', 'String', 'Time', \
#                                                                        'Reference', 'Text', 'Constructor'], 7),
            CTextCol( u'Тип',            ['typeName'],  7),
            CTextCol( u'Область',        ['valueDomain'], 12),
            CTextCol( u'Штраф',          ['penalty'],  12),
            CBoolCol( u'Вектор',         ['isVector'], 6),
            CTextCol( u'Норматив',       ['norm'],    12),
            CEnumCol( u'Пол',            ['sex'],  [u'-', u'М', u'Ж'], 5),
            CTextCol( u'Возраст',        ['age'],  12),
            CBoolCol( u'Видимость при выполнении работ',  ['visibleInJobTicket'], 6),
            CBoolCol( u'Назначаемый',    ['isAssignable'], 6),
            ]
        self.tableName = 'ActionPropertyType'
        self.parent = parent
        self.order = ['name', 'descr']
        self.action = action
        self.actionProperty = actionProperty
        self.idList = idList
        self.selectedIds = []
        self.updateData = False
        self.preSetupUi()
        self.setupUi(self)
        self.postSetupUi()


    def preSetupUi(self):
        self.addModels('Table',CTableModel(self, self.cols, self.tableName))


    def postSetupUi(self):
        self.setModels(self.tblNew,   self.modelTable, self.selectionModelTable)
        self.tblNew.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.modelTable.setIdList(self.idList)
        self.selectionModelTable.clearSelection()
        self.tblNew.setFocus(Qt.OtherFocusReason)
        self.txtActionInfo.setHtml(self.getActionBanner())
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint)


    def updateBtnReplaceText(self):
        self.btnReplace.setText(u'Заменить' if self.selectedIds else u'Добавить')
        self.btnReplace.update()


    @QtCore.pyqtSlot()
    def on_btnSelectAll_clicked(self):
        self.selectedIds=self.modelTable.idList()
        self.updateBtnReplaceText()
        for id in self.modelTable.idList():
            index = self.modelTable.index(self.modelTable.idList().index(id), 0)
            self.selectionModelTable.select(index, QtGui.QItemSelectionModel.Select|
                                                                    QtGui.QItemSelectionModel.Rows)


    @QtCore.pyqtSlot()
    def on_btnClearSelection_clicked(self):
        self.selectedIds = []
        self.selectionModelTable.clearSelection()
        self.updateBtnReplaceText()


    @QtCore.pyqtSlot()
    def on_btnReplace_clicked(self):
        self.updateData = True
        if self.selectedIds == []:
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
        self.selectedIds =self.tblNew.selectedItemIdList()
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.updateBtnReplaceText()


    def getActionBanner(self):
        def formatAmountEvaluation(amountEvaluation):
            d = {0:u'Количество вводится непосредственно',
                 1:u'По числу визитов',
                 2:u'По длительности события',
                 3:u'По длительности события без выходных дней',
            }
            return d.get(amountEvaluation, d[0])
        str = u'''Тип действия:<br>
        Название: <b>%s</b>, код: <b>%s</b>, класс: <b>%s</b>, пол: <b>%s</b>,<br>
        возраст: <b>%s</b>, кабинет: <b>%s</b>, контекст: <b>%s</b><br>
        отображается в форме бланка: <b>%s</b>, генерирует график: <b>%s</b><br>
        количество по умолчанию <b>%s</b>, <b>%s</b>.<br>
        ''' % (self.action['name'], self.action['code'], self.action['class'],  formatSex(self.action['sex']),
                  self.action['age'],  self.action['office'], self.action['context'],
                  formatBool(self.action['showInForm']),  formatBool(self.action['genTimetable']),
                  self.action['amount'], formatAmountEvaluation(self.action['amountEvaluation']))

        str += u''' Свойство:<br>
        Название: <b>%s</b>, описание: <b>%s</b><br>
        относительный индекс: <b>%s</b>, имя типа значения: <b>%s</b>,<br>
        возможные значения: <b>%s</b>,<br>
        является вектором: <b>%s</b>, пол: <b>%s</b>, возраст: <b>%s</b>,<br>
        нормировка: <b>%s</b>, код шаблона <b>%s</b>,<br>
        штраф: <b>%s</b>, видимость при выполнении работ <b>%s</b>,<br>
        назначаемый <b>%s</b>
        ''' % (self.actionProperty['name'],  self.actionProperty['descr'],
               self.actionProperty['idx'],   self.actionProperty['typeName'],
               self.actionProperty['valueDomain'],
               formatBool(self.actionProperty['isVector']), formatSex(self.actionProperty['sex']),  self.actionProperty['age'],
               self.actionProperty['norm'], self.actionProperty['template_code'],
               self.actionProperty['penalty'], formatBool(self.actionProperty['visibleInJobTicket']),
               formatBool(self.actionProperty['isAssignable'])
              )

        if self.actionProperty['unit']:
            str += u''',единица измерения: <b>%s(%s)</b>.<br>''' % (self.actionProperty['unit']['name'],
                                                                    self.actionProperty['unit']['code'],)

        result = u'<html><body>%s</body><html>' % str
        return  str


class CImportActionType(QtGui.QDialog, Ui_ImportActions):
    def __init__(self, fileName,  parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.progressBar.reset()
        self.progressBar.setValue(0)
        self.fileName = ''
        self.aborted = False
        self.connect(self, QtCore.SIGNAL('import()'), self.import_, Qt.QueuedConnection)
        self.connect(self, QtCore.SIGNAL('rejected()'), self.abort)
        if fileName != '' :
            self.edtFileName.setText(fileName)
            self.btnImport.setEnabled(True)
            self.fileName = fileName


    def abort(self):
        self.aborted = True


    def import_(self):
        self.aborted = False
        self.btnAbort.setEnabled(True)
        success,  result = QtGui.qApp.call(self, self.doImport)

        if self.aborted or not success:
            self.progressBar.setText(u'Прервано')

        self.btnAbort.setEnabled(False)


    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        self.fileName = QtGui.QFileDialog.getOpenFileName(
            self, u'Укажите файл с данными', self.edtFileName.text(), u'Файлы XML (*.xml)')
        if self.fileName != '' :
            self.edtFileName.setText(self.fileName)
            self.btnImport.setEnabled(True)


    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.close()


    @QtCore.pyqtSlot()
    def on_btnAbort_clicked(self):
        self.abort()


    @QtCore.pyqtSlot()
    def on_btnImport_clicked(self):
        self.emit(QtCore.SIGNAL('import()'))


    def doImport(self):
        fileName = self.edtFileName.text()

        if fileName.isEmpty():
            return

        inFile = QtCore.QFile(fileName)
        if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, u'Импорт типов действий',
                                      QString(u'Не могу открыть файл для чтения %1:\n%2.')
                                      .arg(fileName)
                                      .arg(inFile.errorString()))
        else:
            self.progressBar.reset()
            self.progressBar.setValue(0)
            self.progressBar.setFormat(u'%v байт')
            self.statusLabel.setText('')
            self.progressBar.setMaximum(max(inFile.size(), 1))
            myXmlStreamReader = CMyXmlStreamReader(self)
            self.btnImport.setEnabled(False)
            if (myXmlStreamReader.readFile(inFile)):
                self.progressBar.setText(u'Готово')
            else:
                self.progressBar.setText(u'Прервано')
                if self.aborted:
                    self.logBrowser.append(u'! Прервано пользователем.')
                else:
                    self.logBrowser.append(u'! Ошибка: файл %s, %s' % (fileName, myXmlStreamReader.errorString()))
            self.edtFileName.setEnabled(False)
            self.btnSelectFile.setEnabled(False)
