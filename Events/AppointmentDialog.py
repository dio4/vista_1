# -*- coding: utf-8 -*-

import datetime
import json
import urllib

from PyQt4       import QtGui, QtCore
from PyQt4.QtSql import QSqlQuery

import s11_client
from library.Utils        import forceBool, forceString, getVal
from Ui_AppointmentDialog import Ui_Dialog

def ShowAppointmentDialog(widget, clientId):
    dlg = CAppointmentDialog(widget, clientId)
    dlg.exec_()

class CAppointmentDialog(QtGui.QDialog, Ui_Dialog):
    serverSelected = -1
    specialitySelected = -1
    doctorSelected = -1
    dateSelected = -1
    timeSelected = -1

    port = None
    serverId = ''
    clientId = 0
    patientId = 0

    trueLpuList = [u'п51', u'п48']  # for test

    lpuList = [
        # structure view:
        #       name
        #       proxy
        #       serverId
        {'name': u'',                        'proxy': r'',                                        'serverId': u''},
        # {'name': u'Поликлиника №48',         'proxy': r'http://83.149.4.106/soap/proxy.php?wsdl', 'serverId': u'п48'},
        # {'name': u'Поликлиника №51',         'proxy': r'http://83.149.4.106/soap/proxy.php?wsdl', 'serverId': u'п51'},
        # {'name': u'Поликлиника №21',         'proxy': r'http://83.149.4.106/soap/proxy.php?wsdl', 'serverId': u'п21'},
        # {'name': u'Детская поликлиника №8',  'proxy': r'http://83.149.4.106/soap/proxy.php?wsdl', 'serverId': u'д8'},
        # {'name': u'Женская консультация №5', 'proxy': r'http://83.149.4.106/soap/proxy.php?wsdl', 'serverId': u'жк5'}
    ]

    @classmethod
    def addLpuToList(cls, lpu):
        if lpu not in cls.lpuList: cls.lpuList.append(lpu)

    specList = [
        # structure view:
        #       speciality
        #       specialityRegionalCode
    ]
    doctorsList = [
        # structure view:
        #       id
        #       lastName
        #       firstName
        #       patrName
    ]
    datesList = [
        # structure view:
        #       date
        #       available
    ]
    timeList = [
        # structure view:
        #       time
    ]

    def __init__(self, parent, clientId):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.clientId = clientId
        self.getPatientInfo()

        # replace lpuList variable with a new data
        useRemoteList = forceBool(getVal(QtGui.qApp.preferences.appPrefs, 'EGISZ', ''))
        if useRemoteList:
            remoteAddress = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'EGISZAddress', ''))
            lpuRes = urllib.urlopen(remoteAddress + r"/lpulist.php").read()
            lpuRes = json.loads(lpuRes)
            locator = s11_client.s11ServiceLocator()
            ##self.port = locator.gets11Port(remoteAddress + r"/soap/proxy.php?wsdl")

            for item in lpuRes:
                if forceString(item.get('key', None)).lower() != u'понко' and forceString(item.get('key', None)).lower() != u'п48'\
                        and forceString(item.get('key', None)).lower() != u'п51':
                    continue
                # if item not in self.trueLpuList: continue # !!! for test !!!
                if (item['internal']):
                    url = remoteAddress + r"/proxy.php?wsdl"
                else:
                    url = item['url'] + r"?wsdl"
        
                port = locator.gets11Port(url)
                
                if item.has_key('name'):
                    lpuName = item['name']
                else:
                    req = s11_client.getOrganisationInfoIn()
                    req._serverId = item['key']
                    result = port.getOrganisationInfo(req)
                    lpuName = unicode(result._shortName.decode('utf-8'))

                self.addLpuToList({'name': lpuName, 'proxy': url, 'serverId': item['key']})


        for item in self.lpuList:
            self.cmbLpuList.addItem(item['name'])

    def dateToSet(self, date):
        return (date.year, date.month, date.day, 0, 0, 0, 0, 0, 0)

    def timeToSet(self, time):
        return (0, 0, 0, time.hour, time.minute, time.second, 0, 0, 0)

    def humanLongToShortName(self, lastName, firstName, patrName = ""):
        result = u'{0} {1}.{2}.'.format(lastName, firstName[0] if firstName else "", patrName[0] if patrName else "")
        if not patrName:
            result = result[:-1]
        return result

    def getPatientShortName(self):
        return self.humanLongToShortName(self.lastName, self.firstName, self.patrName)

    def getDoctorShortName(self, id):
        for item in self.doctorsList:
            if item['id'] == id:
                return self.humanLongToShortName(item['lastName'], item['firstName'], item['patrName'])
        return ''

    def getPatientInfo(self):
        qrySelect = QSqlQuery(QtGui.qApp.db.db)
        sqlText = 'SELECT lastName, firstName, patrName, birthDate FROM Client WHERE id = {0}'.format(self.clientId)
        if not (qrySelect.exec_(sqlText)):
            QtGui.QMessageBox.critical(self, u'Ошибка 0x001', u'Ошибка получения данных о пациете.', QtGui.QMessageBox.Close)
            return 1
        if not qrySelect.first():
            QtGui.QMessageBox.critical(self, u'Ошибка 0x002', u'Ошибка получения данных о пациете.', QtGui.QMessageBox.Close)
            return 2
        self.lastName = unicode(qrySelect.value(0).toString())
        self.firstName = unicode(qrySelect.value(1).toString())
        self.patrName = unicode(qrySelect.value(2).toString())
        self.birthDate = qrySelect.value(3).toDateTime().toPyDateTime()
        return 0

    def getSelectedLpu(self):
        index = self.serverSelected
        if index > 0:
            return self.lpuList[index]['serverId']
        else:
            return 0

    def getSelectedSpeciality(self):
        index = self.specialitySelected
        if index > 0:
            return self.specList[index]['specialityRegionalCode']
        else:
            return 0

    def getSelectedDoctor(self):
        index = self.doctorSelected
        if index > 0:
            return self.doctorsList[index]['id']
        else:
            return 0

    def getSelectedDate(self):
        index = self.dateSelected
        if index >= 0:
            return self.dateToSet(self.datesList[index]['date'])
        else:
            return -1

    def getSelectedTime(self):
        index = self.timeSelected
        if index >= 0:
            return self.timeToSet(self.timeList[index]['time'])
        else:
            return -1

    def clearFromSpecialityList(self):
        self.cmbSpec.clear()

    def clearFromDoctorsList(self):
        self.cmbDoctor.clear()

    def clearFromDates(self):
        self.lstDate.clear()

    def clearFromTimes(self):
        self.lstTime.clear()

    @QtCore.pyqtSlot(int)
    def on_cmbLpuList_currentIndexChanged(self, index):
        self.serverSelected = index
        if index <= 0:
            self.clearFromSpecialityList()
            return

        locator = s11_client.s11ServiceLocator()
        self.port = locator.gets11Port(self.lpuList[self.serverSelected]['proxy'])
        self.serverId = self.getSelectedLpu()

        serverId = self.serverId
        lastName, firstName, patrName = self.lastName, self.firstName, self.patrName
        birthDate = self.dateToSet(self.birthDate)

        req = s11_client.findPatientIn()
        req._serverId, req._lastName, req._firstName, req._patrName, req._birthDate = serverId, lastName, firstName, patrName, birthDate
        result = self.port.findPatient(req)
        self.lblAdd.setText('')
        if not result._success:
            #QtGui.QMessageBox.critical(self, u'Ошибка', u'Пациент не найден\n' + result._message + '\n' + result._patientId, QtGui.QMessageBox.Close)
            self.lblAdd.setText(u'Пациент не найден в выбранном ЛПУ')
            self.cmbSpec.clear()
            return

        self.patientId = result._patientId

        req = s11_client.getPersonnelIn()
        req._serverId, req._orgStructureId, req._recursive = serverId, 0, True
        result = self.port.getPersonnel(req)

        specialityList = ['']
        self.specList = [{'speciality': '', 'specialityRegionalCode': ''}]
        for item in result._list:
            speciality, specialityRegionalCode = item._speciality.decode('utf-8'), item._specialityRegionalCode
            if speciality not in specialityList:
                specialityList.append(speciality)
                self.specList.append({'speciality': speciality, 'specialityRegionalCode': specialityRegionalCode})

        self.cmbSpec.clear()
        for item in self.specList:
            self.cmbSpec.addItem(item['speciality'])

    @QtCore.pyqtSlot(int)
    def on_cmbSpec_currentIndexChanged(self, index):
        self.specialitySelected = index
        if index <= 0:
            self.clearFromDoctorsList()
            return

        serverId = self.serverId

        req = s11_client.getPersonnelIn()
        req._serverId, req._orgStructureId, req._recursive = serverId, 0, True
        result = self.port.getPersonnel(req)

        self.doctorsList = [{'id': 0, 'lastName': '', 'firstName': '', 'patrName': ''}]
        for item in result._list:
            specialityRegionalCode = item._specialityRegionalCode
            if specialityRegionalCode == self.getSelectedSpeciality():
                id = item._id
                lastName = item._lastName.decode('utf-8')
                firstName = item._firstName.decode('utf-8')
                patrName = item._patrName.decode('utf-8')
                self.doctorsList.append({'id': id, 'lastName': lastName, 'firstName': firstName, 'patrName': patrName})

        self.cmbDoctor.clear()
        for item in self.doctorsList:
            if item['lastName']:
                doctorName = self.getDoctorShortName(item['id'])
            else:
                doctorName = ''
            self.cmbDoctor.addItem(doctorName)

    @QtCore.pyqtSlot(int)
    def on_cmbDoctor_currentIndexChanged(self, index):
        self.doctorSelected = index
        if index <= 0:
            self.clearFromDates()
            return

        serverId = self.serverId
        personId = self.getSelectedDoctor()
        today = self.dateToSet(datetime.datetime.now())
        afterTwoWeeks = self.dateToSet(datetime.datetime.now() + datetime.timedelta(days=14))

        req = s11_client.getTicketsAvailabilityIn()
        req._serverId, req._personId, req._begDate, req._endDate = serverId, personId, today, afterTwoWeeks
        result = self.port.getTicketsAvailability(req)

        self.datesList = []
        self.lstDate.clear()
        for item in sorted(result._list, cmp=lambda x,y: cmp(x._date, y._date)):
            date = item._date
            free = item._free
            if free > 0:
                self.lstDate.addItem(u'{0:02}.{1:02}.{2}, свободно: {3}'.format(date[2], date[1], date[0], free))
                self.datesList.append({'date': datetime.date(date[0], date[1], date[2]), 'available': free})

    @QtCore.pyqtSlot(int)
    def on_lstDate_currentRowChanged(self, currentRow):
        self.dateSelected = currentRow
        if currentRow < 0:
            self.clearFromTimes()
            return

        serverId = self.serverId
        personId = self.getSelectedDoctor()
        date = self.getSelectedDate()

        req = s11_client.getWorkTimeAndStatusIn()
        req._serverId, req._personId, req._date = serverId, personId, date
        result = self.port.getWorkTimeAndStatus(req)._amb

        self.timeList = []
        self.lstTime.clear()
        for item in sorted(result._tickets, cmp=lambda x,y: cmp(x._time, y._time)):
            if item._free:
                time = item._time
                self.lstTime.addItem(u'{0:02}:{1:02}'.format(time[3], time[4]))
                self.timeList.append({'time': datetime.time(time[3], time[4], time[5])})

    @QtCore.pyqtSlot(int)
    def on_lstTime_currentRowChanged(self, currentRow):
        if currentRow < 0:
            return
        self.timeSelected = currentRow

    @QtCore.pyqtSlot()
    def on_btnOk_clicked(self):
        serverId = self.serverId
        personId = self.getSelectedDoctor()
        patientId = self.patientId
        date = self.getSelectedDate()
        time = self.getSelectedTime()
        timeStr = '{0:02}:{1:02}'.format(time[3], time[4])

        req = s11_client.getPatientQueueIn()
        req._serverId, req._patientId = serverId, patientId
        result = self.port.getPatientQueue(req)
        for item in result._list:
            if item._date == date and item._personId == personId:
                message = u'Пациент уже записан в этот день к выбранному врачу на время {0}:{1}.\n\nЖелаете ли Вы удалить предыдущую запись?'.format(item._time[3], item._time[4])
                if QtGui.QMessageBox.question(self, u'Внимание!', message,  QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                    req = s11_client.dequeuePatientIn()
                    req._serverId, req._patientId, req._queueId = serverId, patientId, item._queueId
                    req._note = u'Удалено через "ВИСТА-МЕД"'
                    result = self.port.dequeuePatient(req)
                    if result._success:
                        QtGui.QMessageBox.information(self, u'Информация', u'Пациент успешно удален')
                    else:
                        QtGui.QMessageBox.critical(self, u'Ошибка', u'Не удалось удалить пациента\n\nОшибка: ' + result._message, QtGui.QMessageBox.Close)
                    self.on_cmbDoctor_currentIndexChanged(0)
                    self.on_cmbDoctor_currentIndexChanged(self.cmbDoctor.currentIndex())
                return

        message = u'Записать пациента {0} на {1} к выбранному врачу?'.format(self.getPatientShortName(), timeStr)
        if QtGui.QMessageBox.question(self, u'Внимание!', message,  QtGui.QMessageBox.Yes|QtGui.QMessageBox.No, QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
            return

        req = s11_client.enqueuePatientIn()
        req._serverId, req._personId, req._patientId, req._date, req._time = serverId, personId, patientId, date, time
        req._note = u'Добалено через "ВИСТА-МЕД"'
        result = self.port.enqueuePatient(req)
        if result._success:
            QtGui.QMessageBox.information(self, u'Информация', u'Пациент успешно добавлен')
        else:
            QtGui.QMessageBox.critical(self, u'Ошибка', u'Не удалось добавить пациента\n\nОшибка: ' + result._message, QtGui.QMessageBox.Close)
        self.close()


    @QtCore.pyqtSlot()
    def on_btnCancel_clicked(self):
        self.close()
