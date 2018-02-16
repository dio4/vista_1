#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from string import split

from PyQt4 import QtCore, QtGui

from library.DialogBase  import CDialogBase
from library.Utils       import forceBool, forceInt, forceRef, forceString, toVariant

if 'QXmlStreamReader' in QtCore.__dict__:
    from PyQt4.QtCore import QXmlStreamReader
#else:
#    from QtXml import QXmlStreamReader

from Ui_SocCardRbEditor import Ui_RbEditor


#########################################################################

def bcd(dec):
	return ((dec/10)<<4)+(dec%10)


def unbcd(bcd):
	return ((bcd>>4)*10)+bcd%16

#########################################################################

socialInfoFields = (
        'cardNumber', 'cardSerial',  # Серия и номер соц. карты
        'lastName', 'firstName', 'patrName', 'birthDate', 'sex',
        'numberSocial',  # Идентификационный номер социального регистра
        'SNILS', 'INN', 'docType', 'docSerial', 'docNumber',
        'policySerial', 'policyNumber', 'orgCode',
        'policyDate' # дата действия полиса ??
                    )

errorText = {
       0 : u'Нет ошибки',
    1000 : u'Переданы неверные параметры',
    1001 : u'Ошибка открытия COM-порта',
    1002 : u'Недостаточно памяти',
    1003 : u'Библиотека не была проинициализирована',
    1004 : u'Ошибка при посылке данных',
    1005 : u'Неверный ответ от пинпада',
    1006 : u'Пинпад не отвечает',
    1007 : u'Неверная длина ответа от пинпада',
    1008 : u'Повторный вызов',
    1009 : u'Ошибка получения даты/времени',
    1010 : u'Получены данные неправильного размера',
    1011 : u'Ошибка инициализации крипто-модуля',
    1012 : u'Ошибка получения TTC',
    1013 : u'Ошибка работы с файлом транзакций',
    1014 : u'Ошибка расчета MAC',
    1015 : u'Ошибка чтения файла стоп- или блок-листа',
    1016 : u'Карта находится в стоп-листе',
    1017 : u'Карта находится в блок-листе',
    2000 : u'Для работы требуется библиотека Qt v4.5 и выше'
}


vitalInfoMasks = {
# 1. Данные о хронических заболеваниях
    0x0000000001:  u'Астма',
    0x0000000002:  u'Заболевание сердца',
    0x0000000004:  u'Заболевание сосудов',
    0x0000000008:  u'Эпилепсия',
    0x0000000010:  u'Неврологические нарушения',
    0x0000000020:  u'Глаукома',
    0x0000000040:  u'Имеются трансплантированные органы',
    0x0000000080:  u'Имеются съемные протезы',
    0x0000000100:  u'Вживлен водитель сердечного ритма',
    0x0000000200:  u'Фенотип медленной ацетиляции',
    0x0000000400:  u'Нарушение свертываемости крови',
    0x0000000800:  u'Диабет',
    0x0000001000:  u'Находится на лечении гемодиализом',
    0x0000002000:  u'Отсутствуют один или несколько органов',
# 2. Данные о принимаемых препаратах
    0x0000004000:  u'Антипсихотические препараты',
    0x0000008000:  u'Антиконвульсионные препараты',
    0x0000010000:  u'Против аритмии',
    0x0000020000:  u'Регулирующие кровяное давление',
    0x0000040000:  u'Получает стрептокиназу',
    0x0000080000:  u'Регулирующие свертываемость крови',
    0x0000100000:  u'Для лечения диабета',
    0x0000200000:  u'Антигистаминные препараты',
# 3. Данные об аллергиях
    0x0000400000:  u'К анальгетикам',
    0x0000800000:  u'К шерсти животных',
    0x0001000000:  u'К антибиотикам',
    0x0002000000:  u'К цитрусовым',
    0x0004000000:  u'К домашней пыли',
    0x0008000000:  u'К яйцам',
    0x0010000000:  u'К орехам',
    0x0020000000:  u'К пыльце',
    0x0040000000:  u'К другим агентам',
    0x0080000000:  u'К рыбе и морепродуктам',
    0x0100000000:  u'К йоду',
    0x0200000000:  u'К молочным продуктам',
}

