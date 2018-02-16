select 'Импорт простых услуг (Axx.xx.xxx)...' as ' ';
update tmpA
set rbService_type = 0 -- неизвестно
where rbService_type is null;
update tmpA
set rbServiceType_type = 0 -- неизвестно
where rbServiceType_type is null;
update tmpA
set rbServiceClass_type = 0 -- неизвестно
where rbServiceClass_type is null;

select 'Устанавливаем соответствия для простых услуг...' as ' ';
-- сперва по полному совпадению кода:
update tmpA, rbService
set tmpA.rbService_id = rbService.id,
tmpA.rbService_type = 3
where rbService.code = concat('А', tmpA.code)
and tmpA.rbService_type = 0;
-- теперь предполагаем, что буква А могла быть пропущена:
update tmpA, rbService
set tmpA.rbService_id = rbService.id,
tmpA.rbService_type = 3
where rbService.code = tmpA.code
and tmpA.rbService_type = 0;

-- теперь с типами:
update tmpA, rbServiceType
set tmpA.rbServiceType_id = rbServiceType.id,
tmpA.rbServiceType_type = 3 -- типы всегда переписываются
where rbServiceType.section = 'А'
and rbServiceType.code = tmpA.code
and tmpA.rbServiceType_type = 0;

-- теперь с классами:
update tmpA, rbServiceClass
set tmpA.rbServiceClass_id = rbServiceClass.id,
tmpA.rbServiceClass_type = 3 -- классы всегда переписываются
where rbServiceClass.section = 'А'
and rbServiceClass.code = substr(tmpA.code from 4)
and tmpA.rbServiceClass_type = 0;


select 'Обновление простых услуг...' as ' ';
select concat(convert(count(*) using utf8), ' услуг обновляется...') as ' '
from tmpA
where tmpA.rbService_type = 3;

update tmpA, rbService
set rbService.code = concat('А', tmpA.code),
rbService.name = tmpA.name,
rbService.nomenclatureLegacy = 1
where tmpA.rbService_id = rbService.id
and tmpA.rbService_type = 3;

select concat(convert(count(*) using utf8), ' типов услуг обновляется...') as ' '
from tmpA
where tmpA.rbServiceType_type = 3;

update tmpA, rbServiceType
set rbServiceType.name = tmpA.name
where tmpA.rbServiceType_id = rbServiceType.id
and tmpA.rbServiceType_type = 3;

--select concat(convert(count(*) using utf8), ' классов услуг обновляется...') as ' '
--from tmpA
--where tmpA.rbServiceClass_type = 3;

update tmpA, rbServiceClass
set rbServiceClass.name = tmpA.name
where tmpA.rbServiceClass_id = rbServiceClass.id
and tmpA.rbServiceClass_type = 3;


select 'Добавление простых услуг...' as ' ';

update tmpA
set rbService_type = 5
where length(code) = 9
and rbService_type = 0;

select concat(convert(count(*) using utf8), ' услуг добавляется...') as ' '
from tmpA
where tmpA.rbService_type = 5;

insert into rbService(code, name, eisLegacy, nomenclatureLegacy, infis, begDate, endDate)
select  concat('А', tmpA.code) as code,
	name,
	0 as eisLegacy,
	1 as nomenclatureLegacy,
	concat('А', tmpA.code) as infis, -- ???????????????????????
	'0000-00-00' as begDate, -- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	'2200-01-01' as endDate
from tmpA
where tmpA.rbService_type = 5;

update tmpA
set rbServiceType_type = 5
where length(code) = 2
and rbServiceType_type = 0;

select concat(convert(count(*) using utf8), ' типов услуг добавляется...') as ' '
from tmpA
where tmpA.rbServiceType_type = 5;

insert into rbServiceType(section, code, name, `class`)
select  'А' as section,
	code,
	name,
	3 as `class`
from tmpA
where tmpA.rbServiceType_type = 5;

update tmpA
set rbServiceClass_type = 5
where length(code) = 5
and rbServiceClass_type = 0;

--select concat(convert(count(*) using utf8), ' классов услуг добавляется...') as ' '
--from tmpA
--where tmpA.rbServiceClass_type = 5;

insert into rbServiceClass(section, code, name)
select distinct -- одни и те же классы повторяются несколько раз с разными типами
	'А' as section,
	substr(code from 4 for 2) as code,
	name
from tmpA
where tmpA.rbServiceClass_type = 5;


















