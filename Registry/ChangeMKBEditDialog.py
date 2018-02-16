# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui, QtCore

from library.interchange        import setLineEditValue
from library.ItemsListDialog    import CItemEditorBaseDialog
from library.Utils              import forceRef, forceString, forceStringEx, toVariant

from Events.Utils               import getAvailableCharacterIdByMKB, getMKBName

from Ui_ChangeMKBEditDialog     import Ui_ChangeMKBEditDialog


class CChangeMKBEditDialog(CItemEditorBaseDialog, Ui_ChangeMKBEditDialog):
    def __init__(self, parent):
        CItemEditorBaseDialog.__init__(self, parent, 'Diagnosis')
        self.setupUi(self)
        self.setWindowTitleEx(u'Исправить шифр МКБ')
        self.setupDirtyCather()
        self.oldMKB = ''
        self.oldCharacterId = None
        self.characterId = None


    def setRecord(self, record):
        CItemEditorBaseDialog.setRecord(self, record)
        setLineEditValue(self.edtMKB,   record, 'MKB')
        setLineEditValue(self.edtMKBEx, record, 'MKBEx')
        self.oldMKB = forceStringEx(self.edtMKB.text())
        self.oldCharacterId = record.value('character_id')
        self.setIsDirty(False)


    def getRecord(self):
        record = CItemEditorBaseDialog.getRecord(self)
        record.setValue('MKB', QtCore.QVariant(forceStringEx(self.edtMKB.text()))) # getLineEditValue не годится, т.к. edtMKB.text() возвращает unicode а не QString
        record.setValue('MKBEx', QtCore.QVariant(forceStringEx(self.edtMKBEx.text())))
        record.setValue('character_id', toVariant(self.characterId))
        return record


    def saveInternals(self, id):
        if self.oldCharacterId != self.characterId:
            db = QtGui.qApp.db
            stmt = 'UPDATE Diagnostic SET character_id=%s WHERE diagnosis_id=%d AND character_id IS NOT NULL' % (self.characterId if self.characterId else 'NULL', id)
            db.query(stmt)


    def checkDataEntered(self):
        result = True
        MKB = forceStringEx(self.edtMKB.text())
        result = result and (MKB or self.checkInputMessage(u'Код МКБ', False, self.edtNumber))
        result = result and self.checkAndUpdateDiagnosisCharacter(MKB)
        return result


    def checkAndUpdateDiagnosisCharacter(self, MKB):
        if self.oldCharacterId:
            characterIdList = getAvailableCharacterIdByMKB(MKB)
            db = QtGui.qApp.db
            codes = set()
            for id in characterIdList:
                code = forceString(db.translate('rbDiseaseCharacter', 'id', id, 'replaceInDiagnosis'))
                codes.add(code)
            codes = list(codes)
            codes.sort()
            characterIdList = []
            for code in codes:
                id = forceRef(db.translate('rbDiseaseCharacter', 'code', code, 'id'))
                characterIdList.append(id)
            if self.oldCharacterId in characterIdList:
                self.characterId = self.oldCharacterId
            elif not characterIdList or not characterIdList[-1]:
                self.characterId = None
            else:
                newCharacterId = characterIdList[-1]
                message = u'Заболевание с ранее указанным диагнозом %s (%s) имело характер "%s".\nНовый код диагноза %s (%s) предполагает характер "%s".\nВсё равно исправить код диагноза?' % \
                          (  self.oldMKB,
                             getMKBName(self.oldMKB),
                             forceString(db.translate('rbDiseaseCharacter', 'id', self.oldCharacterId, 'name')),
                             MKB,
                             getMKBName(MKB),
                             forceString(db.translate('rbDiseaseCharacter', 'id', newCharacterId, 'name')),
                          )
                ok = QtGui.QMessageBox.question( self, u'Внимание', message, QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Cancel)
                if ok:
                    self.characterId = newCharacterId
                return ok
        return True