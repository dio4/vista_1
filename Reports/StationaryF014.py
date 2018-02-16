# -*- coding: utf-8 -*-

import itertools
from operator import add
from PyQt4 import QtCore, QtGui

from library.DialogBase         import CDialogBase
from library.MapCode            import createMapCodeToRowIdx
from library.Utils              import forceDate, forceInt, forceRef, forceString, forceBool, getActionTypeIdListByFlatCode
from library.ListModel          import CListModel
from Orgs.Utils                 import getOrgStructureFullName, getOrgStructureDescendants
from Reports.Report             import CReport, normalizeMKB
from Reports.ReportBase         import createTable, CReportBase
from Reports.StationaryF007     import getStringProperty

from Ui_StationaryF14Setup      import Ui_StationaryF14SetupDialog
from Ui_StationaryF14DCSetup    import Ui_StationaryF14DCSetupDialog


class CAgeCategory:
    adults   = 1
    seniors  = 2
    children = 3
    newborn  = 4

    list = [
        u'Не задано',
        u'Взрослые (18 лет и старше)',
        u'Взрослые старше трудоспособного возраста',
        u'Дети (в возрасте 0 - 17 лет включительно)',
        u'Дети (в возрасте до 1 года)'
    ]

    @staticmethod
    def name(category):
        return list[category] if 1 <= category <= 4 else u''


MainRows = [(u'Всего', u'1.0', u'A00-T98'),
 (u'в том числе:\nНекоторые инфекционные и паразитарные болезни', u'2.0', u'A00-B99'),
 (u'из них:\nкишечные инфекции', u'2.1', u'A00-A09'),
 (u'туберкулез органов дыхания', u'2.2', u'A15-A16'),
 (u'менингококковая инфекция', u'2.3', u'A39'),
 (u'сепсис', u'2.4', u'A40-A41'),
 (u'инфекции, передающиеся приемущественно половым путем', u'2.5', u'A50-A64'),
 (u'острый полиомиелит', u'2.6', u'A80'),
 (u'вирусный гепатит', u'2.7', u'B15-B19'),
 (u'болезнь, вызванная ВИЧ', u'2.8', u'B20-B24'),
 (u'Новообразования', u'3.0', u'C00-D48'),
 (u'в том числе:\nзлокачественные новообразования', u'3.1', u'C00-C97'),
 (u'из них:\nзлокачественные новообразования лимфоидной, кроветворной и родственных им тканей', u'3.1.1', u'C81-C96'),
 (u'из них:\nфолликулярная лимфома', u'3.1.1.1', u'C82'),
 (u'мелкоклеточная(диффузная) нефолликулярная лимфома', u'3.1.1.2', u'C83.0'),
 (u'мелкоклеточная с расщепленными ядрами(диффузная) нефолликулярная лимфома', u'3.1.1.3', u'C83.1'),
 (u'крупноклеточная(диффузная) нефолликулярная лимфома', u'3.1.1.4', u'C83.3'),
 (u'другие типы диффузных нефолликулярных лимфом', u'3.1.1.5', u'C83.8'),
 (u'диффузная нефолликулярная лимфома неуточненная', u'3.1.1.6', u'C83.9'),
 (u'зрелые Т/NK-клеточные лимфомы', u'3.1.1.7', u'C84'),
 (u'из них:\nдругие зрелые Т/NK-клеточные лимфомы', u'3.1.1.7.1', u'C84.5'),
 (u'другие и неуточненные типы неходжкинской лимфомы', u'3.1.1.8', u'C85'),
 (u'макроглобулинемия Вальденстрема', u'3.1.1.9', u'C88.0'),
 (u'хронический лимфоцитарный лейкоз', u'3.1.1.10', u'C91.1'),
 (u'хронический миелоидный лейкоз', u'3.1.1.11', u'C92.1'),
 (u'доброкачественные новообразования', u'3.2', u'D10-D36'),
 (u'из них: лейомиома матки', u'3.2.1', u'D25'),
 (u'доброкачественные новообразования яичника', u'3.2.2', u'D27'),
 (u'Болезни крови, кроветворных органов и отдельные нарушения, вовлекающие иммунный механизм', u'4.0', u'D50-D89'),
 (u'из них:\nанемии', u'4.1', u'D50-D64'),
 (u'из них:\nапластические анемии', u'4.1.1', u'D60-D61'),
 (u'нарушения свертываемости крови, пурпура и другие геморрагические состояния', u'4.2', u'D65-D69'),
 (u'из них:\nдиссеминированное внутрисосудистое свертывание (синдром дефибринации)', u'4.2.1', u'D65'),
 (u'гемофилия', u'4.2.2', u'D66-D68'),
 (u'отдельные нарушения, вовлекающие иммунный механизм', u'4.3', u'D80-D89'),
 (u'Болезни эндокринной системы, расстройства питания и нарушения обмена веществ', u'5.0', u'E00-E89'),
 (u'из них:\nболезни щитовидной железы, связанные с йодной недостаточностью, и сходные состояния', u'5.1', u'E01-E03'),
 (u'тиреотоксикоз (гипертиреоз)', u'5.2', u'E05'),
 (u'тиреоидит', u'5.3', u'E06'),
 (u'сахарный диабет', u'5.4', u'E10-E14'),
 (u'из него:\nсахарный диабет I типа', u'5.4.1', u'E10'),
 (u'сахарный диабет II типа', u'5.4.2', u'E11'),
 (u'с поражением глаз', u'5.4.3', u'E10.3,E11.3,E12.3,E13.3,E14.3'),
 (u'гиперфункция гипофиза', u'5.5', u'E22'),
 (u'гипопитуитаризм', u'5.6', u'E23.0'),
 (u'Несахарный диабет', u'5.7', u'E23.2'),
 (u'адреногенитальные расстройства', u'5.8', u'E25'),
 (u'дисфункция яичников', u'5.9', u'E28'),
 (u'дисфункция яичек', u'5.10', u'E29'),
 (u'ожирение', u'5.11', u'E66'),
 (u'фенилкетонурия', u'5.12', u'E70.0-1'),
 (u'нарушения обмена галактозы(галактоземия)', u'5.13', u'E74.2'),
 (u'болезнь Гоше', u'5.14', u'E75.2'),
 (u'нарушения обмена гликозамино-гликанов(мукополисахаридоз)', u'5.15', u'E76.0-3'),
 (u'муковисцидоз', u'5.16', u'E84'),
 (u'Психические расстройства и расстройства поведения', u'6.0', u'F01-F99'),
 (u'из них:\nпсихические расстройства и расстройства поведения, связанные с употреблением психоактивных веществ', u'6.1', u'F10-F19'),
 (u'Болезни нервной системы', u'7.0', u'G00-G98'),
 (u'из них:\nвоспалительные болезни центральной нервной системы', u'7.1', u'G00-G09'),
 (u'из них:\nбактериальный менингит', u'7.1.1', u'G00'),
 (u'энцефалит, миелит и энцефаломиелит', u'7.1.2', u'G04'),
 (u'системные атрофии, поражающие преимущественно центральную нервную систему', u'7.2', u'G10-G12'),
 (u'экстрапирамидные и другие двигательные нарушения', u'7.3', u'G20, G21, G23- G25'),
 (u'из них:\nболезнь Паркинсона', u'7.3.1', u'G20'),
 (u'другие экстрапирамидные и двигательные нарушения', u'7.3.2', u'G25'),
 (u'другие дегенеративные болезни нервной системы', u'7.4', u'G30-G31'),
 (u'болезнь Альцгеймера', u'7.4.1', u'G30'),
 (u'демиелинизирующие болезни центральной нервной системы', u'7.5', u'G35- G37'),
 (u'из них:\nрассеянный склероз', u'7.5.1', u'G35'),
 (u'эпизодические и пароксизмальные расстройства', u'7.6', u'G40-G47'),
 (u'из них:\nэпилепсия, эпилептический статус', u'7.6.1', u'G40-G41'),
 (u'преходящие транзиторные церебральные  ишемические приступы [атаки] и родственные   синдромы', u'7.6.2', u'G45'),
 (u'поражения отдельных нервов, нервных корешков и сплетений, полиневропатии и другие поражения периферической нервной  системы', u'7.7', u'G50-G64'),
 (u'из них:\nсиндром Гийена-Барре', u'7.7.1', u'G61.0'),
 (u'болезни нервно-мышечного синапса и мышц', u'7.8', u'G70-G73'),
 (u'из них:\nмиастения', u'7.8.1', u'G70.0,2'),
 (u'мышечная дистрофия Дюшенна', u'7.8.2', u'G71.0'),
 (u'церебральный паралич и другие паралитические синдромы', u'7.9', u'G80-G83'),
 (u'из них:\nцеребральный паралич', u'7.9.1', u'G80'),
 (u'расстройства вегетативной (автономной) нервной системы', u'7.10', u'G90'),
 (u'сосудистые миелопатии', u'7.11', u'G95.1'),
 (u'Болезни глаза и его придаточного аппарата', u'8.0', u'H00-H59'),
 (u' из них:\nязва роговицы', u'8.1', u'H16.0'),
 (u' из них:\nкатаракты', u'8.2', u'H25-H26'),
 (u'хориоретинальное воспаление', u'8.3', u'H30'),
 (u'отслойка сетчатки с разрывом сетчатки', u'8.4', u'H33.0'),
 (u'дегенерация макулы и заднего полюса', u'8.5', u'H35.3'),
 (u'глаукома', u'8.6', u'H40'),
 (u'дегенеративная миопия', u'8.7', u'H44.2'),
 (u'болезни зрительного нерва и зрительных путей', u'8.8', u'H46-H48'),
 (u'атрофия зрительного нерва', u'8.8.1', u'H47.2'),
 (u'слепота и пониженное зрение', u'8.9', u'H54'),
 (u'из них: слепота обоих глаз', u'8.9.1', u'H54.0'),
 (u'Болезни уха и сосцевидного отростка', u'9.0', u'H60-H95'),
 (u'болезни среднего уха и сосцевидного отростка', u'9.1', u'H65-H66, H68-H74'),
 (u'из них: острый отит', u'9.1.1', u'H65.0, H65.1, H66.0'),
 (u'хронический отит', u'9.1.2', u'H65.2-4, H66.1-3'),
 (u'болезни слуховой (евстахиевой) трубы', u'9.1.3', u'H68-H69'),
 (u'перфорация барабанной перепонки', u'9.1.4', u'H72'),
 (u'другие болезни среднего уха и сосцевидного отростка', u'9.1.5', u'H74'),
 (u'болезни внутреннего уха', u'9.2', u'H80, H81, H83'),
 (u'из них: отосклероз', u'9.2.1', u'H80'),
 (u'болезнь Меньера', u'9.2.2', u'H81.0'),
 (u'кондуктивная и нейросенсорная потеря слуха', u'9.3', u'H90'),
 (u'из них: кондуктивная потеря слуха двусторонняя', u'9.3.1', u'H90.0'),
 (u'нейросенсорная потеря слуха двусторонняя', u'9.3.2', u'H90.3'),
 (u'Болезни системы кровообращения', u'10.0', u'I00-I99'),
 (u'из них:\nострая ревматичесская лихорадка', u'10.1', u'I00-I02'),
 (u'хронические ревматические болезни сердца', u'10.2', u'I05-I09'),
 (u'из них: ревматические поражения клапанов', u'10.2.1', u'I05-I08'),
 (u'болезни, характеризующиеся повышенным кровяным давлением', u'10.3', u'I10-I13'),
 (u'из них:\nэссенциальная гипертензия', u'10.3.1', u'I10'),
 (u'гипертензивная болезнь сердца (гипертоническая болезнь с преимущественным поражением сердца)', u'10.3.2', u'I11'),
 (u'гипертензивная болезнь почек (гипертоническая болезнь с преимущественным поражением почек)', u'10.3.3', u'I12'),
 (u'гипертензивная болезнь сердца и почек (гипертоническая болезнь с преимущественным поражением сердца и почек)', u'10.3.4', u'I13'),
 (u'ишемические болезни сердца', u'10.4', u'I20-I25'),
 (u'из них:\nстенокардия', u'10.4.1', u'I20'),
 (u'из нее:\nнестабильная стенокардия', u'10.4.1.1', u'I20.0'),
 (u'острый инфаркт миокарда', u'10.4.2', u'I21'),
 (u'повторный инфаркт миокарда', u'10.4.3', u'I22'),
 (u'другие формы острой ишемической болезни сердца', u'10.4.4', u'I24'),
 (u'хроническая ишемическая болезнь сердца', u'10.4.5', u'I25'),
 (u'из нее постинфарктный кардиосклероз', u'10.4.5.1', u'I25.8'),
 (u'легочная эмболия', u'10.5', u'I26'),
 (u'другие болезни сердца', u'10.6', u'I30- I51'),
 (u'из них:\nострый перикардит', u'10.6.1', u'I30'),
 (u'острый и подострый эндокардит', u'10.6.2', u'I33'),
 (u'острый миокардит', u'10.6.3', u'I40'),
 (u'кардиомиопатия', u'10.6.4', u'I42'),
 (u'предсердно-желудочковая [атриовентрикулярная] блокада', u'10.6.5', u'I44.0-I44.3'),
 (u'желудочковая тахикардия', u'10.6.6', u'I47.2'),
 (u'фибрилляция и трепетание предсердий', u'10.6.7', u'I48'),
 (u'цереброваскулярные болезни', u'10.7', u'I60-I69'),
 (u'из них:\nсубарахноидальное кровоизлияние', u'10.7.1', u'I60'),
 (u'внутримозговые и другие внутричерепные кровоизлияния', u'10.7.2', u'I61, I62'),
 (u'инфаркт мозга', u'10.7.3', u'I63'),
 (u'инсульт неуточненный, как кровоизлияние или инфаркт', u'10.7.4', u'I64'),
 (u'закупорка и стеноз прецеребральных, церебральных артерий, не приводящие к инфаркту мозга', u'10.7.5', u'I65- I66'),
 (u'другие цереброваскулярные болезни', u'10.7.6', u'I67'),
 (u'из них: церебральный атеросклероз', u'10.7.6.1', u'I67.2'),
 (u'атеросклероз артерий конечностей, тромбангиит облитерирующий ', u'10.8', u'I70.2, I73.1'),
 (u'болезни вен, лимфатических сосудов и лимфатических узлов', u'10.9', u'I80-I89'),
 (u'из них:\nфлебит и тромбофлебит', u'10.9.1', u'I80'),
 (u'тромбоз портальной вены', u'10.9.2', u'I81'),
 (u'варикозное расширение вен нижних конечностей', u'10.9.3', u'I83'),
 (u'Болезни органов дыхания', u'11.0', u'J00-J98'),
 (u' из них:\nострые респираторные инфекции верхних дыхательных путей', u'11.1', u'J00-J06'),
 (u'из них:\nострый ларингит и трахеит', u'11.1.1', u'J04'),
 (u'острый обструктивный ларингит [круп] и эпиглоттит', u'11.1.2', u'J05'),
 (u'грипп', u'11.2', u'J09-J11'),
 (u'пневмонии', u'11.3', u'J12-J18'),
 (u'острые респираторные инфекции нижних дыхательных путей ', u'11.4', u'J20-J22'),
 (u'аллергический ринит (поллиноз)', u'11.5', u'J30.1'),
 (u'хронические болезни миндалин и аденоидов, перитонзиллярный абсцесс', u'11.6', u'J35- J36'),
 (u'бронхит хронический и неуточненный, эмфизема', u'11.7', u'J40-J43'),
 (u'другая хроническая обструктивная легочная болезнь', u'11.8', u'J44'),
 (u'бронхоэктатическая болезнь', u'11.9', u'J47'),
 (u'астма; астматический статус', u'11.10', u'J45, J46'),
 (u'другие интерстициальные легочные болезни, гнойные и некротические состояния нижних дыхательных путей, другие болезни плевры', u'11.11', u'J84-J94'),
 (u'Болезни органов пищеварения', u'12.0', u'K00-K92'),
 (u' из них:\nязва желудка и двенадцатиперстной кишки', u'12.1', u'K25-K26'),
 (u'гастрит и дуоденит', u'12.2', u'K29'),
 (u'грыжи', u'12.3', u'K40-K46'),
 (u'неинфекционный энтерит и колит', u'12.4', u'K50-K52'),
 (u'из них:\nболезнь Крона', u'12.4.1', u'K50'),
 (u'язвенный колит', u'12.4.2', u'K51'),
 (u'другие болезни кишечника', u'12.5', u'K55-K63'),
 (u'из них:\nпаралитический илеус и непроходимость кишечника без грыжи', u'12.5.1', u'K56'),
 (u'дивертикулярная болезнь кишечника', u'12.5.2', u'K57'),
 (u'синдром раздраженного кишечника', u'12.5.3', u'K58'),
 (u'трещина и свищ области заднего прохода и прямой кишки', u'12.5.4', u'K60'),
 (u'абсцесс области заднего прохода и прямой кишки', u'12.5.5', u'K61'),
 (u'геморрой', u'12.6', u'K64'),
 (u'перитонит', u'12.7', u'K65'),
 (u'болезни печени', u'12.8', u'K70-K76'),
 (u'из них:\nфиброз и цирроз печени', u'12.8.1', u'K74'),
 (u'болезни желчного пузыря, желчевыводящих путей', u'12.9', u'K80-K83'),
 (u'болезни поджелудочной железы', u'12.10', u'K85-K86'),
 (u'из них:\nострый панкреатит', u'12.10.1', u'K85'),
 (u'Болезни кожи и подкожной клетчатки', u'13.0', u'L00-L98'),
 (u'из них:\nпузырчатка', u'13.1', u'L10'),
 (u'буллезный пемфигоид', u'13.2', u'L12'),
 (u'дерматит герпетиформный Дюринга', u'13.3', u'L13.0'),
 (u'псориаз, всего', u'13.4', u'L40'),
 (u'из него:\nпсориаз артропатический', u'13.4.1', u'L40.5'),
 (u'дискоидная красная волчанка', u'13.5', u'L93.0'),
 (u'локализованная склеродермия', u'13.6', u'L94.0'),
 (u'Болезни костно-мышечной системы и соединительной ткани', u'14.0', u'M00-M99'),
 (u'из них:\nартропатии', u'14.1', u'M00-M25'),
 (u'из них:\nреактивные артропатии', u'14.1.1', u'M02'),
 (u'серопозитивный и другие ревматоидные артриты', u'14.1.2', u'M05-M06'),
 (u'юношеский (ювенильный) артрит', u'14.1.3', u'M08'),
 (u'артрозы', u'14.1.4', u'M15-M19'),
 (u'системные поражения соединительной ткани', u'14.2', u'M30-M35'),
 (u'из них: системная красная волчанка', u'14.2.1', u'M32'),
 (u'деформирующие дорсопатии', u'14.3', u'M40-M43'),
 (u'спондилопатии', u'14.4', u'M45-M49'),
 (u'из них: анкилозирующий спондилит', u'14.4.1', u'M45'),
 (u'поражения синовиальных оболочек и сухожилий', u'14.5', u'M65-M67'),
 (u'остеопатии и хондропатии', u'14.6', u'M80-M94'),
 (u'из них:\nостеопорозы', u'14.6.1', u'M80-M81'),
 (u'Болезни мочеполовой системы', u'15.0', u'N00-N99'),
 (u' из них:\nгломерулярные, тубулоинтерстициальные болезни почек, другие болезни почки и мочеточника', u'15.1', u'N00-N15, N25-N28'),
 (u'почечная недостаточность', u'15.2', u'N17-N19'),
 (u'мочекаменная болезнь', u'15.3', u'N20-N21, N23'),
 (u'другие болезни мочевой системы', u'15.4', u'N30-N32, N34-N36, N39'),
 (u'болезни предстательной железы', u'15.5', u'N40-N42'),
 (u'доброкачественная дисплазия молочной железы', u'15.6', u'N60'),
 (u'воспалительные болезни женских тазовых органов', u'15.7', u'N70-N73,N75-N76'),
 (u'из них:\nсальпингит и оофорит', u'15.7.1', u'N70'),
 (u'эндометриоз', u'15.8', u'N80'),
 (u'эрозия и эктропион шейки матки', u'15.9', u'N86'),
 (u'расстройства менструаций ', u'15.10', u'N91-N94'),
 (u'женское бесплодие', u'15.11', u'N97'),
 (u'Беременность, роды и послеродовой период', u'16.0', u'O00-O99'),
 (u'Отдельные состояния, возникающие в перинатальном периоде', u'17.0', u'P00-P96'),
 (u'Врожденные аномалии, пороки развития, деформации и хромосомные нарушения', u'18.0', u'Q00-Q99'),
 (u'из них:\nврожденные аномалии [пороки развития] нервной системы', u'18.1', u'Q00-Q07'),
 (u'врожденные аномалии глаза', u'18.2', u'Q10-Q15'),
 (u'врожденные аномалии системы кровообращения', u'18.3', u'Q20-Q28'),
 (u'врожденные аномалии органов пищеварения', u'18.4', u'Q38-Q45'),
 (u'из них: болезнь Гиршпрунга', u'18.4.1', u'Q43'),
 (u'врожденные аномалии женских половых органов', u'18.5', u'Q50-Q52'),
 (u'неопределенность пола и псевдогермафродитизм', u'18.6', u'Q56'),
 (u'врожденный ихтиоз', u'18.7', u'Q80'),
 (u'нейрофиброматоз (незлокачественный)', u'18.8', u'Q85.0'),
 (u'синдром Дауна', u'18.9', u'Q90'),
 (u'Симптомы, признаки и оклонения от нормы, выявленные при клинических и лабораторных исследованиях, не классифицированные в других рубриках', u'19.0', u'R00-R99'),
 (u'Травмы, отравления и некоторые другие последствия воздействия внешних причин', u'20.0', u'S00-T98'),
 (u'из них:\nпереломы', u'20.1', u'S02,S12,S22,S32,S42,S52,S62,S72,S82,S92,T02,T08,T10,T12,T14.2'),
 (u'из них:\nпереломы черепа и лицевых костей', u'20.1.1', u'S02'),
 (u'внутричерепные травмы', u'20.2', u'S06'),
 (u'термические и химические ожоги', u'20.3', u'T20-T30'),
 (u'отравления лекарственными средствами, медикаментами и биологическими веществами', u'20.4', u'T36-T50'),
 (u'из них: отравление наркотиками', u'20.4.1', u'T40.0-T40.6'),
 (u'токсическое действие веществ преимущественно немедицинского назначения', u'20.5', u'T51-T65'),
 (u'из них:\nтоксическое действие алкоголя', u'20.5.1', u'T51'),
 (u' Кроме того:\nфакторы, влияющие на состояние здоровья населения и обращения в учреждения здравоохранения', u'21.0', u'Z00-Z99')
]
RowsChildren = [(u' в том числе с заболеваниями:\nострые респираторные инфекции верхних дыхательных путей, грипп', u'2', u'J00-J06, J10-J11'),
 (u'пневмонии', u'3', u'J12-J18'),
 (u'инфекции кожи и подкожной клетчатки', u'4', u'L00-L08'),
 (u'отдельные состояния, возникающие в перинатальном периоде', u'5', u'P00-P96'),
 (u'из них:\nзамедленный рост и недостаточность питания', u'5.1', u'P05'),
 (u'родовая травма-всего', u'5.2', u'P10-P15'),
 (u'из них:\nразрыв внутричерепных тканей и кровоизлияние вследствие родовой травмы', u'5.2.1', u'P10'),
 (u'дыхательные нарушения, характерные для перинатального периода-всего', u'5.3', u'P20-P28'),
 (u'из них:\nвнутриутробная гипоксия, асфиксия при родах', u'5.3.1', u'P20, P21'),
 (u'из них:\nдыхательное расстройство у новорожденных', u'5.3.2', u'P22'),
 (u'врожденная пневмония', u'5.3.3', u'P23'),
 (u'неонатальные аспирационные синдромы', u'5.3.4', u'P24'),
 (u'инфекционные болезни, специфичные для перинатального периода - всего', u'5.4', u'P35-P39'),
 (u'из них:\nбактериальный сепсис новорожденного', u'5.4.1', u'P36'),
 (u'гемолитическая болезнь плода и новорожденного, водянка плода, обусловленная гемолитической болезнью; ядерная желтуха', u'5.5', u'P55-P57'),
 (u'неонатальная желтуха, обусловленная чрезмерным гемолизом, другими и неуточненными причинами', u'5.6', u'P58-P59'),
 (u'геморрагическая болезнь, диссеминированное внутрисосудистое свертывание у плода и новорожденного, другие перинатальные гематологические нарушения', u'5.7', u'P53, P60, P61'),
 (u'врожденные аномалии(пороки развития), деформации и хромосомные нарушения', u'6', u'Q00-Q99')]
