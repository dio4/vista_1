# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2016 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################


# необходимо выработать формулировки названия прав
# 100 идентификаторов urAccess... это перебор

urAdmin = 'adm'

# Работа
urAccessRegistry       = 'wRegistry'          # имеет доступ к обслуживанию пациентов
urAccessTimeLine       = 'timeLine'           # имеет доступ к графику
urAccessBlanks         = 'wBlanks'            # имеет доступ к учету бланков
urAccessHospitalBeds   = 'wHospitalBeds'      # имеет доступ к коечному фонду
urAccessJobsPlanning   = 'wJobsPlanning'      # имеет доступ к планированию работ
urAccessJobsOperating  = 'wJobsOperating'     # имеет доступ к выполнению работ
urAccessStockControl   = 'wStockControl'      # имеет доступ к складскому учёту
urAccessGraph          = 'wGraph'
urAccessLUD            = 'wLUD'
urAccessQuoting        = 'wQuoting'           # имеет доступ к редактированию квотирования
urAccessQuotingWatch   = 'wQuotingWatch'      # имеет доступ к просмотру квотирования
urAccessTissueJournal  = 'wTissueJournal'     # имеет доступ к лаболаторному журналу
urAddDeferredQueueItems = 'addDeferredQueueItems' # имеет право добавлять записи в ЖОС
urEditDeferredQueueItems = 'editDeferredQueueItems' # имеет право обрабатывать записи в ЖОС
urEditHospitalBedLocationCard = 'editHospitalBedsLocationCard' # имеет право менять месторасположение истории болезни в стационарном мониторе


# Работа -> Обслуживание
# Только чтение
urRegTabReadRegistry   = 'regReadRegistry'    #имеет доступ к вкладке Картотека
urRegTabReadEvents     = 'regReadEvents'      #имеет доступ к вкладке Обращение
urRegTabReadAmbCard    = 'regReadAmbCard'     #имеет доступ к вкладке Мед. карта
urRegTabReadActions    = 'regReadActions'     #имеет доступ к вкладке Обслуживание
urRegTabReadExpert     = 'regReadExpert'      #имеет доступ к вкладке КЭР
urRegTabReadAmbulance  = 'regReadAmbulance'   #имеет доступ к вкладке СМП
urReadHideLeaversPatients = 'regReadLeaversPatients'    #имеет доступ к просмотру выбывших пациентов
urPictureViewAndFind = 'pictureViewAndFind' # имеет доступ к просмотру и поиску снимков
# Запись/изменение
urRegTabWriteRegistry  = 'regWriteRegistry'   #имеет доступ к вкладке Картотека
urEditLocationCard     = 'regEditLocationCard'#имеет право редактировать Место нахождения амбулаторной карты
urEditStatusObservationClient = 'regEditStatusObservationClient'#имеет право редактировать Статус наблюдение пациента
urEditPayedEvents = 'editPayedEvents' #имеет право редактировать оплаченные события
urEditDiagnosticsInPayedEvents = 'editDiagnosticsInPayedEvents' # имеет право редактировать таблицу "Диагнозы" для событий, по которым выставлен/оплачен счет (issue 579)
urRegTabWriteEvents    = 'regWriteEvents'     #имеет доступ к вкладке Обращение
urRegTabWriteAmbCard   = 'regWriteAmbCard'    #имеет доступ к вкладке Мед. карта
urRegTabWriteActions   = 'regWriteActions'    #имеет доступ к вкладке Обслуживание
urRegTabWriteExpert    = 'regWriteExpert'     #имеет доступ к вкладке КЭР
urRegWriteInsurOfficeMark = 'regWriteInsurOfficeMark' #право на изменение данных в документах ВУТ с отметкой страхового стола
urRegTabWriteAmbulance = 'regWriteAmbulance'  #имеет доступ к вкладке СМП
urRegControlDoubles    = 'regControlDoubles'  #имеет доступ к оперативному логическому контролю двойников
urEditOwnEvents     = 'editOwnEvents'   #право на изменение существующего собственного обращения
urEditNotOwnEvents  = 'editNotOwnEvents' #право на изменение чужого обращения
urDoNotCheckResultAndMKB = 'doNotCheckResultAndMKB' #Право закрывать обращение не введя диагноз и результат
urNeedAtLeastOneDiagnosisInOpenEvent = 'needAtLeastOneDiagnosisInOpenEvent' # При сохранении обращения требуется как минимум один диагноз, даже если обращение еще открыто (при наличии права проверка отключается)
urSaveWithoutMes    = 'saveWithoutMes'
urCheckPersonInFindSameEvent = 'regCheckPersonInFindSameEvent' # При поиске дублирующихся обращений искать обращений проверять с учетом ответственного врача (по умолчанию - да)
urRegWithoutSearch = 'regWithoutSearch' # право регистрировать пациента без предварительного поиска. Отсутствие данного права скрывает кнопку "Регистрация" в картотеке.
urCreateSeveralVisits = 'createSeveralVisits' # Право на создание нескольких посещений к врачам одной специальности за один день
urIgnoreVisitCountCheck = 'ignoreVisitCountCheck' # Право игнорировать проверку на некорректное количество посещений
urChangeChkServiceDates = 'changeChkServiceDates' # Имеет право отключать проверку услуг по дате при выборе из списка "Типов мероприятий" по F9
urIgnoreLittleStrangerCheck = 'ignoreLittleStrangerCheck' # Право игнорировать проверку на пустые поля в признаке новорожденного
urSaveEventWithoutGoal = 'saveEventWithoutGoal'   # Право на сохранение обращения без указания цели
urOncoDiagnosisWithoutTNMS = 'oncoDiagnosisWithoutTNMS' # Право на сохранение обращения с диагнозом C% без указания TNMS
urSetEventExecDateF003 = 'setEventExecDateF003'  # Право проставлять дату окончания события в форме 003/у
urChangeEventType = 'changeEventType'
urEditF027IfHospitalizationEventExists = 'editF027IfHospitalizationEventExists' # Право редактировать "Эпикриз на госпитальную комиссию", если его дата окончания меньше даты начала события "Госпитализация"
urEditClientPolicyInClosedEvent = 'editClientPolicyInClosedEvent'  # Право редактировать привязанный полис пациента в закрытом обращении
urSaveClientWithBasicInfo = 'saveClientWithBasicInfo'  # Право сохранять рег.карту только с ФИО, датой рождения, полом и адресом

