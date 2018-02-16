# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

import PyQt4.Qwt5 as Qwt
from PyQt4 import QtCore, QtGui

from Registry.Utils import getClientString
from Reports.ReportBase import CReportBase, createTable
from Reports.ReportView import CReportViewDialog
from ThermalSheet.PropertyOtherModel import CPropertyOtherModel
from Ui_TemperatureListDialog import Ui_TemperatureListDialog
from Ui_TemperatureListParameters import Ui_TemperatureListParameters
from library.DialogBase import CDialogBase
from library.Utils import forceBool, forceDate, forceDouble, forceInt, forceRef, forceString, forceTime, getVal, pyDate, toVariant


class CTemperatureList(CDialogBase, Ui_TemperatureListDialog):
    def __init__(self, parent, params, clientId, eventId):
        CDialogBase.__init__(self, parent)
        self.addModels('TemperatureSheet', CPropertyOtherModel(self))
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.setModels(self.tblTemperatureSheet, self.modelTemperatureSheet, self.selectionModelTemperatureSheet)
        self.parent = parent
        self.params = params
        self.eventId = eventId
        self.clientId = clientId
        self.minValue = 0.0
        self.maxValue = 0.0
        self.dimension = 0
        self.multipleDimension = 0
        self.countGraphic = 0
        self.qwtPlotList = []
        self.y = 0
        self.x = 0

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        self.close()

    @QtCore.pyqtSlot()
    def on_btnRetry_clicked(self):
        self.close()
        dialog = CTemperatureListParameters(self.parent, self.eventId)
        dialog.setParams()
        if dialog.exec_():
            demo = CTemperatureList(self.parent, dialog.params(), self.clientId, self.eventId)
            demo.getInfo()
            demo.exec_()

    @QtCore.pyqtSlot()
    def on_btnPrint_clicked(self):
        widgetIndex = self.tabWidget.currentIndex()
        if widgetIndex == 1:
            model = self.modelTemperatureSheet
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'Таблица температурного листа\n')
            cursor.insertBlock()
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertText(u'Пациент: %s' % (getClientString(self.clientId)))
            cursor.insertText(u'\nОтчёт составлен: ' + forceString(QtCore.QDateTime.currentDateTime()))
            cursor.insertBlock()
            colWidths = [self.tblTemperatureSheet.columnWidth(i) for i in xrange(model.columnCount() - 1)]
            colWidths.insert(0, 10)
            totalWidth = sum(colWidths)
            tableColumns = []
            iColNumber = False
            for iCol, colWidth in enumerate(colWidths):
                widthInPercents = str(max(1, colWidth * 90 / totalWidth)) + '%'
                if iColNumber == False:
                    tableColumns.append((widthInPercents, [u'№'], CReportBase.AlignRight))
                    iColNumber = True
                headers = model.headers
                tableColumns.append((widthInPercents, [forceString(headers[iCol][1])], CReportBase.AlignLeft))
            table = createTable(cursor, tableColumns)
            for iModelRow in xrange(model.rowCount()):
                iTableRow = table.addRow()
                table.setText(iTableRow, 0, iModelRow + 1)
                for iModelCol in xrange(model.columnCount()):
                    index = model.createIndex(iModelRow, iModelCol)
                    text = forceString(model.data(index))
                    table.setText(iTableRow, iModelCol + 1, text)
            html = doc.toHtml(QtCore.QByteArray('utf-8'))
            view = CReportViewDialog(self)
            view.setText(html)
            view.exec_()
        else:
            printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
            printer.setOrientation(QtGui.QPrinter.Landscape)
            dialog = QtGui.QPrintDialog(printer, self)
            if dialog.exec_():
                painter = QtGui.QPainter(printer)
                scale = min(printer.pageRect().width() / self.scrollArea.widget().width(),
                            printer.pageRect().height() / self.scrollArea.widget().height())
                painter.scale(scale, scale)
                self.scrollArea.widget().render(painter)
                painter.end()

    def getDeseaseDayRecords(self, begDate, endDate, actionTypeIdList):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableAPInteger = db.table('ActionProperty_Integer')
        cond = [
            tableAPT['deleted'].eq(0),
            tableAPT['actionType_id'].inlist(actionTypeIdList),
            tableAPT['name'].like(u'День болезни'),
            tableAP['deleted'].eq(0),
            tableAction['deleted'].eq(0),
            tableAction['event_id'].eq(self.eventId),
            db.joinAnd([tableAction['endDate'].dateGe(begDate),
                        tableAction['endDate'].dateLe(endDate)])
        ]
        table = tableAction.innerJoin(tableAP, tableAP['action_id'].eq(tableAction['id']))
        table = table.innerJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
        table = table.innerJoin(tableAPInteger, tableAPInteger['id'].eq(tableAP['id']))
        return db.iterRecordList(table, [tableAPInteger['value'], tableAP['action_id'], tableAction['endDate']], cond, tableAction['endDate'])

    def getTemperatureRecords(self, begDate, endDate, actionIdList, actionTypeIdList):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableAPTemperature = db.table('ActionProperty_Temperature')
        cond = [
            tableAPT['deleted'].eq(0),
            tableAction['id'].inlist(actionIdList),
            tableAPT['actionType_id'].inlist(actionTypeIdList),
            tableAPT['typeName'].like(u'Temperature'),
            tableAP['deleted'].eq(0),
            tableAction['deleted'].eq(0),
            tableAction['event_id'].eq(self.eventId),
            db.joinAnd([tableAction['endDate'].dateGe(begDate),
                        tableAction['endDate'].dateLe(endDate)])
        ]
        table = tableAction.innerJoin(tableAP, tableAP['action_id'].eq(tableAction['id']))
        table = table.innerJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
        table = table.innerJoin(tableAPTemperature, tableAPTemperature['id'].eq(tableAP['id']))
        return db.iterRecordList(table, [tableAPTemperature['value'], tableAP['action_id']], cond, tableAction['endDate'])

    def getArterialPressureMaxRecords(self, begDate, endDate, actionIdList, actionTypeIdList):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableAPAP = db.table('ActionProperty_ArterialPressure')
        cond = [
            tableAPT['deleted'].eq(0),
            tableAction['id'].inlist(actionIdList),
            tableAPT['actionType_id'].inlist(actionTypeIdList),
            tableAPT['typeName'].like(u'ArterialPressure'),
            tableAPT['name'].like(u'АД-макс'),
            tableAP['deleted'].eq(0),
            tableAction['deleted'].eq(0),
            tableAction['event_id'].eq(self.eventId),
            db.joinAnd([tableAction['endDate'].dateGe(begDate),
                        tableAction['endDate'].dateLe(endDate)])
        ]
        table = tableAction.innerJoin(tableAP, tableAP['action_id'].eq(tableAction['id']))
        table = table.innerJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
        table = table.innerJoin(tableAPAP, tableAPAP['id'].eq(tableAP['id']))
        return db.iterRecordList(table, [tableAPAP['value'], tableAP['action_id']], cond, tableAction['endDate'])

    def getArterialPressureMinRecords(self, begDate, endDate, actionIdList, actionTypeIdList):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableAP = db.table('ActionProperty')
        tableAPAP = db.table('ActionProperty_ArterialPressure')
        tableAPT = db.table('ActionPropertyType')
        cond = [
            tableAPT['deleted'].eq(0),
            tableAction['id'].inlist(actionIdList),
            tableAPT['actionType_id'].inlist(actionTypeIdList),
            tableAPT['typeName'].like(u'ArterialPressure'),
            tableAPT['name'].like(u'АД-мин'),
            tableAP['deleted'].eq(0),
            tableAction['deleted'].eq(0),
            tableAction['event_id'].eq(self.eventId),
            db.joinAnd([tableAction['endDate'].dateGe(begDate),
                        tableAction['endDate'].dateLe(endDate)])
        ]
        table = tableAction.innerJoin(tableAP, tableAP['action_id'].eq(tableAction['id']))
        table = table.innerJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
        table = table.innerJoin(tableAPAP, tableAPAP['id'].eq(tableAP['id']))
        return db.iterRecordList(table, [tableAPAP['value'], tableAP['action_id']], cond, tableAction['endDate'])

    def getPulseRecords(self, begDate, endDate, actionIdList, actionTypeIdList):
        db = QtGui.qApp.db
        tableAction = db.table('Action')
        tableAP = db.table('ActionProperty')
        tableAPPulse = db.table('ActionProperty_Pulse')
        tableAPT = db.table('ActionPropertyType')
        cond = [
            tableAPT['deleted'].eq(0),
            tableAction['id'].inlist(actionIdList),
            tableAPT['actionType_id'].inlist(actionTypeIdList),
            tableAPT['typeName'].like(u'Pulse'),
            tableAP['deleted'].eq(0),
            tableAction['deleted'].eq(0),
            tableAction['event_id'].eq(self.eventId),
            db.joinAnd([tableAction['endDate'].dateGe(begDate),
                        tableAction['endDate'].dateLe(endDate)])
        ]
        table = tableAction.innerJoin(tableAP, tableAP['action_id'].eq(tableAction['id']))
        table = table.innerJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
        table = table.innerJoin(tableAPPulse, tableAPPulse['id'].eq(tableAP['id']))
        return db.iterRecordList(table, [tableAPPulse['value'], tableAP['action_id']], cond, tableAction['endDate'])

    def getTemperatureSheetActionTypes(self):
        db = QtGui.qApp.db
        tableAT = db.table('ActionType')
        return db.getDistinctIdList(tableAT, [tableAT['id']], [tableAT['deleted'].eq(0),
                                                               tableAT['flatCode'].like(u'temperatureSheet%')])

    def getInfo(self):
        if self.eventId and self.params:
            APMaxList = {}
            APMinList = {}
            temperatureList = {}
            pulseList = {}
            chkTemperature = self.params.get('chkTemperature', 0)
            chkPulse = self.params.get('chkPulse', 0)
            chkAPMax = self.params.get('chkAPMax', 0)
            chkAPMin = self.params.get('chkAPMin', 0)
            self.multipleDimension = self.params.get('multipleDimension', 0)
            begDate = self.params.get('begDate', None)
            endDate = self.params.get('endDate', None)
            if begDate and endDate and (begDate <= endDate):
                self.multipleDays = 2 if begDate == endDate else (begDate.daysTo(endDate) + 2)
                if (begDate and endDate and chkTemperature or chkPulse or chkAPMax or chkAPMin) and self.multipleDimension and self.multipleDays:
                    actionTypeIdList = self.getTemperatureSheetActionTypes()
                    diseaseDayList = {}
                    actionIdList = []

                    for recordDiseaseDay in self.getDeseaseDayRecords(begDate, endDate, actionTypeIdList):
                        actionId = forceRef(recordDiseaseDay.value('action_id'))
                        actionIdList.append(actionId)
                        diseaseDay = forceInt(recordDiseaseDay.value('value')) - 1
                        endDate = forceDate(recordDiseaseDay.value('endDate'))
                        endDateStr = pyDate(endDate)
                        endTime = forceTime(recordDiseaseDay.value('endDate'))
                        endTimeStr = pyTime(endTime)
                        if (diseaseDay, endTimeStr, endDateStr) not in diseaseDayList.keys():
                            diseaseDayList[(diseaseDay, endTimeStr, endDateStr)] = actionId

                    self.modelTemperatureSheet.loadHeader(diseaseDayList, self.multipleDimension)
                    self.modelTemperatureSheet.loadData(self.eventId, diseaseDayList, actionIdList, begDate, endDate, actionTypeIdList)

                    if chkTemperature:
                        for recordTemperature in self.getTemperatureRecords(begDate, endDate, actionIdList, actionTypeIdList):
                            actionId = forceRef(recordTemperature.value('action_id'))
                            temperature = forceDouble(recordTemperature.value('value'))
                            for key, value in diseaseDayList.items():
                                if actionId == value:
                                    temperatureList[key] = temperature
                                    break
                    if chkAPMax:
                        for recordAPMax in self.getArterialPressureMaxRecords(begDate, endDate, actionIdList, actionTypeIdList):
                            actionId = forceRef(recordAPMax.value('action_id'))
                            APMax = forceInt(recordAPMax.value('value'))
                            for key, value in diseaseDayList.items():
                                if actionId == value:
                                    APMaxList[key] = APMax
                                    break
                    if chkAPMin:
                        for recordAPMin in self.getArterialPressureMinRecords(begDate, endDate, actionIdList, actionTypeIdList):
                            actionId = forceRef(recordAPMin.value('action_id'))
                            APMin = forceInt(recordAPMin.value('value'))
                            for key, value in diseaseDayList.items():
                                if actionId == value:
                                    APMinList[key] = APMin
                                    break
                    if chkPulse:
                        for recordPulse in self.getPulseRecords(begDate, endDate, actionIdList, actionTypeIdList):
                            actionId = forceRef(recordPulse.value('action_id'))
                            pulse = forceInt(recordPulse.value('value'))
                            for key, value in diseaseDayList.items():
                                if actionId == value:
                                    pulseList[key] = pulse
                                    break
                cnt = 0
                self.dimension = round(1 / float(self.multipleDimension), 2)
                self.countGraphic = 0
                if chkTemperature:
                    self.countGraphic += 1
                if chkAPMax:
                    self.countGraphic += 1
                if chkAPMin:
                    self.countGraphic += 1
                if chkPulse:
                    self.countGraphic += 1

                self.qwtPlotList = []
                self.scrollArea.viewport().setAutoFillBackground(True)
                plotLayout = QtGui.QVBoxLayout(QtGui.QFrame(self.scrollArea.widget()))
                if chkTemperature:
                    xa, ya, minValue1, maxValue1, titleList = self.getXY(temperatureList)
                    obj = CCreateGraph(self, xa, ya, minValue1 if minValue1 < 35 else 35, maxValue1 if maxValue1 > 40 else 40, 1, cnt, QtCore.Qt.red, u'Температура', titleList)
                    plotLayout.addWidget(obj.qwtPlot)
                    cnt += 1
                if chkAPMax:
                    xa2, ya2, minValue2, maxValue2, titleList = self.getXY(APMaxList)
                    obj2 = CCreateGraph(self, xa2, ya2, minValue2 if minValue2 < 50 else 50, maxValue2 if maxValue2 > 175 else 175, 25, cnt, QtCore.Qt.blue, u'Давление максимальное', titleList)
                    plotLayout.addWidget(obj2.qwtPlot)
                    cnt += 1
                if chkAPMin:
                    xa3, ya3, minValue3, maxValue3, titleList = self.getXY(APMinList)
                    obj3 = CCreateGraph(self, xa3, ya3, minValue3 if minValue3 < 50 else 50, maxValue3 if maxValue3 > 175 else 175, 25, cnt, QtCore.Qt.blue, u'Давление минимальное', titleList)
                    plotLayout.addWidget(obj3.qwtPlot)
                    cnt += 1
                if chkPulse:
                    xa4, ya4, minValue4, maxValue4, titleList = self.getXY(pulseList)
                    obj4 = CCreateGraph(self, xa4, ya4, minValue4 if minValue4 < 60 else 60, maxValue4 if maxValue4 > 120 else 120, 10, cnt, QtCore.Qt.darkGreen, u'Пульс', titleList)
                    plotLayout.addWidget(obj4.qwtPlot)
                    cnt += 1
                widgetLayout = QtGui.QWidget()
                widgetLayout.setLayout(plotLayout)
                self.scrollArea.setWidget(widgetLayout)

    def getXY(self, infoList):
        periodDayTwoList = {1: u'у', 2: u'в'}
        periodDayThreeList = {1: u'у', 2: u'д', 3: u'в'}
        periodDayFourList = {1: u'у', 2: u'д', 3: u'в', 4: u'н'}
        periodDayAllList = {1: {1: u'д'}, 2: periodDayTwoList, 3: periodDayThreeList, 4: periodDayFourList}
        tempSort = infoList.keys()
        tempSort.sort()
        xList = []
        yList = []
        titleList = {}
        minValue = 0.0
        maxValue = 0.0
        firstIn = True
        dayMinutes = 24 * 60
        multipleDimensionMinutes = dayMinutes / self.multipleDimension
        periodHours = {}
        begHour = 0
        for i in range(1, self.multipleDimension + 1):
            if begHour >= dayMinutes:
                break
            dimensionMinutes = begHour + multipleDimensionMinutes
            if dimensionMinutes >= dayMinutes:
                endHours = dayMinutes - 1
            else:
                endHours = dimensionMinutes
            periodHours[i] = (begHour, endHours)
            begHour += multipleDimensionMinutes
        periodDayList = periodDayAllList.get(self.multipleDimension, {})
        for key in tempSort:
            value = infoList.get(key, 0)
            diseaseDay, endTimeStr, endDateStr = key
            endTime = QtCore.QTime(endTimeStr)
            hours = endTime.hour()
            minutes = endTime.minute()
            endHourMinutes = hours * 60 + minutes
            keyHours = periodHours.keys()
            keyHours.sort()
            for keyHour in keyHours:
                periodHour = periodHours.get(keyHour, None)
                if periodHour and endHourMinutes > periodHour[0] and endHourMinutes <= periodHour[1]:
                    if firstIn:
                        minValue = value
                        maxValue = value
                        firstIn = False
                    if minValue > value:
                        minValue = value
                    if maxValue < value:
                        maxValue = value
                    yList.append(round(value, 2))
                    x = round(len(yList), 2)
                    xList.append(x)
                    periodDay = periodDayList.get(keyHour, u'')
                    titleList[x] = (diseaseDay + 1, endTime, QtCore.QDate(endDateStr), periodDay)
                    break
        return xList, yList, minValue, maxValue, titleList