RowsChildren4001 = [(u'Операций при врожденных пороках развития(ВПР) – всего', u'1', u'Q00-Q99'),
 (u'из них: ВПР системы кровообращения', u'1.1', u'Q20-Q28'),
 (u'из них у родившихся в сроки 22-37 недель беременности', u'1.1.1', u'Q20-Q28'),
 (u'ВПР мочеполовой системы', u'1.2', u'Q60-Q64, Q50-Q56'),
 (u'из них у родившихся в сроки 22-37 недель беременности', u'1.2.1', u'Q60-Q64, Q50-Q56'),
 (u'ВПР нервной системы', u'1.3', u'Q00-Q07'),
 (u'из них у родившихся в сроки 22-37 недель беременности', u'1.3.1', u'Q00-Q07'),
 (u'ВПР органов зрения', u'1.4', u'Q10-Q18'),
 (u'из них у родившихся в сроки 22-37 недель беременности', u'1.4.1', u'Q10-Q18'),
 (u'ВПР органов дыхания', u'1.5', u'Q30-Q34'),
 (u'из них у родившихся в сроки 22-37 недель беременности', u'1.5.1', u'Q30-Q34'),
 (u'расщелина губы и неба', u'1.6', u'Q35-Q37'),
 (u'из них у родившихся в сроки 22-37 недель беременности', u'1.6.1', u'Q35-Q37'),
 (u'ретинопатия недоношенных(родившихся в сроки 22-37 недель беременности)', u'1.7', u'H35.0, H35.1, H35.2, H36.0')]
Rows4100 = [(u'Оперировано больных – всего (чел.)', u'1'),
 (u'из них по ВМТ (чел.)', u'2'),
 (u'из них дети до 17 лет включительно (из гр.1) (чел.)', u'3'),
 (u'из них по ВМТ (чел.)', u'4'),
 (u'Из общего числа операций (стр.1, гр.3) проведено операций с использованием: лазерной  аппаратуры', u'5'),
 (u'криогенной аппаратуры', u'6'),
 (u'эндоскопической аппаратуры', u'7'),
 (u'из них  стерилизации женщин', u'8'),
 (u'Число общих анестезий оперированным', u'9'),
 (u'Умерло в результате общей анестезии', u'10')]
Rows4200 = [(u'на органе зрения (стр. 4.0) – микрохирургические', u'1'),
 (u'на ухе (стр.5.1) - слухоулучшающие', u'2'),
 (u'на желудке по поводу язвенной болезни (стр.9.1) - органосохраняющие', u'3'),
 (u'на сердце: по поводу врожденных пороков – детям в возрасте до 1 года (из стр. 7.1, гр.4)', u'4'),
 (u'катетерных аблаций (из стр. 7.3.2) - всего', u'5'),
 (u'из них умерло', u'6'),
 (u'в том числе проведено катетерных аблаций (из графы 5): детям (0-14 лет)', u'7'),
 (u'из них умерло', u'8'),
 (u'детям (15-17 лет)', u'9'),
 (u'из них умерло', u'10')]
Rows4201 = [(u'трансплантаций всего', u'1'),
 (u'из них умерло', u'2'),
 (u'в том числе детям', u'3'),
 (u'из них умерло', u'4'),
 (u'из них (из гр.1, 2, 3, 4  соответственно): почки', u'5'),
 (u'из них умерло', u'6'),
 (u'в том числе детям', u'7'),
 (u'из них умерло', u'8'),
 (u'поджелудочной железы', u'9'),
 (u'из них умерло', u'10'),
 (u'в том числе детям', u'11'),
 (u'из них умерло', u'12'),
 (u'сердца', u'13'),
 (u'из них умерло', u'14'),
 (u'в том числе детям', u'15'),
 (u'из них умерло', u'16'),
 (u'печени', u'17'),
 (u'из них умерло', u'18'),
 (u'в том числе детям', u'19'),
 (u'из них умерло', u'20'),
 (u'костного мозга', u'21'),
 (u'из них умерло', u'22'),
 (u'в том числе детям', u'23'),
 (u'из них умерло', u'24'),
 (u'легкого', u'25'),
 (u'из них умерло', u'26'),
 (u'в том числе детям', u'27'),
 (u'из них умерло', u'28')]
Rows4202 = [(u'эндопротезирование - всего', u'1'),
 (u'в том числе детям', u'2'),
 (u'из них(гр.1) суставов нижних конечностей', u'3'),
 (u'суставов верхних конечностей', u'4')]
Rows4400 = [(u'Из общего числа оперированных направлено на восстановительное лечение (долечивание)', u'1'),
 (u'из них после операций по поводу язвенной болезни желудка и 12-перстной кишки', u'2'),
 (u'удаления желчного пузыря', u'3'),
 (u'операций на сердце и магистральных сосудах', u'4'),
 (u'операций по поводу панкреатита (панкреонекроза)', u'5'),
 (u'после операций ортопедических, травматологических при дефектах и пороках развития позвоночника, пластики суставов, эндопротезирования и реэндопротезирования, реплантаций конечностей', u'6')]


class CEventOrderModel(CListModel):
    list = [
        u'',
        u'Плановый',
        u'Экстренный',
        u'Самотеком',
        u'Принудительный'
    ]
    def __init__(self):
        CListModel.__init__(self, CEventOrderModel.list)


class CStationaryF14SetupDialog(QtGui.QDialog, Ui_StationaryF14DCSetupDialog):

    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cmbOrgStructure.setOrgId(QtGui.qApp.currentOrgId())
        self.cmbOrgStructure.setValue(QtGui.qApp.currentOrgStructureId())

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrgStructure.setValue(params.get('orgStructureId', None))
        self.cmbOrder.setCurrentIndex(params.get('eventOrder', 0))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['orgStructureId'] = self.cmbOrgStructure.value()
        result['eventOrder'] = self.cmbOrder.currentIndex()
        return result
    