#Работа -> Выполнение работ
urShowColumnsInJobsOperDialog = 'showColumnsInJobsOperDialog'  # Право просмативать столбцы Идентификатор и Статус в списке выполнения работ.
urOpenJobTicketEditor = 'openJobTicketEditor'  # Право открытия редактора работ в журнале выполнения работ

# Регистрационная карточка
urAddClient                             = 'addClient'                               # Право на регистрацию
urEditClientInfo                        = 'editClientInfo'                          # Право на редактирование информации о пациенте (не распространяется на вкладку Квоты)
urDeleteClientOldWorks                  = 'deleteClientOldWorks'                    # Право удалять прежнее место работы пациента
urAddDublicateClientIdentifier          = 'addDublicateClientIdentifier'            # Право на добавление пациенту одинаковых (по внешней учетной системе) идентификаторов
urChangeMonitoringKind                  = 'changeMonitoringKind'                    # Право менять вид (наблюдения) при добавлении нового наблюдения.
urRegWithoutCompulsoryPolicy            = 'regWithoutCompulsoryPolicy'              # Право сохранять регистрационную карту, не указывая полис ОМС
urRegWithoutDocSource                   = 'regWithoutDocSource'                     # Право не указывать дату и место выдачи документа в регистрационной карте
urRegWithoutBirthPlace                  = 'regWithoutBirthPlace'                    # Право не указывать место рождения в регистрационной карте
urRegWithoutCheckNumberCompulsoryPolicy = 'regWithoutCheckNumberCompulsoryPolicy'   # Право не проверять номер полиса ОМС при закрытии
urRegWithEmptyContacts                  = 'regWithEmptyContacts'                    # Право не указывать контакты пациента
urRegWithoutDistrict                    = 'regWithoutDistrict'                      # Право не указывать район проживания пациента
urRegWithoutBodyStats                   = 'regWithoutBodyStats'                     # НИИ Петрова: Право не указывать рост и вес пациента


# Работа -> Обслуживание -> вкладка Обслуживание
# Только чтение, на запись - см. права выше
urReadActionsStatus    = 'regReadActionsStatus'
urReadActionsDiagnostic= 'regReadActionsDiagnostic'
urReadActionsCure      = 'regReadActionsCure'
urReadActionsMisc      = 'regReadActionsMisc'

