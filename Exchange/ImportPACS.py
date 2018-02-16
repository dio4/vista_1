# coding=utf-8
from PyQt4 import QtGui, QtCore
from subprocess import PIPE, Popen, STDOUT
import sys
from Queue import Queue, Empty
from threading import Thread

from Exchange.Ui_ImportPACS import Ui_ImportPACSDialog
from library.DialogBase import CDialogBase
from library.Utils import forceString, getVal, toVariant


class CImportPACS(CDialogBase, Ui_ImportPACSDialog):
    ON_POSIX = 'posix' in sys.builtin_module_names

    def __init__(self, parent):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(u'Импорт снимков в ПАКС-хранилище')
        self.btnImport.setEnabled(False)
        self.edtFileName.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportPACSFileName', '')))
        self.edtAddress.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportPACSAddress', '')))
        self.edtPort.setText(forceString(getVal(QtGui.qApp.preferences.appPrefs, 'ImportPACSPort', '')))
        self.command = ['dcmsend', '-v', '-aet', 'POL120', '-aec', 'POL120',
                        # '--read-from-dicomdir',
                        '--scan-directories', '--recurse']
        self.btnImport.clicked.connect(self.startImport)

    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    @QtCore.pyqtSlot()
    def on_btnSelectFile_clicked(self):
        fileName = QtGui.QFileDialog().getExistingDirectory(
            self, u'Укажите файл или папку с данными', self.edtFileName.text())
        if fileName != '':
            self.edtFileName.setText(QtCore.QDir.toNativeSeparators(fileName))
            self.btnImport.setEnabled(True)

    @QtCore.pyqtSlot(QtCore.QString)
    def on_edtFileName_textChanged(self, fileName):
        self.btnImport.setEnabled(fileName != '')

    def startImport(self):
        self.btnImport.setEnabled(False)
        fileName = str(self.edtFileName.text())
        address = str(self.edtAddress.text())
        port = str(self.edtPort.text())

        QtGui.qApp.preferences.appPrefs['ImportPACSFileName'] = toVariant(fileName)
        QtGui.qApp.preferences.appPrefs['ImportPACSAddress'] = toVariant(address)
        QtGui.qApp.preferences.appPrefs['ImportPACSPort'] = toVariant(port)

        # self.txtLog.append(subprocess.check_output(self.command + [address, port, fileName]))
        p = Popen(self.command + [address, port, fileName], stdin=PIPE, stdout=PIPE, stderr=STDOUT, bufsize=1, close_fds=self.ON_POSIX, shell=True)
        q = Queue()
        t = Thread(target=self.enqueue_output, args=(p.stdout, q))
        t.daemon = True
        t.start()

        while t.isAlive():
            QtGui.qApp.processEvents()
            try:
                line = q.get_nowait()
            except Empty:
                pass
            else:
                self.txtLog.append(line)

        self.btnImport.setEnabled(True)