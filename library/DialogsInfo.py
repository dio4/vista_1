# -*- coding: utf-8 -*-

from library.PrintInfo import CInfo


class CDialogsInfo(CInfo):
    u"""Мастер ввода с набором диалогов"""
    def __init__(self, context):
        CInfo.__init__(self, context)
        self.dialogs = []

    def addDialog(self, dialog):
        """
        Инициализация нового диалога
        :param dialog:
        :return:
        """
        dialog.setContext(self.context)
        if len(self.dialogs):
            self.dialogs[-1].setNext(dialog)
            dialog.setPrev(self.dialogs[-1])
        self.dialogs = self.dialogs + [dialog, ]

    def activate(self, dialog):
        """
        Запуск указанного диалога
        :param:
        :return:
        """
        dialog.exec_()
        return dialog

    def createDialInt(self, title, min, max, step=1, default=None):
        from library.PrintDialog import CIntPrintDialog
        dialog = CIntPrintDialog(title, min, max, step, default)
        self.addDialog(dialog)
        return dialog
    def dialInt(self, title, min, max, step=1, default=None):
        """
        Выводит заданный диапазон целых чисел посредством QSpinBox
        :param title, min, max, step=1, default=None:
        :return диалог с заданным QSpinBox:
        """
        return self.activate( self.createDialInt(title, min, max, step, default) )

    def createDialFloat(self, title, min, max, step, decimals, default=None):
        from library.PrintDialog import CFloatPrintDialog
        dialog = CFloatPrintDialog(title, min, max, step, decimals, default)
        self.addDialog(dialog)
        return dialog
    def dialFloat(self, title, min, max, step, decimals, default=None):
        """
        Выводит заданный диапазон вещественных чисел посредством QSpinBox
        :param title, min, max, step, decimals, default=None:
        :return диалог с заданным QSpinBox:
        """
        return self.activate( self.createDialFloat(title, min, max, step, decimals, default) )

    def createDialBool(self, title, name, default=None):
        from library.PrintDialog import CBoolPrintDialog
        dialog = CBoolPrintDialog(title, name, default)
        self.addDialog(dialog)
        return dialog
    def dialBool(self, title, name, default=None):
        """
        Выводит QCheckBox
        :param title, name, default=None:
        :return диалог с заданным QCheckBox:
        """
        return self.activate( self.createDialBool(title, name, default) )

    def createDialMultiBool(self, title, names, defaults=None):
        from library.PrintDialog import CMultiBoolPrintDialog
        dialog = CMultiBoolPrintDialog(title, names, defaults)
        self.addDialog(dialog)
        return dialog
    def dialMultiBool(self, title, names, defaults=None):
        """
        Выводит заданный набор QCheckBox, names воспринимается как список формата (номер, название)
        :param title, names, defaults=None:
        :return диалог с заданными QCheckBox:
        """
        return self.activate( self.createDialMultiBool(title, names, defaults) )

    def createDialDate(self, title, default=None):
        from library.PrintDialog import CDatePrintDialog
        dialog = CDatePrintDialog(title, default)
        self.addDialog(dialog)
        return dialog
    def dialDate(self, title, default=None):
        """
        Выводит дату посредством CDateEdit
        :param title, default=None:
        :return диалог с заданным CDateEdit:
        """
        return self.activate( self.createDialDate(title, default) )

    def createDialTime(self, title, default=None):
        from library.PrintDialog import CTimePrintDialog
        dialog = CTimePrintDialog(title, default)
        self.addDialog(dialog)
        return dialog
    def dialTime(self, title, default=None):
        """
        Выводит время посредством CTimeEdit
        :param title, default=None:
        :return диалог с заданным CTimeEdit:
        """
        return self.activate( self.createDialTime(title, default) )

    def createDialString(self, title, default=None):
        from library.PrintDialog import CStringPrintDialog
        dialog = CStringPrintDialog(title, default)
        self.addDialog(dialog)
        return dialog
    def dialString(self, title, default=None):
        """
        Выводит строку посредством QLineEdit
        :param title, default=None:
        :return диалог с заданным QLineEdit:
        """
        return self.activate( self.createDialString(title, default) )

    def createDialList(self, title, lst=None, default=None):
        from library.PrintDialog import CListPrintDialog
        if not lst:
            lst = []
        dialog = CListPrintDialog(title, lst, default)
        self.addDialog(dialog)
        return dialog
    def dialList(self, title, lst=None, default=None):
        """
        Выводит заданный список значений в виде QComboBox
        :param title, lst=[], default=None:
        :return диалог с заданным QComboBox:
        """
        if not lst:
            lst = []
        return self.activate( self.createDialList(title, lst, default) )

    def createDialRB(self, title, table, default=None):
        from library.PrintDialog import CRBPrintDialog
        dialog = CRBPrintDialog(title, table, default)
        self.addDialog(dialog)
        return dialog
    def dialRB(self, title, table, default=None):
        """
        Выводит указанный справочник в виде QComboBox
        :param title, table, default=None:
        :return диалог с заданным QComboBox:
        """
        return self.activate( self.createDialRB(title, table, default) )

    def createDialMultiList(self, title, lst=None, default=None):
        from library.PrintDialog import CMultiListPrintDialog
        if not lst:
            lst = []
        dialog = CMultiListPrintDialog(title, lst, default)
        self.addDialog(dialog)
        return dialog
    def dialMultiList(self, title, lst=None, default=None):
        """
        Выводит указанный список в виде QListWidget
        :param title, lst=[], default=None:
        :return диалог с заданным QListWidget:
        """
        if not lst:
            lst = []
        return self.activate( self.createDialMultiList(title, lst, default) )

    def createDialOrg(self, title):
        from library.PrintDialog import COrgPrintDialog
        dialog = COrgPrintDialog(title)
        self.addDialog(dialog)
        return dialog
    def dialOrg(self, title):
        """
        Выводит полный список организаций посредством CItemListDialog
        :param title:
        :return диалог с заданным CItemListDialog:
        """
        return self.activate( self.createDialOrg(title) )

    def createDialInsurerOrg(self, title):
        from library.PrintDialog import CInsurerOrgPrintDialog
        dialog = CInsurerOrgPrintDialog(title)
        self.addDialog(dialog)
        return dialog
    def dialInsurerOrg(self, title):
        """
        Выводит список страховых организаций посредством CInsurerComboBox
        :param title:
        :return диалог с заданным CInsurerComboBox:
        """
        return self.activate(self.createDialInsurerOrg(title))

    def createDialOrgStructure(self, title, org):
        from library.PrintDialog import COrgStructurePrintDialog
        dialog = COrgStructurePrintDialog(title, org)
        self.addDialog(dialog)
        return dialog
    def dialOrgStructure(self, title, org):
        """
        Выводит список подразделений посредством COrgStructureComboBox
        :param title, org:
        :return диалог с заданным COrgStructureComboBox:
        """
        return self.activate( self.createDialOrgStructure(title, org) )

    def createDialPerson(self, title, org=None, orgStructure=None, default=None):
        from library.PrintDialog import CPersonPrintDialog
        dialog = CPersonPrintDialog(title, org, orgStructure, default)
        self.addDialog(dialog)
        return dialog
    def dialPerson(self, title, org=None, orgStructure=None, default=None):
        """
        Выводит список врачей посредством CPersonComboBoxEx
        :param title, org=None, orgStructure=None, default=None:
        :return диалог с заданным CPersonComboBoxEx:
        """
        return self.activate( self.createDialPerson(title, org, orgStructure, default) )

    def createDialService(self, title):
        from library.PrintDialog import CServicePrintDialog
        dialog = CServicePrintDialog(title)
        self.addDialog(dialog)
        return dialog
    def dialService(self, title):
        """
        Выводит список услуг посредством CRBServiceComboBox
        :param title:
        :return диалог с заданным CRBServiceComboBox:
        """
        return self.activate( self.createDialService(title) )