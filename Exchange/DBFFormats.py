#!/usr/bin/env python
# -*- coding: utf-8 -*-
def get_RD1_fields():
    fields = [
        ('NUMTR', 'C', 10), ('DATETR', 'D', 8), ('ID', 'C', 30), ('KOD_OKUD', 'C', 25), ('NAME_ORG', 'C', 200), ('KOD_ORG_OK', 'C', 20), ('KOD_ORG_OG', 'C', 15), ('NAME_OKVED', 'C', 20), ('KOD_ORG_OD', 'C', 20), ('NAME_FS', 'C', 200),  ('KOD_OKOPF', 'C', 40), ('NAME_ORG_P', 'C', 200), ('KOD_ORG_1', 'N', 20), ('KOD_ORG_2', 'N', 15), ('PERIOD', 'N', 2),
#        ('PERIOD_OKUD', 'C', 20),
        ('PERIOD_OKU', 'C', 20),
        ('KOD_OKEI', 'C', 4), ('DATE_DOG', 'D', 8), ('NOMER_DOG', 'C', 8), ('FAM', 'C', 40), ('IM', 'C', 40), ('OT', 'C', 40), ('POL', 'C', 1), ('DR', 'D', 8), ('ADRES_REG', 'C', 200), ('UL', 'C', 200), ('DOM', 'C', 10), ('KOR', 'C', 10), ('KV', 'C', 10), ('O_NAME', 'C', 200), ('S_POL', 'C', 10), ('N_POL', 'N', 20), ('OKVED', 'C', 20), ('SS', 'C', 14), ('DZ_MKB', 'C', 7)]
    for s in ['T', 'H', 'O', 'E', 'N', 'U', 'A']:
        fields.append((s+'_DO', 'D', 8))
    fields.append(('MU_VB', 'N', 1))
    for s in ['F', 'M', 'EKG', 'H', 'G', 'KAK', 'KAM']:
        fields.append((s+'_DI', 'D', 8))
    fields += [
        ('NORMA', 'N', 7, 0),
        ('RECEIVER', 'C', 5),
        ('SMO', 'C', 5),
        ('TYPEADDR', 'C', 1),
        ('AREA', 'C', 3),
        ('REGION', 'C', 4),
        ('NPUNKT', 'C', 30), ('STREET', 'C', 30), ('STREETYPE', 'C', 2), ('ORG', 'C', 200), ('OKVD', 'C', 20), ('PRIK', 'N', 1), ('TMO', 'C', 5), ('DATE_P', 'D', 8), ('INN', 'C', 15), ('RES_G', 'N', 1), ('KOD_PROG', 'N', 1), ('ERR_S', 'C', 100), ('ID_PAT', 'C', 30), ('DATE_OPLAT', 'D', 8), ('DATE_OTKAZ', 'D', 8), ('KOD_OTKAZ', 'N', 3), ('COMMENT',  'C', 250)
        ]
    return fields

def get_RD2_fields():
    fields = [
        ('ADATE', 'D', 8), ('PDATE', 'D', 8), ('GROUP', 'N', 1), ('DIAG', 'C', 6), ('SUMMA', 'N', 9, 2), ('REGNUM', 'N', 10), ('INN', 'C', 12), ('KPP', 'N', 9), ('SNILS', 'C', 14), ('LNAME', 'C', 40), ('FNAME', 'C', 40), ('MNAME', 'C', 40), ('BDATE', 'D', 8), ('SEX', 'C', 1), ('SPOLICY', 'C', 14), ('NPOLICY', 'C', 20), ('WORKV', 'N', 2), ('WORKS', 'N', 2), ('FQNT', 'N', 1)]
    for i in range(1, 7):
        fields.append(('FACTOR'+str(i), 'C', 10))
    for i in range(1, 7):
        fields.append(('DOCTOR'+str(i), 'N', 3))
    return fields

