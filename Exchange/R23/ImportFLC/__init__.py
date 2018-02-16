# -*- coding: utf-8 -*-

from Exchange.R23.ImportFLC.ImportFLCR23 import CImportFLC


def ImportFLC(widget):
    dlg = CImportFLC(widget)
    dlg.exec_()
