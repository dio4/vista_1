# -*- coding: utf-8 -*-


from PyQt4 import QtCore, QtGui

from Ui_TNMSPopup import Ui_TNMSPopup


class CTNMSPopup(QtGui.QFrame, Ui_TNMSPopup):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent, QtCore.Qt.Popup)
        self.combo = parent
#        self.setAttribute(QtCore.Qt.WA_WindowPropagation)
#        self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeCombo)
        self.setupUi(self)
        opt = self.comboStyleOption()
        self.setFrameStyle(parent.style().styleHint(QtGui.QStyle.SH_ComboBox_PopupFrameStyle, opt, parent))
        self.setFocusProxy(self.cmbCTumor)

        for combo in [self.cmbCTumor, self.cmbCNodus, self.cmbCMetastasis, self.cmbCM1Localization, self.cmbCSerum,
                      self.cmbCGrade, self.cmbCLymphatic, self.cmbCVein, self.cmbCPerineural, self.cmbCResection,
                      self.cmbCSt,
                      self.cmbPTumor, self.cmbPNodus, self.cmbPMetastasis, self.cmbPM1Localization, self.cmbPSerum,
                      self.cmbPGrade, self.cmbPLymphatic, self.cmbPVein, self.cmbPPerineural, self.cmbPResection,
                      self.cmbPSt,
                      self.cmbRTumor, self.cmbRNodus, self.cmbRMetastasis, self.cmbRM1Localization, self.cmbRSerum,
                      self.cmbRGrade, self.cmbRLymphatic, self.cmbRVein, self.cmbRPerineural, self.cmbRResection,
                      self.cmbRSt,
                      self.cmbYTumor, self.cmbYNodus, self.cmbYMetastasis, self.cmbYM1Localization, self.cmbYSerum,
                      self.cmbYGrade, self.cmbYLymphatic, self.cmbYVein, self.cmbYPerineural, self.cmbYResection,
                      self.cmbYSt,
                      self.cmbYCTumor, self.cmbYCNodus, self.cmbYCMetastasis, self.cmbYCM1Localization, self.cmbYCSerum,
                      self.cmbYCGrade, self.cmbYCLymphatic, self.cmbYCVein, self.cmbYCPerineural, self.cmbYCResection,
                      self.cmbYCSt,
                      self.cmbYPTumor, self.cmbYPNodus, self.cmbYPMetastasis, self.cmbYPM1Localization, self.cmbYPSerum,
                      self.cmbYPGrade, self.cmbYPLymphatic, self.cmbYPVein, self.cmbYPPerineural, self.cmbYPResection,
                      self.cmbYPSt,
                      self.cmbATumor, self.cmbANodus, self.cmbAMetastasis, self.cmbAM1Localization, self.cmbASerum,
                      self.cmbAGrade, self.cmbALymphatic, self.cmbAVein, self.cmbAPerineural, self.cmbAResection,
                      self.cmbASt]:
            combo.installEventFilter(self)
            self.connect(combo, QtCore.SIGNAL('currentIndexChanged(int)'), self.onAnyCurrentIndexChanged)
        self.on_chkShowExtra_clicked(False)
        self.lblPTumor.setVisible(False)
        self.lblPNodus.setVisible(False)
        self.lblPMetastasis.setVisible(False)
        self.lblPSt.setVisible(False)
        self.cmbPTumor.setVisible(False)
        self.cmbPNodus.setVisible(False)
        self.cmbPMetastasis.setVisible(False)
        self.cmbPSt.setVisible(False)

    def changeVisiblePRow(self):
        if self.lblPTumor.isVisible() :
            self.lblPTumor.setVisible(False)
        else:
            self.lblPTumor.setVisible(True)

        if self.lblPNodus.isVisible() :
            self.lblPNodus.setVisible(False)
        else:
            self.lblPNodus.setVisible(True)

        if self.lblPMetastasis.isVisible() :
            self.lblPMetastasis.setVisible(False)
        else:
            self.lblPMetastasis.setVisible(True)

        if self.lblPSt.isVisible() :
            self.lblPSt.setVisible(False)
        else:
            self.lblPSt.setVisible(True)

        if self.cmbPTumor.isVisible() :
            self.cmbPTumor.setVisible(False)
        else:
            self.cmbPTumor.setVisible(True)

        if self.cmbPNodus.isVisible() :
            self.cmbPNodus.setVisible(False)
        else:
            self.cmbPNodus.setVisible(True)

        if self.cmbPMetastasis.isVisible() :
            self.cmbPMetastasis.setVisible(False)
        else:
            self.cmbPMetastasis.setVisible(True)

        if self.cmbPSt.isVisible() :
            self.cmbPSt.setVisible(False)
        else:
            self.cmbPSt.setVisible(True)


    def comboStyleOption(self):
        opt = QtGui.QStyleOptionComboBox()
        opt.initFrom(self.combo)
        opt.subControls = QtGui.QStyle.SC_All
        opt.activeSubControls = QtGui.QStyle.SC_None
        opt.editable = False # self.combo.isEditable()
        return opt


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if key in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Escape):
                self.combo.hidePopup()
                return True
