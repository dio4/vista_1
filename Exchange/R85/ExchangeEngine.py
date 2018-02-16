# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################

__author__ = 'craz'

'''
    author: craz
    date:   7/29/2015
'''

import logging

from PyQt4 import QtCore

from library.ProgressInformer import CProgressInformer
from library.Utils import forceDouble, forceInt, forceRef, forceStringEx, getClassName

class CExchangeEngine(object):
    encoding = u'utf-8'

    PrimaryMKBTypeCode = 2
    SecondaryMKBTypeCode = 9
    ComplicatedMKBTypeCode = 3

    defaultDateFormat = 'yyyy-MM-dd'

    dummy = u'#' * 32
    dummyN = 0
    dummyD = QtCore.QDate(0, 0, 0)


    def __init__(self, progressInformer = None):
        self._progressInformer = progressInformer if isinstance(progressInformer, CProgressInformer) \
                                                  else CProgressInformer(processEventsFlag=None)
        self._logger = logging.getLogger(name=getClassName(self))
        self._logger.setLevel(logging.NOTSET)

        self.totalPhases = 0
        self.currentPhase = 0

        self.isAbort = False

        self._lastExceptionHandler = None

    def onException(self):
        """
            Вызывает обработчик последнего исключения, если он был задан методомом setLastExceptionHandler.

        """
        if callable(self._lastExceptionHandler):
            self._lastExceptionHandler()

    def setLastExceptionHandler(self, handler):
        """
            Задает обработчик последнего возникшего исключения.

        :param handler: обработчик последнего исключения. Функция без параметров, которая должна вызываться в случае возникновения Exception
        """
        if callable(handler):
            self._lastExceptionHandler = handler

    def logger(self):
        return self._logger


    def setProgressInformer(self, progressInformer):
        if isinstance(progressInformer, CProgressInformer):
            progressInformer.syncWithOther(self._progressInformer)
            self._progressInformer = progressInformer

    def progressInformer(self):
        return self._progressInformer

    def phaseReset(self, phasesCount):
        self.currentPhase = 0
        self.totalPhases = phasesCount

    @property
    def phaseInfo(self):
        return u'[Этап %s/%s] ' % (self.currentPhase, self.totalPhases)

    def nextPhase(self, steps, description = u''):
        self.currentPhase += 1
        self._progressInformer.reset(steps, self.phaseInfo + description)
        self.logger().info(self.phaseInfo + description)

    def nextPhaseStep(self, description = None):
        self._progressInformer.nextStep((self.phaseInfo + description) if description else None)

    def abort(self):
        self.isAbort = True

    def onAborted(self):
        self.logger().info(u'Прервано')
        self._progressInformer.reset(0, u'Прервано')

    def finishPhase(self):
        self._progressInformer.reset(newTotal=0, description=self.phaseInfo + u'Завершено')


class CExchangeR85Engine(CExchangeEngine):
    encoding = u'windows-1251'
    version = u'2.1'

    @staticmethod
    def formatOKATO(OKATO, length=5):
        return forceStringEx(OKATO)[:length].ljust(length, '0')