# Сервис
urAccessAttachClientsForArea = 'attachClientsForArea'  #имеет  доступ к "Выполнить прикрепление пациентов к участкам"
urAccessLogicalControl = 'logiccntl'                   #имеет  доступ к логическому контролю
urAccessLogicalControlDiagnosis = 'logicCntlDiagnosis' #имеет  доступ к логическому контролю ЛУДа
urAccessLogicalControlDoubles   = 'logicCntlDoubles'   #имеет  доступ к контролю двойников
urAccessLogicalControlMES       = 'logicCntlMES'       #имеет  доступ к контролю событий с МЭС
urAccessSchemaClean = 'schemaclean'                    #имеет доступ к очистке бд
urAccessSchemaSync = 'schemaSync'   # может проводить синхронизацию БД

# Расчет
urAccessAccountInfo    = 'acc'                # имеет доступ к учётной информации (договора и счета)
urAccessAccounting     = 'accAccount'         # Расчеты: доступ к счетам независимо от типа финансирования
urAccessAccountingBudget= 'accAccountBudget'  # Расчеты: доступ к счетам с типом финансирования "бюджет"
urAccessAccountingCMI  = 'accAccountCMI'      # Расчеты: доступ к счетам с типом финансирования "ОМС"
urAccessAccountingVMI  = 'accAccountVMI'      # Расчеты: доступ к счетам с типом финансирования "ДМС"
urAccessAccountingCash = 'accAccountCash'     # Расчеты: доступ к счетам с типом финансирования "платно"
urAccessAccountingTargeted = 'accAccountTargeted' # Расчеты: доступ к счетам с типом финансирования "целевой"
urEditAccountItem          = 'editAccountItem' # Имеет право редактировать элемент счета (i1850). В апдейты данное право не стоит помещать, только ручное добавление в базу

urAccessContract       = 'accContract'        # имеет доступ к  договорам
urAccessPriceCalculate = 'accPriceCalculate'  # имеет доступ к кнопке пересчета тарифов
urAccessCashBook       = 'accCashBook'        # имеет доступ к журналу кассовых операций

urAccessEditPayment = 'accEditPayment'      # имеет право на подтверждение/изменение подтверждения оплаты
# Справочники
urAccessRefBooks          =       'ref'                # имеет доступ к справочнику

# Справочники: Адреса
urAccessRefAddress        =       'refAddress'         # имеет доступ к справочнику Адреса
urAccessRefAddressKLADR   =       'refAddressKLADR'    # имеет доступ к справочнику КЛАДР
urAccessRefAddressAreas   =       'refAddressAreas'    # имеет доступ к справочнику Участки

# Cправочники: Классификаторы
urAccessRefClassificators =       'refCl'                      # имеет доступ к справочнику Класификаторы
urAccessRefClOKPF =               'refClOKPF'                  # имеет доступ к справочнику ОКПФ
urAccessRefClOKFS =               'refClOKFS'                  # имеет доступ к справочнику ОКФС
urAccessRefClHurtType =           'refClHurtType'              # имеет доступ к справочнику Типы вредности
urAccessRefClHurtFactorType =     'refClHurtFactorType'        # имеет доступ к справочнику Факторы вредности
urAccessRefClUnit =               'refClUnit'                  # имеет доступ к справочнику Единицы Измерения

# Cправочники: Скорая помощь
urAccessRefEmergency           =  'refEmergency'               # имеет доступ к справочнику Скорая помощь

# Cправочники: Питание
urAccessRefFeed                =  'refFeed'                    # имеет доступ к справочнику Питание