class CStationaryF142000_SetupDialog(CDialogBase, Ui_StationaryF14SetupDialog):

    def __init__(self, parent = None):
        CDialogBase.__init__(self, parent)
        self.setupUi(self)
        self.addModels('EventOrder', CEventOrderModel())
        self.cmbOrder.setModel(self.modelEventOrder)

        db = QtGui.qApp.db
        tableEventType = db.table('EventType')
        tableEventTypePurpose = db.table('rbEventTypePurpose')
        eventTypeFilter = db.joinAnd([
            tableEventType['purpose_id'].inlist(db.getIdList(tableEventTypePurpose, tableEventTypePurpose['id'], tableEventTypePurpose['code'].eq(CStationaryF142000.StationaryEventTypeCode))),
            tableEventType['deleted'].eq(0)
        ])

        self.lstEventType.setTable('EventType', filter=eventTypeFilter)
        self.lstOrgStructure.setTable('OrgStructure')

    def setTitle(self, title):
        self.setWindowTitle(title)

    def setParams(self, params):
        self.edtBegDate.setDate(params.get('begDate', QtCore.QDate.currentDate()))
        self.edtEndDate.setDate(params.get('endDate', QtCore.QDate.currentDate()))
        self.cmbOrder.setCurrentIndex(params.get('eventOrder', 0))
        self.lstEventType.setValues(params.get('eventTypeIdList', []))
        self.lstOrgStructure.setValues(params.get('orgStructureIdList', []))

    def params(self):
        result = {}
        result['begDate'] = self.edtBegDate.date()
        result['endDate'] = self.edtEndDate.date()
        result['eventOrder'] = self.cmbOrder.currentIndex()
        result['eventTypeIdList'] = self.lstEventType.values()
        result['orgStructureIdList'] = self.lstOrgStructure.values()
        return result


