# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


"""
class sending DD Monitoring
"""

import os.path
import gzip
import StringIO

from PyQt4 import QtCore

from FileService_client import FileServiceLocator, UploadFileData
from FileService_types import *

from Registry.MIACExchange.DDMonitoring.XMLSchema_xsd_types import *
from ZSI.wstools.Utility import MessageInterface, ElementProxy




class CMIACDDMonitoringSender(object):
    def __init__(self, tmpDir, compress):
        self.tmpDir = tmpDir
        self.compress = compress
        currentDateTime = QtCore.QDateTime.currentDateTime()
        self.fileName = 'DDMonitoring (Created_%s).xml' % currentDateTime.toString('yyyyMMdd-hhmm')
        if compress:
            self.storage = StringIO.StringIO()
            self.stream = gzip.GzipFile(str(self.fileName), 'wt', 9, self.storage)
        else:
            self.storage = StringIO.StringIO()
            self.stream = self.storage
#        self.writePrefix()




#    def writeRecord(self, dbfRecord):
#        self.stream.write('  <Stattalon>\n')
#        for i, fieldName in enumerate(dbfRecord.dbf.fieldNames):
#            self.stream.write('    <%s>%s</%s>\n' % (fieldName, unicode(dbfRecord[i]).encode('utf-8'), fieldName))
#        self.stream.write('  </Stattalon>\n')

    def writeData(self, t2000, t3000):
        formDec = ns0.form_Dec()
        form = formDec.pyclass()

        form.set_attribute_name(u'12-Д-М-3/1000')
        form.set_attribute_project('DD')
        form.set_attribute_version(0)
#        form.set_attribute_lang('ru')

        lpu = form.new_LPU()
        lpu.set_attribute_lpu_id(51)
        lpu.set_attribute_email('spamtrap@mail.ru')
        form.LPU = lpu

        form._data = form.new_data()
        data = form._data
        data.set_attribute_period(13)

        DD1000 = data.new_DD1000()
        DD1000._Complete = 0
        DD1000._AttachedOrgs = 0
        DD1000._Summary = 0
        DD1000._ORDER_DD = DD1000.new_ORDER_DD()
        DD1000._ORDER_DD._NoEquipment = 0
        DD1000._ORDER_DD._NoExpert = 0
        DD1000._ORDER_DD._NoEqNEx = 0
        data._DD1000 = (DD1000, )


        countDone, countContinued, countByGroup = t2000
        DD2000 = data.new_DD2000()
        DD2000._citizen = DD2000.new_citizen()
        DD2000._citizen._observable = 0
        DD2000._citizen._observated_complete = countDone
        DD2000._citizen._observated_incomplete = countContinued


        DD2000._groups = DD2000.new_groups()
        DD2000._groups._healthy  = countByGroup[0]
        DD2000._groups._risk_II  = countByGroup[1]
        DD2000._groups._risk_III = countByGroup[2]
        DD2000._groups._risk_VI  = countByGroup[3]
        DD2000._groups._risk_V   = countByGroup[4]
        data._DD2000 = (DD2000,  )

        data._DD3000 = data.new_DD3000()
        data._DD3000._A15_A19            =  t3000['A15-A19']
        data._DD3000._malignant = data._DD3000.new_malignant()
        data._DD3000._malignant._C15_C26 = t3000['C15-C26']
        data._DD3000._malignant._C33_C34 = t3000['C33-C34']
        data._DD3000._malignant._C43_C44 = t3000['C43-C44']
        data._DD3000._malignant._C50     = t3000['C50']
        data._DD3000._malignant._C50_C58 = t3000['C50-C58']
        data._DD3000._malignant._C61     = t3000['C61']
        data._DD3000._malignant._C81     = t3000['C81-C96']
        data._DD3000._malignant._D50_D64 = t3000['D50-D64']
        data._DD3000._malignant._E10_E14 = t3000['E10-E14']
        data._DD3000._malignant._E66     = t3000['E66']
        data._DD3000._malignant._E78     = t3000['E78']
        data._DD3000._malignant._I10_I15 = t3000['I10-I15']
        data._DD3000._malignant._I20_I25 = t3000['I20-I25']
        data._DD3000._malignant._R73     = t3000['R73']
        data._DD3000._malignant._R91     = t3000['R91']
        data._DD3000._malignant._R92     = t3000['R92']
        data._DD3000._malignant._R94_3   = t3000['R94.3']

        elt = ElementProxy(None)
        elt.createDocument(None, None)
        formDec.serialize(elt=elt, sw=None, pyobj=form, inline=True)
#        self.stream.write('<?xml version="1.0" encoding="utf-8"?>\n'+unicode(str(elt)).encode('utf-8') )
        self.stream.write('<?xml version="1.0" encoding="utf-8"?>\n'+str(elt))


    def close(self):
        if self.storage != self.stream:
            self.stream.close()


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