# Cправочники: Медицинские
urAccessRefMedical             =   'refMed'                    # имеет доступ к справочнику Медицинские
urAccessRefMedMKB              =   'refMedMKB'                 # имеет доступ к справочнику МКБ
urAccessRefMedMKBSubClass      =   'refMedMKBSubClass'         # имеет доступ к справочнику Субклассификация МКБ
urAccessRefMedDiseaseCharacter =   'refMedDiseaseCharacter'    # имеет доступ к справочнику Характеры заболеваний
urAccessRefMedDiseaseStage     =   'refMedDiseaseStage'        # имеет доступ к справочнику Стадии заболеваний
urAccessRefMedDiseasePhases    =   'refMedDiseasePhases'       # имеет доступ к справочнику Фазы заболевания
urAccessRefMedDiagnosisType    =   'refMedDiagnosisType'       # имеет доступ к справочнику Типы диагноза
urAccessRefMedTraumaType       =   'refMedTraumaType'          # имеет доступ к справочнику Типы травм
urAccessRefMedTempInvalidReason=   'refMedTempInvalidReason'   # имеет доступ к справочнику Причины временной нетрудоспособности
urAccessRefMedHealthGroup      =   'refMedHealthGroup'         # имеет доступ к справочнику Группы здоровья
urAccessRefMedDispanser        =   'refMedDispanser'           # имеет доступ к справочнику Отметки диспансерного наблюдения
urAccessRefMedResult           =   'refMedResult'              # имеет доступ к справочнику Резльтаты осмотра
urAccessRefMedTempInvalidDocument= 'refMedTempInvalidDocument' # имеет доступ к справочнику Документы ВУТ
urAccessRefMedTempInvalidRegime=   'refMedTempInvalidRegime'   # имеет доступ к справочнику Режимы пеорида ВУТ
urAccessRefMedTempInvalidBreak =   'refMedTempInvalidBreak'    # имеет доступ к справочнику Нарушения режима ВУТ
urAccessRefMedTempInvalidResult=   'refMedTempInvalidResult'   # имеет доступ к справочнику Результаты ВУТ
urRefEditMedTempInvalidExpertKAK=  'refEditMedTempInvalidExpertKAK'# имеет право вносить отметки КЭК (заимствовано)
urAccessRefMedComplain         =   'refMedComplain'            # имеет доступ к справочнику Жалобы
urAccessRefMedThesaurus        =   'refMedThesaurus'           # имеет доступ к справочнику Тезаурус
urAccessRefMedBloodType        =   'refMedBloodType'           # имеет доступ к справочнику Группы крови

# Cправочники: Организации
urAccessRefOrganization        =   'refOrg'                    # имеет доступ к подменю Организации
urAccessRefOrgRBNet            =   'refOrgRBNet'               # имеет доступ к справочнику Сеть
urAccessRefOrgBank             =   'refOrgBank'                # имеет доступ к справочнику Банки
urAccessRefOrgOrganisation     =   'refOrgOrganisation'        # имеет доступ к справочнику Организации

# Справочники: Персонал
urAccessRefPerson         = 'refPerson'  # имеет доступ к подменю Персонал
urAccessRefPersonOrgStructure = 'refPersonOrgStructure'# имеет доступ к справочнику Структура ЛПУ
urAccessRefPersonRBSpeciality = 'refPersonRBSpeciality'# имеет доступ к справочнику Специальности
urAccessRefPersonRBPost = 'refPersonRBPost'# имеет доступ к справочнику Должности
urAccessRefPersonRBActivity = 'refPersonRBActivity'# имеет доступ к справочнику Виды(типы) деятельности врача
urAccessRefPersonPersonal = 'refPersonPersonal'# имеет доступ к справочнику Сотрудники

# Справочники: Персонификация
urAccessRefPersonfication = 'refPersnftn'# имеет доступ к подменю Персонификация
urAccessRefPersnftnPolicyKind = 'refPersnftnPolicyKind'# имеет доступ к справочнику Вид полиса
urAccessRefPersnftnPolicyType = 'refPersnftnPolicyType'# имеет доступ к справочнику Тип полиса
urAccessRefPersnftnDocumentTypeGroup = 'refPersnftnDocumentTypeGroup'# имеет доступ к справочнику Группа типа документа
urAccessRefPersnftnDocumentType = 'refPersnftnDocumentType'# имеет доступ к справочнику Тип документа
urAccessRefPersnftnContactType = 'refPersnftnContactType'# имеет доступ к справочнику Способы связи с пациентом

# Справочники: Соц статус
urAccessRefSocialStatus   = 'refSocState'# имеет доступ к подменю Соц статус
urAccessRefSocialStatusType = 'refSocStateType'# имеет доступ к справочнику Соц. статус: тип, льготы
urAccessRefSocialStatusClass = 'refSocStateClass'# имеет доступ к справочнику Классификатор социальных статусов