class CCreateGraph(object):
    def __init__(self, parent, xa, ya, minValue, maxValue, step, qwtPlot, colorCanvas, namePlot=u'', titleList=None):
        if not titleList:
            titleList = {}
        self.parent = parent
        self.qwtPlot = Qwt.QwtPlot(Qwt.QwtText('self.parent.scrollArea.viewport()'))
        if self.parent.countGraphic == 0:
            countGraphic = 1
        else:
            countGraphic = self.parent.countGraphic
        namePlotQwtText = Qwt.QwtText(namePlot)
        font = QtGui.QFont()
        font.setWeight(8)
        font.setBold(False)
        namePlotQwtText.setFont(font)
        self.qwtPlot.setAutoReplot(True)
        self.qwtPlot.setTitle(namePlotQwtText)
        self.qwtPlot.setCanvasBackground(QtCore.Qt.white)

        megaGrid = Qwt.QwtPlotGrid()
        megaGrid.enableXMin(False)
        megaGrid.enableYMin(True)
        megaGrid.attach(self.qwtPlot)

        ca = Qwt.QwtPlotCurve()
        ca.setPen(QtGui.QPen(colorCanvas))
        ca.setData(xa, ya)
        ca.attach(self.qwtPlot)

        self.qwtPlot.enableAxis(Qwt.QwtPlot.xTop, True)
        self.qwtPlot.setAxisScale(Qwt.QwtPlot.yLeft, minValue, maxValue, step)
        axisLen = len(xa) + 1
        self.qwtPlot.setAxisScale(Qwt.QwtPlot.xBottom, 0, axisLen, 1.0)
        self.qwtPlot.setAxisScale(Qwt.QwtPlot.xTop, 0, axisLen, 1.0)
        axisScaleDraw = self.qwtPlot.axisScaleDraw(Qwt.QwtPlot.xBottom)
        self.qwtPlot.setAxisScaleDraw(Qwt.QwtPlot.xBottom, CMyQwtScaleDrawXBottom(axisScaleDraw, titleList))
        axisScaleDraw = self.qwtPlot.axisScaleDraw(Qwt.QwtPlot.xTop)
        self.qwtPlot.setAxisScaleDraw(Qwt.QwtPlot.xTop, CMyQwtScaleDrawXTop(axisScaleDraw, titleList))


