# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from Ui_ParamsForExternalDialog import Ui_ParamsForExternalDialog
from Ui_PersonTemplateDialog import Ui_PersonTemplateDialog
from Ui_TemplateDialog import Ui_TemplateDialog
from Ui_TemplateDialogMany import Ui_TemplateDialogMany
from Ui_TemplateOnRotationDialog import Ui_TemplateOnRotationDialog
from Ui_TemplatePersonsCreate import Ui_TemplatePersonsCreate
from library.DialogBase import CDialogBase
from library.Utils import forceInt, forceString, forceStringEx, agreeNumberAndWord


def callObjectAttributeMethod(mainObject, objectName, methodName, *args):
    return callObjectMethod(getObjectAttribute(mainObject, objectName), methodName, *args)


def callObjectMethod(object, methodName, *args):
    return getObjectAttribute(object, methodName)(*args)


def getObjectAttribute(object, attrName):
    return object.__getattribute__(attrName)


listEdit = {'ambTimeRange': ['edtAmbTimeRange%d', 'edtAmbTimeRange%d2'],
            'homeTimeRange': ['edtHomeTimeRange%d', 'edtHomeTimeRange%d2'],
            'ambPlan': ['edtAmbPlan%d', 'edtAmbPlan%d2', 'edtAmbInterPlan%d'],
            'homePlan': ['edtHomePlan%d', 'edtHomePlan%d2'],
            'ambInterval': ['edtAmbInterval%d', 'edtAmbInterval%d2', 'edtAmbInterInterval%d'],
            'homeInterval': ['edtHomeInterval%d', 'edtHomeInterval%d2']}


def setSignalMapper(self, nameObjects, define, countObjects=None):
    u"""
    Функция для обробоки сигналов, испускаемых несколькими объектами, одним слотом

    :param self: объект класса
    :param nameObjects: список имен объектов
    :param define: слот
    :param countObjects: кол-во объектов
    :return:
    """
    signalMapper = QtCore.QSignalMapper(self)
    indexObject = 0
    countObjects = (len(nameObjects) * 7) / len(nameObjects) if countObjects is None else countObjects
    for nameObject in nameObjects:
        for i in xrange(countObjects):
            object = getObjectAttribute(self, nameObject % (i + 1))
            self.connect(object, QtCore.SIGNAL('editingFinished()'), signalMapper, QtCore.SLOT('map()'))
            signalMapper.setMapping(object, indexObject + i)
        indexObject += countObjects
        signalMapper.mapped.connect(define)


def getOutTurnTime(self, index, secondPeriod=True):
    u"""
    Функция, возвращающая период "Все интервала"

    :param self: объект класса
    :param index: индекс СTimeRangeEdit-a
    :param secondPeriod: второй период
    :return:
    """
    ambTimeRange1 = getObjectAttribute(self, 'edtAmbTimeRange%d' % (index)).timeRange()
    ambTimeRange2 = getObjectAttribute(self, 'edtAmbTimeRange%d2' % (index)).timeRange()
    if ambTimeRange1 and ambTimeRange2 and secondPeriod:
        return ambTimeRange1[1], ambTimeRange2[0]
    return None


def getTimeRange(self, index, indexTimeRange, type):
    u"""
    Функция, возвращающая период времени для приема

    :param self: объект класса
    :param index: индекс СTimeRangeEdit-a
    :param indexTimeRange: индекс периода
    :param type: прием или вызов
    :return:
    """
    return getObjectAttribute(self, type[indexTimeRange] % (index)).timeRange()


def getDiffTime(timeRange):
    u"""
    Функция для получения периода приема в минутах
    :param timeRange: период
    :return:
    """
    if timeRange:
        timeStart, timeFinish = timeRange
        return abs(timeFinish.secsTo(timeStart) / 60)
    else:
        return None


def setValue(self, timeRange, value, edit):
    u"""
    Функция для установки значения интервала или плана в spinBox

    :param self: объект класса
    :param timeRange: период
    :param value: значение периода или плана
    :param edit: spinBox, в который устанавливается значение
    :return:
    """
    diffTime = getDiffTime(timeRange)
    if not value.value():
        return
    if diffTime and value:
        callObjectAttributeMethod(self, edit, 'setValue', diffTime / forceInt(value.value()))
    else:
        callObjectAttributeMethod(self, edit, 'setValue', 0)


def conversion(self, ind, edit, indexTimeRange, value, type, secondPeriod=True):
    u"""
    Функиция для перевода интервала в план и обратно

    :param self: объект класса
    :param ind: индекс текущего spinBox-а
    :param edit: spinBox, для которого осуществляется перевод
    :param indexTimeRange: индекс периода (если indexTimeRange == None, то рассматривается "Вне интервала")
    :param value: значение плана или интервала
    :param type: прием или вызов
    :param secondPeriod: второй период
    :return:
    """
    if indexTimeRange is not None:
        setValue(
            self,
            getTimeRange(self, ind, indexTimeRange, type),
            getObjectAttribute(self, edit),
            value[indexTimeRange] % (ind)
        )
    else:
        setValue(self, getOutTurnTime(self, ind, secondPeriod), getObjectAttribute(self, edit), value[2] % (ind))


def setSpinBoxInterval(self, ind, edit, indexTimeRange, type, secondPeriod=True, onlyOutPeriod=False):
    u"""
    Функция для установки минимального и максимального значений spinBox-а
    аргументы как и у функции conversion

    :param self:
    :param ind:
    :param edit:
    :param indexTimeRange:
    :param type:
    :param secondPeriod:
    :param onlyOutPeriod:
    :return:
    """
    if QtGui.qApp.isAllowedIntersectionOfTime():
        if not onlyOutPeriod:
            maxValue = abs(getDiffTime(getTimeRange(self, ind, indexTimeRange, type)))
            callObjectAttributeMethod(self, edit, 'setMinimum', 1)
            callObjectAttributeMethod(self, edit, 'setMaximum', maxValue)
    else:
        firstTime = callObjectAttributeMethod(self, type[0] % (ind), 'timeRange')
        secondTime = callObjectAttributeMethod(self, type[1] % (ind), 'timeRange')
        if firstTime:
            if firstTime[0] >= firstTime[1]:
                callObjectAttributeMethod(
                    self, type[0] % (ind), 'setStrTimeRange', (firstTime[0].toString('HH:mm'), '  :  ')
                )
        if firstTime and secondTime:
            if secondTime[0] <= firstTime[1]:
                callObjectAttributeMethod(
                    self, type[1] % (ind), 'setTimeRange', (firstTime[1], secondTime[1]))
        if secondTime:
            if secondTime[0] >= secondTime[1]:
                callObjectAttributeMethod(
                    self, type[1] % (ind), 'setStrTimeRange', (secondTime[0].toString('HH:mm'), '  :  ')
                )

        if not onlyOutPeriod:
            callObjectAttributeMethod(self, edit, 'setMinimum', 1)
            maxValue = getTimeRange(self, ind, indexTimeRange, type)
            if maxValue:
                callObjectAttributeMethod(self, edit, 'setMaximum', abs(getDiffTime(maxValue)))
    diffTime = getOutTurnTime(self, ind, secondPeriod)
    if diffTime is not None and edit[3:6] == 'Amb':
        callObjectAttributeMethod(self, 'edtAmbInterPlan%d' % (ind), 'setMinimum', 1)
        callObjectAttributeMethod(self, 'edtAmbInterInterval%d' % (ind), 'setMinimum', 1)
        diffTime = getDiffTime(diffTime)
        callObjectAttributeMethod(self, 'edtAmbInterPlan%d' % (ind), 'setMaximum', abs(diffTime))
        callObjectAttributeMethod(self, 'edtAmbInterInterval%d' % (ind), 'setMaximum', abs(diffTime))


def setInterval(value1, value2, valueInter=None):
    intervals = ''
    if value1:
        intervals += forceString(value1)
    if valueInter:
        intervals += ',' + forceString(valueInter)
    if value2:
        intervals += ',' + forceString(value2)
    return intervals


