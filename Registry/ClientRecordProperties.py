# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtGui

from library.Utils import forceRef, forceString

from Ui_ClientRecordProperties import Ui_ClientRecordProperties


class CRecordProperties(QtGui.QDialog, Ui_ClientRecordProperties):
    def __init__(self, parent, table, recordId=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.table = table
        self.recordId = recordId
        self.setWindowTitle(u'Свойства записи')
        
    def exec_(self):
        self.setInfo()
        return QtGui.QDialog.exec_(self)
        
    def setInfo(self):
        if self.recordId is not None:
            text = u''
            db = QtGui.qApp.db
            record = db.getRecord(self.table, '*', self.recordId)
            createPerson_id = forceRef(record.value('createPerson_id'))
            createPersonName = ''
            if createPerson_id:
                createPersonRecord = db.getRecord('vrbPersonWithSpeciality', '*', createPerson_id)
                if createPersonRecord:
                    createPersonName = forceString(createPersonRecord.value('name'))
            text += u'Создатель записи: %s\n'%createPersonName
            createDatetime = forceString(record.value('createDatetime'))
            createDatetime = createDatetime if createDatetime else ''
            text += u'Дата создания записи: %s\n'%createDatetime
            modifyPerson_id = forceRef(record.value('modifyPerson_id'))
            modifyPersonName = ''
            if modifyPerson_id:
                modifyPersonRecord = db.getRecord('vrbPersonWithSpeciality', '*', modifyPerson_id)
                if modifyPersonRecord:
                    modifyPersonName = forceString(modifyPersonRecord.value('name'))
            text += u'Редактор записи: %s\n'%modifyPersonName
            modifyDatetime = forceString(record.value('modifyDatetime'))
            modifyDatetime = modifyDatetime if modifyDatetime else ''
            text += u'Дата редактирования записи: %s\n'%modifyDatetime
            self.edtInfo.setText(text)
            
            
            