def get_RD3_fields():
    fields = [
        ('NUMTR', 'C', 10), ('DATETR', 'D', 8), ('ID', 'C', 30), ('KOD_OKUD', 'C', 25), ('NAME_ORG', 'C', 200), ('KOD_ORG_OK', 'C', 20), ('KOD_ORG_OG', 'C', 15), ('NAME_OKVED', 'C', 20), ('KOD_ORG_OD', 'C', 20), ('NAME_FS', 'C', 200),  ('KOD_OKOPF', 'C', 40), ('NAME_ORG_P', 'C', 200), ('KOD_ORG_1', 'N', 20), ('KOD_ORG_2', 'N', 15), ('PERIOD', 'N', 2),
#        ('PERIOD_OKUD', 'C', 20),
        ('PERIOD_OKU', 'C', 20),
        ('KOD_OKEI', 'C', 4), ('DATE_DOG', 'D', 8), ('NOMER_DOG', 'C', 8), ('FAM', 'C', 40), ('IM', 'C', 40), ('OT', 'C', 40), ('POL', 'C', 1), ('DR', 'D', 8), ('DET_U', 'C', 100), ('KOD_DET_U', 'C', 7), ('KOD_S_U', 'C', 7), ('ADRES_REG', 'C', 200), ('UL', 'C', 200), ('DOM', 'C', 10), ('KOR', 'C', 10), ('KV', 'C', 10), ('O_NAME', 'C', 200), ('S_POL', 'C', 10), ('N_POL', 'N', 20), ('DZ_MKB', 'C', 7)]
    for s in ['T', 'N', 'O', 'H', 'L', 'G', 'S', 'OT', 'P', 'U', 'E']:
        fields.append((s+'_DO', 'D', 8))
    for s in ['UZI_DI1', 'UZI_DI2', 'UZI_DI3', 'EKG_DI', 'KAK_DI', 'KAM_DI']:
        fields.append((s, 'D', 8))
    fields += [
        ('NORMA', 'N', 7, 0), ('RECEIVER', 'C', 5), ('SMO', 'C', 5), ('TYPEADDR', 'C', 1), ('AREA', 'C', 3), ('REGION', 'C', 4), ('NPUNKT', 'C', 30), ('STREET', 'C', 30), ('STREETYPE', 'C', 2), ('PRIK', 'N', 1), ('TMO', 'C', 5), ('DATE_P', 'D', 8), ('RES_G', 'N', 1), ('KOD_PROG', 'N', 1), ('DATE_OPLAT', 'D', 8), ('DATE_OTKAZ', 'D', 8), ('ERR_S', 'C', 50), ('COMMENT',  'C', 250), ('ID_PAT',  'C', 30)]
    return fields

def get_RD4_fields():
    fields = [
        ('NUMTR', 'C', 15), ('DATETR', 'D', 8), ('ID', 'C', 30), ('KOD_OKUD', 'C', 25), ('NAME_ORG', 'C', 200), ('KOD_ORG_OK', 'C', 20), ('KOD_ORG_OG', 'C', 15), ('NAME_OKVED', 'C', 20), ('KOD_ORG_OD', 'C', 20), ('NAME_FS', 'C', 200),  ('KOD_OKOPF', 'C', 40), ('NAME_ORG_P', 'C', 200), ('KOD_ORG_1', 'C', 10), ('KOD_ORG_2', 'C', 15), ('PERIOD', 'N', 2),
#        ('PERIOD_OKUD', 'C', 20),
        ('PERIOD_OKU', 'C', 20),
        ('KOD_OKEI', 'C', 4), ('DATE_DOG', 'D', 8), ('NOMER_DOG', 'C', 8), ('FAM', 'C', 40), ('IM', 'C', 40), ('OT', 'C', 40), ('POL', 'C', 1), ('DR', 'D', 8), ('ADRES_REG', 'C', 200), ('UL', 'C', 200), ('DOM', 'C', 10), ('KOR', 'C', 10), ('KV', 'C', 10), ('O_NAME', 'C', 200), ('S_POL', 'C', 10), ('N_POL', 'C', 20), ('OKVED', 'C', 20), ('SS', 'C', 14), ('DZ_MKB', 'C', 7)]
    for s in ['T', 'H', 'O', 'E', 'N', 'U', 'A']:
        fields.append((s+'_DO', 'D', 8))
    fields.append(('F_DI', 'D', 8))
    fields.append(('MU_VB', 'N', 1))
    for s in ['M_DI', 'EKG_DI', 'H_DI', 'L_DI', 'G_DI', 'KAK_DI', 'KAM_DI', 'T_DI', 'O_CA', 'O_PSI']:
        fields.append((s, 'D', 8))
    fields += [
        ('NORMA', 'N', 7, 0),
        ('RECEIVER', 'C', 5),
        ('SMO', 'C', 5),
        ('TYPEADDR', 'C', 1),
        ('AREA', 'C', 3),
        ('REGION', 'C', 4),
        ('NPUNKT', 'C', 30), ('STREET', 'C', 30), ('STREETYPE', 'C', 2), ('ORG', 'C', 200), ('OKVD', 'C', 20), ('PRIK', 'N', 1), ('TMO', 'C', 5), ('DATE_P', 'D', 8), ('INN', 'C', 20), ('RES_G', 'N', 1), ('KOD_PROG', 'N', 1), ('ERR_S', 'C', 100), ('ID_PAT', 'C', 30), ('DATE_OPLAT', 'D', 8), ('DATE_OTKAZ', 'D', 8), ('KOD_OTKAZ', 'N', 3), ('N_ACT', 'N', 3), ('DATE_FACT', 'D', 8), ('COMMENT',  'C', 250), ('NUM_V',  'N', 2), ('DATE_V',  'D', 8)
        ]
    return fields


