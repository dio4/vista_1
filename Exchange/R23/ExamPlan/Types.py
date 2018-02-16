# -*- coding: utf-8 -*-

from Exchange.R23.ExamPlan.Utils import ExamKind, ExamStep
from Exchange.R23.TFOMS.Types import Identifiable, PersonItem


class PlanQuantity(Identifiable):
    _typeName = 'cevPlanQuantity'

    def __init__(self, rid=None, orgCode=None, kind=None, year=None, month=None, quantity=None):
        super(PlanQuantity, self).__init__(rid)
        self.orgCode = orgCode
        self.kind = kind
        self.year = year
        self.month = month
        self.quantity = quantity

    def toSOAP(self, qty, factory):
        super(PlanQuantity, self).toSOAP(qty, factory)
        qty.code_mo = self.orgCode
        qty.kind = self.kind
        qty.year = self.year
        qty.mnth = self.month
        qty.quantity = self.quantity

    @classmethod
    def deserialize(cls, obj):
        return cls(
            rid=obj.rid,
            orgCode=str(obj.code_mo),
            kind=obj.kind,
            year=obj.year,
            month=obj.mnth,
            quantity=obj.quantity
        )

    def __repr__(self):
        return u'<PlanQty y: %s, m: %s, k: %s, q: %s>' % (self.year, self.month, self.kind, self.quantity)


class PlanDate(Identifiable):
    _typeName = 'cevPlanDate'

    def __init__(self, rid=None, orgCode=None, kind=None, method=None, date=None, address=None, comment=None):
        super(PlanDate, self).__init__(rid)
        self.orgCode = orgCode
        self.kind = kind
        self.method = method
        self.date = date
        self.address = address
        self.comment = comment

    def toSOAP(self, pd, factory):
        super(PlanDate, self).toSOAP(pd, factory)
        pd.code_mo = self.orgCode
        pd.kind = self.kind
        pd.meth = self.method
        pd.evdt = self.toPyDateTime(self.date)
        pd.address = self.address
        pd.comment = self.comment

    @classmethod
    def deserialize(cls, obj):
        addr = getattr(obj, 'address', None)
        comm = getattr(obj, 'comment', None)
        return cls(rid=obj.rid,
                   orgCode=unicode(obj.code_mo),
                   kind=obj.kind,
                   method=obj.meth,
                   date=cls.toQDate(obj.evdt),
                   address=unicode(addr) if addr else None,
                   comment=unicode(comm) if comm else None)

    def __repr__(self):
        return u'<PlanDate %s>' % self.date


class OrgContact(Identifiable):
    _typeName = 'cevContact'

    def __init__(self, rid=None, orgCode=u'', phone=u'', comment=None):
        super(OrgContact, self).__init__(rid)
        self.orgCode = orgCode
        self.phone = phone
        self.comment = comment

    def toSOAP(self, contact, factory):
        super(OrgContact, self).toSOAP(contact, factory)
        contact.code_mo = self.orgCode
        contact.phone = self.phone
        contact.comment = self.comment

    @classmethod
    def deserialize(cls, obj):
        return cls(rid=obj.rid,
                   orgCode=unicode(obj.code_mo),
                   phone=unicode(obj.phone),
                   comment=unicode(obj.comment))

    def __repr__(self):
        return u'<OrgContact {0}: "{1}" ({2})>'.format(self.orgCode, self.phone, self.comment)


