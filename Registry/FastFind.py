# -*- coding: utf-8 -*-
import re
from PyQt4 import QtGui, QtCore

from Ui_FastFindClient import Ui_FastFindClient


class CFastFindClientWindow(QtGui.QDialog, Ui_FastFindClient):
    u"""
        Окно для быстрого поиска пациентов

        Шаблоны:
        Ф* И* (Руд Его)
        Ф* И* О* (Руд Его Евген)
        Ф* И* О* ДДММГГ (Руд Его Евген 010295)
        Ф* И* О* ДДММГГГГ (Руд Его Евген 01021995)
        Ф* И* ДДММГГ (Руд Его 010295)
        Ф* И* ДДММГГГГ (Руд Его 01021995)
        Ф* ДДММГГ (Руд 010295)
        Ф* ДДММГГГГ (Руд 01021995)
    """

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.btnClose.clicked.connect(self.close)
        self.btnSearch.clicked.connect(self.prepareToSearch)
        self.findFields = None

    def parseFirstName(self, text):
        result = re.search('\s\w+', text, re.UNICODE)
        if result:
            return result.group(0)[1:]
        else:
            return None

    def parseLastName(self, text):
        result = re.search('^\w+', text, re.UNICODE)
        if result:
            return result.group(0)
        else:
            return None

    def parsePatrName(self, text):
        result = [
            re.search('\s\w+\s\d', text, re.UNICODE),
            re.search('\s\w+$', text.trimmed(), re.UNICODE)
        ]
        if result[0]:
            return result[0].group(0)[1:-2]
        elif result[1]:
            return result[1].group(0)[1:]
        else:
            return None

    def parseDate(self, text):
        result = re.search('\d+', text, re.UNICODE)
        if result:
            result = result.group(0)
            if len(result) == 6:
                day = int(result[:2])
                month = int(result[2:4])
                year = 2000 + int(result[4:6]) if int(result[4:6]) < 40 else 1900 + int(result[4:6])
                date = QtCore.QDate()
                date.setDate(year, month, day)
                return date
            elif len(result) == 8:
                day = int(result[:2])
                month = int(result[2:4])
                year = int(result[4:])
                date = QtCore.QDate()
                date.setDate(year, month, day)
                return date
            else:
                return None
        else:
            return None

    def prepareToSearch(self):
        try:
            # firstTemplate:
            # Ф* И* О* ДДММГГ (Руд Его Евген 010295)
            # Ф* И* О* ДДММГГГГ (Руд Его Евген 01021995)
            firstTemplate = re.search('\w+\s\w+\s\w+\s\d+$', self.edtTemplate.text().trimmed(), re.UNICODE)
            # secondTemplate:
            # Ф* И* ДДММГГ (Руд Его Евген 010295)
            # Ф* И* ДДММГГГГ (Руд Его Евген 01021995)
            secondTemplate = re.search('\w+\s\w+\s\d+$', self.edtTemplate.text().trimmed(), re.UNICODE)
            # thirdTemplate:
            # Ф* ДДММГГ (Руд Его Евген 010295)
            # Ф* ДДММГГГГ (Руд Его Евген 01021995)
            thirdTemplate = re.search('\w+\s\d+$', self.edtTemplate.text().trimmed(), re.UNICODE)
            # fourthTemplate:
            # Ф* И* О* (Руд Его Евген)
            fourthTemplate = re.search('\w+\s\w+\s\w+', self.edtTemplate.text().trimmed(), re.UNICODE)
            # lastTemplate
            # Ф* И* (Руд Его)
            if firstTemplate:
                firstName = self.parseFirstName(self.edtTemplate.text())
                lastName = self.parseLastName(self.edtTemplate.text())
                patrName = self.parsePatrName(self.edtTemplate.text())
                birthDate = self.parseDate(self.edtTemplate.text())
            elif secondTemplate:
                firstName = self.parseFirstName(self.edtTemplate.text())
                lastName = self.parseLastName(self.edtTemplate.text())
                patrName = None
                birthDate = self.parseDate(self.edtTemplate.text())
            elif thirdTemplate:
                firstName = None
                lastName = self.parseLastName(self.edtTemplate.text())
                patrName = None
                birthDate = self.parseDate(self.edtTemplate.text())
            elif fourthTemplate:
                firstName = self.parseFirstName(self.edtTemplate.text())
                lastName = self.parseLastName(self.edtTemplate.text())
                patrName = self.parsePatrName(self.edtTemplate.text())
                birthDate = None
            else:
                firstName = self.parseFirstName(self.edtTemplate.text())
                lastName = self.parseLastName(self.edtTemplate.text())
                patrName = None
                birthDate = None

            if lastName and (firstName or birthDate):
                self.findFields = {
                    'firstName': firstName,
                    'lastName': lastName,
                    'patrName': patrName,
                    'birthDate': birthDate
                }
            else:
                self.findFields = None
        except Exception:
            self.findFields = None
        finally:
            self.close()
