##################################################
# file: s11_client.py
# 
# client stubs generated by "ZSI.generate.wsdl2python.WriteServiceModule"
#     wsdl2py.py -b wsdl.xml
# 
##################################################

from ZSI import client
from ZSI.schema import GED

from s11_types import ns0

# Locator
class s11ServiceLocator:
    s11Port_address = "http://gw1.ivistasoft.com/ext/wsdl/netrika2vista/s11proxy.php"
    def gets11PortAddress(self):
        return s11ServiceLocator.s11Port_address
    def gets11Port(self, url=None, **kw):
        return s11BindingSOAP(url or s11ServiceLocator.s11Port_address, **kw)

# Methods
class s11BindingSOAP:
    def __init__(self, url, **kw):
        kw.setdefault("readerclass", None)
        kw.setdefault("writerclass", None)
        # no resource properties
        self.binding = client.Binding(url=url, **kw)
        # no ws-addressing

    # op: test
    def test(self, request, **kw):
        if isinstance(request, testIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(testOut.typecode)
        return response

    # op: getOrganisationInfo
    def getOrganisationInfo(self, request, **kw):
        if isinstance(request, getOrganisationInfoIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(getOrganisationInfoOut.typecode)
        return response

    # op: getOrgStructures
    def getOrgStructures(self, request, **kw):
        if isinstance(request, getOrgStructuresIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(getOrgStructuresOut.typecode)
        return response

    # op: getAddresses
    def getAddresses(self, request, **kw):
        if isinstance(request, getAddressesIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(getAddressesOut.typecode)
        return response

    # op: findOrgStructureByAddress
    def findOrgStructureByAddress(self, request, **kw):
        if isinstance(request, findOrgStructureByAddressIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(findOrgStructureByAddressOut.typecode)
        return response

    # op: getPersonnel
    def getPersonnel(self, request, **kw):
        if isinstance(request, getPersonnelIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(getPersonnelOut.typecode)
        return response

    # op: getTicketsAvailability
    def getTicketsAvailability(self, request, **kw):
        if isinstance(request, getTicketsAvailabilityIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(getTicketsAvailabilityOut.typecode)
        return response

    # op: getTotalTicketsAvailability
    def getTotalTicketsAvailability(self, request, **kw):
        if isinstance(request, getTotalTicketsAvailabilityIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(getTotalTicketsAvailabilityOut.typecode)
        return response

    # op: getWorkTimeAndStatus
    def getWorkTimeAndStatus(self, request, **kw):
        if isinstance(request, getWorkTimeAndStatusIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(getWorkTimeAndStatusOut.typecode)
        return response

    # op: findPatient
    def findPatient(self, request, **kw):
        if isinstance(request, findPatientIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(findPatientOut.typecode)
        return response

    # op: findPatients
    def findPatients(self, request, **kw):
        if isinstance(request, findPatientsIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(findPatientsOut.typecode)
        return response

    # op: getPatientInfo
    def getPatientInfo(self, request, **kw):
        if isinstance(request, getPatientInfoIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(getPatientInfoOut.typecode)
        return response

    # op: getPatientContacts
    def getPatientContacts(self, request, **kw):
        if isinstance(request, getPatientContactsIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(getPatientContactsOut.typecode)
        return response

    # op: getPatientAddress
    def getPatientAddress(self, request, **kw):
        if isinstance(request, getPatientAddressIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(getPatientAddressOut.typecode)
        return response

    # op: getPatientOrgStructures
    def getPatientOrgStructures(self, request, **kw):
        if isinstance(request, getPatientOrgStructuresIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(getPatientOrgStructuresOut.typecode)
        return response

    # op: enqueuePatient
    def enqueuePatient(self, request, **kw):
        if isinstance(request, enqueuePatientIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(enqueuePatientOut.typecode)
        return response

    # op: getPatientQueue
    def getPatientQueue(self, request, **kw):
        if isinstance(request, getPatientQueueIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(getPatientQueueOut.typecode)
        return response

    # op: dequeuePatient
    def dequeuePatient(self, request, **kw):
        if isinstance(request, dequeuePatientIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(dequeuePatientOut.typecode)
        return response

    # op: getStatistic
    def getStatistic(self, request, **kw):
        if isinstance(request, getStatisticIn) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="", **kw)
        # no output wsaction
        response = self.binding.Receive(getStatisticOut.typecode)
        return response

testIn = GED("http://tempuri.org/", "testInDoc").pyclass

testOut = GED("http://tempuri.org/", "testOutDoc").pyclass

getOrganisationInfoIn = GED("http://tempuri.org/", "organisationInfoInDoc").pyclass

getOrganisationInfoOut = GED("http://tempuri.org/", "organisationInfoOutDoc").pyclass

getOrgStructuresIn = GED("http://tempuri.org/", "getOrgStructuresInDoc").pyclass

getOrgStructuresOut = GED("http://tempuri.org/", "getOrgStructuresOutDoc").pyclass

getAddressesIn = GED("http://tempuri.org/", "getAddressesInDoc").pyclass

getAddressesOut = GED("http://tempuri.org/", "getAddressesOutDoc").pyclass

findOrgStructureByAddressIn = GED("http://tempuri.org/", "findOrgStructureByAddressInDoc").pyclass

findOrgStructureByAddressOut = GED("http://tempuri.org/", "findOrgStructureByAddressOutDoc").pyclass

getPersonnelIn = GED("http://tempuri.org/", "getPersonnelInDoc").pyclass

getPersonnelOut = GED("http://tempuri.org/", "getPersonnelOutDoc").pyclass

getTicketsAvailabilityIn = GED("http://tempuri.org/", "getTicketsAvailabilityInDoc").pyclass

getTicketsAvailabilityOut = GED("http://tempuri.org/", "getTicketsAvailabilityOutDoc").pyclass

getTotalTicketsAvailabilityIn = GED("http://tempuri.org/", "getTotalTicketsAvailabilityInDoc").pyclass

getTotalTicketsAvailabilityOut = GED("http://tempuri.org/", "getTotalTicketsAvailabilityOutDoc").pyclass

getWorkTimeAndStatusIn = GED("http://tempuri.org/", "getWorkTimeAndStatusInDoc").pyclass

getWorkTimeAndStatusOut = GED("http://tempuri.org/", "getWorkTimeAndStatusOutDoc").pyclass

findPatientIn = GED("http://tempuri.org/", "findPatientInDoc").pyclass

findPatientOut = GED("http://tempuri.org/", "findPatientOutDoc").pyclass

findPatientsIn = GED("http://tempuri.org/", "findPatientsInDoc").pyclass

findPatientsOut = GED("http://tempuri.org/", "findPatientsOutDoc").pyclass

getPatientInfoIn = GED("http://tempuri.org/", "getPatientInfoInDoc").pyclass

getPatientInfoOut = GED("http://tempuri.org/", "getPatientInfoOutDoc").pyclass

getPatientContactsIn = GED("http://tempuri.org/", "getPatientContactsInDoc").pyclass

getPatientContactsOut = GED("http://tempuri.org/", "getPatientContactsOutDoc").pyclass

getPatientAddressIn = GED("http://tempuri.org/", "getPatientAddressInDoc").pyclass

getPatientAddressOut = GED("http://tempuri.org/", "getPatientAddressOutDoc").pyclass

getPatientOrgStructuresIn = GED("http://tempuri.org/", "getPatientOrgStructuresInDoc").pyclass

getPatientOrgStructuresOut = GED("http://tempuri.org/", "getPatientOrgStructuresOutDoc").pyclass

enqueuePatientIn = GED("http://tempuri.org/", "enqueuePatientInDoc").pyclass

enqueuePatientOut = GED("http://tempuri.org/", "enqueuePatientOutDoc").pyclass

getPatientQueueIn = GED("http://tempuri.org/", "getPatientQueueInDoc").pyclass

getPatientQueueOut = GED("http://tempuri.org/", "getPatientQueueOutDoc").pyclass

dequeuePatientIn = GED("http://tempuri.org/", "dequeuePatientInDoc").pyclass

dequeuePatientOut = GED("http://tempuri.org/", "dequeuePatientOutDoc").pyclass

getStatisticIn = GED("http://tempuri.org/", "getStatisticInDoc").pyclass

getStatisticOut = GED("http://tempuri.org/", "getStatisticOutDoc").pyclass