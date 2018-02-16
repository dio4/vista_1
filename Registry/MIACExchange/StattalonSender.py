# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


"""
class sending stattalons
"""

import os.path
import gzip
import StringIO
from ZSI.schema         import GED

from PyQt4              import QtCore

from FileService_client import FileServiceLocator, UploadFileData
from FileService_types  import empuri_org


class CMIACStattalonSender(object):
    def __init__(self, tmpDir, compress):
        self.tmpDir = tmpDir
        self.compress = compress
        currentDateTime = QtCore.QDateTime.currentDateTime()
        self.fileName = 'Stattalon (Created_%s).xml' % currentDateTime.toString('yyyyMMdd-hhmm')
        if compress:
            self.storage = StringIO.StringIO()
            self.stream = gzip.GzipFile(str(self.fileName), 'wt', 9, self.storage)
        else:
            self.storage = StringIO.StringIO()
            self.stream = self.storage
        self.writePrefix()


    def close(self):
        self.writeSuffix()
        if self.storage != self.stream:
            self.stream.close()


    def writePrefix(self):
        self.stream.write(
#'''<?xml version="1.0" standalone="yes" encoding="utf-8"?>
# 1) utf-8 - по умолчанию (т.к. BOM пустой),
# 2) есть жалоба на явное указание
'''<?xml version="1.0" standalone="yes"?>
<NewDataSet>
  <xs:schema id="NewDataSet" xmlns="" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata">
    <xs:element name="NewDataSet" msdata:IsDataSet="true" msdata:MainDataTable="Stattalon" msdata:UseCurrentLocale="true">
      <xs:complexType>
        <xs:choice minOccurs="0" maxOccurs="unbounded">
          <xs:element name="Stattalon">
            <xs:complexType>
              <xs:sequence>
                <xs:element name="SURNAME" type="xs:string" minOccurs="0" />
                <xs:element name="NAME1" type="xs:string" minOccurs="0" />
                <xs:element name="NAME2" type="xs:string" minOccurs="0" />
                <xs:element name="BIRTHDAY" type="xs:dateTime" minOccurs="0" />
                <xs:element name="SEX" type="xs:string" minOccurs="0" />
                <xs:element name="ORDER" type="xs:string" minOccurs="0" />
                <xs:element name="POLIS_S" type="xs:string" minOccurs="0" />
                <xs:element name="POLIS_N" type="xs:string" minOccurs="0" />
                <xs:element name="POLIS_W" type="xs:string" minOccurs="0" />
                <xs:element name="PAYER" type="xs:string" minOccurs="0" />
                <xs:element name="STREET" type="xs:string" minOccurs="0" />
                <xs:element name="STREETYPE" type="xs:string" minOccurs="0" />
                <xs:element name="AREA" type="xs:string" minOccurs="0" />
                <xs:element name="HOUSE" type="xs:string" minOccurs="0" />
                <xs:element name="KORP" type="xs:string" minOccurs="0" />
                <xs:element name="FLAT" type="xs:string" minOccurs="0" />
                <xs:element name="PROFILE" type="xs:string" minOccurs="0" />
                <xs:element name="PROFILENET" type="xs:string" minOccurs="0" />
                <xs:element name="DATEIN" type="xs:dateTime" minOccurs="0" />
                <xs:element name="DATEOUT" type="xs:dateTime" minOccurs="0" />
                <xs:element name="AMOUNT" type="xs:double" minOccurs="0" />
                <xs:element name="DIAGNOSIS" type="xs:string" minOccurs="0" />
                <xs:element name="SEND" type="xs:boolean" minOccurs="0" />
                <xs:element name="ERROR" type="xs:string" minOccurs="0" />
                <xs:element name="TYPEDOC" type="xs:string" minOccurs="0" />
                <xs:element name="SER1" type="xs:string" minOccurs="0" />
                <xs:element name="SER2" type="xs:string" minOccurs="0" />
                <xs:element name="NPASP" type="xs:string" minOccurs="0" />
                <xs:element name="LONGADDR" type="xs:string" minOccurs="0" />
                <xs:element name="ACC_ID" type="xs:double" minOccurs="0" />
                <xs:element name="ACCITEM_ID" type="xs:double" minOccurs="0" />
                <xs:element name="CLIENT_ID" type="xs:double" minOccurs="0" />
                <xs:element name="SNILS" type="xs:string" minOccurs="0" />
                <xs:element name="PRVD" type="xs:double" minOccurs="0" />
                <xs:element name="Q_RES" type="xs:double" minOccurs="0" />
                <xs:element name="PRIM" type="xs:string" minOccurs="0" />
              </xs:sequence>
            </xs:complexType>
          </xs:element>
        </xs:choice>
      </xs:complexType>
    </xs:element>
  </xs:schema>
'''
        )


    def writeRecord(self, dbfRecord):
        self.stream.write('  <Stattalon>\n')
        for i, fieldName in enumerate(dbfRecord.dbf.fieldNames):
            self.stream.write('    <%s>%s</%s>\n' % (fieldName, unicode(dbfRecord[i]).encode('utf-8'), fieldName))
        self.stream.write('  </Stattalon>\n')


    def writeSuffix(self):
        self.stream.write('</NewDataSet>\n')


    def send(self, address, postBoxName):
        # get a port proxy instance

        loc = FileServiceLocator()
        port = loc.getBasicHttpBinding_IFileService(address)

        # create a new request
        fd = UploadFileData()
        fd.File = self.storage.getvalue()
        open(os.path.join(self.tmpDir, self.fileName), 'wb').write(fd.File)

        # prepare headers
        tns = empuri_org.targetNamespace
        compressed= GED(tns, 'Compressed').pyclass(self.compress)
        fileName  = GED(tns, 'FileName').pyclass(self.fileName)
        postBox   = GED(tns, 'PostBoxName').pyclass(postBoxName)
        signed    = GED(tns, 'Signed').pyclass(False)

        # call the remote method
        port.FileUpload(fd, (compressed, fileName, postBox, signed))