def get_RD5_fields():
    fields = [
        ('NUMTR', 'C', 20),
        ('DATETR', 'D', 8),
        ('ID', 'C', 30),
        ('KOD_OKUD', 'C', 25),
        ('NAME_ORG', 'C', 200),
        ('KOD_ORG_OK', 'C', 20),
        ('KOD_ORG_OG', 'C', 15),
        ('NAME_OKVED', 'C', 20),
        ('KOD_ORG_OD', 'C', 20),
        ('NAME_FS', 'C', 200),
        ('KOD_OKOPF', 'C', 40),
        ('NAME_ORG_P', 'C', 200),
        ('KOD_ORG_1', 'C', 10),
        ('KOD_ORG_2', 'C', 15),
        ('PERIOD', 'N', 2),
        ('PERIOD_OKU', 'C', 20),
        ('KOD_OKEI', 'C', 4),
        ('DATE_DOG', 'D', 8),
        ('NOMER_DOG', 'C', 12),
        ('FAM', 'C', 40),
        ('IM', 'C', 40),
        ('OT', 'C', 40),
        ('POL', 'C', 1),
        ('DR', 'D', 8),
        ('ADRES_REG', 'C', 200),
        ('UL', 'C', 200),
        ('DOM', 'C', 10),
        ('KOR', 'C', 10),
        ('KV', 'C', 10),
        ('O_NAME', 'C', 200),
        ('S_POL', 'C', 10),
        ('N_POL', 'C', 20),
        ('OKVED', 'C', 20),
#        ('SS', 'C', 14),
        ('DZ_MKB', 'C', 7)]
    for s in ['T', 'H', 'O', 'N', 'A']:
        fields.append((s+'_DO', 'D', 8))
    fields += [
        ('ZIM_ZK', 'D', 8),
        ('KAK_DI', 'D', 8),
        ('KAM_DI', 'D', 8),
        ('B_DI', 'D', 8),
        ('H_DI', 'D', 8),
        ('L_DI', 'D', 8),
        ('T_DI', 'D', 8),
        ('KM_DI', 'D', 8),
        ('BA_DI', 'D', 8),
        ('G_DI', 'D', 8),
        ('O_CA', 'D', 8),
        ('O_PSI', 'D', 8),
        ('EKG_DI', 'D', 8),
        ('F_DI', 'D', 8),
        ('MU_VB', 'N', 1),
        ('M_DI', 'D', 8),
        ('NORMA', 'N', 7, 0),
        ('RECEIVER', 'C', 5),
        ('SMO', 'C', 5),
        ('TYPEADDR', 'C', 1),
        ('AREA', 'C', 3),
        ('REGION', 'C', 4),
        ('NPUNKT', 'C', 30),
        ('STREET', 'C', 30),
        ('STREETYPE', 'C', 2),
        ('ORG', 'C', 200),
        ('INN', 'C', 12),
        ('OKVD', 'C', 20),
        ('PRIK', 'N', 1),
        ('TMO1', 'C', 5),
        ('DATE_P', 'D', 8),
        ('RES_G', 'N', 1),
        ('KOD_PROG', 'N', 1),
        ('NUM_V', 'N', 2),
        ('DATE_V', 'D', 8),
        ('ERR_S', 'C', 100),
        ('ERR_REM', 'C', 100),
        ('ID_ERR', 'C', 20),
        ('PERIOD_63', 'C', 150),
        ('DATE_OTKAZ', 'D', 8),
        ('N_ACT', 'N', 3),
        ('DATE_OPLAT', 'D', 8),
        ('DATE_FACT', 'D', 8),
        ('TMO2', 'C', 5),
        ('KOD_OTKAZ', 'N', 3),
        ('COMMENT', 'C', 250),
        ]
    return fields