# Справочники: Учёт
urAccessRefAccount                       = 'refAccount' # имеет доступ к подменю Учёт
urAccessRefAccountRBVisitType            = 'refAccountRBVisitType'# имеет доступ к справочнику Тип визита
urAccessRefAccountEventType              = 'refAccountEventType'# имеет доступ к справочнику Типы событий
urAccessRefAccountRBEventTypePurpose     = 'refAccountRBEventTypePurpose'# имеет доступ к справочнику Назначение типа события
urAccessRefAccountRBEventProfile         = 'refAccountRBEventProfile'# имеет доступ к справочнику Профиль события
urAccessRefAccountRBScene                = 'refAccountRBScene'# имеет доступ к справочнику Место выполнения визита
urAccessRefAccountRBAttachType           = 'refAccountRBAttachType'# имеет доступ к справочнику Тип прикрепления
urAccessRefAccountRBMedicalAidUnit       = 'refAccountRBMedicalAidUnit'# имеет доступ к справочнику Единицы учета мед. помощи
urAccessRefAccountActionPropertyTemplate = 'refAccountActionPropertyTemplate'# имеет доступ к справочнику Библиотека свойств действий
urAccessRefAccountRBActionShedule        = 'refAccountRBActionShedule'       # имеет доступ к справочнику График выполнения назначения
urAccessRefAccountActionType             = 'refAccountActionType'            # имеет доступ к справочнику Типы действий
urAccessRefAccountActionTemplate         = 'refAccountActionTemplate'        # имеет доступ к справочнику Шаблоны действий
urAccessRefAccountRBReasonOfAbsence      = 'refAccountRBReasonOfAbsence'     # имеет доступ к справочнику Причины отсутствия
urAccessRefAccountRBHospitalBedProfile   = 'refAccountRBHospitalBedProfile'  # имеет доступ к справочнику Профили коек

# Справочники: Финансовые
urAccessRefFinancial           = 'refFin'                # имеет доступ к подменю Финансовые
urAccessRefFinRBFinance        = 'refFinRBFinance'       # имеет доступ к справочнику "Источники финансирования"
urAccessRefFinRBService        = 'refFinRBService'       # имеет доступ к справочнику Услуги (профиль ЕИС)
urAccessRefFinRBTariffCategory = 'refFinRBTariffCategory'# имеет доступ к справочнику "Тарифные категории"
urAccessRefFinRBPayRefuseType  = 'refFinRBPayRefuseType' # имеет доступ к справочнику "Причины отказа платежа"
urAccessRefFinRBCashOperation  = 'refFinRBCashOperation' # имеет доступ к справочнику "Кассовые операции"

# Справочники: лекарственные средства и изделия медицинского назначения
urAccessNomenclature           = 'refNomenclature' # имеет доступ к справочнику "Номенклатура лекарственных средств и изделий медицинского назначения"
urAccessStockRecipe            = 'refStockRecipe'  # имеет доступ к справочнику "Рецепты производства ЛСиИМН"

# Справочники: Лаборатория
urAccessLaboratory                  = 'refLaboratory' # имеет доступ к подменю Лаболатория
urAccessEquipment                   = 'refEquipment' # имеет доступ к подменю Оборудование
urAccessEquipmentMaintenanceJournal = 'refEquipmentMaintenanceJournal' # Имеет доступ к редактированию журнала технического обслуживания оборудования

# ---
urAccessUI                = 'ui'         # имеет доступ к интерфейсу пользователя
urAccessExchange          = 'exchng'     # имеет достук к обмену информацией

# Анализ
urAccessAnalysis          = 'aFullAccess'# имеет полный доступ к анализу
urAccessAnalysisPersonal  = 'aPersonal'  # имеет полный доступ к персональному анализу
urAccessAnalysisSubStruct = 'aSubStruct' # имеет полный доступ к анализу подразделения
urAccessReportConstructor = 'reportConstructor' # право на доступ к Консруктору отчётов
urAccessReportConstructorEdit = 'reportConstructorEdit' # право на создание, редактирование инморт и экспорт отчётов в Конструкторе отчётов

# Настройки
urAccessSetupDB                = 'setupDB'                # имеет доступ к настройкам БД
urAccessSetupAccountSystems    = 'setupAccSys'            # имеет доступ к внешним учётным системам
urAccessSetupDefault           = 'setupDefault'           # имеет доступ к установкам значений по умолчанию
urAccessSetupExport            = 'setupAccExpFmt'         # имеет доступ к форматам экспорта
urAccessSetupTemplate          = 'setupTemplate'          # имеет доступ к настройкам шаблонов
urAccessSetupUserRights        = 'setupUsrRights'         # имеет доступ к настройкам прав пользователя
urAccessSetupGlobalPreferencesWatching = 'setupGlobalPreferencesWatching' # имеет доступ к чтению таблицы глобальных настроек
urAccessSetupGlobalPreferencesEdit = 'setupGlobalPreferencesEdit' # имеет доступ к редактированию таблицы глобальных настроек
urAccessCalendar               = 'setupCalendar'          # имеет доступ к настройке календаря
urAccessSetupCounter           = 'setupCounter'           # имеет доступ к настройке счетчиков

