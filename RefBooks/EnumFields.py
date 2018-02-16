# -*- coding: utf-8 -*-
from library.Enum import CEnum


class Sex(CEnum):
    u""" Пол (Client.sex, Patient.sex) """
    NotSet = 0
    Male = 1
    Female = 2

    nameMap = {
        NotSet: u'',
        Male  : u'М',
        Female: u'Ж'
    }


class PersonAcademicDegree(CEnum):
    u""" Ученая степень (Person.academicDegree) """
    No = 0
    CandidateMed = 1
    DoctorMed = 2

    nameMap = {
        No          : u'нет',
        CandidateMed: u'к.м.н',
        DoctorMed   : u'д.м.н'
    }


class PersonOccupationType(CEnum):
    u""" Тип занятия должности (Person.occupationType) """
    NotSet = 0
    Main = 1
    Combined = 2

    nameMap = {
        NotSet  : u'Не указано',
        Main    : u'Основное',
        Combined: u'По совместительству'
    }


class PersonEmploymentType(CEnum):
    u""" Режим работы (Person.employmentType) """
    NotSet = 0
    FullTime = 1
    PartTime = 2
    Contract = 3

    nameMap = {
        NotSet  : u'Не указано',
        FullTime: u'Постоянно',
        PartTime: u'Временно',
        Contract: u'По срочному договору'
    }


class PersonIsReservist(CEnum):
    u""" Военнообязанность (Person.isReservist) """
    NotSet = 0
    Yes = 1
    No = 2

    nameMap = {
        NotSet: u'Не указано',
        Yes   : u'Военнообязан',
        No    : u'Невоеннообязан'
    }


class PersonRegType(CEnum):
    u""" Тип регистрации (Person.regType) """
    NotSet = 0
    Permanent = 1
    Temporary = 2

    nameMap = {
        NotSet   : u'Не указано',
        Permanent: u'Постоянная',
        Temporary: u'Временная'
    }


class PersonMaritalStatus(CEnum):
    u""" Состояние в браке (ОКИН 10) (Person.maritalStatus) """
    NotSet = 0
    NeverMarried = 1
    RegisteredMarriage = 2
    UnregisteredMarriage = 3
    Widowed = 4
    Divorced = 5
    Parted = 6

    nameMap = {
        NotSet              : u'Не указано',
        NeverMarried        : u'Никогда не состоял (не состояла в браке)',
        RegisteredMarriage  : u'Состоит в зарегистрированном браке',
        UnregisteredMarriage: u'Состоит в незарегистрированном браке',
        Widowed             : u'Вдовец (вдова)',
        Divorced            : u'Разведен (разведена)',
        Parted              : u'Разошелся (разошлась)'
    }


class PersonEducationType(CEnum):
    u""" Тип образования (Person_Education.educationType) """
    NotSet = 0
    Internship = 1
    Traineeship = 2
    HigherEducation = 3
    SecondaryEducation = 4

    nameMap = {
        NotSet            : u'Не указано',
        Internship        : u'Интернатура',
        Traineeship       : u'Ординатура',
        HigherEducation   : u'Высшее образование',
        SecondaryEducation: u'Среднее образование'
    }


class PersonOrderType(CEnum):
    u""" Приказы по управлению персоналом: тип перемещения (Person_Order.type) """
    Employment = 0
    Dismission = 1
    Assignment = 2
    Vacation = 3
    Study = 4
    Mission = 5

    nameMap = {
        Employment: u'Приём на работу',
        Dismission: u'Увольнение',
        Assignment: u'Назначение на должность',
        Vacation  : u'Отпуск',
        Study     : u'Учёба',
        Mission   : u'Командировка'
    }


class PersonQALevel(CEnum):
    u""" Уровень внутреннего контроля качества (Person.qaLevel) """
    NotSet = 0
    First = 1
    Second = 2
    VK = 3

    nameMap = {
        NotSet: u'Не задано',
        First : u'Первый',
        Second: u'Второй',
        VK    : u'Врачебная комиссия'
    }