allergyMaskList = ( 0x0000800000, 0x0002000000, 0x0004000000, 0x0008000000,
                   0x0010000000, 0x0020000000, 0x0040000000,  0x0080000000, 0x0200000000)
intoleranceMedicamentMaskList = (0x0000400000,  0x0001000000, 0x0100000000)

    #########################################################################

class CCardReader():
    def __init__(self):
        try:
            #FIXME: Atronah: QAxContainer отсутствует на unix
            import platform
            if platform.system() == "Windows":
                from PyQt4.QAxContainer import QAxObject
                self._object = QAxObject()
            else:
                self._object = None
        except:
            self._object = None

        self._initOk = False
        self._rc = 0


    def __del__(self):
        if self._initOk:
            self.finalize()


    def rc(self):
        return self._rc


    def init(self,  nPortNo,  diDevId,  listIssBSC,  szOperatorId):
        u"""Инициализация компонента кардридера
            nPortNo – номер COM-порта, к которому подключено устройство (0 – для USB-картридера).
            diDevId - номер устройства значения 327681, 327682.... для стенда будет 327681.
            IssBSC[6] - код банка, для стенда 000055551111 в формате BCD.
            szOperatorId - идентификатор оператора, для стенда будет 1."""

        # "{40E105FD-A2B1-437A-8A7C-C0D2073DFF11}"
        if not self._object:
            self._rc = 2000
            return False

        self._object.setControl("KostaVeriFoneCardReader.VFPinpad")

        if not self._object.isNull():
            ba = QtCore.QByteArray()

            for x in listIssBSC:
                ba.append("%c" % bcd(x))

            result = self._object.dynamicCall("InitializeCardReader(int, uint, QVariant, QString)",
                    nPortNo, diDevId, QtCore.QVariant(ba), QtCore.QString(szOperatorId));

            if result.isValid():
                self._rc = forceInt(result)
                # usb кард-ридер почему-то выдает ошибку 1000, но при этом работает
                self._initOk = ((self._rc == 0) or (nPortNo == 0 and self._rc == 1000))
                return self._initOk

        return False


    def finalize(self):
        u"""Закрывает соединение с кардридером"""

        if self._object and (not self._object.isNull()) and self._initOk:
            result = self._object.dynamicCall("FinalizeCardReader()")

            if result.isValid():
                self._rc = forceInt(result)
                self._initOk = False
                return (self._rc == 0)

        return False


    def checkCardType(self):
        u"""Проверяет наличие и правильность типа карты в устройстве"""

        if self._object and (not self._object.isNull()):
            result = self._object.property("CheckCardType")

            if result.isValid():
                return forceBool(result)

        return False


    def socialInfoStr(self):
        u"""Возвращает строку с социальной информацией о пациенте"""

        if self._object and (not self._object.isNull()):
            result = self._object.property("SocialInfoStr")

            if result.isValid():
                return forceString(result)

        return None


    def benefitInfoStr(self):
        u"""Возвращает строку с льготами пациента"""

        if self._object and (not self._object.isNull()):
            result = self._object.property("BenefitInfoStr")

            if result.isValid():
                return forceString(result)

        return None


    def vitalInfoStr(self):
        u"""Возвращает строку с витальной информацией о пациенте"""

        if self._object and (not self._object.isNull()):
            result = self._object.property("VitalInfoStr")

            if result.isValid():
                return forceString(result)

        return None


    def socialInfo(self):
        infoStr = self.socialInfoStr()

        if not infoStr:
            return None

        info = {}
        list = split(infoStr, ';')

        for i in range(0,  min(len(list), len(socialInfoFields))):
            info[socialInfoFields[i]] = forceString(list[i])

        if info.has_key('sex'):
            sexMap = {u'Ж':2, u'ж':2, u'М':1, u'м':1}
            info['sex'] = sexMap.get(info['sex'], 0)

        if info.has_key('birthDate'):
            info['birthDate'] = QtCore.QDate.fromString(info['birthDate'], 'dd.MM.yyyy')

        return info


    def benefitInfo(self):
        u"""Возвращает информацию о льготах пациента в виде списка
        (код льготы , дата начала действия, дата окончания действия)"""

        benefitStr = self.benefitInfoStr()
        benefitList = []

        if benefitStr:
            list = split(benefitStr,';')

            for i in range(0,  len(list)-1, 3):
                if list[i] != '':
                    code = forceString(list[i])
                    begDate = QtCore.QDate().fromString(list[i+1], 'dd.MM.yyyy') if list[i+1] != '' else QtCore.QDate()
                    endDate = QtCore.QDate().fromString(list[i+2], 'dd.MM.yyyy') if list[i+2] != '' else QtCore.QDate()
                    benefitList.append((code,  begDate,  endDate))

        return benefitList


    def vitalInfo(self):
        vitalStr = self.vitalInfoStr()

        return forceInt(vitalStr) if vitalStr else 0


    def errorText(self,  rc):
        return errorText.get(rc,  u'Неизвестная ошибка')


    def decodeVitalInfo(self, vitalInfo=None):
        vital = vitalInfo if vitalInfo else self.vitalInfo()

        allergyList = []
        intoleranceMedicamentList = []
        notesList = []

        for (mask,  descr) in vitalInfoMasks.items():
            if (vital & mask) != 0:
                if mask in allergyMaskList:
                    allergyList.append(descr)
                elif mask in intoleranceMedicamentMaskList:
                    intoleranceMedicamentList.append(descr)
                else:
                    notesList.append(descr)

        return (allergyList,  intoleranceMedicamentList,  notesList)

    #########################################################################