class CMyQwtScaleDraw(Qwt.QwtScaleDraw):
    def __init__(self, parent):
        Qwt.QwtScaleDraw.__init__(self, parent)

    def drawLabel(self, painter, value):
        lbl = self.tickLabel(painter.font(), value)
        if lbl.isEmpty():
            return
        pos = self.labelPosition(value)
        labelSize = lbl.textSize(painter.font())
        if (labelSize.height() % 2):
            labelSize.setHeight(labelSize.height() + 1)
        metricsMap = Qwt.QwtPainter.metricsMap()
        Qwt.QwtPainter.resetMetricsMap()
        labelSize = metricsMap.layoutToDevice(labelSize)
        pos = metricsMap.layoutToDevice(pos)
        m = self.labelMatrix(pos, labelSize)
        painter.save()
        painter.setMatrix(m, True)
        lbl.draw(painter, QtCore.QRect(QtCore.QPoint(0, 0), labelSize))
        Qwt.QwtPainter.setMetricsMap(metricsMap)
        painter.restore()

    def extent(self, pen, font):
        d = 0
        if self.hasComponent(Qwt.QwtAbstractScaleDraw.Labels):
            if (self.orientation() == QtCore.Qt.Vertical):
                d = self.maxLabelWidth(font)
            else:
                d = self.maxLabelHeight(font)
            if (d > 0):
                d += self.spacing()
                d = d * 4
        if self.hasComponent(Qwt.QwtAbstractScaleDraw.Ticks):
            d += self.majTickLength()
        if self.hasComponent(Qwt.QwtAbstractScaleDraw.Backbone):
            penWidth = pen.width()
            pw = 1
            if pw < penWidth:
                pw = penWidth
            d += pw
        minimumExtent = self.minimumExtent()
        if d < minimumExtent:
            d = minimumExtent
        return d