#            elif key == QtCore.Qt.Key_F4 and :
        return QtGui.QFrame.eventFilter(self, obj, event)


    def setValue(self, d):
        def setComboValue(combo, value):
            blocked = combo.blockSignals(True)
            try:
                for i in xrange(combo.count()):
                    if unicode(combo.itemText(i)) == value:
                        combo.setCurrentIndex(i)
                        return
                combo.setCurrentIndex(0)
            finally:
                combo.blockSignals(blocked)

        setComboValue(self.cmbCTumor, d.get('cT', '--'))
        setComboValue(self.cmbCNodus, d.get('cN', '--'))
        setComboValue(self.cmbCMetastasis, d.get('cM', '--'))
        setComboValue(self.cmbCM1Localization, d.get('cM1Loc', '--'))
        setComboValue(self.cmbCSerum, d.get('cS', '--'))
        setComboValue(self.cmbCGrade, d.get('cG', '--'))
        setComboValue(self.cmbCLymphatic, d.get('cL', '--'))
        setComboValue(self.cmbCVein, d.get('cV', '--'))
        setComboValue(self.cmbCPerineural, d.get('cPn', '--'))
        setComboValue(self.cmbCResection, d.get('cR', '--'))
        setComboValue(self.cmbCSt, d.get('cSt', '--'))

        setComboValue(self.cmbPTumor, d.get('pT', '--'))
        setComboValue(self.cmbPNodus, d.get('pN', '--'))
        setComboValue(self.cmbPMetastasis, d.get('pM', '--'))
        setComboValue(self.cmbPM1Localization, d.get('pM1Loc', '--'))
        setComboValue(self.cmbPSerum, d.get('pS', '--'))
        setComboValue(self.cmbPGrade, d.get('pG', '--'))
        setComboValue(self.cmbPLymphatic, d.get('pL', '--'))
        setComboValue(self.cmbPVein, d.get('pV', '--'))
        setComboValue(self.cmbPPerineural, d.get('pPn', '--'))
        setComboValue(self.cmbPResection, d.get('pR', '--'))
        setComboValue(self.cmbPSt, d.get('pSt', '--'))

        setComboValue(self.cmbRTumor, d.get('rT', '--'))
        setComboValue(self.cmbRNodus, d.get('rN', '--'))
        setComboValue(self.cmbRMetastasis, d.get('rM', '--'))
        setComboValue(self.cmbRM1Localization, d.get('rM1Loc', '--'))
        setComboValue(self.cmbRSerum, d.get('rS', '--'))
        setComboValue(self.cmbRGrade, d.get('rG', '--'))
        setComboValue(self.cmbRLymphatic, d.get('rL', '--'))
        setComboValue(self.cmbRVein, d.get('rV', '--'))
        setComboValue(self.cmbRPerineural, d.get('rPn', '--'))
        setComboValue(self.cmbRResection, d.get('rR', '--'))
        setComboValue(self.cmbRSt, d.get('rSt', '--'))

        setComboValue(self.cmbYTumor, d.get('yT', '--'))
        setComboValue(self.cmbYNodus, d.get('yN', '--'))
        setComboValue(self.cmbYMetastasis, d.get('yM', '--'))
        setComboValue(self.cmbYM1Localization, d.get('yM1Loc', '--'))
        setComboValue(self.cmbYSerum, d.get('yS', '--'))
        setComboValue(self.cmbYGrade, d.get('yG', '--'))
        setComboValue(self.cmbYLymphatic, d.get('yL', '--'))
        setComboValue(self.cmbYVein, d.get('yV', '--'))
        setComboValue(self.cmbYPerineural, d.get('yPn', '--'))
        setComboValue(self.cmbYResection, d.get('yR', '--'))
        setComboValue(self.cmbYSt, d.get('ySt', '--'))

        setComboValue(self.cmbYCTumor, d.get('ycT', '--'))
        setComboValue(self.cmbYCNodus, d.get('ycN', '--'))
        setComboValue(self.cmbYCMetastasis, d.get('ycM', '--'))
        setComboValue(self.cmbYCM1Localization, d.get('ycM1Loc', '--'))
        setComboValue(self.cmbYCSerum, d.get('ycS', '--'))
        setComboValue(self.cmbYCGrade, d.get('ycG', '--'))
        setComboValue(self.cmbYCLymphatic, d.get('ycL', '--'))
        setComboValue(self.cmbYCVein, d.get('ycV', '--'))
        setComboValue(self.cmbYCPerineural, d.get('ycPn', '--'))
        setComboValue(self.cmbYCResection, d.get('ycR', '--'))
        setComboValue(self.cmbYCSt, d.get('ycSt', '--'))

        setComboValue(self.cmbYPTumor, d.get('ypT', '--'))
        setComboValue(self.cmbYPNodus, d.get('ypN', '--'))
        setComboValue(self.cmbYPMetastasis, d.get('ypM', '--'))
        setComboValue(self.cmbYPM1Localization, d.get('ypM1Loc', '--'))
        setComboValue(self.cmbYPSerum, d.get('ypS', '--'))
        setComboValue(self.cmbYPGrade, d.get('ypG', '--'))
        setComboValue(self.cmbYPLymphatic, d.get('ypL', '--'))
        setComboValue(self.cmbYPVein, d.get('ypV', '--'))
        setComboValue(self.cmbYPPerineural, d.get('ypPn', '--'))
        setComboValue(self.cmbYPResection, d.get('ypR', '--'))
        setComboValue(self.cmbYPSt, d.get('ypSt', '--'))

        setComboValue(self.cmbATumor, d.get('aT', '--'))
        setComboValue(self.cmbANodus, d.get('aN', '--'))
        setComboValue(self.cmbAMetastasis, d.get('aM', '--'))
        setComboValue(self.cmbAM1Localization, d.get('aM1Loc', '--'))
        setComboValue(self.cmbASerum, d.get('aS', '--'))
        setComboValue(self.cmbAGrade, d.get('aG', '--'))
        setComboValue(self.cmbALymphatic, d.get('aL', '--'))
        setComboValue(self.cmbAVein, d.get('aV', '--'))
        setComboValue(self.cmbAPerineural, d.get('aPn', '--'))
        setComboValue(self.cmbAResection, d.get('aR', '--'))
        setComboValue(self.cmbASt, d.get('aSt', '--'))



    def getValue(self):
        return {
            'cT': unicode(self.cmbCTumor.currentText()),
            'cN': unicode(self.cmbCNodus.currentText()),
            'cM': unicode(self.cmbCMetastasis.currentText()),
            'cM1Loc': unicode(self.cmbCM1Localization.currentText()),
            'cS': unicode(self.cmbCSerum.currentText()),
            'cG': unicode(self.cmbCGrade.currentText()),
            'cL': unicode(self.cmbCLymphatic.currentText()),
            'cV': unicode(self.cmbCVein.currentText()),
            'cPn': unicode(self.cmbCPerineural.currentText()),
            'cR': unicode(self.cmbCResection.currentText()),
            'cSt': unicode(self.cmbCSt.currentText()),

            'pT': unicode(self.cmbPTumor.currentText()),
            'pN': unicode(self.cmbPNodus.currentText()),
            'pM': unicode(self.cmbPMetastasis.currentText()),
            'pM1Loc': unicode(self.cmbPM1Localization.currentText()),
            'pS': unicode(self.cmbPSerum.currentText()),
            'pG': unicode(self.cmbPGrade.currentText()),
            'pL': unicode(self.cmbPLymphatic.currentText()),
            'pV': unicode(self.cmbPVein.currentText()),
            'pPn': unicode(self.cmbPPerineural.currentText()),
            'pR': unicode(self.cmbPResection.currentText()),
            'pSt': unicode(self.cmbPSt.currentText()),

            'rT': unicode(self.cmbRTumor.currentText()),
            'rN': unicode(self.cmbRNodus.currentText()),
            'rM': unicode(self.cmbRMetastasis.currentText()),
            'rM1Loc': unicode(self.cmbRM1Localization.currentText()),
            'rS': unicode(self.cmbRSerum.currentText()),
            'rG': unicode(self.cmbRGrade.currentText()),
            'rL': unicode(self.cmbRLymphatic.currentText()),
            'rV': unicode(self.cmbRVein.currentText()),
            'rPn': unicode(self.cmbRPerineural.currentText()),
            'rR': unicode(self.cmbRResection.currentText()),
            'rSt': unicode(self.cmbRSt.currentText()),

            'yT': unicode(self.cmbYTumor.currentText()),
            'yN': unicode(self.cmbYNodus.currentText()),
            'yM': unicode(self.cmbYMetastasis.currentText()),
            'yM1Loc': unicode(self.cmbYM1Localization.currentText()),
            'yS': unicode(self.cmbYSerum.currentText()),
            'yG': unicode(self.cmbYGrade.currentText()),
            'yL': unicode(self.cmbYLymphatic.currentText()),
            'yV': unicode(self.cmbYVein.currentText()),
            'yPn': unicode(self.cmbYPerineural.currentText()),
            'yR': unicode(self.cmbYResection.currentText()),
            'ySt': unicode(self.cmbYSt.currentText()),

            'ycT': unicode(self.cmbYCTumor.currentText()),
            'ycN': unicode(self.cmbYCNodus.currentText()),
            'ycM': unicode(self.cmbYCMetastasis.currentText()),
            'ycM1Loc': unicode(self.cmbYCM1Localization.currentText()),
            'ycS': unicode(self.cmbYCSerum.currentText()),
            'ycG': unicode(self.cmbYCGrade.currentText()),
            'ycL': unicode(self.cmbYCLymphatic.currentText()),
            'ycV': unicode(self.cmbYCVein.currentText()),
            'ycPn': unicode(self.cmbYCPerineural.currentText()),
            'ycR': unicode(self.cmbYCResection.currentText()),
            'ycSt': unicode(self.cmbYCSt.currentText()),

            'ypT': unicode(self.cmbYPTumor.currentText()),
            'ypN': unicode(self.cmbYPNodus.currentText()),
            'ypM': unicode(self.cmbYPMetastasis.currentText()),
            'ypM1Loc': unicode(self.cmbYPM1Localization.currentText()),
            'ypS': unicode(self.cmbYPSerum.currentText()),
            'ypG': unicode(self.cmbYPGrade.currentText()),
            'ypL': unicode(self.cmbYPLymphatic.currentText()),
            'ypV': unicode(self.cmbYPVein.currentText()),
            'ypPn': unicode(self.cmbYPPerineural.currentText()),
            'ypR': unicode(self.cmbYPResection.currentText()),
            'ypSt': unicode(self.cmbYPSt.currentText()),

            'aT': unicode(self.cmbATumor.currentText()),
            'aN': unicode(self.cmbANodus.currentText()),
            'aM': unicode(self.cmbAMetastasis.currentText()),
            'aM1Loc': unicode(self.cmbAM1Localization.currentText()),
            'aS': unicode(self.cmbASerum.currentText()),
            'aG': unicode(self.cmbAGrade.currentText()),
            'aL': unicode(self.cmbALymphatic.currentText()),
            'aV': unicode(self.cmbAVein.currentText()),
            'aPn': unicode(self.cmbAPerineural.currentText()),
            'aR': unicode(self.cmbAResection.currentText()),
            'aSt': unicode(self.cmbASt.currentText())

        }

