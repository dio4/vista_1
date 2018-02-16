# -*- coding: utf-8 -*-
u"""
Модуль для автоматической замены одних услуг на другие. Более подробная информация в комментарии к :def createModifier
"""
from RefBooks.Tables import rbScene, rbVisitType, EvenType
from RefBooks.Ui_OldStyleServiceModifierRemaker import Ui_OldStyleServiceModifierRemakerDialogForm
from library.TableModel import CTextCol
from library.Utils      import forceStringEx, toVariant
from PyQt4 import QtGui


def parseModifier(modifiers):
    u"""
    Расшифровывает сохранённый в БД модификатор

    :param modifiers: Модификатор. Формат смотри в :def createModifier.
    Несколько (на данный момент 2) модификаторов может быть сохранено вместе с разделителем '/'
    :type modifiers: str

    :return: (action, text, n):
    :rtype: list(int, str|None, int|None)
    """
    result = []
    if modifiers == u'':
        result.append((0, None, None))

    for mod in modifiers.split(u'/'):
        parts = mod.split(u';')
        if parts:
            if parts[0] == u'-' and len(parts) > 1:
                result.append((1, parts[1], None))
            elif parts[0] == u's' and len(parts) > 2:
                result.append((2, parts[1], int(parts[2])))
            elif parts[0] == u'e' and len(parts) > 2:
                result.append((3, parts[1], int(parts[2])))

    if result:
        return result
    else:
        raise ValueError(u'Неизвестный модификатор услуги (%s)' % modifiers)


def createModifier(action, text, n=None):
    u"""
    Создаёт строку, которая будет использоваться для автоматической замены одной услуги на другую.
    Замена производится как переименование кода услуги.

    :param action: тип изменения
        0 — не делать ничего
        1 — заменить всё на text (без сохранения исходного текста)
        2 — добавить text вместо первых n символов
        3 — добавить text вместо последних n символов
    :type action: {0|1|2|3}

    :param text: на что заменяем
    :type text: str

    :param n: Количество символов в исходном имени, которое будет удалено
    :type n: int

    :return: Закодированное представление изменения
        [-|s|e;[n];text]
        - — удаляем то, что было
        s — start. Добавляем в начало
        e — end. Добавляем в конец
    :rtype: str
    """
    if action == 0:
        return u''
    elif action == 1:
        return u'-;%s' % text
    elif action == 2:
        return u's;%s;%i' % (text, n)
    elif action == 3:
        return u'e;%s;%i' % (text, n)
    else:
        raise ValueError(u'Неизвестный модификатор услуги (%s,%s,%i,)' % (action, text, n))


def applyModifier(serviceCode, modifiers):
    u"""
    Изменяет код услуги согласно модификатору
    :param serviceCode: Исходный код.
    :type serviceCode: str

    :param modifiers: Модификатор. Формат смотри в :def createModifier
    Несколько (на данный момент 2) модификаторов может быть сохранено вместе с разделителем '/'
    :type modifiers: str

    :return: Изменённый код услуги
    :rtype: str
    """
    modifiers = parseModifier(modifiers)
    for action, text, n in modifiers:
        if action == 1:
            serviceCode = text
        elif action == 2:
            serviceCode = text + serviceCode[n:]
        elif action == 3:
            serviceCode = serviceCode[:len(serviceCode) - n] + text  # Можно было бы s[:-n], но s[:-0] == u''

    return serviceCode


class CServiceModifierCol(CTextCol):
    titles = [u'Не меняет услугу. ',
              u'Заменяет код услуги на "%(text)s". ',
              u'Изменяет первые %(n)i символов услуги на "%(text)s". ',
              u'Изменяет заключительные %(n)i символов услуги на "%(text)s". ', ]

    def format(self, values):
        modifiers = parseModifier(forceStringEx(values[0]))
        result = u''
        for action, text, n in modifiers:
            result += CServiceModifierCol.titles[action] % {'text': text, 'n': n}
        return toVariant(result)


class COldStyleServiceModifierRemaker(QtGui.QDialog, Ui_OldStyleServiceModifierRemakerDialogForm):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.btnStart.clicked.connect(self.start)
        self.btnClose.clicked.connect(self.close)

    def start(self):
        db = QtGui.qApp.db

        self.logBrowser.append(u'Исправление модификаторов в rbScene')
        sceneRecordList = db.getRecordList(table=rbScene, cols=['id', 'serviceModifier'], where='serviceModifier != \'\'')
        for scene in sceneRecordList:
            QtGui.qApp.processEvents()
            mod = forceStringEx(scene.value('serviceModifier'))
            newMod = self.remakeModifier(mod)
            if newMod is None:
                self.logBrowser.append(u'Не смогли подобрать аналог модификатору %s в rbScene.id = %s' %
                                       (mod, forceStringEx(scene.value('id'))))
                continue
            scene.setValue('serviceModifier', newMod)
            db.updateRecord(rbScene, scene)

        self.logBrowser.append(u'\nИсправление модификаторов в rbVisitType')
        visitTypeRecordList = db.getRecordList(table=rbVisitType, cols=['id', 'serviceModifier'], where='serviceModifier != \'\'')
        for visitType in visitTypeRecordList:
            QtGui.qApp.processEvents()
            mod = forceStringEx(visitType.value('serviceModifier'))
            newMod = self.remakeModifier(mod)
            if newMod is None:
                self.logBrowser.append(u'Не смогли подобрать аналог модификатору %s в rbVisitType.id = %s' %
                                       (mod, forceStringEx(visitType.value('id'))))
                continue
            visitType.setValue('serviceModifier', newMod)
            db.updateRecord(rbVisitType, visitType)

        self.logBrowser.append(u'\nИсправление модификаторов в EventType')
        eventTypeRecordList = db.getRecordList(table=EvenType, cols=['id', 'visitServiceModifier'], where='visitServiceModifier != \'\'')
        for eventType in eventTypeRecordList:
            QtGui.qApp.processEvents()
            mod = forceStringEx(eventType.value('visitServiceModifier'))
            newMod = self.remakeModifier(mod)
            if newMod is None:
                self.logBrowser.append(u'Не смогли подобрать аналог модификатору %s в EvenType.id = %s' %
                                       (mod, forceStringEx(eventType.value('id'))))
                continue
            eventType.setValue('visitServiceModifier', newMod)
            db.updateRecord(EvenType, eventType)

        self.logBrowser.append(u'\n\n')

    @staticmethod
    def remakeModifier(modifier):
        """
        :param modifier: Модификатор старого вида
        :type modifier: str

        :return: Модификатор нового вида. Если не смог опознать модификатор, то обнуляем его
        :rtype: str | None
        """
        if modifier == u'-':
            return u'-;'  # Раньше у удаления сервиса был отдельный синтаксис. Теперь это заменить на ничего
        if modifier.startswith(u'~'):
            return u''  # Раньше так начинались регулярки. Теперь у нас их нет
        if len(modifier) == 1 and modifier != '-':
            return u's;%s;1' % modifier  # Раньше одиночный символ не 0 означал замену первого символа услуги на этот символ
        if modifier.startswith(u'+'):
            return u'-;%s' % modifier[1:]  # Раньше запись, начинающаяся с + означала замену на остальную часть записи
        return None  # Распарсить не смогли