class CExchangeImportEngine(CExchangeEngine):
    def __init__(self, progressInformer = None):
        super(CExchangeImportEngine, self).__init__(progressInformer)
        # ссылка на функцию с аргументами ("заголовок", "Сообщение"), вызов которой выводит запрос к пользователю и возвращает True или False в качестве ответа
        self._userConfirmation = None

    def getElement(self, parentNode, elementName, isRequired=False, mekErrorList=None):
        """Получение DOM-элемента по имени с проверкой его необходимости и заполнением лога ошибок.
        Пытается найти элемент (QDomElement) с именем *elementName* в узле *parentNode*. Если элемент не был найден,
         но при этом указан, как обязательный, то в *mekErrorList* заносятся данные об ошибке.

        :param parentNode: родительский DOM-узел (QDomNode), в котором необходимо искать элемент
        :param elementName: имя искомого элемента
        :param isRequired: искомый элемент является обязательным и его отсутствие - признак ошибки
        :param mekErrorList: список для занесения в него возможных ошибок
        :return: найденный элемент
        """
        element = parentNode.firstChildElement(elementName)
        if element.isNull() and isRequired:
            self.logger().warning(u'Ошибка формата файла. Ожидаемый узел: "%s" не был найден [%s:%s]' % (elementName, parentNode.lineNumber(), parentNode.columnNumber()))
            if isinstance(mekErrorList, list):
                mekErrorList.append((u'5.1.3',
                                     u'Неполное заполнение полей реестра счетов',
                                     parentNode.nodeName(),
                                     elementName))
        return element

    def getElementValue(self, parentNode, elementName, typeName='str', isRequired=False, mekErrorList=None, return_null=False):
        """Получение значения из указанного элемента *elementName* в родительском узле *parentNode*.
        Выполняет поиск элемента с помощью `getElement` и возвращает значение этого элемента, преобразованное
        в указанный тип с помощью `convertValue`.

        :param parentNode: родительский DOM-узел (QDomNode), в котором необходимо искать элемент
        :param elementName: имя искомого элемента
        :param typeName: имя типа, в который необходимо преобразовать значение
        :param isRequired: искомый элемент является обязательным и его отсутствие - признак ошибки
        :param mekErrorList: список для занесения в него возможных ошибок
        :param return_null: возвращать None для null-значений
        :return: значение указанного элемента в нужном формате
        """
        return self.convertValue(self.getElement(parentNode, elementName, isRequired, mekErrorList).text(), typeName,
                                 return_null=return_null)

    @classmethod
    def convertValue(cls, value, typeName='str', return_null=False):
        """Преобразует переданное значение в указанный тип.
        Поддерживаемые типы:
            - 'double' или 'float': Вещественное число. Для преобразование используется forceDouble из library.Utils
            - 'int' или 'n': Целое число. Для преобразование используется forceInt из library.Utils
            - 'ref' или 'r': Ссылка на запись БД. Для преобразование используется forceRef из library.Utils
            - 'date' или 'd': Дата. Значение преобразуется в строку, из которой согласно `defaultDateFormat` в QDate

        :param value: Значение, которое необходимо преобразовать.
        :param typeName: имя типа, в который необходимо преобразовать значение.
        :param return_null: возвращать None для null-значений
        :return: преобразованное значение *value*
        """
        if return_null and value.isNull():
            return None
        typeName = typeName.lower()
        if typeName in ['double', 'float']:
            return forceDouble(value)
        elif typeName in ['int', 'n']:
            return forceInt(value)
        elif typeName in ['ref', 'r']:
            return forceRef(value)
        elif typeName in ['date', 'd']:
            return QtCore.QDate.fromString(forceStringEx(value),
                                             cls.defaultDateFormat)
        return forceStringEx(value)

    def setUserConfirmationFunction(self, func):
        """Устанавоивает функцию для "общения с пользователем".
        Переданная внешняя функция *func* вызывается ,
        когда классу необходимо получить от пользователя ответ "Да"\"Нет" и от нее ожидается результат True\False

        :param func: внешняя функция (или функтор) с параметрами ("Заголовок", "Сообщение"), ответственная за вывод
        сообщения пользователю и получения от него положительного или отрицательного ответа, который она возвращает
        в качестве булевого результата.
        """
        self._userConfirmation = func


    def getUserConfirmation(self, title, message):
        """Передает сообщение-запрос пользователю через функцию-посредник.
        Если до вызова была настроена функция-посредник (с помощью метода `setUserConfirmationFunction`), то передает
        ей свои параметра (заголовок и сообщение) и возвращает полученный от функции-посредника ответ.
        Если функция-посредник отсутствует, всегда возвращает *True*

        :param title: Заголовок обращения к пользователю
        :param message: Сообщение-вопрос к пользователю, предполагающие ответ "Да" или "Нет"
        :return: True, если функция-посредник отсутствует или если пользователь дал утвердительный ответ, иначе False
        """
        return self._userConfirmation(title, message) if callable(self._userConfirmation) else True

class CExchangeImportR85Engine(CExchangeImportEngine):
    encoding = u'windows-1251'
    version = u'2.1'

    @staticmethod
    def formatOKATO(OKATO, length=5):
        return forceStringEx(OKATO)[:length].ljust(length, '0')