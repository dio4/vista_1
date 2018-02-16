#!/usr/bin/env python
# -*- coding: utf-8 -*-

COMMAND = u"""
--use s11;

-- Сперва обновляем информацию о банках:
select 'Обновляем информацию о банках...' as ' ';
--select concat('Updating ', format(count(tmpSMO.SMO_LONG_NAME), 0), ' records...') as ' '

select 'Общее количество банков:' as ' ';
select @max_bank_id := max(id) from Bank;
-- сначала смотрим, какие BIK и имена филиалов отсутствуют; добавляем их
insert into Bank
select distinct
       0 as id,
       '0000-00-00 00:00:00' as createDatetime,
       @user_id as createPerson_id,
       '0000-00-00 00:00:00' as modifyDatetime,
       @user_id as modifyPerson_id,
       0 as deleted,
       BIK,
       '' as name,
       FILIAL as branchName,
       '' as corAccount,
       '' as subAccount
from tmpSMO
where not exists (
select BIK, branchName from Bank
where Bank.BIK = tmpSMO.BIK
and Bank.branchName = tmpSMO.FILIAL);

-- обновляем старые банки
update Bank, tmpSMO
set modifyDatetime = now(), 
    modifyPerson_id = @user_id,
    name = tmpSMO.Bank 
where Bank.BIK = tmpSMO.BIK
and Bank.branchName = tmpSMO.FILIAL
and Bank.id <= @max_bank_id;

-- и новые банки
update Bank, tmpSMO
set createDatetime = now(), 
    createPerson_id = @user_id,
    modifyDatetime = now(), 
    modifyPerson_id = @user_id,
    name = tmpSMO.Bank 
where Bank.BIK = tmpSMO.BIK
and Bank.branchName = tmpSMO.FILIAL
and Bank.id > @max_bank_id;







-- Теперь обновляем информацию об организациях:
select 'Обновляем информацию об организациях...' as ' ';

-- такой ИНН уже существует - обновить информацию
-- Обновляется в случае, если изменилось имя, ИНФИС, КПП, адрес, телефон или руководитель
select concat('Обновление ', format(count(tmpSMO.SMO_LONG_NAME), 0), ' записей...') as ' '
from tmpSMO, Organisation
where tmpSMO.INN = Organisation.INN;

update Organisation, tmpSMO
set Organisation.modifyDatetime = now(), 
    Organisation.modifyPerson_id = @user_id,
    Organisation.infisCode = tmpSMO.CODE,
    Organisation.fullName = tmpSMO.SMO_LONG_NAME,
    Organisation.KPP = tmpSMO.KPP,
    Organisation.Address = tmpSMO.JUR_ADDRESS,
    Organisation.chief = tmpSMO.FIO,
    Organisation.phone = tmpSMO.PHONE,
    Organisation.notes = concat(tmpSMO.REMARK, if(length(trim(tmpSMO.REMARK)) > 0, '. ', ''),
        if(length(tmpSMO.EMAIL) > 0, 'E-mail: ', ''), tmpSMO.EMAIL, if(length(tmpSMO.EMAIL) > 0, '. ', ''),
        if(length(tmpSMO.FAX) > 0, 'Fax: ', ''), tmpSMO.FAX)
where tmpSMO.INN = Organisation.INN
and (tmpSMO.CODE != Organisation.infisCode
    or Organisation.KPP != tmpSMO.KPP
    or Organisation.Address != tmpSMO.ADDRESS
    or Organisation.chief != tmpSMO.FIO
    or Organisation.phone != tmpSMO.PHONE );


-- такого имени нет, но такой старый ИНФИС уже существует - переименовать организацию и обновить информацию
--select concat('Переименование и обновление ', format(count(tmpSMO.SMO_LONG_NAME), 0), ' записей...') as ' '
--from tmpSMO, Organisation
--where (tmpSMO.OLD_CODES like concat(Organisation.infisCode, ',%') -- старый инфис-код в начале
--or tmpSMO.OLD_CODES like concat('%,', Organisation.infisCode, ',%') -- старый инфис-код в середине
--or tmpSMO.OLD_CODES like concat('%,', Organisation.infisCode)) -- старый инфис-код в конце
--and (tmpSMO.CODE != Organisation.infisCode
--or tmpSMO.CODE = '');

--update Organisation, tmpSMO
--set Organisation.modifyDatetime = now(), 
--    Organisation.modifyPerson_id = @user_id,
--    Organisation.fullName = tmpSMO.SMO_LONG_NAME,
--    Organisation.shortName = if(length(tmpSMO.SMO_LONG_NAME) <= 64, tmpSMO.SMO_LONG_NAME, tmpSMO.SMO_SHORT_NAME),
--    Organisation.title = tmpSMO.SMO_SHORT_NAME,
--    Organisation.infisCode = tmpSMO.CODE,
--    Organisation.INN = tmpSMO.INN,
--    Organisation.KPP = tmpSMO.KPP,
--    Organisation.Address = tmpSMO.JUR_ADDRESS,
--    Organisation.chief = tmpSMO.FIO,
--    Organisation.phone = tmpSMO.PHONE,
--    Organisation.notes = concat(tmpSMO.REMARK, if(length(trim(tmpSMO.REMARK)) > 0, '. ', ''),
--				if(length(tmpSMO.EMAIL) > 0, 'E-mail: ', ''), tmpSMO.EMAIL, if(length(tmpSMO.EMAIL) > 0, '. ', ''),
--				if(length(tmpSMO.FAX) > 0, 'Fax: ', ''), tmpSMO.FAX)
--where (tmpSMO.OLD_CODES like concat(Organisation.infisCode, ',%') -- старый инфис-код в начале
--or tmpSMO.OLD_CODES like concat('%,', Organisation.infisCode, ',%') -- старый инфис-код в середине
--or tmpSMO.OLD_CODES like concat('%,', Organisation.infisCode)) -- старый инфис-код в конце
--and (tmpSMO.CODE != Organisation.infisCode
--or tmpSMO.CODE = '');



-- такого ИНН нет - добавить организацию
select concat('Добавление ', format(count(tmpSMO.SMO_LONG_NAME), 0), ' записей...') as ' '
from tmpSMO
where not exists (
    select fullName from Organisation
    where tmpSMO.INN = Organisation.INN);


insert into Organisation
select 0 as id,
       now() as createDatetime, 
       @user_id as createPerson_id,
       now() as modifyDatetime, 
       @user_id as modifyPerson_id,
       0 as deleted,
       SMO_LONG_NAME as fullName,
       if(length(trim(SMO_LONG_NAME)) <= 64, SMO_LONG_NAME, SMO_SHORT_NAME) as shortName,
       SMO_SHORT_NAME as title,
       NULL as net_id,
       CODE as infisCode,
       if(CODE = OLD_CODES, '', OLD_CODES) as obsoleteInfisCode,
       '' as OKVED,
       INN,
       KPP,
       '' as OGRN,
       '' as OKATO, -- можно извлечь из адреса!!!
       '' as OKPF_code,
       NULL as OKPF_id,
       '' as OKFS_code,
       NULL as OKFS_id,
       OKPO,
       '' as FSS,
       '' as region, -- можно извлечь из адреса!!!
       JUR_ADDRESS as Address, 
       FIO as chief,
       PHONE as phone,
       '' as accountant,
       1 as isInsurer,
       0 as isHospital,
       concat(REMARK, if(length(trim(REMARK)) > 0, '. ', ''), if(length(EMAIL) > 0, 'E-mail: ', ''), EMAIL, if(length(EMAIL) > 0, '. ', ''), if(length(FAX) > 0, 'Fax: ', ''), FAX) as notes,
       NULL as head_id
from tmpSMO
where not exists (
    select fullName from Organisation
    where tmpSMO.INN = Organisation.INN);





-- Теперь обновляем информацию о расчетных счетах:
select 'Обновление счетов организаций...' as ' ';

-- добавляем расчетный счет, если его еще нет
insert into Organisation_Account
select 0 as id,
        Organisation.id as organisation_id,
        '' as bankName,
        tmpSMO.PC as name,
        '' as notes,
        (select id from Bank 
        where Bank.BIK = tmpSMO.BIK and Bank.branchName = tmpSMO.FILIAL
        limit 1) as bank_id,
        0 as cash
from tmpSMO, Organisation
where not exists (
select id from Organisation_Account
where organisation_id = Organisation.id
)
and tmpSMO.INN = Organisation.INN;

-- и добавляем расчетный счет PC2, если таковой существует:
insert into Organisation_Account
select 0 as id,
        Organisation.id as organisation_id,
        '' as bankName,
        tmpSMO.PC2 as name,
        'PC2' as notes,
        (select id from Bank 
        where Bank.BIK = tmpSMO.BIK and Bank.branchName = tmpSMO.FILIAL
        limit 1) as bank_id,
        0 as cash
from tmpSMO, Organisation
where (
select count(*) from Organisation_Account
where organisation_id = Organisation.id
) < 2
and tmpSMO.INN = Organisation.INN
and length(tmpSMO.PC2) > 0 and left(tmpSMO.PC2, 1) != ' ' and left(tmpSMO.PC2, 1) != '-';"""