def get_RD6_fields():
    fields = [
        ('NUMTR', 'C', 20),
        ('DATETR', 'D', 8),
        ('ID', 'C', 30),
        ('KOD_OKUD', 'C', 25),
        ('NAME_ORG', 'C', 200),
        ('KOD_ORG_OK', 'C', 20),
        ('KOD_ORG_OG', 'C', 15),
        ('NAME_OKVED', 'C', 20),
        ('KOD_ORG_OD', 'C', 20),
        ('NAME_FS', 'C', 200),
        ('KOD_OKOPF', 'C', 40),
        ('NAME_ORG_P', 'C', 200),
        ('KOD_ORG_1', 'C', 10),
        ('KOD_ORG_2', 'C', 15),
        ('PERIOD', 'N', 2),
        ('PERIOD_OKU', 'C', 20),
        ('KOD_OKEI', 'C', 4),
        ('DATE_DOG', 'D', 8),
        ('NOMER_DOG', 'C', 12),
        ('FAM', 'C', 40),
        ('IM', 'C', 40),
        ('OT', 'C', 40),
        ('POL', 'C', 1),
        ('DR', 'D', 8),
        ('ADRES_REG', 'C', 200),
        ('UL', 'C', 200),
        ('DOM', 'C', 10),
        ('KOR', 'C', 10),
        ('KV', 'C', 10),
        ('O_NAME', 'C', 200),
        ('S_POL', 'C', 10),
        ('N_POL', 'C', 20),
        ('OKVED', 'C', 20),
#        ('SS', 'C', 14),
        ('DZ_MKB', 'C', 7)]
    for s in ['T', 'H', 'O', 'N', 'A']:
        fields.append((s+'_DO', 'D', 8))
    fields += [
        ('ZIM_ZK', 'D', 8),
        ('KAK_DI', 'D', 8),
        ('KAM_DI', 'D', 8),
        ('B_DI', 'D', 8),
        ('H_DI', 'D', 8),
        ('L_DI', 'D', 8),
        ('T_DI', 'D', 8),
        ('KR_DI', 'D', 8),
        ('MK_DI', 'D', 8),
        ('BL_DI', 'D', 8),
        ('AM_DI', 'D', 8),
        ('G_DI', 'D', 8),
        ('O_CA', 'D', 8),
        ('O_PSI', 'D', 8),
        ('EKG_DI', 'D', 8),
        ('F_DI', 'D', 8),
        ('MU_VB', 'N', 1),
        ('M_DI', 'D', 8),
        ('NORMA', 'N', 7, 0),
        ('RECEIVER', 'C', 5),
        ('SMO', 'C', 5),
        ('TYPEADDR', 'C', 1),
        ('AREA', 'C', 3),
        ('REGION', 'C', 4),
        ('NPUNKT', 'C', 30),
        ('STREET', 'C', 30),
        ('STREETYPE', 'C', 2),
        ('ORG', 'C', 200),
        ('INN', 'C', 12),
        ('OKVD', 'C', 20),
        ('PRIK', 'N', 1),
        ('TMO1', 'C', 5),
        ('DATE_P', 'D', 8),
        ('RES_G', 'N', 1),
        ('NUM_PZ', 'N', 8),
        ('DATE_PZ', 'D', 8),
        ('KOD_PROG', 'N', 1),
        ('NUM_V', 'N', 2),
        ('DATE_V', 'D', 8),
        ('ERR_S', 'C', 100),
        ('ERR_REM', 'C', 100),
        ('ID_ERR', 'C', 20),
        ('PERIOD_63', 'C', 150),
        ('DATE_OTKAZ', 'D', 8),
        ('N_ACT', 'N', 3),
        ('DATE_OPLAT', 'D', 8),
        ('DATE_FACT', 'D', 8),
        ('TMO2', 'C', 5),
        ('KOD_OTKAZ', 'N', 3),
        ('COMMENT', 'C', 250),
        ('NUM_PP', 'D', 8),
        ]
    return fields


