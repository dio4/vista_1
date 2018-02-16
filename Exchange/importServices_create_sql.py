#!/usr/bin/env python
# -*- coding: utf-8 -*-

COMMAND = u"""

CREATE TEMPORARY TABLE IF NOT EXISTS `tmpA` (
`code` CHAR( 9 ) NOT NULL ,
 `name` VARCHAR( 200 ) NOT NULL ,
 `rbService_id` INT( 11 ) NULL ,
 `rbService_type` TINYINT( 2 ) NOT NULL DEFAULT '0',
 `rbServiceType_id` INT( 11 ) NULL ,
 `rbServiceType_type` TINYINT( 1 ) NOT NULL DEFAULT '0',
 `rbServiceClass_id` INT( 11 ) NULL ,
 `rbServiceClass_type` TINYINT( 1 ) NOT NULL DEFAULT '0',
 PRIMARY KEY ( `code` ) ,
 INDEX ( `rbService_id` ) 
) ENGINE = MYISAM;

CREATE TEMPORARY TABLE IF NOT EXISTS `tmpB` (
`code` CHAR( 9 ) NOT NULL ,
 `name` VARCHAR( 200 ) NOT NULL ,
`rbService_id` INT( 11 ) NULL ,
`rbService_type` TINYINT( 2 ) NOT NULL DEFAULT '0',
`rbServiceType_id` INT( 11 ) NULL ,
`rbServiceType_type` TINYINT( 1 ) NOT NULL DEFAULT '0',
`rbServiceClass_id` INT( 11 ) NULL ,
`rbServiceClass_type` TINYINT( 1 ) NOT NULL DEFAULT '0',
 PRIMARY KEY ( `code` ) ,
 INDEX ( `rbService_id` ) 
) ENGINE = MYISAM;

CREATE TEMPORARY TABLE IF NOT EXISTS `tmpC` (
`master_code` VARCHAR( 10 ) NOT NULL ,
`master_name` VARCHAR( 200 ) NOT NULL ,
`section` CHAR( 1 ) NOT NULL ,
`code` VARCHAR( 10 ) NOT NULL ,
`name` VARCHAR( 200 ) NOT NULL ,
`required` TINYINT( 1 ) NOT NULL default 0,
 `rbServiceGroup_id` INT( 11 ) NULL ,
 `rbServiceGroup_type` TINYINT( 2 ) NOT NULL DEFAULT '0',
 PRIMARY KEY ( `master_code`, `code` ) ,
 INDEX ( `rbServiceGroup_id` ) 
) ENGINE = MYISAM;

CREATE TEMPORARY TABLE IF NOT EXISTS `tmpD` (
`code` VARCHAR( 14 ) NOT NULL ,
 `name` VARCHAR( 200 ) NOT NULL ,
 `rbService_id` INT( 11 ) NULL ,
 `rbService_type` TINYINT( 2 ) NOT NULL DEFAULT '0',
 `rbServiceType_id` INT( 11 ) NULL ,
 `rbServiceType_type` TINYINT( 1 ) NOT NULL DEFAULT '0',
 PRIMARY KEY ( `code` ) ,
 INDEX ( `rbService_id` ) 
) ENGINE = MYISAM;

CREATE TEMPORARY TABLE IF NOT EXISTS `tmpF` (
`code` VARCHAR( 11 ) NOT NULL ,
 `name` VARCHAR( 200 ) NOT NULL ,
 `rbService_id` INT( 11 ) NULL ,
 `rbService_type` TINYINT( 2 ) NOT NULL DEFAULT '0',
 `rbServiceType_id` INT( 11 ) NULL ,
 `rbServiceType_type` TINYINT( 1 ) NOT NULL DEFAULT '0',
 PRIMARY KEY ( `code` ) ,
 INDEX ( `rbService_id` ) 
) ENGINE = MYISAM;"""