#urCanChangeOwnPassword = 2

# -- в процессе работы:

urAccessF000planner       = 'f000planner'        # показывается планировщик Ф.000
urAccessF001planner       = 'f001planner'        # показывается планировщик Ф.001
urAccessF003planner       = 'f003planner'        # показывается планировщик Ф.003
urAccessF025planner       = 'f25planner'         # показывается планировщик Ф.025
urAccessF030planner       = 'f030planner'        # показывается планировщик Ф.030
urAccessF043planner       = 'f043planner'        # показывается планировщик Ф.043
urAccessF110planner       = 'f110planner'        # показывается планировщик Ф.110
urLoadActionTemplate      = 'loadActionTemplate' # возможно загружать шаблоны действий в F25 etc.
urSaveActionTemplate      = 'saveActionTemplate' # возможно создавать/изменять шаблоны действий в F25 etc.
urCopyPrevAction          = 'copyPrevAction'     # Копировать действия из предыдущих событий в F25 etc.
urChangeMKB               = 'changeMKB'          # исправить шифр МКБ в ЛУД
urChangeDiagnosis         = 'changeDiagnosis'    # изменить диагноз в ЛУД
urChangeDiagnosisPND      = 'changeDiagnosisPND' # право изменять диагноз через регистрационную карточку (реализовано для ПНД, активно при гл. настройке 36)
urLocalControlLUD         = 'localControlLUD'    # доступ к оперативному логическому контролю ЛУДа
urEditReportForm          = 'editReportForm'     # редактировать печатные формы отчетов во внешнем редакторе
urEditOtherPeopleAction   = 'editOtherPeopleAction' # редактировать чужие действия
urHospitalTabReceived     = 'hospitalTabReceived'# имеет доступ к кнопке "Госпитализация" с вкладки "Поступили"
urHospitalTabPlanning     = 'hospitalTabPlanning'# имеет доступ к кнопке "Госпитализация" с вкладки "В очереди"
urLeavedTabPresence       = 'leavedTabPresence'  # имеет доступ к кнопке "Выписка" с вкладки "Присутствуют"
urQueueOverTime           = 'queueOverTime'      # Окно "График": имеет право записывать пациентов на "пустое" время
urQueueToSelfOverTime     = 'queueToSelfOverTime'# Окно "График": имеет право записывать пациентов к себе на "пустое" время
urQueueDeletedTime        = 'queueDeletedTime'   # имеет право удалять созданные другими записи в листе предварительной записи
urQueueToSelfDeletedTime  = 'queueToSelfDeletedTime'  # Окно "График": имеет право удалять созданные им записи в листе предварительной записи
urQueueCancelMinDateLimit = 'queueCancelMinDateLimit' # Окно "График": не ограничивать календарь снизу
urQueueCancelMaxDateLimit = 'queueCancelMaxDateLimit' # Окно "График": не ограничивать календарь сверху
urQueueCheckVPolicy       = 'queueCheckVPolicy'       # Окно "График": проверять, действителен ли ДМС полис, и выводить предупреждение, если нет
urAccessViewFullOrgStructure = 'viewFullOrgStructure' # Окно "График": отображение всей структуры ЛПУ и всех видов деятельности
urDeleteEventWithTissue   = 'deleteEventWithTissue'   # Право на удаление событий с действиями связанными с забором биоматериала
urDeleteActionWithTissue   = 'deleteActionWithTissue'   # Право на удаление действий, связанных с забором биоматериала
urDeleteEventWithJobTicket  = 'deleteEventWithJobTicket'  # Имеет право удалять события при наличии действий связанных с номерком на Работу
urDeleteNotOwnEvents      = 'deleteNotOwnEvents'      # Имеет право удалять чужие События
urDeleteOwnEvents         = 'deleteOwnEvents'         # Имеет право удалять свои События
urDeleteProbe             = 'deleteProbe'             # Абсолютное право на удаление проб
urEditProbePerson         = 'editProbePerson'         # Имеет право редактировать исполнителя в пробах
urEditJobTicket           = 'editJobTicket'           # Имеет право редактировать талончик на работу в действиях
urAddJobTicketToSuperiorOrgStructure = 'addJobTicketToSuperiorOrgStructure'     # Имеет право выдавать талончики на работу в вышестоящую организацию
urAddOvertimeJobTickets   = 'addOvertimeJobTickets'   # Выдавать талончики на работу сверх очереди
urIgnoreJobTicketQuota    = 'ignoreJobTicketQuota'    # Имеет право превышать квоту при выдаче талончиков на работу
urUsePropertyCorrector    = 'usePropertyCorrector'    # Имеет право использовать утилиту 'корректор свойств'
urQueueingOutreaching     = 'queueingOutreaching'     # Имеет право превышать квоту на запись к врачу
urQueueWithEmptyContacts  = 'queueWithEmptyContacts'  # Имеет право добавлять в пердварительную запись пациента без контактов
urEditExecutionPlanAction = 'editExecutionPlanAction' # Имеет право редактировать календарь выполнения назначения
urCreateReferral          = 'createReferral'          # Имеет право создавать новые направления
urCreateSeveralEvents     = 'createSeveralEvents'     # Имеет право создвать несколько обращений одного типа по одной специальности в один день
urCreateSeveralOMSEvents  = 'createSeveralOMSEvents'  # Имеет право на создание нескольких обращений с типом финансирования ОМС к врачам одной специальности за один день
urFastCreateEvent         = 'fastCreateEvent'         # Имеет право быстрого создания обращений
urSaveMovingWithoutMes    = 'saveMovingWithoutMes'    # Может сохранять действие движения без указания МЭС
urIgnoreRestrictActionByFrequency = 'canIgnoreRestrictActionByFrequency' # Имеет право игнорировать жесткий контроль на повторное добавление услуги за период
urDisableCheckActionSpeciality = 'canDisableCheckActionSpeciality' # Имеет право отключать галочку "Планировщик" при добавлении услуги по F9

