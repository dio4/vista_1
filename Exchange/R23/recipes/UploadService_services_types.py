################################################## 
# UploadService_services_types.py 
# generated by ZSI.generate.wsdl2python
##################################################


import ZSI
import ZSI.TCcompound
from ZSI.schema import ElementDeclaration, TypeDefinition, GTD

##############################
# targetNamespace
# http://tempuri.org/
##############################

class ns0:
    targetNamespace = "http://tempuri.org/"

    class ArrayOfRecipeClient_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://tempuri.org/"
        type = (schema, "ArrayOfRecipeClient")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.ArrayOfRecipeClient_Def.schema
            TClist = [GTD("http://tempuri.org/","RecipeClient",lazy=False)(pname=(ns,"RecipeClient"), aname="_RecipeClient", minOccurs=0, maxOccurs="unbounded", nillable=True, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                typecode = self
                def __init__(self):
                    # pyclass
                    self._RecipeClient = []
                    return
            Holder.__name__ = "ArrayOfRecipeClient_Holder"
            self.pyclass = Holder

    class RecipeClient_Def(TypeDefinition):
        #complexType/complexContent extension
        schema = "http://tempuri.org/"
        type = (schema, "RecipeClient")
        def __init__(self, pname, ofwhat=(), extend=False, restrict=False, attributes=None, **kw):
            ns = ns0.RecipeClient_Def.schema
            TClist = [ZSI.TC.String(pname=(ns,"Seria"), aname="_Seria", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Number"), aname="_Number", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Snils"), aname="_Snils", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"PatientFound"), aname="_PatientFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"LpuOgrn"), aname="_LpuOgrn", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"LpuFoms"), aname="_LpuFoms", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"LpuFound"), aname="_LpuFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"DoctorCode"), aname="_DoctorCode", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"DoctorFound"), aname="_DoctorFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"MkbCode"), aname="_MkbCode", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"MkbFound"), aname="_MkbFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TCnumbers.Iint(pname=(ns,"FundingSourceCode"), aname="_FundingSourceCode", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"FundingSourceFound"), aname="_FundingSourceFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"NosologyCode"), aname="_NosologyCode", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"NosologyFound"), aname="_NosologyFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"PrivilegeCode"), aname="_PrivilegeCode", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"PrivilegeCodeFound"), aname="_PrivilegeCodeFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"ProgramFound"), aname="_ProgramFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"ValidPeriodCode"), aname="_ValidPeriodCode", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"ValidPeriodFound"), aname="_ValidPeriodFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TCnumbers.Iint(pname=(ns,"PayPercent"), aname="_PayPercent", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"PayPercentFound"), aname="_PayPercentFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"IsTrn"), aname="_IsTrn", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"TrnCode"), aname="_TrnCode", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"TrnFound"), aname="_TrnFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"MnnCode"), aname="_MnnCode", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"MnnFound"), aname="_MnnFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"CureformCode"), aname="_CureformCode", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"CureformFound"), aname="_CureformFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"UnitCode"), aname="_UnitCode", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"UnitFound"), aname="_UnitFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"IsVk"), aname="_IsVk", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Dosage"), aname="_Dosage", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Decimal(pname=(ns,"Quantity"), aname="_Quantity", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TCtimes.gDateTime(pname=(ns,"SaleDate"), aname="_SaleDate", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TCtimes.gDateTime(pname=(ns,"IssueDate"), aname="_IssueDate", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TCtimes.gDateTime(pname=(ns,"ExpirationDate"), aname="_ExpirationDate", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"RecipeCheck"), aname="_RecipeCheck", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"Uploaded"), aname="_Uploaded", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"IsAnnulled"), aname="_IsAnnulled", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"CauseOfAnnulment"), aname="_CauseOfAnnulment", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"CauseOfAnnulmentFound"), aname="_CauseOfAnnulmentFound", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            attributes = self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            if ns0.Entity_Def not in ns0.RecipeClient_Def.__bases__:
                bases = list(ns0.RecipeClient_Def.__bases__)
                bases.insert(0, ns0.Entity_Def)
                ns0.RecipeClient_Def.__bases__ = tuple(bases)

            ns0.Entity_Def.__init__(self, pname, ofwhat=TClist, extend=True, attributes=attributes, **kw)

    class Entity_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://tempuri.org/"
        type = (schema, "Entity")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.Entity_Def.schema
            TClist = []
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                typecode = self
                def __init__(self):
                    # pyclass
                    return
            Holder.__name__ = "Entity_Holder"
            self.pyclass = Holder

    class ArrayOfDoctorClient_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://tempuri.org/"
        type = (schema, "ArrayOfDoctorClient")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.ArrayOfDoctorClient_Def.schema
            TClist = [GTD("http://tempuri.org/","DoctorClient",lazy=False)(pname=(ns,"DoctorClient"), aname="_DoctorClient", minOccurs=0, maxOccurs="unbounded", nillable=True, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                typecode = self
                def __init__(self):
                    # pyclass
                    self._DoctorClient = []
                    return
            Holder.__name__ = "ArrayOfDoctorClient_Holder"
            self.pyclass = Holder

    class DoctorClient_Def(TypeDefinition):
        #complexType/complexContent extension
        schema = "http://tempuri.org/"
        type = (schema, "DoctorClient")
        def __init__(self, pname, ofwhat=(), extend=False, restrict=False, attributes=None, **kw):
            ns = ns0.DoctorClient_Def.schema
            TClist = [ZSI.TC.String(pname=(ns,"Snils"), aname="_Snils", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Login"), aname="_Login", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"UserId"), aname="_UserId", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Firstname"), aname="_Firstname", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Lastname"), aname="_Lastname", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Patronymic"), aname="_Patronymic", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"DoctorCode"), aname="_DoctorCode", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TCtimes.gDateTime(pname=(ns,"DoctorDeleted"), aname="_DoctorDeleted", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"LpuName"), aname="_LpuName", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"LpuFullname"), aname="_LpuFullname", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"LpuOgrn"), aname="_LpuOgrn", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"JobName"), aname="_JobName", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"SpecialityName"), aname="_SpecialityName", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            attributes = self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            if ns0.Entity_Def not in ns0.DoctorClient_Def.__bases__:
                bases = list(ns0.DoctorClient_Def.__bases__)
                bases.insert(0, ns0.Entity_Def)
                ns0.DoctorClient_Def.__bases__ = tuple(bases)

            ns0.Entity_Def.__init__(self, pname, ofwhat=TClist, extend=True, attributes=attributes, **kw)

    class ArrayOfPersonClient_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://tempuri.org/"
        type = (schema, "ArrayOfPersonClient")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.ArrayOfPersonClient_Def.schema
            TClist = [GTD("http://tempuri.org/","PersonClient",lazy=False)(pname=(ns,"PersonClient"), aname="_PersonClient", minOccurs=0, maxOccurs="unbounded", nillable=True, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                typecode = self
                def __init__(self):
                    # pyclass
                    self._PersonClient = []
                    return
            Holder.__name__ = "ArrayOfPersonClient_Holder"
            self.pyclass = Holder

    class PersonClient_Def(TypeDefinition):
        #complexType/complexContent extension
        schema = "http://tempuri.org/"
        type = (schema, "PersonClient")
        def __init__(self, pname, ofwhat=(), extend=False, restrict=False, attributes=None, **kw):
            ns = ns0.PersonClient_Def.schema
            TClist = [ZSI.TC.String(pname=(ns,"Id"), aname="_Id", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Snils"), aname="_Snils", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Firstname"), aname="_Firstname", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Lastname"), aname="_Lastname", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Patronymic"), aname="_Patronymic", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Sex"), aname="_Sex", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TCtimes.gDateTime(pname=(ns,"Birthday"), aname="_Birthday", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TCtimes.gDateTime(pname=(ns,"Deleted"), aname="_Deleted", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"Uploaded"), aname="_Uploaded", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Check"), aname="_Check", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), GTD("http://tempuri.org/","ArrayOfPrivilegeDocumentClient",lazy=False)(pname=(ns,"PrivilegeDocuments"), aname="_PrivilegeDocuments", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            attributes = self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            if ns0.Entity_Def not in ns0.PersonClient_Def.__bases__:
                bases = list(ns0.PersonClient_Def.__bases__)
                bases.insert(0, ns0.Entity_Def)
                ns0.PersonClient_Def.__bases__ = tuple(bases)

            ns0.Entity_Def.__init__(self, pname, ofwhat=TClist, extend=True, attributes=attributes, **kw)

    class ArrayOfPrivilegeDocumentClient_Def(ZSI.TCcompound.ComplexType, TypeDefinition):
        schema = "http://tempuri.org/"
        type = (schema, "ArrayOfPrivilegeDocumentClient")
        def __init__(self, pname, ofwhat=(), attributes=None, extend=False, restrict=False, **kw):
            ns = ns0.ArrayOfPrivilegeDocumentClient_Def.schema
            TClist = [GTD("http://tempuri.org/","PrivilegeDocumentClient",lazy=False)(pname=(ns,"PrivilegeDocumentClient"), aname="_PrivilegeDocumentClient", minOccurs=0, maxOccurs="unbounded", nillable=True, typed=False, encoded=kw.get("encoded"))]
            self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            ZSI.TCcompound.ComplexType.__init__(self, None, TClist, pname=pname, inorder=0, **kw)
            class Holder:
                typecode = self
                def __init__(self):
                    # pyclass
                    self._PrivilegeDocumentClient = []
                    return
            Holder.__name__ = "ArrayOfPrivilegeDocumentClient_Holder"
            self.pyclass = Holder

    class PrivilegeDocumentClient_Def(TypeDefinition):
        #complexType/complexContent extension
        schema = "http://tempuri.org/"
        type = (schema, "PrivilegeDocumentClient")
        def __init__(self, pname, ofwhat=(), extend=False, restrict=False, attributes=None, **kw):
            ns = ns0.PrivilegeDocumentClient_Def.schema
            TClist = [ZSI.TC.String(pname=(ns,"PersonId"), aname="_PersonId", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"PrivilegeDocumentSeria"), aname="_PrivilegeDocumentSeria", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"PrivilegeDocumentNumber"), aname="_PrivilegeDocumentNumber", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"PrivilegeDocumentName"), aname="_PrivilegeDocumentName", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"PrivilegeCategoryCode"), aname="_PrivilegeCategoryCode", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TCtimes.gDateTime(pname=(ns,"PrivilegeDocumentStart"), aname="_PrivilegeDocumentStart", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TCtimes.gDateTime(pname=(ns,"PrivilegeDocumentEnd"), aname="_PrivilegeDocumentEnd", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TCtimes.gDateTime(pname=(ns,"PrivilegeDocumentDeleted"), aname="_PrivilegeDocumentDeleted", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.Boolean(pname=(ns,"Uploaded"), aname="_Uploaded", minOccurs=1, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"Check"), aname="_Check", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), ZSI.TC.String(pname=(ns,"ProgramName"), aname="_ProgramName", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            attributes = self.attribute_typecode_dict = attributes or {}
            if extend: TClist += ofwhat
            if restrict: TClist = ofwhat
            if ns0.Entity_Def not in ns0.PrivilegeDocumentClient_Def.__bases__:
                bases = list(ns0.PrivilegeDocumentClient_Def.__bases__)
                bases.insert(0, ns0.Entity_Def)
                ns0.PrivilegeDocumentClient_Def.__bases__ = tuple(bases)

            ns0.Entity_Def.__init__(self, pname, ofwhat=TClist, extend=True, attributes=attributes, **kw)

    class RecipesClientSave_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "RecipesClientSave"
        schema = "http://tempuri.org/"
        def __init__(self, **kw):
            ns = ns0.RecipesClientSave_Dec.schema
            TClist = [ZSI.TC.String(pname=(ns,"clientId"), aname="_clientId", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), GTD("http://tempuri.org/","ArrayOfRecipeClient",lazy=False)(pname=(ns,"recipes"), aname="_recipes", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = ("http://tempuri.org/","RecipesClientSave")
            kw["aname"] = "_RecipesClientSave"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                typecode = self
                def __init__(self):
                    # pyclass
                    self._clientId = None
                    self._recipes = None
                    return
            Holder.__name__ = "RecipesClientSave_Holder"
            self.pyclass = Holder

    class RecipesClientSaveResponse_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "RecipesClientSaveResponse"
        schema = "http://tempuri.org/"
        def __init__(self, **kw):
            ns = ns0.RecipesClientSaveResponse_Dec.schema
            TClist = [GTD("http://tempuri.org/","ArrayOfRecipeClient",lazy=False)(pname=(ns,"RecipesClientSaveResult"), aname="_RecipesClientSaveResult", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = ("http://tempuri.org/","RecipesClientSaveResponse")
            kw["aname"] = "_RecipesClientSaveResponse"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                typecode = self
                def __init__(self):
                    # pyclass
                    self._RecipesClientSaveResult = None
                    return
            Holder.__name__ = "RecipesClientSaveResponse_Holder"
            self.pyclass = Holder

    class DoctorsClientSave_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "DoctorsClientSave"
        schema = "http://tempuri.org/"
        def __init__(self, **kw):
            ns = ns0.DoctorsClientSave_Dec.schema
            TClist = [ZSI.TC.String(pname=(ns,"clientId"), aname="_clientId", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), GTD("http://tempuri.org/","ArrayOfDoctorClient",lazy=False)(pname=(ns,"doctors"), aname="_doctors", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = ("http://tempuri.org/","DoctorsClientSave")
            kw["aname"] = "_DoctorsClientSave"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                typecode = self
                def __init__(self):
                    # pyclass
                    self._clientId = None
                    self._doctors = None
                    return
            Holder.__name__ = "DoctorsClientSave_Holder"
            self.pyclass = Holder

    class DoctorsClientSaveResponse_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "DoctorsClientSaveResponse"
        schema = "http://tempuri.org/"
        def __init__(self, **kw):
            ns = ns0.DoctorsClientSaveResponse_Dec.schema
            TClist = [GTD("http://tempuri.org/","ArrayOfDoctorClient",lazy=False)(pname=(ns,"DoctorsClientSaveResult"), aname="_DoctorsClientSaveResult", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = ("http://tempuri.org/","DoctorsClientSaveResponse")
            kw["aname"] = "_DoctorsClientSaveResponse"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                typecode = self
                def __init__(self):
                    # pyclass
                    self._DoctorsClientSaveResult = None
                    return
            Holder.__name__ = "DoctorsClientSaveResponse_Holder"
            self.pyclass = Holder

    class PersonClientSave_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "PersonClientSave"
        schema = "http://tempuri.org/"
        def __init__(self, **kw):
            ns = ns0.PersonClientSave_Dec.schema
            TClist = [ZSI.TC.String(pname=(ns,"clientId"), aname="_clientId", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), GTD("http://tempuri.org/","ArrayOfPersonClient",lazy=False)(pname=(ns,"persons"), aname="_persons", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = ("http://tempuri.org/","PersonClientSave")
            kw["aname"] = "_PersonClientSave"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                typecode = self
                def __init__(self):
                    # pyclass
                    self._clientId = None
                    self._persons = None
                    return
            Holder.__name__ = "PersonClientSave_Holder"
            self.pyclass = Holder

    class PersonClientSaveResponse_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "PersonClientSaveResponse"
        schema = "http://tempuri.org/"
        def __init__(self, **kw):
            ns = ns0.PersonClientSaveResponse_Dec.schema
            TClist = [GTD("http://tempuri.org/","ArrayOfPersonClient",lazy=False)(pname=(ns,"PersonClientSaveResult"), aname="_PersonClientSaveResult", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = ("http://tempuri.org/","PersonClientSaveResponse")
            kw["aname"] = "_PersonClientSaveResponse"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                typecode = self
                def __init__(self):
                    # pyclass
                    self._PersonClientSaveResult = None
                    return
            Holder.__name__ = "PersonClientSaveResponse_Holder"
            self.pyclass = Holder

    class PersonClientCheck_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "PersonClientCheck"
        schema = "http://tempuri.org/"
        def __init__(self, **kw):
            ns = ns0.PersonClientCheck_Dec.schema
            TClist = [ZSI.TC.String(pname=(ns,"clientId"), aname="_clientId", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded")), GTD("http://tempuri.org/","ArrayOfPersonClient",lazy=False)(pname=(ns,"persons"), aname="_persons", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = ("http://tempuri.org/","PersonClientCheck")
            kw["aname"] = "_PersonClientCheck"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                typecode = self
                def __init__(self):
                    # pyclass
                    self._clientId = None
                    self._persons = None
                    return
            Holder.__name__ = "PersonClientCheck_Holder"
            self.pyclass = Holder

    class PersonClientCheckResponse_Dec(ZSI.TCcompound.ComplexType, ElementDeclaration):
        literal = "PersonClientCheckResponse"
        schema = "http://tempuri.org/"
        def __init__(self, **kw):
            ns = ns0.PersonClientCheckResponse_Dec.schema
            TClist = [GTD("http://tempuri.org/","ArrayOfPersonClient",lazy=False)(pname=(ns,"PersonClientCheckResult"), aname="_PersonClientCheckResult", minOccurs=0, maxOccurs=1, nillable=False, typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = ("http://tempuri.org/","PersonClientCheckResponse")
            kw["aname"] = "_PersonClientCheckResponse"
            self.attribute_typecode_dict = {}
            ZSI.TCcompound.ComplexType.__init__(self,None,TClist,inorder=0,**kw)
            class Holder:
                typecode = self
                def __init__(self):
                    # pyclass
                    self._PersonClientCheckResult = None
                    return
            Holder.__name__ = "PersonClientCheckResponse_Holder"
            self.pyclass = Holder

# end class ns0 (tns: http://tempuri.org/)