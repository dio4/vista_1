# -*- coding: utf-8 -*-

import errno
import itertools
import os
import urlparse
import uuid
from PyQt4 import QtCore, QtGui
from socket import error as SocketError

from Exchange.R23.attach import DCExchangeSrv_client as srv
from Exchange.R23.attach.Types import AddressInfo, AttachError, AttachInfo, AttachResult, AttachedClientInfo, DeAttachQuery, DocumentInfo, PolicyInfo
from library.Utils import forceBool, forceDate, forceInt, forceRef, forceString, forceUnicode, fromDateTimeTuple, nameCase, toDateTimeTuple
from library.exception import CSynchronizeAttachException


class CR23AttachService(object):
    TestServerUrl = 'http://193.242.149.82:9090'
    ServiceUrl = 'EchangeServerTFOMS/DCExchangeSrv'

    LogFileName = 'attachServiceSoap.log'

    LoginPreference = 'AttachLogin'
    PasswordPreference = 'AttachPassword'
    UrlPreference = 'AttachUrl'
    DebugPreference = 'DebugSoapAttach'

    PermissionDenied = 10013
    ErrnoMessageMap = {
        PermissionDenied: u'Доступ к сервису заблокирован, проверьте настройки фаервола или отключите его'
    }
    NoConnectMessage = u'Нет связи с сервером ТФОМС'

    def __init__(self, username='', password='', senderCode='', url='', tracefilename=None, timeout=0):
        self.username = username
        self.password = password
        self.senderCode = senderCode
        parsedUrl = urlparse.urlparse(url or CR23AttachService.TestServerUrl)
        self.serviceUrl = '{0}://{1}/{2}'.format(parsedUrl.scheme, parsedUrl.netloc, CR23AttachService.ServiceUrl)
        self.tracefile = open(tracefilename, 'a') if isinstance(tracefilename, basestring) else tracefilename
        if self.tracefile:
            self.tracefile.write('Service URL: {0}\n'.format(self.serviceUrl))
            self.tracefile.flush()
        self.timeout = timeout

    @classmethod
    def getConnection(cls, url=None):
        if hasattr(cls, '_instance') and cls._instance is not None:
            return cls._instance

        cls._instance = cls.createConnection(url)
        return cls._instance

    @classmethod
    def createConnection(cls, url=None, timeout=0):
        prefs = QtGui.qApp.preferences.appPrefs
        username = forceString(prefs.get(CR23AttachService.LoginPreference, ''))
        debugLog = forceBool(prefs.get(CR23AttachService.DebugPreference, False))
        return cls(username=username,
                   senderCode=username,
                   password=forceString(prefs.get(CR23AttachService.PasswordPreference, '')),
                   url=url if url else forceString(prefs.get(CR23AttachService.UrlPreference, '')),
                   tracefilename=os.path.join(QtGui.qApp.logDir, CR23AttachService.LogFileName) if debugLog else None,
                   timeout=timeout)

    def getPort(self):
        locator = srv.DCExchangeSrvLocator()
        return locator.getDCExchangeSrvPort(url=self.serviceUrl, tracefile=self.tracefile, timeout=self.timeout or None)

    @staticmethod
    def getNoConnectMessage(errNo):
        u"""
        :type e: socket.error
        """
        errnoMsg = CR23AttachService.ErrnoMessageMap.get(errNo, '')
        return u'{0}: {1}'.format(CR23AttachService.NoConnectMessage,
                                  errnoMsg if errnoMsg else u'{errno %s: %s}' % (errNo, errno.errorcode.get(errNo, '')))

    @staticmethod
    def insertPackageInformation(req, senderCode, definition):
        orderpack = getattr(req, '_orderpack', None)
        if orderpack is None:
            orderpack = definition('_orderpack')
            req._orderpack = orderpack
        orderpack._p10_packinf = srv.ns0.cPackageInformation_Def('_p10_packinf')
        orderpack._p10_packinf._p10_pakagedate = toDateTimeTuple(QtCore.QDateTime.currentDateTime())
        orderpack._p10_packinf._p11_pakagesender = senderCode
        orderpack._p10_packinf._p12_pakageguid = str(uuid.uuid4())
        orderpack._p10_packinf._p13_zerrpkg = 0
        orderpack._p10_packinf._p14_errmsg = ''

    @staticmethod
    def getAttachResult(node):
        return AttachResult(attachId=node._f10_nzap,
                            errors=[AttachError(err._e10_ecd, forceUnicode(err._e11_ems))
                                    for err in node._f11_flkerrorList._f10_flkerror])

    @staticmethod
    def getBadResults(result, idList=None):
        packrespinf = result._p10_packrespinf
        errorList = packrespinf._r12_orerl._f10_orflker
        attachResultsMap = dict((attachResult.attachId, attachResult)
                                for attachResult in map(CR23AttachService.getAttachResult, errorList))
        if -1 in attachResultsMap:
            commonErrors = attachResultsMap[-1].errors
            del attachResultsMap[-1]
            if idList:
                for attachId in idList:
                    attachResultsMap.setdefault(attachId, AttachResult(attachId=attachId, errors=[])).errors.extend(commonErrors)

        if packrespinf._r10_packinf._p13_zerrpkg != 0 or packrespinf._r11_rsinf._r10_responcecode == AttachError.CriticalErrorPackageRejected:
            err = packrespinf._r11_rsinf
            packageError = AttachError(err._r10_responcecode, forceUnicode(err._responceMessage))
            if idList:
                for attachId in idList:
                    attachResultsMap.setdefault(attachId, AttachResult(attachId=attachId, errors=[])).errors.append(packageError)

        return attachResultsMap.values()

    @staticmethod
    def getResponsePackageErrors(responceInfo):
        if hasattr(responceInfo, '_p10_packinf') and responceInfo._p10_packinf._p13_zerrpkg != 0:
            return [AttachError(responceInfo._p10_packinf._p13_zerrpkg, forceUnicode(responceInfo._p10_packinf._p14_errmsg))]

        if hasattr(responceInfo, '_r10_packinf') and responceInfo._r10_packinf._p13_zerrpkg != 0:
            return [AttachError(responceInfo._r10_packinf._p13_zerrpkg, forceUnicode(responceInfo._r10_packinf._p14_errmsg))]

        return []

    @staticmethod
    def getPersonDef(clientInfo, pname):
        doc = clientInfo.document
        policy = clientInfo.policy

        person = srv.ns0.cPerson_Def(pname)
        person._a10_dct = policy.type
        person._a11_dcs = policy.serial
        person._a12_dcn = policy.number
        person._a13_smcd = policy.insurerCode
        person._a14_trcd = policy.insurerOKATO
        person._a15_pfio = clientInfo.lastName
        person._a16_pnm = clientInfo.firstName
        person._a17_pln = clientInfo.patrName
        person._a18_ps = unicode(clientInfo.sex)
        person._a19_pbd = toDateTimeTuple(clientInfo.birthDate)
        person._a20_pph = clientInfo.contacts
        person._a21_ps = doc.serial
        person._a22_pn = doc.number
        person._a23_dt = doc.type
        person._a24_sl = clientInfo.SNILS
        person._a25_enp = policy.enp

        return person

    @staticmethod
    def getClientInfo(node):
        doc = DocumentInfo(forceUnicode(node._a21_ps), forceUnicode(node._a22_pn), forceInt(node._a23_dt))
        policy = PolicyInfo(forceUnicode(node._a11_dcs), forceUnicode(node._a12_dcn), forceInt(node._a10_dct))
        return AttachedClientInfo(nameCase(forceUnicode(node._a15_pfio)),
                                  nameCase(forceUnicode(node._a16_pnm)),
                                  nameCase(forceUnicode(node._a17_pln)),
                                  forceDate(fromDateTimeTuple(node._a19_pbd)),
                                  doc=doc,
                                  policy=policy)

    @staticmethod
    def getAttachInfoDef(attach, changeSection=False):
        attachInfo = srv.ns0.cAttachInfo_Def('_p13_orcl')
        attachInfo._a10_aad = toDateTimeTuple(attach.begDate)
        attachInfo._a11_snisl = attach.doctorSNILS
        attachInfo._a12_sect = attach.sectionCode
        attachInfo._a13_attp = attach.attachType
        attachInfo._a14_pr = 4 if changeSection else attach.attachReason
        return attachInfo

    @staticmethod
    def getAttachDef(clientAttachInfo, changeSection=False):
        attachItem = srv.ns0.cAttach_Def('_l10_orcl')
        attachItem._p10_nzap = clientAttachInfo.attach.id
        attachItem._p11_mocd = clientAttachInfo.attach.orgCode
        attachItem._p12_pr = CR23AttachService.getPersonDef(clientAttachInfo, '_p12_pr')
        attachItem._p13_orcl = [CR23AttachService.getAttachInfoDef(clientAttachInfo.attach, changeSection)]
        return attachItem

    @staticmethod
    def getAttachListDef(clientAttachInfoList, changeSection=False):
        attachList = srv.ns0.cAttachList_Def('_p11_atachlist')
        attachList._l10_orcl = [CR23AttachService.getAttachDef(clientAttachInfo, changeSection)
                                for clientAttachInfo in clientAttachInfoList]
        return attachList

    @staticmethod
    def getDeAttachDef(clientAttachInfo):
        deattachItem = srv.ns0.cDeAttach_Def('_l10_orcl')
        deattachItem._p10_nzap = clientAttachInfo.attach.id
        deattachItem._p11_pr = CR23AttachService.getPersonDef(clientAttachInfo, '_p11_pr')
        deattachItem._p12_sect = clientAttachInfo.attach.sectionCode
        deattachItem._p13_add = toDateTimeTuple(QtCore.QDateTime.currentDateTime())
        deattachItem._p14_adr = clientAttachInfo.attach.deattachReason
        deattachItem._p15_mo = clientAttachInfo.attach.orgCode
        return deattachItem

    @staticmethod
    def getDeAttachListDef(clientAttachInfoList):
        deattachList = srv.ns0.cDeAttachList_Def('_p11_deatachlist')
        deattachList._l10_orcl = [CR23AttachService.getDeAttachDef(clientAttachInfo)
                                  for clientAttachInfo in clientAttachInfoList]
        return deattachList

    @staticmethod
    def getAttachedClientInfo(node):
        doc = DocumentInfo(forceUnicode(node._a28), forceUnicode(node._a29), forceInt(node._a30))
        policy = PolicyInfo(forceUnicode(node._a05), forceUnicode(node._a06), forceInt(node._a07),
                            enp=forceUnicode(node._a08),
                            insurerCode=forceUnicode(node._a32))
        attaches = [AttachInfo(begDate=fromDateTimeTuple(a._i1),
                               doctorSNILS=forceUnicode(a._i2),
                               sectionCode=forceUnicode(a._i3),
                               orgCode=forceUnicode(a._i4),
                               attachType=forceInt(a._i5))
                    for a in node._a09]
        regAddress = AddressInfo(forceUnicode(node._a12_r), forceUnicode(node._a13_c), forceUnicode(node._a14_n), forceUnicode(node._a15_u),
                                 forceUnicode(node._a16_d), forceUnicode(node._a17_k), forceUnicode(node._a18_k))
        locAddress = AddressInfo(forceUnicode(node._a19_pr), forceUnicode(node._a20_pc), forceUnicode(node._a21_pn), forceUnicode(node._a22_pu),
                                 forceUnicode(node._a23_pd), forceUnicode(node._a24_pk), forceUnicode(node._a25_pk))
        return [AttachedClientInfo(nameCase(forceUnicode(node._a01)),
                                   nameCase(forceUnicode(node._a02)),
                                   nameCase(forceUnicode(node._a03)),
                                   birthDate=forceDate(fromDateTimeTuple(node._a04)),
                                   sex=forceUnicode(node._a10),
                                   SNILS=forceUnicode(node._a31),
                                   doc=doc,
                                   policy=policy,
                                   attach=attach,
                                   regAddress=regAddress,
                                   locAddress=locAddress)
                for attach in attaches]

    @staticmethod
    def getDeAttachedClientInfo(node):
        p = node._p11_pr
        doc = DocumentInfo(forceUnicode(p._a21_ps), forceUnicode(p._a22_pn), forceInt(p._a23_dt))
        policy = PolicyInfo(forceUnicode(p._a11_dcs), forceUnicode(p._a12_dcn), forceInt(p._a10_dct),
                            insurerCode=forceUnicode(p._a13_smcd), insuranceArea=forceUnicode(p._a14_trcd))
        attach = AttachInfo(orgCode=forceUnicode(node._p15_mo),
                            sectionCode=forceUnicode(node._p12_sect),
                            endDate=forceDate(fromDateTimeTuple(node._p13_add)),
                            deattachReason=forceInt(node._p14_adr),
                            id=forceRef(node._p10_nzap))
        return AttachedClientInfo(nameCase(forceUnicode(p._a15_pfio)),
                                  nameCase(forceUnicode(p._a16_pnm)),
                                  nameCase(forceUnicode(p._a17_pln)),
                                  forceDate(fromDateTimeTuple(p._a19_pbd)),
                                  forceInt(p._a18_ps),
                                  doc=doc,
                                  policy=policy,
                                  attach=attach)

    @staticmethod
    def getAttachInfoList(node):
        return [AttachInfo(orgCode=node._p11_mocd,
                           sectionCode=item._a12_sect,
                           begDate=forceDate(fromDateTimeTuple(item._a10_aad)),
                           attachType=forceInt(item._a13_attp),
                           attachReason=forceInt(item._a14_pr),
                           doctorSNILS=forceUnicode(item._a11_snisl))
                for item in node._p13_orcl]

    @staticmethod
    def getDeAttachQueryRecordDef(deattachQueryInfo):
        record = srv.ns0.cDeAttachQueryForMORecord_Def('_p_10orcl')
        record._m01_nzap = deattachQueryInfo.id
        record._m02_mosrc = deattachQueryInfo.srcOrgCode
        record._m03_modes = deattachQueryInfo.destOrgCode
        record._m04_pep = CR23AttachService.getPersonDef(deattachQueryInfo.client, '_m04_pep')
        record._m05_nntf = deattachQueryInfo.number
        record._m06_dntf = toDateTimeTuple(deattachQueryInfo.date)
        return record

    @staticmethod
    def getDeAttachQueryInfo(node):
        return DeAttachQuery(
            id=forceRef(node._m01_nzap),
            srcOrgCode=forceUnicode(node._m02_mosrc),
            destOrgCode=forceUnicode(node._m03_modes),
            client=CR23AttachService.getClientInfo(node._m04_pep)
        )

    @staticmethod
    def getAttachMOSectionDef(personAttach):
        attachMOSection = srv.ns0.cAttachMOSection_Def('_d12_orcl')
        attachMOSection._s10_sect = personAttach.sectionCode
        attachMOSection._s11_dn = toDateTimeTuple(personAttach.begDate)
        attachMOSection._s12_num = None  # TODO: fill by section number (code)
        return attachMOSection

    @staticmethod
    def getAttachDoctorSectionDef(personAttachInfo):
        doctor = srv.ns0.cAttachDoctorSection_Def('_p12_orcl')
        doctor._d10_nzap = personAttachInfo.id
        doctor._d11_snils = personAttachInfo.SNILS
        doctor._d12_orcl = [
            CR23AttachService.getAttachMOSectionDef(personAttachInfo)
        ]
        doctor._d13_dn = toDateTimeTuple(personAttachInfo.begDate)
        doctor._d14_st = personAttachInfo.category
        doctor._d15_mo = personAttachInfo.orgCode
        doctor._d16_sr = personAttachInfo.lastName
        doctor._d17_nm = personAttachInfo.firstName
        doctor._d18_ln = personAttachInfo.patrName
        doctor._d19_br = toDateTimeTuple(personAttachInfo.birthDate)
        doctor._d20_ds = personAttachInfo.specialityCode

        return doctor