def get_RD7_fields():
    fields = [
        ('NUMTR', 'C', 20),
        ('DATETR', 'D', 8),
        ('ID', 'C', 30),
        ('KOD_OKUD', 'C', 25),
        ('NAME_ORG', 'C', 200),
        ('KOD_ORG_OK', 'C', 20),
        ('KOD_ORG_OG', 'C', 15),
        ('NAME_OKVED', 'C', 20),
        ('KOD_ORG_OD', 'C', 20),
        ('NAME_FS', 'C', 200),
        ('KOD_OKOPF', 'C', 40),
        ('NAME_ORG_P', 'C', 200),
        ('KOD_ORG_1', 'C', 10),
        ('KOD_ORG_2', 'C', 15),
        ('PERIOD', 'N', 2),
        ('PERIOD_OKU', 'C', 20),
        ('KOD_OKEI', 'C', 4),
        ('DATE_DOG', 'D', 8),
        ('NOMER_DOG', 'C', 12),
        ('FAM', 'C', 40),
        ('IM', 'C', 40),
        ('OT', 'C', 40),
        ('POL', 'C', 1),
        ('DR', 'D', 8),
        ('PASS_LF', 'C',  6),
        ('PASS_RI', 'C',  2),
        ('PASS_DOC', 'C', 12),
        ('SNILS', 'C', 14),
        ('ADRES_REG', 'C', 200),
        ('UL', 'C', 200),
        ('DOM', 'C', 10),
        ('KOR', 'C', 10),
        ('KV', 'C', 10),
        ('O_NAME', 'C', 200),
        ('S_POL', 'C', 10),
        ('N_POL', 'C', 20),
        ('STATUS_G', 'C', 12),
        ('OKVED', 'C', 20),
        ('DZ_MKB', 'C', 20)]
    for s in ['T', 'H', 'O', 'N', 'A']:
        fields.append((s+'_DO', 'D', 8))
    fields += [
        ('ZIM_ZK', 'D', 8),
        ('ZIM_ST', 'C', 20),
        ('KAK_DI', 'D', 8),
        ('KAM_DI', 'D', 8),
        ('B_DI', 'D', 8),
        ('H_DI', 'D', 8),
        ('L_DI', 'D', 8),
        ('T_DI', 'D', 8),
        ('KR_DI', 'D', 8),
        ('MK_DI', 'D', 8),
        ('BL_DI', 'D', 8),
        ('AM_DI', 'D', 8),
        ('G_DI', 'D', 8),
        ('O_CA', 'D', 8),
        ('O_PSI', 'D', 8),
        ('EKG_DI', 'D', 8),
        ('F_DI', 'D', 8),
        ('MU_VB', 'N', 1),
        ('M_DI', 'D', 8),
        ('M_ST', 'C', 20),
        ('NORMA', 'N', 7, 0),
        ('RECEIVER', 'C', 5),
        ('SMO', 'C', 5),
        ('TYPEADDR', 'C', 1),
        ('AREA', 'C', 3),
        ('REGION', 'C', 4),
        ('NPUNKT', 'C', 30),
        ('STREET', 'C', 30),
        ('STREETYPE', 'C', 2),
        ('ORG', 'C', 200),
        ('INN', 'C', 12),
        ('OKVD', 'C', 20),
        ('PRIK', 'N', 1),
        ('TMO1', 'C', 5),
        ('DATE_P', 'D', 8),
        ('RES_G', 'N', 1),
        ('NUM_PZ', 'N', 8),
        ('DATE_PZ', 'D', 8),
        ('KOD_PROG', 'N', 1),
        ('NUM_V', 'N', 2),
        ('DATE_V', 'D', 8),
        ('ERR_S', 'C', 100),
        ('ERR_REM', 'C', 255),
        ('ERR_REM_NL', 'C', 250),
        ('ID_ERR', 'C', 20),
        ('PERIOD_63', 'C', 150),
        ('DATE_OTKAZ', 'D', 8),
        ('N_ACT', 'N', 3),
        ('DATE_OPLAT', 'D', 8),
        ('DATE_FACT', 'D', 8),
        ('TMO2', 'C', 5),
        ('DATE_TMO2', 'D', 8),
        ('SMO2', 'C', 100),
        ('ID_HISTORY', 'N', 10),
        ('KOD_OTKAZ', 'N', 3),
        ('COMMENT', 'C', 250),
        ('NUM_PP', 'D', 8),
        ]
    return fields


