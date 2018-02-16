#!/usr/bin/env python
# -*- coding: utf-8 -*-

COMMAND = u"""

select 'Определение параметров услуг...' as ' ';

update tmpService2ActionType
left join rbServiceType on rbServiceType.section = left(tmpService2ActionType.code, 1) 
			and rbServiceType.code = substr(tmpService2ActionType.code from 2 for 2)
set `level` = char_length(tmpService2ActionType.code) - char_length(replace(tmpService2ActionType.code, '.', '')) + 1,
tmpService2ActionType.`class` = rbServiceType.`class`
where `level` = 0;


select 'Определение зависимых услуг 4-го уровня...' as ' ';
update tmpService2ActionType
set parentCode = substr(code from 1 for char_length(code) - locate('.', reverse(code)))
where `level` = 5;

replace into tmpParents select * from tmpService2ActionType;

INSERT IGNORE INTO tmpService2ActionType(code, name, parentCode, `level`, `class`)
SELECT rbService.code as code,
       rbService.name as name,
       NULL as 'parentCode',
       4 as 'level',
       rbServiceType.`class` as `class`
       FROM rbService
       LEFT JOIN rbServiceType on rbServiceType.section = left(rbService.code, 1) and rbServiceType.code = substr(rbService.code from 2 for 2)
       where exists (select * from tmpParents
			where `level` = 5
			and tmpParents.parentCode = rbService.code);

select 'Определение зависимых услуг 3-го уровня...' as ' ';
update tmpService2ActionType
set parentCode = substr(code from 1 for char_length(code) - locate('.', reverse(code)))
where `level` = 4;

replace into tmpParents select * from tmpService2ActionType;

INSERT IGNORE INTO tmpService2ActionType(code, name, parentCode, `level`, `class`)
SELECT rbService.code as code,
       rbService.name as name,
       NULL as 'parentCode',
       3 as 'level',
       rbServiceType.`class` as `class`
       FROM rbService
       LEFT JOIN rbServiceType on rbServiceType.section = left(rbService.code, 1) and rbServiceType.code = substr(rbService.code from 2 for 2)
       where exists (select * from tmpParents
			where `level` = 4
			and tmpParents.parentCode = rbService.code);

select 'Определение зависимых услуг 2-го уровня...' as ' ';
update tmpService2ActionType
set parentCode = substr(code from 1 for char_length(code) - locate('.', reverse(code)))
where `level` = 3;

replace into tmpParents select * from tmpService2ActionType;

-- Для Д и Ф импортируются обычные услуги 2-го уровня
INSERT IGNORE INTO tmpService2ActionType(code, name, parentCode, `level`, `class`)
SELECT rbService.code as code,
       rbService.name as name,
       NULL as 'parentCode',
       2 as 'level',
       rbServiceType.`class` as `class`
       FROM rbService
       LEFT JOIN rbServiceType on rbServiceType.section = left(rbService.code, 1) and rbServiceType.code = substr(rbService.code from 2 for 2)
       where	(rbService.code like 'Д%' or rbService.code like 'Ф%')
		and exists (select * from tmpParents
			where `level` = 3
			and tmpParents.parentCode = rbService.code);

-- А для А и В импортируются классы услуг, совмещённые с типами!
INSERT IGNORE INTO tmpService2ActionType(code, name, parentCode, `level`, `class`)
SELECT concat(rbServiceType.section, rbServiceType.code, '.', rbServiceClass.code) as code,
       rbServiceClass.name as name,
       concat(rbServiceType.section, rbServiceType.code) as 'parentCode',
       2 as 'level',
       rbServiceType.`class` as `class`
       FROM rbServiceType,
	    rbServiceClass
       where	(rbServiceType.section = 'А' or rbServiceType.section = 'В')
		and (rbServiceClass.section = 'А' or rbServiceClass.section = 'В')
		and exists (select * from tmpParents
			where `level` = 3
			and rbServiceType.section = left(tmpParents.parentCode, 1)
			and rbServiceType.code = substr(tmpParents.parentCode from 2 for 2)
			and rbServiceClass.section = left(tmpParents.parentCode, 1)
			and rbServiceClass.code = substr(tmpParents.parentCode from 5));




select 'Определение зависимых услуг 1-го уровня...' as ' ';
update tmpService2ActionType
set parentCode = substr(code from 1 for char_length(code) - locate('.', reverse(code)))
where `level` = 2
and parentCode is null;

replace into tmpParents select * from tmpService2ActionType;

-- Все услуги 1-го уровня - это типы!
INSERT IGNORE INTO tmpService2ActionType(code, name, parentCode, `level`, `class`)
SELECT concat(rbServiceType.section, rbServiceType.code) as code,
       name,
       NULL as 'parentCode',
       1 as 'level',
       `class`
       FROM rbServiceType
       where exists (select * from tmpParents
			where `level` = 2
			and tmpParents.parentCode = concat(rbServiceType.section, rbServiceType.code));



select 'Установление соответствий для услуг 1-го уровня...' as ' ';
update tmpService2ActionType
left join ActionType on tmpService2ActionType.code = ActionType.code
			and ActionType.`class` = tmpService2ActionType.`class`
			and (ActionType.deleted = 0 or @compareDeleted)
set tmpService2ActionType.ActionType_id = ActionType.id,
tmpService2ActionType.ActionType_type = 2
where tmpService2ActionType.`level` = 1
and ActionType.id is not NULL;

select concat(count(*), ' соответствий установлено.') as ' ' from tmpService2ActionType
where ActionType_type = 2;

select 'Добавление услуг 1-го уровня...' as ' ';
update tmpService2ActionType
set ActionType_type = 5
where `level` = 1
and ActionType_type = 0;

insert into ActionType(createDatetime, createPerson_id, modifyDatetime, modifyPerson_id, `class`, group_id, code, name, title, amount, nomenclativeService_id, showInForm)
select 	now() as createDatetime,
	@person_id as createPerson_id,
	now() as modifyDatetime,
	@person_id as modifyPerson_id,
	`class`,
	NULL as group_id,
	code,
	name,
	name as title,
--	code as flatCode,
	1 as amount,
	NULL as nomenclativeService_id, -- это тип услуги, а не услуга!
	1 as showInForm
from tmpService2ActionType
where tmpService2ActionType.`level` = 1
and tmpService2ActionType.ActionType_type = 5;


select 'Установление соответствий для добавленных услуг 1-го уровня...' as ' ';
update tmpService2ActionType
left join ActionType on tmpService2ActionType.code = ActionType.code
			and ActionType.`class` = tmpService2ActionType.`class`
			and (ActionType.deleted=0 or @compareDeleted)
set tmpService2ActionType.ActionType_id = ActionType.id,
tmpService2ActionType.ActionType_type = 2
where tmpService2ActionType.`level` = 1
and ActionType.id is not NULL;

select 'Установление соответствий для услуг 2-го уровня...' as ' ';
-- номенклатурных
update tmpService2ActionType
--left join ActionType on tmpService2ActionType.code = ActionType.code
left join ActionType AGroup on AGroup.`class` = tmpService2ActionType.`class`
				and AGroup.code = tmpService2ActionType.parentCode
left join ActionType on ActionType.`class` = tmpService2ActionType.`class`
			and ActionType.group_id = AGroup.id
			and ActionType.code = tmpService2ActionType.code
			and (ActionType.deleted=0 or @compareDeleted)
set tmpService2ActionType.ActionType_id = ActionType.id,
tmpService2ActionType.ActionType_type = 2
where tmpService2ActionType.parentCode <> '-'
and tmpService2ActionType.`level` = 2
and ActionType.id is not NULL;

-- не номенклатурных
update tmpService2ActionType
left join ActionType on tmpService2ActionType.code = ActionType.code
			and (ActionType.deleted=0 or @compareDeleted)
set tmpService2ActionType.ActionType_id = ActionType.id,
tmpService2ActionType.ActionType_type = 3
where ActionType.nomenclativeService_id is NULL
and tmpService2ActionType.parentCode = '-'
and tmpService2ActionType.`level` = 2
and ActionType.id is not NULL;

select if(@updateNames, 'Обновление названий для неноменклатурных услуг 2-го уровня...', '') as ' ';
-- обновление названий, если установлен флажок @updateNames
update tmpService2ActionType
left join ActionType on tmpService2ActionType.ActionType_id = ActionType.id
			and tmpService2ActionType.ActionType_type = 3
set 	ActionType.modifyDatetime = now(),
	ActionType.modifyPerson_id = @person_id,
	ActionType.name = tmpService2ActionType.name,
    	ActionType.title = tmpService2ActionType.name
where ActionType.name <> tmpService2ActionType.name
and @updateNames;

select 'Добавление услуг 2-го уровня' as ' ';
update tmpService2ActionType
set ActionType_type = 5
where `level` = 2
and ActionType_type = 0;

insert into ActionType(createDatetime, createPerson_id, modifyDatetime, modifyPerson_id, `class`, group_id, code, name, title, amount, nomenclativeService_id, showInForm)
select 	now() as createDatetime,
	@person_id as createPerson_id,
	now() as modifyDatetime,
	@person_id as modifyPerson_id,
	tmpService2ActionType.`class` as `class`,
	AGroup.id as group_id,
	tmpService2ActionType.code as code,
	--if(tmpService2ActionType.parentCode <> '-', substr(tmpService2ActionType.code from 5), tmpService2ActionType.code) as code,
	tmpService2ActionType.name as name,
	tmpService2ActionType.name as title,
--	tmpService2ActionType.code as flatCode,
	1 as amount,
	if(tmpService2ActionType.parentCode <> '-', rbService.id, NULL) as nomenclativeService_id,
	1 as showInForm
from tmpService2ActionType
left join ActionType AGroup on AGroup.`class` = tmpService2ActionType.`class`
				and AGroup.code = tmpService2ActionType.parentCode
left join rbService on tmpService2ActionType.code = rbService.code
where tmpService2ActionType.`level` = 2
and tmpService2ActionType.ActionType_type = 5;


select 'Установление соответствий для добавленных услуг 2-го уровня' as ' ';
-- номенклатурных
update tmpService2ActionType
--left join ActionType on tmpService2ActionType.code = ActionType.code
left join ActionType AGroup on AGroup.`class` = tmpService2ActionType.`class`
				and AGroup.code = tmpService2ActionType.parentCode
left join ActionType on ActionType.`class` = tmpService2ActionType.`class`
			and ActionType.group_id = AGroup.id
			and ActionType.code = tmpService2ActionType.code
			and (ActionType.deleted=0 or @compareDeleted)
set tmpService2ActionType.ActionType_id = ActionType.id,
tmpService2ActionType.ActionType_type = 2
where tmpService2ActionType.parentCode <> '-'
and tmpService2ActionType.`level` = 2
and ActionType.id is not NULL;

-- не номенклатурных
update tmpService2ActionType
--left join ActionType on tmpService2ActionType.code = ActionType.code
left join ActionType AGroup on AGroup.`class` = 3
				and AGroup.code = '-'
left join ActionType on ActionType.`class` = 3
			and ActionType.group_id = AGroup.id
			and ActionType.code = tmpService2ActionType.code
set tmpService2ActionType.ActionType_id = ActionType.id,
tmpService2ActionType.ActionType_type = 2
where tmpService2ActionType.parentCode = '-'
and ActionType.nomenclativeService_id is NULL
and tmpService2ActionType.`level` = 2
and ActionType.id is not NULL;



select 'Установление соответствий для услуг 3-го уровня' as ' ';

replace into tmpParents select * from tmpService2ActionType;

update tmpService2ActionType
--left join ActionType on tmpService2ActionType.code = ActionType.code
left join tmpParents on tmpService2ActionType.parentCode = tmpParents.code
left join ActionType AGroup on AGroup.id = tmpParents.ActionType_id
left join ActionType on ActionType.`class` = tmpService2ActionType.`class`
			and ActionType.group_id = AGroup.id
			and ActionType.code = tmpService2ActionType.code
			and (ActionType.deleted = 0 or @compareDeleted)
set tmpService2ActionType.ActionType_id = ActionType.id,
tmpService2ActionType.ActionType_type = 2
where tmpService2ActionType.`level` = 3
and ActionType.id is not NULL;

select 'Добавление услуг 3-го уровня' as ' ';
update tmpService2ActionType
set ActionType_type = 5
where `level` = 3
and ActionType_type = 0;

insert into ActionType(createDatetime, createPerson_id, modifyDatetime, modifyPerson_id, `class`, group_id, code, name, title, amount, nomenclativeService_id, showInForm)
select 	now() as createDatetime,
	@person_id as createPerson_id,
	now() as modifyDatetime,
	@person_id as modifyPerson_id,
	tmpService2ActionType.`class` as `class`,
	AGroup.id as group_id,
	tmpService2ActionType.code as code,
	--substr(tmpService2ActionType.code from char_length(tmpService2ActionType.code) - locate('.', reverse(tmpService2ActionType.code)) + 2) as code,
	tmpService2ActionType.name as name,
	tmpService2ActionType.name as title,
--	tmpService2ActionType.code as flatCode,
	1 as amount,
	rbService.id as nomenclativeService_id,
	1 as showInForm
from tmpService2ActionType
left join tmpParents on tmpService2ActionType.parentCode = tmpParents.code
left join ActionType AGroup on AGroup.id = tmpParents.ActionType_id
left join rbService on tmpService2ActionType.code = rbService.code
where tmpService2ActionType.`level` = 3
and tmpService2ActionType.ActionType_type = 5;

select 'Установление соответствий для добавленных услуг 3-го уровня' as ' ';
update tmpService2ActionType
--left join ActionType on tmpService2ActionType.code = ActionType.code
left join tmpParents on tmpService2ActionType.parentCode = tmpParents.code
left join ActionType AGroup on AGroup.id = tmpParents.ActionType_id
left join ActionType on ActionType.`class` = tmpService2ActionType.`class`
			and ActionType.group_id = AGroup.id
			and ActionType.code = tmpService2ActionType.code
			and (ActionType.deleted = 0 or @compareDeleted)
set tmpService2ActionType.ActionType_id = ActionType.id,
tmpService2ActionType.ActionType_type = 2
where tmpService2ActionType.`level` = 3
and ActionType.id is not NULL;



select 'Установление соответствий для услуг 4-го уровня' as ' ';

replace into tmpParents select * from tmpService2ActionType;

update tmpService2ActionType
--left join ActionType on tmpService2ActionType.code = ActionType.code
left join tmpParents on tmpService2ActionType.parentCode = tmpParents.code
left join ActionType AGroup on AGroup.id = tmpParents.ActionType_id
left join ActionType on ActionType.`class` = tmpService2ActionType.`class`
			and ActionType.group_id = AGroup.id
			and ActionType.code = tmpService2ActionType.code
			and (ActionType.deleted = 0 or @compareDeleted)
set tmpService2ActionType.ActionType_id = ActionType.id,
tmpService2ActionType.ActionType_type = 2
where tmpService2ActionType.`level` = 4
and ActionType.id is not NULL;

select 'Добавление услуг 4-го уровня' as ' ';
update tmpService2ActionType
set ActionType_type = 5
where `level` = 4
and ActionType_type = 0;

insert into ActionType(createDatetime, createPerson_id, modifyDatetime, modifyPerson_id, `class`, group_id, code, name, title, amount, nomenclativeService_id, showInForm)
select 	now() as createDatetime,
	@person_id as createPerson_id,
	now() as modifyDatetime,
	@person_id as modifyPerson_id,
	tmpService2ActionType.`class` as `class`,
	AGroup.id as group_id,
	tmpService2ActionType.code as code,
	--substr(tmpService2ActionType.code from char_length(tmpService2ActionType.code) - locate('.', reverse(tmpService2ActionType.code)) + 2) as code,
	tmpService2ActionType.name as name,
	tmpService2ActionType.name as title,
--	tmpService2ActionType.code as flatCode,
	1 as amount,
	rbService.id as nomenclativeService_id,
	1 as showInForm
from tmpService2ActionType
left join tmpParents on tmpService2ActionType.parentCode = tmpParents.code
left join ActionType AGroup on AGroup.id = tmpParents.ActionType_id
left join rbService on tmpService2ActionType.code = rbService.code
where tmpService2ActionType.`level` = 4
and tmpService2ActionType.ActionType_type = 5;

select 'Установление соответствий для добавленных услуг 4-го уровня' as ' ';
update tmpService2ActionType
--left join ActionType on tmpService2ActionType.code = ActionType.code
left join tmpParents on tmpService2ActionType.parentCode = tmpParents.code
left join ActionType AGroup on AGroup.id = tmpParents.ActionType_id
left join ActionType on ActionType.`class` = tmpService2ActionType.`class`
			and ActionType.group_id = AGroup.id
			and ActionType.code = tmpService2ActionType.code
			and (ActionType.deleted = 0 or @compareDeleted)
set tmpService2ActionType.ActionType_id = ActionType.id,
tmpService2ActionType.ActionType_type = 2
where tmpService2ActionType.`level` = 4
and ActionType.id is not NULL;



select 'Установление соответствий для услуг 5-го уровня' as ' ';

replace into tmpParents select * from tmpService2ActionType;

update tmpService2ActionType
--left join ActionType on tmpService2ActionType.code = ActionType.code
left join tmpParents on tmpService2ActionType.parentCode = tmpParents.code
left join ActionType AGroup on AGroup.id = tmpParents.ActionType_id
left join ActionType on ActionType.`class` = tmpService2ActionType.`class`
			and ActionType.group_id = AGroup.id
			and ActionType.code = tmpService2ActionType.code
			and (ActionType.deleted = 0 or @compareDeleted)
set tmpService2ActionType.ActionType_id = ActionType.id,
tmpService2ActionType.ActionType_type = 2
where tmpService2ActionType.`level` = 5
and ActionType.id is not NULL;

select 'Добавление услуг 5-го уровня' as ' ';
update tmpService2ActionType
set ActionType_type = 5
where `level` = 5
and ActionType_type = 0;

insert into ActionType(createDatetime, createPerson_id, modifyDatetime, modifyPerson_id, `class`, group_id, code, name, title, amount, nomenclativeService_id, showInForm)
select 	now() as createDatetime,
	@person_id as createPerson_id,
	now() as modifyDatetime,
	@person_id as modifyPerson_id,
	tmpService2ActionType.`class` as `class`,
	AGroup.id as group_id,
	tmpService2ActionType.code as code,
	--substr(tmpService2ActionType.code from char_length(tmpService2ActionType.code) - locate('.', reverse(tmpService2ActionType.code)) + 2) as code,
	tmpService2ActionType.name as name,
	tmpService2ActionType.name as title,
--	tmpService2ActionType.code as flatCode,
	1 as amount,
	rbService.id as nomenclativeService_id,
	1 as showInForm
from tmpService2ActionType
left join tmpParents on tmpService2ActionType.parentCode = tmpParents.code
left join ActionType AGroup on AGroup.id = tmpParents.ActionType_id
left join rbService on tmpService2ActionType.code = rbService.code
where tmpService2ActionType.`level` = 5
and tmpService2ActionType.ActionType_type = 5;


select 'Установление соответствий для добавленных услуг 5-го уровня' as ' ';
update tmpService2ActionType
--left join ActionType on tmpService2ActionType.code = ActionType.code
left join tmpParents on tmpService2ActionType.parentCode = tmpParents.code
left join ActionType AGroup on AGroup.id = tmpParents.ActionType_id
left join ActionType on ActionType.`class` = tmpService2ActionType.`class`
			and ActionType.group_id = AGroup.id
			and ActionType.code = tmpService2ActionType.code
			and (ActionType.deleted = 0 or @compareDeleted)
set tmpService2ActionType.ActionType_id = ActionType.id,
tmpService2ActionType.ActionType_type = 2
where tmpService2ActionType.`level` = 5
and ActionType.id is not NULL;


select 'Установление соответствий с услугами для типов действий' as ' ';
update tmpService2ActionType
left join ActionType on tmpService2ActionType.ActionType_id = ActionType.id,
ActionType_Service
set tmpService2ActionType.ActionType_Service_id = ActionType_Service.id,
tmpService2ActionType.ActionType_Service_type = 2
where ActionType_Service.master_id = ActionType.id
and ActionType_Service.finance_id is NULL
and tmpService2ActionType.ActionType_type = 2
and tmpService2ActionType.ActionType_Service_type = 0;

select 'Добавление сведений об услуге по умолчанию для типов действий' as ' ';
-- добавляем услуги для типов действий выше 2 уровня, у которых есть услуги
update tmpService2ActionType
left join rbService on tmpService2ActionType.code = rbService.code
set ActionType_Service_type = 5
where ActionType_type = 2
and `level` >= 2
and rbService.id is not NULL
and ActionType_Service_type = 0;

INSERT INTO ActionType_Service (master_id, idx, finance_id, service_id)
SELECT ActionType.id, 99, NULL, rbService.id
FROM tmpService2ActionType
left join ActionType on tmpService2ActionType.ActionType_id = ActionType.id
left join rbService on tmpService2ActionType.code = rbService.code
where tmpService2ActionType.ActionType_Service_type = 5;


select if(@compareDeleted, 'Снятие пометки на удаление с типов действий, для которых есть услуги...', '') as ' ';
-- снятие пометки на удаление, если установлен флажок @compareDeleted
update tmpService2ActionType
left join ActionType on tmpService2ActionType.ActionType_id = ActionType.id
			and tmpService2ActionType.ActionType_type in (2,3)
set 	ActionType.modifyDatetime = now(),
	ActionType.modifyPerson_id = @person_id,
	ActionType.deleted = 0
where ActionType.deleted = 1
and @compareDeleted;





select 'Удаление временных таблиц...' as ' ';
delete from tmpService2ActionType where 1;
delete from tmpParents where 1;
--drop table tmpService2ActionType;

select 'Синхронизация услуг с типами действий завершена!' as ' ';"""
