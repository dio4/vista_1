# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from Orgs.OrgComboBox import CInsurerComboBox
from Orgs.OrgStructComboBoxes import COrgStructureComboBox
from Orgs.Orgs import COrgsList
from Orgs.PersonComboBoxEx import CPersonComboBoxEx
from Orgs.PersonInfo import CPersonInfo
from Orgs.Utils import COrgInfo, COrgStructureInfo
from Ui_SimplePrintDialog import Ui_Dialog
from library.DateEdit import CDateEdit
from library.DialogBase import CDialogBase
from library.PrintInfo import *
from library.TimeEdit import CTimeEdit, stringToTime
from library.Utils import *
from library.crbcombobox import CRBComboBox
from library.crbservicecombobox import CRBServiceComboBox

u"""Dialogs for print templates"""

class CPrintDialog(CDialogBase):
    u"""Print dialog for selection of variable var"""
    def __init__(self, title, default=None, context=None):
        u"""
        title - title of dialog window
        default - default value for variable
        """
        CDialogBase.__init__(self, None)
        if hasattr(self, 'setupUi'):
            self.setupUi(self)
        self.init(title, default, context)

    def init(self, title, default=None, context=None):
        self.default = default
        self.context = context
        self.var = None
        self.setWindowTitle(title)
        self.prev = self.next = None

    def getVar(self):
        return self.var if self.var!=None else self.default
        
    def getDefault(self):
        return self.default

    def setContext(self, context):
        self.context = context

    def setPrev(self, prev):
        self.prev = prev

    def setNext(self, next):
        self.next = next


    def toPrev(self):
        if self.prev:
            self.reject()
            self.prev.exec_()


    def toNext(self):
        if self.next:
            self.accept()
            self.next.exec_()


    def saveData(self):
        self.var = None
        return True


    def canClose(self):
        self.var = self.default
        return True


class CSimplePrintDialog(CPrintDialog, Ui_Dialog):
    u"""Simple print dialog  with 1 variable"""
    def __init__(self, title, width, height, default=None):
        u"""
        title - title of dialog window
        (width, height) - size of dialog
        default - default value for variable
        """
        CPrintDialog.__init__(self, title, default)
        size = QtCore.QSize(width,height)#.expandedTo(self.minimumSizeHint())
        self.resize(size)



    def setPrev(self, prev):
        CPrintDialog.setPrev(self, prev)
        self.btnPrev.setEnabled(prev != None)


    def setNext(self, next):
        CPrintDialog.setNext(self, next)
        self.btnNext.setEnabled(next != None)


class CIntPrintDialog(CSimplePrintDialog):
    u"""Диалог выбора целого числа (var - целое число)"""
    def __init__(self, title, min, max, step=1, default=None):
        CSimplePrintDialog.__init__(self, title, 100, 20, default)
        self.spinBox = QtGui.QSpinBox(self)
        self.spinBox.setObjectName("spinBox")
        self.spinBox.setMinimum(min)
        self.spinBox.setMaximum(max)
        self.spinBox.setSingleStep(step)
        self.verticalLayout.insertWidget(0, self.spinBox)
        self.setInteger(default if default else min)


    def setInteger(self, val):
        self.spinBox.setValue(val)


    def saveData(self):
        self.var = self.spinBox.value()
        return True



class CFloatPrintDialog(CSimplePrintDialog):
    u"""Диалог выбора вещественного числа (var - вещественное число)"""
    def __init__(self, title, min, max, step, decimals, default=None):
        CSimplePrintDialog.__init__(self, title, 400, 50, default)
        self.spinBox = QtGui.QDoubleSpinBox(self)
        self.spinBox.setObjectName("spinBox")
        self.spinBox.setMinimum(min)
        self.spinBox.setMaximum(max)
        self.spinBox.setDecimals(decimals)
        self.spinBox.setSingleStep(step)
        self.verticalLayout.insertWidget(0, self.spinBox)
        self.setFloat(default if default else min)


    def setFloat(self, val):
        self.spinBox.setValue(val)


    def saveData(self):
        self.var = self.spinBox.value()
        return True