class CCardReaderEmulator(CCardReader):
    def __init__(self):
        self._initOk = False


    def rc(self):
        return 0


    def init(self,  nPortNo,  diDevId,  listIssBSC,  szOperatorId):
        return True


    def finalize(self):
        return True


    def checkCardType(self):
        return True


    def socialInfoStr(self):
        return u'700;102;Пупкин;Василий;Алибабаевич;28.01.1971;М;3;88122341292;'\
            u'780126465781;14;40 97;366512;54 АВ;3478262;СК "Вирилис";16.09.2008;'


    def benefitInfoStr(self):
        return u'101;01.05.2008;28.09.2008;150;17.09.2008;26.09.2008;010;18.08.2008;'\
                    u';083;;30.09.2011;030;;;050;23.09.2008;31.03.2008;'


    def vitalInfoStr(self):
        return u'297795998022'

    #########################################################################

class CDocumentTypeRBXmlStreamReader(QXmlStreamReader):
    def __init__(self,  parent,  showLog = False):
        QXmlStreamReader.__init__(self)
        self.parent = parent
        self.showLog = showLog
        self.elementsList = {}


    def raiseError(self,  str):
        QXmlStreamReader.raiseError(self, u'[%d:%d] %s' % (self.lineNumber(), self.columnNumber(), str))


    def log(self, str,  forceLog = False):
        if (self.showLog or forceLog) and (hasattr(self.parent, 'logBrowser')):
            self.parent.logBrowser.append(str)
            self.parent.logBrowser.update()


    def readFile(self, device):
        self.setDevice(device)

        try:
            while (not self.atEnd()):
                self.readNext()

                if self.isStartElement():
                    if self.name() == "DOC_TYPE":
                        self.readData()
                    else:
                        self.raiseError(u'Неверный формат экспорта данных.')

                if self.hasError():
                    return False

        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
            self.log(u'! Ошибка ввода-вывода: %s' % msg,  True)
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            self.log(u'! Ошибка: %s' % unicode(e),  True)
            return False


        return not self.hasError()


    def readData(self):
        assert self.isStartElement() and self.name() == "DOC_TYPE"
        self.elementsList = {}

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "row"):
                    (code,  name) = self.readRow()
                    self.elementsList[code]=name
                else:
                    self.readUnknownElement()

            if self.hasError():
                break


    def readRow(self):
        assert self.isStartElement() and self.name() == "row"

        rowCode = ''
        rowName = ''

        while not self.atEnd():
            QtGui.qApp.processEvents()
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "DocumentCode"):
                    rowCode = forceString(self.readElementText())
                elif (self.name() == "DocumentName"):
                    rowName = forceString(self.readElementText())
                else:
                    self.readUnknownElement()

        return (rowCode,  rowName)


    def readUnknownElement(self, report = True):
        """ Читает неизвестный элемент, и сообщает об этом,
            если report ==True """

        assert self.isStartElement()

        if report:
            self.log(u'Неизвестный элемент: '+self.name().toString())

        while (not self.atEnd()):
            self.readNext()

            if (self.isEndElement()):
                break

            if (self.isStartElement()):
                self.readUnknownElement(report)

            if self.hasError():
                break

    #########################################################################