def get_131_Fields():
    dbfFields=[
        ('OGRN', 'C', 15),
        ('ID', 'C', 25),
        ('DATE_DOG', 'D', 8),
        ('NOMER_DOG', 'C', 8),
        ('PROG', 'C', 15),
        ('TIP_DD', 'C', 5),
        ('N_MK', 'C', 20),
        ('FAM', 'C', 40),
        ('IM', 'C', 40),
        ('OT', 'C', 40),
        ('POL', 'N', 1),
        ('TYPE_DOC', 'C', 20),
        ('PASSPORT', 'C', 15),
        ('SMO_NAME', 'C', 70),
        ('SMO', 'C', 5),
        ('SN_POLIS', 'C', 35),
        ('SNILS', 'C', 14),
        ('DR', 'D', 8),
        ('ADRES_TYPE', 'N', 1),
        ('NAS_P', 'C', 70),
        ('UL', 'C', 70),
        ('DOM', 'C', 7),
        ('KOR', 'C', 5),
        ('KV', 'C', 5),
        ('RABOTA', 'C', 70),
        ('INN', 'C', 20),
        ('KPP', 'C', 20),
        ('OKVED', 'C', 20),
        ('DOLGN', 'C', 30),
        ('WORKV', 'C', 10),
        ('WORKS', 'N', 2),
        ('FAKTOR', 'C', 10),
        ('PDATE', 'D', 8),
        ('PRIK', 'N', 1),
        ('P_LPY_NAME', 'C', 50),
        ('P_LPY_KOD', 'C', 15),
        ('P_LPY_OGRN', 'C', 15)]
    for (spec, diagNum) in [('T', 5), ('A', 3), ('N', 3), ('U', 3), ('H', 3), ('O', 3), ('E', 3)]:
        dbfFields.append((spec+'_NAME', 'C', 70))
        dbfFields.append((spec+'_KOD', 'C', 12))
        dbfFields.append((spec+'_DO', 'D', 8))
        for iDiag in range(1, diagNum+1):
            dbfFields.append((spec+'_MKB_'+str(iDiag), 'C', 7))
            dbfFields.append((spec+'_V_'+str(iDiag), 'N', 1))
            dbfFields.append((spec+'_ST_'+str(iDiag), 'N', 1))
            dbfFields.append((spec+'_GZ_'+str(iDiag), 'N', 1))
        dbfFields.append((spec+'_SL', 'N', 1))
    for spec in ['1', '2', '3']:
        dbfFields.append(('NAME_'+spec, 'C', 70))
        dbfFields.append(('SPEC_'+spec, 'C', 20))
        dbfFields.append(('KOD_'+spec, 'C', 12))
        dbfFields.append(('DO_'+spec, 'D', 8))
        dbfFields.append(('S_'+spec+'_MKB_1', 'C', 7))
        dbfFields.append(('S_'+spec+'_V_1', 'N', 1))
        dbfFields.append(('S_'+spec+'_ST_1', 'N', 1))
        dbfFields.append(('S_'+spec+'_GZ_1', 'N', 1))
        dbfFields.append(('SL_'+spec, 'N', 1))
    for name in ['H', 'G', 'KAK', 'KAM']:
        dbfFields.append((name+'_DI', 'D', 8))
        dbfFields.append((name+'_DP', 'D', 8))
    dbfFields.append(('MU_VB', 'N', 1))
    for name in ['M', 'UPROST', 'F', 'EKG']:
        dbfFields.append((name+'_DI', 'D', 8))
        dbfFields.append((name+'_DP', 'D', 8))
    for name in ['1','2']:
        dbfFields.append(('DOP_'+name+'_NAME', 'C', 200))
        dbfFields.append(('DI_'+name, 'D', 8))
        dbfFields.append(('DP_'+name, 'D', 8))
    dbfFields.extend([
        ('DATE_DU', 'D', 8),
        ('DATE_OSM_6', 'D', 8),
        ('DZ_MKB_6', 'C', 70),
        ('S_DN', 'N', 1),
        ('PS', 'C', 70),
        ('DATE_ZAV', 'D', 8),
        ('DATE_OPLAT', 'D', 8),
        ('DATE_OTKAZ', 'D', 8),
        ('KOD_OTKAZ', 'N', 3),
        ('COMMENT', 'C', 250)])
    return dbfFields

