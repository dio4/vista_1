#! /usr/bin/env python
# -*- coding: utf-8 -*-


#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
##
## Сообщение протокола ASTM E-1394
##
#############################################################################


from PyQt4.QtCore import *

from HeaderRecord      import CHeaderRecord
from PatientRecord     import CPatientRecord
from OrderRecord       import COrderRecord
from ResultRecord      import CResultRecord
from CommentRecord     import CCommentRecord
from TerminationRecord import CTerminationRecord


class EUnexpectedRecord(Exception):
    def __init__(self, index, string):
        Exception.__init__(self, 'unexpected record #%d %s' % ( index, repr(string)))


class CRecordWithCommentMixin:
    def __init__(self):
        object.__setattr__(self, 'comments', [])

    def newComment(self):
        comment = CCommentRecord()
        self.comments.append(comment)
        comment.seqNo = len(self.comments)
        return comment

    def storeRecords(self, records, delimiters, encoding):
        records.append( self.asString(delimiters, encoding) )
        for i, comment in enumerate(self.comments):
            comment.seqNo = i+1
            records.append( comment.asString(delimiters, encoding) )


    def restoreFromRecords(self, records, i, delimiters, encoding):
        self.setString(records[i], delimiters, encoding)
        i += 1
        while records[i].startswith(CCommentRecord.recordType):
            comment = CCommentRecord()
            comment.setString(records[i], delimiters, encoding)
            self.comments.append(comment)
            i += 1
        return i


class CPatientRecordEx(CPatientRecord, CRecordWithCommentMixin):
    def __init__(self):
        CPatientRecord.__init__(self)
        CRecordWithCommentMixin.__init__(self)
        object.__setattr__(self, 'orders', [])


    def newComment(self):
        comment = CRecordWithCommentMixin.newComment(self)
        comment.code  = 'PC'
        return comment


    def newOrder(self):
        order = COrderRecordEx()
        self.orders.append(order)
        order.seqNo = len(self.orders)
        return order


    def storeRecords(self, records, delimiters, encoding):
        CRecordWithCommentMixin.storeRecords(self, records, delimiters, encoding)
        for i, order in enumerate(self.orders):
            order.seqNo = i+1
            order.storeRecords(records, delimiters, encoding)


    def restoreFromRecords(self, records, i, delimiters, encoding):
        i = CRecordWithCommentMixin.restoreFromRecords(self, records, i, delimiters, encoding)
        while records[i].startswith(COrderRecord.recordType):
            order = COrderRecordEx()
            i = order.restoreFromRecords(records, i, delimiters, encoding)
            self.orders.append(order)
        return i


class COrderRecordEx(COrderRecord, CRecordWithCommentMixin):
    def __init__(self):
        COrderRecord.__init__(self)
        CRecordWithCommentMixin.__init__(self)
        object.__setattr__(self, 'results', [])


    def newComment(self):
        comment = CCommentRecord()
        self.comments.append(comment)
        comment.seqNo = len(self.comments)
        comment.code  = 'RC'
        return comment


    def newResult(self):
        result = CResultRecordEx()
        self.results.append(result)
        result.seqNo = len(self.results)
        return result


    def storeRecords(self, records, delimiters, encoding):
        CRecordWithCommentMixin.storeRecords(self, records, delimiters, encoding)
        for i, result in self.results:
            result.seqNo = i+1
            result.storeRecords(records, delimiters, encoding)


    def restoreFromRecords(self, records, i, delimiters, encoding):
        i = CRecordWithCommentMixin.restoreFromRecords(self, records, i, delimiters, encoding)
        while records[i].startswith(CResultRecord.recordType):
            result = CResultRecordEx()
            i = result.restoreFromRecords(records, i, delimiters, encoding)
            self.results.append(result)
        return i


class CResultRecordEx(CResultRecord, CRecordWithCommentMixin):
    def __init__(self):
        CResultRecord.__init__(self)
        CRecordWithCommentMixin.__init__(self)


    def newComment(self):
        comment = CCommentRecord()
        self.comments.append(comment)
        comment.seqNo = len(self.comments)
        return comment