-- Сложные услуги импортируются так же, как простые
select 'Импорт сложных услуг (Bxx.xxx.xx)...' as ' ';
update tmpB
set rbService_type = 0 -- неизвестно
where rbService_type is null;
update tmpB
set rbServiceType_type = 0 -- неизвестно
where rbServiceType_type is null;
update tmpB
set rbServiceClass_type = 0 -- неизвестно
where rbServiceClass_type is null;

select 'Устанавливаем соответствия для сложных услуг...' as ' ';
-- сперва по полному совпадению кода:
update tmpB, rbService
set tmpB.rbService_id = rbService.id,
tmpB.rbService_type = 3
where rbService.code = concat('В', tmpB.code)
and tmpB.rbService_type = 0;
-- теперь предполагаем, что буква B могла быть пропущена:
update tmpB, rbService
set tmpB.rbService_id = rbService.id,
tmpB.rbService_type = 3
where rbService.code = tmpB.code
and tmpB.rbService_type = 0;

-- теперь с типами:
update tmpB, rbServiceType
set tmpB.rbServiceType_id = rbServiceType.id,
tmpB.rbServiceType_type = 3 -- типы всегда переписываются
where rbServiceType.section = 'В'
and rbServiceType.code = tmpB.code
and tmpB.rbServiceType_type = 0;

-- теперь с классами:
update tmpB, rbServiceClass
set tmpB.rbServiceClass_id = rbServiceClass.id,
tmpB.rbServiceClass_type = 3 -- классы всегда переписываются
where rbServiceClass.section = 'В'
and rbServiceClass.code = substr(tmpB.code from 4)
and tmpB.rbServiceClass_type = 0;


select 'Обновление сложных услуг...' as ' ';
select concat(convert(count(*) using utf8), ' услуг обновляется...') as ' '
from tmpB
where tmpB.rbService_type = 3;

update tmpB, rbService
set rbService.code = concat('В', tmpB.code),
rbService.name = tmpB.name,
rbService.nomenclatureLegacy = 1
where tmpB.rbService_id = rbService.id
and tmpB.rbService_type = 3;

select concat(convert(count(*) using utf8), ' типов услуг обновляется...') as ' '
from tmpB
where tmpB.rbServiceType_type = 3;

update tmpB, rbServiceType
set rbServiceType.name = tmpB.name
where tmpB.rbServiceType_id = rbServiceType.id
and tmpB.rbServiceType_type = 3;

--select concat(convert(count(*) using utf8), ' классов услуг обновляется...') as ' '
--from tmpB
--where tmpB.rbServiceClass_type = 3;

update tmpB, rbServiceClass
set rbServiceClass.name = tmpB.name
where tmpB.rbServiceClass_id = rbServiceClass.id
and tmpB.rbServiceClass_type = 3;


select 'Добавление сложных услуг...' as ' ';

update tmpB
set rbService_type = 5
where length(code) = 9
and rbService_type = 0;

select concat(convert(count(*) using utf8), ' услуг добавляется...') as ' '
from tmpB
where tmpB.rbService_type = 5;

insert into rbService(code, name, eisLegacy, nomenclatureLegacy, infis, begDate, endDate)
select 	concat('В', tmpB.code) as code,
	name,
	0 as eisLegacy,
	1 as nomenclatureLegacy,
	concat('В', tmpB.code) as infis, -- ???????????????????????
	'0000-00-00' as begDate, -- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	'2200-01-01' as endDate
from tmpB
where tmpB.rbService_type = 5;

update tmpB
set rbServiceType_type = 5
where length(code) = 2
and rbServiceType_type = 0;

select concat(convert(count(*) using utf8), ' типов услуг добавляется...') as ' '
from tmpB
where tmpB.rbServiceType_type = 5;

insert into rbServiceType(section, code, name, `class`)
select 	'В' as section,
	code,
	name,
	3 as `class`
from tmpB
where tmpB.rbServiceType_type = 5;

update tmpB
set rbServiceClass_type = 5
where length(code) = 6
and rbServiceClass_type = 0;

--select concat(convert(count(*) using utf8), ' классов услуг добавляется...') as ' '
--from tmpB
--where tmpB.rbServiceClass_type = 5;

insert into rbServiceClass(section, code, name)
select distinct -- одни и те же классы повторяются несколько раз с разными типами
	'В' as section,
	substr(code from 4 for 3) as code,
	name
from tmpB
where tmpB.rbServiceClass_type = 5;



























select 'Импорт состава сложных услуг...' as ' ';
update tmpC
set rbServiceGroup_type = 0 -- неизвестно
where rbServiceGroup_type is null;

