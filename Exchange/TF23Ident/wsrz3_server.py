#coding:utf-8
##################################################
# file: wsrz3_server.py
#
# skeleton generated by "ZSI.generate.wsdl2dispatch.ServiceModuleWriter"
#      C:\Python27\Scripts\wsdl2py-script.py -s Ident.wsdl
#
##################################################

from ZSI.schema import GED, GTD
from ZSI.TCcompound import ComplexType, Struct
from wsrz3_types import *
from ZSI.ServiceContainer import ServiceSOAPBinding

# Messages  
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
getPolicyInfoRequest3.typecode = Struct(pname=("urn:xmethods-delayed-quotes","getPolicyInfo3"), ofwhat=[ZSI.TC.String(pname="paramSource", aname="paramSource", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.Iint(pname="paramRID", aname="paramRID", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="paramForDate", aname="paramForDate", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="personSurname", aname="personSurname", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="personName", aname="personName", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="personPatronymic", aname="personPatronymic", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="personSex", aname="personSex", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="personBirthDate", aname="personBirthDate", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.IunsignedByte(pname="identityType", aname="identityType", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="identitySeries", aname="identitySeries", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="identityNumber", aname="identityNumber", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="Snils", aname="Snils", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TCnumbers.IunsignedByte(pname="policyType", aname="policyType", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="policySeries", aname="policySeries", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True), ZSI.TC.String(pname="policyNumber", aname="policyNumber", typed=False, encoded=None, minOccurs=1, maxOccurs=1, nillable=True)], pyclass=getPolicyInfoRequest3, encoded="urn:xmethods-delayed-quotes")

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


# Service Skeletons
class wsrzService3(ServiceSOAPBinding):
    soapAction = {}
    root = {}
    _wsdl = u"""<?xml version=\"1.0\" ?>
<definitions name=\"wsrz3\" targetNamespace=\"http://10.20.29.5:8080/wsrz\" xmlns=\"http://schemas.xmlsoap.org/wsdl/\" xmlns:soap=\"http://schemas.xmlsoap.org/wsdl/soap/\" xmlns:soapenc=\"http://schemas.xmlsoap.org/soap/encoding/\" xmlns:tns=\"http://10.20.29.5:8080/wsrz\" xmlns:wsdl=\"http://schemas.xmlsoap.org/wsdl/\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\">

<message name=\"getPolicyInfoRequest3\">
 <part name=\"paramSource\" type=\"xsd:string\"/>
 <part name=\"paramRID\" type=\"xsd:int\"/>
 <part name=\"paramForDate\" type=\"xsd:string\"/>
 <part name=\"personSurname\" type=\"xsd:string\"/>
 <part name=\"personName\" type=\"xsd:string\"/>
 <part name=\"personPatronymic\" type=\"xsd:string\"/>
 <part name=\"personSex\" type=\"xsd:string\"/>
 <part name=\"personBirthDate\" type=\"xsd:string\"/>
 <part name=\"identityType\" type=\"xsd:unsignedByte\"/>
 <part name=\"identitySeries\" type=\"xsd:string\"/>
 <part name=\"identityNumber\" type=\"xsd:string\"/>
 <part name=\"Snils\" type=\"xsd:string\"/>
 <part name=\"policyType\" type=\"xsd:unsignedByte\"/>
 <part name=\"policySeries\" type=\"xsd:string\"/>
 <part name=\"policyNumber\" type=\"xsd:string\"/>
</message>

<message name=\"getPolicyInfoResponse3\">
 <part name=\"paramID\" type=\"xsd:int\"/>
 <part name=\"paramRID\" type=\"xsd:int\"/>
 <part name=\"personSurname\" type=\"xsd:string\"/>
 <part name=\"personName\" type=\"xsd:string\"/>
 <part name=\"personPatronymic\" type=\"xsd:string\"/>
 <part name=\"personSex\" type=\"xsd:string\"/>
 <part name=\"personBirthDate\" type=\"xsd:string\"/>
 <part name=\"Snils\" type=\"xsd:string\"/>
 <part name=\"policyType\" type=\"xsd:unsignedByte\"/>
 <part name=\"policySeries\" type=\"xsd:string\"/>
 <part name=\"policyNumber\" type=\"xsd:string\"/>
 <part name=\"policyFromDate\" type=\"xsd:string\"/>
 <part name=\"policyTillDate\" type=\"xsd:string\"/>
 <part name=\"policyOkato\" type=\"xsd:string\"/>
 <part name=\"policyOgrn\" type=\"xsd:string\"/>
 <part name=\"policySmo\" type=\"xsd:string\"/>
 <part name=\"policyKsmo\" type=\"xsd:string\"/>
 <part name=\"ddVP\" type=\"xsd:string\"/>
 <part name=\"ddDATN\" type=\"xsd:string\"/>
 <part name=\"ddDATO\" type=\"xsd:string\"/>
 <part name=\"ddCODE_MO\" type=\"xsd:string\"/>
 <part name=\"resultID\" type=\"xsd:int\"/>
 <part name=\"resultType\" type=\"xsd:int\"/>
 <part name=\"resultCode\" type=\"xsd:int\"/>
 <part name=\"resultMessage\" type=\"xsd:string\"/>
</message>

<portType name=\"wsrzPortType3\">
 <operation name=\"getPolicyInfo3\">
  <input message=\"tns:getPolicyInfoRequest3\"/>
  <output message=\"tns:getPolicyInfoResponse3\"/>
 </operation>
</portType>

<binding name=\"wsrzBinding3\" type=\"tns:wsrzPortType3\">
 <soap:binding style=\"rpc\" transport=\"http://schemas.xmlsoap.org/soap/http\"/>
 <operation name=\"getPolicyInfo3\">
  <soap:operation soapAction=\"urn:xmethods-delayed-quotes#getPolicyInfo3\"/>
  <input>
   <soap:body encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\" namespace=\"urn:xmethods-delayed-quotes\" use=\"encoded\"/>
  </input>
  <output>
   <soap:body encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\" namespace=\"urn:xmethods-delayed-quotes\" use=\"encoded\"/>
  </output>
 </operation>
</binding>

<service name=\"wsrzService3\">
 <port binding=\"tns:wsrzBinding3\" name=\"wsrzPort3\">
  <soap:address location=\"http://10.20.29.5:8080/wsrz/server3.php\"/>
 </port>
</service>
</definitions>"""

    def __init__(self, post='/wsrz/server3.php', **kw):
        ServiceSOAPBinding.__init__(self, post)

    def soap_getPolicyInfo3(self, ps, **kw):
        request = ps.Parse(getPolicyInfoRequest3.typecode)
        return request,getPolicyInfoResponse3()

    soapAction['urn:xmethods-delayed-quotes#getPolicyInfo3'] = 'soap_getPolicyInfo3'
    root[(getPolicyInfoRequest3.typecode.nspname,getPolicyInfoRequest3.typecode.pname)] = 'soap_getPolicyInfo3'
