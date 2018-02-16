# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
##############################################################################
import re
import zipfile
import xml.dom.minidom

class CXLSXReader:
    rows = []

    def _nodeText(self, node):
        return "".join(t.nodeValue for t in node.childNodes if t.nodeType == t.TEXT_NODE)

    def _get_col_num(self, col):
        strpart = col.attributes['r'].value
        colnum = re.sub('[^A-Z]', '', strpart.upper().strip())

        c = 0
        for char in colnum:
            c += ord(char)

        c -= (65) # ASCII to number
        return c

    def __init__(self, filename, progressBar=None):
        if progressBar is not None:
            progressBar.reset()
            progressBar.setFormat('%p%')
            progressBar.setValue(0)
        shared_strings = []
        self.rows = []
        filename = unicode(filename)
        file = zipfile.ZipFile(filename)

        share = xml.dom.minidom.parseString(file.read('xl/sharedStrings.xml'))
        j = share.getElementsByTagName("t")

        for node in j:
            shared_strings.append(self._nodeText(node))

        sheet = xml.dom.minidom.parseString(file.read('xl/worksheets/sheet1.xml'))
        sheetrows = sheet.getElementsByTagName("row")
        if progressBar is not None:
            progressBar.setMaximum(len(sheetrows)-1)
        for index, row in enumerate(sheetrows):
            if progressBar is not None:
                progressBar.setValue(index)
            cols = row.getElementsByTagName("c")
            largest_col_num = 0
            for col in cols:
                colnum = self._get_col_num(col)
                if colnum > largest_col_num:
                    largest_col_num = colnum

            thiscol = ['']*(largest_col_num + 1)

            for col in cols:
                value = ''
                try:
                    value = self._nodeText(col.getElementsByTagName('v')[0])
                except IndexError:
                    continue

                colnum = self._get_col_num(col) # ASCII to number
                try:
                    if col.attributes['t'].value == 's':
                        thiscol[colnum] = shared_strings[int(value)].replace('\n', ' ').strip()
                    else:
                        thiscol[colnum] = value.replace('\n', ' ').strip()
                except KeyError:
                    thiscol[colnum] = value.replace('\n', ' ').strip()
                except AttributeError:
                    pass
                except IndexError:
                    pass
            self.rows.append(thiscol)
        file.close()


    def __getitem__(self, i):
        return self.rows[i]