class CBenefitTypeRBXmlStreamReader(QXmlStreamReader):
    def __init__(self,  parent,  showLog = False):
        QXmlStreamReader.__init__(self)
        self.parent = parent
        self.showLog = showLog
        self.elementsList = {}


    def raiseError(self,  str):
        QXmlStreamReader.raiseError(self, u'[%d:%d] %s' % (self.lineNumber(), self.columnNumber(), str))


    def log(self, str,  forceLog = False):
        if (self.showLog or forceLog) and (hasattr(self.parent,  'logBrowser')):
            self.parent.logBrowser.append(str)
            self.parent.logBrowser.update()


    def readFile(self, device):
        self.setDevice(device)

        try:
            while (not self.atEnd()):
                self.readNext()

                if self.isStartElement():
                    if self.name() == "SPUN_REGLAMENT":
                        self.readReglament()
                    else:
                        self.raiseError(u'Неверный формат экспорта данных.')

                if self.hasError():
                    return False

        except IOError, e:
            QtGui.qApp.logCurrentException()
            msg=''
            if hasattr(e, 'filename'):
                msg = u'%s:\n[Errno %s] %s' % (e.filename, e.errno, e.strerror)
            else:
                msg = u'[Errno %s] %s' % (e.errno, e.strerror)
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка ввода-вывода', msg, QtGui.QMessageBox.Close)
            self.log(u'! Ошибка ввода-вывода: %s' % msg,  True)
            return False
        except Exception, e:
            QtGui.qApp.logCurrentException()
            QtGui.QMessageBox.critical (self.parent,
                u'Произошла ошибка', unicode(e), QtGui.QMessageBox.Close)
            self.log(u'! Ошибка: %s' % unicode(e),  True)
            return False


        return not self.hasError()


    def readReglament(self):
        assert self.isStartElement() and self.name() == "SPUN_REGLAMENT"
        self.elementsList = {}

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "SPRAV_Category"):
                    self.readData()
                else:
                    self.readUnknownElement()

            if self.hasError():
                break


    def readData(self):
        assert self.isStartElement() and self.name() == "SPRAV_Category"

        while (not self.atEnd()):
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "row"):
                    (code,  name) = self.readRow()
                    self.elementsList[code]=name
                else:
                    self.readUnknownElement()

            if self.hasError():
                break


    def readRow(self):
        assert self.isStartElement() and self.name() == "row"

        rowCode = ''
        rowName = ''
        rowShortName = ''

        while not self.atEnd():
            QtGui.qApp.processEvents()
            self.readNext()

            if self.isEndElement():
                break

            if self.isStartElement():
                if (self.name() == "CategoryCode"):
                    rowCode = forceString(self.readElementText())
                elif (self.name() == "CategoryName"):
                    rowName = forceString(self.readElementText())
                elif (self.name() == "CategoryName_Short"):
                    rowShortName = forceString(self.readElementText())
                else:
                    self.readUnknownElement()

        name = rowShortName if rowShortName else rowName
        return (rowCode,  name)


    def readUnknownElement(self, report = True):
        """ Читает неизвестный элемент, и сообщает об этом,
            если report ==True """

        assert self.isStartElement()

        if report:
            self.log(u'Неизвестный элемент: '+self.name().toString())

        while (not self.atEnd()):
            self.readNext()

            if (self.isEndElement()):
                break

            if (self.isStartElement()):
                self.readUnknownElement(report)

            if self.hasError():
                break

    #########################################################################

