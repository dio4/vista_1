# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


class CException(Exception):
    def __str__(self):
        if isinstance(self.message, unicode):
            return self.message.encode('utf8')
        else:
            return self.message

    def __unicode__(self):
        if isinstance(self.message, unicode):
            return self.message
        else:
            return super(Exception, self).__unicode__()


class CRarException(CException):
    def __init__(self, message):
        super(CRarException, self).__init__(message)
        self._windowTitle = u"Ошибка при архивации"

    def __str__(self):
        return self._message

    def __unicode__(self):
        return self._message

    def getWindowTitle(self):
        return self._windowTitle


class CSoapException(CException):
    def __init__(self, message):
        CException.__init__(self, message)


class CDbfImportException(CException):
    def __init__(self, message=''):
        CException.__init__(self, message)


class CSynchronizeAttachException(CException):
    def __init__(self, message):
        CException.__init__(self, message)
        self.umessage = message

    def __str__(self):
        return self.umessage

    def __unicode__(self):
        return self.umessage


class CDatabaseException(CException):
    """
       Root of all database exceptions
    """
    def __init__(self, message, sqlError=None):
        if sqlError:
            message = message + '\n' + unicode(sqlError.driverText()) + '\n' + unicode(sqlError.databaseText())
        CException.__init__(self, message)
        self.sqlError = sqlError