urDeleteClientQuotingRows = 'deleteClientQuotingRows'   # Имеет право удалять квоты пациента
urSeeStaff = 'seeStaff'                                 # Имеет право видеть сотрудников (при включенном разделении на сотрудников/пациентов)

urChangeStateOrgStructureActionsFilter = 'changeStateOrgStructureActionsFilter' # Имеет право включать и отключать фильтр для типов действия "Подразделение"
urDefaultJobTickets = 'defaultJobTickets' # Подстановка номерка в действие по-умолчанию

urEQAccess = 'eqAccess' # Имеет право работать с табло эл.очереди

#atronah: пока сделано в рамках i1492 (и не влияет на эл. очередь из 503)
urEQSettings = 'eqSettings' # Имеет доступ к настройкам эл. очереди
urEQCalling = 'eqCalling' # Имеет право вызывать пациентов через интерфейс
urEQManaging = 'eqManaging' # Имеет право управлять электронной очередью

urECRAccess = 'ecrAccess' # Имеет право работать с кассовым аппаратом через МИС

urCopyPerson = 'copyPerson' # Имеет право копировать записи в Справочники: персонал - сотрудники

urChkKSGDefault = 'chkKSGDefault'  # Отключает условие КСГ при выборе из списка "Типов мероприятий" по F9 по умолчанию
urChkMesNecessityNomenclativeDefault = 'chkMesNecessityNomenclativeDefault'  # Отключает условия МЭС, ЧП, Номенклатура при выборе из списка "Типов мероприятий" по F9 по умолчанию
urCreateEventFromRecommendations = 'createEventFromRecommendations' # Может создавать обращение со вкладки "Направления"

urIgnoreAutoPrintTemplates = 'ignoreAutoPrintTemplates' # Пользователю не предлагается произвести печать, настроенную как автоматическая для типа события
urAutoPrintCostTemplate = 'autoPrintCostTemplate' # Пользователю предлагается производить печать справки о стоимости
urIgnoreDurationVisibilityTimelineWorksInEvent = 'ignoreDurationVisibilityTimelineWorksInEvent' #Не использовать период видимости расписания работ в обращении
urModifyObsoleteQuotas = 'modifyObsoleteQuotas'  # Право редактировать свойство с типом Квота пациента, заполненное квотой, помеченной как Устаревшая
urAccessToRunMoreThanOneProgramm = 'runMoreThanOneProgramm' #Право запускать несколько копий приложения

