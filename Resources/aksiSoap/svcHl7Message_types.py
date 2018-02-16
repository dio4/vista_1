##################################################
# file: svcHl7Message_types.py
#
# schema types generated by "ZSI.generate.wsdl2python.WriteServiceModule"
#    C:\pydev\Python25\wsdl2py.bat -b wsdl.txt
#
##################################################

import ZSI
import ZSI.TCcompound
from ZSI.schema import ElementDeclaration
from ZSI.generate.pyclass import pyclass_type

##############################
# targetNamespace
# urn:hl7-org:v3
##############################

class ns0:
    targetNamespace = "urn:hl7-org:v3"

    class hl7Message_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "hl7Message"
        schema = "urn:hl7-org:v3"
        def __init__(self, **kw):
            ns = ns0.hl7Message_Dec.schema
            TClist = [ZSI.TC.AnyElement(aname="_any", minOccurs=0, maxOccurs=1, nillable=True, processContents="lax")]
            kw["pname"] = (u'urn:hl7-org:v3', u'hl7Message')
            kw["aname"] = "_hl7Message"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            self.nillable=True
            class Holder:
                __metaclass__ = pyclass_type
                typecode = self
                def __init__(self):
                    # pyclass
                    self._any = None
                    return
            Holder.__name__ = "hl7Message_Holder"
            self.pyclass = Holder

# end class ns0 (tns: urn:hl7-org:v3)