def get_131_Fields_new():
    dbfFields=[
        ('OGRN', 'C', 15),
        ('ID', 'C', 25),
        ('DATE_DOG', 'D', 8),
        ('NOMER_DOG', 'C', 8),
        ('PROG', 'C', 15),
        ('TIP_DD', 'C', 5),
        ('N_MK', 'C', 20),
        ('FAM', 'C', 40),
        ('IM', 'C', 40),
        ('OT', 'C', 40),
        ('POL', 'N', 1),
        ('TYPE_DOC', 'C', 20),
        ('PASSPORT', 'C', 15),
        ('SMO_NAME', 'C', 70),
        ('SMO', 'C', 5),
        ('SN_POLIS', 'C', 35),
        ('SNILS', 'C', 14),
        ('DR', 'D', 8),
        ('ADRES_TYPE', 'N', 1),
        ('NAS_P', 'C', 70),
        ('UL', 'C', 70),
        ('DOM', 'C', 7),
        ('KOR', 'C', 5),
        ('KV', 'C', 5),
        ('RABOTA', 'C', 70),
        ('INN', 'C', 20),
        ('KPP', 'C', 20),
        ('OKVED', 'C', 20),
        ('DOLGN', 'C', 30),
        ('WORKV', 'C', 10),
        ('WORKS', 'N', 2),
        ('FAKTOR', 'C', 10),
        ('PDATE', 'D', 8),
        ('PRIK', 'N', 1),
        ('P_LPY_NAME', 'C', 50),
        ('P_LPY_KOD', 'C', 15),
        ('P_LPY_OGRN', 'C', 15)]
    for (spec, diagNum) in [('T', 5), ('A', 3), ('N', 3), ('U', 3), ('H', 3), ('O', 3), ('E', 3)]:
        dbfFields.append((spec+'_NAME', 'C', 70))
        dbfFields.append((spec+'_KOD', 'C', 12))
        dbfFields.append((spec+'_DO', 'D', 8))
        for iDiag in range(1, diagNum+1):
            dbfFields.append((spec+'_MKB_'+str(iDiag), 'C', 7))
            dbfFields.append((spec+'_V_'+str(iDiag), 'N', 1))
            dbfFields.append((spec+'_ST_'+str(iDiag), 'N', 1))
            dbfFields.append((spec+'_GZ_'+str(iDiag), 'N', 1))
        dbfFields.append((spec+'_SL', 'N', 1))
    for spec in ['1', '2', '3']:
        dbfFields.append(('NAME_'+spec, 'C', 70))
        dbfFields.append(('SPEC_'+spec, 'C', 20))
        dbfFields.append(('KOD_'+spec, 'C', 12))
        dbfFields.append(('DO_'+spec, 'D', 8))
        dbfFields.append(('S_'+spec+'_MKB_1', 'C', 7))
        dbfFields.append(('S_'+spec+'_V_1', 'N', 1))
        dbfFields.append(('S_'+spec+'_ST_1', 'N', 1))
        dbfFields.append(('S_'+spec+'_GZ_1', 'N', 1))
        dbfFields.append(('SL_'+spec, 'N', 1))
    for name in ['H', 'L', 'T', 'O_CA', 'O_PSI', 'G', 'KAK', 'KAM']:
        dbfFields.append((name+'_DI', 'D', 8))
        dbfFields.append((name+'_DP', 'D', 8))
    dbfFields.append(('MU_VB', 'N', 1))
    for name in ['M', 'UPROST', 'F', 'EKG']:
        dbfFields.append((name+'_DI', 'D', 8))
        dbfFields.append((name+'_DP', 'D', 8))
    for name in ['1','2']:
        dbfFields.append(('DOP_'+name+'_NAME', 'C', 200))
        dbfFields.append(('DI_'+name, 'D', 8))
        dbfFields.append(('DP_'+name, 'D', 8))
    dbfFields.extend([
        ('DATE_DU', 'D', 8),
        ('DATE_OSM_6', 'D', 8),
        ('DZ_MKB_6', 'C', 70),
        ('S_DN', 'N', 1),
        ('PS', 'C', 70),
        ('DATE_ZAV', 'D', 8),
        ('DATE_OPLAT', 'D', 8),
        ('DATE_OTKAZ', 'D', 8),
        ('KOD_OTKAZ', 'N', 3),
        ('COMMENT', 'C', 250)])
    return dbfFields

#def get_DD_fields():
#    return ['SEX', 'SURNAME', 'NAME', 'SECOND_NAM', 'BIRTHDAY', 'DOC_TYPE', 'SERIA_LEFT', 'SERIA_RIGH', 'DOC_NUMBER', 'POLIS_SERI', 'POLIS_NUMB', 'UNSTRUCT_A', 'AREA_INF', 'CODE_INF', 'HOUSE', 'KORPUS', 'FLAT', 'GR_OKVED', 'RAION', 'NAME_PKC', 'NAME_KR', 'UR_ADR', 'INN_N', 'KPP_N', 'OKVED', 'LPU_PRINT_', 'CODE'] Старая версия
def get_DD_fields():
    return ['SEX', 'SURNAME', 'NAME', 'SECOND_NAM', 'BIRTHDAY', 'POLIS_SERI', 'POLIS_NUMB', 'UNSTRUCT_A', 'AREA_INF', 'CODE_INF', 'HOUSE', 'KORPUS', 'FLAT', 'NAME_PKC', 'NAME_KR', 'UR_ADR', 'INN_N', 'KPP_N', 'OKVED', 'LPU_PRINT', 'CODE']

