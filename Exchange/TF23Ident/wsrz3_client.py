##################################################
# file: wsrz3_client.py
# 
# client stubs generated by "ZSI.generate.wsdl2python.WriteServiceModule"
#     C:\Python27\Scripts\wsdl2py-script.py -s Ident.wsdl
# 
##################################################


import urlparse, types
from ZSI.TCcompound import ComplexType, Struct
from ZSI import client
from ZSI.schema import GED, GTD
import ZSI

# Locator
class wsrzService3Locator:
    wsrzPort3_address = "http://10.20.29.5:8080/wsrz/server3.php"
    def getwsrzPort3Address(self):
        return wsrzService3Locator.wsrzPort3_address
    def getwsrzPort3(self, url=None, **kw):
        return wsrzBinding3SOAP(url or wsrzService3Locator.wsrzPort3_address, **kw)

# Methods
class wsrzBinding3SOAP:
    def __init__(self, url, **kw):
        kw.setdefault("readerclass", None)
        kw.setdefault("writerclass", None)
        # no resource properties
        self.binding = client.Binding(url=url, **kw)
        # no ws-addressing

    # op: getPolicyInfo3
    def getPolicyInfo3(self, request, **kw):
        if isinstance(request, getPolicyInfoRequest3) is False:
            raise TypeError, "%s incorrect request type" % (request.__class__)
        # no input wsaction
        self.binding.Send(None, None, request, soapaction="urn:xmethods-delayed-quotes#getPolicyInfo3", encodingStyle="http://schemas.xmlsoap.org/soap/encoding/", **kw)
        # no output wsaction
        typecode = Struct(pname=None, ofwhat=getPolicyInfoResponse3.typecode.ofwhat, pyclass=getPolicyInfoResponse3.typecode.pyclass)
        response = self.binding.Receive(typecode)
        return response

class getPolicyInfoRequest3:
    def __init__(self, **kw):
        """Keyword parameters:
        paramSource -- part paramSource
        paramRID -- part paramRID
        paramForDate -- part paramForDate
        personSurname -- part personSurname
        personName -- part personName
        personPatronymic -- part personPatronymic
        personSex -- part personSex
        personBirthDate -- part personBirthDate
        identityType -- part identityType
        identitySeries -- part identitySeries
        identityNumber -- part identityNumber
        Snils -- part Snils
        policyType -- part policyType
        policySeries -- part policySeries
        policyNumber -- part policyNumber
        """
        self.paramSource =  kw.get("paramSource")
        self.paramRID =  kw.get("paramRID")
        self.paramForDate =  kw.get("paramForDate")
        self.personSurname =  kw.get("personSurname")
        self.personName =  kw.get("personName")
        self.personPatronymic =  kw.get("personPatronymic")
        self.personSex =  kw.get("personSex")
        self.personBirthDate =  kw.get("personBirthDate")
        self.identityType =  kw.get("identityType")
        self.identitySeries =  kw.get("identitySeries")
        self.identityNumber =  kw.get("identityNumber")
        self.Snils =  kw.get("Snils")
        self.policyType =  kw.get("policyType")
        self.policySeries =  kw.get("policySeries")
        self.policyNumber =  kw.get("policyNumber")