#    @QtCore.pyqtSlot(int)
    def onAnyCurrentIndexChanged(self, index):
        self.combo.updateValueFromPopup()

    @QtCore.pyqtSlot(bool)
    def on_chkShowExtra_clicked(self, checked):
        self.lblCSerum.setVisible(checked)
        self.lblCGrade.setVisible(checked)
        self.lblCLymphatic.setVisible(checked)
        self.lblCVein.setVisible(checked)
        self.lblCPerineural.setVisible(checked)
        self.lblCResection.setVisible(checked)

        self.cmbCM1Localization.setVisible(checked)
        self.cmbCSerum.setVisible(checked)
        self.cmbCGrade.setVisible(checked)
        self.cmbCLymphatic.setVisible(checked)
        self.cmbCVein.setVisible(checked)
        self.cmbCPerineural.setVisible(checked)
        self.cmbCResection.setVisible(checked)

        self.changeVisiblePRow()

        self.lblPSerum.setVisible(checked)
        self.lblPGrade.setVisible(checked)
        self.lblPLymphatic.setVisible(checked)
        self.lblPVein.setVisible(checked)
        self.lblPPerineural.setVisible(checked)
        self.lblPResection.setVisible(checked)

        self.cmbPM1Localization.setVisible(checked)
        self.cmbPSerum.setVisible(checked)
        self.cmbPGrade.setVisible(checked)
        self.cmbPLymphatic.setVisible(checked)
        self.cmbPVein.setVisible(checked)
        self.cmbPPerineural.setVisible(checked)
        self.cmbPResection.setVisible(checked)

        self.lblRTumor.setVisible(checked)
        self.lblRNodus.setVisible(checked)
        self.lblRMetastasis.setVisible(checked)
        self.lblRSerum.setVisible(checked)
        self.lblRGrade.setVisible(checked)
        self.lblRLymphatic.setVisible(checked)
        self.lblRVein.setVisible(checked)
        self.lblRPerineural.setVisible(checked)
        self.lblRResection.setVisible(checked)
        self.lblRSt.setVisible(checked)

        self.cmbRTumor.setVisible(checked)
        self.cmbRNodus.setVisible(checked)
        self.cmbRMetastasis.setVisible(checked)
        self.cmbRM1Localization.setVisible(checked)
        self.cmbRSerum.setVisible(checked)
        self.cmbRGrade.setVisible(checked)
        self.cmbRLymphatic.setVisible(checked)
        self.cmbRVein.setVisible(checked)
        self.cmbRPerineural.setVisible(checked)
        self.cmbRResection.setVisible(checked)
        self.cmbRSt.setVisible(checked)

        self.lblYTumor.setVisible(checked)
        self.lblYNodus.setVisible(checked)
        self.lblYMetastasis.setVisible(checked)
        self.lblYSerum.setVisible(checked)
        self.lblYGrade.setVisible(checked)
        self.lblYLymphatic.setVisible(checked)
        self.lblYVein.setVisible(checked)
        self.lblYPerineural.setVisible(checked)
        self.lblYResection.setVisible(checked)
        self.lblYSt.setVisible(checked)

        self.cmbYTumor.setVisible(checked)
        self.cmbYNodus.setVisible(checked)
        self.cmbYMetastasis.setVisible(checked)
        self.cmbYM1Localization.setVisible(checked)
        self.cmbYSerum.setVisible(checked)
        self.cmbYGrade.setVisible(checked)
        self.cmbYLymphatic.setVisible(checked)
        self.cmbYVein.setVisible(checked)
        self.cmbYPerineural.setVisible(checked)
        self.cmbYResection.setVisible(checked)
        self.cmbYSt.setVisible(checked)

        self.lblYCTumor.setVisible(checked)
        self.lblYCNodus.setVisible(checked)
        self.lblYCMetastasis.setVisible(checked)
        self.lblYCSerum.setVisible(checked)
        self.lblYCGrade.setVisible(checked)
        self.lblYCLymphatic.setVisible(checked)
        self.lblYCVein.setVisible(checked)
        self.lblYCPerineural.setVisible(checked)
        self.lblYCResection.setVisible(checked)
        self.lblYCSt.setVisible(checked)

        self.cmbYCTumor.setVisible(checked)
        self.cmbYCNodus.setVisible(checked)
        self.cmbYCMetastasis.setVisible(checked)
        self.cmbYCM1Localization.setVisible(checked)
        self.cmbYCSerum.setVisible(checked)
        self.cmbYCGrade.setVisible(checked)
        self.cmbYCLymphatic.setVisible(checked)
        self.cmbYCVein.setVisible(checked)
        self.cmbYCPerineural.setVisible(checked)
        self.cmbYCResection.setVisible(checked)
        self.cmbYCSt.setVisible(checked)

        self.lblYPTumor.setVisible(checked)
        self.lblYPNodus.setVisible(checked)
        self.lblYPMetastasis.setVisible(checked)
        self.lblYPSerum.setVisible(checked)
        self.lblYPGrade.setVisible(checked)
        self.lblYPLymphatic.setVisible(checked)
        self.lblYPVein.setVisible(checked)
        self.lblYPPerineural.setVisible(checked)
        self.lblYPResection.setVisible(checked)
        self.lblYPSt.setVisible(checked)

        self.cmbYPTumor.setVisible(checked)
        self.cmbYPNodus.setVisible(checked)
        self.cmbYPMetastasis.setVisible(checked)
        self.cmbYPM1Localization.setVisible(checked)
        self.cmbYPSerum.setVisible(checked)
        self.cmbYPGrade.setVisible(checked)
        self.cmbYPLymphatic.setVisible(checked)
        self.cmbYPVein.setVisible(checked)
        self.cmbYPPerineural.setVisible(checked)
        self.cmbYPResection.setVisible(checked)
        self.cmbYPSt.setVisible(checked)

        self.lblATumor.setVisible(checked)
        self.lblANodus.setVisible(checked)
        self.lblAMetastasis.setVisible(checked)
        self.lblASerum.setVisible(checked)
        self.lblAGrade.setVisible(checked)
        self.lblALymphatic.setVisible(checked)
        self.lblAVein.setVisible(checked)
        self.lblAPerineural.setVisible(checked)
        self.lblAResection.setVisible(checked)
        self.lblASt.setVisible(checked)

        self.cmbATumor.setVisible(checked)
        self.cmbANodus.setVisible(checked)
        self.cmbAMetastasis.setVisible(checked)
        self.cmbAM1Localization.setVisible(checked)
        self.cmbASerum.setVisible(checked)
        self.cmbAGrade.setVisible(checked)
        self.cmbALymphatic.setVisible(checked)
        self.cmbAVein.setVisible(checked)
        self.cmbAPerineural.setVisible(checked)
        self.cmbAResection.setVisible(checked)
        self.cmbASt.setVisible(checked)

        self.showLocalization()
        self.adjustSize()

    def showLocalization(self):
        self.on_cmbCMetastasis_currentIndexChanged()
        self.on_cmbPMetastasis_currentIndexChanged()
        self.on_cmbRMetastasis_currentIndexChanged()
        self.on_cmbYMetastasis_currentIndexChanged()
        self.on_cmbYCMetastasis_currentIndexChanged()
        self.on_cmbYPMetastasis_currentIndexChanged()
        self.on_cmbAMetastasis_currentIndexChanged()

    def on_cmbCMetastasis_currentIndexChanged(self):
        self.cmbCM1Localization.setVisible(self.cmbCMetastasis.currentIndex() == 2 and self.cmbCMetastasis.isVisible())

    def on_cmbPMetastasis_currentIndexChanged(self):
        self.cmbPM1Localization.setVisible(self.cmbPMetastasis.currentIndex() == 2 and self.cmbPMetastasis.isVisible())

    def on_cmbRMetastasis_currentIndexChanged(self):
        self.cmbRM1Localization.setVisible(self.cmbRMetastasis.currentIndex() == 2 and self.cmbRMetastasis.isVisible())

    def on_cmbYMetastasis_currentIndexChanged(self):
        self.cmbYM1Localization.setVisible(self.cmbYMetastasis.currentIndex() == 2 and self.cmbYMetastasis.isVisible())

    def on_cmbYCMetastasis_currentIndexChanged(self):
        self.cmbYCM1Localization.setVisible(self.cmbYCMetastasis.currentIndex() == 2 and self.cmbYCMetastasis.isVisible())

    def on_cmbYPMetastasis_currentIndexChanged(self):
        self.cmbYPM1Localization.setVisible(self.cmbYPMetastasis.currentIndex() == 2 and self.cmbYPMetastasis.isVisible())

    def on_cmbAMetastasis_currentIndexChanged(self):
        self.cmbAM1Localization.setVisible(self.cmbAMetastasis.currentIndex() == 2 and self.cmbAMetastasis.isVisible())
