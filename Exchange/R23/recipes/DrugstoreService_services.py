##################################################
# file: DrugstoreService_services.py
# 
# client stubs generated by "ZSI.generate.wsdl2python.WriteServiceModule"
#     /usr/lib/python-exec/python2.7/wsdl2py drugstore.wsdl
# 
##################################################

from DrugstoreService_services_types import *
import urlparse, types
from ZSI.TCcompound import ComplexType, Struct
from ZSI import client
from ZSI.schema import GED, GTD
import ZSI

# Locator
class DrugstoreServiceLocator:
    DrugstoreServiceSoap_address = "http://10.0.1.154/drugstore/DrugstoreService.asmx"
    def getDrugstoreServiceSoapAddress(self):
        return DrugstoreServiceLocator.DrugstoreServiceSoap_address
    def getDrugstoreServiceSoap(self, url=None, **kw):
        return DrugstoreServiceSoapSOAP(url or DrugstoreServiceLocator.DrugstoreServiceSoap_address, **kw)

# Methods
class DrugstoreServiceSoapSOAP:
    def __init__(self, url, **kw):
        kw.setdefault("readerclass", None)
        kw.setdefault("writerclass", None)
        # no resource properties
        self.binding = client.Binding(url=url, **kw)
        # no ws-addressing

    # op: RemainRequest
    def RemainRequest(self, request, **kw):
        if isinstance(request, RemainRequestSoapIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://tempuri.org/RemainRequest", **kw)
        # no output wsaction
        response = self.binding.Receive(RemainRequestSoapOut.typecode)
        return response

    # op: RemainResponse
    def RemainResponse(self, request, **kw):
        if isinstance(request, RemainResponseSoapIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://tempuri.org/RemainResponse", **kw)
        # no output wsaction
        response = self.binding.Receive(RemainResponseSoapOut.typecode)
        return response

    # op: RemainDownload
    def RemainDownload(self, request, **kw):
        if isinstance(request, RemainDownloadSoapIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://tempuri.org/RemainDownload", **kw)
        # no output wsaction
        response = self.binding.Receive(RemainDownloadSoapOut.typecode)
        return response

    # op: ShipmentRequest
    def ShipmentRequest(self, request, **kw):
        if isinstance(request, ShipmentRequestSoapIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://tempuri.org/ShipmentRequest", **kw)
        # no output wsaction
        response = self.binding.Receive(ShipmentRequestSoapOut.typecode)
        return response

    # op: ShipmentResponse
    def ShipmentResponse(self, request, **kw):
        if isinstance(request, ShipmentResponseSoapIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://tempuri.org/ShipmentResponse", **kw)
        # no output wsaction
        response = self.binding.Receive(ShipmentResponseSoapOut.typecode)
        return response

    # op: ContractorRequest
    def ContractorRequest(self, request, **kw):
        if isinstance(request, ContractorRequestSoapIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://tempuri.org/ContractorRequest", **kw)
        # no output wsaction
        response = self.binding.Receive(ContractorRequestSoapOut.typecode)
        return response

    # op: ContractorResponse
    def ContractorResponse(self, request, **kw):
        if isinstance(request, ContractorResponseSoapIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://tempuri.org/ContractorResponse", **kw)
        # no output wsaction
        response = self.binding.Receive(ContractorResponseSoapOut.typecode)
        return response

    # op: ServerContractorRequest
    def ServerContractorRequest(self, request, **kw):
        if isinstance(request, ServerContractorRequestSoapIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://tempuri.org/ServerContractorRequest", **kw)
        # no output wsaction
        response = self.binding.Receive(ServerContractorRequestSoapOut.typecode)
        return response

    # op: ServerContractorResponse
    def ServerContractorResponse(self, request, **kw):
        if isinstance(request, ServerContractorResponseSoapIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="http://tempuri.org/ServerContractorResponse", **kw)
        # no output wsaction
        response = self.binding.Receive(ServerContractorResponseSoapOut.typecode)
        return response

RemainRequestSoapIn = GED("http://tempuri.org/", "RemainRequest").pyclass

RemainRequestSoapOut = GED("http://tempuri.org/", "RemainRequestResponse").pyclass

RemainResponseSoapIn = GED("http://tempuri.org/", "RemainResponse").pyclass

RemainResponseSoapOut = GED("http://tempuri.org/", "RemainResponseResponse").pyclass

RemainDownloadSoapIn = GED("http://tempuri.org/", "RemainDownload").pyclass

RemainDownloadSoapOut = GED("http://tempuri.org/", "RemainDownloadResponse").pyclass

ShipmentRequestSoapIn = GED("http://tempuri.org/", "ShipmentRequest").pyclass

ShipmentRequestSoapOut = GED("http://tempuri.org/", "ShipmentRequestResponse").pyclass

ShipmentResponseSoapIn = GED("http://tempuri.org/", "ShipmentResponse").pyclass

ShipmentResponseSoapOut = GED("http://tempuri.org/", "ShipmentResponseResponse").pyclass

ContractorRequestSoapIn = GED("http://tempuri.org/", "ContractorRequest").pyclass

ContractorRequestSoapOut = GED("http://tempuri.org/", "ContractorRequestResponse").pyclass

ContractorResponseSoapIn = GED("http://tempuri.org/", "ContractorResponse").pyclass

ContractorResponseSoapOut = GED("http://tempuri.org/", "ContractorResponseResponse").pyclass

ServerContractorRequestSoapIn = GED("http://tempuri.org/", "ServerContractorRequest").pyclass

ServerContractorRequestSoapOut = GED("http://tempuri.org/", "ServerContractorRequestResponse").pyclass

ServerContractorResponseSoapIn = GED("http://tempuri.org/", "ServerContractorResponse").pyclass

ServerContractorResponseSoapOut = GED("http://tempuri.org/", "ServerContractorResponseResponse").pyclass
