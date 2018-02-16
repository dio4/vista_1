#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
## Copyright (C) 2012 SAMSON Group. All rights reserved.
##
#############################################################################
##
## Это программа является свободным программным обеспечением.
## Вы можете использовать, распространять и/или модифицировать её согласно
## условиям GNU GPL версии 3 или любой более поздней версии.
##
#############################################################################

IBT_C_DECLARATION = r'''

typedef long LONG;
typedef unsigned long DWORD;

//  ..\Include\CardLib\il_types.h

typedef unsigned char IL_BYTE;
typedef unsigned short IL_WORD;
typedef unsigned int IL_DWORD;
typedef int IL_INT;
typedef char IL_CHAR;

typedef IL_WORD IL_RETCODE;
typedef IL_DWORD IL_TAG;

typedef void* IL_HANDLE_READER;
typedef void* IL_READER_SETTINGS;
typedef void* IL_HANDLE_CRYPTO;

//  ..\Include\CardLib\CardLibEx.h

typedef struct
{
    IL_BYTE id;
    IL_BYTE fid[2];
    IL_BYTE version;
} IL_RECORD_DEF;

typedef struct
{
    IL_RECORD_DEF rec[32];
    IL_WORD num_records;
} IL_RECORD_LIST;

typedef struct
{
    IL_HANDLE_READER hRdr;
    IL_HANDLE_CRYPTO hCrypto;
    IL_BYTE AppVer;
    IL_BYTE KeyVer;
    IL_BYTE AUC[2];
    IL_BYTE AppStatus;
    IL_BYTE ifLongAPDU;
    IL_BYTE ifGostCrypto;
    IL_BYTE ifSM;
    IL_BYTE ifNeedMSE;
    IL_BYTE ifSign;
    IL_WORD currDF;
    IL_WORD currEF;
    IL_WORD currEFLen;
    IL_RECORD_LIST sectors;
    IL_RECORD_LIST blocks;
    IL_BYTE CIN[10];
} IL_CARD_HANDLE;

//  winscard.h

typedef LONG SCARDCONTEXT;
typedef LONG SCARDHANDLE;

//  ..\Include\Hal\HAL_SCRHandle.h

typedef char* READER_SETTINGS;

typedef struct HANDLE_READER
{
    SCARDCONTEXT hContext;
    SCARDHANDLE hCard;

    READER_SETTINGS prdrSettings;
    DWORD dwShareMode;
    DWORD dwScope;
    DWORD dwProtocol;
    DWORD dwActiveProtocol;
    DWORD dwReaderState;
} HANDLE_READER;

//  ..\Include\CryptoLib\CryptoPKCS11.h

typedef void* IL_PKCS11_HANDLE;

//  ..\Include\CryptoLib\CryptoHandle.h

typedef struct
{
    IL_BYTE SessionSmCounter[8];
    IL_BYTE SKsmciddes[16];
    IL_BYTE SKsmiiddes[16];
    IL_BYTE SKsmcidgost[32];
    IL_BYTE SKsmiidgost[32];
} SM_CONTEXT;

typedef struct
{
    SM_CONTEXT SM;
    IL_BYTE Kifd[16];
    IL_BYTE tmpSifdgost[32];
    IL_BYTE tmpPifdgost[64];
    IL_BYTE SK_sm_id_smc_des[16];
    IL_PKCS11_HANDLE hPkcs11;
} HANDLE_CRYPTO;

//  ..\Include\Hal\HAL_SCRApdu.h

typedef struct IL_APDU
{
    IL_BYTE Cmd[4];
    IL_BYTE DataIn[512];
    IL_BYTE DataOut[512];
    IL_DWORD LengthIn;
    IL_DWORD LengthExpected;
    IL_DWORD LengthOut;
    IL_BYTE  SW1;
    IL_BYTE  SW2;
} IL_APDU;

//  ..\Include\CardLib\FuncLibEx.h

typedef struct
{
    IL_APDU	Apdu;
    IL_BYTE allowed_res_len;
    IL_BYTE allowed_res[40];
} IL_APDU_PACK_ELEM;

//  ..\Include\OpLib\opDescr.h

typedef struct
{
    IL_WORD	Id;
    IL_CHAR Icon[51];
} SECTOR_DESCR;

typedef struct
{
    IL_WORD	SectorId;
    IL_WORD	Id;
    IL_BYTE	FileType;
    IL_DWORD RootTag;
    IL_CHAR Icon[51];
} BLOCK_DESCR;

typedef struct
{
    IL_WORD	SectorId;
    IL_WORD	BlockId;
    IL_WORD	TagId;
    IL_WORD	Type;
    IL_WORD	MaxLen;
    IL_WORD	TPath[3];
    IL_BYTE isMust;
    IL_CHAR Name[51];
} DATA_DESCR;

typedef struct
{
    IL_WORD	SectorId;
    IL_WORD	BlockId;
    IL_WORD BlockLen;
    IL_BYTE *pData;
    IL_WORD DataLen;
} BINTLV_DESCR;

// ..\Include\CryptoLib\CryptoLib.h

typedef struct
{
    IL_BYTE Y[256];
    IL_WORD Y_len;

    IL_BYTE Random[256];
    IL_WORD Random_len;
    IL_BYTE Pidgost[64];
} PROVIDER_SESSION_DATA;

typedef struct
{
    IL_BYTE SK_sm_id_smc_des[16];
    IL_BYTE SK_sm_id_smc_gost[32];
} PROVIDER_SM_CONTEXT;

typedef struct
{
    IL_BYTE IcChallenge[16];
} ISSUER_SESSION_DATA_IN;

typedef struct
{
    IL_BYTE CardCryptogramm[20];
    IL_BYTE CardCryptogrammLength;
} ISSUER_SESSION_DATA_OUT;

typedef struct
{
    IL_BYTE HostChallenge[16];
    IL_BYTE CardCryptogramm[4];
} CHECK_ISSUER_SESSION_DATA_IN;

//  ..\Include\OpLib\OpCtxDef.h

typedef struct 
{
    IL_BYTE *pMsg;
    IL_WORD MsgLen;
    IL_BYTE *pS;
    IL_WORD SLen;
} PROVIDER_AUTH_DATA;

typedef struct
{
    IL_WORD State[32];
    IL_BYTE Index;
    IL_WORD InterruptEvent;
    IL_WORD wCntCycles;

    IL_CHAR PAN[23];
    IL_CHAR AppVersion[4];
    IL_CHAR EffectiveDate[7];
    IL_CHAR ExpirationDate[7];

    IL_CARD_HANDLE* phCrd;
    IL_WORD OperationCode;
    IL_WORD ResultCode;

    IL_BYTE PinNum;
    IL_BYTE PinBlock[8];
    IL_BYTE PinTriesLeft;
    IL_CHAR *pNewPinStr;
    IL_CHAR *pConfirmPinStr;
    IL_CHAR PassPhrase[41];
    IL_BYTE ifPassPhraseUsed;

    IL_BYTE *pMetaInfo;
    IL_WORD MetaInfoLen;
    IL_BYTE MataInfoCrc;

    IL_BYTE *pExtraData;
    IL_WORD ExtraDataLen;
    IL_BYTE ExtraDataCrc;

    IL_BYTE *pRequestHash;
    IL_WORD RequestHashLen;
    IL_BYTE RequestHashCrc;

    IL_CHAR *pSectorsDescrBuf;
    IL_WORD *pSectorsDescrLen;

    IL_CHAR *pCardDataDescr;
    IL_CHAR *pCardDataBuf;
    IL_WORD *pCardDataLen;

    IL_CHAR *pBlockDescr;
    IL_CHAR *pBlockDataBuf;
    IL_WORD *pBlockDataLen;

    IL_BYTE *pPhotoBuf;
    IL_WORD *pPhotoLen;

    IL_BYTE ifAuthOnline;
    IL_BYTE *pAuthRequestBuf;
    IL_WORD *pAuthRequestLen;
    IL_BYTE AuthRequestCrc;

    IL_BYTE *pAuthResponseData;
    IL_WORD AuthResponseLen;
    IL_BYTE *pKeyCert;
    IL_WORD KeyCertLen;
    IL_WORD AuthResult;

    IL_BYTE *pDigitalSignBuf;
    IL_WORD *pDigitalSignLen;
    IL_BYTE *pDigitalSignCertChain;
    IL_WORD *pDigitalSignCertChainLen;

    IL_BYTE AuthRequestIssSessionBuf[1024];
    IL_WORD AuthRequestIssSessionLen;

    IL_APDU_PACK_ELEM *pApduPacket;
    IL_BYTE isApduEncryptedPS;
    IL_WORD *pApduPacketSize;
    IL_WORD *pApduPacketResult;
    IL_BYTE *pApduIn;
    IL_WORD ApduInLen;
    IL_BYTE *pApduOut;
    IL_WORD *ApduOutLen;

    IL_WORD SectorIdAuth;

    SECTOR_DESCR ExSectorDescr[5];
    IL_WORD ExSectorsNum;
    BLOCK_DESCR ExBlockDescr[20];
    IL_WORD ExBlocksNum;
    DATA_DESCR ExDataDescr[50];
    IL_WORD ExDatasNum;
    IL_CHAR *pExSectorDesr;

    DATA_DESCR *pFirstEditDataDescr;
    DATA_DESCR *pFirstEditDataDescrCopy;

    ISSUER_SESSION_DATA_IN  sess_in;
    ISSUER_SESSION_DATA_OUT sess_out;
    CHECK_ISSUER_SESSION_DATA_IN chk_sess_in;

    IL_BYTE isProviderSession;
    IL_BYTE ifGostPS;
    IL_BYTE *pCSpId;
    IL_WORD CSpIdLen;
    PROVIDER_SESSION_DATA ProviderSessionData;
    PROVIDER_SM_CONTEXT PSMContext;
    PROVIDER_AUTH_DATA ProviderAuthData;
    IL_BYTE *pClearData;
    IL_DWORD *pClearDataLen;
    IL_BYTE *pEncryptedData;
    IL_DWORD *pEncryptedDataLen;

    IL_BYTE TmpBuf[8192];
    IL_WORD wTmp;
    IL_BYTE bTmp;

    BINTLV_DESCR BinTlvDescr;

    void (*pDisplayText)(IL_CHAR*);
} s_opContext;

//  ..\Include\Hal\HAL_Parameter.h

IL_RETCODE prmGetParameter(IL_WORD ParamId, IL_BYTE *out_pParamBuf, IL_DWORD *out_pParamLen);

// ..\Include\CryptoLib\CryptoLib.h

IL_RETCODE cryptoInit(IL_HANDLE_CRYPTO *phCrypto);
IL_RETCODE cryptoDeinit(IL_HANDLE_CRYPTO hCrypto);

//  ..\Include\CardLib\FuncLibEx.h

IL_RETCODE flInitReader(IL_CARD_HANDLE* phCrd, IL_READER_SETTINGS ilRdrSettings);
IL_RETCODE flDeinitReader(IL_CARD_HANDLE* phCrd);

//  ..\Include\CardLib\CardLibEx.h

IL_RETCODE clCardOpen(IL_CARD_HANDLE* phCrd);

// ..\Include\OpLib\opApi.h

IL_WORD  opApiInitOperation(s_opContext *p_opContext, IL_CARD_HANDLE *phCrd, IL_BYTE in_opCode,
                            IL_BYTE *in_pMetaInfo, IL_WORD MetaInfoLen,
                            IL_CHAR *out_PAN23, IL_CHAR *out_AppVer4, IL_CHAR *out_effDate7, IL_CHAR *out_expDate7,
                            IL_CHAR *out_PassPrase51, IL_BYTE *out_ifGostCrypto);
IL_WORD  opApiVerifyCitizen(s_opContext *p_opContext, IL_BYTE PinNum, IL_CHAR *in_strPin);
IL_WORD  opApiReadCardData(s_opContext *p_opContext, IL_CHAR *in_CardDataDescr, IL_CHAR *out_pCardDataBuf,
                           IL_WORD *inout_pCardDataLen);
IL_WORD  opApiDeinitOperation(s_opContext *p_opContext);
void     opApiGetVersion(IL_CHAR *out_LibVer, IL_CHAR *out_AppVer);
'''