getPolicyInfoRequest3.typecode = Struct(pname=("urn:xmethods-delayed-quotes","getPolicyInfo3"), ofwhat=[ZSI.TC.String(pname="paramSource", aname="paramSource", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TCnumbers.Iint(pname="paramRID", aname="paramRID", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TC.String(pname="paramForDate", aname="paramForDate", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TC.String(pname="personSurname", aname="personSurname", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TC.String(pname="personName", aname="personName", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TC.String(pname="personPatronymic", aname="personPatronymic", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TC.String(pname="personSex", aname="personSex", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TC.String(pname="personBirthDate", aname="personBirthDate", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TCnumbers.IunsignedByte(pname="identityType", aname="identityType", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TC.String(pname="identitySeries", aname="identitySeries", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TC.String(pname="identityNumber", aname="identityNumber", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TC.String(pname="Snils", aname="Snils", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TCnumbers.IunsignedByte(pname="policyType", aname="policyType", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TC.String(pname="policySeries", aname="policySeries", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True),
                                                                                                        ZSI.TC.String(pname="policyNumber", aname="policyNumber", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=getPolicyInfoRequest3, encoded="urn:xmethods-delayed-quotes")

class getPolicyInfoResponse3:
    def __init__(self, **kw):
        """Keyword parameters:
        paramID -- part paramID
        paramRID -- part paramRID
        personSurname -- part personSurname
        personName -- part personName
        personPatronymic -- part personPatronymic
        personSex -- part personSex
        personBirthDate -- part personBirthDate
        Snils -- part Snils
        policyType -- part policyType
        policySeries -- part policySeries
        policyNumber -- part policyNumber
        policyFromDate -- part policyFromDate
        policyTillDate -- part policyTillDate
        policyOkato -- part policyOkato
        policyOgrn -- part policyOgrn
        policySmo -- part policySmo
        policyKsmo -- part policyKsmo
        ddVP -- part ddVP
        ddDATN -- part ddDATN
        ddDATO -- part ddDATO
        ddCODE_MO -- part ddCODE_MO
        resultID -- part resultID
        resultType -- part resultType
        resultCode -- part resultCode
        resultMessage -- part resultMessage
        """
        self.paramID =  kw.get("paramID")
        self.paramRID =  kw.get("paramRID")
        self.personSurname =  kw.get("personSurname")
        self.personName =  kw.get("personName")
        self.personPatronymic =  kw.get("personPatronymic")
        self.personSex =  kw.get("personSex")
        self.personBirthDate =  kw.get("personBirthDate")
        self.Snils =  kw.get("Snils")
        self.policyType =  kw.get("policyType")
        self.policySeries =  kw.get("policySeries")
        self.policyNumber =  kw.get("policyNumber")
        self.policyFromDate =  kw.get("policyFromDate")
        self.policyTillDate =  kw.get("policyTillDate")
        self.policyOkato =  kw.get("policyOkato")
        self.policyOgrn =  kw.get("policyOgrn")
        self.policySmo =  kw.get("policySmo")
        self.policyKsmo =  kw.get("policyKsmo")
        self.ddVP =  kw.get("ddVP")
        self.ddDATN =  kw.get("ddDATN")
        self.ddDATO =  kw.get("ddDATO")
        self.ddCODE_MO =  kw.get("ddCODE_MO")
        self.resultID =  kw.get("resultID")
        self.resultType =  kw.get("resultType")
        self.resultCode =  kw.get("resultCode")
        self.resultMessage =  kw.get("resultMessage")
getPolicyInfoResponse3.typecode = Struct(pname=("urn:xmethods-delayed-quotes","getPolicyInfo3Response"), ofwhat=[ZSI.TCnumbers.Iint(pname="paramID", aname="paramID", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="paramRID", aname="paramRID", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="personSurname", aname="personSurname", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="personName", aname="personName", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="personPatronymic", aname="personPatronymic", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="personSex", aname="personSex", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="personBirthDate", aname="personBirthDate", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="Snils", aname="Snils", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.IunsignedByte(pname="policyType", aname="policyType", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="policySeries", aname="policySeries", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="policyNumber", aname="policyNumber", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="policyFromDate", aname="policyFromDate", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="policyTillDate", aname="policyTillDate", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="policyOkato", aname="policyOkato", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="policyOgrn", aname="policyOgrn", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="policySmo", aname="policySmo", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="policyKsmo", aname="policyKsmo", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="ddVP", aname="ddVP", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="ddDATN", aname="ddDATN", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="ddDATO", aname="ddDATO", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="ddCODE_MO", aname="ddCODE_MO", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="resultID", aname="resultID", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="resultType", aname="resultType", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="resultCode", aname="resultCode", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="resultMessage", aname="resultMessage", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=getPolicyInfoResponse3, encoded="urn:xmethods-delayed-quotes")