class CBoolPrintDialog(CSimplePrintDialog):
    u"""Диалог выбора логического значения (var - логическое значение True или False)"""
    def __init__(self, title, name, default=None):
        CSimplePrintDialog.__init__(self, title, 400, 50, default)
        self.checkBox = QtGui.QCheckBox(self)
        self.checkBox.setText(name)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout.insertWidget(0, self.checkBox)
        self.setBool(default if default else False)


    def setBool(self, val):
        self.checkBox.setChecked(val)


    def saveData(self):
        self.var = self.checkBox.isChecked()
        return True
        
        
        
class CMultiBoolPrintDialog(CSimplePrintDialog):
    u"""Диалог выбора массива логических значений (var - массив логических значений True или False)"""
    def __init__(self, title, names, defaults=None):
        CSimplePrintDialog.__init__(self, title, 400, 50, defaults)
        self.checkBoxes = []
        for (i, name) in enumerate(names):
            checkBox = QtGui.QCheckBox(self)
            checkBox.setText(name)
            checkBox.setObjectName("checkBox" + str(i))
            self.verticalLayout.insertWidget(i, checkBox)
            self.checkBoxes = self.checkBoxes + [checkBox, ]
        self.setBools(defaults if defaults else [False, ]*len(names))


    def setBools(self, vals):
        for (i, val) in enumerate(vals):
            self.checkBoxes[i].setChecked(val)


    def saveData(self):
        self.var = [False, ]*len(self.checkBoxes)
        for (i, box) in enumerate(self.checkBoxes):
            self.var[i] = box.isChecked()
        return True




class CDatePrintDialog(CSimplePrintDialog):
    u"""Диалог выбора даты (var - объект типа CDateInfo)"""
    def __init__(self, title, default=None):
        CSimplePrintDialog.__init__(self, title, 400, 50, default)
        self.dateEdit = CDateEdit(self)
        self.dateEdit.setObjectName("dateEdit")
        self.verticalLayout.insertWidget(0, self.dateEdit)
        if default:
            self.setDate(default)


    def setDate(self, date):
        #self.setWindowTitle(str(date))!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.dateEdit.setDate(forceDate(date))


    def saveData(self):
        self.var = CDateInfo(self.dateEdit.date())
        return True



class CTimePrintDialog(CSimplePrintDialog):
    u"""Диалог выбора времени (var - объект типа CTimeInfo)"""
    def __init__(self, title, default=None):
        CSimplePrintDialog.__init__(self, title, 400, 50, default)
        self.timeEdit = CTimeEdit(self)
        self.timeEdit.setObjectName("timeEdit")
        self.verticalLayout.insertWidget(0, self.timeEdit)
        if default:
            self.setTime(default)


    def setTime(self, time):
        self.timeEdit.setTime(stringToTime(str(time)))


    def saveData(self):
        self.var = CTimeInfo(self.timeEdit.time())
        return True


class CStringPrintDialog(CSimplePrintDialog):
    u"""Диалог выбора строки (var - строка)"""
    def __init__(self, title, default=None):
        CSimplePrintDialog.__init__(self, title, 400, 50, default)
        self.lineEdit = QtGui.QLineEdit(self)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.insertWidget(0, self.lineEdit)
        if default:
            self.setString(default)


    def setString(self, str):
        self.lineEdit.setText(str)


    def saveData(self):
        self.var = unicode(self.lineEdit.text())
        return True


class CListPrintDialog(CSimplePrintDialog):
    u"""Список с выбором одного из элементов (var - номер элемента)"""
    def __init__(self, title, lst=None, default=None):
        if not lst:
            lst = []
        CSimplePrintDialog.__init__(self, title, 400, 300, default)
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout.insertWidget(0, self.comboBox)
        self.setItems(lst)


    def addItem(self, item):
        self.comboBox.addItem(QString(unicode(item)))


    def addItems(self, lst):
        for item in lst:
            self.addItem(item)


    def setItems(self, lst):
        self.comboBox.clear()
        self.addItems(lst)
        if len(lst):
            self.comboBox.setCurrentIndex(self.default if self.default else 0)


    def getListValue(self):
        return self.comboBox.currentText()


    def saveData(self):
        self.var = self.comboBox.currentIndex()
        return True



