# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################
import re

ord0 = ord('0')
ordA = ord('A')

startChar = re.compile('^[A-Z]')
threeChar = re.compile('^[A-Z][0-9][0-9]$')
fourChar  = re.compile('^[A-Z][0-9][0-9]\.[0-9]$')
threeOrFourChar = re.compile('^[A-Z][0-9][0-9](\.[0-9])?$')


def normalizeCode(prefix, code):
    code = code.strip().upper()
#    if re.match('^[A-Z]', code) != None :
    if startChar.match(code) :
        codeParts = code.split('.')
        prefix = codeParts[0]
    else :
        assert prefix
        code = prefix + '.' + code
#    assert  re.match('^[A-Z][0-9][0-9](\.[0-9])?$', code) != None
    assert threeOrFourChar.match(code) != None
    return prefix, code


def addCodesRange(rowIdx, lowCode, highCode, mapCodesToRowIdx):
    def convCodeToNumber(code):
        r = (ord(code[0])-ordA)
        r = r*10 + (ord(code[1])-ord0)
        r = r*10 + (ord(code[2])-ord0)
        r = r*10 + (ord(code[4])-ord0)
        return r

    def convNumberToCode(num):
        return '%c%c%c.%c' % (num/1000+ordA,
                              (num/100)%10+ord0,
                              (num/10)%10+ord0,
                              (num)%10+ord0)
#        return chr(num/2600+ordA)+chr((num/100)%10+ord0)+chr((num/10)%10+ord0)+'.'+chr((num)%10+ord0)


    assert  lowCode <= highCode

#    if re.match('^[A-Z][0-9][0-9]$', lowCode) != None :
    if threeChar.match(lowCode):
        lowCode = lowCode + '.0'
#    if re.match('^[A-Z][0-9][0-9]$', highCode) != None :
    if threeChar.match(highCode):
        highCode = highCode + '.9'

    low  = convCodeToNumber(lowCode)
    high = convCodeToNumber(highCode)
    for i in xrange(low, high+1) :
        code = convNumberToCode(i)
        mapCodesToRowIdx.setdefault(code,[]).append(rowIdx)


def addCode(rowIdx, code, mapCodesToRowIdx) :
#    if re.match('^[A-Z][0-9][0-9]\.[0-9]', code) != None :
    if fourChar.match(code):
        mapCodesToRowIdx.setdefault(code,[]).append(rowIdx)
#    elif re.match('^[A-Z][0-9][0-9]$', code) != None :
    elif threeChar.match(code):
        addCodesRange(rowIdx, code, code, mapCodesToRowIdx)


def parseRowCodes(rowIdx, codes, mapCodesToRowIdx):
    diagRanges = codes.split(',')
    prefix = ''
    for diagRange in diagRanges:
        diagLimits = diagRange.split('-')
        n = len(diagLimits)
        if n == 1 and diagLimits[0]:
            prefix, code = normalizeCode(prefix, diagLimits[0])
            addCode(rowIdx, code, mapCodesToRowIdx)
        elif n == 2 :
            prefix, lowCode  = normalizeCode(prefix, diagLimits[0])
            prefix, highCode = normalizeCode(prefix, diagLimits[1])
            addCodesRange(rowIdx, lowCode, highCode, mapCodesToRowIdx)
        else :
            assert False, 'Wrong codes range "'+diagRange+'"';


def createMapCodeToRowIdx( codesList ):
    mapCodeToRowIdx = {}
    for rowIdx, code in enumerate(codesList):
        if code:
            parseRowCodes(rowIdx, str(code), mapCodeToRowIdx)
    return mapCodeToRowIdx