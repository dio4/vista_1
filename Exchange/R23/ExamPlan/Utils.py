# -*- coding: utf-8 -*-

from library.Enum import CEnum
from library.Utils import reverseDict


class Month(CEnum):
    nameMap = {
        1 : u'Январь',
        2 : u'Февраль',
        3 : u'Март',
        4 : u'Апрель',
        5 : u'Май',
        6 : u'Июнь',
        7 : u'Июль',
        8 : u'Август',
        9 : u'Сентябрь',
        10: u'Октябрь',
        11: u'Ноябрь',
        12: u'Декабрь',
    }


class Quarter(CEnum):
    nameMap = {
        1: u'Первый',
        2: u'Второй',
        3: u'Третий',
        4: u'Четвертый',
    }
    monthMap = {
        1: (1, 2, 3),
        2: (4, 5, 6),
        3: (7, 8, 9),
        4: (10, 11, 12)
    }

    @classmethod
    def months(cls, quarter):
        return cls.monthMap.get(quarter, [])


class ExamStatus(CEnum):
    u""" Статус отправки в ТФОМС (ClientExaminationPlan.status) """
    NotSent = 0
    Sent = 1
    UpdatedByTFOMS = 2

    nameMap = {
        NotSent       : u'Не отправлено',
        Sent          : u'Отправлено',
        UpdatedByTFOMS: u'Обновлено по информации из ТФОМС'
    }


class ExamKind(CEnum):
    u""" Вид проф. мероприятия (ClientExaminationPlan.kind)"""
    Dispensary = 1
    Preventive = 2

    nameMap = {
        Dispensary: u'Диспансеризация',
        Preventive: u'Проф. осмотр'
    }

    eventProfileRegionalCodeMap = {
        Dispensary: ['211'],
        Preventive: ['261']
    }

    @classmethod
    def getEventProfileCodes(cls, examKind):
        return cls.eventProfileRegionalCodeMap.get(examKind, [])


class ExamKindSpecials(CEnum):
    u""" Вид проф. мероприятия: доп. значения (для фильтров) """
    DispExamDisabled = -1
    nameMap = {
        DispExamDisabled: u'Диспансеризация инвалидов'
    }


class ExamMethod(CEnum):
    u""" Метод осуществления проф. мероприятия """

    InOrg = 1
    MobileTeam = 2
    Delivery = 3

    nameMap = {
        InOrg     : u'По адресу МО',
        MobileTeam: u'Выезд мобильной бригады в отдаленный район',
        Delivery  : u'Доставка граждан из отдаленного района в МО'
    }


