 #!/usr/bin/env python
# -*- coding: utf-8 -*-
from Ui_ImportProfiles import Ui_Dialog
from Cimport import *

def ImportProfiles(widget):
    try:
        setEIS_db()
        dlg=CImportProfiles(widget, QtGui.qApp.EIS_db)
        dlg.exec_()
    except:
        EIS_close()

class CImportProfiles(CEISimport, QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent, EIS_db):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        CImport.__init__(self, self.log)
        self.progressBar.setFormat('%v')
        self.EIS_db=EIS_db
        self.tbl_rbService=tbl('rbService')
        self.fillCmbProfileType()
        
    def fillCmbProfileType(self):
        EIS_db = self.EIS_db
        stmt = 'SELECT PROFILE_TYPE_NAME, ID_PROFILE_TYPE FROM VMU_PROFILE_TYPE'
        query = EIS_db.query(stmt)
        go = query.first()
        while go:
            self.cmbProfileType.addItem(forceString(query.value(0)))
            self.cmbProfileType.setItemData(self.cmbProfileType.count()-1, query.value(1))
            go = query.next()
        index = self.cmbProfileType.findData(QVariant(3))
        if index > -1:
            self.cmbProfileType.setCurrentIndex(index)
        

    def startImport(self):
        db=QtGui.qApp.db
        EIS_db=self.EIS_db
        if not EIS_db:
            return
        n=0
        prof_found=0
        prof_add=0
        
        if self.chkProfileType.isChecked():
            where = 'where VMU_PROFILE.ID_PROFILE_TYPE=%d' % forceInt(self.cmbProfileType.itemData(self.cmbProfileType.currentIndex()))
        else:
            where = ''
        stmt="""
            select *
            from VMU_PROFILE
            %s
        """ % where
        query = EIS_db.query(stmt)
        query.setForwardOnly(True)
        num=query.size()
        if num>0:
            self.progressBar.setMaximum(num)
        else:
            self.progressBar.setMaximum(0)
        while query.next():
            QtGui.qApp.processEvents()
            if self.abort:
                break
            n+=1
            if num<=0:
                self.labelNum.setText(u'всего записей в источнике: '+str(n))
            self.n=n
            record = query.record()
            self.record=record
#                ID_PROFILE=record.value('ID_PROFILE').toInt()[0]
            PROFILE_INFIS_CODE=unicode(record.value('PROFILE_INFIS_CODE').toString())
            PROFILE_BEGIN_DATE=record.value('PROFILE_BEGIN_DATE')
            PROFILE_END_DATE=record.value('PROFILE_END_DATE')

            rbServiceId=None
            cond=u'infis=\"'+PROFILE_INFIS_CODE+u'\"'# and eisLegacy=1'
            rbService=db.getRecordEx(self.tbl_rbService, '*', cond)
            if rbService:
                prof_found+=1
                rbServiceId==forceInt(rbService.value('id'))
                rbService.setValue('eisLegacy', QVariant(1))
                rbService.setValue('begDate', PROFILE_BEGIN_DATE)
                if PROFILE_END_DATE:
                    rbService.setValue('endDate', PROFILE_END_DATE)
                db.updateRecord(self.tbl_rbService, rbService)
            else:
                prof_add+=1
                PROFILE_NAME=unicode(record.value('PROFILE_NAME').toString())
                rbServiceFields=[
                    ('code', PROFILE_INFIS_CODE), ('name', PROFILE_NAME),
                    ('eisLegacy', 1), ('infis', PROFILE_INFIS_CODE),
                    ('begDate', PROFILE_BEGIN_DATE), ('endDate', PROFILE_END_DATE)]
                rbServiceId=getId(self.tbl_rbService, rbServiceFields)
            self.progressBar.setValue(n)
            statusText = u'добавлено %d, найдено %d' % (prof_add, prof_found)
            self.statusLabel.setText(statusText)

        self.log.append(u'добавлено %d, найдено %d' % (prof_add, prof_found))
        self.log.append(u'готово')
        self.progressBar.setValue(n-1)


    def err2log(self, e):
        if self.log:
            self.log.append(u'запись '+str(self.n)+': '+e)