def get_RD_DS_2011_fields():
    fields = [
        ('NUMTR', 'C', 14), ('DATETR', 'D', 8), ('ID', 'C', 30), ('KOD_OKUD', 'C', 25), ('NAME_ORG', 'C', 200), ('KOD_ORG_OK', 'C', 20), ('KOD_ORG_OG', 'C', 15), ('NAME_OKVED', 'C', 20), ('KOD_ORG_OD', 'C', 20), ('NAME_FS', 'C', 200),  ('KOD_OKOPF', 'C', 40), ('NAME_ORG_P', 'C', 200), ('KOD_ORG_1', 'C', 20), ('KOD_ORG_2', 'C', 15), ('PERIOD', 'N', 2), ('PERIOD_OKU', 'C', 20), ('KOD_OKEI', 'C', 4), ('DATE_DOG', 'D', 8), ('NOMER_DOG', 'C', 10), ('FAM', 'C', 40), ('IM', 'C', 40), ('OT', 'C', 40), ('POL', 'C', 1), ('DR', 'D', 8), ('SV_PS_LF', 'C', 6), ('SV_PS_RI', 'C', 6), ('SV_PS_NUM', 'C', 12), ('SNILS', 'C', 15), ('DET_U', 'C', 250), ('OGRN_U', 'C', 20), ('ADRES_REG', 'C', 200), ('UL', 'C', 200), ('DOM', 'C', 10), ('KOR', 'C', 10), ('KV', 'C', 10), ('O_NAME', 'C', 200), ('S_POL', 'C', 10), ('N_POL', 'C', 20), ('PRIZNAK_S', 'C', 1), ('ZAC_RRED', 'C', 85), ('DZ_MKB', 'C', 7)]
    for s in ['T', 'N', 'O', 'H', 'L', 'G', 'S', 'OT', 'P', 'U', 'E']:
        fields.append((s+'_DO', 'D', 8))
    for s in ['UZI_1DI', 'UZI_2DI', 'UZI_3DI', 'UZI_4DI', 'EKG_DI', 'KAK_DI', 'KAM_DI']:
        fields.append((s, 'D', 8))
    fields += [
        ('NORMA', 'N', 7, 2), ('RECEIVER', 'C', 5), ('SMO', 'C', 5), ('TYPEADDR', 'C', 1), ('AREA', 'C', 3), ('REGION', 'C', 4), ('NPUNKT', 'C', 30), ('STREET', 'C', 30), ('STREETYPE', 'C', 2), ('PRIK', 'N', 1), ('TMO', 'C', 5), ('DATE_P', 'D', 8), ('RES_G', 'N', 1), ('KOD_PROG', 'N', 1),
        ('ERR_S', 'C', 100), ('ERR_REM', 'C', 255), ('ERR_REM_NL', 'C', 250), ('ID_ERR', 'C', 20), ('PERIOD_63', 'C', 150), ('N_ACT', 'N', 3), ('SMO2', 'C', 100), ('DATE_OPLAT', 'D', 8), ('DATE_FACT', 'D', 8), ('DATE_OTKAZ', 'D', 8), ('ID_HISTORY', 'N', 10), ('KOD_OTKAZ', 'N', 3),
        ('COMMENT',  'C', 250), ('NUM_PP', 'N', 8), ('NUM_V',  'N', 2), ('DATE_V',  'D', 8)]
    return fields


def get_SailOrgStructure_fields():
    return [('ID','C',4), ('DELETED', 'C', 1), ('CODE', 'C', 15), ('NAME', 'C', 240), ('PARENT_ID', 'C', 4), ('TYPE', 'C', 240), ('HASHOSPITA', 'C', 1)]


def get_SailPerson_fields():
    return [('ID','C',4), ('CODE', 'C', 10), ('FEDERALCOD', 'C', 20), ('REGIONALCO', 'C', 20), ('LASTNAME', 'C', 240), ('FIRSTNAME', 'C', 240), ('PATRNAME', 'C', 240), ('POST_ID', 'C', 10), ('SPECIALITY', 'C', 10), ('ORGSTRUCTU', 'C', 4), ('TARIFFCATE', 'C', 240), ('FINANCE_ID', 'C', 240), ('RETIREDATE', 'D'), ('RETIRED', 'C', 1), ('BIRTHDATE', 'D', 240), ('SEX', 'C', 1), ('SNILS', 'C', 15), ('INN', 'C', 20)]


