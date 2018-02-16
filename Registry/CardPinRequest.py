# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
## Copyright (C) 2012 SAMSON Group. All rights reserved.
##
#############################################################################
##
## Это программа является свободным программным обеспечением.
## Вы можете использовать, распространять и/или модифицировать её согласно
## условиям GNU GPL версии 3 или любой более поздней версии.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils import *

from Ui_CardPinRequesDialog import Ui_CardPinRequestDialog


class CCardPinRequest(QtGui.QDialog, Ui_CardPinRequestDialog):

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.edtPinCode.setValidator(QtGui.QIntValidator(0, 99999999, self))
        self.lblAttempts.setVisible(False)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            event.accept()
            self.accept()
        elif event.key() == QtCore.Qt.Key_Escape:
            event.accept()
            self.reject()
        else:
            QtGui.QDialog.keyPressEvent(self, event)

    def exec_(self, cardNumber=None, begDate=None, endDate=None, passPhase=None, attempts=None):
        if attempts:
            self.edtPinCode.setText('')
            self.lblAttempts.setText(u'Неверный ПИН-код, осталось попыток: %s' % attempts)
            self.lblAttempts.setVisible(True)
        else:
            self.tbCardInfo.setText(
                u'''
                <center>
                    Номер карты:<br>
                    <b>%s</b><br>
                    действительна<br>
                    с <b>%s</b> по <b>%s</b>
                    %s
                </center>
                ''' % (cardNumber, begDate, endDate,
                       '' if not passPhase else u'<br><br>Контрольное приветствие:<br>'
                                                u'<font color="green"><b>%s</b></font>' % passPhase)
            )
        return '' if QtGui.QDialog.exec_(self) == QtGui.QDialog.Rejected else forceString(self.edtPinCode.text())