class CMyQwtScaleDrawXBottom(CMyQwtScaleDraw):
    def __init__(self, parent, titleList=None):
        if not titleList:
            titleList = {}
        CMyQwtScaleDraw.__init__(self, parent)
        self.titleList = titleList

    def tickLabel(self, font, value):
        titleList = self.titleList.get(value, None)
        if titleList:
            diseaseDay, endTime, endDate, periodDay = titleList
            value = u'' + periodDay + u'' + '\n' + u'' + str(diseaseDay) + u''
        else:
            value = u''
        res = Qwt.QwtText()
        res.setText(QtCore.QString(value), Qwt.QwtText.PlainText)
        res.setFont(font)
        textSize = res.textSize(font)
        res.setLayoutAttribute(1, False)
        return res


class CMyQwtScaleDrawXTop(CMyQwtScaleDraw):
    def __init__(self, parent, titleList=None):
        if not titleList:
            titleList = {}
        CMyQwtScaleDraw.__init__(self, parent)
        self.titleList = titleList

    def tickLabel(self, font, value):
        titleList = self.titleList.get(value, None)
        if titleList:
            diseaseDay, endTime, endDate, periodDay = titleList
            value = str(endDate.day()) + u'.' + str(endDate.month()) + u'.' + '\n' + str(endDate.year()) + '\n' + endTime.toString('hh:mm')
        else:
            value = u''
        res = Qwt.QwtText()
        res.setText(QtCore.QString(value), Qwt.QwtText.PlainText)
        res.setFont(font)
        textSize = res.textSize(font)
        res.setLayoutAttribute(1, False)
        return res


