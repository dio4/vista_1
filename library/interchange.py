# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2016 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from library.TimeEdit import CTimeEdit
from library.Utils import *
from library.crbcombobox import CRBComboBox


def setLabelImageValue(label, record, fieldName):
    ba = record.value(fieldName).toByteArray()
    image = QtGui.QImage().fromData(ba)
    pixmap = QtGui.QPixmap().fromImage(image)
    label.setGeometry(0, 0,
                      pixmap.size().width(),
                      pixmap.size().height())
    label.setPixmap(pixmap)


def setLineEditValue(lineEdit, record, fieldName):
    lineEdit.setText(record.value(fieldName).toString())
    lineEdit.setCursorPosition(0)


def setLabelText(label, record, fieldName):
    label.setTextFormat(Qt.PlainText)
    label.setText(record.value(fieldName).toString())


def setTextEditValue(textEdit, record, fieldName):
    textEdit.setPlainText(record.value(fieldName).toString())


def setTextEditHTML(textEdit, record, fieldName):
    textEdit.setHtml(record.value(fieldName).toString())


def setRBComboBoxValue(comboBox, record, fieldName):
    comboBox.setValue(forceRef(record.value(fieldName)))


def setDateEditValue(dateEdit, record, fieldName):
    dateEdit.setDate(forceDate(record.value(fieldName)))


def setDatetimeEditValue(dateEdit, timeEdit, record, fieldName):
    value = record.value(fieldName).toDateTime()
    dateEdit.setDate(value.date())
    # Стандартный QTimeEdit при установке некорректного времени оставляет предыдущее значение, а не сбрасывается в 0.
    time = value.time()
    timeEdit.setTime(time if time.isValid() or isinstance(timeEdit, CTimeEdit) else QtCore.QTime(0, 0, 0))


def setSpinBoxValue(spinBox, record, fieldName):
    spinBox.setValue(forceInt(record.value(fieldName)))


def setBigIntSpinBoxValue(spinBox, record, fieldName):
    spinBox.setValue(forceLong(record.value(fieldName)))


def setDoubleBoxValue(spinBox, record, fieldName):
    spinBox.setValue(forceDouble(record.value(fieldName)))


def setComboBoxValue(comboBox, record, fieldName):
    comboBox.setCurrentIndex(forceInt(record.value(fieldName)))


def setCheckBoxValue(checkBox, record, fieldName):
    checkBox.setChecked(forceInt(record.value(fieldName)) != 0)


def setWidgetValue(widget, record, fieldName, handler=forceRef):
    u"""
    :param widget: instance of QWidget with value() method
    :param record: QSqlRecord instance
    :param fieldName: QSqlField name
    :param handler: value formatter
    """
    widget.setValue(handler(record.value(fieldName)))


def getLineEditValue(lineEdit, record, fieldName):
    record.setValue(fieldName, QVariant(lineEdit.text().simplified()))


def getTextEditValue(textEdit, record, fieldName):
    record.setValue(fieldName, QVariant(textEdit.toPlainText()))


def getTextEditHTML(textEdit, record, fieldName):
    record.setValue(fieldName, QVariant(textEdit.toHtml()))


def getRBComboBoxValue(comboBox, record, fieldName):
    itemId = forceRef(comboBox.value())
    record.setValue(fieldName, toVariant(itemId))
    if isinstance(comboBox, CRBComboBox) and comboBox.order() and 'usedIndex' in comboBox.order():
        updateUsedIndex(comboBox.tableName(), itemId)


def updateUsedIndex(table, changedId):
    # Поддержка индекса частоты использования
    table = QtGui.qApp.db.forceTable(table)
    if table and table.hasField(u'usedIndex'):
        recordList = QtGui.qApp.db.getRecordList(table, '*')
        totalUsedIndex = sum([forceDouble(record.value('usedIndex')) for record in recordList])
        try:
            QtGui.qApp.db.transaction()
            for record in recordList:
                currentUsedIndex = forceDouble(record.value('usedIndex'))
                currentId = forceRef(record.value('id'))
                newIndex = (totalUsedIndex * currentUsedIndex + (0.01 if currentId == changedId else 0.00)) / (totalUsedIndex + 0.01)
                record.setValue('usedIndex', toVariant(newIndex))
                QtGui.qApp.db.updateRecord(table, record)
            QtGui.qApp.db.commit()
        except:
            QtGui.qApp.db.rollback()


def getDateEditValue(dateEdit, record, fieldName):
    record.setValue(fieldName, toVariant(dateEdit.date()))


def getDatetimeEditValue(dateEdit, timeEdit, record, fieldName, useTime):
    date = dateEdit.date()
    if date:
        if useTime:
            value = QDateTime(date, timeEdit.time())
        else:
            value = QDateTime(date)
    else:
        value = QDateTime()
    record.setValue(fieldName, QVariant(value))


def getSpinBoxValue(spinBox, record, fieldName):
    record.setValue(fieldName, QVariant(spinBox.value()))


def getDoubleBoxValue(spinBox, record, fieldName):
    record.setValue(fieldName, QVariant(spinBox.value()))


def getComboBoxValue(comboBox, record, fieldName):
    record.setValue(fieldName, QVariant(comboBox.currentIndex()))


def getCheckBoxValue(checkBox, record, fieldName):
    record.setValue(fieldName, QVariant(1 if checkBox.isChecked() else 0))


def getCheckBoxUniqueValue(checkBox, record, tableName, fieldName):
    if checkBox.isChecked():
        db = QtGui.qApp.db
        table = db.table(tableName)
        db.updateRecords(table.name(), table[fieldName].eq(0))
    getCheckBoxValue(checkBox, record, fieldName)


def getWidgetValue(widget, record, fieldName):
    u"""
    :param widget: QWidget instance with value() method
    :param record: QSqlRecord instance
    :param fieldName: QSqlField name
    """
    record.setValue(fieldName, QVariant(widget.value()))


def getLabelImageValue(image, record, fieldName, tableName):
    if image:
        ba = QByteArray()
        image.open(QIODevice.ReadOnly)
        ba = image.readAll()
        image.close()
        stmt = QString()
        db = QtGui.qApp.db
        db.insertOrUpdate(db.table(tableName), record)
        stream = QTextStream(stmt, QIODevice.WriteOnly)
        stream << ('UPDATE %s SET image=x\'' % tableName)
        stream << ba.toHex()
        stream << ('\' WHERE id=\'%d\'' % (forceInt(record.value('id'))))
        db.query(stmt)