class ExamStep(CEnum):
    u""" Шаг исполнения проф. мероприятия (ClientExaminationPlan.step) """
    D1_Refused = 101
    D1_Started = 102
    D1_Finished = 103
    D1_SentToStage2 = 104
    D2_Refused = 105
    D2_Started = 106
    D2_Finished = 107
    D2_Finished_SentToDS = 108
    D2_Finished_SentTo24HS = 109

    P_Refused = 201
    P_Started = 202
    P_Finished = 203
    P_Finished_SentToDS = 204
    P_Finished_SentTo24HS = 205

    nameMap = {
        D1_Refused            : u'Отказался от диспансеризации',
        D1_Started            : u'Начал диспансеризацию',
        D1_Finished           : u'Завершил 1 этап диспансеризации',
        D1_SentToStage2       : u'Направлен на 2 этап диспансеризации',
        D2_Refused            : u'Отказался от прохождения 2 этапа диспансеризации',
        D2_Started            : u'Начал 2 этап диспансеризации',
        D2_Finished           : u'Завершил 2 этап диспансеризации',
        D2_Finished_SentToDS  : u'Завершил 2 этап диспансеризации и направлен на госпитализацию в дневной стационар',
        D2_Finished_SentTo24HS: u'Завершил 2 этап диспансеризации и направлен на госпитализацию в круглосуточный стационар',

        P_Refused             : u'Отказался от осмотра',
        P_Started             : u'Начал осмотр',
        P_Finished            : u'Завершил осмотр',
        P_Finished_SentToDS   : u'Завершил осмотр и направлен на госпитализацию в дневной стационар',
        P_Finished_SentTo24HS : u'Завершил осмотр и направлен на госпитализацию в круглосуточный стационар'
    }
    startingSteps = (D1_Started,
                     D2_Started,
                     P_Started)
    finishingSteps = (D1_Finished,
                      D1_SentToStage2,
                      D2_Finished,
                      D2_Finished_SentToDS,
                      D2_Finished_SentTo24HS,
                      P_Finished_SentToDS,
                      P_Finished_SentTo24HS)
    dispStageSteps = {
        1: range(D1_Refused,
                 D2_Refused + 1),
        2: range(D2_Started,
                 D2_Finished_SentTo24HS + 1)
    }
    dispStageMap = reverseDict(dispStageSteps)

    examKindSteps = {
        ExamKind.Dispensary: range(D1_Refused,
                                   D2_Finished_SentTo24HS + 1),
        ExamKind.Preventive: range(P_Refused,
                                   P_Finished_SentTo24HS + 1)
    }
    kindMap = reverseDict(examKindSteps)

    resultCodeMap = {
        ExamKind.Dispensary: reverseDict({
            D1_Finished           : ['312', '317', '318', '355', '356'],
            D1_SentToStage2       : ['353', '357', '358'],
            D2_Refused            : ['316'],
            D2_Finished           : ['312'],
            D2_Finished_SentToDS  : ['306'],
            D2_Finished_SentTo24HS: ['305']
        }),
        ExamKind.Preventive: reverseDict({
            P_Finished           : ['312', '343', '344', '345'],
            P_Finished_SentToDS  : ['306'],
            P_Finished_SentTo24HS: ['305']
        })
    }

    @classmethod
    def getExamKind(cls, execStep):
        return cls.kindMap.get(execStep, None)

    @classmethod
    def getDispStage(cls, execStep):
        return cls.dispStageMap.get(execStep)

    @classmethod
    def getStarting(cls, kind, dispStage=None):
        return cls.P_Started if kind == ExamKind.Preventive \
            else cls.D2_Started if dispStage == 2 else cls.D1_Started

    @classmethod
    def getStep(cls, examKind, dispStage=None, resultCode=''):
        return cls.resultCodeMap.get(examKind, {}).get(resultCode) \
            if resultCode else cls.getStarting(examKind, dispStage)

    @classmethod
    def getInvoiceStep(cls, invoiceStatus, resultCode):
        examKind, dispStage = InvoiceStatus.getKindStage(invoiceStatus)
        return cls.getStep((examKind, dispStage), resultCode)


class InvoiceStatus(CEnum):
    Dispensary1 = 1
    Dispensary2 = 2
    Preventive = 3

    kindStageMap = {
        Dispensary1: (ExamKind.Dispensary, 1),
        Dispensary2: (ExamKind.Dispensary, 2),
        Preventive: (ExamKind.Preventive, None)
    }

    @classmethod
    def getKindStage(cls, invoiceStatus):
        return cls.kindStageMap.get(invoiceStatus, (None, None))


class PersonCategory(CEnum):
    u""" Категория гражданина """
    General = 0
    HasBenefits = 1

    nameMap = {
        General    : u'Общие основания',
        HasBenefits: u'Имеет льготу по проф. мероприятиям'
    }


class InfoMethod(CEnum):
    u""" Метод информирования """
    SMS = 1
    EMail = 2
    Phone = 3
    Mail = 4
    Other = 5

    nameMap = {
        SMS  : u'SMS',
        EMail: u'e-mail',
        Phone: u'Телефон',
        Mail : u'Почта',
        Other: u'Прочее'
    }


class InfoStep(CEnum):
    u""" Этап информирования """
    Step1Invitation = 1
    Step1Reminder = 2
    Step2Invitation = 3
    Step2Reminder = 4

    nameMap = {
        Step1Invitation: u'Приглашение на профилактическое мероприятие',
        Step1Reminder  : u'Напоминание о прохождении мероприятия',
        Step2Invitation: u'Приглашение на второй этап диспансеризации',
        Step2Reminder  : u'Напоминание о приглашении на второй этап диспансеризации'
    }


class ExamPlanError(CEnum):
    OrgCodeError = 601
    InsurerCodeError = 602
    ExamKindError = 603
    ExamMethodError = 604
    InfoMethodError = 605
    InfoStepError = 606
    ExamStepError = 607
    ForeignOrgCode = 610
    ExamPlanDateError = 611
    ExamPlanYearMonthError = 612
    InfoDateError = 613
    ExecDateError = 614
    ForeignInsurerCode = 615
    NonIdentifiedPerson = 616
    AttachNotSynced = 617
    PlanningError = 618
    Duplication = 619
    MethodNotAllowed = 620

