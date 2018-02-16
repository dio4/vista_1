# -*- coding: utf-8 -*-
import datetime
import logging

from Exchange.R23.ExamPlan.Types import FactExec, FactInfo, FactInvoice, OrgContact, PlanDate, PlanQuantity
from Exchange.R23.TFOMS.Service import CServiceTFOMS, handleExceptions, logExceptions
from Exchange.R23.TFOMS.Types import ResponsePackage


class CExamPlanServiceTFOMS(CServiceTFOMS):
    u""" Клиент сервиса «Диспансеризация и профилактические осмотры» ТФОМС КК """

    @logExceptions(onexcept=[])
    def getPlanQuantities(self, year, month=None):
        u"""
        Планируемые количества профилактических мероприятий
        :type year: int
        :type month: int
        :rtype: list of PlanQuantity
        """
        try:
            resp = self.cli.service.getEvPlanQtys(
                username=self._username,
                password=self._password,
                sendercode=self._senderCode,
                year=year,
                mnth=month
            )
        except TypeError as e:
            logger = logging.getLogger('suds.client')
            logger.exception(e)
            logger.info(u'Service description:\n%s' % self.cli)
            raise
        evPlanQuantity = resp.evPlanQtys.evPlanQuantity if resp and resp.evPlanQtys and resp.evPlanQtys.evPlanQuantity else []
        return [PlanQuantity.deserialize(planQty) for planQty in evPlanQuantity]

    @logExceptions(onexcept=[])
    def getContacts(self):
        u"""
        Список контактных телефонов МО
        :rtype: list of OrgContact
        """
        resp = self.cli.service.getEvContacts(
            username=self._username,
            password=self._password,
            sendercode=self._senderCode
        )
        evContacts = resp.evContacts.evContact if resp and resp.evContacts and resp.evContacts.evContact else []
        return [OrgContact.deserialize(evContact) for evContact in evContacts]

    @handleExceptions
    def sendContacts(self, contacts):
        u"""
        Передача списка контактных телефонов
        :type contacts: list of OrgContact
        :rtype: ResponsePackage
        """
        evContacts = self.cli.factory.create('cevContacts')
        evContacts.evContact = [contact.serialize(self.cli.factory) for contact in contacts]

        orderpack = self.cli.factory.create('cevContactsPackage')
        orderpack.p10_packinf = self.getPackageInformation()
        orderpack.evContacts = evContacts

        resp = self.cli.service.putEvContacts(
            orderpack=orderpack,
            username=self._username,
            password=self._password,
            sendercode=self._senderCode
        )
        return ResponsePackage.deserialize(resp)

    @logExceptions(onexcept=[])
    def getPlanDates(self):
        u"""
        Планируемые даты профилактических мероприятий
        :rtype: list of PlanDate
        """
        resp = self.cli.service.getEvPlanDates(
            username=self._username,
            password=self._password,
            sendercode=self._senderCode
        )
        evPlanDate = resp.evPlanDates.evPlanDate if resp and resp.evPlanDates and resp.evPlanDates.evPlanDate else []
        return [PlanDate.deserialize(pd) for pd in evPlanDate]

    @handleExceptions
    def sendPlanDates(self, planDates):
        u"""
        Передача планируемых дат проф. мероприятий
        :type planDates: list of PlanDate
        :rtype: ResponsePackage
        """
        evPlanDates = self.cli.factory.create('cevPlanDates')
        evPlanDates.evPlanDate = [planDate.serialize(self.cli.factory) for planDate in planDates]

        orderpack = self.cli.factory.create('cevPlanDatesPackage')
        orderpack.p10_packinf = self.getPackageInformation()
        orderpack.evPlanDates = evPlanDates

        resp = self.cli.service.putEvPlanDates(
            orderpack=orderpack,
            username=self._username,
            password=self._password,
            sendercode=self._senderCode
        )
        return ResponsePackage.deserialize(resp)

    @handleExceptions
    def sendPlanItems(self, planList):
        u"""
        Передача персонифицированного списка лиц, подлежащих проведению проф. мероприятий
        :type planList: list of PlantItem
        :rtype: ResponsePackage
        """
        evPlanList = self.cli.factory.create('cevPlanList')
        evPlanList.evPlan = [planItem.serialize(self.cli.factory) for planItem in planList]

        orderpack = self.cli.factory.create('cevPlanListPackage')
        orderpack.p10_packinf = self.getPackageInformation()
        orderpack.evPlanList = evPlanList

        resp = self.cli.service.putEvPlanList(
            orderpack=orderpack,
            username=self._username,
            password=self._password,
            sendercode=self._senderCode
        )
        return ResponsePackage.deserialize(resp)

    @logExceptions(onexcept=[])
    def getFactInfos(self, insurerCode, infoDate):
        u"""
        Данные об информировании граждан от СМО
        """
        resp = self.cli.service.getEvFactInfos(
            username=self._username,
            password=self._password,
            sendercode=self._senderCode,
            smo_code=insurerCode,
            infodate=datetime.datetime.combine(infoDate, datetime.datetime.min.time())
        )
        evFactInfos = resp.evFactInfos.evFactInfo if resp and resp.evFactInfos and resp.evFactInfos.evFactInfo else []
        return [FactInfo.deserialize(info) for info in evFactInfos]

    def iterFactInvoices(self, year, month):
        u"""
        :rtype: generator[list[FactInvoice]]
        """
        page = 1
        completed = False
        while not completed:
            invoices = self.getFactInvoices(year, month, page)
            if invoices:
                yield invoices
                page += 1
            else:
                completed = True

    @logExceptions(onexcept=[])
    def getFactInvoices(self, year, month, page=1):
        resp = self.cli.service.getEvFactInvcs(
            username=self._username,
            password=self._password,
            sendercode=self._senderCode,
            year=year,
            mnth=month,
            page=page
        )
        evFactInvcs = resp.evFactInvcs if resp and resp.evFactInvcs else []
        return [FactInvoice.deserialize(evFactInvc) for evFactInvc in evFactInvcs]

    @handleExceptions
    def sendFactExecs(self, factExecs):
        u"""
        Передача сведений по факту проведения профилактических мероприятий
        :type factExecs: list of FactExec
        """
        evFactExecs = self.cli.factory.create('cevFactExecs')
        evFactExecs.evFactExec = [factExec.serialize(self.cli.factory) for factExec in factExecs]

        orderpack = self.cli.factory.create('cevFactExecsPackage')
        orderpack.p10_packinf = self.getPackageInformation()
        orderpack.evFactExecs = evFactExecs

        resp = self.cli.service.putEvFactExecs(
            orderpack=orderpack,
            username=self._username,
            password=self._password,
            sendercode=self._senderCode
        )
        return ResponsePackage.deserialize(resp)
