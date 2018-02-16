# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2015 Vista Software. All rights reserved.
##
#############################################################################

__author__ = 'atronah'

'''
    author: atronah
    date:   30.01.2015
'''


from PyQt4 import QtXml, QtCore


class CXMLConstants:
    XMLS_INSTANCE_NS = u'http://www.w3.org/2001/XMLSchema-instance'


class CXMLHelper(object):
    defaultEncoding = u'UTF-8'
    version = u'1.0'


    @staticmethod
    def getRootElement(node):
        document = node.toDocument() if node.isDocument() else node.ownerDocument()
        return document.firstChildElement()


    @classmethod
    def createDomDocument(cls, rootElementName, mainNS = QtCore.QString(), encoding = None):
        domImplementation = QtXml.QDomImplementation()
        domDocType = QtXml.QDomDocumentType()
        doc = domImplementation.createDocument(mainNS, #namespace URI
                                               rootElementName, #root element name
                                               domDocType) # document type
        processingInstruction = doc.createProcessingInstruction(u'xml', u'version="%s" encoding="%s"' % (cls.version,
                                                                                                       cls.defaultEncoding if encoding is None else encoding))
        doc.insertBefore(processingInstruction, cls.getRootElement(doc))
        return doc

    @staticmethod
    def fixNamespace(parentNode, nsURI, nsAlias = None):
        isInheritedNamespace = False
        if nsURI:
            while not parentNode.isNull():
                if parentNode.namespaceURI() == nsURI:
                    nsAlias = parentNode.prefix()
                    isInheritedNamespace = True
                    break
                else:
                    attributes = parentNode.attributes()
                    for idx in xrange(attributes.count()):
                        attr = attributes.item(idx).toAttr()
                        if attr.namespaceURI() == nsURI:
                            nsAlias = attr.prefix()
                        elif attr.name().startsWith('xmlns:') and attr.value() == nsURI:
                            nsAlias = attr.name().remove('xmlns:')
                        else:
                            continue

                        isInheritedNamespace = True
                        break  # for

                    if isInheritedNamespace:
                        break  # while
                parentNode = parentNode.parentNode()

        return nsAlias, isInheritedNamespace


    @classmethod
    def addNode(cls, parentNode, nodeType, nodeName, nsURI = None, nsAlias = None, afterNode = None):
        """
        Добавляет новый узел с именем nodeName в качестве дочернего для узла parentNode.

        Примечание (atronah): Работает с учетом того, что Qt не умеет работать с наследуемыми Namespace'ми
        (добавляет xmlns в каждый елемент, для которого указан namespace)
        :param parentNode: родительский узел, в который необходимо добавить текущий
        :param nodeType: тип добавляемого узла
        :param nodeName: имя текущего, добавляемого узла
        :param nsURI: пространство имен добавляемого узла
        :param nsAlias: псевдоним для пространства имен добавляемого узла
        :param afterNode: узел, после которого необходимо вставить текущий (может быть строкой или QDomNode() или списком)
        :return QDomNode
        """
        node = QtXml.QDomNode()

        if not nodeName:
            return node

        doc = parentNode.ownerDocument()

        nsAlias, isInheritedNamespace = cls.fixNamespace(parentNode, nsURI, nsAlias)
        if nsAlias:
            nodeName = nsAlias + u':' + nodeName



        afterNodeList = afterNode if isinstance(afterNode, (list, tuple)) else [afterNode]
        while afterNodeList:
            afterNode = afterNodeList.pop(0)
            # если элемент, после которого необходимо вставить текущий, не является дочерним узлом родительского
            if not (isinstance(afterNode, QtXml.QDomNode) and afterNode.parentNode() == parentNode):
                # найти элемент в родительском по имение afterNode (если это строка) или последний имеющийся элемент
                afterNode = parentNode.lastChildElement(afterNode if isinstance(afterNode, (basestring, QtCore.QString)) else QtCore.QString())
            if not afterNode.isNull():
                break

        if not isinstance(afterNode, QtXml.QDomNode) or afterNode.isNull():
            afterNode = parentNode.lastChildElement()

        # Если добавляется элемент без NS или с NS, унаседованным от родителя, то создать его без NS
        if not nsURI or isInheritedNamespace:
            if nodeType == QtXml.QDomNode.ElementNode:
                node = parentNode.insertAfter(doc.createElement(nodeName), afterNode)
            elif nodeType == QtXml.QDomNode.AttributeNode:
                node = doc.createAttribute(nodeName)
                parentNode.setAttributeNode(node)
        else:
            if nodeType == QtXml.QDomNode.ElementNode:
                node = parentNode.insertAfter(doc.createElementNS(nsURI, nodeName), afterNode)
            elif nodeType == QtXml.QDomNode.AttributeNode:
                node = doc.createAttributeNS(nsURI, nodeName)
                parentNode.setAttributeNodeNS(node)
        return node


    @classmethod
    def addElement(cls, parentNode, elemName, nsURI = None, nsAlias = None, ifNotExist = False, afterElem = None):
        """
        Добавляет новый элемент с именем elemName внутрь элемента parent.

        :param parentNode:
        :param elemName:
        :param nsURI:
        :param nsAlias: алиас namespace добавляемого элемента
        :param ifNotExist: добавить новый элемент, только если его еще нет, иначе вернуть уже имеющийся
        :param afterElem: элемент, после которого необходимо вставить текущий (может быть строкой или QDomElement())
        :return: добавленный элемент QDomElement
        """

        if ifNotExist:
            element = parentNode.namedItem(elemName)
            if not element.isNull():
                return element

        element = cls.addNode(parentNode=parentNode,
                              nodeType=QtXml.QDomNode.ElementNode,
                              nodeName=elemName,
                              nsURI=nsURI,
                              nsAlias=nsAlias,
                              afterNode=afterElem).toElement()

        return element


    @classmethod
    def addAttribute(cls, element, attrName, nsURI=None, nsAlias=None):
        """
        Добавляет новый атрибут с именем attrName внутрь элемента element.

        :param element: элемент, в который добавляется аттрибут
        :param attrName: имя аттрибута
        :param nsURI: пространство имен аттрибута
        :param nsAlias: алиас namespace добавляемого элемента
        :return: добавленный элемент QDomElement
        """
        if not element.isElement():
            return QtXml.QDomAttr()

        return cls.addNode(parentNode=element,
                           nodeType=QtXml.QDomNode.AttributeNode,
                           nodeName=attrName,
                           nsURI=nsURI, nsAlias=nsAlias).toAttr()


    @classmethod
    def setValue(cls, node, value):
        if node.isAttr():
            attr = node.toAttr()
            attr.setValue(value)
            return True
        elif node.isElement():
            childList = node.childNodes()
            for childIdx in xrange(childList.length()):
                child = childList.item(childIdx)
                if child.isText() or child.isCDATASection():
                    node.removeChild(child)
            elem = node.toElement()
            elem.appendChild(elem.ownerDocument().createTextNode(unicode(value)))
            return True
        return False




    @classmethod
    def addNamespaceDescription(cls, element, nsAlias, nsURI):
        """
        Добавляет описание namespace для указанного алиаса.
        Вставляет атрибут вида 'xmlns:nsAlias="nsURI"'
        :param element: элемент, для которого задаются описания namespace'ов
        :param nsAlias: псевдоним для namespace
        :param nsURI: URI для namespace
        """

        if not element.isElement():
            return False

        if not (nsAlias and nsURI):
            return False

        attr = cls.addAttribute(element, attrName=u'xmlns:' + nsAlias)
        attr.setValue(nsURI)

        return True

    @classmethod
    def nodeParents(cls, node, reverse = False):
        result = []
        node = node.parentNode()
        while node and not node.isDocument():
            result.append(node)
            node = node.parentNode()
        if reverse:
            result.reverse()
        return result


    @classmethod
    def loadDocument(cls, documentSource):
        doc = QtXml.QDomDocument()
        if doc.setContent(documentSource):
            return doc

        return None


import unittest
class XMLHelperTest(unittest.TestCase):
    def setUp(self):
        self.doc = CXMLHelper.createDomDocument('test', encoding='testEnc')

    def test_setValue(self):
        rootElement = CXMLHelper.getRootElement(self.doc)
        testElement = CXMLHelper.addElement(rootElement, 'testSetValue')

        self.assertEqual(unicode(testElement.text()).strip(), u'')
        s = u'some text'
        CXMLHelper.setValue(testElement, s)
        self.assertEqual(unicode(testElement.text()).strip(), s)

        s = s[::-1]
        CXMLHelper.setValue(testElement, s)
        self.assertEqual(unicode(testElement.text()).strip(), s)


    def tearDown(self):
        self.doc.clear()



def main():
    import sys

    unittest.main()

    sys.exit(0)


if __name__ == '__main__':
    main()