class CTemplateDialog(CDialogBase, Ui_TemplateDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbReasonOfAbsence1.setTable('rbReasonOfAbsence')
        self.cmbReasonOfAbsence2.setTable('rbReasonOfAbsence')
        self.cmbReasonOfAbsence3.setTable('rbReasonOfAbsence')
        self.cmbReasonOfAbsence4.setTable('rbReasonOfAbsence')
        self.cmbReasonOfAbsence5.setTable('rbReasonOfAbsence')
        self.cmbReasonOfAbsence6.setTable('rbReasonOfAbsence')
        self.cmbReasonOfAbsence7.setTable('rbReasonOfAbsence')
        today = QtCore.QDate.currentDate()
        self.edtBegDate.setDateRange(today.addMonths(-1), today.addMonths(13))
        self.edtEndDate.setDateRange(today.addMonths(-1), today.addMonths(13))
        self.edtBegDate.setDate(QtCore.QDate(today.year(), today.month(), 1))
        self.edtEndDate.setDate(QtCore.QDate(today.year(), today.month(), today.daysInMonth()))
        self.edtBegDate.setFocus(QtCore.Qt.OtherFocusReason)
        self.prepareColors()
        self.personId = None

        setSignalMapper(self, listEdit['ambTimeRange'], self.edtAmbTimeRange_editingFinished)
        setSignalMapper(self, listEdit['homeTimeRange'], self.edtHomeTimeRange_editingFinished)
        setSignalMapper(self, listEdit['ambPlan'], self.edtAmbPlan_editingFinished)
        setSignalMapper(self, listEdit['homePlan'], self.edtHomePlan_editingFinished)
        setSignalMapper(self, listEdit['ambInterval'], self.edtAmbInterval_editingFinished)
        setSignalMapper(self, listEdit['homeInterval'], self.edtHomeInterval_editingFinished)

    def prepareColors(self):
        for i in xrange(7):
            callObjectAttributeMethod(self, 'btnAmbColor%d' % (i + 1), 'setStandardColors')
            callObjectAttributeMethod(self, 'btnAmbColor%d2' % (i + 1), 'setStandardColors')
            callObjectAttributeMethod(self, 'btnAmbInterColor%d' % (i + 1), 'setStandardColors')
            callObjectAttributeMethod(self, 'btnAmbColor%d' % (i + 1), 'setCurrentColor', QtCore.Qt.white)
            callObjectAttributeMethod(self, 'btnAmbColor%d2' % (i + 1), 'setCurrentColor', QtCore.Qt.white)
            callObjectAttributeMethod(self, 'btnAmbInterColor%d' % (i + 1), 'setCurrentColor', QtCore.Qt.white)

    def setPersonId(self, personId):
        self.personId = personId

    def setDateRange(self, begDate, endDate):
        self.edtBegDate.setDateRange(begDate, endDate)
        self.edtEndDate.setDateRange(begDate, endDate)
        self.edtBegDate.setDate(begDate)
        self.edtEndDate.setDate(endDate)

    def setPersonInfo(self, personId):
        db = QtGui.qApp.db
        record = db.getRecord('Person', 'office, ambPlan, homPlan, office2, ambPlan2, homPlan2, expPlan', personId)
        if record:
            office = forceString(record.value('office'))
            ambPlan = forceInt(record.value('ambPlan'))
            homePlan = forceInt(record.value('homPlan'))
            expPlan = forceInt(record.value('expPlan'))
            office2 = forceString(record.value('office2'))
            ambPlan2 = forceInt(record.value('ambPlan2'))
            homePlan2 = forceInt(record.value('homPlan2'))
            if not ambPlan2:
                ambPlan2 = 0
            if not homePlan2:
                homePlan2 = 0

            for i in range(7):
                callObjectAttributeMethod(self, 'edtAmbOffice%d2' % (i + 1), 'setText', office2)
                callObjectAttributeMethod(self, 'edtAmbPlan%d2' % (i + 1), 'setValue', ambPlan2)
                callObjectAttributeMethod(self, 'edtHomePlan%d2' % (i + 1), 'setValue', homePlan2)
                callObjectAttributeMethod(self, 'edtAmbOffice%d' % (i + 1), 'setText', office)
                callObjectAttributeMethod(self, 'edtAmbPlan%d' % (i + 1), 'setValue', ambPlan)
                callObjectAttributeMethod(self, 'edtHomePlan%d' % (i + 1), 'setValue', homePlan)

    def getWorkPlan(self):
        daysPlanList = []
        for i in range(7):
            result = self.getDayPlan(
                getObjectAttribute(self, 'edtAmbTimeRange%d' % (i+1)), getObjectAttribute(self, 'edtAmbOffice%d' % (i+1)),
                getObjectAttribute(self, 'edtAmbPlan%d' % (i+1)),
                getObjectAttribute(self, 'edtAmbInterval%d' % (i+1)),
                getObjectAttribute(self, 'btnAmbColor%d' % (i+1)),
                getObjectAttribute(self, 'edtAmbTimeRange%d2' % (i+1)), getObjectAttribute(self, 'edtAmbOffice%d2' % (i+1)),
                getObjectAttribute(self, 'edtAmbPlan%d2' % (i+1)),
                getObjectAttribute(self, 'edtAmbInterval%d2' % (i+1)),
                getObjectAttribute(self, 'btnAmbColor%d2' % (i+1)),
                getObjectAttribute(self, 'edtHomeTimeRange%d' % (i+1)),
                getObjectAttribute(self, 'edtHomePlan%d'%(i+1)),
                getObjectAttribute(self, 'edtHomeInterval%d'%(i+1)),
                getObjectAttribute(self, 'cmbReasonOfAbsence%d' % (i+1)),
                getObjectAttribute(self, 'edtHomeTimeRange%d2' % (i+1)),
                getObjectAttribute(self, 'edtHomePlan%d2' % (i+1)),
                getObjectAttribute(self, 'edtHomeInterval%d2' % (i+1)),
                getObjectAttribute(self, 'edtAmbInterOffice%d' % (i+1)),
                getObjectAttribute(self, 'edtAmbInterPlan%d' % (i+1)),
                getObjectAttribute(self, 'edtAmbInterInterval%d' % (i+1)),
                getObjectAttribute(self, 'btnAmbInterColor%d' % (i+1)),
                getObjectAttribute(self, 'chkNotExternalSystem%d' % (i+1)),
                getObjectAttribute(self, 'chkNotExternalSystem%d2' % (i+1)),
                getObjectAttribute(self, 'chkInterNotExternalSystem%d' % (i+1)),
                )
            daysPlanList.append(result)

        daysPlans = []
        if self.rbSingle.isChecked():
            daysPlans = daysPlanList[:1]
        if self.rbDual.isChecked():
            daysPlans = daysPlanList[:2]
        if self.rbNed.isChecked():
            if self.chkFillRedDays.isChecked():
                daysPlans = daysPlanList
            else:
                daysPlans = daysPlanList[:5]
        return (daysPlans, self.chkFillRedDays.isChecked())

    def getDayPlan(self, edtAmbTimeRange, edtAmbOffice, edtAmbPlan, edtAmbInterval, btnAmbColor, edtAmbTimeRange2,
                   edtAmbOffice2, edtAmbPlan2, edtAmbInterval2, btnAmbColor2, edtHomeTimeRange, edtHomePlan,
                   edtHomeInterval, cmbReasonOfAbsence, edtHomeTimeRange2, edtHomePlan2, edtHomeInterval2,
                   edtAmbInterOffice, edtAmbInterPlan, edtAmbInterInterval, btnAmbInterColor, chkNotExternalSystem1,
                   chkNotExternalSystem12, chkInterNotExternalSystem1):
        return (
        self.getTaskPlan(
            edtAmbTimeRange,
            edtAmbOffice,
            edtAmbPlan,
            edtAmbInterval,
            btnAmbColor,
            edtAmbTimeRange2,
            edtAmbOffice2,
            edtAmbPlan2,
            edtAmbInterval2,
            btnAmbColor2,
            edtAmbInterOffice,
            edtAmbInterPlan,
            edtAmbInterInterval,
            btnAmbInterColor
        ),
        self.getTaskPlan(
            edtHomeTimeRange,
            None,
            edtHomePlan,
            edtHomeInterval,
            None,
            edtHomeTimeRange2,
            None,
            edtHomePlan2,
            edtHomeInterval2,
            None,
            None,
            None,
            None,
            None
        ),
        self.getTaskPlan(None, None, None, None, None, None, None, None, None, None, None, None, None, None),
        cmbReasonOfAbsence.value(),
        chkNotExternalSystem1.isChecked(),
        chkNotExternalSystem12.isChecked(),
        chkInterNotExternalSystem1.isChecked()
        )

    def getTaskPlan(self, edtTimeRange, edtOffice, edtPlan, edtInterval, btnColor, edtTimeRange2, edtOffice2, edtPlan2, edtInterval2, btnColor2, edtInterOffice, edtInterPlan, edtInterInterval, btnInterColor):
        # Проверяем наличие двух периодов
        if edtTimeRange2 and edtTimeRange2.isEnabled():
            timeRange2 = edtTimeRange2.timeRange() if edtTimeRange2 else None
            if timeRange2:
                timeStart2, timeFinish2 = timeRange2
            else:
                timeStart2 = None
                timeFinish2 = None
            timeRange1 = edtTimeRange.timeRange() if edtTimeRange else None
            if timeRange1:
                timeStart, timeFinish = timeRange1
            else:
                timeStart = None
                timeFinish = None

            timeRangeStart = min(timeStart, timeStart2) if (timeStart and timeStart2) else (timeStart if timeStart else (timeStart2 if timeStart2 else None))
            timeRangeFinish = max(timeFinish, timeFinish2) if (timeFinish and timeFinish2) else (timeFinish if timeFinish else (timeFinish2 if timeFinish2 else None))
            if timeRangeStart and timeRangeFinish:
                timeRange = timeRangeStart, timeRangeFinish
            else:
                timeRange = None
        else:
            timeRange2 = None
            timeRange1 = None
            timeRange = edtTimeRange.timeRange() if edtTimeRange else None
            if timeRange is None:
                return tuple([None] * 19)

        # Проверяем наличие двух кабинетов
        if edtOffice2 and edtOffice2.isEnabled():
            office2 = forceStringEx(edtOffice2.text()) if edtOffice2 else None
            office1 = forceStringEx(edtOffice.text()) if edtOffice else None
            if edtInterOffice and edtInterOffice.isEnabled():
                interOffice = forceStringEx(edtInterOffice.text()) if edtInterOffice else None
                office = office1 + u', ' + interOffice + u', ' + office2
            else:
                interOffice = None
                office = office1 + u', ' + office2
        else:
            interOffice = None
            office2 = None
            office1 = None
            office = forceStringEx(edtOffice.text()) if edtOffice else None

        # Проверяем наличие двух планов
        if edtPlan2 and edtPlan2.isEnabled():
            plan2 = edtPlan2.value() if edtPlan2 else 0
            interval2 = edtInterval2.value() if edtInterval2 else 0
            plan1 = edtPlan.value() if edtPlan else 0
            interval1 = edtInterval.value() if edtInterval else 0
            if edtInterPlan and edtInterPlan.isEnabled():
                interPlan = edtInterPlan.value() if edtInterPlan else 0
                interInterval = edtInterInterval.value() if edtInterInterval else 0
                plan = plan1 + plan2 + interPlan
                interval = setInterval(interval1, interval2, interInterval)
            else:
                interPlan = 0
                interInterval = None
                plan = plan1 + plan2
                interval = setInterval(interval1, interval2)
        else:
            plan2 = None
            interval2 = None
            plan1 = None
            interval1 = None
            interPlan = None
            interInterval = None
            interval = edtInterval.value() if edtInterval else None
            plan = edtPlan.value() if edtPlan else None

        # Проверяем наличие двух цветов:
        if btnColor2 and btnColor2.isEnabled():
            color2 = btnColor2.currentColorName()
            if color2 == u'#ffffff':
                color2 = None

            if btnInterColor and btnInterColor.isEnabled():
                interColor = btnInterColor.currentColorName()
                if interColor == u'#ffffff':
                    interColor = None
            else:
                interColor = None

        else:
            color2 = None
            interColor = None

        color = color1 = btnColor.currentColorName() if btnColor else None
        if color == u'#ffffff':
            color = None
            color1 = None

        return timeRange, office, plan, interval, color, timeRange1, office1, plan1, interval1, color1, timeRange2, office2, plan2, interval2, color2, interOffice, interPlan, interInterval, interColor

    def getDateRange(self):
        return (self.edtBegDate.date(), self.edtEndDate.date())

    def setEnabledAmbSecondPeriod(self, checked):
        self.edtAmbTimeRange12.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbOffice12.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbPlan12.setEnabled(checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbInterval12.setEnabled(checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.lblAmbInterval12.setEnabled(checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.btnAmbColor12.setEnabled(checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.chkNotExternalSystem12.setEnabled(checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbTimeRange22.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbOffice22.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbPlan22.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbInterval22.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.lblAmbInterval22.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.btnAmbColor22.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.chkNotExternalSystem22.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbTimeRange32.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbOffice32.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbPlan32.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbInterval32.setEnabled(checked and self.rbNed.isChecked())
        self.lblAmbInterval32.setEnabled(checked and self.rbNed.isChecked())
        self.btnAmbColor32.setEnabled(checked and self.rbNed.isChecked())
        self.chkNotExternalSystem32.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbTimeRange42.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbOffice42.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbPlan42.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbInterval42.setEnabled(checked and self.rbNed.isChecked())
        self.lblAmbInterval42.setEnabled(checked and self.rbNed.isChecked())
        self.btnAmbColor42.setEnabled(checked and self.rbNed.isChecked())
        self.chkNotExternalSystem42.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbTimeRange52.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbOffice52.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbPlan52.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbInterval52.setEnabled(checked and self.rbNed.isChecked())
        self.lblAmbInterval52.setEnabled(checked and self.rbNed.isChecked())
        self.btnAmbColor52.setEnabled(checked and self.rbNed.isChecked())
        self.chkNotExternalSystem52.setEnabled(checked and self.rbNed.isChecked())

        self.edtAmbTimeRange62.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtAmbOffice62.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtAmbPlan62.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtAmbInterval62.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.lblAmbInterval62.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.btnAmbColor62.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.chkNotExternalSystem62.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())

        self.edtAmbTimeRange72.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtAmbOffice72.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtAmbPlan72.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtAmbInterval72.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.lblAmbInterval72.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.btnAmbColor72.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.chkNotExternalSystem72.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())

    def setEnabledAmbInterPeriod(self, checked):
        self.edtAmbInterOffice1.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbInterPlan1.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbInterInterval1.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.lblAmbInterInterval1.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.btnAmbInterColor1.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.chkInterNotExternalSystem1.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbInterOffice2.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbInterPlan2.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbInterInterval2.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.lblAmbInterInterval2.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.btnAmbInterColor2.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.chkInterNotExternalSystem2.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbInterOffice3.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbInterPlan3.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbInterInterval3.setEnabled(checked and self.rbNed.isChecked())
        self.lblAmbInterInterval3.setEnabled(checked and self.rbNed.isChecked())
        self.btnAmbInterColor3.setEnabled(checked and self.rbNed.isChecked())
        self.chkInterNotExternalSystem3.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbInterOffice4.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbInterPlan4.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbInterInterval4.setEnabled(checked and self.rbNed.isChecked())
        self.lblAmbInterInterval4.setEnabled(checked and self.rbNed.isChecked())
        self.btnAmbInterColor4.setEnabled(checked and self.rbNed.isChecked())
        self.chkInterNotExternalSystem4.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbInterOffice5.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbInterPlan5.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbInterInterval5.setEnabled(checked and self.rbNed.isChecked())
        self.lblAmbInterInterval5.setEnabled(checked and self.rbNed.isChecked())
        self.btnAmbInterColor5.setEnabled(checked and self.rbNed.isChecked())
        self.chkInterNotExternalSystem5.setEnabled(checked and self.rbNed.isChecked())

        self.edtAmbInterOffice6.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtAmbInterPlan6.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtAmbInterInterval6.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.lblAmbInterInterval6.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.btnAmbInterColor6.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.chkInterNotExternalSystem6.setEnabled(
            checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())

        self.edtAmbInterOffice7.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtAmbInterPlan7.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtAmbInterInterval7.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.lblAmbInterInterval7.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.btnAmbInterColor7.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.chkInterNotExternalSystem7.setEnabled(
            checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())

    def setEnabledHomeSecondPeriod(self, checked):
        self.edtHomeTimeRange12.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtHomePlan12.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtHomeInterval12.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.lblHomeInterval12.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtHomeTimeRange22.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtHomePlan22.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtHomeInterval22.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.lblHomeInterval22.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtHomeTimeRange32.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomePlan32.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomeInterval32.setEnabled(checked and self.rbNed.isChecked())
        self.lblHomeInterval32.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomeTimeRange42.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomePlan42.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomeInterval42.setEnabled(checked and self.rbNed.isChecked())
        self.lblHomeInterval42.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomeTimeRange52.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomePlan52.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomeInterval52.setEnabled(checked and self.rbNed.isChecked())
        self.lblHomeInterval52.setEnabled(checked and self.rbNed.isChecked())

        self.edtHomeTimeRange62.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtHomePlan62.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())

        self.edtHomeTimeRange72.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtHomePlan72.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())

    def setEnabledWeekEnd(self, checked):
        self.edtAmbTimeRange6.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbOffice6.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbPlan6.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbInterval6.setEnabled(checked and self.rbNed.isChecked())
        self.lblAmbInterval6.setEnabled(checked and self.rbNed.isChecked())
        self.btnAmbColor6.setEnabled(checked and self.rbNed.isChecked())
        self.chkNotExternalSystem6.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbTimeRange7.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbOffice7.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbPlan7.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbInterval7.setEnabled(checked and self.rbNed.isChecked())
        self.lblAmbInterval7.setEnabled(checked and self.rbNed.isChecked())
        self.btnAmbColor7.setEnabled(checked and self.rbNed.isChecked())
        self.chkNotExternalSystem7.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomeTimeRange6.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomePlan6.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomeInterval6.setEnabled(checked and self.rbNed.isChecked())
        self.lblHomeInterval6.setEnabled(checked and self.rbNed.isChecked())
        self.cmbReasonOfAbsence6.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomeTimeRange7.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomePlan7.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomeInterval7.setEnabled(checked and self.rbNed.isChecked())
        self.lblHomeInterval7.setEnabled(checked and self.rbNed.isChecked())
        self.cmbReasonOfAbsence7.setEnabled(checked and self.rbNed.isChecked())

    def getCurrentObject(self, index, objects):
        if index < 7:
            ind = index + 1
            edit = objects[0] % (ind)
            indexTimeRange = 0
        elif index < 14:
            ind = index - 6
            edit = objects[1] % (ind)
            indexTimeRange = 1
        else:
            ind = index - 13
            edit = objects[2] % (ind)
            indexTimeRange = None
        return ind, edit, indexTimeRange

    def edtAmbTimeRange_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['ambInterval'])
        editPlan = listEdit['ambPlan'][indexTimeRange] % (ind)
        onlyOutPeriod = False
        if forceInt(getObjectAttribute(self, editPlan).value()):
            onlyOutPeriod = True
        setSpinBoxInterval(self, ind, edit, indexTimeRange, listEdit['ambTimeRange'], self.chkAmbSecondPeriod, onlyOutPeriod)
        setSpinBoxInterval(self, ind, editPlan, indexTimeRange, listEdit['ambTimeRange'], self.chkAmbSecondPeriod, onlyOutPeriod)
        if onlyOutPeriod:
            conversion(self, ind, editPlan, indexTimeRange, listEdit['ambInterval'], listEdit['ambTimeRange'], self.chkAmbSecondPeriod)
        else:
            conversion(self, ind, edit, indexTimeRange, listEdit['ambPlan'], listEdit['ambTimeRange'], self.chkAmbSecondPeriod)
        conversion(self, ind, 'edtAmbInterInterval%d' % (ind), None, listEdit['ambPlan'], None, self.chkAmbInterPeriod.isChecked())

    def edtHomeTimeRange_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['homeInterval'])
        editPlan = listEdit['homePlan'][indexTimeRange] % (ind)
        onlyOutPeriod = False
        if forceInt(getObjectAttribute(self, editPlan).value()):
            onlyOutPeriod = True
        setSpinBoxInterval(self, ind, edit, indexTimeRange, listEdit['homeTimeRange'], self.chkAmbSecondPeriod, onlyOutPeriod)
        setSpinBoxInterval(self, ind, editPlan, indexTimeRange, listEdit['homeTimeRange'], self.chkAmbSecondPeriod, onlyOutPeriod)
        if onlyOutPeriod:
            conversion(self, ind, editPlan, indexTimeRange, listEdit['homeInterval'], listEdit['homeTimeRange'], self.chkAmbSecondPeriod)
        else:
            conversion(self, ind, edit, indexTimeRange, listEdit['homePlan'], listEdit['homeTimeRange'], self.chkAmbSecondPeriod)
        conversion(self, ind, 'edtAmbInterInterval%d' % (ind), None, listEdit['ambPlan'], None, self.chkAmbInterPeriod.isChecked())

    def edtAmbPlan_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['ambPlan'])
        if getObjectAttribute(self, listEdit['ambTimeRange'][indexTimeRange] % (ind)).timeRange():
            conversion(self, ind, edit, indexTimeRange, listEdit['ambInterval'], listEdit['ambTimeRange'], self.chkAmbSecondPeriod)
        else:
            callObjectAttributeMethod(self, edit, 'setValue', 0)

    def edtAmbInterval_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['ambInterval'])
        if getObjectAttribute(self, listEdit['ambTimeRange'][indexTimeRange] % (ind)).timeRange():
            conversion(self, ind, edit, indexTimeRange, listEdit['ambPlan'], listEdit['ambTimeRange'], self.chkAmbSecondPeriod)
        else:
            callObjectAttributeMethod(self, edit, 'setValue', 0)

    def edtHomePlan_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['homePlan'])
        if getObjectAttribute(self, listEdit['homeTimeRange'][indexTimeRange] % (ind)).timeRange():
            conversion(self, ind, edit, indexTimeRange, listEdit['homeInterval'], listEdit['homeTimeRange'], self.chkAmbSecondPeriod)
        else:
            callObjectAttributeMethod(self, edit, 'setValue', 0)

    def edtHomeInterval_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['homeInterval'])
        if getObjectAttribute(self, listEdit['homeTimeRange'][indexTimeRange] % (ind)).timeRange():
            conversion(self, ind, edit, indexTimeRange, listEdit['homePlan'], listEdit['homeTimeRange'], self.chkAmbSecondPeriod)
        else:
            callObjectAttributeMethod(self, edit, 'setValue', 0)

    @QtCore.pyqtSlot(bool)
    def on_chkAmbSecondPeriod_clicked(self, checked):
        self.setEnabledAmbSecondPeriod(checked)
        if not checked and self.chkAmbInterPeriod.isChecked():
            self.chkAmbInterPeriod.setChecked(checked)
            self.setEnabledAmbInterPeriod(checked)

    @QtCore.pyqtSlot(bool)
    def on_chkAmbInterPeriod_clicked(self, checked):
        self.setEnabledAmbInterPeriod(checked)
        for index in xrange(7):
            conversion(self, index + 1, 'edtAmbInterInterval%d' % (index + 1), None, listEdit['ambPlan'], None, self.chkAmbInterPeriod.isChecked())

    @QtCore.pyqtSlot(bool)
    def on_chkHomeSecondPeriod_clicked(self, checked):
        self.setEnabledHomeSecondPeriod(checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFillRedDays_clicked(self, checked):
        self.setEnabledAmbSecondPeriod(self.chkAmbSecondPeriod.isChecked())
        self.setEnabledHomeSecondPeriod(self.chkHomeSecondPeriod.isChecked())
        self.setEnabledWeekEnd(checked)
        if self.rbNed.isChecked():
            self.edtAmbTimeRange6.setFocus(QtCore.Qt.OtherFocusReason)

    @QtCore.pyqtSlot(bool)
    def on_rbNed_toggled(self, checked):
        self.setEnabledAmbSecondPeriod(self.chkAmbSecondPeriod.isChecked())
        self.setEnabledHomeSecondPeriod(self.chkHomeSecondPeriod.isChecked())
        self.setEnabledWeekEnd(self.chkFillRedDays.isChecked())
        self.grbOnePlan.setTitle(u'Понедельник')
        self.grbOddEvenPlan.setTitle(u'Вторник')
        self.grbWeekPlan1.setTitle(u'Среда')
        self.grbWeekPlan2.setTitle(u'Четверг')
        self.grbWeekPlan3.setTitle(u'Пятница')
        self.grbWeekPlan4.setTitle(u'Суббота')
        self.grbWeekPlan5.setTitle(u'Воскресение')

    @QtCore.pyqtSlot(bool)
    def on_rbDual_toggled(self, checked):
        self.setEnabledAmbSecondPeriod(self.chkAmbSecondPeriod.isChecked())
        self.setEnabledHomeSecondPeriod(self.chkHomeSecondPeriod.isChecked())
        self.grbOnePlan.setTitle(u'Нечётный день')
        self.grbOddEvenPlan.setTitle(u'Чётный день')
        self.grbWeekPlan1.setTitle(u'')
        self.grbWeekPlan2.setTitle(u'')
        self.grbWeekPlan3.setTitle(u'')
        self.grbWeekPlan4.setTitle(u'')
        self.grbWeekPlan5.setTitle(u'')

    @QtCore.pyqtSlot(bool)
    def on_rbSingle_toggled(self, checked):
        self.setEnabledAmbSecondPeriod(self.chkAmbSecondPeriod.isChecked())
        self.setEnabledHomeSecondPeriod(self.chkHomeSecondPeriod.isChecked())
        self.grbOnePlan.setTitle(u'Каждый день')
        self.grbOddEvenPlan.setTitle(u'')
        self.grbWeekPlan1.setTitle(u'')
        self.grbWeekPlan2.setTitle(u'')
        self.grbWeekPlan3.setTitle(u'')
        self.grbWeekPlan4.setTitle(u'')
        self.grbWeekPlan5.setTitle(u'')


class CPersonTemplateDialog(CDialogBase, Ui_PersonTemplateDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        today = QtCore.QDate.currentDate()
        self.edtBegDate.setDateRange(today.addMonths(-1), today.addMonths(13))
        self.edtEndDate.setDateRange(today.addMonths(-1), today.addMonths(13))
        self.edtBegDate.setFocus(QtCore.Qt.OtherFocusReason)
        self.personIdList = []

    def setPersonIdList(self, personIdList):
        db = QtGui.qApp.db
        self.personIdList = personIdList
        for personId in self.personIdList:
            if len(self.personIdList) == 1:
                self.lblNamePerson.setText(forceString(db.translate('vrbPersonWithSpeciality', 'id', personId, 'name')))

    def setDateRange(self, begDate, endDate):
        self.edtBegDate.setDateRange(begDate, endDate)
        self.edtEndDate.setDateRange(begDate, endDate)
        self.edtBegDate.setDate(begDate)
        self.edtEndDate.setDate(endDate)

    def getDateRange(self):
        return (self.edtBegDate.date(), self.edtEndDate.date())

    @QtCore.pyqtSlot(bool)
    def on_chkAmbSecondPeriodPerson_clicked(self, checked):
        if not checked:
            self.chkAmbInterPeriodPerson.setChecked(False)


class CTemplatePersonsCreate(QtGui.QWizard, Ui_TemplatePersonsCreate):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ClassicStyle)
        self.setupUi(self)
        self.connect(self, QtCore.SIGNAL('rejected()'), self.abort)
        self.prbTemplateCreate.setMinimum(0)
        self.prbTemplateCreate.setMaximum(1)
        self.lblPersonName.setText('')
        self.abortProcess = False

    def abort(self):
        self.abortProcess = True


class CTemplateDialogMany(CDialogBase, Ui_TemplateDialogMany):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbReasonOfAbsence1.setTable('rbReasonOfAbsence')
        self.cmbReasonOfAbsence2.setTable('rbReasonOfAbsence')
        self.cmbReasonOfAbsence3.setTable('rbReasonOfAbsence')
        self.cmbReasonOfAbsence4.setTable('rbReasonOfAbsence')
        self.cmbReasonOfAbsence5.setTable('rbReasonOfAbsence')
        self.cmbReasonOfAbsence6.setTable('rbReasonOfAbsence')
        self.cmbReasonOfAbsence7.setTable('rbReasonOfAbsence')
        today = QtCore.QDate.currentDate()
        self.edtBegDate.setDateRange(today.addMonths(-1), today.addMonths(13))
        self.edtEndDate.setDateRange(today.addMonths(-1), today.addMonths(13))
        self.edtBegDate.setFocus(QtCore.Qt.OtherFocusReason)
        self.personId = None

    def setPersonId(self, personId):
        self.personId = personId

    def setDateRange(self, begDate, endDate):
        self.edtBegDate.setDateRange(begDate, endDate)
        self.edtEndDate.setDateRange(begDate, endDate)
        self.edtBegDate.setDate(begDate)
        self.edtEndDate.setDate(endDate)

    def getWorkPlan(self):
        daysPlans = []
        if self.personId:
            db = QtGui.qApp.db
            record = db.getRecord('Person', 'office, ambPlan, homPlan, office2, ambPlan2, homPlan2', self.personId)
            if record:
                ambOffice1 = forceString(record.value('office'))
                ambPlan1 = forceInt(record.value('ambPlan'))
                homePlan1 = forceInt(record.value('homPlan'))
                if self.chkAmbSecondPeriod.isChecked():
                    ambOffice2 = forceString(record.value('office2'))
                    ambPlan2 = forceInt(record.value('ambPlan2'))
                else:
                    ambOffice2 = None
                    ambPlan2 = None
                if self.chkHomeSecondPeriod.isChecked():
                    homePlan2 = forceInt(record.value('homPlan2'))
                else:
                    homePlan2 = None

                daysPlanList = []
                for i in range(7):
                    result = self.getDayPlan(
                        getObjectAttribute(self, 'edtAmbTimeRange%d' % (i + 1)), ambOffice1, ambPlan1,
                        getObjectAttribute(self, 'edtAmbTimeRange%d2' % (i + 1)), ambOffice2, ambPlan2,
                        getObjectAttribute(self, 'edtHomeTimeRange%d' % (i + 1)), homePlan1,
                        getObjectAttribute(self, 'cmbReasonOfAbsence%d' % (i + 1)),
                        getObjectAttribute(self, 'edtHomeTimeRange%d2' % (i + 1)), homePlan2
                    )
                    daysPlanList.append(result)

                if self.rbSingle.isChecked():
                    daysPlans = daysPlanList[:1]
                if self.rbDual.isChecked():
                    daysPlans = daysPlanList[:2]
                if self.rbNed.isChecked():
                    if self.chkFillRedDays.isChecked():
                        daysPlans = daysPlanList
                    else:
                        daysPlans = daysPlanList[:5]
        return (daysPlans, self.chkFillRedDays.isChecked())

    def getDayPlan(self, edtAmbTimeRange, edtAmbOffice, edtAmbPlan, edtAmbTimeRange2, edtAmbOffice2, edtAmbPlan2,
                   edtHomeTimeRange, edtHomePlan, cmbReasonOfAbsence, edtHomeTimeRange2, edtHomePlan2):
        return (
        self.getTaskPlan(edtAmbTimeRange, edtAmbOffice, edtAmbPlan, edtAmbTimeRange2, edtAmbOffice2, edtAmbPlan2),
        self.getTaskPlan(edtHomeTimeRange, None, edtHomePlan, edtHomeTimeRange2, None, edtHomePlan2),
        self.getTaskPlan(None, None, None, None, None, None),
        cmbReasonOfAbsence.value()
        )

    def getTaskPlan(self, edtTimeRange, edtOffice, edtPlan, edtTimeRange2, edtOffice2, edtPlan2):
        if edtTimeRange2 and edtTimeRange2.isEnabled():
            timeRange2 = edtTimeRange2.timeRange() if edtTimeRange2 else None
            if timeRange2:
                timeStart2, timeFinish2 = timeRange2
            else:
                timeStart2 = None
                timeFinish2 = None
            timeRange1 = edtTimeRange.timeRange() if edtTimeRange else None
            if timeRange1:
                timeStart, timeFinish = timeRange1
            else:
                timeStart = None
                timeFinish = None

            timeRangeStart = min(timeStart, timeStart2) if (timeStart and timeStart2) else (timeStart if timeStart else (timeStart2 if timeStart2 else None))
            timeRangeFinish = max(timeFinish, timeFinish2) if (timeFinish and timeFinish2) else (timeFinish if timeFinish else (timeFinish2 if timeFinish2 else None))
            if timeRangeStart and timeRangeFinish:
                timeRange = timeRangeStart, timeRangeFinish
            else:
                timeRange = None
        else:
            timeRange2 = None
            timeRange1 = None
            timeRange = edtTimeRange.timeRange() if edtTimeRange else None

        if edtOffice2:
            office2 = forceStringEx(edtOffice2) if edtOffice2 else None
            office1 = forceStringEx(edtOffice) if edtOffice else None
            office = office1 + u', ' + office2
        else:
            office2 = None
            office1 = None
            office = forceStringEx(edtOffice) if edtOffice else None

        if edtPlan2:
            plan2 = edtPlan2 if edtPlan2 else 0
            plan1 = edtPlan if edtPlan else 0
            plan = plan1 + plan2
        else:
            plan2 = None
            plan1 = None
            plan = edtPlan if edtPlan else None
        return (timeRange, office, plan, timeRange1, office1, plan1, timeRange2, office2, plan2)

    def getDateRange(self):
        return (self.edtBegDate.date(), self.edtEndDate.date())

    def setEnabledAmbSecondPeriod(self, checked):
        self.edtAmbTimeRange12.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbTimeRange22.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtAmbTimeRange32.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbTimeRange42.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbTimeRange52.setEnabled(checked and self.rbNed.isChecked())

        self.edtAmbTimeRange62.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtAmbTimeRange72.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())

    def setEnabledHomeSecondPeriod(self, checked):
        self.edtHomeTimeRange12.setEnabled(
            checked and (self.rbSingle.isChecked() or self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtHomeTimeRange22.setEnabled(checked and (self.rbDual.isChecked() or self.rbNed.isChecked()))
        self.edtHomeTimeRange32.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomeTimeRange42.setEnabled(checked and self.rbNed.isChecked())
        self.edtHomeTimeRange52.setEnabled(checked and self.rbNed.isChecked())

        self.edtHomeTimeRange62.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())
        self.edtHomeTimeRange72.setEnabled(checked and self.rbNed.isChecked() and self.chkFillRedDays.isChecked())

    def setEnabledWeekEnd(self, checked):
        self.edtAmbTimeRange6.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbOffice6.setEnabled(checked and self.rbNed.isChecked())
        self.cmbReasonOfAbsence6.setEnabled(checked and self.rbNed.isChecked())

        self.edtAmbTimeRange7.setEnabled(checked and self.rbNed.isChecked())
        self.edtAmbOffice7.setEnabled(checked and self.rbNed.isChecked())
        self.cmbReasonOfAbsence7.setEnabled(checked and self.rbNed.isChecked())

    @QtCore.pyqtSlot(bool)
    def on_chkAmbSecondPeriod_clicked(self, checked):
        self.setEnabledAmbSecondPeriod(checked)

    @QtCore.pyqtSlot(bool)
    def on_chkHomeSecondPeriod_clicked(self, checked):
        self.setEnabledHomeSecondPeriod(checked)

    @QtCore.pyqtSlot(bool)
    def on_chkFillRedDays_clicked(self, checked):
        self.setEnabledAmbSecondPeriod(self.chkAmbSecondPeriod.isChecked())
        self.setEnabledHomeSecondPeriod(self.chkHomeSecondPeriod.isChecked())
        self.setEnabledWeekEnd(checked)
        if self.rbNed.isChecked():
            self.edtAmbTimeRange6.setFocus(QtCore.Qt.OtherFocusReason)

    @QtCore.pyqtSlot(bool)
    def on_rbNed_toggled(self, checked):
        self.setEnabledAmbSecondPeriod(self.chkAmbSecondPeriod.isChecked())
        self.setEnabledHomeSecondPeriod(self.chkHomeSecondPeriod.isChecked())
        self.setEnabledWeekEnd(self.chkFillRedDays.isChecked())
        self.grbOnePlan.setTitle(u'Понедельник')
        self.grbOddEvenPlan.setTitle(u'Вторник')
        self.grbWeekPlan1.setTitle(u'Среда')
        self.grbWeekPlan2.setTitle(u'Четверг')
        self.grbWeekPlan3.setTitle(u'Пятница')
        self.grbWeekPlan4.setTitle(u'Суббота')
        self.grbWeekPlan5.setTitle(u'Воскресение')

    @QtCore.pyqtSlot(bool)
    def on_rbDual_toggled(self, checked):
        self.setEnabledAmbSecondPeriod(self.chkAmbSecondPeriod.isChecked())
        self.setEnabledHomeSecondPeriod(self.chkHomeSecondPeriod.isChecked())
        self.grbOnePlan.setTitle(u'Нечётный день')
        self.grbOddEvenPlan.setTitle(u'Чётный день')
        self.grbWeekPlan1.setTitle(u'')
        self.grbWeekPlan2.setTitle(u'')
        self.grbWeekPlan3.setTitle(u'')
        self.grbWeekPlan4.setTitle(u'')
        self.grbWeekPlan5.setTitle(u'')

    @QtCore.pyqtSlot(bool)
    def on_rbSingle_toggled(self, checked):
        self.setEnabledAmbSecondPeriod(self.chkAmbSecondPeriod.isChecked())
        self.setEnabledHomeSecondPeriod(self.chkHomeSecondPeriod.isChecked())
        self.grbOnePlan.setTitle(u'Каждый день')
        self.grbOddEvenPlan.setTitle(u'')
        self.grbWeekPlan1.setTitle(u'')
        self.grbWeekPlan2.setTitle(u'')
        self.grbWeekPlan3.setTitle(u'')
        self.grbWeekPlan4.setTitle(u'')
        self.grbWeekPlan5.setTitle(u'')


class CTemplateOnRotationDialog(CDialogBase, Ui_TemplateOnRotationDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.cmbReasonOfAbsence1.setTable('rbReasonOfAbsence')
        self.calendarTemplateOnRotation.setList(QtGui.qApp.calendarInfo)
        self.personId = None
        self.selectedDaysList = []
        self.prepareColors()
        setSignalMapper(self, listEdit['ambTimeRange'], self.edtAmbTimeRange_editingFinished, 1)
        setSignalMapper(self, listEdit['homeTimeRange'], self.edtHomeTimeRange_editingFinished, 1)
        setSignalMapper(self, listEdit['ambPlan'], self.edtAmbPlan_editingFinished, 1)
        setSignalMapper(self, listEdit['homePlan'], self.edtHomePlan_editingFinished, 1)
        setSignalMapper(self, listEdit['ambInterval'], self.edtAmbInterval_editingFinished, 1)
        setSignalMapper(self, listEdit['homeInterval'], self.edtHomeInterval_editingFinished, 1)

    def prepareColors(self):
        self.btnAmbColor1.setStandardColors()
        self.btnAmbInterColor1.setStandardColors()
        self.btnAmbColor12.setStandardColors()
        self.btnAmbColor1.setCurrentColor(QtCore.Qt.white)
        self.btnAmbColor12.setCurrentColor(QtCore.Qt.white)
        self.btnAmbInterColor1.setCurrentColor(QtCore.Qt.white)

    def setPersonId(self, personId):
        self.personId = personId

    def setDateRange(self, begDate, endDate):
        self.calendarTemplateOnRotation.setMaximumDate(endDate)
        self.calendarTemplateOnRotation.setMinimumDate(begDate)
        startDate = QtCore.QDate.currentDate()
        if begDate.month() != startDate.month():
            startDate = begDate
        self.calendarTemplateOnRotation.setSelectedDate(startDate)

    def setPersonInfo(self, personId):
        db = QtGui.qApp.db
        # table = db.table('Person')
        record = db.getRecord('Person', 'office, ambPlan, homPlan, office2, ambPlan2, homPlan2, expPlan', personId)
        if record:
            office = forceString(record.value('office'))
            ambInterval = forceInt(record.value('ambPlan'))
            homeInterval = forceInt(record.value('homPlan'))
            # expPlan = forceInt(record.value('expPlan'))
            office2 = forceString(record.value('office2'))
            ambInterval2 = forceInt(record.value('ambPlan2'))
            homeInterval2 = forceInt(record.value('homPlan2'))
            self.edtAmbOffice12.setText(office2)
            self.edtAmbPlan12.setValue(ambInterval2)
            self.edtHomePlan12.setValue(homeInterval2)
            self.edtAmbOffice1.setText(office)
            self.edtAmbPlan1.setValue(ambInterval)
            self.edtHomePlan1.setValue(homeInterval)

    def getWorkPlan(self):
        dayPlan1 = self.getDayPlan(
            self.edtAmbTimeRange1, self.edtAmbOffice1, self.edtAmbPlan1, self.edtAmbInterval1, self.btnAmbColor1,
            self.edtAmbTimeRange12, self.edtAmbOffice12, self.edtAmbPlan12, self.edtAmbInterval12, self.btnAmbColor12,
            self.edtHomeTimeRange1, self.edtHomePlan1, self.edtHomeInterval1, self.cmbReasonOfAbsence1,
            self.edtHomeTimeRange12, self.edtHomePlan12, self.edtHomeInterval12,
            self.edtAmbOfficeInter, self.edtAmbInterPlan1, self.edtAmbInterInterval1, self.btnAmbInterColor1,
            self.chkNotExternalSystem1, self.chkNotExternalSystem12, self.chkInterNotExternalSystem1)
        return ([dayPlan1], self.chkFillRedDays.isChecked())

    def getSelectedDays(self):
        self.selectedDaysList.sort()
        return self.selectedDaysList

    def getDayPlan(self, edtAmbTimeRange, edtAmbOffice, edtAmbPlan, edtAmbInterval, btnAmbColor, edtAmbTimeRange2,
                   edtAmbOffice2, edtAmbPlan2, edtAmbInterval2, btnAmbColor2, edtHomeTimeRange, edtHomePlan,
                   edtHomeInterval, cmbReasonOfAbsence, edtHomeTimeRange2, edtHomePlan2, edtHomeInterval2,
                   edtAmbInterOffice, edtAmbInterPlan, edtAmbInterInterval, btnAmbInterColor, chkNotExternalSystem1,
                   chkNotExternalSystem12, chkInterNotExternalSystem):
        return (
        self.getTaskPlan(
            edtAmbTimeRange,
            edtAmbOffice,
            edtAmbPlan,
            edtAmbInterval,
            btnAmbColor,
            edtAmbTimeRange2,
            edtAmbOffice2,
            edtAmbPlan2,
            edtAmbInterval2,
            btnAmbColor2,
            edtAmbInterOffice,
            edtAmbInterPlan,
            edtAmbInterInterval,
            btnAmbInterColor
        ),
        self.getTaskPlan(
            edtHomeTimeRange,
            None,
            edtHomePlan,
            edtHomeInterval,
            None,
            edtHomeTimeRange2,
            None,
            edtHomePlan2,
            edtHomeInterval2,
            None,
            None,
            None,
            None,
            None
        ),
        self.getTaskPlan(None, None, None, None, None, None, None, None, None, None, None, None, None, None),
        cmbReasonOfAbsence.value(),
        chkNotExternalSystem1.isChecked(),
        chkNotExternalSystem12.isChecked(),
        chkInterNotExternalSystem.isChecked()
        )

    def getTaskPlan(self, edtTimeRange, edtOffice, edtPlan, edtInterval, btnColor, edtTimeRange2, edtOffice2, edtPlan2,
                    edtInterval2, btnColor2, edtInterOffice, edtInterPlan, edtInterInterval, btnInterColor):
        if edtTimeRange2 and edtTimeRange2.isEnabled():
            timeRange2 = edtTimeRange2.timeRange() if edtTimeRange2 else None
            if timeRange2:
                timeStart2, timeFinish2 = timeRange2
            else:
                timeStart2 = None
                timeFinish2 = None
            timeRange1 = edtTimeRange.timeRange() if edtTimeRange else None
            if timeRange1:
                timeStart, timeFinish = timeRange1
            else:
                timeStart = None
                timeFinish = None

            timeRangeStart = min(timeStart, timeStart2) if (timeStart and timeStart2) else (timeStart if timeStart else (timeStart2 if timeStart2 else None))
            timeRangeFinish = max(timeFinish, timeFinish2) if (timeFinish and timeFinish2) else (timeFinish if timeFinish else (timeFinish2 if timeFinish2 else None))
            if timeRangeStart and timeRangeFinish:
                timeRange = timeRangeStart, timeRangeFinish
            else:
                timeRange = None
        else:
            timeRange2 = None
            timeRange1 = None
            timeRange = edtTimeRange.timeRange() if edtTimeRange else None

        if edtOffice2 and edtOffice2.isEnabled():
            office2 = forceStringEx(edtOffice2.text()) if edtOffice2 else None
            office1 = forceStringEx(edtOffice.text()) if edtOffice else None
            if edtInterOffice and edtInterOffice.isEnabled():
                interOffice = forceStringEx(edtInterOffice.text()) if edtInterOffice else None
                office = office1 + u', ' + interOffice + u', ' + office2
            else:
                interOffice = None
                office = office1 + u', ' + office2
        else:
            interOffice = None
            office2 = None
            office1 = None
            office = forceStringEx(edtOffice.text()) if edtOffice else None

        if edtPlan2 and edtPlan2.isEnabled():
            plan2 = edtPlan2.value() if edtPlan2 else 0
            interval2 = edtInterval2.value() if edtInterval2 else 0
            plan1 = edtPlan.value() if edtPlan else 0
            interval1 = edtInterval.value() if edtInterval else 0
            if edtInterPlan and edtInterPlan.isEnabled():
                interPlan = edtInterPlan.value() if edtInterPlan else 0
                interInterval = edtInterInterval.value() if edtInterInterval else 0
                plan = plan1 + plan2 + interPlan
                interval = setInterval(interval1, interval2, interInterval)
            else:
                interPlan = 0
                interInterval = 0
                plan = plan1 + plan2
                interval = setInterval(interval1, interval2)
        else:
            plan2 = None
            interval2 = None
            plan1 = None
            interval1 = None
            interPlan = None
            interInterval = None
            plan = edtPlan.value() if edtPlan else None
            interval = edtInterval.value() if edtInterval else 0

        # Проверяем наличие двух цветов:
        if btnColor2 and btnColor2.isEnabled():
            color2 = btnColor2.currentColorName()
            if color2 == u'#ffffff':
                color2 = None
            if btnInterColor and btnInterColor.isEnabled():
                interColor = btnInterColor.currentColorName()
                if interColor == u'######':
                    interColor = None
            else:
                interColor = None
        else:
            color2 = None
            interColor = None
        color = color1 = btnColor.currentColorName() if btnColor else None
        if color == u'#ffffff':
            color = color1 = None

        return timeRange, office, plan, interval, color, timeRange1, office1, plan1, interval1, color1, timeRange2, office2, plan2, interval2, color2, interOffice, interPlan, interInterval, interColor

    def setEnabledAmbSecondPeriod(self, checked):
        self.edtAmbTimeRange12.setEnabled(checked)
        self.edtAmbOffice12.setEnabled(checked)
        self.edtAmbPlan12.setEnabled(checked)
        self.edtAmbInterval12.setEnabled(checked)
        self.btnAmbColor12.setEnabled(checked)
        self.chkNotExternalSystem12.setEnabled(checked)

    def setEnabledHomeSecondPeriod(self, checked):
        self.edtHomeTimeRange12.setEnabled(checked)
        self.edtHomePlan12.setEnabled(checked)
        self.edtHomeInterval12.setEnabled(checked)

    def getCurrentObject(self, index, objects):
        ind = 1
        edit = objects[index] % (ind)
        indexTimeRange = None if index == 2 else index
        return ind, edit, indexTimeRange

    def edtAmbTimeRange_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['ambInterval'])
        editPlan = listEdit['ambPlan'][indexTimeRange] % (ind)
        onlyOutPeriod = False
        if forceInt(getObjectAttribute(self, editPlan).value()):
            onlyOutPeriod = True
        setSpinBoxInterval(self, ind, edit, indexTimeRange, listEdit['ambTimeRange'], self.chkAmbSecondPeriod, onlyOutPeriod)
        setSpinBoxInterval(self, ind, editPlan, indexTimeRange, listEdit['ambTimeRange'], self.chkAmbSecondPeriod, onlyOutPeriod)
        if onlyOutPeriod:
            conversion(self, ind, editPlan, indexTimeRange, listEdit['ambInterval'], listEdit['ambTimeRange'], self.chkAmbSecondPeriod)
        else:
            conversion(self, ind, edit, indexTimeRange, listEdit['ambPlan'], listEdit['ambTimeRange'], self.chkAmbSecondPeriod)
        conversion(self, ind, 'edtAmbInterInterval%d' % (ind), None, listEdit['ambPlan'], None, self.chkAmbInterPeriod.isChecked())

    def edtHomeTimeRange_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['homeInterval'])
        editPlan = listEdit['homePlan'][indexTimeRange] % (ind)
        onlyOutPeriod = False
        if forceInt(getObjectAttribute(self, editPlan).value()):
            onlyOutPeriod = True
        setSpinBoxInterval(self, ind, edit, indexTimeRange, listEdit['homeTimeRange'], self.chkAmbSecondPeriod, onlyOutPeriod)
        setSpinBoxInterval(self, ind, editPlan, indexTimeRange, listEdit['homeTimeRange'], self.chkAmbSecondPeriod, onlyOutPeriod)
        if onlyOutPeriod:
            conversion(self, ind, editPlan, indexTimeRange, listEdit['homeInterval'], listEdit['homeTimeRange'], self.chkAmbSecondPeriod)
        else:
            conversion(self, ind, edit, indexTimeRange, listEdit['homePlan'], listEdit['homeTimeRange'], self.chkAmbSecondPeriod)
        conversion(self, ind, 'edtAmbInterInterval%d' % (ind), None, listEdit['ambPlan'], None, self.chkAmbInterPeriod.isChecked())

    def edtAmbPlan_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['ambPlan'])
        if getObjectAttribute(self, listEdit['ambTimeRange'][indexTimeRange] % (ind)).timeRange():
            conversion(self, ind, edit, indexTimeRange, listEdit['ambInterval'], listEdit['ambTimeRange'], self.chkAmbSecondPeriod)
        else:
            callObjectAttributeMethod(self, edit, 'setValue', 0)

    def edtAmbInterval_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['ambInterval'])
        if getObjectAttribute(self, listEdit['ambTimeRange'][indexTimeRange] % (ind)).timeRange():
            conversion(self, ind, edit, indexTimeRange, listEdit['ambPlan'], listEdit['ambTimeRange'], self.chkAmbSecondPeriod)
        else:
            callObjectAttributeMethod(self, edit, 'setValue', 0)

    def edtHomePlan_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['homePlan'])
        if getObjectAttribute(self, listEdit['homeTimeRange'][indexTimeRange] % (ind)).timeRange():
            conversion(self, ind, edit, indexTimeRange, listEdit['homeInterval'], listEdit['homeTimeRange'], self.chkAmbSecondPeriod)
        else:
            callObjectAttributeMethod(self, edit, 'setValue', 0)

    def edtHomeInterval_editingFinished(self, index):
        ind, edit, indexTimeRange = self.getCurrentObject(index, listEdit['homeInterval'])
        if getObjectAttribute(self, listEdit['homeTimeRange'][indexTimeRange] % (ind)).timeRange():
            conversion(self, ind, edit, indexTimeRange, listEdit['homePlan'], listEdit['homeTimeRange'], self.chkAmbSecondPeriod)
        else:
            callObjectAttributeMethod(self, edit, 'setValue', 0)

    @QtCore.pyqtSlot(QtCore.QDate)
    def on_calendarTemplateOnRotation_clicked(self, date):
        selectedDate = self.calendarTemplateOnRotation.selectedDate()
        day = selectedDate.day()
        if day not in self.selectedDaysList:
            self.selectedDaysList.append(day)
        else:
            i = self.selectedDaysList.index(day)
            self.selectedDaysList.pop(i)
        self.selectedDaysList.sort()
        self.lblSelectedDays.setText(u', '.join([str(day) for day in self.selectedDaysList]))
        self.lblCountSelectedDays.setText(u'Всего выбрано дней: %d' % (len(self.selectedDaysList)))

    @QtCore.pyqtSlot(bool)
    def on_chkAmbSecondPeriod_clicked(self, checked):
        self.setEnabledAmbSecondPeriod(checked)
        if not checked and self.chkAmbInterPeriod.isChecked():
            self.chkAmbInterPeriod.setChecked(checked)
            self.edtAmbOfficeInter.setEnabled(checked)
            self.edtAmbInterInterval1.setEnabled(checked)
            self.edtAmbInterPlan1.setEnabled(checked)
            self.btnAmbInterColor1.setEnabled(checked)
            # self.setEnabledAmbInterPeriod(checked)

    @QtCore.pyqtSlot(bool)
    def on_chkAmbInterPeriod_clicked(self, checked):
        # self.setEnabledAmbInterPeriod(checked)
        self.edtAmbOfficeInter.setEnabled(checked)
        self.edtAmbInterInterval1.setEnabled(checked)
        self.edtAmbInterPlan1.setEnabled(checked)
        self.btnAmbInterColor1.setEnabled(checked)
        conversion(self, 1, 'edtAmbInterInterval1', None, listEdit['ambPlan'], None, self.chkAmbInterPeriod.isChecked())

    @QtCore.pyqtSlot(bool)
    def on_chkHomeSecondPeriod_clicked(self, checked):
        self.setEnabledHomeSecondPeriod(checked)

    @QtCore.pyqtSlot()
    def on_btnClear_clicked(self):
        self.selectedDaysList = []
        self.lblSelectedDays.setText(u'')
        self.lblCountSelectedDays.setText(u'Всего выбрано дней: %d' % (len(self.selectedDaysList)))


class CParamsForExternalDialog(CDialogBase, Ui_ParamsForExternalDialog):
    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.edtLastAccessibleTimelineDate.setDate(QtCore.QDate())

    @QtCore.pyqtSlot(int)
    def on_edtTimelineAccessibilityDays_valueChanged(self, value):
        self.lblTimelineAccessibilityDaysSuffix.setText(agreeNumberAndWord(value, (u'день', u'дня', u'дней')))
