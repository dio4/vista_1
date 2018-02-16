# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2015 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import os.path
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

from PyQt4                  import QtCore, QtGui

from library.dbfpy.dbf      import Dbf
from library.Utils          import forceBool, forceDate, forceInt, forceString, forceStringEx, \
                                   toVariant,pyDate, getVal

from Ui_ExportAttachClientPage1 import Ui_ExportAttachClientPage1
from Ui_ExportFLCR23Page2       import Ui_ExportFLCR23Page2 # Ui_ExportFLCR23Page2 - используется, т.к. если создавать новую форму, то они будут идентичны

class CExportClientAttachWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)
        self.setWizardStyle(QtGui.QWizard.ModernStyle)
        self.page1 = CExportAttachClientPage1(self)
        self.page2 = CExportAttachClientPage2(self)
        self.addPage(self.page1)
        self.addPage(self.page2)
        self.setWindowTitle(u'Мастер экспорта приписанного населения Краснодарского края')
        self.tmpDir = ''
        self.lpuCode = None

    def getTmpDir(self):
        if not self.tmpDir:
            self.tmpDir = QtGui.qApp.getTmpDir('FAP')
        return self.tmpDir

    def cleanup(self):
        if self.tmpDir:
            QtGui.qApp.removeTmpDir(self.tmpDir)
            self.tmpDir = ''

    def exec_(self):
        QtGui.QWizard.exec_(self)
        self.cleanup()