class CR23ClientAttachService(CR23AttachService):
    def getAttachInformation(self, clientInfo):
        u""" Проверка факта прикрепления пациента """
        try:
            port = self.getPort()

            req = srv.GetAttachInformation()
            req._username = self.username
            req._password = self.password
            req._sendercode = self.senderCode
            self.insertPackageInformation(req, self.senderCode, srv.ns0.cAttachInformationPackage_Def)

            req._orderpack._p11_pr = self.getPersonDef(clientInfo, '_p11_pr')

            resp = port.GetAttachInformation(req)
            responcepack = resp._responcepack
            responceInfo = responcepack._p10_packrespinf

            responceErrors = self.getResponsePackageErrors(responceInfo)
            if responceErrors:
                raise CSynchronizeAttachException(u','.join(map(unicode, responceErrors)))

            attachList = responcepack._p11_atachlist._l10_orcl
            if not attachList:
                errorList = [AttachError(e._e10_ecd, forceUnicode(e._e11_ems))
                             for e in responceInfo._r12_orerl._f10_orflker[0]._f11_flkerrorList._f10_flkerror]
                if AttachError.AttachesNotFound in [e.code for e in errorList]:
                    return AttachResult(result=AttachedClientInfo())
                else:
                    return AttachResult(errors=errorList)

            node = attachList[0]  # len > 1 ?
            client = self.getClientInfo(node._p12_pr)
            client.attaches = self.getAttachInfoList(node)

            return AttachResult(result=client)

        except SocketError as e:
            raise CSynchronizeAttachException(CR23AttachService.getNoConnectMessage(e))

        except Exception:
            raise

        finally:
            if self.tracefile:
                self.tracefile.flush()

    def getAttachedList(self):
        u"""
        Генератор:
        запрашивает списки прикрепленного населения (начиная с индекса 0)
        возвращает длину списка, итератор по нему
        """
        nextId, attachedList = self.getAttachedListIterator(0)
        yield attachedList  # (length, iterator)

        while nextId > 0:
            nextId, attachedList = self.getAttachedListIterator(nextId)
            yield attachedList  # (length, iterator)

    def getAttachedListIterator(self, startId):
        u"""
        [Список прикрепленных (сгенеренные ZSI-типы)] -> (длина списка, итератор по списку из AttachedClientInfo)
        """
        nextId, attachedList = self.getAttachListByRange(startId)
        return nextId, (len(attachedList), itertools.chain.from_iterable(itertools.imap(self.getAttachedClientInfo, attachedList)))

    def getAttachListByRange(self, startId):
        try:
            port = self.getPort()

            req = srv.GetAttachListByRange()
            req._username = self.username
            req._password = self.password
            req._sendercode = self.senderCode
            req._startid = startId
            req._isadres = True
            self.insertPackageInformation(req, self.senderCode, srv.ns0.GetAttachListByRange_Def)

            resp = port.GetAttachListByRange(req)
            responseErrors = self.getResponsePackageErrors(resp._orderpack)
            if responseErrors:
                raise CSynchronizeAttachException(u','.join(map(unicode, responseErrors)))

            nextId = resp._orderpack._p11_nid
            attachedList = resp._orderpack._p12_alist._l10_orcl

            if self.tracefile:
                self.tracefile.write('GetAttachListByRange(startId=%s): %s items' % (startId, len(attachedList)))
                self.tracefile.flush()

            return nextId, attachedList

        except CSynchronizeAttachException:
            QtGui.qApp.logCurrentException()
            raise

        except SocketError as e:
            QtGui.qApp.logCurrentException()
            raise CSynchronizeAttachException(CR23AttachService.getNoConnectMessage(e.errno))

        except Exception:
            QtGui.qApp.logCurrentException()
            raise

        finally:
            if self.tracefile:
                self.tracefile.flush()

    def getAttachListAct(self, year, month):
        u""" Получить список прикрепленных граждан по диапазону согласно актам-сверок на первое число месяца следующего за отчетным """
        nextStartId, attachedClientList = self.getAttachListByRangeAct(year, month, 0)
        while nextStartId > 0:
            nextStartId, clientList = self.getAttachListByRangeAct(year, month, nextStartId)
            attachedClientList.extend(clientList)

        return map(self.getAttachedClientInfo, attachedClientList)

    def getAttachListByRangeAct(self, year, month, startId):
        try:
            port = self.getPort()

            req = srv.GetAttachListByRangeAct()
            req._username = self.username
            req._password = self.password
            req._sendercode = self.senderCode
            req._startid = startId
            req._monthact = month
            req._yearact = year

            resp = port.GetAttachListByRangeAct(req)
            orderpack = resp._orderpack

            nextStartId = resp._orderpack._p11_nid
            attachClientInfoList = orderpack._p12_alist._l10_orcl

            return nextStartId, attachClientInfoList

        except SocketError as e:
            raise CSynchronizeAttachException(CR23AttachService.getNoConnectMessage(e.errno))

        except Exception:
            QtGui.qApp.logCurrentException()
            raise

        finally:
            if self.tracefile:
                self.tracefile.flush()

    def getDeattachByDate(self, date):
        u""" Получить список открепившихся граждан с определенной даты {date} по текущую """
        try:
            port = self.getPort()

            req = srv.GetDeAttachByDate()
            req._username = self.username
            req._password = self.password
            req._sendercode = self.senderCode
            req._controldate = toDateTimeTuple(date)

            resp = port.GetDeAttachByDate(req)
            responceErrors = self.getResponsePackageErrors(resp)
            if responceErrors:
                raise CSynchronizeAttachException(u','.join(map(unicode, responceErrors)))

            deattachList = resp._orderpack._p11_deatachlist._l10_orcl

            if self.tracefile:
                self.tracefile.write('GetDeAttachByDate(): %s items' % len(deattachList))
                self.tracefile.flush()

            return map(self.getDeAttachedClientInfo, deattachList)

        except SocketError as e:
            QtGui.qApp.logCurrentException()
            raise CSynchronizeAttachException(CR23AttachService.getNoConnectMessage(e.errno))

        except Exception:
            QtGui.qApp.logCurrentException()
            raise

        finally:
            if self.tracefile:
                self.tracefile.flush()

    def makeAttach(self, clientAttachInfoList, changeSection=False):
        u""" Выполнить действие по прикреплению пациентов """
        try:
            port = self.getPort()

            orgCode = clientAttachInfoList[0].attach.orgCode or self.senderCode

            req = srv.MakeAttachAction()
            req._username = orgCode
            req._password = self.password
            req._sendercode = orgCode
            self.insertPackageInformation(req, orgCode, srv.ns0.cAttachPersonPackage_Def)

            req._orderpack._p11_atachlist = self.getAttachListDef(clientAttachInfoList, changeSection)

            resp = port.MakeAttachAction(req)
            return self.getBadResults(resp._orderpack, [c.attach.id for c in clientAttachInfoList])

        except SocketError as e:
            raise CSynchronizeAttachException(CR23AttachService.getNoConnectMessage(e.errno))

        except Exception:
            raise

        finally:
            if self.tracefile:
                self.tracefile.flush()

    def makeDeAttach(self, clientAttachInfoList):
        u""" Выполнить действие по откреплению пациентов """
        try:
            port = self.getPort()

            orgCode = clientAttachInfoList[0].attach.orgCode or self.senderCode

            req = srv.MakeDeAttachAction()
            req._username = orgCode
            req._password = self.password
            req._sendercode = orgCode
            self.insertPackageInformation(req, orgCode, srv.ns0.cDeAttachPersonPackage_Def)

            req._orderpack._p11_deatachlist = self.getDeAttachListDef(clientAttachInfoList)

            resp = port.MakeDeAttachAction(req)
            return self.getBadResults(resp._orderpack, [c.attach.id for c in clientAttachInfoList])

        except SocketError as e:
            raise CSynchronizeAttachException(CR23AttachService.getNoConnectMessage(e.errno))

        except Exception:
            raise

        finally:
            if self.tracefile:
                self.tracefile.flush()

    def sendDeAttachQuery(self, deattachQueryList):
        u""" Передать информацию в ТФОМС КК о запросах на открепление от МО """
        try:
            port = self.getPort()

            req = srv.SendQueryForDeAttachForMO()
            req._username = self.username
            req._password = self.password
            req._sendercode = self.senderCode
            self.insertPackageInformation(req, self.senderCode, srv.ns0.cDeAttachQueryForMOPackage_Def)

            req._orderpack._p11_list = srv.ns0.cDeAttachQueryForMOList_Def('_p11_list')
            req._orderpack._p11_list._p_10orcl = map(self.getDeAttachQueryRecordDef, deattachQueryList)

            resp = port.SendQueryForDeAttachForMO(req)
            responceErrors = self.getResponsePackageErrors(resp._orderpack._p10_packrespinf)

            return [AttachResult(attachId=deattachQuery.id, errors=responceErrors) for deattachQuery in deattachQueryList]

        except SocketError as e:
            raise CSynchronizeAttachException(CR23AttachService.getNoConnectMessage(e.errno))

        except Exception:
            raise

        finally:
            if self.tracefile:
                self.tracefile.flush()

    def getDeAttachQuery(self, date):
        u""" Получить список записей на открепление от МО """
        try:
            port = self.getPort()

            req = srv.GetQueryForDeAttachForMO()
            req._username = self.username
            req._password = self.password
            req._sendercode = self.senderCode
            req._synhdate = toDateTimeTuple(date)

            resp = port.GetQueryForDeAttachForMO(req)
            responceErrors = self.getResponsePackageErrors(resp._orderpack)
            if responceErrors:
                raise CSynchronizeAttachException(u','.join(map(unicode, responceErrors)))

            return map(self.getDeAttachQueryInfo, resp._orderpack._p11_list._p_10orcl)

        except SocketError as e:
            raise CSynchronizeAttachException(CR23AttachService.getNoConnectMessage(e.errno))

        except Exception:
            raise

        finally:
            if self.tracefile:
                self.tracefile.flush()


