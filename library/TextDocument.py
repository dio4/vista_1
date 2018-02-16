#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from urllib import unquote_plus

from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from library.pdf417 import pdf417image


class CResourceLoaderMixin:

    def __init__(self):
        self.images = {}


    def setCanvases(self, canvases):
        for key,  val in canvases.iteritems():
            self.images[key] = val.image


    def loadResource(self, type_, url):
        def decode(s):
            return unquote_plus(str(s))

        if type_ == 2 and str(url.scheme()).lower() == 'pdf417':
            #TODO: test with old print templates...
            params = dict([(decode(qi[0]), decode(qi[1])) for qi in url.encodedQueryItems()])
            return pdf417(**params)
        elif type_ == 2 and str(url.scheme()).lower() == 'canvas':
            canvasName = str(url.host())
            result = self.images.get(canvasName, None)
            if not result:
                result = getEmptyImage()
                self.images[canvasName] = result
            return QVariant(result)
        else:
            return QtGui.QTextBrowser.loadResource(self, type_, url)



class CTextDocument(QTextDocument, CResourceLoaderMixin):
    def __init__(self, parent=None):
        QTextDocument.__init__(self, parent)
        CResourceLoaderMixin.__init__(self)




def pdf417(data='', **params):
    try:
        image = pdf417image(data, **params)
        return QVariant(image)
    except:
        return QVariant()


def getEmptyImage():
    image = QImage(16, 16, QImage.Format_RGB32)
    painter = QPainter(image)
    painter.fillRect(0, 0, 16, 16, QBrush(QColor(255, 255, 255)))
    painter.setPen(QPen(QColor(0, 255, 0)))
    painter.drawEllipse(0, 0, 15, 15)
    painter.setPen(QPen(QColor(255, 0, 0)))
    painter.drawLine(0,  0, 15, 15)
    painter.drawLine(0, 15, 15, 0)
    painter.end()
    return image