#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2012-2013 Vista Software. All rights reserved.
##
#############################################################################

import httplib
from xml.dom.minidom import DOMImplementation
from xml.dom.minidom import parseString
from urlparse import urlparse
from library.Utils                import *

#####################################################
class NotTextNodeError:
    pass


def getTextFromNode(node):
    """
    scans through all children of node and gathers the
    text. if node has non-text child-nodes, then
    NotTextNodeError is raised.
    """
    t = ""
    for n in node.childNodes:
	if n.nodeType == n.TEXT_NODE:
	    t += n.nodeValue
	else:
	    raise NotTextNodeError
    return t


def nodeToDic(node):
    """
    nodeToDic() scans through the children of node and makes a
    dictionary from the content.
    three cases are differentiated:
	- if the node contains no other nodes, it is a text-node
    and {nodeName:text} is merged into the dictionary.
	- if the node has the attribute "method" set to "true",
    then it's children will be appended to a list and this
    list is merged to the dictionary in the form: {nodeName:list}.
	- else, nodeToDic() will call itself recursively on
    the nodes children (merging {nodeName:nodeToDic()} to
    the dictionary).
    """
    dic = {} 
    for n in node.childNodes:
	if n.nodeType != n.ELEMENT_NODE:
	    continue
	if n.getAttribute("multiple") == "true":
	    # node with multiple children:
	    # put them in a list
	    l = []
	    for c in n.childNodes:
	        if c.nodeType != n.ELEMENT_NODE:
		    continue
		l.append(nodeToDic(c))
            nn = n.nodeName.split(':')
            if len(nn) == 1:
                nnn = nn[0]
            else:
                nnn = nn[1]
            while nnn in dic:
                nnn += '_'
            dic.update({nnn:l})
	    continue
		
	try:
	    text = getTextFromNode(n)
	except NotTextNodeError:
            # 'normal' node
            nn = n.nodeName.split(':')
            if len(nn) == 1:
                nnn = nn[0]
            else:
                nnn = nn[1]
            while nnn in dic:
                nnn += '_'                
            dic.update({nnn:nodeToDic(n)})
            continue

        # text node
        nn = n.nodeName.split(':')
        if len(nn) == 1:
            nnn = nn[0]
        else:
            nnn = nn[1]
        while nnn in dic:
            nnn += '_'            
        dic.update({nnn:forceString(text)})
	continue
    return dic
    
class CEasySoap:
    
    def __init__(self, url, action):
        self.action = action
        urlP = urlparse(url)
        self.proto = urlP.scheme
        self.port  = urlP.port
        self.host  = urlP.hostname
        self.path  = urlP.path
        self.reset()
        
    def reset(self):
        self.request = {}
        self.headers = {}
        self.result  = {}
        
    def body(self, path, value):
        self.request[ path ] = value
        pass
        
    def header(self, path, value):
        self.headers[ path ] = value
        pass
    
    def call(self):
        # define namespaces used
        soapEnv = "http://schemas.xmlsoap.org/soap/envelope/"
        # DOM document
        impl = DOMImplementation()
        domdoc = impl.createDocument(None, None, None)        
        # SOAP envelope namespace
        seObj = domdoc.createElementNS(soapEnv, "SOAP-ENV:Envelope")
        seObj.setAttributeNS(soapEnv, "xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        seObj.setAttributeNS(soapEnv, "xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
        seObj.setAttributeNS(soapEnv, "xmlns:SOAP-ENV", "http://schemas.xmlsoap.org/soap/envelope/")
        # add it to the root
        domdoc.appendChild(seObj)
        # header
        header = domdoc.createElement("SOAP-ENV:Header")
        # TODO: insert correct path of element
        for key in self.headers.keys():
            v = domdoc.createElement(key)
            vv = domdoc.createTextNode(self.headers[key])
            v.appendChild(vv)
            header.appendChild(v)
        seObj.appendChild(header)
        # body
        body = domdoc.createElement("SOAP-ENV:Body")    
        # TODO: insert data to body request
        seObj.appendChild(body)
        # dump request to string
        soapStr = domdoc.toxml()
        ##PrettyPrint(domdoc, soapStr)
        # construct the header and post
        ws = httplib.HTTP(self.host, self.port)
        ws.putrequest("POST", self.path)
        ws.putheader("Host", self.host)
        ws.putheader("User-Agent", "iVista SOAP Client")
        ws.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
        ws.putheader("Content-length", "%d" % len(soapStr))
        ws.putheader("SOAPAction", "\"%s\"" % self.action)
        ws.endheaders()
        ws.send(soapStr)   
        # get the response
        statuscode, statusmessage, header = ws.getreply()
        if (statuscode != 200):
            raise Exception(statusmessage)
        res = ws.getfile().read()
        self.result = nodeToDic(parseString(res))

        
        