class CR23PersonAttachService(CR23AttachService):
    def sendAttachDoctorSectionInfo(self, personAttachInfoList):
        u""" Передать сведения об участках в МО и медицинском персонале """
        try:
            port = self.getPort()

            req = srv.SendAttachDoctorSectionInformation()
            req._username = self.username
            req._password = self.password
            req._sendercode = self.senderCode
            self.insertPackageInformation(req, self.senderCode, srv.ns0.cAttachDoctorSection_Def)

            req._orderpack._p11_mocd = personAttachInfoList[0].orgCode or self.senderCode
            req._orderpack._p12_orcl = map(self.getAttachDoctorSectionDef, personAttachInfoList)

            resp = port.SendAttachDoctorSectionInformation(req)
            return self.getBadResults(resp._responcepack, [p.id for p in personAttachInfoList])

        except SocketError as e:
            raise CSynchronizeAttachException(CR23AttachService.getNoConnectMessage(e.errno))

        except Exception:
            raise

        finally:
            if self.tracefile:
                self.tracefile.flush()

    # Не используется, т.к. не храним информацию о прикрепленных домах
    def sendAttachMOStreetSection(self, recordList):
        u""" Передать информацию о домах или домовладениях относящихся к врачебному участку в рамках медицинской организации """
        port = self.getPort()
        try:
            req = srv.SendAttachMoStreetSection()
            req._username = self.username
            req._password = self.password
            req._sendercode = self.senderCode
            self.insertPackageInformation(req, self.senderCode, srv.ns0.cAttachMoStreetSection_Def)

            resp = port.SendAttachMoStreetSection(req)

        except SocketError as e:
            raise CSynchronizeAttachException(CR23AttachService.getNoConnectMessage(e.errno))

        except Exception as e:
            QtGui.qApp.logCurrentException()

        finally:
            if self.tracefile:
                self.tracefile.flush()

    # Не используется, т.к. не храним информацию о прикрепленных домах
    def getAttachMOStreetSection(self):
        u""" Извлечь информацию о домах или домовладениях относящихся к врачебному участку в рамках медицинской организации """
        port = self.getPort()
        try:
            req = srv.GetAttachMoStreetSection()
            req._username = self.username
            req._password = self.password
            req._sendercode = self.senderCode

            resp = port.GetAttachMoStreetSection(req)

            return None

        except SocketError as e:
            raise CSynchronizeAttachException(CR23AttachService.getNoConnectMessage(e.errno))

        except Exception as e:
            QtGui.qApp.logCurrentException()

        finally:
            if self.tracefile:
                self.tracefile.flush()


