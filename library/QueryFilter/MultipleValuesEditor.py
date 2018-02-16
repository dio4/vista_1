# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui, QtCore
import s11main_rc
from Reports.ReportsGenerator.TemplateParametersModel import CTemplateParametersModel
from Reports.ReportsGenerator.TemplateParameter import CTemplateParameter

'''
Created on 11.03.2014

@author: atronah
'''






## Окно для редактирования списка значений 
class CMultipleValuesEditDialog(QtGui.QDialog):
    def __init__(self, valueModel, parent = None):
        
#        QtGui.QDialog.__init__(self, parent, flags)
        super(CMultipleValuesEditDialog, self).__init__(parent)
        
        self.setupUi()
        self.tableView.setModel(valueModel)
        self.tableView.setItemDelegateForColumn(1, valueModel.itemDelegate())
        self.tableView.hideColumn(0)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        
    
    
    ## Инициализация интерфейса пользователя    
    def setupUi(self):
        self.setWindowTitle(u'Укажите значения для фильтра')
        
        self.tableView = QtGui.QTableView()
        self.btnOk = QtGui.QPushButton(u'Ок') #TODO: atronah: Почему-то не удалось создать QDialogButtonBox(buttons = Ok)
        self.btnOk.clicked.connect(self.accept)
#        self.toolButton = QtGui.QToolButton()
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.tableView)
        layout.addWidget(self.btnOk)
#        layout.addWidget(self.toolButton)
        self.setLayout(layout)
        
        QtCore.QMetaObject.connectSlotsByName(self)
    
    

## Виджет для редактирования набора значений
class CMultipleValuesEditor(QtGui.QWidget):
    ## Конструктор редактора
    # @param typeName: имя типа (пока соответствует ключам словаря CTemplateParameter.editWidgetInfoForTypes)
    # @param valueEncoder: функция вида (valueList, isHumanReadable) преобразования списка строковых значений в одну строку (CQueryFilterOperator.formatValuesToString)
    # @param valueDecoder: функция вида (valueList, isHumanReadable) преобразования строки в список строковых значений (CQueryFilterOperator.decodeValuesFromString)
    # @param valueCount: количество значений, которые должен обрабатывать редактор (-1 для динамически увеличивающегося числа значений)
    # @param parent: родительсткий виджет
    def __init__(self, typeName, valueEncoder, valueDecoder, valueCount = 1, parent = None):
        super(CMultipleValuesEditor, self).__init__(parent)
        self.setupUi()
        self._typeName = typeName
        self._valueCount = valueCount
        self._valueModel = CTemplateParametersModel(self)
        self._valueEncoder = valueEncoder
        self._valueDecoder = valueDecoder
        self._defaultValue = QtCore.QVariant([None] * self._valueCount)
        self.initValueModel()
        
        
#    def __del__(self):
#        self._valueModel.clear()
        
        
    
    ## Инициализация модели со значениями
    def initValueModel(self):
        self._valueModel.clear()
        for idx in xrange(self._valueCount):
            parameter = CTemplateParameter(name = u'value%d' % idx,
                                           typeName = self._typeName,
                                           sortIndex = idx)
            self._valueModel.addItem(parameter)
    
    
    ## Инициализация интерфейса пользователя    
    def setupUi(self):
        self.lineEdit = QtGui.QLineEdit()
        self.lineEdit.setObjectName(u'lineEdit')
        self.btnEdit = QtGui.QToolButton()
        self.btnEdit.setObjectName(u'btnEdit')
        self.btnEdit.setText('...')
        self.btnEdit.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.btnDefault = QtGui.QToolButton()
        self.btnDefault.setObjectName(u'btnDefault')
        self.btnDefault.setIcon(QtGui.QIcon(QtGui.QPixmap(':/new/prefix1/icons/actions-edit-undo-icon.png')))
        self.btnDefault.setFocusPolicy(QtCore.Qt.ClickFocus)
        
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.btnEdit)
        layout.addWidget(self.btnDefault)
        self.setLayout(layout)
        
        QtCore.QMetaObject.connectSlotsByName(self)
        
        
        
    
    ## Устанавливает режим "только для чтения" для строки редактирования
    def setLineEditReadOnly(self, isReadOnly):
        self.lineEdit.setReadOnly(isReadOnly)
    
    
    ## Установка значений для редактора
    def setValue(self, value):
        if value.type() != QtCore.QVariant.List: 
            return False
        
        self.lineEdit.setText(self._valueEncoder(value, isHumanReadable = True))
        
        valueList = value.toList()
        valueList += [QtCore.QVariant()] * (self._valueModel.rowCount() - len(valueList))
        
        for idx, value in enumerate(valueList):
            if idx not in xrange(self._valueModel.rowCount()):
                return False
            self._valueModel.items()[idx].setValue(value.toString())
        
        
        return True
        
        
    ## Список значений, установленных в редакторе
    def value(self):
        return QtCore.QVariant([parameter.value() if parameter.value() is not None 
                                                  else self._defaultValue.toList()[idx] 
                                for idx, parameter in enumerate(self._valueModel.items())
                                ])
    
    
    ## Установка значений по умолчанию для редактора
    def setDefaultValue(self, defaultValue):
        defaultValueList = defaultValue.toList() if isinstance(defaultValue, QtCore.QVariant) \
                                                    and defaultValue.type() == QtCore.QVariant.List \
                                                 else (defaultValue if isinstance(defaultValue, list) else [defaultValue])
        
        defaultValueList.extend([None] * (self._valueCount - len(defaultValueList)))
        self._defaultValue = QtCore.QVariant(defaultValue)
        return True
        
    
    ## Значение по умолчанию
    def defaultValue(self):
        return self._defaultValue
        
    
    @QtCore.pyqtSlot()
    def on_btnEdit_clicked(self):
        editDialog = CMultipleValuesEditDialog(valueModel = self._valueModel, parent = self)
        if editDialog.exec_():
            self.lineEdit.setText(self._valueEncoder(self.value(), isHumanReadable = True))
    
    
    @QtCore.pyqtSlot()
    def on_btnDefault_clicked(self):
        self.setValue(self.defaultValue())
        
    
    @QtCore.pyqtSlot()
    def on_lineEdit_editingFinished(self):
        value = self._valueDecoder(self.lineEdit.text(), isHumanReadable = True)
        if value.isValid() or self.lineEdit.text().isEmpty():
            self.setValue(value)
        


def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    
    ed = CMultipleValuesEditor(u'str')
    ed.show()
    
    return app.exec_()


if __name__ == '__main__':
    main()