-- для ускорения импорта учитываем только коды, начинающиеся с букв!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
-- а что делать с неначинающимися?????????????????????????????????????
update tmpC
set master_code = concat('В', master_code),
code = concat(section, code);


select 'Устанавливаем соответствия для состава сложных услуг...' as ' ';
update tmpC, rbServiceGroup
left join rbService sGroup on sGroup.id = rbServiceGroup.group_id
left join rbService sService on sService.id = rbServiceGroup.service_id
set tmpC.rbServiceGroup_id = rbServiceGroup.id,
tmpC.rbServiceGroup_type = 2
where sGroup.code = tmpC.master_code
and sService.code = tmpC.code
and tmpC.rbServiceGroup_type = 0;


select 'Добавление состава сложных услуг...' as ' ';
update tmpC
set rbServiceGroup_type = 5
where rbServiceGroup_type = 0;

select concat(convert(count(*) using utf8), ' подчинённых услуг добавляется...') as ' '
from tmpC
where tmpC.rbServiceGroup_type = 5;

insert into rbServiceGroup(group_id, service_id, required)
select  sGroup.id as group_id,
	sService.id as service_id,
	required
from tmpC
left join rbService sGroup on sGroup.code = tmpC.master_code
left join rbService sService on sService.code = tmpC.code
where tmpC.rbServiceGroup_type = 5
and sGroup.id is not NULL
and sService.id is not NULL;

select 'Устанавливаем соответствия для добавленных сложных услуг...' as ' ';
update tmpC, rbServiceGroup
left join rbService sGroup on sGroup.id = rbServiceGroup.group_id
left join rbService sService on sService.id = rbServiceGroup.service_id
set tmpC.rbServiceGroup_id = rbServiceGroup.id,
tmpC.rbServiceGroup_type = 2
where sGroup.code = tmpC.master_code
and sService.code = tmpC.code
and tmpC.rbServiceGroup_type = 5;

-- Очищаем лишние услуги с group_id = 0 или service_id = 0 (а откуда они вообще взялись????????????????????)
delete from rbServiceGroup
where group_id = 0
or service_id = 0;


-- С временными таблицами не прокатывает двойное сравнение!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
--select 'Удаление лишних подчинённых услуг...' as ' ';
--delete from rbServiceGroup
--where exists
--(select * from tmpC
--left join rbService on rbService.code = tmpC.master_code
--where rbService.id = rbServiceGroup.group_id
--)
--and not exists
--(select * from tmpC where tmpC.rbServiceGroup_id = rbServiceGroup.id
--and tmpC.rbServiceGroup_type = 2);























select 'Импорт манипуляций, исследований, процедур и работ (Дxx.xx.xx)...' as ' ';
update tmpD
set rbService_type = 0 -- неизвестно
where rbService_type is null;
update tmpD
set rbServiceType_type = 0 -- неизвестно
where rbServiceType_type is null;

select 'Устанавливаем соответствия для манипуляций, исследований, процедур и работ...' as ' ';
-- сперва по полному совпадению кода:
update tmpD, rbService
set tmpD.rbService_id = rbService.id,
tmpD.rbService_type = 3
where rbService.code = concat('Д', tmpD.code)
and tmpD.rbService_type = 0;
-- теперь предполагаем, что буква Д могла быть пропущена:
update tmpD, rbService
set tmpD.rbService_id = rbService.id,
tmpD.rbService_type = 3
where rbService.code = tmpD.code
and tmpD.rbService_type = 0;

-- теперь с типами:
update tmpD, rbServiceType
set tmpD.rbServiceType_id = rbServiceType.id,
tmpD.rbServiceType_type = 3 -- типы всегда переписываются
where rbServiceType.section = 'Д'
and rbServiceType.code = tmpD.code
and tmpD.rbServiceType_type = 0;


select 'Обновление манипуляций, исследований, процедур и работ...' as ' ';
select concat(convert(count(*) using utf8), ' услуг обновляется...') as ' '
from tmpD
where tmpD.rbService_type = 3;

update tmpD, rbService
set rbService.code = concat('Д', tmpD.code),
rbService.name = tmpD.name,
rbService.nomenclatureLegacy = 1
where tmpD.rbService_id = rbService.id
and tmpD.rbService_type = 3;

select concat(convert(count(*) using utf8), ' типов услуг обновляется...') as ' '
from tmpD
where tmpD.rbServiceType_type = 3;

