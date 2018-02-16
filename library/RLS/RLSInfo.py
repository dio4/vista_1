# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from library.PrintInfo import CInfo
from library.Utils import forceString
from library.DbComboBox import CDbDataCache


class CRLSInfo(CInfo):
    def __init__(self, context, code):
        CInfo.__init__(self, context)
        self.code = code

    def _load(self):
        db = QtGui.qApp.db
        table = db.table('rls.vNomen')

        fields = ['INPName', 'INPName', 'tradeName', 'tradeNameLat', 'dosage', 'form', 'filling', 'packing']
        record = db.getRecordEx(table, fields, table['code'].eq(self.code))
        if record:
            self._tradeName = forceString(record.value('tradeName'))
            self._tradeNameLat = forceString(record.value('tradeNameLat'))
            self._INPName = forceString(record.value('INPName'))
            self._INPNameLat = forceString(record.value('INPNameLat'))
            self._form = forceString(record.value('form'))
            self._dosage = forceString(record.value('dosage'))
            self._filling = forceString(record.value('filling'))
            self._packing = forceString(record.value('packing'))
            return True
        else:
            self._tradeName = ''
            self._tradeNameLat = ''
            self._INPName = ''
            self._INPNameLat = ''
            self._form = ''
            self._dosage = ''
            self._filling = ''
            self._packing = ''
            return False

    tradeName = property(lambda self: self.load()._tradeName)
    tradeNameLat = property(lambda self: self.load()._tradeNameLat)
    INPName = property(lambda self: self.load()._INPName)
    INPNameLat = property(lambda self: self.load()._INPNameLat)
    form = property(lambda self: self.load()._form)
    dosage = property(lambda self: self.load()._dosage)
    filling = property(lambda self: self.load()._filling)
    packing = property(lambda self: self.load()._packing)

    def __str__(self):
        self.load()
        values = filter(bool, [self._INPName, self.tradeName, self._dosage, self._form, self._filling, self._packing])
        return u', '.join(values)


class CRLSExtendedInfo(CInfo):
    def __init__(self, context, code, formId=None, amount=0, note=u''):
        super(CRLSExtendedInfo, self).__init__(context)
        self._code = code
        self._rlsInfo = None
        self._formId = formId
        self._form = u''
        self._amount = amount
        self._note = note

    def _load(self):
        if self._formId:
            tableForm = QtGui.qApp.db.table('rls.rlsForm')
            cache = CDbDataCache.getData('rls.rlsForm', 'name', tableForm['id'].eq(self._formId), addNone=True, noneText=u'-')
            self._form = forceString(cache.strList[-1])

        self._rlsInfo = self.context.getInstance(CRLSInfo, self._code)
        return True

    form = property(lambda self: self.load()._form)
    note = property(lambda self: self.load()._note)
    amount = property(lambda self: self.load()._amount)
    rls = property(lambda self: self.load()._rlsInfo)

    def __str__(self):
        return u', '.join([unicode(self.rls),
                           u'{0} {1}'.format(self.amount, self.form),
                           self.note])

    def __repr__(self):
        return unicode(self)
