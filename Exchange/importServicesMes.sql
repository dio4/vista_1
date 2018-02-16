select 'Создание и заполнение временных таблиц...' as ' ';

CREATE TEMPORARY TABLE if not exists `tmpService` (
`id` INT( 11 ) NOT NULL AUTO_INCREMENT ,
`code` VARCHAR( 64 ) NOT NULL ,
`name` VARCHAR( 255 ) NOT NULL ,
`rbService_id` INT( 11 ) NULL ,
`rbService_type` TINYINT( 1 ) NOT NULL ,
 PRIMARY KEY ( `id` ) ,
INDEX ( `code`),
INDEX ( `rbService_id` ) 
 ) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci;
 
CREATE TEMPORARY TABLE if not exists `tmpService_Contents` (
`id` INT( 11 ) NOT NULL AUTO_INCREMENT ,
`master_id` INT( 11 ) NOT NULL ,
`service_id` INT( 11 ) NOT NULL ,
`necessity` DOUBLE NOT NULL ,
`rbServiceGroup_id` INT( 11 ) NULL ,
`rbServiceGroup_type` TINYINT( 1 ) NOT NULL ,
PRIMARY KEY ( `id` ) ,
INDEX ( `master_id` ),
INDEX( `rbServiceGroup_id` ) 
) ENGINE = MYISAM;

insert ignore into tmpService
select id, code, name, NULL, 0
from mes.mrbService;

insert ignore into tmpService_Contents
select id, master_id, service_id, necessity, NULL, 0
from mes.mrbService_Contents;


select 'Установление соответствий для услуг...' as ' ';
update tmpService, rbService
set tmpService.rbService_id = rbService.id,
tmpService.rbService_type = if(@update_services, 3, 2)
where rbService.code = tmpService.code
and tmpService.rbService_type = 0;


select 'Обновление услуг...' as ' ';
select concat(convert(count(*) using utf8), ' услуг обновляется...') as ' '
from tmpService
where tmpService.rbService_type = 3;

update tmpService, rbService
set rbService.name = tmpService.name
where tmpService.rbService_id = rbService.id
and tmpService.rbService_type = 3;



select 'Добавление услуг...' as ' ';
update tmpService
set rbService_type = 5
where @add_services
and rbService_type = 0;

select concat(convert(count(*) using utf8), ' услуг добавляется...') as ' '
from tmpService
where tmpService.rbService_type = 5;

insert into rbService(code, name, eisLegacy, nomenclatureLegacy, infis, begDate, endDate)
select  code,
	name,
	0 as eisLegacy,
	1 as nomenclatureLegacy,
	tmpService.code as infis, -- ???????????????????????
	'0000-00-00' as begDate, -- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	'2200-01-01' as endDate
from tmpService
where tmpService.rbService_type = 5;



select 'Установление соответствий для добавленных услуг...' as ' ';
update tmpService, rbService
set tmpService.rbService_id = rbService.id,
tmpService.rbService_type = 3
where rbService.code = tmpService.code
and tmpService.rbService_type = 0;



select 'Установление соответствий для состава сложных услуг...' as ' ';
-- упрощаем извлечение master_id и service_id
update tmpService_Contents
left join tmpService tGroup on tmpService_Contents.master_id = tGroup.id
set tmpService_Contents.master_id = tGroup.rbService_id;
update tmpService_Contents
left join tmpService tService on tmpService_Contents.service_id = tService.id
set tmpService_Contents.service_id = tService.rbService_id;

update tmpService_Contents,
rbServiceGroup
left join rbService sGroup on sGroup.id = rbServiceGroup.group_id
left join rbService sService on sService.id = rbServiceGroup.service_id
set tmpService_Contents.rbServiceGroup_id = rbServiceGroup.id,
tmpService_Contents.rbServiceGroup_type = 2
where tmpService_Contents.rbServiceGroup_type = 0
and tmpService_Contents.master_id = sGroup.id
and tmpService_Contents.service_id = sService.id;

select 'Добавление состава сложных услуг...' as ' ';
update tmpService_Contents
left join tmpService on tmpService_Contents.master_id = tmpService.id
set rbServiceGroup_type = 5
where rbServiceGroup_type = 0
and tmpService.rbService_type = 3; -- добавляем состав, только если услуга подлежит редактированию

select concat(convert(count(*) using utf8), ' подчинённых услуг добавляется...') as ' '
from tmpService_Contents
where tmpService_Contents.rbServiceGroup_type = 5;

insert into rbServiceGroup(group_id, service_id, required)
select  master_id as group_id,
	service_id,
	if (necessity=1, 1, 0) as required
from tmpService_Contents
where tmpService_Contents.rbServiceGroup_type = 5;


--select 'Установление соответствий для добавленного состава сложных услуг...' as ' ';
--update tmpC, rbServiceGroup
--left join rbService sGroup on sGroup.id = rbServiceGroup.group_id
--left join rbService sService on sService.id = rbServiceGroup.service_id
--set tmpC.rbServiceGroup_id = rbServiceGroup.id,
--tmpC.rbServiceGroup_type = 2
--where sGroup.code = tmpC.master_code
--and sService.code = tmpC.code
--and tmpC.rbServiceGroup_type = 5;

-- Очищаем лишние услуги с group_id = 0 или service_id = 0 (а откуда они вообще взялись????????????????????)
--delete from rbServiceGroup
--where group_id = 0
--or service_id = 0;

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


select 'Удаление временных таблиц...' as ' ';

delete from tmpService where 1;
delete from tmpService_Contents where 1;


select 'Обновление выполнено!' as ' ';