class CTemperatureListParameters(CDialogBase, Ui_TemperatureListParameters):
    def __init__(self, parent, eventId):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        currentDate = QtCore.QDate().currentDate()
        month = currentDate.month()
        year = currentDate.year()
        self.eventId = eventId
        self.parent = parent
        self.edtMultipleDimension.setValue(2)
        self.getPeriodDate()

    def getPeriodDate(self):
        if self.eventId:
            db = QtGui.qApp.db
            tableAction = db.table('Action')
            tableAPT = db.table('ActionPropertyType')
            tableAP = db.table('ActionProperty')
            tableAT = db.table('ActionType')
            actionTypeIdList = db.getDistinctIdList(tableAT, [tableAT['id']], [tableAT['deleted'].eq(0), tableAT['flatCode'].like(u'temperatureSheet%')])
            cond = [tableAPT['deleted'].eq(0),
                    tableAPT['actionType_id'].inlist(actionTypeIdList),
                    tableAction['deleted'].eq(0),
                    tableAction['event_id'].eq(self.eventId)
                    ]
            tableQuery = tableAction.innerJoin(tableAP, tableAP['action_id'].eq(tableAction['id']))
            tableQuery = tableQuery.innerJoin(tableAPT, tableAPT['id'].eq(tableAP['type_id']))
            recordMIN = db.getRecordEx(tableQuery, 'MIN(Action.begDate) AS begDate', cond)
            recordMAX = db.getRecordEx(tableQuery, 'MAX(Action.begDate) AS begDate', cond)
            begDateMIN = None
            begDateMAX = None
            if recordMIN:
                begDateMIN = forceDate(recordMIN.value('begDate'))
            if recordMAX:
                begDateMAX = forceDate(recordMAX.value('begDate'))
            if not begDateMIN:
                begDateMIN = QtCore.QDate(QtCore.QDate().currentDate().year(),
                                          QtCore.QDate().currentDate().month(), 1)
            if not begDateMAX:
                begDateMAX = QtCore.QDate(QtCore.QDate().currentDate().year(),
                                          QtCore.QDate().currentDate().month(), 15)
            self.edtBegDate.setDate(begDateMIN)
            self.edtEndDate.setDate(begDateMAX)
        else:
            currentDate = QtCore.QDate().currentDate()
            month = currentDate.month()
            year = currentDate.year()
            begDate = QtCore.QDate(year, month, 1)
            endDate = QtCore.QDate(year, month, 15)
            self.edtBegDate.setDate(begDate)
            self.edtEndDate.setDate(endDate)

    def setParams(self):
        currentDate = QtCore.QDate().currentDate()
        month = currentDate.month()
        year = currentDate.year()
        begDate = forceDate(getVal(QtGui.qApp.preferences.appPrefs, 'begDate', None))
        if not begDate:
            begDate = QtCore.QDate(year, month, 1)
        self.edtBegDate.setDate(begDate)
        endDate = forceDate(getVal(QtGui.qApp.preferences.appPrefs, 'endDate', None))
        if not endDate:
            endDate = QtCore.QDate(year, month, 15)
        self.edtEndDate.setDate(endDate)
        self.chkTemperature.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'chkTemperature', False)))
        self.chkPulse.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'chkPulse', False)))
        self.chkAPMax.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'chkAPMax', False)))
        self.chkAPMin.setChecked(forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'chkAPMin', False)))
        multipleDimension = forceInt(getVal(QtGui.qApp.preferences.appPrefs, 'multipleDimension', 0))
        if not multipleDimension:
            multipleDimension = 2
        self.edtMultipleDimension.setValue(multipleDimension)

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['chkTemperature'] = self.chkTemperature.isChecked()
        result['chkPulse'] = self.chkPulse.isChecked()
        result['chkAPMax'] = self.chkAPMax.isChecked()
        result['chkAPMin'] = self.chkAPMin.isChecked()
        result['multipleDimension'] = self.edtMultipleDimension.value()
        QtGui.qApp.preferences.appPrefs['begDate'] = toVariant(self.edtBegDate.date())
        QtGui.qApp.preferences.appPrefs['endDate'] = toVariant(self.edtEndDate.date())
        QtGui.qApp.preferences.appPrefs['chkTemperature'] = toVariant(self.chkTemperature.isChecked())
        QtGui.qApp.preferences.appPrefs['chkPulse'] = toVariant(self.chkPulse.isChecked())
        QtGui.qApp.preferences.appPrefs['chkAPMax'] = toVariant(self.chkAPMax.isChecked())
        QtGui.qApp.preferences.appPrefs['chkAPMin'] = toVariant(self.chkAPMin.isChecked())
        QtGui.qApp.preferences.appPrefs['multipleDimension'] = toVariant(self.edtMultipleDimension.value())
        return result


def pyTime(time):
    if time and time.isValid():
        return time.toPyTime()
    else:
        return None
