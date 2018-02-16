# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore

from Reports.ReportBase import CReportBase
from Resources.Ui_JobsOperatingReportSetupDialog import Ui_JobsOperatingReportSetupDialog
from library.DialogBase import CDialogBase
from library.Utils import setPref, toVariant, forceBool, getPref


class CJobsOperatingReportSetupDialog(CDialogBase, Ui_JobsOperatingReportSetupDialog):
    def __init__(self, parent=None, columnList=None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)

    def savePreferences(self):
        preferences = CDialogBase.savePreferences(self)
        setPref(preferences, 'chkActionType', toVariant(self.chkActionType.isChecked()))
        setPref(preferences, 'chkBarCode', toVariant(self.chkBarCode.isChecked()))
        setPref(preferences, 'chkClientBirthday', toVariant(self.chkClientBirthday.isChecked()))
        setPref(preferences, 'chkClientName', toVariant(self.chkClientName.isChecked()))
        setPref(preferences, 'chkClientSex', toVariant(self.chkClientSex.isChecked()))
        setPref(preferences, 'chkDatetime', toVariant(self.chkDatetime.isChecked()))
        setPref(preferences, 'chkLabel', toVariant(self.chkLabel.isChecked()))
        setPref(preferences, 'chkNotes', toVariant(self.chkNotes.isChecked()))
        setPref(preferences, 'chkRowNumber', toVariant(self.chkRowNumber.isChecked()))
        setPref(preferences, 'chkSetPerson', toVariant(self.chkSetPerson.isChecked()))

        return preferences

    def loadPreferences(self, preferences):
        self.chkActionType.setChecked(
            forceBool(getPref(preferences, 'chkActionType', True)) and self.chkActionType.isEnabled()
        )
        self.chkBarCode.setChecked(
            forceBool(getPref(preferences, 'chkBarCode', True)) and self.chkBarCode.isEnabled()
        )
        self.chkClientBirthday.setChecked(
            forceBool(getPref(preferences, 'chkClientBirthday', True)) and self.chkClientBirthday.isEnabled()
        )
        self.chkClientName.setChecked(
            forceBool(getPref(preferences, 'chkClientName', True)) and self.chkClientName.isEnabled()
        )
        self.chkClientSex.setChecked(
            forceBool(getPref(preferences, 'chkClientSex', True)) and self.chkClientSex.isEnabled()
        )
        self.chkDatetime.setChecked(
            forceBool(getPref(preferences, 'chkDatetime', True)) and self.chkDatetime.isEnabled()
        )
        self.chkLabel.setChecked(
            forceBool(getPref(preferences, 'chkLabel', True)) and self.chkLabel.isEnabled()
        )
        self.chkNotes.setChecked(
            forceBool(getPref(preferences, 'chkNotes', True)) and self.chkNotes.isEnabled()
        )
        self.chkRowNumber.setChecked(
            forceBool(getPref(preferences, 'chkRowNumber', True)) and self.chkRowNumber.isEnabled()
        )
        self.chkSetPerson.setChecked(
            forceBool(getPref(preferences, 'chkSetPerson', True)) and self.chkSetPerson.isEnabled()
        )

        CDialogBase.loadPreferences(self, preferences)

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.chkRowNumber.setChecked(params.get('00', self.chkRowNumber.isEnabled()))
        self.chkDatetime.setChecked(params.get('01', self.chkDatetime.isEnabled()))
        self.chkClientName.setChecked(params.get('02', self.chkClientName.isEnabled()))
        self.chkClientSex.setChecked(params.get('03', self.chkClientSex.isEnabled()))
        self.chkClientBirthday.setChecked(params.get('04', self.chkClientBirthday.isEnabled()))
        self.chkActionType.setChecked(params.get('05', self.chkActionType.isEnabled()))
        self.chkSetPerson.setChecked(params.get('06', self.chkSetPerson.isEnabled()))
        self.chkLabel.setChecked(params.get('07', self.chkLabel.isEnabled()))
        self.chkNotes.setChecked(params.get('08', self.chkNotes.isEnabled()))
        self.chkBarCode.setChecked(params.get('09', self.chkBarCode.isEnabled()))

    def params(self):
        return {
            '00': self.chkRowNumber.isChecked(),
            '01': self.chkDatetime.isChecked(),
            '02': self.chkClientName.isChecked(),
            '03': self.chkClientSex.isChecked(),
            '04': self.chkClientBirthday.isChecked(),
            '05': self.chkActionType.isChecked(),
            '06': self.chkSetPerson.isChecked(),
            '07': self.chkLabel.isChecked(),
            '08': self.chkNotes.isChecked(),
            '09': self.chkBarCode.isChecked()
        }

    def getReportColumns(self):
        return {
            '00': ('5?', [u'№'], CReportBase.AlignRight),
            '01': ('10?', [u'Дата и время'], CReportBase.AlignLeft),
            '02': ('20?', [u'Ф.И.О.,\n дата рождения, адрес'], CReportBase.AlignLeft),
            '03': ('5?', [u'Пол'], CReportBase.AlignLeft),
            '04': ('10?', [u'Дата рождения'], CReportBase.AlignLeft),
            '05': ('30?', [u'Тип действия'], CReportBase.AlignLeft),
            '06': ('20?', [u'Назначил, дата'], CReportBase.AlignLeft),
            '07': ('10?', [u'Отметка'], CReportBase.AlignLeft),
            '08': ('10?', [u'Примечание'], CReportBase.AlignLeft),
            '09': ('5?', [u'Штрих-код'], CReportBase.AlignLeft),
        }

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        def checkSelectedColumnsCount():
            columnsCount = 0
            params = self.params()
            for x in self.params():
                if params[x]:
                    columnsCount += 1
            return columnsCount >= 2

        buttonCode = self.buttonBox.standardButton(button)
        if buttonCode == QtGui.QDialogButtonBox.Ok:
            if checkSelectedColumnsCount():
                self.accept()
            else:
                QtGui.QMessageBox.warning(self, u'Ошибка', u'Выберете минимум 2 колонки для отчета.')
        else:
            self.reject()


def main():
    import sys
    from s11main import CS11mainApp
    from library.database import connectDataBaseByInfo

    QtGui.qApp = CS11mainApp(sys.argv, False, 'S11App.ini', False)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName(u'utf8'))

    connectionInfo = {
        'driverName': 'mysql',
        'host': 'pacs',
        'port': 3306,
        'database': 's11vm',
        'user': 'dbuser',
        'password': 'dbpassword',
        'connectionName': 'vista-med',
        'compressData': True,
        'afterConnectFunc': None
    }
    QtGui.qApp.db = connectDataBaseByInfo(connectionInfo)

    w = CJobsOperatingReportSetupDialog(None)
    w.exec_()


if __name__ == '__main__':
    main()