update tmpD, rbServiceType
set rbServiceType.name = tmpD.name
where tmpD.rbServiceType_id = rbServiceType.id
and tmpD.rbServiceType_type = 3;



select 'Добавление манипуляций, исследований, процедур и работ...' as ' ';

update tmpD
set rbService_type = 5
where length(code) >= 5
and rbService_type = 0;

select concat(convert(count(*) using utf8), ' услуг добавляется...') as ' '
from tmpD
where tmpD.rbService_type = 5;

insert into rbService(code, name, eisLegacy, nomenclatureLegacy, infis, begDate, endDate)
select  concat('Д', tmpD.code) as code,
	name,
	0 as eisLegacy,
	1 as nomenclatureLegacy,
	concat('Д', tmpD.code) as infis, -- ???????????????????????
	'0000-00-00' as begDate, -- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	'2200-01-01' as endDate
from tmpD
where tmpD.rbService_type = 5;

update tmpD
set rbServiceType_type = 5
where length(code) = 2
and rbServiceType_type = 0;

select concat(convert(count(*) using utf8), ' типов услуг добавляется...') as ' '
from tmpD
where tmpD.rbServiceType_type = 5;

insert into rbServiceType(section, code, name, `class`)
select 	'Д' as section,
	code,
	name,
	3 as `class`
from tmpD
where tmpD.rbServiceType_type = 5;























-- F импортируется так же, как D:
select 'Импорт услуг медицинского сервиса (Фxx.xx.xx)...' as ' ';
update tmpF
set rbService_type = 0 -- неизвестно
where rbService_type is null;
update tmpF
set rbServiceType_type = 0 -- неизвестно
where rbServiceType_type is null;

select 'Устанавливаем соответствия для услуг медицинского сервиса...' as ' ';
-- сперва по полному совпадению кода:
update tmpF, rbService
set tmpF.rbService_id = rbService.id,
tmpF.rbService_type = 3
where rbService.code = concat('Ф', tmpF.code)
and tmpF.rbService_type = 0;
-- теперь предполагаем, что буква F могла быть пропущена:
update tmpF, rbService
set tmpF.rbService_id = rbService.id,
tmpF.rbService_type = 3
where rbService.code = tmpF.code
and tmpF.rbService_type = 0;

-- теперь с типами:
update tmpF, rbServiceType
set tmpF.rbServiceType_id = rbServiceType.id,
tmpF.rbServiceType_type = 3 -- типы всегда переписываются
where rbServiceType.section = 'Ф'
and rbServiceType.code = tmpF.code
and tmpF.rbServiceType_type = 0;

select 'Обновление услуг медицинского сервиса...' as ' ';
select concat(convert(count(*) using utf8), ' услуг обновляется...') as ' '
from tmpF
where tmpF.rbService_type = 3;

update tmpF, rbService
set rbService.code = concat('Ф', tmpF.code),
rbService.name = tmpF.name,
rbService.nomenclatureLegacy = 1
where tmpF.rbService_id = rbService.id
and tmpF.rbService_type = 3;

select concat(convert(count(*) using utf8), ' типов услуг обновляется...') as ' '
from tmpF
where tmpF.rbServiceType_type = 3;

update tmpF, rbServiceType
set rbServiceType.name = tmpF.name
where tmpF.rbServiceType_id = rbServiceType.id
and tmpF.rbServiceType_type = 3;


select 'Добавление услуг медицинского сервиса...' as ' ';

update tmpF
set rbService_type = 5
where length(code) >= 5
and rbService_type = 0;

select concat(convert(count(*) using utf8), ' услуг добавляется...') as ' '
from tmpF
where tmpF.rbService_type = 5;

insert into rbService(code, name, eisLegacy, nomenclatureLegacy, infis, begDate, endDate)
select 	concat('Ф', tmpF.code) as code,
	name,
	0 as eisLegacy,
	1 as nomenclatureLegacy,
	concat('Ф', tmpF.code) as infis, -- ???????????????????????
	'0000-00-00' as begDate, -- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	'2200-01-01' as endDate
from tmpF
where tmpF.rbService_type = 5;

update tmpF
set rbServiceType_type = 5
where length(code) = 2
and rbServiceType_type = 0;

select concat(convert(count(*) using utf8), ' типов услуг добавляется...') as ' '
from tmpF
where tmpF.rbServiceType_type = 5;

insert into rbServiceType(section, code, name, `class`)
select  'Ф' as section,
	code,
	name,
	3 as `class`
from tmpF
where tmpF.rbServiceType_type = 5;