class CExportAttachClientPage1(QtGui.QWizardPage, Ui_ExportAttachClientPage1):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.setupUi(self)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(1)
        self.progressBar.setText('')
        self.setWindowTitle(u'Экспорт приписанного населения')
        self.setExportMode(False)
        self.done = False
        self.aborted = False
        self.parent = parent
        self.connect(parent, QtCore.SIGNAL('rejected()'), self.abort)
        self.cmbInsurer.setFilter('infisCode IN (\'1207\', \'1807\', \'1507\', \'4407\', \'1107\')')
        self.lstOrgStructure.setTable('OrgStructure')


    def setExportMode(self, bool):
        self.btnCancel.setEnabled(bool)
        self.btnExport.setEnabled(not bool)
        self.btnExport.setEnabled(not bool)

    def log(self, str):
        self.logBrowser.append(str)
        self.logBrowser.update()

    def getDbfName(self):
        lpuId = QtGui.qApp.currentOrgId()
        insurerCode = forceString(QtGui.qApp.db.translate('Organisation', 'id', self.cmbInsurer.value(), 'infisCode'))
        lpuCode = forceString(QtGui.qApp.db.translate('Organisation', 'id', lpuId, 'infisCode'))
        return u'%s%s' % (insurerCode + lpuCode, forceString(self.edtDate.date().toString('MMyyyy')))


    def createDbf(self):
        dbfName = os.path.join(self.parent.getTmpDir(), 'Fap_' + self.getDbfName() + '.dbf')
        dbf = Dbf(dbfName, new=True, encoding='cp866')
        dbf.addField(
            ('SMO_CODE', 'C', 4),        # код СМО плательщика (п.1 примечаний); обязательное; SPR02
            ('CODE_MO',  'C', 5),        # код структурноего подразделения медицинской организации в системе ОМС(ФАП) (п.7 примечаний); обязательное; SPR01
            ('SPV',      'N', 1),        # тип документа, подтверждающего факт страхования по ОМС; обязательное
            ('SPS',      'C', 12),       # серия документа, подтверждающего факт страхования по ОМС; обязательное для документов ОМС, имеющих серию
            ('SPN',      'C', 20),       # номер документа, подтверждающего факт страхования по ОМС (п.3 примечаний); обязательное
            ('FIO',      'C', 40),       # фамилия (п.4 примечаний); обязательное
            ('IMA',      'C', 40),       # имя (п.4 примечаний); обязательное
            ('OTCH',     'C', 40),       # отчество (п.4 примечаний)
            ('DATR',     'D'),           # дата рождения (п.5 примечаний); обязательное
            ('RESULT',   'N', 1),        # результат сверки (п.6 примечаний); обязательное, заполняется СМО по результатам проведенной сверки
            )
        return dbf

    def createQuery(self):
        db = QtGui.qApp.db

        tableInsurer = db.table('Organisation').alias('Insurer')
        tableOrgStructure = db.table('OrgStructure')

        lstOrgStructureDict = self.lstOrgStructure.nameValues()
        lstOrgStructure = lstOrgStructureDict.keys()

        insurerHeaderId = self.cmbInsurer.value()
        cond = [tableOrgStructure['id'].inlist(lstOrgStructure),
                db.joinOr([tableInsurer['head_id'].eq(insurerHeaderId), tableInsurer['id'].eq(insurerHeaderId)])]

        stmt = u'''SELECT Client.lastName,
                           Client.firstName,
                           Client.patrName,
                           Client.birthDate,
                           Insurer.infisCode,
                           OrgStructure.bookkeeperCode,
                           OrgStructure.name AS orgStructureName,
                           ClientPolicy.serial,
                           ClientPolicy.number,
                           rbPolicyKind.code AS policyKindCode
                   FROM Client
                        INNER JOIN ClientAttach ON ClientAttach.client_id = Client.id AND DATE(ClientAttach.begDate) <= DATE_SUB(%(date)s,INTERVAL DAYOFMONTH(%(date)s)-1 DAY)
                                    AND (DATE(ClientAttach.endDate) >=  DATE_SUB(DATE_ADD(DATE_SUB(%(date)s,INTERVAL DAYOFMONTH(%(date)s)-1 DAY),INTERVAL 1 MONTH), INTERVAL 1 DAY) OR DATE(ClientAttach.endDate) IS NULL) AND ClientAttach.deleted = 0
                        INNER JOIN rbAttachType ON rbAttachType.id = ClientAttach.attachType_id AND rbAttachType.code != 8
                        INNER JOIN ClientPolicy ON ClientPolicy.client_id = Client.id AND DATE(ClientPolicy.begDate) <= DATE_SUB(DATE_ADD(DATE_SUB(%(date)s, INTERVAL DAYOFMONTH(%(date)s) - 1 DAY), INTERVAL 1 MONTH), INTERVAL 1 DAY) AND (DATE(ClientPolicy.endDate) > DATE_SUB(DATE_ADD(DATE_SUB(%(date)s, INTERVAL DAYOFMONTH(%(date)s) - 1 DAY), INTERVAL 1 MONTH), INTERVAL 1 DAY) OR DATE(ClientPolicy.endDate) IS NULL) AND ClientPolicy.deleted = 0

                        INNER JOIN rbPolicyKind ON rbPolicyKind.id = ClientPolicy.policyKind_id AND rbPolicyKind.code IN ('1', '2', '3')
                        INNER JOIN rbPolicyType ON rbPolicyType.id = ClientPolicy.policyType_id AND rbPolicyType.name LIKE 'ОМС%%'
                        INNER JOIN OrgStructure ON OrgStructure.id = ClientAttach.orgStructure_id
                        INNER JOIN Organisation Insurer ON Insurer.id = ClientPolicy.insurer_id
                   WHERE %(cond)s
                   ORDER BY Client.lastName, Client.firstName, Client.patrName, Client.birthDate''' % {'date': 'DATE(\'%s\')' % self.edtDate.date().toString(QtCore.Qt.ISODate),
                                                                                                       'cond': db.joinAnd(cond)}

        return db.query(stmt)

    def prepareToExport(self):
        self.done = False
        self.aborted = False
        self.lpuCode = None
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setExportMode(True)
        dbf = self.createDbf()
        self.progressBar.reset()
        self.progressBar.setMaximum(1)
        self.progressBar.setValue(0)
        self.progressBar.setText(u'Запрос в БД...')
        QtGui.qApp.processEvents()
        query = self.createQuery()
        self.progressBar.setMaximum(max(query.size(), 1))
        self.progressBar.reset()
        self.progressBar.setValue(0)
        return dbf, query

    def process(self, dbf, record, insurerCode):
        row = dbf.newRecord()
        row['SMO_CODE'] = insurerCode
        row['CODE_MO'] = forceString(record.value('bookkeeperCode'))
        row['SPV'] = forceInt(record.value('policyKindCode'))
        row['SPS'] = forceString(record.value('serial'))
        row['SPN'] = forceString(record.value('number'))
        row['FIO'] = forceString(record.value('lastName'))
        row['IMA'] = forceString(record.value('firstName'))
        row['OTCH'] = forceString(record.value('patrName'))
        row['DATR'] = pyDate(forceDate(record.value('birthDate')))
        row.store()

    def exportInt(self):
        dbf, query = self.prepareToExport()

        insurerCode = forceString(QtGui.qApp.db.translate('Organisation', 'id', self.cmbInsurer.value(), 'infisCode'))

        self.log(u'ЛПУ: код инфис: "%s".' % insurerCode)

        if not insurerCode:
            self.log(u'<b><font color=red>ОШИБКА</font></b>:'
                     u'Для текущего ЛПУ не задан код инфис')

        self.exportedClients = set()

        # Составляем множество событий, содержащих услуги с модернизацией
        query.exec_() # встаем перед первой записью

        while query.next():
            QtGui.qApp.processEvents()
            record = query.record()
            if self.aborted:
                break
            if not forceBool(record.value('bookkeeperCode')):
                self.log(u'<b><font color=red>ОШИБКА</font></b>:'
                         u'Для подразделения %s не указан код бухгалтерии. Данные выгружены не будут.' % forceString(record.value('orgStructureName')))
                continue
            self.progressBar.step()
            self.process(dbf, record, insurerCode)
        dbf.close()

    def export(self):
        (result, rc) = QtGui.qApp.call(self, self.exportInt)
        self.setExportMode(False)
        if self.aborted or not result:
            self.progressBar.setText(u'прервано')
        else:
            self.progressBar.setText(u'готово')
            self.done = True
            self.emit(QtCore.SIGNAL('completeChanged()'))


    def isComplete(self):
        return self.done


    def abort(self):
        self.aborted = True

    @QtCore.pyqtSlot()
    def on_btnExport_clicked(self):
        self.export()


    @QtCore.pyqtSlot()
    def on_btnCancel_clicked(self):
        self.abort()

