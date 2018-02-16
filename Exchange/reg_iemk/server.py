# -*- coding: utf-8 -*-
# ############################################################################
##
## Copyright (C) 2014 Vista Software. All rights reserved.
##
##############################################################################

__author__ = 'craz'

'''
    author: craz
    date:   12.11.2014
'''

import sys

from PyQt4 import QtCore

from IemcServer_services import SendEventDataRequest, SendEventDataResponse
from IemcServer_services_types import ns0
from Exchange.reg_iemk.ImportR67XML_VM import CImportR67XML_VM
from Exchange.reg_iemk.iemc_settings import CRegIemcSettings
from ZSI.twisted.wsgi import SOAPApplication, soapmethod, SOAPHandlerChainFactory

class IemcService(SOAPApplication):
    factory = SOAPHandlerChainFactory
    wsdl_content = dict(name='IemcServer',
                        targetNamespace="urn:iemcServer",
                        imports=(),
                        portType='')
    def __init__(self, config_name='reg_iemc', **kw):
        self.importer = CImportR67XML_VM(config_name)
        super(IemcService, self).__init__(**kw)

    def __call__(self, env, start_response):
        self.env = env
        return SOAPApplication.__call__(self, env, start_response)

    @soapmethod(SendEventDataRequest.typecode,
                SendEventDataResponse.typecode,
                operation="SendEventData",
                soapaction="SendEventData")
    def soap_SendEventData(self, request, response, **kw):
        self.importer.startImport(request)
        res = self.importer.getEventsLog()
        responseList = []
        for message, type, recordId in res:
            error = ns0.ErrorType_Def('_Error')
            error._description = message
            error._type = type
            error._remoteId = recordId
            responseList.append(error)
        response.Error = responseList
        return request, response


def main():
    from wsgiref.simple_server import make_server
    from ZSI.twisted.wsgi import WSGIApplication
    import argparse

    parser = argparse.ArgumentParser(description='Import IEMC or Reg Data to to specified database.')
    parser.add_argument('-c', dest='config', type=str, default='reg_iemc',
                        help='name of config file without extension. reg_iemc by default')

    qApp = QtCore.QCoreApplication(sys.argv)
    args = vars(parser.parse_args(sys.argv[1:]))
    settings = CRegIemcSettings(args['config'])
    application = WSGIApplication()
    httpd = make_server('', settings.getServicePort(), application)
    application['iemcServer'] = IemcService(args['config'])

    print 'listening...'
    httpd.serve_forever()

if __name__=='__main__':
    main()