# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2014 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

from PyQt4 import QtCore, QtGui

from library.Utils          import forceInt, forceString
from Orgs.Utils             import getOrgStructureDescendants
from Reports.Report         import CReport
from Reports.ReportBase     import createTable, CReportBase
from Reports.StatReportDDFoundIllnesses import MKBinString

from Ui_ReportF14Children import Ui_ReportF14Children



def selectData(params, lstOrgStructure):
    db = QtGui.qApp.db
    begDate         = params.get('begDate')
    endDate         = params.get('endDate')
    order           = params.get('order')
    orgStructureId  = params.get('orgStructureId')
    typeHosp        = params.get('typeHosp')
    cmbOrgStructure = params.get('cmbOrgStructure')
    eventTypeId     = params.get('eventTypeId')
    eventPurposeId  = params.get('eventPurposeId')
    financeId       = params.get('financeId')

    tableAction = db.table('Action')
    tableEvent = db.table('Event')
    tableEventType = db.table('EventType')

    cond = [tableAction['endDate'].dateGe(begDate),
            tableAction['endDate'].dateLe(endDate)]

    if order:
        cond.append(tableEvent['order'].eq(order))
    if eventTypeId:
        cond.append(tableEvent['eventType_id'].eq(eventTypeId))
    if eventPurposeId:
        cond.append(tableEventType['purpose_id'].eq(eventPurposeId))
    if typeHosp == 1:
        cond.extend([u'OrgStructure.hasDayStationary = 0', 'OrgStructure.type != 4'])
    elif typeHosp == 2:
        cond.append(u'OrgStructure.hasDayStationary = 1')
    elif typeHosp == 3:
        cond.append('aps_amb.value IS NOT NULL')
    if lstOrgStructure and cmbOrgStructure:
        tableOrgStructure = db.table('OrgStructure')
        cond.append(tableOrgStructure['id'].eq(lstOrgStructure))
    if orgStructureId and not cmbOrgStructure:
        tableOrgStructure = db.table('OrgStructure')
        cond.append(tableOrgStructure['id'].inlist(getOrgStructureDescendants(orgStructureId)))
    if financeId:
        cond.append(tableAction['finance_id'].eq(financeId))

    stmt = u'''SELECT act.MKB,
                      COUNT(DISTINCT Action.id) AS leaved,
                      COUNT(DISTINCT  IF(Event.`order` = 2, Event.id, NULL)) AS extraLeaved,
                      COUNT(DISTINCT IF(aps.value = 'СМП', Action.id, NULL)) AS SMPLeaved,
                      COUNT(DISTINCT IF(age(Client.birthDate, Action.endDate) < 1, Action.id, NULL)) AS SmallLeaved,
                      COUNT(DISTINCT IF(rbResult.federalCode IN (5, 6, 11, 12), Action.id, NULL)) AS DeadAll,
                      COUNT(DISTINCT IF(ActionProperty_String.value = 'умер' AND age(Client.birthDate, Action.endDate) < 1, Action.id, NULL)) AS DeadSmallLeaved,
                      sum(IF(OrgStructure.hasDayStationary = 1, datediff(Event.execDate, Event.setDate) + 1, datediff(Event.execDate, Event.setDate))) AS duration,
                      sum(IF(age(Client.birthDate, Event.setDate) < 1, IF(OrgStructure.hasDayStationary = 1, datediff(Event.execDate, Event.setDate) + 1, datediff(Event.execDate, Event.setDate)), 0)) AS durationSmall,
                      COUNT(IF(rbEventTypePurpose.code = '5', Event.id, NULL)) AS vskr,
                      COUNT(IF(rbEventTypePurpose.code = '5' AND rbResult.code in ('1', '2', '3', '4', '5'), Event.id, NULL)) AS rash
                FROM ActionType
                    INNER JOIN Action ON Action.actionType_id = ActionType.id AND Action.deleted = 0
                    INNER JOIN Event ON Event.id = Action.event_id AND Event.deleted = 0
                    INNER JOIN EventType ON EventType.id = Event.eventType_id
                    INNER JOIN rbEventTypePurpose ON rbEventTypePurpose.id = EventType.purpose_id
                    INNER JOIN Client ON Client.id = Event.client_id
                    INNER JOIN ActionPropertyType ON ActionPropertyType.actionType_id = ActionType.id AND ActionPropertyType.name = 'Исход госпитализации' AND ActionPropertyType.deleted = 0
                    LEFT JOIN ActionProperty ON ActionProperty.action_id = Action.id AND ActionProperty.type_id = ActionPropertyType.id AND ActionProperty.deleted = 0
                    LEFT JOIN ActionProperty_String ON ActionProperty_String.id = ActionProperty.id
                    INNER JOIN Action act ON act.event_id = Action.event_id AND act.id = (SELECT MAX(a.id)
                                                                                          FROM ActionType at
                                                                                            INNER JOIN Action a ON a.actionType_id = at.id AND a.deleted = 0
                                                                                          WHERE a.event_id = Event.id AND at.flatCode = 'moving' AND at.deleted = 0)
                    LEFT JOIN ActionProperty ap_os ON ap_os.action_id = act.id AND ap_os.type_id = (SELECT apt.id
                                                                                                    FROM ActionPropertyType apt
                                                                                                    WHERE apt.actionType_id = act.actionType_id AND apt.name = 'Отделение пребывания' AND apt.deleted = 0) AND ap_os.deleted = 0

                    LEFT JOIN ActionProperty_OrgStructure ON ActionProperty_OrgStructure.id = ap_os.id
                    LEFT JOIN OrgStructure ON OrgStructure.id = ActionProperty_OrgStructure.value
                    LEFT JOIN Action act_received ON act_received.event_id = Event.id AND act_received.actionType_id = (SELECT at.id
                                                                                                                        FROM ActionType at
                                                                                                                        WHERE at.flatCode = 'received' AND at.deleted = 0) AND act_received.deleted = 0
                    LEFT JOIN ActionProperty ap ON ap.action_id = act_received.id AND ap.type_id = (SELECT apt.id
                                                                                                    FROM ActionPropertyType apt
                                                                                                        INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'received' AND at.deleted = 0
                                                                                                    WHERE apt.name = 'Прочие направители' AND apt.deleted = 0) AND ap.deleted = 0
                    LEFT JOIN ActionProperty ap_amb ON ap_amb.action_id = act_received.id AND ap_amb.type_id = (SELECT apt.id
                                                                                                                FROM ActionPropertyType apt
                                                                                                                    INNER JOIN ActionType at ON at.id = apt.actionType_id AND at.flatCode = 'received' AND at.deleted = 0
                                                                                                                WHERE apt.name = 'Причина отказа от госпитализации' AND apt.deleted = 0) AND ap_amb.deleted = 0
                    LEFT JOIN ActionProperty_String aps ON aps.id = ap.id
                    LEFT JOIN ActionProperty_String aps_amb ON aps_amb.id = ap_amb.id
                    LEFT JOIN rbResult ON rbResult.id = Event.result_id
                WHERE ActionType.flatCode = 'leaved' AND %s AND ActionType.deleted = 0
                GROUP BY act.MKB''' % (db.joinAnd(cond))

    return db.query(stmt)