class CMultiListPrintDialog(CSimplePrintDialog):
    u"""Список с выбором множества элементов (var - массив номеров элементов)"""
    def __init__(self, title, lst=None, default=None): # default: 0 - ничего, 1 - 1-я позиция, 2 - все позиции
        if not lst:
            lst = []
        self.begSelection = default
        if self.begSelection == 0:
            defaultPos = []
        elif self.begSelection == 1:
            defaultPos = [0, ]
        elif self.begSelection == 2:
            defaultPos = xrange(len(lst))
        else:
            defaultPos = [0, ]
        CSimplePrintDialog.__init__(self, title, 400, 300, defaultPos)
        self.listWidget = QtGui.QListWidget(self)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.verticalLayout.insertWidget(0, self.listWidget)
        self.setItems(lst)


    def addItem(self, item):
        self.listWidget.addItem(QString(item))


    def addItems(self, lst):
        for item in lst:
            self.addItem(item)


    def setItems(self, lst):
        self.listWidget.clear()
        self.addItems(lst)
        #for i in self.getDefault():
        #    if i < len(lst):
        #        self.listWidget.setCurrentRow(i, QtGui.QItemSelectionModel.Select)
        if self.begSelection == 0:
            pass
        elif self.begSelection == 1:
            self.listWidget.setCurrentRow(self.getDefault()[0] if len(self.getDefault()) else 0)
        elif self.begSelection == 2:
            self.listWidget.selectAll()
        else:
            self.listWidget.setCurrentRow(0)

    def getListValues(self):
        return [unicode(self.listWidget.item(i).text()) for i in xrange(self.listWidget.count()) if self.listWidget.item(i).isSelected()]


    def saveData(self):
        self.var = [i for i in xrange(self.listWidget.count()) if self.listWidget.item(i).isSelected()]
        return True



class COrgPrintDialog(CPrintDialog, COrgsList):
    u"""Диалог выбора организации (var - объект типа COrgInfo)"""
    def __init__(self, title):
       COrgsList.__init__(self, None, forSelect=True)
       CPrintDialog.init(self, title)


    def saveData(self):
        self.var = COrgInfo(self.context, self.currentItemId())
        return True


class CRBPrintDialog(CSimplePrintDialog):
    u"""Выбор элемента из справочника
    var - код элемента
    или объект класса, если этот класс задан"""
    def __init__(self, title, table, class_=None, combo=None, default=None):
        CSimplePrintDialog.__init__(self, title, 200, 100, default)
        self.class_ = class_
        if combo:
            self.comboBox = combo(self)
        else:
            self.comboBox = CRBComboBox(self)
            self.comboBox.setTable(table)
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout.insertWidget(0, self.comboBox)


    def getId(self):
        return self.comboBox.value()


    def getCode(self):
        return self.comboBox.code()


    def getName(self):
        return self.comboBox.model().getName(self.comboBox.currentIndex())


    def saveData(self):
        if self.class_:
            self.var = self.context.getInstance(self.class_, self.getId())
        else:
            self.var = self.getCode()
        return True


class COrgStructurePrintDialog(CRBPrintDialog):
    u"""Диалог выбора подразделения (var - объект типа COrgStructureInfo)"""
    def __init__(self, title, org):
        u"""org - организация COrgInfo, из которой выбираем подразделение"""
        CRBPrintDialog.__init__(self, title, 'OrgStructure', COrgStructureInfo, COrgStructureComboBox)
        self.org = org
        self.comboBox.setOrgId(self.org.id)


class CPersonPrintDialog(CRBPrintDialog):
    u"""Выбор врача (var - объект тип CPersonInfo)"""
    def __init__(self, title, org=None, orgStructure=None, default=None):
        CRBPrintDialog.__init__(self, title, 'Person', CPersonInfo, CPersonComboBoxEx, default)
        self.org = org
        self.orgStructure = orgStructure
        if self.org:
            self.comboBox.setOrgId(self.org.id)
        if self.orgStructure:
            self.comboBox.setOrgStructureId(self.orgStructure.id)


class CServicePrintDialog(CRBPrintDialog):
    u"""Выбор услуги (var - объект тип CServiceInfo)"""
    def __init__(self, title, default=None):
        from Events.EventInfo import CServiceInfo
        CRBPrintDialog.__init__(self, title, 'rbService', CServiceInfo, CRBServiceComboBox, default)
        self.comboBox.setTable('rbService')


class CInsurerOrgPrintDialog(CRBPrintDialog):
    u"""Диалог выбора страховой компании"""
    def __init__(self, title):
        CRBPrintDialog.__init__(self, title, 'Organisation', COrgInfo, CInsurerComboBox)
        self.comboBox.setFilter('isInsurer')