class CRbEditDialog(CDialogBase, Ui_RbEditor):
    def __init__(self,  tableName,  code,  name,  filter=None, parent=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.edtSocCode.setText(code)
        self.edtRbName.setText(name)
        self.edtName.setText(name)
        self.cmbRb.setTable(tableName)
        #self.cmbRb.setShowFields(CRBComboBox.showCodeAndName)
        if filter:
            self.cmbRb.setFilter(filter)
        self.chkSelect.setFocus()
        self.tableName = tableName
        id = self.lookupIdByName(name)

        if id:
            self.cmbRb.setValue(id)
        else:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)


    def lookupIdByName(self,  name):
        db = QtGui.qApp.db
        table = db.table(self.tableName)
        record = db.getRecordEx(table, 'id',
                                [table['name'].eq(name)], 'id')

        return forceInt(record.value(0)) if record else None


    @QtCore.pyqtSlot()
    def on_chkSelect_clicked(self):
        self.edtCode.setEnabled(False)
        self.edtName.setEnabled(False)
        self.cmbRb.setEnabled(True)


    @QtCore.pyqtSlot()
    def on_chkAddNew_clicked(self):
        self.edtCode.setEnabled(True)
        self.edtName.setEnabled(True)
        self.cmbRb.setEnabled(False)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(not (\
            self.edtName.text().isEmpty() or self.edtCode.text().isEmpty()))


    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtCode_textChanged(self):
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(not (\
            self.edtName.text().isEmpty() or self.edtCode.text().isEmpty()))


    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtName_textChanged(self):
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(not (\
            self.edtName.text().isEmpty() or self.edtCode.text().isEmpty()))


    @QtCore.pyqtSlot(int)
    def on_cmbRb_currentIndexChanged(self,  idx):
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(idx != 0)

#########################################################################

def askUserForDocumentTypeId(parent,  socCode,  name):
    tableName = 'rbDocumentType'
    dialog = CRbEditDialog(tableName,  socCode,  name ,  None,  parent)
    id = None

    if dialog.exec_():
        db = QtGui.qApp.db
        table = db.table(tableName)

        if dialog.chkSelect.isChecked():
            id = dialog.cmbRb.value()
            record = db.getRecord(table, 'id, socCode', id)
            record.setValue('socCode',  toVariant(socCode))
            db.updateRecord(table, record)
        else:
            record = table.newRecord()
            record.setValue('code',  toVariant(dialog.edtCode.text()))
            record.setValue('name',  toVariant(dialog.edtName.text()))
            record.setValue('socCode',  toVariant(socCode))
            id = db.insertRecord(table, record)

    return id


def askUserForBenefitId(parent,  socCode,  name):
    classId = forceRef(QtGui.qApp.db.translate('rbDocumentType', 'name', u'льгота', 'id'))
    filter = 'class_id=%d' % classId if classId else None
    dialog = CRbEditDialog('vrbSocStatusType',  socCode,  name ,  filter,  parent)
    id = None

    if dialog.exec_():
        db = QtGui.qApp.db
        table = db.table('rbSocStatusType')

        if dialog.chkSelect.isChecked():
            id = dialog.cmbRb.value()
            record = db.getRecord(table, 'id, socCode', id)
            record.setValue('socCode',  toVariant(socCode))
            db.updateRecord(table, record)
        else:
            record = table.newRecord()
            record.setValue('code',  toVariant(dialog.edtCode.text()))
            record.setValue('name',  toVariant(dialog.edtName.text()))
            record.setValue('socCode',  toVariant(socCode))
            id = db.insertRecord(table, record)

    return id


def loadXmlRb(parent, fileName,  xmlReader):
    elements = {}

    try:
        if fileName:
            inFile = QtCore.QFile(fileName)
            if not inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                QtGui.QMessageBox.warning(parent, u'Социальная Карта: Импорт справочников XML',
                                  u'Не могу открыть файл для чтения %s:\n%s.' %\
                                  (fileName, inFile.errorString()))
            else:
                if (xmlReader.readFile(inFile)):
                    elements = xmlReader.elementsList
    finally:
        return elements


def loadDocumentTypeRb(parent,  fileName):
    xmlReader = CDocumentTypeRBXmlStreamReader(parent)
    return loadXmlRb(parent, fileName, xmlReader)


def loadBenefitTypeRb(parent,  fileName):
    xmlReader = CBenefitTypeRBXmlStreamReader(parent)
    return loadXmlRb(parent, fileName, xmlReader)