class CReportF14Children(CReport):
    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Состав больных в стационаре, сроки и исходы лечения')

    def getSetupDialog(self, parent):
        result = CF14Children(parent)
        result.setTitle(self.title())
        return result

    def build(self, params):
        resultSet = [
            [u'Всего', u'1.0', u'A00-T98', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'в том числе: некоторые инфекционные и паразитарные болезни', u'2.0', u'A00-B99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: кишечные инфекции', u'2.1', u'A00-A09', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'туберкулез органов дыхания', u'2.2', u'A15-A16', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'менингококковая инфекция', u'2.3', u'A39', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'сепсис', u'2.4', u'A40-A41', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'инфекции, передающиеся преимущественно половым путем', u'2.5', u'A50-A64', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'острый полиомиелит', u'2.6', u'A80', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'вирусный гепатит', u'2.7', u'B15-B19', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезнь, вызыванная ВИЧ', u'2.8', u'B20-B24', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'новообразования', u'3.0', u'C00-D48', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'в том числе: злокачественные новообразования', u'3.1', u'C00-C97', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: злокачественные новообразования лимфатической и кроветворной тканей', u'3.1.1', u'C81-C96', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: фолликулярная (нодулярная) неходжкинская лимфома', u'3.1.1.1', u'C82', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'мелкоклеточная (диффузная) неходжкинская лимфома', u'3.1.1.2', u'C83.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'мелкоклеточная с расщепленными ядрами (диффузная)неходжкинская лимфома', u'3.1.1.3', u'C83.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'крупноклеточная (диффузная)неходжкинская лимфома', u'3.1.1.4', u'C83.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'иммунобластная (диффузная)неходжкинская лимфома', u'3.1.1.5', u'C83.4', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие типы диффузных неходжкинских лимфом', u'3.1.1.6', u'C83.8', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'диффузная неходжкинская лимфома неуточненная', u'3.1.1.7', u'C83.9', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'периферические и кожные T-клеточные лимфомы', u'3.1.1.8', u'C84', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: другие и неуточненные T-клеточные лимфомы', u'3.1.1.8.1', u'C84.5', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие и неуточненные типы неходжкинской лимфомы', u'3.1.1.9', u'C85', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'макроглобулинэмия Вальденстрема', u'3.1.1.10', u'C88.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'хронический лимфоцитарный лейкоз', u'3.1.1.11', u'C91.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'хронический миелоидный лейкоз', u'3.1.1.12', u'C92.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'доброкачественные новообразования', u'3.2', u'D10-D36', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: лейомиома матки', u'3.2.1', u'D25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'доброкачественные новообразования яичника', u'3.2.2', u'D27', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни крови, кроветворных органов и отдельные нарушения, вовлекающие иммунный механизм', u'4.0', u'D50-D89', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: анемия', u'4.1', u'D50-D64', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'апластические анемии', u'4.1.1', u'D60-D61', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'нарушения свертываемости крови', u'4.2', u'D65-D69', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'в том числе: диссеминированное внутрисосудистое свертывание (синдром дефибринации)', u'4.2.1', u'D65', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гемофилия', u'4.2.2', u'D66-D68', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'отдельные нарушения, вовлекающие иммунный механизм', u'4.3', u'D80-D89', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни эндокринной системы, расстройства питания и нарушения обмена веществ', u'5.0', u'E00-E89', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: гипотиреоз', u'5.1', u'E01-E03', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'тиреотоксикоз (гипертиреоз)', u'5.2', u'E05', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'тиреоидит', u'5.3', u'E06', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'сахарный диабет', u'5.4', u'E10-E14', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'в том числе: сахарный диабет инсулинзависимый', u'5.4.1', u'E10', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'сахарный диабет инсулиннезависимый', u'5.4.2', u'E11', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них с поражением глаз (из стр.5.4)', u'5.4.3', u'E10.3, E11.3, E12.3, E13.3, E14.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гиперфункция гипофиза', u'5.5', u'E22', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гипопитуитаризм', u'5.6', u'E23.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'несахарный диабет', u'5.7', u'E23.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'адреногенитальнве расстройства', u'5.8', u'E25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'дисфункция яичников', u'5.9', u'E28', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'дисфункция яичек', u'5.10', u'E29', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'ожирение', u'5.11', u'E66', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'фенилкетонурия', u'5.12', u'E70.0, E70.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'нарушения обмена галактозы (галактоземия)', u'5.13', u'E74.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезнь Гоше', u'5.14', u'E75.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'нарушения обмена гликозамино-гликанов (мукополисахаридоз)', u'5.15', u'E76.0-E76.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'муковисцидоз', u'5.16', u'E84', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'психические расстройства и расстройства поведения', u'6.0', u'F01-F99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: психические расстройства и расстройства поведения, связанные с употреблением психоактивных веществ', u'6.1', u'F10-F19', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни нервной системы', u'7.0', u'G00-G99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: воспалительные болезни центральной нервной системы', u'7.1', u'G00-G09', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: бактериальный менингит', u'7.1.1', u'G00', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'энцефалит, миелит и энцефаломиелит', u'7.1.2', u'G04', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'системные атрофии, поражающие преимущественно центральную нервную систему', u'7.2', u'G10-G12', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'экстрапирамидные и другие двигательные нарушения', u'7.3', u'G20, G21, G23-G25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них:болезнь Паркинсона', u'7.3.1', u'G20', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие экстрапирамидные и двигательные нарушения', u'7.3.2', u'G25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие дегенеративные болезни нервной системы', u'7.4', u'G30-G31', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: болезнь Альцгеймера', u'7.4.1', u'G30', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'демиелинизирующие болезни центральной нервной системы', u'7.5', u'G35-G37', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: рассеянный склероз', u'7.5.1', u'G35', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'эпизодические и пароксизмальные расстройства', u'7.6', u'G40-G47', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: эпилепсия, эпилептический статус', u'7.6.1', u'G40-G41', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'преходящие транзиторные церебральные ишемические приступы [атаки] и родственные синдромы', u'7.6.2', u'G45', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'поражения отдельных нервов, нервных корешков и сплетений, полиневропатии и другие поражения периферической нервной системы', u'7.7', u'G50-G64', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: синдром Гийена-Барре', u'7.7.1', u'G61.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни нервно-мышечного синапса и мышц', u'7.8', u'G70-G73', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: миастения', u'7.8.1', u'G70.0, G70.2, G70.9', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'мышечная дистрофия Дюшенна', u'7.8.2', u'G71.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'церебральный паралич и другие паралитические синдромы', u'7.9', u'G80-G83', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: церебральный паралич', u'7.9.1', u'G80', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'расстройства вегетативной (автономной)', u'7.10', u'G90', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'сосудистые миелопатии', u'7.11', u'G95.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни глаза и его придаточного аппарата', u'8.0', u'H00-H59', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: язва роговицы', u'8.1', u'H16.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'катаракты', u'8.2', u'H25-H26', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'дегенерация макулы и заднего полюса', u'8.3', u'H35.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'глаукома', u'8.4', u'H40', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'неврит зрительного нерва', u'8.5', u'H46', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'слепота и пониженное зрение', u'8.6', u'H54', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: слепота обоих глаз', u'8.6.1', u'H54.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни уха и сосцевидного отростка', u'9.0', u'H60-H95', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни среднего уха и сосцевидного отростка', u'9.1', u'H65-H66, H68-H74', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: острый отит', u'9.1.1', u'H65.0, H65.1, H66.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'хронический отит', u'9.1.2', u'H65.2-H65.4, H66.1-H66.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни слуховой (евстахиевой) трубы', u'9.1.3', u'H68-H69', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'перфорация барабанной перепонки', u'9.1.4', u'H72', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие болезни среднего уха и сосцевидного отростка', u'9.1.5', u'H74', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни внутреннего уха', u'9.2', u'H80, H81, H83', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: отосклероз', u'9.2.1', u'H80', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезнь Меньера', u'9.2.2', u'H81.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'ондуктивная и нейросенсорная', u'9.3', u'H90', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: кондуктивная потеря слуха двусторонняя', u'9.3.1', u'H90.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'нейросенсорная потеря слуха двусторонняя', u'9.3.2', u'H90.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни системы кровообращения', u'10.0', u'I00-I99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: острая ревматическая лихорадка', u'10.1', u'I00-I02', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'хронические ревматические болезни сердца', u'10.2', u'I05-I09', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни, характеризующиеся повышенным кровяным давлением', u'10.3', u'I10-I13', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: эссенциальная гипертензия', u'10.3.1', u'I10', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гипертензивная болезнь сердца (гипертоническая болезнь с преимущественным поражением сердца)', u'10.3.2', u'I11', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гипертензивная (гипертоническая) болезнь с преимущественным поражением почек', u'10.3.3', u'I12', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гипертензивная (гипертоническая) болезнь с преимущественным поражением сердца и почек', u'10.3.4', u'I13', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'ишемические болезни сердца', u'10.4', u'I20-I25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: стенокардия', u'10.4.1', u'I20', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из нее: нестабильная стенокардия', u'10.4.1.1', u'I20.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'острый инфаркт миокарда', u'10.4.2', u'I21', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'повторный инфаркт миокарда', u'10.4.3', u'I22', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие формы острых ишемических болезней сердца', u'10.4.4', u'I24', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'хроническая ишемическая болезнь сердца', u'10.4.5', u'I25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из нее постинфарктный кардиосклероз', u'10.4.5.1', u'I25.8', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'легочная эмболия', u'10.5', u'I26', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие болезни сердца', u'10.6', u'I30-I52', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: острый и подострый эндокардит', u'10.6.1', u'I33', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'острый миокардит', u'10.6.2', u'I40', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'кардиомиопатия', u'10.6.3', u'I42', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'предсердно-желудочковая [атриовентрикулярная] блокада', u'10.6.4', u'I44.0-I44.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'желудочковая тахикардия', u'10.6.5', u'I47.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'фибрилляция и трепетание предсердий', u'10.6.6', u'I48', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'цереброваскулярные болезни', u'10.7', u'I60-I69', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: субарахноидальное кровоизлияние', u'10.7.1', u'I60', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'внутримозговые и другие внутричерепные кровоизлияния', u'10.7.2', u'I61,I62', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'инфаркт мозга', u'10.7.3', u'I63', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'инсульт неуточненный, как кровоизлияние или инфаркт', u'10.7.4', u'I64', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'закупорка и стеноз прецеребральных, це- ребральных артерий, не приводящих к инфаркту мозга и другие цереброваскулярные болезни', u'10.7.5', u'I65-I66', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие цереброваскулярные болезни', u'10.7.6', u'I67', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'в том числе: церебральный атеросклероз', u'10.7.6.1', u'I67.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'атеросклероз артерий конечностей, тромбангиит облитерирующий', u'10.8', u'I70.2,I73.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни вен, лимфатических сосудов и лимфатических узлов', u'10.9', u'I80-I89', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: флебит и тромбофлебит', u'10.9.1', u'I80', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'тромбоз портальной вены', u'10.9.2', u'I81', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'варикозное расширение вен нижних конечностей', u'10.9.3', u'I83', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни органов дыхания', u'11.0', u'J00-J98', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: острые респираторные верхних дыхательных путей', u'11.1', u'J00-J06', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: острый ларингит и трахеит', u'11.1.1', u'J04', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'острый обструктивный ларингит [круп] и эпиглоттит', u'11.1.2', u'J05', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'грипп', u'11.2', u'J10-J11', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'пневмония', u'11.3', u'J12-J18', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'острые респираторные инфекции', u'11.4', u'J20-J22', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'аллергический ринит (поллиноз)', u'11.5', u'J30.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'хронические болезни миндалин и аденоидов, перитонзиллярный абсцесс', u'11.6', u'J35-J36', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'бронхит хронический и неуточненный, эмфизема', u'11.7', u'J40-J43', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другая хроническая обструктивная легочная болезнь, бронхоэктатическая болезнь', u'11.8', u'J44, J47', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'астма; астматический статус', u'11.9', u'J45, J46', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'др. интерстициальные легочные болезни, гнойные и некротические состояния нижних дыхат. путей, др. б-ни плевры', u'11.10', u'J84-J94', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни органов пищеварения', u'12.0', u'K00-K92', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: язва желудка и двенадцатиперстной кишки', u'12.1', u'K25-K26', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'гастрит и дуоденит', u'12.2', u'K29', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'грыжи', u'12.3', u'K40-K46', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'неинфекционный энтерит и колит', u'12.4', u'K50-K52', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: болезнь Крона', u'12.4.1', u'K50', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'язвенный колит', u'12.4.2', u'K51', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие болезни кишечника', u'12.5', u'K55-K63', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них:паралитический илеус и непроходимость кишечника без грыжи', u'12.5.1', u'K56', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'дивертикулярная болезнь кишечника', u'12.5.2', u'K57', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'геморрой', u'10.9.4', u'K64', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'перитонит', u'12.6', u'K65', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни печени', u'12.7', u'K70-K76', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: фиброз и цирроз печени', u'12.7.1', u'K74', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни желчного пузыря, желчевыводящих путей', u'12.8', u'K80-K83', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни поджелудочной железы', u'12.9', u'K85-K86', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'острый панкреатит', u'12.9.1', u'K85', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни кожи и подкожной клетчатки', u'13.0', u'L00-L99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них псориаз, всего', u'13.1', u'L40', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'в том числе: псориаз артропатический', u'13.1.1', u'L40.5', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'дискоидная красная волчанка', u'13.2', u'L93.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'локализованная склеродермия', u'13.3', u'L94.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни костно-мышечной системы и соединительной ткани', u'14.0', u'M00-M99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: артропатии', u'14.1', u'M00-M25', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: реактивные артропатии', u'14.1.1', u'M02', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'серопозитивный и другие ревматоидные артриты', u'14.1.2', u'M05-M06', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'юношеский (ювенильный) артрит', u'14.1.3', u'M08', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'артрозы', u'14.1.4', u'M15-M19', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'системные поражения соединительной ткани', u'14.2', u'M30-M35', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'деформирующие дорсопатии', u'14.3', u'M40-M43', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'спондилопатии', u'14.4', u'M45-M49', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'синовиты и теносиновиты', u'14.5', u'M65-M68', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'остеопатии и хондропатии', u'14.6', u'M80-M94', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: остеопорозы', u'14.6.1', u'M80-M81', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни мочеполовой системы', u'15.0', u'N00-N99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: гломерулярные, тубулоинтерстициальные болезни почек, почечная недостаточность и другие болезни почки и мочеточника', u'15.1', u'N00-N15, N25-N28', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'почечная недостаточность', u'15.2', u'N17-N19', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'мочекаменная болезнь', u'15.3', u'N20-N21, N23', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'другие болезни мочевой системы', u'15.4', u'N30-N32, N34-N36, N39', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезни предстательной железы', u'15.5', u'N40-N42', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'доброкачественная дисплазия молочной железы', u'15.6', u'N60', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'воспалительные болезни женских тазовых органов', u'15.7', u'N70-N76', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: сальпингит и оофорит', u'15.7.1', u'N70', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'эндометриоз', u'15.8', u'N80', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'расстройства менструаций', u'15.9', u'N91-N94', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'женское бесплодие', u'15.10', u'N97', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'беременность, роды и послеродовой период', u'16.0', u'O00-O99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'отдельные состояния, возникающие в перинатальном периоде', u'17.0', u'P00-P96', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'врожденные аномалии (пороки развития), деформации и хромосомные нарушения', u'18.0', u'Q00-Q99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: врожденные аномалии [пороки развития]', u'18.1', u'Q00-Q07', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'врожденные аномалии системы кровообращения', u'18.2', u'Q20-Q28', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'врожденные аномалии кишечника', u'18.3', u'Q41, Q42', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'болезнь Гиршпрунга', u'18.4', u'Q43.1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'врожденные аномалии тела и шейки матки, другие врожденные аномалии женских половых', u'18.5', u'Q51-Q52', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'неопределенность пола и псевдогермафродитизм', u'18.6', u'Q56', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'врожденный ихтиоз', u'18.7', u'Q80', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'нейрофиброматоз (незлокачественный)', u'18.8', u'Q85.0', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'синдром Дауна', u'18.9', u'Q90', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'симптомы, признаки и отклонения от нормы, выявленные при клинических и лабораторных исследованиях, не классифицированные в других рубриках', u'19.0', u'R00-R99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'травмы, отравления и некоторые другие последствия воздействия внешних причин', u'20.0', u'S00-T98', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: переломы', u'20.1', u'S02, S12, S22, S32, S42, S52, S62, S72, S82, S82, T02, T08, T10, T12, T14.2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: переломы черепа и лицевых костей', u'20.1.1', u'S02', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'внутричерепные травмы', u'20.2', u'S06', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: термические и химические ожоги', u'20.3', u'T20-T32', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'отравления лекарственными средствами, медикаментами и биологическими веществами, токсическое действие веществ преимущественно немедицинского назначения', u'20.4', u'T36-T65', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: токсическое действие алкоголя', u'20.4.1', u'T51', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'Кроме того:факторы, влияющие на состояние здоровья и обращения в учреждения здравоохранения', u'21.0', u'Z00-Z99', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'из них: носительство инфекционной болезни', u'21.1', u'Z22', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [u'наличие илеостомы, колостомы', u'21.2', u'Z93.2, Z93.3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        lstOrgStructureDict = params.get('lstOrgStructure', None)
        lstOrgStructure = lstOrgStructureDict.keys()
        query = selectData(params, lstOrgStructure)
        self.setQueryText(forceString(query.lastQuery()))
        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(self.title())
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.insertBlock()

        tableColumns = [
                ( '38%', [u'Наименование болезни' ], CReportBase.AlignLeft),
                ( '4%',  [u'№ строки' ], CReportBase.AlignLeft),
                ( '10%', [u'Код по МКБ Х пересмотра'], CReportBase.AlignLeft),
                ( '5%',  [u'Состав больных в стационаре, сроки и исходы лечения',  u'Выписано больных'], CReportBase.AlignLeft),
                ( '5%',  [u'', u'Из них достав. по экстр показан.' ], CReportBase.AlignLeft),
                ( '6%',  [u'', u'Из них больных, доставл. СМП'], CReportBase.AlignLeft),
                ( '6%',  [u'', u'В т.ч. в возр. до 1 года'], CReportBase.AlignLeft),
                ( '6%',  [u'', u'Проведено выписанными койко-дней'], CReportBase.AlignLeft),
                ( '6%',  [u'', u'В т.ч. в возр. до 1 года'], CReportBase.AlignLeft),
                ( '5%',  [u'', u'Умерло', u'Всего'], CReportBase.AlignLeft),
                ( '5%',  [u'', u'', u'Из них', u'патологоанатомических вскрытий'], CReportBase.AlignLeft),
                ( '5%',  [u'', u'', u'', u'Установлено расхождений диагнозов'], CReportBase.AlignLeft),
                ( '5%',  [u'', u'', u'В т.ч. в возр. до 1 года'], CReportBase.AlignLeft)]

        table = createTable(cursor, tableColumns)
        table.mergeCells(0, 0, 4, 1)
        table.mergeCells(0, 1, 4, 1)
        table.mergeCells(0, 2, 4, 1)
        table.mergeCells(0, 3, 1,10)
        table.mergeCells(1, 3, 3, 1)
        table.mergeCells(1, 4, 3, 1)
        table.mergeCells(1, 5, 3, 1)
        table.mergeCells(1, 6, 3, 1)
        table.mergeCells(1, 7, 3, 1)
        table.mergeCells(1, 8, 3, 1)
        table.mergeCells(1, 9, 1, 4)
        table.mergeCells(2, 9, 2, 1)
        table.mergeCells(2, 10, 1, 2)
        table.mergeCells(2, 12, 2, 1)

        while query.next():
            record = query.record()
            code = forceString(record.value('MKB'))
            leaved = forceInt(record.value('leaved'))
            extraLeavel = forceInt(record.value('extraLeaved'))
            SMPLeaved = forceInt(record.value('SMPLeaved'))
            SmallLeaved = forceInt(record.value('SmallLeaved'))
            duration = forceInt(record.value('duration'))
            durationSmall = forceInt(record.value('durationSmall'))
            DeadAll = forceInt(record.value('DeadAll'))
            DeadSmallLeaved = forceInt(record.value('DeadSmallLeaved'))
            vskr = forceInt(record.value('vskr'))
            rash = forceInt(record.value('rash'))

            for row in resultSet:
                if MKBinString(code, row[2]):
                    row[3] += leaved
                    row[4] += extraLeavel
                    row[5] += SMPLeaved
                    row[6] += SmallLeaved
                    row[7] += duration
                    row[8] += durationSmall
                    row[9] += DeadAll
                    row[10] += vskr
                    row[11] += rash
                    row[12] += DeadSmallLeaved

        for list in resultSet:
            i = table.addRow()
            for index, value in enumerate(list):
                table.setText(i, index, value)
        return doc

class CF14Children(QtGui.QDialog, Ui_ReportF14Children):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.lstOrgStructure.setTable('OrgStructure')
        self.cmbFinance.setTable('rbFinance')
        self.cmbEventType.setTable('EventType')
        self.cmbEventPurpose.setTable('rbEventTypePurpose')

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbTypeHosp.setCurrentIndex(params.get('typeHosp', 0))
        self.cmbOrder.setCurrentIndex(params.get('order', 0))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbFinance.setValue(params.get('financeId', None))
        self.cmbEventType.setValue(params.get('eventTypeId', None))
        self.cmbEventPurpose.setValue(params.get('eventPurpossId', None))
        self.chkOrgStructure.setChecked(params.get('cmbOrgStructure', False))
        self.on_chkOrgStructure_clicked(self.chkOrgStructure.isChecked())

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['typeHosp'] = self.cmbTypeHosp.currentIndex()
        result['order'] = self.cmbOrder.currentIndex()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['lstOrgStructure'] = self.lstOrgStructure.nameValues()
        result['cmbOrgStructure'] = self.chkOrgStructure.isChecked()
        result['financeId'] = self.cmbFinance.value()
        result['eventTypeId'] = self.cmbEventType.value()
        result['eventPerposeId'] = self.cmbEventPurpose.value()
        return result

    @QtCore.pyqtSlot(bool)
    def on_chkOrgStructure_clicked(self, checked):
        self.lstOrgStructure.setVisible(checked)
        self.cmbOrgStructure.setVisible(not checked)