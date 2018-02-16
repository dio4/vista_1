#!/usr/bin/env python
# -*- coding: utf-8 -*-

COMMAND = u"""

--use s11;

-- Текущая организация - та, в которой работает текущий юзер:
select @org_id := Organisation.id from Organisation, Person
where Person.id = @user_id
and Person.org_id = Organisation.id;
select @org_id := ifnull(@org_id, 0);

-- Сперва обновляем информацию о банках:
select 'Обновляем информацию о банках...' as ' ';
select 'Общее количество банков:' as ' ';
select @max_bank_id := max(id) from Bank;
-- сначала смотрим, какие BIK и имена филиалов отсутствуют; добавляем их
--select concat('Updating ', format(count(tmpLPU.LPU_LONG_NAME), 0), ' records...') as ' '
insert into Bank
select distinct
       0 as id,
      '0000-00-00 00:00:00' as createDatetime,
       NULL as createPerson_id,
       '0000-00-00 00:00:00' as modifyDatetime,
       NULL as modifyPerson_id,
       0 as deleted,
       BIK,
       '' as name,
       FILIAL as branchName,
       '' as corAccount,
       '' as subAccount
       from tmpLPU
       where not exists (
        select BIK, branchName from Bank
        where Bank.BIK = tmpLPU.BIK
        and Bank.branchName = tmpLPU.FILIAL);

-- обновляем старые банки
update Bank, tmpLPU
set modifyDatetime = now(), 
    modifyPerson_id = @user_id,
    name = tmpLPU.Bank 
where Bank.BIK = tmpLPU.BIK
and Bank.branchName = tmpLPU.FILIAL
and Bank.id <= @max_bank_id;

-- и новые банки
update Bank, tmpLPU
set createDatetime = now(), 
    createPerson_id = @user_id,
    modifyDatetime = now(), 
    modifyPerson_id = @user_id,
    name = tmpLPU.Bank 
where Bank.BIK = tmpLPU.BIK
and Bank.branchName = tmpLPU.FILIAL
and Bank.id > @max_bank_id;







-- Теперь обновляем информацию об организациях:
select 'Обновляем информацию об организациях...' as ' ';

-- такой ИНН уже существует - обновить информацию
-- Обновляется в случае, если изменился ИНФИС, имя, КПП, адрес, телефон или руководитель
select concat('Обновление ', format(count(tmpLPU.LPU_LONG_NAME), 0), ' записей...') as ' '
from tmpLPU, Organisation
where tmpLPU.INN = Organisation.INN
and Organisation.id != @org_id; -- не надо обновлять информацию о собственной организации

update Organisation, tmpLPU
set Organisation.modifyDatetime = now(), 
    Organisation.modifyPerson_id = @user_id,
    Organisation.infisCode = tmpLPU.CODE,
    Organisation.obsoleteInfisCode = tmpLPU.OLD_CODES,
    Organisation.fullName = tmpLPU.LPU_LONG_NAME,
    Organisation.Address = tmpLPU.JUR_ADDRESS,
    Organisation.chief = tmpLPU.FIO,
    Organisation.phone = tmpLPU.PHONE,
    Organisation.notes = concat(tmpLPU.REMARK, if(length(trim(tmpLPU.REMARK)) > 0, '. ', ''),
        if(length(tmpLPU.EMAIL) > 0, 'E-mail: ', ''), tmpLPU.EMAIL, if(length(tmpLPU.EMAIL) > 0, '. ', ''),
        if(length(tmpLPU.FAX) > 0, 'Fax: ', ''), tmpLPU.FAX)
where tmpLPU.INN = Organisation.INN
--and ((tmpLPU.CODE != Organisation.infisCode)
--    or (Organisation.obsoleteInfisCode != tmpLPU.OLD_CODES)
--    or (Organisation.fullName != tmpLPU.LPU_LONG_NAME)
--    or (Organisation.Address != tmpLPU.ADDRESS)
--    or (Organisation.chief != tmpLPU.FIO)
--    or (Organisation.phone != tmpLPU.PHONE) )
and Organisation.id != @org_id; -- не надо обновлять информацию о собственной организации


-- такого имени нет, но такой старый ИНФИС уже существует - переименовать организацию и обновить информацию
--select 'Переименование и обновление записей...' as ' ';
--select concat('Переименование и обновление ', format(count(tmpLPU.LPU_LONG_NAME), 0), ' записей...') as ' '
--from tmpLPU, Organisation
--where (tmpLPU.OLD_CODES like concat(Organisation.infisCode, ',%') -- старый инфис-код в начале
--or tmpLPU.OLD_CODES like concat('%,', Organisation.infisCode, ',%') -- старый инфис-код в середине
--or tmpLPU.OLD_CODES like concat('%,', Organisation.infisCode)) -- старый инфис-код в конце
--and tmpLPU.CODE != Organisation.infisCode;

--update Organisation, tmpLPU
--set Organisation.modifyDatetime = now(), 
--    Organisation.modifyPerson_id = @user_id,
--    Organisation.fullName = tmpLPU.LPU_LONG_NAME,
--    Organisation.shortName = if(length(trim(tmpLPU.LPU_LONG_NAME)) <= 64, tmpLPU.LPU_LONG_NAME, tmpLPU.LPU_PRINT_NAME),
--    Organisation.title = tmpLPU.LPU_PRINT_NAME,
--    Organisation.infisCode = tmpLPU.CODE,
--    Organisation.INN = tmpLPU.INN,
--    Organisation.Address = tmpLPU.JUR_ADDRESS,
--    Organisation.chief = tmpLPU.FIO,
--    Organisation.phone = tmpLPU.PHONE,
--    Organisation.notes = concat(tmpLPU.REMARK, if(length(trim(tmpLPU.REMARK)) > 0, '. ', ''),
--				if(length(tmpLPU.EMAIL) > 0, 'E-mail: ', ''), tmpLPU.EMAIL, if(length(tmpLPU.EMAIL) > 0, '. ', ''),
--				if(length(tmpLPU.FAX) > 0, 'Fax: ', ''), tmpLPU.FAX)
--where (tmpLPU.OLD_CODES like concat(Organisation.infisCode, ',%') -- старый инфис-код в начале
--or tmpLPU.OLD_CODES like concat('%,', Organisation.infisCode, ',%') -- старый инфис-код в середине
--or tmpLPU.OLD_CODES like concat('%,', Organisation.infisCode)) -- старый инфис-код в конце
--and (tmpLPU.CODE != Organisation.infisCode or tmpLPU.CODE = '');



-- такого ИНН нет - добавить организацию
select concat('Добавление записей...') as ' ';
select concat('Добавляем ', format(count(tmpLPU.LPU_LONG_NAME), 0), ' записей...') as ' '
from tmpLPU
where not exists (
    select fullName from Organisation
    where tmpLPU.INN = Organisation.INN);

insert into Organisation
select 0 as id,
       now() as createDatetime, 
       @user_id as createPerson_id,
       now() as modifyDatetime, 
       @user_id as modifyPerson_id,
       0 as deleted,
       LPU_LONG_NAME as fullName,
       if(length(trim(LPU_LONG_NAME)) <= 64, LPU_LONG_NAME, LPU_PRINT_NAME) as shortName,
       LPU_PRINT_NAME as title,
       if(LPU_LONG_NAME like '%Стомат%' or LPU_LONG_NAME like '% стомат%', 4,
        if(LPU_LONG_NAME like 'Жен%' or LPU_LONG_NAME like '% Жен%' or LPU_LONG_NAME like '% жен%' or LPU_LONG_NAME like '%Родильн%' or LPU_LONG_NAME like '%родильн%' or LPU_LONG_NAME like '%Роддом%' or LPU_LONG_NAME like '%роддом%', 3,
	 if(LPU_LONG_NAME like 'Дет%' or LPU_LONG_NAME like '% Дет%' or LPU_LONG_NAME like '% дет%', 2, 1)))
	  as net_id,
       CODE as infisCode,
       OLD_CODES as obsoleteInfisCode,
       '' as OKVED,
       INN,
       '' as KPP,
       '' as OGRN,
       '' as OKATO, -- можно извлечь из адреса!!!
       '' as OKPF_code,
       ID_PARENT as OKPF_id, -- хитрый финт ушами: временно вставляем сюда id предка, чтобы не дублировать tmpLPU!!!!!!!!!!!!!!!!!!!!!!!!
       '' as OKFS_code,
       NULL as OKFS_id,
       OKPO,
       '' as FSS,
       '' as region, -- можно извлечь из адреса!!!
       JUR_ADDRESS as Address, 
       FIO as chief,
       PHONE as phone,
       '' as accountant,
       0 as isInsurer,
       if(ID_LPU_TYPE in (3, 4, 6, 14, 17, 18, 19, 36), 1,
        if(ID_LPU_TYPE in (1, 2, 5, 8, 9, 10, 11, 12, 21, 22, 23, 24, 30, 31, 32, 34, 35, 38, 39, 40, 41, 42, 43, 44), 0,
	 if(LPU_LONG_NAME like '%Больниц%' or LPU_LONG_NAME like '%больниц%'
	    or LPU_LONG_NAME like '%Б-ца%' or LPU_LONG_NAME like '%б-ца%'
	    or LPU_LONG_NAME like '%Госпиталь%' or LPU_LONG_NAME like '%госпиталь%'
	    or LPU_LONG_NAME like '%Родильн%' or LPU_LONG_NAME like '%родильн%'
	    or LPU_LONG_NAME like '%Роддом%' or LPU_LONG_NAME like '%роддом%'
	    or LPU_LONG_NAME like '%Стационар%' or LPU_LONG_NAME like '%cтационар%' or LPU_LONG_NAME like '%cтационар'
	    or LPU_LONG_NAME like '%ЦРБ%' or LPU_LONG_NAME like '%ЦКБ%' or LPU_LONG_NAME like '%ЦРКБ%', 1, 0))) as isHospital,
       concat(REMARK, if(length(trim(REMARK)) > 0, '. ', ''), if(length(EMAIL) > 0, 'E-mail: ', ''), EMAIL, if(length(EMAIL) > 0, '. ', ''), if(length(FAX) > 0, 'Fax: ', ''), FAX) as notes,
       NULL as head_id
from tmpLPU
where tmpLPU.id = tmpLPU.ID_PAYER -- добавляем только те организации, которые платят за себя (а значит, являются юр. лицами и имеют ИНН)
and not exists (
    select fullName from Organisation
    where tmpLPU.INN = Organisation.INN);

-- А вот теперь можно добавить информацию о предках, если они есть:
update Organisation, tmpLPU,
       Organisation o -- таблица, в которой хранится предок
set Organisation.head_id = o.id
where tmpLPU.INN = o.INN
and Organisation.OKPF_id = tmpLPU.id;
and Organisation.id <> o.id; -- если id==ID_PARENT, значит, предков нет

-- вот теперь стираем временный неправильный OKPF_id
update Organisation, tmpLPU
set Organisation.OKPF_id = NULL
where tmpLPU.INN = Organisation.INN;




-- Теперь обновляем информацию о расчетных счетах:
select 'Обновление счетов организаций...' as ' ';

-- добавляем расчетный счет, если его еще нет
insert into Organisation_Account
select 0 as id,
       Organisation.id as organisation_id,
       '' as bankName,
       tmpLPU.PC as name,
       '' as notes,
        (select id from Bank 
            where Bank.BIK = tmpLPU.BIK and Bank.branchName = tmpLPU.FILIAL
            limit 1) as bank_id,
        0 as cash
from tmpLPU, Organisation
where not exists (
select id from Organisation_Account
where organisation_id = Organisation.id
)
and tmpLPU.INN = Organisation.INN;

-- и добавляем расчетный счет PC2, если таковой существует:
insert into Organisation_Account
select 0 as id,
       Organisation.id as organisation_id,
       '' as bankName,
       tmpLPU.PC2 as name,
       'PC2' as notes,
        (select id from Bank 
            where Bank.BIK = tmpLPU.BIK and Bank.branchName = tmpLPU.FILIAL
            limit 1) as bank_id,
        0 as cash
from tmpLPU, Organisation
where (
select count(*) from Organisation_Account
where organisation_id = Organisation.id
) < 2
and tmpLPU.INN = Organisation.INN
and length(tmpLPU.PC2) > 0 and left(tmpLPU.PC2, 1) != ' ' and left(tmpLPU.PC2, 1) != '-';"""