class CR23LoginAccessService(CR23AttachService):
    TestConnectResultMap = {
        0: u'Ошибка соединения',
        1: u'Подключение установлено'
    }
    LoginErrorMap = {
        1 : u'Операция завершилась успешно',
        0 : u'Неизвестная ошибка',
        -1: u'Данные неполны',
        -2: u'Пароль указан неверно',
        -3: u'Указанный логин уже зарегистрирован в БД'
    }

    def makeTestConnect(self):
        u""" Проверка связи с сервером МИАЦ """
        try:
            port = self.getPort()
            req = srv.MakeTestConnect()
            resp = port.MakeTestConnect(req)

            return CR23LoginAccessService.TestConnectResultMap[resp._retresult]

        except SocketError as e:
            raise CSynchronizeAttachException(CR23AttachService.getNoConnectMessage(e.errno))

        except Exception:
            raise

        except CSynchronizeAttachException:
            raise

        finally:
            if self.tracefile:
                self.tracefile.flush()

    def setLoginAccess(self, username, password, senderCode, oldpassword=None):
        u""" Регистрация организации в сервисе """
        port = self.getPort()
        try:
            req = srv.SetLoginAccess()
            req._username = username
            req._password = password
            req._sendercode = senderCode
            req._oldpassword = oldpassword

            resp = port.SetLoginAccess(req)
            return CR23LoginAccessService.LoginErrorMap[resp._return]

        except SocketError as e:
            raise CSynchronizeAttachException(CR23AttachService.getNoConnectMessage(e.errno))

        except Exception:
            return CR23LoginAccessService.LoginErrorMap[0]

        finally:
            if self.tracefile:
                self.tracefile.flush()

    def setLoginAccessMultiple(self, password):
        u""" Регистрация всех подразделений организации в сервисе (с одним паролем) """
        db = QtGui.qApp.db
        tableOrgStructure = db.table('OrgStructure')
        bookkeeperRecords = db.getRecordList(tableOrgStructure, cols=['bookkeeperCode', 'name'],
                                             where=[tableOrgStructure['deleted'].eq(0),
                                                    tableOrgStructure['bookkeeperCode'].ne('')],
                                             isDistinct=True, group='bookkeeperCode', order='bookkeeperCode')
        results = []
        for record in bookkeeperRecords:
            code = forceString(record.value('bookkeeperCode'))
            name = forceString(record.value('name'))
            result = self.setLoginAccess(code, password, code)
            results.append(name + ': ' + result)
        return u',\n'.join(results)