class CStationaryF014(CReport):

    def __init__(self, parent):
        CReport.__init__(self, parent)
        self.setTitle(u'Форма 014.')
        self.stationaryF14SetupDialog = None
        self.clientDeath = 8

    def getSetupDialog(self, parent):
        result = CStationaryF14SetupDialog(parent)
        result.setTitle(self.title())
        self.stationaryF14SetupDialog = result
        return result

    def dumpParams(self, cursor, params):

        def dateRangeAsStr(begDate, endDate):
            result = ''
            if begDate:
                result += u' с ' + forceString(begDate)
            if endDate:
                result += u' по ' + forceString(endDate)
            return result

        description = []
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventOrder = params.get('eventOrder', 0)
        if begDate and endDate:
            description.append(u'за период' + dateRangeAsStr(begDate, endDate))
        orgStructureId = params.get('orgStructureId', None)
        if orgStructureId:
            description.append(u'подразделение: ' + getOrgStructureFullName(orgStructureId))
        else:
            description.append(u'подразделение: ЛПУ')
        if eventOrder:
            eventOrderStr = u'по свойству "Доставлен по экстренным показаниям"'
        else:
            eventOrderStr = u'по атрибуту События "экстренно"'
        description.append(u'учет экстренных пациентов ' + eventOrderStr)
        description.append(u'отчёт составлен: ' + forceString(QtCore.QDateTime.currentDateTime()))
        columns = [('100%', [], CReportBase.AlignLeft)]
        table = createTable(cursor, columns, headerRowCount=len(description), border=0, cellPadding=2, cellSpacing=0)
        for i, row in enumerate(description):
            table.setText(i, 0, row)

        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertBlock()

    def getOrgStructureIdList(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        if treeItem:
            return treeItem.getItemIdList()
        return []

    def getOrgStructureId(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        if treeItem:
            return treeItem._id

    def getOrgStructureName(self, treeIndex):
        treeItem = treeIndex.internalPointer() if treeIndex.isValid() else None
        if treeItem:
            return treeItem._name


class CStationaryF142000(CStationaryF014):

    AutopsyEventTypeCode = '15'
    AutopsyEventTypePurposeCode = '5'
    StationaryEventTypeCode = '101'  # Событие "Стационар"
    PreliminaryDiagnosisTypeCodes = ['2', '7', '8', '11']  # Предварительный диагноз
    FinalDiagnosisTypeCodes = ['1', '4']  # заключительный диагноз
    StationaryMedicalAidTypeCodes = ['1', '2', '3']  # Стационарная помощь

    def __init__(self, parent=None):
        CStationaryF014.__init__(self, parent)
        self.setTitle(u'Форма 14. 2000')
        self.ageCategory = 0
        self.mapMainRows = {}
        self.reportMainData = []

    def getSetupDialog(self, parent):
        result = CStationaryF142000_SetupDialog(parent)
        result.setTitle(self.title())
        return result

    def getAgeCategoryCond(self, ageCategory=None):
        db = QtGui.qApp.db
        Client = db.table('Client')
        Event = db.table('Event')
        age = db.func.age(Client['birthDate'], Event['setDate'])
        ageCategoryCond = {
            CAgeCategory.newborn : age.lt(1),
            CAgeCategory.children: age.lt(18),
            CAgeCategory.adults  : age.ge(18),
            CAgeCategory.seniors : db.joinOr([db.joinAnd([Client['sex'].eq(1), age.ge(60)]),
                                              db.joinAnd([Client['sex'].eq(2), age.ge(55)])])
        }
        return ageCategoryCond[ageCategory or self.ageCategory]

    def selectLeaved(self, begDate, endDate, eventOrder, eventTypeIdList, orgStructureIdList):
        db = QtGui.qApp.db
        Action = db.table('Action')
        ActionType = db.table('ActionType')
        Client = db.table('Client')
        Event = db.table('Event')
        EventType = db.table('EventType')
        EventTypePurpose = db.table('rbEventTypePurpose')
        OrgStructure = db.table('OrgStructure')
        Person = db.table('Person')

        Leaved = Action.alias('Leaved')
        LeavedAT = ActionType.alias('LeavedAT')
        Received = Action.alias('Received')
        ReceivedAT = ActionType.alias('ReceivedAT')

        FinalDiagnosis = db.table('Diagnosis').alias('FinalDiagnosis')
        FinalDiagnosisType = db.table('rbDiagnosisType').alias('FinalDiagnosisType')
        FinalDiagnostic = db.table('Diagnostic').alias('FinalDiagnostic')

        def joinAPS(queryTable, actionTable, propertyName, alias):
            tableAP = db.table('ActionProperty').alias(alias + 'AP')
            tableAPS = db.table('ActionProperty_String').alias(alias + 'APS')
            tableAPT = db.table('ActionPropertyType').alias(alias + 'APT')
            queryTable = queryTable.leftJoin(tableAPT, [tableAPT['name'].like(propertyName), tableAPT['actionType_id'].eq(actionTable['actionType_id']), tableAPT['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(tableAP, [tableAP['type_id'].eq(tableAPT['id']), tableAP['action_id'].eq(actionTable['id']), tableAP['deleted'].eq(0)])
            queryTable = queryTable.leftJoin(tableAPS, tableAPS['id'].eq(tableAP['id']))
            return tableAPS, queryTable

        table = LeavedAT.innerJoin(Leaved, [Leaved['actionType_id'].eq(LeavedAT['id']), Leaved['deleted'].eq(0)])
        table = table.innerJoin(Event, [Event['id'].eq(Leaved['event_id']), Event['deleted'].eq(0)])
        table = table.innerJoin(ReceivedAT, [ReceivedAT['flatCode'].eq('received'), ReceivedAT['deleted'].eq(0)])
        table = table.innerJoin(Received, [Received['actionType_id'].eq(ReceivedAT['id']), Received['event_id'].eq(Event['id']), Received['deleted'].eq(0)])
        table = table.innerJoin(EventType, [EventType['id'].eq(Event['eventType_id']), EventType['deleted'].eq(0)])
        table = table.innerJoin(EventTypePurpose, EventTypePurpose['id'].eq(EventType['purpose_id']))
        table = table.innerJoin(Client, [Client['id'].eq(Event['client_id']), Client['deleted'].eq(0)])

        table = table.innerJoin(FinalDiagnosisType, FinalDiagnosisType['code'].inlist(CStationaryF142000.FinalDiagnosisTypeCodes))
        table = table.innerJoin(FinalDiagnostic, [FinalDiagnostic['event_id'].eq(Event['id']), FinalDiagnostic['diagnosisType_id'].eq(FinalDiagnosisType['id']), FinalDiagnostic['deleted'].eq(0)])
        table = table.innerJoin(FinalDiagnosis, [FinalDiagnosis['id'].eq(FinalDiagnostic['diagnosis_id']), FinalDiagnosis['deleted'].eq(0)])

        DeliveredByAPS, table = joinAPS(table, Received, u'Кем доставлен', 'DeliveredBy')
        HospReusltAPS, table = joinAPS(table, Leaved, u'Исход госпитализации', 'HospResult')

        table = table.innerJoin(Person, [Person['id'].eq(Event['execPerson_id']), Person['deleted'].eq(0)])
        table = table.innerJoin(OrgStructure, [OrgStructure['id'].eq(Person['orgStructure_id']), OrgStructure['deleted'].eq(0)])

        cond = [
            LeavedAT['flatCode'].eq('leaved'),
            LeavedAT['deleted'].eq(0),
            Event['execDate'].dateGe(begDate),
            Event['execDate'].dateLe(endDate)
        ]

        if self.ageCategory:
            cond.append(self.getAgeCategoryCond())

        if eventOrder:
            cond.append(Event['order'].eq(eventOrder))

        if eventTypeIdList:
            cond.append(EventType['id'].inlist(eventTypeIdList))
        else:
            cond.append(EventTypePurpose['code'].eq(CStationaryF142000.StationaryEventTypeCode))

        if orgStructureIdList:
            cond.append(OrgStructure['id'].inlist(reduce(add, map(getOrgStructureDescendants, orgStructureIdList))))

        cols = [
            db.count('*').alias('cnt'),
            FinalDiagnosis['MKB'].alias('finalMKB'),
            db.makeField(DeliveredByAPS['value'].ne(u'')).alias('byUrgent'),
            db.makeField(DeliveredByAPS['value'].like(u'%СМП%')).alias('byEmergency'),
            db.sum(db.greatest(db.datediff(Leaved['endDate'], Received['begDate']), 1)).alias('bedDays'),
            db.makeField(HospReusltAPS['value'].inlist([u'смерть', u'умер'])).alias('death')
        ]

        group = [
            'finalMKB',
            'byUrgent',
            'byEmergency',
            'death',
        ]

        if self.ageCategory == CAgeCategory.children:
            cols.extend([
                db.makeField(self.getAgeCategoryCond(CAgeCategory.newborn)).alias('isNewborn')
            ])
            group.extend([
                'isNewborn'
            ])

        stmt = db.selectStmt(table, cols, cond, group)
        return db.query(stmt)

    def selectAutopsy(self, begDate, endDate, orgStructureIdList):
        db = QtGui.qApp.db
        Client = db.table('Client')
        Event = db.table('Event')
        EventType = db.table('EventType')
        Diagnosis = db.table('Diagnosis')
        DiagnosisType = db.table('rbDiagnosisType')
        Diagnostic = db.table('Diagnostic')

        FinalDiagnosis = Diagnosis.alias('FinalDiagnosis')
        FinalDiagnostic = Diagnostic.alias('FinalDiagnostic')
        FinalDiagnosisType = DiagnosisType.alias('FinalDiagnosisType')

        PreliminaryDiagnosis = Diagnosis.alias('PreliminaryDiagnosis')
        PreliminaryDiagnostic = Diagnostic.alias('PreliminaryDiagnostic')
        PreliminaryDiagnosisType = DiagnosisType.alias('PreliminaryDiagnosisType')

        table = EventType.innerJoin(Event, [Event['eventType_id'].eq(EventType['id']), Event['deleted'].eq(0)])
        table = table.innerJoin(Client, [Client['id'].eq(Event['client_id']), Client['deleted'].eq(0)])

        table = table.innerJoin(FinalDiagnosisType, FinalDiagnosisType['code'].inlist(CStationaryF142000.FinalDiagnosisTypeCodes))
        table = table.innerJoin(FinalDiagnostic, [FinalDiagnostic['event_id'].eq(Event['id']), FinalDiagnostic['diagnosisType_id'].eq(FinalDiagnosisType['id']), FinalDiagnostic['deleted'].eq(0)])
        table = table.innerJoin(FinalDiagnosis, [FinalDiagnosis['id'].eq(FinalDiagnostic['diagnosis_id']), FinalDiagnosis['deleted'].eq(0)])

        table = table.innerJoin(PreliminaryDiagnosisType, PreliminaryDiagnosisType['code'].inlist(CStationaryF142000.PreliminaryDiagnosisTypeCodes))
        table = table.innerJoin(PreliminaryDiagnostic, [PreliminaryDiagnostic['event_id'].eq(Event['id']), PreliminaryDiagnostic['diagnosisType_id'].eq(PreliminaryDiagnosisType['id']), PreliminaryDiagnostic['deleted'].eq(0)])
        table = table.innerJoin(PreliminaryDiagnosis, [PreliminaryDiagnosis['id'].eq(PreliminaryDiagnostic['diagnosis_id']), PreliminaryDiagnosis['deleted'].eq(0)])

        cond = [
            EventType['code'].eq(CStationaryF142000.AutopsyEventTypeCode),
            EventType['deleted'].eq(0),
            Event['execDate'].dateGe(begDate),
            Event['execDate'].dateLe(endDate)
        ]

        if self.ageCategory:
            cond.append(self.getAgeCategoryCond())

        cols = [
            FinalDiagnosis['MKB'].alias('finalMKB'),
            db.count(Event['id'], distinct=True).alias('cnt'),
            db.countIf(FinalDiagnosis['MKB'].ne(PreliminaryDiagnosis['MKB']), Event['id'], distinct=True).alias('cntDiff')
        ]

        group = Event['id']

        stmt = db.selectStmt(table, cols, cond, group)
        return db.query(stmt)

    def createTable(self, cursor, params):
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'1. СОСТАВ БОЛЬНЫХ В СТАЦИОНАРЕ, СРОКИ И ИСХОДЫ ЛЕЧЕНИЯ\n(2000)')
        cursor.insertBlock()
        self.dumpParams(cursor, params)

        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()

        name = {
            CAgeCategory.adults: u'А. Взрослые (18 лет и старше)',
            CAgeCategory.seniors: u'Б. Взрослые старше трудоспособного возраста (с 55 лет у женщин и с 60 лет у мужчин)',
            CAgeCategory.children: u'В. Дети (в возрасте 0-17 лет включительно)'
        }

        keyColumnWidth = 15.0
        keyColumn = ('%.4f%%' % keyColumnWidth, [u'Наименование болезни', u'', u'', u'', u'1'], CReportBase.AlignLeft)

        if self.ageCategory == CAgeCategory.children:
            cols = [
                [u'№ строки', u'', u'', u'', u'2'],
                [u'Код по МКБ-10 пересмотра', u'', u'', u'', u'3'],
                [name.get(self.ageCategory), u'Выписано пациентов', u'Всего', u'', u'18'],
                [u'', u'', u'из них доставленных по экстренным показаниям', u'', u'19'],
                [u'', u'', u'из гр.19: пациентов, доставленных скорой мед. помощью', u'', u'20'],
                [u'', u'', u'из гр.18 в возрасте до 1 года', u'', u'21'],
                [u'', u'Проведено выписанными койко-дней', u'', u'', u'22'],
                [u'', u'из них (из гр.22) в возрасте до 1 года', u'', u'', u'23'],
                [u'', u'Умерло', u'Всего', u'', u'24'],
                [u'', u'', u'Из них:', u'Проведено патолого-анатомических вскрытий', u'25'],
                [u'', u'', u'', u'Установлено расхождений диагнозов', u'26'],
                [u'', u'', u'из гр.10: умерло в возрасте до 1 года', u'', u'27'],
            ]

        else:
            cols = [
                [u'№ строки', u'', u'', u'', u'2'],
                [u'Код по МКБ-10 пересмотра', u'', u'', u'', u'3'],
                [name.get(self.ageCategory), u'Выписано больных', u'Всего', u'', u'4'],
                [u'', u'', u'из них доставленных по экстренным показаниям', u'', u'5'],
                [u'', u'', u'из них пациентов, доставленных скорой мед. помощью (из гр.5)', u'', u'6'],
                [u'', u'Проведено выписанными койко-дней', u'', u'', u'7'],
                [u'', u'Умерло', u'Всего', u'', u'8'],
                [u'', u'', u'Из них', u'Проведено патолого-анатомических вскрытий', u'9'],
                [u'', u'', u'', u'Установлено расхождений диагнозов', u'10'],
            ]

        columnWidth = '%.4f%%' % ((100.0 - keyColumnWidth) / len(cols))
        table = createTable(cursor, [keyColumn] + [(columnWidth, descr, CReportBase.AlignCenter) for descr in cols])

        for c in [0, 1, 2]:
            table.mergeCells(0, c, 4, 1)

        if self.ageCategory in (CAgeCategory.adults, CAgeCategory.seniors):
            table.mergeCells(0, 3, 1, 7)
            table.mergeCells(1, 3, 1, 3)
            for c in [3, 4, 5]:
                table.mergeCells(2, c, 2, 1)
            table.mergeCells(1, 6, 3, 1)
            table.mergeCells(1, 7, 1, 3)
            table.mergeCells(7, 2, 2, 1)
            table.mergeCells(2, 8, 1, 2)
        elif self.ageCategory == CAgeCategory.children:
            table.mergeCells(0, 3, 1, 10)
            table.mergeCells(1, 3, 1, 4)
            for c in [3, 4, 5, 6]:
                table.mergeCells(2, c, 2, 1)
            for c in [7, 8]:
                table.mergeCells(1, c, 3, 1)
            table.mergeCells(1, 9, 1, 4)
            for c in [9, 12]:
                table.mergeCells(2, c, 2, 1)
            table.mergeCells(2, 10, 1, 2)

        return table

    def processLeaved(self, record):
        raise NotImplementedError

    def processAutopsy(self, record):
        raise NotImplementedError

    def build(self, params):
        eventOrder = params.get('eventOrder', 0)
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        eventTypeIdList = params.get('eventTypeIdList', [])
        orgStructureIdList = params.get('orgStructureIdList', [])

        self.rowSize = 7 if self.ageCategory != CAgeCategory.children else 10
        self.mapMainRows = createMapCodeToRowIdx([row[2] for row in MainRows])
        self.reportMainData = [[0] * self.rowSize for _ in xrange(len(MainRows))]

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)

        table = self.createTable(cursor, params)

        query = self.selectLeaved(begDate, endDate, eventOrder, eventTypeIdList, orgStructureIdList)
        self.addQueryText(forceString(query.lastQuery()))
        while query.next():
            self.processLeaved(query.record())

        query = self.selectAutopsy(begDate, endDate, orgStructureIdList)
        self.addQueryText(forceString(query.lastQuery()))
        while query.next():
            self.processAutopsy(query.record())

        for row, rowDescr in enumerate(MainRows):
            reportLine = self.reportMainData[row]
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            table.setText(i, 2, rowDescr[2])
            for col in xrange(self.rowSize):
                table.setText(i, 3+col, reportLine[col])

        return doc


class CStationaryF142000_Adults(CStationaryF142000):

    def __init__(self, parent=None):
        CStationaryF142000.__init__(self, parent)
        self.ageCategory = CAgeCategory.adults

    def processLeaved(self, record):
        finalMKB = normalizeMKB(forceString(record.value('finalMKB')))
        cnt = forceInt(record.value('cnt'))
        byUrgent = forceBool(record.value('byUrgent'))
        byEmergency = forceBool(record.value('byEmergency'))
        bedDays = forceInt(record.value('bedDays'))
        death = forceBool(record.value('death'))

        for row in self.mapMainRows.get(finalMKB, []):
            reportLine = self.reportMainData[row]
            reportLine[0] += cnt  # Выписано
            if byUrgent:
                reportLine[1] += cnt  # По экстренным показаниям
            if byEmergency:
                reportLine[2] += cnt  # По экстренным показаниям: СМП
            reportLine[3] += bedDays  # Койко-дни
            if death:
                reportLine[4] += cnt  # Умерло

    def processAutopsy(self, record):
        finalMKB = normalizeMKB(forceString(record.value('finalMKB')))
        cnt = forceInt(record.value('cnt'))
        cntDiff = forceInt(record.value('cntDiff'))

        for row in self.mapMainRows.get(finalMKB, []):
            reportLine = self.reportMainData[row]
            reportLine[5] += cnt
            reportLine[6] += cntDiff


class CStationaryF142000_Seniors(CStationaryF142000_Adults):

    def __init__(self, parent=None):
        CStationaryF142000_Adults.__init__(self, parent)
        self.ageCategory = CAgeCategory.seniors


class CStationaryF142000_Children(CStationaryF142000):

    def __init__(self, parent=None):
        CStationaryF142000.__init__(self, parent)
        self.ageCategory = CAgeCategory.children

    def processLeaved(self, record):
        finalMKB = normalizeMKB(forceString(record.value('finalMKB')))
        cnt = forceInt(record.value('cnt'))
        byUrgent = forceBool(record.value('byUrgent'))
        byEmergency = forceBool(record.value('byEmergency'))
        bedDays = forceInt(record.value('bedDays'))
        death = forceBool(record.value('death'))
        isNewborn = forceBool(record.value('isNewborn'))

        for row in self.mapMainRows.get(finalMKB, []):
            reportLine = self.reportMainData[row]
            reportLine[0] += cnt  # Выписано
            if byUrgent:
                reportLine[1] += cnt  # По экстр. показаниям
            if byEmergency:
                reportLine[2] += cnt  # По экстр. показаниям: СМП
            if isNewborn:
                reportLine[3] += cnt  # Выписано: до 1 года
            reportLine[4] += bedDays  # Койко-дни
            if isNewborn:
                reportLine[5] += bedDays  # Койко-дни: до 1 года
            if death:
                reportLine[6] += cnt  # Умерло
                if isNewborn:
                    reportLine[9] += cnt  # Умерло: до 1 года

    def processAutopsy(self, record):
        finalMKB = normalizeMKB(forceString(record.value('finalMKB')))
        cnt = forceInt(record.value('cnt'))
        cntDiff = forceInt(record.value('cntDiff'))

        for row in self.mapMainRows.get(finalMKB, []):
            reportLine = self.reportMainData[row]
            reportLine[7] += cnt
            reportLine[8] += cntDiff

class CStationaryF143000(CStationaryF014):

    def __init__(self, parent=None):
        CStationaryF014.__init__(self, parent)
        self.stationaryF14SetupDialog = None

    def build(self, params):
        orgStructureIndex = self.stationaryF14SetupDialog.cmbOrgStructure._model.index(self.stationaryF14SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14SetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureId = self.getOrgStructureId(orgStructureIndex)
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        params['orgStructureId'] = orgStructureId
        if not begDate or not endDate:
            currentDate = QtCore.QDate.currentDate()
            begDate = QtCore.QDate(currentDate.year(), 1, 1)
            endDate = currentDate
        if begDate and endDate:
            rowSize = 6
            mapRowsChildrenOutMoving = createMapCodeToRowIdx([ row[2] for row in RowsChildren ])
            reportMainDataOutMoving = [ [0] * rowSize for row in xrange(len(RowsChildren)) ]
            reportMainDataAll = [[0] * rowSize]
            reportMainDataOthers = [[0] * rowSize]

            def findReceived(orgStructureIdList, orgStructureId, begDateTime, endDateTime):
                db = QtGui.qApp.db
                tableAPT = db.table('ActionPropertyType')
                tableAP = db.table('ActionProperty')
                tableActionType = db.table('ActionType')
                tableAction = db.table('Action')
                tableEvent = db.table('Event')
                tableClient = db.table('Client')
                tableAPOS = db.table('ActionProperty_OrgStructure')
                tableOS = db.table('OrgStructure')
                tableDiagnosis = db.table('Diagnosis')
                tableDiagnostic = db.table('Diagnostic')
                tableRBDiagnosisType = db.table('rbDiagnosisType')
                tableEventType = db.table('EventType')
                tableRBMedicalAidType = db.table('rbMedicalAidType')
                queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
                queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
                queryTable = queryTable.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
                queryTable = queryTable.innerJoin(tableRBMedicalAidType, tableEventType['medicalAidType_id'].eq(tableRBMedicalAidType['id']))
                queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
                queryTable = queryTable.leftJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
                queryTable = queryTable.leftJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
                queryTable = queryTable.innerJoin(tableDiagnostic, tableEvent['id'].eq(tableDiagnostic['event_id']))
                queryTable = queryTable.innerJoin(tableDiagnosis, tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']))
                queryTable = queryTable.innerJoin(tableRBDiagnosisType, tableDiagnostic['diagnosisType_id'].eq(tableRBDiagnosisType['id']))
                cond = [tableActionType['id'].inlist(getActionTypeIdListByFlatCode('received%')),
                 tableAction['deleted'].eq(0),
                 tableEvent['deleted'].eq(0),
                 tableActionType['deleted'].eq(0),
                 tableClient['deleted'].eq(0),
                 tableEventType['deleted'].eq(0)]
                cond.append(tableRBMedicalAidType['code'].inlist([1, 2, 3]))
                if orgStructureId and orgStructureIdList:
                    queryTable = queryTable.innerJoin(tableAPOS, tableAPOS['id'].eq(tableAP['id']))
                    queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableAPOS['value']))
                    cond.append(tableOS['type'].ne(0))
                    cond.append(tableOS['deleted'].eq(0))
                    cond.append(db.joinAnd([tableOS['deleted'].eq(0),
                     tableAP['deleted'].eq(0),
                     tableAPT['deleted'].eq(0),
                     tableAP['action_id'].eq(tableAction['id'])]))
                    cond.append(tableOS['id'].inlist(orgStructureIdList))
                cond.append(u'Action.begDate >= Client.birthDate AND Action.begDate <= ADDDATE(Client.birthDate, 6)')
                joinOr1 = db.joinOr([tableAction['begDate'].isNull(), tableAction['begDate'].dateGe(begDateTime)])
                joinOr2 = db.joinOr([tableAction['begDate'].isNull(), tableAction['begDate'].dateLe(endDateTime)])
                cond.append(db.joinAnd([joinOr1, joinOr2]))
                cond.append(u"rbDiagnosisType.code = '1' OR (rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id AND (NOT EXISTS (SELECT DC.id FROM Diagnostic AS DC INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id WHERE DT.code = '1' AND DC.event_id = Event.id LIMIT 1)))")
                cols = u"Action.begDate, Action.endDate, Client.id AS clientId, Client.birthDate, Client.weight, Diagnosis.MKB, (SELECT ClientAttach.begDate FROM ClientAttach INNER JOIN rbAttachType ON ClientAttach.attachType_id=rbAttachType.id\nAND (rbAttachType.code='%s') AND (ClientAttach.deleted=0) WHERE Client.id=ClientAttach.client_id AND ((Action.begDate IS NULL) OR (ClientAttach.begDate IS NOT NULL AND Action.begDate IS NOT NULL AND DATE(ClientAttach.begDate)>=DATE(Action.begDate))) AND ((Action.endDate IS NULL) OR (ClientAttach.begDate IS NOT NULL AND Action.endDate IS NOT NULL AND DATE(ClientAttach.begDate)<=DATE(Action.endDate)))) AS clientAttachBegDate" % self.clientDeath
                records = db.getRecordListGroupBy(queryTable, cols, cond, 'Event.id')
                self.addQueryText(queryText=db.selectStmt(queryTable, cols, cond, group='Event.id'), queryDesc=u'CStationaryF143000 (может немного отличаться от настоящего)')
                reportDataAll = reportMainDataAll[0]
                reportDataOthers = reportMainDataOthers[0]
                for record in records:
                    MKBRec = normalizeMKB(forceString(record.value('MKB')))
                    clientAttachBegDate = forceDate(record.value('clientAttachBegDate'))
                    birthDate = forceDate(record.value('birthDate'))
                    weight = forceInt(record.value('weight'))
                    begDate = forceDate(record.value('begDate'))
                    endDate = forceDate(record.value('endDate'))
                    maxDeathDate = None
                    if clientAttachBegDate:
                        maxDeathDate = birthDate.addDays(6) if birthDate else None
                    for row in mapRowsChildrenOutMoving.get(MKBRec, []):
                        reportLine = reportMainDataOutMoving[row]
                        if weight >= 500 and weight < 1000:
                            reportLine[0] += 1
                        elif weight >= 1000:
                            reportLine[3] += 1
                        if clientAttachBegDate:
                            if weight >= 500 and weight < 1000:
                                if maxDeathDate and clientAttachBegDate <= maxDeathDate:
                                    reportLine[2] += 1
                                reportLine[1] += 1
                            elif weight >= 1000:
                                if maxDeathDate and clientAttachBegDate <= maxDeathDate:
                                    reportLine[5] += 1
                                reportLine[4] += 1

                    if not mapRowsChildrenOutMoving.get(MKBRec, []):
                        if weight >= 500 and weight < 1000:
                            reportDataOthers[0] += 1
                            if clientAttachBegDate:
                                if maxDeathDate and clientAttachBegDate <= maxDeathDate:
                                    reportDataOthers[2] += 1
                                reportDataOthers[1] += 1
                        elif weight >= 1000:
                            reportDataOthers[3] += 1
                            if clientAttachBegDate:
                                if maxDeathDate and clientAttachBegDate <= maxDeathDate:
                                    reportDataOthers[5] += 1
                                reportDataOthers[4] += 1
                    if weight >= 500 and weight < 1000:
                        reportDataAll[0] += 1
                        if clientAttachBegDate:
                            reportDataAll[1] += 1
                            if maxDeathDate and clientAttachBegDate and clientAttachBegDate <= maxDeathDate:
                                reportDataAll[2] += 1
                    elif weight >= 1000:
                        reportDataAll[3] += 1
                        if clientAttachBegDate:
                            reportDataAll[4] += 1
                            if maxDeathDate and clientAttachBegDate and clientAttachBegDate <= maxDeathDate:
                                reportDataAll[5] += 1

        doc = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(doc)
        cursor.setCharFormat(CReportBase.ReportTitle)
        cursor.insertText(u'2.Состав больных новорожденных, поступивших в возрасте 0-6 дней жизни, и исходы их лечения\n(3000)')
        cursor.insertBlock()
        self.dumpParams(cursor, params)
        cursor.setCharFormat(CReportBase.ReportBody)
        cursor.insertBlock()
        cols = [('25%', [u'Наименование заболеваний',
           u'',
           u'',
           u'1'], CReportBase.AlignLeft),
         ('5%', [u'№ строки',
           u'',
           u'',
           u'2'], CReportBase.AlignLeft),
         ('10%', [u'Код по МКБ X пересмотра',
           u'',
           u'',
           u'3'], CReportBase.AlignLeft),
         ('10%', [u'Массой тела при рождении до 1000 г(500-999 г)',
           u'Поступило больных в первые 0-6 дней после рождения',
           u'',
           u'4'], CReportBase.AlignLeft),
         ('10%', [u'',
           u'Из них умерло',
           u'всего',
           u'5'], CReportBase.AlignLeft),
         ('10%', [u'',
           u'',
           u'из них в первые 0-6 дней после рождения',
           u'6'], CReportBase.AlignLeft),
         ('10%', [u'Массой тела при рождении 1000 г и более',
           u'Поступило больных в первые 0-6 дней после рождения',
           u'',
           u'7'], CReportBase.AlignLeft),
         ('10%', [u'',
           u'Из них умерло',
           u'всего',
           u'8'], CReportBase.AlignLeft),
         ('10%', [u'',
           u'',
           u'из них в первые 0-6 дней после рождения',
           u'9'], CReportBase.AlignLeft)]
        table = createTable(cursor, cols)
        table.mergeCells(0, 0, 3, 1)
        table.mergeCells(0, 1, 3, 1)
        table.mergeCells(0, 2, 3, 1)
        table.mergeCells(0, 3, 1, 3)
        table.mergeCells(1, 4, 1, 2)
        table.mergeCells(1, 3, 2, 1)
        table.mergeCells(0, 6, 1, 3)
        table.mergeCells(1, 6, 2, 1)
        table.mergeCells(1, 7, 1, 2)
        row = table.addRow()
        table.setText(row, 0, u'Всего больных новорожденных')
        table.setText(row, 1, u'1')
        table.setText(row, 2, u'')
        findReceived(orgStructureIdList, orgStructureId, begDate, endDate)
        reportDataAll = reportMainDataAll[0]
        reportDataOthers = reportMainDataOthers[0]
        for col in xrange(rowSize):
            table.setText(row, 3 + col, reportDataAll[col])

        for row, rowDescr in enumerate(RowsChildren):
            reportLine = reportMainDataOutMoving[row]
            i = table.addRow()
            table.setText(i, 0, rowDescr[0])
            table.setText(i, 1, rowDescr[1])
            table.setText(i, 2, rowDescr[2])
            for col in xrange(rowSize):
                table.setText(i, 3 + col, reportLine[col])

        rowOthers = table.addRow()
        table.setText(rowOthers, 0, u'прочие болезни')
        table.setText(rowOthers, 1, u'7')
        table.setText(rowOthers, 2, u'')
        for col in xrange(rowSize):
            table.setText(rowOthers, 3 + col, reportDataOthers[col])

        return doc


class CStationaryF144000(CStationaryF014):

    def __init__(self, parent = None):
        CStationaryF014.__init__(self, parent)
        self.stationaryF14SetupDialog = None

    def build(self, params):
        orgStructureIndex = self.stationaryF14SetupDialog.cmbOrgStructure._model.index(self.stationaryF14SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14SetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex) if orgStructureIndex.row() else []
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        doc = QtGui.QTextDocument()
        if not begDate or not endDate:
            currentDate = QtCore.QDate.currentDate()
            begDate = QtCore.QDate(currentDate.year(), 1, 1)
            endDate = currentDate
        if begDate and endDate:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'3.Хирургическая работа учреждения\n(4000)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('19%', [u'Наименование операции',
               u'',
               u'',
               u'1'], CReportBase.AlignLeft),
             ('3%', [u'№ строки',
               u'',
               u'',
               u'2'], CReportBase.AlignLeft),
             ('3.25%', [u'Число операций, проведенных в стационаре',
               u'всего',
               u'',
               u'3'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'из них: детям 0-17 лет включительно',
               u'0-14 лет включительно',
               u'4'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'',
               u'из них (из гр.4) в возрасте до 1 года',
               u'5'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'',
               u'15-17 лет включительно',
               u'6'], CReportBase.AlignLeft),
             ('3.25%', [u'Из них операций с применением высоких медицинских технологий (ВМП)',
               u'всего',
               u'',
               u'7'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'из них: детям 0-17 лет включительно',
               u'0-14 лет включительно',
               u'8'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'',
               u'из них (из гр.8) в возрасте до 1 года',
               u'9'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'',
               u'15-17 лет включи-тельно',
               u'10'], CReportBase.AlignLeft),
             ('3.25%', [u'Число операций, при которых наблюдались осложнения в стационаре',
               u'всего',
               u'',
               u'11'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'из них: детям 0-17 лет включительно',
               u'0-14 лет включительно',
               u'12'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'',
               u'из них (из гр.12) в возрасте до 1 года',
               u'13'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'',
               u'15-17 лет включительно',
               u'14'], CReportBase.AlignLeft),
             ('3.25%', [u'из них после операций, с применением ВМП',
               u'всего',
               u'',
               u'15'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'из них: детям 0-17 лет включительно',
               u'0-14 лет включительно',
               u'16'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'',
               u'из них (из гр.16) в возрасте до 1 года',
               u'17'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'',
               u'15-17 лет включительно',
               u'18'], CReportBase.AlignLeft),
             ('3.25%', [u'Умерло оперированных в стационаре',
               u'всего',
               u'',
               u'19'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'из них: детям 0-17 лет включительно',
               u'0-14 лет включительно',
               u'20'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'',
               u'из них (из гр.20) в возрасте до 1 года',
               u'21'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'',
               u'15-17 лет включительно',
               u'22'], CReportBase.AlignLeft),
             ('3.25%', [u'из них умерло после операций, проведенных с применением ВМП',
               u'всего',
               u'',
               u'23'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'из них: детям 0-17 лет включительно',
               u'0-14 лет включительно',
               u'24'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'',
               u'из них (из гр.24) в возрасте до 1 года',
               u'25'], CReportBase.AlignLeft),
             ('3.25%', [u'',
               u'',
               u'15-17 лет включительно',
               u'26'], CReportBase.AlignLeft)]
            table = createTable(cursor, cols)
            table.mergeCells(0, 0, 3, 1)
            table.mergeCells(0, 1, 3, 1)
            table.mergeCells(0, 2, 1, 4)
            table.mergeCells(1, 2, 2, 1)
            table.mergeCells(1, 3, 1, 3)
            table.mergeCells(0, 6, 1, 4)
            table.mergeCells(1, 6, 2, 1)
            table.mergeCells(1, 7, 1, 3)
            table.mergeCells(0, 10, 1, 4)
            table.mergeCells(1, 10, 2, 1)
            table.mergeCells(1, 11, 1, 3)
            table.mergeCells(0, 14, 1, 4)
            table.mergeCells(1, 14, 2, 1)
            table.mergeCells(1, 15, 1, 3)
            table.mergeCells(0, 18, 1, 4)
            table.mergeCells(1, 18, 2, 1)
            table.mergeCells(1, 19, 1, 3)
            table.mergeCells(0, 22, 1, 4)
            table.mergeCells(1, 22, 2, 1)
            table.mergeCells(1, 23, 1, 3)
            mapCodeToRowIdx = self.getRowsSurgery()
            mapCodesToRowIdx = self.getSurgery(mapCodeToRowIdx, orgStructureIdList, begDate, endDate)
            keys = mapCodesToRowIdx.keys()
            keys.sort()
            for key in keys:
                items = mapCodesToRowIdx[key]
                i = table.addRow()
                for row, item in enumerate(items):
                    table.setText(i, row, forceString(item))

        return doc

    def getRowsSurgery(self):
        mapCodeToRowIdx = {}
        db = QtGui.qApp.db
        tableActionType = db.table('ActionType')
        cond = [tableActionType['deleted'].eq(0), tableActionType['class'].eq(2)]
        cond.append(db.joinOr([tableActionType['code'].like(u'1-2'), tableActionType['code'].like(u'А16%')]))
        stmt = db.selectStmt(tableActionType, [tableActionType['code'],
         tableActionType['name'],
         tableActionType['group_id'],
         tableActionType['id'].alias('actionTypeId')], cond,  order = u'ActionType.code, ActionType.group_id')
        records = db.query(stmt)
        self.addQueryText(queryText=forceString(records.lastQuery()), queryDesc=u'getRowsSurgery')
        numbers = [1]
        mapCodeToRowIdx[''] = (u'Всего операций', 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        while records.next():
            record = records.record()
            code = QtCore.QString(forceString(record.value('code')))
            name = forceString(record.value('name'))
            if not mapCodeToRowIdx.get(code, None):
                codeList = code.split('.')
                lenCodeList = len(codeList)
                if len(numbers) < lenCodeList:
                    for i in range(lenCodeList - len(numbers)):
                        numbers.append(0)

                elif len(numbers) > lenCodeList:
                    for i in range(len(numbers) - lenCodeList):
                        numbers[len(numbers) - (1 + i)] = 0

                numbers[lenCodeList - 1] += 1
                rowIdx = u'.'.join((str(number) for number in numbers))
                mapCodeToRowIdx[code] = (name,
                 rowIdx,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0,
                 0)
                rowIdx = []

        return mapCodeToRowIdx

    def getSurgery(self, mapCodeToRowIdx, orgStructureIdList, begDateTime, endDateTime):

        def setValueMapCodeToRowIdx(mapCodeToRowIdx, code, quotaTypeWTMP, ageClient, countDeathSurgery, countComplication):
            if mapCodeToRowIdx.get(code, None):
                items = mapCodeToRowIdx[code]
                valueName = items[0]
                valueRow = items[1]
                valueSurgery = items[2] + 1
                valueSurgeryChildren14 = items[3]
                valueSurgeryChildren1 = items[4]
                valueSurgeryChildren17 = items[5]
                valueSurgeryWTMP = items[6]
                valueSurgeryWTMP14 = items[7]
                valueSurgeryWTMP1 = items[8]
                valueSurgeryWTMP17 = items[9]
                valueComplication = items[10]
                valueComplication14 = items[11]
                valueComplication1 = items[12]
                valueComplication17 = items[13]
                valueComplicationWTMP = items[14]
                valueComplicationWTMP14 = items[15]
                valueComplicationWTMP1 = items[16]
                valueComplicationWTMP17 = items[17]
                valueDeath = items[18]
                valueDeath14 = items[19]
                valueDeath1 = items[20]
                valueDeath17 = items[21]
                valueDeathWTMP = items[22]
                valueDeathWTMP14 = items[23]
                valueDeathWTMP1 = items[24]
                valueDeathWTMP17 = items[25]
                if quotaTypeWTMP:
                    valueSurgeryWTMP += 1
                if countComplication:
                    valueComplication += 1
                if countComplication and quotaTypeWTMP:
                    valueComplicationWTMP += 1
                if countDeathSurgery:
                    valueDeath += 1
                if countDeathSurgery and quotaTypeWTMP:
                    valueDeathWTMP += 1
                if ageClient < 18:
                    if ageClient > 0 and ageClient < 15:
                        valueSurgeryChildren14 += 1
                        if quotaTypeWTMP:
                            valueSurgeryWTMP14 += 1
                        if countComplication:
                            valueComplication14 += 1
                        if countComplication and quotaTypeWTMP:
                            valueComplicationWTMP14 += 1
                        if countDeathSurgery:
                            valueDeath14 += 1
                        if countDeathSurgery and quotaTypeWTMP:
                            valueDeathWTMP14 += 1
                    elif ageClient > 0 and ageClient < 1:
                        valueSurgeryChildren1 += 1
                        if quotaTypeWTMP:
                            valueSurgeryWTMP1 += 1
                        if countComplication:
                            valueComplication1 += 1
                        if countComplication and quotaTypeWTMP:
                            valueComplicationWTMP1 += 1
                        if countDeathSurgery:
                            valueDeath1 += 1
                        if countDeathSurgery and quotaTypeWTMP:
                            valueDeathWTMP1 += 1
                    elif ageClient >= 15 and ageClient < 18:
                        valueSurgeryChildren17 += 1
                        if quotaTypeWTMP:
                            valueSurgeryWTMP17 += 1
                        if countComplication:
                            valueComplication17 += 1
                        if countComplication and quotaTypeWTMP:
                            valueComplicationWTMP17 += 1
                        if countDeathSurgery:
                            valueDeath17 += 1
                        if countDeathSurgery and quotaTypeWTMP:
                            valueDeathWTMP17 += 1
                mapCodeToRowIdx[code] = (valueName,
                 valueRow,
                 valueSurgery,
                 valueSurgeryChildren14,
                 valueSurgeryChildren1,
                 valueSurgeryChildren17,
                 valueSurgeryWTMP,
                 valueSurgeryWTMP14,
                 valueSurgeryWTMP1,
                 valueSurgeryWTMP17,
                 valueComplication,
                 valueComplication14,
                 valueComplication1,
                 valueComplication17,
                 valueComplicationWTMP,
                 valueComplicationWTMP14,
                 valueComplicationWTMP1,
                 valueComplicationWTMP17,
                 valueDeath,
                 valueDeath14,
                 valueDeath1,
                 valueDeath17,
                 valueDeathWTMP,
                 valueDeathWTMP14,
                 valueDeathWTMP1,
                 valueDeathWTMP17)

        if mapCodeToRowIdx:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableAction = db.table('Action')
            tableActionType = db.table('ActionType')
            tableClient = db.table('Client')
            tableRBService = db.table('rbService')
            tableEventType = db.table('EventType')
            tableRBMedicalAidType = db.table('rbMedicalAidType')
            table = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
            table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
            table = table.innerJoin(tableRBMedicalAidType, tableEventType['medicalAidType_id'].eq(tableRBMedicalAidType['id']))
            table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            cond = [tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('received%')),
             tableEvent['deleted'].eq(0),
             tableAction['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableClient['deleted'].eq(0),
             tableEventType['deleted'].eq(0)]
            cond.append(tableRBMedicalAidType['code'].inlist([1, 2, 3]))
            joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
            joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateGe(begDateTime), tableAction['begDate'].dateLe(endDateTime)])
            joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].dateGe(begDateTime)])
            joinOr4 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateLe(begDateTime), db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].dateGe(begDateTime)])])
            cond.append(db.joinOr([joinOr1,
             joinOr2,
             joinOr3,
             joinOr4]))
            if orgStructureIdList:
                cond.append(getDataOrgStructure(u'Направлен в отделение', orgStructureIdList))
            eventIdList = db.getDistinctIdList(table, 'Event.id', cond)
            if eventIdList:
                cols = [tableAction['id'].alias('actionId'),
                 tableAction['event_id'],
                 tableActionType['id'].alias('actionTypeId'),
                 tableActionType['group_id'].alias('groupId'),
                 tableActionType['code'],
                 tableActionType['name']]
                cols.append('IF((SELECT QuotaType.class FROM QuotaType WHERE QuotaType.id = ActionType.quotaType_id LIMIT 1) = 0, 1, 0) AS quotaTypeWTMP')
                cols.append('age(Client.birthDate, Event.setDate) AS ageClient')
                cols.append('%s AS countDeathSurgery' % getStringProperty(u'Исход операции', u"(APS.value LIKE 'умер%' OR APS.value LIKE 'смерть%')"))
                cols.append('%s AS countComplication' % getStringProperty(u'Осложнение', u"(APS.value NOT LIKE '' OR APS.value NOT LIKE ' ')"))
                table = tableAction.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))
                table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
                table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
                table = table.innerJoin(tableRBService, tableRBService['id'].eq(tableActionType['nomenclativeService_id']))
                cond = [tableAction['event_id'].inlist(eventIdList),
                 tableEvent['deleted'].eq(0),
                 tableAction['deleted'].eq(0),
                 tableActionType['deleted'].eq(0),
                 tableClient['deleted'].eq(0),
                 tableActionType['class'].inlist([2, 3]),
                 tableAction['endDate'].isNotNull()]
                #cond.append(db.joinOr([tableRBService['code'].like(u'1-2'), tableRBService['code'].like(u'А16%')]))
                cond.append(db.joinOr([tableActionType['serviceType'].eq('4'), db.joinOr([tableActionType['code'].like(u'1-2'), tableActionType['code'].like(u'А16%'), tableActionType['code'].like(u'6%'), tableActionType['code'].like(u'о%')])]))
                records = db.getRecordList(table, cols, cond, u'ActionType.group_id, ActionType.code')
                self.addQueryText(queryText=db.selectStmt(table, cols, cond, order=u'ActionType.group_id, ActionType.code'), queryDesc=u'mapCodeToRowIdx (может немного отличаться от настоящего.)')
                for record in records:
                    quotaTypeWTMP = forceInt(record.value('quotaTypeWTMP'))
                    ageClient = forceInt(record.value('ageClient'))
                    countDeathSurgery = forceInt(record.value('countDeathSurgery'))
                    countComplication = forceInt(record.value('countComplication'))
                    code = QtCore.QString(forceString(record.value('code')))
                    setValueMapCodeToRowIdx(mapCodeToRowIdx, u'', quotaTypeWTMP, ageClient, countDeathSurgery, countComplication)
                    codeList = [QtCore.QString(code)]
                    indexPoint = code.lastIndexOf(u'.', -1, QtCore.Qt.CaseInsensitive)
                    while indexPoint > -1:
                        code.truncate(indexPoint)
                        codeList.append(QtCore.QString(code))
                        indexPoint = code.lastIndexOf(u'.', -1, QtCore.Qt.CaseInsensitive)

                    for code in codeList:
                        setValueMapCodeToRowIdx(mapCodeToRowIdx, code, quotaTypeWTMP, ageClient, countDeathSurgery, countComplication)

        return mapCodeToRowIdx