class CExportAttachClientPage2(QtGui.QWizardPage, Ui_ExportFLCR23Page2):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)
        self.setTitle(u'Экспорт приписанного населения')
        self.setSubTitle(u'для выполнения шага нажмите кнопку "Завершить"')

        self.pathIsValid = True
        homePath = QtCore.QDir.toNativeSeparators(QtCore.QDir.homePath())
        exportDir = forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ExportFapDif', homePath))
        self.edtDir.setText(exportDir)

    def isComplete(self):
        return self.pathIsValid

    def validatePage(self):
        baseName = 'Fap_' + self.parent.page1.getDbfName() + '.dbf'
        zipFileName = 'Fap_' + self.parent.page1.getDbfName() + '.zip'
        zipFilePath = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                zipFileName)
        zf = ZipFile(zipFilePath, 'w', allowZip64=True)

        filePath = os.path.join(forceStringEx(self.parent.getTmpDir()),
                                                os.path.basename(baseName))
        zf.write(filePath, os.path.basename(baseName), ZIP_DEFLATED)
        zf.close()

        dst = os.path.join(forceStringEx(self.edtDir.text()), zipFileName)
        success, result = QtGui.qApp.call(self, shutil.move, (zipFilePath, dst))

        if success:
            QtGui.qApp.preferences.appPrefs['ExportFapDif'] = toVariant(self.edtDir.text())

        return success


    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtDir_textChanged(self):
        dir = forceStringEx(self.edtDir.text())
        pathIsValid = os.path.isdir(dir)
        if self.pathIsValid != pathIsValid:
            self.pathIsValid = pathIsValid
            self.emit(QtCore.SIGNAL('completeChanged()'))


    @QtCore.pyqtSlot()
    def on_btnSelectDir_clicked(self):
        dir = QtGui.QFileDialog.getExistingDirectory(self,
                 u'Выберите директорию для сохранения файла выгрузки',
                 forceStringEx(self.edtDir.text()),
                 QtGui.QFileDialog.ShowDirsOnly)
        if forceString(dir):
            self.edtDir.setText(QtCore.QDir.toNativeSeparators(dir))

