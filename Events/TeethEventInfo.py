# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
from PyQt4 import QtGui

from Events.EventInfo      import CEventInfo


STOMAT_TABLE = """<table cellpadding=0 cellspacing=0 width=100%% border="1">
<tr><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
<tr><td><b>8</b></td><td><b>7</b></td><td><b>6</b></td><td><b>5</b></td><td><b>4</b></td><td><b>3</b></td><td><b>2</b></td><td><b>1</b></td><td><b>1</b></td><td><b>2</b></td><td><b>3</b></td><td><b>4</b></td><td><b>5</b></td><td><b>6</b></td><td><b>7</b></td><td><b>8</b></td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
<tr><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td><td bgcolor="%s">%s</td></tr>
</table>"""

PARODENT_TABLE = """<table cellpadding=0 cellspacing=0 width=100%% border="1">
<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
<tr><td><b>8</b></td><td><b>7</b></td><td><b>6</b></td><td><b>5</b></td><td><b>4</b></td><td><b>3</b></td><td><b>2</b></td><td><b>1</b></td><td><b>1</b></td><td><b>2</b></td><td><b>3</b></td><td><b>4</b></td><td><b>5</b></td><td><b>6</b></td><td><b>7</b></td><td><b>8</b></td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
</table>
"""

class CTeethEventInfo(CEventInfo):
    def __init__(self, context, id):
        CEventInfo.__init__(self, context, id)
        self.action_stomat = None
        self.action_parodent = None

    def _load(self):
        db = QtGui.qApp.db
        for act in self.actions:
            if act.flatCode == 'dentitionInspection':
                self.action_stomat = act
            if act.flatCode == 'parodentInsp':
                self.action_parodent = act
        if self.action_stomat is not None and self.action_parodent is not None:
            return True
        else:
            return False
            
    def getStomatTable(self):
        if self.action_stomat is None: self._load()
        colors = ["white", "lightGray", "orange", "cyan", "blue", "green", "darkGreen", "magenta", "yellow", "red"]
        props = ()
        for i in xrange(16):
            status = self.action_stomat[u"Статус.Верхний.%i"%(i+1)].value
            props += (colors[int(status[0]) if len(status) else 0], )
            props += (status[0] if len(status) else status, )
        for i in xrange(16):
            props += (self.action_stomat[u"Подвижность.Верхний.%i"%(i+1)].value, )
        for i in xrange(16):
            props += (self.action_stomat[u"Состояние.Верхний.%i"%(i+1)].value, )
        for i in xrange(16):
            props += (self.action_stomat[u"Состояние.Нижний.%i"%(i+1)].value, )
        for i in xrange(16):
            props += (self.action_stomat[u"Подвижность.Нижний.%i"%(i+1)].value, )
        for i in xrange(16):
            status = self.action_stomat[u"Статус.Нижний.%i"%(i+1)].value
            props += (colors[int(status[0]) if len(status) else 0], )
            props += (status[0] if len(status) else status, )
        return STOMAT_TABLE % props
     
    def getParodentTable(self):
        if self.action_parodent is None: self._load()
        props = ()
        for i in xrange(16):
            props += (self.action_parodent[u"Клиновидный дефект.Верхний.%i"%(i+1)].value, )
            props += (self.action_parodent[u"Рецессия.Верхний.%i"%(i+1)].value, )
            props += (self.action_parodent[u"Подвижность.Верхний.%i"%(i+1)].value, )
            props += (self.action_parodent[u"Глубина кармана.Верхний.%i"%(i+1)].value, )
            props += (self.action_parodent[u"Глубина кармана.Нижний.%i"%(i+1)].value, )
            props += (self.action_parodent[u"Подвижность.Нижний.%i"%(i+1)].value, )
            props += (self.action_parodent[u"Рецессия.Нижний.%i"%(i+1)].value, )
            props += (self.action_parodent[u"Клиновидный дефект.Нижний.%i"%(i+1)].value, )
        return PARODENT_TABLE % props
        
    stomat              = property(lambda self: self.load().getStomatTable())
    parodent            = property(lambda self: self.load().getParodentTable())
    