urAccessExportImportMIAC = 'exportImportMIAC' #Право осуществлять Экспорт/Импорт приписанного населения

DefaultDisabledRights = [urQueueCheckVPolicy, urEditAccountItem, urAccessExportImportMIAC]

urCycleDay = 'editCycleDay' # Право на редактирование и просмотр "День цикла" в обращении
urViewPolicyInStat = 'viewPolicyInStat' # Видеть полис на вкладке «Стат. учет». (для МСЧ3)
urAccessCrossingDates = 'accessCrossingDates' # Разрешить ввод полисов одного типа с пересечением дат
urAccessEditAutoPrimacy = 'accessEditAutoPrimacy' # Разрешить изменять первичность/повторность при автоматическом определении
urAllowNotFillContacts = 'allowNotFillContacts' # Право не заполнять поле "Контакты"
urAccessEditTimelineDialog = 'accessEditTimelineDialog' # Право на редактирование данных в окне "Учёт рабочего времени"
urEditFilledTimetableAction = 'editFilledTimetableAction'  # Право на редактирование расписания за день, в котором есть записанные пациенты
urAccessEditJobPlanner = 'accessEditJobPlanner' # Право на редактирование данных в окне "Планирование работ"
urAccessSetUnconscious = 'accessSetUnconscious' # Право на выставление пациента как "Поступил без сознания"
urSaveClientDuplicate = 'saveClientDuplicate' # Право сохранять регистрационную карточку нового пациента при обнаружении двойника
urSaveWithoutPrelimDiagF003 = 'saveWithoutPrelimDiagF003' # Право на сохранение обращения без предварительного диагноза (вкладка Стат.учет)
urSaveWithoutFinalDiagF003 = 'saveWithoutFinalDiagF003' # Право на сохранение обращения без заключительного диагноза
urActionTypeForceDelete = 'actionTypeForceDelete'  # Право удалять защищенные типы действий (i3418)
urEventLock = 'eventLock'  # Право блокировать обращения и редактировать блокированные обращения
urDisableCheckMKBInput = 'disableCheckMKBInput'  # Разрешить при включенной настройке №30 вводить коды МКБ как угодно
urEditSetVIPStatus = 'editSetVIPStatus'  # Разрешить изменять и присваивать пациентам статус VIP
urSetVIPComment = 'setVIPComment'  # Разрешить изменять комментарий к VIP-статусу пациента
urActionSetVerified = 'actionSetVerified'  # Право изменять в ручную статус проверки действия (i3592)
urAllowEditAllRegistryCard = 'allowEditAllRegistryCard'  # Право на редактировие всех рег.карт
urDisableCheckNewMKBWithOld = 'disableCheckNewMKBWithOld'  # Право отключать контроль диагнозов (Только для группы 'K') на сравнение с введенным ранее диагнозом той же группы
urNotAllowCreateManyEventsAtOneSetDate = 'notAllowCreateManyEventsAtOneSetDate'  # Право на запрет на создание нескольких обращений (любого типа) на одного клиента, за один день, от одного врача
urAllowSaveEventsWithoutCSG = 'allowSaveEventsWithoutCSG'  # Право, позволяющее сохранять обращение без КСГ (форма 003)
urDisableCheckRefferal = 'disableCheckRefferal'  # Право, отключающее предупреждения, связанные с незаполнением информации по направлениям
urEditClientWorkPlace = 'editClientWorkPlace'  # Право на редактирование Занятости сотрудников в рег. карте пациента
urSignedUpClientMoreOneTime = 'signedUpClientMoreOneTime'  # Право записывать пациента более одного раза к врачу одной специальности
urEditImplantsAndProsthesis = 'editImplantsAndProsthesis'  # Право на редактирование полей `Протезы`, `Имплантаты` в рег. карте пациента
urSkipOncologyForm90 = 'skipOncologyForm90'  # Возможность пропускать добавление формы 90 при включенной настройке 71
urCheckWorkFilling = 'checkWorkFilling'  # Проверять заполненность блока "Занятость" пациента в рег. карте
urSkipEventCreationAfterMoving = 'skipEventCreationAfterMoving'  # Право, пропускающее создание обращения при переводе пациента в действии "Движение"
urSkipCheckCancelationReason = 'skipCheckCancelationReason' # Право, пропустить проверку заполненности причины отказа
urSkipCheckClientContacts = 'notCheckClientContacts' # Право, пропустить проверку заполнености контактов