class CMessage(object):
    def __init__(self):
        self.patients = []


    def newPatient(self):
        patient = CPatientRecordEx()
        self.patients.append(patient)
        patient.seqNo = len(self.patients)
        return patient


    def getRecords(self, delimiters='|\\^&', encoding='utf8'):
        # return records as list of strings
        headerRecord = CHeaderRecord()
        headerRecord.setStdFields()
        result = [ headerRecord.asString(delimiters, encoding) ]
        for i, patient in enumerate(self.patients):
            patient.seqNo = i+1
            patient.storeRecords(result, delimiters, encoding)
        terminationRecord = CTerminationRecord()
        terminationRecord.seqNo = 1
        terminationRecord.code = 'N'
        result.append(terminationRecord.asString(delimiters, encoding))
        return result


    def setRecords(self, records, encoding='utf8'):
        # set records as list of strings
        headerRecord = CHeaderRecord()
        headerRecord.setString(records[0], encoding)
        delimiters = headerRecord.delimiters
        i = 1
        while i<len(records):
            if records[i].startswith(CPatientRecordEx.recordType):
                patient = CPatientRecordEx()
                i = patient.restoreFromRecords(records, i, delimiters, encoding)
                self.patients.append(patient)
            if records[i].startswith(CTerminationRecord.recordType):
                return
            raise EUnexpectedRecord(i, records[i])


if __name__ == '__main__':

    def createMessage():
        m = CMessage()
        p = m.newPatient()
        p.patientId = '3780115'
        p.laboratoryPatientId = '1234567'
        p.firstName = 'firstName'
        p.lastName  = 'lastName'
        p.birthDate = QDate(1990, 12, 31)
        p.sex       = 'M'
        p.age       = 21
        p.ageUnit   = 'years'

        c = p.newComment()
        c.source    = 'L'
        c.text      = 'this is comment to patient'

        o = p.newOrder()
        o.specimenId      =  '12120001'
        o.instrumentSpecimenId = '00000000000000'
        o.assayCode       =  'NA'
        o.assayName       =  'Sodium'
        o.requestDateTime =  QDateTime.currentDateTime()
        o.specimenCollectionDateTime  = QDateTime(2001, 10, 23, 10, 57, 15)
        o.actionCode      =  'N'
        o.specimenDescr   =  'S'
        o.userField1      =  'CHIM'
        o.userField2      =  'AXM'
        o.laboratoryField1=  'Lab1'
        o.laboratoryField2=  '12120'
        o.reportTypes     =  'O'
        o.specimenInstitution='LAB2'
        c = o.newComment()
        c.source    = 'L'
        c.text      = 'this is comment to order'
        records = m.getRecords()
        for record in records:
            print record
        return records


    def parseMessage(records, encoding='utf8'):
        def explore(level, title, obj):
            print '\t'*level, '===', title, '='*20
            for name, descr in sorted(type(obj).structure.iteritems(), key=lambda fd: [fd[1][0]] if isinstance(fd[1][0], int) else list(fd[1][0])):
                print '\t'*level+ name + '\t=',getattr(obj, name)

        m = CMessage()
        m.setRecords(records, encoding)
        for ip, p in enumerate(m.patients):
            explore(0, 'patient #%d'%ip, p)
            for ipc, c in enumerate(p.comments):
                explore(1, 'comment #%d to patient #%d'%(ipc, ip), c)
            for io, o in enumerate(p.orders):
                explore(1, 'order #%d to patient #%d'%(io, ip), o)
                for ioc, oc in enumerate(o.comments):
                    explore(2, 'comment #%d to order #%d to patient #%d'%(ioc, io, ip), oc)
                for ir, r in enumerate(o.results):
                    explore(2, 'result #%d to order #%d to patient #%d'%(ir, io, ip), r)
                    for irc, rc in enumerate(r.comments):
                        explore(3, 'comment #%d to result #%d to order #%d to patient #%d'%(irc, ir, io, ip), rc)


    def loadAndParseMessage(fileName, encoding):
        f = file(fileName)
        records = [ line for line in (line.rstrip('\r\n') for line in f) if line ]
        parseMessage(records, encoding)


    print createMessage()
#    parseMessage(createMessage())
#    loadAndParseMessage('samples/res1.res', 'cp1251')