class CStationaryF144001(CStationaryF014):

    def __init__(self, parent = None):
        CStationaryF014.__init__(self, parent)
        self.stationaryF14SetupDialog = None

    def build(self, params):
        orgStructureIndex = self.stationaryF14SetupDialog.cmbOrgStructure._model.index(self.stationaryF14SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14SetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex) if orgStructureIndex.row() else []
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        doc = QtGui.QTextDocument()
        if not begDate or not endDate:
            currentDate = QtCore.QDate.currentDate()
            begDate = QtCore.QDate(currentDate.year(), 1, 1)
            endDate = currentDate
        if begDate and endDate:
            rowSize = 4
            mapRowsChildren4001 = createMapCodeToRowIdx([ row[2] for row in RowsChildren4001 ])
            reportMainData = [ [0] * rowSize for row in xrange(len(RowsChildren4001)) ]
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'Операции у детей в возрасте до 1 года\n(4001)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('22%', [u'Наименование операции', u'1'], CReportBase.AlignLeft),
             ('3%', [u'№ строки', u'2'], CReportBase.AlignLeft),
             ('18.75%', [u'Число операций в стационаре', u'3'], CReportBase.AlignLeft),
             ('18.75%', [u'из них операций с применением высоких медицинских технологий (ВМП)', u'4'], CReportBase.AlignLeft),
             ('18.75%', [u'Число операций, при которых наблюдались осложнения в стационаре', u'5'], CReportBase.AlignLeft),
             ('18.75%', [u'Умерло оперированных в стационаре', u'6'], CReportBase.AlignLeft)]
            table = createTable(cursor, cols)
            records = self.getRowsChildren4001(orgStructureIdList, begDate, endDate)
            for record in records:
                MKBRec = normalizeMKB(forceString(record.value('MKB')))
                embryonalPeriodWeek = forceInt(record.value('embryonalPeriodWeek'))
                quotaTypeWTMP = forceInt(record.value('quotaTypeWTMP'))
                countDeathSurgery = forceInt(record.value('countDeathSurgery'))
                countComplication = forceInt(record.value('countComplication'))
                for row in mapRowsChildren4001.get(MKBRec, []):
                    reportLine = reportMainData[row]
                    if row == 2 or row == 4 or row == 6 or row == 8 or row == 10 or row == 12 or row == 13:
                        if embryonalPeriodWeek >= 22 and embryonalPeriodWeek <= 37:
                            reportLine[0] += 1
                            if quotaTypeWTMP:
                                reportLine[1] += 1
                            if countComplication:
                                reportLine[2] += 1
                            if countDeathSurgery:
                                reportLine[3] += 1
                    else:
                        reportLine[0] += 1
                        if quotaTypeWTMP:
                            reportLine[1] += 1
                        if countComplication:
                            reportLine[2] += 1
                        if countDeathSurgery:
                            reportLine[3] += 1

            for row, rowDescr in enumerate(RowsChildren4001):
                reportLine = reportMainData[row]
                i = table.addRow()
                name, line = rowDescr[:2]
                table.setText(i, 0, name)
                table.setText(i, 1, line)
                for col in xrange(rowSize):
                    table.setText(i, 2 + col, reportLine[col])

        return doc

    def getRowsChildren4001(self, orgStructureIdList, begDateTime, endDateTime, isHospital = None):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableClient = db.table('Client')
        tableRBService = db.table('rbService')
        tableDiagnosis = db.table('Diagnosis')
        tableDiagnostic = db.table('Diagnostic')
        tableRBDiagnosisType = db.table('rbDiagnosisType')
        tableEventType = db.table('EventType')
        tableRBMedicalAidType = db.table('rbMedicalAidType')
        table = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
        table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
        table = table.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        table = table.innerJoin(tableRBMedicalAidType, tableEventType['medicalAidType_id'].eq(tableRBMedicalAidType['id']))
        table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        cond = [tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('received%')),
         tableEvent['deleted'].eq(0),
         tableAction['deleted'].eq(0),
         tableActionType['deleted'].eq(0),
         tableClient['deleted'].eq(0),
         tableEventType['deleted'].eq(0)]
        cond.append(tableRBMedicalAidType['code'].inlist([1, 2, 3]))
        cond.append('age(Client.birthDate, Event.setDate) <= 1')
        joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
        joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateGe(begDateTime), tableAction['begDate'].dateLe(endDateTime)])
        joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].dateGe(begDateTime)])
        joinOr4 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateLe(begDateTime), db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].dateGe(begDateTime)])])
        cond.append(db.joinOr([joinOr1,
         joinOr2,
         joinOr3,
         joinOr4]))
        if orgStructureIdList:
            cond.append(getDataOrgStructure(u'Направлен в отделение', orgStructureIdList))
        eventIdList = db.getDistinctIdList(table, 'Event.id', cond)
        self.addQueryText(queryText=db.selectStmt(table, 'Event.id', cond), queryDesc=u'getRowsChildren4001 getEventIdList' )
        if eventIdList:
            cols = [tableAction['id'].alias('actionId'),
             tableAction['event_id'],
             tableDiagnosis['MKB'],
             tableClient['embryonalPeriodWeek']]
            cols.append('IF((SELECT QuotaType.class FROM QuotaType WHERE QuotaType.id = ActionType.quotaType_id LIMIT 1) = 0, 1, 0) AS quotaTypeWTMP')
            cols.append('%s AS countDeathSurgery' % getStringProperty(u'Исход операции', u"(APS.value LIKE 'умер%' OR APS.value LIKE 'смерть%')"))
            cols.append('%s AS countComplication' % getStringProperty(u'Осложнение', u"(APS.value NOT LIKE '' OR APS.value NOT LIKE ' ')"))
            table = tableAction.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))
            table = table.innerJoin(tableRBService, tableRBService['id'].eq(tableActionType['nomenclativeService_id']))
            table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            table = table.innerJoin(tableDiagnostic, tableEvent['id'].eq(tableDiagnostic['event_id']))
            table = table.innerJoin(tableDiagnosis, tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']))
            table = table.innerJoin(tableRBDiagnosisType, tableDiagnostic['diagnosisType_id'].eq(tableRBDiagnosisType['id']))
            cond = [tableAction['event_id'].inlist(eventIdList),
             tableEvent['deleted'].eq(0),
             tableAction['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableClient['deleted'].eq(0),
             tableActionType['class'].inlist(2, 3),
             tableAction['endDate'].isNotNull(),
             tableDiagnosis['deleted'].eq(0),
             tableDiagnostic['deleted'].eq(0)]
            cond.append(u"rbDiagnosisType.code = '1' OR (rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id AND (NOT EXISTS (SELECT DC.id FROM Diagnostic AS DC INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id WHERE DT.code = '1' AND DC.event_id = Event.id LIMIT 1)))")
            #cond.append(db.joinOr([tableRBService['code'].like(u'1-2'), tableRBService['code'].like(u'А16%')]))
            cond.append(db.joinOr([tableActionType['serviceType'].eq('4'), db.joinOr([tableActionType['code'].like(u'1-2'), tableActionType['code'].like(u'А16%'), tableActionType['code'].like(u'6%'), tableActionType['code'].like(u'о%')])]))
            self.addQueryText(queryText=db.selectStmt(table, cols, cond), queryDesc=u'getRowsChildren4001')
            return db.getRecordList(table, cols, cond)
        return []


class CStationaryF144100(CStationaryF014):

    def __init__(self, parent = None):
        CStationaryF014.__init__(self, parent)
        self.stationaryF14SetupDialog = None

    def build(self, params):
        orgStructureIndex = self.stationaryF14SetupDialog.cmbOrgStructure._model.index(self.stationaryF14SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14SetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex) if orgStructureIndex.row() else []
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        doc = QtGui.QTextDocument()
        if not begDate or not endDate:
            currentDate = QtCore.QDate.currentDate()
            begDate = QtCore.QDate(currentDate.year(), 1, 1)
            endDate = currentDate
        if begDate and endDate:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'(4100)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('22%', [u'Строка 1'], CReportBase.AlignLeft), ('3%', [u'№ графы'], CReportBase.AlignLeft), ('75%', [u''], CReportBase.AlignLeft)]
            table = createTable(cursor, cols)
            records = self.getOperation(orgStructureIdList, begDate, endDate)
            reportLine = [0] * 10
            eventIdList = []
            for record in records:
                eventId = forceRef(record.value('event_id'))
                if eventId and eventId not in eventIdList:
                    eventIdList.append(eventId)
                reportLine[0] += 1
                ageClient = forceInt(record.value('ageClient'))
                if ageClient:
                    reportLine[2] += 1
                if forceInt(record.value('quotaTypeWTMP')):
                    reportLine[1] += 1
                    if ageClient:
                        reportLine[3] += 1

            if eventIdList:
                records = self.getAnesthesia(eventIdList)
                for record in records:
                    if forceInt(record.value('countDeathSurgery')):
                        reportLine[9] += 1
                    reportLine[8] += 1

            reportLine[4] = u'-'
            reportLine[5] = u'-'
            reportLine[6] = u'-'
            reportLine[7] = u'-'
            for rowDescr in Rows4100:
                i = table.addRow()
                name, line = rowDescr
                table.setText(i, 0, name)
                table.setText(i, 1, line)

            table.setText(1, 2, reportLine[0])
            table.setText(2, 2, reportLine[1])
            table.setText(3, 2, reportLine[2])
            table.setText(4, 2, reportLine[3])
            table.setText(5, 2, reportLine[4])
            table.setText(6, 2, reportLine[5])
            table.setText(7, 2, reportLine[6])
            table.setText(8, 2, reportLine[7])
            table.setText(9, 2, reportLine[8])
            table.setText(10, 2, reportLine[9])
        return doc

    def getAnesthesia(self, eventIdList):
        if eventIdList:
            db = QtGui.qApp.db
            tableEvent = db.table('Event')
            tableAction = db.table('Action')
            tableActionType = db.table('ActionType')
            tableEventType = db.table('EventType')
            tableRBMedicalAidType = db.table('rbMedicalAidType')
            cols = [tableAction['id'].alias('actionId'), tableAction['event_id']]
            cols.append('%s AS countDeathSurgery' % getStringProperty(u'Исход анестезии', u"(APS.value LIKE '%смерть в результате общей анестезии%')"))
            table = tableAction.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))
            table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
            table = table.innerJoin(tableRBMedicalAidType, tableEventType['medicalAidType_id'].eq(tableRBMedicalAidType['id']))
            cond = [tableAction['event_id'].inlist(eventIdList),
             tableEvent['deleted'].eq(0),
             tableAction['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableActionType['class'].eq(2),
             tableAction['endDate'].isNotNull(),
             tableActionType['id'].inlist(getActionTypeIdListByFlatCode('anesthesia%')),
             tableEventType['deleted'].eq(0)]
            cond.append(tableRBMedicalAidType['code'].inlist([1, 2, 3]))
            self.addQueryText(db.selectStmt(table, cols, cond), queryDesc=u'getAnesthesia')
            return db.getRecordList(table, cols, cond)
        return []

    def getOperation(self, orgStructureIdList, begDateTime, endDateTime):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableClient = db.table('Client')
        tableRBService = db.table('rbService')
        tableEventType = db.table('EventType')
        tableRBMedicalAidType = db.table('rbMedicalAidType')
        table = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
        table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
        table = table.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        table = table.innerJoin(tableRBMedicalAidType, tableEventType['medicalAidType_id'].eq(tableRBMedicalAidType['id']))
        table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        cond = [tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('received%')),
         tableEvent['deleted'].eq(0),
         tableAction['deleted'].eq(0),
         tableActionType['deleted'].eq(0),
         tableClient['deleted'].eq(0),
         tableEventType['deleted'].eq(0)]
        cond.append(tableRBMedicalAidType['code'].inlist([1, 2, 3]))
        joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
        joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateGe(begDateTime), tableAction['begDate'].dateLe(endDateTime)])
        joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].dateGe(begDateTime)])
        joinOr4 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateLe(begDateTime), db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].dateGe(begDateTime)])])
        cond.append(db.joinOr([joinOr1,
         joinOr2,
         joinOr3,
         joinOr4]))
        if orgStructureIdList:
            cond.append(getDataOrgStructure(u'Направлен в отделение', orgStructureIdList))
        eventIdList = db.getDistinctIdList(table, 'Event.id', cond)
        self.addQueryText(queryText=db.selectStmt(table, 'Event.id', cond), queryDesc=u'getOperation getEventIdList')
        if eventIdList:
            cols = [tableAction['id'].alias('actionId'),
             tableAction['event_id'],
             tableActionType['id'].alias('actionTypeId'),
             tableActionType['group_id'].alias('groupId'),
             tableActionType['code'],
             tableActionType['name'],
             tableRBService['code'].alias('codeService')]
            cols.append('IF((SELECT QuotaType.class FROM QuotaType WHERE QuotaType.id = ActionType.quotaType_id LIMIT 1) = 0, 1, 0) AS quotaTypeWTMP')
            cols.append('age(Client.birthDate, Event.setDate) AS ageClient')
            table = tableAction.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))
            table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            table = table.innerJoin(tableRBService, tableRBService['id'].eq(tableActionType['nomenclativeService_id']))
            cond = [tableAction['event_id'].inlist(eventIdList),
             tableEvent['deleted'].eq(0),
             tableAction['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableClient['deleted'].eq(0),
             tableActionType['class'].inlist([2, 3]),
             tableAction['endDate'].isNotNull()]
            #cond.append(db.joinOr([tableRBService['code'].like(u'1-2'), tableRBService['code'].like(u'А16%')]))
            cond.append(db.joinOr([tableActionType['serviceType'].eq('4'), db.joinOr([tableActionType['code'].like(u'1-2'), tableActionType['code'].like(u'А16%'), tableActionType['code'].like(u'6%'), tableActionType['code'].like(u'о%')])]))
            self.addQueryText(queryText=db.selectStmt(table, cols, cond), queryDesc=u'getOperation')
            return db.getRecordList(table, cols, cond)
        return []


class CStationaryF144200(CStationaryF014):

    def __init__(self, parent = None):
        CStationaryF014.__init__(self, parent)
        self.stationaryF14SetupDialog = None

    def build(self, params):
        orgStructureIndex = self.stationaryF14SetupDialog.cmbOrgStructure._model.index(self.stationaryF14SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14SetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex) if orgStructureIndex.row() else []
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        doc = QtGui.QTextDocument()
        if not begDate or not endDate:
            currentDate = QtCore.QDate.currentDate()
            begDate = QtCore.QDate(currentDate.year(), 1, 1)
            endDate = currentDate
        if begDate and endDate:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'(4200)Из общего числа операций(единиц)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('22%', [u'Строка 1'], CReportBase.AlignLeft), ('3%', [u'№ графы'], CReportBase.AlignLeft), ('75%', [u''], CReportBase.AlignLeft)]
            table = createTable(cursor, cols)
            reportLineEye = self.getTypeOperation(orgStructureIdList, begDate, endDate, u"rbService.code LIKE 'А16.26.%%'")
            reportLineEar = self.getTypeOperation(orgStructureIdList, begDate, endDate, u"rbService.code LIKE 'А16.25.%%'")
            reportLineBelly = self.getTypeOperation(orgStructureIdList, begDate, endDate, u"rbService.code LIKE 'А16.16.021' OR rbService.code LIKE 'А16.16.013'")
            reportLineHeart = self.getTypeOperation(orgStructureIdList, begDate, endDate, u"rbService.code LIKE '1-2' OR rbService.code LIKE 'А16%'", True)

            def getReportLine(records):
                reportLine = 0
                for record in records:
                    actionId = forceRef(record.value('actionId'))
                    if actionId:
                        reportLine += 1

                return reportLine

            for rowDescr in Rows4200:
                i = table.addRow()
                name, line = rowDescr
                table.setText(i, 0, name)
                table.setText(i, 1, line)

            table.setText(1, 2, getReportLine(reportLineEye))
            table.setText(2, 2, getReportLine(reportLineEar))
            table.setText(3, 2, getReportLine(reportLineBelly))
            table.setText(4, 2, getReportLine(reportLineHeart))
            table.setText(5, 2, u'-')
            table.setText(6, 2, u'-')
            table.setText(7, 2, u'-')
            table.setText(8, 2, u'-')
            table.setText(9, 2, u'-')
            table.setText(10, 2, u'-')
        return doc

    def getTypeOperation(self, orgStructureIdList, begDateTime, endDateTime, codeOperation, children = False):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableClient = db.table('Client')
        tableRBService = db.table('rbService')
        tableEventType = db.table('EventType')
        tableRBMedicalAidType = db.table('rbMedicalAidType')
        table = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
        table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
        table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        table = table.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        table = table.innerJoin(tableRBMedicalAidType, tableEventType['medicalAidType_id'].eq(tableRBMedicalAidType['id']))
        cond = [tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('received%')),
         tableEvent['deleted'].eq(0),
         tableAction['deleted'].eq(0),
         tableActionType['deleted'].eq(0),
         tableClient['deleted'].eq(0),
         tableEventType['deleted'].eq(0)]
        cond.append(tableRBMedicalAidType['code'].inlist([1, 2, 3]))
        joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
        joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateGe(begDateTime), tableAction['begDate'].dateLe(endDateTime)])
        joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].dateGe(begDateTime)])
        joinOr4 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateLe(begDateTime), db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].dateGe(begDateTime)])])
        cond.append(db.joinOr([joinOr1,
         joinOr2,
         joinOr3,
         joinOr4]))
        if orgStructureIdList:
            cond.append(getDataOrgStructure(u'Направлен в отделение', orgStructureIdList))
        eventIdList = db.getDistinctIdList(table, 'Event.id', cond)
        self.addQueryText(queryText=db.selectStmt(table, 'Event.id', cond), queryDesc=u'getTypeOperation getEventIdList')
        if eventIdList:
            cols = [tableAction['id'].alias('actionId'), tableAction['event_id']]
            table = tableAction.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))
            table = table.innerJoin(tableRBService, tableRBService['id'].eq(tableActionType['nomenclativeService_id']))
            table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            cond = [tableAction['event_id'].inlist(eventIdList),
             tableEvent['deleted'].eq(0),
             tableAction['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableClient['deleted'].eq(0),
             tableActionType['class'].eq(2),
             tableAction['endDate'].isNotNull()]
            cond.append(codeOperation)
            if children:
                tableDiagnosis = db.table('Diagnosis')
                tableDiagnostic = db.table('Diagnostic')
                tableRBDiagnosisType = db.table('rbDiagnosisType')
                cols.append(tableDiagnosis['MKB'])
                table = table.innerJoin(tableDiagnostic, tableEvent['id'].eq(tableDiagnostic['event_id']))
                table = table.innerJoin(tableDiagnosis, tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']))
                table = table.innerJoin(tableRBDiagnosisType, tableDiagnostic['diagnosisType_id'].eq(tableRBDiagnosisType['id']))
                cond.append(tableDiagnosis['deleted'].eq(0))
                cond.append(tableDiagnostic['deleted'].eq(0))
                cond.append('age(Client.birthDate, Event.setDate) <= 1')
                cond.append("Diagnosis.MKB >= 'Q20' AND Diagnosis.MKB <= 'Q28'")
                cond.append(u"rbDiagnosisType.code = '1' OR (rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id AND (NOT EXISTS (SELECT DC.id FROM Diagnostic AS DC INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id WHERE DT.code = '1' AND DC.event_id = Event.id LIMIT 1)))")
            self.addQueryText(queryText=db.selectStmt(table, cols, cond), queryDesc=u'getTypeOperation')
            return db.getRecordList(table, cols, cond)
        return []


class CStationaryF144201(CStationaryF014):

    def __init__(self, parent = None):
        CStationaryF014.__init__(self, parent)
        self.stationaryF14SetupDialog = None

    def build(self, params):
        orgStructureIndex = self.stationaryF14SetupDialog.cmbOrgStructure._model.index(self.stationaryF14SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14SetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex) if orgStructureIndex.row() else []
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        doc = QtGui.QTextDocument()
        if not begDate or not endDate:
            currentDate = QtCore.QDate.currentDate()
            begDate = QtCore.QDate(currentDate.year(), 1, 1)
            endDate = currentDate
        if begDate and endDate:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'(4201)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('22%', [u'Строка 1'], CReportBase.AlignLeft), ('3%', [u'№ графы'], CReportBase.AlignLeft), ('75%', [u''], CReportBase.AlignLeft)]
            table = createTable(cursor, cols)

            def getReportLine(records):
                reportLine = [0,
                 0,
                 0,
                 0]
                for record in records:
                    countDeathSurgery = forceInt(record.value('countDeathSurgery'))
                    clientAge = forceInt(record.value('clientAge'))
                    reportLine[0] += 1
                    if countDeathSurgery:
                        reportLine[1] += 1
                    if clientAge <= 17:
                        reportLine[2] += 1
                        if countDeathSurgery:
                            reportLine[3] += 1

                return reportLine

            recordsAll = self.getTransplantation(orgStructureIdList, begDate, endDate, u'трансплантация%')
            recordsBuds = self.getTransplantation(orgStructureIdList, begDate, endDate, u'трансплантация почки%')
            recordsPancreat = self.getTransplantation(orgStructureIdList, begDate, endDate, u'трансплантация поджелудочной железы%')
            recordsHearts = self.getTransplantation(orgStructureIdList, begDate, endDate, u'трансплантация сердца%')
            recordsBaking = self.getTransplantation(orgStructureIdList, begDate, endDate, u'трансплантация печени%')
            recordsMedulla = self.getTransplantation(orgStructureIdList, begDate, endDate, u'трансплантация костного мозга%')
            recordsLung = self.getTransplantation(orgStructureIdList, begDate, endDate, u'трансплантация легк%')
            for rowDescr in Rows4201:
                i = table.addRow()
                name, line = rowDescr
                table.setText(i, 0, name)
                table.setText(i, 1, line)

            def setReportLine(reportLine, i):
                table.setText(i, 2, reportLine[0])
                table.setText(i + 1, 2, reportLine[1])
                table.setText(i + 2, 2, reportLine[2])
                table.setText(i + 3, 2, reportLine[3])

            reportLineAll = getReportLine(recordsAll)
            setReportLine(reportLineAll, 1)
            reportLineBuds = getReportLine(recordsBuds)
            setReportLine(reportLineBuds, 5)
            reportLinePancreat = getReportLine(recordsPancreat)
            setReportLine(reportLinePancreat, 9)
            reportLineHearts = getReportLine(recordsHearts)
            setReportLine(reportLineHearts, 13)
            reportLineBaking = getReportLine(recordsBaking)
            setReportLine(reportLineBaking, 17)
            reportLineMedulla = getReportLine(recordsMedulla)
            setReportLine(reportLineMedulla, 21)
            reportLineLung = getReportLine(recordsLung)
            setReportLine(reportLineLung, 25)
        return doc

    def getTransplantation(self, orgStructureIdList, begDateTime, endDateTime, nameTrasplantate):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableClient = db.table('Client')
        tableRBService = db.table('rbService')
        tableEventType = db.table('EventType')
        tableRBMedicalAidType = db.table('rbMedicalAidType')
        table = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
        table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
        table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        table = table.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        table = table.innerJoin(tableRBMedicalAidType, tableEventType['medicalAidType_id'].eq(tableRBMedicalAidType['id']))
        cond = [tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('received%')),
         tableEvent['deleted'].eq(0),
         tableAction['deleted'].eq(0),
         tableActionType['deleted'].eq(0),
         tableClient['deleted'].eq(0),
         tableEventType['deleted'].eq(0)]
        cond.append(tableRBMedicalAidType['code'].inlist([1, 2, 3]))
        joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
        joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateGe(begDateTime), tableAction['begDate'].dateLe(endDateTime)])
        joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].dateGe(begDateTime)])
        joinOr4 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateLe(begDateTime), db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].dateGe(begDateTime)])])
        cond.append(db.joinOr([joinOr1,
         joinOr2,
         joinOr3,
         joinOr4]))
        if orgStructureIdList:
            cond.append(getDataOrgStructure(u'Направлен в отделение', orgStructureIdList))
        eventIdList = db.getDistinctIdList(table, 'Event.id', cond)
        self.addQueryText(queryText=db.selectStmt(table, 'Event.id', cond), queryDesc=u'getTransplantation getEventIdList')
        if eventIdList:
            cols = [tableAction['id'].alias('actionId'), tableAction['event_id']]
            cols.append('age(Client.birthDate, Event.setDate) AS clientAge')
            cols.append('%s AS countDeathSurgery' % getStringProperty(u'Исход операции', u"(APS.value LIKE 'умер%' OR APS.value LIKE 'смерть%')"))
            table = tableAction.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))
            table = table.innerJoin(tableRBService, tableRBService['id'].eq(tableActionType['nomenclativeService_id']))
            table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            cond = [tableAction['event_id'].inlist(eventIdList),
             tableEvent['deleted'].eq(0),
             tableAction['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableClient['deleted'].eq(0),
             tableActionType['class'].eq(2),
             tableAction['endDate'].isNotNull()]
            cond.append(tableRBService['name'].like(nameTrasplantate))
            self.addQueryText(queryText=db.selectStmt(table, cols, cond), queryDesc=u'getTransplantation')
            return db.getRecordList(table, cols, cond)
        return []


class CStationaryF144202(CStationaryF014):

    def __init__(self, parent = None):
        CStationaryF014.__init__(self, parent)
        self.stationaryF14SetupDialog = None

    def build(self, params):
        orgStructureIndex = self.stationaryF14SetupDialog.cmbOrgStructure._model.index(self.stationaryF14SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14SetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex) if orgStructureIndex.row() else []
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        doc = QtGui.QTextDocument()
        if not begDate or not endDate:
            currentDate = QtCore.QDate.currentDate()
            begDate = QtCore.QDate(currentDate.year(), 1, 1)
            endDate = currentDate
        if begDate and endDate:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'(4202)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('22%', [u'Строка 1'], CReportBase.AlignLeft), ('3%', [u'№ графы'], CReportBase.AlignLeft), ('75%', [u''], CReportBase.AlignLeft)]
            table = createTable(cursor, cols)
            for rowDescr in Rows4202:
                i = table.addRow()
                name, line = rowDescr
                table.setText(i, 0, name)
                table.setText(i, 1, line)

            records = self.getEndoprosthesis(orgStructureIdList, begDate, endDate)
            reportLine = [0, 0]
            for record in records:
                reportLine[0] += 1
                if forceInt(record.value('clientAge')) <= 17:
                    reportLine[1] += 1

            table.setText(1, 2, reportLine[0])
            table.setText(2, 2, reportLine[1])
            table.setText(3, 2, u'-')
            table.setText(4, 2, u'-')
        return doc

    def getEndoprosthesis(self, orgStructureIdList, begDateTime, endDateTime):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableClient = db.table('Client')
        tableRBService = db.table('rbService')
        tableEventType = db.table('EventType')
        tableRBMedicalAidType = db.table('rbMedicalAidType')
        table = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
        table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
        table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        table = table.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        table = table.innerJoin(tableRBMedicalAidType, tableEventType['medicalAidType_id'].eq(tableRBMedicalAidType['id']))
        cond = [tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('received%')),
         tableEvent['deleted'].eq(0),
         tableAction['deleted'].eq(0),
         tableActionType['deleted'].eq(0),
         tableClient['deleted'].eq(0),
         tableEventType['deleted'].eq(0)]
        cond.append(tableRBMedicalAidType['code'].inlist([1, 2, 3]))
        joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
        joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateGe(begDateTime), tableAction['begDate'].dateLe(endDateTime)])
        joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].dateGe(begDateTime)])
        joinOr4 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateLe(begDateTime), db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].dateGe(begDateTime)])])
        cond.append(db.joinOr([joinOr1,
         joinOr2,
         joinOr3,
         joinOr4]))
        if orgStructureIdList:
            cond.append(getDataOrgStructure(u'Направлен в отделение', orgStructureIdList))
        eventIdList = db.getDistinctIdList(table, 'Event.id', cond)
        self.addQueryText(queryText=db.selectStmt(table, 'Event.id', cond), queryDesc=u'getEndoprosthesis getEventIdList')
        if eventIdList:
            cols = [tableAction['id'].alias('actionId'), tableAction['event_id']]
            cols.append('age(Client.birthDate, Event.setDate) AS clientAge')
            table = tableAction.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))
            table = table.innerJoin(tableRBService, tableRBService['id'].eq(tableActionType['nomenclativeService_id']))
            table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            cond = [tableAction['event_id'].inlist(eventIdList),
             tableEvent['deleted'].eq(0),
             tableAction['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableClient['deleted'].eq(0),
             tableActionType['class'].eq(2),
             tableAction['endDate'].isNotNull()]
            cond.append(tableRBService['name'].like(u'%эндопротезирование%'))
            self.addQueryText(queryText=db.selectStmt(table, cols, cond), queryDesc=u'getEndoprosthesis')
            return db.getRecordList(table, cols, cond)
        return []


class CStationaryF144400(CStationaryF014):

    def __init__(self, parent = None):
        CStationaryF014.__init__(self, parent)
        self.stationaryF14SetupDialog = None

    def build(self, params):
        orgStructureIndex = self.stationaryF14SetupDialog.cmbOrgStructure._model.index(self.stationaryF14SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14SetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex) if orgStructureIndex.row() else []
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        doc = QtGui.QTextDocument()
        if not begDate or not endDate:
            currentDate = QtCore.QDate.currentDate()
            begDate = QtCore.QDate(currentDate.year(), 1, 1)
            endDate = currentDate
        if begDate and endDate:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'(4400)')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cols = [('22%', [u'Строка 1'], CReportBase.AlignLeft), ('3%', [u'№ графы'], CReportBase.AlignLeft), ('75%', [u''], CReportBase.AlignLeft)]
            table = createTable(cursor, cols)
            recordsAll = self.getRestoration(orgStructureIdList, begDate, endDate, u'')
            recordsBelly = self.getRestoration(orgStructureIdList, begDate, endDate, u"rbService.code LIKE 'А16.16.021' OR rbService.code LIKE 'А16.16.013'")
            recordsBiliary = self.getRestoration(orgStructureIdList, begDate, endDate, u"rbService.code LIKE 'А16.14.009'")
            recordsHeart = self.getRestoration(orgStructureIdList, begDate, endDate, u"(rbService.code >= 'А16.12.001' AND rbService.code <= 'А16.12.023') OR (rbService.code >= 'А16.12.025' AND rbService.code <= 'А16.12.028') OR (rbService.code >= 'А16.10.001' AND rbService.code <= 'А16.10.018')")
            recordsSubBelly = self.getRestoration(orgStructureIdList, begDate, endDate, u"(rbService.code >= 'А16.15.001' AND rbService.code <= 'А16.15.012')")
            recordsSubBone = self.getRestoration(orgStructureIdList, begDate, endDate, u"(rbService.code >= 'А16.04.001' AND rbService.code <= 'А16.04.023') OR (rbService.code >= 'А16.03.021' AND rbService.code <= 'А16.03.041') OR (rbService.code LIKE 'А16.31.017') OR (rbService.code LIKE 'А16.31.018')")

            for rowDescr in Rows4400:
                i = table.addRow()
                name, line = rowDescr
                table.setText(i, 0, name)
                table.setText(i, 1, line)

            table.setText(1, 2, len(recordsAll))
            table.setText(2, 2, len(recordsBelly))
            table.setText(3, 2, len(recordsBiliary))
            table.setText(4, 2, len(recordsHeart))
            table.setText(5, 2, len(recordsSubBelly))
            table.setText(6, 2, len(recordsSubBone))
        return doc

    def getRestoration(self, orgStructureIdList, begDateTime, endDateTime, codeRestoration):
        db = QtGui.qApp.db
        tableEvent = db.table('Event')
        tableAction = db.table('Action')
        tableActionType = db.table('ActionType')
        tableClient = db.table('Client')
        tableRBService = db.table('rbService')
        tableEventType = db.table('EventType')
        tableRBMedicalAidType = db.table('rbMedicalAidType')
        table = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
        table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
        table = table.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        table = table.innerJoin(tableRBMedicalAidType, tableEventType['medicalAidType_id'].eq(tableRBMedicalAidType['id']))
        table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        cond = [tableAction['actionType_id'].inlist(getActionTypeIdListByFlatCode('received%')),
         tableEvent['deleted'].eq(0),
         tableAction['deleted'].eq(0),
         tableActionType['deleted'].eq(0),
         tableClient['deleted'].eq(0),
         tableEventType['deleted'].eq(0)]
        cond.append(tableRBMedicalAidType['code'].inlist([1, 2, 3]))
        joinOr1 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNull()])
        joinOr2 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateGe(begDateTime), tableAction['begDate'].dateLe(endDateTime)])
        joinOr3 = db.joinAnd([tableAction['begDate'].isNull(), tableAction['endDate'].isNotNull(), tableAction['endDate'].dateGe(begDateTime)])
        joinOr4 = db.joinAnd([tableAction['begDate'].isNotNull(), tableAction['begDate'].dateLe(begDateTime), db.joinOr([tableAction['endDate'].isNull(), tableAction['endDate'].dateGe(begDateTime)])])
        cond.append(db.joinOr([joinOr1,
         joinOr2,
         joinOr3,
         joinOr4]))
        cond.append(u'''EXISTS(SELECT RBS.id
                      FROM Action AS A
                      INNER JOIN ActionType AS AT ON A.actionType_id=AT.id
                      INNER JOIN rbService AS RBS ON RBS.id = AT.nomenclativeService_id
                      WHERE A.event_id = Action.event_id AND A.deleted = 0 AND AT.deleted = 0 AND RBS.name LIKE '%восстановительное лечение%')''')
        if orgStructureIdList:
            cond.append(getDataOrgStructure(u'Направлен в отделение', orgStructureIdList))
        eventIdList = db.getDistinctIdList(table, 'Event.id', cond)
        self.addQueryText(queryText=db.selectStmt(table, 'Event.id', cond), queryDesc=u'getRestoration getEventIdList')
        if eventIdList:
            cols = [tableAction['id'].alias('actionId'), tableAction['event_id']]
            table = tableAction.innerJoin(tableActionType, tableAction['actionType_id'].eq(tableActionType['id']))
            table = table.innerJoin(tableRBService, tableRBService['id'].eq(tableActionType['nomenclativeService_id']))
            table = table.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
            table = table.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
            cond = [tableAction['event_id'].inlist(eventIdList),
             tableEvent['deleted'].eq(0),
             tableAction['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableClient['deleted'].eq(0),
             tableActionType['class'].eq(2),
             tableAction['endDate'].isNotNull()]
            if codeRestoration:
                cond.append(codeRestoration)
            cond.append(u'''EXISTS(SELECT RBS.id
                                  FROM Action AS A
                                  INNER JOIN ActionType AS AT ON A.actionType_id=AT.id
                                  INNER JOIN rbService AS RBS ON RBS.id = AT.nomenclativeService_id
                                  WHERE A.event_id = Action.event_id AND A.deleted = 0 AND AT.deleted = 0 AND RBS.name LIKE '%восстановительное лечение%' AND DATE(A.begDate) >= DATE(Action.begDate))'''
                        )
            self.addQueryText(db.selectStmt(table, cols, cond, u'Action.event_id'), queryDesc=u'getRestoration')
            return db.getRecordListGroupBy(table, cols, cond, u'Action.event_id')
        return []


class CStationaryF142100(CStationaryF014):

    def __init__(self, parent = None):
        CStationaryF014.__init__(self, parent)
        self.stationaryF14SetupDialog = None

    def getInfoByReport(self, orgStructureIdList, begDateTime, endDateTime, isHospital = None):
        reportMainData = [0,
         0,
         0,
         0,
         0]
        db = QtGui.qApp.db
        tableAPT = db.table('ActionPropertyType')
        tableAP = db.table('ActionProperty')
        tableActionType = db.table('ActionType')
        tableAction = db.table('Action')
        tableEvent = db.table('Event')
        tableClient = db.table('Client')
        tableOrg = db.table('Organisation')
        tableOS = db.table('OrgStructure')
        tableAPHB = db.table('ActionProperty_HospitalBed')
        tableOSHB = db.table('OrgStructure_HospitalBed')
        tableDiagnosis = db.table('Diagnosis')
        tableDiagnostic = db.table('Diagnostic')
        tableRBDiagnosisType = db.table('rbDiagnosisType')
        tableEventType = db.table('EventType')
        tableRBMedicalAidType = db.table('rbMedicalAidType')
        queryTable = tableActionType.innerJoin(tableAction, tableActionType['id'].eq(tableAction['actionType_id']))
        queryTable = queryTable.innerJoin(tableEvent, tableAction['event_id'].eq(tableEvent['id']))
        queryTable = queryTable.innerJoin(tableEventType, tableEvent['eventType_id'].eq(tableEventType['id']))
        queryTable = queryTable.innerJoin(tableRBMedicalAidType, tableEventType['medicalAidType_id'].eq(tableRBMedicalAidType['id']))
        queryTable = queryTable.innerJoin(tableClient, tableEvent['client_id'].eq(tableClient['id']))
        queryTable = queryTable.innerJoin(tableDiagnostic, tableEvent['id'].eq(tableDiagnostic['event_id']))
        queryTable = queryTable.innerJoin(tableDiagnosis, tableDiagnostic['diagnosis_id'].eq(tableDiagnosis['id']))
        queryTable = queryTable.innerJoin(tableRBDiagnosisType, tableDiagnostic['diagnosisType_id'].eq(tableRBDiagnosisType['id']))
        actionTypeIdList = getActionTypeIdListByFlatCode('leaved%')
        cond = [tableActionType['id'].inlist(actionTypeIdList),
         tableAction['deleted'].eq(0),
         tableEvent['deleted'].eq(0),
         tableActionType['deleted'].eq(0),
         tableClient['deleted'].eq(0),
         tableDiagnosis['deleted'].eq(0),
         tableDiagnostic['deleted'].eq(0),
         tableAction['endDate'].isNotNull(),
         tableEventType['deleted'].eq(0)]
        cond.append(tableRBMedicalAidType['code'].inlist([1, 2, 3]))
        joinOr1 = db.joinOr([tableAction['begDate'].isNull(), tableAction['begDate'].dateGe(begDateTime)])
        joinOr2 = db.joinOr([tableAction['begDate'].isNull(), tableAction['begDate'].dateLe(endDateTime)])
        cond.append(db.joinAnd([joinOr1, joinOr2]))
        cond.append(u"rbDiagnosisType.code = '1' OR (rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id AND (NOT EXISTS (SELECT DC.id FROM Diagnostic AS DC INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id WHERE DT.code = '1' AND DC.event_id = Event.id LIMIT 1)))")
        cond.append(getStringProperty(u'Исход госпитализации', u"(APS.value LIKE '%%переведен%%')"))
        cols = [tableEvent['id'].alias('eventId'),
         tableAction['id'].alias('actionId'),
         tableAction['endDate'],
         tableClient['id'].alias('clientId'),
         tableClient['embryonalPeriodWeek'],
         tableClient['birthDate'],
         tableEvent['setDate']]
        cols.append(u" EXISTS(SELECT APS_S.value\n                        FROM Action AS A_S\n                        INNER JOIN ActionType AS AT_S ON AT_S.id = A_S.actionType_id\n                        INNER JOIN ActionPropertyType AS APT_S ON APT_S.actionType_id = AT_S.id\n                        INNER JOIN ActionProperty AS AP_S ON AP_S.type_id = APT_S.id\n                        INNER JOIN ActionProperty_String AS APS_S ON APS_S.id = AP_S.id\n                        WHERE A_S.actionType_id IN (%s)\n                        AND A_S.deleted=0\n                        AND AP_S.deleted=0\n                        AND APT_S.deleted=0\n                        AND AP_S.action_id = A_S.id\n                        AND A_S.event_id = Event.id\n                        AND APT_S.name LIKE 'Исход госпитализации%%') AS trasferedType" % ','.join((str(actionTypeId) for actionTypeId in actionTypeIdList if actionTypeId)))
        stmt = db.selectStmt(queryTable, cols, cond)
        query = db.query(stmt)
        self.addQueryText(queryText=query.lastQuery(), queryDesc=u'getInfoByReport')
        cols = [tableAction['begDate'],
         tableEvent['id'].alias('eventId'),
         tableAction['id'].alias('actionId'),
         tableAction['endDate'],
         tableClient['id'].alias('clientId'),
         tableOSHB['master_id'],
         tableDiagnosis['MKB'],
         tableOrg['isMedical']]
        queryTable = queryTable.innerJoin(tableAPT, tableAPT['actionType_id'].eq(tableActionType['id']))
        queryTable = queryTable.innerJoin(tableAP, tableAP['type_id'].eq(tableAPT['id']))
        queryTable = queryTable.innerJoin(tableAPHB, tableAPHB['id'].eq(tableAP['id']))
        queryTable = queryTable.innerJoin(tableOSHB, tableOSHB['id'].eq(tableAPHB['value']))
        queryTable = queryTable.innerJoin(tableOS, tableOS['id'].eq(tableOSHB['master_id']))
        queryTable = queryTable.innerJoin(tableOrg, tableOrg['id'].eq(tableOS['organisation_id']))
        while query.next():
            record = query.record()
            eventId = forceRef(record.value('eventId'))
            embryonalPeriodWeek = forceInt(record.value('embryonalPeriodWeek'))
            birthDate = forceDate(record.value('birthDate'))
            setDate = forceDate(record.value('setDate'))
            trasferedType = forceString(record.value('trasferedType'))
            cond = [tableActionType['flatCode'].like('moving%'),
             tableAction['deleted'].eq(0),
             tableEvent['deleted'].eq(0),
             tableEvent['id'].eq(eventId),
             tableAP['deleted'].eq(0),
             tableActionType['deleted'].eq(0),
             tableAPT['deleted'].eq(0),
             tableOS['type'].ne(0),
             tableOS['deleted'].eq(0),
             tableOrg['deleted'].eq(0),
             tableClient['deleted'].eq(0),
             tableDiagnosis['deleted'].eq(0),
             tableAPT['typeName'].like('HospitalBed'),
             tableAP['action_id'].eq(tableAction['id'])]
            cond.append(u"rbDiagnosisType.code = '1' OR (rbDiagnosisType.code = '2' AND Diagnostic.person_id = Event.execPerson_id AND (NOT EXISTS (SELECT DC.id FROM Diagnostic AS DC INNER JOIN rbDiagnosisType AS DT ON DT.id = DC.diagnosisType_id WHERE DT.code = '1' AND DC.event_id = Event.id LIMIT 1)))")
            order = u'Action.begDate DESC'
            firstRecord = db.getRecordEx(queryTable, cols, cond, order)
            if firstRecord:
                isHospitalRecord = None
                masterId = forceRef(firstRecord.value('master_id'))
                MKBRec = normalizeMKB(forceString(firstRecord.value('MKB')))
                if isHospital != None:
                    isHospitalRecord = forceInt(firstRecord.value('isMedical'))
                if MKBRec and isHospital == isHospitalRecord and masterId in orgStructureIdList:
                    reportMainData[0] += 1
                    if birthDate.addDays(30) > setDate:
                        reportMainData[1] += 1
                    if embryonalPeriodWeek and embryonalPeriodWeek < 36:
                        reportMainData[2] += 1
                    if u'переведен в стационар восстановительного лечения' in trasferedType.lower():
                        reportMainData[3] += 1
                    if u'переведен в санаторий' in trasferedType.lower():
                        reportMainData[4] += 1

        return reportMainData

    def build(self, params):
        orgStructureIndex = self.stationaryF14SetupDialog.cmbOrgStructure._model.index(self.stationaryF14SetupDialog.cmbOrgStructure.currentIndex(), 0, self.stationaryF14SetupDialog.cmbOrgStructure.rootModelIndex())
        orgStructureIdList = self.getOrgStructureIdList(orgStructureIndex)
        begDate = params.get('begDate', QtCore.QDate())
        endDate = params.get('endDate', QtCore.QDate())
        doc = QtGui.QTextDocument()
        if not begDate or not endDate:
            currentDate = QtCore.QDate.currentDate()
            begDate = QtCore.QDate(currentDate.year(), 1, 1)
            endDate = currentDate
        if begDate and endDate:
            doc = QtGui.QTextDocument()
            cursor = QtGui.QTextCursor(doc)
            cursor.setCharFormat(CReportBase.ReportTitle)
            cursor.insertText(u'2100')
            cursor.insertBlock()
            self.dumpParams(cursor, params)
            cursor.setCharFormat(CReportBase.ReportBody)
            cursor.insertBlock()
            cursor.insertBlock()
            reportMainData = self.getInfoByReport(orgStructureIdList, begDate, endDate)
            result = u'Кроме того, больные, переведенные в другие стационары %s, в том числе новорожденные %s, из них недоношенные %s, из числа переведенных в другие стационары переведено: в стационары восстановительного лечения %s, в санатории %s.' % (str(reportMainData[0]),
             str(reportMainData[1]),
             str(reportMainData[2]),
             str(reportMainData[3]),
             str(reportMainData[4]))
            cursor.insertText(result)
            cursor.insertBlock()
        return doc


def getDataOrgStructure(nameProperty, orgStructureIdList):
    orgStructureList = [u'NULL']
    for orgStructureId in orgStructureIdList:
        orgStructureList.append(forceString(orgStructureId))

    return "EXISTS(SELECT APOS2.value\n    FROM ActionPropertyType AS APT2\n    INNER JOIN ActionProperty AS AP2 ON AP2.type_id=APT2.id\n    INNER JOIN ActionProperty_OrgStructure AS APOS2 ON APOS2.id=AP2.id\n    INNER JOIN OrgStructure AS OS2 ON OS2.id=APOS2.value\n    WHERE APT2.actionType_id=Action.actionType_id AND AP2.action_id=Action.id AND APT2.deleted=0 AND APT2.name LIKE '%s' AND OS2.type != 0 AND OS2.deleted=0 AND APOS2.value %s)" % (nameProperty, u' IN (' + ','.join(orgStructureList) + ')')
