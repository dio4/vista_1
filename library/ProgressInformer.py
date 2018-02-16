# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012-2015 ООО "Виста". All rights reserved.
##
#############################################################################

"""
Created on 11/03/15

@author: atronah
"""


from PyQt4 import QtCore



class CProgressInformer(QtCore.QObject):
    currentChanged = QtCore.pyqtSignal(int)
    totalChanged = QtCore.pyqtSignal(int)
    descritionChanged = QtCore.pyqtSignal(QtCore.QString)

    progressChanged = QtCore.pyqtSignal(int, int, QtCore.QString)

    def __init__(self, description = u'', total = 0, start = 0, processEventsFlag = QtCore.QEventLoop.AllEvents, parent = None):
        """

        :param description: Начальное описание состояния прогреса
        :param total: Общее число шагов
        :param start: начальный шаг
        :param processEventsFlag: флаг, передаваемый в QCoreApplication.processEvents(), если None, то processEvents не вызывается
        """
        super(CProgressInformer, self).__init__(parent)
        self._total = total
        self._start = start
        self._current = max(0, start)
        self._description = description
        self._isEmitSummary = True
        self._processEventsFlag = processEventsFlag if processEventsFlag in (QtCore.QEventLoop.AllEvents,
                                                                             QtCore.QEventLoop.ExcludeUserInputEvents,
                                                                             QtCore.QEventLoop.ExcludeSocketNotifiers,
                                                                             QtCore.QEventLoop.WaitForMoreEvents) \
                                                    else None

        self.currentChanged.connect(self.emitSummary)
        self.totalChanged.connect(self.emitSummary)
        self.descritionChanged.connect(self.emitSummary)



    @property
    def current(self):
        """
        Текущая позиция прогресса.
        """
        return self._current


    @current.setter
    def current(self, value):
        if self._current != value and value >= 0:
            self._current = value
            if self._current > self._total:
                self.total = self._current
            self.currentChanged.emit(self._current)


    @property
    def total(self):
        """
        Общее число шагов.
        """
        return self._total


    @total.setter
    def total(self, value):
        if self._total != value and value >= self._current:
            self._total = value
            self.totalChanged.emit(self._total)


    @property
    def description(self):
        """
        Описание текущего шага.
        """
        return self._description


    @description.setter
    def description(self, value):
        if value is not None and value != self._description:
            self._description = QtCore.QString(value)
            self.descritionChanged.emit(self._description)


    def syncWithOther(self, otherInformer):
        """
        Синхронизирует параметры текущего информера с параметрами информера, переданного в параметрах.
        Синхронизации подлежат параметры current, total, description

        :param otherInformer: другой информер, данные которого необходимо записать в текущий информер
        """
        if isinstance(otherInformer, CProgressInformer):
            self._isEmitSummary = False
            self.total = otherInformer.total
            self.current = otherInformer.current
            self.description = otherInformer.description
            self._isEmitSummary = False


    def reset(self, newTotal = None, description = None):
        """
        Обнуляет текущее состояние прогреса.
        Устанавливает текущий шаг в стартовую/нулевую позицию. Общее число меняет на newTotal, если оно задано, иначе не изменяет.
        Обновляет описание текущего шага на description, если задан, либо на пустую строку.

        :param newTotal: новое общее число шагов.
        :param description: новое описание текущего состояния.
        """
        self._isEmitSummary = False
        self.current = max(0, self._start)
        if newTotal is not None:
            self.total = newTotal
        self.description = description if description is not None else u''

        self._isEmitSummary = True
        self.emitSummary()


    @QtCore.pyqtSlot()
    @QtCore.pyqtSlot(QtCore.QString)
    def nextStep(self, description = None):
        """
            Переходит на следующий шаг, обновляя описание на description, если оно задано.

        :param description: новое описание для очередного шага. Если не задано, оставляется прежнее.
        """
        self._isEmitSummary = False
        self.current += 1
        self.description = description
        self._isEmitSummary = True
        self.emitSummary()


    @QtCore.pyqtSlot()
    def emitSummary(self):
        """
        Вызывает сигнал смены всех основных параметров.
        И, при наличии инстанса для QCoreApplication, вызывает обработчик событий приложения.
        """
        if self._isEmitSummary:
            self.progressChanged.emit(self._current, self._total, self._description)

        if self._processEventsFlag is not None:
            app = QtCore.QCoreApplication.instance()
            if app:
                app.processEvents(self._processEventsFlag)





def main():
    import sys
    from PyQt4 import QtGui
    from library.ProgressBar import CProgressBar
    app = QtGui.QApplication(sys.argv)

    p = CProgressBar()
    p.setRange(0, 0)
    p.show()
    app.processEvents()

    pi = CProgressInformer(description=u'test')
    pi.progressChanged.connect(p.setProgress)
    pi.total = 1000
    for i in xrange(pi.total):
        for j in xrange(100000):
            x = 8 * 9
        pi.current += 1


    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