class FactInvoice(Identifiable):
    _typeName = 'cevFactInvc'

    def __init__(self, rid=None, year=None, month=None, orgCode=None, insurerCode=None, begDate=None, endDate=None, date=None,
                 invoiceStatus=None, resultCode=None, person=None):
        super(FactInvoice, self).__init__(rid)
        self.year = year
        self.month = month
        self.orgCode = orgCode
        self.insurerCode = insurerCode
        self.begDate = begDate  # type: QtCore.QDate
        self.endDate = endDate  # type: QtCore.QDate
        self.date = date  # type: QtCore.QDate
        self.invoiceStatus = invoiceStatus
        self.resultCode = resultCode
        self.person = person  # type: PersonItem

    def toSOAP(self, fi, factory):
        fi.year = self.year
        fi.month = self.month
        fi.code_mo = self.orgCode
        fi.smo_code = self.insurerCode
        fi.invcdatn = self.toPyDateTime(self.begDate)
        fi.invcdato = self.toPyDateTime(self.endDate)
        fi.invcdate = self.toPyDateTime(self.date)
        fi.invcstts = self.invoiceStatus
        fi.ishob = self.resultCode
        fi.person = self.person.serialize(factory)

    @classmethod
    def deserialize(cls, obj):
        return cls(
            rid=obj.rid,
            year=obj.year,
            month=obj.month,
            orgCode=obj.code_mo,
            insurerCode=obj.smo_code,
            begDate=cls.toQDate(obj.invcdatn),
            endDate=cls.toQDate(obj.invcdato),
            date=cls.toQDate(obj.invcdate),
            invoiceStatus=obj.invcstts,
            resultCode=obj.ishob,
            person=PersonItem.deserialize(obj.person)
        )


class FactInfo(Identifiable):
    _typeName = 'cevFactInfo'

    def __init__(self, rid=None, insurerCode=None, orgCode=None, date=None, method=None, step=None, person=None):
        super(FactInfo, self).__init__(rid)
        self.insurerCode = insurerCode
        self.orgCode = orgCode
        self.date = date  # type: QtCore.QDate
        self.method = method
        self.step = step
        self.person = person  # type: PersonItem

    def toSOAP(self, factInfo, factory):
        factInfo.smo_code = self.insurerCode
        factInfo.code_mo = self.orgCode
        factInfo.infodate = self.toPyDateTime(self.date)
        factInfo.infometh = self.method
        factInfo.infostep = self.step
        factInfo.person = self.person.serialize(factory)

    @classmethod
    def deserialize(cls, obj):
        return cls(
            rid=obj.rid,
            insurerCode=obj.smo_code,
            orgCode=obj.code_mo,
            date=cls.toQDate(obj.infodate),
            method=obj.infometh,
            step=obj.infostep,
            person=PersonItem.deserialize(obj.person)
        )


class FactExec(Identifiable):
    _typeName = 'cevFactExec'

    def __init__(self, rid=None, insurerCode=None, orgCode=None, date=None, step=None, person=None):
        super(FactExec, self).__init__(rid)
        self.insurerCode = insurerCode
        self.orgCode = orgCode
        self.date = date  # type: QtCore.QDate
        self.step = step
        self.person = person  # type: PersonItem

    def toSOAP(self, factExec, factory):
        # factExec.smo_code = self.insurerCode or None
        super(FactExec, self).toSOAP(factExec, factory)
        factExec.code_mo = self.orgCode or None
        factExec.execdate = self.toPyDateTime(self.date)
        factExec.execstep = self.step
        factExec.person = self.person.serialize(factory)

    @classmethod
    def deserialize(cls, obj):
        return cls(
            rid=obj.rid,
            insurerCode=unicode(obj.smo_code),
            orgCode=obj.code_mo,
            date=cls.toQDate(obj.execdate),
            step=obj.execstep,
            person=PersonItem.deserialize(obj.person)
        )

    def __repr__(self):
        return u'<FactExec {0}: {1} ({2})>'.format(self.date.toPyDate() if self.date else None, ExamStep.getName(self.step), self.person)


class PlanItem(Identifiable):
    _typeName = 'cevPlan'

    def __init__(self, rid=None, kind=None, year=None, month=None, orgCode=None, sectionCode=None, category=None, person=None):
        super(PlanItem, self).__init__(rid)
        self.kind = kind
        self.year = year
        self.month = month
        self.orgCode = orgCode
        self.sectionCode = sectionCode
        self.category = category
        self.person = person  # type: PersonItem

    def toSOAP(self, plan, factory):
        super(PlanItem, self).toSOAP(plan, factory)
        plan.kind = self.kind
        plan.year = self.year
        plan.mnth = self.month
        plan.code_mo = self.orgCode
        plan.dfSection = self.sectionCode
        plan.category = self.category
        plan.person = self.person.serialize(factory)

    def __repr__(self):
        return u'<PlanItem {0}.{1} ({2}): {3}>'.format(self.month, self.year, ExamKind.getName(self.kind), self.person)