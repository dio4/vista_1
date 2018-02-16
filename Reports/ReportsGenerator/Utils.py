# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2013 Vista Software. All rights reserved.
##
#############################################################################

"""
Created on 11.03.2013

@author: atronah
"""

from PyQt4 import QtGui


def firstTextTableFromDocument(document):
    table = None
    if isinstance(document, QtGui.QTextDocument):
        for frame in document.rootFrame().childFrames():
            if isinstance(frame, QtGui.QTextTable):
                return frame
    return table


def setBorderForAllTablesInDocument(document, border):
    childFrames = document.rootFrame().childFrames()
    for frame in childFrames:
        if isinstance(frame, QtGui.QTextTable):
            tableFormat = frame.format()
            tableFormat.setBorder(border)
            frame.setFormat(tableFormat)


def resizeTextTableInDocument(document, rows, columns, tableFormatForNew = QtGui.QTextTableFormat()):
    table = firstTextTableFromDocument(document)
    if table:
        if rows is None:
            rows = table.rows()
        if columns is None:
            columns = table.columns()
        table.resize(rows, columns)
    else:
        if columns == 0 or columns == None:
            columns = 1
        if rows == 0:
            rows = 1
        cursor = QtGui.QTextCursor(document)
        cursor.insertTable(rows, columns, tableFormatForNew)
        