#! /usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
##
## Copyright (C) 2006-2012 Chuk&Gek and Vista Software. All rights reserved.
##
#############################################################################

try:
    import smartcard
except ImportError:
    pass

from ScardsModule.scard_reader import POMSReader, POMSDataDecoder, owner_information, smo_information


class Scard():
    def __readFromScard__(self, cardreader, onlyMainInfo):
        reader = POMSReader(cardreader)
        reader.connect()
        owner_info = reader.get_owner_information()
        out = POMSDataDecoder(owner_info, owner_information).decode_all()
        if not onlyMainInfo:
            smo_info = reader.get_smo_information()
            smo_decoded = POMSDataDecoder(smo_info, smo_information).decode_all()
            out.update(smo_decoded)
        reader.disconnect()
        return out

    def getCardReaderList(self):
        return smartcard.listReaders()

    def getClientInfo(self, cardreader, onlyMainInfo = False):
        info = self.__readFromScard__(str(cardreader), onlyMainInfo)
        out =  {
            'lastname': info['last_name'],
            'name': info['first_name'],
            'patrname': info['patr_name'],
            'gender': 'М' if info['sex'] == 1 else 'Ж',
            'birthday': info['birth_date'],
            'born_in': info['birth_place'],
            'country': {
                'code': info['citizenship']['country_code'] if info['citizenship'] else None,
                'name': info['citizenship']['country_cyrillic_name'] if info['citizenship'] else None
            },
            'policy': {
                'number': info['policy_number'],
                'beg_date': info['issue_date'],
                'end_date': info['expire_date']
            },
            # Insurance Number of Individual Ledger Account aka СНИЛС
            'SNILS': info['snils']
        }

        if not onlyMainInfo:
            out.update({
                'smo': {
                    'OGRN': info['ogrn'],
                    'OKATO': info['okato'],
                    'beg_date': info['insurance_start_date'],
                }
            })

        return out

if __name__ == '__main__':
    f = Scard().getCardReaderList()
